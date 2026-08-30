# LIFEOS-P3-141 Provider Restoration v2 UI Key Closure — Independent Review

## Conclusion

**PASS — bounded, synthetic/offline independent review only.**

This review is an independent, read-only assessment of frozen candidate commit
`633014f80e967b8b349a491f205d459e01662ef1`.  It establishes the Revision-2
receipt binding for the candidate tree digest
`275f021971f6f0f0d27406acac34befbd4054ccbe97c82eae273f2f91c9a6950`.

This is not PM acceptance; it does not enable any real Provider, close R-0056,
freeze an asset, or authorize Stage 4.

## Isolation, ordering, and P0 rule

- Before candidate/Git/search/tree contact, this review wrote and hashed
  `test_design.md`, `write_allowlist.md`, and `precontact_seal.md`.  The seal
  records hashes `0cefab4c18e15b0b968f029c3919ca02ee9c4a1cfaf1dd78c0b8b87fdcfcc506`,
  `334f027b47e8698e88b68e21acf5f119021530004a16d814b74ff431982d2a12`, and
  `2a29d34767cae9cd004c7701a647a3c8be92cea6ee23bd513f4a03d98a97febd`.
- The candidate was never modified.  All dynamic state used the single
  review-owned temporary root stated in `write_allowlist.md`; no real Provider,
  credential, public-network endpoint, user text, Pilot-6 root, or its
  `capture.sqlite` was accessed.
- The loopback fixture was review-owned at `127.0.0.1:11434`, recorded method
  and payload length only, and was stopped before the clean regression run.
- No P0 occurred.  Invalid preliminary runs (fixture active, then missing the
  required test-root variable) were preserved but excluded; the final clean
  run is the only test result counted below.
- The first receipt-generator revision sorted relative path strings rather than
  the candidate build's component-aware `PathBuf` order; the Phase-C gate
  rejected that receipt before runtime-root inspection.  The review-owned
  generator was corrected, the candidate digest was rederived, and the clean
  receipt is the only binding submitted for the positive gate.

## Direct-PID native binding gate

Each UI action used review-owned Swift Accessibility/CoreGraphics code.  It
starts from the PID returned by that candidate launch, obtains that exact
`AXApplication`, then an `AXWindow`, then an `AXWebArea`/`AXWebView`; the
same PID is rechecked before every bound interaction and capture.  It does
not query a bundle id, application name, frontmost window, or an existing
P3-137 window.

| Required viewport | Fresh candidate PID | Result | Evidence |
| --- | ---: | --- | --- |
| default 1280 x 1024 request | 1770 | exact PID/window/WebArea bound; host exposed 1280 x 949 | `evidence/raw/restart_direct_pid_1770.json`, `evidence/raw/desktop_1280x1024_geometry.jsonl`, `evidence/restart_pid_1770.png` |
| 700 x 760 | 2709 | exact PID/window/WebArea bound; post-set size 700 x 760 | `evidence/raw/compact_pid_2709_binding.json`, `evidence/raw/compact_700x760_geometry.json`, `evidence/compact_700x760_pid_2709.png` |
| 560 x 640 | 3555 | exact PID/window/WebArea bound; post-set size 560 x 640 | `evidence/raw/narrow_pid_3555_binding.json`, `evidence/raw/narrow_560x640_geometry.json`, `evidence/narrow_560x640_pid_3555.png` |

The first live candidate launch was also bound by its exact returned PID
`99006`; raw direct-binding records are retained in `evidence/raw/desktop_*`.
The desktop host's available work area capped a 1280 x 1024 native resize at
1280 x 949.  This is an explicitly recorded host limitation, not substituted
evidence: the candidate configuration declares 1280 x 1024 and the other two
required runtime sizes were observed exactly.

## Independent checks

- The review-owned source verifier reports the frozen synthetic key in runtime
  and UI, no legacy UI key, the exact ordered 20 IPC operations, five profiles,
  Custom's OpenAI-compatible adapter and visible cloud semantics, explicit
  test → select → enable ordering, first-send lock, and both Revision-2 gate
  checks (`evidence/raw/static_verifier_candidate.json`).
- Actual Tauri exercised the Chinese control **“仅保存这条 Work”** and closed
  the resulting modal; the review-owned synthetic runtime summary reports one
  capture and one audit row without reading content
  (`evidence/desktop_capture_modal.png`, `evidence/desktop_capture_after_save_closed.png`,
  `evidence/raw/desktop_synthetic_db_after_save.json`).
- The Settings screen displayed OpenAI, Anthropic, Ollama, LM Studio, and
  Custom.  Custom visibly covers “DeepSeek、Kimi 或 OpenAI-compatible 服务”.
  The loopback-only Custom flow visibly reached connection success, selected
  `review-fixture-model`, then enabled it
  (`evidence/desktop_custom_after_test.png`, `evidence/desktop_custom_enabled_attempt2.png`).
- A first Work AI request produced the synthetic observation/suggestion and
  one loopback POST; afterward a provider change was rejected with
  `provider_locked_after_first_send`.  After restart, the fixture log stayed
  at two model GETs and one send POST: no implicit resend
  (`evidence/desktop_work_ai_first_send.png`,
  `evidence/desktop_locked_profile_rejected.png`,
  `evidence/raw/restart_direct_pid_1770.json`).
- The final clean offline regression run set review-owned
  `LIFEOS_P3_141_V2_GATE_TEST_ROOT` and passed **54/54**: 50 runtime tests and
  four v2 receipt-gate tests (`evidence/raw/cargo_test_final_clean.log`).
- The negative Phase-C build rejects before runtime-root inspection when the
  explicit v2 receipt is absent (`evidence/raw/phase_c_v2_gate_negative_missing_receipt.log`).
- The positive Phase-C build, launched from the separately declared detached
  candidate worktree, accepted the committed v2 receipt and finished offline
  compilation (`evidence/raw/phase_c_v2_gate_positive.log`).
- Four independently generated semantic mutations all caused this review's
  verifier to fail: UI key mismatch, legacy key reintroduction, one missing
  IPC, and removal of the Phase-C v2 gate
  (`evidence/raw/static_semantic_mutations_v4.jsonl`).

## Counted result

| Category | Result |
| --- | --- |
| final clean tests | 54 / 54 passed (50 runtime + 4 receipt gate) |
| IPC | 20 / 20 exact ordered names |
| Provider profiles | 5 / 5 |
| semantic mutations | 4 / 4 rejected by the review-owned verifier |
| viewport direct bindings | 3 / 3 fresh PID → AXWindow → AXWebArea bindings |

## Review boundary

**Fact:** the bounded candidate and its synthetic/loopback mechanisms satisfy
the checks above.  **Inference:** this supports only an independent synthetic
PASS and its v2 Phase-C receipt.  **Not concluded:** PM Accepted, real Provider
activation, real personal-data use, risk closure, freeze status, or Stage 4.
