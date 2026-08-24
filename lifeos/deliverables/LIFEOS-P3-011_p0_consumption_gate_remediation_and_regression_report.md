# LIFEOS-P3-011｜P3-009 P0 消费门返工与回归补测报告

- 任务类型：工程返工 / P0 修复 / 回归测试
- 主责角色：工程负责人
- 协审角色：数据与权限、AI 信任与安全、QA / 测试、技术架构负责人
- 日期：2026-08-11
- 结论：**Pass with Conditions**

## 1. 任务摘要

1. **[事实]** 已用最小查询改动修复 `canConsume()`：匹配当前 subject / purpose / location / processor / generation 的授权集合必须“总计恰好一行且该行是 allow”才放行。因此 allow+deny、allow+unknown、duplicate allow、仅 deny、仅 unknown、缺失授权均 fail closed。
2. **[事实]** 新增 4 项回归测试：2 项 P0 覆盖授权冲突、异常授权集合及 read / search / recovery / suggest / exportMemory；2 项 P1 覆盖重复建议的确认轨迹保持与非 candidate derivation 的 feedback 写入口拒绝。
3. **[事实]** 最终验证为 **14 PASS / 0 FAIL，P0 FAIL=0，P1 OPEN=0**；P3-009 原有 10 项测试全部继续通过，八类默认关闭能力负测继续通过。
4. **[事实]** P1-1、P1-2 已以窄范围修复；P1-3 至 P1-8 未扩散实现，保留为后续迁移清单。
5. **[事实]** 未修改 P3-001 或项目账本；未启用真实 Vault、Tauri / IPC、文件导出、真实数据、外部模型、向量、同步、多设备、L3 或外部用户。
6. **[推断]** 本次补丁关闭了 P3-010 指定的 P0 与两个同范围 P1，但 P3-009 是否恢复为工程基线候选仍必须经过独立复评和 PM 确认。

## 2. 修改文件清单

工程代码与测试：

- `lifeos/engineering/LIFEOS-P3-009/src/consumption-gate.ts`
- `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts`
- `lifeos/engineering/LIFEOS-P3-009/tests/invariants.test.ts`
- `lifeos/engineering/LIFEOS-P3-009/scripts/validate.mjs`

验证脚本刷新 evidence：

- `lifeos/engineering/LIFEOS-P3-009/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-009/evidence/test_run.log`
- `lifeos/engineering/LIFEOS-P3-009/evidence/invariant_migration_matrix.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/default_off_matrix.md`
- `lifeos/engineering/LIFEOS-P3-009/evidence/architecture_conformance.md`

本报告为唯一新增的 `lifeos/deliverables/` 文件。**[事实]** P3-001 的既有 snapshot manifest 共 7 个文件，修复后只读重算结果为 0 mismatch，snapshot ID 仍为 `ff526a340443057ad56abec75e30f44a387b4cdb3e3850464cc2890b9ff173fd`。

## 3. P0 根因与修复说明

### 根因

**[已验证事实]** 原查询在 SQL `WHERE` 中先过滤 `decision='allow'`，只要求 allow 计数等于 1。于是相同授权上下文同时存在一行 allow 和一行 deny 时，deny 对计数不可见，门仍返回 true。P3-010 的 AD-1 及 PM 复现已证明旧实现会从 `read()` 返回用户原文，构成本任务的修复前失败证据。

### 修复

新查询在完整匹配上下文内统计授权总行数与 allow 行数，只有 `total === 1 && allow_count === 1` 时通过。这个判定同时覆盖：

- allow+deny、allow+unknown 或多行 allow：总数不为 1，拒绝；
- 仅 deny、仅 unknown：allow 数不为 1，拒绝；
- 缺失授权：总数为 0，拒绝；
- generation、purpose、location、processor 错配：无法形成当前上下文唯一 allow，拒绝。

**[边界]** 未改变 Authorization 对象体系、表结构或 API；未将实现细节声明为 Schema / API 冻结。

## 4. 新增 / 修改测试清单

| 测试 | 级别 | 覆盖结论 |
|---|---|---|
| `P0 T-GATE allow+deny conflict blocks every consumption entry` | P0 | 冲突后 read 返回 null；search / recovery 为空；suggest 为 null；exportMemory 无 artifact / derivation 且不含用户原文 |
| `P0 T-GATE missing duplicate or unknown authorization fails closed` | P0 | missing、duplicate allow、allow+unknown 三类授权集合均拒绝 |
| `P1 T-ID repeated suggestion preserves confirmation and feedback trace` | P1 | 重复 suggest 保持同一 ID、confirmed 状态、active feedback，且 Derivation 只有一行 |
| `P1 T-WRITE-GATE feedback rejects non-candidate derivation explicitly` | P1 | 即使证据仍可消费，status=stale 的 Derivation 也不得写 Feedback |

P0 测试不是 happy path：它直接复现冲突/不确定授权集合，并逐一经过所有已实现消费入口。原有 10 项 H1-H9 / T-ARCH 测试未经删除或改名，最终全部继续通过。

## 5. 测试命令与结果摘要

```bash
cd lifeos/engineering/LIFEOS-P3-009
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --experimental-strip-types --test tests/invariants.test.ts
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs
```

- 环境：macOS arm64；Node v24.14.0；内建 `node:sqlite`。
- 结果：14 tests / 14 pass / 0 fail；P0 fail 0；P1 open 0。
- 原有测试：10 / 10 继续通过。
- 新增测试：4 / 4 通过。
- Evidence snapshot：`26eae1f16ffb4bf61c824ecf59552066fb063fcb7b981a0f0694f7b85bf62881`。
- 已知非阻断提示：`node:sqlite` 仍输出 experimental warning；这不是生产依赖冻结依据。

## 6. Evidence 更新清单

`validate.mjs` 已将机器结果标记为 P3-011 对 P3-009 的 remediation run，并刷新测试日志、逐文件 SHA-256 与 snapshot。`MANIFEST.md` 的 14/0、运行时间和 snapshot 与 `test_results.json`、`test_run.log` 一致。迁移矩阵、默认关闭矩阵和架构符合性文件由同次脚本重生；八项关闭能力仍均为 false 且运行时抛出 `DisabledCapability`。

## 7. P1-1 / P1-2 处理结果

### P1-1：已修复

`suggest()` 从 `INSERT OR REPLACE` 改为 `INSERT OR IGNORE`，冲突时保留既有 Derivation；随后读取并返回当前 status。`feedback(confirm / edit_confirm / reject / correct)` 同步更新 Derivation 状态。重复恢复页面不再把 confirmed 候选重置为 candidate，也不删除或孤立既有 Feedback。

### P1-2：已修复

`feedback()` 现在显式要求 `d.status === 'candidate'`，再执行 Project 和 evidence 消费门检查。stale、confirmed、edited_confirmed、invalid 等非候选状态均不得继续写入。修复未引入 `derivation_input` 或复杂 generation staling。

## 8. P1-3 至 P1-8 后续迁移清单

以下均**未在本任务实现**：

1. P1-3：多证据 `derivation_input` 与非主证据撤回传播。
2. P1-4：独立 generation mismatch staling 机制。
3. P1-5：`important_link` 及其写入口门。
4. P1-6：restore_candidates、权威投影与旧包不复活。
5. P1-7：授权 `expires_at` 与 `retract_feedback`。
6. P1-8：suggestion ID 的完整 generation 绑定；当前 fallback generation 仍未迁移。

**[建议，需 PM 后续另立任务]** 独立复评若通过，再按风险顺序迁移上述历史防线；本会话不创建或启动后续任务。

## 9. 未启用真实能力声明

**[事实]** 本任务只使用可丢弃合成夹具与内存/受控 SQLite 测试路径。未读取或写入真实 Obsidian Vault、真实用户数据或真实系统路径；未接入 Tauri / IPC、文件系统导出、云 / 第三方模型、向量、同步、多设备、L3、外部自动化或外部用户。R-0040 与 R-0042 未关闭。未冻结 Schema、API、模块边界、Tauri 配置、导出格式、生产 SLA 或工程基线。

## 10. 本地预检

已按项目规则调用 `python3 lifeos/tools/local_precheck.py` 检查本报告。预检状态为 **Skipped / Local Model Unavailable**，错误为 `[Errno 54] Connection reset by peer`，符合允许跳过场景且不阻塞交付。预检报告：`lifeos/local_prechecks/LIFEOS-P3-011_LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report_local_precheck.md`。本地预检不替代 PM Review 或后续独立复评。

## 11. 角色检查点与关卡

- **工程负责人：Pass。** P0 以最小查询改动关闭；测试、脚本与 evidence 可复跑；写入范围受控。
- **数据与权限负责人：Pass（合成边界）。** deny/conflict/duplicate allow/missing/unknown 全部 fail closed；read/search/recovery/suggest/exportMemory 复用 `read()` → `canConsume()` 门。
- **AI 信任与安全负责人：Pass（本任务边界）。** 重复建议不再静默重置确认状态；非 candidate feedback 显式拒绝；P1-3 至 P1-8 未冒充完成。
- **QA / 测试负责人：Pass。** 修复前失败由 P3-010 AD-1 和 PM 复现支持；修复后 14/14，P0=0，evidence 三方一致。
- **技术架构负责人：Pass with Conditions。** 未冻结实现细节、未启用真实能力；仍需独立复评，R-0040 保持 Open / Conditional。
- **关卡：** P0 修复验证通过；回归测试通过；P1 同范围修复评估通过；evidence manifest 更新通过；默认关闭能力回归通过。工程基线恢复与风险关闭仍需 PM / 后续独立评审确认。

## 12. 结论

**Pass with Conditions。** P0 allow+deny 冲突已 fail closed，异常授权集合及所有已实现消费入口有可执行回归；原有 10 项与新增 4 项测试全部通过，P0 失败为 0；P1-1 / P1-2 已完成窄范围修复；真实能力仍全部关闭。条件是：本结论仅限合成、单进程、受控测试包，且必须由不同 Agent 独立复评并经 PM 确认后，才能判断 P3-009 是否恢复为后续工程基线候选。

## 13. 需 PM 确认

1. 是否接受 P3-011 进入独立复评；专项会话不自行启动复评。
2. P3-009 是否恢复工程基线候选、R-0042 是否关闭，必须等待独立复评与 PM 决策；本报告不作该结论。
