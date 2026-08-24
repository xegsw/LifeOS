# LIFEOS-P3-052 Evidence Manifest

## 结论与范围

- 结论：**Rework**。独立主证据在全部八个 SQLite 配置中复现 2 个 P1 和 2 个 P2 合同 bypass；因此不满足任务卡“0 P0/P1/明确 P2 bypass”的 Pass 条件。
- 范围：只审查 P3-048 当前候选 SQL（SHA-256：`56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d`）与合成 SQLite；不修改候选工程、历史 Evidence 或主账本。
- 安全边界：未连接真实数据库、用户数据、Vault、Tauri/IPC、网络、云服务或第三方系统；文件型数据库均为临时合成库。
- 影响边界：本 Evidence 仅作为 R-0048 风险决策前置输入；不关闭 R-0048，不影响已关闭 R-0049，不冻结资产、不恢复工程基线、不启用真实能力、不进入下一阶段。

## 独立性与封存顺序

1. 在读取 P3-046/P3-047/P3-048/P3-049/P3-050 的攻击脚本、结果、Review 或 Manifest 前，已创建 `independent_attack_plan.md`。
2. 计划 SHA-256 已封存于 `independent_attack_plan.sha256`：`28c02a3cad630f119e4e2a877ddf93421f785f76b3c1c701f24ee354c450fee7`。
3. `independent_lifecycle_review.py` 仅以 Python 标准库直接加载当前 candidate SQL；未 import、调用、复制或机械改写 P3-047 runner 或历史 attack helper。
4. 独立矩阵完成并落盘后，才读取历史 PM-CE-01 至 PM-CE-05、P3-047 PM-CE-06、P3-048/P3-050 Review/Evidence 作延迟对照。

## P3-052 独立矩阵

| 项目 | 结果 |
|---|---:|
| 逻辑用例 | 23 |
| 配置 | memory/file × FK ON/OFF × recursive triggers ON/OFF = 8 |
| 总实例 | 184 |
| PASS | 152 |
| BYPASS | 32 |
| FAIL / UNKNOWN | 0 / 0 |
| 文件 integrity / quick / FK 检查异常 | 0 |
| 退出码 | 1（因发现 bypass，符合 runner 退出合同） |

四类唯一发现各在八配置中稳定复现：

| ID | 级别 | 已验证事实 |
|---|---|---|
| C01 | P1 | 可直接插入 `authorization_state_change` OutboxJob，并以 active Authorization 的当前 generation 完成；无需 lifecycle command 或 AuditEntry，形成伪造的已完成 lifecycle 投递。 |
| C08-C09 | P1 | lifecycle job 通过 retention 删除后，可复用已删除的 job ID/idempotency key 重新插入不同 payload；保留的 binding 不阻止该重放。 |
| D01-a | P2 | 新 Authorization 可在 `generation=7` 时完成配置并激活；候选仅要求 `generation >= 1`，未落实合同的初始值 `1`。 |
| D01-b | P2 | proposed 行可预写 `revoked_at_ms` 并随后激活；active 非 revoked 状态未被强制为 NULL。 |

## 回归与历史对照

- P3-031 在隔离临时副本 `/private/tmp/lifeos-p3-052-p3-031.deqZGB` 复跑：70 PASS（P0 18、P1 27、P2 25），0 FAIL / Not Implemented，退出码 0。结果副本：`p3_031_isolated_results.json`；日志副本：`p3_031_isolated_test_run.log`。
- P3-031 已覆盖并通过当前 PM-CE-01 至 PM-CE-06 回归；P3-052 另以不依赖旧 helper 的独立 fixture 验证 PM-CE-01 hash/Submission binding、PM-CE-02 future availability/CAS、PM-CE-03 completion CAS、PM-CE-04 Tombstone control envelope 和 PM-CE-05 generic cleanup 语义。
- P3-046 原 PM 反例（5 BYPASS）与 P3-047 原 PM-CE-06（8 BYPASS）仅作为历史对照，未被作为本轮主证据或写入覆盖。
- P3-050 的独立 Pass 仅覆盖 Tombstone 改绑路径，不能覆盖或抵消本轮发现的完整 R-0048 Outbox / initial-lifecycle 缺口。

## 只读保留

- `read_only_hashes_before.txt` 与 `read_only_hashes_after.txt` 字节一致。
- 核对集包含 P3-046/P3-047 执行 Evidence、两套 PM 反例脚本/结果/Manifest、当前 P3-048 candidate SQL 与其 Manifest，共 14 个只读文件。
- 所有 14 个 SHA-256 均保持一致；历史失败 Evidence 未被重写。

## 文件索引

| 文件 | 用途 |
|---|---|
| `independent_attack_plan.md` | 延迟读取前封存的攻击计划 |
| `independent_attack_plan.sha256` | 计划哈希封存 |
| `independent_lifecycle_review.py` | 自建独立 runner |
| `independent_attack_results.json` | 184 个结构化实例结果与 bypass 明细 |
| `independent_attack_run.log` | 本轮 runner 摘要日志 |
| `independent_attack_environment.json` | Python / SQLite / 配置与独立性声明 |
| `integrity_and_fk.json` | 每个实例的完整性检查 |
| `p3_031_isolated_results.json` | 隔离 P3-031 回归结果副本 |
| `p3_031_isolated_test_run.log` | 隔离 P3-031 回归日志副本 |
| `read_only_hashes_before.txt` / `read_only_hashes_after.txt` | 历史资产保留证明 |

## P3-052 Artifact Hashes

| 文件 | SHA-256 |
|---|---|
| `independent_attack_plan.md` | `28c02a3cad630f119e4e2a877ddf93421f785f76b3c1c701f24ee354c450fee7` |
| `independent_lifecycle_review.py` | `b0bf9f50ea3885d3168623d5616e35d07222b7a5cac91cde49d66d1c7d8fa56d` |
| `independent_attack_results.json` | `7804f20d84bb4d44ce56cbf3bb112d9caa660dd8cf87894f99d376f640c8e2ab` |
| `independent_attack_environment.json` | `7b5a1d08239179a073ce35c1022930f2c4e4031587ff04fdd6bdc083e1c36f70` |
| `integrity_and_fk.json` | `8d5bdf8e75f76f47787cdbccd68109dd39e15728676f72093cc4e8957ed8dc3a` |
| `p3_031_isolated_results.json` | `645e7339bb5c8f50b115750f0ed03f0a2419d2b9a3de5d879cb648f5d4b74e74` |
| `p3_031_isolated_test_run.log` | `988a19ba64bd3f9271bd2d0046839ccb77968a20c5bc7bd6267f9c9d50ab5390` |
| `read_only_hashes_before.txt` / `after.txt` | `8df537568898e5857d131abd263a7e1a3e6a8402e4860f19b1dbb993372aaf8b` |

## Local Precheck / 本地预检

- 报告：`lifeos/local_prechecks/LIFEOS-P3-052_LIFEOS-P3-052_r0048_lifecycle_evidence_full_scope_isolated_independent_re_review_local_precheck.md`。
- 状态：`Skipped / Local Model Unavailable`。首次调用受 sandbox 限制；获准的局域网重试由对端以 `Connection reset by peer` 终止。
- 处理：按项目允许跳过规则继续人工复核。该预检不构成 PM Review、Independent Review、风险关闭或冻结结论。
