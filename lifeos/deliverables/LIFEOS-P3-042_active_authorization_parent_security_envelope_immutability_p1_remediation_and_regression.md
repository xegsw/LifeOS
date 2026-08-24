# LIFEOS-P3-042｜Active Authorization 父表安全包络字段不可变 P1 整改与回归

## 1. 任务信息与边界

- 任务状态：专项工程执行完成，等待 PM 验收；不代表 Accepted 或风险关闭。
- 实际模型：`gpt-5.6-sol` + `xhigh`；首选路由可用，未触发 `gpt-5.5` 后备或任何降级。
- 主责角色检查：技术架构/工程整改检查已完成。协审输入已按 AI 信任安全、数据/领域模型、QA Evidence 与 PM 检查点整理；Gate 2/3/4 仅形成候选工程证据，正式通过结论仍由对应评审与 PM 作出。
- 授权边界：只改 P3-031 候选 SQL、相关合同测试/evidence，并新建 P3-042 runner/evidence。本任务未修改 P3-039/P3-040/P3-041 原件、PM 账本或 Stitch，未启动 P3-043。
- 数据/能力边界：只使用合成空库与合成数据、内存 SQLite 和任务目录文件 SQLite；未连接真实 DB/Vault/文件/Tauri/IPC，未执行真实 migration，未使用网络、云/第三方模型、向量、同步、多设备、L3 或外部用户。

## 2. 实际修改

1. `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql`
   - 新增 `authorization_security_envelope_immutable_while_active`。
   - 当 `OLD.status='active'` 时，以 `IS NOT` 逐字段比较八个安全包络字段；任何实际变化统一 `RAISE(ABORT, 'active_authorization_security_envelope_immutable')`。
2. `lifeos/engineering/LIFEOS-P3-031/tests/run_contract_tests.py`
   - 新增 CT-P1-17/18，覆盖八字段、NULL、复合、多行、no-op、合法激活/退休/新版本路径。
   - 仅扩展合成 fixture 参数，未接入真实能力。
3. `lifeos/engineering/LIFEOS-P3-031/evidence/`
   - 更新 manifest、44 项结构化结果和完整日志。
4. `lifeos/engineering/LIFEOS-P3-042/`
   - 新建双后端专项 runner、候选 SQL 快照、隔离回归快照、环境/完整性/hash/preservation evidence。

P3-031 shell 未修改。P3-040 通过临时项目树隔离复跑，其原始目录无写入；P3-041 五个原始 evidence 文件前后 hash 一致。

## 3. Authorization 全字段安全矩阵

| 字段 | 分类 | 当前保护/允许路径 | 测试依据 |
|---|---|---|---|
| `id` | 已有结构身份 | PK；本测试 FK=ON 且已有子行时改名失败 | `update_id_active` PASS/PASS |
| `logical_key` | 已有版本身份 | `authorization_version_identity_immutable` | `update_logical_key_active` PASS/PASS |
| `grantor_ref` | 本任务安全包络 | active 不可改 | `update_grantor_active` PASS/PASS |
| `processor` | 本任务安全包络 | active 不可改 | `update_processor_active` PASS/PASS |
| `purpose` | 本任务安全包络 | active 不可改 | `update_purpose_active` PASS/PASS |
| `location` | 本任务安全包络 | active 不可改 | `update_location_active` PASS/PASS |
| `status` | 已有生命周期 | forward-only；合法退休需 generation+1 与 audit/outbox | 回退拒绝及三种退休均 PASS/PASS |
| `version_no` | 已有版本身份 | 原地修改拒绝 | `update_version_no_active` PASS/PASS |
| `generation` | R-0048 非范围 | 仅保证不下降；独立升高仍是已知风险，不是维护白名单 | 2 个 R-0048 用例 KNOWN_LIMITATION |
| `valid_from_ms` | 本任务安全包络 | active 不可改 | `update_valid_from_active` PASS/PASS |
| `expires_mode` | 本任务安全包络 | active 不可改 | at↔indefinite PASS/PASS |
| `expires_at_ms` | 本任务安全包络、nullable | `IS NOT` NULL 安全比较 | 值改、NULL↔值 PASS/PASS |
| `revoked_at_ms` | 相邻生命周期观察 | 当前 active 可改；本任务未擅改生命周期合同 | KNOWN_LIMITATION/PASS reproduction |
| `policy_version` | 本任务安全包络 | active 不可改 | `update_policy_version_active` PASS/PASS |
| `supersedes_id` | 已有版本身份 | 原地修改拒绝 | `update_supersedes_id_active` PASS/PASS |
| `created_at_ms` | 相邻来源/历史观察 | 当前 active 可改；未纳入窄 trigger | KNOWN_LIMITATION/PASS reproduction |
| `updated_at_ms` | 明确维护字段 | active 可单独更新 | `updated_at_only` PASS/PASS |

R-0049 管理的是 `authorization_scope`、`authorization_action`、`authorization_policy` 的 terminal 历史语义，不是父表字段；仍列为本任务非范围。

## 4. 整改映射与反例重放

八字段均由同一个真实 SQLite `BEFORE UPDATE OF ... ON authorization` trigger 保护，不依赖应用层约定、CHECK 偶然失败或测试期望替换。错误码在单字段、复合字段、退休同时改字段和多行更新中保持一致；多行 UPDATE 发生任一 active 行变异时整条语句原子回滚。

| P3-041 P1 原名 | P3-042 memory | P3-042 file |
|---|---|---|
| `update_processor_active` | PASS | PASS |
| `update_purpose_active` | PASS | PASS |
| `update_location_active` | PASS | PASS |
| `update_grantor_active` | PASS | PASS |
| `update_expiry_to_indefinite_active` | PASS | PASS |
| `update_policy_version_active` | PASS | PASS |
| `compound_field_update_active` | PASS | PASS |

补充用例 `valid_from_ms`、`expires_at_ms` 时间单改、at→indefinite、indefinite→at、NULL→值、退休+包络复合更新、多行原子回滚全部 PASS/PASS。active 全八字段重复同值/no-op 和仅 `updated_at_ms` 更新均合法。

合法路径未回退：proposed/granted 激活前配置并激活、active→revoked/expired/superseded 的 generation+1 + audit/outbox、旧版本 superseded 后创建并激活安全包络不同的完整新版本，均 PASS/PASS。需要改变授权含义时必须创建新版本，不能改写旧 active 版本。

## 5. 三套测试与 Evidence 结果

| 测试集 | 统计 | 缺陷统计 | 退出码 |
|---|---|---|---:|
| P3-031 | P0 18 PASS；P1 18 PASS；P2 8 PASS；总计 44/44 | FAIL 0；Not Implemented 0；Unknown 0 | 0 |
| P3-040 隔离全量 | P1 126 PASS；P2 2 PASS；总计 128/128 | FAIL 0；Not Implemented 0；Unknown 0 | 0 |
| P3-042 | P1 26 PASS；P2 26 PASS；P2 Known Limitation 26 | 新增 P0 0；新增 P1 0；FAIL 0；Not Implemented 0；Unknown 0 | 0 |

P3-042 为 13 个 P1 逻辑用例、13 个 P2 合法/既有保护逻辑用例、13 个 P2 非范围观察逻辑用例，各自在 memory/file 执行。39 个文件库的 integrity/quick/FK 检查全部通过。

稳定 hash：

- 候选 SQL：`50d253...cf7c` → `ceedad...a6b`
- P3-031 tests：`074e93...072e` → `e934df...d275`
- P3-042 runner：`f76d78ccb9b724675070198966fe048f62356af5a68cbe4f8ad927aaa0628c42`
- P3-042 results/log：`2e60c22289971d96662e2777497abe33439531c4458fff5cd3dc6ce8835d70f6` / `27e267a441a244ecc7908fafa7bfe165333e9d9994d1bc2d995e4d58ef298acd`
- P3-041 五个原始 evidence 文件执行前后均与既有期望 hash 一致；完整 hash 表见 preservation JSON。

完整命令、逐文件 hash、候选快照、结构化统计与日志见 `lifeos/engineering/LIFEOS-P3-042/evidence/MANIFEST.md`。

## 6. 非范围、剩余风险与事实校正

- R-0048 未修复：5 个 audit/outbox 预置/UPDATE/DELETE与 2 个 generation 用例，共 7 个逻辑用例继续复现。
- R-0049 未修复：4 个 terminal 子表 INSERT/UPDATE 用例继续复现。
- P3-041 原始 evidence 中 12 个 P2 记录保持不变；其中 `update_valid_from_active` 被本任务目标明确要求纳入八字段整改，现已转为 P3-042 定向 PASS。因此当前仍可复现且属于 R-0048/R-0049 的是 11 个，而不是 12 个。报告不把历史证据保留与当前行为混为一谈。
- 新的相邻 P2 观察：active 时 `created_at_ms`、`revoked_at_ms` 可修改。它们可能涉及来源/生命周期语义，但并非任务卡列出的八字段同根安全包络；已保留最小复现，未扩大 trigger。需 PM 决定后续分类与是否另立任务。
- R-0040、R-0043、R-0044、R-0046、R-0047、R-0048、R-0049 均未关闭；R-0045 未改变。

## 7. 不可外推与建议

本结果只证明当前候选 SQL 在合成空库/合成数据、Python SQLite 3.51.0、内存与任务文件库条件下的行为。不能外推到真实非空旧库升级、真实用户数据、Vault/文件/Tauri/IPC、并发/性能/跨平台、生产 SLA，也不构成 Schema/API/SQL migration/工程基线冻结或真实能力准入。

工程执行建议：本任务可提交 PM 验收，并在 PM 明确创建后交由隔离会话执行 P3-043；本会话未启动 P3-043，也不得承担自己的独立复评。PM 仍需决定 `created_at_ms`/`revoked_at_ms` 的风险归类，并确认任务卡“历史 12 个 P2 保留”与“当前 R-0048/R-0049 仅 11 个可复现”的口径。

## 8. Local Precheck / 本地预检

- 计划命令：`python3 lifeos/tools/local_precheck.py lifeos/deliverables/LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression.md`
- 实际报告路径：`lifeos/local_prechecks/LIFEOS-P3-042_LIFEOS-P3-042_active_authorization_parent_security_envelope_immutability_p1_remediation_and_regression_local_precheck.md`
- 结果：`Skipped / Local Model Unavailable`；局域网本地模型调用超时（`Errno 60`），按项目允许跳过规则继续，不阻塞任务。PM 仍须按原流程复核。
- 本地预检只作覆盖/措辞辅助，不是 PM Review、Independent Review、Accepted、风险关闭或准入结论。
