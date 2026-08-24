# LIFEOS-P3-098 Independent Test Design

Status: FROZEN BEFORE CANDIDATE RUNTIME/CLI SOURCE INSPECTION

This design derives from `ABF-P3-098-v1`. It does not import, execute, copy, or
translate P3-097 runner/tests or PM counterexample source. All fixtures use the
fixed synthetic strings `alpha`, `alpha-conflict`, and `sentinel-p3-098` inside
new `/private/tmp/lifeos-p3-098-*` directories.

## Test architecture

- Load only the fixed P3-097 runtime/CLI public entry points.
- Create a fresh fixture directory for every leaf test; no fixture sharing.
- Snapshot path object type, existence, bytes/hash, SQLite rows, audit order,
  page bytes/hash, sidecars, shadow/temp files, and sentinel bytes before/after.
- Assign one test ID, fixture ID, and execution ID per leaf.
- Intercept the actual live-target `os.replace` call and invoke the original
  syscall for all other replacements; the injected branch raises at the real
  syscall boundary.
- Inject candidate-close, cleanup, page invalidation, and post-publish FD-close
  errors only at deterministic task-local operations, while preserving a trace.
- Run the Evidence gate against deliberately incomplete synthetic result sets.
- Recompute fixed candidate and Manifest hashes before and after execution.
- Remove every `/private/tmp/lifeos-p3-098-*` fixture and require zero residue.

## Frozen leaf matrix

| ABF row | Independent leaf test IDs | Black-box action and assertions |
|---|---|---|
| M-001 | IR-P3-098-001-RUNTIME, IR-P3-098-001-CLI, IR-P3-098-001-REOPEN | First saved through runtime and CLI in separate fixtures; close/reopen verifies exactly one capture and one saved audit, stale page removed, sentinel unchanged, zero residue. |
| M-002 | IR-P3-098-002-REPEAT, IR-P3-098-002-CONFLICT | Repeat same idempotency key/text adds no capture and exact repeat audit while retaining trusted page; same key/different text is rejected with byte-identical DB/page/sentinel. |
| M-003 | IR-P3-098-003-SAVED-REPLACE | Existing DB/page; fail actual live-target `os.replace` syscall during saved and require explicit failure plus byte-identical DB/page/sentinel and zero sidecar/shadow/temp. |
| M-004 | IR-P3-098-004-REPEAT-REPLACE | Existing repeat/page; fail actual live-target `os.replace` syscall and require no capture/audit/page/sentinel change and zero residue. |
| M-005 | IR-P3-098-005-MISSING-REPLACE | Missing DB; fail actual live-target `os.replace`; DB/page remain absent, sentinel unchanged, zero residue. |
| M-006 | IR-P3-098-006-CANDIDATE-CLOSE | Raise on candidate DB close after commit but before live publish; no live change and zero residue. |
| M-007 | IR-P3-098-007-SIDECAR-TRANSIENT, IR-P3-098-007-SIDECAR-PERSISTENT | Produce candidate sidecar; first cleanup failure then recovery may succeed with accurate state; persistent cleanup failure must not publish and must end with supported zero residue. |
| M-008 | IR-P3-098-008-PAGE-INVALIDATE, IR-P3-098-008-PUBLISH-AFTER-PAGE | Fail page invalidation preparation; separately fail live publish after page preparation. Both preserve a consistent before DB/page pair and sentinel, with zero residue. |
| M-009 | IR-P3-098-009-SAVED-FD-CLOSE | Raise only when closing the post-publish path-gate FD after saved; return `saved`, persist exact capture/audit, invalidate stale page, preserve sentinel. |
| M-010 | IR-P3-098-010-REPEAT-FD-CLOSE | Same injection for repeat; return `idempotent_repeat`, keep one capture, add exact repeat audit, retain trusted page and sentinel. |
| M-011 | IR-P3-098-011-ANCESTOR-DB-LINK, -FINAL-DB-LINK, -FINAL-PAGE-LINK, -DB-HARDLINK, -PAGE-HARDLINK, -DB-FIFO, -DB-DIR, -PAGE-FIFO, -PAGE-DIR, -DB-NONCANON, -PAGE-NONCANON | For each path/object class, call every applicable public entry independently and require refusal before any target/live/page/sentinel mutation. External targets remain byte-identical. |
| M-012 | IR-P3-098-012-RENDER-EXTERNAL, IR-P3-098-012-CLEAR-EXTERNAL | Request fixed parent-external output from render and clear public entry points; both reject with external sentinel, DB, and canonical page unchanged. |
| M-013 | IR-P3-098-013-SCHEMA-PK, -SCHEMA-NOTNULL, -SCHEMA-UNIQUE, -SOURCE, -AUDIT-FUTURE, -AUDIT-REVERSE | Independently mutate canonical constraints, source identity, audit time future relation, and audit ordering. Read/render/capture applicable entries fail closed; DB bytes remain unchanged and stale page is invalidated only per contract. |
| M-014 | IR-P3-098-014-MISSING-ROW, -DUP-EXEC, -MISSING-ASSERT, -UNREPRODUCIBLE | Feed the independent Evidence gate one defect at a time; each yields nonzero exit and positive Not Implemented without altering candidate/history. |
| M-015 | IR-P3-098-015-HASH-PRE, -HASH-POST, -ENG-MANIFEST, -PM-MANIFEST, -HISTORY, -FORBIDDEN-SCAN, -RESIDUE | Recompute all fixed files and Manifest entries, validate referenced history hashes, scan source/dependencies/strings for forbidden capabilities, and prove zero task-local residue. |

## Pass gate

The independent runner exits zero only if every frozen leaf above executed once,
all IDs are unique, each row has concrete assertions and before/after state,
all candidate/history hashes match, forbidden capabilities remain closed, all
temporary fixtures are removed, and P0/P1/P2/Unknown/Not Implemented are zero.

No N/A is permitted. A structurally unreachable branch must be proven by a
separate leaf with source-location evidence after this design hash is frozen.
