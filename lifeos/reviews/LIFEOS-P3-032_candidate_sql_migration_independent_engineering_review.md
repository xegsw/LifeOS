# LIFEOS-P3-032｜候选 SQL migration 与合成空库合同测试独立工程评审

## 评审信息

- 对应任务 ID：LIFEOS-P3-031
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-031_candidate_sql_migration_and_contract_tests.md`
- 独立评审角色：独立工程评审负责人、QA / Evidence Reviewer
- 协审视角：数据 / 领域模型负责人、AI 信任与安全负责人、技术架构负责人
- 评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-032_candidate_sql_migration_independent_engineering_review.md`
- 评审结论：**Pass with Conditions**
- 更新时间：2026-08-13

## 评审摘要

1. **[事实]** 独立复跑 P3-031 测试套件（临时目录隔离执行）：33 PASS / 0 FAIL / 0 Not Implemented，退出码 0，与 P3-031 声称和 PM 复跑结果一致。源文件（SQL、测试脚本、复跑脚本）SHA-256 hash 全部匹配 MANIFEST。
2. **[事实]** `test_results.json` 和 `test_run.log` 的实际 SHA-256 hash 与 MANIFEST 记录不匹配（源文件未变，生成文件被 PM 复跑覆盖但未更新 MANIFEST）。不影响测试结论可信度，但 evidence 完整性存在 P2 级瑕疵。
3. **[事实]** 未发现 P0 级设计漏洞。候选 SQL 覆盖核心表、CHECK、FK、unique/partial index、trigger 和 migration meta，P3-030 的两项 P1 和三项 P2 均已形成候选实现层证据。
4. **[事实]** 发现 2 项 P1：`authorization_activation_complete` trigger 仅覆盖 BEFORE UPDATE 路径，直接 INSERT with status='active' 可绕过全部激活完整性检查（R-0044 相关）；`derivation_activation_complete` trigger 存在相同模式问题。
5. **[事实]** 发现 4 项 P2：evidence hash 不匹配、tombstone 无 DELETE 保护、tombstone status_transition INSERT 旁路、authorization 子表无 DELETE 保护。
6. **[推断]** R-0043 可作为"关闭候选 / 待 PM 与用户确认"进入 PM 决策，残留风险为 DELETE+INSERT 旁路（P2 级）。
7. **[推断]** R-0044 在 INSERT 旁路补齐前不建议进入关闭候选。修复方案明确：增加 BEFORE INSERT trigger 拒绝直接 active 插入或执行同等完整性检查。
8. **[建议｜需 PM 确认]** P3-031 在 2 项 P1 补齐后可作为后续真实 DB / Tauri 前置验证的候选输入。最小 Tauri shell / handler 仍被阻塞。

## 已通过内容

### 承接关系

1. P3-031 候选 SQL 准确实现了 P3-029 §2-4 的表分层、P3-027 §3-10 的 P1 条件整改和 P3-028 的 3 个 P2 清洁项处理口径。✓
2. P3-030 的 P1-1（tombstone generation monotonic trigger）已实现为 `tombstone_generation_monotonic` BEFORE UPDATE trigger，DB-P0-15 验证 generation 5→4 被拒。✓
3. P3-030 的 P1-2（authorization activation completeness 测试）已实现为 `authorization_activation_complete` BEFORE UPDATE trigger 和 CT-P1-07 测试。✓
4. P3-030 的 P2-1（DerivationInput input_type 显式 enum CHECK）已实现。CT-P2-06 读取实际 schema 验证。✓
5. P3-030 的 P2-2（并发/stale tombstone upgrade 负测）已由 CT-P2-07 覆盖。✓
6. P3-030 的 P2-3（Tombstone status 转换矩阵和强制层级）已由 `tombstone_status_transition` trigger 和 CT-P2-08 覆盖。✓
7. 四 invoke DTO parser 测试（IPC-P0-01 至 IPC-P0-03）严格停留在纯函数解析，未创建 handler、capability 或 Tauri 配置。✓
8. 候选 SQL 首部和 meta 均标明 candidate-only，未冒充生产冻结 migration。✓

### 核心约束反例验证

| 攻击方向 | 验证结果 |
|---|---|
| ArtifactVersion 不可变性 | BEFORE UPDATE + BEFORE DELETE trigger 全覆盖 ✓ |
| SemanticObjectVersion 不可变性 | BEFORE UPDATE + BEFORE DELETE trigger 全覆盖 ✓ |
| Feedback 追加式 | BEFORE UPDATE + BEFORE DELETE trigger 全覆盖 ✓ |
| ContentIdentity 条件身份 | CHECK 四分支 + trigger 补充 AI derivation 激活检查 ✓ |
| DerivationInput 恰一引用 | CHECK 恰一非空 + type-column 一致性 + 四 partial unique index ✓ |
| Feedback retract 线性链 | partial unique on retracts_feedback_id + BEFORE INSERT trigger 验证 target/actor/seq ✓ |
| Feedback dependency 跨 target | BEFORE INSERT trigger 验证 target tuple 完全相同 ✓ |
| Authorization deny 优先 | strict_intersection 纯函数验证，deny 全局阻断 ✓ |
| Tombstone generation 单调（UPDATE 路径） | BEFORE UPDATE trigger 拒绝 generation 降低 ✓ |
| Tombstone status 转换 | BEFORE UPDATE trigger 强制转换矩阵 ✓ |
| Outbox CAS | WHERE 子句 CAS 模式，DB-P0-13 验证 ✓ |
| Submission 幂等 | UNIQUE (namespace, idempotency_key) + DB-P0-14 验证 ✓ |
| FTS 回连权威 | DB-P0-11 验证 tombstoned 内容不泄露 ✓ |
| Migration 原子回滚 | CT-P1-01 故障注入验证无残留 ✓ |

## 关键问题

### P1

| # | 发现 | 位置 | 风险 | 建议 |
|---|---|---|---|---|
| P1-1 | **`authorization_activation_complete` trigger 仅覆盖 BEFORE UPDATE 路径，不覆盖 BEFORE INSERT。** trigger 定义为 `BEFORE UPDATE OF status ON authorization WHEN NEW.status = 'active' AND OLD.status <> 'active'`。直接 `INSERT INTO authorization (..., 'active', ...)` 可绕过全部 scope/action/policy 完整性检查。这是 R-0044 描述的"直接 DB 写入"场景的精确旁路。CT-P1-07 仅测试 UPDATE 路径（propose→active），未测试直接 INSERT active。 | 001_candidate_schema.sql L483-502 | 不完整授权可通过直接 INSERT 变为 active，影响 strict_intersection、缓存键、审计与消费门。R-0044 关闭候选受阻。 | 增加 BEFORE INSERT trigger：方案 A（拒绝 INSERT status='active'，强制 propose→active 两步流程）或方案 B（BEFORE INSERT 执行同等 scope/action/policy 完整性检查）。同时增加测试：`INSERT INTO authorization (..., 'active', ...) → trigger rejects`。 |
| P1-2 | **`derivation_activation_complete` trigger 仅覆盖 BEFORE UPDATE 路径，不覆盖 BEFORE INSERT。** 与 P1-1 相同模式。trigger 定义为 `BEFORE UPDATE OF status ON derivation WHEN NEW.status = 'active' AND OLD.status <> 'active'`。直接 INSERT with status='active' 绕过 input/constraint 检查。`content_identity_ai_derivation_complete`（BEFORE INSERT）提供二级检查（验证 derivation active + 有 inputs + 有 constraints），但 derivation 本身可处于不一致 active 状态。 | 001_candidate_schema.sql L430-437 | Derivation 可在不具备 inputs/constraints 的情况下处于 active 状态，影响应用层消费门判断。 | 增加 BEFORE INSERT trigger 拒绝 INSERT status='active' 或执行同等检查。增加对应测试。 |

### P2

| # | 发现 | 位置 | 建议 |
|---|---|---|---|
| P2-1 | **Evidence hash 不匹配。** `test_results.json` 实际 hash `db2e54bd...` vs MANIFEST `aa55e60d...`；`test_run.log` 实际 hash `31d9e0a4...` vs MANIFEST `0e202933...`。源文件（SQL、测试脚本、复跑脚本）hash 全部匹配。原因是 PM 复跑覆盖了生成文件但未更新 MANIFEST。 | evidence/MANIFEST.md | PM 复跑后更新 MANIFEST 中的生成文件 hash，或在 MANIFEST 中注明"生成文件 hash 随每次运行变化，以源文件 hash 为准"。 |
| P2-2 | **Tombstone 无 DELETE 保护。** artifact_version 和 feedback 均有 BEFORE DELETE trigger 阻止删除，但 tombstone 表没有。DELETE + INSERT with lower generation 可绕过 `tombstone_generation_monotonic` trigger。但 DELETE+INSERT 是更激进的攻击（完全移除 tombstone 而非仅降低 generation），且主要 UPDATE 路径已覆盖。 | 001_candidate_schema.sql L267-277 | 考虑增加 tombstone BEFORE DELETE trigger 或在应用事务 guard 中覆盖此路径。当前为 P2，因为主要攻击向量（UPDATE 降低 generation）已被 trigger 阻断。 |
| P2-3 | **`tombstone_status_transition` trigger 仅覆盖 UPDATE 路径。** 直接 INSERT 可设置任意 cleanup_status。但初始 cleanup_status 由应用层设置，直接 INSERT 场景属于 DB 维护路径。 | 001_candidate_schema.sql L510-519 | 低优先级。应用事务 guard 应负责初始状态正确性。 |
| P2-4 | **Authorization 子表（scope/action/policy）无 DELETE 保护。** 授权激活后，直接 DELETE authorization_scope/action/policy 行可使授权 active 但不完整。但 strict_intersection 在运行时查询当前 scope/action，删除后自然无法匹配（fail closed）。 | 001_candidate_schema.sql L119-150 | 低风险。strict_intersection 的运行时查询机制使删除 scope/action 后授权自然失效。但审计完整性受影响。 |

## 必须整改项

无 P0 级必须整改项。

以下 P1 项建议在后续整改任务中补齐：

1. **P1-1**：增加 `authorization_activation_complete` 的 INSERT 覆盖。建议方案 A（BEFORE INSERT 拒绝 status='active'，强制两步流程），因为：
   - 更简单，一条 trigger 即可
   - 与应用流程一致（propose → grant → activate）
   - 避免 INSERT 时需要先插入子表再检查的复杂时序问题
   - 增加测试：`INSERT INTO authorization (..., 'active', ...) → rejected`

2. **P1-2**：增加 `derivation_activation_complete` 的 INSERT 覆盖。同样建议方案 A（BEFORE INSERT 拒绝 status='active'）。

## 条件通过项

| 条件 | 适用范围 | 失效条件 |
|---|---|---|
| P1-1 authorization INSERT trigger 补齐 | 后续整改任务或真实 DB 验证前置任务 | 若未补齐即尝试关闭 R-0044 |
| P1-2 derivation INSERT trigger 补齐 | 后续整改任务 | 若未补齐即进入真实 DB 验证 |
| P2-1 MANIFEST hash 更新 | 下次 PM 复跑或 evidence 整理 | 若源文件 hash 也不匹配 |
| P2-2 tombstone DELETE 保护 | 后续整改任务或真实 DB 验证前置任务 | 若直接 DB 维护路径成为现实威胁 |
| R-0043 残留风险（DELETE+INSERT 旁路） | R-0043 关闭决策 | 若 PM 判定 DELETE 旁路不可接受 |
| 候选 SQL 不外推为生产冻结 | 所有后续引用 | 任何文案将候选 SQL 称为"已冻结"或"生产 migration" |

## 关卡检查

### Gate 2：数据与来源评审 — Pass with Conditions

- 用户原文 / AI 生成 / AI 推断建议 / 外部引用 / 用户确认事实的区分：ContentIdentity 八类条件 CHECK + trigger ✓
- DerivationInput 恰一引用 + type 一致性 + partial unique ✓
- Feedback 追加式 + 线性 retract 链 + 跨 target dependency trigger ✓
- Tombstone generation fencing（UPDATE 路径）+ 清理失败不解阻断 ✓
- **条件**：P1-2 derivation INSERT 旁路补齐后 Gate 2 完全通过

### Gate 3：AI 权限与信任评审 — Pass with Conditions

- deny 全局阻断不可被具体 allow 覆盖 ✓
- strict_intersection 形式化定义完整（纯函数验证） ✓
- 四 invoke 拆分，destruct capability 独立隔离 ✓
- DTO parser 严格封闭，不冒充真实 IPC ✓
- **条件**：P1-1 authorization INSERT 旁路补齐后 Gate 3 完全通过

### Gate 4：技术可行性评审 — Pass with Conditions

- migration 可在 SQLite 3.51.0 空库原子创建 ✓
- 故障注入回滚验证无残留 ✓
- CHECK / trigger / partial index / transaction guard 分责合理 ✓
- 单一复跑入口，退出码合同正确 ✓
- **条件**：P1-1 和 P1-2 INSERT trigger 补齐；P2-1 MANIFEST 更新

## R-0043 独立判断

### 风险描述
Tombstone generation 单调性若未由 DB trigger 强制，直接 DB 写入可能降低 tombstone generation 并绕过删除 / 撤回消费门。

### 独立评估

**覆盖路径**：
- `tombstone_generation_monotonic` BEFORE UPDATE trigger 阻止 generation 降低 ✓
- DB-P0-15 验证 generation 5→4 被拒，原值不变 ✓
- CT-P2-07 验证 stale generation CAS（第二次 upgrade 0 行）和 generation 降低被拒 ✓
- DB-P0-09 验证 expected generation CAS fencing ✓

**未覆盖路径**：
- DELETE tombstone → INSERT with lower generation（P2-2）。但此路径完全移除 tombstone，不仅仅是降低 generation，属于更激进的攻击。在实际应用中，tombstone 的 DELETE 不在正常流程中。
- INSERT 初始 generation 无前值可比，不适用单调性。

**判断**：R-0043 描述的核心风险（"直接 DB 写入可能降低 tombstone generation"）已被 `tombstone_generation_monotonic` trigger 覆盖。DELETE+INSERT 旁路存在但属于不同类别的攻击（完全移除 tombstone），且 P2-2 已记录。

**结论**：R-0043 **可进入"关闭候选 / 待 PM 与用户确认"**，残留风险为 DELETE+INSERT 旁路（P2 级），建议在后续真实 DB 验证前置任务中评估是否需要 tombstone DELETE 保护。

## R-0044 独立判断

### 风险描述
Authorization activation completeness 若缺少合同测试，实现可能遗漏 0 scope、0 action、incomplete policy 或旧版本未 superseded 的 active 阻断。

### 独立评估

**覆盖路径**：
- `authorization_activation_complete` BEFORE UPDATE trigger 阻止 propose→active 转换时不完整授权 ✓
- CT-P1-07 验证 0 scopes、0 actions、incomplete policy、unsuperseded old version 四类均被拒绝 ✓
- `uq_authorization_active_logical` partial unique index 确保同一 logical_key 只有一个 active ✓

**未覆盖路径**：
- **直接 INSERT with status='active'**（P1-1）。trigger 仅 `BEFORE UPDATE OF status`，不触发 INSERT。直接 `INSERT INTO authorization (..., 'active', ...)` 绕过全部 scope/action/policy 完整性检查。这是 R-0044 描述的"直接 DB 写入"场景的精确旁路。
- 授权激活后 DELETE scope/action/policy 子表行（P2-4）。但 strict_intersection 运行时查询自然 fail closed。

**判断**：R-0044 描述的核心风险（"实现可能遗漏 0 scope、0 action、incomplete policy 或旧版本未 superseded 的 active 阻断"）在 UPDATE 路径已覆盖，但 INSERT 路径存在明确旁路。此旁路使得"直接 DB 写入创建 active 授权"成为可能，与 R-0044 风险描述直接相关。

**结论**：R-0044 **不建议在 INSERT 旁路补齐前进入关闭候选**。修复方案明确且简单：增加 BEFORE INSERT trigger 拒绝 status='active' 或执行同等完整性检查。修复后可重新评估关闭候选资格。

## 测试 / Evidence 复核

### 独立复跑结果

| 项目 | 结果 |
|---|---|
| 复跑环境 | 临时目录隔离执行，未修改 P3-031 原始 evidence |
| Python | 3.9.6 |
| SQLite | 3.51.0 |
| P0 | 18 PASS / 0 FAIL |
| P1 | 7 PASS / 0 FAIL |
| P2 | 8 PASS / 0 FAIL |
| Total | 33 PASS / 0 FAIL |
| 退出码 | 0 |

### Evidence Hash 验证

| 文件 | MANIFEST hash | 实际 hash | 匹配 |
|---|---|---|---|
| `001_candidate_schema.sql` | `f26df8a9...` | `f26df8a9...` | ✓ |
| `run_contract_tests.py` | `3c25a1e6...` | `3c25a1e6...` | ✓ |
| `run_validation.sh` | `61f9d6a1...` | `61f9d6a1...` | ✓ |
| `test_results.json` | `aa55e60d...` | `db2e54bd...` | ✗ |
| `test_run.log` | `0e202933...` | `31d9e0a4...` | ✗ |

**判定**：源文件 hash 全部匹配，测试逻辑未被篡改。生成文件 hash 不匹配是因为 PM 复跑覆盖了文件但未更新 MANIFEST（P2-1）。独立复跑确认 33 PASS / 0 FAIL 结论可信。

### 退出码合同验证

`run_validation.sh` 使用 `set -eu`，Python `main()` 返回 `1 if any(r["status"] == "FAIL" for r in results) else 0`。任一 FAIL（包括 P0 FAIL）均返回非零退出码。独立复跑退出码为 0。✓

### 测试过拟合分析

| 测试类别 | 过拟合风险 | 判定 |
|---|---|---|
| DB-P0-01~06, 09~11, 13~15 | 真实 DB 约束测试，使用内存 SQLite + 合成夹具 | 低风险 ✓ |
| DB-P0-07~08 | 纯 Python 函数 `strict_intersection` 测试 | 正确分类为事务 guard ✓ |
| DB-P0-12 | 纯 Python dict 比较（restore evaluation） | 正确分类为事务 guard ✓ |
| IPC-P0-01~03 | 纯 DTO parser 测试 | 正确分类为合同解析，非 IPC 端到端 ✓ |
| CT-P1-01 | 故障注入 + rollback 验证 | 有效验证原子性 ✓ |
| CT-P1-05 | 纯 Python dict（details_token） | 正确分类为事务 guard ✓ |
| CT-P1-07 | **仅测试 UPDATE 路径** | **遗漏 INSERT 路径（见 P1-1）** |
| CT-P2-01~05 | 纯 Python/DTO 测试 | 正确分类 ✓ |
| CT-P2-06~08 | 真实 DB schema/trigger 测试 | 有效 ✓ |

**关键缺失测试**：
1. `INSERT INTO authorization (..., 'active', ...) → should be rejected`（P1-1 对应）
2. `INSERT INTO derivation (..., 'active', ...) → should be rejected`（P1-2 对应）
3. `DELETE FROM tombstone WHERE ... → should be rejected` 或 `DELETE + INSERT with lower generation → should be rejected`（P2-2 对应）

## 边界声明复核

| 声明 | 验证 |
|---|---|
| 候选 SQL 标明 candidate-only | ✓ SQL 首部注释 + meta 行 candidate_only=1 |
| 未连接真实 DB/Vault/Tauri/IPC | ✓ 仅使用内存 SQLite + 合成夹具 |
| IPC-P0 仅 DTO parser | ✓ 纯 Python 函数，无 handler/capability/Tauri |
| 不冻结 Schema/API | ✓ 交付物和 PM Review 均明确声明 |
| 不关闭 R-0040/R-0043/R-0044 | ✓ 风险保持 Open |
| schema_checksum 为候选标识 | ✓ 值为 `candidate:sha256-computed-by-test-harness` |

**未发现候选 SQL 被误写为生产冻结 migration 的表达。** ✓

## semantic_object 聚合 / 拆表门复核

| 类型 | 专属字段 | 计数 | 状态 |
|---|---|---|---|
| Assertion | statement, valid_from, valid_until, qualification | 4 | 安全 |
| Decision | decision_text, question, options_considered, rationale, validity_window | 5 | 触及上限 |
| Action | action_text, due_at, defer_until, commitment_to, result_ref | 5 | 触及上限 |
| Event | event_type, description, occurrence | 3 | 安全 |

与 P3-029/P3-030 复核结果一致。CT-P2-05 保留拆表硬门。✓

## 风险

| 风险 ID | 描述 | 级别 | 状态 |
|---|---|---|---|
| R-P3-032-01 | Authorization INSERT 旁路使不完整授权可直接创建为 active | P1 | Open，需整改 |
| R-P3-032-02 | Derivation INSERT 旁路使无 inputs/constraints 的 derivation 可直接创建为 active | P1 | Open，需整改 |
| R-P3-032-03 | Tombstone DELETE+INSERT 旁路可绕过 generation 单调性 | P2 | Open，残留风险 |
| R-0040 | Tauri / IPC 安全风险 | 既有 | 保持 Open / Conditional |
| R-0043 | Tombstone generation 单调性 | 既有 | 可进入关闭候选（待 PM + 用户确认） |
| R-0044 | Authorization activation completeness | 既有 | 不建议进入关闭候选（INSERT 旁路未补齐） |

## 需要 PM 决策

1. **[需 PM 确认]** 是否接受 P3-031 为 Pass with Conditions，条件为 P1-1 和 P1-2 在后续整改任务中补齐？
2. **[需 PM 确认]** R-0043 是否可标记为"关闭候选 / 待 PM 与用户确认"？残留风险为 DELETE+INSERT 旁路（P2 级）。
3. **[需 PM 确认]** R-0044 是否保持 Open，直到 INSERT 旁路补齐后再重新评估关闭候选资格？
4. **[需 PM 确认]** 是否允许启动 P3-033 条件整改任务，补齐 P1-1（authorization INSERT trigger）、P1-2（derivation INSERT trigger）和缺失测试？
5. **[需 PM 确认]** P2-1 evidence MANIFEST hash 更新是否在下一次 evidence 整理时完成？
6. **[需 PM 确认]** 以下内容仍不得外推为 Schema/API 冻结、真实 DB 验证通过、真实 Tauri/IPC 通过或 R-0040 关闭？

## 最终建议

1. **评审结论：Pass with Conditions。** P3-031 候选 SQL migration 和合成空库合同测试在核心约束覆盖、测试可复跑性和边界声明方面成立。未发现 P0。2 项 P1（INSERT 旁路）需在后续整改任务中补齐。

2. **R-0043 可进入关闭候选。** `tombstone_generation_monotonic` trigger 覆盖了风险描述的核心路径（UPDATE 降低 generation）。DELETE+INSERT 旁路为 P2 级残留风险。建议 PM 与用户确认后关闭，残留风险记入 RISK_LOG。

3. **R-0044 不建议进入关闭候选。** `authorization_activation_complete` trigger 的 INSERT 旁路（P1-1）与 R-0044 风险描述直接相关。建议在 P3-033 整改任务中补齐 BEFORE INSERT trigger 和对应测试后，重新评估关闭候选资格。

4. **允许启动 P3-033 条件整改任务。** 范围：(a) 增加 authorization BEFORE INSERT trigger；(b) 增加 derivation BEFORE INSERT trigger；(c) 增加对应测试（INSERT with status='active' → rejected）；(d) 更新 evidence MANIFEST hash。仍不得冻结 Schema/API、关闭 R-0040、连接真实 DB/Tauri/IPC 或进入下一阶段。

5. **最小 Tauri shell / handler 仍被阻塞。** 启动条件为：(a) P3-033 整改完成并通过 PM 验收；(b) P3-024 M-01/M-04/M-20 补丁另立任务完成；(c) 候选 SQL migration 整改后通过 PM 验收。

6. **声明**：本评审为只读独立反例评审，在临时目录中复跑测试，未修改 P3-031 原始候选 SQL、测试、脚本或 evidence；未修改 P3-031 交付物或 PM Review；未修改项目账本；未连接真实 DB/Vault/Tauri/IPC；未执行真实 SQL migration；未关闭 R-0040/R-0043/R-0044；未冻结 Schema/API；未启动后续任务。
