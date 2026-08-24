# LIFEOS-P3-005 P3-001 第二轮 P0 返工与补测

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- 本任务卡明确列出的输入材料
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

你是 LifeOS 项目的专项工程返工会话，不是 PM 主会话，也不是独立评审会话。请只完成本任务，不要自行扩大范围。本任务明确授权你在 `lifeos/engineering/LIFEOS-P3-001/` 内修改关闭 P3-004 指出的三项 P0 所需的最小代码、测试、合成夹具和 evidence，并创建返工报告；不得扩展 UI、真实数据、真实 Vault、真实 Tauri、云 / 第三方模型、向量、同步、多设备、L3 或外部用户能力。

## 任务信息

- 任务 ID：LIFEOS-P3-005
- 任务名称：P3-001 第二轮 P0 返工与补测
- 优先级：P0
- 任务类型：条件整改 / 补丁型工程任务
- 建议交付报告篇幅：1500-3000 字；完整日志、测试输出和断言证据写入 evidence
- 主责角色：工程负责人 / 技术架构负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、质量 / 测试负责人、PM
- 必须通过的评审关卡：Gate 2、Gate 3、Gate 4；Gate 1 仅检查未扩范围，Gate 5 不做结果层验证
- 状态：Ready

## 背景

用户已采纳 `LIFEOS-P3-004` 的 `Rework` 结论并允许启动本任务。P3-004 复评确认：P3-003 使原四项 P0 的固定反例通过，基础验证仍为 16 PASS / 0 FAIL / P0=0 / P1=0；但独立复评发现三项新增 P0，说明底层信任不变量仍未关闭：

1. `restore_candidates()` 只做包对包比较，恢复门不读取权威当前控制状态；旧控制包或重算校验的伪造控制包可自证恢复对象。
2. `suggest_next_step()` 用完整证据集合计算候选身份，但 `derivation` 只持久化一个 `input_version_id`；撤回非主证据后，候选仍活跃并可导出。
3. `can_consume()` 带默认 purpose / location / processor；真实消费入口未显式传入授权上下文；同 subject 冲突 Authorization 可被非确定性选行后放行。

这些问题继续击穿 H2、H4、H5、H9 与 `T-ARCH`。P3-001 当前仍为 `Rework`，R-0041 仍为 `Open`。本任务完成后仍须 PM 验收和再次独立工程复评；本任务自身不能恢复工程基线或关闭 R-0041。

## 目标

在不扩大能力与产品范围的前提下，最小修改 P3-001 实现与验证体系，关闭 P3-004 指出的三项 P0，并把 P3-004 的失败反例全部纳入自动回归与真实断言 evidence。

## 范围

本任务必须覆盖：

### 1. 恢复门读取权威当前控制状态

- `restore_candidates()` 或其调用路径不得再依赖调用方传入的旧包 / 可重算包自证当前状态。
- 恢复候选必须在可信执行边界读取权威当前状态，至少覆盖：Artifact 当前 generation、current_version_id、deleted / tombstone、Source connected / tombstoned、Authorization 当前唯一决策、Derivation 当前状态、Feedback 当前状态。
- 旧包、旧控制快照、重算公开 SHA-256 的伪造控制包不得使已撤回、已删除、断源、撤回反馈或授权失效对象复活。
- 如因当前测试形态无法引入真实生产恢复边界，应在合成工程内建立明确的“当前权威读取接口”，并在报告中说明它仍不是正式导出 / 恢复协议。

### 2. Derivation 完整证据依赖持久化与失效传播

- 候选 Derivation 必须持久化完整证据依赖，而不是只保存一个 `input_version_id`。
- 任一参与证据的 ArtifactVersion / Artifact / Source / Authorization 被撤回、删除、断源、授权失效或 generation 变化时，相关 Derivation 必须失效或被消费 / 导出阻断。
- `export_test_package()`、恢复候选、搜索 / 建议等消费路径不得导出或使用依赖已失效证据的 Derivation。
- 补充自动回归：先生成候选，再撤回非主证据（例如 `artifact-decision`），断言候选 stale / 阻断、导出 derivations 零命中、相关 Feedback / Link 不被非法保留。

### 3. 授权上下文显式传入与冲突 fail closed

- 所有消费入口必须显式传入 purpose、location、processor、project / subject、expected version、generation / 时效等授权上下文；不得由默认允许值静默补齐。
- `can_consume()` 不应以默认本地允许上下文掩盖调用方缺失；调用方缺失上下文必须 fail closed。
- 同一 subject 出现多条当前 Authorization、allow / deny 冲突、重复 allow、缺失、过期、generation 不一致、维度不一致或未知状态时，必须 fail closed。
- 补充自动回归：`read_artifact()`、`recovery_package()`、`search()`、`export_test_package()` 等真实消费入口在授权上下文缺失 / 冲突时均不得消费。

### 4. 保留并复跑既有验证

- 保留 P3-001 原 11 项验证和 P3-003 新增 5 项回归，不得删除或弱化既有测试来获得通过结果。
- 新增 P3-004 三项 P0 的失败反例进入统一验证命令。
- evidence 必须由真实断言和运行结果生成，不得使用超出真实覆盖范围的固定摘要。
- evidence manifest 必须记录本次内容哈希或等价可唯一定位快照、夹具版本、环境、命令、断言、结果、限制和复跑时间。

## 非范围

本任务暂时不要做：

- 不扩展产品 UI、动态交互、首页 / 今日页、Stitch 或 PRD。
- 不处理任何真实数据、低敏真实副本、真实敏感材料、真实 Vault 或用户真实路径。
- 不启用真实 Tauri / IPC / 文件导出扩权、Obsidian、云 / 第三方模型、向量、同步 / 多设备、L3、外部用户、Beta 或商业化。
- 不重写 P3-001 为生产应用，不做无关重构、技术栈迁移或工程目录大调整。
- 不冻结 Schema、API、UI、Tauri capability、正式导出格式、生产 SLA 或最终目录结构。
- 不调整核心领域实体、技术架构合同、V1 范围或 AI 权限边界；如修复必须改变这些冻结边界，立即暂停并标记“需 PM 确认”。
- 不自行把 P3-001 恢复为工程基线，不自行关闭 R-0041，不自行宣称独立复评通过。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/tasks/LIFEOS-P3-001_min_vertical_slice_engineering.md`
- `lifeos/tasks/LIFEOS-P3-003_p0_remediation_and_regression.md`
- `lifeos/tasks/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`
- `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- `lifeos/deliverables/LIFEOS-P3-003_p0_remediation_and_regression_report.md`
- `lifeos/reviews/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-004_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-001/README.md`
- `lifeos/engineering/LIFEOS-P3-001/src/lifeos_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-001/fixtures/synthetic_v1.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`
- `lifeos/deliverables/LIFEOS-P2-016_technical_architecture_freeze_decision_package.md`
- `lifeos/FREEZE_STATUS.md` 中 P3-001、P3-004、技术架构、MVP 开发准入相关行
- 决策 `D-0138`、`D-0139` 与风险 `R-0041`

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的直接依赖。
- 重点读取 P3-004 报告第 4、5、6、7 节；三项新增 P0 是强制关闭项。
- 不主动读取完整 `lifeos/PROJECT_CONTEXT.md`；如发现需要改变产品定位、V1 范围、技术架构、数据模型或 AI 权限边界，停止实现并请求 PM 确认。
- 不主动读取全量项目历史或无关 Review / Deliverable / Evidence。
- 测试日志写入 evidence；聊天只报告 PASS / FAIL、P0 失败数、P1 遗留与关键路径。

## 工程与证据路径

在既有 P3-001 工程目录内完成最小补丁：

- 实现与测试：`lifeos/engineering/LIFEOS-P3-001/`
- evidence：`lifeos/engineering/LIFEOS-P3-001/evidence/`
- 返工报告：`lifeos/deliverables/LIFEOS-P3-005_second_p0_remediation_and_regression_report.md`

如新增专项 evidence 文件，应从 `evidence/MANIFEST.md` 建立可追踪入口；不要另建会被误认为生产目录的新工程骨架。

## 角色检查点

主责角色必须重点回答：

- 三项 P0 是否在实现层根因修复，而非只屏蔽 P3-004 的临时反例？
- 修复是否保持 SQLite + FTS-first、权威 / 派生 / outbox 分责和消费前重检合同？
- 全部测试与 evidence 是否可复跑、断言驱动并唯一定位本次代码快照？

协审角色必须重点检查：

- AI 信任与安全：证据撤回是否传播到 AI 候选；授权上下文缺失 / 冲突是否 fail closed。
- 数据 / 领域模型：Derivation 与完整证据集合、ArtifactVersion、Authorization、Feedback、Link 的身份关系是否清楚。
- 技术架构：恢复门是否读取权威当前状态；消费入口是否重检来源、版本、tombstone、generation、证据和授权。
- 质量 / 测试：P3-004 三项反例是否全部成为自动回归测试；是否覆盖旧包、伪造控制包、非主证据撤回、冲突授权和真实消费入口。
- PM：任务未扩展到真实能力、UI、冻结、Gate 5、Beta 或商业化结论。

## 核心问题

请重点回答：

- 三项 P0 的根因、最小修复和对应自动回归测试分别是什么？
- 恢复候选是否必须读取权威当前状态？旧包 / 伪造控制包是否不能再恢复对象？
- Derivation 是否持久化完整证据依赖？任一证据撤回是否会使候选失效或阻断导出？
- 所有消费入口是否显式传入授权上下文？冲突 / 缺失 / 歧义 Authorization 是否 fail closed？
- 原 16 项验证集和新增回归集的 PASS / FAIL、P0 失败数、P1 遗留是什么？
- 是否存在范围、架构、核心语义或 AI 权限边界偏离？

## 交付物

请将完整返工报告保存为：

`lifeos/deliverables/LIFEOS-P3-005_second_p0_remediation_and_regression_report.md`

报告必须包括：

- 结论摘要，并明确区分事实、推断、建议
- 三项 P0 的根因、代码改动、测试 ID、断言与结果对照
- 创建 / 修改文件清单
- 复跑命令和测试摘要：PASS / FAIL、P0 失败数、P1 遗留
- H2、H4、H5、H9 与 `T-ARCH` 对照
- evidence manifest 路径与快照标识
- 原 16 项验证集回归结果
- 能力启用请求；如无，写“无”
- 范围 / 架构 / 核心语义 / AI 权限边界偏离；如无，写“无”
- 未关闭风险、需 PM 确认事项与后续独立复评建议

## 验收标准

只有满足以下条件，任务才算完成：

- 三项 P0 均有实现层修复和自动回归测试，且 P0 失败数为 0。
- 旧包、旧控制快照或重算校验伪造控制包不能再自证恢复对象。
- Derivation 完整证据依赖已持久化，任一证据撤回 / 删除 / 断源 / 授权失效后候选失效或被导出阻断。
- `read_artifact()`、`recovery_package()`、`search()`、`export_test_package()` 等真实消费入口在授权上下文缺失 / 冲突 / 歧义时均 fail closed。
- 原 16 项验证集完整通过，且新增回归测试实际纳入统一验证命令。
- evidence 由真实断言 / 结果生成，manifest 能唯一定位本次内容快照且不夸大覆盖。
- 已生成指定返工报告，并完成本地预检或说明允许跳过的原因。
- 未处理真实数据、未启用真实能力、未扩 UI、未修改 Stitch、未冻结新的生产资产。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，只输出摘要、报告路径、evidence 路径、测试结果和是否需要 PM 决策。

若任何 P0 失败、三项 P0 缺少真实执行路径证据，或修复必须改变冻结边界，任务必须报告 `Partial` / `Blocked`，不得写 Pass、Accepted 或已恢复工程基线。

## 限制条件

- 只允许使用合成数据和本地受控目录。
- 只允许修改关闭三项 P0、必要测试和 evidence 所需的最小文件。
- 不允许删除或弱化既有测试来获得通过结果。
- 不允许调用真实云 / 第三方模型、上传数据、创建外部账号、部署服务或调用付费资源。
- 不允许启用真实 Vault、Tauri 文件能力、导出路径扩权、向量、同步 / 多设备、L3、外部用户 / Beta / 商业化。
- 不允许冻结 Schema、API、UI、Tauri capability、正式导出格式、生产 SLA 或最终目录结构。
- P3-005 完成后仍须 PM 验收，并建议另行启动再次独立工程复评；本任务自身不能把 P3-001 标记回工程基线。

## 回复格式

请严格使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`。聊天中不要粘贴完整报告或大段日志。
