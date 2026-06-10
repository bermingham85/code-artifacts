# ANIM-01 — Capability Map (animation production system)

**Phase:** ANIM-01 of `APEX-ANIM-MB-WO-00001`
**Authored:** 2026-06-07T03:58:00Z (`authored_utc`) by `author` (top-level keys in `ANIM-01-evidence.json`)
**Source of truth:** every claim in this map is anchored to a row in `ANIM-01-evidence.json` (same dir). If a row here is not in evidence JSON, it is wrong — file a finding and re-mint.
**Doctrine policy applied:** every claim grounded in filesystem read, file content quote, or upstream-of-record JSON quote. (The WO §0 labels this "R20 (no guessing / preserve detail)"; the doctrine file `CLAUDE_CODEX_DOCTRINE.rules.json` actually defines R20 as "Stuck-loop re-research" — finding logged as **F6**, separately from the policy itself, which is upheld here regardless of rule ID.)

---

## 0. Headline corrections to the WO

### 0.1 Naming
The WO body names three aspirational entities — **`scene-director`**, **`animation-agent`**, **`music_video_pipeline`** — verbatim source quotes in evidence `wo_quotes.wo_named_aspirational_labels_in_source` (from §S6 and §S7). A search across `C:/Users/Owner/Repos/code-artifacts` and `X:/Automations/apex/projects/jesse_animate` returned zero artifacts named that way (see evidence `wo_named_entities_not_found_as_first_class`). The operational reality:

| WO label | On-disk artifact | Status |
|---|---|---|
| `scene-director` | `muscle_music_video.py` (modes: keyframes / animate / stitch / full) | presence confirmed |
| `animation-agent` | (per WO §S6 = fal.ai cloud fallback) — **NOT WIRED**; see gap G9. Local I2V (separate concern) is `muscle_music_video.py --mode animate`; linkage to Wan 2.2 i2v two-stage MoE is **inferred** from same-session PHASE_STATE quotes (evidence `pipeline_to_wan22_animate_linkage`) — ANIM-02 to confirm by reading the script. | local I2V present; fal.ai animation-agent missing |
| `music_video_pipeline/assemble_video.py` | `muscle_music_video.py --mode stitch` + sibling `stitch_video.py` | presence confirmed |

The two artifacts that are mapped to real on-disk code live under `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/`. ANIM-02 onward must use the real names. The fal.ai `animation-agent` row is a gap (G9) — no on-disk artifact today.

### 0.2 Model install scope
WO §4 quote (evidence `wo_quotes.section_4_hardware_mapping_quote`): *"To add (gated install): FLUX.1 Kontext, Wan 2.2 I2V, LTX-Video, HunyuanVideo, kohya for LoRA training."* On-disk inventory contradicts this for **three of the five** (see evidence `models_resolved_for_wo_stages`):

| WO listed | Real status |
|---|---|
| FLUX.1 Kontext | PRESENT — `C:/ComfyUI/models/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors` |
| Wan 2.2 I2V (MoE) | PRESENT — `wan2.2_i2v_{high,low}_noise_14B_fp8_scaled.safetensors` |
| LTX-Video | PRESENT — `C:/ComfyUI/models/unet/ltx-2-19b-dev-fp8.safetensors` |
| HunyuanVideo | INSTALL GAP — `find C:/ComfyUI/models -iname '*hunyuan*'` returned 0 |
| kohya_ss | INSTALL GAP — no presence in standard locations |

Therefore ANIM-02 install scope reduces to **HunyuanVideo + kohya_ss only**. The other three are confirm-and-document.

### 0.3 Grog deliverable size
`PHASE_STATE.json session_2026_04_01_mv` claims the shipped MP4 is `34.8MB`. `stat` on the actual file reports `47,983,724 bytes = 47.98 MB decimal = 45.76 MiB binary`. Finding **F4** — PHASE_STATE.json needs reconciliation.

---

## 1. Existing pipelines and muscles (operational)

### 1.1 Music-video production pipeline
- `muscle_music_video.py` — modes `keyframes` / `animate` / `stitch` / `full` per its file-header docstring (quoted in evidence `.pipelines[0].modes_declared_in_header`). ComfyUI endpoint declared in header: `http://127.0.0.1:8189`. Header self-labels `APEX-MB-PY-XXXXX (pending governance)` — gap G6.
- `muscle_mv_regenerate.py` — sibling; presence confirmed by `ls` 2026-06-07.
- `stitch_video.py` — sibling; presence confirmed by `ls` 2026-06-07.

### 1.2 Character pipeline muscles
Per `PHASE_STATE.json:muscles_built[]` (rows in evidence `muscles_per_phase_state_json.rows`):
- `muscle_comfyui_runner` (APEX-MB-PY-00043)
- `muscle_character_catalogue` (APEX-MB-PY-00044)
- `muscle_character_designer` (APEX-MB-PY-00045)
- `muscle_char_consistency` (APEX-MB-PY-00046)
- `run_character_pipeline` (APEX-MB-PY-00047)
- `muscle_image_analyser` (APEX-MB-PY-00048)

Per `PHASE_STATE.json:session_2026_04_01.governance` (in evidence `muscles_per_phase_state_json.additional_named_in_phase_state`):
- `run_fictional_character_sheets.py` (JESS-MB-PY-00000)

### 1.3 Adjacent character scripts
`X:/Automations/apex/projects/jesse_animate/scripts/` (`ls` 2026-06-07):
- `batch_generate_galinda.py`
- `prepare_lora_dataset.py`
- `scan_batch_output.py`

### 1.4 ComfyUI workflows shipped with jesse_animate
`X:/Automations/apex/projects/jesse_animate/comfyui_workflows/` (`ls` 2026-06-07):
- `character_gen_flux_v1.json`
- `character_gen_flux_ipadapter_v1.json`
- `character_gen_pulid_ipadapter_v1.json`
- `character_pose_generator_v1.json`
- `lumina_workflow_v1.json`

---

## 2. Models present on `C:/ComfyUI/models/`

### 2.1 Loras (`C:/ComfyUI/models/loras/`)
- `ip-adapter-faceid-plusv2_sdxl_lora.safetensors` (S3 reference)
- `kontext-turnaround-sheet-v1.safetensors` (canonical S2 LoRA)
- `kontext-turnaround-sheet-v1 (1).safetensors` — candidate duplicate; verify by hash/size in ANIM-02 before delete/quarantine
- `kontext-turnaround-sheet-v1 (2).safetensors` — candidate duplicate; verify in ANIM-02
- `kontext-turnaround-sheet-v1 (3).safetensors` — candidate duplicate; verify in ANIM-02

### 2.2 Checkpoints (`C:/ComfyUI/models/checkpoints/`)
- `sd_xl_base_1.0.safetensors`

### 2.3 Diffusion models (`C:/ComfyUI/models/diffusion_models/`)
Full ls 2026-06-07 enumerated in evidence `comfyui_models.diffusion_models_per_ls_2026_06_07`. Highlights mapped to WO stages:
- FLUX.1 Kontext: `flux1-dev-kontext_fp8_scaled.safetensors`
- FLUX.1 dev base: `flux1-dev-fp8.safetensors`
- Wan 2.2 i2v MoE pair: `wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors` + `wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors`
- Wan 2.2 t2v MoE pair: `wan2.2_t2v_{high,low}_noise_14B_fp8_scaled.safetensors`
- Wan 2.2 fun camera: `wan2.2_fun_camera_{high,low}_noise_14B_fp8_scaled.safetensors`
- Wan 2.1 variants (3 files)
- HiDream i1 dev fp8
- FantasyTalking (3 variants)

### 2.4 UNet (`C:/ComfyUI/models/unet/`)
- `ltx-2-19b-dev-fp8.safetensors` (LTX-2 19B; WO label "LTX-Video" generic)
- `hidream_e1_1_bf16.safetensors`
- `neta-lumina-v1.0.safetensors`

### 2.5 Other relevant model dirs
- `C:/ComfyUI/models/controlnet/flux-controlnet-union-pro.safetensors`
- `C:/ComfyUI/models/pulid/pulid_flux_v0.9.0.safetensors`

### 2.6 Install gaps (negative-inventoried)
- **HunyuanVideo** — `find -iname '*hunyuan*'` returned 0; install in ANIM-02.
- **kohya_ss** — no presence in `C:/ComfyUI/models` or `C:/Users/Owner/Repos`; install in ANIM-02.

---

## 3. Character source assets (sources cited by WO §S1, evidence `wo_quotes.section_s1_quote`)

Per `ls X:/characters/` 2026-06-07 (evidence `character_source_assets`):
- `galinda/` — directory present.
- `casting_pool.html` — file present.
- `midjourney_session_1` ... `midjourney_session_5` — 5 directories, each with sibling `.zip` of same basename (`midjourney_session_N.zip` present alongside).

Characters at reference-lock per `PHASE_STATE.json session_2026_04_01` (verbatim quotes in evidence `character_renders_quoted_from_phase_state_json`):
- **Grog** — quote: *"DONE — 15/15 renders (3 turnarounds + 6 poses + 6 expressions). Ref: midjourney ogre a944. characters/grog/kontext_sheets/"*. `shot_list.json` primary_ref quoted: `X:/Automations/apex/projects/jesse_animate/characters/grog/primary_ref.png`. `shot_list.json` also locks scale_rule, young_grog_rule, and grog_identifiers strings (verbatim in evidence `shot_pipeline_details_quoted_from_shot_list_json`).
- **Lirian** — quote: *"DONE — 15/15 renders (3 turnarounds + 6 poses + 6 expressions). Ref: generated seed1337. characters/lirian/kontext_sheets/"*.
- **Background cast** — quote: *"DONE — 6/6 complete, 90 renders total (0 errors)"*; characters `bg_bart`, `bg_camille`, `bg_iris`, `bg_marco`, `bg_mena`, `bg_olive`; `db_registered: true`, `assets_registered: true`.

**Galinda** has a discrepancy logged as **F1** (`evidence.findings[0]`). PHASES.md row quoted in `evidence.findings[0].phases_md_row_quoted`: *"| 2.2 | Galinda Proof | ⬜ PENDING | One character end-to-end through factory. Pipeline validated. |"*. PHASE_STATE.json fragment quoted in `evidence.findings[0].phase_state_next_action_quoted_fragment`: *"Phase 2.2 ✅ FORMAL SIGN-OFF DONE — galinda.animation_status=production_ready in Supabase, kontext_validated=PRODUCTION_READY, 15/15 renders 0 failures, identity confirmed."*. Resolve in ANIM-03 pre-flight.

### 3.1 Shipped music-video deliverable
`grog_too_big_for_playground_mv.mp4` at `X:/Automations/apex/projects/jesse_animate/music_video/grog_playground/grog_too_big_for_playground_mv.mp4` (47,983,724 bytes = 47.98 MB decimal = 45.76 MiB binary; PHASE_STATE.json claims 34.8MB — F4). `PHASE_STATE.json:session_2026_04_01_mv.shots` quoted verbatim in evidence `shot_counts_quoted_from_phase_state_json.quote`: *"20/20 complete — 19 Wan2.2 i2v two-stage MoE + 1 skip (existing). Zero errors."*

---

## 4. Doctrine and governance state (read-only confirmation)

- Doctrine dir per `ls` 2026-06-07: `APEX_DOCTRINE_v1.0.md`, `CLAUDE_CODEX_DOCTRINE.md`, `CLAUDE_CODEX_DOCTRINE.rules.json`, `conformance-checklist.md`, `DOCTRINE_v1.0_LOCK_PROPOSAL.md`, `NOTE_FOR_CODEX.md`, `media/`.
- `PLAN_CRITERIA.md` header line quoted: `# APEX Auto-Ingest — Plan Criteria (master)`.
- `SUBPROJECTS.md` H2 headings quoted: SP-A..SP-J (10 rows); **no `SP-ANIM` heading present** — finding F2.
- Codex CLI: version reported by `codex --version` 2026-06-07 = `codex-cli 0.135.0`; binary at `C:/Users/Owner/AppData/Local/Programs/OpenAI/Codex/bin/codex.exe`.
- Codex sandbox: every shell call from inside codex exec returned `windows sandbox: spawn setup refresh` this session; review proceeded via inline-stdin workaround.
- Work-gate audit for this phase at `apex/audit/work_gate/2026-06-07T03-57-46Z-APEX.json`; quoted: `status: "WARN"`, `official_write_allowed: true`, `blockers: []`, `warnings: ["working tree is dirty; inspect user changes before editing"]`.

---

## 5. AGEN core-five recovery context (WO §3.6)

Per `head` of `C:/Users/Owner/apex_governance/handovers/AGEN-completion.handover.md` 2026-06-07 (verbatim quotes in evidence `agen_recovery_context`):

- Handover status line: *"BLOCKED — build artifacts deleted/missing from canonical source-of-truth; signed-off baseline is stale; programme cannot reach cert without artifact restoration or rebuild."*
- Body line on deletion: *"the build artifacts those transcripts reviewed have since been deleted from both the C: working tree and the X: canonical mirror"*
- Spawn-prompt root per handover: `X:/Automations/apex/spawned_prompts/AGEN-*`.

WO §3.6 quoted verbatim in evidence `wo_quotes.section_3_6_core_five_quote`: *"Plus finish the in-flight core five (Specification/Verification/Architecture/Builder/Router) — recover from the saved build prompts at X:\\Automations\\apex\\spawned_prompts\\AGEN-* and Codex review transcripts (verbatim recovery, not invention), then commit + PR this time (the May gap was a missing commit step, not a deletion)."* ANIM-07 parallel slot adopts this — but with the standing warning that canonical artifacts are gone and a transcript-only rebuild is what's available.

---

## 6. Gap list (handover to ANIM-02+)

| ID | Gap | Receiving phase |
|---|---|---|
| G1 | Verify (by hash/size) and delete or quarantine 3 candidate-duplicate `kontext-turnaround-sheet-v1 (N).safetensors` files | ANIM-02 |
| G2 | CLOSED IN ANIM-01: FLUX.1 Kontext located at `C:/ComfyUI/models/diffusion_models/flux1-dev-kontext_fp8_scaled.safetensors`. ANIM-02 wires into muscle config but no further locating needed. | CLOSED |
| G3 | CLOSED IN ANIM-01: Wan 2.2 i2v MoE pair located at `C:/ComfyUI/models/diffusion_models/wan2.2_i2v_{high,low}_noise_14B_fp8_scaled.safetensors`. ANIM-02 wires into muscle config. | CLOSED |
| G3b | CLOSED IN ANIM-01: LTX-2 located at `C:/ComfyUI/models/unet/ltx-2-19b-dev-fp8.safetensors`. ANIM-02 wires into muscle config. | CLOSED |
| G4 | Install HunyuanVideo (negative inventory confirmed) | ANIM-02 |
| G5 | Install kohya_ss for per-character LoRA training (negative inventory confirmed) | ANIM-02 |
| G6 | Register `muscle_music_video.py` + `muscle_mv_regenerate.py` + `stitch_video.py` in `apex/docs/DOCUMENT_REGISTER.md` | ANIM-02 |
| G7 | Resolve Galinda Phase 2.2 sign-off discrepancy (F1) before ANIM-03 reuses galinda as lead | ANIM-03 |
| G8 | Add `SP-ANIM` section to `apex_governance/SUBPROJECTS.md` with ANIM-01..ANIM-07+ enumerated | ANIM-02 |
| G9 | Wire fal.ai cloud fallback (key-resolution route: TBD by ANIM-05 follow-on; evidence-of-route not collected in ANIM-01) | ANIM-05 follow-on |
| G10 | Supabase tracking/write for QC per WO §S8 (schema migration if needed). Operator-gated before any Supabase write or migration. ANIM-04 to scope. | ANIM-04 / NEEDS_OPERATOR |
| G11 | Recover + commit AGEN core-five from `X:/Automations/apex/spawned_prompts/AGEN-*` per AGEN-completion handover; transcript-only rebuild (canonical artifacts gone) | ANIM-07 parallel |

---

## 7. Findings (logged for governance follow-up)

- **F1**: PHASES.md says Phase 2.2 PENDING; PHASE_STATE.json says formally signed off. Resolve in ANIM-03 pre-flight.
- **F2**: `SUBPROJECTS.md` has no `SP-ANIM` row (10 H2 headings SP-A..SP-J only).
- **F3**: 177 untracked `apex/audit/work_gate/*.json` files (count per `git status --porcelain | grep "^?? apex/audit/work_gate/" | wc -l` 2026-06-07; evidence `findings[2].count_via_git_status_porcelain_grep_untracked_2026_06_07`). Dir contains 181 total files per `ls | wc -l` (evidence `findings[2].count_via_ls_wc_l_2026_06_07`). Infrastructure follow-on WO — flag for `.gitignore` review.
- **F4**: PHASE_STATE.json claims Grog MP4 is 34.8MB; actual stat 47,983,724 bytes = 47.98 MB decimal (45.76 MiB binary).
- **F5**: WO §4 says FLUX.1 Kontext + Wan 2.2 I2V + LTX-Video are "to add"; all three are PRESENT.
- **F6**: WO §0 labels doctrine rule R20 as "no guessing / preserve detail"; `CLAUDE_CODEX_DOCTRINE.rules.json` actually defines R20 as *"Stuck-loop re-research. When R16 caps fire, before R17 arbiter, automatically re-run internal+external research scoped to the artifact's stuck point. Arbiter receives the re-research output as additional context."* The WO citation is a mislabel. Resolve in ANIM-02 by either correcting the WO or finding the correct doctrine rule ID for "no guessing".

---

## 8. Provenance

Every row in this map cites a row in `ANIM-01-evidence.json` (same directory). Verbatim quotes are tagged in the JSON via field names ending `_quote`, `_quoted`, or `_quoted_fragment`. Negative-presence claims (e.g. HunyuanVideo not installed) name the search command and the zero-match result. WO `APEX-ANIM-MB-WO-00001` lives at the path in evidence `wo_quotes.wo_path`; the WO sections cited by this map (§S1, §S2, §S6, §S7, §S8, §3.6, §4) are captured verbatim in `wo_quotes`.
