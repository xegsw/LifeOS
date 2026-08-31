# P3-141 Revision 3 Bundle Lineage Closure v4 — Prohibited-path declaration

## Absolute prohibitions

- Do not access, probe, stat, hash, read, copy, create, write, remove, or clean Pilot-6, its database, its sidecars, or any real-data root.
- Do not access real text, Health values, real Provider endpoints, API keys, credentials, network, cloud, system Keychain, Vault, or system permissions.
- Do not access or mutate Revision 1, Revision 2, or v3 historical temporary roots. v3 records are immutable historical inputs when explicitly listed after this seal.
- Do not capture the desktop, a full screen, another application, or any region outside the exact target native window.
- Do not use bundle/application/frontmost-window substitution for direct-PID proof.
- Do not create, write, scan, or clean outside the v4 temporary root declared in the run plan, except the exact workspace paths in the write allowlist.

## Fail-closed rule

If direct PID → unique exact-title AXWindow → AXWebArea/WebView → bounded target-window capture cannot be established, stop positive GUI validation. No compact/narrow substitution, synthetic screenshot, browser screenshot, or desktop fallback is allowed.
