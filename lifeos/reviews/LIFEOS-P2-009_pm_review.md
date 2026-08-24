# LIFEOS-P2-009｜SP-09 容量与性能技术 Spike PM Review

## 验收信息

- 任务 ID：LIFEOS-P2-009
- 任务名称：SP-09 100 万内容单元 / 300 万分块容量与性能技术 Spike
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P2-009_sp09_capacity_performance_spike_report.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P2-009_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Pass with Conditions
- 是否允许进入下一任务：Conditional
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 更新时间：2026-08-09

## PM 总结

1. P2-009 完成了 SP-09 的核心目标：在合成数据下实际运行 1 万 / 10 万 / 100 万内容单元与 3 万 / 30 万 / 300 万分块三档验证，不是仅靠外推。
2. PM 复跑 `python3 lifeos/spikes/SP-09/run_spike.py --tiers 10000,100000 --full --keep-work`，结果与交付物一致：1 万、10 万档通过；100 万档仅 `capture_during_full_fts_rebuild_under_one_second` 失败；脚本返回非零属于已知条件失败。
3. 核心安全底线未失败：权限过滤、墓碑优先、撤回 / 删除不复活、旧 generation 不活跃、日志隐私扫描均满足任务最低断言。
4. 关键条件失败成立且表达清楚：100 万档全量 FTS rebuild 阻塞捕获约 4 秒，超过“后台维护不阻塞捕获 1 秒”的候选门槛。
5. 因此 PM 结论为 `Accepted`，但资产状态只能是 `Pass with Conditions`，不能视为无条件技术通过，更不能冻结技术架构或进入正式 MVP 开发。
6. SP-09 可作为技术架构候选综合评审和 Stage 2 收口判断的重要输入；下一步应先由用户确认是否采纳，再启动技术架构候选综合评审任务。
7. 证据包 README 存在一个小路径不一致：`resource_summary.md`、`failure_samples.md` 实际位于 `lifeos/spikes/SP-09/` 根目录，而非 `evidence/` 下。该问题不影响核心验证，但后续可在采纳后顺手修正。

## 角色与关卡验收

- 主责角色覆盖情况：覆盖。容量、性能、查询、删除、备份、恢复、索引重建、向量成本、未验证边界与架构触发阈值均有明确结论。
- 协审角色覆盖情况：覆盖。数据 / 领域模型、AI 信任与安全、产品架构、体验设计四类视角均有自检。
- 已通过关卡：
  - Gate 2 数据与来源评审：Pass（限合成规模与恢复语义层）。
  - Gate 3 AI 权限与信任评审：Pass（限本地运行时门控层）。
- 未通过或需后续确认关卡：
  - Gate 4 技术可行性评审：Pass with Conditions。SQLite / FTS5 主路径可行，但全量 FTS rebuild 阻塞前台捕获；PostgreSQL、pgvector、ANN、真实长文、附件、冷缓存、跨平台和生产并发仍未验证。
- 是否属于关键冻结事项：是，影响技术架构候选与正式 MVP 开发准入。
- 是否需要独立评审：需要，但不是本任务内完成。建议下一任务进入技术架构候选综合评审 / Stage 2 收口判断。
- 独立评审路径：待创建。
- 独立评审结论：未开始。
- 是否允许进入下一任务或下一阶段：允许进入下一任务；不允许进入下一阶段。

## 验收与冻结区分

- 任务是否验收通过：通过，状态为 `Accepted`。
- 对应资产是否冻结：不冻结，状态为 `Pass with Conditions`。
- 冻结范围：无。
- 未冻结内容：
  - 技术架构；
  - SQLite / PostgreSQL / pgvector 选型；
  - Schema / API / 队列 / 备份方案；
  - FTS 模式、索引维护策略、向量维度、分块策略；
  - 性能 SLA、容量承诺、备份 / 灾备 SLA；
  - 正式 MVP 开发准入。
- 是否允许进入下一任务：Conditional。用户确认采纳 P2-009 后，建议启动技术架构候选综合评审与 Stage 2 收口判断。
- 是否允许进入下一阶段：No。Stage 3 仍需技术架构评审、条件整改、PM/用户确认和冻结。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：需要。

## 需要用户确认的事项

1. 问题：是否采纳 P2-009 / SP-09 的 `Pass with Conditions` 结论？
   - PM 建议：采纳。
   - 可选方向：采纳并进入技术架构候选综合评审；或要求专项会话先修正 README 小路径问题并补充说明后再采纳。
   - 不确认的影响：无法把 SP-09 作为 Stage 2 收口和架构评审输入。

2. 问题：是否接受 V1 技术候选方向先采用 FTS-first，而非把向量作为默认硬依赖？
   - PM 建议：接受为候选输入，不冻结为最终架构。SP-07 未证明向量净增益，SP-09 显示全量高维向量成本显著。
   - 可选方向：FTS-first；部分高价值内容向量覆盖；后续真实授权标注集再评估语义检索。
   - 不确认的影响：技术架构评审会在“向量是否硬依赖”上继续悬空。

3. 问题：是否将“全量索引维护不能阻塞前台权威捕获超过 1 秒”列为技术架构冻结前必须整改条件？
   - PM 建议：列为必须整改条件。
   - 可选方向：影子索引 / 影子数据库短切换；维护窗口；分段可中断维护；权威短事务落盘 + 异步索引。
   - 不确认的影响：正式开发可能把长写锁体验问题带入产品地基。

4. 问题：是否允许下一步启动技术架构候选综合评审与 Stage 2 收口判断？
   - PM 建议：用户采纳 P2-009 后启动。
   - 可选方向：先做架构综合评审；或先补 PostgreSQL/pgvector 专项验证；或先做 SP-09 条件补丁。
   - 不确认的影响：Stage 2 无法有序收口。

## 整改建议

- 非阻断整改：修正 `lifeos/spikes/SP-09/README.md` 中 `resource_summary.md` 与 `failure_samples.md` 的路径说明。
- 架构前置整改条件：下一步技术架构候选评审必须处理全量 FTS rebuild 阻塞捕获的问题，不能用“用户等一下”作为正式方案。
- 后续验证缺口：PostgreSQL / FTS、pgvector / ANN、真实长文、附件、冷缓存、跨平台、生产并发和恢复磁盘峰值仍需在架构评审中明确是“后续验证项”还是“V1 移出范围”。

## 可接受内容

- 100 万内容单元 / 300 万分块的合成 SQLite + FTS5 实测结果。
- FTS-first 作为 V1 本地与早期搜索地基候选输入。
- 向量默认后置、不作为 V1 硬依赖的候选判断。
- 权限过滤、墓碑优先、撤回 / 删除不复活在规模查询中的门控模式。
- 可重建派生物不作为用户权威资产的容量策略。
- 技术架构触发阈值与禁止优化清单。

## 不接受或需谨慎内容

- 不接受将本次 SQLite / FTS5 结果外推为正式技术架构冻结。
- 不接受将热缓存、单机、短文本、单进程结果外推为生产 SLA。
- 不接受将 PostgreSQL / pgvector / ANN 视为已验证。
- 不接受用关闭耐久、取消权限过滤、绕过 tombstone、先返回再撤回等方式换性能。
- 不接受把 SP-09 完成直接等同于 Stage 3 MVP 开发准入。

## 对项目文件的更新建议

- `lifeos/PROJECT_CONTEXT.md`：暂不更新。
- `lifeos/PM_OPERATING_MODEL.md`：暂不更新。
- `lifeos/TASK_REGISTRY.md`：将 P2-009 更新为 Accepted。
- `lifeos/DECISION_LOG.md`：新增 D-0109，记录 PM 验收与条件。
- `lifeos/FREEZE_STATUS.md`：将 SP-09 更新为 Pass with Conditions；MVP 开发准入继续 Blocked / Not Allowed。
- `lifeos/CURRENT_STATUS.md`：更新为等待用户确认是否采纳 P2-009。
- `lifeos/RISK_LOG.md`：后续技术架构评审时建议补充，不在本次直接更新。
- `lifeos/OPEN_QUESTIONS.md`：后续技术架构评审时建议补充，不在本次直接更新。

## 下一步任务建议

用户确认采纳 P2-009 后，建议启动：

`LIFEOS-P2-010｜技术架构候选综合评审与 Stage 2 收口判断`

该任务应综合 SP-01 至 SP-09，形成技术架构候选、条件整改清单、不可冻结项、Stage 2 是否可收口，以及 Stage 3 开发准入仍缺哪些前置。
