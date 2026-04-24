# BERMCOIN-APX-MSC-00005 — Monthly Limit Reset Cron

**Pattern:** Reset usage counters → reactivate paused items → notify members
**Reuse for:** Any subscription product with monthly usage limits

## Flow (runs 1st of month at midnight)
1. UPDATE usage table SET counter = 0
2. UPDATE items SET status = 'active' WHERE status = 'paused_limit'
3. UPDATE members SET monthly_counter = 0
4. Query reactivated members
5. Notify each via preferred channels: "Your [feature] is back"
6. Insert audit_log for reset event
7. Notify ops with count

## Trigger Options
- n8n Cron: `0 0 1 * *`
- Supabase pg_cron extension
- Supabase trigger on member UPDATE (auto-resets if month boundary crossed)
