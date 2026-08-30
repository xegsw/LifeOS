# LIFEOS-P3-141 Provider Restoration v2 UI Key Closure: Independent Review Test Design

## Identity and isolation

This is a fresh, review-owned, read-only assessment of candidate commit `633014f8`, limited to `lifeos/engineering/LIFEOS-P3-141/closure-provider-restoration-v2-ui-key/candidate/`. No prior review PID, window, WebView, capture, fixture, database, tool output, or conclusion will be used as evidence.

## Prohibited subjects

Do not access any Pilot-6 root or `capture.sqlite`; do not access real Provider endpoints, credentials, user text, or the public network. The candidate is never repaired. A P0 stops the positive-path examination immediately.

## Binding gate (first dynamic gate)

For every launched candidate viewport, review-owned Swift/CoreGraphics/Accessibility code must use the exact PID returned by that launch to bind `PID -> native AXWindow -> AXWebView` while the process remains alive. Bundle identifiers, application names, the frontmost window, and any pre-existing window are prohibited substitutes. On failure, retain only the process state plus direct PID-scoped raw error and fail closed.

## Verification sequence after binding

1. Independently inventory candidate engineering manifest and validate lineage/fixed inputs.
2. Verify UI/runtime provider-key alignment and removal of the old key.
3. Exercise a synthetic offline actual-Tauri save through the label `仅保存这条 Work`.
4. Check five provider semantics, explicit test -> select -> enable state progression, and first-send locking.
5. Check exactly 20 IPC operations, ABF-v2 build/receipt gates along positive and negative paths, at least four semantic mutations, restart, failure-close, and no implicit send.
6. Repeat native PID/window/WebView binding for 1280x1024, 700x760, and 560x640 viewports.
7. Generate review-owned verifier output and a non-self-referential manifest. Execute only marker-gated, literal-path cleanup under the one authorized temporary root.

## Decision rule

Only a fully evidenced binding gate and all required checks may produce an independent limited-scope PASS and v2 receipt. Any P0, binding failure, unavailable evidence capture, identity ambiguity, prohibited contact, or verifier failure yields NOT PASS / fail closed, with no claim about PM acceptance, real Provider enablement, risk closure, freeze, or Stage 4.
