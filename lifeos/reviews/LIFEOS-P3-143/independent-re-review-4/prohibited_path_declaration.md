# Prohibited-Boundary Declaration — LIFEOS-P3-143 Independent Re-review-4

This reviewer declares that the following are prohibited from every existence check, `stat`, hash, inventory, read, copy, mutation, command argument, environment probe, screenshot, cleanup, and derived artifact:

- Pilot-6, every other Pilot, and every retained or old runtime root.
- Real databases, real user paths/files/text, personal Context, Memory, Health, exports, and any real credentials.
- DeepSeek and every other Provider authority, endpoint, proxy, DNS/redirect operation, network receipt, API key, environment credential, or actual Keychain item.
- Any second `/private/tmp/lifeos-p3-143*` root, including a root derived from another run-id.

Only the exact synthetic root declared in `test_design.md` is permitted. No real page text will be read; native evidence is restricted to identity, role, geometry, screenshot dimensions, and target-window binding. Candidate, engineering, historical-review, task, and PM assets are strictly read-only.

If a prohibited-boundary contact would occur, the reviewer stops before executing that operation and reports it; it is never normalized as test coverage.
