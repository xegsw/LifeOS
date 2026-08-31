# P0 observation: actual Settings UI exposes session-only credential semantics

## Binding facts

- Directly launched app PID: `5841`.
- Exact native window title: `LifeOS · P3-141 Controlled Pilot Candidate`.
- Native accessibility chain: that PID → one exact-title `AXWindow` → `AXWebArea`.
- Native frame at capture: `x=221`, `y=33`, `width=1280`, `height=949`.
- A fresh display-scoped capture was taken immediately after the recorded PID/title/WebArea binding because macOS did not expose `AXWindowNumber`. It was then precisely deleted: the display fallback included unrelated desktop information and therefore violated the task's zero-real-text boundary. No screenshot is retained in the review package.

## Direct observation

The rendered Cloud Settings screen states all of the following in Chinese:

- `本次会话 API Key 已提供；输入可更新`
- `API Key 仅保留在本次会话，可随时清除。`
- `清除本次会话 API Key`

## Finding and effect

This is a P0 contradiction of the frozen Revision 3 requirement that API keys are encrypted SQLite credentials that persist across restart and are managed by store/update/delete; the product must not expose session or environment credentials as an option. It also conflicts with the required delete wording and lifecycle boundary.

Per the task contract, this actual-Tauri P0 ends positive validation immediately. Independently, the display-capture boundary failure invalidates this review attempt as an independent review. No conclusion of independent Pass, PM Accepted, Phase C restoration, Pilot-6 authorization, real Provider authorization, risk closure, product freeze, or Stage 4 readiness is available from this review.
