# LIFEOS-P3-048 Evidence MANIFEST

## 1. 授权范围、模型与不可外推

- 任务：LIFEOS-P3-048｜Tombstone 向 Authorization 改绑旁路 P2 整改及回归。
- 实际模型：`gpt-5.6-sol` + `xhigh`；首选可用，无降级、无后备模型。
- 修改范围：P3-031 当前候选 SQL、合同测试及当前 evidence；P3-048 专项目录与交付物。
- 只读范围：P3-047/P3-046 任务、报告、runner、输入、原执行 Evidence、PM Review 与全部 PM 反例 Evidence。
- 数据范围：仅 fresh 内存 SQLite、`lifeos/engineering/LIFEOS-P3-048/work/` 内合成文件 SQLite 与代码内合成夹具。
- 未连接真实 DB、Vault、用户文件、导出路径、Tauri/IPC、网络、云/第三方模型、向量、同步、多设备、L3 或外部用户；未执行真实 migration。
- 本 Evidence 仅证明列出的候选 SQL 合成矩阵，不代表 PM Accepted、独立评审通过、风险关闭、Schema/API/migration/工程基线冻结或生产适用。

## 2. 环境、命令与退出合同

- 工作目录：`/Users/xxe/Documents/No.2`
- 命令：`lifeos/engineering/LIFEOS-P3-048/scripts/run_validation.sh`
- Python：3.9.6
- SQLite：3.51.0
- 平台：macOS 26.6.2 arm64
- 专项退出码：0；嵌套 P3-031 退出码：0。
- 配置矩阵：memory/file × `foreign_keys` ON/OFF × `recursive_triggers` ON/OFF，共 8 个配置。
- 退出非零条件：任一 FAIL/Not Implemented/Unknown、PM-CE-06 未执行、P3-047 等价统计不为 297 PASS、P3-031 非零、候选/快照不一致、只读 hash 变化或文件库检查失败。

## 3. 修复合同

原 trigger 仅在 `OLD.subject_type='authorization'` 时冻结包络，导致 generic Tombstone 可被 UPDATE 改绑。补丁把条件收窄为：`OLD` 或 `NEW` 任一侧涉及 Authorization 且 `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at_ms` 任一变化即拒绝。

未全局冻结 generic Tombstone；generic generation CAS、控制字段更新和 cleanup 正向状态变化继续按旧合同工作。P3-047 的 Outbox CAS、Submission/hash 与 retention 主体未重写。

## 4. PM-CE-06 与相邻矩阵

| 类别 | 维度 | PASS | FAIL | NI / Unknown |
|---|---|---:|---:|---:|
| original | 原 PM-CE-06 × 8 配置 | 8 | 0 | 0 |
| direction | generic→Authorization、Authorization→generic、Authorization A→B × 8 | 24 | 0 | 0 |
| field | 六 cleanup 状态 × 6 单字段 + 1 复合字段 × 8 | 336 | 0 | 0 |
| status_time_combo | 身份/包络 + cleanup_status + updated_at 同语句，六状态 × 8 | 48 | 0 | 0 |
| replace | INSERT OR REPLACE、冲突 INSERT、DELETE/reinsert、UPDATE OR REPLACE、UPSERT UPDATE × 8 | 40 | 0 | 0 |
| multirow | 合法 generic 行与非法改绑行同一 UPDATE 的整句原子失败 × 8 | 8 | 0 | 0 |
| legal | 正向状态、failed/vendor retry、cleaned、generic 既有语义、no-op × 8 | 72 | 0 | 0 |
| time | 无状态改时间与状态变化时倒退时间 × 8 | 16 | 0 | 0 |
| **P3-048 专项合计** |  | **552** | **0** | **0** |

六状态为 `accepted`、`active_blocked`、`cleanup_pending`、`cleanup_failed`、`vendor_limited`、`cleaned`。单字段为 `subject_type`、`subject_id`、`generation`、`command_id`、`reason_code`、`blocked_at_ms`；复合字段一次改写全部六项。

合法 trace 为：accepted→active_blocked→cleanup_pending→cleanup_failed→cleanup_pending→vendor_limited→cleanup_pending→cleaned。每步 `updated_at_ms` 单调增加；generic Tombstone 的 generation/control/status 既有更新路径仍通过。72 个 P3-048 before/after/trace 快照存于 `atomic_snapshots.json`。

## 5. 回归与文件完整性

| 回归入口 | P0 PASS | P1 PASS | P2 PASS | Total PASS | FAIL | NI / Unknown | 退出码 |
|---|---:|---:|---:|---:|---:|---:|---:|
| P3-048 专项 | 0 | 0 | 552 | 552 | 0 | 0 | 0 |
| P3-047 当前协议等价入口 | 0 | 144 | 153 | 297 | 0 | 0 | 0 |
| P3-031 当前全量 | 18 | 27 | 25 | 70 | 0 | 0 | 0 |

P3-047 等价入口直接复用只读 runner 中的 AC-01..18、PM-CE-01..05 与 P3-044-current 断言函数，但把输入和 work/evidence 重定向到 P3-048 目录；未调用原 P3-047 写 Evidence 的 `main()`，未覆盖旧 Evidence。等价回归另外保留 120 份原子快照和 56 条状态机 trace。

文件库检查：P3-048 专项 68 个 + P3-047 等价回归 148 个，共 216 个；全部 `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`。

## 6. 只读基线 before/after 证明

`input/read_only_preservation.json` 枚举 40 个只读文件，每项含 `expected_sha256`、`before_sha256`、`after_sha256`、`unchanged`。结果：40/40 满足 expected = before = after 且 `unchanged=true`。

| 组 | 文件数 | before/after 结果 |
|---|---:|---|
| P3-047 task/report/input/runner/execution Evidence | 16 | 16/16 unchanged |
| P3-047 PM Review 与 PM-CE-06 Evidence | 4 | 4/4 unchanged |
| P3-046 task/report/input/runner/execution Evidence | 16 | 16/16 unchanged |
| P3-046 PM Review 与 PM-CE-01..05 Evidence | 4 | 4/4 unchanged |

关键旧失败证据：

| 只读文件 | before = after SHA-256 |
|---|---|
| P3-047 PM-CE-06 脚本 | `54c1efea5de67c263f33ed3fa69d38bef01bd488e5346962b096b0072c396e50` |
| P3-047 PM-CE-06 结果（0 PASS / 8 BYPASS） | `f09d3aebd044aaf87a4ca2cfbace02a4962287c2fbb06dd69624707d81a0e7a5` |
| P3-047 PM Evidence MANIFEST | `0a9e68b2aab707a3d68e583820ebfcaf7c8a7dfa5660bb9d272566d4cfcf1855` |
| P3-046 PM 原反例脚本 | `725dc0b2a4e36e9eac9949c9dbc9cb969493a67c303f5684ad268d63d8edb777` |
| P3-046 PM 原反例结果 | `541fe7980e7ab7d4ce6c38188aeacac477813760ff0810ada0cfee40ff16e560` |

旧 BYPASS/Rework 结果仍是历史事实；新候选的 PASS 只写入 P3-048 Evidence。

## 7. 输入与输出 SHA-256

### 当前候选输入

| 文件 | SHA-256 |
|---|---|
| P3-031 candidate SQL | `56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d` |
| P3-048 SQL snapshot | `56f3c77f8fe1c4baec690b6b2fb9f849aee7a6bb9d433de61d7ea9fc317eac6d` |
| P3-031 tests | `6729d48eeb9e523b5875165c053701602d6e10d5171fd27f235e680dcb34b3b5` |
| P3-031 shell | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` |
| P3-048 Python runner | `6d5d4b75d3b6439aa903d554d29b80c30ad1470539bb802115fcdda67b3156c2` |
| P3-048 shell | `385981b4b0637198ef142d3943732da9383f47d21d4eb060969044cb3702b800` |

### P3-048 Evidence

| 文件 | SHA-256 |
|---|---|
| `test_results.json` | `fc698f8e46230038f5d9110db3b49e1e5971ca11750bea9fde1ca018a5787fb1` |
| `test_run.log` | `01729149ba61be7293aae67e6f2b898d78314898f2e47a5febae7222ef48c92e` |
| `atomic_snapshots.json` | `3fe8f21def1d23a92768f4626c5f6a2974d72938e62283e0fbba3dbab7924a80` |
| `checks/integrity_and_fk.json` | `d4c46c8c75a20b0a8d18d4773b56170b4a1d2daee5021938c2d7878512e329d7` |
| `environment.json` | `c8cdc5c2f35e40e97ae8744db52c37cece2914bc2e38ba7e4a88f51a82d63548` |
| `input/read_only_preservation.json` | `3cea21fa5d2ae4e67d254de3029ba1135ade9c3fa12e4c32377394c554032c6d` |
| `input/source_hashes.json` | `cc15690e84432584260e4ca8cf19490ef3607658700e0db900a22368222d16ae` |
| `regressions/p3_047_equivalent_results.json` | `85518c2b3a5fa8929b675910ba32756af96388ce08070c2cbce3700d21b29d1f` |
| `regressions/p3_047_equivalent_atomic_snapshots.json` | `91dba2eb5e2fd52174f0ec71015aca1e7f91adbab76989ff5fffbe6f283addfe` |
| `regressions/p3_047_equivalent_state_machine_traces.json` | `560076f8e66308570f78fece965eef564a6ca81bb3a4e5a8438997a06fa27e6d` |
| `regressions/p3_047_equivalent_integrity_and_fk.json` | `268e4a743896af25bb70a2196b375378873bc0d0778d7d1c888b069e377b8018` |
| `regressions/p3_031_test_results.json` | `59fc105b4a4e49330271299a4f881d9a59bf97c6b77fce4eb313f8f88943c2a7` |
| `regressions/p3_031_test_run.log` | `e3e07027121e117dca135e17eb665c7c79a705050bb0b15c8b4cfb172ef0a314` |

### 报告与本地预检

| 文件 | SHA-256 / 状态 |
|---|---|
| P3-048 交付物 | `adb589a335c42e706e4c618a63147c72fc31878ed1297fe02d382afb774b45d4` |
| 本地预检 | `6bd0753fa9b13879414f71c50336c7faab2fac6468fad714f160de90188f1c17`；`Skipped / Local Model Unavailable`（请求超时） |

## 8. 角色、关卡与剩余边界

- 技术架构 / 数据完整性执行侧检查：通过；补丁仅扩展 OLD/NEW 判断。
- Gate 2、Gate 3、Gate 4：执行侧候选证据通过，仍需 PM 复跑和隔离独立复评。
- SQLite 不认证真实调用者；未验证真实迁移、生产并发、权限入口、备份恢复、性能容量或跨平台。
- 未修改 PM 账本，未关闭风险，未冻结资产，未恢复工程基线，未进入下一阶段，未启动后续任务。
