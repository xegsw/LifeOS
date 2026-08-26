# LIFEOS-P3-119 Evidence Entry

This directory contains only the task-local synthetic fixture, PID-scoped Swift helper, runner, retained self-check Evidence and a non-self Manifest.

## Result

`evidence/final_assessment.json` records the self-check result: **Not Pass**. The conclusive `execution-8` reached a verified dedicated Chrome PID/window and native S0 capture, then posted the first PID-scoped click. The following S1 capture was byte-identical to S0, so the frozen fail-closed rule stopped all subsequent GUI events.

## Evidence order

1. `evidence/execution-8/fixed-inputs.jsonl` — ten frozen input hashes.
2. `evidence/execution-8/raw/static_audit.json` and `helper_compile.log` — PID-only API/source audit and Swift compilation.
3. `evidence/execution-8/raw/P119-M003-attest.json`, `images/S0.png` — PID/window and S0.
4. `evidence/execution-8/raw/P119-E001-click.json`, `images/S1.png`, `raw/S1-pixels.json` — precise target event and failed state transition.
5. `evidence/execution-8/cleanup.jsonl` — exact PID shutdown and root absence.

The earlier `initial` and `execution-1` to `execution-7` directories are immutable self-check history. They contain setup, compilation, PID-window and pixel-verifier failures that were corrected before the decisive clean run; their temporary roots were also removed. They are not evidence of a completed GUI sequence.

No Computer Use, app selector, AppleScript, AX, global event post, CDP/DevTools, headless browser, network, P3-116 candidate, existing Chrome profile, external data or other-window capture was used.
