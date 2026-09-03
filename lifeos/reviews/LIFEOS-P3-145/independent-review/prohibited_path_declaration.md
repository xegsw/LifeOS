# LIFEOS-P3-145 Phase B — Prohibited Boundary Declaration

For the entire Phase B attempt, the reviewer must perform zero `access`, `exists`, `stat`, `probe`, `hash`, `read`, `create`, `write`, or `cleanup` against the retained real-user root `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7`, its `capture.sqlite`, or any content beneath it. The same zero-contact rule applies to all real personal text, real credentials, credential storage, real Provider endpoints, and all network targets.

These real paths and data must not be placed in shell commands as targets, environment variables, test fixtures, cleanup lists, screenshots, hashes, logs, or Evidence. This declaration names the prohibited boundary solely to make the prohibition auditable; it does not authorize inspection.

Only a newly created synthetic DB and fixed non-sensitive canaries under the review-owned temporary root are permitted. Any prohibited-boundary contact is a P0 irrecoverable invalidation: immediately stop, preserve the failed history, do not perform cleanup of the prohibited boundary, and report `Invalidated Attempt`.
