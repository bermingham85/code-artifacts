# BERMCOIN-APX-MSC-00002 — Rate Fetch 3-Source Fallback

**Pattern:** Primary API → Backup API → Cache → Stale flag → Ops alert
**Reuse for:** Any data-dependent monitoring product

## Flow
1. Try primary source (e.g., Frankfurter) with 8s timeout
2. If failed → try fallback 1 (e.g., open.er-api.com)
3. If failed → try fallback 2 (e.g., exchangerate-api.com)
4. If all failed → read from cache table, mark `is_stale=true, stale_since=NOW()`
5. If stale > 4 hours → trigger self-healing workflow + alert ops
6. Always: upsert cache, insert history record

## Stale Data Rules
- Stale data can still be shown to members with disclaimer
- Stale > 4h triggers ops alert
- Stale > 24h stops all nudges for affected pairs
