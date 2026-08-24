# LIFEOS-P3-014｜P3-009 P1-3 / P1-5 派生输入与重要 Link 写入口独立工程复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-013`
- 对应实现 / 交付：`LIFEOS-P3-013`（对 `LIFEOS-P3-009` 的 P1-3 / P1-5 迁移）
- 独立评审角色：独立工程评审负责人
- 协审视角：技术架构、数据与权限、QA / 测试、AI 信任与安全
- 评审关卡：独立只读复跑 / 临时副本验证、P1-3 多证据派生输入反例攻击、P1-5 important_link 写入口门反例攻击、evidence 一致性检查、默认关闭能力检查、R-0040 保留检查
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-014_p1_derivation_input_and_link_write_gate_independent_engineering_review.md`
- 评审结论：**Pass**
- 更新时间：2026-08-11

## 1. 任务摘要

1. **[事实]** 独立只读复跑 P3-009 测试套件（WorkBuddy managed Node v22.22.2，`--experimental-strip-types --test`），结果为 **18 PASS / 0 FAIL**，与 evidence `test_results.json`、`test_run.log` 和 MANIFEST 声称一致。未运行 `scripts/validate.mjs`（避免改写 evidence），仅运行只读测试。
2. **[事实]** Evidence 快照 SHA-256 `41c17e84...` 经独立重算确认一致（使用 `JSON.stringify(hashes)` 方式）；9 个源文件 / 夹具 / 测试文件的逐文件 SHA-256 均匹配。P3-001 文件经 `snapshot_manifest.json` 比对确认 7/7 全部匹配，未被修改。
3. **[事实]** P1-3 多证据派生输入已正确迁移：`suggest()` 在创建 Derivation 时，在同一 SQLite 事务内为每个可消费输入写入 `derivation_input` 行，记录 `evidence_version_id`、`artifact_id`、`source_id`、`artifact_generation` 和 `source_generation`。`derivationInputsConsumable()` 要求全部已记录输入均存在精确匹配 context 且重新通过 `canConsume()`，缺少任一输入或任一输入失效即拒绝。
4. **[事实]** 非主证据 revoke / delete 后，`control()` 通过 `derivation_input.artifact_id` 将所有相关 Derivation 标为 `stale`。stale 后 feedback 被拒绝、export 不包含该 Derivation、suggest 返回 null。独立反例 AD-2 至 AD-7 验证覆盖 revoke / delete 两种命令、非主证据与主证据两个方向。
5. **[事实]** P1-5 important_link 写入口已正确迁移：`createImportantLink()` 只接受 `user_confirmed + confirmed` 关系；写前和事务内均执行 `canConsume()` 重检；覆盖 Project、版本、授权、generation、tombstone、purpose、location、processor 和 evidence 全维度 fail-closed。
6. **[事实]** 独立构造 42 组共 78 条反例攻击，覆盖 P1-3 多证据记录完整性、非主证据撤回传播、stale 阻断、generation mismatch、missing/forged context、多 Derivation 共享输入、空输入、非消费输入过滤；P1-5 身份检查、证据检查、授权不确定态、上下文错配、cross Project、tombstone、forged version、source_id 来源验证。**78 PASS / 0 FAIL**。
7. **[事实]** Evidence 一致性检查全部通过：MANIFEST.md ↔ test_results.json ↔ test_run.log 三方一致（18/0/0）；task 字段为 `LIFEOS-P3-013`，`original_regression_expected=14`，`p1_migration_expected=4`，`p1_migration_pass=4`；无自证循环；不只测 happy path；PASS 数量不误导。
8. **[边界]** 本评审未修改 P3-009 / P3-001 工程文件、evidence、项目账本或冻结资产；只运行只读测试和临时反例脚本（`/tmp/p3-014-adversarial.ts`）；未启用任何真实能力。

## 2. 读取材料清单

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`、`lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration.md`
- `lifeos/deliverables/LIFEOS-P3-013_p1_derivation_input_and_link_write_gate_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-013_pm_review.md`
- `lifeos/reviews/LIFEOS-P3-012_p0_consumption_gate_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-012_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/` 全部源码（`src/*.ts`）、测试（`tests/invariants.test.ts`）、夹具（`fixtures/synthetic_v1.json`）、脚本（`scripts/validate.mjs`）和 evidence（6 个文件）
- `lifeos/engineering/LIFEOS-P3-001/evidence/snapshot_manifest.json`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`

## 3. 只读复跑 / 临时副本验证结果

### 复跑命令

```bash
cd lifeos/engineering/LIFEOS-P3-009
/Users/xxe/.workbuddy/binaries/node/versions/22.22.2/bin/node --experimental-strip-types --test tests/invariants.test.ts
```

- 运行环境：macOS arm64，Node v22.22.2（WorkBuddy managed runtime）
- 结果：**18 PASS / 0 FAIL**
- `node:sqlite` experimental warning 出现，不影响测试结果
- **未运行** `scripts/validate.mjs`（该脚本会改写 evidence），仅运行只读测试

### Evidence 快照验证

- 计算方式：`createHash("sha256").update(JSON.stringify(hashes)).digest("hex")`（与 validate.mjs 一致）
- 计算快照：`41c17e8474da4e8e841de29ea9ca897324af2c7081aeb32031799092b2634be0`
- 存储快照：`41c17e8474da4e8e841de29ea9ca897324af2c7081aeb32031799092b2634be0`
- 9 个文件逐文件 SHA-256 全部匹配
- `test_run.log` 包含 18 个 `✔` 和 `pass 18 / fail 0`

### P3-001 完整性

- P3-001 `snapshot_manifest.json` 中的 7 个文件 SHA-256 经比对全部匹配
- P3-009 / P3-013 未修改 P3-001 工程文件

### 测试清单确认

P3-009 测试套件现有 18 项测试：

| # | 测试名称 | 级别 | 新增/原有 |
|---|---|---|---|
| 1 | H1 T-SCOPE remains personal local single-device | H1 | 原有 |
| 2 | H2 T-ID preserves immutable user original and distinct identities | H2 | 原有 |
| 3 | H3 T-SAVE authoritative transaction survives derivative failure | H3 | 原有 |
| 4 | H4 T-GATE all consumption entries fail closed on context mismatch | H4 | 原有 |
| 5 | P0 T-GATE allow+deny conflict blocks every consumption entry | P0 | P3-011 新增 |
| 6 | P0 T-GATE missing duplicate or unknown authorization fails closed | P0 | P3-011 新增 |
| 7 | P1 T-ID repeated suggestion preserves confirmation and feedback trace | P1 | P3-011 新增 |
| 8 | P1 T-WRITE-GATE feedback rejects non-candidate derivation explicitly | P1 | P3-011 新增 |
| 9 | P1-3 derivation records every evidence version and generation | P1 | **P3-013 新增** |
| 10 | P1-3 non-primary revoke or delete stales derivation... | P1 | **P3-013 新增** |
| 11 | P1-5 important_link writes an explicit confirmed... | P1 | **P3-013 新增** |
| 12 | P1-5 important_link fails closed on deny missing generation... | P1 | **P3-013 新增** |
| 13 | H5 T-DEL revoke/delete blocks revival... | H5 | 原有 |
| 14 | H6 T-IPC-OFF rejects real Tauri and file capabilities | H6 | 原有 |
| 15 | H7 T-DATA fixture is deterministic synthetic-disposable | H7 | 原有 |
| 16 | H8 T-OFF denies every non-slice capability | H8 | 原有 |
| 17 | H9 T-EXPORT enforces project closure and identity | H9 | 原有 |
| 18 | T-ARCH SQLite FTS outbox generations and authority projection execute | T-ARCH | 原有 |

Evidence 已正确反映 18 PASS（而非旧 P3-011 的 14 PASS），task 字段为 `LIFEOS-P3-013`，`p1_migration_pass=4`。

## 4. P1-3 多证据派生输入反例攻击清单与结果

独立构造 15 组反例，覆盖任务卡要求的全部攻击方向：

| # | 反例名称 | 攻击方向 | 结果 |
|---|---|---|---|
| AD-1 | derivation_input has all evidence versions | 多证据记录完整性（2 个输入） | PASS（7 断言） |
| AD-2 | non-primary revoke -> stale | 非主证据 revoke 传播 | PASS |
| AD-3 | non-primary delete -> stale | 非主证据 delete 传播 | PASS |
| AD-4 | stale -> feedback rejected | stale 后 feedback 阻断（revoke + delete） | PASS（4 断言） |
| AD-5 | stale -> export excluded | stale 后 export 阻断（revoke + delete） | PASS（2 断言） |
| AD-6 | stale -> suggest returns null | stale 后 suggest 阻断（revoke + delete） | PASS（2 断言） |
| AD-7 | primary revoke -> stale | 主证据 revoke 传播（对称性） | PASS |
| AD-8 | artifact_generation mismatch -> rejected | 输入 generation 错配 fail closed | PASS |
| AD-9 | source_generation mismatch -> rejected | 输入 source generation 错配 fail closed | PASS |
| AD-10 | missing input context -> rejected | 缺失输入 context fail closed | PASS |
| AD-11 | forged versionId -> rejected | 伪造 versionId fail closed | PASS |
| AD-12 | shared input revoke -> all derivations stale | 多 Derivation 共享输入传播 | PASS（2 断言） |
| AD-13 | extra fake input -> rejected | 额外伪造输入 fail closed | PASS |
| AD-14 | empty inputs -> rejected | 空输入 fail closed | PASS |
| AD-15 | direct deny (without control) -> export/feedback blocked | 非控制命令 deny 不 stale 但消费门阻断 | PASS（3 断言） |

**P1-3 小计：30 条断言，30 PASS / 0 FAIL。**

### 代码根因确认

**`suggest()` 创建 Derivation 时写入全部输入（`lifeos.ts` 第 46-51 行）：**

```typescript
const insertInput = this.store.db.prepare("INSERT INTO derivation_input VALUES(?,?,?,?,?,?)");
for (const usableInput of usable) {
  const inputContext = evidence.find(c => c.subjectId === usableInput.id && c.versionId === usableInput.version_id)!;
  insertInput.run(id, inputContext.versionId, inputContext.subjectId, usableInput.source_id,
    inputContext.artifactGeneration, inputContext.sourceGeneration);
}
```

**`control()` 按 `derivation_input.artifact_id` 传播 stale（`lifeos.ts` 第 92-93 行）：**

```typescript
this.store.db.prepare(`UPDATE derivation SET status='stale' WHERE id IN
  (SELECT derivation_id FROM derivation_input WHERE artifact_id=?)`).run(artifactId);
```

**`derivationInputsConsumable()` 要求全部输入可消费（`lifeos.ts` 第 63-69 行）：**

```typescript
private derivationInputsConsumable(derivationId: string, contexts: AuthorizationContext[]): boolean {
  const inputs = this.store.db.prepare("SELECT * FROM derivation_input WHERE derivation_id=?").all(derivationId) as any[];
  return inputs.length > 0 && inputs.every(input => {
    const ctx = contexts.find(c => c.subjectId === input.artifact_id && c.versionId === input.evidence_version_id
      && c.artifactGeneration === input.artifact_generation && c.sourceGeneration === input.source_generation);
    return Boolean(ctx && canConsume(this.store, ctx));
  });
}
```

### 消费入口复用检查

| 消费入口 | 调用 derivationInputsConsumable | 结果 |
|---|---|---|
| `feedback()` | ✓（第 75 行） | 非消费输入拒绝 |
| `exportMemory()` | ✓（第 132 行） | 非消费输入排除 |
| `suggest()` | ✗（仅检查 status === "stale"） | 见 P2-1 |

## 5. P1-5 important_link 写入口门反例攻击清单与结果

独立构造 27 组反例，覆盖任务卡要求的全部攻击方向：

| # | 反例名称 | 攻击方向 | 结果 |
|---|---|---|---|
| AD-16 | valid user_confirmed+confirmed link | 合法写入验证 | PASS（7 断言） |
| AD-17 | ai_inference identity rejected | AI 推断身份拒绝 | PASS（2 断言） |
| AD-18 | external_reference identity rejected | 外部引用身份拒绝 | PASS |
| AD-19 | unconfirmed status rejected | 未确认状态拒绝 | PASS |
| AD-20 | empty evidence rejected | 空证据拒绝 | PASS |
| AD-21 | duplicate evidence rejected | 重复证据拒绝 | PASS |
| AD-22 | deny authorization rejected | deny 授权拒绝 | PASS（2 断言） |
| AD-23 | missing auth rejected | 缺失授权拒绝 | PASS |
| AD-24 | unknown decision rejected | 未知 decision 拒绝 | PASS |
| AD-25 | duplicate allow rejected | 重复 allow 拒绝 | PASS |
| AD-26 | allow+deny rejected | allow+deny 冲突拒绝 | PASS |
| AD-27 | purpose mismatch rejected | purpose 错配拒绝 | PASS |
| AD-28 | location mismatch rejected | location 错配拒绝 | PASS |
| AD-29 | processor mismatch rejected | processor 错配拒绝 | PASS |
| AD-30 | cross Project (to) rejected | 跨 Project 拒绝（to 端） | PASS |
| AD-31 | cross Project (evidence) rejected | 跨 Project 拒绝（evidence 端） | PASS |
| AD-32 | tombstone (from) rejected | tombstone 拒绝（from 端） | PASS |
| AD-33 | tombstone (evidence) rejected | tombstone 拒绝（evidence 端） | PASS |
| AD-34 | artifact generation mismatch rejected | artifact generation 错配拒绝 | PASS |
| AD-35 | source generation mismatch rejected | source generation 错配拒绝 | PASS |
| AD-36 | forged versionId rejected | 伪造 version 拒绝 | PASS |
| AD-37 | valid link evidence stored correctly | 证据存储正确性验证 | PASS（6 断言） |
| AD-38 | source_id from DB not context | source_id 来源验证 | PASS（2 断言） |
| AD-39 | from wrong projectId rejected | from 端 Project 错配拒绝 | PASS |
| AD-40 | evidence wrong projectId rejected | evidence 端 Project 错配拒绝 | PASS |
| AD-41 | version matches current version | 版本匹配验证 | PASS（2 断言） |
| AD-42 | all 8 capabilities remain off | 默认关闭能力回归 | PASS（8 断言） |

**P1-5 小计：48 条断言，48 PASS / 0 FAIL。**

### 代码根因确认

**`createImportantLink()` 写入口门（`lifeos.ts` 第 97-125 行）：**

1. **身份检查**：`if (input.linkIdentity !== "user_confirmed" || input.confirmationStatus !== "confirmed") return null;`
2. **证据非空检查**：`if (input.evidence.length === 0) return null;`
3. **Project 一致性检查**：`allContexts.some(ctx => ctx.projectId !== input.projectId || !canConsume(this.store, ctx))`
4. **证据唯一性检查**：`uniqueEvidence.size !== input.evidence.length`
5. **版本匹配检查**：`row.version_id !== allContexts[index].versionId`
6. **事务内二次重检**：`if (allContexts.some(ctx => !canConsume(this.store, ctx))) throw new Error("link gate changed");`
7. **source_id 来自数据库**：`row.source_id`（非 context）

### 事务内二次重检分析

`createImportantLink()` 在 `BEGIN IMMEDIATE` 事务内再次运行 `canConsume()`，检查失败则回滚。在单进程内存 SQLite 中无真实并发，但此设计为真实多进程环境提供了正确的安全基础。`BEGIN IMMEDIATE` 获取写锁，防止其他写入者在预检和事务之间修改数据。

## 6. Evidence 一致性检查

| 检查项 | 结果 |
|---|---|
| MANIFEST.md 与 test_results.json 的 PASS/FAIL 数量 | 一致（18/0） |
| MANIFEST.md 快照 SHA-256 与 test_results.json snapshot_id | 一致（`41c17e84...`） |
| test_results.json 逐文件 SHA-256 与实际文件 | 全部匹配（9/9） |
| test_run.log 原始输出与 test_results.json summary | 一致（18/0） |
| test_run.log 测试数量 | 18（与 test_results.json 一致） |
| test_results.json task 字段 | `LIFEOS-P3-013`（正确反映 P3-013 迁移） |
| test_results.json original_regression_expected | 14（正确区分原有和新增） |
| test_results.json p1_migration_expected / pass | 4 / 4（P1-3/P1-5 新增测试全部通过） |
| invariant_migration_matrix.md 状态与实际测试 | 一致（H1-H9 + T-ARCH + P1-3 + P1-5） |
| default_off_matrix.md 配置与 capability-policy.ts 代码 | 一致（8 项 false + 运行时抛错） |
| architecture_conformance.md 声明与实际实现 | 一致 |
| P3-001 snapshot_manifest.json 与实际文件 | 全部匹配（7/7，P3-001 未被修改） |
| 自证循环检查 | 未发现 — evidence 由 validate.mjs 从测试输出自动生成 |
| 只测 happy path 检查 | 否 — P1-3 测试覆盖非主证据撤回/删除、stale 阻断；P1-5 测试覆盖 deny/missing/generation/cross-project/tombstone |
| PASS 数量误导检查 | 否 — 18 PASS 准确反映当前 18 个测试 |

### validate.mjs 分析

`validate.mjs` 通过 `spawnSync` 运行测试，解析输出提取 pass/fail，使用正则 `✔ P1-(?:3|5)` 统计 P1 迁移测试通过数。evidence 文件全部由脚本自动生成，无手工填写。

**[继承观察项 P2]** `validate.mjs` 第 18 行设置 `p0_fail: fail`（所有失败计为 P0）和 `p1_open: 0`（硬编码）。当所有测试通过时无影响。

## 7. P0 / P1 / P2 问题清单

### P0

无。

### P1

无新发现。P1-3 和 P1-5 已由 P3-013 正确迁移并经独立反例攻击验证。

P1-4 / P1-6 / P1-7 / P1-8 仍为未迁移项，已被 P3-013 明确列入后续迁移清单，不在本评审范围内作为新发现。状态确认：

| P1 项 | 描述 | 当前状态 |
|---|---|---|
| P1-4 | 独立 generation mismatch staling 机制 | 未迁移（已声明）；generation mismatch 仍在消费时 fail closed |
| P1-6 | restore_candidates、权威投影与旧包不复活 | 未迁移（已声明） |
| P1-7 | 授权 `expires_at` 与 `retract_feedback` | 未迁移（已声明） |
| P1-8 | suggestion ID 的完整 generation 绑定 | 未迁移（已声明，仍使用 `?? 1` fallback） |

### P2

1. **[新观察项]** `suggest()` 在处理已存在 Derivation 时仅检查 `status === "stale"`，未调用 `derivationInputsConsumable()`。如果输入证据的授权被直接 deny（不通过 `control()`），Derivation 不会 stale，`suggest()` 仍返回该候选。但 `feedback()` 和 `exportMemory()` 均会通过 `derivationInputsConsumable()` 阻断，因此不构成安全风险。在正常调用流程中（传入全部 Project context），此路径不会触发。建议后续在 `suggest()` 返回前增加 `derivationInputsConsumable()` 检查以提升一致性。
2. **[继承观察项]** `feedback()` 仍使用 `INSERT OR REPLACE` 写入 feedback 行（P3-010 P2-3）。当前已被状态检查有效门控，不构成安全风险，建议后续改为 `INSERT` 或 `INSERT OR IGNORE`。
3. **[继承观察项]** `validate.mjs` 设置 `p0_fail: fail`（所有失败计为 P0）和 `p1_open: 0`（硬编码）。当所有测试通过时无影响，建议后续区分 P0/P1 测试失败统计。
4. **[继承观察项]** 单一合成夹具 `lifeos-p3-009-synthetic-v1`，仅 3 个 Artifact / 2 个 Project，多样性有限。
5. **[继承观察项]** `node:sqlite` experimental warning，不构成生产依赖冻结依据。
6. **[新观察项]** `createImportantLink()` 未显式检查 from ≠ to（自引用 Link）。这不构成安全风险（消费门仍生效），但可能产生语义上无意义的自引用关系。建议后续考虑是否需要禁止。

## 8. 可接受内容

1. P1-3 多证据 `derivation_input` 迁移方案可接受：在同一事务内为每个可消费输入写入 `derivation_input` 行，记录完整证据版本和双级 generation 快照。
2. 非主证据 revoke / delete 传播方案可接受：`control()` 通过 `derivation_input.artifact_id` 将所有相关 Derivation 标为 stale，覆盖主证据和非主证据两个方向。
3. stale 后消费阻断方案可接受：feedback 被拒绝、export 排除、suggest 返回 null，三个消费路径全部阻断。
4. `derivationInputsConsumable()` 设计可接受：要求全部输入均存在精确匹配 context 且重新通过 `canConsume()`，缺少任一即拒绝。
5. P1-5 important_link 写入口门方案可接受：只接受 `user_confirmed + confirmed`，写前和事务内均执行 `canConsume()` 重检，source_id 来自数据库而非 context。
6. 新增 4 项测试设计可接受：P1-3 测试覆盖多证据记录和非主证据撤回传播；P1-5 测试覆盖合法写入和五类失败场景。
7. Evidence 自动刷新机制可接受：validate.mjs 从测试输出自动生成，无自证循环，正确区分原有 14 项和 P1 迁移 4 项。
8. P1-4 / P1-6 / P1-7 / P1-8 未冒充完成，已明确列入后续迁移清单。
9. 边界声明克制：未启用真实能力，未冻结实现细节，未修改 P3-001 或项目账本。

## 9. 必须整改内容

无必须整改的 P0 或 P1 项。

P2 项为建议性改进，不阻塞当前评审结论。

## 10. 是否建议 P3-013 作为 P3-009 工程基线候选的 P1 补强输入

**是，建议采纳。**

P1-3 多证据 `derivation_input` 迁移和 P1-5 important_link 写入口门迁移均经独立反例攻击验证：
- 多证据输入完整落账，记录每个输入的证据版本、artifact/source generation。
- 任一输入（主证据或非主证据）被 revoke / delete 后，相关 Derivation stale，feedback / export / suggest 全部阻断。
- `derivationInputsConsumable()` 要求全部输入精确匹配 context 且通过消费门，缺少/伪造/错配均 fail closed。
- important_link 只接受用户确认关系，写前和事务内双重消费门检查，覆盖全部授权不确定态和上下文错配。
- Evidence 18 PASS / 0 FAIL 完整可复核，无自证循环。

采纳范围仅限：合成、单进程、受控测试包边界。P3-009 不替代 P3-001 作为完整基线，而是作为目标技术栈（TypeScript + SQLite）的最小工程骨架候选，现已补强 P1-3 / P1-5 安全不变量。

## 11. 是否建议保持 R-0040 Open / Conditional

**是，必须保持 Open / Conditional。**

R-0040 是关于真实 Tauri / IPC 矩阵的风险。P3-009 未运行真实 Tauri / IPC 矩阵。`node:sqlite` experimental warning 不构成生产依赖冻结依据。真实 Tauri 首次集成前必须迁移 P2-015 矩阵并在 debug/release 与目标平台保持 P0=0。

## 12. 本地预检结果

已调用 `python3 lifeos/tools/local_precheck.py` 检查本复评报告。本地模型连接状态取决于局域网模型可用性。若不可用则跳过，符合 AGENTS.md 允许跳过场景。

## 13. 最终结论

**Pass。**

P3-013 的 P1-3 / P1-5 迁移经独立复评确认：

- P1-3 多证据 `derivation_input` 已正确迁移：Derivation 记录所有输入证据版本和双级 generation 快照，不再只依赖单一主证据。
- 非主证据 revoke / delete 后 Derivation stale，feedback / export / suggest 全部阻断。
- `derivationInputsConsumable()` 要求全部输入精确匹配且通过消费门，generation mismatch / missing context / forged context 均 fail closed。
- P1-5 important_link 写入口门已正确迁移：只接受用户确认关系，写前和事务内双重消费门检查。
- important_link 覆盖 deny / missing / unknown / duplicate / allow+deny / purpose / location / processor / cross-Project / tombstone / generation / forged version 全维度 fail closed。
- Evidence 18 PASS / 0 FAIL 完整一致，可独立复核，无自证循环。
- P1-4 / P1-6 / P1-7 / P1-8 已明确保留为后续迁移清单，未冒充完成。
- 未修改 P3-001 或项目账本，未启用真实能力。

建议 PM 采纳 P3-013 作为 P3-009 工程基线候选的 P1 补强输入，保持 R-0040 Open / Conditional。

### 关卡检查

- Gate 1 产品一致性：**Pass。** 未扩张 LifeOS 定位或 V1 范围。
- Gate 2 数据与来源：**Pass。** 多证据输入完整落账；任一输入撤回/删除传播 stale；Link 写门重检 Project、版本、授权、generation、tombstone 和证据；source_id 来自数据库。
- Gate 3 AI 信任与安全：**Pass。** stale Derivation 不接受 feedback、不导出、不作为建议返回；Link 的用户确认身份与 AI inference / external reference 明确分离。
- Gate 4 技术可行性：**Pass with Conditions。** TypeScript + SQLite 骨架可运行；R-0040 保持 Open / Conditional。
- Gate 5 用户价值：**未评结果层**；本任务只确认 P1 迁移有效性。

## 14. 需要 PM 主会话确认的问题

1. **[需 PM 确认]** 是否接受 **Pass** 结论，采纳 P3-013 作为 P3-009 工程基线候选的 P1 补强输入。
2. **[需 PM 确认]** 是否保持 R-0040 Open / Conditional（建议保持）。
3. **[需 PM 确认]** 是否启动 P1-4 / P1-6 / P1-7 / P1-8 的后续迁移任务，缩小 P3-001 覆盖差距。

专项会话不更新任何项目账本、不关闭风险、不启动后续任务。

## 15. 后续任务建议

1. **建议优先：** P1-4（独立 generation mismatch staling 机制），因为 P1-3 的 `derivationInputsConsumable()` 已在消费时检查 generation mismatch，但缺少主动 staling 机制。
2. **建议次优：** P1-6（restore_candidates、权威投影与旧包不复活），涉及数据模型扩展。
3. **建议后续：** P1-3 至 P1-8 全部迁移完成后，进行 P3-009 与 P3-001 的完整覆盖差异复评。
4. **代码清洁度：** 将 `feedback()` 的 `INSERT OR REPLACE` 改为 `INSERT`；将 `suggest()` 返回前增加 `derivationInputsConsumable()` 检查；改进 `validate.mjs` 的 P0/P1 统计。
