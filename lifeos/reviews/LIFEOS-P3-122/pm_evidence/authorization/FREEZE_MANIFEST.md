# LIFEOS-P3-122 Acceptance Freeze Manifest

- Decision: `D-0492`
- Status: `Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery / Rework 0/2 / Not Frozen`
- No engineering or temporary root was created during PM freeze.

| Layer | Path | SHA-256 |
|---|---|---|
| Final task card | `lifeos/tasks/LIFEOS-P3-122_p3_121_host_independent_native_viewport_and_evidence_lineage_successor.md` | `1666bcad2a11a4949f695c60a9dcd417ffbe8eef647ef6e8c5d77d4497f48d14` |
| Frozen ABF | `lifeos/tasks/LIFEOS-P3-122_p3_121_host_independent_native_viewport_and_evidence_lineage_successor_acceptance_basis_freeze.md` | `2aacd353ad50e5d00c92f168e3f508f5e6488336ebcc8385aba56437e70b0a42` |
| Authorization | `lifeos/reviews/LIFEOS-P3-122/pm_evidence/authorization/MANIFEST.md` | `d88495bd47e8df104952bd0c92e4ac498741eb5c75440f927c4e4359da805f8a` |
| P3-116 visual allowlist | `lifeos/tasks/LIFEOS-P3-122_visual_source_allowlist.md` | `381348fc60a6f8bf703bdd4b93ed430c1cc09a53230133d8c7817723635cb0ac` |
| P3-121 Runtime allowlist | `lifeos/tasks/LIFEOS-P3-122_runtime_source_allowlist.md` | `7deff71878556878b1059fb5a26f5e71b1d636c638d91c659a3fe65d49e00287` |

## Frozen boundary

- Visual: direct P3-116 actual DOM/CSS/Token/page-specific inheritance; P3-121 `ui/` prohibited as visual input.
- Runtime: P3-121 Tauri shell and exactly three existing IPC; fresh synthetic DB only.
- Viewport: native logical geometry plus actual host screenshot; no macOS display-scaling change.
- Model routing: no fixed single Codex model; project whitelist and configuration disclosure remain mandatory.
- Prohibited: Pilot, real DB/path/text, network, product model, new IPC, Schema/API, risk/freeze/stage changes.
