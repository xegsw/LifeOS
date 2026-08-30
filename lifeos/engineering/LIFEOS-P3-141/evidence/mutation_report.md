# P3-141 Closure mutation report

- Baseline: P3-140 candidate 79 files, tree `6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e`; current candidate tree is recorded only in current `source_lineage.json` after final recomputation.
- Attempt-8 changes are confined to `build.rs`, `Cargo.toml`, `src/runtime.rs`, replay/verifier tools and task-local Evidence. The phase-C receipt gate now precedes *all* runtime-root parsing and rejects the retired environment token.
- New negative mutations passed: missing receipt; retired string; directory, receipt link and ancestor link; unauthorized hierarchy; wrong candidate/ABF/Manifest hash; Rework/Blocked; malformed, duplicate and extra fields; stale candidate tree; dirty review history; and a clean exact-binding receipt in an unrelated Git root. Each review-shaped fixture was deliberately non-accepting, never a valid or accepted Pass asset.
- The only positive mutation is explicit `synthetic_review` compilation without a receipt. No Phase-C root, marker, database, capture, provider, model, network request or accepting independent receipt was created in this closure.
- Provider mutation remains explicit: after one loopback send, Ollama → LM Studio returns `provider_locked_after_first_send`; restart does not enable or resend.
- Retained direct-PID AX assets prove the native accessibility adapter's former synthetic run, but are historical after the phase-C gate rewrite and are not reused as a current real-mode receipt claim. A future independent review must perform its own current-bundle capture.
- No mutation uses real content, Health data, credentials, a real Provider, network target or prohibited root.
