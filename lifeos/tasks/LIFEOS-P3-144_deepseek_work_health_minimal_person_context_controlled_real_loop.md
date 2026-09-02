# LIFEOS-P3-144｜DeepSeek 驱动的 Work＋Health 最小个人上下文受控真实闭环

## 任务信息

- 任务 ID：LIFEOS-P3-144
- 标题：DeepSeek 驱动的 Work＋Health 最小个人上下文受控真实闭环
- 风险等级：L3
- 优先级／缺陷严重性：P0
- 状态：Ready / Authorized / Engineering Start Pending / ABF-P3-144-v1 Frozen / Not Product Frozen
- 主责 Agent／会话类型：全新 Codex 隔离工程会话；独立评审由未参与实现的全新隔离会话执行
- 所需执行能力：本地文件、Rust/Tauri、SQLite、actual Tauri、受控 HTTPS、原生窗口操作、结构化非内容 Evidence
- 是否需要独立评审：Mandatory
- 独立评审触发理由：真实个人数据、真实 DB、加密凭据、第三方网络、AI 最小披露和 Health 安全边界
- 用户授权依据：用户于 2026-09-02 明确确认 Pilot-7、数据额度、单一 DeepSeek、逐次披露确认、禁止能力、保留策略，并回复“确认并创建、启动 P3-144 完整 Task Contract”。该一次授权覆盖本合同内创建、启动、工程、合成验证、独立评审、用户操作真实 Gate、Evidence、同任务 Closure Cycle 和 PM 验收；L3 最终采纳仍需用户确认。

## 授权与安全语境

LifeOS 是用户本人拥有并授权维护的本地项目。本任务只验证用户主动输入、逐次选择并逐次确认发送的少量低敏感 Work 与非医疗 Health/Fitness Current State。真实内容只能存在于 Pilot-7、实际 App 有界内存以及用户本次明确确认的 DeepSeek 请求中；不得进入工程／评审 Evidence、日志、截图、hash、聊天或测试夹具。

Pilot-7 在 Phase A 合成工程和 Phase B 全新独立评审通过前是禁止路径：任何 Agent、脚本或预检不得对其执行 `exists`、`stat`、枚举、hash、读取、创建、写入或清理。Phase C 只由用户在实际 App 中输入真实内容并逐次确认发送。

## Task Contract

### 1. 唯一用户结果

用户可以在高保真 LifeOS App 中：

1. 手工输入最多 3 条低敏感 Work 短文本和最多 3 条非医疗 Health/Fitness Current State，每条不超过 200 字符；
2. 从 Global AI 发起问题时，由 LifeOS 在本地组装与当前请求相关的最小上下文；
3. 发送前看到本次拟披露的具体条目、类型、数量、DeepSeek 目标和处理位置，可逐条移除；
4. 每次请求都必须再次明确确认，确认后才向单一 DeepSeek 发送；
5. 将返回结果保存为可追溯的 AI Understanding／Suggestion，而不是静默写成用户事实；
6. 对结果执行确认、编辑、拒绝、忽略或纠正，反馈后相关 Understanding／Today 投影按语义更新，关闭重开后保持一致。

### 2. 不得回退的既有基线

1. 继承 P3-142／P3-143 高保真 Shell、模型设置、Cloud 8／Local 4、Cloud／Local 分离、主服务唯一槽位、加密 SQLite 凭据和三档响应式行为。
2. 保持恰好 20 项 IPC；不得新增隐藏 IPC、删除注册项或改变既有 IPC 名称。
3. 继承 P3-138 的模型无关长期 Memory、Durable Memory／Current State／AI Understanding 分离、L1/L2/L3 Context 和最小必要披露原则。
4. 继承 P3-139／P3-140 已进入 P3-143 候选的 Context Resolver、跨域 Today、Evidence／Feedback 和失败关闭语义；当前正式工程输入以已交付 main 的 P3-143 候选及 D-0595～D-0614 为准。
5. 保存配置、保存凭据、测试、模型选择、启用、组装上下文、确认披露、发送和反馈是相互独立的用户动作。

### 3. 允许范围

- 允许修改：
  - `lifeos/engineering/LIFEOS-P3-144/`
  - `lifeos/deliverables/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md`
  - `lifeos/reviews/LIFEOS-P3-144/`
- 允许只读输入：
  - `lifeos/engineering/LIFEOS-P3-143/candidate/`
  - P3-143 Task／ABF／deliverable／PM Review／最终 Independent Review／Manifest
  - P3-138 产品合同与 D-0595～D-0614；若当前提交中缺少独立 P3-138／139／140 文件，不得以未跟踪工作区副本替代正式输入
  - `lifeos/architecture/LifeOS架构基线V1.0.md`
  - `lifeos/product/LIFEOS_MODEL_SETTINGS_BASELINE_V1.md`
- 合成工程唯一临时根：`/private/tmp/lifeos-p3-144-engineering-v1`
- 独立评审唯一临时根：`/private/tmp/lifeos-p3-144-independent-review-v1`
- 真实用户根：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7`
- 真实 DB：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7/capture.sqlite`，进入 Phase C 时必须为全新 DB；不得接管任何既有 DB
- 真实输入额度：Work 最多 3 条；非医疗 Health/Fitness Current State 最多 3 条；每条最多 200 字符；均由用户在 App 内手工输入
- 唯一真实 Provider：DeepSeek；只允许用户明确确认后的请求访问 `https://api.deepseek.com` 精确 HTTPS authority
- 凭据：用户只在 App 内输入；SQLite 保存 AEAD 密文和非敏感 reference，密钥材料由任务专用 OS Credential Store 项隔离；首轮保留加密凭据
- Phase C 完成后保留 Pilot-7、DB 和加密凭据；任何真实资产清理须另行确认

### 4. 禁止范围

- Phase A／B 禁止对 Pilot-7 及其 DB 做任何 access／stat／probe／hash／create／cleanup。
- 禁止真实内容进入 Evidence、日志、错误、截图、Manifest、hash、命令参数、环境变量、聊天或测试夹具；独立评审不得读取真实内容。
- 禁止后台发送、自动 fallback、其他 Provider、代理继承、跨 authority 重定向、静默重试、并行发送、工具调用、Agent 行动、clear、export、同步和外部文件读取。
- 禁止把完整 DB、全部 Memory、全部 Work 或全部 Health 数据发送给模型；未在披露面板中逐项展示且由用户本次确认的内容不得发送。
- 禁止医疗诊断、治疗建议、药物建议、紧急医疗判断或把非医疗 Current State 升级为医疗事实。
- 禁止 AI 输出自动升级为用户事实、Durable Memory、Decision、Action 或确认状态。
- 禁止修改 Frozen Architecture V1.0、核心领域语义、Cloud 8／Local 4、20 IPC 名单、关键 Schema/API 合同、P3-143 候选／历史 Evidence／Review／Manifest。
- 禁止关闭 R-0055／R-0056、冻结产品、恢复旧 Pilot-6、进入 Stage 4 或自动创建后继任务。

### 5. 架构与数据语义

```text
User intent / page context
        ↓
Application / Context Resolver（本地）
        ↓
Always-on Profile + Current Snapshot + task-specific retrieval
        ↓
最小披露预览（可移除）
        ↓ 用户逐次确认
ModelPort → DeepSeek Adapter
        ↓
Derivation / AI Understanding / Suggestion
        ↓
用户确认／编辑／拒绝／忽略／纠正
        ↓
Feedback + Audit + affected projection invalidation
```

- UI 只调用严格 DTO；不得直连 SQL、Credential Store、DeepSeek SDK 或网络。
- Durable Memory、Current State 和 AI Understanding 必须分表意／分类型管理；本任务真实 Health 只进入 Current State。
- Context Resolver 必须先做 Domain、type、validity、recency、authorization 和 scope 的确定性过滤，并执行条数／字符／token budget；首版不要求向量数据库。
- 披露预览必须来源于本次 request-scoped context，展示真实将发送的条目；发送 receipt 记录对象 identity／类型／数量／Provider／model／时间／授权结果，但不记录正文或正文 hash。
- DeepSeek 响应进入 Derivation／AI Understanding 或 Suggestion，保存 provider/model identity、source/evidence refs、时间、状态和用户反馈；不得保存为用户原文。
- 用户纠正后，受影响 Understanding、Snapshot／Today 投影必须失效或重算；历史 lineage 保留，不静默覆盖。

### 6. 恰好 20 项 IPC

保持 P3-143 的完整注册列表：

`capture_record`、`get_today`、`runtime_status`、`confirm_capture_context`、`get_context_recovery`、`get_context_next_action`、`decide_context_next_action`、`record_action_result`、`assemble_global_ai_context`、`get_evidence_backed_understanding`、`decide_understanding_feedback`、`get_ai_provider_settings`、`save_ai_provider_settings`、`save_ai_provider_credential`、`test_ai_provider_connection`、`set_ai_provider_enabled`、`upsert_durable_memory`、`update_current_state`、`resolve_request_context`、`get_context_disclosure_receipt`。

不得新增“send”隐藏 IPC。真实发送必须由既有 `resolve_request_context`／`get_context_disclosure_receipt`／既有 Global AI 用户动作路径和严格状态机完成。若工程证明在不改变关键 IPC／DTO 合同下无法完成，应在修改前停止并回报 PM；不得自行扩展合同。

### 7. Acceptance Contract

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | P3-143 高保真 Shell／Settings／三档 native UI、Cloud 8／Local 4 和恰好 20 IPC 无回退 | lineage、exact-list、direct PID 三档 actual-Tauri | target-only screenshot／AXWindow／WebView、hash |
| AC-02 | Phase A／B 对 Pilot-7 零接触 | 预接触禁止声明、命令审计、root allowlist | structured zero-contact receipt |
| AC-03 | 合成 Work／Health 写入分别落入正确语义；Health 仅为 Current State | schema／domain tests、重启 | before/after、restart matrix |
| AC-04 | 每类最多 3 条、每条最多 200 字符；超额、空值、未知字段和错误类型写前拒绝 | review-owned boundary mutations | DB unchanged、stable errors |
| AC-05 | Context Resolver 只选当前请求相关、有效、已授权的最小条目 | positive／negative retrieval matrix | selected refs／excluded reasons；无真实正文 |
| AC-06 | 过期、被更正、撤销、未确认或跨 Domain 条目不进入请求 | validity／scope mutations | zero-send counter、selection ledger |
| AC-07 | 每次发送前展示本次确切披露集合、Provider、model、处理位置和预算；用户可逐条移除 | actual-Tauri 操作与 DTO 检查 | synthetic disclosure snapshots |
| AC-08 | 每一次发送都要求新的显式确认；旧确认、重启前确认、集合变化后确认均不可复用 | stale/replay/restart mutation | zero-network、stable failure |
| AC-09 | 未确认、取消、移除全部条目、超预算、Provider未启用或凭据缺失时网络计数为0 | state-machine matrix | network harness、DB unchanged |
| AC-10 | 只允许 DeepSeek 精确 authority；无 fallback、后台、代理、重定向、重试、并行或其他 Provider | adapter/network mutations | per-provider ledger、request counter |
| AC-11 | 真实内容零 Evidence／日志／截图／hash；独立评审和 PM 只看非内容 receipt | taint canary 合成攻击；real non-content audit | zero-match scan；不得扫描真实正文 |
| AC-12 | AI 输出明确标为 Derivation／Understanding／Suggestion，带 provider/model 和 evidence refs，不成为用户事实 | repository/state assertions | type/source/lineage snapshots |
| AC-13 | 用户可确认、编辑、拒绝、忽略、纠正；每种结果持久化并可重启复核 | feedback matrix | before/after、fresh restart |
| AC-14 | 纠正／撤销会使受影响 Understanding、Snapshot／Today 投影失效或重算，不改写历史 | dependency mutations | lineage、projection status |
| AC-15 | Health 只作非医疗状态和约束；医疗请求／诊断性输出稳定拒绝或明确转为非医疗安全提示 | safety fixtures/mutations | structured safety result |
| AC-16 | 凭据继续为 SQLite 密文＋分离密钥材料，跨重启可用；Key／DB任一缺失或篡改在网络前失败 | credential lifecycle/mutations | secret-free receipts |
| AC-17 | 合成工程 Gate 完整通过后，才允许全新隔离独立评审 | Phase A matrix／Manifest | non-self-referential Manifest |
| AC-18 | 独立评审先封存自有 test design，再接触候选；复算 lineage 并执行自有 mutation、fresh DB/PID/root | review protocol | independent Manifest／report |
| AC-19 | 只有 Independent Pass 后才允许 Phase C 创建／访问 Pilot-7 | phase gate assertion | signed non-content phase receipt |
| AC-20 | 用户在实际 App 内手工输入不超过授权额度；Agent 不观察、复制或代填 | user-operated Gate | count/type/length-bucket receipt，不含正文/hash |
| AC-21 | 每次真实请求均先显示并由用户确认最小披露，只向 DeepSeek 发送；无其他网络 | target authority／user-action counters | non-content network/disclosure receipt |
| AC-22 | Pilot-7／DB／加密凭据关闭重开后保持；本轮不执行 clear／cleanup | fresh PID restart | count/type/status receipt；零正文 |
| AC-23 | P3-143 及历史只读，失败尝试保全，Manifest 可独立复算 | before/after hash、history ledger | verifier result |
| AC-24 | 锁屏、AX、截图或临时网络问题按 checkpoint 暂停并定向恢复 | pause/resume演练 | checkpoint.json、excluded artifacts |

Pass 公式：AC-01～AC-24 全部 Pass；P0=0、P1=0、Unknown=0、Not Implemented=0。P2 仅允许不影响真实内容边界、凭据、授权、用户结果、Evidence 可信度、数据生命周期和可复现性的已披露事实。

### 8. 分阶段执行与停止规则

1. **Phase A — 合成／离线工程 Gate**：只在工程根和合成临时根实现、测试、mutation、actual-Tauri、Evidence／Manifest。Pilot-7、DeepSeek真实网络和真实凭据零接触。
2. **Phase B — 全新隔离独立评审**：评审先冻结自有 test design 和禁止路径声明，再只读候选；使用全新合成 DB/root/PID，完成自有反例和三档 native Evidence。不得访问 Pilot-7、真实网络或真实凭据。
3. **Phase C — 用户操作真实 Gate**：仅在 Phase B Pass 后进入。用户在 App 内创建／使用 Pilot-7、输入真实短文本和凭据、逐次确认最小披露并发送。Agent 不读取屏幕中的真实正文，不截图正文，不采集正文 hash；仅产生非内容 receipt。
4. **Phase D — 非内容终局复核与 PM 验收**：独立评审只读核对 Phase C 非内容 receipt、候选 lineage、网络 authority、计数与重启状态，不读取真实内容、不重放真实请求。PM 按 ABF 裁决；L3 Pass 后等待用户最终采纳。
5. 任一真实内容越界、禁止目标访问、后台发送、其他 Provider 请求、明文凭据泄漏或只读历史修改，立即停止并记录 `Irrecoverable Invalidation`，由 PM 判断受污染阶段；不得淡化为普通 Evidence Gap。
6. 锁屏、AXWindow、截图、用户暂未操作或 Provider 暂时不可用，写 checkpoint 并记 `Paused — Resumable`／`Blocked`，不得重做未受影响阶段。

### 9. Evidence 等级

- 本任务采用 L3：逐行 ABF 矩阵、runner、before/after、hash、review-owned mutation、candidate/history 保全、非自指 Manifest、精确临时根清理和独立评审。
- 合成 Evidence 可包含固定非敏感 canary；真实 Evidence 只允许 count、type、length bucket、object ID、authority、model ID、status class、时间、授权结果和 lineage ref，不得包含正文或正文 hash。
- 工程／独立临时根须 0700，marker 为普通 0600 文件且内容精确匹配；错误／缺失／symlink marker 必须拒绝清理。Phase A／B 结束后精确清理各自唯一临时根。
- Pilot-7、真实 DB 和加密凭据首轮保留，不属于临时清理范围。

### 10. 新任务触发器

仅当需要改变 Provider、真实目录／数据类型／额度、医疗边界、凭据方案、网络目标、权限、架构、20 IPC／Schema关键合同、产品语义或 ABF，或历史污染无法可信恢复时新建任务。同范围代码、测试、Evidence、Manifest、UI文案和失败关闭缺口留在 P3-144 Closure Cycle。

### 11. CI / 可恢复执行

- CI 检查清单：合成离线单元／合同测试、20 IPC exact-list、Provider／authority静态守卫、Context／budget／feedback／Health safety mutation、baseline lineage、JSON／Manifest verifier、凭据 canary 零泄漏；CI 禁止 Pilot-7、真实凭据、真实 DeepSeek 和 GUI 用户操作。
- 人工／环境 Gate：direct-PID actual Tauri 三档、AXWindow／WebView、用户逐次披露确认、DeepSeek 真实发送、fresh restart。
- 检查点路径：`lifeos/engineering/LIFEOS-P3-144/evidence/checkpoint.json`；独立评审使用其自身目录下 `checkpoint.json`。
- 可恢复执行阶段：`preflight / build_test / data_lifecycle / app_launch / native_window_binding / visual_capture / cleanup / manifest / independent_review / real_user_gate / final_review`。
- 环境暂停时的 `resume_from` 规则：合同、候选、基线和已完成 Evidence hash 不变、禁止边界零接触且 App/writer/DB 状态安全时，从最早受影响阶段继续；不机械重跑已通过阶段。
- 候选或合同变化后的最早受影响阶段：代码／DTO／Schema变化从 `build_test`；数据语义变化从 `data_lifecycle`；UI-only变化从 `app_launch`；截图问题从 `visual_capture`；Evidence／Manifest-only变化从对应阶段；ABF实质变化关闭任务并新建。
- 只有禁止路径／真实内容／错误Provider／未确认网络／凭据泄漏接触、只读候选或历史被修改、或正 Evidence 无法与污染分离，才触发 `Irrecoverable Invalidation`。

## 输入与最小启动包

必须读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/tasks/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop_acceptance_basis_freeze.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

定向补读：

- `lifeos/ACCEPTANCE_GOVERNANCE.md`、`lifeos/CI_CD_GOVERNANCE.md`
- `lifeos/PM_OPERATING_MODEL.md` 独立评审、L3、Closure Cycle、可恢复执行相关章节
- `lifeos/ROLE_MATRIX.md` PM／工程／独立评审边界
- `lifeos/STAGE_GATES.md` Stage 3→4 与 AI 权限关卡相关章节
- `lifeos/architecture/LifeOS架构基线V1.0.md`
- P3-143 Task／ABF／PM Review 与 candidate；历史全部只读

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-144_deepseek_work_health_minimal_person_context_controlled_real_loop.md`
- 工程 Evidence：`lifeos/engineering/LIFEOS-P3-144/`
- 独立评审：`lifeos/reviews/LIFEOS-P3-144/independent-review/`
- 真实 Gate 非内容 receipt：`lifeos/reviews/LIFEOS-P3-144/real-use/real-use-receipt.json`
- PM Review：`lifeos/reviews/LIFEOS-P3-144_pm_review.md`
- 聊天回复：结论、测试／Evidence摘要、P0/P1/P2/Unknown/Not Implemented、资产／风险／Stage状态、路径和真正新增的用户决策。

## PM 验收

- PM 只按长期质量原则与 ABF-P3-144-v1 验收，不在提交后移动终点。
- 工程 Agent 不得独立评审自己的结果；独立评审只读且不得修复候选。
- L3 PM Pass 后仍等待用户最终采纳；不得自动合并 main、关闭 R-0055／R-0056、冻结产品或进入 Stage 4。
