# BERMCOIN-APX-MSC-00003 — Multichannel Member Dispatch

**Pattern:** Read member channels array → dispatch to Telegram / Email / WhatsApp
**Reuse for:** Any multi-channel Bermech notification system

## Flow
1. Read member `preferred_channels` array
2. For each channel in array:
   - **telegram**: Send via Telegram Bot API (no affiliate links)
   - **email**: Send via Brevo transactional API (affiliate links OK, must include unsubscribe + legal)
   - **whatsapp**: Send via Meta Cloud API utility template (Pro only, no affiliate links)
3. Log which channels fired in nudge_log

## Channel Rules
- Telegram: no affiliate links, no marketing
- Email: affiliate links OK, must include disclaimer + unsubscribe
- WhatsApp: utility template only (not marketing), no affiliate links, Pro plan only
- Always include "Not financial advice" and "Verify before sending"
