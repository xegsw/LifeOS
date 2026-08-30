# P3-141 Closure mutation report

- Baseline: P3-140 candidate 79 files, tree `6d5659826e3e4b642b94c848d9e97f43cd93f9a2468863ebd396a4f76389940e`; current candidate: 79 files, tree `6a45b656a7bd1203485818872242d4ce2b9db572f197bec869356a6d807a87e1`.
- Closure changes are confined to `build.rs`, `src/runtime.rs`, `src/runtime/today_intelligence.rs`, replay/verifier tools and task-local Evidence. The receipt gate now precedes root parsing, and real root creation/reopen has strict ownership/schema/regular-file/link/sidecar validation.
- Negative mutations passed: missing receipt with intentionally malformed root; existing empty/expected/unknown roots; root and ancestor links; directory/non-SQLite DB; sidecar; malformed IPC/DTO; stale/budget/authorization failure; unsafe/closed-profile Provider and protocol failures.
- Positive mutation passed: correct receipt creates a fresh temporary root, writes one synthetic capture, validates marker+schema, then reopens read-only without changing DB bytes. The actual bundle initialization creates only marker and DB; its fixed Today fixture does zero Provider/model/network dispatch.
- Provider mutation remains explicit: after one loopback send, Ollama → LM Studio returns `provider_locked_after_first_send`; restart does not enable or resend.
- No mutation uses real content, Health data, credentials, a real Provider, network target or prohibited root.
