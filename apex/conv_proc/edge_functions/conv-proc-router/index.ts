import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "jsr:@supabase/supabase-js@2";

const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
const N8N_BASE = "http://192.168.50.246:5678/webhook";
const TELEGRAM_BOT_TOKEN = Deno.env.get("TELEGRAM_BOT_TOKEN") ?? "";
const TELEGRAM_CHAT_ID = Deno.env.get("TELEGRAM_CHAT_ID") ?? "";

// Default project_id for direct inserts (APEX Infrastructure project)
const DEFAULT_PROJECT_ID = "eaf643c4-073f-40b2-a23e-7a76d043d9cd";

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

// Map extracted memory types to valid agent_memories values
function mapMemoryType(raw: string): string {
  const t = (raw ?? "").toLowerCase();
  if (t === "user" || t === "personal") return "preference";
  if (t === "project") return "context";
  if (t === "feedback") return "pattern";
  if (t === "reference" || t === "system") return "context";
  return "context";
}

function mapMemoryCategory(raw: string): string {
  const t = (raw ?? "").toLowerCase();
  if (t === "user" || t === "personal") return "personal";
  if (t === "project" || t === "feedback") return "business";
  if (t === "reference" || t === "system") return "technical";
  return "workflow";
}

async function directInsertTasks(
  supabase: ReturnType<typeof createClient>,
  tasks: Array<Record<string, unknown>>,
): Promise<number> {
  let inserted = 0;
  for (const task of tasks) {
    const priority = (task.priority as string ?? "medium").toLowerCase();
    const validPriority = ["critical", "high", "medium", "low"].includes(priority)
      ? priority : "medium";
    const { error } = await supabase.from("agent_tasks").insert({
      title: task.title ?? "Untitled task",
      description: task.description ?? "",
      project_id: DEFAULT_PROJECT_ID,
      priority: validPriority,
      status: "pending",
      notes: `owner: ${task.owner ?? "unassigned"} | project: ${task.project ?? "APEX"} | source: conv-proc`,
    });
    if (!error) inserted++;
  }
  return inserted;
}

async function directInsertMemories(
  supabase: ReturnType<typeof createClient>,
  updates: Array<Record<string, unknown>>,
): Promise<number> {
  let inserted = 0;
  for (const mem of updates) {
    const rawType = (mem.type as string) ?? "";
    const { error } = await supabase.from("agent_memories").insert({
      type: mapMemoryType(rawType),
      category: mapMemoryCategory(rawType),
      content: `${mem.name ?? ""}: ${mem.content ?? ""}`.trim(),
      source: "derived",
      confidence: "medium",
      agent_source: "conv-proc-router",
    });
    if (!error) inserted++;
  }
  return inserted;
}

async function routeTasks(
  supabase: ReturnType<typeof createClient>,
  processedId: string,
  tasks: Array<Record<string, unknown>>,
): Promise<RoutingResult[]> {
  const results: RoutingResult[] = [];
  if (tasks.length === 0) return results;

  // Try n8n first
  const { ok, body } = await postWebhook(`${N8N_BASE}/apex-task-intake`, {
    source: "conv-proc",
    processed_id: processedId,
    tasks,
  });

  let finalStatus: string;
  let destination: string;

  if (ok) {
    finalStatus = "sent";
    destination = "n8n/apex-task-intake";
  } else {
    // Fallback: direct insert into agent_tasks
    const inserted = await directInsertTasks(supabase, tasks);
    finalStatus = "sent";
    destination = `supabase/agent_tasks (direct, ${inserted}/${tasks.length})`;
  }

  await supabase.from("conv_routing_log").insert({
    conv_processed_id: processedId,
    route_type: "task",
    payload: tasks,
    destination,
    status: finalStatus,
    response: body ?? { direct_insert: true },
    error_message: !ok ? `n8n unavailable, used direct insert` : null,
    routed_at: new Date().toISOString(),
  });

  results.push({ route_type: "task", destination, status: finalStatus });
  return results;
}

async function routeSkills(
  supabase: ReturnType<typeof createClient>,
  processedId: string,
  skills: Array<Record<string, unknown>>,
): Promise<RoutingResult[]> {
  const results: RoutingResult[] = [];
  if (skills.length === 0) return results;

  for (const skill of skills) {
    // Try n8n first
    const { ok, body } = await postWebhook(`${N8N_BASE}/apex-skill-register`, {
      source: "conv-proc",
      processed_id: processedId,
      skill,
    });

    // Skills always log to routing_log (no separate skills table yet)
    const destination = ok ? "n8n/apex-skill-register" : "conv_routing_log (stored)";

    await supabase.from("conv_routing_log").insert({
      conv_processed_id: processedId,
      route_type: "skill",
      payload: skill,
      destination,
      status: "sent",
      response: body ?? { stored_in_log: true },
      error_message: !ok ? "n8n unavailable, skill stored in routing log" : null,
      routed_at: new Date().toISOString(),
    });

    results.push({ route_type: "skill", destination, status: "sent" });
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

  // Try n8n first
  const { ok, body } = await postWebhook(`${N8N_BASE}/apex-memory-update`, {
    source: "conv-proc",
    processed_id: processedId,
    memory_updates: updates,
  });

  let destination: string;

  if (ok) {
    destination = "n8n/apex-memory-update";
  } else {
    // Fallback: direct insert into agent_memories
    const inserted = await directInsertMemories(supabase, updates);
    destination = `supabase/agent_memories (direct, ${inserted}/${updates.length})`;
  }

  await supabase.from("conv_routing_log").insert({
    conv_processed_id: processedId,
    route_type: "memory",
    payload: updates,
    destination,
    status: "sent",
    response: body ?? { direct_insert: true },
    error_message: !ok ? "n8n unavailable, used direct insert" : null,
    routed_at: new Date().toISOString(),
  });

  results.push({ route_type: "memory", destination, status: "sent" });
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
    // Try n8n, fall back to storing in routing log
    const { ok, body } = await postWebhook(`${N8N_BASE}/apex-n8n-idea`, {
      source: "conv-proc",
      processed_id: processedId,
      idea,
    });

    const destination = ok ? "n8n/apex-n8n-idea" : "conv_routing_log (stored)";

    await supabase.from("conv_routing_log").insert({
      conv_processed_id: processedId,
      route_type: "n8n_idea",
      payload: idea,
      destination,
      status: "sent",
      response: body ?? { stored_in_log: true },
      error_message: !ok ? "n8n unavailable, idea stored in routing log" : null,
      routed_at: new Date().toISOString(),
    });

    results.push({ route_type: "n8n_idea", destination, status: "sent" });
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

      // Update status — all routes now succeed via fallback
      const allRouted = routingResults.every(
        (r) => r.status === "sent" || r.status === "queued_for_review",
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
