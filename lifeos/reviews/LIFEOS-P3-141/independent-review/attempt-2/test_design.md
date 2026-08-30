# LIFEOS-P3-141 Phase B Independent Review — Attempt 2 Test Design

## Precontact declaration

This is a fresh, review-owned Phase B plan.  It was written before any read,
metadata lookup, inventory, hash, or other contact with the P3-141 candidate.
The prior failed review is historical input only and cannot supply a positive
conclusion.  Phase C assets, real data, credentials, external network
endpoints, and every retained Pilot are excluded from this review.

## Scope and conclusion ceiling

- Review only the P3-141 synthetic candidate and review-owned, synthetic
  evidence in the authorized worktree and one task-local temporary root.
- Confirm the frozen 12-input lineage, the P3-140 79-file source lineage, the
  P3-141 candidate before/after state, prior-attempt preservation, and exact
  cleanup.
- The only passing conclusion allowed is `PASS_SYNTHETIC_INDEPENDENT` for
  Phase B.  `M-008`, `M-009`, and `M-017` are recorded as
  `PENDING_PHASE_C`; no full P3-141, PM, freeze, risk, or Stage conclusion is
  allowed.

## Independent test program

| Group | Review-owned check | Required result |
|---|---|---|
| P0 | Validate the 12 fixed input byte/hash values against the frozen inventory; verify the P3-140 79-file tree claim and the P3-141 candidate before state. | Every declared value matches; mismatch stops positive review. |
| P1 | Preserve and inventory prior failed-review history as read-only; snapshot candidate file hashes before dynamic work. | No review write outside attempt-2; candidate snapshot is stable. |
| P2 | Run review-owned path-boundary counterexamples only below the task-local temporary root: missing target, pre-existing target, symlink, ancestor symlink, non-regular target, and root mismatch. | Every invalid case fails before DB/provider/request writes; valid synthetic root is accepted only when fresh. |
| P3 | In synthetic real-mode, attempt receipt/create paths before runtime-root resolution and assert stable fail-closed code plus zero request/receipt/snapshot/audit/Memory/State changes. | `context_budget_rejected` is used for Resolver budget rejection; all pre-write failures preserve sentinels/counts. |
| P4 | Exercise the provider closure: four allowed categories, single selected category, save → test → enable → send, first-send lock, restart lock, and rejections for Custom, switch, second provider, fallback, and background send. | Exactly one explicit synthetic dispatch; prohibited routes reject without a dispatch. |
| P5 | Enumerate and invoke exactly 20 IPC endpoints; validate no extra endpoint and no external dispatch except the task-local loopback fixture. | 20/20 closed set, no 21st IPC. |
| P6 | Exercise request-scoped minimum disclosure, token-budget reject/exact/over-by-one, Health removal, identity separation, feedback stale/recompute, safety-stop, write-before-failure, request-id uniqueness, and restart behavior. | Non-content receipts/counts prove semantics; no raw synthetic prompt/response is persisted in review artifacts. |
| P7 | Add review-owned semantic mutations that invalidate one asserted outcome each, and require the review verifier to fail for each mutation. | Control passes; all mutations fail for the expected independent reason. |
| P8 | Direct-launch actual Tauri at desktop, compact, and narrow viewports. For each launch, bind only its returned PID to exact title `LifeOS · P3-141 Controlled Pilot Candidate`, exactly one AXWindow and one AXWebView, then capture only that window. | Three readable screenshots show the P3-141 title and synthetic-only UI; stale/global windows are never used. |
| P9 | Scan review-owned artifacts for forbidden content classes; compare candidate after state; remove only the exact task-local temporary root and record the outcome. | Candidate unchanged; content exclusion passes; temporary root absent. |

## Stop rules

Immediately stop and report `NOT PASS` if a forbidden target is contacted, an
unbound or stale GUI identity is used, the candidate changes, an artifact
contains real content/credentials, an external network target is contacted,
the temporary root cannot be cleaned exactly, or a required dynamic capture
cannot be obtained.

## Evidence policy

All test sources, inputs, outputs, screenshots, hash records, and verifier
are review-owned and retained beneath this attempt.  Candidate tests may be
read for comparison but never become the only positive evidence.  JSON
receipts contain only fixture labels, enums, counters, opaque refs, hashes,
and timestamps—never real or synthetic user prose, health values, prompts,
responses, or credentials.
