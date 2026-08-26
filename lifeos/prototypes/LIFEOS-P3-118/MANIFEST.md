# LIFEOS-P3-118 Evidence Manifest

- Scope: P3-118-only helper, plan, and fail-closed evidence. The frozen P3-116/P3-117 assets are external read-only inputs, rehashed in `evidence/preflight/fixed_inputs.json`.
- Status: `Blocked` before Chrome launch, Computer Use query, native window capture, or screenshot creation.
- Excluded by design: this manifest itself and ephemeral Swift module-cache artifacts; no candidate or historical asset is included or modified.
- Delivery report reference: `lifeos/deliverables/LIFEOS-P3-118_p3_116_current_candidate_pid_scoped_native_gui_dynamic_evidence_successor.md`.

| Relative path | SHA-256 | Bytes |
|---|---|---:|
| `evidence/preflight/cleanup_prelaunch.json` | `90b52c8b0eba0ca5d742cb8f6a0a1d1378ad78a836995ff7dfc746871bf29f60` | 515 |
| `evidence/preflight/fixed_inputs.json` | `752f77f048d3f1033cd2a1f5cf2ea89b520b1477f85938e0891d3a95e4244d5f` | 5427 |
| `evidence/preflight/static_audit.json` | `ec7d47cb09f386f52e1ebad6159fe83386c013f352d80166760a7b81ca2256e5` | 420 |
| `evidence/results/blocked_package_verification.json` | `1321338778b52f8dfeaccf8bddc66d4ff12fd57e6bab2b876baab015ac1b74e2` | 499 |
| `evidence/results/computer_use_pid_binding_assessment.json` | `0f26f886b151cee36d88fc7dcf882bc4367ec0fb69d39f959a2f43a65833d451` | 624 |
| `evidence/results/computer_use_pid_binding_assessment.md` | `77301df244cb8cea979da2ff1ce9dc634d11a400c710c9a38eb6f4bd5d22e13b` | 2038 |
| `evidence/results/dynamic_closure.json` | `ce650771deb6681fde1681b1cc5d3384703ac54d8a01a61268a1e588b6069336` | 18469 |
| `evidence/results/manifest_verification.json` | `f948f864c5f892389df597f84a39f64759d9078b1ee78788c8bbae33cab4daaf` | 199 |
| `evidence/results/results.json` | `e8981412aa4e5f543b52bb57147bf6f1d74e2f8ee096d02ab5a513b1e8c50cba` | 4080 |
| `test_plan.json` | `3550b9c5da4c4fc46d4d55bf840c39fc0eb73bcb1115f37a72b587657cac6845` | 7068 |
| `tools/build_blocked_results.py` | `9a72846e99815095ea9d9b8db89e217905ce90c1a4561531fd839835c7661958` | 3546 |
| `tools/build_manifest.py` | `f1d642984acd5a29ec0e95dc9a9c2faa56890c3cbb33fe45f69429732febd279` | 1803 |
| `tools/pid_window_attest` | `b6856a527d14b31542243871d2dd8fe64e4d4d5693bcbb5c2554220c9d43e45f` | 168560 |
| `tools/pid_window_attest.swift` | `bacb9e7275fef2cbbe6201f4c64cc60af26678fb0274242c0b9eac65c2819931` | 4010 |
| `tools/record_prelaunch_cleanup.py` | `d9ea613b0ededcbf0b52567a60b469e302cf5a505276235c120e37ad4a1990f3` | 1268 |
| `tools/static_audit.py` | `d67b04e8397e66a11158501b915981b90c68fddbfb3acb1c4e7b955bc3d8246d` | 1807 |
| `tools/verify_blocked_package.py` | `dfff6be622183148a323aa7265a06c7d8ad7e9388d6558a00edd0cfc5ac87eeb` | 2073 |
| `tools/verify_manifest.py` | `c126052581e5929e8b99bf476011eeaee45b2dd1b6659cd4864cadf6cdc46e4e` | 1834 |
| `tools/verify_preflight.py` | `087258008d8ed2c277103609d96d6e2701177c2e36adfff3059b4cc735b2b85a` | 4934 |
