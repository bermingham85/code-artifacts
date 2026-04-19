#!/usr/bin/env npx ts-node
/**
 * BERMCOIN-BCK-SCR-00001 - Rate History Backfill
 * Fetches 90 days of ECB rates for 10 currency pairs via Frankfurter API.
 * Interpolates missing weekend/holiday dates from adjacent business days.
 */

const SUPABASE_URL = process.env.SUPABASE_URL!;
const SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY!;
if (!SUPABASE_URL || !SERVICE_KEY) { console.error("Missing env vars"); process.exit(1); }

const headers: Record<string, string> = {
  "Content-Type": "application/json",
  apikey: SERVICE_KEY,
  Authorization: `Bearer ${SERVICE_KEY}`,
  Prefer: "resolution=ignore-duplicates",
};

const PAIRS: [string, string][] = [
  ["EUR","BRL"],["EUR","NGN"],["EUR","INR"],["EUR","MXN"],["EUR","UAH"],
  ["GBP","NGN"],["GBP","INR"],["USD","MXN"],["EUR","PLN"],["EUR","GBP"],
];

async function fetchFrankfurter(from: string, to: string, start: string) {
  const url = `https://api.frankfurter.app/${start}..?from=${from}&to=${to}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error(`Frankfurter ${res.status} for ${from}/${to}`);
  const data = await res.json();
  return data.rates || {};
}

function interpolate(rates: {date:string,rate:number}[]) {
  if (rates.length === 0) return [];
  rates.sort((a, b) => a.date.localeCompare(b.date));
  const result: {date:string,rate:number,interpolated:boolean}[] = [];
  const startDate = new Date(rates[0].date);
  const endDate = new Date(rates[rates.length - 1].date);
  const rateMap = new Map(rates.map(r => [r.date, r.rate]));

  for (let d = new Date(startDate); d <= endDate; d.setDate(d.getDate() + 1)) {
    const ds = d.toISOString().slice(0, 10);
    if (rateMap.has(ds)) {
      result.push({ date: ds, rate: rateMap.get(ds)!, interpolated: false });
    } else {
      let before: number | null = null;
      let after: number | null = null;
      for (let i = result.length - 1; i >= 0; i--) {
        if (!result[i].interpolated) { before = result[i].rate; break; }
      }
      for (const r of rates) {
        if (r.date > ds) { after = r.rate; break; }
      }
      const interp = before !== null && after !== null ? (before + after) / 2 : (before || after || 0);
      result.push({ date: ds, rate: interp, interpolated: true });
    }
  }
  return result;
}

async function main() {
  console.log("=== Bermcoin Rate Backfill ===
");
  const d = new Date(); d.setDate(d.getDate() - 90);
  const start = d.toISOString().slice(0, 10);
  let totalInserted = 0, totalInterpolated = 0, failures = 0;

  for (const [from, to] of PAIRS) {
    try {
      console.log(`Fetching ${from}/${to} from ${start}...`);
      let rawRates: {date:string,rate:number}[];

      if (from === "EUR") {
        const data = await fetchFrankfurter("EUR", to, start);
        rawRates = Object.entries(data).map(([date, vals]: any) => ({date, rate: vals[to]})).filter((r: any) => r.rate);
      } else {
        const eurFrom = await fetchFrankfurter("EUR", from, start);
        const eurTo = await fetchFrankfurter("EUR", to, start);
        rawRates = [];
        for (const [date, vals] of Object.entries(eurFrom) as any) {
          const fromRate = vals[from];
          const toRate = (eurTo[date] || {})[to];
          if (fromRate && toRate) rawRates.push({date, rate: toRate / fromRate});
        }
      }

      const filled = interpolate(rawRates);
      totalInterpolated += filled.filter(r => r.interpolated).length;

      const rows = filled.map(r => ({
        from_ccy: from, to_ccy: to, rate: r.rate,
        source: r.interpolated ? "interpolated" : "ecb_historical",
        is_interpolated: r.interpolated,
        recorded_at: r.date + "T12:00:00Z"
      }));

      for (let i = 0; i < rows.length; i += 100) {
        const batch = rows.slice(i, i + 100);
        const res = await fetch(`${SUPABASE_URL}/rest/v1/rates_history`, {
          method: "POST", headers, body: JSON.stringify(batch)
        });
        if (res.ok) totalInserted += batch.length;
        else console.error(`  Insert error: ${res.status}`);
      }
      console.log(`  ${from}/${to}: ${filled.length} rows (${filled.filter(r=>r.interpolated).length} interpolated)`);
    } catch (e: any) {
      console.error(`  FAILED ${from}/${to}: ${e.message}`);
      failures++;
    }
  }
  console.log("
=== Backfill Complete ===");
  console.log(`Total inserted: ${totalInserted}`);
  console.log(`Interpolated: ${totalInterpolated}`);
  console.log(`Failures: ${failures}`);
}

main().catch(console.error);
