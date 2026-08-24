# SP-02 Read-only Invariant Report

- Result: **PASS**
- Scan windows: 10; identical before/after: 10/10.
- Content hash changes caused by scanner: 0.
- Strong metadata changes inside scan windows: 0.
- Scanner write/rename/delete/sidecar/.obsidian-write calls: 0/0/0/0/0.
- Boundary reads/indexes/egress: 0/0/0.

Each scanner window changed fixture permissions to `0555/0444`, took a tree/hash/metadata snapshot, scanned, took a second snapshot, and compared them before test-driven external mutations resumed. Strong metadata is relative tree, bytes/hash, size, `mtime_ns`, mode and `(device,inode)` within one local scan window. `atime`, birth time, Finder/cloud-provider metadata and cross-platform inode stability are not strong assertions. Python-level access instrumentation covers the candidate scanner; it is not an OS-wide syscall sandbox. The permission layer and before/after snapshots cover accidental writes by this process in the tested environment.
