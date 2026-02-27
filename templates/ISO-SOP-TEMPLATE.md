---
# DOCUMENT CONTROL HEADER
doc_ref:         "[PROJECT]-[ORIG]-SOP-[SEQ5]"
title:           "SOP: [What this procedure does]"
doc_level:       "3"
project:         "[BRM / JESS / TALE / PIG / SYS]"
originator:      "[DC / ORCH / BOT / SYS]"
function_code:   "[e.g. DOC-ISSUE]"
status:          "DRAFT"
version:         "D01"
created_by:      "[name]"
created_date:    "YYYY-MM-DD"
approved_by:     ""
approved_date:   ""
review_due:      ""
parent_ref:      ""   # The Level 2 spec this SOP implements
github_path:     "[path/to/this/sop.md]"
---

---

## REVISION HISTORY

| Version | Date       | Author | Status   | Summary                |
|---------|------------|--------|----------|------------------------|
| D01     | YYYY-MM-DD |        | DRAFT    | Initial draft          |

---

## 1. PURPOSE

> One sentence. What job does this SOP govern?

---

## 2. SCOPE

> When does this SOP apply? When does it NOT apply?

---

## 3. RESPONSIBILITIES

| Role         | Responsibility                              |
|--------------|---------------------------------------------|
| [Worker/Agent] | [What they do in this procedure]           |
| Orchestrator | [What orchestrator does]                    |

---

## 4. INPUTS REQUIRED

> What must exist / be provided before this procedure can start?
> If any input is missing → the procedure stops and returns NEEDS_INFO.

| Input          | Required? | Source         | Validation Rule      |
|----------------|-----------|----------------|----------------------|
| ticket_id      | YES       | Ticket system  | starts_with: TKT-    |
| project        | YES       | Caller         | one_of: BRM,JESS...  |
| [field]        | YES/NO    | [where]        | [rule]               |

---

## 5. PROCEDURE — STEP BY STEP

> Every step numbered. No ambiguity. The script does exactly this, in this order.

### Step 1 — [Name of step]
- Action: [what happens]
- Input: [what is used]
- Output: [what is produced]
- If fails: [what happens — STOP / RETRY / RETURN]

### Step 2 — [Name of step]
- Action:
- Input:
- Output:
- If fails:

### Step N — Complete
- Action: Write output to outbox
- Status set to: COMPLETE
- Ticket moved to: completed/
- Log entry written

---

## 6. FAIL-BACK RULES

| Failure Condition         | Response Status | Return To    | Action                  |
|---------------------------|-----------------|--------------|-------------------------|
| Missing required field    | NEEDS_INFO      | Sender       | List missing fields     |
| Invalid field value       | NEEDS_INFO      | Sender       | State valid options     |
| Processing error          | FAILED          | Orchestrator | Include error detail    |
| Dependency unavailable    | FAILED          | Orchestrator | Include dependency name |

---

## 7. OUTPUTS

| Output         | Location          | Format  | Always included?    |
|----------------|-------------------|---------|---------------------|
| Result JSON    | worker/outbox/    | JSON    | YES                 |
| Log entry      | worker/logs/      | .log    | YES                 |
| Ticket archive | completed/        | JSON    | YES on success      |

---

## 8. RELATED DOCUMENTS

| Ref Code | Title | Relationship |
|----------|-------|--------------|
|          |       |              |
