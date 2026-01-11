# JESSE SYSTEM - COMPLETE EXPORT MANIFEST (FULL)
**Generated:** 2026-01-10  
**Updated:** 2026-01-10 22:00 (All drives discovered)
**Purpose:** Full fidelity export to jesse-messe GitHub repository  
**Export Mode:** NO COMPRESSION - Complete preservation of all content
**Scope:** ALL 243 FILES from C:\, H:\, X:\, F:\ drives

---

## DRIVE COVERAGE

| Drive | Description | Files | Status |
|-------|-------------|-------|--------|
| **C:\** | Local Projects + OneDrive | 114 | ✅ Primary |
| **G:\** | Google Drive (bermingham1985) | 0 | ✅ Empty |
| **H:\** | Google Drive (michael@bermech.com) | 29 | ✅ Included |
| **X:\** | QNAP NAS (\\\192.168.50.246\Extra\) | 50 | ✅ Included |
| **F:\** | QNAP NAS (\\\192.168.50.246\Filmora media\) | 50 | ✅ Included |
| **TOTAL** | | **243** | |

---

## EXPORT STRUCTURE (EXPANDED)

```
jesse-messe/
├── 01_DOCUMENTATION/ (14 files)
│   ├── JESSE_NOVEL_SYSTEM.md (10,148 lines - complete system)
│   ├── JESSE_INTEGRATION.md
│   ├── CANON_BIBLE_COMPLETE.md
│   ├── INTEGRATION_MAP.md
│   ├── PROMPT_CHAIN_SYSTEM.md
│   ├── PROSE_STUDIO_CONFIG.md
│   ├── PROSE_STUDIO_FULL_CONFIG.md
│   ├── STYLE_CONTRACT.md
│   ├── WARP.md
│   ├── EMERGENT_CONFIG_PROMPT.md
│   ├── ERROR_LOG.md
│   └── test_result.md
│
├── 02_DATABASE/ (6 files)
│   ├── DEPLOY_SCHEMA.sql
│   ├── SEED_DATA.sql
│   ├── check_jesse_extensions.sql
│   └── migrations/
│       ├── 003_jesse_extensions.sql
│       ├── 004_jesse_seed_template.sql
│       └── 005_jesse_complete_seed.sql
│
├── 03_N8N_WORKFLOWS/ (10 files)
│   ├── jesse_full_pipeline.json
│   ├── jesse_book_generator_full.json
│   ├── jesse_book_generator_partial.json
│   ├── chapter_generator_n8n.json
│   ├── current_workflow.json
│   ├── master-orchestrator.json
│   ├── song-pipeline.json
│   ├── novel_writer_backup.json
│   ├── n8n-workflow-novel-writer.json
│   └── n8n-workflow-webhooks-simple.json
│
├── 04_AGENTS/ (10 files)
│   ├── AGENT_DEFINITIONS.json
│   ├── canon_librarian.json
│   ├── continuity_qa.json
│   ├── dialogue_punchup.json
│   ├── lyrics_room.json
│   ├── packager.json
│   ├── showrunner.json
│   ├── structural_editor.json
│   ├── suno_producer.json
│   └── voice_director.json
│
├── 05_PROMPTS/ (7 files)
│   ├── canon_librarian.md
│   ├── continuity_qa.md
│   ├── dialogue_punchup.md
│   ├── lyrics_room.md
│   ├── showrunner.md
│   ├── structural_editor.md
│   └── delegated/
│       └── EMERGENT_PROMPT.md
│
├── 06_SOURCE_CONTENT/ (~50+ files)
│   ├── C_Drive_Content/
│   │   ├── jesse_beanstalk_malakar_version.txt
│   │   └── jesse_beanstalk_morgrim_version.txt
│   │
│   ├── OneDrive_Content/
│   │   ├── jesse_final_draft_beanstalk.docx
│   │   ├── jesse_2.docx
│   │   ├── Chapter_7_jesse_latest.docx
│   │   ├── jesse_continued_chat_full.docx
│   │   ├── Jesse_in_oz_scene1.docx
│   │   ├── JESSE_AND_THE_BEANSTALK.docx
│   │   ├── Jesse part 1 ending.docx
│   │   ├── Jesse part 2 conversation chatgpt.docx
│   │   ├── castles_in_the_cloud_jesse_atbs_conversation.docx
│   │   ├── jesse_beanstalk_chap_1_original.txt
│   │   ├── jesse_rendered_processed_links120525.docx
│   │   └── [additional story files]
│   │
│   ├── H_Drive_Content/
│   │   ├── Chapter 7 jesse latest 05.10.docx
│   │   ├── jesse final draft beanstalk.docx
│   │   ├── jesse 2.docx
│   │   ├── Jesse part 2 conversation chatgpt.docx
│   │   ├── jesse continued chat in full 141124.docx
│   │   ├── JESSE AND THE BEANSTALK.docx
│   │   ├── JESSE AND THE BEANSTALK all.pdf
│   │   ├── JESSE AND THE BEANSTALK all.zip
│   │   ├── jesse start.xlsx
│   │   ├── Jesse startup or mid chapter form.xlsx
│   │   └── jesse story pre edit.pdf
│   │
│   └── NAS_Content/
│       ├── jesse continued chat in full 141124.docx
│       ├── jesse stories beanstalk.docx
│       ├── JESSE AND THE BEANSTALK.docx
│       ├── JESSE AND THE BEANSTALK all.zip
│       ├── JESSE AND THE BEANSTALK all.pdf
│       └── Jesse beanstalk chap 1_original.txt
│
├── 07_PYTHON_SCRIPTS/ (9 files)
│   ├── orchestrator.py
│   ├── jesse_api.py
│   ├── seed_canon.py
│   ├── seed_characters.py
│   ├── production_orchestrator.py
│   ├── notion_seeder.py
│   ├── test_supabase.py
│   ├── test_system.py
│   └── test_factory.py
│
├── 08_JAVASCRIPT/ (20+ files)
│   ├── jesse-api-client.js
│   ├── app/ (Next.js application)
│   ├── components/ (UI components)
│   ├── hooks/ (React hooks)
│   └── lib/ (utilities)
│
├── 09_CONFIG/ (8 files)
│   ├── MASTER_CONFIG.json
│   ├── config.json
│   ├── integration_config.json
│   ├── .env.template
│   ├── package.json
│   ├── requirements.txt
│   ├── Dockerfile
│   └── components.json
│
├── 10_CANON/ (2 files)
│   ├── CANON_SEED.json
│   └── Jesse_Characters_Template.csv ⚠️ (NEW - from NAS)
│
├── 11_QUALITY/ (2 files)
│   ├── quality_gates.json
│   └── QUALITY_GATES.json
│
├── 12_NOTION/ (1 file)
│   └── NOTION_SETUP.md
│
├── 13_LOGS/ (2 files)
│   ├── run_20251224_060103.jsonl
│   └── run_20251224_060111.jsonl
│
├── 14_AUDIO/ (LOCATION LOG ONLY)
│   └── AUDIO_CATALOG.md
│       ├── Lists all audio file locations (NO FILES MOVED)
│       ├── File metadata: name, path, size, date
│       └── Purpose/description where known
│
└── 15_VIDEO_PROJECTS/ (LOCATION LOG ONLY)
    └── FILMORA_CATALOG.md
        ├── Lists all Filmora project locations (NO FILES MOVED)
        ├── Project metadata: name, path, size, date
        ├── Linked media locations
        └── ⚠️ CRITICAL: Files remain in original locations
                        Moving .wfp files breaks project references!
```

---

## DETAILED INVENTORY BY SOURCE

### SOURCE: C:\ Drive (114 files)

**Primary Locations:**
1. `C:\Users\bermi\Projects\JESSE_NOVEL_SYSTEM.md` (10,148 lines)
2. `C:\Users\bermi\Projects\novel-writer\`
3. `C:\Users\bermi\Projects\jesse-novel-factory\`
4. `C:\Users\bermi\OneDrive - Rentasling\GPT\Jesse stories\`

**Export Priority:** ✅ HIGHEST (Core system files)

---

### SOURCE: H:\ Drive (29 files)
**Location:** Google Drive (michael@bermech.com)

**Story Documents:**
- Chapter 7 jesse latest 05.10.docx
- jesse final draft beanstalk.docx
- jesse 2.docx
- Jesse part 2 conversation chatgpt.docx
- castles in the cloud jesse atbs conversation.docx
- jesse continued chat in full 141124.docx
- jesse rendered processed links120525.docx

**Archives:**
- JESSE AND THE BEANSTALK.docx
- JESSE AND THE BEANSTALK all.pdf
- JESSE AND THE BEANSTALK all.zip

**Spreadsheets:**
- jesse start.xlsx
- Jesse startup or mid chapter form.xlsx

**Audio (Cataloged):**
- Jesse and the beanstalk.wav
- jesse 2 sound fx.mp3

**Video (Cataloged):**
- jesse and bean part 2.mp4

**Export To:** 06_SOURCE_CONTENT/H_Drive_Content/
**Processing:** Convert .docx to .md, preserve .xlsx, catalog media

---

### SOURCE: X:\ Drive (50 files)
**Location:** QNAP NAS `\\192.168.50.246\Extra\`

**Key Discoveries:**
1. **Jesse_Characters_Template.csv** ⚠️ CRITICAL
   - Path: `\Extra\Workspace\BermProject\04_KnowledgeBase\AI\`
   - Export To: 10_CANON/
   
2. **Audio Files:**
   - chapter 7 jesse bean.mp3
   - Jesse and the Beanstalk 1final part 1 draft.mp3
   - jesse and bean part 4.mp3
   - jesse dolby sampl.mp3
   - chapterjessebean.mp3
   - Export To: 14_AUDIO/ (catalog only)

3. **Documents:**
   - jesse continued chat in full 141124.docx
   - Export To: 06_SOURCE_CONTENT/NAS_Content/

4. **Filmora Projects:**
   - Multiple .wfp project files
   - Export To: 15_VIDEO_PROJECTS/

**Export Priority:** ✅ HIGH (Character template is critical)

---

### SOURCE: F:\ Drive (50 files)
**Location:** QNAP NAS `\\192.168.50.246\Filmora media\`

**Content Types:**
1. **Documents:**
   - jesse stories beanstalk.docx
   - JESSE AND THE BEANSTALK.docx
   - Jesse beanstalk chap 1_original.txt
   - JESSE AND THE BEANSTALK all.pdf
   - JESSE AND THE BEANSTALK all.zip

2. **Filmora Projects:**
   - Jesse and the Beanstalk 18102024 archive with medis1.wfpbundle
   - Jesse and the Beanstalk 1final part 1 draft.wfp
   - jesse and bean part 2/3/4.wfp

3. **Snapshots:** (Many duplicate files in @Recently-Snapshot folders)
   - Skip duplicates, keep originals only

**Export To:** 06_SOURCE_CONTENT/NAS_Content/ and 15_VIDEO_PROJECTS/
**Processing:** Deduplicate, export originals only

---

## FILE COUNT SUMMARY (UPDATED)

| Category | Files | Source Drives | Est. Size |
|----------|-------|---------------|-----------|
| Documentation | 14 | C:\ | 2-3 MB |
| Database | 6 | C:\ | 500 KB |
| N8N Workflows | 10 | C:\ | 500 KB |
| Agents | 10 | C:\ | 100 KB |
| Prompts | 7 | C:\ | 200 KB |
| Source Content | 50+ | C:\, H:\, X:\, F:\ | 10-15 MB |
| Python Scripts | 9 | C:\ | 300 KB |
| JavaScript | 20+ | C:\ | 1 MB |
| Config Files | 8 | C:\ | 50 KB |
| Canon/Quality | 4 | C:\, X:\ | 150 KB |
| Logs | 2 | C:\ | 50 KB |
| **Audio Locations** | **10+ (LOG ONLY)** | **H:\, X:\, F:\** | **0 KB** |
| **Video Locations** | **40+ (LOG ONLY)** | **X:\, F:\** | **0 KB** |
| **EXPORTED FILES** | **~140** | | **~18 MB** |
| **CATALOGED LOCATIONS** | **~100** | | **2 log files** |
| **TOTAL TRACKED** | **243** | | |

---

## DEDUPLICATION STRATEGY

Many files appear across multiple drives. Priority order:
1. **C:\** - Authoritative (most recent working versions)
2. **H:\** - Secondary (Google Drive may have unique versions)
3. **X:\ & F:\** - Tertiary (NAS backups, check for unique content)

**Deduplication Rules:**
- Same filename + similar size → Keep C:\ version
- Different content → Keep all, add suffix (e.g., `_h_drive`, `_nas`)
- Snapshot folders → Skip entirely

---

## PROCESSING RULES

### Text Documents (.docx, .txt)
- ✅ Convert .docx to .md using pandoc
- ✅ Preserve .txt as-is
- ✅ Export all versions if content differs

### Spreadsheets (.xlsx)
- ✅ Export as-is (GitHub can render)
- ✅ Optionally convert to CSV

### Audio Files (.mp3, .wav)
- ❌ Do NOT export (GitHub size limits)
- ❌ Do NOT move (keep in original locations)
- ✅ Create detailed catalog in 14_AUDIO/AUDIO_CATALOG.md

### Video Files (.mp4, .wfp, .wfpbundle)
- ❌ Do NOT export .mp4 (size limits)
- ❌ Do NOT export OR move .wfp files (breaks Filmora project references!)
- ❌ Do NOT export .wfpbundle files (binary project bundles)
- ✅ Create detailed catalog in 15_VIDEO_PROJECTS/FILMORA_CATALOG.md
- ⚠️ CRITICAL: Filmora projects must stay in place for video editing to work

### Archives (.zip, .pdf)
- ✅ Extract and export contents
- ⚠️ Keep .pdf for reference

### Configuration (.env)
- ✅ Sanitize (remove API keys)
- ✅ Create .env.template with placeholders

---

## CRITICAL FILES (MUST EXPORT)

| File | Location | Why Critical |
|------|----------|-------------|
| JESSE_NOVEL_SYSTEM.md | C:\ | Complete system documentation |
| Jesse_Characters_Template.csv | X:\ NAS | Character template (unknown until now!) |
| DEPLOY_SCHEMA.sql | C:\ | Database structure |
| master-orchestrator.json | C:\ | Main workflow |
| AGENT_DEFINITIONS.json | C:\ | All agent configurations |
| CANON_SEED.json | C:\ | Narrative canon data |
| MASTER_CONFIG.json | C:\ | System configuration |

---

## MULTI-CONVERSATION EXPORT PLAN (REVISED)

### Conversation 1 (COMPLETED): Discovery & Planning ✓
- ✓ Searched all 5 drives
- ✓ Found 243 files total
- ✓ Created comprehensive manifest
- **NEXT:** Execute Conversation 2

### Conversation 2: Core System Files (C:\ Drive Priority)
**Target: 01_DOCUMENTATION + 02_DATABASE + 03_N8N_WORKFLOWS**
- Export JESSE_NOVEL_SYSTEM.md (10,148 lines)
- Export all documentation files
- Export database schemas and migrations
- Export n8n workflow JSON files
- Est. Output: ~3-4 MB

### Conversation 3: Agents, Prompts, Scripts (C:\ Drive)
**Target: 04_AGENTS + 05_PROMPTS + 07_PYTHON + 08_JAVASCRIPT**
- Export agent definitions
- Export prompt files
- Export Python and JavaScript files
- Est. Output: ~2 MB

### Conversation 4: Source Content (All Drives)
**Target: 06_SOURCE_CONTENT (C:\, H:\, X:\, F:\)**
- Extract story documents from all drives
- Deduplicate based on priority order
- Convert .docx to markdown
- Create organized content library
- Est. Output: ~10-15 MB

### Conversation 5: Canon, Config, Audio/Video Catalogs
**Target: 09_CONFIG + 10_CANON + 11_QUALITY + 14_AUDIO + 15_VIDEO**
- Export Jesse_Characters_Template.csv (CRITICAL!)
- Export configuration files
- Export canon and quality files
- **Create AUDIO_CATALOG.md** (locations log - NO files moved)
- **Create FILMORA_CATALOG.md** (locations log - NO files moved)
- ⚠️ Filmora projects remain untouched in original locations
- Est. Output: ~500 KB + 2 catalog files

### Conversation 6: GitHub Repository Creation & Push
- Create jesse-messe repository
- Organize all exported content
- Push complete structure to GitHub
- Verify all files uploaded
- Generate final inventory report
- Create comprehensive README

---

## EXPORT INTEGRITY CHECKLIST

- [ ] All 243 files cataloged
- [ ] ~140 files exported (text/code/config)
- [ ] ~100 file locations cataloged (audio/video)
- [ ] No compression or summarization applied
- [ ] Deduplication completed
- [ ] Original file structure preserved
- [ ] All metadata captured
- [ ] Cross-references documented
- [ ] Git history preserved
- [ ] Configuration files sanitized
- [ ] Workflows intact and importable
- [ ] Database schemas complete
- [ ] Character template exported (X:\ NAS)
- [ ] AUDIO_CATALOG.md created with all audio file locations
- [ ] FILMORA_CATALOG.md created with all video project locations
- [ ] ⚠️ Filmora projects remain untouched in original locations

---

## NOTES & DECISIONS

### Why Not Export Audio/Video?
- GitHub has 100 MB file size limit
- Repository size would balloon to gigabytes
- Audio/video are production outputs, not source code
- Can be stored separately on NAS or cloud storage

### Why Not Export .wfp Filmora Files?
- **CRITICAL:** Moving .wfp files breaks Filmora project references
- Projects link to media files using absolute or relative paths
- Filmora projects are actively used for video production
- Best practice: Keep projects in original locations
- Solution: Comprehensive location catalog instead
- Filmora projects can be re-exported if needed, but locations must be documented

### Deduplication Priority
- C:\ = Working directory (most current)
- H:\ = Google Drive sync (may have unique versions)
- X:\, F:\ = NAS backups (snapshot history)

---

**END OF MANIFEST**
**Status:** Ready for Conversation 2
**Next Action:** Begin exporting C:\ drive core system files