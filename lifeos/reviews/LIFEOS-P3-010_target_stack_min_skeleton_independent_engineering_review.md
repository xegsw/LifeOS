# LIFEOS-P3-010｜目标技术栈最小工程骨架独立工程评审

## 评审信息

- 对应任务 ID：`LIFEOS-P3-010`
- 对应实现 / 交付：`LIFEOS-P3-009`
- 独立评审角色：独立工程评审负责人
- 协审视角：技术架构、数据与权限、QA / 测试、AI 信任与安全
- 评审关卡：独立复跑 / 只读验证、P3-001→P3-009 不变量覆盖差异检查、P0 反例攻击、默认关闭能力检查、证据链完整性检查
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`
- 评审结论：**Rework**
- 更新时间：2026-08-11

## 1. 任务摘要

1. **[事实]** 独立只读复跑 P3-009 测试套件（Node v22.22.2，`--experimental-strip-types --test`），结果为 **10 PASS / 0 FAIL**，与 evidence `test_results.json`、`test_run.log` 和 MANIFEST 声称一致。未运行 `scripts/validate.mjs`，未改写原 evidence。
2. **[事实]** Evidence 快照 SHA-256 `64d18d9c...` 经独立重算确认一致；9 个源文件 / 夹具 / 测试文件的逐文件 SHA-256 均匹配。P3-001 文件经 `snapshot_manifest.json` 比对确认未被修改。
3. **[事实]** P3-009 遵守任务卡边界：工程文件只在 `lifeos/engineering/LIFEOS-P3-009/` 内创建；未修改 P3-001、项目账本、Stitch、PRD 或冻结资产；八类默认关闭能力均为 `Object.freeze(false)` + 运行时负测抛错；R-0040 保持 Open / Conditional。
4. **[P0 发现]** 消费门 `canConsume()` 只计数 `decision='allow'` 的授权行，不检查 `decision='deny'`。当同时存在 allow 和 deny 时，门返回 `true`（应 fail closed）。P3-001 的 `T-GATE-EXPLICIT-CONTEXT-AND-CONFLICTS` 14 条断言明确覆盖此场景并期望拒绝。反例 AD-1 已验证此漏洞。
5. **[P1 发现]** `suggest()` 使用 `INSERT OR REPLACE`，重复调用时静默覆盖已有 Derivation，丢失确认状态。反例 AD-5 已验证：已有 `confirm` feedback 的候选被重置为 `candidate`。P3-001 的 `T-ID-CONFIRMATION-REGRESSION` 10 条断言覆盖此场景。
6. **[事实]** P3-001 的 23 项测试 / 136 条断言中，P3-009 的 10 项聚合测试覆盖约 24 条断言（17.6%），主要覆盖上下文错配、基本不可变性、基本删除/撤回、能力关闭和基本导出闭包。112 条断言未被覆盖，其中包含 P0 级别的历史防线（授权冲突、写入口门、恢复权威投影、Derivation 完整证据撤回、generation 绑定）。
7. **[推断]** P3-009 成功证明消费门和能力门可以脱离 Python harness 复用，模块化结构合理。但 1 项 P0 消费门缺陷意味着当前骨架不能安全地作为后续工程基线候选。
8. **[边界]** 本评审未修改 P3-009 / P3-001 工程文件、evidence、项目账本或冻结资产；只运行只读测试和临时反例脚本（`/tmp/p3-010-adversarial.mjs`）；未启用任何真实能力。

## 2. 读取材料清单

- `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`、`lifeos/AGENT_BRIEFING_PACK.md`、`lifeos/PM_OPERATING_MODEL.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md`
- `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
- `lifeos/tasks/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration.md`
- `lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`
- `lifeos/reviews/LIFEOS-P3-009_pm_review.md`
- `lifeos/engineering/LIFEOS-P3-009/` 全部源码（`src/*.ts`）、测试（`tests/invariants.test.ts`）、夹具（`fixtures/synthetic_v1.json`）、脚本（`scripts/validate.mjs`）和 evidence（6 个文件）
- `lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`（838 行，23 个测试）
- `lifeos/reviews/LIFEOS-P3-008_third_p0_remediation_independent_engineering_re_review.md`
- `lifeos/reviews/LIFEOS-P3-008_pm_review.md`
- `lifeos/deliverables/LIFEOS-P2-019_min_vertical_slice_acceptance_contract.md`

## 3. 复跑 / 只读验证结果

### 复跑命令

```bash
cd lifeos/engineering/LIFEOS-P3-009
node --experimental-strip-types --test tests/invariants.test.ts
```

- 运行环境：macOS arm64，Node v22.22.2（WorkBuddy managed runtime）
- 结果：10 PASS / 0 FAIL
- `node:sqlite` experimental warning 出现，不影响测试结果
- **未运行** `scripts/validate.mjs`（该脚本会改写 evidence），仅运行只读测试

### Evidence 快照验证

- 计算快照：`64d18d9c056571c94077e94ff4efdd3ac720233feaa376cadff0593045345d2a`
- 存储快照：`64d18d9c056571c94077e94ff4efdd3ac720233feaa376cadff0593045345d2a`
- 9 个文件逐文件 SHA-256 全部匹配
- `test_run.log` 包含 10 个 `ok` 和 `pass 10 / fail 0`
- `test_results.json` 的 `summary` 与 MANIFEST 声称一致

### P3-001 完整性

- P3-001 `snapshot_manifest.json` 中的文件 SHA-256 经比对全部匹配
- P3-009 未修改 P3-001 工程文件

## 4. P3-001 → P3-009 覆盖差异矩阵

### 测试级映射

| P3-001 测试 | 断言数 | P3-009 对应 | 覆盖状态 | 风险级别 |
|---|---:|---|---|---|
| T-SCOPE | 0 | H1 T-SCOPE | **部分覆盖** — P3-001 检查 4 项包内容 + capabilities false；P3-009 检查 2 项 + capabilities false | P2 |
| T-ID | 0 | H2 T-ID | **部分覆盖** — P3-001 测 5 种 feedback kind + 不可变性 + 跨 Project 读；P3-009 测 suggestion identity + 不可变性 + 5 类内容身份 + external_ref evidence throw | P2 |
| T-ID-CONFIRMATION-REGRESSION | 10 | 无 | **未覆盖** — 重复建议保持同一身份和确认状态；新证据生成新身份 | **P1**（AD-5 验证失败） |
| T-SAVE | 0 | H3 T-SAVE | **部分覆盖** — P3-001 测文件 DB + 重启 + 重复提交；P3-009 测内存 DB + failBeforeCommit + 索引失败 | P2 |
| T-SAVE-CRASH-BOUNDARY | 11 | 无 | **未覆盖** — 进程杀死边界、before/after commit、重启读取、FTS 故障隔离、Derivation 故障隔离 | P1（已声明未迁移） |
| T-GATE | 0 | H4 T-GATE（部分） | **部分覆盖** — P3-001 测 expiry + deny + stale lease + evidence gaps；P3-009 测 7 类上下文错配 | P2 |
| T-GATE-AUTH-CONTEXT | 12 | H4 T-GATE（部分） | **部分覆盖** — P3-001 测 location/processor/both/unknown/missing auth 共 6 种变异 + 合法精确匹配 + 缺失上下文；P3-009 测 location/processor/purpose 变异 | P2 |
| T-GATE-EXPLICIT-CONTEXT-AND-CONFLICTS | 14 | 无 | **未覆盖** — 缺失上下文、allow/deny 冲突、duplicate allow、时间策略倒拨 | **P0**（AD-1 验证失败） |
| T-DEL | 0 | H5 T-DEL | **部分覆盖** — P3-001 测 3 命令 + retract_feedback；P3-009 测 revoke + delete（2 命令） | P2 |
| T-DEL-OLD-PACKAGE-CONTROLS | 17 | 无 | **未覆盖** — 旧包恢复后 Artifact/Derivation/Feedback 不复活 | P1（无 restore 机制） |
| T-RESTORE-AUTHORITATIVE-CURRENT-GATE | 3 | 无 | **未覆盖** — 旧上下文自证、伪造控制状态、权威 tombstone 优先 | P1（无 restore 机制） |
| T-RESTORE-AUTHORITATIVE-PAYLOAD-PROJECTION | 7 | 无 | **未覆盖** — 伪造载荷投影来自权威行 | P1（无 restore 机制） |
| T-DERIVATION-COMPLETE-EVIDENCE-REVOCATION | 6 | 无 | **未覆盖** — 完整证据持久化、非主证据撤回传播 stale | P1（单证据模型） |
| T-DERIVATION-GENERATION-BINDING | 10 | 无 | **未覆盖** — generation 变化后旧候选 stale、新身份、全消费入口阻断 | P1（generation 仅在 control() 中变化） |
| T-EXPORT | 0 | H9 T-EXPORT（部分） | **部分覆盖** — P3-001 测完整/部分/失败导出 + 恢复后排除；P3-009 测 Project 闭包 + 内容身份 | P2 |
| T-EXPORT-PROJECT-CLOSURE | 12 | H9 T-EXPORT（部分） | **部分覆盖** — P3-001 测跨 Project 泄漏 + feedback/link 包含 + 版本/授权/来源闭包 + 篡改包拒绝；P3-009 测 Project 闭包 + 内容身份 | P2 |
| T-EXPORT-ALL-STATE-PROJECT-CLOSURE | 12 | 无 | **未覆盖** — 混合 Project Derivation/Feedback/Link 从所有 state 字段零泄漏 | P1（单证据模型） |
| T-WRITE-GATES-FEEDBACK-AND-LINK | 22 | 无 | **未覆盖** — feedback/link 写入口在 22 类异常下 fail closed | **P1**（feedback 不检查 derivation status） |
| T-IPC-OFF | 0 | H6 T-IPC-OFF | **覆盖** — 3 类能力运行时拒绝 | 无 |
| T-OFF | 0 | H8 T-OFF | **覆盖** — 全部 8 类能力运行时拒绝 | 无 |
| T-DATA | 0 | H7 T-DATA | **覆盖** — synthetic-disposable + 秘密/路径/邮箱模式扫描 | 无 |
| T-UX | 0 | 无 | **未覆盖** — 10 种语义状态合约 | P2（已声明未迁移） |
| T-ARCH | 0 | T-ARCH | **部分覆盖** — P3-001 测 lease fencing + backup + FTS rebuild 非阻塞；P3-009 测表存在 + FTS + revoke | P2 |

### 断言级统计

- P3-001 总断言数：136（11 组记录断言 + 12 组隐含断言）
- P3-009 间接覆盖断言数：~24（17.6%）
- 未覆盖断言数：~112（82.4%）
- 其中 P0 级别未覆盖：14（T-GATE-EXPLICIT-CONTEXT-AND-CONFLICTS）+ 22（T-WRITE-GATES-FEEDBACK-AND-LINK）= 36
- 其中 P1 级别未覆盖：10 + 11 + 17 + 3 + 7 + 6 + 10 + 12 = 76

## 5. 反例攻击清单与结果

独立构造 12 条反例，覆盖任务卡要求的 6 类攻击方向：

| # | 反例名称 | 攻击方向 | 结果 | 级别 |
|---|---|---|---|---|
| AD-1 | conflicting allow+deny authorization | 授权冲突 fail closed | **FAIL** | **P0** |
| AD-2 | feedback on stale derivation | 删除/撤回后旧 derivation 不可写 | PASS | — |
| AD-3 | feedback after delete of evidence | 删除后 feedback 写入口拒绝 | PASS | — |
| AD-4 | cross-project suggestion/export leak | 跨 Project recovery/export/suggestion 不泄漏 | PASS | — |
| AD-5 | duplicate suggestion ID overwrites | INSERT OR REPLACE 丢失确认状态 | **FAIL** | **P1** |
| AD-6 | CAPABILITIES immutability | 默认关闭能力不可变 | PASS | — |
| AD-7 | suggestion ID fallback generation | generation 绑定检查 | PASS（确认缺陷存在） | P2 |
| AD-8 | missing authorization | 缺失授权 fail closed | PASS | — |
| AD-9 | duplicate allow authorizations | 重复 allow fail closed | PASS | — |
| AD-10 | tombstoned source blocks consumption | Source tombstone 阻断消费 | PASS | — |
| AD-11 | generation mismatch in export | generation 错配 fail closed | PASS | — |
| AD-12 | feedback with wrong project | 跨 Project feedback 拒绝 | PASS | — |

### AD-1 详情（P0）

**攻击方法：** 在已有 `allow` 授权的 Artifact 上插入第二条 `deny` 授权，然后调用 `read()`。

**代码根因：** `consumption-gate.ts` 第 23-27 行：

```typescript
const auth = store.db.prepare(`SELECT COUNT(*) n FROM authorization WHERE subject_id=?
  AND purpose=? AND location=? AND processor=? AND decision='allow' AND generation=?`).get(...);
return auth.n === 1;
```

此查询只计数 `decision='allow'` 的行。当同时存在 1 行 allow 和 1 行 deny 时，`auth.n === 1`，函数返回 `true`。deny 被完全忽略。

**P3-001 对照：** P3-001 的 `can_consume()` 明确检查 allow/deny 冲突并 fail closed。`T-GATE-EXPLICIT-CONTEXT-AND-CONFLICTS` 14 条断言中的 `conflicting_allow_deny_can_consume` 断言期望 `False`。

**影响：** 违反 H4（"未知即拒绝"）。如果攻击者或 bug 在 authorization 表中插入 deny 行，系统不会阻止已授权的访问。这是一个安全防线遗漏。

### AD-5 详情（P1）

**攻击方法：** 对同一证据集合调用两次 `suggest()`，第一次后添加 `confirm` feedback，第二次后检查 derivation status。

**代码根因：** `lifeos.ts` 第 38 行：

```typescript
this.store.db.prepare("INSERT OR REPLACE INTO derivation VALUES(?,?,?,?,?,?,?,?)").run(...)
```

`INSERT OR REPLACE` 语义：当主键冲突时，先 DELETE 旧行再 INSERT 新行。旧行的 `status` 字段（可能已为 `confirmed`）被重置为 `candidate`。关联的 `feedback` 行因为外键约束可能被级联删除（如果启用了外键级联）或成为孤儿（如果未启用）。

**P3-001 对照：** P3-001 的 `suggest_next_step()` 对已确认候选返回同一身份和状态，不覆盖。`T-ID-CONFIRMATION-REGRESSION` 10 条断言覆盖此场景。

**影响：** 审计轨迹丢失、确认状态不保留。重复建议（例如用户多次打开 Project 恢复页面）会重置已确认的候选。

## 6. Evidence 一致性检查

| 检查项 | 结果 |
|---|---|
| MANIFEST.md 与 test_results.json 的 PASS/FAIL 数量 | 一致（10/0） |
| MANIFEST.md 快照 SHA-256 与 test_results.json snapshot_id | 一致（`64d18d9c...`） |
| test_results.json 逐文件 SHA-256 与实际文件 | 全部匹配 |
| test_run.log 原始输出与 test_results.json summary | 一致 |
| invariant_migration_matrix.md 状态与实际测试 | 一致 |
| default_off_matrix.md 配置与 capability-policy.ts 代码 | 一致 |
| architecture_conformance.md 声明与实际实现 | 一致 |
| P3-001 snapshot_manifest.json 与实际文件 | 全部匹配（P3-001 未被修改） |
| 自证循环检查 | 未发现 — evidence 由 validate.mjs 从测试输出自动生成，不是手工填写 |
| 只测 happy path 检查 | H4 和 H5 包含异常路径测试；但缺少授权冲突、写入口门、恢复投影等异常路径 |
| PASS 数量误导检查 | 10 PASS 准确反映当前 10 个测试的状态；但 10 个测试不足以覆盖 P3-001 的 23 个测试 / 136 条断言 |

## 7. P0 / P1 / P2 问题清单

### P0

1. **[P0-1] 消费门不检查 deny 授权。** `canConsume()` 只计数 `decision='allow'` 行，忽略 `decision='deny'`。同时存在 allow 和 deny 时返回 `true`，违反 H4 "未知即拒绝" 和 P3-001 历史防线。反例 AD-1 已验证。修复方法：查询改为检查是否存在 deny 行，或在 count allow 的同时 count deny 并要求 deny=0。

### P1

1. **[P1-1] `suggest()` 使用 INSERT OR REPLACE 丢失确认状态。** 重复建议时旧 Derivation 被静默覆盖，`status` 重置为 `candidate`，已有 feedback 成为孤儿或丢失。反例 AD-5 已验证。P3-001 的 `T-ID-CONFIRMATION-REGRESSION` 10 条断言覆盖此场景。
2. **[P1-2] `feedback()` 不显式检查 derivation status。** 虽然当前实现中 derivation stale 总是伴随 evidence tombstone（消费门间接拦截），但缺少显式 status 检查是结构弱点。若未来添加不伴随 tombstone 的 staling 机制，feedback门将失守。
3. **[P1-3] 无 `derivation_input` 表，Derivation 只绑定单个 evidence_version_id。** 无法检测非主证据撤回对候选的影响。P3-001 的 `T-DERIVATION-COMPLETE-EVIDENCE-REVOCATION` 6 条断言覆盖此场景。
4. **[P1-4] 无 generation 变化的独立 staling 机制。** P3-009 中 generation 仅在 `control()` 中递增，且 `control()` 同时标记 derivation stale。但缺少独立的 `_invalidate_generation_mismatches()` 机制。P3-001 的 `T-DERIVATION-GENERATION-BINDING` 10 条断言覆盖此场景。
5. **[P1-5] 无 `important_link` 表和 `add_important_link()` 方法。** Link 写入口门完全未实现。P3-001 的 `T-WRITE-GATES-FEEDBACK-AND-LINK` 22 条断言中约一半覆盖 Link。
6. **[P1-6] 无 restore_candidates 机制。** 恢复权威投影、伪造包拒绝、旧包不复活完全未实现。P3-001 的 `T-RESTORE-AUTHORITATIVE-CURRENT-GATE`（3 条）和 `T-RESTORE-AUTHORITATIVE-PAYLOAD-PROJECTION`（7 条）覆盖此场景。
7. **[P1-7] 无 `expires_at` 列和 `retract_feedback` 命令。** 时间授权过期和 feedback 撤回未实现。
8. **[P1-8] suggestion ID 使用 fallback generation（1）。** `read()` 不返回 `artifact_generation`，`suggest()` 中 `input.artifact_generation ?? 1` 总是使用 fallback。不同 generation 的建议共享同一 ID。

### P2

1. **[继承观察项]** 单一合成夹具 `lifeos-p3-009-synthetic-v1`，仅 3 个 Artifact / 2 个 Project，多样性有限。
2. **[继承观察项]** `node:sqlite` experimental warning，不构成生产依赖冻结依据。
3. **[新观察项]** `feedback()` 使用 `INSERT OR REPLACE`，与 `suggest()` 有相同的静默覆盖问题。同一 `feedback:{derivationId}:{kind}` ID 的重复调用会覆盖旧 feedback。
4. **[新观察项]** `processIndexJobs()` 中 lease fencing 使用 `WHERE lease_generation=?` 条件更新，但缺少独立的 `claim_job()` / `complete_index_job()` API。P3-001 的 `T-ARCH` 测试了 lease 抢占和删除后完成失败。
5. **[新观察项]** H4 测试的 7 类 corruption 未包含 `subjectId` 错配（指向不存在的 Artifact）。虽然 `canConsume()` 会因 `!row` 返回 false，但缺少显式测试。

## 8. 可接受内容

1. P3-009 的模块化 TypeScript + SQLite 骨架结构合理，成功证明消费门和能力门可以脱离 Python harness 复用。
2. `CAPABILITIES` 使用 `Object.freeze()` 比 P3-001 的可变字典更安全。
3. `content-identity.ts` 的五类内容身份包络设计清晰，非用户原文强制要求 evidence。
4. `artifact_version_no_update` 和 `artifact_version_no_delete` 触发器有效保护原文不可变性。
5. 默认关闭能力的八类负测覆盖充分，不存在隐藏启用路径。
6. Evidence 生成自动化（validate.mjs），无自证循环。
7. 边界声明克制：交付报告明确声明仅限合成、单进程、受控测试包边界，未外推为生产级实现。
8. P3-001 未被修改；项目账本、冻结资产未被篡改。

## 9. 必须整改内容

### P0 必须整改（阻塞基线候选）

1. **修复 `canConsume()` 的 deny 检查。** 必须在查询中检查 `decision='deny'` 行的存在性。建议方案：
   - 方案 A：`SELECT COUNT(*) n_allow FROM ... WHERE decision='allow' ...` + `SELECT COUNT(*) n_deny FROM ... WHERE decision='deny' ...`，要求 `n_allow === 1 && n_deny === 0`。
   - 方案 B：`SELECT decision FROM ... WHERE ... ORDER BY decision`，检查结果集不含 `deny`。
   - 修复后必须新增反例测试覆盖 allow+deny 冲突场景。

### P1 建议整改（不阻塞当前评审，但后续工程任务必须覆盖）

2. 将 `suggest()` 的 `INSERT OR REPLACE` 改为先查后插，保留已有 Derivation 的 status。
3. 在 `feedback()` 中添加 `d.status !== 'stale'` 检查。
4. 后续工程任务中迁移 `derivation_input` 表、generation staling 机制、`important_link` 写入口、restore_candidates 恢复门、`expires_at` 和 `retract_feedback`。

## 10. 是否建议 P3-009 作为后续工程基线候选

**否，当前不建议。**

P0-1（消费门不检查 deny 授权）是一个安全防线遗漏，违反 H4 "未知即拒绝" 原则，且是 P3-001 历史评审中明确覆盖的 P0 防线。在 P0-1 修复并通过复评之前，P3-009 不应作为后续工程基线候选。

修复 P0-1 后，建议创建 P3-010 补丁评审或 P3-011 返工任务，由 Codex 修复后由 WorkBuddy 或其他独立 Agent 复评。复评通过后，P3-009 可作为后续工程基线候选，但仍仅限合成、单进程、受控测试包边界。

## 11. 是否建议保持 R-0040 Open / Conditional

**是，必须保持 Open / Conditional。**

P3-009 未运行真实 Tauri / IPC 矩阵。`node:sqlite` experimental warning 不构成生产依赖冻结依据。真实 Tauri 首次集成前必须迁移 P2-015 矩阵并在 debug/release 与目标平台保持 P0=0。

## 12. 本地预检结果

已调用 `python3 lifeos/tools/local_precheck.py lifeos/reviews/LIFEOS-P3-010_target_stack_min_skeleton_independent_engineering_review.md`。本地模型连接状态：待验证（历史会话中本地模型不可用，连接被对端重置）。若不可用则跳过，符合 AGENTS.md 允许跳过场景。

预检报告路径：`lifeos/local_prechecks/LIFEOS-P3-010_..._local_precheck.md`（状态取决于本地模型可用性）。

## 13. 最终结论

**Rework。**

P3-009 的模块化迁移方向正确，evidence 完整可复核，边界声明克制，P3-001 未被修改。但独立反例攻击发现 1 项 P0（消费门不检查 deny 授权），违反 H4 不变量和 P3-001 历史防线。此缺陷必须修复后才能作为后续工程基线候选。

同时识别 8 项 P1（INSERT OR REPLACE 丢失确认状态、feedback 不检查 derivation status、无 derivation_input 表、无 generation staling、无 important_link、无 restore_candidates、无 expires_at/retract_feedback、suggestion ID fallback generation），这些不阻塞当前 Rework 结论，但后续工程任务必须逐项覆盖。

### 关卡检查

- Gate 1 产品一致性：**Pass。** 未扩张 LifeOS 定位或 V1 范围。
- Gate 2 数据与来源：**Rework。** 消费门不检查 deny 授权，违反 H4 "未知即拒绝"；Derivation 只绑定单个 evidence，非主证据撤回不传播。
- Gate 3 AI 信任与安全：**Rework。** 确认状态可被 INSERT OR REPLACE 静默重置；feedback 不显式检查 derivation status。
- Gate 4 技术可行性：**Pass with Conditions。** TypeScript + SQLite 骨架可运行；node:sqlite experimental 不影响当前测试；R-0040 保持 Open / Conditional。
- Gate 5 用户价值：**未评结果层**；本任务只确认没有被错误外推。

## 14. 需要 PM 主会话确认的问题

1. **[需 PM 确认]** 是否接受 `Rework` 结论，要求 P3-009 修复 P0-1 后重新提交独立评审。
2. **[需 PM 确认]** P0-1 修复任务推荐 Agent：Codex（工程修复）；复评推荐 Agent：WorkBuddy 或其他独立 Agent。
3. **[需 PM 确认]** 是否将 P1-1 至 P1-8 纳入后续工程任务的迁移清单，作为 P3-009 修复后的验收条件。
4. **[需 PM 确认]** R-0040 是否保持 Open / Conditional（建议保持）。

专项会话不更新任何项目账本、不关闭风险、不启动后续任务。

## 15. 后续任务建议

1. **建议优先：** 创建 P3-009 P0 返工任务（P3-011），修复 `canConsume()` 的 deny 检查，新增 allow+deny 冲突反例测试，完成后由独立 Agent 复评。
2. **建议次优：** P0 修复通过后，将 P1-1（INSERT OR REPLACE）和 P1-2（feedback status 检查）一并修复，因为修改量小且与 P0 修复同属消费门/写入口范畴。
3. **建议后续：** 在 P3-009 通过独立评审后，逐步迁移 P1-3 至 P1-8 对应的 P3-001 历史测试，缩小覆盖差距。
