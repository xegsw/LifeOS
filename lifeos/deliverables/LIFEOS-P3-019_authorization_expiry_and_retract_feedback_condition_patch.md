# LIFEOS-P3-019｜授权 expires_at 与 retract_feedback 条件补丁报告

## 任务信息

- 任务 ID：LIFEOS-P3-019
- 任务名称：P1-7 条件补丁：授权 `expires_at` 与 `retract_feedback`
- 执行 Agent：Codex
- 任务类型：P3 Engineering Fast Lane / P1 条件补丁 / 工程硬化 / 回归测试
- 更新时间：2026-08-11
- 专项结论：**Pass（需 PM 验收）**

## 修复 / 验证目标

- 为受控 Authorization 增加可空 `expires_at_ms`，并由统一消费门按确定性时钟判断有效性。
- 让已过期授权一致阻断所有已实现消费及写入口，同时保留无期限授权的原行为。
- 增加用户显式、幂等的 feedback 撤回；保留历史记录并取消 Derivation 的用户确认语义。
- 证明撤回不会复活 stale、invalid 或授权失效的 Derivation，且原 30 项回归保持通过。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-009/src/store.ts`
- `lifeos/engineering/LIFEOS-P3-009/src/consumption-gate.ts`
- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`
- `lifeos/engineering/LIFEOS-P3-009/evidence/` 下指定 evidence 文件

未修改 `src/types.ts`：确定性时钟是 `LifeOS` 的受控运行依赖，Authorization 过期值保存在 SQLite 权威行中，无需扩大公共上下文类型。

## P1-7 条件关闭说明

**[已验证事实]** Authorization 新增可空整数 `expires_at_ms`。`NULL` 延续既有非过期行为；当 `expires_at_ms <= now` 时，统一 `canConsume()` fail closed。`LifeOS` 构造器可注入 `nowMs`，测试使用固定时间，不依赖系统时钟。

**[已验证事实]** `read`、`search`、`recovery`、`suggest`、`feedback`、`exportMemory`、`restoreCandidates` 与 `createImportantLink` 均通过同一消费门或其组合路径阻断过期授权。Authority projection 同步携带 `expires_at_ms`，恢复候选会对当前值、包内值与当前有效性重新核对。过期后不会写入 active feedback、important link，也不会返回旧 Derivation 或恢复候选。

**[已验证事实]** 新增 `retractFeedback(feedbackId, "user")`，运行时拒绝非用户 actor。首次撤回把行状态从 `active` 改为 `retracted`，重复撤回返回同一状态且不新增/删除记录。若原状态为 `confirmed` / `edited_confirmed`，Derivation 改为非可消费的 `feedback_retracted`；若已是 `stale` / `invalid`，保持原状态，避免撤回复活。`suggest`、导出与恢复候选均排除 `feedback_retracted`。

**[合理推断]** P1-7 已在合成、单进程、受控测试包边界内满足授权到期与反馈撤回条件；这不代表生产时间权威、正式权限策略或真实审计 UI 已实现。

## 测试摘要

- 直接复跑：`node --experimental-strip-types --test tests/invariants.test.ts`
- Evidence 生成：`node scripts/validate.mjs`
- 最终结果：**34 PASS / 0 FAIL；P0 FAIL=0**。
- 原有回归：30/30；新增 P1-7：4/4；P1-6：5/5；P1-8：4/4；P1-4：2/2；P3-015：1/1；P1-3 / P1-5：4/4；H1-H9 / T-ARCH 全部通过。
- 新增覆盖：无期限/未来期限放行；到期时八类入口阻断；显式幂等撤回及历史保留；撤回后 confirmed/corrected/stale/过期 Derivation 不复活。
- Snapshot：`332e9e47382f8c403a89695398779b6e9d6f682d37f867d850390aece0e00f6c`。
- 异常：仅有 `node:sqlite` experimental warning；系统无全局 Node，使用 Codex bundled Node v24.14.0 复跑，不影响测试语义。

## Evidence 更新

- Manifest：`lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- 机器结果：`lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- 原始日志：`lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- 矩阵：`invariant_migration_matrix.md`、`architecture_conformance.md`、`default_off_matrix.md`

同次验证的 Manifest、JSON、日志和矩阵均为 34/0、原回归 30/30、P1-7 4/4；八类默认关闭能力未被破坏。

## 非范围、剩余风险与角色关卡

- 未实现真实时间服务、后台调度、通知、自动扫描/清理、真实 UI、正式审计、正式权限策略、多设备同步或生产 SLA。
- 未启用真实数据、Vault、Tauri / IPC、文件导出、云 / 第三方模型、向量、同步、多设备、L3 或外部用户；未修改 P3-001 或项目账本。
- 未冻结 Schema、API、模块边界、导出格式或工程基线；R-0040 保持 Open / Conditional。
- 工程负责人、数据与权限、AI 信任与安全、QA 关卡：**Pass（受控边界）**；技术架构：**Pass with Conditions**，真实时间权威及 R-0040 仍在边界外。任务卡指定无需独立复评，最终仍需 PM 验收。

## 本地预检

已按规则调用，状态为 **Skipped / Local Model Unavailable**，错误为 `[Errno 54] Connection reset by peer`，符合允许跳过场景，不阻塞工程交付。报告：`lifeos/local_prechecks/LIFEOS-P3-019_LIFEOS-P3-019_authorization_expiry_and_retract_feedback_condition_patch_local_precheck.md`。该结果不替代 PM Review。

## 是否触发用户确认与结论

- 是否触发用户级确认：**No**。未涉及 P0、风险关闭、工程基线恢复、真实能力启用、阶段切换或关键冻结边界变化。
- 最终结论：**Pass（需 PM 验收）**。专项会话不关闭 R-0040、不更新账本、不启动后续任务。
