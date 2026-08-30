# P3-141 final-bundle screenshot identity review

## Current positive screenshot evidence

Manual visual inspection of the native top bar was performed after each direct-PID AX binding and capture. The visible title in every retained frame is exactly `LifeOS · P3-141 Controlled Pilot Candidate`.

| Viewport | Direct launch PID | AX proof | Retained image | SHA-256 | Visible native title |
|---|---:|---|---|---|---|
| desktop | 22698 | 1 AXWindow, title exact, 1 AXWebArea | `screenshots/desktop_redacted_state.jpeg` | `1164f6dc80fd1f112201e98cd5dc88044cb224a3ad76f43ac76f5b4d9cd38643` | `LifeOS · P3-141 Controlled Pilot Candidate` |
| compact | 22049 | 1 AXWindow, title exact, 1 AXWebArea | `screenshots/compact_redacted_state.jpeg` | `b70ba3b4fde61ea358a89411ec60067fb26ef7587e2ad629f7ef1957f24d935c` | `LifeOS · P3-141 Controlled Pilot Candidate` |
| narrow | 22474 | 1 AXWindow, title exact, 1 AXWebArea | `screenshots/narrow_redacted_state.jpeg` | `caaf22a5719b88334a5440324580bffb4d1b2c244a03b5ef2f931108018ead59` | `LifeOS · P3-141 Controlled Pilot Candidate` |

The body continues to display the retained P3-140 Today semantic surface; that is not the candidate identity. Only the native title specified above is used as the screenshot identity assertion.

## Invalidated previous evidence

The compact and narrow images committed in `4960a36e77bbb816a58bfaee34c89f6d17eca8d9` are **not positive Evidence**. Human visual inspection showed their top bars as `LifeOS · P3-140 Cross-domain Today`, while the former `actual_tauri_viewports.json` asserted the P3-141 candidate title. Their prior PIDs and hashes are retained in `actual_tauri_viewports.json` and `failure_history.md`; the files were replaced only after that invalidation was recorded.

All current and invalidated screenshots are fixed synthetic UI only. No real Pilot, personal content, Health values, credential, Provider traffic, or network response was inspected or recorded.
