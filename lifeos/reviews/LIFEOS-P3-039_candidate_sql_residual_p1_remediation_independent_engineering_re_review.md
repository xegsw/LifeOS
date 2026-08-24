# LIFEOS-P3-039｜候选 SQL 残留 P1 整改隔离独立工程复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-039
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-038_candidate_sql_residual_p1_remediation_and_regression.md`
- 独立评审角色：独立工程评审负责人 / QA / Evidence Reviewer
- 协审视角：数据 / 领域模型、AI 信任与安全、技术架构
- 评审关卡：Gate 2 数据与来源评审、Gate 3 AI 权限与信任评审、Gate 4 技术可行性评审
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-039_candidate_sql_residual_p1_remediation_independent_engineering_re_review.md`
- Evidence 路径：`lifeos/reviews/LIFEOS-P3-039/evidence/`
- 评审结论：**Pass with Conditions**
- 更新时间：2026-08-17

## 独立性声明

本评审会话未参与 P3-038 工程整改。本会话是 WorkBuddy 独立评审会话，与执行 P3-038 的 Codex 工程整改会话隔离。评审使用临时副本复跑、独立反例脚本和只读 hash 校验，未修改 P3-031 / P3-037 / P3-038 原始工程文件、交付物、PM Review 或 evidence。

## 评审摘要

1. **[事实]** P3-038 对 P2-2、P2-3、P2-4 三项已知 P1 的整改在 DB 层真实有效。29 个独立反例中，14 个已知攻击面攻击全部被候选 SQL trigger 拒绝（P2-2 六类、P2-3 八类、P2-4 四类含 inactive 清理路径），状态、generation 和 audit 在拒绝后不变。
2. **[事实]** 独立复跑 P3-031 为 38 PASS / 0 FAIL / 退出码 0，P3-038 为 12 PASS / 0 FAIL / 退出码 0，与 PM Review 和交付物报告一致。三个稳定源文件 hash 全部匹配，P3-037 五个 failure evidence 文件 hash 全部未变。
3. **[事实 — 新发现 P1×11]** 独立反例攻击发现 active Authorization 子表的 INSERT、UPDATE、`INSERT OR REPLACE` 和 `authorization_id` 改绑路径全部缺少 DB 层约束。11 个反例证明可以在父授权保持 active、generation 不变、audit 不追加的情况下：新增 allow scope、新增 action、将 scope effect 从 allow 改为 deny（或反向）、交换 scope target、将 scope 改绑到其他 authorization、改写 policy 的 training_allowed / sensitivity_rank / external_send_allowed、改写 action 值（read → export_candidate）、以及通过 `INSERT OR REPLACE` 整体替换 scope 或 policy 行。
4. **[判断]** P3-038 的三项已知 P1 整改真实成立，但 P3-037 PM Review 和 P3-038 任务卡均明确要求独立复评检查"active Authorization 子表 INSERT / UPDATE / 改绑等同类变异路径，避免只对已知 DELETE 用例过拟合"。本评审发现该预测正确：P3-038 只增加了 `BEFORE DELETE` trigger，未覆盖 `BEFORE INSERT`、`BEFORE UPDATE` 或 `INSERT OR REPLACE`，导致同类审计 / generation fencing 缺口以不同操作形式继续存在。
5. **[判断]** R-0043 的 Tombstone 旁路面（P2-2/P2-3）已真实关闭，但 R-0046 的 Authorization 子表面从 DELETE 扩展到 INSERT/UPDATE/REPLACE，不能进入关闭候选。R-0044 建议由 PM 重新评估是否需要重开，因为 INSERT/UPDATE/REPLACE 旁路与 R-0044 关闭条件中"候选 SQL 变更或真实 DB migration 发现新旁路"的失效条件直接相关。

## 已通过内容

### P2-2 Tombstone DELETE / REPLACE / DELETE+INSERT（PASS）

6 个独立反例全部被候选 SQL trigger 拒绝：

| 攻击 | SQLite 错误 | 结果 |
|---|---|---|
| 普通 DELETE | `tombstone_delete_forbidden` | 原行不变，六类门 DENY |
| `INSERT OR REPLACE` generation=4（降代） | `tombstone_reinsert_forbidden` | 原行不变 |
| `INSERT OR REPLACE` generation=5（同代） | `tombstone_reinsert_forbidden` | 原行不变 |
| `INSERT OR REPLACE` generation=6（升代） | `tombstone_reinsert_forbidden` | 原行不变 |
| DELETE+INSERT 单事务 commit | `tombstone_delete_forbidden` | 事务中止，原行不变 |
| DELETE+INSERT 事务后 rollback | `tombstone_delete_forbidden` | rollback 后原行完整恢复 |

`tombstone_no_delete`（无条件 BEFORE DELETE）与 `tombstone_insert_contract`（BEFORE INSERT 检查重复主键和 `accepted` 初态）的组合在 SQLite `INSERT OR REPLACE` 的冲突处理之前触发，有效阻断了所有重插路径。P2-2：**PASS**。

### P2-3 Tombstone 初始状态与转换（PASS）

8 个独立反例覆盖：

| 攻击 | SQLite 错误 | 结果 |
|---|---|---|
| 直接 INSERT `active_blocked` | `tombstone_must_start_accepted` | 零残留 |
| 直接 INSERT `cleaned` | `tombstone_must_start_accepted` | 零残留 |
| 直接 INSERT `cleanup_failed` | `tombstone_must_start_accepted` | 零残留 |
| 直接 INSERT `vendor_limited` | `tombstone_must_start_accepted` | 零残留 |
| 合法 `accepted` 起点 | 无 | 成功 |
| `accepted → active_blocked → cleanup_pending → cleaned` | 无 | 全部成功 |
| 非法 `accepted → cleaned`（跳转） | `tombstone_status_transition_invalid` | 拒绝 |
| generation 降低 UPDATE（5→3） | `tombstone_generation_must_not_decrease` | 拒绝 |

P2-3：**PASS**。

### P2-4 Active Authorization 子表 DELETE（PASS）

4 个独立反例覆盖：

| 攻击 | SQLite 错误 | 结果 |
|---|---|---|
| active scope DELETE | `active_authorization_scope_delete_forbidden` | 父状态/generation/audit/子行数不变 |
| active action DELETE | `active_authorization_action_delete_forbidden` | 同上 |
| active policy DELETE | `active_authorization_policy_delete_forbidden` | 同上 |
| inactive（revoked）scope DELETE | 无 | 允许清理 |

三个 `BEFORE DELETE` trigger 只在父授权为 `active` 时触发拒绝；父授权处于非 active 状态时子行仍可清理，清理路径未被锁死。P2-4：**PASS**。

### 两套回归统计与退出码（PASS）

| 套件 | 独立复跑结果 | 退出码 | 与报告一致 |
|---|---|---|---|
| P3-031 合成空库 | 38 PASS / 0 FAIL / 0 Not Implemented（P0=18, P1=12, P2=8） | 0 | Yes |
| P3-038 受控文件型 | 12 PASS / 0 FAIL / 0 Not Implemented / 0 Unknown（P0=2, P1=10） | 0 | Yes |

### Evidence / hash / 路径隔离（PASS）

- P3-031 三个稳定源文件 hash 全部匹配 P3-038 MANIFEST 记录。
- P3-037 五个 failure evidence 文件 hash 全部未变（MANIFEST.md、test_results.json、三个 check JSON）。
- P3-038 `test_results.json` hash 匹配 MANIFEST（`bdf6f992...f816d`）。
- P3-031 `test_results.json` hash 匹配 MANIFEST（`e5a18677...ba25c`）。
- 临时副本复跑使用 `/tmp/p3-039-yWfgBq/` 隔离目录，未修改原始工程文件。

## 关键问题

### 新发现 P1×11：Active Authorization 子表 INSERT / UPDATE / 改绑旁路

P3-038 的三个 `BEFORE DELETE` trigger 只覆盖了 DELETE 操作，未覆盖 INSERT、UPDATE 和 `INSERT OR REPLACE`。独立反例攻击发现以下 11 条旁路全部成立：

#### ADJ-1：直接 INSERT 新 scope（P1）

```sql
-- 父授权 active 时，直接 INSERT 新 allow scope 成功
INSERT INTO authorization_scope VALUES ('scope-extra', 'auth-1', 'allow', NULL, NULL, 'art-1');
```

结果：INSERT 成功，父 generation 不变（仍为 1），audit 不追加。攻击者可直接扩大授权范围。

#### ADJ-1b：直接 INSERT 新 action（P1）

```sql
INSERT INTO authorization_action VALUES ('action-export', 'auth-1', 'export_candidate');
```

结果：INSERT 成功，父 generation / audit 不变。攻击者可直接新增 export_candidate 权限。

#### ADJ-2：UPDATE scope effect（P1）

```sql
UPDATE authorization_scope SET effect='deny' WHERE id='scope-allow';
```

结果：UPDATE 成功，effect 从 allow 变为 deny，父 generation / audit 不变。可缩小或扩大权限边界。

#### ADJ-2b：UPDATE scope target（P1）

```sql
UPDATE authorization_scope SET project_id='proj-2' WHERE id='scope-allow';
```

结果：UPDATE 成功，scope 绑定的 project 变更，父 generation / audit 不变。可重定向授权范围。

#### ADJ-3：authorization_id 改绑（P1）

```sql
UPDATE authorization_scope SET authorization_id='auth-2' WHERE id='scope-allow';
```

结果：UPDATE 成功，scope 从 auth-1 移至 auth-2，auth-1 的 generation / audit 不变。可跨授权迁移权限。

#### ADJ-4：UPDATE policy training_allowed（P1）

```sql
UPDATE authorization_policy SET training_allowed=1 WHERE authorization_id='auth-1';
```

结果：UPDATE 成功，training_allowed 从 0 变为 1，父 generation / audit 不变。可直接开启训练许可。

#### ADJ-4b：UPDATE policy sensitivity_rank（P1）

```sql
UPDATE authorization_policy SET sensitivity_rank=5 WHERE authorization_id='auth-1';
```

结果：UPDATE 成功，sensitivity_rank 从 2 变为 5，父 generation / audit 不变。可提升敏感等级。

#### ADJ-4c：UPDATE policy external_send_allowed（P1）

```sql
UPDATE authorization_policy SET external_send_allowed=1 WHERE authorization_id='auth-1';
```

结果：UPDATE 成功，external_send_allowed 从 0 变为 1，父 generation / audit 不变。可开启外部发送许可。

#### ADJ-5：UPDATE action 值（P1）

```sql
UPDATE authorization_action SET action='export_candidate' WHERE id='action-read';
```

结果：UPDATE 成功，action 从 read 变为 export_candidate，父 generation / audit 不变。可升级操作权限。

#### ADJ-6：INSERT OR REPLACE scope 整体替换（P1）

```sql
INSERT OR REPLACE INTO authorization_scope VALUES ('scope-allow', 'auth-1', 'deny', 'proj-1', NULL, NULL);
```

结果：INSERT OR REPLACE 成功，effect 从 allow 变为 deny，父 generation / audit 不变。可整体替换 scope 行。

#### ADJ-7：INSERT OR REPLACE policy 整体替换（P1）

```sql
INSERT OR REPLACE INTO authorization_policy VALUES
  ('auth-1', 'none', NULL, 5, 1, 1, '["evil"]', '["*"]', '[]', '[]', 999, 999);
```

结果：INSERT OR REPLACE 成功，training_allowed=1, external_send_allowed=1, sensitivity_rank=5, recipients/regions 改写，父 generation / audit 不变。可整体替换 policy 行。

### 影响评估

这 11 个旁路属于同一风险类别：active Authorization 子表的 DB 层完整性约束只覆盖了 DELETE，未覆盖 INSERT / UPDATE / REPLACE。影响包括：

- **权限扩大**：新增 allow scope、新增 action、将 action 从 read 升级为 export_candidate。
- **权限改写**：修改 scope effect、target、policy 的 training/sensitivity/external_send 字段。
- **审计缺口**：所有操作在父授权 generation 不变、audit 不追加的情况下完成，与 P3-037 P2-4 发现的 DELETE 旁路性质完全相同。
- **INSERT OR REPLACE 绕过**：由于没有 `BEFORE INSERT` trigger 检查"active 父授权是否已存在同类子行"，`INSERT OR REPLACE` 可以通过 PK 冲突替换方式绕过 UPDATE trigger。

## 必须整改项

以下必须在 R-0043 / R-0046 进入关闭候选前整改：

1. **[P1-NEW-01]** 为 `authorization_scope` 增加 `BEFORE INSERT` trigger，在父授权为 active 时拒绝非受控路径的新增 scope（或要求父授权先退出 active 并递增 generation + audit）。
2. **[P1-NEW-02]** 为 `authorization_scope` 增加 `BEFORE UPDATE` trigger，在父授权为 active 时拒绝 effect / project_id / source_id / artifact_id / authorization_id 字段的直接改写。
3. **[P1-NEW-03]** 为 `authorization_action` 增加 `BEFORE INSERT` 和 `BEFORE UPDATE` trigger，在父授权为 active 时拒绝新增 action 或改写 action 值。
4. **[P1-NEW-04]** 为 `authorization_policy` 增加 `BEFORE INSERT` 和 `BEFORE UPDATE` trigger，在父授权为 active 时拒绝整体替换或字段改写。
5. **[P1-NEW-05]** 确认 `INSERT OR REPLACE` 在 SQLite 中的 trigger 触发顺序，确保 `BEFORE INSERT` trigger 在冲突解析之前生效（与 Tombstone `tombstone_insert_contract` 相同的设计模式）。

## 条件通过项

- **条件 1**：P2-2、P2-3、P2-4 三项已知 P1 的整改真实有效，可接受作为 R-0043 的 Tombstone 面关闭候选证据。
- **条件 2**：11 个新发现 P1 必须由后续整改任务（建议 P3-040）在候选 SQL 层增加 active Authorization 子表的 INSERT / UPDATE / REPLACE trigger 后关闭。
- **条件 3**：整改完成后必须再次由隔离独立评审会话复核。
- **失效条件**：若候选 SQL 变更、真实 DB migration 发现新旁路、或 11 个 P1 中的任意一个在真实 DB 中被证明可利用，本结论降级为 Rework。

## 关卡检查

- **Gate 1 产品一致性评审**：不适用（本任务为工程复评，不涉及产品定位）。
- **Gate 2 数据与来源评审**：**Pass with Conditions**。Tombstone 删除不复活、初始状态诚实性和 Authorization 子表 DELETE 完整性在候选层通过；但 INSERT / UPDATE / REPLACE 同类旁路仍存在。
- **Gate 3 AI 权限与信任评审**：**Pass with Conditions**。Authorization DELETE 旁路被拒绝；`active_blocked` 前全消费门证明仍属于应用 guard；但 INSERT / UPDATE / REPLACE 可在 generation / audit 不变时改写权限边界，影响 AI 信任边界。
- **Gate 4 技术可行性评审**：**Pass with Conditions**。两套回归、hash、恢复与退出合同通过；独立复跑可信；但 11 个新 P1 必须在进入真实 DB / Tauri / IPC 前整改。
- **Gate 5 用户价值验证评审**：不适用。

## 风险

- **R-0040**：保持 Open / Conditional。本评审未触碰真实 Tauri / IPC。
- **R-0043**：Tombstone 面（P2-2/P2-3）已真实关闭，可作为关闭候选的 Tombstone 面证据；但 Authorization 子表的新 P1 属于 R-0046 范畴，不影响 R-0043 的 Tombstone 面。建议 PM 在后续整改后统一判断 R-0043 是否可关闭。
- **R-0044**：**建议 PM 重新评估**。R-0044 关闭条件中包含"若候选 SQL 变更或真实 DB migration 发现新旁路，本风险需重新打开"。本评审发现的 11 个 INSERT / UPDATE / REPLACE 旁路与 R-0044 追踪的 Authorization activation completeness 直接相关——active 授权的权限边界可在不经过 activation completeness 检查的情况下被改写。
- **R-0045**：保持 Closed。本评审未发现 Derivation 新旁路。
- **R-0046**：**不可进入关闭候选**。P3-038 关闭了 DELETE 旁路，但 INSERT / UPDATE / REPLACE 旁路属于同一审计 / generation fencing 缺口，R-0046 的覆盖范围必须扩展到这些操作。

## 需要 PM 决策

1. **是否接受 P3-038 为 Pass with Conditions**：三项已知 P1 真实关闭，但 11 个新 P1 需要后续整改。
2. **是否启动 P3-040 整改任务**：为 active Authorization 子表增加 INSERT / UPDATE / REPLACE trigger，并扩展合同测试和文件型回归。
3. **R-0044 是否重新打开**：建议 PM 基于 INSERT / UPDATE / REPLACE 旁路的发现重新评估。
4. **R-0043 / R-0046 的关闭路线**：R-0043 的 Tombstone 面可进入关闭候选；R-0046 必须等待 INSERT / UPDATE / REPLACE 整改通过后才能进入关闭候选。
5. **R-0045 是否保持 Closed**：本评审未发现 Derivation 新旁路，建议保持 Closed。

## 不可外推声明

本评审仅在当前候选 SQL 快照、合成空库、macOS arm64 / SQLite 3.51.0 受控文件 fixture 和单进程范围内成立。不得外推为：

- 生产 migration、非空旧库 upgrade 或真实用户 DB 验证通过。
- 真实 Vault、真实用户文件、真实导出路径或真实敏感数据处理通过。
- 真实 Tauri / IPC、跨平台、并发进程、WAL / 断电或生产 backup SLA 验证通过。
- Schema / API、SQL migration、Tauri capability、导出格式、生产 SLA 或工程基线冻结。
- R-0040 / R-0043 / R-0046 关闭、R-0044 重新打开（仅建议 PM 评估）、正式 MVP 准入或下一阶段准入。

## 最终建议

P3-038 判定为 **Pass with Conditions**：

1. P2-2、P2-3、P2-4 三项已知 P1 在 DB 层真实关闭，测试可复核、未过拟合。
2. 两套回归（38 PASS / 12 PASS）可独立复现，退出码和 hash 可信。
3. 11 个新发现 P1（active Authorization 子表 INSERT / UPDATE / REPLACE 旁路）必须由后续整改任务关闭后，R-0043 / R-0046 才能进入风险关闭决策。
4. 建议 PM 启动 P3-040 整改任务，范围最小包括：为 `authorization_scope` / `authorization_action` / `authorization_policy` 增加 active 父授权下的 `BEFORE INSERT` 和 `BEFORE UPDATE` trigger，确保 `INSERT OR REPLACE` 也被覆盖，并扩展合同测试和文件型回归。
5. 整改完成后必须再次由隔离独立评审会话复核。
