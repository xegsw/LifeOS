# LIFEOS-P3-037 Validation Summary

- Overall: FAIL / Rework input
- Exit code: `1`
- P0: {'PASS': 2, 'FAIL': 0, 'NOT_IMPLEMENTED': 0, 'UNKNOWN': 0}
- P1: {'PASS': 5, 'FAIL': 3, 'NOT_IMPLEMENTED': 0, 'UNKNOWN': 0}
- P2: {'PASS': 0, 'FAIL': 0, 'NOT_IMPLEMENTED': 0, 'UNKNOWN': 0}
- P2-2: FAIL
- P2-3: FAIL
- P2-4: FAIL（runtime recheck fail-closed=`True`；audit integrity=`False`）
- Source fixture unchanged: `True`
- Backup/restore: `PASS`
- Integrity/FK: `PASS`
- No real DB/Vault/Tauri/IPC/real-file capability was accessed or enabled.
