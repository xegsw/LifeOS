# P3-144 independent re-review-2 pre-contact test design

## Scope and independence

- Reviewer: a new isolated review session; this document is authored before any
  candidate, P3-144 engineering Evidence, prior Review, deliverable, or
  Manifest is enumerated or read.
- Candidate under review: the immutable `461423b3` commit only, with the full
  SHA to be read from Git after this seal. The review will be read-only and
  will not modify the candidate, ABF, task contract, historical Evidence, or
  PM ledger.
- Runtime: only a fresh synthetic fixture and
  `/private/tmp/lifeos-p3-144-independent-review-v1`; no real Provider,
  credential, text, network request, or Pilot resource.

## Ordered review plan

1. Verify this pre-contact seal, then read the named Closure-2 and prior
   re-review-1 inputs; extract every prior Closure List item and map it to a
   review-owned test or direct source assertion.
2. Bind the exact candidate commit, verify clean read-only lineage, immutable
   blob identities, the exact 20 IPC names, and both required complete-suite
   profiles in the CI registration. Run `cargo test --locked --offline --
   --test-threads=1` under frozen `independent-review`; require 21/21.
3. Create a fresh 0700 synthetic review root with an ordinary 0600 marker;
   record before/after DB, network-ledger, process, and root state. All test
   data are fixed non-sensitive canaries.
4. Use review-owned tests (not candidate tests or its verifier) for
   ABF-M-003..019: correct Work/Health placement and restart; four boundary
   inputs (fourth, >200, empty, unknown field); relevance, domain, validity,
   authorization, scope and budget exclusion; disclosure parity/removal;
   cancel/no-confirm/replay/stale/restart; DeepSeek-only authority with no
   fallback, background, proxy, redirect, retry, parallelism, or other
   Provider; encrypted credential restart/missing/tamper; explicit AI
   identity; five feedback actions; correction/revocation invalidation; and
   Health medical-request fail-closed behavior.
5. For every negative mutation, assert the stable error plus zero change to
   the synthetic DB and zero network/authority counter before failure. Check
   synthetic canary scans of review Evidence, logs, screenshots, and Manifest
   inputs without inspecting any real content.
6. Launch the reviewed App freshly per viewport, bind launch-returned PID to
   one exact-title AXWindow then AXWebArea/WebView, and capture target-only
   readable desktop, compact, and narrow Evidence. Any unavailable AX or
   screenshot capability becomes a checkpointed `Paused — Resumable` at
   `visual_capture`; bad raster artifacts go only in `excluded/`.
7. Stop writers and PIDs, validate the exact ordinary marker, clean only the
   fixed review root, produce a non-self-referential final Manifest and an
   independent verifier, then recompute it after cleanup.

## Pass/fail discipline

- A candidate failure, missing 21/21 suite, source/lineage drift, or a failed
  review-owned semantic mutation is reported as P0/P1/P2 as warranted; the
  reviewer does not repair it.
- Pilot-7 access, real network/Provider/credential/text access, or mutation
  of read-only material invalidates this review attempt immediately.
- A desktop/AX/screenshot environmental outage alone is not a candidate
  failure. It is paused with the earliest affected stage and a resume-safe
  checkpoint.
- Only a complete Phase-B contract with P0=0, P1=0, Unknown=0 and Not
  Implemented=0 can be reported as Independent Pass. Such a pass only permits
  PM consideration of Phase C; it is not PM acceptance, real-Provider
  approval, risk closure, product freeze, or Stage 4.
