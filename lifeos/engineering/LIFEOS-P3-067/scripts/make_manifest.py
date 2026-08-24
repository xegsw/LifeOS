#!/usr/bin/env python3
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[1]
# Fixed, task-local evidence names; no directory discovery or caller-supplied path.
paths = [root / 'evidence' / name for name in ('test_results.json', 'test_run.log', 'cross_restart_audit_snapshots.json', 'operator_chain_ready_preview.json', 'operator_chain_first_confirm.json', 'operator_chain_idempotent.json', 'operator_cli_chain.json')]
lines = ['# LIFEOS-P3-067 Evidence Manifest', '', '仅包含任务目录内 Python 标准库与 SQLite 的非敏感合成演练证据。所有外部能力关闭；不构成真实恢复、备份、导出、权限、工程基线或 Stage 4 证明。', '', '| 文件 | SHA-256 |', '|---|---|']
for path in paths:
    lines.append(f'| `{path.name}` | `{hashlib.sha256(path.read_bytes()).hexdigest()}` |')
lines += ['', 'Rework canonical CLI chain：以当前 Manifest 列出的 `operator_chain_*` 与 `operator_cli_chain.json` 为准；它们证明同一干净 task-local run 先 ready preview、再首次 CONFIRM 恢复、最后幂等回执。`cross_restart_audit_snapshots.json` 证明 `recovery_not_confirmed` 与 `recovery_blocked` 在关闭并重开合成 SQLite 后仍保留且顺序可核验。先前未列入本 Manifest 的 CLI Evidence 保留为历史，不作为本次 Rework 主证据。', '', '边界静态检查：代码和结果明确声明 network、Tauri/IPC、Vault、真实路径、导出、cloud、sync、多设备、L3、外部用户均为 disabled/not_used；不存在网络库、目录扫描或外部动作实现。']
(root / 'evidence' / 'MANIFEST.md').write_text('\n'.join(lines) + '\n')
