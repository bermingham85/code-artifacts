import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const ANTHROPIC_API_KEY = Deno.env.get("ANTHROPIC_API_KEY")!;

const EXTRACTION_PROMPT = `You are an APEX extraction agent. Given this conversation transcript, extract:
1. TASKS: concrete actionable items with owner, project, priority (high/medium/low)
2. SKILLS: reusable procedures that worked and should be saved as automation patterns
3. MEMORY UPDATES: facts about the user, projects, or systems that should persist across sessions
4. N8N IDEAS: workflow automations suggested or implied in the conversation
5. SUPABASE CHANGES: schema additions or data inserts required

Rules:
- Only extract items explicitly discussed or clearly implied
- Tasks must be actionable with a clear deliverable
- Skills must be reusable patterns, not one-off fixes
- Memory updates must be non-obvious facts worth persisting
- N8N ideas must be automatable workflows
- Supabase changes must be concrete DDL or DML

Return ONLY valid JSON. Schema:
{
  "tasks": [{"title": "", "owner": "", "project": "", "priority": "high|medium|low", "description": ""}],
  "skills": [{"name": "", "description": "", "trigger": "", "steps": [""]}],
  "memory_updates": [{"type": "user|project|feedback|reference", "name": "", "content": ""}],
  "n8n_ideas": [{"name": "", "trigger": "", "description": "", "nodes": [""]}],
  "supabase_changes": [{"type": "migration|insert|update", "table": "", "description": "", "sql": ""}]
}

If a category has no items, return an empty array for it.`;

const EXTRACTION_MODEL = "claude-sonnet-4-6-20250514";
const MAX_BATCH_SIZE = 5;

async function callClaude(
  conversationText: string,
): Promise<{ result: Record<string, unknown[]>; tokens: number }> {
  const response = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "x-api-key": ANTHROPIC_API_KEY,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify({
      model: EXTRACTION_MODEL,
      max_tokens: 4096,
      messages: [
        {
          role: "user",
          content: `${EXTRACTION_PROMPT}\n\n--- CONVERSATION TRANSCRIPT ---\n${conversationText.slice(0, 100000)}`,
        },
      ],
    }),
  });

  if (!response.ok) {
    const errBody = await response.text();
    throw new Error(`Anthropic API error ${response.status}: ${errBody}`);
  }

  const data = await response.json();
  const text = data.content?.[0]?.text ?? "{}";
  const tokens =
    (data.usage?.input_tokens ?? 0) + (data.usage?.output_tokens ?? 0);

  // Extract JSON from response (handle markdown code blocks)
  const jsonMatch = text.match(/```json?\s*([\s\S]*?)```/) ?? [null, text];
  const parsed = JSON.parse(jsonMatch[1]!.trim());

  return { result: parsed, tokens };
}

function flattenConversation(rawJson: Record<string, unknown>): string {
  const parsed = rawJson.parsed as Record<string, unknown> | undefined;
  if (parsed?.turns && Array.isArray(parsed.turns)) {
    return (parsed.turns as Array<{ role: string; content: string }>)
      .map((t) => `${t.role}: ${t.content}`)
      .join("\n\n");
  }
  // Fallback: stringify raw
  const raw = rawJson.raw;
  return typeof raw === "string" ? raw : JSON.stringify(raw);
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "POST required" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY);

  try {
    const body = await req.json().catch(() => ({}));
    const batchSize = Math.min(body.batch_size ?? MAX_BATCH_SIZE, 10);

    // Fetch pending records
    const { data: pendingRows, error: fetchErr } = await supabase
      .from("conv_raw")
      .select("id, raw_json, source_file")
      .eq("status", "pending")
      .order("created_at", { ascending: true })
      .limit(batchSize);

    if (fetchErr) throw new Error(`Fetch error: ${fetchErr.message}`);
    if (!pendingRows || pendingRows.length === 0) {
      return new Response(
        JSON.stringify({ message: "No pending conversations", processed: 0 }),
        { headers: { "Content-Type": "application/json" } },
      );
    }

    const results = [];

    for (const row of pendingRows) {
      // Mark as processing
      await supabase
        .from("conv_raw")
        .update({ status: "processing" })
        .eq("id", row.id);

      try {
        const conversationText = flattenConversation(row.raw_json);
        const { result, tokens } = await callClaude(conversationText);

        // Write extraction result
        const { data: processed, error: insertErr } = await supabase
          .from("conv_processed")
          .insert({
            conv_raw_id: row.id,
            tasks: result.tasks ?? [],
            skills: result.skills ?? [],
            memory_updates: result.memory_updates ?? [],
            n8n_ideas: result.n8n_ideas ?? [],
            supabase_changes: result.supabase_changes ?? [],
            extraction_model: EXTRACTION_MODEL,
            extraction_tokens_used: tokens,
            status: "extracted",
            processed_at: new Date().toISOString(),
          })
          .select("id")
          .single();

        if (insertErr) throw new Error(insertErr.message);

        // Mark raw as processed
        await supabase
          .from("conv_raw")
          .update({ status: "processed" })
          .eq("id", row.id);

        results.push({
          raw_id: row.id,
          processed_id: processed!.id,
          source_file: row.source_file,
          status: "extracted",
          tokens,
          counts: {
            tasks: (result.tasks ?? []).length,
            skills: (result.skills ?? []).length,
            memory_updates: (result.memory_updates ?? []).length,
            n8n_ideas: (result.n8n_ideas ?? []).length,
            supabase_changes: (result.supabase_changes ?? []).length,
          },
        });
      } catch (err) {
        const errorMsg = (err as Error).message;
        await supabase
          .from("conv_raw")
          .update({ status: "error", error_message: errorMsg })
          .eq("id", row.id);

        results.push({
          raw_id: row.id,
          source_file: row.source_file,
          status: "error",
          error: errorMsg,
        });
      }
    }

    return new Response(
      JSON.stringify({ processed: results.length, results }),
      { headers: { "Content-Type": "application/json" } },
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ error: (err as Error).message }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }
});
