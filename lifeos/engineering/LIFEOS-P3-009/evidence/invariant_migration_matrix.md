# H1-H9 / T-ARCH migration matrix

| Invariant | Status | Executable coverage | Boundary / residual |
|---|---|---|---|
| H1 / T-SCOPE | Executable PASS | personal, local, single-device slice and capability closure | no UI/value validation |
| H2 / T-ID | Executable PASS | immutable user original; stable suggestion ID binds Project plus sorted complete input/version/source/generation set; explicit feedback retraction preserves history while removing confirmation authority; confirmed important-link identity/source/version/evidence binding | external-reference adapter mapped only |
| H3 / T-SAVE | Executable PASS (narrow) | SQLite transaction rollback; authority survives index failure; idempotent outbox shape | process-kill/fsync/durability remains unmigrated |
| H4 / T-GATE | Executable PASS | read/search/recovery/suggest/feedback/export, read-only restore candidate evaluation and important-link writes recheck project, purpose, location, processor, version, generations, tombstone, evidence, authorization and optional expiry against an injected deterministic clock; restore candidates re-read current authority and reject package content/identity mismatch | real time service/IPC/external processor absent |
| H5 / T-DEL | Executable PASS (active block) | delete/revoke/authorization expiry of any derivation input and independent artifact/source generation mismatch block feedback/export/suggest; explicit user feedback retraction is idempotent, retains the row, removes confirmed authority and never revives stale/invalid/unauthorized Derivations; old memory packages cannot revive blocked or stale Artifact/Derivation candidates | physical cleanup and formal restore/write-back protocol unmigrated |
| H6 / T-IPC-OFF | Executable PASS (closed state) | Tauri, Vault and filesystem export throw | real Tauri matrix deliberately not run; R-0040 remains |
| H7 / T-DATA | Executable PASS (synthetic) | fixture classification and secret/path/email pattern scan | no real-data gate |
| H8 / T-OFF | Executable PASS | all eight excluded capability calls reject | no enablement path exists |
| H9 / T-EXPORT | Executable PASS (memory) | Project closure, content identity, minimum authority projection and read-only restore candidates in controlled memory package | final UI, filesystem format and real backup/restore unmigrated |
| T-ARCH | Executable PASS (minimum) | SQLite+FTS-first; authority/derivation inputs/important links/outbox/tombstone separation; consumer/write recheck | lease fencing, long rebuild nonblocking and SQLite-aware backup mapped but unmigrated |

Status is limited to this synthetic single-process skeleton and is not production or capability approval.
