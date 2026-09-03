# ABF-P3-145-v1｜Work＋Health 跨域 Today 个性化与反馈适应真实闭环

## 冻结信息

- 任务 ID：LIFEOS-P3-145
- ABF ID／版本：ABF-P3-145-v1
- 生效决策：待用户确认完整Task Contract后登记
- 冻结时间：待确认
- ABF文件SHA-256：确认后由PM记录在任务卡／决策日志；本文件不自指
- 状态：Draft
- 本文件是否在专项会话开始前冻结：尚未启动专项会话

## 本轮唯一用户结果

- 单一结果：复用Pilot-7既有Work与加密DeepSeek服务，将一条用户确认的长期信息和当天非医疗Health状态共同纳入Person-level Today／Global AI最小上下文；反馈后后续理解或建议发生可解释变化并跨重启保持。
- 不冻结：产品整体、UI资产、Runtime、IPC、Schema/API、Provider、风险或Stage。
- 非范围：医疗、其他Provider、后台发送、fallback、clear、export、同步、工具调用、风险关闭和Stage 4。

## 授权和能力边界

- 允许目录：`lifeos/engineering/LIFEOS-P3-145/`、`lifeos/reviews/LIFEOS-P3-145/`、对应deliverable；工程／评审唯一临时根。
- 允许数据：Phase A/B仅固定合成数据；Phase C复用Pilot-7 `capture.sqlite`，新增1～3条Health Current State与1条Durable Memory，每条≤200字符。
- 允许入口：P3-144恰好20 IPC中的既有能力、actual Tauri UI、用户逐次确认后最多2次DeepSeek请求。
- 严格只读：P3-144 candidate／Task／ABF／Review／Evidence／Manifest、Architecture V1.0、IA V1.0与历史账本。
- 禁止：Phase A/B触达Pilot-7；真实正文Evidence；其他Provider／authority；后台／fallback／重试／重定向；医疗；清理真实资产；关键合同／风险／冻结／Stage变化。
- 投递前额外用户确认：必须一次确认完整P3-145 Task Contract所列Pilot-7复用、数据额度、最多2次DeepSeek、保留策略和全部禁止边界。

## 引用的长期质量原则

- L1-1数据主权：只处理逐次确认的最小Context和精确DeepSeek目标。
- L1-2内容身份：Memory、Current State、AI Understanding与原文分离。
- L1-3生命周期完整：新增、选择、反馈、失效、重启一致。
- L1-4失败关闭：未确认／超预算／高风险Health／凭据失败均在网络与持久化前停止。
- L1-5用户控制：每次披露发送由用户确认，AI不得替用户确认。
- L1-6／7审计与Evidence：真实内容不入Evidence，仅使用可复核非内容refs／状态／authority。
- L1-8／9历史与授权：P3-144只读，重跑不扩大范围。
- L1-10可复核：固定合成夹具、review-owned mutation与Manifest。
- L1-11／12防回退：baseline lineage matrix逐项验证，用户确认优先。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | P3-144已确认UI／Provider／20 IPC／DB／披露／反馈基线不回退 | P0 | lineage matrix全Pass | Closure Cycle；实质合同变化则新任务 |
| ABF-I-02 | Memory／State／Understanding身份分离 | P0 | 类型、来源、validity、确认状态可审计 | Closure Cycle |
| ABF-I-03 | Today最多一个Person-level Focus且允许空 | P1 | 跨域与证据不足夹具均符合 | Closure Cycle |
| ABF-I-04 | 每次只向DeepSeek发送本次确认的最小Context | P0 | 披露refs等于实际request refs；其他网络0 | 立即停止；越界则Invalidated |
| ABF-I-05 | 反馈导致受影响投影可解释变化，历史不覆盖 | P1 | dependency before/after及restart成立 | Closure Cycle |
| ABF-I-06 | Health非医疗且高风险路径网络前停止 | P0 | safety mutation零网络／零部分写入 | 立即停止 |
| ABF-I-07 | 真实正文／凭据零Evidence，Agent不读取 | P0 | 流程审计和合成taint攻击通过 | 越界则Invalidated |
| ABF-I-08 | Pilot-7与既有DB无损保留、普通文件0600 | P0 | 非内容计数／状态／权限前后一致 | 立即停止 |
| ABF-I-09 | 一次独立评审后才进入真实Gate | P0 | 时间与Manifest谱系成立 | 不得进入Phase C |
| ABF-I-10 | 环境问题checkpoint恢复，不机械重做 | P2 | resume_from与摘要校验成立 | Paused — Resumable |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | lineage | P3-144固定输入 | 复算并回归 | 全部继承 | 历史只读 | IR-LINEAGE | matrix/hash |
| ABF-M-002 | update_current_state | 合成DB | 1～3、空值、201字符、未知字段 | 合法写入；非法写前拒绝 | 非目标表 | RT-STATE | before/after |
| ABF-M-003 | upsert_durable_memory | 合成DB | 确认／未确认／替代 | 仅确认有效项进入Profile | 原文／历史 | RT-MEMORY | lineage |
| ABF-M-004 | get_today | Work＋Health＋Memory | 正常／证据不足／冲突 | 最多1 Focus或合法空 | 无Domain配额 | RT-TODAY | reason refs |
| ABF-M-005 | resolve_request_context | 混合有效性 | 相关／跨域／过期／撤回 | 只选最小有效授权refs | 全库不出境 | RT-RESOLVE | selected/excluded |
| ABF-M-006 | disclosure UI | 已组装集合 | 移除／取消／集合改变 | 预览同步；旧确认失效 | network=0 | GUI-DISCLOSE | AX/snapshot |
| ABF-M-007 | confirm/send | 未确认／旧确认／空集合 | 尝试发送 | 稳定拒绝 | DB与network不变 | RT-CONFIRM | counters |
| ABF-M-008 | DeepSeek adapter | 已确认合成请求 | 重定向／代理／超时／其他target | 精确authority或失败关闭 | 无fallback／重试 | RT-NET | ledger |
| ABF-M-009 | response persistence | 合成响应 | 保存／重启 | typed Understanding/Suggestion | 不成用户事实 | RT-RESULT | metadata |
| ABF-M-010 | feedback | 有效Understanding | 五类反馈／重复消费／纠正 | 终态单次消费；受影响投影变化 | 历史不覆盖 | RT-FEEDBACK | dependency matrix |
| ABF-M-011 | Health safety | 高风险合成文本 | 解析／发送 | 网络前保守停止 | DB无部分写入 | RT-SAFETY | zero-network |
| ABF-M-012 | credential | 合成密文／缺Key／篡改 | 启用／发送 | 正常或网络前拒绝 | 明文零日志 | RT-CRED | secret-free receipt |
| ABF-M-013 | actual Tauri | fresh bundle/PID | 三档导航、Today、披露、回答、反馈 | exact PID→AXWindow→WebView | 基线视觉 | GUI-NATIVE | target-only evidence |
| ABF-M-014 | restart | 已完成合成闭环 | 关闭重开 | 状态与投影一致，不重发 | network count | RT-RESTART | before/after |
| ABF-M-015 | independent review | precontact seal | reviewer mutations | 自有测试捕获语义破坏 | candidate只读 | IR-MUTATION | report/Manifest |
| ABF-M-016 | real preflight | Independent Pass | 进入Pilot-7前核门 | 只允许已确认边界 | 正文不可观察 | REAL-GATE | non-content receipt |
| ABF-M-017 | real cross-domain | 用户手工操作 | 输入／Today／披露／最多2次请求 | 唯一用户结果成立 | 其他Provider／后台=0 | REAL-LOOP | non-content receipt |
| ABF-M-018 | real feedback/restart | 用户完成反馈 | 刷新／关闭重开 | 可解释变化并保持 | 既有数据不丢失 | REAL-RESTART | counts/status/refs |
| ABF-M-019 | cleanup | task-local temp root | 错误／正确marker | 错误拒绝；正确精确清理 | Pilot-7不清理 | CLEANUP | receipt |
| ABF-M-020 | final Manifest | 全部Evidence | 独立复算 | 非自指、hash全匹配 | 历史保全 | MANIFEST | verifier |

## Evidence 合同

- Runner／测试源码：保留于P3-145工程／评审目录。
- 逐行结果：AC-01～20与ABF-M-001～020均有独立记录，不能由总测试批量映射。
- before／after：合成DB完整；真实DB仅count／type／status／opaque refs／mode，不读正文。
- source／history：P3-144候选和历史逐文件hash；P3-145固定候选Manifest。
- Manifest：工程和独立评审各自非自指Manifest及verifier。
- 清理：只清理两个task-local临时根；Pilot-7、DB、凭据保留。

## 计数与Pass公式

- 必须报告P0、P1、P2、Unknown、Not Implemented。
- Pass：所有AC／ABF适用行Pass；P0／P1／Unknown／Not Implemented为0；P2不影响用户结果、安全边界、生命周期或Evidence可信度。
- N/A：仅平台确实不适用且合同明确允许，不可代替未执行。

## Closure Cycle与退出规则

- 首次不通过一次列全合同内缺口；同结果／数据／目录／Provider／权限／架构／ABF不变时在P3-145内收口，无需重复授权。
- Provider、真实根、数据类型／额度、网络目标、医疗边界、凭据、关键IPC／Schema/API或ABF变化时关闭并新建任务。
- 锁屏、AX、截图、runner或临时网络不可用时写checkpoint并`Paused — Resumable`。
- Blocked：用户输入／Provider服务等必要外部条件长期不可用；不得伪造Evidence。

## 候选基线与只读保全

- 候选输入：P3-144 accepted candidate与终局Review/Evidence/Manifest；确认时记录精确commit／hash。
- 历史只读：所有P3-144及P3-145失败／排除Evidence。
- 允许变化：仅P3-145工程、交付物和评审目录；PM账本由PM维护。

## 启动前质疑窗口

- 执行方歧义：必须在候选复制、真实根探测或工程动作前提出。
- PM处理：不改变本ABF的解释可澄清；实质变化则关闭并新建。
- 最终冻结版本：待用户一次确认后由PM填写并计算外部hash。
