# BERMCOIN-APX-MSC-00008 — Support Ticket Pipeline

**Pattern:** Public form → Supabase table → n8n poll → Telegram ops alert → email confirmation
**Reuse for:** Any Bermech product needing support without external helpdesk SaaS

## Flow
1. Contact form submits to support_tickets (RLS: public insert, user can read own)
2. n8n WF-06 polls every 5 min for new open tickets
3. Forwards to Telegram ops chat (no PII beyond email — GDPR)
4. Sends confirmation email to member via Brevo
5. Updates ticket status to in_progress
6. Resolution tracked manually — update status to resolved/closed

## Tables
- support_tickets (user_id, email, category, subject, body, status, priority, created_at)
- feedback (user_id, type, score, comment, metadata, created_at)

## SLA: 24h response target (tracked by created_at vs first reply)
