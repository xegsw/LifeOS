# P3-141 Provider Restoration v2 Gate — Test Design

## Scope

This is a narrow receipt/build-gate repair for Revision 2 only. The candidate starts byte-for-byte from commit `48a26320646219117b28e81cd77dd6c8206fe99c` and may change only `build.rs` and build-gate tests. Provider profiles, Adapter protocol, UI labels, IPC, Work/Health, Memory/State/Resolver, feedback, restart and root lifecycle are regression-protected, not redesigned.

## Positive synthetic proof

1. A Phase-C gate receipt under an explicit review-owned input root, with only the Revision-2 task identity, fixed-inventory identity, `ABF-P3-141-v2`, frozen ABF hash, current candidate commit/tree and a distinct independent-review Manifest identity/hash, authorizes a `phase_c_real` compile gate.
2. The authorized receipt is regular, non-linked, canonically under the explicit approved review root, schema-valid, size-bounded, has no duplicate keys or unknown fields, and hashes exactly to the supplied review Manifest identity.
3. The positive gate test uses a wholly fictional receipt and synthetic runtime under only `/private/tmp/lifeos-p3-141-provider-restoration-v2-gate-v1`; it does not launch Phase C, access a real root, call a Provider or use credentials/network.

## Fail-closed negative proof

Before runtime-root resolution or any write, reject: missing receipt/path, v1 ID/hash, mixed v1/v2 values, old attempt-8 receipt, old candidate commit/tree, stale or wrong review Manifest, Rework/Blocked verdict, dirty/uncommitted source identity, linked file/ancestor link, directory, malformed JSON, duplicate key, extra field, invalid field value, fallback field, and unexpected receipt root.

## Regression proof

Run the candidate offline synthetic test suite. Record the preserved 50 tests, including five Provider profiles/Adapters, Custom OpenAI-compatible loopback protocol, save→test→enable, first-send lock/no fallback/no repeat, exact 20 IPC, Work/Health, Memory/State/Resolver, feedback, failure atomicity, restart and receipt/root gates.

## Evidence and stop rules

No actual-Tauri work belongs to this engineering repair; a new independent review must acquire its own three direct-PID evidence. Preserve the failed independent review read-only. Create only a new source lineage, gate-test results, negative matrix, regression result, cleanup receipt and a non-self-referential Manifest. On any gate bypass, source drift, unexpected write root, real-provider/network attempt or prohibited-target operation: stop positive evidence and report P0.
