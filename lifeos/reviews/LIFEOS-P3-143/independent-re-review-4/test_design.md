# LIFEOS-P3-143 Mandatory Independent Re-review-4 — Test Design

## Review identity and sealed execution constants

- Review: `independent-re-review-4` (fresh isolated independent review; reviewer-owned Evidence only).
- Composite fixed commit: `4f4e6ff2`.
- Candidate business-code commit: `dcbc3251`.
- `6935abde`, `a95a0beb`, and `4f4e6ff2` are history-review-only additions; they are not substituted for candidate proof.
- Sole permitted candidate runtime root, exactly: `/private/tmp/lifeos-p3-143-independent-review-finalgui-20260902`.
- Sole build profile, exactly: `independent-review`.
- Sole run-id, exactly: `finalgui-20260902`.

Every Rust harness, candidate build, fresh `.app` bundle, direct launch, root-matrix case, and cleanup must use the exact same profile, run-id, and literal root above. A command whose effective run-id differs must not be executed. No second `/private/tmp/lifeos-p3-143*` root may be created; invalid run-id coverage is build-time rejection only.

## Independence, permitted scope, and safety boundary

The reviewer will read candidate, P3-143 engineering Evidence, and named review history only after this document, the allowlist, prohibited declaration, and precontact seal are written and hashed. All candidate, engineering, task, and historical review inputs remain read-only. This review writes only its own output directory and creates/removes only the sealed single runtime root.

No Pilot-6, other Pilot, real database, real user path, real text, personal Context/Memory/Health, Provider endpoint, API key, Keychain credential, proxy, network connection, or real-Provider receipt may be accessed, probed, hashed, read, copied, modified, or cleaned. The review is synthetic and offline; no page text will be read during native UI evidence.

## Method and acceptance checks

1. Verify the fixed inputs and commits once after the seal, freeze their hashes/state, and stop on missing or inconsistent input.
2. Build review-owned Rust harnesses against the fixed composite source. Re-run the root-authority positive and negative matrix, write-before invariants, Cloud 8 / Local 4 preservation, exact 20 IPC assertion, action separation, and DeepSeek authority/no-proxy/no-redirect static checks.
3. Run two required semantic mutations and the stated negative root cases without altering the candidate. For every root case, stop writers then marker-gate the reset; retain case records showing sentinel/DB/filesystem pre-write invariants.
4. Build a fresh actual `.app` using the sealed constants. Obtain a new direct system-launch PID, bind that exact PID to exact title `LifeOS · 模型设置（安全凭据验证）`, then AXWindow and AXWebArea/WebView. Capture only target-window desktop/geometry Evidence at 1160×768 and 700×760 without reading page text.
5. Stop the exact PID, exercise wrong/missing/symlink marker refusal in review-owned disposable controls, then marker-gated clean the single literal root and prove absence.
6. Produce a review-owned matrix, verifier, checkpoint, independent review, and non-self-referential final manifest. The conclusion may be `Independent Pass` only if all applicable contract evidence is re-run in this review and counts are P0=0, P1=0, Unknown=0, and Not Implemented=0.

## Failure handling

- Missing frozen inputs, input/hash identity conflict, precontact breach, prohibited-boundary contact, or read-only modification: stop and record the stipulated failing/invalid state.
- Locked desktop, unavailable AX, screenshot service, or temporary evidence tooling failure: checkpoint `Paused — Resumable`; stop writers/App and resume only from the affected phase.
- An invalid run-id is rejected before runtime creation. A marker-gate failure refuses cleanup. Neither condition authorizes another runtime root.

## Non-claims

This review does not rerun the real DeepSeek Gate, request or observe credentials, close risks, alter Frozen status, or authorize Stage 4. It does not substitute any earlier review result for evidence generated during this review.
