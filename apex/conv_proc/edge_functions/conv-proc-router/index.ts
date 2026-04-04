import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const N8N_BASE = "http://192.168.50.246:5678/webhook";
const TELEGRAM_BOT_TOKEN = Deno.env.get("TELEGRAM_BOT_TOKEN") ?? "";
const TELEGRAM_CHAT_ID = Deno.env.get("TELEGRAM_CHAT_ID") ?? "";

interface RoutingResult {
  route_type: string;
  destination: string;
  status: string;
  response?: unknown;
  error?: string;
}

async function postWebhook(
  url: string,
  payload: unknown,
): Promise<{ ok: boolean; body: unknown }> {
  try {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const body = await res.json().catch(() => res.statusText);
    return { ok: res.ok, body };
  } catch (err) {
    return { ok: false, body: (err as Error).message };
  }
}

async function sendTelegram(message: string): Promise<void> {
  if (!TELEGRAM_BOT_TOKEN || !TELEGRAM_CHAT_ID) return;
  await fetch(
    `https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: TELEGRAM_CHAT_ID,
        text: message,
        parse_mode: "Markdown",
      }),
    },
  );
}

async function routeTasks(
  supabase: ReturnType<typeof createClient>,
  processedId: string,
  tasks: Array<Record<string, unknown>>,
): Promise<RoutingResult[]> {
  const results: RoutingResult[] = [];
  if (tasks.length === 0) return results;

  const { ok, body } = await postWebhook(`${N8N_BASE}/apex-task-intake`, {
    source: "conv-proc",
    processed_id: processedId,
    tasks,
  });

  const result: RoutingResult = {
    route_type: "tasks",
    destination: "n8n/apex-task-intake",
    status: ok ? "routed" : "failed",
    response: body,
  };
  if (!ok) result.error = String(body);

  await supabase.from("conv_routing_log").insert({
    conv_processed_id: processedId,
    route_type: "tasks",
    payload: tasks,
    destination: "n8n/apex-task-intake",
    status: result.status,
    response: body,
    error_message: result.error ?? null,
    routed_at: new Date().toISOString(),
  });

  results.push(result);
  return results;
}

async function routeSkills(
  supabase: ReturnType<typeof createClient>,
  processedId: string,
  skills: Array<Record<string, unknown>>,
): Promise<RoutingResult[]> {
  const results: RoutingResult[] = [];
  if (skills.length === 0) return results;

  // Store skills as records in Supabase for later file generation
  for (const skill of skills) {
    const { ok, body } = await postWebhook(`${N8N_BASE}/apex-skill-register`, {
      source: "conv-proc",
      processed_id: processedId,
      skill,
    });

    const result: RoutingResult = {
      route_type: "skill",
      destination: "n8n/apex-skill-register",
      status: ok ? "routed" : "failed",
      response: body,
    };
    if (!ok) result.error = String(body);

    await supabase.from("conv_routing_log").insert({
      conv_processed_id: processedId,
      route_type: "skill",
      payload: skill,
      destination: "n8n/apex-skill-register",
      status: result.status,
      response: body,
      error_message: result.error ?? null,
      routed_at: new Date().toISOString(),
    });

    results.push(result);
  }
  return results;
}

async function routeMemoryUpdates(
  supabase: ReturnType<typeof createClient>,
  processedId: string,
  updates: Array<Record<string, unknown>>,
): Promise<RoutingResult[]> {
  const results: RoutingResult[] = [];
  if (updates.length === 0) return results;

  const { ok, body } = await postWebhook(`${N8N_BASE}/apex-memory-update`, {
    source: "conv-proc",
    processed_id: processedId,
    memory_updates: updates,
  });

  const result: RoutingResult = {
    route_type: "memory_updates",
    destination: "n8n/apex-memory-update",
    status: ok ? "routed" : "failed",
    response: body,
  };
  if (!ok) result.error = String(body);

  await supabase.from("conv_routing_log").insert({
    conv_processed_id: processedId,
    route_type: "memory_updates",
    payload: updates,
    destination: "n8n/apex-memory-update",
    status: result.status,
    response: body,
    error_message: result.error ?? null,
    routed_at: new Date().toISOString(),
  });

  results.push(result);
  return results;
}

async function routeN8nIdeas(
  supabase: ReturnType<typeof createClient>,
  processedId: string,
  ideas: Array<Record<string, unknown>>,
): Promise<RoutingResult[]> {
  const results: RoutingResult[] = [];
  if (ideas.length === 0) return results;

  for (const idea of ideas) {
    const { ok, body } = await postWebhook(`${N8N_BASE}/apex-n8n-idea`, {
      source: "conv-proc",
      processed_id: processedId,
      idea,
    });

    const result: RoutingResult = {
      route_type: "n8n_idea",
      destination: "n8n/apex-n8n-idea",
      status: ok ? "routed" : "failed",
      response: body,
    };
    if (!ok) result.error = String(body);

    await supabase.from("conv_routing_log").insert({
      conv_processed_id: processedId,
      route_type: "n8n_idea",
      payload: idea,
      destination: "n8n/apex-n8n-idea",
      status: result.status,
      response: body,
      error_message: result.error ?? null,
      routed_at: new Date().toISOString(),
    });

    results.push(result);
  }
  return results;
}

async function routeSupabaseChanges(
  supabase: ReturnType<typeof createClient>,
  processedId: string,
  changes: Array<Record<string, unknown>>,
): Promise<RoutingResult[]> {
  const results: RoutingResult[] = [];
  if (changes.length === 0) return results;

  // Log for human review - don't auto-apply DDL
  for (const change of changes) {
    await supabase.from("conv_routing_log").insert({
      conv_processed_id: processedId,
      route_type: "supabase_change",
      payload: change,
      destination: "review_queue",
      status: "queued_for_review",
      routed_at: new Date().toISOString(),
    });

    results.push({
      route_type: "supabase_change",
      destination: "review_queue",
      status: "queued_for_review",
    });
  }
  return results;
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
    const batchSize = Math.min(body.batch_size ?? 5, 20);

    // Fetch extracted records pending routing
    const { data: rows, error: fetchErr } = await supabase
      .from("conv_processed")
      .select("id, tasks, skills, memory_updates, n8n_ideas, supabase_changes")
      .eq("status", "extracted")
      .order("created_at", { ascending: true })
      .limit(batchSize);

    if (fetchErr) throw new Error(fetchErr.message);
    if (!rows || rows.length === 0) {
      return new Response(
        JSON.stringify({ message: "No extracted records to route", routed: 0 }),
        { headers: { "Content-Type": "application/json" } },
      );
    }

    const batchResults = [];
    let totalTasks = 0;
    let totalSkills = 0;

    for (const row of rows) {
      const routingResults: RoutingResult[] = [];

      routingResults.push(
        ...(await routeTasks(supabase, row.id, row.tasks ?? [])),
      );
      routingResults.push(
        ...(await routeSkills(supabase, row.id, row.skills ?? [])),
      );
      routingResults.push(
        ...(await routeMemoryUpdates(supabase, row.id, row.memory_updates ?? [])),
      );
      routingResults.push(
        ...(await routeN8nIdeas(supabase, row.id, row.n8n_ideas ?? [])),
      );
      routingResults.push(
        ...(await routeSupabaseChanges(supabase, row.id, row.supabase_changes ?? [])),
      );

      totalTasks += (row.tasks ?? []).length;
      totalSkills += (row.skills ?? []).length;

      // Update status
      const allRouted = routingResults.every(
        (r) => r.status === "routed" || r.status === "queued_for_review",
      );
      await supabase
        .from("conv_processed")
        .update({ status: allRouted ? "routed" : "partially_routed" })
        .eq("id", row.id);

      batchResults.push({
        processed_id: row.id,
        routing: routingResults,
        status: allRouted ? "routed" : "partially_routed",
      });
    }

    // Send Telegram notification
    await sendTelegram(
      `*CONV-PROC batch complete*\n` +
        `Conversations routed: ${rows.length}\n` +
        `Tasks: ${totalTasks} | Skills: ${totalSkills}`,
    );

    return new Response(
      JSON.stringify({ routed: batchResults.length, results: batchResults }),
      { headers: { "Content-Type": "application/json" } },
    );
  } catch (err) {
    return new Response(
      JSON.stringify({ error: (err as Error).message }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }
});
