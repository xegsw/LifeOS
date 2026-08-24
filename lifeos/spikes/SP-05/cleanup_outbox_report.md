# Cleanup outbox report

- Deterministic idempotency key: `sha256(command_id + node_id)`.
- Lease generation increments on claim; an expired lease can be reclaimed.
- Cleanup effect and verification are idempotent; a crash after effect but before status converges on retry.
- Retry exhaustion produces a visible dead letter and keeps active blocking.
- Machine checks: {'total': 6, 'passed': 6, 'failed': 0}.
