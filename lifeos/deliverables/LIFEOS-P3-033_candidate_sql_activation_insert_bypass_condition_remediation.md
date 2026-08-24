# LIFEOS-P3-033｜候选 SQL activation INSERT 旁路条件整改

## 1. 任务摘要

- **[已验证事实]** 已仅在授权的 P3-031 候选 SQL、合成空库测试与 evidence 范围内，补齐 Authorization 和 Derivation 直接 `INSERT status='active'` 旁路。
- **[已验证事实]** 采用 P3-032 推荐的方案 A：新增两个 `BEFORE INSERT` trigger，直接拒绝 active 父记录，强制执行“先插入非 active → 补齐子记录 → UPDATE 激活”的两步流程。
- **[已验证事实]** 新增 CT-P1-08、CT-P1-09 两条负测，分别验证直接 active INSERT 被指定 trigger 拒绝，且失败后表中无残留父行。
- **[已验证事实]** 最终复跑 35 PASS / 0 FAIL / 0 Not Implemented：P0 18、P1 9、P2 8；验证命令退出码为 0，任一严重级别 FAIL 均会返回非零。
- **[推断]** P3-032 的两个 P1 已形成“候选实现层、待 PM 验收的关闭候选”证据；R-0044、R-0045 仍保持 Open，本会话不关闭风险。

## 2. 修改范围

本任务实际修改：

- `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
- `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
- `lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_results.json`
- `lifeos/engineering/LIFEOS-P3-031/evidence/test_run.log`
- 本交付物。

复跑入口 `scripts/run_validation.sh` 无需修改。未修改 P3-032 独立评审、P3-032 PM Review、P3-031 PM Review、Stitch、其他工程目录或任何 PM 账本。

## 3. 候选 SQL 修改

### 3.1 Authorization

新增 `authorization_no_direct_active_insert`：

- 触发时机：`BEFORE INSERT ON authorization`。
- 条件：`NEW.status = 'active'`。
- 行为：`RAISE(ABORT, 'authorization_must_start_inactive')`。

选择直接拒绝而非在 INSERT 时复刻完整性检查，原因是 scope、action、policy 均以 Authorization 为 FK 父记录，无法安全地在父记录 INSERT 前先建立子记录。允许直接 active INSERT 会制造天然的检查时序缺口；强制先 proposed/granted、补齐子记录、再由既有 `authorization_activation_complete` 检查 UPDATE 激活，是更小、更明确的 fail-closed 路径。

### 3.2 Derivation

新增 `derivation_no_direct_active_insert`：

- 触发时机：`BEFORE INSERT ON derivation`。
- 条件：`NEW.status = 'active'`。
- 行为：`RAISE(ABORT, 'derivation_must_start_inactive')`。

DerivationInput 与 DerivationConstraint 同样依赖父 Derivation。直接 active INSERT 无法同时证明 inputs / constraint 已存在，因此必须先 draft，再插入完整输入与限制，最后由既有 `derivation_activation_complete` 在 UPDATE 激活时验证。

两项修改没有放宽 Authorization、Derivation、ContentIdentity、证据链或消费门；只封闭 P3-032 指出的 INSERT 路径。

## 4. 测试脚本修改与复跑

新增：

- `CT-P1-08`：合成空库中直接 INSERT active Authorization；断言错误包含 `authorization_must_start_inactive`，并断言目标 ID 行数为 0。
- `CT-P1-09`：先建立合成 active Authorization，再直接 INSERT active Derivation；断言错误包含 `derivation_must_start_inactive`，并断言目标 ID 行数为 0。

原有 proposed/draft → 完整子记录 → UPDATE active 正路径和缺 scope/action/policy/input/constraint 负路径继续通过，证明整改没有破坏既有两步激活合同。

复跑命令：

```bash
lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh
```

| 严重级别 | PASS | FAIL | Not Implemented |
|---|---:|---:|---:|
| P0 | 18 | 0 | 0 |
| P1 | 9 | 0 | 0 |
| P2 | 8 | 0 | 0 |
| **Total** | **35** | **0** | **0** |

测试脚本主函数仍对任一 `status == FAIL` 返回 1，因此 P0/P1/P2 任一失败均导致复跑命令非零退出。

## 5. P3-032 条件处理

| 条件 | 处理结果 | 证据 |
|---|---|---|
| P1-1 Authorization INSERT active 旁路 | 已补齐候选 DB trigger 与负测 | `authorization_no_direct_active_insert`、CT-P1-08 |
| P1-2 Derivation INSERT active 旁路 | 已补齐候选 DB trigger 与负测 | `derivation_no_direct_active_insert`、CT-P1-09 |
| P2-1 MANIFEST 生成文件 hash 不一致 | 已修复本次快照并明确 hash 口径 | MANIFEST §4 |
| P2-2 Tombstone DELETE 保护 | 未处理，任务卡非范围 | 保留为 P2 残留风险 |
| P2-3 Tombstone status INSERT 路径 | 未处理，任务卡非范围 | 保留为 P2 残留风险 |
| P2-4 Authorization 子表 DELETE 保护 | 未处理，任务卡非范围 | 运行时 strict_intersection 仍应 fail closed；审计完整性风险保留 |

MANIFEST 现在将 hash 分为两类：SQL、测试脚本、复跑脚本是稳定的“源文件 hash”；`test_results.json` 和 `test_run.log` 是带逐项耗时的“本次生成快照 hash”，后者在 PM 再次复跑后可能合理变化，不能再与稳定源输入 hash 混用。

## 6. 风险与关卡

- **R-0044**：Authorization UPDATE completeness 与直接 active INSERT 两条路径现均有候选 SQL / 合成空库证据，可进入“待 PM 验收的关闭候选”；风险仍为 Open。
- **R-0045**：Derivation UPDATE completeness 与直接 active INSERT 两条路径现均有候选 SQL / 合成空库证据，可进入“待 PM 验收的关闭候选”；风险仍为 Open。
- **R-0043**：本次没有修改 Tombstone SQL 或测试；其 Open / Closure Candidate 状态不受本任务改变，P3-032 记录的 DELETE+INSERT P2 残留仍在。
- **R-0040**：没有任何真实 Tauri / IPC 新证据，继续 Open / Conditional。
- 新发现 P0/P1/P2：无。P3-032 的其余三个 P2 按范围纪律明确保留，未擅自处理或降级。

角色检查点：技术架构与数据/领域模型视角确认两条直接 INSERT active 路径已由 DB fail closed；AI 信任与安全视角确认授权与 AI 派生完整性未放宽；QA / Evidence 视角确认新增负测、统计、退出合同及 hash 口径一致。

- Gate 2：执行 Agent 自审 **Pass with Conditions**；Derivation INSERT 旁路已补齐，仍待 PM 验收，真实 DB 未验证。
- Gate 3：执行 Agent 自审 **Pass with Conditions**；Authorization INSERT 旁路已补齐，仍待 PM 验收，真实 IPC 未验证。
- Gate 4：执行 Agent自审 **Pass with Conditions**；35 项合成测试通过、evidence 口径已修复，仍不代表生产 migration、WAL/backup、耐久、性能或跨平台通过。

## 7. Evidence、PM 决策与下一步建议

Evidence manifest：`lifeos/engineering/LIFEOS-P3-031/evidence/MANIFEST.md`。

本地预检：`lifeos/local_prechecks/LIFEOS-P3-033_LIFEOS-P3-033_candidate_sql_activation_insert_bypass_condition_remediation_local_precheck.md`。状态为 **Skipped / Local Model Unavailable**（connection reset by peer），符合失败降级规则，未作为工程结论或 PM 验收依据。

**[需 PM 决策]** PM 应确认：P3-032 两项 P1 是否已满足整改条件；R-0044 / R-0045 是否进入关闭候选但保持 Open；是否需要另行启动 P3-034 轻量独立复评或风险关闭决策包。建议先由 PM 复跑并验收，再决定是否需要隔离的轻量独立复评；本会话不启动后续任务。

## 8. 非冻结 / 非真实能力声明

本任务仅修改候选 SQL、合成测试与 evidence；未连接或迁移真实数据库，未连接真实 Vault、用户数据、真实 Tauri / IPC 或真实文件能力，未启用云、第三方模型、向量、同步、多设备、L3 或外部用户。未冻结 Schema/API、SQL migration、Tauri 配置、导出格式、生产 SLA 或工程基线；未关闭 R-0040、R-0043、R-0044、R-0045；未进入下一阶段，未启动 P3-034 或其他后续任务。
