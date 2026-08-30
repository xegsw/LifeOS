# P3-141 Phase A attempt history

The following failed commands were not used as positive evidence.  Each was corrected within this same authorized Closure Cycle; no prohibited target was accessed.

| Attempt | Outcome | Resolution |
|---|---|---|
| `cargo fmt --check` | rustfmt component unavailable in the supplied Rust toolchain | Recorded as a tooling limitation; compilation and tests use the supplied offline toolchain. |
| First compile after Provider-response assertion | assertion addressed a field on `Status` instead of Provider response | Corrected to assert the closed Provider list directly; final 42/42 test run passed. |
| First verifier invocation | inventory key was `entries`, not `inputs` | Corrected parser; final verifier reports all 12 fixed inputs matching. |
| First exact-filter Phase-C test | filter selected zero tests | Re-run with its fully discovered test name filter; one Phase-C gate test passed. |
| First expected-build-failure wrapper | zsh reserves the name `status` | Re-run with `phase_gate_code`; the intended build gate returned 101 and the wrapper exited successfully. |

No test failure left open.  The unavailable formatter is non-functional tooling only and does not alter the candidate, test, or Evidence conclusion.
