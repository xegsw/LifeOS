# LIFEOS-P3-003｜P3-001 四项 P0 返工与补测报告

- 任务类型：条件整改 / 补丁型工程任务
- 主责角色：工程负责人 / 技术架构负责人
- 协审视角：AI 信任与安全、数据 / 领域模型、质量 / 测试、PM
- 工程自检状态：**Completed，待 PM 验收与后续独立工程复评**
- 最终结果：**16 PASS / 0 FAIL；P0 失败 0；P1 遗留 0**
- Evidence 快照：`285c74ac96f2ea978c91baaf8d526c61fbbb944407f21e221aabe1556a21860c`

## 1. 结论摘要

1. **[事实]** 四项 P0 均已在实现层修复，并分别进入自动回归测试；原 11 项验证集与新增 5 项回归测试统一复跑为 16 PASS / 0 FAIL。
2. **[事实]** 双 Project 合成夹具证明导出 Project A 时，Project B 的 Artifact、Feedback、Link、跨 Project Link、Source、Authorization、ArtifactVersion 与 Derivation 均未进入 A 的合法闭包；记录断言 12 条。
3. **[事实]** `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 四类命令均完成“旧包 → 控制命令 → 恢复候选”回归；受控 Artifact、非法 Derivation / Feedback、搜索与队列未复活，物理清理仍诚实标注为 `not_claimed`。
4. **[事实]** 重复建议不再覆盖已确认候选；普通确认保持 `confirmed`，编辑后确认保持 `edited_confirmed`。证据未变化时复用同一派生身份，证据变化时生成新身份，旧确认及 Feedback 保留可追踪。
5. **[事实]** Authorization 消费门现完整检查 Project / subject、purpose、location、processor、decision、generation、时效与精确版本；错配、未知、缺失、过期、撤回均 fail closed。
6. **[事实]** 提交边界使用真实子进程强杀：提交前退出码 86 时权威记录与 submission 均为 0；提交后退出码 87 时重启可读。FTS 与 Derivation 注入失败均未逆转权威提交。
7. **[推断]** 当前证据足以提交 PM 验收，并建议另行启动独立工程复评；不等于 P3-001 已恢复工程基线，也不关闭 R-0041。
8. **[建议]** PM 验收应抽查 `regression_assertions.json`、`snapshot_manifest.json` 与原始日志；独立复评应优先重放四个原始反例及包篡改负测。

## 2. 四项 P0 根因、修复与回归对照

| P0 | 根因 | 最小实现修复 | 自动测试与关键断言 | 结果 |
|---|---|---|---|---|
| 跨 Project 导出泄漏 | Artifact 按 Project 过滤，但 Feedback / Link 使用全表扫描 | 以当前合法 Artifact 集合为根，构造 ArtifactVersion、Source、Authorization、Derivation、Feedback、Link 闭包；Link 两端均须可达；tombstone 与控制状态仅限目标 Project | `T-EXPORT-PROJECT-CLOSURE`：B 的两个 Artifact、B Feedback、B Link、跨 Project Link、B Project 标识均零命中；A 的版本、来源、授权集合与 Artifact 闭合 | PASS |
| 撤回后旧包复活 | `restore_candidates()` 只检查 Artifact tombstone，撤权、断源与反馈撤回不可见 | 导出当前 `control_states`、`derivation_states`、`feedback_states`；恢复前重检包校验和、Project、授权上下文、来源、精确版本、generation、tombstone 与派生 / Feedback 当前状态；未知状态拒绝 | `T-DEL-OLD-PACKAGE-CONTROLS`：四命令分别执行旧包恢复；Artifact / Derivation / Feedback、搜索、队列共 17 条真实断言通过 | PASS |
| 确认状态静默重置 | 固定 Derivation ID 配合 `INSERT OR REPLACE` 重建为 `unconfirmed` | 候选身份由完整证据版本集合确定；改用 `INSERT OR IGNORE`；读取并返回既有状态；区分 `confirmed` 与 `edited_confirmed` | `T-ID-CONFIRMATION-REGRESSION`：确认 / 编辑确认后重复建议保持身份和状态；Feedback 保留；证据变化生成新身份且旧确认可查，共 10 条断言 | PASS |
| Authorization location / processor 错配仍消费 | 消费 SQL 只筛 purpose，未核对 location / processor | `can_consume()` 显式接收并校验 purpose、location、processor；缺失上下文先拒绝；同时核对 decision、generation、时效、Project 与精确版本 | `T-GATE-AUTH-CONTEXT`：location、processor 分别错配、同时错配、未知 location / processor、缺失授权 / 上下文、错误版本均拒绝；合法精确匹配允许，共 12 条断言 | PASS |

## 3. 必要 P1 补测与 Evidence 改进

### 3.1 强杀 / 提交边界

`T-SAVE-CRASH-BOUNDARY` 使用独立 Python 子进程在权威事务提交前、提交后执行进程级退出，而非只抛出可捕获异常。提交前强杀后重开数据库，Artifact 与 Submission 均为 0；提交后强杀后重启可读，且后续 FTS 失败不影响权威原文。另用 SQLite trigger 注入 Derivation 写失败，回滚派生事务后权威 Artifact 仍可读。共 11 条断言，PASS。

### 3.2 防止单 Project / happy path 过拟合

- `T-GATE` 保留原拒绝、过期、跨 Project、stale job / lease 路径；新增授权上下文矩阵。
- `T-DEL` 保留当前态四命令活跃阻断；新增四类旧包恢复测试。
- `T-EXPORT` 保留完整、部分失败和 tombstone 路径；新增双 Project 闭包与包校验和篡改拒绝。
- 合成夹具升级为 `lifeos-p3-003-synthetic-v2`，增加 Project B 与两条确定性捕获；仍为 `synthetic-disposable`。

### 3.3 真实断言与快照

验证器不再用固定摘要代替新增覆盖。五个回归测试在执行时记录 case、actual、expected、passed，合计 62 条，写入 `evidence/regression_assertions.json` 与 `test_results.json`。`snapshot_manifest.json` 保存工程目录中非 evidence 文件逐文件 SHA-256，并计算组合快照标识。Manifest 同时记录环境、命令、夹具、时间、限制、测试优先级和断言数量。

## 4. 创建 / 修改文件

### 修改

- `lifeos/engineering/LIFEOS-P3-001/src/lifeos_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-001/fixtures/synthetic_v1.json`
- `lifeos/engineering/LIFEOS-P3-001/README.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/` 下既有 evidence（由统一命令真实重建）

### 新增

- `lifeos/engineering/LIFEOS-P3-001/evidence/regression_assertions.json`
- `lifeos/engineering/LIFEOS-P3-001/evidence/snapshot_manifest.json`
- 本报告

未修改 Stitch、项目账本、冻结状态、PRD、原型或外部系统。

## 5. 复跑命令与结果

```bash
cd lifeos/engineering/LIFEOS-P3-001
python3 run_validation.py
python3 -m py_compile run_validation.py src/lifeos_slice.py tests/test_vertical_slice.py
```

- 原验证集：11 PASS / 0 FAIL。
- 新增回归集：5 PASS / 0 FAIL。
- 合计：16 PASS / 0 FAIL；P0 失败 0；P1 遗留 0。
- 真实记录断言：62 / 62 PASS。
- Evidence manifest：`lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`。
- 内容快照：`285c74ac96f2ea978c91baaf8d526c61fbbb944407f21e221aabe1556a21860c`。

## 6. H2、H3、H4、H5、H9 与 T-ARCH 对照

| 合同 | 自检 | 依据与边界 |
|---|---|---|
| H2 | PASS | 确认身份与 Feedback 不被重复建议覆盖；证据变化新建派生身份；用户原文未改写 |
| H3 | PASS | 提交前 / 后真实强杀边界、重启、FTS / Derivation 故障隔离通过 |
| H4 | PASS | Project、来源、精确版本、完整本地授权上下文、generation、tombstone、包完整性均 fail closed |
| H5 | PASS | 四命令当前态和旧包恢复态均完成活跃阻断；物理清理未被夸大 |
| H9 | PASS（受控测试包层） | 双 Project 合法闭包、部分失败、校验和冲突、不复活通过；未启用正式文件导出 |
| T-ARCH | PASS（专项自检） | 保持 SQLite + FTS-first、权威 / 派生 / outbox 分责、消费前重检与默认关闭；未冻结实现细节 |

## 7. 角色检查点与关卡

- 工程 / 技术架构：四项均修复根因，不是屏蔽测试；统一命令可复跑且快照可唯一定位。
- AI 信任与安全：确认语义不回退；location / processor 等未知即拒绝；撤回后不再消费或恢复非法派生。
- 数据 / 领域模型：Project 闭包、Source / ArtifactVersion / Derivation / Feedback / Link 身份未混淆；未声称 Schema 冻结。
- 质量 / 测试：四个独立反例均成为自动回归；强杀、双 Project、四命令旧包、授权错配和篡改包均走真实路径。
- PM 范围检查：只使用合成数据与本地受控目录；无 UI、真实 Vault、Tauri、云 / 模型、向量、同步、L3、外部用户或 Gate 5 外推。

专项自检：Gate 1 范围检查通过；Gate 2、Gate 3、Gate 4 建议通过本任务工程自检，仍须 PM 验收及后续独立工程复评。Gate 5 未评结果层。

## 8. 能力、偏离、风险与待确认

- 能力启用请求：**无**。
- 范围偏离：**无**。
- 技术架构合同偏离：**无**。
- 核心领域语义偏离：**无**。
- AI 权限边界变化：**无**；本次仅把既有冻结语义落实为完整 fail-closed 校验。
- 未关闭风险：R-0041 仍须保持 Open，直至 PM 验收与独立工程复评完成；真实 Tauri 相关 R-0040 不受本任务影响。
- **[需 PM 确认]** 是否接受本专项返工交付，并另行启动独立工程复评。专项会话不自行将 P3-001 恢复为工程基线，不关闭 R-0041，不更新项目账本。

