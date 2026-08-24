# LIFEOS-P3-067｜合成恢复与失败披露受控实现及验证

## 任务结论

### 已验证事实

- 已在全新隔离目录 `lifeos/engineering/LIFEOS-P3-067/` 创建只依赖 Python 标准库与任务内 SQLite 的合成恢复演练包。
- `capture()` 仅在 SQLite 事务提交成功后返回 `saved`；提交前故障与非法合成输入均返回可见 `failed`，且不会留下可被伪称为已保存的记录。
- 重开同一任务内 SQLite 后，已提交合成记录可预览；恢复计划携带来源、记录 ID、版本和预期保存状态。未知计划、来源不匹配、版本不匹配、撤回及 tombstone 均阻断。
- CLI 只接受受限 `run-id`，固定映射到本任务 `runtime/`；不接受任意 DB／路径参数。它先输出预览，只有显式传入 `CONFIRM` 才执行恢复，并披露成功、失败或受阻原因。
- 窄 Rework 已将 CLI 演练改为每次使用新的任务内受限 `run-id`：先建立一个已提交、未恢复的合成记录，再连续形成 `ready preview → 首次 CONFIRM 恢复 → 后续幂等回执`。三段黑盒 CLI 输出由独立脚本断言并合成为单一链 Evidence。
- 第二轮窄 Rework 已将 `recovery_not_confirmed` 与 `recovery_blocked` 审计写入置于 SQLite 事务内，确保拒绝确认或恢复被阻断后立即关闭并重开同一合成数据库，审计仍可核验；不改变 fail-closed 返回、恢复状态或外部能力边界。
- 测试通过 15/15：14 项 fault/recovery 测试加 1 项干净 CLI 链端到端断言；P0/P1/P2/Unknown/Not Implemented 均为 0，退出码为 0。新增跨重启 `recovery_not_confirmed` 与 tombstone blocked 审计顺序断言，并覆盖提交前故障、重启、非法／未知输入、显式确认、重复恢复幂等、撤回／tombstone、来源／版本错配、审计和边界关闭态。
- 结构化结果、运行日志、含审计与记录的 CLI 快照及 SHA-256 Manifest 已写入本任务 Evidence。静态检查未发现网络库、HTTP、socket、subprocess、目录扫描或任意绝对路径输入实现。
- 只读输入未被修改：复核了 P3-063 与 P3-065 Evidence Manifest 的当前 hash；本任务未写入这些目录、任何项目账本或历史工程资产。

### 合理推断

- 在本任务严格的单进程、合成 SQLite 和任务目录边界内，`saved`、失败披露、恢复候选身份/版本检查与 tombstone 不复活语义形成了可复跑的最小演练闭环。
- 该结果可作为后续 PM 验收和全新隔离独立复评的输入，不能外推为真实备份、崩溃恢复、文件恢复、权限运行链、真实 DB、并发/WAL、Tauri/IPC 或 Stage 4 能力。

### 未验证项

- 未验证物理断电、磁盘满、损坏 SQLite 的真实恢复、并发/WAL、迁移、真实备份或任意真实路径／个人数据。
- 未验证真实 Tauri/IPC、Vault、导出、网络/云、同步、多设备、L3、外部用户或 Alpha 使用场景。

## 实现与 Evidence

| 项目 | 路径 / 结果 |
|---|---|
| 合成实现 | `lifeos/engineering/LIFEOS-P3-067/src/recovery.py` |
| 操作者 CLI | `lifeos/engineering/LIFEOS-P3-067/scripts/recovery_cli.py` |
| 回归与 CLI 演练入口 | `lifeos/engineering/LIFEOS-P3-067/scripts/run_tests.sh` |
| 测试结果 | `lifeos/engineering/LIFEOS-P3-067/evidence/test_results.json`：15 PASS / 0 FAIL |
| Rework CLI 单一链 | `lifeos/engineering/LIFEOS-P3-067/evidence/operator_cli_chain.json`：ready → first recovery → idempotent |
| CLI 快照 | `lifeos/engineering/LIFEOS-P3-067/evidence/operator_chain_first_confirm.json` 与 `operator_chain_idempotent.json` |
| 第二轮 Rework 审计快照 | `lifeos/engineering/LIFEOS-P3-067/evidence/cross_restart_audit_snapshots.json`：关闭并重开后 `recovery_not_confirmed` 与 `recovery_blocked` 均保留且顺序可核验 |
| Evidence hash 清单 | `lifeos/engineering/LIFEOS-P3-067/evidence/MANIFEST.md` |

所有运行结果固定声明：network disabled；Tauri/IPC、Vault、真实路径、导出、云、同步、多设备、L3、外部用户均 not used；external action none。

## 角色与关卡自检

- 主责（技术架构）：合成事务回执、重启、候选校验、失败披露、审计和可复跑 Evidence 已覆盖。
- 协审（数据／领域模型）：来源、记录身份、版本、保存状态与撤回/tombstone 不复活已覆盖；不新增或冻结领域模型。
- 协审（AI 信任与安全）：显式 `CONFIRM`、fail-closed 阻断和无外部动作已覆盖；未启用 AI 或真实权限。
- 协审（产品／体验）：CLI 预览、确认、成功／失败／受阻原因可观察；不等价于真实 UI 可用性验证。
- 协审（独立 QA）：本次仅执行侧自检；任务卡要求的全新隔离独立复评尚未执行。
- Gate 1–4：合成恢复适用项自检成立（Gate 1 非范围清晰；Gate 2 来源/版本/状态可见；Gate 3 确认与撤回阻断；Gate 4 故障、重启、审计与可复跑）。任何 Stage 4 Gate 均未判定通过。

## 风险与停止边界

- R-0013、R-0019、R-0021 与 R-0040 均未关闭、未重开且状态不变。
- 第二轮 Rework 的执行侧回归未发现本任务范围内 P0/P1、明确 P2 bypass、Unknown、Not Implemented、Evidence 冲突或越权访问。若 PM 复跑发现任一项，应停止，不以条件通过掩盖。
- 本任务不冻结资产、不恢复工程基线、不更新账本、不启用真实能力、不进入 Stage 4。

## PM 决策与后续

### 需要 PM 决策

1. 是否验收本任务的第二轮 Rework 为受控合成演练完成，并将其仅作为新的全新隔离独立复评输入。
2. 如验收，是否授权创建新的全新隔离独立复评；该复评应工程只读、独立 runner，并重跑故障／恢复／tombstone／跨重启审计／边界关闭态反例。

### 建议

建议在 PM 验收前不扩大至真实路径、真实 DB、备份或 Tauri/IPC；这些均需专属任务、独立评审与用户明确授权。
