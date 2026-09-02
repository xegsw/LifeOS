# P3-144 Phase A prohibited-path declaration

- Phase: A — synthetic/offline engineering gate.
- This session must not access, probe, `stat`, enumerate, hash, read, create, write, or clean the Pilot-7 root or its database before a separately sealed independent review has passed and Phase C is explicitly reached.
- The prohibited real-user root is named only as a contractual boundary in the task card and is not an allowed filesystem target for this Phase A work.
- No real credential, real DeepSeek request, other Provider request, real personal content, retained Pilot, or historical runtime root is an allowed target.
- All writes are limited to `lifeos/engineering/LIFEOS-P3-144/` and the declared P3-144 deliverable. The only disposable runtime root is `/private/tmp/lifeos-p3-144-engineering-v1`.

Declaration result: PASS — Phase A work begins with the real-user root excluded from every filesystem and cleanup operation.
