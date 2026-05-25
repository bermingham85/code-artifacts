# SPEC-APEX-AUTONOMOUS-DELIVERY-SYSTEM - Apex autonomous delivery stack

| Field | Value |
|---|---|
| Ref Code | APEX-MB-DOC-00002 |
| Version | 1.0 |
| Status | DRAFT |
| Created | 2026-05-23 |
| Owner | Apex |
| Scope | Headless laptop automation delivery system using Claude, Codex, n8n/Make, bridge tools, APIs, Git, monitoring, backup, and recovery |

## 1. Apex System Summary

The Apex autonomous delivery system is a controlled automation pipeline, not a loose task runner. It discovers requirements, prepares a dedicated headless laptop, creates authenticated remote access, builds automation workflows, adds backup and recovery, tests each phase, records evidence, self-reviews, and signs off each phase independently.

The operating model combines these roles:

| Role | Responsibility |
|---|---|
| Systems architect | Designs the target architecture, phase boundaries, assumptions, and risk controls |
| DevOps engineer | Configures laptop, services, startup, network, monitoring, deployment, and rollback |
| Automation engineer | Builds n8n/Make workflows, scripts, API calls, queues, retries, and error workflows |
| QA engineer | Defines binary acceptance tests, evidence requirements, and regression checks |
| Security reviewer | Enforces authorization, least privilege, credential storage, audit logs, and access boundaries |
| Recovery planner | Designs WOL, restart, smart plug/fingerbot fallback, backup, restore, and incident paths |
| Documentation writer | Maintains runbooks, templates, registers, handover docs, and operational records |
| Release manager | Controls phase gates, change records, signoffs, rollback, and production readiness |

### Internal Architecture Iterations

| Iteration | Design | Key improvement | Decision |
|---|---|---|---|
| 1 | Baseline functional design | Claude plans, Codex edits, n8n runs workflows, laptop hosts jobs | Rejected as too weak for recovery and audit |
| 2 | Robust production design | Adds health checks, backups, retry policies, locks, logs, and remote access hardening | Accepted as minimum production bar |
| 3 | Apex autonomous design | Adds evidence registers, independent certificates, fallback trees, bridge packet contract, and final handover pack | Selected target |

### Control Rule

Agents proceed without repeatedly asking the user what to do next. They make safe assumptions, record them, and continue unless blocked by credentials, authorization, payment, physical action, data-loss risk, unauthorized-access risk, or unsafe electrical/device behavior.

## 2. Assumptions Register

| ID | Assumption | Confidence | Validation method | Risk if wrong |
|---|---|---:|---|---|
| ASM-001 | The headless laptop is owned or explicitly administered by the user | Medium | User confirmation before access setup | Unauthorized administration risk |
| ASM-002 | Windows 11 is the primary laptop OS | Medium | Run inventory script | Setup commands may need Linux equivalents |
| ASM-003 | Ethernet is available or can be added for reliable Wake-on-LAN | Medium | Physical/network check | WOL may be unreliable on Wi-Fi |
| ASM-004 | Tailscale or equivalent private mesh VPN is acceptable | High | Confirm installed tool or policy | Need alternate VPN path |
| ASM-005 | n8n on the NAS remains the preferred always-on orchestrator | High | Existing Apex docs reference NAS n8n | Workflows need a different orchestrator |
| ASM-006 | Secrets can be stored in approved credential stores, not plaintext files | High | Credential handling review | Production cannot pass security signoff |
| ASM-007 | Smart plug/fingerbot is optional and requires explicit user approval before purchase/use | High | User approval | Physical fallback remains manual |

## 3. Architecture

### System Components

| Component | Primary function | Backup/fallback |
|---|---|---|
| Headless laptop | Local worker for scripts, AI jobs, file processing, GPU tasks, and repo maintenance | Manual laptop access, replacement worker |
| Tailscale/VPN | Private authenticated network path | LAN-only SSH, emergency physical access |
| SSH keys/Tailscale SSH | Secure unattended shell access | Local admin account with MFA-controlled remote desktop |
| n8n/Make | Workflow orchestration, webhooks, schedules, branching, error workflows | Local Task Scheduler scripts |
| Apex repo | Source of truth for specs, templates, scripts, work orders, audit records | Git remote and backup archive |
| Claude | Architecture, prompts, workflow reasoning, documentation, QA criteria | Codex executor for focused implementation |
| Codex | Local code edits, command execution, tests, repo changes, log parsing | Manual operator packet |
| Watchdog | Health checks and controlled restart/remediation | Manual restart runbook |
| Backup targets | Restore points, config backups, workflow exports, repo backup | Offline external backup |

### Delivery Pipeline

1. Intake request.
2. Create or update Assumptions Register.
3. Create Task Packet.
4. Claude plans and produces implementation criteria.
5. Codex implements local changes and runs checks.
6. n8n/Make orchestrates scheduled or event-driven flows.
7. Evidence is written to audit logs.
8. Claude reviews Codex output.
9. Codex performs ship-gate review where required by doctrine.
10. Phase certificate is issued or blocker report is produced.

## 4. Tool Stack

| Layer | Preferred tool | Rule |
|---|---|---|
| Remote network | Tailscale or private VPN | Authenticated access only; device ACLs required |
| Shell access | SSH keys or Tailscale SSH | No passwords for unattended automation |
| Desktop access | RDP/Parsec/Chrome Remote Desktop only if needed | Must be authenticated and audited |
| Workflow orchestration | n8n first, Make.com where useful | Every workflow has trigger, owner, retry, timeout, and error path |
| Local scheduling | Windows Task Scheduler or systemd/cron | Jobs must use locks and logs |
| Versioning | Git | All scripts/config/docs version-controlled |
| Secrets | Credential manager, n8n credentials, OS secret store, or cloud secret manager | No plaintext secret files |
| Monitoring | Health endpoint, log files, n8n alerts, Telegram/Slack/email | Alerts include job ID and evidence path |
| Backup | Local restore point plus cloud/external copy | Restore tests scheduled monthly |

## 5. Laptop Headless Setup Plan

### Laptop Setup Checklist

| Check | Target state | Evidence |
|---|---|---|
| Inventory | CPU, GPU, RAM, disk, OS, hostname, network adapter captured | `audit/headless_inventory/*.json` |
| Hostname | Stable name such as `apex-worker-01` | Screenshot or command output |
| IP plan | Router DHCP reservation or static IP | Router note or network config export |
| Local account | Least-privilege service account for automation | Account name, no password value |
| Admin account | Separate admin account retained | Account existence only |
| Security updates | Enabled where compatible | Update policy screenshot/log |
| Firewall | Default deny inbound except approved services | Firewall export |
| Logging | Script logs, Windows Event Logs, workflow logs enabled | Log path list |
| Disk health | SMART/health check available | Inventory evidence |
| Boot readiness | Startup services wait for network/disk/lock checks | Startup plan file |

### BIOS/UEFI Checklist

| Setting | Recommended value | Notes |
|---|---|---|
| Restore after AC power loss | Enabled when supported | Enables smart plug recovery |
| Wake-on-LAN | Enabled when supported | Prefer Ethernet |
| Boot on schedule | Enabled if available | Useful as daily fallback |
| Sleep/hibernate | Disable only if they break automation | Preserve security and stability |
| Secure Boot | Keep enabled | Do not weaken security for convenience |
| Full-disk encryption | Preserve where possible | Ensure reboot management is practical |

## 6. Remote Access Plan

All unattended access must be approved, authenticated, and auditable.

| Access path | Use | Security control | Evidence |
|---|---|---|---|
| Tailscale SSH | Primary shell access | Tailnet ACLs, device auth, user auth | Tailnet device entry and ACL reference |
| SSH keys | Direct LAN/VPN shell access | Ed25519 key, no password auth, key rotation | Public key fingerprint only |
| Remote desktop | GUI-only tasks | MFA-capable service or VPN-only exposure | Access log |
| Service account | Scheduled jobs | Least privilege, scoped folders | Account policy |
| API service accounts | n8n/Make/API calls | Per-service credentials and rate limits | Credential reference names |

Forbidden:

- Backdoors or hidden persistence.
- Password-only unattended SSH.
- Publicly exposed RDP/SSH without VPN or equivalent access control.
- Plaintext credentials in repo, scripts, logs, workflow exports, or handover docs.

## 7. Power/WOL/Smart Plug/Fingerbot Plan

### Power Control Architecture

| Priority | Method | Use case | Guardrail |
|---:|---|---|---|
| 1 | OS-level scheduled restart | Routine maintenance | Skip if backup/deploy/write lock exists |
| 2 | SSH-triggered graceful restart | Remote controlled restart | Confirm no active critical jobs |
| 3 | Watchdog service restart | Single failed service | Service cooldown and loop prevention |
| 4 | Wake-on-LAN | Laptop asleep/off but WOL-capable | Packet from same LAN helper where needed |
| 5 | BIOS AC restore via smart plug | Laptop wedged and heartbeat dead | Graceful shutdown attempted first |
| 6 | Fingerbot/button pusher | Last physical fallback | Only if mechanically safe and approved |

### Restart Runbook

1. Check heartbeat and active lock files.
2. Check backup/deployment status.
3. Attempt service restart.
4. Attempt graceful OS restart.
5. Wait cooldown window.
6. Attempt WOL if powered down.
7. Use smart plug only after timeout and no active write evidence.
8. Use fingerbot only if pre-approved and safe.
9. Log action, reason, actor, time, and result.
10. Run post-recovery health checks before resuming jobs.

## 8. Claude/Codex Bridge Operating Model

### Division of Labor

| Claude | Codex |
|---|---|
| Architecture and phase plans | Local code edits |
| Prompt and workflow reasoning | Repo changes |
| API payload design | Script creation |
| Documentation and runbooks | Test execution |
| QA criteria and signoff templates | CI checks |
| Security review criteria | Config file updates |
| Review of Codex completion reports | Log parsing and safe repair commands |

### Bridge Protocol

Every implementation unit uses a Task Packet. The orchestrator must provide task ID, goal, input files, constraints, expected output, test command, success criteria, rollback plan, and evidence required.

Codex returns a Task Result containing files changed, commands run, test results, errors, fixes applied, remaining risks, evidence links/logs, rollback instructions, and recommended next task.

Claude reviews the Task Result and chooses one decision:

| Decision | Meaning |
|---|---|
| Approve | Criteria satisfied; phase can continue |
| Request automated revision | Codex can fix safely from the packet |
| Reject | Result violates constraints or criteria |
| Escalate | Genuine blocker exists |

## 9. Automation Workflow Blueprints

### Required Workflow Catalogue

| ID | Workflow | Trigger | Output | Error path |
|---|---|---|---|---|
| WF-ADS-001 | Intake to Task Packet | Webhook/manual | Validated Task Packet | Dead-letter invalid intake |
| WF-ADS-002 | Laptop health monitor | Schedule every 5 minutes | Health event and alert if failed | Recovery workflow |
| WF-ADS-003 | Codex implementation loop | Task Packet created | Task Result | Blocker report |
| WF-ADS-004 | Claude review loop | Task Result created | Review decision | Revision or escalation |
| WF-ADS-005 | Backup export | Daily/weekly/pre-deploy | Backup artifact and checksum | Backup failure alert |
| WF-ADS-006 | Power recovery | Heartbeat failure | Restart/WOL/fallback action | Manual escalation |
| WF-ADS-007 | Signoff pack generator | Phase evidence complete | Certificate | Missing evidence report |

### n8n/Make Workflow Rules

Every workflow must define:

- Owner.
- Purpose.
- Trigger.
- Input schema.
- Output schema.
- Idempotency key.
- Timeout.
- Retry policy.
- Error workflow.
- Log location.
- Credential references.
- Backup path.
- Evidence requirements.

External writes must be guarded by lookup/idempotency checks. Batch work must use rate limiting and retry behavior. n8n workflow exports must not contain live tokens or private webhook URLs.

## 10. Resource Scheduling and Startup Clash Rules

### Routine Catalogue

| Routine | Priority | Lock | Resource policy |
|---|---:|---|---|
| Health check | 100 | none | Lightweight; always allowed |
| Backup | 90 | `backup.lock` | Pauses non-critical jobs |
| Deployment | 85 | `deploy.lock` | Blocks restart and heavy jobs |
| AI prompt batch | 60 | `ai.lock` | Queue; rate limit APIs |
| GPU/local model job | 50 | `gpu.lock` | One GPU job at a time |
| Report generation | 40 | `report.lock` | Skip if disk low |
| Data cleanup | 30 | `cleanup.lock` | Requires backup if destructive |

### Startup Sequence

1. OS boot.
2. Network/VPN wait.
3. Disk and secrets store readiness check.
4. Tailscale/SSH readiness check.
5. Apex health check.
6. Backup status check.
7. Scheduler lock cleanup for stale locks only.
8. Start watchdog.
9. Start low-risk services.
10. Resume queued jobs only after health passes.

### Resource Rules

- One heavy GPU job at a time.
- Use lock files for GPU, deployment, backup, and destructive cleanup.
- Check disk space before large jobs.
- Check memory before high-RAM jobs.
- Pause non-critical jobs during backup or deployment.
- Never resume queued jobs after restart until health checks pass.

## 11. Backup and Restore Plan

| Backup type | Schedule | Contents | Verification |
|---|---|---|---|
| Critical config | Daily | Apex config, service definitions, workflow exports without secrets | JSON/YAML parse and checksum |
| Full backup | Weekly | Repo, scripts, docs, workflow exports, state DB exports | Backup report and sample restore |
| Pre-deployment | Before production change | Changed files and current state | Rollback command tested or documented |
| Pre-destructive action | Before deletes/migrations | Target data and config | Restore point exists |
| Restore drill | Monthly | Restore selected config/workflow/state | Drill report |

RTO target: 4 hours for laptop worker restoration after replacement hardware is available.

RPO target: 24 hours for critical config and workflow state; 1 hour for active work orders where practical.

Secrets backup procedure stores only recovery instructions and secret reference names. Secret values are never exported to this repo.

## 12. Monitoring and Alerts

| Signal | Detection | Alert threshold | Evidence |
|---|---|---|---|
| Laptop offline | Missed heartbeat | 2 missed checks | Heartbeat log |
| Disk full | Disk free below threshold | Less than 15 percent or configured GB | Health report |
| RAM exhausted | Memory pressure | Above 90 percent sustained | Health report |
| GPU locked | Lock older than TTL or GPU busy | Stale lock or queue timeout | Lock metadata |
| n8n workflow failed | Error workflow trigger | Any critical workflow failure | n8n execution ID |
| Backup failed | Missing artifact/checksum | Any scheduled backup failure | Backup log |
| Auth expires | API failure/auth error | First failure | Credential reference, no secret |
| Rate limit | HTTP 429/API limit | First limit event | Retry log |

Alerts must include component, severity, job ID, first failure time, last check time, evidence path, and next automated action.

## 13. Troubleshooting Matrix

| Issue | Detection | Likely causes | Automated fix | Manual fallback | Prevention | Evidence after recovery |
|---|---|---|---|---|---|---|
| Laptop offline | Heartbeat miss | Power, network, OS hang | WOL then controlled power fallback | Physical access | UPS, AC restore, watchdog | Health pass log |
| WOL fails | No boot after WOL | Wi-Fi, BIOS disabled, wrong MAC | Send from LAN helper | Press power | Ethernet, BIOS check | WOL attempt log |
| VPN unavailable | Tailscale device absent | Auth expiry, network | Restart Tailscale service | LAN SSH | Device expiry alerts | VPN status log |
| SSH fails | Connection/auth error | Key issue, service down | Restart SSH service via local task if possible | Remote desktop | Key rotation and service monitor | SSH test log |
| Remote desktop fails | GUI access unavailable | Service down, ACL, display issue | Restart remote desktop service | SSH-only runbook | GUI used only when needed | Access log |
| n8n/Make fails | Error workflow | Credentials, expression, API outage | Retry with backoff | Manual run | Workflow tests | Execution ID |
| Claude API/Claude Code fails | Non-zero exit/API error | Auth, model, rate limit | Retry/backoff, switch allowed mode | Manual review | Auth expiry monitor | Transcript |
| Codex fails | Non-zero exit/review blocked | Auth, command, test failure | Safe repair or blocker report | Manual packet | Bridge smoke test | Task Result |
| Disk full | Low disk signal | Logs/cache/artifacts | Rotate logs, pause jobs | Manual cleanup | Quotas | Disk report |
| RAM exhausted | High memory | Heavy jobs overlap | Kill non-critical job | Reboot if safe | Queue and memory gate | Process report |
| GPU locked | Stale GPU lock | Crashed job | Release stale lock after TTL check | Manual process review | Lock metadata | GPU health |
| Startup clash | Multiple services start | Missing dependencies | Delay and lock-based startup | Disable duplicate task | Startup sequence | Boot log |
| Smart plug fails | No power action | Cloud/API/outlet issue | Retry once, alert | Physical power cycle | Local fallback | Action log |
| Fingerbot fails | Button not pressed | Battery, alignment | None beyond alert | Manual press | Monthly test | Drill report |
| Backup fails | Missing checksum | Disk/cloud/auth | Retry backup | Manual backup | Backup health check | Verified checksum |
| Auth expires | 401/403 | Token expiry | Alert and pause affected workflow | Re-authenticate | Expiry reminders | Credential test |
| API rate limit | 429 | Batch too fast | Backoff and queue | Reduce schedule | Rate limiter | Retry log |
| Cloud outage | Service status/API failure | Provider outage | Queue and fallback path | Wait/manual provider choice | Local cache | Incident note |
| LAN outage | VPN/LAN tests fail | Router/ISP | Local-only queue | Physical network check | UPS/router monitor | Network log |
| Power outage | UPS/smart plug offline | Mains outage | Graceful UPS shutdown | Wait/manual | UPS | Boot recovery log |

## 14. Security and Credential Rules

| Rule | Requirement |
|---|---|
| Authorization | Only administer devices/accounts/services the user owns or is allowed to administer |
| Authentication | Use SSH keys, Tailscale SSH, VPN, ACLs, service accounts, and audit logs |
| Least privilege | Automation accounts get only the paths and APIs they need |
| Secrets | Store in credential stores; never commit plaintext values |
| Audit | Remote access, power actions, deployments, backups, and signoffs are logged |
| Change control | No unreviewed production change |
| Destructive work | Requires backup, rollback, and explicit gate |
| Physical devices | Smart plug/fingerbot actions require safety rules and cooldowns |

## 15. Testing Plan

| Phase | Test | Evidence |
|---|---|---|
| Discovery | Run inventory script and review assumptions | Inventory JSON |
| Headless setup | SSH/VPN/firewall/service readiness check | Access test log |
| Power recovery | Simulated service failure, WOL dry run where possible | Recovery drill report |
| Bridge workflow | Sample Task Packet through Codex result and Claude review | Task Result transcript |
| Automation stack | n8n/Make dry-run and error workflow test | Execution IDs |
| Resource scheduling | Lock contention simulation | Resource guard output |
| Backup/restore | Backup artifact plus sample restore | Restore drill report |
| Troubleshooting | Tabletop incident run | Incident report |
| Security | Credential scan and access review | Security checklist |
| Production readiness | Full signoff pack review | Final readiness report |

## 16. Independent Signoff Certificates

Required certificate set:

| Certificate | Pass condition |
|---|---|
| Architecture Signoff | Architecture, assumptions, risks, and rollback exist |
| Security Signoff | Access model, credentials, ACLs, and audit logs are documented |
| Remote Access Signoff | Authenticated remote shell path tested |
| Power Recovery Signoff | Restart/WOL/fallback tree documented and safely tested or deferred |
| Automation Workflow Signoff | Workflows have owner, trigger, error path, retry, timeout, logs |
| Backup/Restore Signoff | Backup exists and restore procedure is tested or scheduled |
| Monitoring Signoff | Health checks and alerts tested |
| Troubleshooting Signoff | Matrix and runbooks exist |
| Final Production Readiness Signoff | All required certificates pass or have accepted blockers |

A signoff can pass only if deliverables exist, tests were run or a test procedure is documented, evidence is attached, risks are recorded, rollback exists, and recovery path exists.

## 17. Final Production Readiness Report

Production readiness requires:

- No open critical security risks.
- No plaintext secrets in repo or workflow exports.
- Remote access tested and logged.
- Restart path tested or explicitly blocked by physical constraints.
- Backups created and verification scheduled.
- Critical workflows have error paths.
- Resource locks exist for heavy jobs.
- Evidence register contains proof for every phase.
- Final handover pack exists.

## 18. Next Implementation Commands and Files

### Files Added by This Spec Set

| File | Purpose |
|---|---|
| `docs/spec/SPEC-APEX-AUTONOMOUS-DELIVERY-SYSTEM.md` | Master production spec |
| `docs/templates/apex_task_packet_template.json` | Claude to Codex task packet contract |
| `docs/templates/apex_completion_certificate_template.md` | Phase signoff certificate template |
| `docs/templates/apex_workflow_blueprint_template.md` | n8n/Make workflow blueprint template |
| `registry/muscle_headless_inventory.ps1` | Read-only laptop inventory script |
| `registry/muscle_resource_guard.ps1` | Job lock and resource gate script |
| `docs/tools/muscle_headless_inventory/blueprint.md` | Approval blueprint for the inventory support tool |
| `docs/tools/muscle_headless_inventory/guidance.md` | Usage guidance for the inventory support tool |
| `docs/tools/muscle_headless_inventory/test_record.md` | Test evidence and approval stamp for the inventory support tool |
| `docs/tools/muscle_resource_guard/blueprint.md` | Approval blueprint for the resource guard support tool |
| `docs/tools/muscle_resource_guard/guidance.md` | Usage guidance for the resource guard support tool |
| `docs/tools/muscle_resource_guard/test_record.md` | Test evidence and approval stamp for the resource guard support tool |

### Approval Status

The two support tools are approved in `registry/TOOL_INDEX.md` and `registry/manifest.json`. The master spec and reusable templates are active in `docs/DOCUMENT_REGISTER.md`.

### Safe First Commands

Run from the Apex repo on the target laptop:

```powershell
powershell -ExecutionPolicy Bypass -File .\registry\muscle_headless_inventory.ps1 -OutputDir .\audit\headless_inventory
powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName health-check -MinDiskFreeGB 5 -MinMemoryFreeGB 1
powershell -ExecutionPolicy Bypass -File .\registry\muscle_resource_guard.ps1 -JobName health-check -Release
```

### Blocker Report Format

If blocked, produce:

| Field | Required content |
|---|---|
| Exact blocker | Specific missing access, credential, approval, physical action, or safety risk |
| Why it blocks progress | Direct dependency |
| Lowest-friction resolution | Smallest safe user action |
| Safe fallback path | Work that can continue or degraded mode |
| Independent work | Tasks that can proceed without the blocker |
