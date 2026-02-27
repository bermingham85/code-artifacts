# BERMECH CODE-ARTIFACTS
## Core System Repository

> **THIS IS THE CORE REPO.**
> Every Claude session, every AI agent, every automation, every new build — starts here.
> If it is not registered here, it does not officially exist in the Bermech system.

---

## What This Repo Is

This is the single source of truth for all Bermech automation infrastructure.
It contains every controlled document, worker script, workflow, template, schema,
and design document across all projects: BRM, JESS, TALE, PIG, SYS.

**GitHub is the version control system.** Full commit history, approval via PR,
SHA integrity on every file. Nothing is duplicated elsewhere.

**PostgreSQL (QNAP NAS)** holds metadata only: document status, approval records,
ref codes, and the live Document Register.

---

## Projects

| Code | Name              | Description                        |
|------|-------------------|------------------------------------|
| BRM  | Bermech / Bermech Ltd | Airbnb, infrastructure, core ops |
| JESS | Jesse Music       | Music production, creative         |
| TALE | Taleweaver        | Book automation                    |
| PIG  | The Balding Pig   | Satirical content brand            |
| SYS  | System            | Cross-project infrastructure       |

---

## Folder Structure

```
code-artifacts/
│
├── .github/
│   ├── CODEOWNERS                  ← Who approves changes to what
│   └── workflows/
│       └── dc-validate.yml         ← Auto-validates DC compliance on every PR
│
├── docs/                           ← LEVEL 1 & 2: Architecture + Design
│   ├── SYSTEM_ARCHITECTURE.md
│   ├── DEFINITIVE_DESIGN.md
│   └── DOCUMENT_REGISTER.md        ← Auto-generated. Do not edit manually.
│
├── workers/                        ← LEVEL 3: Python worker scripts
│   ├── _base/
│   │   └── base_worker.py          ← Every worker inherits this
│   ├── DC/                         ← Document Control Agent
│   │   ├── MANIFEST.json
│   │   ├── dc_agent.py
│   │   └── templates/
│   ├── ORCH/                       ← Orchestrator
│   └── BOT/                        ← BrianBrainBot
│
├── workflows/                      ← n8n workflow JSON exports
│   └── BRM-ORCH-WF-00001-ticket-intake.json
│
├── templates/                      ← LEVEL 4: ISO-standard fill-in templates
│   ├── ISO-DOC-TEMPLATE.md         ← Standard document template
│   ├── ISO-SOP-TEMPLATE.md         ← Standard operating procedure
│   ├── ISO-CHANGE-LOG.md           ← Change log template
│   ├── MANIFEST-TEMPLATE.json      ← Worker manifest template
│   └── TICKET-TEMPLATE.json        ← Ticket template
│
├── schema/                         ← Database schemas
│   └── doc_control_schema.sql
│
└── PROJECT_MEMORY_BANK.json        ← System-wide context for all AI sessions
```

---

## Document Reference Code Format

```
[PROJECT]-[ORIGINATOR]-[TYPE]-[SEQ5]

Examples:
  BRM-DC-PY-00001    Doc Control Agent Python script
  BRM-ORCH-WF-00001  Orchestrator n8n workflow
  BRM-SYS-SQL-00001  System database schema
  SYS-SYS-MD-00001   Cross-project architecture doc
```

## Document Levels (ISO hierarchy)

| Level | Type           | Examples                              |
|-------|----------------|---------------------------------------|
| 1     | Architecture   | System design, strategy docs          |
| 2     | Design/Spec    | Worker specs, flow designs, manifests |
| 3     | SOP/Script     | Python workers, n8n workflows         |
| 4     | Template/Record| Templates, tickets, logs              |

---

## For Claude Sessions

At the start of any session involving builds or changes:

1. Fetch `PROJECT_MEMORY_BANK.json` for full system context
2. Check `docs/DOCUMENT_REGISTER.md` — does the thing you are building already exist?
3. All new files get a ref code **before** being created
4. All changes go via PR to `main` — no direct pushes
5. Register new files in PostgreSQL after PR merge

**GitHub repo:** `https://github.com/bermingham85/code-artifacts`
**PostgreSQL:** `192.168.50.246:5432` — `bermech_ops` database
**n8n:** `http://192.168.50.246:5678`

---

## Branch Strategy

```
main          ← Protected. Production. PR + approval required.
feature/*     ← New capabilities
fix/*         ← Bug fixes
draft/*       ← Early work, not ready for review
setup/*       ← Infrastructure and configuration
```
