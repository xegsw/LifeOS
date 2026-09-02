# LIFEOS-P3-144 Acceptance Basis Freeze

## 冻结信息

- 任务 ID：LIFEOS-P3-144
- ABF ID／版本：ABF-P3-144-v1
- 生效决策：D-0645
- 冻结时间：2026-09-02（Asia/Shanghai）
- ABF 文件 SHA-256：由非自指 Freeze Manifest 记录
- 状态：Frozen / Authorized
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 要完成的单一结果：在 Pilot-7 中以单一 DeepSeek 完成 Work＋非医疗 Health/Fitness Current State 的本地最小上下文组装、逐次可见披露确认、真实回答、AI派生区分、反馈和重启闭环。
- 明确不冻结的产品需求：产品实现、Schema/API、工程基线、其他 Provider、医疗能力、导出／同步／工具调用、风险关闭和 Stage 4。
- 明确非范围：后台发送、自动 fallback、其他 Provider、clear、export、同步、工具调用、医疗诊断、真实内容 Evidence。

## 授权和能力边界

- 允许目录：任务卡列出的 P3-144 engineering/deliverable/review、两个固定 `/private/tmp` 根，以及仅在 Phase C 允许的 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-7`。
- 允许数据与夹具：Phase A/B 固定非敏感合成夹具；Phase C 用户手工最多 3 条 Work＋3 条非医疗 Health/Fitness Current State，每条 ≤200 字符。
- 允许入口／接口：P3-143 高保真 Tauri App 与恰好 20 IPC。
- 允许工具／环境：离线构建测试、actual Tauri、SQLite、任务专用 Credential Store、Phase C 用户触发的 DeepSeek 精确 HTTPS authority。
- 严格只读资产：P3-143 candidate、Task／ABF／deliverable／Review／Evidence／Manifest；Frozen Architecture V1.0；模型设置基线；正式提交中存在的 P3-138相关资产和账本决策。
- 禁止能力与外部目标：其他 Provider／域名、后台网络、fallback、代理／跨authority redirect、clear/export/sync/tool use、真实内容 Evidence、医疗能力。
- 投递前额外用户确认：已完成。用户的完整确认覆盖本 ABF；Phase C 仅需要用户在 App 内逐次确认具体披露，不需要重复治理授权。L3 最终采纳仍待任务完成后确认。

## 引用的长期质量原则

- L1-1 数据主权：Phase A/B Pilot-7 零接触；Phase C 只处理用户逐次确认的最小内容。
- L1-2 内容身份：Work原文、Current State、AI Understanding／Suggestion和确认事实严格区分。
- L1-3 生命周期完整：捕获、筛选、披露、发送、派生、反馈、纠正、重启一致。
- L1-4 失败关闭：未确认、超额、过期、无凭据、错误Provider／authority或篡改均在网络／写入前停止。
- L1-5 用户控制：每次发送均重新展示并确认；AI不替用户确认事实或行动。
- L1-6／7 审计与Evidence诚实：审计只保留非内容 refs／计数／状态；真实正文和hash均不进入Evidence。
- L1-8／9 历史与授权：P3-143历史只读，重跑不扩大授权。
- L1-10 可复核：合成矩阵、review-owned mutations、Manifest和重启行为可复算。
- L1-11／12 已确认能力不回退、用户原始确认优先：高保真UI、Cloud8／Local4、加密凭据和20 IPC完整继承。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | Pilot-7阶段隔离 | P0 | Phase A/B零access；Phase C前置Independent Pass | Irrecoverable Invalidation／Closure |
| ABF-I-02 | 真实输入额度与类型 | P0 | Work≤3、Health State≤3、每条≤200；Health非医疗 | Closure |
| ABF-I-03 | 本地最小Context | P0 | 仅相关、有效、授权、预算内条目入包 | Closure |
| ABF-I-04 | 逐次可见确认 | P0 | 每次展示确切集合且确认不可重放 | Closure |
| ABF-I-05 | 单一DeepSeek目标 | P0 | 只有确认后向精确authority发送 | Closure／Irrecoverable Invalidation |
| ABF-I-06 | 零隐式能力 | P0 | 无后台、fallback、其他Provider、clear/export/sync/tool use | Closure／Irrecoverable Invalidation |
| ABF-I-07 | 真实内容零Evidence | P0 | 日志／截图／hash／Evidence／Manifest零正文 | Irrecoverable Invalidation |
| ABF-I-08 | AI身份与追溯 | P0 | 输出为Derivation／Understanding／Suggestion且带refs/provider/model | Closure |
| ABF-I-09 | 用户反馈控制 | P0 | confirm/edit/reject/ignore/correct完整且可重启 | Closure |
| ABF-I-10 | Health安全 | P0 | 仅非医疗Current State；医疗语义失败关闭／安全提示 | Closure |
| ABF-I-11 | 凭据安全 | P0 | SQLite密文＋分离密钥；缺失／篡改网络前拒绝 | Closure／Irrecoverable Invalidation |
| ABF-I-12 | UI／架构／20 IPC防回退 | P0 | P3-143 lineage、Cloud8/Local4、三档UI和exact20一致 | Closure |
| ABF-I-13 | 可恢复执行 | P1 | 环境中断checkpoint后定向resume | Paused — Resumable |
| ABF-I-14 | 独立性与历史保全 | P0 | reviewer先封存设计、candidate/history只读、Manifest可复算 | Closure／Invalidated Attempt |
| ABF-I-15 | 保留策略 | P0 | Phase A/B临时根精确清理；Pilot-7/DB/凭据不清理 | Closure |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | baseline | fixed P3-143 | 复算UI/provider/IPC/source | lineage一致 | 历史只读 | T-LINEAGE | hashes/exact-list |
| ABF-M-002 | preflight | Phase A/B | 检查禁止声明与allowlist | 不探测Pilot-7 | Pilot-7零接触 | T-ZERO-CONTACT | command audit |
| ABF-M-003 | capture Work | empty synthetic DB | 1～3条合法输入 | 原文身份正确持久化 | Health不变 | T-WORK | lifecycle JSON |
| ABF-M-004 | Health State | same | 1～3条非医疗状态 | Current State持久化 | Durable Memory不变 | T-HEALTH | lifecycle JSON |
| ABF-M-005 | boundary | same | 4th／>200／空／unknown field | 写前拒绝 | DB不变 | T-LIMIT | negative matrix |
| ABF-M-006 | resolver | mixed fixture | Work请求 | 只选相关最小refs | Health非相关项排除 | T-RESOLVE-W | selection receipt |
| ABF-M-007 | resolver | mixed fixture | Health请求 | 只选相关最小refs | Work非相关项排除 | T-RESOLVE-H | selection receipt |
| ABF-M-008 | validity | expired/corrected/revoked | resolve | 排除失效条目 | DB不写 | T-VALIDITY | exclusion ledger |
| ABF-M-009 | budget | over count/token | resolve | 稳定拒绝或有界裁切且可解释 | network=0 | T-BUDGET | budget result |
| ABF-M-010 | disclosure | assembled request | 打开预览／移除项 | UI与实际packet refs一致 | 未发送 | T-DISCLOSE | synthetic target screenshot |
| ABF-M-011 | confirmation | disclosed request | cancel／no confirm | 不发送 | DB不变 | T-CONFIRM-NEG | counters |
| ABF-M-012 | replay | old confirmation | restart／set changed | 旧确认失效 | network=0 | T-REPLAY | structured failure |
| ABF-M-013 | provider guard | other profiles present | 路由／fallback攻击 | 仅DeepSeek可选且无发送 | other counters=0 | T-PROVIDER | ledger |
| ABF-M-014 | authority guard | redirect/proxy/bad URL | request | 网络前或首跳后安全拒绝 | 无额外目标 | T-AUTHORITY | harness |
| ABF-M-015 | credential | encrypted fixture | restart／missing／tamper | 正常跨重启；反例网络前拒绝 | 零秘密Evidence | T-CREDENTIAL | receipts |
| ABF-M-016 | AI result | synthetic response | persist | Derivation/Understanding/Suggestion | user facts不变 | T-DERIVATION | state snapshot |
| ABF-M-017 | feedback | persisted result | 5种用户动作 | 状态正确且可重启 | history lineage保留 | T-FEEDBACK | matrix |
| ABF-M-018 | correction | dependency graph | correct/revoke | affected projections失效／重算 | 原始Evidence不改 | T-INVALIDATE | lineage |
| ABF-M-019 | medical guard | diagnosis/treatment fixtures | ask/process | 拒绝或非医疗安全提示 | 无医疗事实写入 | T-HEALTH-SAFE | safety matrix |
| ABF-M-020 | native desktop | fresh PID | full flow synthetic | 控件完整可达 | 无目标外截图 | T-DESKTOP | PID→AX→WebView |
| ABF-M-021 | native compact | fresh PID | same | 无截断 | same | T-COMPACT | native Evidence |
| ABF-M-022 | native narrow | fresh PID | same | 无横溢 | same | T-NARROW | native Evidence |
| ABF-M-023 | Phase A Gate | all engineering rows | verify Manifest | Pass才可评审 | Pilot/real network零接触 | T-PHASE-A | engineering Manifest |
| ABF-M-024 | independent | sealed design | review-owned mutations | 独立Pass | candidate/history只读 | T-INDEPENDENT | review Manifest |
| ABF-M-025 | real setup | Independent Pass | 用户创建Pilot/DB并输入额度内内容 | 只记录非内容计数 | 正文零Evidence | U-REAL-INPUT | non-content receipt |
| ABF-M-026 | real disclosure | request ready | 用户查看、移除、确认 | packet与确认一致 | 未选内容不发送 | U-REAL-DISCLOSE | refs/count receipt |
| ABF-M-027 | real DeepSeek | fresh confirmation | user sends | 单一authority单次请求 | 无fallback/background | U-REAL-SEND | non-content network receipt |
| ABF-M-028 | real feedback | response visible | user feedback | AI身份／lineage正确 | 不静默升级事实 | U-REAL-FEEDBACK | status-only receipt |
| ABF-M-029 | real restart | Pilot retained | close/reopen | DB/credential/state一致 | 无后台发送 | U-REAL-RESTART | count/status receipt |
| ABF-M-030 | final retention | end of run | cleanup check | synthetic roots absent；Pilot retained | 不清理真实资产 | T-RETENTION | absence/retained receipt |
| ABF-M-031 | pause/resume | environment issue | checkpoint/resume | 只重跑受影响阶段 | completed hashes一致 | T-RESUME | checkpoint |
| ABF-M-032 | final lineage | all phases | recompute | non-self-referential Manifest Pass | history unchanged | T-FINAL | verifier |

## Evidence 合同

- runner／测试源码：工程与独立评审各自拥有；评审不得只复用候选 verifier。
- 逐行结果：ABF-M-001～032逐行记录状态、时间、候选identity、断言和Evidence refs。
- before／after：合成DB、真实非内容计数、Provider/credential状态、network counters、projection lineage、temp roots。
- 真实内容保护：不得读取真实正文来做 leak scan；用合成 canary 证明实现机制，用非内容 receipt 证明真实 Gate。
- source／history hash：固定P3-143 candidate与正式只读输入；评审复算Git blob／Manifest。
- Manifest：非自指、分 candidate/fixed/history/evidence，配独立 verifier。
- 临时清理：先停PID/writer，再验证精确普通marker；错误／缺失／symlink marker拒绝。Pilot-7、DB、加密凭据首轮保留。

## 计数与 Pass 公式

- P0／P1／P2／Unknown／Not Implemented：逐项诚实报告。
- Pass：ABF-I-01～15和ABF-M-001～032全部Pass；P0=0、P1=0、Unknown=0、Not Implemented=0。
- 允许的P2：仅不影响真实内容、Health安全、授权、凭据、网络目标、生命周期、Evidence可信度和用户结果的已披露事实。
- 合同外N/A：其他Provider真实能力、医疗、图片／语音、clear/export/sync/tool use、风险关闭、产品冻结、Stage4。

## Closure Cycle 与退出规则

- 首次PM不通过一次列明全部合同内缺口；同语义代码、测试、Evidence、Manifest和文案留在P3-144 Closure Cycle，无需重复授权。
- 必须新建任务：Provider／目录／数据类型／额度／医疗／权限／凭据／网络／架构／20 IPC／Schema关键合同或本ABF实质改变，或历史污染无法可信恢复。
- Blocked：用户尚未完成App内操作、DeepSeek外部不可用或系统Credential Store长期不可用；保留checkpoint，不降低验收。
- 环境锁屏、AX或截图不可用：Paused — Resumable，不判Rework。

## 候选基线与只读保全

- 候选输入：P3-143已交付main的`lifeos/engineering/LIFEOS-P3-143/candidate/`及其最终Manifest／PM Review。
- 历史只读：P3-138～P3-143正式提交资产、D-0595～D-0644、模型设置基线与Frozen Architecture V1.0。
- 允许变化：仅任务卡明列的P3-144工程、交付物、评审路径；PM账本只由PM主会话更新。

## 启动前质疑窗口

- 执行方如发现正式输入缺失、固定20 IPC不能承载流程、DeepSeek authority或真实内容保护语义歧义，必须在修改候选、访问Pilot或联网前暂停回报。
- PM处理：当前合同禁止以未跟踪历史文件补洞；优先以P3-143当前正式候选和账本决策为权威输入。
- 最终冻结版本：ABF-P3-144-v1。
- 专项会话开始后不得实质修改本ABF；需要修改则关闭并新建任务。
