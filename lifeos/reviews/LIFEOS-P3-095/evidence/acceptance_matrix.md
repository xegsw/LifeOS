# LIFEOS-P3-095 验收标准 → 独立测试 → Evidence

| 任务卡验收标准 | 独立测试／结果 | Evidence | 状态 |
|---|---|---|---|
| 当前源码与历史 Evidence hash 一致 | 9 个重点只读资产前后 hash 一致；attempt-1 12/12、attempt-2 6/6、attempt-3 14/14 条目匹配 | `source_hashes_before.json`、`source_hashes_after.json`、`history_manifest_check.json` | PASS |
| runner 独立性 | 新写 runner 仅导入 `src/local_capture.py`；未导入／调用／复制执行侧测试或 runner | `scripts/independent_runner.py` | PASS |
| 首次、幂等、同键异文、空输入 | O-01～O-04 | `offline_results.json` | PASS |
| 进程重启复读 | 独立 child process 只回传脱敏布尔与计数 | `offline_results.json` O-05 | PASS |
| 今日页身份／时间／本地来源 | O-06 | `offline_results.json` | PASS |
| 原子失败无半成品 | O-07 | `offline_results.json` | PASS |
| 损坏 DB fail-closed | O-08 | `offline_results.json` | PASS |
| 精确确认清理、清理后不可展示 | DB 清空与再次渲染拒绝成立，但旧 HTML 仍存在 | `offline_results.json` O-09～O-10 | FAIL / P1 |
| 禁止能力静态关闭 | AST 反查公开运行时与 CLI，未见网络／HTTP／云／Tauri/IPC 等调用 | `static_boundary_results.json` | PASS |
| Chrome `file:` 动态矩阵 | 因先行 P1 按任务卡停止 | `dynamic_closure.md` | NOT IMPLEMENTED（4 项） |
| 运行期 SQLite／HTML 清理 | 独立 runner 运行目录与匹配前缀残留为零 | `cleanup_results.json` | PASS |
| 全部系统临时残留为零 | 独立语法检查 pycache 精确删除被工具审批拒绝 | `environment_exception.json` | FAIL / P1 |
| PM Evidence 路径可复算 | PM Review 的 hash 值匹配实际文件，但 Manifest 所列相对路径不解析 | `history_manifest_check.json` | P2 |

