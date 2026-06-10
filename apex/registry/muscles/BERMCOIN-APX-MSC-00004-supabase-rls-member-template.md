# BERMCOIN-APX-MSC-00004 — Supabase RLS Member Template

**Pattern:** Standard RLS policy set for member-owned data with public read tables
**Reuse for:** Any Supabase-backed member product

## Policies
- **Member-owned tables** (members, rate_watches, nudge_log):
  `FOR ALL USING (auth.uid() = id/user_id)`
- **Public read tables** (rates_history, config, rate_cache):
  `FOR SELECT USING (true)`
- **Service role bypass**: n8n and backend jobs use SUPABASE_SERVICE_ROLE_KEY which bypasses RLS natively

## Enable RLS
All tables must have `ALTER TABLE x ENABLE ROW LEVEL SECURITY` before policies apply.
Tables without policies and with RLS enabled default to DENY ALL for non-service-role.
