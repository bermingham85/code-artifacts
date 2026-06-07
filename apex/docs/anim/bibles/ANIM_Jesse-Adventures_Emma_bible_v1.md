# Character Bible — Emma

**File:** `ANIM_Jesse-Adventures_Emma_bible_v1.md`
**Authored:** 2026-06-07T05:26:13+00:00
**Brand:** Jesse-Adventures
**Phase:** ANIM-03 (WO `APEX-ANIM-MB-WO-00001`)

## 1. Source of canon (cited verbatim)
- `PROJECT_SPEC.md` §1.8 canon row:
  > | Gemma 2 2B FP16 | 5GB | Text encoder | Also on X:/ComfyUI |

## 2. Visual identity
- Derived from PROJECT_SPEC row: `| Gemma 2 2B FP16 | 5GB | Text encoder | Also on X:/ComfyUI |`

## 3. Personality and behaviour cues
- **Story role:** see README.md if present; otherwise leave for next bible version.

## 4. Reference pack (S3)
- **angle_front** — `X:\Automations\apex\projects\jesse_animate\characters\emma\emma_angle_front_00001_.png` (sha256=2f20ede22c2a2568…, 396949 B)
- **angle_three_quarter** — `X:\Automations\apex\projects\jesse_animate\characters\emma\emma_angle_three_quarter_00001_.png` (sha256=da8480f406f6a473…, 368516 B)
- **angle_side** — `X:\Automations\apex\projects\jesse_animate\characters\emma\emma_angle_side_00001_.png` (sha256=4e63070c754fb888…, 369887 B)
- **angle_back** — `X:\Automations\apex\projects\jesse_animate\characters\emma\emma_angle_back_00001_.png` (sha256=9a4fc7e692767107…, 336591 B)
- **expression_neutral** — `X:\Automations\apex\projects\jesse_animate\characters\emma\emma_expr_neutral_00001_.png` (sha256=a39c872ad17e3c2a…, 361635 B)
- **alt_form** — `X:\Automations\apex\projects\jesse_animate\characters\emma\emma_alt_form_00001_.png` (sha256=4ae010d1aba24f9a…, 509793 B)

## 5. Do / Don't
- **Do**: lock the trigger word listed in `status.json` (when present); use it on every prompt.
- **Don't**: regenerate or replace `primary_ref` without an ADR — it is the consistency anchor for FaceID + LoRA.

## 6. Findings logged for follow-up
- F-ANIM03-02: emma has no status.json under X:\Automations\apex\projects\jesse_animate\characters\emma; bible built from PROJECT_SPEC + render-set inference.

## 7. Copyright / differentiation
- Differentiation doc: `X:/Automations/apex/projects/jesse_animate/characters/<name>/copyright/differentiation_doc.md` (when populated).
