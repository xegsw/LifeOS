# LIFEOS-P3-052 PM Evidence Manifest

## 边界

PM 仅复跑用户授权的本地候选 SQL 与合成 SQLite 脚本。未写入工程、历史 Evidence、真实数据库或外部系统。

## 复跑结果

| 项目 | 结果 |
|---|---|
| 独立生命周期矩阵 | 184 实例：152 PASS / 32 BYPASS / 0 FAIL / 0 UNKNOWN；runner exit 1（符合发现 bypass 的合同） |
| P1-01 伪造 lifecycle Outbox | 8/8 BYPASS |
| P1-02 retention 后 replay | 8/8 BYPASS |
| P2-01 初始 generation 非 1 | 8/8 BYPASS |
| P2-02 active 前预写 revoked 时间 | 8/8 BYPASS |
| 只读保留 | P3-052 before/after hash 清单字节一致 |

## Hash

| 文件 | SHA-256 |
|---|---|
| PM 重跑结构化结果 | `21f5187e527cea834579113d1fa6b5b10dc9e9bd40f345cfe9d0cdd55065b392` |
| PM 重跑完整性检查 | `8d5bdf8e75f76f47787cdbccd68109dd39e15728676f72093cc4e8957ed8dc3a` |
| 原独立计划 | `28c02a3cad630f119e4e2a877ddf93421f785f76b3c1c701f24ee354c450fee7` |
| 原独立 runner | `b0bf9f50ea3885d3168623d5616e35d07222b7a5cac91cde49d66d1c7d8fa56d` |

本 Manifest 支持 Rework，不关闭 R-0048，不影响 R-0049 的既有有限范围关闭。
