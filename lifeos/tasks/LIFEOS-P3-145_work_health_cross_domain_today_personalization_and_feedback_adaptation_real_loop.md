# LIFEOS-P3-145｜Work＋Health 跨域 Today 个性化与反馈适应真实闭环

## 任务信息

- 任务 ID：LIFEOS-P3-145
- 标题：Work＋Health 跨域 Today 个性化与反馈适应真实闭环
- 风险等级：L3
- 优先级／缺陷严重性：P0
- 状态：Draft / Awaiting Single Real-Boundary Confirmation / ABF-P3-145-v1 Draft / Not Product Frozen
- 主责 Agent／会话类型：全新 Codex 隔离工程会话；一次全新隔离独立评审由未参与实现的会话执行
- 所需执行能力：本地文件、Rust/Tauri、SQLite、actual Tauri、受控 DeepSeek HTTPS、原生窗口操作、非内容 Evidence
- 是否需要独立评审：Mandatory（一次，位于真实 Gate 前）
- 独立评审触发理由：复用真实个人 DB、增加真实 Health Current State／Durable Memory、向第三方披露跨域最小 Context
- 当前授权依据：用户已授权 P3-144 合并 main，并授权创建、启动 P3-145 完整 Task Contract。由于下列 Pilot-7 复用、真实数据额度和网络次数在授权前尚未完整展示，本卡先创建为 Draft；用户一次确认本完整合同后立即转 Ready 并启动，不再拆分确认。

## 授权与安全语境

LifeOS 是用户本人拥有并授权维护的本地项目。本任务只验证一个真实结果：LifeOS 能在不扩大披露的前提下，把用户已确认的长期信息、当天 Work 与非医疗 Health/Fitness 状态综合为一个 Today 重点，并让用户反馈对后续理解或建议产生可解释变化。

真实正文只存在于 Pilot-7、App 的有界内存以及用户逐次确认的 DeepSeek 请求中。Agent、测试、Evidence、日志、截图、hash、命令、环境变量和聊天均不得读取或记录真实正文。

## Task Contract

### 1. 唯一用户结果

用户在现有高保真 LifeOS App 中复用 P3-144 已保留的数据和 DeepSeek 服务：

1. 保留既有 Work 记录，不重新录入；
2. 手工增加 1～3 条非医疗 Health/Fitness Current State，并确认 1 条低敏感长期偏好或约束为 Durable Memory；
3. Today 依据 Person 整体优先级只给出最多一个 Focus，可明确显示“当前没有特别需要处理的事情”；
4. 用户从 Global AI 发起一次跨域问题，发送前看到确切最小披露条目、类型、DeepSeek目标与预算，并可移除；
5. 用户逐次确认后才发送，AI结果保留为可追溯 Understanding／Suggestion；
6. 用户给出一次确认、编辑、拒绝、忽略或纠正反馈后，刷新或第二次请求能够看到 Today／Understanding／Suggestion 的可解释变化；
7. 关闭重开后，数据、披露审计、反馈及最新有效投影保持一致。

### 2. Baseline lineage matrix（不得回退）

| 基线 | P3-145 强制继承 | 回归证明 |
|---|---|---|
| P3-142／143 Settings | Cloud 8／Local 4、Cloud／Local分离、主服务槽位、加密凭据、保存／测试／选择／启用分离 | exact registry、credential lifecycle、三档 actual-Tauri |
| P3-144 Shell／交互 | icon-only Rail、高保真页面、Global AI、披露预览、回答区、终态反馈可见 | DOM/CSS hash lineage、用户可见语义测试 |
| P3-144 Runtime | 恰好20 IPC、`capture.sqlite`、普通文件0600、单次反馈消费、重启恢复 | exact IPC、DB类型／权限、restart tests |
| P3-138语义（D-0595～D-0600） | Durable Memory／Current State／AI Understanding分离，模型不是记忆库，最小Context | type／lineage／resolver mutations |
| P3-139／140语义（D-0601～D-0614） | 本地Context Resolver、预算、跨域Today、Evidence与反馈适应 | deterministic selection、Today/feedback tests |
| P3-144安全边界 | 仅DeepSeek、逐次确认、无后台／fallback、正文零Evidence、Health非医疗 | network ledger、taint mutations、safety matrix |

任何删除、隐藏、改名、弱化或替代上述行为均为 P0 回退；不得以“本轮未修改”为由放行。

### 3. 允许范围

- 允许修改：
  - `lifeos/engineering/LIFEOS-P3-145/`
  - `lifeos/deliverables/LIFEOS-P3-145_work_health_cross_domain_today_personalization_and_feedback_adaptation_real_loop.md`
  - `lifeos/reviews/LIFEOS-P3-145/`
- 严格只读输入：
  - `lifeos/engineering/LIFEOS-P3-144/candidate/`
  - P3-144 Task／ABF／deliverable／Review／Evidence／Manifest
  - `lifeos/architecture/LifeOS架构基线V1.0.md`
  - `lifeos/architecture/LifeOS高保真原型IA-V1.0.md`
  - D-0595～D-0614、D-0645～D-0647
- 工程唯一临时根：`/private/tmp/lifeos-p3-145-engineering-v1`
- 独立评审唯一临时根：`/private/tmp/lifeos-p3-145-independent-review-v1`
- 真实用户根：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7`
- 真实 DB：复用现有 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7/capture.sqlite`；不得创建第二个活动 DB、不得清空、覆盖、替换或降级现有数据
- 真实新增额度：Health/Fitness Current State 1～3条；Durable Memory 1条；每条不超过200字符，均由用户在App内手工输入
- 既有 Work：只由 App 按用户当前请求选择；Agent 不读取正文，不要求重新输入
- 真实 Provider：仅已启用的 DeepSeek，精确 authority `https://api.deepseek.com`
- 真实网络额度：最多2次由用户逐次确认的请求；无确认则0次
- 凭据：复用已加密保存的 DeepSeek 凭据；不得读取、导出、记录、迁移或要求用户在聊天中提供
- 资产策略：任务结束继续保留 Pilot-7、`capture.sqlite`、占位历史文件和加密凭据；任何清理另行确认

### 4. 禁止范围

- Phase A／B 禁止对 Pilot-7及其DB、凭据做任何 access／stat／probe／hash／create／cleanup。
- 禁止真实正文进入 Evidence、日志、错误、截图、Manifest、hash、命令参数、环境变量或聊天；禁止扫描真实正文来证明“不泄漏”。
- 禁止后台发送、自动fallback、其他Provider、代理继承、跨authority重定向、静默重试、并行发送、工具调用、Agent行动、clear、export、同步和外部文件读取。
- 禁止把完整DB、全部Memory、全部Work或全部Health发送给模型；未在本次披露预览逐项展示并确认的内容不得发送。
- 禁止医疗诊断、治疗／药物／紧急医疗建议；高风险Health输入必须在网络前保守停止。
- 禁止AI输出自动升级为用户事实、Durable Memory、Decision、Action或确认状态。
- 禁止修改Frozen Architecture V1.0、产品IA、Cloud 8／Local 4、20 IPC名单、关键Schema/API、P3-144候选和历史。
- 禁止关闭R-0055／R-0056、冻结产品、恢复Pilot-6、进入Stage 4、自动合并main或自动创建后继任务。

### 5. 架构与数据语义

```text
User intent
  → local Person Profile + incremental Current Snapshot
  → task-specific Context Resolver
  → one request-scoped minimal disclosure preview
  → user confirmation
  → ModelPort → DeepSeek Adapter
  → AI Understanding / Suggestion
  → user feedback
  → affected snapshot / Today / understanding invalidation or recompute
```

- UI只能调用Application DTO，不直连SQL、Credential Store或网络。
- Durable Memory是用户确认且长期有效的信息；Current State是短时状态；AI Understanding必须保持推断身份、来源、provider/model、validity和可纠正性。
- Context Resolver先按Domain、type、validity、recency、authorization和scope确定性过滤，再执行条数／字符／token预算；不得全库发送。
- Today按Person整体优先级产生最多一个Focus，不按Domain配额填卡；证据不足时允许空状态。
- 反馈只改变受影响投影；历史Evidence和原始记录不被静默覆盖。

### 6. IPC 与关键合同

- 保持 P3-144 恰好20项IPC及名称不变。
- P3-145优先复用既有 `upsert_durable_memory`、`update_current_state`、`resolve_request_context`、`get_today`、`decide_understanding_feedback` 与披露收据能力。
- 不新增隐藏发送IPC；若不改变关键IPC／DTO／Schema合同就无法完成，必须在修改前停止并回报PM，不能自行扩展。

### 7. Acceptance Contract

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | baseline lineage matrix全部继承，无UI／Provider／IPC／DB安全回退 | hash／语义回归／三档actual-Tauri | lineage matrix、target-only截图／AX |
| AC-02 | Phase A／B对Pilot-7、真实DB和凭据零接触 | 预接触封存、allowlist、命令审计 | zero-contact receipt |
| AC-03 | 复用DB前后既有P3-144对象计数／状态不丢失，DB保持普通文件0600 | 非内容before/after、restart | count/state/mode receipt |
| AC-04 | 新增1～3条Health Current State与1条Durable Memory，均≤200字符且类型分离 | 合成边界mutation；用户非内容计数 | DB unchanged on reject |
| AC-05 | AI Understanding保持推断身份，不自动升级为Memory或用户事实 | state/type assertions | lineage snapshots |
| AC-06 | Snapshot增量更新；过期、撤回、被纠正或未授权内容不进入当前投影 | lifecycle mutations | affected-slice before/after |
| AC-07 | Today按Person整体优先级最多一个Focus，允许合法空状态，不按Domain配额 | cross-domain fixtures | Today decision reasons |
| AC-08 | Work与Health共同影响结果时，实际使用refs可审计；不需要某域时不得强行披露 | positive/negative resolver matrix | selected refs/excluded reasons |
| AC-09 | 披露预览逐项显示真实将发送对象、类型、DeepSeek目标、模型、位置和预算，并允许移除 | actual-Tauri与DTO测试 | synthetic disclosure snapshots |
| AC-10 | 每次请求需要新确认；集合变化、取消、重启、旧确认或空集合均零网络 | replay/restart mutations | network counter、DB unchanged |
| AC-11 | 最多2次请求且只到DeepSeek精确authority；无后台、fallback、其他Provider、重定向或重试 | network harness／ledger | per-target non-content receipt |
| AC-12 | 响应保存为Understanding／Suggestion，带source refs、provider/model、时间与状态 | persistence/restart | typed metadata receipt |
| AC-13 | 一次用户反馈使后续Today／Understanding／Suggestion产生可解释变化；无关投影不变 | feedback dependency mutations | before/after reasons |
| AC-14 | 纠正／撤回保留历史并使受影响投影失效或重算；反馈不可重复消费 | mutation／restart | lineage与stable errors |
| AC-15 | 医疗或高风险Health语义在网络前保守停止，且无部分写入 | safety mutations | zero-network／DB unchanged |
| AC-16 | 凭据继续密文＋分离密钥；缺失／篡改／删除在网络前失败 | credential lifecycle | secret-free receipt |
| AC-17 | 真实正文零Evidence／日志／截图／hash，Agent不读取正文 | 合成canary攻击＋流程审计 | zero-match synthetic scan |
| AC-18 | 关闭重开后Memory／State／Understanding／Feedback／Today与披露审计一致 | fresh PID restart | non-content state counts |
| AC-19 | 一次全新隔离独立评审在Phase C前完成；不重复评审未变化候选 | review-owned mutations／Manifest | independent report／Manifest |
| AC-20 | 历史只读、临时根marker-gated精确清理、环境问题可从checkpoint恢复 | hash／cleanup mutations | checkpoint、cleanup receipt |

Pass公式：AC-01～AC-20全部Pass；P0=0、P1=0、Unknown=0、Not Implemented=0。P2只能是已披露、可分离且不影响真实内容、凭据、网络授权、用户结果、数据生命周期或Evidence可信度的事实。

### 8. 分阶段执行

1. **Phase A 合成工程 Gate**：只在P3-145工程根和工程临时根实现、测试、mutation、actual-Tauri、Evidence与Manifest；真实根、真实DB、真实凭据、真实网络零接触。
2. **Phase B 一次全新隔离独立评审**：先封存review-owned test design／allowlist／禁止声明，再只读候选；使用全新合成DB/root/PID验证AC-01～20适用行。仅当候选或安全合同实质变化才需要新的独立复评。
3. **Phase C 用户操作真实 Gate**：Phase B Pass且用户已确认本完整合同后，用户在App内操作Pilot-7；Agent不观察或代填正文。最多新增授权数据并完成最多2次逐次确认的DeepSeek请求和一次反馈。
4. **Phase D 非内容PM终局验收**：只核对计数、类型、状态、authority、时间、refs、权限和重启，不读取正文、不重放网络。L3 PM Pass后等待用户最终采纳。

### 9. Evidence 等级

- L3：逐行矩阵、review-owned mutation、before/after、candidate/history hash、非自指Manifest、精确清理和一次独立评审。
- 合成Evidence可用固定非敏感canary；真实Evidence只允许count、type、length bucket、opaque object ID、authority、model ID、status、time、authorization和lineage refs。
- 工程／评审临时根0700，marker为普通0600文件；错误／缺失／symlink marker拒绝清理。Pilot-7不属于清理范围。

### 10. 新任务触发器

只有Provider、真实根、数据类型／额度、医疗边界、凭据、网络目标、权限、架构、关键IPC／Schema/API、核心产品语义或ABF需要变化，或正Evidence与污染无法分离时才新建任务。同范围代码、测试、UI文案、Evidence、Manifest和失败关闭修正留在P3-145 Closure Cycle。

### 11. CI／可恢复执行

- CI 检查清单：合成离线测试、20 IPC exact-list、baseline lineage、Memory／State／Understanding类型、resolver预算、跨域Today、feedback dependency、Health safety、authority、credential canary与Manifest verifier；禁止真实数据／DB／凭据／Provider／GUI操作。
- 人工Gate：direct-PID actual-Tauri三档、AXWindow／WebView、用户披露确认、真实DeepSeek、restart。
- Checkpoint：`lifeos/engineering/LIFEOS-P3-145/evidence/checkpoint.json`；评审在自有目录保存checkpoint。
- 阶段：`preflight / build_test / data_lifecycle / app_launch / native_window_binding / visual_capture / cleanup / manifest / independent_review / real_user_gate / final_review`。
- 环境暂停：合同、候选、基线摘要和已完成Evidence hash不变且禁止边界零接触时，从`resume_from`继续；锁屏／AX／截图／临时网络问题不得判Rework。
- 最早受影响阶段：代码／DTO从`build_test`；数据语义从`data_lifecycle`；UI-only从`app_launch`；截图从`visual_capture`；Evidence-only从相应阶段；ABF实质变化则关闭并新建。
- Irrecoverable Invalidation仅限：禁止真实路径／正文／凭据／目标接触、未确认网络、只读资产修改或正Evidence无法与污染分离。

## 输入与最小启动包

必须读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/tasks/LIFEOS-P3-145_work_health_cross_domain_today_personalization_and_feedback_adaptation_real_loop_acceptance_basis_freeze.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`

定向补读：

- `lifeos/ACCEPTANCE_GOVERNANCE.md`、`lifeos/CI_CD_GOVERNANCE.md`
- `lifeos/PM_OPERATING_MODEL.md`中L3、独立评审、Closure Cycle与可恢复执行章节
- `lifeos/ROLE_MATRIX.md`中PM／工程／独立评审边界
- `lifeos/STAGE_GATES.md`中Stage 3→4与AI权限关卡
- Frozen `lifeos/architecture/LifeOS架构基线V1.0.md`
- `lifeos/architecture/LifeOS高保真原型IA-V1.0.md`
- P3-144 Task／ABF／candidate／Review／Evidence／Manifest（只读）

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-145_work_health_cross_domain_today_personalization_and_feedback_adaptation_real_loop.md`
- 工程／Evidence：`lifeos/engineering/LIFEOS-P3-145/`
- 独立评审：`lifeos/reviews/LIFEOS-P3-145/independent-review/`
- 真实Gate非内容收据：`lifeos/reviews/LIFEOS-P3-145/real-use/real-use-receipt.json`
- PM Review：`lifeos/reviews/LIFEOS-P3-145_pm_review.md`

## 一次性授权方式

用户确认本卡完整边界后，创建、启动、实现、测试、动态Evidence、一次独立评审、Phase C用户操作、同任务Closure Cycle和PM验收均获授权，不再重复确认。L3最终采纳、资产清理、风险关闭、产品冻结、main合并与Stage切换仍不包含在内。

## PM 验收

PM只按长期质量原则与Frozen ABF-P3-145-v1验收，不移动终点。执行Agent不独立评审自己的结果；独立评审只读且不修复候选。P3-145 PM Pass后等待用户最终采纳，不自动关闭风险、冻结产品、合并main或进入Stage 4。
