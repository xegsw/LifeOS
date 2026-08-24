# Sync strategy comparison

| Strategy | Strength | Failure/cost in SP-06 | V1 disposition |
|---|---|---|---|
| Server authority + immutable versions + append-only Feedback/operation log | Simple deterministic ordering, explicit conflicts, strong fences | Requires server availability to reconcile; conflict UX needed | Recommended candidate |
| Field-level LWW | Cheap and superficially convergent | Silently drops original edits and user accept/reject/correct intent | Prohibited for authoritative fields |
| Finite CRDT | Useful for narrow commutative fields or future collaborative text | Adds causal metadata, merge policy, tombstone/authorization interaction; no V1 multiplayer need | Not justified now; reconsider per-field with evidence |
| Queue as authority | Easy async plumbing | Retry, stale lease, policy and tombstone races can publish old state | Prohibited; queue is execution aid only |

This comparison does not freeze a protocol, database, event stream, or service topology.
