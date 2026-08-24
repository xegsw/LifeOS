# LIFEOS-P3-063｜可真实使用 MVP 最小闭环受控实现与验证

## 结论

### D-0273 Rework 更新

此前执行侧程序化夹具验证虽通过 7 项，但 `scripts/run_demo.py` 将原文、幂等键与下一步确认写死，未能证明操作者可输入记录并显式确认。根据 D-0273，本次已在原隔离目录完成窄 Rework：运行入口现在要求操作者显式传入 `--synthetic-only`、`--text`、`--idempotency-key` 和 `--next-step`；输入仍只能进入本目录 `runtime/`，`--run-id` 不接受路径。入口不再删除既有 SQLite 文件，以便通过同一合成幂等键复现重复提交与冲突路径。

执行命令为：

```sh
lifeos/engineering/LIFEOS-P3-063/scripts/run_demo.sh --synthetic-only --text '操作者输入的合成原文：整理研究问题' --idempotency-key 'operator-rework-001' --next-step '操作者显式确认：明天阅读此合成记录' --run-id operator-rework
```

该命令退出码为 0，并生成 `runtime/operator-rework_snapshot.json`；快照保留操作者提供的合成原文和 `user_confirmed` 确认身份，且明确 `external_action=none`、`ai_features=disabled`。本次 Rework 后全量回归为 11 PASS／0 FAIL，P0／P1／P2／Unknown／Not Implemented 均为 0。D-0271 所指“固定夹具入口”缺口已由新增可操作 CLI 和端到端验证覆盖；是否接受该整改仍由 PM 判断。

### 事实

已在全新隔离目录 `lifeos/engineering/LIFEOS-P3-063/` 创建并本地运行一个仅使用 Python 标准库和 SQLite 的最小闭环。它可完成：受控本地输入一条非敏感合成记录、仅在 SQLite 事务成功提交后显示“已保存”、显示原文与来源／内容身份、恢复预置受控 Project，并由用户显式确认一条下一步。所有运行数据、临时数据库、日志、快照和测试结果均位于该目录内。

本次执行未修改 P3-009、P3-031、历史 Evidence、任何项目账本或冻结资产。没有安装或运行 Tauri／IPC；没有访问真实系统路径、Vault、Obsidian、用户目录、文件选择器、网络、云／第三方模型、真实个人数据、真实数据库、导出、同步、多设备、外部用户或 L3。

运行脚本 `scripts/run_demo.sh` 在操作者提供合成参数后退出码为 0，完成闭环并生成 `runtime/operator-rework_snapshot.json`。回归脚本 `scripts/run_tests.sh` 退出码为 0，结构化结果为：PASS 11、FAIL 0、P0 0、P1 0、P2 0、Unknown 0、Not Implemented 0。完整日志、结果和输入／实现 hash 已写入 [Evidence Manifest](../engineering/LIFEOS-P3-063/evidence/MANIFEST.md)。

### 推断

该资产足以作为“受控本地运行的 MVP 最小闭环”实施侧 Evidence，特别是为 R-0019 的“未提交不得显示已保存”提供一个具体、可复跑的实现验证。但它只覆盖本任务的合成 SQLite、单进程、单用户、隔离本地目录边界，不能外推为生产耐久、物理断电安全、备份恢复、真实桌面壳、真实个人数据、基础导出、基础权限设置、Alpha 用户可用或 Stage 4 准入。

### 建议（需 PM 确认）

PM 可在验收后安排一份全新隔离的独立工程／体验复评，重点反向验证成功回执、写入失败、重复提交、重启恢复、来源／AI 身份和显式确认语义。该建议不等于本任务自行启动后续工作，不建议在复评前将该资产作为真实能力启用、风险关闭或阶段推进依据。

## 实现范围与运行方式

运行入口是 `scripts/run_demo.sh`。该脚本只调用 `scripts/run_demo.py`，后者创建本目录 `runtime/controlled_mvp.sqlite`，依次执行：

1. 以合成文本调用 `capture()`；
2. `capture()` 开启 `BEGIN IMMEDIATE` 事务、写入记录、调用 `COMMIT`；只有 commit 返回后才构造 `saved: true` 与“已保存”回执；
3. 查询已保存记录并显示 `original_text`、`source_identity=user_local_entry`、`content_identity=user_original`；
4. 仅恢复预置的 `project-synthetic-001`，以防止任何范围外 Project 被恢复；
5. 调用 `confirm_next_step()` 记录 `confirmation_identity=user_confirmed`。返回数据固定声明 `external_action=none` 与 `autonomy_level=L0`。

数据模型有意保持窄小：`projects`、`records`、`next_step_confirmations` 三张表。`records.content_identity` 由 SQLite CHECK 约束固定为 `user_original`，而来源身份固定为 `user_local_entry`。所有响应额外明确 `ai_features=disabled`；本实现没有 AI 生成、推断、建议字段或调用路径，因此不能把用户原文和 AI 内容混在一起。

这不是 P3-031 候选 SQL 的迁移、替代或变体。P3-009 的身份和恢复语义、P3-031 的内容身份约束只作为只读设计参照，其 hash 已记录在 Manifest。实现没有建立 Tauri／IPC mock，也没有借由 mock 宣称验证真实能力。

## 失败路径与验证

`tests/test_mvp.py` 使用临时 SQLite 数据库并由 `scripts/run_tests.sh` 产生日志和 JSON 结果。十一项通过用例如下：

| 测试 | 可观察结果 |
|---|---|
| commit_then_saved_and_identity_visible | 成功 commit 后才返回“已保存”；原文、用户本地来源、用户原文身份和 AI 关闭状态均可见。 |
| duplicate_submit_is_idempotent | 相同幂等键和原文不重复写入，回执标记重复提交。 |
| idempotency_conflict_is_visible | 同一幂等键对应不同原文时返回可见的“保存失败”，不静默覆盖。 |
| write_failure_never_reports_saved_or_persists | 在 commit 前注入 SQLite 写入失败，事务回滚、数据库无该记录且不返回成功。 |
| restart_preserves_committed_record | 关闭并重新打开 SQLite 后，已经提交的合成记录仍可读取。 |
| controlled_restore_and_explicit_confirmation | 仅受控 Project 可恢复；未知 Project 明确拒绝；下一步只能经显式用户确认记录。 |
| no_external_action_or_ai_enabled | 确认结果无外部动作、L0，记录和快照均表明 AI 功能关闭。 |
| e2e_operator_input_and_explicit_confirmation | 子进程调用操作者 CLI；快照证明输入原文、显式确认与无外部动作。 |
| e2e_empty_input_is_visible_and_never_saved | CLI 空原文以非零退出和可见“保存失败”结束，输出不含“已保存”。 |
| e2e_idempotency_conflict_is_visible_and_never_saved | CLI 用同一合成幂等键提交不同文本时非零退出、可见失败且不显示成功。 |
| e2e_precommit_failure_is_visible_and_never_saved | CLI 在提交前注入受控失败；快照 `saved=false`，输出不含“已保存”。 |

失败注入是一项预期拒绝验证，而不是测试失败：`fail_before_commit=True` 在 INSERT 后、COMMIT 前产生受控 SQLite 异常。实现捕获异常后回滚并返回“保存失败：未完成提交”；测试随后查询数据库以确认记录不存在。它验证当前进程内的事务语义，不验证磁盘满、进程被强杀、物理断电、文件系统虚假 flush、备份或跨平台恢复。因此，R-0019 及所有相关开放风险维持其现有状态，未在本任务中关闭或重新打开。

## 角色和关卡自检

- 技术架构：已覆盖本地 SQLite 事务、可复跑脚本、重启读取和可观察失败；未冻结任何运行时配置、Schema/API 或技术架构。
- 产品：闭环直接对应“捕获 → 来源可见 → Project 上下文恢复 → 下一步确认”，无企业后台、任务自动化或范围外能力。Gate 1 的本任务适用实现检查通过；真实 MVP／Stage 4 Gate 1 仍未通过。
- 数据／领域模型：用户原文、来源、内容身份和确认状态分开存储；未把该窄表结构误称为核心领域模型或正式 Schema。Gate 2 的本任务适用语义检查通过。
- AI 信任与安全：AI 功能默认关闭且无调用路径；重大下一步必须显式确认，确认不产生外部动作。Gate 3 的本任务适用关闭态与确认检查通过；真实权限运行链及撤回链未验证。
- 体验／QA：成功、失败、重复提交、范围外恢复拒绝和确认状态都有可观察结构化结果。Gate 4 的本任务适用可运行性检查通过；真实桌面体验、可访问性、恢复演练与 Gate 5 用户价值验证仍未通过。

任务卡要求 Gate 1–4 的本任务适用定义和受控运行证据，本次均具备。绝不据此声称任一 Stage 4 Gate 已通过。Stage 3→4 的其余四项硬门槛——基础导出、基础权限设置、错误／数据恢复策略和 Alpha 使用说明——均不在本任务范围内，仍须独立授权、实现和复评。

## Evidence、预检与剩余边界

Evidence 位于 `lifeos/engineering/LIFEOS-P3-063/evidence/`：`MANIFEST.md` 提供复跑命令与 SHA-256；`test_run.log` 是完整运行日志；`test_results.json` 是机器可读统计；`runtime/demo_snapshot.json` 保存成功路径快照。复跑会覆盖本任务自身的日志、JSON、快照和临时数据库，不覆盖历史 P3 资产。

已按项目规则调用本地预检；局域网模型因 sandbox 网络限制不可访问，故按允许跳过场景记录为 `Skipped / Local Model Unavailable`，报告见 `lifeos/local_prechecks/LIFEOS-P3-063_LIFEOS-P3-063_usable_mvp_minimum_closed_loop_controlled_implementation_and_verification_local_precheck.md`。预检只用于字段完整性、范围与术语检查，不承担 PM 验收、独立复评、冻结、风险判断或 Stage 4 决策。

仍需保留的限制：没有真实 Tauri／IPC、路径 scope、Vault、文件导出、真实 DB migration、真实个人数据、网络、云／第三方模型、同步、多设备、外部用户、L3、并发／WAL、物理断电、磁盘满、备份或恢复演练；不关闭 R-0019、R-0040 或任何风险，也不冻结工程基线或进入 Stage 4。
