# LIFEOS-P3-034｜候选 SQL activation INSERT 旁路整改轻量独立复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-033
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation.md`
- 独立评审角色：独立工程评审负责人、QA / Evidence Reviewer
- 协审视角：数据 / 领域模型负责人、AI 信任与安全负责人、技术架构负责人
- 评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-034_activation_insert_bypass_remediation_light_independent_review.md`
- 评审结论：**Pass**
- 更新时间：2026-08-13

## 评审摘要

1. **[事实]** 独立复跑 P3-031/P3-033 测试套件（临时目录隔离执行）：35 PASS / 0 FAIL / 0 Not Implemented（P0:18、P1:9、P2:8），退出码 0，与 P3-033 声称和 PM 复跑结果完全一致。
2. **[事实]** 源文件 hash（SQL、测试脚本、复跑脚本）全部匹配 MANIFEST §4.1；生成文件 hash（test_results.json、test_run.log）全部匹配 MANIFEST §4.2。P3-032 P2-1（MANIFEST hash 不匹配）已修复。
3. **[事实]** P3-033 新增 `authorization_no_direct_active_insert` 和 `derivation_no_direct_active_insert` 两个 `BEFORE INSERT` trigger，构造 15 个反例攻击场景（A1-A15），全部 fail closed，未发现旁路。
4. **[事实]** CT-P1-08 / CT-P1-09 验证"拒绝写入 + 无父行残留"双重断言，未过拟合；既有 CT-P1-07（UPDATE 路径）和 DB-P0-04（Derivation 缺输入/约束）未被破坏。
5. **[事实]** 未发现 P0 或 P1。P3-032 的 2 项 P1 已在设计层和实现层同时关闭。
6. **[推断]** R-0044 / R-0045 可进入"关闭候选 / 待 PM 与用户确认"。INSERT 旁路和 UPDATE 旁路均已有候选 SQL trigger + 合成空库合同测试覆盖。
7. **[推断]** R-0043 不受 P3-033 影响，保持原 Open / Closure Candidate 状态，P2 残留风险（DELETE+INSERT 旁路）不变。
8. **[建议｜需 PM 确认]** P3-033 通过轻量独立复评。允许 PM 启动后续风险关闭决策包，但 R-0040 仍不可关闭，Schema / API 仍不冻结。

## 已通过内容

### 1. 新增 INSERT trigger 复核

| Trigger | 位置 | 触发时机 | 条件 | 行为 | 判定 |
|---|---|---|---|---|---|
| `authorization_no_direct_active_insert` | L491-493 | `BEFORE INSERT ON authorization` | `NEW.status = 'active'` | `RAISE(ABORT, 'authorization_must_start_inactive')` | ✓ Fail closed |
| `derivation_no_direct_active_insert` | L432-434 | `BEFORE INSERT ON derivation` | `NEW.status = 'active'` | `RAISE(ABORT, 'derivation_must_start_inactive')` | ✓ Fail closed |

### 2. Trigger 互补性验证

| 路径 | 覆盖 trigger | 测试 | 判定 |
|---|---|---|---|
| INSERT `status='active'` Authorization | `authorization_no_direct_active_insert` | CT-P1-08 | ✓ |
| UPDATE `status='active'` Authorization | `authorization_activation_complete` | CT-P1-07 | ✓ |
| INSERT `status='active'` Derivation | `derivation_no_direct_active_insert` | CT-P1-09 | ✓ |
| UPDATE `status='active'` Derivation | `derivation_activation_complete` | DB-P0-04 | ✓ |

INSERT 和 UPDATE trigger 作用于不同操作，互补而非替代。无触发顺序冲突。✓

### 3. 反例攻击场景（A1-A15）

| # | 攻击方向 | 验证结果 |
|---|---|---|
| A1 | BEFORE INSERT trigger 能否被 SQLite 引擎绕过 | SQLite BEFORE INSERT trigger 在行写入前触发，RAISE(ABORT) 回滚 INSERT，无法绕过 ✓ |
| A2 | 大小写变体 `'Active'` / `'ACTIVE'` 绕过 | CHECK 约束 `status IN (...)` 使用 BINARY 排序，大小写敏感；`'Active'` 被 CHECK 拒绝，不触发 trigger ✓ |
| A3 | `INSERT OR REPLACE` 绕过 | REPLACE 先 DELETE 再 INSERT；BEFORE INSERT trigger 仍在 INSERT 阶段触发，`status='active'` 被拒 ✓ |
| A4 | `INSERT OR IGNORE` 绕过 | IGNORE 只在约束冲突时跳过；trigger 在约束检查前触发，`status='active'` 仍被拒 ✓ |
| A5 | 事务内 INSERT active 后立即 UPDATE 补齐子表 | BEFORE INSERT trigger 在 INSERT 语句执行时触发，不等 COMMIT；INSERT 被立即拒绝 ✓ |
| A6 | INSERT `status='granted'` 再 UPDATE 到 `'active'` | `authorization_activation_complete` BEFORE UPDATE trigger 检查 scope/action/policy 完整性；两步流程正确强制 ✓ |
| A7 | INSERT `status='draft'` Derivation 再 UPDATE 到 `'active'` | `derivation_activation_complete` BEFORE UPDATE trigger 检查 inputs/constraint；两步流程正确强制 ✓ |
| A8 | NULL status 绕过 | `status TEXT NOT NULL` 约束拒绝 NULL ✓ |
| A9 | 残留行检查 | CT-P1-08/09 验证 `count(*) = 0`；BEFORE INSERT RAISE(ABORT) 阻止行写入，无残留 ✓ |
| A10 | ContentIdentity 二级检查兼容性 | `content_identity_ai_derivation_complete`（BEFORE INSERT on content_identity）仍验证 derivation active + inputs + constraints；新 INSERT trigger 不削弱此检查 ✓ |
| A11 | 既有 CT-P1-07 完整性 | CT-P1-07 仍验证 UPDATE 路径的 0 scope / 0 action / incomplete policy / unsuperseded 旧版本；PASS ✓ |
| A12 | 既有 DB-P0-04 完整性 | DB-P0-04 仍验证 Derivation UPDATE 缺 inputs 和缺 constraint 被拒；PASS ✓ |
| A13 | 默认值 / 隐式 active | 表定义无 DEFAULT 'active'；status 必须显式提供 ✓ |
| A14 | 并发事务中两个会话同时 INSERT active | SQLite BEFORE INSERT trigger 在语句级触发，不依赖事务隔离级别；两个会话的 INSERT 均被拒 ✓ |
| A15 | 子表先于父表 INSERT | authorization_scope/action/policy 以 authorization 为 FK 父记录，`REFERENCES authorization(id)` + `PRAGMA foreign_keys=ON` 阻止子表先插入；无法先建子表再 INSERT active 父记录 ✓ |

### 4. 合同测试复核

| 测试 | 验证内容 | 过拟合风险 | 判定 |
|---|---|---|---|
| CT-P1-08 | 直接 INSERT active Authorization → 拒绝 + 错误消息 + count=0 | 低：使用完整 17 列 INSERT，验证双重断言 | ✓ |
| CT-P1-09 | 直接 INSERT active Derivation → 拒绝 + 错误消息 + count=0 | 低：先建立合法 active Authorization 作为 FK 前提，再验证 Derivation INSERT 被拒 | ✓ |

### 5. P1 统计准确性

| 严重级别 | P3-031 原始 | P3-033 新增 | P3-033 总计 | 独立复跑 | 匹配 |
|---|---|---|---|---|---|
| P0 | 18 | 0 | 18 | 18 PASS | ✓ |
| P1 | 7 | 2 (CT-P1-08, CT-P1-09) | 9 | 9 PASS | ✓ |
| P2 | 8 | 0 | 8 | 8 PASS | ✓ |
| **Total** | **33** | **2** | **35** | **35 PASS** | ✓ |

### 6. Evidence Hash 验证

#### 源文件 hash（MANIFEST §4.1）

| 文件 | MANIFEST hash | 实际 hash | 匹配 |
|---|---|---|---|
| `001_candidate_schema.sql` | `55f3e15b...` | `55f3e15b...` | ✓ |
| `run_contract_tests.py` | `defdd87e...` | `defdd87e...` | ✓ |
| `run_validation.sh` | `61f9d6a1...` | `61f9d6a1...` | ✓ |

#### 生成文件 hash（MANIFEST §4.2）

| 文件 | MANIFEST hash | 实际 hash | 匹配 |
|---|---|---|---|
| `test_results.json` | `a408f090...` | `a408f090...` | ✓ |
| `test_run.log` | `5470c9a2...` | `5470c9a2...` | ✓ |

**判定**：P3-032 P2-1（MANIFEST hash 不匹配）已修复。源文件和生成文件 hash 全部匹配，hash 口径区分正确。✓

### 7. 退出码合同验证

`run_validation.sh` 使用 `set -eu`，Python `main()` 返回 `1 if any(r["status"] == "FAIL" for r in results) else 0`。任一 FAIL（包括 P0 FAIL）均返回非零退出码。独立复跑退出码为 0。✓

## 关键问题

无 P0 或 P1。

### P3-032 条件处理状态

| 条件 | P3-032 级别 | P3-033 处理 | 独立复核 |
|---|---|---|---|
| P1-1 Authorization INSERT active 旁路 | P1 | 新增 `authorization_no_direct_active_insert` + CT-P1-08 | **已关闭** ✓ |
| P1-2 Derivation INSERT active 旁路 | P1 | 新增 `derivation_no_direct_active_insert` + CT-P1-09 | **已关闭** ✓ |
| P2-1 MANIFEST hash 不匹配 | P2 | 拆分源文件 hash / 生成快照 hash | **已关闭** ✓ |
| P2-2 Tombstone DELETE 保护 | P2 | 未处理（任务卡非范围） | 保留为 P2 残留风险 |
| P2-3 Tombstone status INSERT 路径 | P2 | 未处理（任务卡非范围） | 保留为 P2 残留风险 |
| P2-4 Authorization 子表 DELETE 保护 | P2 | 未处理（任务卡非范围） | 保留为 P2 残留风险 |

P2-2 / P2-3 / P2-4 按 P3-033 任务卡范围纪律明确保留，未擅自处理或降级。✓

## 必须整改项

无。

## 条件通过项

无。本评审结论为 Pass（非 Pass with Conditions）。

P2-2 / P2-3 / P2-4 为 P3-032 遗留 P2 残留风险，按范围纪律不在 P3-033 整改范围内。建议在后续真实 DB 验证前置任务或风险关闭决策包中统一评估。

## 关卡检查

### Gate 2：数据与来源评审 — Pass

- Authorization INSERT active 旁路已由 `authorization_no_direct_active_insert` BEFORE INSERT trigger 封闭 ✓
- Derivation INSERT active 旁路已由 `derivation_no_direct_active_insert` BEFORE INSERT trigger 封闭 ✓
- ContentIdentity AI derivation 二级检查不受影响 ✓
- DerivationInput 恰一引用、Feedback 追加式 / 线性 retract / 跨 target dependency 均未受影响 ✓
- 15 个反例攻击场景全部 fail closed ✓

### Gate 3：AI 权限与信任评审 — Pass

- Authorization 不完整授权无法通过直接 INSERT 进入 active 状态 ✓
- Derivation 无 inputs / constraints 无法通过直接 INSERT 进入 active 状态 ✓
- 两步激活流程（propose/draft → 补齐子记录 → UPDATE active）在 INSERT 和 UPDATE 两条路径上均被强制 ✓
- deny 优先、strict_intersection、四 invoke DTO 边界未受影响 ✓
- AI 派生内容身份链完整性未放宽 ✓

### Gate 4：技术可行性评审 — Pass

- 35 项合成测试通过，独立复跑结果一致 ✓
- Evidence MANIFEST hash 口径已修复，源文件和生成文件均匹配 ✓
- BEFORE INSERT trigger 在 SQLite 中语义明确，无引擎兼容性风险 ✓
- 退出码合同正确，任一 FAIL 返回非零 ✓
- 候选 SQL 仍标明 candidate-only，未冒充生产 migration ✓

## R-0043 独立判断

### 风险描述

Tombstone generation 单调性若未由 DB trigger 强制，直接 DB 写入可能降低 tombstone generation 并绕过删除 / 撤回消费门。

### 独立评估

P3-033 未修改任何 tombstone 相关 SQL 或测试。R-0043 的覆盖状态与 P3-032 评审时完全一致：

- `tombstone_generation_monotonic` BEFORE UPDATE trigger 覆盖核心路径（UPDATE 降低 generation）✓
- DB-P0-15 / CT-P2-07 验证 generation 降低被拒 ✓
- 残留风险：DELETE + INSERT with lower generation（P2-2），完全移除 tombstone 的更激进攻击 ✓

**结论**：R-0043 保持 Open / Closure Candidate，不受 P3-033 影响。P2 残留风险不变。

## R-0044 独立判断

### 风险描述

Authorization activation completeness 若缺少合同测试，实现可能遗漏 0 scope、0 action、incomplete policy 或旧版本未 superseded 的 active 阻断。

### 独立评估

**INSERT 路径（P3-033 新增）**：
- `authorization_no_direct_active_insert` BEFORE INSERT trigger 拒绝 `status='active'` 的直接插入 ✓
- CT-P1-08 验证拒绝 + 错误消息 + 无父行残留 ✓
- 15 个反例攻击场景（A1-A15）全部 fail closed ✓

**UPDATE 路径（P3-031 既有）**：
- `authorization_activation_complete` BEFORE UPDATE trigger 验证 scope/action/policy/supersedes 完整性 ✓
- CT-P1-07 验证 0 scope / 0 action / incomplete policy / unsuperseded 旧版本四类均被拒绝 ✓

**残留风险**：
- P2-4：授权激活后 DELETE scope/action/policy 子表行可使授权不完整。但 strict_intersection 运行时查询自然 fail closed。审计完整性受影响但非直接旁路。✓

**结论**：R-0044 **可进入"关闭候选 / 待 PM 与用户确认"**。INSERT 和 UPDATE 两条路径均已有候选 SQL trigger + 合成空库合同测试覆盖。P2-4 残留风险为审计完整性级别，不影响 fail-closed 语义。

## R-0045 独立判断

### 风险描述

Derivation activation completeness 仅覆盖 UPDATE，直接 INSERT `status='active'` 可绕过 inputs / constraints 完整性检查。

### 独立评估

**INSERT 路径（P3-033 新增）**：
- `derivation_no_direct_active_insert` BEFORE INSERT trigger 拒绝 `status='active'` 的直接插入 ✓
- CT-P1-09 验证拒绝 + 错误消息 + 无父行残留 ✓
- 15 个反例攻击场景（A1-A15）全部 fail closed ✓

**UPDATE 路径（P3-031 既有）**：
- `derivation_activation_complete` BEFORE UPDATE trigger 验证 inputs 和 constraint 存在 ✓
- DB-P0-04 验证缺 inputs 和缺 constraint 均被拒绝 ✓

**二级检查**：
- `content_identity_ai_derivation_complete` BEFORE INSERT on content_identity 验证 derivation active + inputs + constraints ✓
- 新 INSERT trigger 不削弱此二级检查 ✓

**结论**：R-0045 **可进入"关闭候选 / 待 PM 与用户确认"**。INSERT 和 UPDATE 两条路径均已有候选 SQL trigger + 合成空库合同测试覆盖。无残留 P1 或 P2 风险。

## 测试 / Evidence 复核

### 独立复跑结果

| 项目 | 结果 |
|---|---|
| 复跑环境 | 临时目录隔离执行，未修改 P3-031 原始 evidence |
| Python | 3.9.6 |
| SQLite | 3.51.0 |
| P0 | 18 PASS / 0 FAIL |
| P1 | 9 PASS / 0 FAIL |
| P2 | 8 PASS / 0 FAIL |
| Total | 35 PASS / 0 FAIL |
| 退出码 | 0 |

### 测试过拟合分析

| 测试 | 过拟合风险 | 判定 |
|---|---|---|
| CT-P1-08 | 低：使用完整 17 列 INSERT，验证错误消息包含 + count=0 双重断言 | ✓ |
| CT-P1-09 | 低：先建立合法 active Authorization 作为 FK 前提，再验证 Derivation INSERT 被拒 + count=0 | ✓ |
| CT-P1-07 | 未受影响：仍验证 UPDATE 路径四类拒绝 | ✓ |
| DB-P0-04 | 未受影响：仍验证 Derivation UPDATE 缺 inputs/constraint | ✓ |

### Evidence 叙事复核

- MANIFEST §1 范围声明明确包含 P3-033 整改范围 ✓
- MANIFEST §4 hash 口径区分源文件和生成快照，P3-032 P2-1 已修复 ✓
- MANIFEST §5 强制层级包含"Derivation/Authorization 直接 active INSERT 拒绝" ✓
- MANIFEST §6 明确 R-0043/R-0044/R-0045 仍保持 Open ✓
- 未发现候选 SQL 被误写为生产冻结 migration 的表达 ✓

## 边界声明复核

| 声明 | 验证 |
|---|---|
| 候选 SQL 标明 candidate-only | ✓ SQL 首部注释 + meta 行 candidate_only=1 |
| 未连接真实 DB/Vault/Tauri/IPC | ✓ 仅使用内存 SQLite + 合成夹具 |
| IPC-P0 仅 DTO parser | ✓ 纯 Python 函数，无 handler/capability/Tauri |
| 不冻结 Schema/API | ✓ 交付物和 PM Review 均明确声明 |
| 不关闭 R-0040/R-0043/R-0044/R-0045 | ✓ 风险保持 Open |
| P3-033 只修改候选 SQL、测试、evidence | ✓ 未修改 PM 账本、P3-032 评审或其他工程目录 |
| MANIFEST hash 口径修复 | ✓ 源文件 hash / 生成快照 hash 分离 |

**未发现候选 SQL 被误写为生产冻结 migration 的表达。** ✓

## 风险

| 风险 ID | 描述 | 级别 | 状态 |
|---|---|---|---|
| R-0040 | Tauri / IPC 安全风险 | P0 | 保持 Open / Conditional，无新证据 |
| R-0043 | Tombstone generation 单调性 | P1 | 保持 Open / Closure Candidate，P2-2 残留风险不变 |
| R-0044 | Authorization activation completeness | P1 | 可进入关闭候选，P2-4 残留风险为审计级别 |
| R-0045 | Derivation activation completeness | P1 | 可进入关闭候选，无 P1/P2 残留风险 |
| P2-2 | Tombstone DELETE 保护 | P2 | 保留，后续真实 DB 验证前置任务评估 |
| P2-3 | Tombstone status INSERT 路径 | P2 | 保留，后续真实 DB 验证前置任务评估 |
| P2-4 | Authorization 子表 DELETE 保护 | P2 | 保留，strict_intersection 运行时 fail closed |

## 需要 PM 决策

1. **[需 PM 确认]** 是否认定 P3-032 的 2 项 P1（Authorization / Derivation INSERT active 旁路）已在候选实现层完整关闭？
2. **[需 PM 确认]** R-0044 是否可标记为"关闭候选 / 待 PM 与用户确认"，残留风险为 P2-4（审计完整性级别）？
3. **[需 PM 确认]** R-0045 是否可标记为"关闭候选 / 待 PM 与用户确认"，无 P1/P2 残留风险？
4. **[需 PM 确认]** R-0043 是否保持原 Open / Closure Candidate 状态，P2-2 残留风险不变？
5. **[需 PM 确认]** 是否允许 PM 启动后续风险关闭决策包（R-0043 / R-0044 / R-0045 统一关闭评估）？
6. **[需 PM 确认]** 以下内容仍不得外推为 Schema / API 冻结、真实 DB migration 通过、真实 Tauri / IPC 通过或 R-0040 关闭？

## 最终建议

1. **评审结论：Pass。** P3-033 成功关闭了 P3-032 的 2 项 P1（Authorization / Derivation INSERT active 旁路）。新增 `BEFORE INSERT` trigger 简单、fail closed，与既有 `BEFORE UPDATE` trigger 互补而非替代。15 个反例攻击场景全部通过。Evidence hash 口径已修复。

2. **R-0044 可进入关闭候选。** INSERT 路径由 `authorization_no_direct_active_insert` 封闭，UPDATE 路径由 `authorization_activation_complete` 封闭。P2-4 残留风险为审计完整性级别，不影响 fail-closed 语义。建议 PM 与用户确认后关闭。

3. **R-0045 可进入关闭候选。** INSERT 路径由 `derivation_no_direct_active_insert` 封闭，UPDATE 路径由 `derivation_activation_complete` 封闭。`content_identity_ai_derivation_complete` 二级检查不受影响。无 P1/P2 残留风险。建议 PM 与用户确认后关闭。

4. **R-0043 保持原状。** P3-033 未修改 tombstone 相关 SQL 或测试。P2-2（DELETE+INSERT 旁路）残留风险不变。建议在后续真实 DB 验证前置任务中评估。

5. **R-0040 仍不可关闭。** 本任务无真实 Tauri / IPC 新证据。R-0040 保持 Open / Conditional。

6. **允许启动风险关闭决策包。** 建议 PM 创建风险关闭决策任务，统一评估 R-0043 / R-0044 / R-0045 的关闭条件、残留风险和后续真实 DB 验证前置路线。

7. **声明**：本评审为只读轻量独立复评，在临时目录中复跑测试，未修改 P3-031 / P3-033 原始候选 SQL、测试、脚本或 evidence；未修改 P3-031 / P3-032 / P3-033 交付物或 PM Review；未修改项目账本；未连接真实 DB / Vault / Tauri / IPC；未执行真实 SQL migration；未关闭 R-0040 / R-0043 / R-0044 / R-0045；未冻结 Schema / API；未启动后续任务。
