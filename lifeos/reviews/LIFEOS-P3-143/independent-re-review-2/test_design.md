# LIFEOS-P3-143 Mandatory Independent Re-review-2 — Test Design

Status: pre-contact design; authored before any candidate, engineering-Evidence, or historical-Review contact.

## Scope and independence

This review will treat commit `dcbc32518d92e16e26f8c7dfec682630f5d51cde` as read-only. It will create no candidate code, import no candidate tests as proof, and use only a new review-owned test harness, a new review-owned synthetic runtime root, and a new synthetic SQLite database.

## Ordered method

1. Verify the fixed commit, the 126-entry Engineering Manifest, the listed closure evidence, and the precise historical lineage as immutable inputs.
2. Derive a review-owned build and run entry point from the fixed candidate without modifying the candidate. Bind each dynamic run to its exact executable/source digest.
3. Run two distinct valid independent-review run IDs. Record rejection before writes for short, long, case-variant, separator, traversal, absolute-path, unknown-profile, engineering-review-mixed, and environment-path-injected IDs.
4. Exercise missing-root creation, then create an existing-root/no-marker sentinel fixture. For every invalid marker/root/DB form, attest that no file, runtime, DB, Keychain, network, or state write occurs and that the sentinel/tree metadata stay unchanged.
5. Independently check Cloud8/Local4 and exactly 20 IPC declarations without a real Provider call, credential read, network access, or Keychain access.
6. Where actual-Tauri is contract-required and the desktop services are available, record a fresh direct PID to exact-title AXWindow to AXWebView/Area chain and screenshot/geometry. If unavailable, checkpoint and mark only that GUI portion Paused — Resumable.
7. Verify exact marker-gated cleanup on only this review's synthetic root, including reject controls for missing, wrong, and symlink markers.

## Pass rule

Pass requires review-owned positive and negative evidence for every applicable line, a non-self-referential manifest, a verifier that recomputes its inputs, no prohibited-boundary contact, and a clean exact-root cleanup. A missing frozen input, a pre-contact-order breach, a candidate modification, or a required dynamic GUI evidence gap follows the contract stop/paused rule rather than being inferred away.
