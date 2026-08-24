# LIFEOS-P3-017 PM Review

## 验收信息

- 任务 ID：LIFEOS-P3-017
- 任务名称：P1-8 条件补丁：suggestion ID 完整 generation 绑定
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-017_suggestion_id_full_generation_binding_condition_patch.md`
- PM Review 路径：`lifeos/reviews/LIFEOS-P3-017_pm_review.md`
- 任务验收状态：Accepted
- 资产冻结状态：Accepted but Not Frozen
- 是否允许进入下一任务：Yes
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 实际执行 Agent：Codex
- Agent 与任务匹配度：High
- 更新时间：2026-08-11

## PM 总结

- P3-017 按任务卡完成 P1-8：`suggest()` 的 ID 已从旧的主证据倾向切换为 `suggestion:v2:<sha256>`，由 Project 与完整可消费输入集合稳定生成。
- ID payload 等价绑定每个输入的 evidence version、Artifact、Source、artifact generation、source generation，并对输入集合做稳定排序。
- PM 复跑 P3-009 测试：25 PASS / 0 FAIL / P0=0；与专项报告和 evidence manifest 一致。
- PM 定向复现 5 组关键场景均 PASS：顺序稳定、非主 Artifact generation 变化、非主 Source generation 变化、输入集合变化、direct-deny 旧建议阻断。
- 本任务未迁移 P1-6 / P1-7，未修改 P3-001，未启用真实 Tauri / IPC、真实 Vault、真实数据、云 / 第三方模型、向量、同步、多设备、L3 或外部用户。
- R-0040 保持 Open / Conditional；本验收不关闭风险、不恢复或冻结新的工程基线、不进入下一阶段。
- 本地预检因本地模型连接重置跳过，不作为 PM 验收依据。

## P3 快车道 Review

- 是否适用 P3 快车道：Yes
- 验收结论：Accepted
- 测试复跑摘要：`/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --experimental-strip-types --test tests/invariants.test.ts`，25 PASS / 0 FAIL / P0=0
- 是否存在 P0：No
- P1 / P2 是否可留在快车道：Yes
- 风险状态是否变化：No；R-0040 仍为 Open / Conditional
- 是否触发用户确认：No
- 是否允许继续下一工程补丁：Yes
- 修改文件：任务交付物声明修改 `src/lifeos.ts`、`tests/invariants.test.ts`、`scripts/validate.mjs` 与 P3-009 evidence 文件；PM 本轮更新 PM Review 与项目账本
- evidence 路径：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- Agent 适配度记录：Codex 与 P3 快车道工程补丁匹配度 High
- 是否必须退出快车道：No

## 角色与关卡验收

- 主责角色覆盖情况：工程负责人覆盖。代码集中在 suggestion ID 规范化、完整输入绑定、稳定排序和 hash 生成；未顺手迁移 P1-6 / P1-7。
- 协审角色覆盖情况：数据与权限、AI 信任、QA / 测试、技术架构均覆盖。
- 已通过关卡：P1-8 suggestion ID 完整 generation 绑定；P1-4 staling 回归；P3-015 suggest 旧候选消费门回归；P1-3 / P1-5 回归；H1-H9 / T-ARCH 回归；evidence manifest 更新；默认关闭能力回归。
- 未通过或需后续确认关卡：P1-6 / P1-7 仍未迁移；真实 Tauri / IPC 仍未验证；R-0040 未关闭。
- 是否属于关键冻结事项：No
- 是否需要独立评审：No；P3 快车道适用，未发现 P0 或退出快车道条件
- 独立评审路径：不适用
- 独立评审结论：不适用
- 是否允许进入下一任务或下一阶段：允许进入下一 P1 / P2 窄工程补丁；不允许进入下一阶段

## 验收与冻结区分

- 任务是否验收通过：Yes，Accepted
- 对应资产是否冻结：No，Accepted but Not Frozen
- 冻结范围：无
- 未冻结内容：生产 Schema、API、模块边界、真实 Tauri / IPC、真实 Vault、真实数据、导出格式、生产 SLA、工程基线扩展
- 是否允许进入下一任务：Yes
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：Yes
- 是否需要更新 `lifeos/FREEZE_STATUS.md`：Yes

## 需要用户确认的事项

无强制确认事项。

## 整改建议

无本任务内必须返工项。

## 可接受内容

- P1-8 在 P3-009 合成、单进程、受控测试包边界内可接受。
- suggestion ID 现在稳定绑定 Project 与完整输入集合，不再只依赖首个输入、主证据或 `artifact_generation ?? 1` fallback。
- 同一输入集合不同顺序得到同一 ID；非主 Artifact / Source generation 变化得到新 ID，并使旧 Derivation stale / 阻断。
- 已确认 suggestion 的重复调用仍保留确认状态和 active feedback，不静默重置为 candidate。

## 不接受或需谨慎内容

- 不得把 P3-017 的通过理解为 P1-6 / P1-7 已迁移。
- 不得把合成单进程测试通过外推为真实 Tauri / IPC、真实 Vault、真实模型或生产并发通过。
- 不得关闭 R-0040。
- 不得恢复或冻结新的工程基线。

## 对项目文件的更新建议

- `lifeos/TASK_REGISTRY.md`：更新 P3-017 为 Accepted。
- `lifeos/FREEZE_STATUS.md`：更新 P1-8 suggestion ID 完整 generation 绑定状态。
- `lifeos/DECISION_LOG.md`：新增 D-0167。
- `lifeos/CURRENT_STATUS.md`：更新当前状态和下一步建议。
- `lifeos/AGENT_ROUTING_SCORECARD.md`：追加 Codex 适配度记录。
- `lifeos/RISK_LOG.md`：不更新；R-0040 保持 Open / Conditional。

## Agent 分派与适配度评估

- 本任务推荐 Agent：Codex
- 本任务实际执行 Agent：Codex
- 是否符合推荐：Yes
- Agent 与任务类型匹配度：High
- 主要优势：工程实现、测试覆盖、evidence 更新、短报告边界控制均符合 P3 快车道要求。
- 主要问题：本地预检不可用；Codex 仍不应作为自己后续高风险独立复评者。
- 以后更适合分派给该 Agent 的任务类型：P3 快车道工程补丁、受控测试迁移、evidence 更新、回归测试。
- 不建议分派给该 Agent 的任务类型：对自己刚完成工程的高风险独立复评。
- 是否需要更新 `lifeos/AGENT_ROUTING_SCORECARD.md`：Yes

## 下一步任务建议

建议继续 P3 快车道，优先处理：

- 候选：P1-6 restore candidates、权威投影与旧包不复活。

P1-7 授权 `expires_at` 与 `retract_feedback` 可作为其后下一项。
