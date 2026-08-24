# LIFEOS-P3-075｜最小本地 MVP 受控运行时能力包

## 结论

- **事实：**已在 `lifeos/engineering/LIFEOS-P3-075/` 完成一个仅接受非敏感测试文本的 task-local SQLite 运行时闭环；操作者须显式确认保存和下一步。
- **事实：**干净临时副本自检为 **17 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0**。首次、幂等重复、关闭重开、空输入、未确认、幂等键冲突、提交前失败、未知项目和未确认下一步均已覆盖。
- **事实：**本包没有网络、云、Tauri/IPC、真实路径／文件导出、Vault、AI 消费、同步、多设备、L3 或外部用户通道；外部动作固定为 `none`。
- **推断：**当前实现可作为“受控非敏感本地运行时”后续 PM 验收的 Evidence 输入。
- **非结论：**不构成 R-0019 或 R-0040 关闭、个人数据许可、生产耐久、真实恢复／导出／权限链、Alpha 或 Stage 4 准入。

## 交付内容

- 运行时：`lifeos/engineering/LIFEOS-P3-075/src/local_runtime.py`
- 操作者 CLI：`lifeos/engineering/LIFEOS-P3-075/scripts/runtime_cli.py`
- 单元测试：`lifeos/engineering/LIFEOS-P3-075/tests/test_runtime.py`
- 可复跑自检：`lifeos/engineering/LIFEOS-P3-075/scripts/run_self_check.py`
- Evidence Manifest：`lifeos/engineering/LIFEOS-P3-075/evidence/MANIFEST.md`

CLI 要求 `--non-sensitive-test-only`、`--text`、`--idempotency-key`、`--confirm-save`、`--next-step` 与 `--confirm-next-step`。未确认、空输入、冲突或注入的提交前失败均返回可见失败；只有 SQLite 事务提交后才显示“已保存”。

成功回执和可读记录分别保留用户原文、`operator_local_entry` 来源身份、`user_original` 内容身份、显式操作者确认、AI 关闭和 `external_action: none`。项目恢复仅允许固定的受控 task-local 项目；未知项目明确拒绝。下一步只在操作者明确确认后记录，且不会触发外部动作。

## 包内交付前自检

自检在系统临时目录新建干净副本中执行，未复用工作树运行时 SQLite。结果见 `evidence/self_check_results.json` 与 `evidence/self_check.log`。

| 验收标准 | 测试／检查 | Evidence | 结果 |
| --- | --- | --- | --- |
| AC-1 显式输入、幂等键与下一步 | operator CLI first run | `self_check_results.json` 的 `operator_first_snapshot` | PASS |
| AC-2 提交后才成功、失败无半成品 | 空／未确认、冲突、注入 pre-commit failure | `self_check.log`、`failure_snapshot`、单元测试 | PASS |
| AC-3 身份与关闭态可见 | `test_identity_receipt_and_view_are_visible` | `operator_first_snapshot` | PASS |
| AC-4 幂等与关闭重开 | 重复 CLI、`test_committed_record_survives_reopen` | `operator_repeat_snapshot`、自检日志 | PASS |
| AC-5 受控恢复与显式下一步 | unknown-project、next-step positive/negative tests | 单元测试日志 | PASS |
| AC-6 禁止通道静态关闭 | `BOUNDARIES` 与源码 import/API 模式扫描 | `static_prohibited_tokens` | PASS，0 命中 |
| AC-7 不作越界声明 | 本交付物与 Manifest 的范围核对 | 本文、Manifest | PASS |

原子失败／半成品清理／失败披露／拒绝阻断／fail-closed 均已覆盖。提交前注入失败会回滚记录与 pending audit，避免留下半成品；这是有意的审计语义。已成功提交的保存与下一步有 task-local audit 事件。未覆盖项：无。

历史只读输入 `P3-063`、`P3-067`、`P3-072` 和 P3-074 授权重跑 Manifest 的 SHA-256 在自检前后相同，未被覆盖。

## 复跑

```bash
python3 lifeos/engineering/LIFEOS-P3-075/scripts/run_self_check.py
python3 lifeos/engineering/LIFEOS-P3-075/scripts/make_manifest.py
```

## 角色与关卡

- 主责：Codex 工程执行。
- 协审：PM 验收；之后必须由**全新隔离**工程／体验会话独立复评。
- 本包内自检关卡：通过。
- 需 PM 确认：PM 验收结论；不得由本执行会话宣称最终验收、风险关闭、冻结或阶段变更。
- 需用户确认：在全新隔离独立复评通过后，是否采纳该受控 Evidence 作为后续能力规划输入。

## 边界与待确认

- **事实：**实际运行时文件只会位于本任务 `runtime/` 或自检系统临时副本内；交付前已清理调试运行时文件，未保留操作者输入。
- **建议：**PM 验收应复跑上述命令并核验 `MANIFEST.md` 的 hash；之后再决定是否创建独立复评任务。
- **待确认：**无新的产品、技术架构、数据模型或 AI 权限边界变更建议。
