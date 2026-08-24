# LIFEOS-P3-009 PM Review｜目标技术栈最小工程骨架与 P3-001 不变量迁移

## 验收信息

- 任务 ID：LIFEOS-P3-009
- 任务名称：目标技术栈最小工程骨架与 P3-001 不变量迁移
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- Evidence Manifest 路径：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-009_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen / Pass with Conditions
- 是否允许进入下一任务：Conditional，用户确认采纳后启动独立工程评审
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-11

## PM 总结

1. P3-009 按任务卡在 `lifeos/engineering/LIFEOS-P3-009/` 建立了隔离 TypeScript + Node.js + SQLite 最小工程骨架，未修改 P3-001、项目账本、Stitch 或冻结资产。
2. 交付物明确承认本任务只覆盖合成、单进程、受控测试包边界，未外推为生产级真实技术栈、真实 Tauri / IPC、真实 Vault、真实数据或外部能力通过。
3. PM 使用 bundled Node v24.14.0 复跑 `scripts/validate.mjs`，结果为 10 PASS / 0 FAIL，P0 失败 0；`test_results.json` 已更新为 PM 复跑时间 `2026-08-11T06:01:42.987Z`。
4. PM 追加只读抽样复核 4 类历史高风险反例方向：删除后 feedback 不写入、跨 Project 导出闭包、撤回后旧 generation 阻断、processor mismatch fail closed，均通过。
5. 本地预检已调用，但局域网模型连接重置，输出 `Skipped / Local Model Unavailable`；不作为 PM 验收依据。
6. 任务可验收为 Accepted，但只能作为后续独立工程评审输入；不得冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA，不得关闭 R-0040。

## 角色与关卡验收

- 主责角色覆盖情况：工程负责人覆盖充分；最小骨架、运行命令、测试结果、evidence 和复跑路径均清楚。
- 协审角色覆盖情况：
  - 技术架构负责人：覆盖；明确继承技术架构 V0.1 合同，未冻结新实现细节，保留 R-0040。
  - 数据与权限负责人：覆盖；用户原文、AI 生成、AI 推断 / 建议、外部引用来源身份有明确策略，消费门对授权、来源、版本、tombstone、generation、evidence 进行重检。
  - QA / 测试负责人：覆盖；H1-H9 / T-ARCH 有矩阵，P0 失败 0，未迁移项清楚。
- 已通过关卡：工程自测、H1-H9 / T-ARCH 迁移覆盖检查、默认关闭能力检查、evidence manifest 完整性检查。
- 未通过或需后续确认关卡：真实 Tauri / IPC、真实 Vault、真实数据、真实文件导出、进程杀死耐久、SQLite-aware backup、长 FTS rebuild、lease fencing、正式恢复协议均未通过。
- 是否属于关键冻结事项：否；本任务是工程迁移候选，不是冻结任务。
- 是否需要独立评审：Yes。
- 独立评审路径：待创建，建议 `lifeos/reviews/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`。
- 独立评审结论：未开始。
- 是否允许进入下一任务或下一阶段：允许用户确认后进入 P3-010 独立工程评审；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：生产 Schema、API、模块边界、包管理策略、Tauri capability / IPC、真实 Vault、真实数据、导出格式、备份恢复协议、同步、多设备、向量、云 / 第三方模型、L3、生产 SLA、工程基线。
- 是否允许进入下一任务：Conditional；用户确认采纳 P3-009 后，可启动 P3-010 独立工程评审。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes，将 P3-009 从 Ready 更新为 Accepted but Not Frozen / Pass with Conditions。

## PM 复核记录

### 复跑命令

```bash
cd lifeos/engineering/LIFEOS-P3-009
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs
```

结果：

- Node：v24.14.0
- 测试：10 PASS / 0 FAIL
- P0 失败：0
- P1 Open：0
- 快照：`64d18d9c056571c94077e94ff4efdd3ac720233feaa376cadff0593045345d2a`

### PM 抽样反例

PM 通过临时只读脚本抽查以下 4 类历史高风险方向：

- `feedback_after_delete_no_write`：PASS
- `cross_project_export_closed`：PASS
- `stale_generation_after_revoke_blocked`：PASS
- `processor_mismatch_fail_closed`：PASS

### 本地预检

- 预检路径：`lifeos/local_prechecks/LIFEOS-P3-009_LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report_local_precheck.md`
- 预检状态：Skipped / Local Model Unavailable
- 错误：`[Errno 54] Connection reset by peer`
- PM 判断：允许跳过；不影响 PM 独立复核。

## 需要用户确认的事项

1. 问题：是否采纳 P3-009 的 Accepted / Pass with Conditions 结论，并启动 P3-010 独立工程评审？
   - PM 建议：采纳，并启动 P3-010。
   - 可选方向：A. 采纳并进入独立评审；B. 要求 P3-009 先返工补齐未迁移项；C. 暂停工程线。
   - 不确认的影响：P3-009 只能停留为 PM 已验收但未被用户采纳的工程输入，不能启动独立评审。
2. 问题：是否继续保持 R-0040 为 Open / Conditional？
   - PM 建议：保持 Open / Conditional。
   - 可选方向：A. 保持打开；B. 若希望关闭，则必须另立真实 Tauri debug/release 与目标平台迁移复测任务。
   - 不确认的影响：若误关闭，会把等价骨架证据外推成真实 Tauri 安全证据，风险过高。

## 整改建议

本任务不要求返工。但后续独立评审必须重点攻击：

- P3-001 23 个历史测试与 P3-009 10 个聚合测试之间是否存在关键断言遗漏。
- 恢复包、generation、Project 全状态闭包、Feedback / Link 写入口和导出旁路是否存在新的自证循环。
- Node `node:sqlite` experimental warning 是否影响后续工程栈选择。
- H3 / H5 / H9 未迁移项是否被误读为已完成。

## 可接受内容

- P3-009 可作为“目标技术栈最小骨架迁移候选”。
- P3-009 的 evidence 可作为后续 P3-010 独立工程评审输入。
- TypeScript + Node.js + SQLite 的最小实现可以继续作为受控工程验证路径，但不冻结为生产实现。
- H1-H9 / T-ARCH 可执行迁移矩阵可作为后续工程任务追踪格式。

## 不接受或需谨慎内容

- 不接受把 P3-009 PASS 外推为真实 Tauri / IPC、真实 Vault、真实数据、文件导出、云 / 第三方模型、同步、多设备或 L3 通过。
- 不接受用 P3-009 替代 P3-001 的全部历史 evidence。
- 不接受关闭 R-0040。
- 不接受冻结生产 Schema / API / 模块边界 / 包管理策略 / 导出格式 / SLA。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：将 P3-009 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：将 P3-009 更新为 Accepted but Not Frozen / Pass with Conditions，并记录下一步为 P3-010 独立工程评审。
- `lifeos/DECISION_LOG.md`：新增 PM 接受 P3-009 的决策记录。
- `lifeos/CURRENT_STATUS.md`：更新当前等待用户确认与下一步。
- `lifeos/RISK_LOG.md`：R-0040 保持 Open / Conditional；本次无需关闭风险。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：工程目录隔离清楚；能复跑测试并生成 evidence；边界声明克制，没有擅自冻结或启动后续任务。
- 主要问题：测试从 P3-001 的 23 项聚合为 10 项，独立评审必须验证是否漏掉关键子断言。
- 以后更适合分派给该 Agent 的任务类型：工程实现、技术 Spike、P0 修复、回归测试、evidence 整理。
- 不建议分派给该 Agent 的任务类型：对自己刚完成工程的独立复评或冻结前最终裁判。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：暂不需要；当前结论符合既有分派规则。

## 下一步任务建议

建议用户确认采纳后启动：

- `LIFEOS-P3-010`：P3-009 目标技术栈最小工程骨架独立工程评审
- 推荐执行 Agent：WorkBuddy
- 任务类型：独立评审 / 反例攻击
- 是否允许修改工程文件：No
- 是否允许修改项目账本：No

P3-010 通过前，不得把 P3-009 作为后续工程基线，也不得启动真实 Tauri / IPC、真实 Vault、真实数据或外部能力。
