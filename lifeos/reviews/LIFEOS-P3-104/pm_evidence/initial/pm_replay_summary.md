# LIFEOS-P3-104 PM isolated replay summary

- Frozen ABF hash: PASS.
- Engineering Manifest: 68/68 PASS.
- Frozen historical inputs: 14/14 PASS.
- Cargo.lock: 438/438 inventory PASS; hash unchanged.
- Fresh copied candidate: `/private/tmp/lifeos-p3-104-pm-20pdjCDD/candidate`.
- Offline static checks: 44/44 PASS.
- Offline Rust tests: 6/6 PASS.
- Offline no-bundle debug build: exit 0.
- PM-reconstructed offline `.app` bundle build: exit 0.
- Submitted dynamic closure structure/hash verification: 17/17 PASS.
- PM actual-app actions: first open, save, repeat, conflict, atomic failure, unknown IPC, extra fields and close/reopen all PASS.
- PM negative startup matrix: lexical name, parent symlink, existing-target file symlink, hardlink, sidecar, stale shadow, tampered content and unexpected schema 8/8 PASS.
- PM-P3-104-CE-01 dangling final DB symlink: FAIL; actual app accepted and replaced the link while reporting saved.
- PM-P3-104-EV-01: submitted replay instructions do not include the exact offline bundle command/log required by the actual-app launcher.
- Final counts before remediation: P0=0, P1=1, P2=1, Unknown=0, Not Implemented=0.
