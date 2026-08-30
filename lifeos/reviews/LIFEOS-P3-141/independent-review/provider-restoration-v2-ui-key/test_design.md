# LIFEOS-P3-141 Provider Restoration v2 UI Key Closure — Independent Review Test Design

## Status and independence

- Review type: ABF-P3-141-v2 Mandatory Independent Review / fresh isolated re-review.
- Candidate is read-only and must not be contacted until this document, `write_allowlist.md`, and `precontact_seal.json` are written and sealed.
- This review owns every executable test, synthetic fixture, capture, receipt, screenshot, AX record, manifest, verifier, mutation payload, and cleanup record it relies on.
- Prohibited: any contact with Pilot-6 or its retained database; real Provider endpoints, credentials, real text, public network; candidate modification; PM ledger/risk/freeze/stage modification.

## Review-owned roots

- Persistent review root: `lifeos/reviews/LIFEOS-P3-141/independent-review/provider-restoration-v2-ui-key/`.
- Only disposable root: `/private/tmp/lifeos-p3-141-provider-restoration-v2-ui-key-independent-review-v1`.
- All disposable test data use explicitly synthetic, non-sensitive fixture strings. No external network is permitted; test adapters must be loopback/offline only.

## Entry gates (all fail closed)

1. Read the specified Revision-2 contract, ABF-v2, fixed inventory, user confirmation, governance, predecessor reviews, PM intake, and attempt-3 Rework report from the main tree as immutable inputs.
2. Verify the candidate is the declared main lineage (`01b08f78`) and validate the frozen input inventory and the candidate engineering Manifest without writing the candidate.
3. Confirm the review write allowlist and the single disposable root before any build, test, app launch, or mutation.
4. Bind every dynamic run to the exact candidate source hash, produced binary hash, runtime root, PID, AXWindow, AXWebView and screenshot/receipt. Missing any required binding is a failed/Unknown check, never inferred from a candidate assertion.

## Independent validation matrix

| ID | Independent check | Required positive fact | Negative/fail-closed control |
| --- | --- | --- | --- |
| IR-01 | Lineage and engineering Manifest | Exact candidate revision and manifest fields/hash inventory independently recompute | Altered fixture manifest/hash must make review verifier fail |
| IR-02 | UI adapter/runtime-key closure | UI adapter uses the current runtime key; legacy `p3-130-capture-001` is absent from relevant candidate/build/runtime evidence | Inject legacy key into disposable copy/evidence and require detection |
| IR-03 | Review-owned Capture | In actual Tauri, click `仅保存这条 Work` using a synthetic record; receipt succeeds and is not `argument_schema_rejected` | Malformed/omitted argument controls reject before persistence and do not report success |
| IR-04 | Provider profiles and selection state | OpenAI, Anthropic, Ollama, LM Studio and Custom OpenAI-compatible are independently represented; DeepSeek/Kimi are Custom semantics | Unsupported provider/profile/endpoint state rejects before any send |
| IR-05 | Explicit transition and send lock | Test -> select -> enable is explicit; first send locks selected provider/model and no implicit send occurs | Send before enable and post-lock switching fail closed/no request emission |
| IR-06 | IPC surface | Exactly 20 registered IPC commands match the frozen list | Missing, duplicate or extra command control fails verifier |
| IR-07 | Phase-C v2 receipt/build gate | Only valid v2 receipt/build gate enables Phase-C path | v1, absent, malformed, or mismatched receipt are rejected before Phase-C |
| IR-08 | Semantic mutations | At least four non-trivial disposable mutations against independently parsed evidence/semantics fail with their expected reason | Untampered pristine control passes |
| IR-09 | Desktop geometry | 1280x1024 actual Tauri usable state is bound PID -> AXWindow -> AXWebView | Missing/mismatched identity/bounds fails, never falls back to app name |
| IR-10 | Compact geometry | 700x760 actual Tauri usable state is bound PID -> AXWindow -> AXWebView | Same binding negative control |
| IR-11 | Narrow geometry | 560x640 actual Tauri usable state is bound PID -> AXWindow -> AXWebView | Same binding negative control |
| IR-12 | Lifecycle safety | Restart preserves expected controlled state; failures close; no implicit external/real send | Unavailable/invalid adapter leaves no send/audit success claim |
| IR-13 | Final integrity and cleanup | Self-authored manifest verifier checks hashes, lineage, semantic records, all markers, and exact cleanup | Delete/alter a required marker or retain a listed temp artifact; verifier must fail |

## Stop rule

Any P0 (including forbidden-path contact, candidate mutation, weak/absent binding, real-network/provider/credential access, Phase-C v1 binding, non-review-owned evidence, or verifier false positive) immediately ends positive validation. The candidate is not repaired and this review may issue only a failed/invalid conclusion with preserved permitted evidence and exact authorized cleanup.

## Bounded conclusion

Even if every review check passes, the conclusion is only an independent v2 technical receipt in the synthetic/offline scope. It is not PM acceptance, real Provider enablement, R-0056 closure, any freeze, or Stage 4 approval.
