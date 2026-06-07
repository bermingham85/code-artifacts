# Character Bible — Lirian

**File:** `ANIM_Jesse-Adventures_Lirian_bible_v1.md`
**Authored:** 2026-06-07T07:03:30+00:00
**Brand:** Jesse-Adventures
**Phase:** ANIM-03 (WO `APEX-ANIM-MB-WO-00001`)

## 1. Source of canon (cited verbatim)
- `PROJECT_SPEC.md` §1.8 canon row:
  > | Lirian | Charlotte | Elfan, winged, combat trainer |

## 2. Visual identity
- Derived from PROJECT_SPEC row: `| Lirian | Charlotte | Elfan, winged, combat trainer |`

## 3. Personality and behaviour cues
- **Story role:** see README.md if present; otherwise leave for next bible version.

## 4. Reference pack (S3)
- **primary_ref** — `X:\Automations\apex\projects\jesse_animate\characters\lirian\lirian_candidate_seed1337.png` (sha256=8c5b334fa4f9f4c7bade8f41347550da2034c0ba3c2f318108552c71e24451a1, 980022 B)
- **turnaround_seed** — `X:\Automations\apex\projects\jesse_animate\characters\lirian\kontext_sheets\turnaround_seed256.png` (sha256=2cc69ba8e78bbf00f26142ba95c83578b9e0c612c6766b884a74695d8c2deedd, 1039046 B)
- **expression_happy** — `X:\Automations\apex\projects\jesse_animate\characters\lirian\kontext_sheets\expr_happy.png` (sha256=8713de04f61fa3986e6c9a80698ab42246d824243aea650a243b234bf6fe9040, 1128744 B)
- **expression_angry** — `X:\Automations\apex\projects\jesse_animate\characters\lirian\kontext_sheets\expr_angry.png` (sha256=42d8ac76f07ec06450650acdc068921adf8b9119b6edcd8db873cce367a07628, 1000631 B)
- **expression_sad** — `X:\Automations\apex\projects\jesse_animate\characters\lirian\kontext_sheets\expr_sad.png` (sha256=d7cc266789a5e994e1d1d65281e20423573dec98d245c208cf353a9075b80660, 1128939 B)
- **pose_action** — `X:\Automations\apex\projects\jesse_animate\characters\lirian\kontext_sheets\pose_bow_drawn.png` (sha256=d3359da3e8140f5ced13ca24859c109d6814ed820f04409b02ad6babfdf3d912, 1397710 B)
- **pose_idle** — `X:\Automations\apex\projects\jesse_animate\characters\lirian\kontext_sheets\pose_listening.png` (sha256=b725f573d33078a7b077d583b05d994f8d3a7f3bb7d16c7cc6c80eb2fc5021fd, 1176718 B)

## 5. Do / Don't
- **Do**: lock the trigger word listed in `status.json` (when present); use it on every prompt.
- **Don't**: regenerate or replace `primary_ref` without an ADR — it is the consistency anchor for FaceID + LoRA.

## 6. Findings logged for follow-up
- F-ANIM03-02: lirian has no status.json under X:\Automations\apex\projects\jesse_animate\characters\lirian; bible built from PROJECT_SPEC + render-set inference.

## 7. Copyright / differentiation
- Differentiation doc: `X:/Automations/apex/projects/jesse_animate/characters/<name>/copyright/differentiation_doc.md` (when populated).
