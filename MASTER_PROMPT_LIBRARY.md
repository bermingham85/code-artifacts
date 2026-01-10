# MASTER PROMPT LIBRARY
**Version:** 2.2 | **Updated:** 2025-12-29 | **Location:** C:\Users\bermi\Projects\

---

## QUICK JUMP (By Usage Frequency)

| Shortcut | Prompt | Click to Jump |
|----------|--------|---------------|
| `[resume]` | Continue incomplete project | [→ Go](#1-project-resume) |
| `[n8n]` | Generate n8n workflow JSON | [→ Go](#2-n8n-workflow-creation) |
| `[handover]` | Create WARP.md for project | [→ Go](#3-project-handover) |
| `[agent]` | Create AI agent in n8n | [→ Go](#4-ai-agent-management) |
| `[mcp]` | Build MCP server | [→ Go](#5-mcp-server-creation) |
| `[architect]` | Design automation system | [→ Go](#6-automation-architecture) |
| `[gpt2sys]` | Convert ChatGPT to system | [→ Go](#7-gpt-to-system) |
| `[organize]` | Create file organization script | [→ Go](#8-file-organization) |
| `[template]` | Create prompt template | [→ Go](#9-prompt-template-generation) |
| `[transactions]` | Build categorizer workflow | [→ Go](#10-transaction-processing) |
| `[midjourney]` | Continue MJ automation | [→ Go](#11-midjourney-automation) |
| `[governance]` | Create governance docs | [→ Go](#12-governance-documentation) |
| `[save prompt]` | Capture this conversation | [→ Go](#13-save-prompt) |
| `[task operator]` | Protocol-bound task execution | [→ Go](#14-task-operator) |
| `[compact]` | Compress conversation to memory bank | [→ Go](#15-project-compaction) |

---

## HOW TO USE

**Option A - Shortcut (fastest):** Say `[shortcut]` + context in any Claude conversation
```
[resume] the animation-agent project
[n8n] workflow that monitors Gmail for invoices
[handover] for taleweaver
```

**Option B - Copy prompt:** Click link above → Copy "One-Hit Prompt" → Fill placeholders → Paste

---

## 1. PROJECT RESUME
**Shortcut:** `[resume]`

### Purpose
Continue an incomplete project with full context.

### Required Inputs
- `PROJECT_PATH`: Path to project folder
- `LAST_KNOWN_STATUS`: What was done last
- `NEXT_GOAL`: What to accomplish this session

### One-Hit Prompt
```
Resume project at: {PROJECT_PATH}

Last Status: {LAST_KNOWN_STATUS}
Goal for this session: {NEXT_GOAL}

Steps:
1. Read WARP.md if exists (or README.md, STATUS.md)
2. List directory structure
3. Read recent code/config changes
4. Identify incomplete items
5. Continue from last checkpoint

Do NOT:
- Start over
- Recreate existing files
- Ask for confirmation on documented decisions

Context from memory: Use past conversations about this project.
Complete working solutions only - no partial implementations.
```

### Flow
```
[Read WARP.md] → [Scan Project] → [Identify State] → [Continue] → [Update WARP.md]
```

---

## 2. N8N WORKFLOW CREATION
**Shortcut:** `[n8n]`

### Purpose
Generate import-ready n8n workflow JSON from requirements.

### Required Inputs
- `WORKFLOW_NAME`: Name for the workflow
- `TRIGGER_TYPE`: webhook | schedule | manual | email
- `STEPS_DESCRIPTION`: What the workflow should do
- `INTEGRATIONS`: APIs/services to connect (e.g., Gmail, Notion, Claude)

### One-Hit Prompt
```
Create a complete n8n workflow JSON file.

Name: {WORKFLOW_NAME}
Trigger: {TRIGGER_TYPE}
Steps: {STEPS_DESCRIPTION}
Integrations: {INTEGRATIONS}

Requirements:
1. Output valid JSON importable directly into n8n
2. Include proper node IDs and connections
3. Configure HTTP nodes with method, URL, auth headers
4. Use expressions for dynamic data (e.g., {{$node["Name"].json["field"]}})
5. Add error handling with IF nodes where needed
6. Include credential placeholders marked as [CREDENTIAL_NAME]

Output format: Single .json file ready for n8n import.
Save to: C:\Users\bermi\Projects\bermech-n8n-workflows\
```

### Flow
```
[Parse Requirements] → [Design Node Chain] → [Generate JSON] → [Validate] → [Save]
```

---

## 3. PROJECT HANDOVER
**Shortcut:** `[handover]`

### Purpose
Create WARP.md handover documents for project continuation between AI systems or sessions.

### Required Inputs
- `PROJECT_PATH`: Full path to project folder
- `PROJECT_NAME`: Name of the project
- `CURRENT_STATUS`: What's done / what's remaining

### One-Hit Prompt
```
Create a complete WARP.md handover document for project at {PROJECT_PATH}.

Project: {PROJECT_NAME}
Current Status: {CURRENT_STATUS}

WARP.md must include:
1. HANDOVER METADATA (timestamp, from/to AI, priority)
2. OBJECTIVE (clear goal statement)
3. PREREQUISITES (dependencies, environment, tools needed)
4. SUCCESS CRITERIA (checkboxes for completion)
5. EXECUTION STEPS (numbered, with exact commands)
6. EXPECTED OUTPUT (what each step should produce)
7. TROUBLESHOOTING (common issues and fixes)
8. CONTINUATION PROMPT (copy-paste prompt for next session)

Read existing project files first. Make steps concrete and executable.
Save WARP.md to project root.
```

### Flow
```
[Read Project] → [Analyze State] → [Generate WARP.md] → [Save to Root]
```

---

## 4. AI AGENT MANAGEMENT
**Shortcut:** `[agent]`

### Purpose
Create and manage AI agents in n8n with registry and deduplication.

### Required Inputs
- `AGENT_PURPOSE`: What the agent does
- `CAPABILITIES`: List of tools/actions it can perform
- `TRIGGER`: How it's activated

### One-Hit Prompt
```
Create an AI Agent in n8n that manages other agents.

Purpose: {AGENT_PURPOSE}
Capabilities: {CAPABILITIES}
Trigger: {TRIGGER}

Use n8n AI Agent structure:
1. @n8n/n8n-nodes-langchain AI Agent node as core
2. Claude Sonnet as reasoning model
3. Vector Store for memory/knowledge
4. Tools the agent can call

Agent must:
- Search registry before creating duplicates
- Track performance metrics
- Learn from execution history
- Visualize agent relationships

Reference: C:\Users\bermi\Projects\agent-agency-mcp\

Output:
1. n8n workflow JSON
2. Agent registration API spec
3. Notion database schema for registry
```

### Flow
```
[Receive Task] → [Search Registry] → [Check Duplicates] → [Route] → [Execute] → [Update Metrics]
```

---

## 5. MCP SERVER CREATION
**Shortcut:** `[mcp]`

### Purpose
Build Model Context Protocol servers for tool integration.

### Required Inputs
- `SERVER_NAME`: Name for the MCP server
- `TOOLS`: List of tools to expose
- `TRANSPORT`: stdio | http | websocket

### One-Hit Prompt
```
Create an MCP server for Claude Desktop integration.

Name: {SERVER_NAME}
Tools: {TOOLS}
Transport: {TRANSPORT}

Requirements:
1. TypeScript/Node.js implementation
2. Proper tool schema definitions (JSON Schema)
3. Error handling with clear messages
4. Environment variable configuration
5. Claude Desktop config snippet

Structure:
- src/index.ts (main server)
- src/tools/*.ts (tool implementations)
- package.json (dependencies)
- README.md (setup instructions)
- claude_desktop_config.json snippet

Reference: C:\Users\bermi\Projects\chatgpt-mcp-server\

Save to: C:\Users\bermi\Projects\{SERVER_NAME}\
```

### Flow
```
[Define Tools] → [Create Schemas] → [Implement Handlers] → [Setup Transport] → [Test] → [Document]
```

---

## 6. AUTOMATION ARCHITECTURE
**Shortcut:** `[architect]`

### Purpose
Design modular automation systems with clear component separation.

### Required Inputs
- `SYSTEM_NAME`: Name for the automation system
- `GOAL`: What the system should achieve autonomously
- `COMPONENTS`: List of modules needed
- `TECH_STACK`: Preferred tools (n8n, Python, APIs)

### One-Hit Prompt
```
Design a fully automated system for: {GOAL}

System Name: {SYSTEM_NAME}
Components: {COMPONENTS}
Tech Stack: {TECH_STACK}

Deliverables:
1. ARCHITECTURE DOCUMENT with data flow diagram
2. COMPONENT BREAKDOWN (numbered modules with responsibilities)
3. API SPECIFICATIONS (endpoints, methods, payloads)
4. DATABASE SCHEMA (if needed)
5. WARP.MD HANDOVER for execution
6. FAILURE POINTS + RECOVERY procedures

Requirements:
- Modular design (each component replaceable)
- Self-healing where possible
- Minimal human intervention
- Direct API integrations preferred
- Mark any assumptions as "NEEDS VERIFICATION"

Save all documents to: C:\Users\bermi\Projects\{SYSTEM_NAME}\docs\
```

### Flow
```
[Define Goals] → [Design Components] → [Map Data Flow] → [Create Specs] → [Generate WARP.md]
```

---

## 7. GPT-TO-SYSTEM
**Shortcut:** `[gpt2sys]`

### Purpose
Convert ChatGPT conversations into working systems.

### Required Inputs
- `CONVERSATION_EXPORT`: Path to ChatGPT export or paste
- `PROJECT_NAME`: Name for the resulting project
- `GOAL`: What the conversation was trying to build

### One-Hit Prompt
```
Review the attached ChatGPT conversation and construct a working system.

Conversation: {CONVERSATION_EXPORT}
Project: {PROJECT_NAME}
Goal: {GOAL}

Extract and build:
1. All code blocks (combine into working files)
2. Configuration/environment variables
3. Database schemas mentioned
4. API specifications discussed
5. Workflow definitions

Create:
- Complete project structure
- Working code (not fragments)
- Installation script
- WARP.md for continuation
- Test commands

Fix any:
- Broken code references
- Missing imports
- Incomplete implementations

Save to: C:\Users\bermi\Projects\{PROJECT_NAME}\
```

### Flow
```
[Parse Conversation] → [Extract Code] → [Identify Gaps] → [Complete] → [Create Project] → [WARP.md]
```

---

## 8. FILE ORGANIZATION
**Shortcut:** `[organize]`

### Purpose
Organize files across local, NAS, and cloud storage.

### Required Inputs
- `SOURCE_PATH`: Path to organize
- `DESTINATION_BASE`: Where organized files go
- `RULES`: Organization rules (by date, type, project, etc.)

### One-Hit Prompt
```
Create a file organization system for: {SOURCE_PATH}

Destination: {DESTINATION_BASE}
Organization Rules: {RULES}

Build a Python script that:
1. SCANS source directory recursively
2. CATEGORIZES files by: extension, date, content
3. DEDUPLICATES using hash comparison
4. CREATES organized folder structure
5. MOVES files (with rollback capability)
6. GENERATES summary report

Requirements:
- Dry-run mode by default (--execute flag to apply)
- Skip system/hidden files
- Handle name conflicts with timestamps
- Log all operations to ./logs/organize-YYYYMMDD.log
- Preserve original metadata

Save script to: C:\Users\bermi\Projects\file-organizer\
```

### Flow
```
[Scan Source] → [Hash Files] → [Find Duplicates] → [Categorize] → [Create Structure] → [Move/Report]
```

---

## 9. PROMPT TEMPLATE GENERATION
**Shortcut:** `[template]`

### Purpose
Create reusable n8n prompt templates for AI nodes.

### Required Inputs
- `TEMPLATE_PURPOSE`: What the prompt template does
- `INPUT_VARIABLES`: Variables the template accepts
- `OUTPUT_FORMAT`: Expected output structure

### One-Hit Prompt
```
Create an n8n prompt template.

Purpose: {TEMPLATE_PURPOSE}
Input Variables: {INPUT_VARIABLES}
Output Format: {OUTPUT_FORMAT}

Template must:
1. Use {{variable}} syntax for n8n expressions
2. Include clear instructions for the AI
3. Specify output format explicitly
4. Handle edge cases
5. Be reusable across workflows

Output as:
- .txt file with the prompt template
- Example n8n Code node that uses it
- Test input/output pair

Save to: C:\Users\bermi\Projects\auto-agent-creator\prompts\
```

### Flow
```
[Define Purpose] → [List Variables] → [Write Template] → [Create Example] → [Test]
```

---

## 10. TRANSACTION PROCESSING
**Shortcut:** `[transactions]`

### Purpose
Categorize financial transactions for QuickBooks import.

### Required Inputs
- `TRANSACTION_SOURCE`: Where transactions come from
- `RULES_LOCATION`: Path to categorization rules
- `OUTPUT_FORMAT`: CSV columns needed

### One-Hit Prompt
```
Build transaction categorizer workflow for n8n.

Source: {TRANSACTION_SOURCE}
Rules: {RULES_LOCATION}
Output Format: {OUTPUT_FORMAT}

Triple Rinse Process:
1. FIRST PASS: Apply known rules (merchant → category mapping)
2. SECOND PASS: AI classification for unknowns (Claude/GPT)
3. THIRD PASS: Human review for low-confidence items

Workflow must:
- Accept pasted text or webhook input
- Parse multiple transactions at once
- Apply learned rules from previous categorizations
- Output QuickBooks-compatible CSV
- Store new rules for future use

Reference: C:\Users\bermi\Projects\hourly-autopilot-system\
Save to: C:\Users\bermi\Projects\bermech-n8n-workflows\transaction-categorizer.json
```

### Flow
```
[Input] → [Parse] → [Rule Match] → [AI Classify] → [Human Review] → [Output CSV]
```

---

## 11. MIDJOURNEY AUTOMATION
**Shortcut:** `[midjourney]`

### Purpose
Automate Midjourney image generation via Discord browser automation.

### Required Inputs
- `PROMPTS_SOURCE`: Where prompts come from (CSV, Sheet, manual)
- `OUTPUT_FOLDER`: Where to save generated images
- `BATCH_SIZE`: How many images per run

### One-Hit Prompt
```
Continue Midjourney universal automation project.

Prompt Source: {PROMPTS_SOURCE}
Output: {OUTPUT_FOLDER}
Batch Size: {BATCH_SIZE}

Reference: C:\Users\bermi\Projects\midjourney-news-automation\

Use existing Playwright-based browser automation in agents/midjourney-browser-agent.js.

Adapt for:
1. Universal prompt input (any source, not just RSS)
2. Visual status cards (Done, Processing, Error)
3. Process any quantity (1 or 100 prompts)
4. Bank images with metadata JSON

Steps:
1. Read existing agent code
2. Create prompt input adapter
3. Build status display
4. Test with single prompt
5. Scale to batch

USER CONTEXT: Requires complete working solutions, step-by-step guidance, minimal partial implementations.
```

### Flow
```
[Load Prompts] → [Open Discord] → [Type /imagine] → [Wait] → [Upscale] → [Download] → [Save+Metadata]
```

---

## 12. GOVERNANCE DOCUMENTATION
**Shortcut:** `[governance]`

### Purpose
Create AI governance rules, capabilities, and policies.

### Required Inputs
- `SCOPE`: What systems/projects this governs
- `RULES`: Key rules to enforce
- `CAPABILITIES`: What AI can/cannot do

### One-Hit Prompt
```
Create comprehensive AI governance documentation.

Scope: {SCOPE}
Key Rules: {RULES}
Capabilities: {CAPABILITIES}

Generate three documents:

1. GLOBAL_AI_RULES.md
   - Absolute rules that cannot be overridden
   - Protected zones and boundaries
   - Escalation procedures

2. CAPABILITIES_MANIFEST.md
   - Claude capabilities (design, review, no execution)
   - Warp capabilities (file ops, git, no autonomous decisions)
   - Tool ecosystem (n8n, MCP servers)
   - CAN/CANNOT sections for each system

3. SECRETS_POLICY.md
   - Secret storage locations (NO VALUES)
   - Naming conventions
   - Rotation procedures
   - Access control

Reference: C:\Users\bermi\Projects\ai-governance\

Save to: C:\Users\bermi\Projects\ai-governance\
```

### Flow
```
[Define Scope] → [List Rules] → [Map Capabilities] → [Document Secrets] → [Create WARP.md]
```

---

## 13. SAVE PROMPT
**Shortcut:** `[save prompt]`

### Purpose
Capture current conversation as a reusable prompt template and add to this library.

### Trigger
Say `[save prompt]` at end of any successful conversation.

### Auto-Process
1. **Analyze**: Identify the task/goal accomplished
2. **Reverse Engineer**: Extract minimum prompt for same result
3. **Categorize**: Match to existing category or create new
4. **Format**: Use this document's template structure
5. **Append**: Add to MASTER_PROMPT_LIBRARY.md with next number

### Template Used
```markdown
## [NUMBER]. [CATEGORY NAME]
**Shortcut:** `[shortcut]`

### Purpose
[One sentence]

### Required Inputs
- `INPUT_1`: [Description]

### One-Hit Prompt
\```
[Reverse-engineered prompt]
\```

### Flow
\```
[Step 1] → [Step 2] → [Result]
\```
```

---

## 14. TASK OPERATOR
**Shortcut:** `[task operator]` or `[bootstrap]`

### Purpose
Protocol-bound task execution with Golden Path extraction for replayable procedures.

### Required Inputs
- None for bootstrap (auto-detects state)
- Task name + description for new tasks

### One-Hit Prompt
```
Read C:\Users\bermi\Projects\TASK_OPERATOR\_SHORTCUT_PROMPT.md
Then bootstrap: list all stage folders and report current state.
```

### Flow
```
[bootstrap] → [detect state] → [register/monitor/extract] → [Golden Path]
```

### Key Commands
| Command | Action |
|---------|--------|
| `[task operator]` | Full bootstrap with state report |
| `new task: {name}` | Register task to 01_ACTIVE |
| `closeout` | Mark current task complete |
| `extract` | Generate Golden Path from review |
| `career` | Show capability synthesis |

### Outputs Location
`C:\Users\bermi\Projects\TASK_OPERATOR\`

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.3 | 2025-01-08 | Added Task Operator (#14) for protocol-bound task execution |
| 2.2 | 2025-12-29 | Reordered by usage frequency, improved quick jump links |
| 2.1 | 2025-12-29 | Added shortcut triggers for all prompts |
| 2.0 | 2025-12-29 | Complete rewrite with 12 categories, flow diagrams |
| 1.0 | 2025-08-14 | Initial orchestrator prompt |


---

## 15. PROJECT COMPACTION
**Shortcut:** `[compact]` or `[compress]`

### Purpose
Compress conversation history into token-efficient memory bank for continuation without rediscovery. Creates ~91% token savings.

### Required Inputs
- `PROJECT_PATH`: Path to project folder (or use current)
- `GITHUB_REPO`: Repository URL (or detect from .git)

### One-Hit Prompt
```
[PROJECT COMPACTION]

Project: {PROJECT_PATH}
Repo: {GITHUB_REPO}

Execute 6-phase compaction:

PHASE 1 - DISCOVERY
- Search conversation_search for code artifacts (SQL, Python, JSON, workflows)
- Check local project files
- Review GitHub state

PHASE 2 - EXTRACTION
- Pull working code only (latest versions)
- Note dependencies
- Document decisions made

PHASE 3 - CONSOLIDATION
Create in project directory:
- PROJECT_MEMORY_BANK.json (~4,500 tokens)
- /sql_schemas/ - Database schemas
- /workflows/ - n8n JSON
- /scripts/ - Python, JS, PS1
- HANDOVER.md - Next session instructions

PHASE 4 - PERSISTENCE
1. git add -A && git commit -m "Compaction" && git push
2. POST to http://localhost:8765/api/memory
3. Update Claude memory if significant

PHASE 5 - VERIFICATION
- curl http://localhost:8765/context (confirm data)
- Verify JSON has no BOM
- Confirm GitHub push

PHASE 6 - HANDOVER
Create HANDOVER.md with:
- Context load command
- Access control table
- DONE/REMAINING tasks
- START COMMAND for next session

Output: GitHub URL + token estimate + continuation prompt
```

### Flow
```
[Discovery] → [Extraction] → [Consolidation] → [Persistence] → [Verification] → [Handover]
```

### Token Economics
| Before | After | Savings |
|--------|-------|---------|
| 50,000 tokens | 4,500 tokens | 91% |

### Key Files Created
- `PROJECT_MEMORY_BANK.json` - Master context
- `HANDOVER.md` - Session continuation
- Context API updated at localhost:8765

### Related
- Full documentation: C:\Users\bermi\Projects\MASTER_PROMPT_LIBRARY\PROJECT_COMPACTION.md
- Skill: [skill:project-compaction]
- Code artifacts: https://github.com/bermingham85/code-artifacts

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 2.4 | 2026-01-10 | Added Project Compaction (#15) for token-efficient session handover |
| 2.3 | 2025-01-08 | Added Task Operator (#14) for protocol-bound task execution |
| 2.2 | 2025-12-29 | Reordered by usage frequency, improved quick jump links |
| 2.1 | 2025-12-29 | Added shortcut triggers for all prompts |
| 2.0 | 2025-12-29 | Complete rewrite with 12 categories, flow diagrams |
| 1.0 | 2025-08-14 | Initial orchestrator prompt |
