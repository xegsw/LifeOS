# LIFEOS-P3-068 Independent Evidence Manifest

本清单由全新隔离独立复评生成。P3-067 工程、其测试及既有 Evidence 均只读；独立 runner 未导入、调用或复制 P3-067 测试文件，只在 `/private/tmp/lifeos-p3068-independent/` 的一次性副本中复制候选 `src/recovery.py` 与 `scripts/recovery_cli.py` 并执行黑盒 CLI。

| 文件 | SHA-256 | 说明 |
|---|---|---|
| `independent_runner.py` | `f5a5538748acc82d3c49555ef510c33cebc521819cac590cfa01685fa74a198a` | 新写独立 runner |
| `independent_results.json` | `cb4d59aa78aae8a801ac4113a8cc60d8627d09d707c2c03fee3dbdc0386f5fef` | 34 PASS / 1 P1 FAIL |
| `lifeos/engineering/LIFEOS-P3-067/src/recovery.py` | `b0a15c08ab01f9eeda6cc41f2466dc5da68b3c1fa55f66e7d3f4b3a5465e78bc` | 被评审候选源 |
| `lifeos/engineering/LIFEOS-P3-067/scripts/recovery_cli.py` | `02b7f5166d4f19503623dd9d596b698e8fa4cbf31693c3444880d2c34558b537` | 被评审候选 CLI |
| `lifeos/engineering/LIFEOS-P3-067/evidence/MANIFEST.md` | `f64b98314320d8e7c23964bef9f05ff4fef028e9b39e1d8850a6df54f95b9281` | P3-067 Rework Evidence 清单 |

## 候选 Evidence 对账

- P3-067 Manifest 中的六个主 Evidence SHA-256 均与当前文件一致：`test_results.json`、`test_run.log`、`operator_chain_ready_preview.json`、`operator_chain_first_confirm.json`、`operator_chain_idempotent.json`、`operator_cli_chain.json`。
- 独立 runner 复现：capture 仅提交后报告 saved；提交前故障和非法输入不伪称保存；重启、未知计划、来源／版本不匹配、tombstone 与缺少确认均 fail-closed；黑盒 CLI 链为 ready preview → 首次 CONFIRM `idempotent=false` → 二次 CONFIRM `idempotent=true`。
- 失败项：`recovery_not_confirmed` 在内存 snapshot 可见，但其写入不在事务／commit 中；关闭连接、重启后审计记录消失。`recover()` 的 blocked 路径同样在事务外写审计。此项记为 P1，故独立 runner 以 exit 1 完成并产出结构化结果。
- 静态检查未发现候选源中的网络、HTTP、socket、subprocess、目录扫描或任意 DB／路径参数；Tauri/IPC、Vault、导出、云、同步、多设备、L3、外部用户均为关闭态声明，未实现外部动作。

该 Evidence 仅适用于合成 SQLite、单进程、任务目录与关闭态边界；不代表真实恢复、备份、真实路径、Tauri/IPC、风险关闭、冻结或 Stage 4。
