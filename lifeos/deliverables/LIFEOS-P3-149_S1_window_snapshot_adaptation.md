# P3-149 S1 无样本ID窗口快照适配

状态：工程 Completed / 合成离线L2自测通过，待普通PM收尾。独立评审未新增，真实阶段未启动。原161项交付及原报告保持只读；原PM合成Pass不自动外推到本增量。

## 结果与边界

S1新增独立的health-window-snapshot-v1输入，不需要sampleId/revision；旧health-envelope-v1解析和幂等语义保留。按逻辑来源名称组、metric、精确窗口、offset和查询口径识别窗口快照，只允许完整非空合成快照原子替代同范围观察。不把导出批次或内容摘要伪装为样本身份/逐样本更正。

用户展示的iOS26.6.1字段菜单仅支持“该菜单未见ID/revision”的事实，不据此断言整个系统不支持ID。来源名称组未区分同名设备。未知/部分/分页未完成/空结果保留历史与等待提示，不能覆盖已有有效State，也不认定源端删除；发送方字段不证明真实权限完整。

S1窗口是范围观察，不是日权威总量。同metric的不同scope/部分重叠窗口拒绝激活，不合并相加；不同来源/查询/offset的相交范围也保守拒绝。非重叠范围分别保存。同scope依capturedAtMs维护已接受完整非空批次水位，旧包只留历史，相同时间冲突拒绝；同内容重新导出不刷新State新鲜度。observedAt仍来自样本结束时间，receivedAt独立保存。批次generation/supersedes为批次级谱系。

v1日投影和S1窗口双向检查相交范围，不会同时叠加进同组State。范围/协议切换不自动迁移旧数据；需要后续明确替代合同。sleep只有明确explicit-asleep区间可计入并取并集；没有猜测真实睡眠类别。步数/运动无ID重复或重叠行输出不确定，不凭内容摘要强行去重。

0新增IPC、operation、SQLite表/列，复用health_batch/source/current_state JSON扩展。健康模型拒绝守卫保留并实际回归；未接触真实健康、iCloud、网络、Provider、凭据、148 App或148运行根。未提交/推送/合并，未更改PM账本。

## 实施顺序与差异

按S1任务卡授权，先复算原161项/原报告并复制增量candidate，再保存精确设计，随后编码。设计：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-149/S1/design/snapshot-contract.md`。

S1候选新增3文件：health_snapshot.rs、其17项模块测试、test_snapshot_ui.mjs。修改5文件：健康ingestion分发/双向互斥、main模块注册、健康view及生成JS、来源preview拒绝回归。精确差异：S1/evidence/candidate-diff.json。

Provider/加密实现、IPC集合、116整体/142设置/原健康CSS、ConversationFlow均未修改。旧87项通过结果按影响面继承，未重复全套评审；本轮不是全105项Rust套件运行。

## 验证与Evidence

- Rust **36/36**：18项S1新增相关验证（17模块＋1实际来源preview），18项受影响的原健康/来源guard回归。日志 `S1/evidence/tests-final.log`。
- 前端 **19/19**：原16项回归＋3项S1窗口/等待历史/实际resolver拒绝。日志 `S1/evidence/ui-tests.log`。
- 覆盖同快照重放、完整同范围替代、顺序规范化、未知/部分/空/分页未完不覆盖、冲突/乱序/水位、重叠范围、来源策略变更拒绝、同名不当设备身份、超限/未知字段/类别、事务中断、重启、v1双向互斥、前后端模型不披露。
- actual App：120步完整窗口→140步完整更正；随后170步完整性未知包不覆盖，保留140及等待提示；原4条v1 State逐字不变。证据 `S1/evidence/actual-ingestion.json`。
- App关闭重开后重放全部收件箱，records/sources/states逐字不变。证据 `restart-before.json`、`restart-after.json`。
- 精确PID→AXWindow→WebArea→匹配CG几何截图：`s1-me`、`s1-settings`、`s1-history`、`s1-narrow`。桌面1280×949及窄窗口700×760；窗口口径、来源名称组、不完整等待和批次历史可读。未用原截图冒充本增量。
- 结构化结果 `S1/evidence/results.json`。网络socket检查为空，仅作为当时观察；边界结论还依赖未变的engineering编译路由和模型拒绝测试，未声称全程抓包。
- 确定性复跑入口 `S1/tools/run_checks.py`；`exercise_inbox.py`为已执行的一次性GUI合成夹具入口，O_EXCL保护已有文件，不覆盖既有批次。未声称远程CI已运行。

合成S1剩余缺口 **P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0**。真实字段语义、权限/分页完整性、文件发布、传输/自动化等未验证，明确排除本轮Pass范围，不伪报实机同步。

## 保全、展示与交付

工程包：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-149/S1/`。
新快捷指令方案：`S1/design/shortcuts-s1.md`。它替代未来路径对样本ID的硬依赖，但明确真实可信完整性仍待验证，不能将真实数据标成synthetic-fixture导入当前App。

原FINAL_MANIFEST SHA256仍为 `ec7ac1ce37fc740df97654bde6574e40a1762cb3950dc448a5caeef7b48658d7`；161项、原报告收尾复算全部不变，未修改PM历史。S1自己的FINAL_MANIFEST是增量完整性清单，不是冻结或ABF。

同一149根marker核验后停止旧149展示PID91721；本轮PID93383完成动态验证后停止。当前S1展示PID **93517**，App `/private/tmp/lifeos-p3-149-health-source-v1/LifeOS P3-149.app`，标题LifeOS P3-149 - Synthetic Offline，留在Me。二进制SHA256：`02af1b89089587448b7fbc451bd00b40e5151921945eb128301bd5386340d5f7`，候选摘要与launch-s1display.json一致。新旧合成数据及App保留，无清理真实资产。

检查点 `S1/checkpoint.json`；未发生环境暂停或授权越界。主责Codex专项工程；协审/独立评审保持暂停，PM为验收方。复用会话，上一交付已结束；已读取新增S1卡、CURRENT_STATUS和回复模板，复用同会话已读且未变AGENTS/架构/IA/CI规则。自评适配High。

需PM：本S1合成增量普通验收收尾。真实阶段继续等待精确边界及源端验证，不启动新任务，不外推冻结/风险关闭/Stage结论。
