# LIFEOS-P3-143｜真实 AI 服务与加密凭据安全启用闭环

## 任务信息

- 任务 ID：LIFEOS-P3-143
- 标题：真实 AI 服务与加密凭据安全启用闭环
- 风险等级：L3
- 优先级／缺陷严重性：P1
- 状态：Ready / Authorized / Engineering Start Pending / ABF-P3-143-v1 Frozen / Not Product Frozen
- 主责 Agent／会话类型：全新 Codex 隔离工程会话
- 所需执行能力：本地文件、Rust/Tauri、actual Tauri、SQLite、macOS Keychain、受控 HTTPS、原生窗口操作、结构化 Evidence
- 是否强制独立评审：是；工程 Gate Pass 后由未参与实现的全新隔离会话执行
- 用户授权依据：用户已明确要求 DeepSeek，并在 P3-142 完成后回复“创建并开始”；该授权覆盖本合同内工程、合成验证、一次 DeepSeek 真实 Gate、Evidence、同任务 Closure Cycle、独立评审和 PM 验收，不覆盖最终用户采纳、风险关闭、产品冻结或 Stage 4。

## 授权与安全语境

LifeOS 是用户本人拥有并授权维护的本地项目。本任务只启用用户主动配置的单一 DeepSeek 云端服务，并仅使用固定非敏感合成请求验证真实连接。用户只在实际 App 内手工输入 API Key；任何 Agent、脚本、日志、Evidence、聊天或截图不得读取、代填、回显、复制、hash 或保存明文 Key。

本任务不访问任何 Pilot、真实个人 DB、真实个人路径、真实文本、Health 数据或 Person Context。真实网络只允许在明确的 Real Gate 中、由用户动作触发、访问本合同冻结的 DeepSeek HTTPS authority；其他 Provider 保留在设置目录中，但不在本轮宣称真实可用。

## Task Contract

### 1. 唯一用户结果

用户可以在 P3-142 已完成的高保真中文“模型设置”页面中选择 DeepSeek 作为主 AI 服务，手工输入 API Key，将其以“SQLite 密文 + 与数据库分离的 macOS Keychain 密钥材料”跨重启保存；随后依次执行测试连接、读取可用模型、选择模型、明确启用，并仅对一条固定非敏感合成 canary 发起一次真实请求。删除凭据后，所有后续真实调用立即失败关闭。

### 2. 不得回退的既有产品基线

1. Settings 仍位于 Global Shell 左下角弱化齿轮入口；Today／Me／Contexts／Memory 与 P3-142 高保真布局不变。
2. Provider 目录不得减少：
   - Cloud 8：OpenAI、Anthropic、Google Gemini、DeepSeek、Kimi、OpenRouter、其他 OpenAI-compatible、自定义兼容接口。
   - Local 4：Ollama、LM Studio、OpenAI-compatible 本地接口、自定义本地服务。
3. Cloud／Local 选择器和配置字段必须分离；不得把 DeepSeek 或 Kimi 藏进 Custom。
4. API Key 产品语义固定为“加密保存在本地 SQLite 并跨重启”，不得恢复“本次会话”“环境变量”或明文普通业务表。
5. 保存配置、保存凭据、测试连接、选择模型、明确启用、发送数据是相互独立的动作；前一步不得静默触发后一步。
6. 保持恰好 20 项 IPC；本任务通过既有严格版本化 DTO 完成，不增删注册项。
7. 主 AI 服务仍是唯一默认槽位；备用服务可选且默认关闭；无自动 fallback、后台探测、并行发送或静默云端补齐。

### 3. 允许修改与运行范围

- 任务卡与验收依据：
  - `lifeos/tasks/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md`
  - `lifeos/tasks/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation_acceptance_basis_freeze.md`
  - `lifeos/tasks/LIFEOS-P3-143_acceptance_freeze_manifest.json`
- 工程与交付：
  - `lifeos/engineering/LIFEOS-P3-143/`
  - `lifeos/deliverables/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md`
- PM Review：`lifeos/reviews/LIFEOS-P3-143_pm_review.md`
- 唯一运行／Evidence 临时根：`/private/tmp/lifeos-p3-143-real-ai-secure-activation-v1`
- 临时根内允许：全新合成／Gate SQLite、构建缓存、App bundle、task marker、脱敏结构化 Evidence；结束时必须先由用户在 App 内删除凭据，再验证密文和 reference 已失效，最后 marker-gated 精确清理。
- 允许真实组件：macOS Keychain 中仅 P3-143 专用、可精确删除的密钥材料项；SQLite 只保存 API Key 密文、nonce／版本、Credential Reference 和非敏感配置。
- 允许真实网络：仅在 AC-17 Real Gate 中访问 `https://api.deepseek.com` 的明确 HTTPS authority；禁止 HTTP、重定向跨 authority、代理继承、任意自定义 endpoint、后台请求和其他域名。具体模型从用户主动测试返回结果选择，不在合同中写死易漂移模型名。
- 固定真实请求内容：工程在 ABF 中冻结的一条无个人含义、无项目含义、无路径和无凭据的短 canary；响应正文只在 App 内瞬时显示，不进入 Evidence。
- 允许只读输入：P3-142 任务、candidate、交付物、PM Review、Evidence／Manifest；P3-139／140／141 与 `lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md` 的定向基线输入。

### 4. 禁止范围

- 不访问、探测、stat、hash、读取、复制、修改或清理任何 Pilot、真实个人 DB、真实用户路径／文件／文本、Health 数据、Person Context、Memory 内容或旧 `/private/tmp` Runtime 根。
- 不读取、打印、截图、录屏、OCR、hash、导出、缓存或在聊天中索取 API Key；不得把 Key 放入命令行参数、环境变量、配置文件、日志或 Evidence。
- 不允许真实个人内容、P3-139 Context、P3-140 Today、P3-141 Pilot 数据进入 Provider 请求。
- 不真实连接 OpenAI、Anthropic、Gemini、Kimi、OpenRouter、Ollama、LM Studio 或 Custom；它们必须保留可见目录和正确状态，但本轮标记“未验证／尚未配置”。
- 不实现自动 fallback、后台健康检查、定时请求、自动重试未知结果、并行 Provider、工具调用、Agent 行动、语音／图片真实上传或云端补齐。
- 不修改 Frozen Architecture V1.0、核心领域模型、AI 权限与信任模型、P3-142 历史候选／Evidence／Review／Manifest、P3-141 ABF 或产品设置基线。
- 不关闭或降级 R-0055／R-0056，不恢复 Pilot-6，不冻结产品，不进入 Stage 4。

### 5. 架构与凭据边界

必须遵循：

```text
UI → Application → Domain / Capability → Ports → Adapters
```

- UI 只提交严格 DTO，不接触 SQL、网络、厂商 SDK、Keychain 或明文 Key 的持久化表达。
- `CredentialPort` 负责保存、装载、更新和删除；`ProviderConfiguration` 只保存非敏感字段和 Credential Reference。
- API Key 使用经审查的 AEAD 加密；SQLite 保存 ciphertext、nonce、algorithm/version、provider/profile identity 和 reference。
- 解密密钥材料保存在 macOS Keychain 的 P3-143 专用项，与 SQLite 文件物理分离；Keychain 项不得包含 Provider API Key 明文。
- 明文 API Key 只允许存在于用户输入控件和单次调用所需的有界内存；使用后立即清空 UI 与运行期副本，错误路径亦同。
- DB 被复制但缺少正确 Keychain 密钥、ciphertext／nonce／AAD 被篡改、reference 不匹配或密钥被删除时，必须在网络前失败关闭。
- `ModelProviderAdapter` 使用 OpenAI-compatible HTTPS 合同连接 DeepSeek；`Capability Registry` 只采信真实 probe／响应，不根据品牌猜测能力。
- `Capability Router` 只可选择当前用户明确启用的单一 DeepSeek profile；未启用、凭据缺失、未测试、模型未选或处理政策不匹配均不得发送。

### 6. 恰好 20 项 IPC

本任务保留 P3-142 的完整列表且不得增删：

`capture_record`、`get_today`、`runtime_status`、`confirm_capture_context`、`get_context_recovery`、`get_context_next_action`、`decide_context_next_action`、`record_action_result`、`assemble_global_ai_context`、`get_evidence_backed_understanding`、`decide_understanding_feedback`、`get_ai_provider_settings`、`save_ai_provider_settings`、`save_ai_provider_credential`、`test_ai_provider_connection`、`set_ai_provider_enabled`、`upsert_durable_memory`、`update_current_state`、`resolve_request_context`、`get_context_disclosure_receipt`。

真实发送只能通过既有、严格受控的用户动作路径完成，不得新增隐藏 IPC 或 WebView 直连网络。

### 7. Acceptance Contract

| ID | 验收不变量 | 必须验证／Evidence |
|---|---|---|
| AC-01 | P3-142 高保真 Shell、Settings 页面、三档响应式和 Global AI 空间关系无回退 | source lineage、三档 direct-PID actual-Tauri 截图／AXWindow／WebView |
| AC-02 | Cloud 8／Local 4、主服务、备用服务和高级设置完整保留，Cloud／Local 分离 | Registry snapshot、UI 状态矩阵、provider deletion mutation |
| AC-03 | 恰好 20 IPC，UI 不直连 SQL／Keychain／网络／SDK | exact-list、dependency scan、隐藏 IPC mutation |
| AC-04 | SQLite 只有密文及非敏感 reference；Keychain 密钥材料与 DB 分离 | schema/value 分类、DB byte scan、Keychain item metadata（无秘密） |
| AC-05 | 明文 canary API Key 不出现在 SQLite、WAL/SHM、日志、错误、截图、Evidence、Manifest、导出、进程参数或环境 | review-owned canary leak scan 与可丢弃 mutation |
| AC-06 | UI 只显示掩码和必要尾部识别，不泄露前缀、长度或可逆派生 | 三档截图、DOM／AX text scan、mask mutation |
| AC-07 | 凭据跨 fresh App restart 可用；DB 与 Keychain 缺一不可解密 | 两次 fresh PID restart、DB-only／key-only negative matrix |
| AC-08 | 更新凭据使旧密文／reference／运行期副本失效；删除后调用立即阻断 | update/delete lifecycle、before/after snapshot、zero-network proof |
| AC-09 | ciphertext、nonce、AAD、provider/profile identity、version 或 reference 任一篡改均在网络前失败关闭 | mutation matrix、network counter=0、DB unchanged |
| AC-10 | 保存配置／凭据不触发测试、模型读取、启用或发送 | action counters、network counter、state snapshots |
| AC-11 | 测试连接只能由用户点击触发，并诚实区分认证失败、网络失败、超时、模型不存在、能力不支持 | synthetic negative adapters + bounded real error classification；错误中零秘密 |
| AC-12 | 模型列表只在测试成功后出现；改变 endpoint／Key／模型／高级参数后必须重测 | state machine matrix、restart matrix |
| AC-13 | 未选择并明确启用 DeepSeek 模型前不得发送；禁用后立即阻断 | router decision receipt、positive/negative counters |
| AC-14 | 无后台探测、自动 fallback、代理继承、跨 authority 重定向、未知结果重试或并行 Provider | network harness、redirect/proxy/retry mutation |
| AC-15 | 除 DeepSeek 外所有 Provider 保留但无真实请求；不得把“目录可见”等同“真实验证” | per-provider zero-network ledger、UI truthful state |
| AC-16 | Real Gate 前，合成／loopback 全矩阵、凭据生命周期、泄漏攻击、失败关闭、三档 native Evidence 和 Manifest 全 Pass | Phase-A Final Manifest、verifier、逐行矩阵 |
| AC-17 | 用户在 App 内手工输入 Key 后，只向 `https://api.deepseek.com` 发起用户触发的测试／模型读取和一条固定 canary 请求；不发送任何个人 Context | non-content network receipt：authority、method class、status class、timestamps、byte/token buckets；不得含 Key、prompt、response |
| AC-18 | Real Gate 响应只瞬时呈现；Evidence／日志／DB 不保留正文，发送前 UI 明示 Provider、处理位置和合成范围 | target-window screenshot（无正文／Key）、disclosure receipt、content-taint scan |
| AC-19 | Real Gate 结束先通过 UI 删除凭据，再证明 DB ciphertext/reference、Keychain项和运行期副本失效；最后精确清理唯一临时根 | deletion receipt、post-delete restart deny、marker-gated cleanup、final absence |
| AC-20 | P3-142 和全部历史只读不变，失败尝试保全；Final Manifest 非自指且可独立复算 | before/after hash、history ledger、Manifest verifier |
| AC-21 | 锁屏、AX、截图或暂时网络不可用写 checkpoint 并 `Paused — Resumable`，环境恢复后从 `resume_from` 继续，不全量重做 | checkpoint／resume 演练与候选／合同／基线摘要 |
| AC-22 | 全新隔离独立评审先冻结自有 test design，再接触候选；覆盖凭据泄漏、DB复制、篡改、删除、失败切换、权限漂移和真实单目标 Gate | review-owned tests/mutations、fresh PID/DB/root、独立 Manifest |

Pass 公式：AC-01～AC-22 全部 Pass，P0=0、P1=0、Unknown=0、Not Implemented=0；P2 仅可为不影响安全边界、唯一用户结果和复现性的已披露事实。真实 Provider 成功但任一凭据／内容泄漏或权限绕过仍为 Fail。

### 8. 分阶段执行与停止规则

1. **Phase A — 合成与离线工程 Gate**：实现、静态扫描、凭据 canary、DB／Keychain 分离、严格状态机、失败关闭、三档 actual-Tauri、mutation、Manifest。不得访问真实 DeepSeek。
2. **Phase B — 用户操作的单一 DeepSeek Real Gate**：只有 Phase A 全 Pass 后执行。用户只在 App 内手工输入 Key；Agent 不观察输入。真实 Gate 使用固定合成 canary，不接个人数据。
3. **Phase C — 全新隔离独立评审**：工程 Gate 和 Real Gate 均完成后启动；候选、Evidence 和历史只读，评审使用自己的合成 canary／DB／root，并由用户在实际 App 内重新手工提供所需凭据或完成交互。
4. **Phase D — PM 验收**：PM 只读取非内容 Evidence 并复算 Manifest；L3 PM Pass 后等待用户最终确认。

停止／暂停：

- 锁屏、AXWindow、截图、临时网络不可用、Provider 暂时超时：写 checkpoint，停止 writer/App，状态为 `Paused — Resumable`，不判 Rework、不重做已闭合阶段。
- API Key 未由用户输入：停在 Phase B 用户 Gate，不索取 Key，不降低验收。
- 禁止路径／个人数据实质接触、明文 Key 泄漏、历史覆盖或候选身份不可恢复：立即停止并记录 P0；是否可同任务恢复由 PM 按污染可分离性判断。
- 同合同代码／测试／Evidence／Manifest 缺口全部留在 P3-143 Closure Cycle；只有用户结果、Provider真实目标、权限、存储方案、IPC／Schema关键合同或数据范围变化才新建任务。

### 9. Evidence 与清理

- L3 Evidence：逐行 AC matrix、固定输入／候选 hash、review-owned tests、正负路径、fresh restart、DB／Keychain lifecycle、canary leak scan、网络 authority ledger、mutation、三档原生 Evidence、checkpoint、精确 cleanup、非自指 Final Manifest/verifier。
- Evidence 只允许非内容元数据；不得包含 API Key、prompt、response、模型输出正文、个人数据或可逆派生。
- 唯一临时根 marker 必须是普通文件、0600、精确 task/run identity；根与 runtime direct child 均须 canonical、非 symlink、权限收紧。错误／缺失／symlink marker 必须拒绝删除。
- Keychain 清理由专用 CredentialPort 删除精确 P3-143 item，不得枚举、读取或修改其他项目／用户凭据。

## 输入与最小启动包

必须读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡与 `ABF-P3-143-v1`
- `lifeos/ACCEPTANCE_GOVERNANCE.md` 的 L3、独立评审、Closure Cycle 和可恢复执行条款
- `lifeos/CI_CD_GOVERNANCE.md`
- `lifeos/PM_OPERATING_MODEL.md` 中授权、真实能力和高风险验收章节
- `lifeos/ROLE_MATRIX.md` 中 Stage 3、工程／独立评审角色
- `lifeos/STAGE_GATES.md` 中 AI 权限、真实能力和 Stage 3→4 条款
- `lifeos/architecture/LifeOS架构基线V1.0.md` 的分层、Port／Adapter、Authorization、凭据／网络边界
- `lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md`
- P3-142 任务卡、最终交付物、PM Review、candidate、Evidence／Manifest

不得用相似历史资产替代精确输入；不得全文翻阅无关 Pilot 或真实数据历史。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-143_real_ai_service_and_encrypted_credential_secure_activation.md`
- 候选：`lifeos/engineering/LIFEOS-P3-143/candidate/`
- Evidence：`lifeos/engineering/LIFEOS-P3-143/evidence/`
- Final Manifest：`lifeos/engineering/LIFEOS-P3-143/FINAL_MANIFEST.json`
- PM Review：`lifeos/reviews/LIFEOS-P3-143_pm_review.md`

## PM 验收与交付策略

- P3-143 是单一结果级 L3 任务；实现、测试、真实 Gate、Evidence、包内修正和复跑都留在同一任务，不拆成“Keychain任务”“网络任务”“截图任务”或“Manifest任务”。
- 工程 Gate Pass 后必须由全新隔离会话独立评审；实现会话不得评审自己。
- CI 只运行合成、确定性、无凭据／无真实 Provider的检查；真实 DeepSeek、Keychain 和桌面操作是可恢复人工 Gate。
- L3 不适用低风险自动合并 main。PM Pass 后仍须用户最终确认，之后才决定合并；不 force push，不上传任何敏感／临时资产。
- 本任务 Pass 不关闭 R-0055／R-0056，不冻结设置产品，不恢复 Pilot-6，不进入 Stage 4。

