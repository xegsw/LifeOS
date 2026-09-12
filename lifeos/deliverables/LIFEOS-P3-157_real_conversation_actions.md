# P3-157 自然对话安排真实接入

2026-09-10，Codex工程专项，L3。工程、合成安全验证、同范围修复和已授权正常切换完成；等待用户ABF-08实际结果及PM终局，不宣称Complete、Independent Pass或用户通过。独立评审依D-0661用户例外继续暂停。

## 执行结果与范围

在156完整173文件基线上接入受控真实模式的本地有限句式行动。当前完整候选174文件，新增1、修改10、删除0；设置、Provider选择、Key加密无TTL、来源/健康/对话、154错误归属及155恢复均保留。没有重画页面或新增任务操作按钮。

已批准v6 prepare/commit/snapshot、Action/事件/反馈/澄清语义沿用D-0660。真实快照合并行动及反馈；本地安排解析仍使用156有限句式，不调用云端解析，也不把模型输出当确认。原文、唯一目标、版本、授权、来源校验和事务幂等未简化。

新existing_schema检查在Store打开及每次v6请求前校验12张既有表及其列、类型、主键；缺库/缺表/错误Schema在业务写入前拒绝，不补建或迁移。prepare_database_file在existing-only策略下不创建缺失文件；测试直接在157合成文件上覆盖真实策略函数。没有新增公开任意根参数。物理SQL Schema、14命令和v4/v5合同不变。

## 授权与历史

依据：5ed8任务卡LIFEOS-P3-157_real_conversation_actions.md与LIFEOS-P3-157_acceptance_basis.md，D-0661记录用户“确认，启动”。本轮真实目标已在卡内精确列出；不重复索取启动/同范围授权。任务和ABF副本/hash在inputs与baseline-snapshot.json。

156完整244项Manifest、173候选及原报告在启动前和切换后逐项核对，均保全。155历史切换报告、最终PM Review及完整旧App代码身份核对；不覆写旧报告/Manifest/checkpoint或合成156实例。

关键读取：最新CURRENT_STATUS、157合同/ABF、SESSION_REPORT_TEMPLATE、156与155最终Review、156获批提案、155切换报告；定向核对PM/角色/Gate3/例外/累积产品/权限/CI恢复条款。未变化根AGENTS及相关已完整读取治理内容复用，并核对当前差异。职责为工程实现、数据/领域和AI安全自检，PM负责验收和账本；不自行转派。

## 合成安全Gate

254项检查通过：Rust123、行动36、真实mode本地接线3、原UI25、集成14、来源健康组合11、连续会话8、澄清UI5、错误归属6、Flow竞态8、来源恢复7、时效6；另含2项编译模式拒绝。即252项行为/回归加2项构建守卫；不重复计数复跑。

5个有效mutation均被检出：允许缺失existing-only库补建、跳过feedback表、跳过列合同、真实界面漏接行动、跳过本地行动路径。Rust变体均出现实际测试失败而非编译错误，JS变体出现断言失败。变体只在157独占合成根执行，未接触真实资产；原候选不被变体修改。

| ABF | 证据与结论 |
|---|---|
| 01 | 173继承→174完整候选，1新增/10修改/0删除；旧能力完整回归通过 |
| 02 | 每张必需表缺失、错列/类型/主键/视图、缺库、错根/owner、混合模式；读取不修复和失败关闭通过 |
| 03 | 既有自然表达/歧义/引用/否定/模型伪造拒写；额外覆盖有效create中篡改确认内容；界面无必经按钮 |
| 04 | 原子事务故障回滚、同请求重放、迟到版本冲突、草稿保留、丢失响应后只读恢复通过 |
| 05 | 来源过期/纠正/撤权、建议stale、历史/身份分离、不复活、不长期化通过 |
| 06 | real-mode DTO doubles验证本地保存与恢复不进入云端/凭据调用；旧真实网络/Key守卫及逐次披露回归通过 |
| 07 | 固定完整旧包和新包代码身份通过；正常退出及单次新PID启动回执匹配 |
| 08 | 等待用户正常表达记录/更新、退出重启后反馈，仅收通过或固定错误码 |

合成真实mode DTO double只改变返回标签，不运行真实测试driver、不访问真实库。UI布局和156有限句式保持；本轮只去掉真实快照漏合并行动的分支，以接线测试验证。按影响复用156已接受的宽窄观察，不读取真实AX/截图。

## 非内容实际切换

旧App：/private/tmp/lifeos-p3-155-source-update-v1/LifeOS P3-155 Source Update.app。旧binary SHA256 8716005747edc7d0fb21df7a816c0cf10684fb110b9b48e9fad29b984a1eb14c，所有包代码文件摘要与155固定清单匹配。即时匹配PID74377/local.lifeos.p3-155.source-update；正常退出normal_quit_requested=true、exited=true。没有强杀或删除锁。

新完整App：/private/tmp/lifeos-p3-157-real-actions-v1/LifeOS P3-157 Real Actions.app。

新binary SHA256 d907337cbfdb88ab887925e955a79d97414dd7fd1e34cc0c261f9a8c5904d56d。174源码映射在evidence/real-bundle.json；包含原alias_metadata helper。单次claim后直接启动PID84364，controlled_conversation_started、running=true，proc_pidpath匹配精确包内binary；随后只检查两固定包的进程身份，仅新84364。PID是收据时事实，不保证未来持续在线。

Agent未读取真实正文、DB值、Key、AX、截图、内容日志或内容hash。代码包摘要属于启动身份；仅接收固定startup状态和代码路径/PID。App内部按合同复用现有真实库/凭据/上下文；不自动导入、刷新、test/models或发送，不迁移补建、不重置Key。本地有限句式保存不需Key；普通DeepSeek仍由用户逐次查看披露并确认。

## 最少用户验收（交PM收口）

1. 在当前P3-157对话中，用自己的内容按“我明天先……。”说定一件安排，确认直接出现简短本地反馈，今日页显示它；不用再点采纳或保存。
2. 用“把……改成……。”调整，或“……先不做了。”取消；确实完成时可说“……做完了。”。确认反馈与状态一致，多目标时只回答必要澄清。
3. 正常退出并重开同一个P3-157 App，确认安排/反馈仍在，取消或完成项没有自动重新出现；原会话与设置保留，无需重录Key。

仅回复“通过”，或哪一步的固定错误码；不提供正文、Key或截图。本轮无需为验收执行导入/刷新/云端发送。真实结果由用户声明，Agent不会代替用户重复操作真实内容。

## 交付与恢复

工程根：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-157/。

主要资产：完整candidate；inputs合同/ABF；baseline-snapshot；impact-matrix；candidate-diff；check-summary及回归/5mutation日志；real-bundle；package-identity、normal-quit、launch-claim、launch、identity-before/after；FINAL_MANIFEST。

只读核验：tools/verify_delivery.py，仅核对工作区Evidence、源码和父156，不探测真实数据或运行状态。离线复跑：tools/rerun.py，在精确157合成根中新建副本/日志后调用run_checks.py，历史输入不改写；不自动运行GUI、真实模式或再次切换。switch_once.py的旧claim存在即拒绝重启，恢复时先检查既有结果，不盲启。

checkpoint.json恢复点user_actual_actions_validation；App保持已启动状态，旧包和用户数据保留。用户验收前检查点已发送PM。已有工程和安全Gate不因用户等待/桌面锁屏重复执行。

当前P0/P1/P2=0/0/0，Unknown=1（ABF-08用户实际结果待确认），Not Implemented=0仅指本次批准范围。有限句式、128行动/32768字节上下文上限沿156保留，不宣称开放域语言理解、云端行动解析、任何外部执行或生产SLA。

需PM及用户完成终局验收；不关闭风险、不冻结、不切Stage、不更新PM账本、不自动合并main、不清理用户数据、不启动158。未宣称Git提交/推送或CI全绿。
