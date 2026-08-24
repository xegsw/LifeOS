# SP-02 Reconciliation Report

- Initial observed Markdown artifacts: 12.
- Normal incremental: add/modify/delete = 1/1/1; expected 1/1/1.
- Missed watcher event: reconciliation recovered 1 unobserved add; expected 1.
- Offline changes: add/modify/delete = 1/1/1; expected 1/1/1.
- Explicit moves: 20/20 (100%); wrong strong merges: 0.
- Copy-delete: automatic moves 0; candidates 1.
- Temporarily unreachable: no read, not represented as deletion or latest. Recovery found 1 new file.
- After disconnect: watcher active = false, new reads = 0.

The event watcher is a simulated subscription flag, not a frozen watcher library. Correctness comes from periodic full reconciliation. Automatic movement requires a unique unchanged local platform file key; path and content hash are observations, not permanent identity. Hash-only matches create new Artifacts plus candidate Links.
