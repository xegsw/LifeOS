# P3-159 统一主动引擎实施记录

状态：In Progress，A 确定性证据已整理，等待 PM 门槛核对；B 实际请求 0，C 未启动。D-0675 合同内实施继续，不是最终交付或 PM Pass。独立评审为 User Exception / Paused。以下分节按历史增量保留，当前结果以末节为准。

## 已实现及已验证

完整继承 182 文件的 D0674 基线，快照提交 `46829c74eeb83c270a3258949c5d27db5bdea296`，逐文件身份保持一致。现有 Shell、原 14 个 Tauri command、ModelPort、Provider/凭据、原存储与行动事务保留。

候选增加 Host 事件合并、相关有界上下文、结构化判断与自然回应候选、推迟/拒绝/纠正、当前限制、持久预算、前台调度以及 Today/对话/设置接线。混合行动的附带反馈由原 v8 行动事务原子提交；提交前重新核对范围、资料版本与模型配置。已有源更新通过提交游标接入，不扫描真实原目录。

21 项完整离线回归入口已在前一候选通过（构建、Rust、IPC、设置、来源、错误恢复及 UI 等），新增修改正在重跑。新增测试覆盖资料变化阻止关联行动与反馈、同轮限制加建议、无关项目不继承行动关联，以及新用途 1 MiB 上限不扩大旧聊天解析上限。该计数仅表示测试入口，不能代替 24 条合同验收。

## 实际 App 检查与包内修复

第一次本任务离线完整 App 已直接启动并绑定 PID 37571、精确二进制和合成窗口。Today 空状态和合成未联网标识可见。设置检查发现主动帮助区继承了横向 flex，文字挤成窄列；轮询无变化仍重建 DOM，导致元素标识失效。上述错误截图不作正视觉 Evidence。已正常退出该实例，正在修复纵向布局和无变化不重渲染，然后重新构建复验。

用户截图的 `dto_rejected` 表示本地请求协议拒绝且草稿保留；尚无证据唯一定位当时哪个请求字段，不宣称该历史现象已闭环。

## 剩余验收

- A：修复后的实际设置/焦点/回应/窄窗口验证；每个必要写边界的故障、竞态和兼容性矩阵仍须完成。
- B：同完整 Host 的真实模型开发场景和固定候选后的 PM 未见样本未执行。实际 POST 0，不能宣称自然语义已通过。
- C：A/B 门槛后同身份真实包接入、用户一次启用用途、真实推迟重启和实际到期、用户最终验收均未开始。
- 非交付状态：不称 P3-158 Complete，不改写 P3-157 真实失败，不关闭风险/冻结/Stage，不合并远端主线。

## 证据入口

工程根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-159/`。

- `checkpoint.json`：恢复点与阶段边界。
- `evidence/offline-verification.json`：当前完整离线运行及源码身份；以 exitCode 与 sourceAfter 为准。
- `evidence/A-run-*/`：每次运行的保留日志，失败不覆盖。
- `evidence/A-native-attempt-1.json`：首轮实际 App 身份、视觉缺口与正常退出事实。
- `tools/verify_proactive.py --offline`：固定离线复跑入口。

主责为工程/数据/AI 信任/体验接线；L3 执行侧自检持续进行，PM 验收与用户真实验收待完成。当前无新增范围决策请求；本报告记录工程进度，不替代最终五项用户结果说明。

## 第二轮实际界面复验

首轮设置布局与空轮询重渲染已修正。第二个同源离线 App（PID 38248，binary SHA256 `86d46e7d2730cdc2d1bb5e3ab2f5706a61b1af66810537b6cafdfedb67a4ba04`）实际显示纵向设置，常规与窄窗口均可阅读；范围勾选、启用、关闭已通过 UI 操作，关闭后保留 1 次合成失败预留计数。已正常退出，未访问真实内容或凭据。完整 21 项回归再次通过；随后新增凭据不可用后的用途暂停与明确恢复提示，影响项正复验。第二轮记录见 `evidence/A-native-attempt-2.json`。主动候选/自然回应视觉和完整 A 矩阵仍未完成。

## 2026-09-12 后续离线增量

第四轮实际合成 App（PID 40504）展示单条主动建议，输入“先讨论一下”得到讨论回应。仅本任务合成库核对 Action event 0、proactive feedback 1；使用明确标记的离线模型 fixture，不是自然语义模型验证。发现成功后输入 DOM 未清空、对话外重复回应，已修正待最新 App 复验。原生本地日/时区/DST 与时钟回拨预算测试已通过，GUI 合成时钟文件正常退出后精确删除。

D-0676 公共 interaction-v1 的 Host canonical turnId 与旧 UUID 对应、同一键盘/主动回应入口、幂等提交和最终 AssistantTurn 投影已接入离线模式。22 项前一完整候选回归全部通过；当前增加旧入口修正与语音 A2 后执行 23 项完整回归。不能将前一结果覆盖当前未完成的完整检查。

PM 指出的两个旧 UI 入口已对账：Apple 测试导出漂移到 SourcesController，实际入口另有运行中重入和失败文件身份缺陷，已同范围修正并映射等效断言。健康原始 kind/modelEligible=false 不能因 caller status/source spoof 获准进入模型，core 和 Host allowed 同时补硬过滤；合法已授权 projection/用户自述仍保留。依据 D-0650、D-0675 合同47/153/159行，原健康功能与主动云端排除分开。导入/健康 18 tests、源恢复及 Host 新边界定向通过；精确计数以保留日志为准。

固定 voice A2 commit f5a64094943c72701625f77f74c2064d81a1745d 的14源码 blob逐一复算后接入，未复制旧182基底或活跃候选。同源 Rust模块和不可用设置/Consumer适配器已注册；现有 sources/requests 实现 BudgetStore 持久 CAS，缺账/坏账/重启/重复/冲突拒绝经过测试。两个音频状态/control IPC只提供 unavailable/安全关闭语义，enable拒绝。未接原生设备、未初始化用途、未发模型。语音 final/session/segment durable binding、Host speech registry、联合回执及声学/KWS仍待完成；技术部分通过不等于 A Pass。

## 当前增量核对（2026-09-12）

前述首轮布局和回应缺口已有后继 Evidence：attempt5 验证成功后输入清空、Global AI 单次反馈和不可用语音设置；attempt6 验证 Today 恢复后只显示一次回应。两个精确合成实例均正常退出。新增加的“在对话中继续”转回原对话预览，保留原文且不自动确认发送，其实际 UI 路径仍待补查。

当前 23 项完整离线回归已于 11:12 UTC 全部通过，包含 C 同库对话/行动分支、语音 final 持久绑定、12 个额外写边界故障与完整旧能力回归。此后又补 C 历史缓存投影拒绝及主动控制历史查询筛选，正在重跑同一入口；不能把前一个源码身份的通过套给新增代码。最新 online-synthetic 与 controlled-real 均仅作离线编译检查成功，未运行网络模式。

C 按 PM 已明确的既有预算解释，实现 v7/v8 共用 operation-budget-C 累计最多8次；缺账/坏账拒绝，不初始化为0，失败/未知不退款。合成正例覆盖普通回答与原 Action 事务，反例覆盖查询/second阶段/合成模式伪造；共享最后额度并发测试只允许一个预留成功。未读取真实计数，真实剩余额度 Unknown，C 未启动。

语音固定 v2 commit 0d8a53453954a672f91635214a3e539a33e844ac 的17文件和 worker closure 93c98bb0826b98778dbf4b3daa9ccf102e61de69 均按指定 blob/hash 接入。Host final 只接受已登记 session/ASR/segment、当前 generation 和相同文本摘要；重启关闭活动会话，已落地回执仍能读取。当前为离线合同 fake，未接原生采集或 MiMo，speech registry/联合声学仍未完成，不宣称语音 A3 Pass，也不以语音等待暂停159。

## A 当前证据收口

2026-09-12 11:34 UTC，完整23个离线入口通过，Rust 290通过、0失败。运行期间220文件候选不变，原182文件基线完整保留；三种模式完整构建均通过。最终源码的四项语义 mutation 在隔离副本中均被断言检出；较早一次缺少测试 fixture 的编译失败已排除，不作正证据。入口为 evidence/A-acceptance-matrix.json、offline-verification.json、A-mode-build-*.json 及最新 A-mutations-*/results.json。这些是确定性工程结果，不是 B/C 自然语义验收。

实际离线 attempt7（PID48920）保留新话题原文，转回原有明确发送预览；未自动发送普通请求，合成 Action event 仍为0。精确实例正常退出，场景时钟已移除。真正关闭和重开 Store 的测试覆盖到期前已完成、取消、依据过期、对话撤权，以及仍有效时进入重新判断的分支。行动主体曾缺少 conversation 当前授权复核，现已修正，并由对应 mutation 验证测试可检出该遗漏。

PM 的 B_action_budget_interpretation 保留 D0670 原 v8 累计模型16/8、回合及工具8/4分池，缺历史拒绝；用户仍须亲自确认每次精确普通预览。新用途96/48与旧用途预留同时受外层144/每日48限制，不转移用途额度。最后额度并发、事务回滚、本地无 POST 不虚计均已测试；16项开发语义场景已在执行前记录。

B 完整未签名包位于 /private/tmp/lifeos-p3-159-unified-proactive-v1/build/B-20260912T113603667076/LifeOS Online Synthetic.app，unsigned binary 为 e19489c0627db65ad8e7c32b25920d3ccc8639f135f3817adbe19911ebbb7087。尚未签名或启动，B 实际 POST 仍为0，C 未启动。Voice A3 保持部分实现且禁用，未启用麦克风、音频、MiMo 或真实语音权限。


## B 凭据读取 Closure 与恢复入口（当前状态）

前三次 B 实际启动的生产分析预留累计为 **3**，实际模型 POST 为 **0**。首轮读取卡在现有系统钥匙串调用，正常退出；修正为非交互读取且不持 Store/业务锁等待后，第二轮约11毫秒、第三轮约8毫秒返回 `credential_unavailable`，UI可操作，没有自动重试。第三轮未命中新增的 -25308 分类，不能据此认定钥匙串锁定、ACL或系统交互要求。快速返回不代表后台稳定读取通过。

三次原始启动记录及 B-native-quit-1/2/3.json 均保留，精确 PID 已正常退出，B 场景时钟已移除。旧预留不退款，未重置任何计数。B 的模型语义仍未执行，C 未启动；用户截图的历史 dto_rejected 仍不能唯一定位，不宣称闭环。

PM 已给出 credential_recovery_interpretation.md，允许当前同身份完整 B App 的现有设置进行用户亲自触发的一次交互式只读检查。正在实现并离线验证：设置按钮只打开原生菜单，只有原生用户菜单事件可开始单次检查；前端不能用 authorized/reference/start 直接读取。检查仅绑定已选固定配置，原有进程交互策略不强开，临时 Key 不进入 UI、缓存、日志或后续模型请求；零 POST、零预留、零配置修改，成功仍保持主动暂停。取消、窗口关闭、60秒超时、profile/grant 变化后丢弃迟到结果。检查只报告固定阶段和数字 OSStatus，不输出系统错误描述或账户/路径。

凭据依赖的 B 阶段为 Paused — Resumable；其他离线实施继续。准备完成前不再次进行真实读取，也不要求用户盲目解锁。恢复点见 checkpoint.json；剩余条件为用户经明确设置入口完成一次检查，再依结果确定既有恢复流程。该入口准备不等于 PM Pass / B Pass / C 开放。


## 只读恢复入口已准备（最新）

当前221文件源码的完整23入口回归通过（Rust 302），运行期间源码身份不变；online-synthetic / controlled-real 完整构建通过。新增8项Rust检查、3项UI检查通过，单次原生身份绕过与迟到profile校验绕过两项mutation均被断言检出。先前一次UI产物更新导致sourceStable=false的运行已排除；其测试虽通过，不作为固定源码通过凭证。

恢复包 `/private/tmp/lifeos-p3-159-unified-proactive-v1/build/B-20260912T121528193077/LifeOS Online Synthetic.app` 已沿原身份签名，strict/deep验证通过；签名后binary SHA256 `6c117619d7c80c3173c62de81f9b5e287c94fde98f00c87c1d22faf62d12bc5a`。直接启动PID 57492，exact app AX与截图确认“设置 → 模型设置 → 主动帮助 → 只读检查凭据…”可见；只进行了导航与滚动，没有点击检查按钮或原生菜单，没有新增凭据读取。App留在该入口供用户操作，今日判断仍3次且主动帮助暂停。

状态为 B 凭据依赖阶段 Paused — Resumable；恢复需用户点击只读入口并选择原生“检查一次”，OS提示也仅由用户处理。成功也不自动恢复后台用途。检查入口无模型端口/预算/配置写调用，前端只有打开原生菜单、状态和取消，没有start或任意引用入口。工程/数据/AI信任/体验执行自检已覆盖该增量，PM验收和B/C真实语义关卡仍未通过；独立评审User Exception / Paused。精确源码差异、测试、使用计数和限制见 `evidence/B-credential-recovery-closure.json`；禁止边界接触为No。


## 用户实际入口失败及同范围修正（优先于前述准备状态）

用户操作后显示“检查入口暂不可用，未自动重试”，实际入口未走通。旧UI吞掉具体错误，因此不能唯一追溯此次运行分支；按钮可见证据不能代表入口可用。已在原签名合成App中观察该失败状态并正常退出，记录 B-recovery-entry-failure.json，不要求用户重复尝试。

确定的代码缺陷是恢复 binding 使用底层 provider_store::settings 的原始 enabled/modelId，漏掉 settings_lifecycle 中的生效选择/启用。修正同时绑定 effective provider_view 和 raw profile，前者负责模型/授权/设置版本，后者负责精确凭据版本。新增真实Store合成回归证明 raw.enabled=false 而 effective.enabled=true 的正常配置应允许进入菜单；关闭生效模型后必须拒绝。前端只显示允许清单中的固定诊断，不接收潜在账户/路径/Key详情。

按用户“设置太复杂”反馈同步简化主动帮助区：默认开关、实际状态、关注范围摘要及单一凭据处理入口；范围、独立来源正文许可与简短启用披露按需展开，预算/模型/排除说明/固定诊断/提醒决定放折叠详情。关闭沿已保存授权集，不保存未确认范围；不修改或删除合成场景来美化显示。

## 修正后的同一完整包（最新）

最终固定221文件源码通过23项完整离线入口和16项主动UI测试，Rust精确计数见 B-recovery-compact-closure.json，三模式完整构建通过。三项凭据授权/迟到绑定/原始配置误用 mutation 均被断言检出。实际A包验证网页处理按钮打开原生菜单，未选之前读取0，取消不读取，原生选择只经 SyntheticKeyPort 成功1次且仍暂停；一键关闭、关闭跨重启、开启先展示许可、范围与来源独立说明均成立。最后将 Store 等待移至工作线程后，最终A PID59557再次实际走通菜单及假凭据完成路径，正常退出，专用暂停fixture逐项核对后清理。未触及真实钥匙串。

当前签名在线合成完整App：`/private/tmp/lifeos-p3-159-unified-proactive-v1/build/B-20260912T123713279683/LifeOS Online Synthetic.app`；signed SHA256 `075f3bdfe2394c1b0eaffb8b43bcdb949baa785c235804dbeddb25bb57cb6aeb`，direct PID59580，strict/deep签名通过。已打开设置→模型设置，默认只显示开关、状态、关注范围2项/调整、处理凭据问题及折叠详情。B的资料和权限未为视觉删改；生产预留3、网络预算行仍无/POST0再次只读核对。

用户入口为“处理凭据问题…”后选择原生“检查一次”。Agent没有点击B入口或执行真实凭据读取，此步骤仍需用户亲自完成。平台错误原因及稳定后台读取仍Unknown，B语义与C未过；独立评审例外、风险与Stage不变。坏入口事实保留于 B-recovery-entry-failure.json，旧按钮可见结论不作为入口通过。源码差异、动态Evidence及计数见 B-recovery-compact-closure.json 和对应Manifest；PM与真实体验最终验收待完成。


## 用户手动检查成功与当前策略状态（后继增量）

用户截图和精确PID59580的合成App AX确认：手动检查finished/ok，当前进程手动读取1次。随后非内容持久收据显示一次独立 proactive_policy 保存/恢复，expectedRevision3→revision/generation4、enabled=true；本代pauseReason为空，旧gen1/2/3失败仍保留。不能从收据推断具体按钮，但可确认当前已解除本代暂停。生产预留3、POST0，不能外推后台凭据成功或B语义通过。

矛盾源于历史 credentialCheckText 成功分支硬编码“主动帮助仍暂停”，而顶部读取当前Host状态。现将详情仅作为那次手动检查的结果，当前开启/关闭/暂停及恢复入口继续唯一依据Host policy/pauseReason；成功检查仍不自动修改策略。新增恢复/再次暂停/关闭组合测试，用户无需再次手动检查。精确事实见 evidence/B-user-check-success-state.json。PM允许按原B合同继续一次受控非交互验证，失败/未知停止该项重试，不增加C或语音权限。


## 单次受控后台验证结果（当前恢复点）

历史检查文案修正通过完整23入口回归、17项主动UI测试，online-synthetic与controlled-real构建通过。新B完整包沿原身份签名，strict/deep验证通过；直接PID60742绑定精确合成App窗口，未再点击交互凭据检查或保存策略。

继承第4版开启策略、原有合成授权与累计预留3次后，只执行一次编译隔离场景时钟触发。后台读取约10毫秒返回credential_unavailable，生产预留变为4、回应0、B网络预算行仍不存在、实际POST0。界面显示“已暂停，现有凭据暂不可用”，详情判断4次，与持久状态一致。手动检查成功仍是历史事实，不能外推到后台。后台收据未记录具体OSStatus/阶段，不能断言钥匙串锁定或ACL原因。

已停止重试并正常退出精确PID60742，核验进程消失，逐值核对后移除本次B场景时钟。没有退款、改策略、重置预算、启动C或启用音频。B01停在模型POST前，模型语义仍Not Executed；B凭据依赖阶段Paused — Resumable，待PM核对后续诊断范围，独立评审User Exception / Paused。原始截图dto_rejected仍未唯一定位，不声明已修复。结果见evidence/B-status-controlled-result.json；恢复点见checkpoint.json。


## 后台诊断丢失的离线修正（最新）

PM指出的确定缺陷已修复：READ_DIAGNOSTIC原在线程局部保存，而worker只传回读取结果，导致后台阶段/OSStatus被丢弃；-25308分支另有漏记。现在worker每次初始化诊断，捕获白名单阶段和数字OSStatus后与结果同传，Host不读父线程TLS，并将诊断写入既有非内容request元数据。成功、失败、worker忙/超时/断开/启动失败分开记录；未知阶段丢弃，Key仍Zeroizing且迟到不POST，不携带账户/service/ref/配置值或系统错误描述。

完整23入口回归通过，Rust 306项通过，online/real构建通过，三个诊断丢失mutation被断言检出。离线覆盖-25308及其他OS错误、默认钥匙串阶段、锁忙、父子TLS隔离、超时/并发拒绝/迟到丢弃、断开与下一次初始化，并核对worker到非内容收据和预算不额外消费。历史Unknown来自原诊断丢失，不能表述为OS不可诊断。

本增量没有启动App、真实凭据读取、策略恢复或POST；B仍预留4/回应0/POST0、第4代暂停。后续一次验证的精确方案已写入evidence/B-diagnostic-single-verification-plan.json，交PM协调；不让用户重复检查或解锁。闭环证据见evidence/B-diagnostic-offline-closure.json。该离线修正不等于B/C通过或整体Complete。


## PM协调的单次B诊断验证（最新）

固定221文件与方案逐项一致。原签名新B包PID61815，启动核对第4代暂停、预留4/回应0/POST0、原模型及两项合成范围；经现有设置“调整→确认保存范围”保存原范围一次，Host生成revision/generation5，未直接编辑DB。

仅一次B01后台非交互读取，收据现在明确记录credentialDiagnostic={stage:single_item_read,osStatus:-25293}，约10毫秒后credential_unavailable。生产预留4→5、回应0、实际POST0，模型语义未执行。该数字仅定位到本次系统读取失败，不能单凭它确定具体ACL/密码/身份根因。已停止重试，正常退出精确PID61815并核验消失，逐值核对后删除本次场景时钟。

一次异步状态变更导致旧AX索引的详情点击误开原生检查菜单；未选择检查项，Escape及显式取消后AX确认已取消，未启动交互凭据读取，该导航不计正Evidence。随后重新取索引的详情确认判断5/回应0。另一次ScreenCaptureKit暂错恢复后继续，未重启或扩大权限。无ACL/信任/缓存/真实C/音频改动。结果evidence/B-diagnostic-once-result.json，原历史全部保留；等待PM就精确诊断协调下一步，不要求用户重复解锁/手动检查。


## 公开依赖核对与离线语音联合接线（后继增量）

源码/固定依赖及Apple文档确认-25293为授权或认证失败，不能唯一归因。实际失败在默认钥匙串条目的FindGenericPassword阶段；没有进一步真实读取。单项非秘密ACL只读差异已提交PM，尚未授权/实现/执行，见evidence/B-auth-source-review.md与B-single-item-metadata-scope.md。

离线ASR Gateway已通过新Host Adapter连到持久session/ASR registry和原canonical UserTurn，完整SSE EOF才产出一轮待授权对话预览；partial/重复EOF不产生新轮或Action。每个传输边界重核会话、generation、policy与conversation撤权，失败取消fake传输且不退预算。没有改导入的P3-160固定模块；native权限仍禁用，Transport/PCM均合成，实际MiMo/音频为0。

完整23入口回归、Rust 308项、online/real构建通过，两个联合接线mutation被断言检出。SpeechOutput registry/TTS projection及真实native音频producer仍未完成，不宣称实际语音可用。证据evidence/A-voice-joint-closure.json。B仍第5代暂停、预留5/回应0/POST0；旧单次计划的候选hash作为历史保留，后继候选不得直接复用旧批准。


## A SpeechOutput登记与TTS联合接线（最新）

已新增Host-only SpeechOutput registry：当前AssistantTurn投影digest、session/generation、TTS用途、conversation许可和主动surface decision/可见性逐边界核验；任意文字/伪造引用不准入。PCM解析后入队前再次核验；HTTP EOF仅draining，独立native消费完成才关闭。SpeechInterrupted只变音频状态，TTS-only取消不影响并发ASR或业务，旧打断不误停新输出。ASR联合测试改用Worker合成帧到Utterance，明确Host与local epoch区分，完整Final才进原preview。

P3-160 A3固定59d8e2ef的9项artifact hash一致，建议已采用，未覆盖当前Host或改其生产voice模块。完整23入口、Rust 316项、三项mutation、online/real构建均通过；当前源码222文件。原文字/Action/预览回归保持通过。固定5文件接口快照已供160接线，见evidence/A-speech-registry-closure.json和A-speech-registry-boundary.md。

实际native producer、完成/背压通知与设备/声学仍待接，不提供可用语音开关或自动speech请求，不宣称真实语音Pass。本增量凭据读取/设备/播放/POST均0；B仍第5代暂停、预留5/回应0/POST0，元数据提案未执行。


## A native playback 联合增量（2026-09-12）

已按 a38a90cf 三文件 before/after 合入完整候选，18 文件 v4 清单一致。Host 消费反馈适配处理容量、generation/token、EOF 后排空、撤权/打断，4 项联合 fake 测试和2项 mutation 已通过。完整24步回归、320 Rust测试、同App Rust→Swift 3项测试通过。证据：`engineering/LIFEOS-P3-159/evidence/A-native-playback-joint-closure.json`。这是离线适配证明，串行producer/event-loop尚待接线；真实设备、播放、语音POST为0，未作完整可用或联合验收结论。


## 一次批准的单项元数据检查（2026-09-12）

完整同身份B Host已执行一次并正常退出，configuration_binding / OSStatus null，未进入钥匙串条目查询；ACL/提示标志和两个App匹配均Unknown，不推断后台拒绝根因。不补第二次探测。分析预留5/反馈0/generation5/POST0前后不变，后台仍暂停。离线24步与325 Rust测试通过，3项C mutation检出。完整报告与Manifest：`engineering/LIFEOS-P3-159/evidence/B-metadata-once-report.md`、`B-metadata-once-manifest.json`。PM需要评估此真实诊断能力边界；原离线语音接线继续，未称整体可用或验收通过。


## PM定位的元数据有效绑定缺陷已离线修正

首次失败源于新增raw enabled/model门槛遗漏原生命周期合并语义，不能描述成已验证的OS能力限制。现已抽取原有效配置决策供两入口共用，生产Store忠实合成对照到同C fake FFI通过，完整24步回归与双模式构建通过。报告：`engineering/LIFEOS-P3-159/evidence/B-metadata-binding-fix.md`。首次失败保留，无第二次真实访问，后台根因与恢复仍Unknown。


## A ASR producer 原入口联合增量

Host串行音频→ASR→原对话预览适配已实现，部分文本不提交、唯一final交回同interaction链、终端transport释放、撤权/设备丢失保留预算并清理。完整24步/329 Rust通过，双模式构建通过。证据：`engineering/LIFEOS-P3-159/evidence/A-producer-manifest.json`。App顶层audio/ASR/TTS循环和生命周期组合仍待接入，真实音频保持未启用，不能称完整可用。


## 最新：A统一语音循环离线组合

VoiceRuntime已组合音频、ASR、原interaction预览、SpeechOutput/TTS与消费排空，逐tick撤权与关闭清理已验证。最终24步/332 Rust、同App Swift FFI3项、双模式构建通过，230完整候选文件来源稳定；160的18文件仍匹配。报告与Manifest：`engineering/LIFEOS-P3-159/evidence/A-runtime-closure.md`、`A-runtime-manifest.json`。

App真实设备/Detector/CredentialAccess启用入口保持disabled；声学、MiMo与真实联合验收未执行。B一次元数据检查结束，绑定缺陷仅离线修正，无再次读取、POST或解除暂停。需要PM评估B认证未解决边界；整体仍In Progress，独立评审Paused，不称完整可用。
