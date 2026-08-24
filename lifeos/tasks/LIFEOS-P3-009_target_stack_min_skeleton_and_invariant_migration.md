# LIFEOS-P3-009 目标技术栈最小工程骨架与 P3-001 不变量迁移

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程会话，不是 PM 主会话。请只完成本任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P3-009
- 任务名称：目标技术栈最小工程骨架与 P3-001 不变量迁移
- 优先级：P0
- 任务类型：工程实现型任务 / 目标技术栈迁移任务
- 建议篇幅：工程交付报告 2000-4000 字；超出内容放入“后续任务建议”
- 推荐执行 Agent：Codex
- 推荐理由：本任务需要创建隔离工程目录、迁移测试不变量、运行本地测试并生成 evidence manifest，更适合工程实现型 Agent
- 是否需要后续独立评审：Yes
- 是否允许修改工程文件：Yes，仅限本任务授权范围
- 是否允许修改项目账本：No
- 主责角色：工程负责人
- 协审角色：技术架构负责人、数据与权限负责人、QA / 测试负责人
- 必须通过的评审关卡：工程自测、H1-H9 / T-ARCH 迁移覆盖检查、默认关闭能力检查、evidence manifest 完整性检查
- 状态：Ready

## 背景

`LIFEOS-P3-001` 已在合成数据、单进程、受控测试包边界内恢复为后续工程基线候选，`R-0041` 已关闭。但该结论不代表生产级真实技术栈、真实 Tauri / IPC、真实 Vault、真实数据、同步、多设备、云 / 第三方模型或外部用户能力通过。

当前下一步不是直接开发完整 App，而是把 P3-001 已验证的 H1-H9 / T-ARCH 不变量迁移到更接近目标技术栈的最小工程结构中，证明这些安全合同可以脱离 Python 合成 harness 后继续成立。

目标技术架构 V0.1 合同为：单设备本地优先；本地权威原文与控制账本；SQLite + FTS-first；派生可重建、向量后置；权威 / 派生 / outbox-job 分责；所有消费入口重检授权、来源、版本、tombstone、generation、证据和租约；Obsidian 默认关闭，仅保留只读条件适配器；Tauri / IPC 仅冻结后端安全合同和复测触发器。

## 目标

本任务完成后，需要回答：

- P3-001 的核心安全不变量能否迁移到目标工程结构中？
- 目标技术栈最小骨架是否能在本地受控目录内运行测试，并生成可复核证据？
- H1-H9 / T-ARCH 中哪些已经形成可执行测试，哪些仍只是映射或待迁移项？
- 在不启用真实 Vault、真实 Tauri 文件能力、真实数据和外部能力的前提下，下一步工程扩展的安全边界是什么？

## 授权范围

允许：

- 读取 `lifeos/engineering/LIFEOS-P3-001/` 作为迁移参考，但不得修改 P3-001 文件。
- 在 `lifeos/engineering/LIFEOS-P3-009/` 下创建最小工程骨架、源文件、合成夹具、测试、脚本和 evidence。
- 在 `lifeos/deliverables/` 下创建本任务工程交付报告。
- 使用本地可用的 Node / TypeScript / SQLite / 测试工具；如依赖缺失，可在本任务隔离目录内建立降级可运行 harness，并在报告中明确“不等于真实 Tauri / SQLite 完整集成”。
- 运行本地脚本、测试、类型检查或等效验证命令。

不允许：

- 修改 `lifeos/engineering/LIFEOS-P3-001/`。
- 修改 `lifeos/CURRENT_STATUS.md`、`TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`DECISION_LOG.md`、`RISK_LOG.md`、`OPEN_QUESTIONS.md`。
- 修改 Stitch、产品 PRD、冻结资产或项目背景包。
- 处理真实用户数据、真实 Obsidian Vault、真实敏感文件或外部用户资料。
- 启用真实 Tauri 文件能力、真实 IPC capability、导出路径扩权、同步 / 多设备、向量、云 / 第三方模型、L3 自动动作或外部自动化。
- 宣布 Schema、API、UI、Tauri 配置、导出格式、生产 SLA、工程基线或 MVP 开发结果冻结。

## 输入材料

请参考：

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- `lifeos/AGENT_BRIEFING_PACK.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P3-001_min_vertical_slice_engineering.md`
- `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/reviews/LIFEOS-P3-008_third_p0_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-008_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 只读取当前任务的直接依赖文件；不要主动读取无关 Deliverable、无关 Review、无关 Evidence 或全项目历史。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `lifeos/DECISION_LOG.md`；如需决策依据，只读取 D-0148 及最近 5-10 条相关决策。
- 若上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。

## 范围

本任务必须覆盖：

1. 建立或确认 `lifeos/engineering/LIFEOS-P3-009/` 隔离工程目录。
2. 输出最小工程骨架，至少包含：
   - `README.md`
   - 源码目录
   - 合成 fixtures
   - 测试目录
   - evidence 目录
   - 可复跑的验证命令说明
3. 从 P3-001 迁移或重建 H1-H9 / T-ARCH 不变量追踪矩阵，至少说明：
   - 已可执行覆盖项
   - 已映射但未可执行覆盖项
   - 暂不适合迁移项及原因
4. 优先迁移以下 P0 防线为可执行测试：
   - 用户原文不可丢失或静默覆盖
   - 用户原文、AI 生成、AI 推断 / 建议、外部引用来源身份清楚
   - 所有消费入口重检 authorization、source、version、tombstone、generation、evidence
   - 撤回 / 删除后不得恢复复活
   - 跨 Project / location / processor 不得越权消费或导出
   - 默认关闭真实 Vault、真实 Tauri 文件能力、外部模型、向量、同步、多设备、L3
5. 生成 evidence 包，至少包含：
   - `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
   - 测试结果摘要文件
   - H1-H9 / T-ARCH 迁移矩阵
   - 默认关闭能力矩阵
6. 创建工程交付报告：
   - `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
7. 完成本地预检，或说明符合允许跳过的原因。

## 非范围

本任务暂时不要做：

- 不开发完整首页 / 今日页 UI。
- 不接入真实 Obsidian Vault。
- 不启用真实 Tauri 文件访问、真实 IPC capability 或真实系统路径 scope。
- 不实现真实云同步、多设备同步、外部模型、向量检索或 L3 自动动作。
- 不迁移真实用户资料。
- 不冻结生产 Schema、API、模块边界、包管理策略、打包方案、导出格式或 SLA。
- 不关闭 R-0040。
- 不创建后续任务；如认为需要，只写入“后续任务建议”。

## 角色检查点

工程负责人必须重点回答：

- 最小工程骨架能否本地复跑？
- 测试命令、fixtures、evidence 是否可复核？
- 本任务是否严格限制在 `lifeos/engineering/LIFEOS-P3-009/` 和指定交付物内？

技术架构负责人必须重点检查：

- 是否继承技术架构 V0.1 合同，而不是冻结新的实现细节？
- 是否清楚区分“目标技术栈骨架 / 降级 harness / 真实 Tauri 集成”？
- 是否保留 R-0040 的真实 Tauri 复测触发器？

数据与权限负责人必须重点检查：

- 用户原文、AI 生成、AI 推断 / 建议、外部引用来源是否有身份边界？
- authorization、source、version、tombstone、generation、evidence 是否在消费入口被重检？
- 删除 / 撤回 / 恢复 / 导出是否避免复活和越权？

QA / 测试负责人必须重点检查：

- H1-H9 / T-ARCH 是否有追踪矩阵？
- P0 测试失败是否为 0？
- 若存在未覆盖项，是否明确原因、风险和下一步？

## 交付物格式

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`

报告必须包含：

- 任务摘要
- 实际创建 / 修改文件清单
- 工程骨架说明
- 运行命令与测试结果摘要
- H1-H9 / T-ARCH 迁移矩阵
- 默认关闭能力矩阵
- 与 P3-001 的差异
- 未覆盖项、风险和后续建议
- 本地预检结果或跳过原因
- 结论：Pass / Pass with Conditions / Rework / Blocked

注意：聊天回复不要粘贴完整报告，只输出摘要、交付物路径、evidence manifest 路径、是否需要 PM 决策。

## 验收标准

只有满足以下条件，任务才算完成：

- 已创建或确认 `lifeos/engineering/LIFEOS-P3-009/` 隔离工程目录。
- 已输出可复跑的最小工程骨架或明确说明阻塞原因。
- 已生成 evidence manifest。
- 已完成 H1-H9 / T-ARCH 迁移矩阵。
- P0 测试失败数为 0；如 P0 失败数大于 0，结论必须为 Rework 或 Blocked。
- 未修改 P3-001 工程基线文件。
- 未启用真实数据、真实 Vault、真实 Tauri 文件能力或外部能力。
- 已生成指定交付报告。
- 已完成本地预检或说明允许跳过原因。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。

## 完成后的 PM 提示

完成后请在会话中只输出：

- 简短总结
- 交付物路径
- evidence manifest 路径
- 测试摘要
- 是否需要 PM 决策

不要修改项目账本，不要自行启动 P3-010，不要宣布资产冻结。
