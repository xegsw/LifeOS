# Fresh visual comparison

The reference was rendered freshly from the fixed P3-116 source before implementation. The candidate is run with a local fixed-DTO mock only for visual DOM/token/geometry comparison; this is supplementary to, not a substitute for, the actual Tauri Runtime chain.

- Reference: `reference-1280.png`.
- Candidate viewports: `candidate-1280x1024-empty.png`, `candidate-1160x768-empty.png`, and `candidate-700x760-empty.png`.
- Computed inherited tokens are `--ink #101a31`, `--blue #176df5`, and `--line rgba(31, 53, 92, 0.08)` at all three viewports.
- The 1280 geometry preserves a 92px icon rail, 1112px main region and 59px fixed composer. At 700px it preserves a 92px rail, reachable composer, and the P3-116 narrow-screen layout.
- Workflow screenshots cover the existing Candidate panel, accepted Focus and AI Workspace without a second renderer.

The exact DOM/class/landmark signatures, computed token values, geometry and typed invoke receipts are machine-readable in `visual-mock-results.json`.
