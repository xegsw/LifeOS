# LIFEOS-P3-031 / P3-033 / P3-038 / P3-040 / P3-042 / P3-044 / P3-046 / P3-047 / P3-048 Evidence Manifest

## 1. 范围声明

- 基线任务：LIFEOS-P3-031 候选 SQL migration 编写 + 合成空库合同测试实现。
- 既有整改：LIFEOS-P3-033 Authorization / Derivation 直接 INSERT active 旁路条件整改。
- 本次整改：LIFEOS-P3-038 Tombstone DELETE / REPLACE、非 `accepted` 初始 INSERT、active Authorization 子表 DELETE 三项残留 P1 整改。
- 最新整改：LIFEOS-P3-040 active Authorization 子表 INSERT / UPDATE / REPLACE / OLD-NEW 改绑与状态翻转逃逸 P1 整改；active 退出采用 generation +1、audit/outbox 前置、终态不可复活的候选合同。
- 当前整改：LIFEOS-P3-042 active Authorization 父表八个安全包络字段不可原地改写；NULL、复合、多行及合法生命周期路径由合同测试覆盖。
- 最新整改：LIFEOS-P3-044 在冲突解析前拒绝以主键或版本唯一键替换既有 active Authorization，并拒绝 active 父记录直接 DELETE，封堵 REPLACE/DELETE+INSERT 重建旁路。
- 当前整改：LIFEOS-P3-046 将 P3-045 条件包实现为一次性 append-only lifecycle command；active→terminal 在同一 SQLite 语句/事务生成 generation +1、DB 时间、最小 AuditEntry 与 OutboxJob，并增加 append-only audit、outbox 载荷/运行态、terminal 历史及 Authorization tombstone 受控清理约束。
- 最新整改：LIFEOS-P3-047 以 append-only Submission 绑定 lifecycle command，以 append-only runtime command 统一 claim/renew/retry/cancel/dead-letter/complete 的 availability、owner、lease、generation CAS；冻结 Authorization tombstone 控制包络，并以预配置 retention policy + 每任务不可变 binding 区分 Authorization 生命周期历史与普通终态 Outbox 清理。
- 当前整改：LIFEOS-P3-048 将 Authorization Tombstone 控制包络不可变条件从仅检查 `OLD` 扩展为同时检查 `OLD` / `NEW` subject type，拒绝 generic→Authorization、Authorization→generic 与 Authorization A→B 改绑，同时保留 generic Tombstone 既有 generation CAS 与 cleanup 状态语义。
- 数据边界：仅使用内存 / 临时合成 SQLite 空库和代码内合成夹具。
- 未连接真实 DB、真实 Vault、真实用户文件、真实 Tauri / IPC、云、第三方模型、向量、同步、多设备、L3 或外部用户。
- `IPC-P0-*` 仅测试进程内纯 DTO parser；没有创建 handler、capability 或 Tauri 配置。
- 本 evidence 不代表 Schema/API、SQL migration 或工程基线冻结，也不关闭 R-0040、R-0043、R-0044、R-0046、R-0047、R-0048、R-0049、R-0050，不重新打开或关闭 R-0045。

## 2. 复跑入口与环境

- 工作目录：项目根目录 `/Users/xxe/Documents/No.2`
- 命令：`lifeos/engineering/LIFEOS-P3-031/scripts/run_validation.sh`
- Python：3.9.6
- SQLite：3.51.0（Python bundled runtime；FTS5 已启用）
- 网络：未使用
- 临时数据库：每个 DB 测试使用新内存库；测试总控在本 evidence 目录下创建并自动清理空临时目录。
- 退出合同：任一测试 FAIL（包括任一 P0 FAIL）均返回非零；本次退出码为 0。

## 3. 结果摘要

| 严重级别 | PASS | FAIL | Not Implemented |
|---|---:|---:|---:|
| P0 | 18 | 0 | 0 |
| P1 | 27 | 0 | 0 |
| P2 | 25 | 0 | 0 |
| **Total** | **70** | **0** | **0** |

覆盖关系：

- P0：DB-P0-01 至 DB-P0-15、IPC-P0-01 至 IPC-P0-03。
- P1：既有 P3-040/P3-042/P3-044 active parent/children 与替换/重建防线保持；AC-06、AC-07、AC-14、AC-15、AC-16 和 PM-CE-02/03 覆盖 runtime command 的 availability/owner/lease/generation CAS、三终态原子退休、successor 激活及故障回滚。
- P2：既有 Derivation/Tombstone 合同保持；AC-01 至 AC-05、AC-08 至 AC-13、AC-17、AC-18 和 PM-CE-01/04/05/06 覆盖 Submission/hash 绑定、append-only 历史、Tombstone OLD/NEW 双侧包络、参数化 retention 与普通终态 Outbox 清理。
- CT-P1-01 对 migration 注入语法故障并显式 rollback，验证无业务表、索引或 trigger 残留。

## 4. Evidence 文件与 hash 口径

### 4.1 源文件 hash（复跑输入）

源文件 hash 用于确认本次测试实际运行的候选 SQL与测试逻辑；只有源文件未变时，结果才可视为同一输入的复跑。

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `migrations/001_candidate_schema.sql` | 候选空库 migration | `56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d` |
| `tests/run_contract_tests.py` | 合成 DB、事务 guard 与纯 DTO 合同测试 | `6729d48eeb9e523b5875165c053701602d6e10d5171fd27f235e680dcb34b3b5` |
| `scripts/run_validation.sh` | 单一复跑入口；保留 Python 非零退出码 | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` |

### 4.2 本次生成文件 hash（运行快照）

生成文件含逐项耗时，每次复跑均可能变化。下列 hash 仅对应本 manifest 更新前最近一次 P3-048 复跑快照；PM 再次复跑覆盖文件后，应按新快照核对，不能把旧生成文件 hash 当作稳定源输入 hash。

| 文件 | 用途 | 本次快照 SHA-256 |
|---|---|---|
| `evidence/test_results.json` | 机器可读逐项结果与统计 | `59fc105b4a4e49330271299a4f881d9a59bf97c6b77fce4eb313f8f88943c2a7` |
| `evidence/test_run.log` | 完整本次复跑日志 | `e3e07027121e117dca135e17eb665c7c79a705050bb0b15c8b4cfb172ef0a314` |

以上 hash 对应 2026-08-20 P3-048 最终复跑；若候选 SQL、测试或脚本变更，必须重跑并更新源文件 hash 与生成快照。

## 5. 强制层级与证据边界

- DB 强制：枚举、FK、exact-one、不可变版本/Feedback、current pointer ownership、Derivation/Authorization 直接 active INSERT 拒绝与 UPDATE activation completeness、active Authorization 父子写入/替换/重建拒绝、Submission 绑定的一次性 lifecycle command、同事务 terminal generation/time/audit/outbox、AuditEntry append-only、OutboxJob immutable payload + runtime-command CAS、terminal parent/children 与 OLD/NEW 双侧 Authorization Tombstone 控制包络不可变、参数化 retention cleanup gate、版本 identity、Feedback retract/dependency、Tombstone 单向状态、unique/partial index 与 idempotency。
- 事务 guard / 服务层候选：Authorization `strict_intersection`、权威消费门、stale generation CAS、恢复评估、FTS post-filter、详情 token。测试为纯函数或受控 SQL 组合，不冒充真实应用入口。
- DTO parser：四 invoke 的封闭 action、精确字段集合、版本门和 destruct 必填项。仅为合同解析测试，不是 IPC 端到端证据。
- `active_blocked`：DB trigger 只约束状态转换；进入该状态前“所有消费门已拒绝”的证明仍属于应用事务 guard，不能由 SQLite 单独证明。

## 6. 已知限制与后续复核入口

- 未做真实 DB 升级、WAL/backup、进程杀死、性能/容量、跨平台或真实 IPC 验证。
- `schema_checksum` 当前为候选标识，尚非发布期构建系统计算并签入的生产 checksum。
- 合成合同与 P3-048 文件型回归通过只能支持 PM 验收和后续隔离复评输入；不得据此关闭 R-0048/R-0049 或冻结 Schema/API，全部风险状态仍由 PM 维护。
- P3-048 专项 evidence 与本地预检由本任务独立目录保存；本地预检不作为验收依据。
- 本会话未启动后续任务，也不承担本补丁的独立复评。
