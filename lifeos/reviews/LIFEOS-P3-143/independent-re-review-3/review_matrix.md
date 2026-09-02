# LIFEOS-P3-143 Independent Re-review-3 — Row Matrix

Candidate: immutable `a95a0beb27dc0dac183f8a29da550f43af0d6ce3`; business-code lineage is `dcbc32518d92e16e26f8c7dfec682630f5d51cde`. All checks below are offline and use no credential, Provider, Keychain item, personal data, or network target.

| Row | Independent action | Result | Evidence |
|---|---|---|---|
| IR-RR3-P0-001 | The sealed design/binding authorized only literal root `rereview3-20260902`; later source-built bundle used `bundleui-20260902` and created a second root | **Procedural P0 — review invalidated** | `p0_procedural_invalidation.md`, `native_bundle_runtime_root_binding.md` |
| Input / seal | New directory; test design, allowlist, prohibited declaration and seal hashed before candidate contact | Pass | `precontact_seal.md`, `input_availability.md` |
| Fixed input | Ten Freeze Manifest hashes and all required P3-143/review history inputs checked | Pass | `fixed_inputs.sha256` |
| Candidate lineage | 85 candidate paths from `a95a0beb`, Engineering Final Manifest 126/126, P3-142 Manifest and three historical review manifests recomputed | Pass | `evidence_engineering_final_manifest.json`, `evidence_p3_142_manifest.json`, `evidence_history_manifest.json` |
| Phase-A history | The 113-entry pre-Real-Gate Manifest is retained historical context; its old source values predate current candidate and have no declared immutable Git snapshot, so it is not used as current positive evidence | Recorded, non-positive | `evidence_phase_a_manifest.json` |
| Cloud8 / Local4 | Review-owned parser checked exact Cloud 8 and Local 4 registry identities | Pass | `evidence_static_contract.json` |
| IPC / action boundary | Exact ordered 20 IPC, credential/test/select/enable/canary separation, exact DeepSeek authority and proxy/redirect static guards checked | Pass | `evidence_static_contract.json` |
| Static mutations | Remove missing-marker guard, duplicate IPC, evil authority and proxy removal all detected by review-owned mutation checks | Pass (4/4) | `evidence_static_contract.json` |
| Root absent | Fresh literal review root created authorized 0700 root, exact 0600 marker and runtime child before DB | Pass | review-owned harness result |
| Existing valid marker | Existing exact marker revalidated without changing sentinel/DB semantics | Pass | review-owned harness result |
| Existing missing marker | Missing marker rejected before runtime/DB write; sentinel and filesystem stayed unchanged | Pass | review-owned harness result |
| Wrong marker / marker symlink / marker mode | Wrong payload, symlink and 0640 marker each rejected before writes | Pass | review-owned harness result |
| Root shape | Root symlink, wrong parent, traversal, mixed profile and unknown profile all rejected before writes | Pass | review-owned harness result |
| Runtime child | Absent/valid 0700 child accepted; symlink and wrong-permission child rejected | Pass | review-owned harness result |
| DB child | Absent/direct regular DB accepted; symlink rejected; wrong-parent authority rejected before DB construction | Pass | review-owned harness result |
| Run identifiers | Two valid `independent-review` profile compiles (`rereview3-20260902`, `secondrun-20260902`); short/overlong/case/slash/dot-dot/absolute/unknown malformed IDs rejected | Pass | harness build results and test result |
| Runtime environment injection | Runtime `LIFEOS_*` injection did not change compile-time root authority; no injected root was created | Pass | review-owned harness result |
| Refusal immutability | Sentinel, DB and filesystem pre/post state was asserted on every refusal path | Pass | review-owned harness result |
| Root cleanup | Writer stopped; ordinary 0600 exact marker and 0700 literal root validated; exact marker-gated cleanup produced final absence | Pass | `cleanup_receipt.json` |
| ABF-M-014 / M-015 / M-016 | Source-built bundle direct PID 99755 bound to exact title, AXWindow and AXWebArea; target-only desktop/1160×768/700×760 captures each matched that PID and CG window id | Technically observed, **non-positive after P0** | `evidence/native_*`, `p0_procedural_invalidation.md` |
| ABF-M-021 | PID stopped; both known roots are absent after marker-gated cleanup | Pass for containment, non-positive for verdict | `cleanup_receipt.json`, `checkpoint.json` |
| ABF-M-022 | Fresh controls, review-owned attacks, read-only lineage and technical native chain were obtained, but IR-RR3-P0-001 invalidates the independent conclusion | **Invalidated** | `p0_procedural_invalidation.md` |

Review-owned root test command: `cargo test --locked --offline … review_owned_single_root_authority_matrix -- --nocapture`; final output was `1 passed; 0 failed`, emitted `network_requests:0`, and confirmed root absence after cleanup.
