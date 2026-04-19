# BERMCOIN  Exchange Rate Notification Service

**Owner:** Bermech Limited, Dublin, Ireland
**Domain:** bermcoin.money / bermcoin.com
**Pronunciation:** sheh-GOO (from Portuguese "chegou"  it arrived)
**Session:** BERMCOIN-BCK-SES-00001
**Date:** 2026-04-11

## What It Does

Watches exchange rates. Sends one instant message the moment a member's target rate arrives.
Information service only. Not regulated. Never handles money.

## Plans

| Plan | Watches | Routes | Nudges/mo | Channels | Price |
|------|---------|--------|-----------|----------|-------|
| Free | 1 | 1 | 3 | Telegram, Email | Free |
| Standard | 3 | 3 | 10 | Telegram, Email | EUR 2/mo or EUR 20/yr |
| Pro | 10 | 10 | 30 | Telegram, Email, WhatsApp | EUR 10/mo or EUR 75/yr |

## Architecture

- **Database:** Supabase (project ylcepmvbjjnwmzvevxid)
- **Workflows:** n8n on QNAP NAS (192.168.50.246:5678)
- **Payments:** Stripe (test mode)
- **Rate Source:** ECB via Frankfurter API (primary)
- **Fallbacks:** open.er-api.com, exchangerate-api.com, cache
- **Notifications:** Telegram (@Brianbrainboxbot), Brevo (email), Meta Cloud API (WhatsApp, Pro only)

## Tables

members, rate_watches, rates_history, rate_cache, config, audit_log, nudge_log, affiliate_conversions, churn_log

## Workflows

WF-01 Onboarding, WF-02 Rate Watchdog, WF-03 Monthly Reset, WF-04 Offboarding, WF-05 Self-Healing
WF-06 Support Router, WF-07 Feedback Digest, WF-08 Weekly Report, WF-09 Growth Metrics

## Currency Pairs

EUR/BRL, EUR/NGN, EUR/INR, EUR/MXN, EUR/UAH, GBP/NGN, GBP/INR, USD/MXN, EUR/PLN, EUR/GBP
