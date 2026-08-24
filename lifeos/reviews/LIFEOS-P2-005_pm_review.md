# LIFEOS-P2-005 PM Review｜SP-05 撤回 / 删除传播、依赖发现与清理验证技术 Spike

## 验收信息

- 任务 ID：LIFEOS-P2-005
- 任务名称：SP-05 撤回 / 删除传播、依赖发现与清理验证技术 Spike
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P2-005_sp05_revocation_delete_propagation_cleanup_spike_report.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P2-005_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Yes，建议进入 SP-06
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-08

## PM 总结

1. P2-005 已按任务卡完成交付，交付物覆盖四类命令、依赖登记、影响集合、两阶段阻断 / 清理、故障注入、第三方 mock、备份 / 重导入 / 离线回放不复活、审计隐私和角色关卡自检。
2. PM 已复跑 `python3 lifeos/spikes/SP-05/run_spike.py`，结果为 `67/67 PASS`，P0 失败 0，机器结论 `PASS`。
3. 本次 SP-05 可接受为 `Pass`，但严格限于 macOS arm64、Python 3.9.6、标准库、确定性合成夹具、单进程状态机和 mock 第三方。
4. 可沉淀为后续输入的核心合同是：四类命令不可互相冒充；撤回 / 删除提交后活跃阻断零遗漏；物理清理可异步但状态必须诚实；墓碑 / 撤回优先于备份恢复、旧导入、来源重连、离线回放和旧队列重试。
5. 本次不冻结生产删除 SLA、真实第三方删除能力、真实备份窗口、跨设备同步一致性、Schema、API、队列实现、搜索实现、技术架构或 MVP 开发准入。
6. 下一步建议启动 SP-06：离线同步与 Action / Decision / Link / Feedback 状态一致性。

## 角色与关卡验收

- 主责角色覆盖情况：Pass。AI 信任与安全视角覆盖了撤回 / 删除真实运行效果、四命令语义分离、活跃阻断零遗漏、供应商限制披露和审计不可还原。
- 协审角色覆盖情况：Pass。技术架构、数据 / 领域模型、产品架构、体验设计均有明确自检。
- 已通过关卡：Gate 3、Gate 2、Gate 4 在本次合成实现 / 测试语义 / 单进程候选机制范围内通过。
- 未通过或需后续确认关卡：真实多设备同步、真实队列并发、真实备份窗口、真实供应商删除能力、容量性能、正式删除体验文案仍未通过。
- 是否属于关键冻结事项：否。本任务是技术 Spike 执行，不是技术架构冻结或 MVP 开发准入。
- 是否需要独立评审：否。技术架构冻结或正式进入 MVP 开发前才需要独立评审。
- 独立评审路径：不适用。
- 独立评审结论：不适用。
- 是否允许进入下一任务或下一阶段：允许进入下一 Spike；不允许进入 Stage 3。

## 验收与冻结区分

- 任务是否验收通过：是，Accepted。
- 对应资产是否冻结：否。
- 冻结范围：无。
- 未冻结内容：正式 Schema、API、状态枚举、队列、搜索、备份策略、供应商删除能力、删除 SLA、跨设备同步、容量性能、技术架构、MVP 开发准入。
- 是否允许进入下一任务：Yes，建议 SP-06。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：是。

## PM 复核证据

- 复跑命令：`python3 lifeos/spikes/SP-05/run_spike.py`
- 复跑结果：`{"spike": "SP-05", "total": 67, "passed": 67, "failed": 0, "result": "PASS"}`
- 抽查文件：
  - `lifeos/spikes/SP-05/results.json`
  - `lifeos/spikes/SP-05/test_matrix.csv`
  - `lifeos/spikes/SP-05/active_blocking_scan_report.md`
  - `lifeos/spikes/SP-05/cleanup_outbox_report.md`
  - `lifeos/spikes/SP-05/cleanup_fault_injection_report.md`
  - `lifeos/spikes/SP-05/third_party_cleanup_matrix.md`
  - `lifeos/spikes/SP-05/backup_restore_replay_report.md`
  - `lifeos/spikes/SP-05/reimport_reconnect_offline_replay_report.md`
  - `lifeos/spikes/SP-05/raw_logs/privacy_scan.json`
- 抽查结论：证据包与报告主结论一致。活跃阻断扫描覆盖 12 条路径且 misses 为 0；第三方 mock 区分 success / delayed / unsupported / failure；备份、旧导入、来源重连、离线回放和旧队列重试复活数为 0；隐私扫描命中 0。

## 需要用户确认的事项

1. 问题：是否采纳 P2-005 的 PM 验收结论？
   - PM 建议：采纳。
   - 可选方向：采纳 / 要求返工 / 暂缓。
   - 不确认的影响：SP-05 不能作为 SP-06、SP-07、SP-08、SP-09 和技术架构候选输入。
2. 问题：是否接受 SP-05 的不可降级门槛？
   - PM 建议：接受“活跃阻断零遗漏 + 物理清理状态诚实披露 + 墓碑优先不复活 + 四命令语义分离”作为后续实现 P0 门槛。
   - 可选方向：接受 / 部分接受 / 降级。
   - 不确认的影响：删除 / 撤回体验和技术架构会缺少统一底线。
3. 问题：是否采纳 V1 能力处置？
   - PM 建议：本地四命令与 FTS 候选保留；向量非 Must；不保留可还原 prompt 副本；L3 候选继续降级；真实云 / 第三方保持关闭。
   - 可选方向：采纳 / 调整 / 后置。
   - 不确认的影响：后续 SP-06 / SP-07 / 架构任务的能力边界会模糊。
4. 问题：是否启动 SP-06？
   - PM 建议：启动 SP-06 离线同步与 Action / Decision / Link / Feedback 状态一致性。
   - 可选方向：启动 SP-06 / 暂停技术验证线 / 插入项目管理任务。
   - 不确认的影响：多设备离线、旧队列、用户确认状态和 AI 候选覆盖风险无法继续验证。

## 整改建议

无必须返工项。

后续任务需继承以下限制：

- 不得把本次 Pass 解释为生产删除 SLA。
- 不得把 mock 第三方删除能力解释为真实供应商能力。
- 不得把单进程状态机解释为跨设备 / 跨进程同步通过。
- 不得把状态枚举样例直接冻结为正式 Schema 或 UI 文案。

## 可接受内容

- 四类命令分离：`revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback`。
- 两阶段语义：阶段 A 事务内活跃阻断，阶段 B 异步物理清理与状态追踪。
- 活跃阻断 P0 底线：读取、搜索、恢复包、今日建议、队列、模型调用、再派生、导出 / 重导入不得继续使用受影响数据。
- 物理清理状态：`physical_cleanup_pending`、`physical_cleanup_failed`、`vendor_limited`、`physically_cleaned`、`completed_no_physical_cleanup_required` 等可作为后续体验 / 技术候选输入。
- 墓碑 / 撤回优先：备份恢复、旧导入、来源重连、离线副本回放、旧队列重试不得复活。
- 审计和清理证明最小化：解释事件，但不可还原正文、路径、prompt、向量或真实对象 ID。

## 不接受或需谨慎内容

- 不接受将 SP-05 Pass 外推为正式 MVP 开发准入。
- 不接受将 mock 删除状态外推为真实云 / 第三方供应商删除承诺。
- 不接受以“物理清理 pending”继续允许活跃读取、搜索、建议或模型调用。
- 不接受把 `active_blocked` 文案写成“所有副本已删除”。
- 对 Source 级批量删除、向量清理、生产备份改写和跨设备墓碑合并仍需 SP-06 / SP-09 / 架构复验。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：更新 P2-005 PM 验收状态和核心口径。
- `lifeos/TASK_REGISTRY.md`：P2-005 更新为 Accepted。
- `lifeos/FREEZE_STATUS.md`：SP-05 更新为 Accepted but Not Frozen，等待用户确认。
- `lifeos/DECISION_LOG.md`：新增 D-0101。
- `lifeos/RISK_LOG.md`：新增生产删除 SLA、依赖遗漏 / outbox 原子性、状态文案误导相关风险。
- `lifeos/OPEN_QUESTIONS.md`：新增生产实现与体验口径待确认问题。

## 下一步任务建议

建议用户确认采纳 P2-005 后，启动：

`LIFEOS-P2-006｜SP-06 离线同步与 Action / Decision / Link / Feedback 状态一致性技术 Spike`

该任务应验证 3-5 台设备离线编辑、重复上传、乱序、并发 Feedback、撤回和删除下，原文版本与用户权威状态不被 AI 候选或旧设备覆盖。
