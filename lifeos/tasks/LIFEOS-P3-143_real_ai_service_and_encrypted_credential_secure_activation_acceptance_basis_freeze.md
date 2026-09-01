# ABF-P3-143-v1｜真实 AI 服务与加密凭据安全启用闭环

## 冻结信息

- 任务 ID：LIFEOS-P3-143
- ABF ID／版本：ABF-P3-143-v1
- 生效决策：D-0641
- 冻结时间：2026-09-01
- ABF 文件 SHA-256：记录于 `lifeos/tasks/LIFEOS-P3-143_acceptance_freeze_manifest.json`，不在本文件自指。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 用户在 P3-142 模型设置中心中选择 DeepSeek，手工输入 API Key；API Key 以 SQLite 密文跨重启保存、密钥材料与 DB 分离；用户逐次测试、选模型、启用并发送一条固定无个人含义 canary，随后删除凭据并证明后续调用失败关闭。
- 不冻结：具体 DeepSeek 模型目录、生产 SLA、其他 Provider 的真实能力、产品整体实现、Schema/API、风险或 Stage。
- 非范围：Pilot、个人 DB／文本／Context／Memory／Health、语音／图片真实上传、自动 fallback、Agent／工具调用、同步、导出、风险关闭、Stage 4。

## 授权和能力边界

- 允许目录：`lifeos/engineering/LIFEOS-P3-143/`、对应 deliverable/review/task 文件、唯一 `/private/tmp/lifeos-p3-143-real-ai-secure-activation-v1`。
- 允许数据：全新合成 SQLite、固定无个人含义 canary、用户在 App 内输入但不被 Agent 观察的 DeepSeek API Key。
- 允许入口：P3-142 已有 Settings UI 与恰好 20 IPC；不得新增隐藏入口。
- 允许外部目标：仅用户触发访问 `https://api.deepseek.com`；TLS 必须校验，禁止跨 authority redirect、代理继承和后台请求。
- 允许系统凭据：仅创建／读取／删除 P3-143 专用 macOS Keychain 密钥材料项；禁止枚举或触碰其他项。
- 严格只读：P3-139／140／141／142 任务、candidate、Evidence、Review、Manifest 与模型设置产品基线。
- 禁止：任何 Pilot／真实个人资产／其他 Provider／其他网络目标／明文 Key Evidence／产品模型读取个人内容。
- 额外确认：用户已用“我就要用 DeepSeek”及“创建并开始”覆盖本 ABF 的单一 Provider 真实 Gate；Key 仍只由用户在 App 内手工输入。L3 PM Pass 后仍等待用户最终确认。

## 引用的长期质量原则

- L1-1／L1-3：用户数据与原文主权；本轮不发送个人数据，canary 为固定合成文本。
- L1-4／L1-5：来源／派生可追溯且重大动作由用户确认；保存、测试、选择、启用、发送分离。
- L1-7／L1-9：Evidence 必须可复核且结论匹配事实；非内容 Evidence、逐行矩阵和独立 Manifest。
- L1-10／L1-11：边界与失败关闭；未授权、缺密钥、篡改、错误目标均在网络／写入前停止。
- L1-12：历史只读保全；P3-142 及此前资产不得覆盖。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | Provider 与 UI 防回退 | P0 | Cloud 8／Local 4、Cloud/Local分离、高保真三档与恰好20 IPC全保留 | Rework |
| ABF-I-02 | 凭据密文持久化 | P0 | SQLite无明文，ciphertext跨fresh PID重启可解密 | Rework |
| ABF-I-03 | 密钥材料分离 | P0 | DB副本在无对应Keychain项时不可解密，Keychain不保存Provider Key明文 | Rework |
| ABF-I-04 | 全生命周期零泄漏 | P0 | Key canary未命中DB/WAL/SHM/log/error/screenshot/Evidence/env/argv/export | Rework；若真实泄漏不可分离则停止并由PM判断关闭 |
| ABF-I-05 | 用户逐次控制 | P0 | 保存、测试、模型读取、选择、启用、发送均不互相静默触发 | Rework |
| ABF-I-06 | 单一真实 Provider／目标 | P0 | 仅明确启用的DeepSeek可向精确authority发送 | Rework |
| ABF-I-07 | 最小披露 | P0 | 唯一真实prompt为冻结canary，零Pilot／个人Context／Health | Rework；实质越界接触立即停止 |
| ABF-I-08 | 篡改与缺失失败关闭 | P0 | DB、密钥、AAD、reference、授权任一无效均network counter=0 | Rework |
| ABF-I-09 | 更新／删除完备 | P0 | 旧密文、reference、Keychain项和运行期副本全部失效 | Rework |
| ABF-I-10 | 无隐式调用 | P0 | 无后台检查、fallback、proxy、跨authority redirect、并行或未知结果重试 | Rework |
| ABF-I-11 | Evidence 诚实 | P0 | 正文与Key零Evidence；成功／失败分类和authority可审计 | Rework |
| ABF-I-12 | 可恢复执行 | P1 | 锁屏／截图／暂时网络问题生成有效checkpoint，可定向resume | Paused — Resumable |
| ABF-I-13 | 独立性与清理 | P0 | fresh reviewer、fresh DB/root/PID；错误marker拒绝，正确marker精确清理 | Rework／Blocked |

## 冻结验收矩阵

每行必须有独立夹具、动作、断言和 Evidence；不得由总测试结果批量映射。

| 行 ID | 入口／场景 | 操作／失败点 | 预期结果 | 必须保持不变 | Evidence |
|---|---|---|---|---|---|
| ABF-M-001 | P3-142 baseline | 复算Provider/UI/20 IPC/source lineage | 全部一致 | P3-142只读 | lineage + exact-list |
| ABF-M-002 | 保存非敏感Provider config | 保存并重启 | 配置恢复，无网络 | 凭据／启用未变化 | lifecycle JSON |
| ABF-M-003 | 保存Key canary | 用户输入后保存 | DB仅密文；Keychain仅分离密钥材料 | 日志/Evidence零明文 | leak scan + DB classification |
| ABF-M-004 | fresh restart | 关闭并以fresh PID重开 | 可经CredentialPort解密，UI仅掩码尾部 | 无后台请求 | PID/DB/network receipt |
| ABF-M-005 | DB-only copy | 无Keychain项打开复制DB | 网络前稳定拒绝 | DB不写 | structured failure |
| ABF-M-006 | key/cipher/AAD/reference mutation | 逐项变异 | 全部认证失败并拒绝网络 | 原DB/Keychain不变 | review-owned mutations |
| ABF-M-007 | update credential | 保存第二canary | 第一密文/reference失效 | 未触发测试/发送 | before/after + scan |
| ABF-M-008 | delete credential | 用户删除后fresh restart并调用 | 立即拒绝；DB/reference/Keychain/runtime副本失效 | Provider config可保留 | deletion lifecycle |
| ABF-M-009 | save/test/select/enable/send | 每一步单独执行 | 仅显式步骤推进 | 其他counter为0 | state/counter matrix |
| ABF-M-010 | invalid URL/provider/DTO | unknown field、HTTP、非法authority、重复ID | 持久化／网络前拒绝 | DB/Keychain不变 | negative matrix |
| ABF-M-011 | redirect/proxy/DNS/timeout | synthetic攻击fixture | 无跨authority、无proxy、无未知重试 | 零额外请求 | network harness |
| ABF-M-012 | error classification | auth/network/timeout/model/capability | UI诚实分类且零secret | config/DB不被部分推进 | structured errors |
| ABF-M-013 | provider truthfulness | 遍历Cloud8/Local4 | 仅DeepSeek可进入本轮真实Gate，其余未验证 | 目录不减少 | per-provider ledger |
| ABF-M-014 | desktop | fresh PID打开Settings | 目标窗口完整、掩码安全 | 无桌面外内容截图 | PID→AXWindow→WebView + screenshot |
| ABF-M-015 | compact | 同上 | 控件可达、无截断 | 同上 | native evidence |
| ABF-M-016 | narrow | 同上 | 控件可达、无横向溢出 | 同上 | native evidence |
| ABF-M-017 | Phase A Gate | 全部合成测试、mutation、Manifest | 通过后才允许真实Gate | DeepSeek零访问 | Phase-A manifest |
| ABF-M-018 | DeepSeek test/model list | 用户点击测试 | 仅精确authority请求；成功后展示真实返回模型 | 零个人数据、零正文Evidence | non-content receipt |
| ABF-M-019 | DeepSeek canary send | 用户选模型、启用并发送冻结canary | App瞬时显示响应；仅非内容审计 | Pilot/Context/Memory零读取 | disclosure + network receipt |
| ABF-M-020 | post-send cleanup | UI删凭据、重启拒绝、精确清理root | DB/Keychain/runtime全部失效，root absent | 其他Keychain项零触达 | cleanup receipt |
| ABF-M-021 | environment pause | 锁屏／AX／暂时网络不可用 | checkpoint并定向resume | 已闭合阶段Evidence不重做 | checkpoint/resume log |
| ABF-M-022 | independent review | fresh seal、fresh assets、review-owned attacks | ABF-I-01～13独立通过 | candidate/history只读 | independent Manifest |

## Evidence 合同

- 可运行 runner／测试源码：工程与独立评审各自保留；独立评审不得调用候选 verifier 作为唯一结论。
- 逐行结构化结果：ABF-M-001～022 每行独立状态、时间、输入 identity、断言与 Evidence refs。
- before／after：candidate、P3-142 history、SQLite、Credential Reference、Keychain item metadata、network counters、root。
- 日志／快照：只允许脱敏结构；不得含 Key、prompt、response 或个人内容。
- Manifest：非自指、区分 candidate／fixed inputs／history／evidence，独立 verifier 可复算。
- 复跑：合成回归可离线重复；真实 Gate 必须用户主动操作，不自动重放。
- 临时清理：先停 App/writer，验证精确marker，再清理唯一root；Keychain只删精确P3-143项。

## 计数与 Pass 公式

- P0/P1/P2/Unknown/Not Implemented 必须逐项报告。
- Pass：ABF-I-01～013、ABF-M-001～022 全部 Pass；P0=0、P1=0、Unknown=0、Not Implemented=0。
- P2 只允许不影响凭据机密性／持久性、Provider目录、授权、网络目标、个人数据边界、Evidence可信度和复现性的事实。
- 允许 N/A：其他 Provider 的真实连接、语音／图片、Pilot、风险关闭、产品冻结、Stage 4；必须标为合同外 N/A，不能标成已实现。

## Closure Cycle 与退出规则

- 首次 PM 不通过一次性列出合同内全部缺口；代码、测试、Evidence、Manifest和同语义失败关闭均留在同一 P3-143 Closure Cycle。
- 同任务条件：唯一结果、DeepSeek目标、目录、数据、凭据方案、20 IPC、授权、架构与本ABF不变。
- 新任务条件：实质改变 Provider 真实目标、个人数据范围、存储／密钥方案、权限、IPC／Schema关键合同，或污染无法与正Evidence可信分离。
- Blocked：缺少用户手工凭据、Provider外部不可用、系统Credential Store不可用且非候选缺陷；记录checkpoint，不降低验收。

## 候选基线与只读保全

- 候选输入：P3-142 `FINAL_MANIFEST.json` 与本 ABF Freeze Manifest 固定的精确清单。
- 历史只读：P3-139／140／141／142 任务、candidate、Evidence、Review、Manifest。
- 允许变化：仅本任务卡列出的 P3-143 任务、工程、交付物和 Review 路径。

## 启动前质疑窗口

- 执行方发现精确输入缺失、任务根冲突、DeepSeek authority或凭据方案歧义时，必须在候选／网络／Keychain接触前暂停回报。
- 最终冻结版本：ABF-P3-143-v1。
- 专项会话开始后不得实质修改本 ABF；如需改变冻结边界，关闭当前任务并新建任务。

