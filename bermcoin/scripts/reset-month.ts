#!/usr/bin/env npx ts-node
/**
 * BERMCOIN-BCK-SCR-00003 - Manual Monthly Reset
 * Resets nudge counters and reactivates paused watches.
 */

const SUPABASE_URL = process.env.SUPABASE_URL!;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!;
if (!SUPABASE_URL || !SERVICE_KEY) { console.error("Missing env vars"); process.exit(1); }

const headers: Record<string, string> = {
  "Content-Type": "application/json",
  apikey: SERVICE_KEY,
  Authorization: \,
  Prefer: "return=representation",
};

async function main() {
  console.log("=== Bermcoin Monthly Reset ===
");

  const r1 = await fetch(\, {
    method: "PATCH", headers,
    body: JSON.stringify({ nudges_this_month: 0 })
  });
  console.log("Watch counters reset:", r1.ok ? "OK" : r1.status);

  const r2 = await fetch(\, {
    method: "PATCH", headers,
    body: JSON.stringify({ status: "looking" })
  });
  const reactivated = r2.ok ? (await r2.json()).length : 0;
  console.log("Watches reactivated:", reactivated);

  const r3 = await fetch(\, {
    method: "PATCH", headers: { ...headers, Prefer: "return=minimal" },
    body: JSON.stringify({ nudges_this_month: 0, last_nudge_reset: new Date().toISOString() })
  });
  console.log("Member counters reset:", r3.ok ? "OK" : r3.status);

  await fetch(\, {
    method: "POST", headers: { ...headers, Prefer: "return=minimal" },
    body: JSON.stringify({
      config_key: "monthly_reset",
      new_value: "manual_reset_" + new Date().toISOString(),
      changed_by: "manual_script"
    })
  });
  console.log("
Audit logged. Reset complete.");
}

main().catch(console.error);
