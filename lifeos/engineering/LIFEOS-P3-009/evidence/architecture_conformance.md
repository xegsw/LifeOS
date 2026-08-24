# T-ARCH conformance

- Executable: Node/TypeScript modules use built-in SQLite and FTS5; immutable authority, normalized derivation inputs, important links/evidence, outbox/job, tombstone and authorization responsibilities are separate.
- Executable: every implemented consumer and important-link write receives explicit context and fails closed on project, version, artifact/source generation, tombstone, purpose, location, processor, evidence, authorization mismatch or authorization expiry; expiry tests use an injected deterministic clock.
- Executable: feedback IDs are insert-once; duplicate, conflicting and post-retraction writes fail closed without changing user text or status. Explicit user feedback retraction is idempotent, retains feedback history, removes confirmed/edited-confirmed Derivation authority and does not revive stale, invalid or unauthorized Derivations.
- Executable: read-only restore candidate evaluation re-reads current authority and verifies package content hashes, identity and the complete derivation_input set without writing authority, FTS or outbox; derivation.evidence_version_id remains legacy compatibility/display metadata only.
- Executable: suggestion IDs bind Project and the stable-sorted complete input set, including exact evidence version, Artifact, Source and both generations; revoke/delete or an independent current-generation mismatch of any input makes the old derivation stale and prevents ID reuse.
- Executable: index failure does not roll back an already committed authoritative capture.
- Closed: real Tauri/IPC, Vault, filesystem export, cloud/model, vector, sync/multi-device, L3 and external users.
- Mapped, not executable here: process-kill durability, lease fencing race, long FTS rebuild nonblocking, SQLite-aware real backup/restore/write-back and model-provider replacement boundary.
- No claim: production schema/API/module boundary/package strategy/export format/SLA freeze. R-0040 is unchanged.
