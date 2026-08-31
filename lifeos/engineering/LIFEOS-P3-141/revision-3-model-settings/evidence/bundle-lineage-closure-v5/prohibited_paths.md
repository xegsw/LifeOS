# P3-141 Revision 3 Bundle Lineage Closure v5 — Prohibited-path declaration

- Do not access, probe, stat, hash, read, copy, create, write, remove or clean Pilot-6, its database, sidecars or any real-data root.
- Do not access real text, Health data, real Provider endpoints, API keys, credentials, network, cloud, Keychain, Vault or system permission data.
- Do not mutate v1, v2, v3 or v4 historical artifacts. v4 is a read-only blocked history and cannot supply positive Evidence.
- Do not access old temporary roots. Only the exact v5 root is permitted.
- Do not capture the desktop, full screen, another application or any region beyond the exact bound target AXWindow.
- Do not replace direct-PID proof with bundle, app-selector, frontmost-window or cached-window proof.

If the full direct PID → unique exact-title AXWindow → AXWebArea/WebView → target-window-only capture chain fails, stop positive GUI validation. Do not substitute compact, narrow, browser, synthetic, desktop or full-screen evidence.
