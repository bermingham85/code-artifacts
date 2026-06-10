# P1 — supabase_project_guard.py delta proposal vs. bc4c6a8 boundary doc

| Field | Value |
|---|---|
| Date | 2026-06-02 |
| Authority | `docs/policy/SUPABASE_SHARED_PROJECT_BOUNDARY.md` (APEX-MB-DOC-00038), `docs/policy/SUPABASE_PROJECT_ISOLATION.md` (APEX-MB-DOC-00037) |
| Existing script | `registry/supabase_project_guard.py` |
| Mode | Proposal only — no edits applied this session |
| Authority gate to apply | Codex review per `feedback_codex_primary_gate` |

## What the existing guard already does (correct)

- Takes `--expect-code APEX` (defaults to APEX).
- Takes `--forbid-code JESS` (appendable; defaults to a one-item list `["JESS"]`).
- Reads PostgREST `agent_projects` filtered by `code IN (...)`. Read-only, no rows printed.
- Returns exit 0 / 2 / 3 with a JSON summary.
- Never prints key values; `secrets_printed: false` always.

## Gap vs `SUPABASE_SHARED_PROJECT_BOUNDARY.md`

The boundary doc lists **11 project codes** with three treatment classes:

| Class | Codes |
|---|---|
| In-scope for Apex coordination | APEX |
| Work-order-gated (shared infra) | INFR, GOVN, GNRL |
| Protected (read-only unless WO names) | AGEN, BERM, FINX, JESS, MILK, TALE, BPIG |

The guard's default forbid list is just `["JESS"]`. That's narrower than the boundary
doc's protected set, so a script that calls `supabase_project_guard.py --expect-code APEX`
with defaults would NOT reject a BERM/FINX/MILK/TALE/BPIG/AGEN write target.

## Three small deltas (proposed)

### Delta D-G1: default forbid list = all 6 protected codes

Change the default to match the boundary doc:

```python
parser.add_argument(
    "--forbid-code",
    action="append",
    default=["AGEN", "BERM", "FINX", "JESS", "MILK", "TALE", "BPIG"],
)
```

Behavior: still appendable (call sites can add more); now blocks every project the boundary
doc marks protected. Existing call sites that pass `--expect-code APEX` keep working; the
only behavior change is that a call site using `--expect-code BERM` (for example) would
now exit 3 unless explicitly authorized (per boundary §"only with explicit work order").

### Delta D-G2: optional `--shared-code` arg for INFR/GOVN/GNRL warning

Add a third class so the boundary doc's "Work-order-gated" tier is representable:

```python
parser.add_argument(
    "--shared-code",
    action="append",
    default=["INFR", "GOVN", "GNRL"],
    help="Project codes treated as shared infra — emit warning unless --allow-shared.",
)
parser.add_argument(
    "--allow-shared",
    action="store_true",
    help="Acknowledge shared-infra write context.",
)
```

If `--expect-code` is in `--shared-code` and `--allow-shared` is not set, emit a warning
field in the JSON and return exit 4. Caller scripts can pass `--allow-shared` after the
operator/work-order has approved.

### Delta D-G3: doc-read marker

Boundary doc requires the loader to have read `SUPABASE_SHARED_PROJECT_BOUNDARY.md`
before writes. Cheapest enforcement: env var `APEX_BOUNDARY_DOC_READ=APEX-MB-DOC-00038-v1.0`
that the guard verifies:

```python
expected_marker = "APEX-MB-DOC-00038-v1.0"
if os.environ.get("APEX_BOUNDARY_DOC_READ") != expected_marker:
    result["boundary_doc_marker"] = "MISSING_OR_STALE"
    print(json.dumps(result, indent=2, sort_keys=True))
    return 5
```

Operators set the env var once per session after acknowledging the doc. Calls sites in
muscles can set it in their own preflight. Migrations + ad-hoc scripts MUST set it.

## What the existing seed tasks claim is already done

`SUPABASE_PROJECT_ISOLATION.md` §"Current APEX Seed Tasks" lists:

| Task | Status |
|---|---|
| Implement APEX Supabase write guard in workflows and scripts | complete |

So this script is the "guard." The 3 deltas above don't contradict its completeness — they
extend it for the just-landed `SUPABASE_SHARED_PROJECT_BOUNDARY.md` which postdates the
original guard.

## Authority to apply

Per `feedback_codex_primary_gate`, edits to `registry/supabase_project_guard.py` should be
Codex-gated before commit. This proposal is the gate input. On APPROVED, applies as a
single commit on `apex/estate-seed-00004`.

## What this proposal does NOT do

- Does not edit `registry/supabase_project_guard.py`.
- Does not change current behavior — every existing call site keeps working unchanged today.
- Does not enable any RLS or write any Supabase row.
- Does not promote the boundary doc out of ACTIVE status.
