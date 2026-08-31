# P3-141 Revision 3 v5 native visual review

## Scope and method

This is a human review of three images captured only from the direct launch PID's
unique, exact-title `AXWindow` frame.  The associated pre- and post-click JSON
records prove the direct PID, exact title, unique `AXWindow`, `AXWebArea`, stable
frame, frontmost state, no overlap, and backing scale before the capture.  The
Settings click was an accessibility-button frame click inside that same window;
it was not a desktop-coordinate or full-screen fallback.

## Observations

| Viewport | Image SHA-256 | Visible result |
| --- | --- | --- |
| desktop (1280 x 949 pt) | `4016f9a94ea627e66c5e7c61e450636912b90e8d783612a93f45048b11f634a2` | Settings page; cloud card lists OpenAI, Anthropic, DeepSeek, Kimi, and an OpenAI-compatible service; local card lists Ollama, LM Studio, and a local-compatible service; OpenAI selected; encrypted controlled-local SQLite/key-separation notice; distinct save, save-key, and test controls. |
| compact (1160 x 768 pt) | `a79c3b015f1e1ea08421eb7fb2e004884153fb755f10d55ec672f9006f522a01` | Same Settings mode, provider boundaries, OpenAI selection, and encryption/key-separation notice in the compact layout. |
| narrow (700 x 760 pt) | `a8c51070bb5949bc49163a45e57c1368e435e1782e2e7ed73d0d0b20599d5c0a` | Same Settings page and provider boundaries in the narrow layout; the lower form continues below the target-window viewport, which is expected responsive clipping rather than a substituted screen. |

The page has no visible `本次会话` wording in these actual-App captures.  This
visual fact is not used as an exhaustive textual/semantic proof: the static
contract and mutation records provide that coverage.  `删除已保存 API Key` is
not expected in this empty-credential synthetic state; its update/delete
semantics are covered by the offline Rust regression rather than a fabricated
credential interaction.

## Limits

This review proves only the synthetic/offline actual-app surface bound to the
recorded PIDs.  It does not authorize real credentials, a real Provider, Pilot,
Phase C, an independent review, PM acceptance, or a product/stage decision.
