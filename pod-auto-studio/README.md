# POD Auto Studio — Build-Ready Package v2 (Codex-gated, human-out-of-loop)
Generated 2026-06-09T23:13:54.318768+00:00 | 61 tasks / 347 microtasks | authority AGEN-GOVN-001 v4.0

## Safety layer (replaces human approval)
- Reviewer/cert authority = Codex (OpenAI gpt-5) via second-opinion skill (scripts/review.py).
- Decision map: PASS proceed/certify/activate; REVISE iterate max2 then re-judge; REJECT hold DRAFT + notify.
- FAIL-CLOSED: no provider or non-PASS => stays DRAFT/uncertified, run blocked, watchdog + Telegram notify. Persona fallback NOT accepted as a cert.
- Telegram @Brianbrainybot = notify-only digest. No human authorisation gate.

## Research protocol (mandatory per task, never skipped)
Rule-0 + Rule-1: Supabase tables -> n8n workflows -> code-artifacts -> prior work/Notion -> open-source/community templates. ADAPT if >=70% match. Log to pod.research_log before building.

## Files
- pod_auto_studio_build_package.json — all 61 tasks, microtasks, tools, muscles, gates, Codex authority, research_step.
- n8n_POD-MICH-MUSC-00017_drop_orchestrator.json — importable skeleton, single-design pipeline, Codex gate before Shopify activate.
- n8n_POD-MICH-MUSC-00018_batch_spawner.json — importable skeleton, weekly/webhook, wave cap 4, fan-out to 00017, Codex batch review.

## Import order
1. Run foundation WO-PODAS-0001..0008 (schema, keys, adapters, brand loader).
2. Import the two skeletons INACTIVE; Rule-0 reconcile node params/creds vs /share/Container/apex-microprompter/standards/SPEC.md.
3. Build muscles 00001-00016 (SPEC->BUILD, each Codex-certified) so the orchestrator's executeCommand adapters resolve.
4. Activate 00017, smoke 1 theme, Codex PASS, then activate 00018 weekly tick.

## Inherited governance (every task)
Governance Block verbatim on every LLM prompt; 12-check Prompt Gate; Doc Control register pre+post; Naming Authority; backup .bak before live edits; read-only-first; wave cap 4 hard; state in Supabase not memory; PRs to main; keys from ENV chain only.
