# LIFEOS-P3-047 Evidence MANIFEST

## 1. 范围、配置与不可外推声明

- 任务：LIFEOS-P3-047｜Outbox CAS 与生命周期控制包络 P0 整改及回归。
- 实际配置：`gpt-5.6-sol` + `xhigh`；无降级、无后备模型。
- 授权修改：P3-031 当前候选 SQL、合同测试及 evidence；P3-047 专项目录与交付物。
- 只读资产：P3-046 原报告、测试入口、全部 Evidence、PM Review、PM 新增反例脚本与结果。
- 数据范围：仅合成内存 SQLite、`lifeos/engineering/LIFEOS-P3-047/work/` 内合成文件 SQLite、代码内合成数据。
- 未连接真实 DB、Vault、真实用户文件、Tauri/IPC、网络、云、第三方模型、向量、同步、多设备、L3 或外部用户；未执行真实 migration。
- 本 evidence 只证明本候选输入在所列合成矩阵中的结果，不代表 PM Accepted、Independent Review、风险关闭、Schema/API/SQL migration/工程基线冻结或生产适用。

## 2. 复跑入口与退出合同

- 工作目录：`/Users/xxe/Documents/No.2`
- 单一入口：`lifeos/engineering/LIFEOS-P3-047/scripts/run_validation.sh`
- Python：3.9.6
- SQLite：3.51.0
- 平台：macOS 26.6.2 arm64
- 专项退出码：0；嵌套 P3-031 全量退出码：0。
- 非零条件：任一 FAIL、Not Implemented、Unknown、P3-031 非零、只读 hash 变化、候选/快照 hash 不同、integrity/quick/FK 检查失败。

测试轴：

- DB：`:memory:` 与任务目录合成文件库。
- `PRAGMA foreign_keys`：ON / OFF。
- `PRAGMA recursive_triggers`：ON / OFF。
- AC-14：`revoked` / `expired` / `superseded` × autocommit / commit / rollback × 8 DB/PRAGMA 配置。
- AC-16：audit / outbox 故障注入 × 8 DB/PRAGMA 配置。
- PM-CE-03：正常 lease / expired lease × 8 DB/PRAGMA 配置。
- PM-CE-05：generic / before retention / at retention / unconfigured，外加一次严格 after-retention 边界。

## 3. 结果统计

| 范围 | P1 PASS | P2 PASS | 合计 PASS | FAIL | NI / Unknown |
|---|---:|---:|---:|---:|---:|
| AC-01 至 AC-18 | 112 | 104 | 216 | 0 | 0 |
| PM-CE-01 至 PM-CE-05 | 24 | 49 | 73 | 0 | 0 |
| P3-044 当前直接相关回归 | 8 | 0 | 8 | 0 | 0 |
| **P3-047 专项** | **144** | **153** | **297** | **0** | **0** |

P3-031 当前全量回归：P0 18 PASS、P1 27 PASS、P2 24 PASS，合计 69 PASS，0 FAIL/Not Implemented，退出码 0。

专项逐项覆盖：AC-01..13 各 8 实例；AC-14 72；AC-15 8；AC-16 16；AC-17..18 各 8；PM-CE-01 8、PM-CE-02 8、PM-CE-03 16、PM-CE-04 8、PM-CE-05 33；P3-044 当前直接回归 8。

完整性 evidence：120 份原子快照、56 条状态机 trace、148 个文件库检查；全部 `integrity_check=ok`、`quick_check=ok`、`foreign_key_check=[]`。

## 4. 根因—补丁—反例—合法路径—剩余边界

| ID / 严重度 | 根因 | 候选补丁 | 原攻击迁移结果 | 合法路径 | 剩余边界 |
|---|---|---|---|---|---|
| PM-CE-02 / P1 | future availability 可 claim；无旧 generation CAS | append-only runtime claim command 精确匹配旧 status、availability、owner、generation；DB 当前时间校验已到期 | 8/8 PASS，原攻击均被拒绝 | 到期 pending 任务通过匹配 command 进入 processing | SQLite 不认证真实 worker 身份；command intent 的授权仍属应用层 |
| PM-CE-03 / P1 | processing 可无 owner/gen 条件直接 complete | 裸运行态 UPDATE 拒绝；complete 要求 owner、generation、未过期 lease 与当前 Authorization generation 全匹配 | 正常/过期 lease 共 16/16 PASS | 同一协议覆盖 claim、renew、retry、cancel、dead-letter、complete | 未做真实多进程竞争、崩溃恢复或性能测试 |
| PM-CE-01 / P2 | canonical hash 可畸形且 lifecycle command 未绑定 Submission | hash 精确格式；append-only Submission 与 command 绑定 namespace、idem、hash、command、subject、result | 8/8 PASS | Submission + command 在同一 savepoint/事务原子提交 | Submission 是受控意图记录，不等于认证身份或新核心实体冻结 |
| PM-CE-04 / P2 | terminal Authorization 的控制包络可改写 | terminal/tombstone 冻结 subject、generation、command、reason、blocked/terminal time | 8/8 PASS；每实例覆盖六状态与各控制字段 | active→terminal 原路径保持 | 不开放 terminal 复活、替换或重建；正式清理策略未冻结 |
| PM-CE-05 / P2 | generic terminal Outbox 过度禁删；Authorization 历史无 retention | ordinary terminal/no-lease 可删；Authorization lifecycle 需预配置 policy、创建时不可变 binding、audit/terminal command、DB-time 到期 | 33/33 PASS | 参数化 retention 到期后的窄清理；缺配置/绑定默认拒绝 | policy/binding 是候选 SQL 控制包络；正式期限、权限、运维和 SLA 待 PM 后续安排 |

runtime 操作采用统一责任模型：每条 append-only command 同时声明旧事实与目标变化，DB trigger 先比较当前事实与 DB 时间，再应用唯一变化。普通 `outbox_job` runtime mutation 不能绕过；retention binding append-only，不能由普通 runtime mutation 倒退。此机制不声称 DB 能识别调用者身份。

## 5. 只读失败基线保留证明

`evidence/input/read_only_preservation.json` 保存以下 18 个文件的 expected、before、after SHA-256 及 `unchanged`。全部 before = after = expected，全部 `unchanged=true`：

| 只读文件 | before / after SHA-256 |
|---|---|
| P3-046 交付物 | `94dac087ee1dfacbdf9b448b7fef08a90109ee7282a89293739342b9dbb800b9` |
| P3-046 Evidence MANIFEST | `9ef071fa5c74c2283125b48f0cc8c91c07f3f667849c2eac1cc14f0654a463fb` |
| P3-046 Python runner | `106a959cb9dedd49d8b2866e80aef3f4ee7010bf26800d7b3da9d83a4d851e4a` |
| P3-046 shell 入口 | `268c4c0a6a04017222cc1d1838fd9c1c3baa0d930f66087ef4767eaf142bd028` |
| P3-046 test results | `6e918b089196077bbca7e6ac0ee24b122ab2c9fb4eeb2ab358d514a622b332bb` |
| P3-046 test log | `152ef9022c18ed3bfd0c566bb50f4e9564a3f461e2fff737038666914427dce9` |
| P3-046 atomic snapshots | `6acd7d65c92752b61b96174d04a28c3320314cff260bf6d280e0267c6bca38dd` |
| P3-046 state traces | `9484580f4ff676081fb128cc935709510baa02244333fc45ce72f7d95e2fa56f` |
| P3-046 environment | `98e16eae0c263606cb92e71916b70b62b5a69437e4b46371967cf8842817f805` |
| P3-046 integrity/FK checks | `ffb7557407eb113d269e5042f1758ddf6f95457260f8d13420932d825279ef3c` |
| P3-046 P3-044 preservation input | `349b7befca98472416503d4b38da9e790a4b365efddf739a8a08b1fc63080593` |
| P3-046 source hashes | `19e1c9a58d77dd85e6120b99278975a23d6d865d38336b4c89fb9254c4eecd1b` |
| P3-046 P3-031 regression results | `7fb8bbc1f688267efc84c17674f2f527f6c2c6fe54f0a81e393c20340b0319a5` |
| P3-046 P3-031 regression log | `fe20e2f76225199e647c892f78c6fe365a0b2ebb77ff433190083b6c447b5600` |
| P3-046 PM Review | `0ce9b79aa212065f53b9f8a7cffe10e7a1587b6e37b5ab5acb7305b2260a04b5` |
| PM 反例 Evidence MANIFEST | `b5f3c954f932f068cd192ba74a792e2a0c55f47fb93132e98bf94d9909286aaf` |
| PM 原反例脚本 | `725dc0b2a4e36e9eac9949c9dbc9cb969493a67c303f5684ad268d63d8edb777` |
| PM 原反例结果 | `541fe7980e7ab7d4ce6c38188aeacac477813760ff0810ada0cfee40ff16e560` |

原 PM 反例结果保持 BYPASS / Rework 历史事实；P3-047 在自己的 runner 和结果文件中对当前候选重新执行等价攻击。

## 6. 源输入与 Evidence SHA-256

### 6.1 当前源与入口

| 文件 | SHA-256 |
|---|---|
| `P3-031/migrations/001_candidate_schema.sql` | `7000ca397db8c737681bee1edff05caefcebffb1555f30697b61feb4a0df2854` |
| `P3-047/input/001_candidate_schema.sql` | `7000ca397db8c737681bee1edff05caefcebffb1555f30697b61feb4a0df2854` |
| `P3-031/tests/run_contract_tests.py` | `49cbc1981c4b9211a36d53b4481d719cbc103574f0cc15490631ea177e121914` |
| `P3-031/scripts/run_validation.sh` | `611a2714629bb0c5dbd7d067d2e3e504e943e32fb1c9bcf52a74f6c24446230d` |
| `P3-047/scripts/run_validation.py` | `b5ff216ba75cea3cb88a22dcba821306ee772bcdfc792997db983e3bce959e22` |
| `P3-047/scripts/run_validation.sh` | `385981b4b0637198ef142d3943732da9383f47d21d4eb060969044cb3702b800` |

候选源与任务输入快照完全相同。

### 6.2 P3-047 生成 Evidence

| 文件 | SHA-256 |
|---|---|
| `evidence/test_results.json` | `46cf1d4e38b9e673e6d9a998477d2ae10176dd355fc7b813476c30c6fd4bea7d` |
| `evidence/test_run.log` | `f958b3c9afdf57fa03e9e3dbd2f04afa2328c2452e478649bb1160eba6b602f0` |
| `evidence/atomic_snapshots.json` | `7b91ff714348e66dc51c5fcccbb67d1eb117e3c7285d236b4c355dcd5b0904dc` |
| `evidence/state_machine_traces.json` | `560076f8e66308570f78fece965eef564a6ca81bb3a4e5a8438997a06fa27e6d` |
| `evidence/environment.json` | `57bca0510a649ec85f1970ea6f718ae910be3f88b4038192ac7fe7cd01ba2ef2` |
| `evidence/checks/integrity_and_fk.json` | `268e4a743896af25bb70a2196b375378873bc0d0778d7d1c888b069e377b8018` |
| `evidence/input/read_only_preservation.json` | `b358b8fbc624bdace2658fedeaf7abd7329cfa2e9fb96896f03ef180bdf0ed27` |
| `evidence/input/source_hashes.json` | `194af5ebfb41eab968cb4da910c59a7d80650797457d7ddc9c4c6e510657b62b` |
| `evidence/regressions/p3_031_test_results.json` | `2e1c04a9fa721b01c44e75681d08c5df4a52690fa04de36ae678e5d3359a9261` |
| `evidence/regressions/p3_031_test_run.log` | `4e5740af03f25ebdb85543c01ec69c984f0bd58faaf8e553b6f3a389a0dd48d1` |

### 6.3 交付物与本地预检

| 文件 | SHA-256 / 状态 |
|---|---|
| P3-047 交付物 | `1e38966d41f2b8eb17ca47c145696490ab5e886cc1f072b5c059d492914a08b2` |
| 本地预检报告 | `7c297b7a3e0c3151743dde7f6be464d32a17d7f41608cac985fddbbf2167e38c`；`Skipped / Local Model Unavailable`（请求超时） |

本地预检仅为低风险辅助；超时后按项目规则继续，不能替代 PM Review 或独立评审。

## 7. 评审关卡与风险边界

- 工程执行侧：候选补丁、五反例迁移、AC-01..18、P3-031 全量、P3-044 直接回归及 evidence 自检完成。
- QA / Evidence：执行侧材料齐备，不等于独立评审通过。
- AI 信任与安全、数据 / 领域模型：等待隔离独立复评。
- PM：需要验收并决定是否进入隔离独立复评。
- 未修改 PM 账本，未关闭任何风险，未冻结任何资产，未启动后续任务。
