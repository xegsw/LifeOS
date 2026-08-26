# LIFEOS-P3-121 PM Design Contract Counterexamples

## Scope

This is a read-only PM comparison of the Frozen P3-116 source/contract against the current P3-121 candidate and current actual-App Evidence. It does not modify either candidate, does not rerun Tauri, does not access Pilot or real data, and does not introduce a new acceptance requirement.

## Existing L1/L2 mapping

| Finding | Frozen mapping | P3-116 source | P3-121 current candidate / Evidence | PM conclusion |
|---|---|---|---|---|
| Rail labels are permanently visible instead of icon-only with hover/focus disclosure | ABF-I-02; M-003; M-019 | `styles.css:35-40` defines icon buttons and tooltip opacity 0 until hover/focus | `candidate/ui/styles.css:21-24` renders `.rail-button em` at 10px permanently | P1 contract violation |
| Shell, brand and primary type scale are compressed | ABF-I-02; M-003; M-004; M-019 | `styles.css:31,33,65,88` uses 92px rail, 56px brand, 43-58px Today heading and larger focus surface | `candidate/ui/styles.css:17,19,26,32` uses 80px rail, 39px brand, materially smaller hierarchy and 202px focus minimum | P1 contract violation; weak Dashboard/personal-space hierarchy is not faithfully inherited |
| Runtime/debug state occupies the product shell and Global AI area | ABF-I-02; M-003; M-004; M-019 | `styles.css:174` keeps a centered, spacious Global AI composer with Quick Capture secondary | `candidate/ui/styles.css:29,42` adds runtime pills/notices and compresses the composer into a control cluster | P1 contract violation; Runtime must remain a minimal data connection rather than reshape the product hierarchy |
| Three exact actual-App viewports are absent | ABF-I-03; M-009 | Frozen responsive contract requires 1280x1024, 1160x768 and 700x760 actual-App rows | `actual-app-trace.json:M-009` reports `NOT_IMPLEMENTED`; three resize attempts returned `noWindowsAvailable` | Not Implemented 1 |
| M-019 self-check is too coarse for the Frozen visual contract | L1-6; L1-7; L1-10; ABF-I-02; M-019 | Frozen source makes the rail disclosure, scale, spacing and Global AI relationship directly observable | `actual-app-trace.json:M-019` only checks narrow rail, off-white hierarchy and absence of forbidden chrome | M-019 PASS is not accepted by PM |

## Rework closure boundary

- Keep the existing Tauri/WebView architecture and the same three IPC commands.
- Directly inherit the P3-116 layout, visual tokens and interaction behavior; do not redesign or compress them.
- Restore icon-only Rail with hover/focus labels, P3-116 whitespace, type scale, identity colors and Global AI spatial relationship.
- Inject Runtime only as the minimum synthetic data/status connection; do not add product-shell density or debug-dashboard chrome.
- Produce actual-App Evidence at exactly 1280x1024, 1160x768 and 700x760 using the same DOM, with main actions and composer reachable.
- Preserve the current Frozen ABF, directories, synthetic DB, three IPC, history and prohibited capabilities.

## Counts

- P0: 0
- P1: 1
- P2: 0
- Unknown: 0
- Not Implemented: 1

