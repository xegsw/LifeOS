# LIFEOS-P3-002｜合成数据最小纵向闭环独立工程评审

## 评审信息

- 对应任务 ID：`LIFEOS-P3-002`
- 对应实现 / 交付：`LIFEOS-P3-001` / `lifeos/deliverables/LIFEOS-P3-001_min_vertical_slice_engineering_report.md`
- 主责角色：独立工程评审负责人
- 协审视角：技术架构、AI 信任与安全、数据 / 领域模型、质量 / 测试、体验设计、PM
- 评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅检查未被外推
- 评审结论：**Rework**
- 更新时间：2026-08-09

## 1. 评审结论摘要

1. **[事实]** 隔离复跑 `py_compile` 通过，原验证器为 **11 PASS / 0 FAIL / P0=0**，与 P3-001 报告和 PM Review 一致。
2. **[事实]** 独立对抗检查复现 4 项原测试未覆盖的 P0：跨 Project 导出泄漏、处理撤回后恢复复活、已确认候选被静默重置、授权位置 / 处理者错配仍可消费。
3. **[判断]** 这些问题击穿 H2、H4、H5、H9 与 `T-ARCH`。按 P2-019 / P2-020“任何 P0 不得 Pass with Conditions”，结论只能为 `Rework`。
4. **[建议]** P3-001 暂不得作为后续 MVP 工程基线；先做窄范围返工补测，再独立复评。
5. **[边界]** 本评审未修改 P3-001、未写功能、未启用真实能力、未处理真实数据、未冻结生产资产。

## 2. 复跑命令与结果

`run_validation.py` 会重写 `evidence/`。为同时满足复跑与“不修改 P3-001”，评审对原目录生成 SHA-256 清单，将同一快照复制到 `/tmp/lifeos-p3-002.PWSWrd/LIFEOS-P3-001` 后执行等价命令；复跑前后原目录哈希无差异。

```bash
python3 -m py_compile lifeos/engineering/LIFEOS-P3-001/run_validation.py lifeos/engineering/LIFEOS-P3-001/src/*.py
cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py
```

- `py_compile`：PASS；`run_validation.py`：11 PASS / 0 FAIL / P0=0，退出码 0。
- 原测试无失败；独立新增反例有 4 项 P0，见第 7 节。
- 既有 evidence：`lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`；临时 evidence 未替换原件。

## 3. 抽查范围与证据质量

**[事实]** 已读取任务卡指定的 P3-001 任务卡、报告、PM Review、P2-019、P2-020、P2-016、相关冻结状态，及验证器、核心代码、测试、夹具和全部 evidence。抽查覆盖权威保存、ArtifactVersion 不可变、七类语义身份、Project 恢复、候选与五类 Feedback、四命令、tombstone / generation / lease、默认关闭、导出 / 恢复、FTS 回连和隐私扫描。

**[判断]** 原验证器确实运行 11 个 unittest，但部分 evidence 是 `build_evidence()` 在测试后写入的固定摘要，不是逐断言记录。例如 `consumption_gate.json` 声称覆盖 source、exact_version、evidence、lease，实际 `T-GATE` 未覆盖全部维度；`revocation_delete_e2e.json` 声称恢复残留为 0，实际只用 `delete_content` 测不复活。

## 4. P2-019 / P2-020 / P3-001 对照验收

| 合同项 | 结果 | 核心判断 |
|---|---|---|
| 权威保存 | 部分通过 | 失败回滚、重启、幂等、索引故障隔离通过；未测强杀 |
| 身份 / 不可变版本 | 部分通过 | 表和触发器成立；已确认 Derivation 可被静默重置 |
| Project 恢复 | 部分通过 | 单 Project 读取 / 搜索合法；导出附件跨 Project 泄漏 |
| 候选与五类 Feedback | 未通过 | 不改原文；但确认后再次建议会恢复为未确认 |
| 四命令 / 不复活 | 未通过 | 多数当前面阻断；处理撤回的旧包仍可恢复 Artifact |
| generation / lease | 部分通过 | delete tombstone、stale lease 通过；撤回 / 断源未进入恢复控制门 |
| 默认关闭 / 数据边界 | 通过（关闭态） | 无真实适配器、外部调用或真实数据；不构成启用许可 |
| 导出 / 恢复 | 未通过 | Feedback / Link 未按 Project / 授权过滤；恢复只看 tombstone |
| FTS-first | 通过（窄范围） | FTS 为派生，搜索回连权威，捕获不依赖索引成功 |

## 5. H1-H9 与 T-ARCH 独立判断

| ID | 结论 | 依据 |
|---|---|---|
| H1 | Pass | 单用户、单设备、本地 Project 恢复，无范围扩张 |
| H2 | **Fail / P0** | 确认状态被下一次建议静默重置 |
| H3 | Conditional | 已测失败 / 重启 / 幂等，未测强杀 |
| H4 | **Fail / P0** | location / processor 未校验；导出附件绕过 Project / 授权 |
| H5 | **Fail / P0** | 处理撤回后旧包仍恢复 Artifact |
| H6 | Pass（关闭态） | 无 Tauri / 文件 / Vault；R-0040 未触发且仍 Open / Conditional |
| H7 | Pass（合成层） | 指定 fixture 模式扫描零命中 |
| H8 | Pass（关闭态） | 八类能力为 false 且无适配器 |
| H9 | **Fail / P0** | 导出泄漏及撤回后复活；UX 仅是诚实标注的无 UI 语义走查 |
| T-ARCH | **Fail** | 分责 / FTS / lease 局部成立，但所有消费入口重检合同不成立 |

## 6. 默认关闭能力与数据边界

**[事实]** 未发现真实 Vault、Tauri、文件导出、网络、模型、向量、同步、L3 或外部用户适配器；导出是内存测试包，夹具为 `synthetic-disposable`。

**[判断]** location / processor 错配仍可消费不代表已发生云调用，但证明未来处理者切换时不能 fail-closed，故为 P0。`DISABLED_CAPABILITIES` 是可变类字典，且值改为 true 时 `capability_call()` 静默返回；当前无适配器，列 P2 防御性缺口，不得把改布尔值视作能力启用门。

## 7. P0 / P1 / P2 问题清单

### P0

1. **跨 Project 导出泄漏。** `export_test_package(project_id)` 过滤 Artifact，却全量导出 active Feedback 和 Link。导出 Project A 时复现 Project B 的 Feedback / Link。
2. **撤回后恢复复活。** `restore_candidates()` 只读 Artifact tombstone；`revoke_processing` 没有恢复门可见的控制记录。复现 `artifact-stop` 撤回后仍进入 `restored`。
3. **确认被静默撤销。** 确认后 Derivation 为 `confirmed`；再次 `suggest_next_step()` 以固定 ID 执行 `INSERT OR REPLACE`，同一记录回到 `unconfirmed`，原 Feedback 仍在。
4. **Authorization 未完整 fail-closed。** 将授权改为 `location='cloud'`、`processor='third_party'` 后，`can_consume()` 仍返回 true；当前实现未校验这两个维度。

### P1

1. `T-GATE`、`T-DEL`、`T-EXPORT` 过拟合单 Project / 单路径，固定摘要 evidence 超过实际断言覆盖。
2. `T-SAVE` 未执行合同明确列出的进程强杀 / 提交边界测试。
3. Manifest 的 `working-tree-no-commit plus current working-tree contents` 没有内容哈希，不能唯一复现实装快照。

### P2

1. 关闭能力开关为可变类状态，缺少不可绕过的未来启用门语义。
2. 隐私扫描仅覆盖有限正则和指定 fixture，不是附件或真实副本的数据门证据。

## 8. 角色与关卡

- 独立工程 / 技术架构 / AI 信任安全 / 数据领域 / 质量测试：**Rework / 未通过**；分别受消费与恢复门、确认状态、跨 Project 语义及覆盖不足阻断。
- 体验设计：**条件覆盖**；语义状态说明诚实，但不能宣称动态 UI 已实现。
- PM：需确认 Rework、返工顺序和账本处理，不得冻结或启用能力。
- Gate 1：**Pass**；Gate 2、Gate 3、Gate 4：**Fail**。
- Gate 5：**未评结果层**；本任务没有产生外部用户、Beta、商业化或用户价值通过证据。

## 9. 工程基线、不得外推与 PM 决策

**[建议] 不允许 P3-001 作为后续工程基线输入。** 在 4 项 P0 关闭并独立复评前，只可把权威捕获事务轮廓、不可变版本触发器、FTS 回连、outbox 同事务登记、stale lease 拒绝和合成夹具作为局部探索材料；实现细节不冻结。

不得把 11 PASS 外推为 P2-019 DoD、独立评审通过、真实能力安全、正式 MVP 完成、无条件 Stage 3、Gate 5、Beta 或商业化通过；不冻结 Schema、API、UI、Tauri capability、导出格式、生产 SLA 或最终目录。

**需 PM 主会话确认：**

1. 是否接受 `Rework`，保持真实能力关闭，并禁止 P3-001 作为后续工程基线。
2. 是否创建一个窄范围返工 / 补测任务：先关闭 4 项 P0，再补强杀和可追踪 evidence；不得扩展到 UI、真实 Tauri、真实数据或外部能力。

## 10. 后续建议与范围声明

下一步应是返工补测，而非基线整理或能力启用：修复 Project / 授权约束下的导出；让恢复门统一消费撤回、断源、删除及当前授权 / generation；保护确认状态；完整校验 Authorization；补双 Project、旧包 + 四命令、确认后重复建议、错配授权、强杀测试，并从实际断言生成 evidence。P0 全部关闭后再独立复评。

本任务只创建本评审文件；未修改 P3-001 代码、测试、夹具、evidence、Stitch、PRD、冻结资产或项目账本，未连接外部服务或启用真实能力。任务状态、风险、决策记录与下一任务由 PM 主会话处理。
