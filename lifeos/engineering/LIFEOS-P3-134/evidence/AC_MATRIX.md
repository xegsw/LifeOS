# LIFEOS-P3-134 acceptance matrix

All rows use only the frozen P3-116/P3-133 inputs, fixed non-sensitive synthetic DTOs, and the task-local temporary root.

| AC | Result | Evidence |
| --- | --- | --- |
| AC-01 | PASS | `verification.json`: 13 fixed inputs hash/type matched; P3-133 candidate source was 75 regular files. |
| AC-02 | PASS | `verification.json`: six mandatory P3-116 visual-contract files are byte-identical; final candidate has 75 regular files and no links. |
| AC-03 | PASS | `visual/visual-mock-results.json`: P3-116 rail, landmarks, classes and page states retained; allowed adapter adds only runtime state. |
| AC-04 | PASS | `runtime/viewport-native-receipt.json` correlates final-code screenshots/AX with direct native Tauri `inner_size` probes (2560×2048, 2320×1536, 1400×1520 backing pixels) and actual WebView AX geometry probes (1280×1024, 1160×768, 700×760 logical pixels). The 1160/700 screenshots are exact native pixel sizes; 1280 lifecycle screenshot host-cropping is explicitly separated from the native-bound proof. |
| AC-05 | PASS | Fresh `visual/reference-1280.png` and candidate DOM/token/geometry signatures share P3-116 tokens and structural rail/main/composer layout; runtime-only state changes are documented. |
| AC-06 | PASS | Visual workflow reaches empty, insufficient, Candidate panel, normal Focus, Me, Context Detail, Memory Detail and AI Workspace. |
| AC-07 | PASS | `verification.json` direct-capability scan is clean; visual images show no debug dashboard, receipt, JSON dump or IPC list. |
| AC-08 | PASS | `verification.json` records exactly 11 handler commands and adapter invokes as a strict subset; `runtime/cargo-test-final.log` is 5/5 offline. |
| AC-09 | PASS | `runtime/final3-action-ax.txt` records explicit Capture, explicit Context, explicit Candidate acceptance, Focus and completion. Capture reads its textarea before busy/render in `ui/runtime-adapter.js`; non-content SQLite/audit counts are in `verification.json`. |
| AC-10 | PASS | final actual AX shows one Focus only after acceptance and zero LifeOS noticed where runtime basis is absent; completion returns to insufficient. |
| AC-11 | PASS | P3-116 fixture panels remain visually marked synthetic/unwired by the adapter; Runtime is only used for the local Work Context. |
| AC-12 | PASS | actual Candidate panel exposes Person/Page/Selection and temporary removal; mock workflow verifies request-local Global Context without a persistence write. |
| AC-13 | PASS | retained byte-identical P3-116 CSS contains reduced-motion, contrast, focus and narrow-screen rules; visual runner used reduced motion and all primary actions remained reachable. |
| AC-14 | PASS | offline Rust tests cover invalid synthetic input/no-write, empty/insufficient path, closed IPC allowlist, and runtime root checks. The first bundle build without a build-time runtime root failed closed before output. |
| AC-15 | PASS | final actual Tauri quit/reopen retained non-content counts `(1,1,1,1,0,1,2,5,0)` and returned the same insufficient state after completed Action. |
| AC-16 | PASS | The 1160 and 700 bundles were closed before the exact task-root removal. `cleanup.json` records the no-glob/no-`find` cleanup and absence postcondition; the final non-self-referential Manifest and zero-write replayer are regenerated afterward. |

No P3-116 or P3-133 historical artifact, Pilot root, real database, model, network, credential, PM ledger, risk, freeze, or Stage asset was modified.
