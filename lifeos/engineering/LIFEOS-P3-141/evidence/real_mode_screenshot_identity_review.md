# Receipt-enabled real-mode screenshot identity review

Each final retained frame was reviewed by eye after a direct PID launch and native AX/WebView state read. The visible native top bar in every frame reads exactly `LifeOS · P3-141 Controlled Pilot Candidate`; the body intentionally retains P3-140 Today semantics and is not used as the candidate-identity assertion.

| Viewport | PID | Screenshot | SHA-256 | Visible candidate title | Synthetic-only check |
|---|---:|---|---|---|---|
| desktop | 49613 | `screenshots/real_mode_desktop_redacted_state.jpeg` | `d5659960732be4dde4861e99ac23d8ccd10fca0d7164856ee0ccfa0bba6dd6bd` | exact | pass |
| compact | 49643 | `screenshots/real_mode_compact_redacted_state.jpeg` | `c56b55f3533aa4d74a673f47660a12f91787eccd8c2867989346f38f65954ff2` | exact | pass |
| narrow | 49714 | `screenshots/real_mode_narrow_redacted_state.jpeg` | `f509d5078d5110d404e0ea3c9144bfd2644345674bfad789c6b861b4bc868c71` | exact | pass |

The screenshots use obvious fixed synthetic work/health examples, say `离线 · 无 Provider`, and contain no real content, credential, Provider request/response, or network state. Old conflicting P3-140-title compact/narrow frames and the first receipt-enabled fixture-rejection desktop attempt remain failure history only.
