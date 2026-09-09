# LIFEOS-P3-149 健康来源接收与当前状态闭环

状态：工程交付 Completed，合成离线 L2 自测通过，待 PM 验收。独立评审/复核按用户指示暂停；未声称 Independent Pass、真实 iPhone 同步、风险关闭、冻结或 Stage 切换。主责 Codex 专项工程；复用已结束 P3-148 的工程会话，148保持只读。

## 结果

合成健康文件进入本任务固定 inbox 后，由打开中的实际 Tauri App 接收。严格校验、事务原子保存、重复幂等、迟到/版本更正、按 offset 分日投影和重启恢复已接通。Me显示健康近况，Memory显示样本/版本，Settings → 数据与隐私显示来源与拒绝文件。健康接入不授权 AI；没有写入长期 memories。

新增 Tauri IPC、Request operation、SQLite表/列均为0。复用 records/sources/states 的 JSON 扩展；临时接收错误作为 snapshot.sources 中的 health_source 运行态投影，未新增顶层响应字段。启动仅初始化149新合成库的既有结构，不迁移旧库。健康领域规则、内部 HealthRepository port、SQLite/固定目录 adapter 分离。

## 精确合同与边界

- 执行合同：`/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/tasks/LIFEOS-P3-149_health_source_current_state_integration.md`。批准快照：工程包 `contract-inputs/approved-task-card.md`。实施设计先于代码，PM批准JSON扩展及多来源规则后继续；不另索用户重复授权。
- 工程包：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-149/`。
- 唯一合成运行根：`/private/tmp/lifeos-p3-149-health-source-v1`，本任务0700根/0600marker校验；收件箱0700，文件0600，拒绝符号链接/硬链接及超限内容。
- 分支 `codex/l2-p3-149-health-source`；未提交、未推送、未合并，未更新PM账本。未探测旧运行根、真实健康/iCloud/手机/个人数据库/真实Provider或凭据。
- 148候选87项hash和其Manifest hash收尾复算不变。116整体、142设置和既有conversation CSS逐字不变；新增健康行样式单独位于health.css，不增加一级导航。

## 语义

三指标仅为 sleep区间、steps计数、exercise分钟；不将缺失当0、不将未返回当删除、不推断疼痛疲劳。128KiB/256样本/7天为单个合成包限额，超过即拒绝，不宣称支持真实7天全量。固定inbox最多64项，超限显式暂停而非截断/饥饿扫描。

批次身份按source.id+batchId；同身份不同内容拒绝。同样本/版本一致无重复写入，冲突整批回滚；多个版本保留历史，最高版本决定投影。更正只重算旧/新日、metric及offset，撤出旧日显示无当前样本，不伪造零值。

睡眠只合并明确睡眠区间；步数/运动同源重叠输出不确定，不简单累计。多来源分别展示，无来源优先级依据时个人汇总null、“暂无法可靠合并”，不默认选最大值。跨日计数量按区间比例估算并明确标注，offset不同分别保存。观察时间使用输入offset显示；接收时间单独标“本机时间”。重放旧样本不会使观察新鲜度刷新。

健康raw/State的modelEligible=false和observed有实际守卫：正常前端resolver排除，后端local_prepare拒绝伪造健康ref；来源支撑prepare实际返回的items不包含健康，移除唯一笔记后健康不会补入，返回no_match且无发送token。

## 验证

最终 Rust **87/87**，前端 **16/16**。日志：`evidence/rust-tests-final.log`、`evidence/ui-tests-final.log`。确定性复跑入口 `tools/run_self_checks.py`；仅本地离线执行，未声称远程CI运行。GUI不进入无人值守CI。

| 条目 | 工程结论与证据 |
|---|---|
| A1 | Pass：字段、单位、时间、样本数/字节限额、重复key、无效UTF8；异常零写入；真实App坏批次数据前后完全一致。 |
| A2 | Pass：批内重复/冲突、批次冲突、迟到、版本乱序、重复导入不刷新状态。 |
| A3 | Pass：睡眠并集、同源重叠、多来源不合并、跨日分摊、不同offset、缺失不补0；前端额外验证UTC-5显示。 |
| A4 | Pass：保留版本refs；实际App重启后更正只改变1条步数State，其余3条逐字不变。 |
| A5 | Pass：事务中断trigger全回滚后可重试；SQLite关闭重开；App关闭期间排队文件，重开接收且历史保留。 |
| A6 | Pass：实际PID→精确AXWindow→WebArea→匹配CG几何截图；1280×949和700×760，Me/Memory/Settings及来源版本、错误提示可读可滚动。 |
| A7 | Pass：既有9项Flow回归，加重试间编辑、实际remove入口、取消失败、移除期间编辑回归；8云4本地目录及加密生命周期回归保留。 |
| A8 | Pass：engineering唯一profile；健康不纳入实际resolver/prepare；Provider/Keychain为合成port；App网络socket检查空；无系统后台服务注册。socket快照仅为当时观察，结合编译路由与mock测试构成边界证据，不单独冒充全程网络追踪。 |
| A9 | Pass：官方文档支持的搭建方案、未设备验证字段和下一真实阶段一次性边界清单已交付；不虚报可安装快捷指令/真实同步。 |

结构化汇总 `evidence/results.json`；App动态重复/坏包证明 `actual-inbox-atomic-replay.json`；重启证明 `restart-before.json` / `restart-after.json`。正交付截图为 `delivery-*.png/json`；`actual-*`与`final-*`保留实施过程证据。

合成范围剩余缺口：**P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0**。真实设备字段、同步、健康权限、自动化行为均不在本轮通过范围，待设备验证项集中于快捷指令方案。

## 过程异常与保全

完整自检发现继承测试仍期待旧凭据lineage可用，与已继承的生产拒绝逻辑不符；仅修正149测试期待，不放宽生产逻辑。别名helper缺失、环境变量/相对编译路径和健康测试激活夹具均在本包修正。初期编译/失败日志完整保留，最终87项全过。

桌面工具首次仍报锁定，写checkpoint并由用户再次解锁后继续，无环境Rework。一次截图误选本App菜单条，保留为`excluded-menubar-capture.png`并排除正证据；随后使用精确AX窗口位置尺寸绑定CG。窗口调整动画期间AX/CG暂不一致的抓取未生成正截图，待一致后补取。旧AXhelper没有MainWindow回退时拒绝操作，工程tools增加同PID精确窗口回退后成功。无禁止边界接触。

## 实际 App 与保留

App：`/private/tmp/lifeos-p3-149-health-source-v1/LifeOS P3-149.app`。
当前展示PID **91721**，标题 **LifeOS P3-149 - Synthetic Offline**，1280×949，停留Me供查看。最终二进制SHA256：`0e3950265d1f79d6af8c942c666fface354585dfe49151c7d991843a79f08dc6`。`launch-healthdisplay.json`记录全候选文件摘要并已复算一致。

首轮PID90089、第二轮PID91380已核对精确可执行路径后停止；当前App及本任务新库/夹具/缓存保留用于展示，未清理。没有操作P3-148展示App。当前合成库含5个健康样本版本、3个批次收据、2个健康来源、4条健康State。拒绝的04-bad.json作为合成反例保留，设置页因此显示1个文件未接收，这是预期负路径。

## 交付与PM

实施映射：`design/01-health-envelope-and-projection.md`。
快捷指令方案：`design/02-shortcuts-setup-and-real-boundary.md`，含Apple官方来源链接。
检查点：`checkpoint.json`。包摘要与文件hash：`FINAL_MANIFEST.json`（交付完整性清单，非Frozen ABF）。

需PM确认：本合成结果验收。独立评审仍暂停；真实阶段须先一次性核对精确设备、数据、路径、DB、网络、权限、披露和清理边界。不得从本报告直接启动真实阶段，不提出无关后继微任务。

上下文：已读取AGENTS、CURRENT_STATUS（旧144指针按149卡定向覆盖）、149卡/批准快照、指定草案与SESSION_REPORT模板；定向补读架构Source/State/Context/授权、IA Me/Memory/Settings及CI可恢复规则。局部工具输出截断已对实际使用段定向补读。未调用可选本地模型；自评适配High。
