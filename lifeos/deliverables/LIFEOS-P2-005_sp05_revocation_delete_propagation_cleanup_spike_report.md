# LIFEOS-P2-005｜SP-05 撤回 / 删除传播、依赖发现与清理验证技术 Spike 报告

- 任务 ID：LIFEOS-P2-005
- 主责角色：AI 信任与安全负责人
- 协审角色：技术架构负责人、数据 / 领域模型负责人、产品架构负责人、体验设计负责人
- 评审关卡：Gate 3、Gate 2、Gate 4
- 执行日期：2026-08-08
- 证据范围：macOS arm64、Python 标准库、确定性合成夹具、单进程状态机、mock 第三方

## 0. 结论标记

- **[已验证事实]** 本任务在授权范围内创建并复跑了 67 项确定性测试，结果 67/67 PASS、P0 失败 0、活跃路径漏阻断 0、删除后复活 0、审计 / 日志 / 清理证明禁用模式命中 0；未连接真实 Vault，未调用真实模型、云或第三方。
- **[结论]** SP-05 判定为 **`Pass`（严格限本次合成 mock 候选实现层）**。四命令分离、依赖发现、两阶段语义、故障恢复、不复活、供应商限制披露和隐私断言均通过，证据可一条命令复跑。
- **[边界]** 此 Pass 不证明生产队列、真实跨设备同步、真实备份窗口、真实供应商删除能力、容量性能或法律合规；不冻结 Schema、API、状态枚举、技术架构、删除 SLA、V1 范围或 MVP 开发准入。
- **[建议｜需 PM 确认]** V1 可继续保留本地撤回 / 删除能力为 Must 候选，但正式实现必须继承“提交即阻断、墓碑优先、清理状态诚实披露”的 P0 门槛；真实云 / 第三方处理继续关闭，直至真实处理者资格与删除边界专项验证通过。

## 1. 任务边界与结论摘要

本次只验证 SP-05 的最小传播契约：一个内存依赖图表示 Source、Artifact、ArtifactVersion、Derivation、Feedback、Authorization、AuditEntry、Link 以及索引、缓存、队列、备份、离线和第三方副本；命令在阶段 A 原子化改变可消费状态并生成清理 outbox，阶段 B 用租约、幂等键、重试、死信和验证状态清理可控物理副本。

**[已验证事实]** 该模型覆盖 22 类依赖、6 组影响集合样例、12 条活跃消费路径、4 种第三方删除能力、5 种复活入口及关键故障点。它足以检验传播不变量，因为测试判断的是命令后果、可消费性和状态收敛，而不是某一数据库或消息系统的字段实现。

**[推断]** “墓碑 / 授权版本 + outbox + 消费前重检 + 幂等清理”可作为正式架构设计的候选机制。单进程 mock 尚不能证明跨进程事务边界、并发线性化、批量清理吞吐或真实设备最终收敛。

## 2. 最小传播模型与非冻结说明

最小模型由三部分组成：一是带 `inputs` 的依赖图，用于从命令根对象计算传递影响集合；二是权威限制层，包括 Authorization 版本、Source 连接状态、Feedback 当前效力和不可被旧代覆盖的 tombstone；三是清理 outbox，每个物理依赖使用 `sha256(command_id + node_id)` 形成幂等键，并保留租约代、尝试数、状态和原因码。

影响集合分为 `invalidated`、`retained` 与 `physical_cleanup`。运行时先基于 `invalidated` 和权威限制拒绝消费；物理清理只处理可控且确需移除的副本。用户确认历史、Feedback 历史、最小 AuditEntry 与清理证明不因证据删除而静默消失，但必须退出自动建议依据，必要时进入 `review_required`。

本模型没有把节点类型映射成数据库表，没有规定 REST / event API，没有选择正式队列、搜索或备份实现，也没有承诺状态时限。因此它是可执行验证夹具，不是 Schema / API / 技术架构冻结。

## 3. 四类命令效果矩阵

| 命令 | 立即改变 | 默认保留 | 异步处置 | 不得冒充 |
|---|---|---|---|---|
| `revoke_processing` | 命中六维范围的 Authorization 失效、版本递增；相关消费拒绝 | 原文、合法外部指针、确认与反馈历史 | 失效 / 重建依赖派生、索引、缓存、prompt、队列及第三方副本 | 不断源，不表示内容已删除 |
| `disconnect_source` | 停止继续读取、监听或同步 | 外部原件不受控；已有副本依保留许可重判 | 实时依赖失效；无物理清理需求时明确报 `completed_no_physical_cleanup_required` | 不撤销全部处理许可，不自动删除合法副本 |
| `delete_content` | 写目标墓碑；目标及传递依赖退出全部活跃路径 | 非目标用户确认 / Feedback 历史与最小审计；唯一证据失效者待复核 | 删除可控原文 / 版本 / 分块 / 索引 / 缓存 / prompt / 队列 / 备份 / 离线 / vendor mock | 不等同断源；外部原件不受控时必须披露 |
| `retract_feedback` | 追加撤回语义，旧 Feedback 当前效力为 false | 原文、来源、Feedback 历史和对象身份 | 直接依赖 Feedback 的物化派生失效、重建或清理 | 不删除原文，不伪造外部副作用 |

**[已验证事实]** 16 项命令语义断言全部通过。单 Artifact、单 ArtifactVersion、Source 级删除的影响集合不同；删除单版本不包含兄弟版本，Source A 的影响不扩到 Source B。Project 撤权、特定目的、位置 / 处理者和目录排除均生成边界明确的影响集合：搜索目的不命中摘要，第三方处理者不命中本地 FTS，排除目录不命中同源正常目录。未知或遗漏时默认阻断；本次只验证合成目录节点，不宣称真实文件扫描通过。

## 4. 依赖登记与影响集合生成

登记覆盖用户原文、外部原文副本 / 指针、ArtifactVersion、分块、FTS、向量 mock、摘要、恢复片段、候选 Action / Decision、重要 Link、确认对象、Feedback、缓存、prompt、队列、对象文件 / 指针、备份、离线 outbox、第三方 mock、AuditEntry 与清理证明。

必须显式登记的是原文 / 版本所有权、Derivation 输入、重要 Link 证据、确认对象证据、Feedback 引用、prompt / 队列发送 manifest、对象文件、离线副本和第三方发送记录；FTS、向量、缓存、备份可以“显式 owner / manifest + 重建扫描”双重发现。任何依赖索引缺失、扫描失败、代际不明或边界未知时，必须保守 `active_blocked`，不得因为尚未发现物理副本而允许消费。

多输入 Derivation 测试中，删除 Project A 输入后仍有 Project B 合法输入，可以生成新 Derivation 并披露证据缺口；当所有输入均被墓碑覆盖时拒绝重建。跨 Project Link 作为依赖被发现并退出展示，Project 关系没有成为扩权来源。

## 5. 两阶段状态机与用户可见语义

阶段 A：`accepted → active_blocked → physical_cleanup_pending | completed_no_physical_cleanup_required`。同一提交写命令、Authorization 版本 / tombstone / Feedback 或 Source 状态、依赖失效、最小 AuditEntry 与 outbox。只有完成该提交才向用户回执；`active_blocked` 的含义只是“LifeOS 已停止使用”，绝不等于物理删除完成。

阶段 B：`physical_cleanup_pending ↔ physical_cleanup_failed → physically_cleaned`。第三方不支持完全删除时为 `vendor_limited`；唯一证据不可用的用户确认对象为 `review_required`。`physically_cleaned` 必须有目标不存在的验证证明；失败或死信持续保留 `active_blocked`。

**[体验建议]** 用户文案可分别表达“已停止使用”“仍在清理副本”“清理失败，将继续重试”“供应商限制，LifeOS 已停止继续使用但无法确认对方立即删除”“已完成可控副本清理”“无需物理清理”“需要你复核”。具体 UI 不在本任务范围，需后续 PRD / 体验任务确认。

## 6. 活跃阻断验证

**[已验证事实]** 删除事务提交后，本地读取、FTS 查询、向量近邻 mock、Project 恢复包、首页 / 今日建议、AI 候选生成、队列领取、模型网关发送、跨 Project 展示、再派生、导出和重导入共 12 条路径全部拒绝；另测模型调用计数保持 0。活跃阻断类别 13/13 PASS，漏阻断为 0。

每个消费函数先检查节点当前状态、祖先墓碑及路径资格。队列 payload 即使仍物理存在也无法领取；prompt 副本即使清理尚未开始也无法发送。该顺序证明“物理清理稍后完成”不能作为运行时继续使用的理由。

## 7. 可还原副本清理验证

FTS posting、向量 mock、缓存、prompt 副本、队列 payload 和可还原摘要分别执行清理并验证 `physical_present=false`，6/6 PASS。恢复包、候选对象、重要 Link、对象文件、备份、离线副本和第三方副本也均进入依赖影响集合；完整样例记录在证据包。

prompt 的推荐默认不是长期保留后再清理，而是“不保存或只保留不可逆最小 manifest”；本测试保留 prompt mock 是为了证明最坏情况下仍能发现和清理。FTS / 向量查询还必须有墓碑过滤，因此清理中的陈旧 posting 也不能被命中。

## 8. 故障注入、幂等、租约、重试与死信

**[已验证事实]** 覆盖清理前失败、清理中 / 网络失败、清理效果完成但状态落盘前崩溃、重复消息、乱序 / 已完成任务重复执行、租约过期后换 worker 领取、失败后重试以及重试耗尽进入死信。6 项聚合断言全部通过：重复清理不产生破坏；效果先发生而状态未写入时，下一次验证后收敛；死信可见且活跃读取仍拒绝。

**[限制]** 这些是确定性单进程故障点，不代表正式事务数据库与消息系统已通过 crash-consistency、并发或容量测试。正式实现必须复验“outbox 与墓碑同事务”“租约 fencing”“幂等副作用”和“验证后完成”四项不变量。

## 9. 墓碑优先与不复活

备份恢复在开放正常查询前先加载并验证 tombstone / restriction；旧代数据不能覆盖更新代墓碑。旧导入包、来源重连、离线 outbox 回放和旧队列重试均在接纳 / 领取 / 发送前重检当前代。五类入口全部拒绝已删版本，复活数 0。

Source 重连只恢复“允许继续读取”的连接能力，不能删除或覆盖内容墓碑。备份物理改写 / 到期、不可达离线设备清理仍属于阶段 B，不影响阶段 A 阻断。真实多设备冲突与同步盘竞态属于 SP-06，不能由本结果外推。

## 10. 第三方 mock 清理与诚实披露

第三方 mock 覆盖成功、延迟、不支持、失败四种模式，分别得到 `physically_cleaned`、`physical_cleanup_pending`、`vendor_limited`、`physical_cleanup_failed`；四种情况下活跃使用均为 blocked。没有把 API 接受请求、到期删除或“不支持删除”误报为完成。

**[建议｜需 PM 确认]** 真实云 / 第三方处理继续保持关闭。未来只有在具体处理者的政策版本、地区 / 子处理者、训练 / 评估、保留、删除接口、删除证明与失败披露通过专项验证后，才可按目的和范围开启。若无法证明，应移出 V1，而不是降低默认拒绝门槛。

## 11. 用户确认对象、Feedback 与证据失效

删除或撤权不会静默删除用户确认的 Action / Decision / Assertion 历史。若唯一证据失效，对象保留身份与历史但进入 `evidence_unavailable / review_required`，退出今日建议、恢复包排序和自动再派生依据。若对象本身是显式 `delete_content` 目标，才执行对象删除。

Feedback 采用追加历史：确认、拒绝、纠正、完成、延期的旧事件保留；`retract_feedback` 只撤销指定事件当前效力，并让直接依赖它的派生重算、stale 或 invalid。测试覆盖确认撤回及其他四种反馈类别的语义分离，不把撤回写成删除原文。

## 12. 审计、日志、清理证明与隐私

AuditEntry 只记录命令类别、作用域化 command 引用、状态、受控原因码、scope digest 和序号；清理证明只记录作用域化 job / command 引用、依赖类别、结果、原因码和验证 digest。它们不记录正文、完整路径、prompt、模型输出、向量、原始对象 ID 或第三方 payload。

隐私扫描对合成正文 / prompt sentinel、Home 路径、私钥头、向量字段和值和私有 Vault 路径执行正则检查，命中 0；另测清理证明不可出现原始对象 ID。**[限制]** 本次未做大规模 ID 枚举、时间关联或跨日志重识别攻击；正式实现还需访问控制、保留期和聚合粒度专项验证。

## 13. 测试矩阵与最低断言

| 类别 | 结果 |
|---|---:|
| 四命令语义 | 16/16 |
| 状态语义 | 4/4 |
| 活跃阻断 | 13/13 |
| 依赖发现 / 作用域 | 8/8 |
| Derivation 重建 | 3/3 |
| 物理清理 | 6/6 |
| 故障恢复 | 6/6 |
| 第三方清理 | 4/4 |
| 不复活 | 5/5 |
| 隐私 | 2/2 |
| **合计** | **67/67** |

最低验收断言全部通过：四命令不互相冒充；活跃阻断漏失为 0；依赖类型覆盖成立；清理在故障、重复、租约和重试后收敛；死信不解除阻断；可还原副本清理后不命中；恢复 / 重放不复活；确认历史进入待复核而非静默删除；供应商受限不误报；审计不可还原。

## 14. 最终结论与 V1 影响

**最终结论：`Pass`，仅限本次合成 mock 候选实现层。** 判定依据是任务定义的全部 P0 断言通过且证据可复跑；mock 与单进程是任务预先允许的实验边界，不单独构成条件失败。

**[建议｜需 PM 确认]**

1. V1 保留 `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 四个独立产品意图，不合并为一个“删除 / 断开”动作。
2. 本地原文 / FTS / 缓存 / 可重建派生可继续作为候选能力，但任何正式实现必须复验全部消费入口；向量仍不是 V1 Must，可保持关闭而不影响最低 FTS 路径。
3. 不保留可还原 prompt 副本；候选 Action / Decision / Link 继续优先作为 L1 Derivation，SP-06 前不升级为持久 L3 默认对象。
4. Obsidian 仍为 Should + 条件项；断源不删除外部 Vault，删除只覆盖 LifeOS 可控副本并披露外部原件边界。
5. 真实云 / 第三方保持关闭；本次不解除 Stage 3 阻塞。正式 MVP 开发仍需后续 Spike、技术架构独立评审及 PM 确认。

风险建议交 PM 判断是否登记：依赖登记遗漏导致暗副本、状态文案把阻断误写为删除完成、生产 outbox 非原子、旧设备 / 同步盘墓碑代际冲突、供应商删除政策变化、最小审计被关联重识别、批量 Source 删除容量不足。

## 15. 后续 Spike 与架构候选影响

- SP-06 应复用 tombstone generation、消费前重检和 `review_required`，验证真实多设备 / 离线冲突，不重复定义四命令。
- SP-07 可继续以 FTS + 元数据为 Must 候选；向量若启用，必须继承 owner 登记、查询过滤和可重建清理。
- SP-08 必须验证删除前旧导出包往返仍墓碑优先，并保持 AuditEntry 最小化。
- SP-09 需验证 Source 级批量影响扫描、outbox backlog、重建与备份改写容量；未通过前可降级为单 Artifact / 小范围删除。
- 技术架构评审可评估关系型依赖索引、transactional outbox、租约 worker 与恢复 gate，但本报告不冻结具体组件。

## 16. 需要 PM / 用户确认的问题

1. 是否验收 SP-05 为本次边界内 `Pass`，并把“活跃阻断零遗漏 + 物理清理真实状态 + 墓碑优先”作为后续实现不可降级门槛？
2. 是否采纳 V1 能力处置：本地四命令与 FTS 候选保留，向量非 Must、prompt 不做可还原保留、L3 候选继续降级、真实第三方保持关闭？
3. 是否把依赖遗漏、生产 outbox 原子性、同步复活、供应商限制和审计重识别风险写入 PM 风险登记？专项会话未修改 PM 文件。
4. 是否确认本次 Pass 不冻结 Schema / API / 架构 / SLA，不解除正式 MVP 开发阻塞？

## 17. 角色与关卡自检

- **主责｜AI 信任与安全负责人：Pass（SP-05 合成实现层）。** 事务提交真实改变运行时消费，12 条路径漏阻断为 0；四命令分离；清理失败和 vendor 限制诚实披露；审计 / 证明最小化。
- **技术架构负责人：Pass（候选机制层）。** tombstone、授权版本、依赖图、transactional outbox 语义、幂等键、租约、重试、死信和恢复 gate 可执行；未冻结正式架构，跨进程与容量待后续。
- **数据 / 领域模型负责人：Pass。** Source、Artifact / Version、Derivation、Feedback、Authorization、AuditEntry、Link、墓碑与清理状态边界清楚；未把节点类型当数据库表冻结。
- **产品架构负责人：Pass。** 语义服务个人可信外脑的数据主权与掌控感，没有扩成企业合规后台或 IT 运维控制台。
- **体验设计负责人：Pass（状态语义层）。** `active_blocked`、pending、failed、vendor limited、cleaned、no cleanup、review required 均可转成用户语言；具体文案 / UI 待后续。

| 关卡 | 本任务结论 | 边界 |
|---|---|---|
| Gate 3 AI 权限与信任 | **Pass（合成实现层）** | 撤回 / 删除零漏阻断、状态诚实、历史与证据边界成立；真实供应商未通过 |
| Gate 2 数据与来源 | **Pass（测试语义层）** | 来源 / 原文 / 派生 / 确认 / 墓碑 / 审计边界成立；Schema、真实 Vault、同步未冻结 |
| Gate 4 技术可行性 | **Pass（单进程候选机制层）** | 67/67 可复跑；生产并发、容量、真实备份 / 设备 / vendor 仍待验证 |

以上是专项会话自检；是否作为项目关卡正式验收、是否更新冻结状态或允许后续阶段，仍需 PM 主会话决定。

## 18. 证据包路径

- `lifeos/spikes/SP-05/run_spike.py`：可复跑验证脚本
- `lifeos/spikes/SP-05/results.json`、`test_matrix.csv`：机器结果与完整测试矩阵
- `lifeos/spikes/SP-05/dependency_registry.md`、`impact_set_samples.json`：依赖登记与影响集合
- `lifeos/spikes/SP-05/propagation_state_machine.md`、`cleanup_outbox_report.md`：两阶段语义与 outbox
- `lifeos/spikes/SP-05/active_blocking_scan_report.md`：12 条活跃路径扫描
- `lifeos/spikes/SP-05/cleanup_fault_injection_report.md`：故障、幂等、租约、重试和死信
- `lifeos/spikes/SP-05/backup_restore_replay_report.md`、`reimport_reconnect_offline_replay_report.md`：不复活证据
- `lifeos/spikes/SP-05/third_party_cleanup_matrix.md`：第三方 mock 能力矩阵
- `lifeos/spikes/SP-05/cleanup_proof_samples.json`、`raw_logs/`：最小清理证明、审计与隐私扫描
- `lifeos/spikes/SP-05/environment.md`、`fixtures.md`、`cleanup.md`：环境、夹具和清理说明

复跑命令：`python3 lifeos/spikes/SP-05/run_spike.py`
