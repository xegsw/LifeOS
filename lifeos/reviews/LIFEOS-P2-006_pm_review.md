# LIFEOS-P2-006｜SP-06 离线同步与状态一致性技术 Spike PM Review

## 验收信息

- 任务 ID：LIFEOS-P2-006
- 任务名称：SP-06 离线同步与 Action / Decision / Link / Feedback 状态一致性技术 Spike
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P2-006_sp06_offline_sync_state_consistency_spike_report.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P2-006_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Conditional（用户确认采纳后允许）
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-09

## PM 总结

- SP-06 在任务授权边界内完成：Python 标准库、确定性合成夹具、单账号、单进程服务端权威状态机与 mock 队列。
- PM 复跑 `python3 lifeos/spikes/SP-06/run_spike.py`，结果为 39/39 PASS，P0 失败 0。
- 交付物覆盖幂等、乱序、离线重放、原文不覆盖、AI 候选不替用户确认、Feedback 追加历史、tombstone / restriction 优先、队列发布前重检和 LWW 失败样例。
- 可接受的技术方向是“客户端操作 ID + 不可变版本 + 服务端权威投影 + 对象级前置版本 + append-only Feedback / 操作日志 + tombstone/restriction generation 优先 + 队列发布前重检”。
- V1 同步能力应继续收窄为单账号、少设备、非实时、对象级同步、显式冲突处理；不承诺生产 SLA。
- Action / Decision / Link 三类 AI 候选不应默认物化为 L3 持久业务对象，建议继续以 L1 Derivation 展示，用户明确接受后才进入权威对象。
- 本任务不冻结 Schema、API、同步协议、队列实现、技术栈、技术架构或 MVP 开发准入。
- 证据包具备 `SP-06_report.md` 作为摘要入口；后续 Spike 应按最新规则补齐 `README.md` 或 `MANIFEST.md`。

## 角色与关卡验收

- 主责角色覆盖情况：Pass。最小同步协议、幂等、前置版本、tombstone generation、租约 fencing、队列非权威、显式冲突和非 SLA 边界均已覆盖。
- 协审角色覆盖情况：Pass。
  - 数据 / 领域模型：ArtifactVersion、Action、Decision、Link、Feedback、Derivation、Authorization、AuditEntry 的身份与历史未被覆盖。
  - AI 信任与安全：AI 候选不可自确认；撤回、删除、断源和旧队列 fail closed。
  - 产品架构：保持个人外脑单账号场景，未扩为多人协作或企业同步平台。
  - 体验设计：形成双版本、候选分歧、旧设备拒绝、恢复内容过期、待复核等状态语言，但正式 UI 未验证。
- 已通过关卡：Gate 4 技术可行性评审、Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审，均限合成单进程候选机制层。
- 未通过或需后续确认关卡：生产事务原子性、跨进程 / 跨平台、真实多设备、正式冲突 UI、容量性能、导出恢复合并仍未验证。
- 是否属于关键冻结事项：是，影响未来技术架构候选和 V1 同步能力；但本次不冻结。
- 是否需要独立评审：暂不需要；技术架构冻结或正式 MVP 开发准入前需要综合独立评审。
- 独立评审路径：无。
- 独立评审结论：不适用。
- 是否允许进入下一任务或下一阶段：用户确认采纳后允许进入下一技术 Spike；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：是，Accepted。
- 对应资产是否冻结：否，Accepted but Not Frozen。
- 冻结范围：无。
- 未冻结内容：同步 SLA、设备数承诺、实时性、Schema、API、事件流、队列实现、租约实现、云端权威范围、技术栈、技术架构、正式 MVP 开发准入。
- 是否允许进入下一任务：Conditional，需用户确认采纳 P2-006。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes。

## 需要用户确认的事项

1. 是否采纳 P2-006 / SP-06 为有限边界内 Accepted，并允许后续 Spike 继承最小同步合同。
   - PM 建议：采纳。
   - 可选方向：采纳 / 要求轻量补证据入口 / 返工。
   - 不确认的影响：无法把 SP-06 作为 SP-07、SP-08、SP-09 和后续技术架构候选输入。
2. 是否采纳 V1 同步处置方向：单账号、少设备、非实时、对象级前置版本、原文双版本、显式冲突、队列非权威。
   - PM 建议：采纳为条件性方向，不冻结实现。
   - 可选方向：采纳 / 更保守为单设备本地优先 / 推迟云同步。
   - 不确认的影响：SP-07 恢复包与搜索状态难以确定冲突、旧版本和撤回内容如何处理。
3. 是否确认 Action / Decision / Link 三类 AI 候选继续降级为 L1 Derivation，用户明确接受后才进入权威业务对象。
   - PM 建议：确认。
   - 可选方向：确认 / 指定某一类对象继续验证 L3 物化。
   - 不确认的影响：V1 AI 主动性边界与同步复杂度会重新膨胀。
4. 是否将生产原子性、分布式租约、正式冲突体验、长离线窗口和容量复验列为技术架构冻结前条件。
   - PM 建议：确认。
   - 可选方向：确认 / 拆成单独风险项 / 并入 SP-09 和架构冻结评审。
   - 不确认的影响：容易把合成状态机 Pass 误读为生产同步能力已就绪。

## 整改建议

- 不要求专项会话返工核心技术内容。
- 建议在后续 Spike 证据包统一增加 `README.md` 或 `MANIFEST.md`；P2-006 已有 `SP-06_report.md`，本次作为轻量证据入口接受。
- 后续若用户希望完全对齐最新证据规范，可补一个 `lifeos/spikes/SP-06/MANIFEST.md`，仅做路径索引，不改变技术结论。

## 可接受内容

- 最小同步合同可作为后续 SP-07 / SP-08 / SP-09 输入。
- 字段级 LWW 不得用于原文、用户确认、Action / Decision / Link / Feedback 等权威语义。
- 队列只作为执行辅助，不作为权威状态来源。
- tombstone、Authorization、policy、Source restriction、lease 和对象版本必须在发布前重检。
- AI 候选不能自动转为用户确认对象，用户反馈必须追加历史并可重算当前状态。
- 不安全自动合并必须降级为显式冲突或用户处理。

## 不接受或需谨慎内容

- 不接受把 SP-06 Pass 外推为生产多设备同步已可上线。
- 不接受冻结同步协议、Schema、API、队列实现、租约实现或云端权威范围。
- 不接受进入正式 MVP 开发。
- 不接受把 L3 候选物化作为 V1 默认能力。
- 不接受用字段级 LWW 简化用户权威对象冲突。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：暂不更新。
- `lifeos/PM_OPERATING_MODEL.md`：暂不更新。
- `lifeos/TASK_REGISTRY.md`：将 LIFEOS-P2-006 从 Ready 更新为 Accepted。
- `lifeos/DECISION_LOG.md`：新增 D-0103，记录 PM 接受 P2-006 并建议 SP-07。
- `lifeos/FREEZE_STATUS.md`：将 SP-06 更新为 Accepted but Not Frozen，等待用户确认是否采纳。
- `lifeos/RISK_LOG.md`：暂不更新；生产原子性、租约、冲突 UI、容量等风险可在架构冻结前统一整理。
- `lifeos/OPEN_QUESTIONS.md`：暂不更新。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P2-006。

## 下一步任务建议

- 用户确认采纳 P2-006 后，启动 SP-07：混合搜索、Project 恢复包与可信建议证据。
- SP-07 应继承 SP-03 证据链、SP-04 授权判定、SP-05 删除 / 撤回传播、SP-06 同步状态一致性，重点验证搜索与恢复包不会展示失效证据、冲突分支、撤回内容或旧队列输出。
- 正式 MVP 开发仍保持 Blocked / Not Allowed。
