# BERMCOIN-APX-MSC-00001 — Stripe-Supabase Magic Link Onboard

**Pattern:** Stripe checkout → Supabase upsert → inviteUserByEmail magic link
**Reuse for:** Any Stripe-gated Bermech product needing passwordless onboarding

## Flow
1. Webhook receives Stripe `checkout.session.completed`
2. Verify Stripe signature (reject 400 if invalid)
3. Extract: email, plan, stripe_customer_id, stripe_subscription_id, affiliate_ref
4. Upsert member into Supabase `members` table (ON CONFLICT email DO UPDATE)
5. Call Supabase Auth `inviteUserByEmail` → sends magic link welcome email
6. If affiliate_ref exists → insert `affiliate_conversions`
7. Notify ops via Telegram (no PII — GDPR)
8. Error branch → Telegram ops + audit_log

## Environment Variables Required
- STRIPE_WH_CHECKOUT_SECRET
- SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY
- TELEGRAM_BOT_TOKEN, OPS_CHAT_ID

## GDPR Notes
- Never log email to Telegram
- Member can delete account and all data
