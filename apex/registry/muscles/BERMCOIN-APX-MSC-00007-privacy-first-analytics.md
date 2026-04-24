# BERMCOIN-APX-MSC-00007 — Privacy-First Analytics

**Pattern:** Self-hosted event tracking with rate limiting, no cookies, no PII, GDPR compliant
**Reuse for:** Any Bermech product needing analytics without third-party trackers

## Flow
1. Frontend generates random session_id per browser session (sessionStorage, not persistent)
2. Events POST to edge function: {page, action, session_id, metadata}
3. Edge function: rate-limits by IP hash (60/min), inserts to page_events table
4. IP is hashed with server secret — never stored raw
5. No cookies set. No fingerprinting. No cross-site tracking.

## Events tracked
- page_view, email_gate_passed, waitlist_signup, watch_created, calculator_used
- dashboard_view, nps_submitted, feature_request, support_ticket_created

## Tables
- page_events (session_id, page, action, metadata, created_at)
- rate_limit_log (ip_hash, endpoint, count, window_start)

## Edge Function: collect-event (no JWT — public endpoint, rate-limited)
