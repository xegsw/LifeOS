# P3-124 Independent Test Design

Created before reading candidate implementation files or historical runners.

## Independence contract

This review will use a newly written, task-local Python runner. It must not import, copy, execute, or subprocess P3-122/P3-123 runner code. Historical Evidence is an input only; all claims require independently produced result files.

## Frozen matrix coverage

| Frozen row | Independent method | Required result |
|---|---|---|
| M-001 | Parse physical allowlist; hash fixed inputs; prove permitted roots initially absent | preflight JSON |
| M-002 | Scan runner source and command log for historical runner references | independence JSON |
| M-003 | Recompute candidate bytes/hashes and inspect source layers | source-lineage JSON |
| M-004 | Copy only the positive allowlist into temp root; run locked offline build/test | build logs/result |
| M-005–M-007 | Drive actual task-local Tauri App at all three logical sizes; capture page/geometry state | per-action matrix, traces, screenshots |
| M-008–M-009 | Use only fresh synthetic DB and three allowed IPCs; verify lifecycle and failure-before-change | runtime/negative results |
| M-010 | Static and runtime inventory for disallowed capability/network/model paths | boundary JSON |
| M-011 | Recompute declared engineering and PM lineage hashes | lineage JSON |
| M-012 | Pristine control plus nine disposable verifier mutations | mutation result JSON |
| M-013 | Close app, exact-delete only the fixed temp root, re-hash historical inputs | cleanup JSON |
| M-014 | Write a non-self-referential manifest and row-level review | review/manifest |

## Stop rules

Any fixed-input/hash/authorization conflict blocks before temp-root, DB, build, or App creation. Any unavailable required actual-App/native geometry capture blocks rather than treating historical screenshots, static source, or accessibility data as dynamic proof.
