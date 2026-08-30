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
| Prior compact screenshot, PID 20253, SHA-256 `f57fda31b33e1d3e38a27b53e6a7fedceeb1805b8ef0779af1951c568f58966f` | Human visual inspection found native top bar `LifeOS · P3-140 Cross-domain Today`, conflicting with the prior JSON assertion that it was P3-141 | Invalidated; never used as positive Evidence. Its PID, hash, reason and originating commit `4960a36e77bbb816a58bfaee34c89f6d17eca8d9` remain in `actual_tauri_viewports.json` and `screenshot_identity_review.md`. |
| Prior narrow screenshot, PID 20522, SHA-256 `b821405162984b87957f79e85e6b98a113c3e2d4c820b65ac747f57dbd7665d0` | Human visual inspection found native top bar `LifeOS · P3-140 Cross-domain Today`, conflicting with the prior JSON assertion that it was P3-141 | Invalidated; never used as positive Evidence. Its PID, hash, reason and originating commit `4960a36e77bbb816a58bfaee34c89f6d17eca8d9` remain in `actual_tauri_viewports.json` and `screenshot_identity_review.md`. |
| Direct AXWindowNumber capture attempt for replacement compact screenshot | the direct AXWindow did not expose `AXWindowNumber`; no image was emitted by that attempt | Preserved as a failed method only. Final images were captured after the exact target PID/AX title/AXWebArea assertion and direct AXRaise; each result was manually checked for the visible P3-141 title. |

No test failure left open. The unavailable formatter is non-functional tooling only and does not alter the candidate, test, or Evidence conclusion. Screenshot failures above did not read, write, inspect, or enumerate any prohibited target.
