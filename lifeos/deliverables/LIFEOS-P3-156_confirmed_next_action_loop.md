# P3-156 自然对话中的安排与进展闭环

2026-09-10。Codex专项，L2离线合成；工程、自检、同范围修复及完整合成候选已交付，等待PM验收。最终窗口补读遇锁屏，checkpoint为Paused — Resumable；不宣称Complete、PM Pass或Independent Pass。独立评审继续暂停。

## 结果

正常聊天的明确安排可直接记下，明确完成/调整/取消可直接更新，歧义才澄清。没有采纳、保存、完成等必经按钮；Today沿原布局最多一个已说定Focus。每个行动保留稳定ID、版本事件、确认原文引用、来源引用、时间与反馈；来源失效时保留用户说定内容并显示需要用户判断。不会自动长期化、复活已完成/取消项或执行外部行动。

最终候选173文件，完整继承155的166文件，7新增、14修改、0删除。Shell、Settings、Provider列表、加密持久无TTL、草稿/对话、来源/健康及154/155恢复链路保留。构建入口candidate/Cargo.toml；不重组精简样机。

## 授权与谱系

D-0659授权本任务；D-0660记录用户对已展示最小协议差异回复“允许”。精确minimal-protocol-proposal.md SHA256 cf8e88ed446a503e73b8804cb71fc871df628a711d0f7ca96d273d09d63bd381。authorization/保留批准前checkpoint、旧合同摘要、获批任务卡副本、授权谱系及原进展报告。未改历史提案或155资产。

保持14个IPC命令、v4/v5请求响应及物理SQL Schema；只在合成模式接入获批v6 prepare/commit/snapshot和Action DTO/Port/既有JSON表事件语义。新增action_domain.ts、action_application.ts、action_view.ts及Rust actions Adapter，UI不接SQL。TS Application/Domain确定性复核模型候选，Host事务内再核草稿原文、packet、唯一目标、版本、来源授权和建议有效状态。新build guard直接拒绝controlled-real构建。

## 验证事实

243项唯一检查通过：Rust118、原UI25、集成14、来源/健康组合11、连续会话8、澄清UI5、错误归属6、Flow竞态8、来源恢复7、时效6、新增行动35。详见evidence/check-summary.json及逐项日志；重复复跑不重复计数。最后旧建议status检查由最终actions35覆盖，未受影响旧能力按差异复用。对共享cancel/模拟建议输出和Flow另做affected-final复跑，全过。

| 合同项 | 实际覆盖 |
|---|---|
| 完整累积基线 | 155父Manifest315、切换增量14、166源码逐文件hash保全；当前差异7/14/0 |
| 四操作与误写拒绝 | 实际Host及Application创建/调整/完成/取消；引用、假设、否定、闲聊、询问、可能性、举例、过去经历、伪造候选拒写 |
| 幂等与草稿 | 同请求重放、不一致payload拒绝；事务故障全回滚；响应丢失后只读恢复，不再次写入 |
| 重启与迟到 | 同ID跨进程恢复、版本冲突、cancel草稿、完成/取消不复活；已完成历史不影响唯一未完目标 |
| 依据与权限 | 来源过期、纠正、撤权各自复位后独立验证；旧建议stale在提交处拒绝；失效依据不删除行动，仍允许用户明确取消 |
| Today/对话 | 单Focus转义/无操作按钮；actual App正常输入创建与完成；宽窄窗口下输入/反馈可见 |
| 模型替换 | OfflineA/B共用同一行动身份/反馈/来源；模型伪造候选在写入前被Application拒绝 |
| 离线完整App | final bundle绑定173源码，编译拒绝真实模式；最终直接PID80426启动回执成功 |

最初Rust运行未设置umask077导致两项合成权限夹具失败，记录保留；修正测试入口环境后定向6项通过，随后完整118通过。首次模块path构建错误亦保留且已修复。这些失败日志不进入正通过计数。没有沿用155的13 mutation作为本轮新证据；L2用伪造候选、版本/权限反例及事务故障测试验证失败关闭。

## actual App与视觉边界

首次合成App直接PID79815，精确binary经proc_pidpath核对。CUA只选择本任务合成包，获取精确标题窗口、HTML content与tauri://localhost；聊天输入“我明天先整理合成报告结论。”直接产生记录；“报告结论做完了。”直接完成并从Today移除。正常Cmd-Q后重启PID79905，原始表达与完成反馈保留，无复活。两进程均正常退出。

CUA原生内联图像检查了宽窗与拖窄后的中文输入/反馈，无任务按钮或新导航；不声称所有视口或精确逻辑尺寸全覆盖。图像在本任务会话内，没有伪造本地PNG或截图hash。evidence/visual-observations.md记录完整观察和两次元素过期后的新AX定位恢复。

最终包仅在之后加了旧建议status复核，UI与布局代码未变，前述视觉按影响面复用。final包直接启动PID80426、binary身份匹配；最后CUA补读返回Mac is locked，尚无最终PID的AX回执。该项是可恢复环境暂停，不是Rework/候选缺陷，也未使先前有效观察失效。PM需判断是否要求解锁后仅补最终窗口；不要重跑无关构建、测试和原视觉。

## 交付位置与复跑

工程根：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-156/。

最终App：/private/tmp/lifeos-p3-156-next-action-v1/LifeOS P3-156 Synthetic Actions Final.app。

Binary SHA256：0e0b7e39f9a7e42c5d85facd80a5da08f6164e4927f7ca38aacead84727f1adb。源码和包清单：evidence/synthetic-bundle-final.json。旧合成演示包和收据保留，不作为最终包身份。

- capability-map.md、minimal-protocol-proposal.md：既有能力映射与获批差异。
- evidence/candidate-diff.json、baseline-snapshot.json：逐文件继承和影响。
- evidence/check-summary.json：243检查及日志摘要。
- tools/verify_delivery.py：交付Manifest、历史和源码摘要验证，不探测真实App/DB。
- tools/rerun.py：只在精确已拥有156根离线复跑，umask077、Cargo locked/offline；新日志放该合成根reruns/<uuid>，不改历史Evidence，不启动GUI或真实模式。
- checkpoint.json：resume_from=final_native_window；最终合成App保持空闲，解锁后如需只补窗口观察。

## 限制与待决

这是合成模型与有限明确句式的工程实现，不是任意开放域语言理解或真实能力启用。含糊/未支持表达不依据模型置信度写行动。准备上下文上限128行动、32768字节，超限失败关闭；显示分页不会把截断列表误当唯一目标。完整原始事件在库内保留；本轮不进行真实数据迁移/接入，不改变正式领域冻结或Stage。

已发现且未修复的P0/P1/P2=0/0/0；Unknown=1（最终PID AX补读因锁屏未完成）；Not Implemented=0指本次获批合成接线，不包含真实模式/开放域能力。已有宽窄窗和正常重启观察的范围如上，不将Unknown静默写Pass。

需PM决定：接受本离线工程及未变UI视觉复用，或要求解锁后补最终窗口。当前不更新PM账本、不关闭风险、不冻结、不提交推送/自动合并、不启动后继。真实App未关闭/替换，真实来源/ZIP/DB/凭据/Provider/网络接触为0；真实使用权限不从155继承。只有最终合成App处于运行空闲状态。
