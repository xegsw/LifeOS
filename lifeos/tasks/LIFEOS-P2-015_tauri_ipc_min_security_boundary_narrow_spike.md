# LIFEOS-P2-015｜Tauri / IPC 最小安全边界窄测

## 启动语

请先读取当前项目根目录的 `AGENTS.md`，再读取：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- 本任务输入材料中列出的直接依赖文件

你是 LifeOS 项目的专项任务会话，不是 PM 主会话。请只完成下方任务，不要自行扩大范围。

## 任务信息

- 任务 ID：LIFEOS-P2-015
- 任务名称：Tauri / IPC 最小安全边界窄测
- 优先级：P0
- 任务类型：研究型任务（技术 Spike 执行，允许有限本地验证代码）
- 建议篇幅：2000-4000 字正文；原始日志、测试结果、路径攻击样例和失败证据放入证据目录，不计入正文
- 主责角色：技术架构负责人
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、体验设计负责人、PM
- 必须通过的评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 状态：Ready

## 背景

`LIFEOS-P2-012` 与 `LIFEOS-P2-013` 已确认：Tauri / IPC 最小安全边界窄测是技术架构冻结前硬条件。原因是 LifeOS 若采用桌面壳，Renderer、IPC、文件 scope、Obsidian 只读来源和导出写入边界必须先证明不会绕过领域授权门。

本任务只做最小可丢弃集成或等价可执行 harness 的安全边界验证。它不是正式桌面端开发，不冻结 Tauri capability 名称、IPC 命令签名、API、文件布局或技术架构。

## 目标

本任务完成后，需要回答：

1. Renderer 是否无法获得任意文件读写、目录遍历、shell、进程、网络或通用路径能力？
2. IPC 命令是否必须经过后端授权门、路径规范化、scope 校验、来源 / 版本 / generation / 租约重检？
3. Obsidian Vault 是否满足零写命令、零删除命令、零重命名命令？
4. 导出是否只能写入用户授权目标，且覆盖 / 合并需要明确确认？
5. IPC 返回内容是否保留用户原文、外部来源、AI 派生、AI 推断 / 建议、用户确认等内容身份？
6. 当前结果是否足以关闭 R-0040，或需要降级 / 返工？

## 范围

本任务必须覆盖：

- 使用最小可丢弃 Tauri 集成，或等价可执行 harness；纯说明、截图或人工推理不足。
- 使用合成目录与合成文件，不使用真实 Vault、真实用户文件、真实路径或真实敏感内容。
- 构造临时允许根、模拟 Obsidian Vault、授权导出目录、边界外目录、symlink 越界样例、隐藏 / 排除项、异常编码、`..`、绝对路径注入、NUL 等攻击样例。
- 枚举最小命令白名单和默认拒绝路径。
- 验证 IPC 响应内容身份不丢失。
- 形成证据包入口 `README.md` 或 `MANIFEST.md`。

## 非范围

本任务暂时不要做：

- 不开发正式桌面端、正式 UI、正式导出功能、正式 Obsidian 接入或正式设置页。
- 不冻结 Tauri capability 名称 / 配置、IPC 命令签名、API、Schema、文件布局或技术架构。
- 不修改 Stitch、PRD、V1 范围、核心领域模型或 AI 权限模型。
- 不连接真实 Obsidian Vault，不处理真实敏感数据。
- 不调用真实模型、真实云、真实第三方 API、外部账号或付费资源。
- 不进入正式 MVP 开发。
- 不为了通过测试而放宽用户授权、来源追踪、Obsidian 只读、导出确认、AI 内容身份或日志隐私底线。

## 授权的本地修改范围

本任务明确允许专项会话：

- 在 `lifeos/spikes/P2-015-tauri-ipc-boundary/` 下创建和修改最小可丢弃 Tauri 集成或等价 harness、合成目录 / 文件夹具、IPC / capability / 路径 scope 测试脚本、路径攻击样例、测试矩阵、原始结果、失败样例、环境说明和证据入口。
- 在 `lifeos/deliverables/` 下创建最终 Markdown 交付物：
  - `lifeos/deliverables/LIFEOS-P2-015_tauri_ipc_min_security_boundary_narrow_spike_report.md`
- 运行本地命令执行验证。
- 创建临时目录用于测试，但必须是明确任务目录或系统临时目录；不得使用 `$HOME`、`~`、仓库根目录或广泛路径作为清理目标。

本任务不允许专项会话修改 PM 文件、现有非 Spike 项目代码或无关文件；不得删除、覆盖或移动用户真实数据。

## 输入材料

请参考：

- `lifeos/CURRENT_STATUS.md`
- `lifeos/PM_OPERATING_MODEL.md`
- `lifeos/ROLE_MATRIX.md`
- `lifeos/STAGE_GATES.md`
- `lifeos/FREEZE_STATUS.md` 中“技术架构”“技术架构冻结条件最终补丁”“Obsidian 只读接入条件需求”“MVP 开发准入”相关行
- `lifeos/RISK_LOG.md` 中 R-0040
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/deliverables/LIFEOS-P1-017_obsidian_readonly_condition_requirements.md`
- `lifeos/reviews/LIFEOS-P1-017_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-003_sp02_obsidian_readonly_source_identity_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-003_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-004_sp04_authorization_processing_boundary_spike_report.md`
- `lifeos/reviews/LIFEOS-P2-004_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-013_technical_architecture_freeze_condition_final_patch.md`
- `lifeos/reviews/LIFEOS-P2-013_pm_review.md`
- `lifeos/DECISION_LOG.md` 中 D-0098、D-0117、D-0118

读取规则：

- 先读取 `lifeos/CURRENT_STATUS.md`，再读取本任务卡明确列出的输入材料。
- 优先读取 P2-013 第 6 节 Tauri / IPC 窄测合同、P1-017 的 Obsidian 只读边界、P2-004 的授权判定边界。
- 不主动读取完整 evidence 日志；先读 evidence `README.md` / `MANIFEST.md`，仅在需要复核失败原因时读取对应日志。
- 不主动读取完整 `PROJECT_CONTEXT.md`，除非发现产品定位、V1 范围、技术架构、数据模型或 AI 权限边界冲突。
- 不主动读取全量 `DECISION_LOG.md`；只读取任务卡指定决策或最近 5-10 条相关决策。
- 如果上下文不足，先列出缺少哪些文件和原因，不自行全量翻历史。
- 聊天回复只输出摘要、交付物路径、是否需要 PM 决策。

## 核心 P0 断言

必须至少验证并报告：

1. Renderer 无任意文件读写、目录遍历、原始数据库、shell、进程、网络或通用路径命令。
2. 未知 IPC 默认拒绝。
3. 路径必须规范化，并以真实路径核对允许根。
4. `..`、绝对路径注入、异常编码、NUL、symlink 越界、scope 外 token 默认拒绝。
5. `.obsidian`、隐藏 / 排除项、未授权附件默认拒绝。
6. Obsidian Vault 写命令、删除命令、重命名命令均为 0。
7. 通用写命令不能借路径参数写入 Vault。
8. 导出仅写用户授权目标；越界、静默覆盖 / 合并、执行导出内容均拒绝。
9. IPC 响应必须保留来源、版本和内容身份：用户原文、外部来源、AI 派生、AI 推断 / 建议、用户确认。
10. 执行前必须重检授权、来源、版本、tombstone / restriction generation 与租约；不匹配即 fail closed。
11. 日志不得泄漏正文、真实路径、真实 Vault 名、完整 prompt / 输出或可还原敏感数据。

## Pass / Conditions / Fail 标准

- Pass：全部 P0 断言通过；越权成功、Vault 写 / 删 / 改名命令、导出越界、身份丢失均为 0；证据包可复核。
- Pass with Conditions：全部 P0 安全断言通过，仅非目标平台、打包模式或非 V1 能力存在有限缺口；相关能力关闭，条件与补测触发器获 PM 接受。
- Fail：任一 P0 断言失败或无可执行证据；任意文件权、越界、Vault 写能力、导出越界、默认放行、身份丢失均直接 Fail。

## 角色检查点

主责角色必须重点回答：

- Tauri / IPC 边界是否真的关闭 R-0040？
- 最小实现或 harness 是否足以作为冻结前证据，而不是文档推理？
- 如果失败，应关闭哪些命令、收窄哪些 capability，或是否需要更换桌面壳候选？

协审角色必须重点检查：

- AI 信任与安全负责人：授权门、默认拒绝、重大动作确认、AI 内容身份和日志隐私是否成立。
- 数据 / 领域模型负责人：Source、Artifact、版本、Derivation、Feedback、Authorization、tombstone / generation 是否在 IPC 响应中保留。
- 体验设计负责人：权限拒绝、越界、导出确认、只读限制和失败状态是否能转译成用户可理解状态。
- PM：本任务是否只关闭 R-0040，不偷渡技术架构冻结或 MVP 准入。

## 交付物

请将完整交付物保存为：

`lifeos/deliverables/LIFEOS-P2-015_tauri_ipc_min_security_boundary_narrow_spike_report.md`

交付物至少包括：

1. 执行摘要
2. 测试环境与最小集成 / harness 说明
3. 合成目录与攻击样例说明
4. 验证方案与证据入口
5. P0 断言结果矩阵
6. Renderer、IPC、路径 scope、Vault 只读、导出边界与内容身份结果
7. 日志隐私扫描结果
8. Pass / Conditions / Fail 结论
9. 可冻结输入、不可外推内容与降级建议
10. 风险与待 PM 确认事项

## 验收标准

只有满足以下条件，任务才算完成：

- 已运行最小可执行验证，或明确说明本机环境阻塞和等价验证边界。
- 完整证据包已写入 `lifeos/spikes/P2-015-tauri-ipc-boundary/`，并有 `README.md` 或 `MANIFEST.md`。
- 完整交付物已保存到指定路径。
- 明确区分事实、实测、估算、推断和建议。
- 覆盖所有 P0 断言。
- 明确结论是 Pass、Pass with Conditions、Fail 还是 Blocked。
- 明确哪些结论需要 PM / 用户确认。
- 会话回复使用 `lifeos/templates/SESSION_REPORT_TEMPLATE.md`，且不粘贴完整交付物正文。

## 限制条件

- 不修改产品代码。
- 不修改 Stitch。
- 不处理真实敏感数据、真实 Vault 或真实第三方数据。
- 不调用真实模型、真实云、真实第三方 API 或付费资源。
- 不冻结技术架构、Schema、API、Tauri capability、IPC 命令签名或 MVP 开发准入。

## 回复格式

请严格使用：

`lifeos/templates/SESSION_REPORT_TEMPLATE.md`

注意：会话回复不要粘贴完整交付物正文，只输出摘要和交付物路径。
注意：不要在聊天中复述任务卡全文、历史背景或大段决策；完整内容写入交付物文件。
