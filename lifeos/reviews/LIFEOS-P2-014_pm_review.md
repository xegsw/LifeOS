# LIFEOS-P2-014｜FTS 维护隔离窄测 PM Review

## 验收信息

- 任务 ID：LIFEOS-P2-014
- 任务名称：FTS 维护隔离窄测
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P2-014_fts_maintenance_isolation_narrow_spike_report.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P2-014_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-09

## PM 总结

1. P2-014 完成了任务卡要求的 10 万 / 30 万快速档与 100 万 / 300 万主档验证，交付物、证据入口和机器结果完整。
2. PM 复跑 `python3 lifeos/spikes/P2-014-fts-maintenance-isolation/run_spike.py --tiers 100000,1000000`，结果为 `{"overall_pass": true}`，用时约 29 秒。
3. 主档捕获最大等待为 2.952 ms，低于 1 秒门槛；误报保存、权限泄漏、tombstone 泄漏、restriction generation 泄漏均为 0。
4. 证据支持关闭 R-0039 的“FTS 长维护阻塞前台权威捕获”冻结前硬风险。
5. 本任务不冻结 SQLite Schema、FTS 表、PRAGMA、调度策略、worker、API、性能 SLA 或技术架构。
6. 本任务不允许进入 Stage 3 / 正式 MVP 开发。

## 角色与关卡验收

- 主责角色覆盖情况：已覆盖。技术架构负责人视角下，FTS 维护隔离、权威短事务、影子索引、generation fencing、校验后切换和失败回退均有可复核证据。
- 协审角色覆盖情况：已覆盖。数据 / 领域模型、AI 信任与安全、体验设计和 PM 边界均有说明。
- 已通过关卡：Gate 2 数据与来源评审；Gate 3 AI 权限与信任评审；Gate 4 技术可行性评审（P2-014 范围）。
- 未通过或需后续确认关卡：技术架构整体冻结仍需结合 P2-015 和后续冻结决策。
- 是否属于关键冻结事项：属于技术架构冻结前硬条件，但本任务自身不是冻结决策。
- 是否需要独立评审：不需要新增独立评审；P2-012 已完成技术架构独立评审，本任务是其条件验证。
- 独立评审路径：`lifeos/reviews/LIFEOS-P2-012_technical_architecture_independent_review.md`
- 独立评审结论：Pass with Conditions，要求 FTS 与 Tauri / IPC 两项窄测。
- 是否允许进入下一任务或下一阶段：允许进入技术架构冻结补充 / 决策准备；不允许进入 Stage 3。

## 验收与冻结区分

- 任务是否验收通过：是，Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：SQLite / FTS 实现细节、生产 SLA、跨平台表现、真实长文 / 附件、UI 端到端时延、技术架构整体。
- 是否允许进入下一任务：Conditional。需结合 P2-015 验收结论，进入技术架构冻结补充 / 决策准备。
- 是否允许进入下一阶段：否。
- 是否只是后续任务输入：是。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：是。

## 需要用户确认的事项

1. 是否采纳 P2-014 的 `Accepted / Pass` 结论。
   - PM 建议：采纳。
   - 可选方向：采纳并允许关闭 R-0039；或要求补测后再关闭。
   - 不确认的影响：R-0039 继续停留为 Open，技术架构冻结无法完全收口。

2. 是否接受 P2-014 第 8 节责任边界作为技术架构冻结输入。
   - PM 建议：接受责任边界，不接受 harness 细节冻结。
   - 可选方向：作为冻结输入；或要求技术架构冻结附件再整理一次。
   - 不确认的影响：后续冻结决策无法明确继承哪些 FTS 约束。

## 整改建议

无强制返工。后续正式实现时必须把该矩阵迁移为工程测试，不能只继承文档结论。

## 可接受内容

- “已保存”只由权威耐久提交决定。
- FTS 是可重建派生，长维护不得持有会阻塞权威捕获的长写锁。
- posting 只是候选，消费前必须回连当前权限、active、tombstone、generation、Source / ArtifactVersion。
- 新 generation 只能在校验后切换；旧任务须 fencing；失败影子不得污染合法索引。

## 不接受或需谨慎内容

- 不得把本任务外推为生产搜索 SLA。
- 不得冻结 FTS5、三文件布局、PRAGMA、worker、调度或表结构。
- 不得把合成主档外推为真实附件、跨平台、冷缓存或 UI 端到端体验。

## 对项目文件的更新建议

- `TASK_REGISTRY.md`：P2-014 更新为 Accepted。
- `FREEZE_STATUS.md`：P2-014 更新为 Accepted but Not Frozen；技术架构仍未冻结。
- `DECISION_LOG.md`：新增 PM 接受 P2-014 的决策记录。
- `RISK_LOG.md`：R-0039 可标记为待用户确认关闭，或在用户采纳后关闭。
- `CURRENT_STATUS.md`：更新等待用户确认事项。

## 下一步任务建议

等待用户确认是否采纳 P2-014 与 P2-015。若采纳，可启动技术架构冻结补充 / 决策准备；仍不得进入 Stage 3。

## 聊天回复边界

聊天中只输出验收结论、资产状态、下一步 / 下一阶段状态、修改文件和需要用户确认的问题。
