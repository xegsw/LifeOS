# P3-146 合同准备与固定输入定位报告

日期：2026-09-08。主责：Codex 专项合同准备；New Session。

当前状态：合同准备报告已形成，待 PM 定稿；工程未启动。需要 PM 决策：Yes。风险：拟定 L2 合成离线；ABF：N/A。本文件不是工程交付、PM Pass 或正式执行授权。

**阅读顺序：第 6～10 节为当前核验和合同 delta，第 10 节为最终定稿建议；第 1～5 节保留初次准备快照，已被后续明确结论取代，不作为当前阻塞清单。** PM 已校正 D-0651 路径、给出 139/140/145 Review 及固定 SourcePort 规范，固定输入定位缺口全部关闭；不需新任务。剩余是 PM 正式合同决定：DTO/Schema、离线构建边界和 CI 落点，不是缺少输入。

## 1. 事实与输入定位

权威 PM 根：`/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb`。

| 输入 | 定位与核对结果 |
|---|---|
| 正式任务卡 | `/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb/lifeos/tasks/LIFEOS-P3-146_natural_conversation_memory_and_source_integration.md`，52 行完整读取；状态 Created / Contract Preparation，明确禁止工程启动 |
| PM 当前状态 | `/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb/lifeos/CURRENT_STATUS.md`，462 行读至 EOF；输出截断部分已定向补读。顶部 D-0652 优先，旧 145 启动描述保留为历史 |
| PM 登记 | `/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb/lifeos/TASK_REGISTRY.md`，定向读取 D-0651/D-0652 与 139～146 相关行；没有以本工作树旧 main 推断状态 |
| D-0651 直接依据 | 卡写 `PM工作树architecture/自然对话与记忆治理增量说明.md`；精确解析为 `/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb/architecture/自然对话与记忆治理增量说明.md`，`wc -l` 返回 `No such file or directory`。未搜索近似路径、未擅自添加目录前缀 |
| 本树规则与模板 | `/Users/xxe/.codex/worktrees/5ed8/No.2/AGENTS.md` 318 行、`lifeos/templates/SESSION_REPORT_TEMPLATE.md` 72 行、`lifeos/ACCEPTANCE_GOVERNANCE.md` 197 行、`lifeos/CI_CD_GOVERNANCE.md` 112 行均完整读取 |
| 本树身份 | `/Users/xxe/.codex/worktrees/5ed8/No.2`；HEAD `9d4dac3c016edec2acacfcda7f966effb860804c`；分支名为空，即 detached HEAD；tracked status/diff 为空，交付目录原有 untracked 为空。未创建分支或提交 |
| 145 工程输入 | 指定 `/Users/xxe/.codex/worktrees/d510/No.2`、commit `2bd2fb43792ae7de67bc764d8eed063f1ec22824`；在直接输入缺失处停止候选接触，尚未验证 commit、文件清单、接口或合成 Evidence。该身份目前仅为任务卡声明 |

PM 登记确认 139 为 Memory/State/Context、预算失败关闭的历史 PM Pass/独立复评通过；140 为跨域 Today/反馈合成闭环的历史 PM Pass/Independent Pass。这里仅确认登记状态，未复核其实现或复跑测试。

145 的准确口径：凭据兼容工程完成，安全独立 Delta 按用户决定暂缓，Phase C/真实 Gate 暂停，终局未通过。不能从前序真实使用或合成通过继承真实授权，不能称 145 Accepted。

## 2. 缺口与恢复条件

| 编号 | 缺口及影响 | PM 所需补充 |
|---|---|---|
| IN-01 | D-0651 固定依据在任务卡所写精确路径缺失，无法核对产品增量与完整合同；当前停止依赖该依据的候选分析 | 给出正确绝对路径或在该固定位置补齐输入，并明确是路径纠正还是内容变化 |
| IN-02 | 卡仅泛称历史 139/140 复用，未逐项列出工程接口、合成 Evidence 及直接依赖的最新 PM Review 固定输入 | 指定允许读取的精确输入；可明确只从 145 指定 commit 内继承的 139/140 实现定位，无需返回旧临时根 |
| IN-03 | 凭据基线保护与 145 暂缓 Delta 的兼容边界未落实到文件/入口清单 | 指定 145 最新 PM Review 的绝对路径及可读章节、合成输入清单；不提供真实收据/DB/凭据 |
| IN-04 | 最终工程唯一写根与“确定性检查进 CI”存在落点待明确 | PM 指定由谁更新全局 CI 注册；若仍只准写任务工程根，执行侧交付 task-local 检查入口及注册 delta 文档，由 PM 处理外部注册 |
| IN-05 | 新树 detached，145 不在本树已核验基线内 | 最终合同明确从固定 commit 以正向文件清单拷入新工程根；不直接切到/合并整个 145 高风险祖先，不自动 push |

IN-01 是已实测输入阻塞；IN-02～05 是准备期待明确项，不是候选 P0/P1。当前未评估候选质量，不以零缺陷计数表示通过。完整接口核验与完整可执行合同尚未完成，不把本文件当作 Ready。

## 3. 接口复用与缺口表（待源码核验）

下表的“方向”来自任务卡和 PM 登记，不是已确认函数名、DTO、表或 IPC。恢复后每行须补精确 `commit:path:line`、签名、调用链、测试及兼容 delta，禁止直接按猜测另建实现。

| 能力 | 复用方向 | 必须核验的缺口 |
|---|---|---|
| 一次保存/草稿/幂等 | 既有 Capture/Application/Repository 与成功回执 | request key 绑定、同键异文冲突、事务完成点、超时后结果查询与草稿持久化时机 |
| 自动有限 Context | 139 Resolver 与既有权限/有效期/预算门 | 自动选取是否已有入口；最终 packet 与各层预算是否一致；无获准输入时如何返回 |
| 有价值澄清 | 既有 Current State/Question/Feedback 链 | 单问题选择、问题身份、五种处置与沉默状态是否已有持久化；不能把全部回答当 Feedback |
| 记忆更新/纠正 | 139 Current State、Durable Memory、候选理解与历史 | 类型区分、确认动作、有效时间、supersedes 和依赖投影失效；不新增第二套 Memory |
| 后续建议可解释变化 | 140 Today/跨域 Focus/反馈 | 依据版本如何绑定建议；纠正后旧依据退出与无关投影保持一致 |
| SourcePort | 既有 Source/Artifact/授权消费门 | 是否已有可复用 SourceItem DTO、版本去重和撤权排除；未知不等于不存在 |
| 两个离线 Adapter | 既有 ModelPort 与离线测试 Adapter | 模型切换仅影响生成，资产/确认/反馈不得按模型隔离或重置 |
| UI 与基线 | 145 指定 commit 中 Settings/窄图标 Rail/Global AI | 继承文件清单、关键可达流程及凭据相关功能隔离；不运行真实凭据或 Provider |

## 4. 完整合同建议稿（需核验后由 PM 定稿）

### 唯一结果及边界

一个用户自然记录或回答必要澄清后，原始表达仅保存一次，系统使用获准且有效的来源自动形成有限上下文；建议能追溯当前理解及纠正原因；关闭重开、切换两个离线测试 Adapter 后个人资产和反馈一致。对话与两类合成来源在同一 Source/Memory/Context 链集成，整包实现、UI、测试、Evidence 和包内修正仍属于 P3-146。

准备期只写本任务文档。以下工程路径仅为待最终合同启用的建议：`/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/engineering/LIFEOS-P3-146/`；构建、夹具、全新合成 DB、App 运行与缓存仅在最终批准的 `/private/tmp/lifeos-p3-146-conversation-source-v1` 子目录中，启用前按 marker/所有权/非链接边界核验。本轮未探测或创建该临时根。

禁止 Pilot、任何真实个人 DB/文本/Vault/健康数据/Keychain/凭据；零网络、零 Provider/模型服务、零真实同步/录音/通知/后台采集；不修改历史候选、PM 账本、冻结、风险、Stage，不自动 git push。架构链保持 UI→Application→Domain/Capability→Ports→Adapters；UI 不直连 SQL/网络/凭据。

### 行为与验收建议

| AC | 可执行判据 | 正负与持久化验证 |
|---|---|---|
| 01 一次保存 | 一次操作生成一条原始记录和稳定回执，UI 只在成功回执后清除草稿 | 注入提交前失败、提交成功但回执丢失；重试不重复写；同键异 payload 失败且不改原文；重启继续同请求 |
| 02 草稿保留 | 保存失败仍可见原文，可继续编辑或重试；草稿与已保存记录身份分离 | 异常/刷新/重开不得把未保存内容展示为已成功；具体草稿落盘范围由合同明确 |
| 03 自动 Context | 只消费获准、有效、当前版本；所有层和最终 packet 有统一预算约束 | 空集、预算不足、过期、撤权、旧版本均结构化处理；失败前不持久化错误 packet/request；网络调用为零 |
| 04 澄清价值 | 每轮最多一个问题；缺口不影响建议则不问，已有有效来源可回答则不问 | 同一固定场景改变缺口是否影响行动/优先级；记录可审计触发原因，不依赖模型主观评分宣告通过 |
| 05 处置抑制 | answered/deferred/ignored/refused 与未响应分离，跨重启有效 | 建议以稳定问题身份和依据版本绑定处置：暂缓在明确到期前不再问，忽略/拒绝不因重启或换模型重问；重开规则须 PM 定稿；沉默不产生事实/确认 |
| 06 类型与确认 | 原文、当前状态、确认长期记忆、AI 候选、请求上下文可区分 | 明确长期保存使用一个清晰动作；普通回答不强制额外反馈；推断未经确认不得成为 Durable Memory；来源导入不等于用户确认 |
| 07 纠正 | 新纠正保留旧版本及关联，旧理解退出当前使用；仅重算受影响投影 | 同一证据链纠正前后对比，旧建议标明依据变化；无关投影不变；过期/归档/删除各自语义分明，不新增实际删除 |
| 08 合成来源 | Markdown 和健康模拟输入共用 SourcePort，记录来源/事件时间/导入时间/版本/权限状态 | 同 ID 同版本重复导入幂等；新版本可追溯；同版本异内容冲突失败；来源间 ID 不串；撤权后在所有消费门排除 |
| 09 连续性 | 两个离线 Adapter 与真实进程重启后，原始资产/确认/反馈/有效上下文语义一致 | A→重启→B→A；允许建议措辞不同，不允许丢失反馈、重问已拒问题或复活撤权来源 |
| 10 UI/基线 | 保存、失败草稿、澄清处置、纠正、来源依据和建议变化在 actual Tauri 可达；Settings/Rail/Global AI 既有行为不静默回退 | 固定源码/二进制/launch PID/目标窗口与关键截图绑定；不得用测试通过或旧截图替代真实关键操作 |

来源字段建议仅为语义草案：source_id、item_id、version、source_type、event_time（含时区）、ingested_at、provenance、授权/有效性引用、内容摘要绑定。正式字段名、Schema、Migration、IPC 均须先与既有合同对齐；关键变化作为精确 delta 交 PM，不在准备期创建代码。

健康模拟建议仅含非医疗示例，如步数计数与睡眠时长，必须保留单位、区间、来源、版本和重复记录规则；它们是候选夹具字段，尚非用户授权的真实采集字段。真实 iPhone 采集机制、字段许可、时间窗、传输机制、撤权与设备后台行为在本轮均未验证。可行性合同应列出需要证明的设备授权→数据取得→字段归一→传输→SourcePort 链，不宣称 HealthKit 已验证、持续同步已实现或真实健康接入已可用。本轮禁止联网，不做外部 API 可行性事实断言。

### 执行、Evidence、停止与完成

一个执行负责人先固定接口及基线谱系，继而在同一包中打通合成对话与 SourcePort，完成单元/集成/失败关闭/幂等/重启/Adapter 切换，再做定向 actual-App。不会先完成对话才开始来源合同设计，也不自行转派。

确定性测试入口留在任务工程根；每项结果绑定输入、预期、实际、日志与候选身份。CI 只跑合成确定性检查，GUI/真实能力不进入 CI。具体命令必须在源码核验后给出，不以猜测的 runner 名称填成可复跑入口。

L2 Evidence 包含正负路径、事务失败、重试、来源版本/授权排除、纠正、真实进程重启与双 Adapter 矩阵及关键操作截图。动态阶段边界使用正式 checkpoint 模板记录 contract/candidate/baseline 摘要、完成项、排除产物和 resume_from；GUI 暂不可得为 Paused — Resumable，恢复只补受影响阶段。marker 不符/链接/归属不明时不清理；只清理本任务拥有的精确根，先停止写入者。

最终 Pass：AC 全覆盖；P0/P1/Unknown/合同内 Not Implemented 均为 0；非阻断 P2 单列；不外推真实能力。独立评审不默认触发；若出现权限、凭据、删除、安全边界或关键 Schema/API 实质变化，先交 PM 判断风险与定向补读，准备建议不构成这些变更的授权。普通包内缺陷留在本任务 Closure Cycle；用户结果、真实目标、权限、核心语义或冻结合同实质变化才按治理处理新任务。

## 5. 本轮交付与 PM 所需决定

已完成：正式卡、根规则、回复模板、PM 最新状态/登记核对；固定缺失事实及本树身份；合同建议和接口待核验清单；阻塞已通知来源 PM 任务 `01a0290d-4255-7c52-8e62-6b888d2d678a`。

未完成：D-0651 全文、固定候选身份与接口核验、139/140/145 直接材料验证、最终完整可执行合同。未执行任何工程/测试/build/App，未接触禁止边界，未读取真实内容或凭据；不需要 Key。

主责检查点：输入核对部分完成，直接输入门未通过；PM 合同确认待办；独立评审未触发。没有工程 Pass/Independent Pass/PM Pass。

请 PM 校正 IN-01，并补齐 IN-02/03 固定输入与 IN-04/05 合同落点。收到校正后可在本准备会话继续只读核验并更新同一交付物；工程仍等待最终合同明确放行，不新建微任务。

## 6. 路径校正后的当前事实

PM 通过来源任务明确提供准确路径并更新同一正式卡，现卡 54 行全文补读；其余未变启动文件未重新全文读取。新增四文件均完整读取，无残留截断：

- `/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb/lifeos/architecture/自然对话与记忆治理增量说明.md`（121 行）。
- `/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-139_pm_final_review.md`（54 行）。
- `/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-140_pm_final_review.md`（62 行）。
- `/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb/lifeos/reviews/LIFEOS-P3-145_pm_review.md`（45 行）。

路径修正属于 PM 编排校正，不是候选缺陷。145 Review 截至 a55 窗口 delta，明确未终局通过；不能外推覆盖新 2bd2fb43 凭据实现。D-0651 内较早的工程 hash、等待145通过的路线草案已由当前卡/D-0652 的“允许146准备、145安全复核暂缓”更新，历史不修改。

固定候选的当前 HEAD 确为 `2bd2fb43792ae7de67bc764d8eed063f1ec22824`。代码核验全部使用 `git show <固定commit>:<精确路径>` / 限定路径 `git grep` / `git ls-tree`；未依据漂移的工作文件、未读取整个候选目录的 Evidence 或运行产物。下面路径均相对于该 commit 的 `lifeos/engineering/LIFEOS-P3-145/candidate/`，行号也是该不可变 blob 行号。没有执行、编译或复跑测试。

139 Review 确认历史 Durable Memory/State 分离、纠正谱系、L1/L2/L3、FTS/Top-K/预算以及 request receipt；140 Review 确认历史 0～1 问题、skip 降级、反馈失效/重算、0 durable promotion 和20 IPC。两者是历史合成验收事实，不保证145二进制包含相同行为。

### 6.1 实际接线与复用矩阵

| 能力 | 固定源码事实 | P3-146 应复用/补齐 |
|---|---|---|
| 编译入口 | `src/main.rs:3–8` 只声明 deepseek、runtime、secure_credentials 并调用 runtime::run；限定 main/runtime/build/Cargo 全文搜索没有 memory_context/today_intelligence 声明、include 或调用 | 两个历史文件是留存源件，不是当前二进制可调用能力；先在 Application/Repository 接线，并验证其实际进入编译与 IPC 链 |
| 历史 Memory 底座 | `src/runtime/memory_context.rs:7` 依赖父级 now/read/write/Error/Paths；57/73/89 为历史三种 DTO；195–232 有 durable_memories、current_state_events、receipt/snapshot/audit；269 起事务 mutation；300–312 保留 supersedes/superseded_by | 生命周期规则与算法可移植复用；当前父 runtime 无对应接口，不能只增加 mod 声明即称集成完成；为任务自有仓储适配，不另建 Memory 引擎 |
| 历史 Resolver | `memory_context.rs:425–495` 授权、L1/L2预算预留、L3 FTS/Top-K、最终预算与事务内 receipt；186–188 只接受单一固定来源引用，176 查询只允许 planning/focus/recovery | 复用过滤/预算顺序；扩展到经过校验的任务 SourceItem 引用和合成自然输入，不能把 source refs 任意字符串直接当授权 |
| 当前保存 | `runtime.rs:1657–1664` DTO 无幂等键/来源/时间/版本；742–813 新生成 ID、写 context_item 后另连接写 audit；1996–2039 capture 支持 store/revoke/correct | 保留 capture 入口名；增加严格版本化请求与请求回执，原文/投影/审计同事务；不能把同文本相等当幂等，用户两次主动相同表达可以是两条 |
| 当前草稿 | `ui/app.js:207–227` 在 await invoke 前清空 textarea 并 render；当前 state 中 drafts 是模型配置草稿 | 新增对话草稿生命周期，成功回执后清空，失败和关闭重开保留；不与 Settings draft 混用 |
| 当前理解与记忆 | `runtime.rs:564–568` context_item 按 item_type 区分数据、derivation 保存AI身份/来源/model；2307–2380 confirmed=true 才存长期记忆 | 可保留兼容响应与 UI；内部统一到139语义的 Memory/State，context_item 只作原始记录或兼容投影，不产生两个可独立修改的长期权威 |
| 当前纠正 | `runtime.rs:872–880` 先 retire 再 insert；883–912 按 refs 失效 derivation。ContextItem 627–636 无 replacement/version 字段 | 复用依赖失效选择规则，补原子纠正和持久替代关系；负测在新写失败时旧版本仍有效，不能先丢当前理解 |
| 当前本地组装 | `runtime.rs:993–1060` 授权/active/时效筛选、最多3项/480字符/120估算token，空集失败；`app.js:307–314` 需要手动组装 | 复用有限选择与逐次披露；本地自动准备由 Application 触发。新增历史 Resolver 的层次语义，不能只把按钮改成自动点击 |
| 同名发送入口 | `runtime.rs:2442–2519` resolve_request_context 接受 confirm_send；2481先 load_api_key_string，2483后才区分 real/synthetic | 不作为无凭据离线 Resolver。增加专门的本地操作分支或 Application 入口，须在凭据/Provider之前完成隔离；云端 confirm_send 原语义不得改变 |
| Today 与问题 | 当前 `runtime.rs:2041–2143` 是 person_today_projection，无 Question；历史 `today_intelligence.rs:65–147` 有 TodayRequest/Question，479–509 有 missing_health/skip | 复用 Today 的证据/降级/反馈算法；补稳定 question_id、缺口身份、依据版本、处置持久化和价值规则，不能用固定 scenario 字符串替代实际输入驱动 |
| 历史反馈 | `today_intelligence.rs:37–43` 有唯一幂等键；99–105 为五种建议反馈；611–628 缓存，631–667事务反馈，721–747调用 Resolver | 建议反馈与回答事实分离；拒绝建议不等于拒绝问题。复用事件机制并补 question target/type，不强制普通回答反馈 |
| Provider/Adapter | 当前入口无 SourcePort/ModelPort/ModelAdapter 接线；直接调用 deepseek。历史 today 的 model()（453）是固定合成规则函数 | 将推理接入同一 ModelPort 契约下两个纯进程内 Adapter；不是调用 Ollama/LM Studio，也不是切两项真实Provider配置 |
| 构建与旧根 | `build.rs:3–12,23–73` 固定145 engineering/review/real profile；`runtime.rs:15–22` 固定旧 marker；tools/run_phase_a_checks.mjs:12–24 初始化旧根并无筛选运行 cargo test | 不得直接运行旧 runner、原 build 或全量旧 tests；P3-146复制范围内编写新根绑定与安全测试入口，保留历史字节不动 |
| IPC/系统边界 | `runtime.rs:34–55,2582–2602` 恰好20 IPC；2146–2168的5个旧动作明确 unavailable；capabilities/main.json:6只有core:default | 保持20名称与现有安全拒绝；不能把 unavailable 动作泛化成新的任意命令入口；新增语义按精确DTO delta |

### 6.2 输入和实现缺口的归类

以上属于 P3-146 准备期查明的集成差距，不是独立评审，不为145重开风险或撤回历史Review。关键事实已回报PM。特别是“139/140历史已通过”与“145当前接线”必须在最终 baseline lineage matrix 分开。

该阶段曾缺少的 SourcePort 规范原件已由 PM 随后补齐，核验与最小 DTO 对齐见第10节。没有搜索历史 SourcePort/Spike 目录或旧临时根。

## 7. 建议正式合同中的精确 delta

以下为供 PM 一次定稿的整体建议，**不是已实施或已批准变化**；第4节 AC-01～10全部保留。新增字段的最终命名可机械对齐既有 SourcePort，语义不得缩减。若 PM 判断其中涉及关键 Schema/API/权限合同变化，应在工程前完成风险判断、定向补读与必要确认；不得因本文件称“L2建议”自动跳过。

| Delta | 明确修改建议 | 兼容/边界 |
|---|---|---|
| D146-01 请求身份 | capture_record 的新版本请求：request_id、conversation_id、turn_id、原始text、输入类型、来源引用；幂等以 task+operation+request_id 绑定完整payload与回执 | 保留v1受控操作的响应含义；不接受未知字段；同键异文返回冲突；成功回执丢失后的重试返回原ID；原文保持输入字节，trim仅作空白校验/派生 |
| D146-02 草稿与原子提交 | task-local draft 持久化，并在保存事务中写原始记录、类型投影、审计、回执；ack后标草稿已提交 | 一个草稿ID只对应一个最终请求；重新编辑产生新修订；启动先恢复未提交草稿；回执错误不能误报已提交记录未保存 |
| D146-03 唯一类型权威 | 将历史139生命周期接到单一 Repository：原始表达保留在记录层，Durable Memory/Current State独立类型，AI保持derivation；145 UI兼容项为可重建投影 | 不双写两个可独立编辑的Memory真源；仅新合成空库初始化，不迁移真实DB；保留确认、有效时间、generation和替代关系 |
| D146-04 本地上下文操作 | 复用 assemble_global_ai_context 增加严格带版本的 local_prepare，返回request/context refs、included/excluded理由、预算和generation；自动调用后呈现结果与来源 | 不自动调用confirm_send；不创建云端确认/receipt假象；现有云端披露/修订/移除/确认消费路径保留语义，但本任务不可发起 |
| D146-05 澄清事件 | 增加问题稳定身份 purpose+missing_field+context+validity_window；持久状态 pending/answered/deferred/ignored/refused，沉默只保留pending；答案的request_id绑定原始记录和正确类型 | 复用反馈事件基础但target_type分离；不把 answered 当确认所有AI推断；不新增独立Question数据库或推理引擎 |
| D146-06 纠正 | expected_generation、replacement_id、supersedes持久绑定；先全验证，再单事务替代/审计/受影响失效 | 保留旧原文和过去有效区间；本轮无物理删除入口。无关projection generation/内容保持不变 |
| D146-07 Source映射 | 一个SourcePort，两种纯合成Adapter；SourceItem具有来源/原生item身份/版本、观测与导入时间、内容类型、引用与授权generation；同源同版本重复无新增 | source导入默认不确认长期记忆；撤权仅以任务内合成授权事件验证既有排除语义，不扩大真实权限；具体DTO须与规范原件对齐 |
| D146-08 两个测试Adapter | OfflineA与OfflineB只接收相同有限ContextPacket，输出带版本refs和model_id的候选，措辞允许不同；使用相同Repository | 调用计数区分本地测试Adapter与网络/Provider/Keychain；后3者必须0。不得把设置里的合成本地目录标识当已运行模型 |
| D146-09 任务根与测试边界 | 新任务仅一个固定合成根和P3-146 marker；新增仅本地的编译profile，拒绝旧根/任意覆盖/真实profile；旧凭据生产源保留为受保护输入 | 不能以“synthetic”字符串保证不读Keychain；在路由进入前注入 NoNetwork/NoCredential 实现，触达即失败；是否以编译特性隔离由PM定稿，不改变145凭据语义 |
| D146-10 CI接入 | 交付 task-local runner、显式测试allowlist、预检根约束与结构化输出；PM处理全局注册或给出额外精确文件授权 | 不直接运行旧全量cargo test；其中3255/3366/3401等测试涉及真实系统凭据接口，必须排除；禁止复制/执行旧清理工具 |

### 建议固定的交互和合成边界

- 保留 Today/Me/Contexts/Memory 窄图标 Rail、Settings 辅助入口、Global AI；不整体重设计。明确“保存并记住这条长期偏好”动作本身表达对象级确认，可映射confirmed=true，不再显示同义勾选。含糊表达先保存原文/候选。
- 保存/回答成功后自动本地准备 Context；保存成功而准备失败时仍显示“记录已保存，上下文暂不可用”，不把两者合成一个失败回执。重试Context不得重复保存原文。
- 拟定每次用户保存/回答/主动打开Today为一个评估触发，最多一个问题；已有有效证据填满字段或两个选项对建议无影响则不问。无后台计时器、通知或循环追问。
- 建议暂缓必须选明确的时间（夹具时钟可控）；忽略/拒绝在相同缺口及有效窗口内不再问。仅依据过期或Context实质改变时重新评估，展示原因；单纯重启、模型切换、重新措辞不形成新缺口。拒绝不使未知事实变成否定。
- 保留200字符的单次合成表达上限作为初版验收边界；单场景使用至多3条Work、3条Health和1条确认长期记忆，纠正历史不计活跃额度。跨多场景使用本任务根内独立全新夹具，不能静默扩大145真实额度。Source原文与memory/context预算分开计；完整原文不可为满足context预算而截断。
- 原始Source样例限定任务工程目录自有的两份短Markdown和两份模拟健康JSON，禁止文件选择器/任意路径参数；Adapter仅消费Application传入的受控内容和虚拟来源身份，不跟随Markdown链接、图片或嵌入资源。导入大小/格式错误写前拒绝。
- 健康合成初版建议仅使用睡眠时长/时间区间和显式模拟的观察值；不得从iPhone数据推定energy、pain、training_load或available_time，缺失字段保持未知。由本地规则映射睡眠区间时保留原始量与映射版本，不把算法映射当用户确认。

### 健康采集可行性合同（不验证真实机制）

真实候选链为设备端用户授权取得限定字段→明确时间窗/单位/时区→一次导出或明确传输→SourcePort导入→来源/去重/撤权过滤。每一步须未来精确授权及验证；快捷指令、局域网或原生采集目前只是候选机制，不选定为已可用能力。本轮只能证明给定模拟负载的解析、异常/缺字段/重复/新版本/撤权行为；未验证设备可用字段、授权粒度、后台频率、补传、断连恢复、传输安全或持续同步。UI须标“合成来源演练/一次导入”，不能标“iPhone健康已连接”。无需本轮用户提供个人健康样本。

## 8. 建议执行顺序、验证入口与完成判定

这些是同一结果任务的内部阶段，不拆任务：

1. PM定稿固定SourcePort输入、D146 delta、写入与安全构建边界；执行侧在任务分支记录正向源文件清单、输入hash、基线语义和读取边界。
2. 先固定共享DTO/Repository/Source映射和离线ModelPort，证明139/140代码真正可调用；在新合成根打通对话+来源的最薄垂直流程。不能用两个断开的demo作为合成集成。
3. 同一事务层完成保存/草稿/幂等、类型/纠正、问题处置与有限Context；两个Adapter和Source撤权均走这条链。
4. 运行L2确定性测试与定向actual-App；包内关闭缺口后一次提交完整Evidence/复跑入口。不得为通过而降低已列AC或以历史测试计数替代本轮执行。

计划的本任务入口为 `candidate/tools/run_p3_146_checks.mjs`（尚未创建），职责固定为根与marker预检、format、locked/offline build、**只运行已审查allowlist**、对话/Source/Adapter结构化矩阵、基线回归及结果汇总。测试和构建环境的CARGO_TARGET_DIR/TMPDIR全部派生到唯一任务临时根；Node/Rust工具链从现有本机路径只读发现，不联网安装。原145 runner的 `cargo test --locked --offline -- --test-threads=1` 是无筛选旧测试运行，不能照搬为146安全命令。生成后的入口命令和允许测试名必须进入正式Evidence，准备文档不伪称可立即运行。

额外关键断言：

| 矩阵 | 必须观察的事实 |
|---|---|
| 保存/故障 | 提交前失败无新记录/审计；提交后ack丢失重试回原ID；同键异文拒绝；保存成功而Context失败不重复原文；关闭重开恢复草稿/回执 |
| 澄清/来源 | 同缺口无来源问1条，有获准答案问0条；无关来源不压制必要问题；过期/撤权答案不复活；五处置加沉默逐项重启；忽略/拒绝与建议反馈不串 |
| 类型/纠正 | 用户明确长期意图与AI推断分开；普通回答无强制反馈；纠正失败回滚，成功仅失效相关refs；旧历史存在但不进入新Context |
| 预算 | 所有必需层预留和最终packet一致；预算不足写前拒绝；raw source无限加载路径不可达；估算算法版本可复算；维持历史32/39/38边界语义测试，不承诺新refs仍恰好39 |
| Source | 同版本去重、新版本替代、乱序版本拒绝/明确处理、版本碰撞失败、时间/单位异常、来源身份不串、撤权generation阻断旧缓存 |
| 连续性 | A生成→用户反馈→进程退出→B读取同资产→A读取；比对IDs/版本/授权/有效Context，不比较回答逐字一致 |
| 安全基线 | UI无SQL/网络/凭据；20 IPC名/拒绝语义可核对；Settings/Rail/Global AI无回退；全流程NoNetwork/NoCredential触达为0，不能只硬编码counter=0 |
| actual-App | 同候选launch PID与目标窗口；主保存、失败草稿、问题回答/暂缓/拒绝、来源依据、纠正后建议及关闭重开可达；宽/窄两档建议1280×1024及700×760，记录真实窗口几何，不改变系统缩放 |

正式动态执行读取 `lifeos/templates/EXECUTION_CHECKPOINT_TEMPLATE.json`，在preflight/build_test/data_lifecycle/app_launch/native_window_binding/visual_capture/cleanup/manifest记录检查点。本轮无动态执行，所以没有创建假checkpoint。GUI故障按Paused — Resumable处理，不作候选失败；错误截图仅排除并补对应步骤。

Pass公式沿用正式卡：P0/P1/Unknown/合同内Not Implemented=0，AC逐项有本轮证据，P2逐项披露；L2不另建Frozen ABF或冻结Manifest。工程成功不等于PM验收；不改变145安全Delta/Phase C、风险、冻结或Stage。

## 9. 当前交付结论与 PM 决策项

准备期已完成：最小启动包与四项校正直接输入；指定commit确认；核心接口、UI、构建/测试入口的定向静态核验；复用矩阵、集成缺口、整体合同delta和验收建议。按范围未启动工程、测试、App或实际来源/模型；没有修改d510、历史Review或PM账本；无push。适合由本专项继续同一工程线，但只有PM正式卡放行后才执行。

需 PM 定稿：

1. SourcePort 规范输入已补齐并在第10节核对；采纳与其一致的最小 DTO 建议，不将规范可选字段误当必填。
2. 明确采纳139/140“语义复用+重新接线”的范围，接受其在145当前入口未接线的事实，不能仅以20 IPC名称不变当完整继承。
3. 对D146-01～10中的DTO/Schema、单一权威、NoCredential/NoNetwork构建隔离作精确风险判断与必要定向补读；决定L2是否仍成立/是否触发独立评审。不得偷渡凭据安全变更或真实授权。
4. 明确本任务工程写根、任务分支、临时root/marker、CI注册责任、草稿保存/问题冷却/夹具额度等建议值；不自动合并整个145高风险祖先。

这四项属于同一准备合同定稿，不建议新建微任务。不需要Key、真实DB或健康/Vault样本。当前无工程Pass/独立Pass/PM Pass；报告自检不替代最终合同判断。

## 10. 最终补齐：SourcePort、最小持久化 delta 与一次定稿建议

### 10.1 固定规范核验

已按 PM 新增精确输入读取 `2bd2fb43792ae7de67bc764d8eed063f1ec22824:lifeos/architecture/LifeOS架构基线V1.0.md`，总205行，定向读取60–140行覆盖SourcePort及所属架构/Repository/Search/Model/Adapter边界。没有假设PM工作树存在同文件。原任务卡本次新增SourcePort段已续读；其余未变部分复用完整读取结果。

规范第100–103行：Source负责连接状态、发现、读取、变化同步，SourceItem“可包含”候选字段；Adapter→SourceItem→Ingestion Application→Authorization→Domain→Repository，默认只读。第90–98行要求Repository不暴露SQL/handle、Application定义事务、搜索消费重新核对授权/来源/版本/tombstone/generation。第105–108行要求Model仅推理、保留调用元数据、不直接操作Repository。第71行明确目标TypeScript Application/Core、Rust负责Host/安全边界。

因此：P3-146只提供合成read/discover能力；连接状态写“synthetic_fixture”，变化由显式加载新版本演练，sync/外部write返回明确unsupported，不宣称已连接设备。新Application/Ports边界须按V1.0分离，不能把UI直接SQL或新增全部核心逻辑塞进Rust作为默认方案。既有Rust Memory算法允许通过适配复用，不借本任务全仓迁移；新增Application协调优先放TypeScript，Rust仅承接受控仓储/IPC。具体适配方式需PM确认，但不改变V1.0。

### 10.2 最小 DTO 建议（全部为拟新增的 v2，不伪称现有接口）

| DTO | 必需字段 | 可选字段/约束 |
|---|---|---|
| SourceItemV2 | sourceId、externalId、sourceType（synthetic_markdown/synthetic_health）、version（正整数）、content、mimeType | title、createdAt、updatedAt、parentRef、metadata可选；本轮只接受内联content，contentRef不开放；sourceId来自任务注册表，不接受任意路径；contentHash由Ingestion计算，不信任客户端声明 |
| IngestionEnvelopeV2 | requestId、SourceItemV2、authorizationRef、observedAt、validUntil或明确无期限原因 | ingestedAt由可信本地Clock赋值；授权由Repository实际核验；导入不能提供confirmed=true；version相同但hash不同拒绝；版本倒退拒绝，不覆盖当前 |
| ConversationSaveV2 | requestId、conversationId、turnId、text、intent（record/answer/remember）、observedAt | answer必须questionId；remember必须明确statement/scope与当前用户动作confirmation；普通record/answer不得携带伪造确认；validUntil为临时State必填；sourceRef由Ingestion生成 |
| QuestionDecisionV2 | requestId、questionId、expectedGeneration、decision（answer/defer/ignore/refuse） | answer引用同事务保存的turnId；defer必须resumeAt；ignore/refuse禁止answerText；无响应不调用该mutation。建议通过严格版本化的反馈入口区分targetType=question与原understanding，不共用语义 |
| LocalPrepareV2 | requestId、conversationId、purpose、expectedGeneration、budget | removedRefs可选且仅请求范围；budget由合同上限约束；返回contextPacketId/included/excluded及理由/usedBudget/generation；错误不生成云端确认 |
| OfflineModelCallV2 | requestId、modelId（OfflineA/OfflineB）、contextPacketId、inputRefs | 返回outputId、model/provider元数据、开始/结束时间、usage及候选；Adapter不得传入DB/path或授予执行权限；失败可重试但不重新写原始输入 |

协议落点建议：capture_record处理ConversationSaveV2及合成Source导入的严格tagged union；assemble_global_ai_context处理LocalPrepareV2；decide_understanding_feedback区分原v1理解反馈与v2 QuestionDecision；resolve_request_context保留v1 confirm_send并新增明确的offline_generate分支，必须在锁设置/凭据/确认消费前分流；get_today读取统一当前投影。仍20个IPC，不用五个unavailable命令扩展任意执行能力。此为精确API增量，是否属于关键合同变化由PM裁决，不能因IPC数量不变就宣称API未变。

### 10.3 最小持久化建议与事务

仅P3-146全新合成库，不修改真实/145数据库，不运行任何旧库migration。建议在139/140已有语义上作以下增量；具体SQL可在正式授权后编写，本轮未创建Schema文件：

| 存储增量 | 最小语义与唯一约束 |
|---|---|
| 原始记录来源列/来源版本实体 | raw_id、source_id、external_id、version、content_hash、raw_text、observed_at、ingested_at、valid_until、authorization_ref、generation、supersedes；UNIQUE(source_id,external_id,version)；用户原文和来源原文不可被派生摘要覆盖 |
| 请求回执实体 | request_id主键、operation、payload_digest、result_ref、committed_at；与原始记录/类型投影/审计同一事务提交；重复相同请求读回结果，异payload冲突 |
| 草稿实体 | draft_id主键、conversation_id、turn_id、revision、text、status、request_id；成功事务标committed，UI确认后清空；未提交草稿跨重启可恢复，不作为当前事实消费 |
| 问题处置事件 | question_id、purpose/missing_field/context/window组成稳定身份、generation、decision、resume_at、answer_ref、basis_refs、observed_at；事件保留历史、最新状态可重建；请求回执承担幂等 |
| 既有Memory/State/derivation增量 | 复用source_refs/generation/validity/supersedes；依据引用绑定source版本与授权generation；不另建平行Memory权威；兼容context_item视图只读派生 |

必须维护三种事务：保存原文+派生状态+审计+回执；纠正旧新版本+受影响失效+审计+回执；问题回答原文+State/候选+问题状态+审计+回执。Context/model后续失败不回滚已经明确成功的原文保存，且不误报保存失败。所有SQL由Storage Adapter执行，Application定义事务意图，不向UI/Model传连接或表名。

不将所有SourcePort候选字段强制必填。健康时间区间/单位放受限metadata；未知观测时间不能伪填为导入时间，缺少必需时间的健康State不进入当前建议，但可保留为未解析合成原始来源并说明原因。原始来源仍不是永久保留承诺，真实保留策略不在本轮启用。

### 10.4 最终待 PM 的一次决定

建议PM将第4节AC、第6节实际谱系、第7～8节范围/阶段及本节最小DTO/存储方案合并成**一份P3-146最终Task Contract**，明确标出API/Schema与离线编译隔离增量。单一负责人、任务自有分支与写根、零真实/网络/凭据、20 IPC及既有基线不回退继续保持。CI全局注册由PM负责，执行侧仅交付task-local检查入口及注册建议，除非正式卡另列可写文件。

建议状态：Preparation Completed / Awaiting PM Contract Decision；工程仍Not Started。所有固定输入已定位，剩余待决定项不是输入Blocked或候选缺陷。若PM判增量属于关键Schema/API或安全边界变化，应补正式定向阅读与适用独立关卡再放行；本准备阶段没有自行接受风险或改变权限。

最终报告没有宣告动态能力通过：测试、实际App、合成Source/Adapter及新DTO均为待工程完成的合同内容。145仍凭据工程完成/安全Delta暂缓/真实Gate暂停，139/140历史验收保持原边界。没有向用户索取Key、个人数据或真实来源。
