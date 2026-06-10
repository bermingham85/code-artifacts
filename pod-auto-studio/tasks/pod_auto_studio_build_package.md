# POD Auto Studio — Build Package (AGEN-GOVN-001 v4.0)
61 tasks / 347 microtasks | project BERM-PODAS | wave cap 4 | approval @Brianbrainybot
_User authorised completion of every task with any required muscle/tool._

## Governance contract (applies to every task)
- **authority**: AGEN-GOVN-001 v4.0 (GOVERNANCE.md). Applies to EVERY task and process. No exceptions.
- **rule_0_audit_before_build**: Check Supabase tables+rowcounts, n8n workflows, GitHub bermingham85/code-artifacts for existing assets; report; build ONLY gaps; never drop populated tables.
- **rule_1_research_first**: Search prior work + open-source/n8n-community/Supabase templates; if existing covers 70%+ ADAPT not rebuild; log build|adapt|reuse decision.
- **rule_2_modular_connected_documented**: n8n webhooks orchestrate, Supabase persists, Notion documents; spec registered before build, completion after; tests prove spec.
- **rule_3_document_control**: Register every artifact via webhook http://192.168.50.246:5678/webhook/log-entry + Notion DB 22674ec0311480a7b76cc22a158c1fd4; name [PROJECT]-[TYPE]-[NAME]-v[VERSION].[EXT].
- **naming_authority**: QNAP:8767 / pipeline-governance SUB-04; muscle execution codes [PROJECT]-[ORIG]-MUSC-[SEQ5].
- **prompt_gate**: Every LLM dispatch: Registry Lookup -> Governance Auditor (12-check C1-C12) -> Peer Advisor if fail -> Register -> Dispatch.
- **governance_block**: Canonical 'GOVERNANCE RULES — APPLY AT ALL TIMES' block prepended verbatim to every LLM prompt at every layer.
- **twelve_check**: C1 gov-block present; C2 JSON-only; C3 token limit; C4 scope bounded; C5 no cross-task deps; C6 required fields; C7 confidence field; C8-C12 full-plan checks.
- **infra_safety**: Backup .bak.YYYY-MM-DD before live config edits; read-only first; infra 24/7.
- **state**: Live state in Supabase (pod.* + microprompter.*); tracking in system, never memory.
- **concurrency**: Wave cap 4 parallel HARD.
- **delivery**: PRs to main only; check docs/DOCUMENT_REGISTER.md before any build.
- **approval**: Human gate via Telegram @Brianbrainybot (BRIAN_BOT_TOKEN); 'Got it' callback; email escalation on no-ack 24h.
- **keys**: Resolve X:\Automations\claudeclaw\.env -> Windows ENV -> QNAP /share/Container/<svc>/.env. Never ask/store/relocate keys.

## Phase map 0–8
- 0: Intake/normalise -> canonical record
- 1: Plan/decompose, assign refs, set wave
- 2: Retrieve context (brand-blocks, registry, content_hash) read-only
- 3: Generate (LLM/image) behind Prompt Gate + Governance Block
- 4: Validate/QC (12-check, vision QC, copyright gate)
- 5: Transform/assemble (mockups, pricing, copy bundle)
- 6: Persist/register (Supabase pod.*, Doc Control, content_hash dedup)
- 7: Dispatch/act (Printify create, Shopify publish, social) post-approval
- 8: Verify/close (acceptance, watchdog heartbeat, mark Done, digest)

## Tasks

### WO-PODAS-0001  (BERM-DDL-PODAS-0001-v1)
Create Supabase pod.* schema (themes, designs, drops, mockups, listings, qc_scores, approvals, social_posts; content_hash dedup)  
type Schema | prio Critical | target gpu-workstation
tools: Supabase MCP
microtasks: Rule-0: list pg_tables + rowcounts; never drop populated | Design DDL (tables, enums, FK, content_hash unique idx) | Apply migration on branch via Supabase MCP | Add RLS + indexes (status, content_hash) | Smoke insert/select then rollback | Doc Control register pre+post; PR to main
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: all tables+RLS+indexes created ; content_hash unique ; status enum present ; migration in code-artifacts

### WO-PODAS-0002  (BERM-DOC-PODAS-0002-v1)
Register PODAS project + all refs in DOCUMENT_REGISTER.md; open Naming Authority entries  
type Governance | prio High | target qnap
deps: WO-PODAS-0001
tools: Naming Authority 8767, Doc Control webhook
microtasks: Define rule/gate logic | Wire into Prompt Gate / audit path | Test pass+fail cases | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: every ref below registered, no duplicates

### WO-PODAS-0003  (BERM-CODE-PODAS-0003-v1)
Verify all API keys (Printify, OpenAI, Replicate, Remove.bg, Cloudinary, Shopify, Google Trends, Telegram) resolve from ENV chain  
type Integration | prio Critical | target gpu-workstation
tools: bash, ENV
microtasks: Rule-1 reuse check | Resolve keys from ENV chain (never prompt) | Adapter w/ JSON contract + retry/error-handler | Smoke live call read-only first | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: all keys resolve; none missing; nothing written to repo/memory

### WO-PODAS-0004  (BERM-WKFL-PODAS-0004-v1)
Import pod-orchestrator n8n shell (schedule + manual webhook) INACTIVE on QNAP n8n 5678  
type Workflow Import | prio High | target qnap
deps: WO-PODAS-0001, WO-PODAS-0003
tools: n8n MCP 5678
microtasks: Rule-0 search existing wf same name | Backup live config .bak.YYYY-MM-DD | Import template INACTIVE | Rewire nodes (storage->Supabase, approval->@Brianbrainybot, brand->brand-blocks) | Validate connections + blind-Postman check | Activate behind flag; Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: imported inactive; .bak taken; connections valid

### WO-PODAS-0005  (BERM-CODE-PODAS-0005-v1)
Refactor printify-service.py -> muscle adapter (create/upload/variants/publish), JSON stdin/stdout  
type Integration | prio High | target gpu-workstation
deps: WO-PODAS-0003
tools: python, Printify API
microtasks: Rule-1 reuse check | Resolve keys from ENV chain (never prompt) | Adapter w/ JSON contract + retry/error-handler | Smoke live call read-only first | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: --InputFile JSON in/out; idempotent on content_hash; smoke passes

### WO-PODAS-0006  (BERM-CODE-PODAS-0006-v1)
Refactor openai-service.py -> image+copy muscle adapter, JSON contract  
type Integration | prio High | target gpu-workstation
deps: WO-PODAS-0003
tools: python, OpenAI/Replicate API
microtasks: Rule-1 reuse check | Resolve keys from ENV chain (never prompt) | Adapter w/ JSON contract + retry/error-handler | Smoke live call read-only first | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: image+text endpoints callable; model configurable; smoke passes

### WO-PODAS-0007  (BERM-CODE-PODAS-0007-v1)
Build brand-conditioning loader from brand-blocks tokens.json (palette/type/voice) for all design+copy prompts  
type Integration | prio High | target gpu-workstation
deps: WO-PODAS-0006
tools: python
microtasks: Rule-1 reuse check | Resolve keys from ENV chain (never prompt) | Adapter w/ JSON contract + retry/error-handler | Smoke live call read-only first | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: tokens injected; per-brand selectable (Mickey Bubbles, Gremlo, BPIG)

### WO-PODAS-0008  (BERM-DOC-PODAS-0008-v1)
Version claude-design-pod-6concepts prompt into Supabase prompts_library (with Governance Block)  
type Docs | prio Medium | target gpu-workstation
deps: WO-PODAS-0001
tools: Supabase MCP
microtasks: Draft doc/runbook/skill | Cross-link refs + kill-switch | Register in Doc Control / context server | Add playbook pathway
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: stored, versioned, is_active, input_variables documented, Governance Block embedded

### WO-PODAS-0009  (BERM-WKFL-PODAS-0009-v1)
Pull n8n 11175 (Trends->GPT4o->SD->VisionQC->Printify); rewire storage->Supabase, approval->Telegram  
type Workflow Import | prio High | target qnap
deps: WO-PODAS-0004
tools: web_fetch, n8n MCP
microtasks: Rule-0 search existing wf same name | Backup live config .bak.YYYY-MM-DD | Import template INACTIVE | Rewire nodes (storage->Supabase, approval->@Brianbrainybot, brand->brand-blocks) | Validate connections + blind-Postman check | Activate behind flag; Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Airtable->Supabase; Slack->@Brianbrainybot; validates

### WO-PODAS-0010  (BERM-WKFL-PODAS-0010-v1)
Pull n8n 11181 (Drive->Vision->Remove.bg->Cloudinary->Shopify draft->social); rewire to brand-blocks+Supabase  
type Workflow Import | prio High | target qnap
deps: WO-PODAS-0004, WO-PODAS-0007
tools: web_fetch, n8n MCP
microtasks: Rule-0 search existing wf same name | Backup live config .bak.YYYY-MM-DD | Import template INACTIVE | Rewire nodes (storage->Supabase, approval->@Brianbrainybot, brand->brand-blocks) | Validate connections + blind-Postman check | Activate behind flag; Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: brand conditioning wired; Shopify draft path verified

### WO-PODAS-0011  (BERM-WKFL-PODAS-0011-v1)
Pull n8n 8848 (brand SEO copy); map Brand Guidelines node -> brand-blocks  
type Workflow Import | prio Medium | target qnap
deps: WO-PODAS-0007
tools: web_fetch, n8n MCP
microtasks: Rule-0 search existing wf same name | Backup live config .bak.YYYY-MM-DD | Import template INACTIVE | Rewire nodes (storage->Supabase, approval->@Brianbrainybot, brand->brand-blocks) | Validate connections + blind-Postman check | Activate behind flag; Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: copy node parameterised by brand; Printify/Printful swap confirmed

### BERM-MICH-MUSC-00001-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC theme_intake: Intake theme/brief or schedule tick -> theme record  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00001
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00001-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY theme_intake  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00001
deps: BERM-MICH-MUSC-00001-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00002-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC trend_scan: Google Trends + marketplace/social signals -> ranked candidate themes  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00002
deps: BERM-MICH-MUSC-00001-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00002-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY trend_scan  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00002
deps: BERM-MICH-MUSC-00002-SPEC
tools: OpenAI/Replicate, python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00003-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC concept_brainstorm: LLM theme -> N brand-conditioned concepts  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00003
deps: BERM-MICH-MUSC-00002-SPEC, WO-PODAS-0008
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00003-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY concept_brainstorm  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00003
deps: BERM-MICH-MUSC-00003-SPEC
tools: OpenAI/Replicate, python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00004-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC brand_conditioner: Inject brand-blocks tokens into prompts  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00004
deps: WO-PODAS-0007
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00004-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY brand_conditioner  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00004
deps: BERM-MICH-MUSC-00004-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00005-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC image_generate: Replicate Flux/SD or openai adapter -> raw design  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00005
deps: BERM-MICH-MUSC-00003-SPEC, BERM-MICH-MUSC-00004-SPEC, WO-PODAS-0006
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00005-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY image_generate  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00005
deps: BERM-MICH-MUSC-00005-SPEC
tools: OpenAI/Replicate, python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00006-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC copyright_risk_check: Vision/LLM IP/trademark risk gate; reject risky  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00006
deps: BERM-MICH-MUSC-00005-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00006-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY copyright_risk_check  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00006
deps: BERM-MICH-MUSC-00006-SPEC
tools: OpenAI/Replicate, python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00007-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC bg_remove_cleanup: Remove.bg/rembg -> transparent print-ready PNG  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00007
deps: BERM-MICH-MUSC-00006-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00007-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY bg_remove_cleanup  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00007
deps: BERM-MICH-MUSC-00007-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00008-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC vision_qc_score: Rate 1-10 quality/printability; gate <7 reject  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00008
deps: BERM-MICH-MUSC-00007-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00008-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY vision_qc_score  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00008
deps: BERM-MICH-MUSC-00008-SPEC
tools: OpenAI/Replicate, python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00009-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC mockup_generate: Cloudinary overlay -> product mockups  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00009
deps: BERM-MICH-MUSC-00008-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00009-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY mockup_generate  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00009
deps: BERM-MICH-MUSC-00009-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00010-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC listing_copywrite: SEO title/desc/tags in brand voice  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00010
deps: BERM-MICH-MUSC-00004-SPEC, BERM-MICH-MUSC-00008-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00010-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY listing_copywrite  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00010
deps: BERM-MICH-MUSC-00010-SPEC
tools: OpenAI/Replicate, python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00011-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC price_calculator: 3x cost rule + premium for high QC -> retail  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00011
deps: BERM-MICH-MUSC-00008-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00011-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY price_calculator  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00011
deps: BERM-MICH-MUSC-00011-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00012-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC printify_product_create: Printify product via adapter (blueprint_id, provider, variants, images)  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00012
deps: WO-PODAS-0005, BERM-MICH-MUSC-00010-SPEC, BERM-MICH-MUSC-00011-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00012-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY printify_product_create  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00012
deps: BERM-MICH-MUSC-00012-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00013-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC shopify_publish_sync: Publish/sync Printify->Shopify (draft/active)  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00013
deps: BERM-MICH-MUSC-00012-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00013-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY shopify_publish_sync  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00013
deps: BERM-MICH-MUSC-00013-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00014-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC approval_gate: Telegram @Brianbrainybot one-tap approve/reject; 24h escalation  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00014
deps: BERM-MICH-MUSC-00013-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00014-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY approval_gate  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00014
deps: BERM-MICH-MUSC-00014-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00015-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC social_promo: Draft IG+Pinterest posts (no person names)  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00015
deps: BERM-MICH-MUSC-00014-SPEC
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00015-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY social_promo  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00015
deps: BERM-MICH-MUSC-00015-SPEC
tools: OpenAI/Replicate, python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00016-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC registry_state: Write pod.* + Doc Control; dedup by content_hash  
type Muscle Spec | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00016
deps: WO-PODAS-0001
tools: APEX Microprompter spec, Naming Authority
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: I/O contract+phases 0-8+content_hash gating defined; registered

### BERM-MICH-MUSC-00016-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+SMOKE+CERTIFY registry_state  
type Muscle Build | prio High | target gpu-workstation | exec BERM-MICH-MUSC-00016
deps: BERM-MICH-MUSC-00016-SPEC
tools: python, Supabase MCP
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: Step-1 smoke passes; certified; live state in Supabase

### BERM-MICH-MUSC-00017-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC drop_orchestrator: chain 00001->00016 single design end-to-end  
type Muscle Spec | prio Critical | target gpu-workstation | exec BERM-MICH-MUSC-00017
deps: BERM-MICH-MUSC-00001-SPEC, BERM-MICH-MUSC-00002-SPEC, BERM-MICH-MUSC-00003-SPEC, BERM-MICH-MUSC-00004-SPEC, BERM-MICH-MUSC-00005-SPEC, BERM-MICH-MUSC-00006-SPEC, BERM-MICH-MUSC-00007-SPEC, BERM-MICH-MUSC-00008-SPEC, BERM-MICH-MUSC-00009-SPEC, BERM-MICH-MUSC-00010-SPEC, BERM-MICH-MUSC-00011-SPEC, BERM-MICH-MUSC-00012-SPEC, BERM-MICH-MUSC-00013-SPEC, BERM-MICH-MUSC-00014-SPEC, BERM-MICH-MUSC-00015-SPEC, BERM-MICH-MUSC-00016-SPEC
tools: APEX Microprompter spec
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: resumable by request_id; QC-reject skip; phases 0-8 mapped

### BERM-MICH-MUSC-00017-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+CERTIFY drop_orchestrator  
type Muscle Build | prio Critical | target qnap | exec BERM-MICH-MUSC-00017
deps: BERM-MICH-MUSC-00017-SPEC, BERM-MICH-MUSC-00001-BUILD, BERM-MICH-MUSC-00002-BUILD, BERM-MICH-MUSC-00003-BUILD, BERM-MICH-MUSC-00004-BUILD, BERM-MICH-MUSC-00005-BUILD, BERM-MICH-MUSC-00006-BUILD, BERM-MICH-MUSC-00007-BUILD, BERM-MICH-MUSC-00008-BUILD, BERM-MICH-MUSC-00009-BUILD, BERM-MICH-MUSC-00010-BUILD, BERM-MICH-MUSC-00011-BUILD, BERM-MICH-MUSC-00012-BUILD, BERM-MICH-MUSC-00013-BUILD, BERM-MICH-MUSC-00014-BUILD, BERM-MICH-MUSC-00015-BUILD, BERM-MICH-MUSC-00016-BUILD
tools: n8n MCP, Supabase MCP
muscles: BERM-MICH-MUSC-00001, BERM-MICH-MUSC-00002, BERM-MICH-MUSC-00003, BERM-MICH-MUSC-00004, BERM-MICH-MUSC-00005, BERM-MICH-MUSC-00006, BERM-MICH-MUSC-00007, BERM-MICH-MUSC-00008, BERM-MICH-MUSC-00009, BERM-MICH-MUSC-00010, BERM-MICH-MUSC-00011, BERM-MICH-MUSC-00012, BERM-MICH-MUSC-00013, BERM-MICH-MUSC-00014, BERM-MICH-MUSC-00015, BERM-MICH-MUSC-00016
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: one theme produces one live draft listing fully automated; approval honoured

### BERM-MICH-MUSC-00018-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC batch_spawner META-MUSCLE: theme list/tick -> spawn M orchestrator runs, fan-out/fan-in, wave cap 4, dedup, full Supabase tracking  
type Muscle Spec | prio Critical | target gpu-workstation | exec BERM-MICH-MUSC-00018
deps: BERM-MICH-MUSC-00017-SPEC
tools: pipeline-governance master orchestrator template, APEX Microprompter spec
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: fan-out/fan-in + wave cap 4 + per-run tracking + self-heal defined

### BERM-MICH-MUSC-00018-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD+CERTIFY batch_spawner (spawns + completes ALL POD work autonomously)  
type Muscle Build | prio Critical | target qnap | exec BERM-MICH-MUSC-00018
deps: BERM-MICH-MUSC-00018-SPEC, BERM-MICH-MUSC-00017-BUILD
tools: n8n MCP, Supabase MCP, Telegram
muscles: BERM-MICH-MUSC-00017
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: weekly tick produces full drop set; wave cap 4 enforced; one Telegram digest for batch approval; watchdog covers

### WO-PODAS-0050  (BERM-CODE-PODAS-0050-v1)
Connect AutoDS account+API; map to Shopify  
type Integration | prio Medium | target gpu-workstation
deps: WO-PODAS-0003
tools: AutoDS API
microtasks: Rule-1 reuse check | Resolve keys from ENV chain (never prompt) | Adapter w/ JSON contract + retry/error-handler | Smoke live call read-only first | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: auth ok; store linked

### BERM-MICH-MUSC-00019-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC ds_product_finder: Pull AutoDS winning candidates by criteria  
type Muscle Spec | prio Medium | target gpu-workstation | exec BERM-MICH-MUSC-00019
deps: WO-PODAS-0050
tools: APEX Microprompter spec
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: contract+phases defined

### BERM-MICH-MUSC-00019-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD ds_product_finder  
type Muscle Build | prio Medium | target gpu-workstation | exec BERM-MICH-MUSC-00019
deps: BERM-MICH-MUSC-00019-SPEC
tools: python, AutoDS API
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify | Prompt Gate 12-check before any LLM dispatch | Prepend Governance Block verbatim
acceptance: smoke passes; certified

### BERM-MICH-MUSC-00020-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC ds_score_filter: Score $30-80, sell>=3x, rating, saturation; gate  
type Muscle Spec | prio Medium | target gpu-workstation | exec BERM-MICH-MUSC-00020
deps: BERM-MICH-MUSC-00019-SPEC
tools: APEX Microprompter spec
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: contract+phases defined

### BERM-MICH-MUSC-00020-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD ds_score_filter  
type Muscle Build | prio Medium | target gpu-workstation | exec BERM-MICH-MUSC-00020
deps: BERM-MICH-MUSC-00020-SPEC
tools: python, AutoDS API
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: smoke passes; certified

### BERM-MICH-MUSC-00021-SPEC  (BERM-SPEC-PODAS-SPEC-v1)
SPEC ds_import_list: Import approved -> Shopify draft + auto-fulfilment  
type Muscle Spec | prio Medium | target gpu-workstation | exec BERM-MICH-MUSC-00021
deps: BERM-MICH-MUSC-00020-SPEC, BERM-MICH-MUSC-00014-SPEC
tools: APEX Microprompter spec
microtasks: Rule-1 reuse search; log build|adapt|reuse | Define stdin->stdout JSON contract | Map micro-steps to phases 0-8 | Define content_hash gating + idempotency | Embed Governance Block + token limit | Write SPEC to standards/; Naming Authority + Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: contract+phases defined

### BERM-MICH-MUSC-00021-BUILD  (BERM-CODE-PODAS-BUILD-v1)
BUILD ds_import_list  
type Muscle Build | prio Medium | target gpu-workstation | exec BERM-MICH-MUSC-00021
deps: BERM-MICH-MUSC-00021-SPEC
tools: python, AutoDS API
microtasks: Pull SPEC; confirm contract | Implement adapter (JSON in/out, error-handler) | If LLM: wire Prompt Gate (registry->auditor 12-check->register->dispatch) | Step-1 atomic smoke test | Foreman/indexer certify | Write Supabase live state; Doc Control completion register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: smoke passes; certified

### WO-PODAS-0060  (BERM-DOC-PODAS-0060-v1)
Post Make-MCP-connect: list scenarios, export any POD blueprints, diff vs 11175/11181, keep better  
type Research | prio Low | target gpu-workstation
tools: Make MCP
microtasks: Enumerate source | Extract + diff vs current | Log decision | No build without approval
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: scenarios enumerated; POD blueprints exported or confirmed absent

### WO-PODAS-0070  (BERM-DOC-PODAS-0070-v1)
Weekly schedule trigger -> BERM-MICH-MUSC-00018 (theme set -> drop batch) + manual webhook  
type Orchestration | prio High | target qnap
deps: BERM-MICH-MUSC-00018-BUILD
tools: n8n MCP
muscles: BERM-MICH-MUSC-00018
microtasks: Define DAG fan-out/fan-in | Enforce wave cap 4 hard | Retry + self-heal + watchdog hook | Telegram batch digest node | Smoke end-to-end on 1 item | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: weekly cron active; manual webhook live

### WO-PODAS-0071  (BERM-DOC-PODAS-0071-v1)
Supervisor watchdog coverage for orchestrator+spawner (heartbeat, retry, Telegram alert)  
type Orchestration | prio Medium | target gpu-workstation
deps: BERM-MICH-MUSC-00018-BUILD
tools: existing APEX watchdog
microtasks: Define DAG fan-out/fan-in | Enforce wave cap 4 hard | Retry + self-heal + watchdog hook | Telegram batch digest node | Smoke end-to-end on 1 item | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: alerts on stall; retries

### WO-PODAS-0072  (BERM-DOC-PODAS-0072-v1)
Cost-discipline guard: content_hash cache, skip unchanged regen, per-batch image-gen spend cap  
type Governance | prio High | target gpu-workstation
deps: WO-PODAS-0001
tools: Supabase MCP
microtasks: Define rule/gate logic | Wire into Prompt Gate / audit path | Test pass+fail cases | Doc Control register
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: no duplicate paid gen; spend cap enforced

### WO-PODAS-0073  (BERM-DOC-PODAS-0073-v1)
Run automated-review-system over drops before approval digest  
type QA Review | prio Medium | target gpu-workstation
deps: BERM-MICH-MUSC-00017-BUILD
tools: automated-review-system skill
microtasks: Define scoring rubric | Run automated-review-system over outputs | Flag/route fails before approval | Log to Supabase
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: each drop scored/flagged pre-Telegram

### WO-PODAS-0080  (BERM-DOC-PODAS-0080-v1)
Save 'pod-auto-studio' skill once spawner certified; POST localhost:8765/api/skills  
type Docs | prio Medium | target gpu-workstation
deps: BERM-MICH-MUSC-00018-BUILD
tools: context server 8765
microtasks: Draft doc/runbook/skill | Cross-link refs + kill-switch | Register in Doc Control / context server | Add playbook pathway
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: saved+retrievable; playbook pathway added

### WO-PODAS-0081  (BERM-DOC-PODAS-0081-v1)
Runbook + CLAUDE.md entry (inputs, brands, schedule, approval, kill-switch)  
type Docs | prio Low | target gpu-workstation
deps: WO-PODAS-0080
tools: operations runbook
microtasks: Draft doc/runbook/skill | Cross-link refs + kill-switch | Register in Doc Control / context server | Add playbook pathway
gates: Rule-0 audit | Rule-1 research-first | Doc Control register pre | Naming Authority code | Doc Control register complete | Backup before live edit | Read-only-first infra | Foreman/indexer certify
acceptance: complete; kill-switch documented