# P3-141 Revision 3 Final Independent Re-review 1 — Test Design

## Identity and stopping rule

- Review type: fresh, isolated, read-only mandatory independent re-review under `ABF-P3-141-v3`.
- Candidate identity to be verified only after this control is sealed: commit `476e5f069671dc7d0dc53be88f9d328901d6d543`.
- Any precontact-order defect, prohibited-path contact, candidate modification, network action, or missing required native direct-PID evidence is fail-closed. Candidate repair and Phase C work are out of scope.

## Review-owned positive and negative checks

1. Recompute fixed inputs, candidate identity, the interactive-GUI-v2 engineering input commit, and the prior Blocked review history. Verify the candidate remains unchanged before and after all review work.
2. Write review-owned source and runtime checks using only a fresh synthetic SQLite database, fresh synthetic credential strings, and a task-local loopback fixture. Prove the five Cloud and three Local visible choices, separate mode state, exactly 20 IPC names, and the narrow credential-write DTO.
3. Prove API-key lifecycle on synthetic data only: encrypted SQLite fields contain no plaintext; restart keeps the credential usable; update supersedes the previous credential; delete renders it unavailable; key material is outside the SQLite payload and unusable/tampered states fail before a write.
4. Prove save, connection test, provider selection, enablement, and send are separate state transitions. Negative cases must show no implicit fallback, background send, or retry.
5. Perform independent semantic mutations against disposable copies or review-owned payloads: provider-set fallback, session-credential fallback, Cloud/Local cross-use, generic-root use, and cleanup-marker bypass. Each mutation must be rejected by review-owned checks.
6. Build and launch a fresh offline actual-Tauri artifact without injecting test files into the candidate. For desktop, compact, and narrow viewports, bind the launch-returned live PID to an exact-title native AXWindow and AXWebArea/WebView, then record Settings navigation, screenshot, requested/actual geometry, source/binary hashes, and PID exit. If any binding is unavailable, stop dynamic positive proof and return Blocked.
7. Exercise cleanup only through a review-owned marker-gated tool: a missing, wrong, or symlink marker must refuse deletion; only a correct mode-0600 regular marker may clean the one literal temporary root after writers have exited.
8. Produce a non-self-referential final Manifest plus a review-owned verifier. Run the verifier against an unmodified control and mutations, and recheck candidate hashes after cleanup.

## Data and confidentiality controls

- Inputs, database records, fixtures, and credentials are newly invented synthetic values. No real Provider, API key, Pilot data, Health value, personal text, network, or cloud call is allowed.
- Evidence must contain only synthetic state identifiers, error codes, non-secret hashes, geometry, PID/bundle identity, and counts. It must not include plaintext credentials.

## Decision rules

- `Pass` requires all ABF3-M-001 through ABF3-M-012, fresh native evidence at all three viewports, clean post-run candidate integrity, and five-category counts `P0/P1/P2/Unknown/Not Implemented = 0/0/0/0/0`.
- Any P0 stops further positive validation. A GUI/environment blockage is reported as `Blocked` rather than as a candidate defect. A candidate defect is `Rework`; neither result changes Phase C, PM status, risks, freezes, or Stage.
