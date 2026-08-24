# LIFEOS-P3-074｜Alpha 使用说明受控草案与内部可理解性验证包

## 授权与安全语境

LifeOS 是用户本人拥有并明确授权维护的本地项目。本任务仅限指定本地工作区中的 Markdown 文档、既有只读 Review／Evidence 和合成场景，目的是防御性产品文案校对、边界澄清与本地回归式可理解性验证。

不涉及外部目标、外部用户、未授权访问、真实凭据、网络扫描、真实攻击、持久化、数据窃取或安全控制规避。任务中出现的权限、失败、导出、恢复或边界术语，仅用于准确说明本项目当前合成受控能力及其限制，不授权扩大操作范围。所有删除、权限、外部写入和重大行动仍须遵守既有用户确认与安全关卡。

## 状态、角色与模型路由

- 状态：`Ready / Awaiting Explicit Execution Authorization`。创建本任务卡不构成执行授权。
- 主责：新建或与工程执行隔离的 Codex 文档／验证专项会话；不得由 P3-072 执行会话自证。
- 推荐模型：`gpt-5.6-terra`；推荐推理强度：`high`。
- 选择理由：需将多项受控边界、已验证事实和未实现能力准确分层，避免把合成 Evidence 写成真实 Alpha 能力。
- 允许降级模型：`gpt-5.6-luna` + `high`。
- 禁止降级条件：涉及真实能力、风险关闭／重开、资产冻结、工程基线恢复、Stage 4 准入或范围冲突时不得执行，应回报 PM。
- 必须升级条件：出现 P0/P1、Evidence 冲突、越权范围或“当前能力是否已可真实使用”的判断歧义时停止并回报 PM。
- 后备模型：`gpt-5.5` + `xhigh`，仅在记录实际配置及原因后使用。

## 目标与直接输入

在不启动 Alpha、不给外部用户分发的前提下，完成一份**受控 Alpha 使用说明草案**及内部可理解性验证包。草案必须明确区分：

1. 当前仅在合成／临时沙盒中验证的受控能力；
2. 用户明确确认、拒绝／阻断、失败披露、恢复提示和退出／反馈的预期交互；
3. 尚未实现、默认关闭或仍需要单独授权的真实能力；
4. 已知限制、不可承诺事项和停止条件。

直接输入（只读）包括：

- `lifeos/CURRENT_STATUS.md`、`lifeos/FREEZE_STATUS.md`、`lifeos/RISK_LOG.md` 中 R-0040；
- `lifeos/STAGE_GATES.md` 中 Gate 1、3、4、5；
- P3-063／P3-064、P3-065／P3-066、P3-067／P3-069、P3-070／P3-071、P3-072／P3-073 的最终 PM Review、独立 Review（如有）、交付物及 Manifest；
- 本任务卡和当前 `lifeos/templates/` 中与专项交付物、PM 验收相关的模板。

## 允许范围与禁止事项

允许仅写入本任务自己的交付物和 Evidence 目录；历史任务、工程代码、主账本、风险、冻结状态及既有 Evidence 均只读。

不得联系、招募或引导外部用户；不得发布、分发或宣称启动 Alpha；不得启用真实 DB、个人数据、真实文件／路径、真实导出、Vault、Tauri/IPC、网络、云／第三方模型、同步、多设备、L3 或外部用户。不得关闭或重开风险、恢复工程基线、冻结资产、修改 Schema/API 或进入 Stage 4。

## P3-074+ 包内交付前自检关卡

在提交 PM 前，执行侧必须在干净临时文档副本完成并保留 Evidence：

- 首次阅读、重复阅读／幂等校对、版本更新后复读三种内部演练；本任务无运行时重启，版本更新后复读是经记录的等价替代。
- 对每项任务验收标准建立“验收标准 → 内部场景／检查项 → Evidence 文件”的逐项矩阵。
- 静态核查：不得将合成受控验证描述为真实能力、真实导出、真实恢复、已启动 Alpha 或 Stage 4 已准入；发现即在本能力包内纠正并重验。
- 保存可复查检查清单或 runner、逐项结构化结果、版本 hash、日志／快照、输入只读 hash、Manifest 与复跑说明。
- 明确核对历史只读资产未被覆盖，并在交付物中报告自检结论及任何未覆盖项；未覆盖项不得表述为通过。

执行侧在 PM 验收前发现的文案、测试、Evidence 或可理解性问题，须优先在本能力包内修正，不另建 Rework 任务号。只有 PM 验收或全新隔离独立复评发现实质 P0/P1、合同违反、Evidence 冲突、独立性不足、越权、范围扩大或关闭态失效时，才构成正式 Rework。

## 交付与验收

- 交付物：`lifeos/deliverables/LIFEOS-P3-074_alpha_usage_guide_controlled_draft_and_internal_clarity_package.md`。
- Evidence：`lifeos/engineering/LIFEOS-P3-074/evidence/` 或任务实际使用的等价 task-local 目录，必须含 Manifest。
- 本地预检：按 `lifeos/tools/local_precheck.py` 规则执行；超时、不可用或越界时记录后继续人工核验。
- 任务完成后仅提交 PM 验收；若未来拟将草案用于真实 Alpha、对外分发、真实用户路径或 Stage 4 准入，必须另建独立任务、独立复评并取得用户明确确认。

## 完成判定

只有在草案、内部场景矩阵和 Evidence 完整、所有受控能力与禁止边界准确、未把合成 Evidence 外推为真实能力且自检通过时，才可提交 PM。此任务通过不构成 Alpha 启动、Stage 4 准入、风险关闭、资产冻结或真实能力授权。

## D-0311 授权重跑指令

用户已授权在本任务原边界内进行一次干净、可追溯的重新执行。既有未授权交付物、执行侧 Evidence 和 PM Evidence 必须只读保留；不得覆盖、删除或改写。

- 仅可新增：`lifeos/deliverables/LIFEOS-P3-074_alpha_usage_guide_controlled_draft_and_internal_clarity_package_authorized_rerun.md` 与 `lifeos/engineering/LIFEOS-P3-074/evidence/authorized_rerun/` 下的 task-local Evidence。
- 必须在新建临时文档副本完成首次阅读、重复阅读／幂等校对、版本更新后复读等价演练；重新保存 runner、逐项结果、日志、输入 hash、Manifest、复跑说明与验收→场景→Evidence 矩阵。
- 仍不得触达真实数据、真实路径或文件导出、外部用户、Alpha、Tauri/IPC、网络、云／第三方模型、风险、冻结、工程基线或 Stage 4。
- 完成后只提交 PM 验收；本授权不构成对任何后续任务或真实能力的授权。
