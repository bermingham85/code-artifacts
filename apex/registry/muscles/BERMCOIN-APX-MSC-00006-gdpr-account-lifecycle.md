# BERMCOIN-APX-MSC-00006 — GDPR Account Lifecycle

**Pattern:** Consent tracking + data export + account deletion with 30-day grace period
**Reuse for:** Any Bermech product handling EU personal data

## Flow
1. On signup: record consent_log entries (privacy_policy, terms_of_service, data_processing) with version
2. Data export: Supabase Edge Function gathers all user data across tables, returns JSON (GDPR Article 20)
3. Account deletion: soft-delete with 30-day grace period, pause all services, anonymise after grace expires
4. Consent revocation: user can revoke marketing consent independently of service consent

## Tables
- consent_log (user_id, consent_type, version, granted, granted_at, revoked_at)
- deletion_requests (user_id, status, grace_expires_at, completed_at, anonymised_data)
- data_export_log (user_id, format, requested_at, completed_at, file_size_bytes)

## Edge Functions
- delete-account (JWT required) — creates deletion request, pauses watches, marks cancelled
- export-data (JWT required) — gathers all user data, returns downloadable JSON
- stripe-portal (JWT required) — creates Stripe Customer Portal session

## Compliance
- GDPR Articles 12-23 (Irish DPC jurisdiction)
- 30-day grace period before permanent deletion
- Anonymisation not deletion — preserves aggregate analytics
