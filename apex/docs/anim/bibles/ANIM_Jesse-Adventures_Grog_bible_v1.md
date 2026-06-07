# Character Bible — Grog

**File:** `ANIM_Jesse-Adventures_Grog_bible_v1.md`
**Authored:** 2026-06-07T08:44:46+00:00
**Brand:** Jesse-Adventures
**Phase:** ANIM-07 (WO `APEX-ANIM-MB-WO-00001`)

## 1. Source of canon (cited verbatim)
- `PROJECT_SPEC.md` §1.8 canon row:
  > | Grog | Callum | Warrior, rescued by Lirian |

## 2. Visual identity
- Derived from PROJECT_SPEC row: `| Grog | Callum | Warrior, rescued by Lirian |`

## 3. Personality and behaviour cues
- **Story role:** see README.md if present; otherwise leave for next bible version.

## 4. Reference pack (S3)
- **primary_ref** — `X:\Automations\apex\projects\jesse_animate\characters\grog\primary_ref.png` (sha256=8f3aa8c6f3b261c9326b4481b8b0671851eb3d8cb6a40ad5cd28109b1a3c7881, 1065787 B)
- **turnaround_seed** — `X:\Automations\apex\projects\jesse_animate\characters\grog\kontext_sheets\turnaround_seed256.png` (sha256=027147a829b956cb108e58956017f7764c436988bd2d614dba2cd833ba383b7d, 1108832 B)
- **expression_happy** — `X:\Automations\apex\projects\jesse_animate\characters\grog\kontext_sheets\expr_happy.png` (sha256=4e2a3f33397c3db4739a19117fd315c89a4e76746792aa172b435690c119e6d2, 1487011 B)
- **expression_angry** — `X:\Automations\apex\projects\jesse_animate\characters\grog\kontext_sheets\expr_angry.png` (sha256=8f102e6c10a680b49ce35aecd741a1817d0b33227fe15434126d7326b3671800, 1396719 B)
- **expression_sad** — `X:\Automations\apex\projects\jesse_animate\characters\grog\kontext_sheets\expr_sad.png` (sha256=e3e3482c1bff911159e83fe8b4731f6fd85158b030e892786322c62a2ded8d7c, 1519404 B)
- **pose_action** — `X:\Automations\apex\projects\jesse_animate\characters\grog\kontext_sheets\pose_lifting_boulder.png` (sha256=a5246da412e41fc3b2d79057791a44f9657334124ad1675b73340ce4c5c24aa6, 1650490 B)
- **pose_idle** — `X:\Automations\apex\projects\jesse_animate\characters\grog\kontext_sheets\pose_arms_crossed.png` (sha256=4f2ad90ed18ae398fe54f276d51c25f2f290e72c2ca36173fc47c2c09febcbf4, 1484912 B)

## 5. Do / Don't
- **Do**: lock the trigger word listed in `status.json` (when present); use it on every prompt.
- **Don't**: regenerate or replace `primary_ref` without an ADR — it is the consistency anchor for FaceID + LoRA.

## 6. Findings logged for follow-up
- F-ANIM03-02: grog has no status.json under X:\Automations\apex\projects\jesse_animate\characters\grog; bible built from PROJECT_SPEC + render-set inference.

## 7. Copyright / differentiation
- Differentiation doc: `X:/Automations/apex/projects/jesse_animate/characters/<name>/copyright/differentiation_doc.md` (when populated).
