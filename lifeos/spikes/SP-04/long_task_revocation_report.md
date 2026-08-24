# Long-task revocation report

| Checkpoint | Decision | Output state |
|---|---|---|
| enqueue | DENY | quarantined |
| execute | DENY | quarantined |
| derive_segment_1 | ALLOW | ephemeral_not_published |
| derive_segment_2 | DENY | quarantined |
| publish | DENY | quarantined |
| index | DENY | quarantined |
| recovery_package | DENY | quarantined |

Revocation is injected before segment 2. Segment 2 and all later publish/index/recovery-package checkpoints deny; the race output remains quarantined and therefore cannot become visible, searchable, or recoverable.
