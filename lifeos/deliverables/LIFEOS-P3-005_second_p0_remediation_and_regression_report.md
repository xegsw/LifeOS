# LIFEOS-P3-005｜P3-001 第二轮 P0 返工与补测报告

- 任务类型：条件整改 / 补丁型工程任务
- 主责角色：工程负责人 / 技术架构负责人
- 协审视角：AI 信任与安全、数据 / 领域模型、质量 / 测试、PM
- 工程自检状态：**Completed，待 PM 验收与再次独立工程复评**
- 统一验证结果：**19 PASS / 0 FAIL；P0 失败 0；P1 遗留 0**
- 原 16 项验证集：**16 PASS / 0 FAIL**
- 新增 P3-005 对抗回归：**3 PASS / 0 FAIL，23 / 23 条记录断言通过**
- 全部记录断言：**85 / 85 PASS**
- Evidence 快照：`3779cd5efe2d55a5bafe7e78cef4bd8eac230df52b394c14be69fe189965f3a3`

## 1. 结论摘要

1. **[事实]** P3-004 指出的三项 P0 均完成实现层最小修复，并分别进入统一验证命令。原 11 项验证、P3-003 的 5 项回归和本次 3 项对抗回归合计 19 PASS / 0 FAIL，P0 失败 0，P1 遗留 0。
2. **[事实]** `restore_candidates()` 已改为实例级可信执行边界，只接受待恢复旧包，恢复时直接读取当前 SQLite 权威控制状态；调用方旧上下文、包内旧控制快照或重算公开 SHA-256 的伪造控制字段均不能使已删除对象复活。
3. **[事实]** 新增 `derivation_input` 关系持久化候选的完整 ArtifactVersion 证据集合。撤回非主证据 `artifact-decision` 后，候选变为 `stale`，导出中的 Derivation、相关 Feedback 与两端不再合法的 Link 均为零命中，建议消费返回“暂无可靠建议”。
4. **[事实]** `can_consume()` 不再提供允许型 purpose / location / processor / now 默认值，并要求精确版本、Artifact generation 与 Source generation。`read_artifact()`、`recovery_package()`、`search()`、`suggest_next_step()`、`export_test_package()` 和恢复门均要求调用方显式传入对象级授权上下文；缺失即拒绝。
5. **[事实]** 同 subject 的 Authorization 必须恰好一条；缺失、重复 allow、allow / deny 冲突、未知或错配维度、过期、撤回、版本 / generation 不一致均 fail closed，不再使用 `fetchone()` 非确定性选行放行。
6. **[推断]** 本次合成工程证据足以提交 PM 验收，并支持启动再次独立工程复评；它不证明正式恢复协议、真实数据、真实 Tauri、真实 Vault 或生产安全，也不代表 P3-001 已恢复为工程基线。
7. **[建议]** 独立复评优先变换包内控制状态与校验和、撤回不同位置的证据依赖、构造重复 / 冲突 Authorization，并从所有真实消费入口重放缺失上下文反例。

## 2. 三项 P0 根因、代码改动与回归对照

| P0 | 根因 | 最小代码修复 | 测试 ID、关键断言 | 结果 |
|---|---|---|---|---|
| 恢复门由包自证当前状态 | 静态函数只比较 stale / control 两个调用方包；公开 SHA-256 只能发现未重算损坏，不能证明当前性或可信性 | 改为 `LifeOSSlice.restore_candidates()` 实例方法；只校验旧包内容完整性，随后从当前数据库读取 Artifact、current_version_id、generation、deleted / tombstone、Source、唯一 Authorization、Derivation / 完整依赖、Feedback；包内 `control_states` 不参与放行 | `T-RESTORE-AUTHORITATIVE-CURRENT-GATE`：旧授权上下文不能自证；伪造允许控制字段并重算 SHA-256 后仍不能恢复；当前 tombstone generation 保持 2。3 / 3 PASS | PASS |
| Derivation 仅保存单一输入 | 候选身份用完整证据集合计算，但失效图和导出只认识 `input_version_id`，撤回非主证据不传播 | 新增 `derivation_input(derivation_id, version_id, ordinal)`；生成时登记全部证据版本；失效按依赖表反查；导出 / 恢复要求依赖集合完整、全部位于当前允许闭包且状态有效 | `T-DERIVATION-COMPLETE-EVIDENCE-REVOCATION`：两项证据完整持久化；撤回 `artifact-decision` 后 candidate stale；Derivation / Feedback / Link 导出零命中；建议消费阻断。6 / 6 PASS | PASS |
| 隐式授权上下文与冲突选行 | 允许型默认参数掩盖调用方缺失；Artifact 与多条 Authorization join 后 `fetchone()` 可能任取 allow | 默认上下文全部改为空并检查；上下文显式携带 subject、Project、purpose、location、processor、精确版本、Artifact / Source generation、now；先读取 Artifact / Source，再单独读取全部 Authorization，数量不等于 1 即拒绝 | `T-GATE-EXPLICIT-CONTEXT-AND-CONFLICTS`：四类指定入口缺失上下文零消费；allow / deny 冲突在 can/read/search/recovery/export 全拒绝；重复 allow、Artifact / Source generation 错配拒绝；调用方不能回拨策略时钟。14 / 14 PASS | PASS |

## 3. 权威恢复边界与完整依赖说明

恢复候选仍是合成工程内的进程级接口，不是正式文件导出、签名、迁移或恢复协议。旧包的 SHA-256 只用于检测包内容是否在生成后变化；即使攻击性调用方修改旧包中的控制字段并重算哈希，是否恢复仍由当前 SQLite 权威状态决定。Artifact 必须仍属于同一 Project，当前版本和 generation 必须与旧包候选一致，并通过当前 Source、tombstone 和唯一 Authorization 门。Derivation 与 Feedback 也分别读取当前状态，不接受旧包自报状态。

候选的完整证据集合以 ArtifactVersion ID 有序持久化。当前实现保留既有 `input_version_id` 字段以维持本次最小切片兼容，但所有失效、导出与恢复判断以 `derivation_input` 完整集合为准，不再把单一字段当作完整依赖图。Artifact 撤权 / 删除、Source 断开会先定位相关版本，再将任何包含这些版本的 Derivation 标为 `stale`；导出仅保留依赖全集均处于当前合法 Artifact 闭包的活跃 Derivation，因此其 Feedback 与 Link 也无法绕过父级门。

## 4. 显式授权上下文与 fail-closed 规则

本次合成入口统一采用对象级上下文：`subject_id`、`project_id`、`expected_version_id`、`expected_generation`、`expected_source_generation`、`purpose`、`location`、`processor`、`now`。这些字段不充当授权凭证，而是声明当前消费请求；最终授权仍从权威表读取并逐维核对。任一字段缺失或不一致即拒绝。

Authorization 当前唯一决策采用保守规则：同 subject 必须恰好存在一条记录，且 decision 为 allow、generation 等于 Artifact generation、purpose / location / processor 精确匹配、未过期。缺失、多条、重复 allow、allow / deny 冲突、未知 decision 或维度不一致都拒绝。该规则是对既有冻结 fail-closed 合同的工程落实，不冻结生产 Schema、策略语言或 API。

## 5. 创建 / 修改文件清单

### 修改

- `lifeos/engineering/LIFEOS-P3-001/src/lifeos_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-001/fixtures/synthetic_v1.json`
- `lifeos/engineering/LIFEOS-P3-001/README.md`
- `lifeos/engineering/LIFEOS-P3-001/evidence/` 下既有 evidence（由统一命令真实重建）

### 创建

- `lifeos/deliverables/LIFEOS-P3-005_second_p0_remediation_and_regression_report.md`

未修改 Stitch、PRD、原型、项目账本、冻结状态或外部系统。

## 6. 复跑命令、结果与 Evidence

```bash
cd lifeos/engineering/LIFEOS-P3-001
python3 -m py_compile run_validation.py src/*.py tests/*.py
python3 run_validation.py
```

- 原 P3-001 验证集：11 PASS / 0 FAIL。
- P3-003 回归集：5 PASS / 0 FAIL。
- 原 16 项验证集：16 PASS / 0 FAIL。
- P3-005 新增回归：3 PASS / 0 FAIL。
- 合计：19 PASS / 0 FAIL；P0 失败 0；P1 遗留 0。
- 记录断言：85 / 85 PASS；其中本次三组 23 / 23 PASS。
- Fixture：`lifeos-p3-005-synthetic-v3`，`synthetic-disposable`。
- Evidence manifest：`lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`。
- 内容快照：`3779cd5efe2d55a5bafe7e78cef4bd8eac230df52b394c14be69fe189965f3a3`；7 个非 evidence 工程文件逐文件 SHA-256 已记录于 `snapshot_manifest.json`。

Evidence 由 unittest 真实结果、case / actual / expected / passed 断言、原始日志、运行环境和内容哈希生成；无固定成功摘要替代执行结果。Manifest 明确限制：无真实数据、Vault、Tauri / IPC、文件导出、云 / 模型、向量、同步、L3、外部用户、生产打包或 SLA。

## 7. H2、H4、H5、H9 与 T-ARCH 对照

| 合同 | 专项自检 | 依据与限制 |
|---|---|---|
| H2 | PASS（合成工程层） | 用户原文未改写；Derivation 身份和完整证据版本集合可追踪；任一证据失效传播到候选及相关消费闭包 |
| H4 | PASS（合成工程层） | 所有消费入口显式接收上下文并读取当前唯一 Authorization；缺失、重复、冲突、未知、过期、版本 / generation 错配均拒绝 |
| H5 | PASS（合成工程层） | 四类既有控制回归保留；非主证据撤回传播；恢复门读取当前权威状态，旧 / 伪造控制快照不复活 |
| H9 | PASS（受控测试包层） | 完整 / 部分导出、Project 闭包、当前恢复候选和不复活通过；不外推为正式导出 / 恢复协议 |
| T-ARCH | PASS（专项自检） | 保持 SQLite + FTS-first、权威 / 派生 / outbox 分责、消费前重检、派生可失效重建与外部能力默认关闭；未冻结实现细节 |

## 8. 角色检查点与评审关卡

- 工程 / 技术架构：三项修复均改变根执行路径，而非只屏蔽固定反例；统一命令可复跑，快照可唯一定位本次内容。
- AI 信任与安全：证据撤回传播到 AI / 规则候选；上下文缺失与授权歧义 fail closed；用户 Feedback 不作为绕过父级证据门的独立通行证。
- 数据 / 领域模型：Derivation 与完整 ArtifactVersion 集合、Artifact、Source、Authorization、Feedback、Link 的消费关系清楚；未宣称 `derivation_input` 为生产 Schema 冻结。
- 质量 / 测试：P3-004 三项反例全部自动化；覆盖旧上下文、伪造并重算哈希的包、非主证据撤回、缺失上下文、allow / deny 冲突、重复 allow 和真实消费入口。
- PM 范围：仅合成数据与本地受控目录；无 UI、真实能力、Gate 5、Beta、商业化或冻结外推。

专项自检关卡：Gate 1 范围检查通过；Gate 2、Gate 3、Gate 4 在本任务合成工程证据层建议通过，仍须 PM 验收与后续独立工程复评。Gate 5 未做结果层验证。

## 9. 能力、偏离、风险与待确认

- 能力启用请求：**无**。
- 范围偏离：**无**。
- 技术架构合同偏离：**无**。
- 核心语义偏离：**无**；新增依赖关系是冻结 Derivation 完整证据语义的最小实现，不调整核心实体。
- AI 权限边界偏离：**无**；仅落实既有显式上下文和未知即拒绝规则。
- 未关闭风险：R-0041 继续保持 Open；P3-001 继续保持 Rework，直至 PM 验收与再次独立工程复评完成。R-0040 不受本任务影响。
- **[需 PM 确认]** 是否接受本专项返工交付，并授权再次独立工程复评。专项会话不自行恢复 P3-001 工程基线、不关闭 R-0041、不更新任何项目账本。

## 10. 后续独立复评建议

再次独立工程复评应从实现外部重新构造反例，而非只复跑本任务预设数据：尝试提供旧授权上下文、修改包内 generation / deleted / Source / Authorization / Derivation / Feedback 后重算哈希；分别撤回候选证据集合中的每一项并检查搜索、建议、导出、恢复；构造多条 allow、allow / deny、未知 decision、过期与多维错配；确认所有消费入口在省略任一上下文字段时均零消费。独立复评通过前不得把当前 19 PASS 外推为工程基线恢复或风险关闭。
