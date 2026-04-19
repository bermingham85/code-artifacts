# BERMCOIN Build Log
## Date: 2026-04-11
## Work Order: WO-BERMCOIN-BUILD
## Branch: bermcoin-full-build
## Operator: APEX Factory (Claude Opus 4.6)

### Phase Summary

| Phase | Description | Status |
|-------|-------------|--------|
| 1 | Supabase Schema (10 migrations) | COMPLETE |
| 2 | RLS Policies (6 policies, 7 tables) | COMPLETE |
| 3 | Auth Triggers (handle_new_auth_user, auto_reset_nudges) | COMPLETE |
| 4 | Stripe Products (4 price IDs in config) | COMPLETE |
| 5 | n8n Workflows (9 active) | COMPLETE |
| 6 | 90-Day Rate Backfill (7 pairs, 644 rows) | COMPLETE |
| 7 | Frontend Pages (landing, login, dashboard) | COMPLETE |
| 8 | ENV + Push (.env.example, BERMCOIN-SPEC.md) | COMPLETE |
| 9 | Smoke Tests (13/13 PASS) | COMPLETE |
| 10 | APEX Muscles (5 registered on QNAP) | COMPLETE |
| 11 | Document Register (33 entries on QNAP) | COMPLETE |
| 12 | Close-Out (PR, build log, final report) | COMPLETE |

### Smoke Test Results

| # | Test | Result |
|---|------|--------|
| 01 | Members table exists | PASS |
| 02 | Config seeds present (28 keys) | PASS |
| 03 | Watch insert with FK | PASS |
| 04 | RLS policies (6 on 6 tables) | PASS |
| 05 | Rates history row count (644) | PASS |
| 06 | Rate cache upsert | PASS |
| 07 | Rate watches columns | PASS |
| 08 | Fresh cache entry | PASS |
| 09 | Cross-rate math | PASS |
| 10 | n8n workflows (9 active) | PASS |
| 11 | Stripe price IDs in config (4+2) | PASS |
| 12 | Auth triggers (2 functions) | PASS |
| 13 | EUR/BRL 90-day history (92 rows) | PASS |

### Known Gaps

1. EUR/NGN, EUR/UAH, GBP/NGN - ECB does not support these currencies
2. TELEGRAM_BOT_TOKEN, SUPABASE_SERVICE_ROLE_KEY, BREVO_API_KEY - empty in .env (manual setup required)
3. Rate cache not yet populated by live cron (WF-02 needs env vars to run)

### Architecture

- **Database**: Supabase (ylcepmvbjjnwmzvevxid)
- **Workflows**: n8n on QNAP NAS (192.168.50.246:5678)
- **Rate Source**: Frankfurter API (ECB) with 3-source fallback
- **Auth**: Magic link (no passwords)
- **Payments**: Stripe Checkout (test mode)
- **Notifications**: Telegram, Email (Brevo), WhatsApp
- **Compliance**: Irish GDPR, audit_log table
