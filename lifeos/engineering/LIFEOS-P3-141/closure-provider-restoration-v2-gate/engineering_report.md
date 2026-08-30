# LIFEOS-P3-141 Provider Restoration v2 Gate Repair — Engineering Report

## Engineering gate

`READY_FOR_FRESH_INDEPENDENT_REVIEW`. The previous Provider Restoration independent review found a valid P0 and remains Rework. This closure repairs only the receipt/build gate; it does not declare a new independent Pass, PM acceptance, Phase C authorization, real self-use, risk closure or Stage change.

## P0 closure

`phase_c_real` no longer accepts any Phase-B receipt input. It accepts only `LIFEOS_P3_141_PHASE_C_V2_RECEIPT_PATH` pointing to the new v2 filename/schema, with exact Revision-2 task and fixed-inventory identities, `ABF-P3-141-v2` and frozen hash, `PASS`, a clean current candidate `HEAD` and tree, plus a clean peer independent-review worktree's v2 Manifest/hash/identity. The verifier rejects prior v1 identifiers/hashes/schemas, mixed values, old candidate/tree or review Manifest, non-PASS verdicts, dirty candidate/review worktrees, links/ancestor links/directories, malformed/duplicate/extra/fallback JSON and alternate paths before runtime-root resolution.

## Evidence

- Offline regression: 54/54 (`50` existing candidate tests plus `4` v2 gate contract/file-boundary tests).
- Build-path negative controls: missing v2 receipt and legacy Phase-B input both fail before runtime-root inspection; a review-shaped fictional fixture is rejected because the candidate worktree is dirty, also before root creation.
- Existing five Provider profiles, Custom protocol, single enable/first-send lock/no fallback, exact 20 IPC, Work/Health, Memory/State/Resolver, feedback, restart and failure-closed tests remain green.
- No actual-Tauri was repeated; the new independent review must obtain its own desktop/compact/narrow direct-PID evidence.

## Boundaries and next action

Only `/private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1` is used for synthetic cargo artifacts, test files and a non-acceptable review-shaped dirty-candidate fixture. No real Provider, credentials, network, personal content or prohibited target was accessed. The failed review remains read-only. After cleanup, the only next action is a new isolated independent review; this engineering session must not start it or Phase C.

P0=0, P1=0, P2=0, Unknown=0, Not Implemented=0 for this narrow repair. Independent review and Phase C/D/E remain `PENDING`.
