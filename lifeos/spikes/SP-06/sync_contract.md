# SP-06 minimum sync contract

This is a candidate verification contract, not a frozen Schema or API.

1. Every client mutation carries a globally unique `operation_id`, stable `device_id`, operation kind, target, payload digest, and the relevant `base_version` / generation snapshots.
2. Reusing an `operation_id` with the same envelope returns the recorded result and increments an explainable retry count; a changed envelope is rejected.
3. Artifact versions are immutable. A matching base advances the server-authoritative current pointer; a stale base is retained as a conflict branch and never silently overwrites.
4. Action, Decision, Link, candidate decisions, and Feedback use object-level compare-and-append. A stale base becomes an explicit conflict; client time never wins.
5. Feedback is append-only. Retraction is a new event referencing the prior event. Current state is a projection over effective events, never a rewrite of history.
6. Tombstone / restriction generation, Authorization version, and policy version are monotonic server-authoritative fences. Unknown or stale snapshots fail closed.
7. A queue is transport only. Before visible publication, a task rechecks object version, Authorization state/version, policy version, tombstone generation, source state, and an owner+generation lease fence.
8. AI candidates remain Derivation identity. Only an explicit, matching user operation can create a user-authority projection; AI generation cannot confirm itself.
