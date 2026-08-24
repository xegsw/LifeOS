# LIFEOS-P3-072｜基础导出受控沙盒能力包交付物

## 结论

本能力包已在唯一可写隔离目录 `lifeos/engineering/LIFEOS-P3-072/` 内完成。它仅对非敏感合成记录提供“预览 → 精确 `CONFIRM` → 一次性新建系统临时沙盒 JSON 文件 → 内容／来源／身份 hash 回执”的本地演练。

这不是对真实文件导出、真实用户路径、真实数据库、Vault、Tauri/IPC、云／第三方、同步、多设备、L3、外部用户、R-0040 关闭、工程基线恢复、资产冻结或 Stage 4 的验证或授权。

## 实现事实

- `src/sandbox_export.py` 使用内存 SQLite 保存合成记录、预览 token、单次导出状态与审计；没有创建或连接真实数据库。
- `preview()` 仅展示来源、内容 ID／版本／内容 hash、范围、目标类别、确认要求、禁止覆盖与失败语义；默认无文件动作。
- `confirm_and_export()` 只接受精确大写 `CONFIRM` 和当前预览 token。来源、版本、未知、冲突、撤回、tombstone、token 不匹配或二次导出均返回 `blocked` 并记录审计。
- 成功时只用 `tempfile.mkdtemp()` 新建系统临时沙盒；目标文件由隐藏临时文件写入、`fsync`、`os.link` 无覆盖发布构成。结果回执含来源、内容身份、计划 hash、导出内容 hash、文件名和内容匹配结果。
- 写入失败、重名／覆盖和越界路径测试均 fail-closed、审计并清理临时目录；最终 `visible_output_count=0`。
- 静态检查确认没有网络客户端、Tauri/IPC、Vault、云、子进程或真实数据库实现／导入；禁止能力在回执中保持关闭。

## 验证结果

执行：`python3 lifeos/engineering/LIFEOS-P3-072/scripts/run_tests.py`

结果：**7 PASS / 0 FAIL**，退出码 0。

| 任务卡完成定义 | 证据 |
| --- | --- |
| 预览、精确确认、单次临时沙盒输出与 hash 回执 | `test_preview_discloses_confirmation_and_temporary_target`、`test_exact_confirm_writes_once_to_new_temporary_sandbox_with_matching_receipt`、`evidence/export_receipt.json` |
| 来源／版本／范围／确认／冲突／撤回／tombstone／未知 fail-closed 且审计 | `test_missing_or_mismatched_confirmation_or_preview_token_fails_closed`、`test_source_version_unknown_conflict_revoked_and_tombstoned_fail_closed_and_audit` |
| 重名／覆盖、越界路径、写入失败无可见半成品 | `test_collision_and_escaped_path_are_blocked_without_overwrite_or_visible_output`、`test_write_failure_is_audited_and_leaves_no_visible_output` |
| 外部及非临时路径能力关闭 | `test_static_boundary_contract_and_source_imports_are_closed` |

## 角色与关卡

- 主责：技术架构负责人。受控临时路径、原子发布、失败清理和可重复回归已在合成单进程边界内验证。
- 协审：数据／领域模型负责人（来源、内容身份／版本与范围披露）；AI 信任与安全负责人（精确确认、拒绝／撤回／冲突阻断、审计）；产品／体验（“确认后一次性临时输出、非真实导出”的可观察语义）。
- Gate 2、Gate 3、Gate 4：仅在本任务合成受控范围内通过。
- Gate 1、Gate 5：不适用为真实价值或真实路径验证，不能外推为 Stage 4 准入。

## Evidence

- 工程说明：`lifeos/engineering/LIFEOS-P3-072/README.md`
- 结构化测试结果：`lifeos/engineering/LIFEOS-P3-072/evidence/test_results.json`
- 合成临时输出回执：`lifeos/engineering/LIFEOS-P3-072/evidence/export_receipt.json`
- 哈希清单：`lifeos/engineering/LIFEOS-P3-072/evidence/MANIFEST.md`

## 推断、建议与待确认

推断：在非敏感合成数据、单进程、内存 SQLite 与新建系统临时目录的窄边界内，能力维持明确确认、单次输出、无覆盖和失败不留可见输出的语义。

建议：PM 可在一次正式验收后，决定是否发起全新隔离独立复评；独立复评必须核验当前 hash、路径隔离、确认绑定、原子失败、Evidence 与关闭态。

需 PM 确认：是否接受本能力包进入全新隔离独立复评。任何真实文件／路径、Tauri/IPC、Vault、真实数据、风险关闭、冻结或阶段决定均需另立任务、独立复评和用户明确授权。

## 范围记录

事实：未修改 P3-070／P3-071 或其他历史工程、Review、Evidence、风险、冻结、决策或任务账本。任务卡模型路由未触发降级或后备配置。
