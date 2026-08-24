# LIFEOS-P3-044 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-044
- 任务名称：Active Authorization 替换／重建旁路 P1 整改与回归
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression.md`
- Evidence manifest：`lifeos/engineering/LIFEOS-P3-044/evidence/MANIFEST.md`
- 本地预检：`lifeos/local_prechecks/LIFEOS-P3-044_LIFEOS-P3-044_active_authorization_replace_rebuild_bypass_p1_remediation_and_regression_local_precheck.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-044_pm_review.md`
- 任务验收状态：Accepted / Remediation Regression Passed
- 资产冻结状态：Accepted but Not Frozen / Pending Independent Re-review
- 是否允许进入下一任务：Conditional；用户采纳本 P0 整改结论后，只允许创建 P3-045 隔离独立工程复评
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes；仅作为 P3-045 独立复评输入
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-20

## PM 总结

- 专项会话按任务卡使用 `gpt-5.6-sol` + `xhigh`，未降级，并严格限定在 P3-031 当前候选 SQL/tests/evidence 与新建 P3-044 受控回归包内。
- 当前候选 SQL 增加 `authorization_no_replace_while_active` 与 `authorization_no_delete_while_active`：前者在 SQLite conflict resolution 的隐式删除前拒绝与既有 active 父记录发生 id 或 `(logical_key, version_no)` 冲突的 INSERT/REPLACE；后者拒绝直接删除 active 父记录。
- PM 在独立临时项目树复跑 P3-044 总入口，退出码为 0；P3-031、P3-040 current、P3-042 current 三套回归退出码均为 0。
- P3-044 专属结果为 P1 160 PASS、P2 40 PASS + 18 Known Limitation、P3 2 Observation；无 FAIL、Not Implemented 或 Unknown。共 220 个实例，文件库 integrity/quick/FK 检查全部通过。
- PM 额外手工验证版本唯一键替换、partial active logical index 冲突和直接 DELETE：分别稳定返回 `active_authorization_replace_forbidden`、`authorization_must_start_inactive` 和 `active_authorization_delete_forbidden`；原 active 父记录及三类子表保持不变。
- 当前 candidate、snapshot、tests、runner 与 evidence 关键 hash 均和 manifest/source_hashes 一致；P3-043 七个受保护文件 hash 保持不变。
- 本任务没有关闭任何风险，没有冻结 Schema/API 或工程基线，没有启用真实 DB/Vault/Tauri/IPC 或进入下一阶段。
- 由于本任务属于 P0 优先级权限整改，执行自检与 PM 复跑通过后仍必须经 P3-045 隔离独立复评；用户确认前不创建 P3-045。

## P3 快车道 Review

- 是否适用 P3 快车道：No
- 原因：任务涉及权限与证据链核心边界的 P0 优先级整改，并要求隔离独立复评，必须使用完整 PM Review。

## 测试与 Evidence 复核

### PM 独立复跑

- 复跑方式：复制 P3-031/P3-040/P3-042/P3-044 及直接依赖到 `/tmp/lifeos-p3044-pm.kDiqtF/`，在临时项目树运行 P3-044 总入口，未覆盖专项会话 evidence。
- 总入口退出码：0。
- P3-031 current：46/46 PASS，退出码 0。
- P3-040 current：128/128 PASS，退出码 0。
- P3-042 current：52 PASS + 26 P2 Known Limitation，退出码 0。
- P3-044：200 PASS、18 P2 Known Limitation、2 P3 Observation；P1 为 160/160 PASS。
- P0/P1 FAIL：0。
- Not Implemented / Unknown：0 / 0。

### 定向攻击

- 相同 `(logical_key, version_no)`、不同 id 的 REPLACE 被 replacement trigger 拒绝。
- 不同版本、不同 id、相同 logical key 的 direct-active REPLACE 被 direct-active contract 拒绝，不能利用 partial unique index 删除旧 active 行。
- 直接 DELETE active 父记录被 delete trigger 拒绝。
- 三次拒绝后原父记录保持 `('auth1','logical1','active','local',1)`，scope/action/policy 数量保持 1/1/1。

### Evidence 完整性

- `candidate_source` 与 P3-044 snapshot 均为 `0b7f3393...aa0d376`。
- P3-031 contract tests 为 `58a4cb97...760ba9`。
- P3-044 runner 为 `1e297a9e...2774c3`。
- 交付报告列出的 test results、test log、environment、integrity/FK、source hashes 和 P3-043 preservation hash 均与当前文件一致。
- 本地预检因局域网模型连接超时标记 `Skipped / Local Model Unavailable`；符合允许跳过条件，PM 已人工完成任务卡、报告、SQL、测试、manifest、结构化结果、hash 与独立复跑核对。

## 角色与关卡验收

- 主责角色覆盖情况：通过；真实 SQLite trigger、稳定错误、冲突键矩阵、PRAGMA/后端/事务组合、失败原子性和合法 successor 路径均有实现与 evidence。
- 协审角色覆盖情况：通过执行层验收；授权父表安全包络未通过替换/重建被静默改写，R-0048/R-0049 被保留为非范围，原始评审 evidence 未被污染。
- Gate 2 数据与来源：Pass for Remediation Candidate；父/子/evidence 原子状态和历史证据保留成立，最终状态待独立复评。
- Gate 3 AI 权限与信任：Pass for Remediation Candidate；已知替换/重建 P1 在当前候选和受控矩阵内关闭，最终权限边界结论待 P3-045。
- Gate 4 技术可行性：Pass for Remediation Candidate；合成内存/文件 SQLite 与 FK/recursive/事务矩阵成立，不外推到真实 migration、并发/WAL、崩溃恢复或跨平台。
- 是否属于关键冻结事项：No；本任务不冻结 Schema/API，但涉及高风险权限边界。
- 是否需要独立评审：Yes，P3-045。
- 独立评审路径：尚未创建。
- 独立评审结论：Pending。

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted / Remediation Regression Passed。
- 对应资产是否冻结：No。
- 冻结范围：无。
- 未冻结内容：生产 Schema/API、候选 SQL migration、Authorization 权限合同、Tauri capability/IPC、真实 migration、工程基线和生产 SLA。
- 是否允许进入下一任务：Conditional；用户采纳后只能进入 P3-045 隔离独立复评。
- 是否允许进入下一阶段：No。
- 是否只是后续任务输入：Yes。
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：No；没有核心资产冻结状态变化。

## 风险状态

- R-0044：从 Reopened / Rework 更新为 Reopened / Remediation Candidate；不关闭。
- R-0047：从 Open / Rework 更新为 Open / Remediation Candidate；不关闭。
- R-0050：从 Open / Remediation Ready 更新为 Open / Remediation Candidate；不关闭。
- R-0043、R-0046：保持 Closure Candidate，不关闭。
- R-0048、R-0049：保持 Open / Known Limitation；18 个 P2 Known Limitation 继续保留。
- R-0040 保持 Open / Conditional，R-0045 保持 Closed。

## 需要用户确认的事项

- 问题：是否采纳 P3-044 的 `Accepted / Remediation Regression Passed` 结论，并创建 P3-045 隔离独立工程复评。
- PM 建议：采纳并创建 P3-045；由未参与 P3-044 执行的新建 WorkBuddy 隔离会话进行反例攻击和 evidence 复核。
- 不确认的影响：P3-044 保持已完成但未获得用户采纳，R-0044/R-0047/R-0050 保持开放，不能进入风险关闭或 Schema/API 后续判断。

## 可接受内容

- active 父记录冲突 INSERT/REPLACE 的 fail-closed `BEFORE INSERT` 合同。
- active 父记录直接 DELETE 的 fail-closed 合同。
- id 与版本身份双冲突维度、FK/recursive ON/OFF、内存/文件、事务原子性测试矩阵。
- P3-043 原 P1 迁移和 P2/P3 非范围保留方式。
- 当前候选回归、hash 与 evidence manifest 可作为 P3-045 的直接输入。

## 不接受或需谨慎内容

- 不把执行自检与 PM 复跑写成风险关闭或 Schema/API 冻结。
- 不把合成 SQLite 结果外推到真实非空旧库、并发/WAL、断电、跨平台、真实 Tauri/IPC 或生产 SLA。
- 不把 R-0048/R-0049 的 P2 Known Limitation 解释为已解决。
- P3-045 通过前，不恢复/冻结新的工程基线，不关闭 R-0044/R-0047/R-0050。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex。
- 本任务实际执行 Agent：Codex。
- 是否符合推荐：Yes。
- Agent 与任务类型匹配度：High。
- 主要优势：范围纪律好；SQL trigger 设计集中；当前候选多套回归、PRAGMA/事务矩阵、hash 和原 evidence 保留完整；主动保留 P2 Known Limitation。
- 主要问题：执行者不能独立复评自己的高风险权限整改；最终反例覆盖和严重级别仍需外部独立会话确认。
- 以后更适合分派给该 Agent 的任务类型：候选 SQL 权限整改、合同测试、受控回归和 evidence 整理。
- 不建议分派给该 Agent 的任务类型：对自己刚完成的 P0 权限整改进行独立复评或风险关闭裁决。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：Yes。

## 下一步任务建议

- 用户确认采纳后创建 P3-045：Active Authorization 替换／重建旁路整改隔离独立工程复评。
- P3-045 必须新建隔离会话，原 P3-044 工程与 evidence 只读；应主动攻击冲突目标选择、trigger 顺序、UPSERT/REPLACE 变体、PRAGMA、事务保存点、合法 successor 和相邻 R-0048/R-0049 组合。
- 本轮不创建或启动 P3-045，不关闭风险，不冻结资产，不进入下一阶段。
