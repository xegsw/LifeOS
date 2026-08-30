# P3-141 Phase A attempt history

The following failed commands were not used as positive evidence.  Each was corrected within this same authorized Closure Cycle; no prohibited target was accessed.

| Attempt | Outcome | Resolution |
|---|---|---|
| `cargo fmt --check` | rustfmt component unavailable in the supplied Rust toolchain | Recorded as a tooling limitation; compilation and tests use the supplied offline toolchain. |
| First compile after Provider-response assertion | assertion addressed a field on `Status` instead of Provider response | Corrected to assert the closed Provider list directly; final 42/42 test run passed. |
| First verifier invocation | inventory key was `entries`, not `inputs` | Corrected parser; final verifier reports all 12 fixed inputs matching. |
| First exact-filter Phase-C test | filter selected zero tests | Re-run with its fully discovered test name filter; one Phase-C gate test passed. |
| First expected-build-failure wrapper | zsh reserves the name `status` | Re-run with `phase_gate_code`; the intended build gate returned 101 and the wrapper exited successfully. |
| First desktop screenshot attempt through terminal `screencapture` | the command did not write an output file | Not used as evidence; replaced by a direct AX-window-rectangle capture for the same directly launched synthetic PID. |
| First standard CoreGraphics screenshot API invocation | the current SDK marks the direct API unavailable | Not used as evidence; the final capture used the supported legacy symbol only with the directly observed AX rectangle. |
| First compact/narrow screenshot capture immediately after the synthetic failure-close action | compositor frame was stale and still displayed the pre-action fixed synthetic view | Not used as failure-close screenshot evidence. The final retained images are viewport-only fixed-synthetic frames; the failure-close assertion is retained independently from the freshly read direct app accessibility state. |
| First AppleScript descendant-button selector | selector conversion returned an AppleScript type error | Not used as evidence; the existing synthetic UI control was activated through the direct app accessibility target and its returned state was freshly read. |

No test failure left open. The unavailable formatter is non-functional tooling only and does not alter the candidate, test, or Evidence conclusion. Screenshot failures above did not read, write, inspect, or enumerate any prohibited target.
