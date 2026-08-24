# LIFEOS-P3-012｜P3-009 P0 消费门返工独立工程复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-012`
- 对应实现 / 交付：`LIFEOS-P3-011`（对 `LIFEOS-P3-009` 的 P0 返工）
- 独立评审角色：独立工程评审负责人
- 协审视角：技术架构、数据与权限、QA / 测试、AI 信任与安全
- 评审关卡：独立只读复跑 / 临时副本验证、P3-010 AD-1 回归复核、消费入口反例攻击、P1-1 / P1-2 修复复核、evidence 一致性检查、默认关闭能力检查
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-012_p0_consumption_gate_remediation_independent_engineering_re_review.md`
- 评审结论：**Pass**
- 更新时间：2026-08-11

## 1. 任务摘要

1. **[事实]** 独立只读复跑 P3-009 测试套件（WorkBuddy managed Node v22.22.2，`--experimental-strip-types --test`），结果为 **14 PASS / 0 FAIL**，与 evidence `test_results.json`、`test_run.log` 和 MANIFEST 声称一致。未运行 `scripts/validate.mjs`（避免改写 evidence），仅运行只读测试。
2. **[事实]** Evidence 快照 SHA-256 `26eae1f1...` 经独立重算确认一致（使用 `JSON.stringify(hashes)` 方式）；9 个源文件 / 夹具 / 测试文件的逐文件 SHA-256 均匹配。P3-001 文件经 `snapshot_manifest.json` 比对确认 7/7 全部匹配，未被修改。
3. **[事实]** P3-010 的 P0（AD-1：allow+deny 授权冲突放行）已关闭。`canConsume()` 改为在完整匹配上下文内统计授权总行数（`total`）与 allow 行数（`allow_count`），只有 `total === 1 && allow_count === 1` 时通过。allow+deny、allow+unknown、duplicate allow、仅 deny、仅 unknown、缺失授权、generation/purpose/location/processor 错配均 fail closed。
4. **[事实]** P1-1（`suggest()` 使用 `INSERT OR REPLACE` 丢失确认状态）已修复。改为 `INSERT OR IGNORE`，冲突时保留既有 Derivation，随后读取并返回当前 status。重复 suggest 经独立验证保持 confirmed、invalid、edited_confirmed 三种状态，feedback 仍为 active，Derivation 只有一行。
5. **[事实]** P1-2（`feedback()` 不显式检查 derivation status）已修复。现在显式要求 `d.status === "candidate"`，stale、confirmed、edited_confirmed、invalid 等非候选状态均不得继续写入。独立验证 stale、confirmed、invalid 三种状态均被拒绝，无 feedback 写入。
6. **[事实]** 独立构造 16 组共 39 条反例攻击，覆盖 P3-010 AD-1 回归、授权不确定态（missing/duplicate allow/unknown/allow+unknown/only deny）、上下文错配（generation/purpose/location/processor）、tombstone 阻断、跨 Project 泄漏、P1-1 状态保持（confirmed/invalid/edited_confirmed）、P1-2 非候选拒绝（stale/confirmed/invalid）、导出 stale 过滤、证据撤回后 feedback 拒绝、全证据阻断后 suggest 返回 null、FTS 搜索不泄漏。**39 PASS / 0 FAIL**。
7. **[事实]** Evidence 一致性检查全部通过：MANIFEST.md ↔ test_results.json ↔ test_run.log 三方一致（14/0/0）；迁移矩阵、默认关闭矩阵、架构符合性文件与实际代码一致；无自证循环（evidence 由 validate.mjs 从测试输出自动生成）；PASS 数量不误导。
8. **[边界]** 本评审未修改 P3-009 / P3-001 工程文件、evidence、项目账本或冻结资产；只运行只读测试和临时反例脚本（`/tmp/p3-012-adversarial.mjs`）；未启用任何真实能力。

## 2. 读取材料清单

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration.md`
- `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-009_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`
- `lifeos/reviews/LIFEOS-P3-010_pm_review.md`
- `lifeos/tasks/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression.md`
- `lifeos/deliverables/LIFEOS-P3-011_p0_consumption_gate_remediation_and_regression_report.md`
- `lifeos/reviews/LIFEOS-P3-011_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/` 全部源码（`src/*.ts`）、测试（`tests/invariants.test.ts`）、夹具（`fixtures/synthetic_v1.json`）、脚本（`scripts/validate.mjs`）和 evidence（6 个文件）
- `lifeos/engineering/LIFEOS-P3-001/evidence/snapshot_manifest.json`
- `lifeos/reviews/LIFEOS-P3-008_third_p0_remediation_independent_engineering_re_review.md`（历史参考）
- `lifeos/reviews/LIFEOS-P3-008_pm_review.md`（历史参考）
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`

## 3. 只读复跑 / 临时副本验证结果

### 复跑命令

```bash
cd lifeos/engineering/LIFEOS-P3-009
/Users/xxe/.workbuddy/binaries/node/versions/22.22.2/bin/node --experimental-strip-types --test tests/invariants.test.ts
```

- 运行环境：macOS arm64，Node v22.22.2（WorkBuddy managed runtime）
- 结果：**14 PASS / 0 FAIL**
- `node:sqlite` experimental warning 出现，不影响测试结果
- **未运行** `scripts/validate.mjs`（该脚本会改写 evidence），仅运行只读测试

### Evidence 快照验证

- 计算方式：`createHash("sha256").update(JSON.stringify(hashes)).digest("hex")`（与 validate.mjs 一致）
- 计算快照：`26eae1f16ffb4bf61c824ecf59552066fb063fcb7b981a0f0694f7b85bf62881`
- 存储快照：`26eae1f16ffb4bf61c824ecf59552066fb063fcb7b981a0f0694f7b85bf62881`
- 9 个文件逐文件 SHA-256 全部匹配
- `test_run.log` 包含 14 个 `✔` 和 `pass 14 / fail 0`
- `test_results.json` 的 `summary` 与 MANIFEST 声称一致

### P3-001 完整性

- P3-001 `snapshot_manifest.json` 中的 7 个文件 SHA-256 经比对全部匹配
- P3-009 / P3-011 未修改 P3-001 工程文件

### 测试清单确认

P3-009 测试套件现有 14 项测试：

| # | 测试名称 | 级别 | 新增/原有 |
|---|---|---|---|
| 1 | H1 T-SCOPE remains personal local single-device | H1 | 原有 |
| 2 | H2 T-ID preserves immutable user original and distinct identities | H2 | 原有 |
| 3 | H3 T-SAVE authoritative transaction survives derivative failure | H3 | 原有 |
| 4 | H4 T-GATE all consumption entries fail closed on context mismatch | H4 | 原有 |
| 5 | P0 T-GATE allow+deny conflict blocks every consumption entry | P0 | **P3-011 新增** |
| 6 | P0 T-GATE missing duplicate or unknown authorization fails closed | P0 | **P3-011 新增** |
| 7 | P1 T-ID repeated suggestion preserves confirmation and feedback trace | P1 | **P3-011 新增** |
| 8 | P1 T-WRITE-GATE feedback rejects non-candidate derivation explicitly | P1 | **P3-011 新增** |
| 9 | H5 T-DEL revoke/delete blocks revival through read search recovery export | H5 | 原有 |
| 10 | H6 T-IPC-OFF rejects real Tauri and file capabilities | H6 | 原有 |
| 11 | H7 T-DATA fixture is deterministic synthetic-disposable | H7 | 原有 |
| 12 | H8 T-OFF denies every non-slice capability | H8 | 原有 |
| 13 | H9 T-EXPORT enforces project closure and identity | H9 | 原有 |
| 14 | T-ARCH SQLite FTS outbox generations and authority projection execute | T-ARCH | 原有 |

Evidence 已正确反映 14 PASS（而非旧 P3-009 的 10 PASS），task 字段为 `LIFEOS-P3-011`。

## 4. P3-010 AD-1 回归复核

### 攻击方法

在已有 `allow` 授权的 Artifact（artifact-2）上插入第二条 `deny` 授权（相同 subject/purpose/location/processor/generation），然后逐一调用所有已实现消费入口。

### 结果

| 消费入口 | 期望 | 实际 | 结果 |
|---|---|---|---|
| `read()` | null | null | PASS |
| `search()` | 空数组 | 空数组 | PASS |
| `recovery()` | 空数组 | 空数组 | PASS |
| `suggest()` | null | null | PASS |
| `exportMemory().artifacts` | 空数组 | 空数组 | PASS |
| `exportMemory().derivations` | 空数组 | 空数组 | PASS |
| `exportMemory()` 不含用户原文 | 不匹配 `SYNTH_ORIGINAL_NEXT` | 不匹配 | PASS |

**AD-1 已关闭。** allow+deny 冲突时所有消费入口均 fail closed，用户原文不泄漏。

### 代码根因修复确认

`consumption-gate.ts` 第 23-29 行：

```typescript
const auth = store.db.prepare(`SELECT COUNT(*) total,
  SUM(CASE WHEN decision='allow' THEN 1 ELSE 0 END) allow_count
  FROM authorization WHERE subject_id=? AND purpose=?
  AND location=? AND processor=? AND generation=?`).get(
    ctx.subjectId, ctx.purpose, ctx.location, ctx.processor, ctx.artifactGeneration,
  ) as any;
return auth.total === 1 && auth.allow_count === 1;
```

新查询在完整匹配上下文内统计授权总行数与 allow 行数。此判定同时覆盖所有不确定态：

- allow+deny：total=2，拒绝 ✓
- allow+unknown：total=2，拒绝 ✓
- duplicate allow：total=2，拒绝 ✓
- 仅 deny：total=1, allow_count=0，拒绝 ✓
- 仅 unknown：total=1, allow_count=0，拒绝 ✓
- 缺失授权：total=0，拒绝 ✓
- generation/purpose/location/processor 错配：WHERE 不匹配，total=0，拒绝 ✓

## 5. 授权不确定态反例攻击清单与结果

独立构造 16 组反例，覆盖任务卡要求的全部攻击方向：

| # | 反例名称 | 攻击方向 | 结果 |
|---|---|---|---|
| AD-1 | allow+deny conflict | P3-010 P0 回归 | **PASS**（已关闭） |
| AD-2 | missing auth | 缺失授权 fail closed | PASS |
| AD-3 | duplicate allow | 重复 allow fail closed | PASS |
| AD-4 | unknown decision | 未知 decision fail closed | PASS |
| AD-5 | allow+unknown | allow+unknown fail closed | PASS |
| AD-6 | only deny (no allow) | 仅 deny fail closed | PASS |
| AD-7 | generation mismatch | generation 错配 fail closed | PASS |
| AD-8 | purpose mismatch | purpose 错配 fail closed | PASS |
| AD-9 | location mismatch | location 错配 fail closed | PASS |
| AD-10 | processor mismatch | processor 错配 fail closed | PASS |
| AD-11 | tombstoned artifact | tombstone 阻断所有消费入口 | PASS |
| AD-12 | cross-project consumption | 跨 Project 读取拒绝 | PASS |
| AD-13 | export filters stale derivations | 导出排除 stale derivation | PASS |
| AD-14 | feedback after evidence revoked | 证据撤回后 feedback 拒绝 | PASS |
| AD-15 | suggest with all evidence blocked | 全证据阻断后 suggest 返回 null | PASS |
| AD-16 | search blocks allow+deny leak | FTS 搜索不泄漏 allow+deny | PASS |

**总计 39 条断言，39 PASS / 0 FAIL。**

### 消费入口旁路检查

所有已实现消费入口均复用同一消费门 `canConsume()`：

| 消费入口 | 调用路径 | 复用 canConsume |
|---|---|---|
| `read()` | 直接调用 `canConsume()` | ✓ |
| `search()` | 通过 `read()` 间接调用 | ✓ |
| `recovery()` | 通过 `read()` 间接调用 | ✓ |
| `suggest()` | 通过 `recovery()` → `read()` 间接调用 | ✓ |
| `exportMemory()` | 通过 `recovery()` → `read()` 间接调用 | ✓ |
| `feedback()` | 直接调用 `canConsume()` 检查证据 | ✓ |

不存在绕过消费门的消费路径。

## 6. P1-1 / P1-2 修复复核

### P1-1：`suggest()` 确认状态保持

**修复方法：** `INSERT OR REPLACE` → `INSERT OR IGNORE`，冲突时保留既有 Derivation，随后读取并返回当前 status。

**独立验证：**

| 场景 | 期望 | 实际 | 结果 |
|---|---|---|---|
| 首次 suggest | status="candidate" | "candidate" | PASS |
| confirm 后重复 suggest | status="confirmed" | "confirmed" | PASS |
| reject 后重复 suggest | status="invalid" | "invalid" | PASS |
| edit_confirm 后重复 suggest | status="edited_confirmed" | "edited_confirmed" | PASS |
| 重复 suggest 后 feedback 仍 active | status="active" | "active" | PASS |
| 重复 suggest 后 Derivation 只有一行 | COUNT=1 | 1 | PASS |
| 重复 suggest 返回同一 ID | id 相同 | 相同 | PASS |

**P1-1 已关闭。** 重复建议不再静默重置确认状态，feedback 追踪保留完整。

### P1-2：`feedback()` 非候选状态拒绝

**修复方法：** 在 feedback 函数入口添加 `d.status !== "candidate"` 检查，非候选状态直接返回 null。

**独立验证：**

| 场景 | 期望 | 实际 | 结果 |
|---|---|---|---|
| stale derivation feedback | null | null | PASS |
| stale derivation 无 feedback 写入 | COUNT=0 | 0 | PASS |
| confirmed derivation feedback | null | null | PASS |
| invalid derivation feedback | null | null | PASS |
| 证据撤回后 feedback（derivation 变 stale） | null | null | PASS |

**P1-2 已关闭。** 非候选状态的 Derivation 不接受 feedback 写入。

### P1-2 覆盖完整性

`feedback()` 的状态检查覆盖所有非候选状态：

- `stale`：拒绝 ✓（control 命令设置）
- `confirmed`：拒绝 ✓（confirm feedback 设置）
- `edited_confirmed`：拒绝 ✓（edit_confirm feedback 设置）
- `invalid`：拒绝 ✓（reject/correct feedback 设置）
- `candidate`：允许 ✓（唯一可写状态）

不存在遗漏的非候选状态。

### `feedback()` INSERT OR REPLACE 分析

`feedback()` 仍使用 `INSERT OR REPLACE INTO feedback`（P3-010 P2-3），但经分析当前已被状态检查有效门控：

1. 首次调用：status="candidate" → 执行 INSERT → 更新 status 为 confirmed/edited_confirmed/invalid
2. 第二次调用（相同 kind）：status 不再是 "candidate" → 返回 null → INSERT OR REPLACE 不可达
3. 第二次调用（不同 kind）：status 不再是 "candidate" → 返回 null → INSERT OR REPLACE 不可达

因此 `INSERT OR REPLACE` 对于重复调用是死代码。这是一个 P2 级别的代码清洁度问题，不构成安全风险。建议后续将 `INSERT OR REPLACE` 改为 `INSERT` 或 `INSERT OR IGNORE` 以消除歧义。

## 7. Evidence 一致性检查

| 检查项 | 结果 |
|---|---|
| MANIFEST.md 与 test_results.json 的 PASS/FAIL 数量 | 一致（14/0） |
| MANIFEST.md 快照 SHA-256 与 test_results.json snapshot_id | 一致（`26eae1f1...`） |
| test_results.json 逐文件 SHA-256 与实际文件 | 全部匹配（9/9） |
| test_run.log 原始输出与 test_results.json summary | 一致（14/0） |
| test_run.log 测试数量 | 14（与 test_results.json 一致） |
| invariant_migration_matrix.md 状态与实际测试 | 一致 |
| default_off_matrix.md 配置与 capability-policy.ts 代码 | 一致（8 项 false + 运行时抛错） |
| architecture_conformance.md 声明与实际实现 | 一致 |
| P3-001 snapshot_manifest.json 与实际文件 | 全部匹配（7/7，P3-001 未被修改） |
| 自证循环检查 | 未发现 — evidence 由 validate.mjs 从测试输出自动生成 |
| 只测 happy path 检查 | 否 — P0 测试直接复现冲突/不确定授权；P1 测试覆盖状态保持和非候选拒绝；H4 测试 7 类错配 |
| PASS 数量误导检查 | 否 — 14 PASS 准确反映当前 14 个测试；evidence task 字段为 P3-011 |
| evidence 是否反映 P3-011 的 14 PASS（而非旧 10 PASS） | 是 — MANIFEST、test_results.json、test_run.log 均为 14 |

### validate.mjs 分析

`validate.mjs` 通过 `spawnSync` 运行测试，解析输出提取 pass/fail，自动计算文件 hash 和 snapshot。evidence 文件（MANIFEST.md、test_results.json、test_run.log、三个矩阵文件）全部由脚本自动生成，无手工填写。

**观察项（P2）：** `validate.mjs` 第 17 行设置 `p0_fail: fail`（所有失败计为 P0）和 `p1_open: 0`（硬编码）。当所有测试通过时无影响；但若 P1 测试失败，会被标记为 P0 FAIL，且 p1_open 仍为 0。这是保守但可能误导的标记方式。建议后续区分 P0/P1 测试失败的统计。

## 8. P0 / P1 / P2 问题清单

### P0

无。P3-010 的 P0-1 已关闭，经独立反例攻击验证。

### P1

无新发现。P3-010 的 P1-1 和 P1-2 已由 P3-011 修复并经独立验证关闭。

P1-3 至 P1-8 仍为未迁移项，已被 P3-011 明确列入后续迁移清单，不在本评审范围内作为新发现。以下为状态确认：

| P1 项 | 描述 | 当前状态 |
|---|---|---|
| P1-3 | 多证据 `derivation_input` 与非主证据撤回传播 | 未迁移（已声明） |
| P1-4 | 独立 generation mismatch staling 机制 | 未迁移（已声明） |
| P1-5 | `important_link` 及其写入口门 | 未迁移（已声明） |
| P1-6 | restore_candidates、权威投影与旧包不复活 | 未迁移（已声明） |
| P1-7 | 授权 `expires_at` 与 `retract_feedback` | 未迁移（已声明） |
| P1-8 | suggestion ID 的完整 generation 绑定 | 未迁移（已声明，仍使用 `?? 1` fallback） |

### P2

1. **[继承观察项]** `feedback()` 仍使用 `INSERT OR REPLACE` 写入 feedback 行（P3-010 P2-3）。当前已被状态检查有效门控，不构成安全风险，但建议后续改为 `INSERT` 或 `INSERT OR IGNORE` 以消除歧义。
2. **[新观察项]** `validate.mjs` 设置 `p0_fail: fail`（所有失败计为 P0）和 `p1_open: 0`（硬编码）。当所有测试通过时无影响；建议后续区分 P0/P1 测试失败的统计。
3. **[继承观察项]** 单一合成夹具 `lifeos-p3-009-synthetic-v1`，仅 3 个 Artifact / 2 个 Project，多样性有限。
4. **[继承观察项]** `node:sqlite` experimental warning，不构成生产依赖冻结依据。

## 9. 可接受内容

1. P0 修复方案可接受：`canConsume()` 改为 `total === 1 && allow_count === 1`，最小查询改动，同时覆盖所有不确定态。
2. P1-1 修复方案可接受：`INSERT OR IGNORE` 保留既有 Derivation，读取当前 status 返回。
3. P1-2 修复方案可接受：显式 `d.status === "candidate"` 检查，覆盖所有非候选状态。
4. 新增 4 项测试设计可接受：P0 测试覆盖所有消费入口和不确定授权集合；P1 测试覆盖状态保持和非候选拒绝。
5. Evidence 自动刷新机制可接受：validate.mjs 从测试输出自动生成，无自证循环。
6. P1-3 至 P1-8 未冒充完成，已明确列入后续迁移清单。
7. 边界声明克制：未启用真实能力，未冻结实现细节，未修改 P3-001 或项目账本。
8. 模块化 TypeScript + SQLite 骨架结构合理，消费门和能力门有效复用。

## 10. 必须整改内容

无必须整改的 P0 或 P1 项。

P2 项为建议性改进，不阻塞当前评审结论。

## 11. 是否建议 P3-009 恢复为后续工程基线候选

**是，建议恢复。**

P3-010 的 P0（消费门不检查 deny 授权）已由 P3-011 修复并经本独立复评确认关闭。P1-1（INSERT OR REPLACE 丢失确认状态）和 P1-2（feedback 不检查 derivation status）已修复并经独立反例验证。所有授权不确定态均 fail closed。所有消费入口复用同一消费门，不存在旁路。Evidence 完整可复核。P1-3 至 P1-8 已明确列入后续迁移清单。

恢复范围仅限：合成、单进程、受控测试包边界。P3-009 不替代 P3-001 作为完整基线，而是作为目标技术栈（TypeScript + SQLite）的最小工程骨架候选。

## 12. 是否建议关闭或降级 R-0042

**建议关闭 R-0042。**

R-0042 是 P3-010 评审后新增的风险，专门记录 "P3-009 `canConsume()` 不检查 deny 授权，allow+deny 冲突时仍放行"。该 P0 已由 P3-011 修复并经本独立复评确认关闭。修复方案正确、最小、覆盖完整，经 39 条独立反例验证无旁路。

关闭 R-0042 的前提是 PM 确认本复评结论。

## 13. 是否建议保持 R-0040 Open / Conditional

**是，必须保持 Open / Conditional。**

R-0040 是关于真实 Tauri / IPC 矩阵的风险，与 R-0042 无关。P3-009 未运行真实 Tauri / IPC 矩阵。`node:sqlite` experimental warning 不构成生产依赖冻结依据。真实 Tauri 首次集成前必须迁移 P2-015 矩阵并在 debug/release 与目标平台保持 P0=0。

## 14. 本地预检结果

已调用 `python3 lifeos/tools/local_precheck.py` 检查本复评报告。本地模型连接状态取决于局域网模型可用性。若不可用则跳过，符合 AGENTS.md 允许跳过场景。

## 15. 最终结论

**Pass。**

P3-011 的 P0 消费门返工经独立复评确认：
- P3-010 的 P0（allow+deny 授权冲突放行）已关闭，所有消费入口 fail closed。
- 授权不确定态（missing/duplicate allow/unknown/allow+unknown/only deny/generation/purpose/location/processor mismatch）全部 fail closed。
- P1-1（suggest 确认状态保持）已修复，覆盖 confirmed/invalid/edited_confirmed 三种状态。
- P1-2（feedback 非候选拒绝）已修复，覆盖 stale/confirmed/edited_confirmed/invalid 四种状态。
- Evidence 完整一致，可独立复核，无自证循环。
- P1-3 至 P1-8 已明确保留为后续迁移清单，未冒充完成。
- 未修改 P3-001 或项目账本，未启用真实能力。

建议 PM 将 P3-009 恢复为后续工程基线候选（合成、单进程、受控测试包边界），建议关闭 R-0042，保持 R-0040 Open / Conditional。

### 关卡检查

- Gate 1 产品一致性：**Pass。** 未扩张 LifeOS 定位或 V1 范围。
- Gate 2 数据与来源：**Pass。** 消费门正确检查 deny/冲突/重复/未知/不匹配；所有消费入口复用同一门。
- Gate 3 AI 信任与安全：**Pass。** 确认状态保持完整；非候选 Derivation 不接受 feedback；无静默重置。
- Gate 4 技术可行性：**Pass with Conditions。** TypeScript + SQLite 骨架可运行；R-0040 保持 Open / Conditional。
- Gate 5 用户价值：**未评结果层**；本任务只确认 P0 返工有效性。

## 16. 需要 PM 主会话确认的问题

1. **[需 PM 确认]** 是否接受 **Pass** 结论，恢复 P3-009 为后续工程基线候选（合成、单进程、受控测试包边界）。
2. **[需 PM 确认]** 是否关闭 R-0042（P3-009 P0 消费门 allow+deny 冲突放行）。
3. **[需 PM 确认]** 是否保持 R-0040 Open / Conditional（建议保持）。
4. **[需 PM 确认]** 是否启动 P1-3 至 P1-8 的后续迁移任务，缩小 P3-001 覆盖差距。

专项会话不更新任何项目账本、不关闭风险、不启动后续任务。

## 17. 后续任务建议

1. **建议优先：** P3-009 恢复工程基线候选后，按风险顺序逐步迁移 P1-3 至 P1-8 对应的 P3-001 历史测试。
2. **建议次优：** 优先迁移 P1-3（derivation_input 多证据）和 P1-5（important_link 写入口），因为它们涉及数据模型扩展，影响面较大。
3. **建议后续：** 在 P1-3 至 P1-8 迁移完成后，进行 P3-009 与 P3-001 的完整覆盖差异复评，确认 136 条断言覆盖率达到可接受水平。
4. **代码清洁度：** 将 `feedback()` 的 `INSERT OR REPLACE` 改为 `INSERT`，将 `validate.mjs` 的 `p0_fail`/`p1_open` 统计改为区分 P0/P1 测试。
