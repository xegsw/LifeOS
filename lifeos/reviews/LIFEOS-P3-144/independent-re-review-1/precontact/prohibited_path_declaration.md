# P3-144 Independent Re-review 1 — Prohibited-path and capability declaration

## Absolute prohibition

`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7` and every descendant, including its `capture.sqlite`, are prohibited during this Phase B review. The reviewer must not access, stat, exists-check, probe, enumerate, hash, create, read, write, copy, move, or clean up those paths. They are absent from command targets, allowlists, fixtures, manifests, inventory, and cleanup logic.

## Additional prohibitions

- No real DeepSeek request, no network egress, no proxy, redirect, fallback, retry, background send, or other Provider.
- No real credential, OS credential-store secret, personal content, personal database, or retained Pilot access.
- No modification of candidate, engineering evidence, PM ledger, risk, freeze, stage, P3-143 history, first P3-144 review, or Closure materials.
- No candidate/engineering/first-review/deliverable/manifest contact occurred before the precontact seal described in `seal.json`.

## Required handling

An attempted prohibited contact is P0/Irrecoverable Invalidation. An unavailable GUI or local tool is `Paused — Resumable` with a checkpoint, unless a more specific frozen stop condition applies.
