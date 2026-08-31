# P3-141 Revision 3 Bundle Lineage Closure v5 — Test design

## Design before Candidate contact

| ID | Requirement | Independent engineering proof | Fail condition |
|---|---|---|---|
| TD-01 | Exact v5 root authorization | `build.rs` and `runtime.rs` each accept only the literal `bundle-lineage-v5` addition while retaining all other root validation | Any generic path relaxation or non-listed Candidate change |
| TD-02 | Baseline product semantics | Source and copied resource scans require Cloud 5, Local 3, encrypted SQLite persistence, update/delete, 20 IPC and no session/environment product wording | Missing/merged Provider, old wording, credential or IPC regression |
| TD-03 | Source → bundle → binary | Candidate inventory, copied input inventory, bundle resource inventory, binary SHA-256 and binary text scan agree | Wrong tree, stale resource or binary mismatch |
| TD-04 | Mutation resistance | Disposable copies reject session wording, provider removal/merge, mode bypass, IPC regression, encryption removal, stale resource and wrong tree | Any mutation still validates |
| TD-05 | Native Settings evidence | For each 1280×1024, 1160×768 and 700×760: direct launched PID → unique exact-title AXWindow → AXWebArea/WebView → frontmost matching frame → bounded target-only capture; assert Settings UI semantics | Any missing chain element, overlap/frame change, pixel-scale mismatch or capture outside target window |
| TD-06 | Cleanup and archive | Wrong/missing/symlink markers reject; only exact v5 root cleans; read-only verifier recomputes hashes and requires root absent | Any cleanup overreach, residual root or verifier mismatch |

No test uses Pilot-6, actual personal data, real credentials, real Provider/network, cloud, desktop capture or full-screen capture.
