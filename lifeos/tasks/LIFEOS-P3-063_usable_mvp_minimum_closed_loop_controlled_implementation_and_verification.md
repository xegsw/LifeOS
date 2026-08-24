# LIFEOS-P3-063｜可真实使用 MVP 最小闭环受控实现与验证

## 授权与安全语境

> **授权与安全语境：** LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限任务卡指定的本地工作区、隔离工程目录和非敏感合成测试记录，用于防御性软件工程、最小本地运行闭环实现、缺陷修复与回归验证；不涉及外部目标、真实用户数据或真实凭据、未授权访问、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。文中“权限、撤回、攻击、反例、旁路、风险”等术语仅用于本项目内部的防御性验证，不授权扩大操作范围。真实文件导出、Vault、云、第三方模型、同步、多设备、L3、外部用户和 Stage 4 仍未获授权。

## 任务信息与路由

- 任务 ID：`LIFEOS-P3-063`；优先级：P0；类型：受控本地 MVP 实现与验证；建议篇幅：2500–4000 字；P3 Engineering Fast Lane：No。
- 推荐执行 Agent：Codex，新建隔离工程执行会话；推荐模型／推理强度：`gpt-5.6-terra` + `xhigh`。
- 推荐理由：该任务首次把受控工程约束用于可运行的本地 MVP 闭环，涉及“已保存”语义、来源身份、恢复与用户确认，必须与既有独立评审会话隔离。
- 允许降级模型：None；后备模型：None。
- 禁止降级条件：任何耐久保存、来源／AI 身份、恢复、确认语义、权限边界、R-0040、真实运行环境或 P0/P1 判断。
- 必须升级条件：发现需启用 Tauri/IPC、真实文件路径、真实个人数据、云／第三方、外部用户或无法在隔离本地环境验证耐久／恢复时，立即停止并回报 PM；不得自行换模或扩大范围。
- 是否需要后续独立评审：Yes。执行会话不得评审自己成果；PM 验收后必须新建隔离独立工程／体验复评。
- 是否允许修改工程文件：Yes，仅限 `lifeos/engineering/LIFEOS-P3-063/` 与本任务明确的交付物／Evidence／本地预检路径。
- 是否允许修改项目账本：No。
- 主责角色：技术架构／工程实现；协审：产品、数据／领域模型、AI 信任与安全、独立 QA／体验。
- 必须通过的关卡：Gate 1、2、3、4 的本任务适用定义与受控运行证据；不得判定任一 Stage 4 Gate 通过。
- 状态：Ready。

## 会话与读取

- 使用全新隔离 Codex 工程执行会话；不得复用 P3-061／P3-062 的阶段治理会话、P3-050／P3-054／P3-057 的独立评审会话，或任何将执行本任务后续独立复评的会话。
- 最小启动包：`AGENTS.md`、`lifeos/CURRENT_STATUS.md`、本任务卡、`lifeos/templates/ENGINEERING_FAST_LANE_REPORT_TEMPLATE.md`（仅作报告结构参考）、`lifeos/templates/SESSION_REPORT_TEMPLATE.md`。
- 定向规则补读：`PM_OPERATING_MODEL.md` 的 P0、独立评审、用户确认与冻结规则；`ROLE_MATRIX.md` 的产品／数据／AI 信任／技术／体验检查点；`STAGE_GATES.md` 的 Stage 3→4 与 Gate 1–5；`FREEZE_STATUS.md` 当前阶段判断。
- 直接输入：`lifeos/reviews/LIFEOS-P3-062_pm_review.md`、`lifeos/deliverables/LIFEOS-P3-062_stage3_to_stage4_admission_baseline_and_minimum_capability_acceptance_package.md`、`lifeos/reviews/LIFEOS-P3-061_pm_review.md`、`lifeos/engineering/LIFEOS-P3-009/` 的只读骨架／测试入口、`lifeos/engineering/LIFEOS-P3-031/` 的只读候选 SQL／合同测试入口，以及 `RISK_LOG.md` 的 R-0019、R-0040 和相关开放风险。

## 授权范围与目标

在**全新隔离目录** `lifeos/engineering/LIFEOS-P3-063/` 中创建一个无需网络、无需 Tauri/IPC、无需 Vault／文件选择器的本地可运行最小闭环，仅使用非敏感合成记录：

1. 用户在受控本地入口输入一条记录，系统只在 SQLite 事务提交成功后显示“已保存”。
2. 保存后可看到原文与来源身份；AI 生成／推断／建议必须保持默认关闭，且不得与用户原文混淆。
3. 用户可恢复一个受控 Project 上下文，并显式确认一个下一步；不得自动创建承诺、外部动作或 L3 行为。
4. 对进程重启／重新打开、写入失败、重复提交和错误“已保存”提供可复现验证；失败必须可见、不得静默丢失。
5. 生成可复跑的本地运行脚本、测试、结构化结果、日志、快照和 Evidence Manifest；所有测试数据及临时数据库必须在 P3-063 隔离目录内。

“可运行”指本地受控运行时可由执行者启动、完成上述闭环并复跑，不代表真实 Tauri 桌面壳、真实个人数据、真实文件系统接入或外部用户可用。

## 非范围与硬停止条件

- 不修改 `lifeos/engineering/LIFEOS-P3-009/`、`lifeos/engineering/LIFEOS-P3-031/`、任何历史 Evidence 或项目账本；只读引用其约束。
- 不安装、配置、运行或模拟真实 Tauri／IPC capability；不访问真实系统路径、Vault、Obsidian、用户目录或文件选择器。
- 不使用真实个人数据、真实用户数据库、真实凭据、真实云／第三方模型、网络服务、导出、同步、多设备、外部用户或 L3。
- 不冻结 Schema/API、工程基线、导出格式、运行时配置或 Stage 4；不关闭／重开风险。
- 若闭环需要 Tauri/IPC、真实路径 scope、真实数据或任何外部写入，必须停止并记录 `Blocked`，由 PM 决定是否另行启动 R-0040 专项前置验证；不得用 mock 冒充真实 Tauri/IPC。
- 若出现 P0/P1、无法证明“已保存”只在提交后显示、来源／AI 身份混淆、恢复越过授权／tombstone 约束、Evidence 不可复跑或范围越界，必须停止并如实报告，不得以测试数量抵消。

## 必须交付与验收

- 工程资产：仅在 `lifeos/engineering/LIFEOS-P3-063/`；包含最小运行入口、SQLite schema／适配层、测试、合成夹具、复跑脚本和 `evidence/MANIFEST.md`。
- 交付物：`lifeos/deliverables/LIFEOS-P3-063_usable_mvp_minimum_closed_loop_controlled_implementation_and_verification.md`，明确事实、测试统计、退出码、P0/P1/P2/Unknown/Not Implemented、范围、失败路径、只读输入 hash 与未实现能力。
- 独立复评输入：保存执行侧测试日志、结构化结果、快照、运行说明、hash 和 `evidence/MANIFEST.md`；不得覆盖 P3-009/P3-031 或历史失败 Evidence。
- 默认运行本地预检；不可用时记录允许跳过原因。会话回复使用 `SESSION_REPORT_TEMPLATE.md`，只输出摘要、路径和需要 PM 决策。
- 通过最低条件：完整闭环在隔离本地运行中可重复验证；失败不显示成功；原文／来源／AI 内容／确认状态可区分；无自动外部动作；无 P0/P1、Unknown、Not Implemented 或范围越界。即使通过，也只可进入 PM 验收和隔离独立复评，绝不等于 Stage 4。

## Rework 授权（D-0273）

PM 已确认执行侧 7 项程序化夹具测试有效，但将该成果调整为 Rework：`scripts/run_demo.py` 把原文、幂等键和下一步确认文本写死，不能满足“操作者输入记录并显式确认下一步”的验收标准。

- 用户已授权仅在 `lifeos/engineering/LIFEOS-P3-063/` 内执行窄 Rework。
- 必须增加可由操作者提供的本地**合成**原文、幂等键和下一步确认文本入口；可为无网络的命令行交互或明确参数入口，但不得继续仅依赖固定夹具。
- 必须增加端到端正／负测试：正常输入、空输入、幂等冲突、提交前失败、显式确认与不产生外部动作；成功回执仍只能在提交后显示。
- 不得改动原任务的任何禁止边界、模型路由、目录授权、Evidence 保留、独立复评或 Stage 4 限制。
- 可复用原 P3-063 工程执行会话（若其仍只处理本任务且无未完成其他工作）；若不可用，则新建隔离 Codex 工程会话。无论何种方式，执行会话不得承担后续独立复评。
