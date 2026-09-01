# LIFEOS-P3-142｜模型设置与 AI 服务配置中心 V1——合成离线完整闭环

## 任务信息

- 任务 ID：LIFEOS-P3-142
- 标题：模型设置与 AI 服务配置中心 V1——合成离线完整闭环
- 风险等级：L2
- 优先级／缺陷严重性：P1
- 状态：Accepted / Complete / PM Pass / Governance V2.1 L2 / Not Frozen
- 主责 Agent／会话类型：Codex 工程执行会话；可复用同一设置／Runtime 工程线会话，但不得与 P3-141 Phase C 并行修改
- 所需执行能力：本地文件、离线构建与测试、actual Tauri、三档原生窗口视觉操作、结构化 Evidence
- 是否需要独立评审：Conditional
- 独立评审触发理由：本任务为合成离线 L2，默认由包内自检与 PM 验收关闭；只有实际触及凭据／网络／真实 Provider，发生不可恢复 Evidence 污染，或 PM 发现长期基线回退争议时才升级独立评审。本任务不得自行升级范围。

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务仅实现合成离线的设置中心、Provider／Capability 合同与 Tauri UI，不授权访问 Pilot、真实 DB、真实路径、真实文本、真实 API Key、网络、云端或本地真实模型服务。需要这些边界时立即停止并回报 PM。

本任务由用户在完整方案与视觉参考展示后要求创建，并于 2026-09-01 明确回复“开始”。工程任务已按完整合同投递至隔离 worktree；合同内实现、测试、actual-Tauri、Evidence、Manifest 与包内修正不再重复确认。

## Task Contract

### 1. 唯一用户结果

用户得到一个与 LifeOS 现有高保真风格一致、可在 actual Tauri 中运行的中文“模型设置 / AI 服务配置中心 V1”：普通用户只配置一个可替换的主 AI 服务，LifeOS 在内部根据 Provider Registry、Capability Registry、授权策略和服务状态自动汇总并路由文字、视觉、语音、工具调用与长文本能力；所有行为使用固定合成数据和离线 Adapter 完成，不产生任何真实网络或凭据接触。

### 2. 允许范围

- 允许修改目录／文件：
  - `lifeos/engineering/LIFEOS-P3-142/`
  - `lifeos/deliverables/LIFEOS-P3-142_model_settings_ai_service_configuration_center_v1.md`
- 唯一临时根：`/private/tmp/lifeos-p3-142-ai-service-config-center-v1`
- 临时根内允许：全新合成 SQLite DB、合成配置、离线 loopback fixture、构建缓存、actual-Tauri App bundle、截图与 Evidence；必须以 task marker 绑定并在结束时精确清理。
- 允许只读输入：
  - `lifeos/architecture/LifeOS架构基线V1.0.md`
  - `lifeos/architecture/LifeOS高保真原型IA-V1.0.md`
  - `lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md`
  - `lifeos/deliverables/LIFEOS-P3-128_person_context_memory_core_domain_mapping_and_fast_track_engineering_contract.md`
  - `lifeos/tasks/LIFEOS-P3-141_person_level_work_health_controlled_n1_pilot_revision_2.md`
  - `lifeos/deliverables/LIFEOS-P3-141_revision-3_bundle-lineage-and-native-capture-closure-v5_report.md`
  - `lifeos/engineering/LIFEOS-P3-141/revision-3-model-settings/candidate/`
  - P3-139、P3-140 与 P3-141 已确认的任务／Review／Evidence，只在任务卡明确引用时定向只读
- 视觉参考：`/Users/xxe/.codex/generated_images/01a0290d-4255-7c52-8e62-6b888d2d678a/exec-db38fb92-44d7-4faa-868a-bd6d38938e0d.png`。该图提供 Shell、留白、色彩、卡片、字号与密度方向；本任务以下文字合同优先于图中旧的信息架构。
- 允许数据：固定、无个人含义、可公开的合成 Provider 配置和合成能力 metadata；禁止使用看似真实的 API Key。
- 允许 Provider 目录：
  - 云端服务：OpenAI、Anthropic、Google Gemini、DeepSeek、Kimi、OpenRouter、其他 OpenAI-compatible 服务、自定义兼容接口。
  - 本地服务：Ollama、LM Studio、OpenAI-compatible 本地接口、自定义本地服务。
  - 以上只表示可选择的可扩展目录；默认页面只能有一个主服务，不得把多个 Provider 显示为同时已连接。
- 允许接口：保持 P3-141 已确认的恰好 20 项 IPC，不增不减：
  1. `capture_record`
  2. `get_today`
  3. `runtime_status`
  4. `confirm_capture_context`
  5. `get_context_recovery`
  6. `get_context_next_action`
  7. `decide_context_next_action`
  8. `record_action_result`
  9. `assemble_global_ai_context`
  10. `get_evidence_backed_understanding`
  11. `decide_understanding_feedback`
  12. `get_ai_provider_settings`
  13. `save_ai_provider_settings`
  14. `save_ai_provider_credential`
  15. `test_ai_provider_connection`
  16. `set_ai_provider_enabled`
  17. `upsert_durable_memory`
  18. `update_current_state`
  19. `resolve_request_context`
  20. `get_context_disclosure_receipt`
- 设置中心新增状态通过版本化严格 DTO 进入既有设置 IPC；不得用新增 IPC 绕过合同。
- 允许实现：Provider Registry、Capability Registry、Capability Router、Synthetic/Offline Provider Adapter、Synthetic CredentialPort、非敏感 Provider Config 持久化、离线 capability discovery、合成配置关闭重开恢复。

### 3. 禁止范围

- 不实现：真实 Provider Adapter 调用、真实模型列表、真实 Capability Probe、真实云端补齐、真实自动切换、真实语音／视觉模型调用、真实 OS Credential Store、真实 API Key 生命周期、真实网络失败语义、Phase C 或 Pilot。
- 不访问、探测、stat、hash、读取、复制、修改或清理：任何 Pilot 目录、真实 DB、真实用户路径／文件／文本、旧 `/private/tmp` Runtime 根、系统凭据库、环境变量中的凭据、网络端点、云服务、本地 Ollama／LM Studio 实例。
- 不修改：P3-139／P3-140／P3-141 候选、Evidence、Review、Manifest、ABF 或历史；`lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md`；Frozen Architecture V1.0；PM 账本；风险；冻结状态；Stage。
- 不允许 UI 直接访问厂商 SDK、网络、SQLite SQL、Credential Store、本地模型进程或 API Key。
- 不把完整凭据写入页面、普通业务表、日志、错误、截图、Evidence、Manifest、导出或聊天。
- 不将 P3-141 的“加密 SQLite 凭据”权威语义静默改为 Keychain。P3-142 只提供 Synthetic CredentialPort 合同；未来是否迁移至 OS Credential Store 必须由新的 L3 任务和用户确认决定。
- 不创建 P3-143，不关闭或重开 R-0056，不恢复 P3-141 Phase C，不冻结产品，不进入 Stage 4。

### 4. 架构边界

必须遵循：

```text
UI
  ↓
Application
  ↓
Domain / Capability
  ↓
Ports
  ↓
Adapters
```

- `ModelPort`：表达厂商无关的推理能力。
- `ModelProviderAdapter`：Provider 适配层；合成任务只能使用 Synthetic/Offline 实现。
- `Provider Registry`：记录支持、配置与启用状态，Provider 集合须可扩展，不能散落硬编码在业务页面。
- `Capability Registry`：由 Adapter metadata 报告 `text.reasoning`、`vision.understanding`、`speech.transcription`、`speech.synthesis`、`tool.use`、`long_context`、`structured_output`、`embedding` 等能力，不得仅凭厂商名猜测。
- `Capability Router`：依据任务能力、授权、本地／云端策略、服务状态、能力、处理位置、上下文与备用服务选择 Adapter；没有授权时必须失败关闭。
- `Provider Configuration`：只保存非敏感配置。
- `CredentialPort`：本任务只实现合成端口与不含秘密的引用，不引入真实凭据保存方案。

### 5. 页面与状态集合

- Global Shell：窄图标 Rail，一级入口仅 Today / Me / Contexts / Memory；Settings 为左下角弱化齿轮；无通知中心、铃铛、用户头像或账户卡片。
- Settings 二级导航：通用、模型设置、数据与隐私、备份与导出、关于；仅“模型设置”完整可用，其余明确“暂未开放”，不得伪装为已实现。
- 主 AI 服务：未配置态、已配置态、测试中、测试成功、认证／连接／能力合成失败态；默认只存在一个槽位。
- 添加／更换服务：云端与本地分组；云端／本地表单字段不同；Provider 列表可扩展。
- 能力状态：可用、本地处理、自动匹配、尚未配置、当前服务不支持、暂时不可用。
- 运行策略：优先使用本地、允许云端补齐、服务失败时自动切换、优先响应更快；云端补齐和自动切换默认关闭。
- 备用服务：可选、默认未配置，视觉权重低于主服务。
- 高级设置：默认折叠且所有能力覆盖为“自动”；可呈现文字、视觉、语音输入、语音输出、工具调用、温度、最大输出、超时、上下文与本地参数的合成设置。
- Global AI：所有主要页面可达；Settings 页视觉弱化。

### 6. Acceptance Contract

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | Settings 入口在 Global Shell 左下角，一级 Rail 仍为 Today／Me／Contexts／Memory 的纯图标结构 | actual Tauri 三档截图与 DOM/AX 定位 | 三档原生窗口截图、geometry、PID→AXWindow→WebView/Area |
| AC-02 | 页面视觉继承参考图的留白、字号、色彩、圆角、边框和 Global AI 空间关系，不成为企业后台或卡片墙 | 视觉矩阵与 PM 人工核验 | 三档同状态对比图、visual checklist |
| AC-03 | UI 全中文；Settings 是二级区域，其他分类仅真实标注暂未开放 | 文案扫描与交互检查 | 页面状态清单、负例扫描 |
| AC-04 | 默认只配置一个主 AI 服务；未配置态与已配置态均清晰 | UI 状态回放 | 两态截图与状态 JSON |
| AC-05 | 云端 8 类、本地 4 类 Provider 分组清晰，未把选项显示为同时连接 | Registry 查询、UI 选择器、负例 | Provider Registry snapshot、截图 |
| AC-06 | Provider 集合通过 Registry／Adapter metadata 扩展，不在 Core Domain 或页面分支中固定厂商世界观 | 结构扫描、增加 disposable synthetic provider mutation | 扫描结果、mutation result |
| AC-07 | 云端与本地配置表单只显示各自必要字段，非法或跨模式字段失败关闭 | DTO 正负矩阵 | structured results |
| AC-08 | Capability Registry 从 Adapter metadata 汇总文字、视觉、语音、工具、长文本等状态，不凭厂商名猜测 | metadata fixture 与 provider-name mutation | registry output、mutation result |
| AC-09 | 普通用户不需逐项选择文字／视觉／语音模型；缺失能力给出明确原因与补齐入口 | UI walkthrough | 状态截图与交互日志 |
| AC-10 | 云端补齐默认关闭；未明确授权时 Router 不得选择云端补齐 | router 正负测试 | decision receipt、fail-closed record |
| AC-11 | 自动切换默认关闭，且只能在已配置、已授权、处理政策匹配的服务之间发生 | router matrix | structured positive/negative results |
| AC-12 | 备用服务可选且视觉弱化，未配置不阻塞主服务 | UI／state test | 截图、state JSON |
| AC-13 | 高级设置默认折叠、默认自动，展开后覆盖项不改变 Core Domain | UI 状态与 DTO round-trip | before/after JSON、截图 |
| AC-14 | UI 只调用 Application DTO；不直接访问 SDK、SQL、网络、Credential Store 或本地模型进程 | dependency/static scan 与运行期 deny fixture | scan report、deny log |
| AC-15 | Provider Config 与 Synthetic Credential Reference 可保存，关闭重开后恢复；不出现明文秘密 | 两次 fresh restart、DB schema/值分类检查 | restart lifecycle、redaction scan |
| AC-16 | `API Key` 输入仅使用固定非秘密夹具；页面、日志、DB 普通表、错误、截图、Evidence 无完整值 | canary scan 与负例 | redaction report |
| AC-17 | 未知字段、非法 Provider、非法 URL、重复 Provider ID、非法 capability、越界优先级均在任何持久化或状态切换前失败关闭 | 输入矩阵与前后 DB snapshot | structured negative matrix |
| AC-18 | Cloud／Local 未保存草稿与持久化 active mode 分离；保存／测试／选择／启用行为不会跨模式漂移 | mode-switch lifecycle | action/state matrix |
| AC-19 | 恰好保留 20 项 IPC，设置新状态只经版本化严格 DTO 进入既有 IPC | 注册表扫描与 schema mutation | exact-list report、mutation result |
| AC-20 | P3-139／140／141 只读谱系不变；P3-141 已确认设置基线的既有不变量无回退 | before/after hash 与 baseline checklist | lineage report |
| AC-21 | Synthetic/Offline Adapter 不产生 DNS、HTTP(S)、真实 loopback 服务探测或模型进程接触 | network deny harness 与日志扫描 | zero-network report |
| AC-22 | 三档目标窗口 desktop／compact／narrow 均无截断、横向溢出、控件遮挡或不可达操作 | actual Tauri direct PID 核验 | 三档截图、geometry、AX evidence |
| AC-23 | 任务内确定性测试纳入 CI；串行与默认并行均通过，不依赖 GUI 或真实服务 | CI 与本地测试 | test logs、CI registration |
| AC-24 | 锁屏、AX、截图不可用时写 checkpoint 并 Paused — Resumable；恢复后只从受影响阶段继续 | checkpoint 演练或静态验证 | checkpoint schema／resume log |
| AC-25 | 唯一临时根具备精确 marker、权限、symlink／traversal／wrong-marker 失败关闭，结束后仅精确清理该根 | root negative matrix 与 cleanup | cleanup receipt、final absence |
| AC-26 | 工程交付物、Evidence、测试与候选形成可复核的非自指 Manifest；历史失败不被覆盖 | verifier | Manifest 与 verification result |

Pass 公式：AC-01～AC-26 全部通过；P0=0、P1=0、Unknown=0、Not Implemented=0；P2 仅允许存在不影响唯一用户结果、边界和复现性的已披露非阻断事实。任何真实网络、真实 Provider、真实凭据或 Pilot 接触直接停止，不得以本任务 Pass 覆盖。

### 7. Evidence 等级

- 本任务采用 L2：结构化正负路径、重复／重启、失败关闭、actual-Tauri 三档视觉、确定性测试、关键 mutation、只读谱系与精确清理 Evidence。
- 不要求独立 Frozen ABF 或强制独立评审。
- Evidence 至少包括：AC matrix、Provider/Capability registry snapshots、DTO 正负矩阵、router authorization matrix、restart lifecycle、redaction scan、zero-network report、IPC exact-list、baseline lineage、三档 native Evidence、root/cleanup matrix、test logs、Final Manifest 与 verifier。

### 8. 新任务触发器

- 只有要启用真实 API Key、OS Credential Store 或真实加密凭据迁移、真实网络、真实 Provider／模型列表／Capability Probe、本地 Ollama／LM Studio 连接、真实云端补齐／自动切换、Pilot 或真实个人数据时，才创建 L3 后继任务。
- Provider／Capability 接口、页面、合成 Adapter、测试、Evidence、Manifest、文案、布局和本任务内缺陷均留在 P3-142 Closure Cycle，不拆微任务。
- P3-143 只是后继编号建议；本任务不得自动创建。

### 9. CI / 可恢复执行

- CI 检查清单：格式／编译、strict DTO、Provider/Capability Registry、router authorization、invalid input fail-closed、restart persistence、credential redaction、exact 20 IPC、baseline lineage、zero-network、serial/default-parallel tests、Manifest verifier。
- 人工／环境 Gate：actual Tauri desktop／compact／narrow、direct PID→精确标题 AXWindow→WebView/Area、视觉核验。
- 检查点写入：`lifeos/engineering/LIFEOS-P3-142/evidence/checkpoint.json`
- 可恢复阶段：`preflight` → `build_test` → `data_lifecycle` → `app_launch` → `native_window_binding` → `visual_capture` → `cleanup` → `manifest`
- 最早受影响阶段：由候选、合同或环境变化首次影响的上述阶段确定；恢复时从该阶段继续，并仅重跑其下游依赖。
- 环境暂停：保存候选摘要、合同摘要、已完成阶段和 `resume_from`；桌面恢复且三者一致时只重跑受影响的 GUI 阶段及其下游 Manifest。
- 候选变化：从最早受影响的构建／测试阶段恢复；不机械重做仍由相同 candidate hash 支撑的无关阶段。
- 只有候选或合同身份无法恢复、历史被覆盖、禁止目标发生实质接触或正 Evidence 无法与污染资产分离，才触发 `Irrecoverable Invalidation`。

## 输入与最小启动包

必须读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/ACCEPTANCE_GOVERNANCE.md` 中 L2 与 Closure Cycle 条款
- `lifeos/CI_CD_GOVERNANCE.md` 中低风险分支、CI 与可恢复执行条款
- `lifeos/architecture/LifeOS架构基线V1.0.md` 中 UI→Application→Domain/Capability→Ports→Adapters、ModelPort、Authorization 与本地数据边界章节
- `lifeos/architecture/LifeOS高保真原型IA-V1.0.md` 中 Global Shell、Settings 与 Global AI 章节
- `lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md`
- P3-141 Revision 3 v5 交付物及其候选的定向输入

不得全文翻阅与任务无关的历史。若直接输入路径在执行分支缺失，停止并回报 PM，不以相似文件替代。

## 执行要求

1. 开始前检查已有修改并保全用户资产；P3-141 全部只读。
2. 先建立 P3-142 独立候选，不在 P3-141 目录直接修补。
3. 严格执行视觉合同；Runtime 只提供数据与能力状态，不改变布局、密度和 Shell。
4. 所有实现、测试、Evidence、Manifest 与同范围修正留在一个任务内。
5. 包内自检完成后提交 PM；专项会话不得修改 PM 账本、风险、冻结或 Stage。
6. 不自动启动真实能力任务或 P3-141 Phase C。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-142_model_settings_ai_service_configuration_center_v1.md`
- 候选：`lifeos/engineering/LIFEOS-P3-142/candidate/`
- Evidence：`lifeos/engineering/LIFEOS-P3-142/evidence/`
- Final Manifest：`lifeos/engineering/LIFEOS-P3-142/FINAL_MANIFEST.json`
- PM Review：`lifeos/reviews/LIFEOS-P3-142_pm_review.md`
- 复跑入口：由工程交付物给出 task-local 离线命令；不得依赖真实服务。

## PM 验收与交付策略

- PM 只按长期质量原则与 AC-01～AC-26 验收，不在提交后移动终点。
- 首次不通过一次性列明全部合同内缺口，进入同一 P3-142 Closure Cycle。
- 本任务为普通 L2；PM Pass 后按 D-0636 自动提交并推送 `codex/l2-*` 任务分支，CI 全绿且 main 可快进时自动合并。若仓库仍分叉则停止自动合并并回报，不 force push、不静默携带无关提交。
- PM Pass 只代表合成离线设置中心完成，不代表真实 Provider、凭据、网络、Pilot、风险关闭、产品冻结或 Stage 4。
