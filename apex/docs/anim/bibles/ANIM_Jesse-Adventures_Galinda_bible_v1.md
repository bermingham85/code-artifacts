# Character Bible — Galinda

**File:** `ANIM_Jesse-Adventures_Galinda_bible_v1.md`
**Authored:** 2026-06-07T05:26:20+00:00
**Brand:** Jesse-Adventures
**Phase:** ANIM-03 (WO `APEX-ANIM-MB-WO-00001`)

## 1. Source of canon (cited verbatim)
- `status.json` (authoritative — last updated `2026-03-26T23:59:00Z`):
  - **age:** young adult woman (early 20s)
  - **hair:** blonde curly, shoulder-length, bouncy waves
  - **eyes:** large blue eyes, Pixar-style expressive
  - **skin:** fair, rosy cheeks, warm complexion
  - **build:** young adult woman, slim, stylized Pixar proportions (slightly large head, expressive features)
  - **height:** average adult female
  - **personality:** sassy, dramatic, secretly kind, loves sparkles
  - **source_inspiration:** Good Witch from Oz — sufficiently differentiated as original Pixar-style young woman
  - **signature_items:**
    - crystal tiara
    - sparkly star-tipped wand
    - pink sparkly ruffled layered dress (knee-length)
    - pink high-heeled shoes
- `README.md` excerpt (first 12 lines, sibling source):
  > # Galinda — Character Profile
  > 
  > **Role:** Good Witch of the Oxzian (supporting character)
  > **First Appearance:** Chapter 2 (Jesse Adventures — Oz arc)
  > **Supabase ID:** `ad4214a8-5b32-4c85-9f83-afad25d68bdf`
  > **Trigger Word:** `galinda_character`
  > **Priority:** Template guinea pig (first character through pipeline)
  > 
  > ---
  > 
  > ## Canon
  > 

## 2. Visual identity
- **Hair:** blonde curly, shoulder-length, bouncy waves
- **Eyes:** large blue eyes, Pixar-style expressive
- **Skin:** fair, rosy cheeks, warm complexion
- **Build:** young adult woman, slim, stylized Pixar proportions (slightly large head, expressive features)
- **Height:** average adult female
- **Signature items / default outfit:**
  - crystal tiara
  - sparkly star-tipped wand
  - pink sparkly ruffled layered dress (knee-length)
  - pink high-heeled shoes

## 3. Personality and behaviour cues
- **Personality:** sassy, dramatic, secretly kind, loves sparkles
- **Story role:** see README.md if present; otherwise leave for next bible version.

## 4. Reference pack (S3)
- **primary_ref** — `X:\Automations\apex\projects\jesse_animate\characters\galinda\primary_ref.png` (sha256=ca1124612b3fe370…, 1478739 B)
- **angle_front** — `X:\Automations\apex\projects\jesse_animate\characters\galinda\angles\galinda_front_00003_.png` (sha256=e73222b04c407a09…, 854144 B)
- **angle_three_quarter** — `X:\Automations\apex\projects\jesse_animate\characters\galinda\angles\galinda_front_three_quarter_00003_.png` (sha256=9016893634ecddaf…, 756394 B)
- **angle_side** — `X:\Automations\apex\projects\jesse_animate\characters\galinda\angles\galinda_side_left_00003_.png` (sha256=034a0d61f95f2d7d…, 718478 B)
- **angle_back** — `X:\Automations\apex\projects\jesse_animate\characters\galinda\angles\galinda_back_00003_.png` (sha256=30ca9a8560ea3192…, 601208 B)

## 5. Do / Don't
- **Do**: lock the trigger word listed in `status.json` (when present); use it on every prompt.
- **Don't**: regenerate or replace `primary_ref` without an ADR — it is the consistency anchor for FaceID + LoRA.

## 6. Findings logged for follow-up
- F-ANIM03-01: canon mismatch on galinda age — status.json says 'young adult woman (early 20s)', README.md describes a child. Bible locks the status.json value as authoritative because it matches the 2026-04-07 PHASE_STATE.json formal sign-off; operator to merge or fork the README.

## 7. Copyright / differentiation
- Source inspiration: Good Witch from Oz — sufficiently differentiated as original Pixar-style young woman
- Differentiation doc: `X:/Automations/apex/projects/jesse_animate/characters/<name>/copyright/differentiation_doc.md` (when populated).
