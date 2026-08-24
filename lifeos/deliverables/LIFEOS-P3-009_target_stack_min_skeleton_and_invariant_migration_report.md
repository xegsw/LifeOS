# LIFEOS-P3-009｜目标技术栈最小工程骨架与 P3-001 不变量迁移报告

- 任务类型：工程实现型任务 / 目标技术栈迁移任务
- 主责角色：工程负责人
- 协审角色：技术架构负责人、数据与权限负责人、QA / 测试负责人
- 日期：2026-08-11
- 结论：**Pass with Conditions**

## 1. 任务摘要

1. **[事实]** 已在 `lifeos/engineering/LIFEOS-P3-009/` 建立隔离的 TypeScript + Node.js + SQLite 最小工程骨架。运行时为随附 Node v24.14.0，SQLite 使用内建 `node:sqlite`，未联网安装依赖。
2. **[事实]** 已将 H1-H9 与 T-ARCH 重建为 10 个可执行测试，最终结果为 **10 PASS / 0 FAIL，P0 失败 0，P1 Open 0**。证据快照 SHA-256 为 `64d18d9c056571c94077e94ff4efdd3ac720233feaa376cadff0593045345d2a`。
3. **[事实]** 用户原文不可变、五类内容身份、消费入口 fail closed、撤回/删除不复活、Project/location/processor 边界和八类默认关闭能力已形成可执行覆盖。
4. **[事实]** 未修改 P3-001；未处理真实数据、真实 Vault；未接入真实 Tauri/IPC、文件导出、外部模型、向量、同步、多设备、L3 或外部用户。
5. **[推断]** P3-001 的根安全合同可以迁移到模块化 TypeScript/SQLite 骨架，但当前结果只证明合成、单进程、受控测试包边界，不证明生产耐久、真实 Tauri 或正式导出/恢复协议。

## 2. 实际创建 / 修改文件清单

工程根文件：`README.md`、`package.json`；合成夹具：`fixtures/synthetic_v1.json`；源码：`src/types.ts`、`src/content-identity.ts`、`src/capability-policy.ts`、`src/store.ts`、`src/consumption-gate.ts`、`src/lifeos.ts`；测试与脚本：`tests/invariants.test.ts`、`scripts/validate.mjs`；证据：`evidence/MANIFEST.md`、`test_results.json`、`test_run.log`、`invariant_migration_matrix.md`、`default_off_matrix.md`、`architecture_conformance.md`；本报告为唯一创建的 `lifeos/deliverables/` 文件。

**[事实]** 本会话对 P3-001 只执行读取，所有写入工具调用均只指向 P3-009、指定交付报告及本地预检输出；未修改 P3-001。当前工作树将整个 P3-001 目录显示为既有未跟踪目录，因此不能用 Git diff 作为逐文件前后证明。项目账本、冻结资产、Stitch、PRD 和背景包均未修改。

## 3. 工程骨架说明

- `AuthorityStore`：以 SQLite 保存 Source、Artifact、不可变 ArtifactVersion、Authorization、Derivation、Feedback、Tombstone、OutboxJob 和 Submission；FTS5 为派生查询路径。
- `consumption-gate`：消费前重检 subject、Project、精确 version、artifact/source generation、tombstone、purpose、location、processor 和唯一有效 Authorization；未知或冲突一律拒绝。
- `content-identity`：运行时明确区分 `user_original`、`ai_generated`、`ai_inference`、`ai_suggestion`、`external_reference`；非用户原文必须携带 evidence。
- `capability-policy`：八类非本切片能力使用冻结的 false 配置，并在运行调用时抛出 `DisabledCapability`。
- `LifeOS`：提供捕获、读取、FTS 搜索、恢复候选、下一步建议、Feedback、撤回/删除和内存测试包导出；所有消费入口复用同一 fail-closed 门。

**[边界]** 这些模块是“不变量落点”，不是生产模块边界或 Schema/API 冻结。内存导出不触及系统路径；没有 Renderer、IPC、插件、网络或外部适配器。

## 4. 运行命令与测试结果摘要

```bash
cd lifeos/engineering/LIFEOS-P3-009
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node scripts/validate.mjs
```

最终复跑环境：macOS arm64、Node v24.14.0、Node 内建 SQLite/FTS5。结果：10 tests、10 pass、0 fail、P0 fail 0。`validate.mjs` 会复跑测试，写入原始日志、机器可读摘要、源码/夹具 SHA-256 快照、迁移矩阵和默认关闭矩阵；任何测试失败均以非零退出码结束。

**[事实]** 首轮实现复跑曾因 JSON snake_case 到 TypeScript camelCase 的夹具映射错误出现 6 个建数失败，修正集中映射后业务测试全过。随后发现 Node 24 默认 reporter 使用 `ℹ pass`，证据生成器最初误解析为失败；解析器已兼容并重新生成最终 10/10 证据。最终 manifest 与机器结果一致。

## 5. H1-H9 / T-ARCH 迁移矩阵

| 不变量 | 状态 | 本任务可执行覆盖 | 尚未迁移 / 限制 |
|---|---|---|---|
| H1 / T-SCOPE | PASS | 个人、本地、单设备切片；非范围能力关闭 | 无真实 UI / Gate 5 价值证据 |
| H2 / T-ID | PASS | 原文不可变；五类身份包络；AI/外部身份需证据；Feedback 不覆盖原文 | 无真实外部来源适配器 |
| H3 / T-SAVE | PASS（窄测） | 权威事务失败回滚；已提交原文不受索引失败影响；outbox 幂等结构 | 进程杀死边界、fsync/掉电、生产耐久未迁移 |
| H4 / T-GATE | PASS | read/search/recovery/suggest/export 统一重检授权、来源关联、版本、tombstone、generation、evidence、purpose/location/processor | 无真实 IPC、外部处理者或跨进程竞态 |
| H5 / T-DEL | PASS（活跃阻断） | revoke/delete 分别验证 read/search/recovery/suggest/export 不复活，旧 context 失效 | 异步物理清理、正式 restore 协议未迁移 |
| H6 / T-IPC-OFF | PASS（关闭态） | Tauri、Vault、文件导出运行时拒绝 | 真实 Tauri 矩阵未运行；R-0040 不变 |
| H7 / T-DATA | PASS（合成层） | synthetic-disposable 标记与私钥/AWS key/email/用户路径模式扫描 | 不授权真实数据 |
| H8 / T-OFF | PASS | Vault、Tauri/IPC、文件导出、外部模型、向量、同步/多设备、L3、外部用户八项负测 | 不存在启用路径 |
| H9 / T-EXPORT | PASS（内存层） | Project 闭包、内容身份、撤回后排除 | 无最终 UI、文件格式、备份恢复 |
| T-ARCH | PASS（最小层） | SQLite+FTS-first；权威/派生/outbox/tombstone 分责；消费门回连权威 | lease fencing、长 rebuild 非阻塞、SQLite-aware 备份仅映射 |

完整矩阵见 `evidence/invariant_migration_matrix.md`。上述 PASS 仅限本任务边界。

## 6. 默认关闭能力矩阵

八类能力均为“配置 false + 运行时负测抛错”：真实 Obsidian Vault、真实 Tauri/IPC、文件系统导出/路径 scope、云/第三方模型、向量索引、同步/多设备、L3 动作、外部用户。本骨架不存在 UI、IPC 或 adapter 旁路。完整矩阵见 `evidence/default_off_matrix.md`。

## 7. 与 P3-001 的差异

- **[事实]** 从 Python 单文件语义 harness 迁移为 TypeScript 多模块结构，并使用 Node 内建 SQLite；这是更接近目标应用语言/运行时的骨架，但没有引入 Tauri 壳。
- **[事实]** P3-001 的 23 个测试在本任务中按根不变量合并为 10 个迁移测试；不是逐测试等价复制。当前优先覆盖任务卡指定 P0 防线。
- **[事实]** P3-001 已有的 process-kill、旧包控制、完整恢复投影、双 Project 全 state 闭包、lease 细测和 UX 语义态未全部一比一迁移；均在证据矩阵中标为已映射或未迁移。
- **[推断]** 本次模块化证明消费门和能力门可脱离 Python harness 复用；但覆盖数量减少意味着不能用 P3-009 替代 P3-001 的全部历史证据。

## 8. 未覆盖项、风险和后续建议

### 风险

1. **[风险]** `node:sqlite` 在 Node v24 仍输出 experimental warning；这不影响本次测试，但不构成生产依赖冻结依据。
2. **[风险]** H3 未迁移进程杀死、磁盘同步和 SQLite-aware backup；H5/H9 未迁移正式 restore、物理清理和文件导出。因此当前不得进入低敏真实副本或真实路径能力。
3. **[风险]** lease fencing、长 FTS rebuild 不阻塞捕获、真实 Renderer/IPC 路径 scope 尚无本栈证据。R-0040 必须保持 `Open / Conditional`。
4. **[风险]** 当前测试按根不变量聚合，独立评审应抽查是否存在 P3-001 子断言遗漏，而非只比较 PASS 数量。

### 后续建议

- **[建议，非本任务启动]** 后续独立工程评审逐项对照 P3-001 23 测试与本任务 10 测试，重点攻击恢复包、generation、Project 全状态闭包及旁路。
- **[建议，需 PM 确认后另立任务]** 真实 Tauri 首次集成前迁移 P2-015 矩阵，并在 debug/release 与目标平台保持 P0=0；失败时关闭命令并收窄 scope。
- **[建议，需 PM 确认后另立任务]** 在任何真实数据门前补齐进程杀死耐久、数据库感知备份恢复、异步清理与不复活 E2E。

## 9. 本地预检

已按项目规则调用 `python3 lifeos/tools/local_precheck.py lifeos/deliverables/LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report.md`。本地模型连接被对端重置，预检状态为 `Skipped / Local Model Unavailable`，符合允许跳过场景，未阻塞工程自检。预检报告：`lifeos/local_prechecks/LIFEOS-P3-009_LIFEOS-P3-009_target_stack_min_skeleton_and_invariant_migration_report_local_precheck.md`。本地预检不替代 PM Review 或独立评审。

## 10. 角色检查点与关卡自检

- **工程负责人：Pass。** 隔离目录、README、源码、fixtures、tests、脚本与 evidence 均可复跑；P3-001 未修改。
- **技术架构负责人：Pass with Conditions。** 继承 V0.1 合同且未冻结实现细节；明确区分 TypeScript/SQLite 骨架与真实 Tauri；R-0040 触发器保留。
- **数据与权限负责人：Pass（合成边界）。** 五类身份明确；实现的全部消费入口重检关键上下文；撤回/删除与 Project/location/processor 边界有负测。
- **QA / 测试负责人：Pass with Conditions。** H1-H9/T-ARCH 有追踪矩阵，最终 P0 失败 0，未迁移项有原因和风险；仍需任务卡要求的后续独立评审。
- **工程自测：通过；迁移覆盖检查：通过（含明确未迁移项）；默认关闭能力检查：通过；evidence manifest 完整性检查：通过。**

## 11. 结论

**Pass with Conditions。** P3-001 的核心 P0 安全不变量已在 TypeScript + Node.js + SQLite 最小目标栈骨架中形成可执行证明，最终 10/10 PASS、P0 失败 0，且默认关闭能力未被启用。条件是：本结论仅适用于合成、单进程、受控内存测试包；P3-001 的细粒度耐久/恢复/竞态覆盖未被本任务替代；真实 Tauri、真实数据、真实路径或外部能力启用前必须另行复测并由 PM 决策。本任务不冻结 Schema/API/模块/包管理/Tauri 配置/导出格式/SLA，不关闭 R-0040，不宣布工程基线或 MVP 结果冻结。

## 12. 需 PM 确认

1. 是否接受本任务进入后续独立工程评审；专项会话不自行验收或启动后续任务。
2. 是否认可未迁移清单继续作为关闭能力，而非把本任务 PASS 外推为真实 Tauri、真实数据或生产实现通过。
