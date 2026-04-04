import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

interface ConversationTurn {
  role: string;
  content: string;
  timestamp?: string;
  tool_calls?: unknown[];
}

interface ParsedConversation {
  turns: ConversationTurn[];
  metadata: Record<string, unknown>;
  source_format: string;
}

function parseClaudeJsonExport(raw: string): ParsedConversation {
  const data = JSON.parse(raw);

  // Claude JSON export format: array of messages or { chat_messages: [...] }
  const messages = Array.isArray(data)
    ? data
    : data.chat_messages ?? data.messages ?? data.conversation ?? [];

  const turns: ConversationTurn[] = messages.map((msg: Record<string, unknown>) => ({
    role: (msg.role as string) ?? (msg.sender as string) ?? "unknown",
    content: typeof msg.content === "string"
      ? msg.content
      : Array.isArray(msg.content)
        ? (msg.content as Array<Record<string, unknown>>)
            .filter((b) => b.type === "text")
            .map((b) => b.text)
            .join("\n")
        : JSON.stringify(msg.content),
    timestamp: (msg.created_at as string) ?? (msg.timestamp as string) ?? undefined,
    tool_calls: (msg.tool_calls as unknown[]) ?? (msg.tool_use as unknown[]) ?? undefined,
  }));

  return {
    turns,
    metadata: {
      model: data.model ?? data.model_slug ?? null,
      title: data.title ?? data.name ?? null,
      created_at: data.created_at ?? null,
      uuid: data.uuid ?? data.id ?? null,
    },
    source_format: "claude_json",
  };
}

function parseMarkdownTranscript(raw: string): ParsedConversation {
  const turns: ConversationTurn[] = [];
  // Split on common patterns: "Human:", "Assistant:", "User:", "Claude:"
  const pattern = /^(Human|Assistant|User|Claude|System):\s*/gim;
  const parts = raw.split(pattern).filter(Boolean);

  for (let i = 0; i < parts.length - 1; i += 2) {
    const role = parts[i].toLowerCase().replace("claude", "assistant").replace("user", "human");
    const content = parts[i + 1]?.trim() ?? "";
    if (content) {
      turns.push({ role, content });
    }
  }

  return { turns, metadata: {}, source_format: "markdown" };
}

function parsePlainText(raw: string): ParsedConversation {
  // Fallback: treat as a single block of conversation text
  return {
    turns: [{ role: "unknown", content: raw }],
    metadata: {},
    source_format: "plain_text",
  };
}

async function computeHash(content: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(content);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
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
    const contentType = req.headers.get("content-type") ?? "";
    let files: Array<{ name: string; content: string }> = [];

    if (contentType.includes("application/json")) {
      const body = await req.json();
      // Accept: { files: [{ name, content }] } or { name, content } or raw conversation
      if (body.files && Array.isArray(body.files)) {
        files = body.files;
      } else if (body.name && body.content) {
        files = [{ name: body.name, content: body.content }];
      } else {
        // Treat entire body as a single conversation
        files = [{ name: "inline_upload.json", content: JSON.stringify(body) }];
      }
    } else {
      const text = await req.text();
      files = [{ name: "inline_upload.txt", content: text }];
    }

    const results = [];

    for (const file of files) {
      const hash = await computeHash(file.content);

      // Deduplicate by hash
      const { data: existing } = await supabase
        .from("conv_raw")
        .select("id")
        .eq("file_hash", hash)
        .maybeSingle();

      if (existing) {
        results.push({ file: file.name, status: "duplicate", id: existing.id });
        continue;
      }

      // Parse based on content
      let parsed: ParsedConversation;
      try {
        parsed = parseClaudeJsonExport(file.content);
      } catch {
        if (file.content.match(/^(Human|Assistant|User|Claude):/im)) {
          parsed = parseMarkdownTranscript(file.content);
        } else {
          parsed = parsePlainText(file.content);
        }
      }

      const { data, error } = await supabase
        .from("conv_raw")
        .insert({
          source_file: file.name,
          raw_json: { raw: file.content, parsed },
          status: "pending",
          file_hash: hash,
          ingested_at: new Date().toISOString(),
        })
        .select("id")
        .single();

      if (error) {
        results.push({ file: file.name, status: "error", error: error.message });
      } else {
        results.push({ file: file.name, status: "ingested", id: data.id });
      }
    }

    return new Response(JSON.stringify({ results, count: results.length }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (err) {
    return new Response(
      JSON.stringify({ error: (err as Error).message }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }
});
