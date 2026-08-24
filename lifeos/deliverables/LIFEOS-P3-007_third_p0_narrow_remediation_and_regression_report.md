# LIFEOS-P3-007｜P3-001 第三轮 P0 窄范围返工与补测报告

- 任务类型：补丁 / 条件整改型任务
- 主责角色：工程返工负责人 / 技术架构负责人
- 协审视角：AI 信任与安全、数据 / 领域模型、质量 / 测试、PM
- 工程自检状态：**Completed，待 PM 验收与后续独立工程复评**
- 统一验证结果：**23 PASS / 0 FAIL；P0=0；P1=0**
- 记录断言：**136 / 136 PASS**；其中 P3-007 四组根因回归 **51 / 51 PASS**
- Evidence 快照：`ff526a340443057ad56abec75e30f44a387b4cdb3e3850464cc2890b9ff173fd`

## 1. 任务结论摘要

1. **[事实]** 已在授权目录内完成 P3-006 四项 P0 的窄范围修复：恢复包载荷改为当前 SQLite 权威投影；Feedback / Link 写入口复用当前对象与完整证据门；混合 Project Derivation / Feedback 从全部导出 state 载荷中整体剔除；Derivation 依赖身份绑定 Artifact 与 Source generation。
2. **[事实]** 新增四组自动回归：`T-RESTORE-AUTHORITATIVE-PAYLOAD-PROJECTION`、`T-WRITE-GATES-FEEDBACK-AND-LINK`、`T-EXPORT-ALL-STATE-PROJECT-CLOSURE`、`T-DERIVATION-GENERATION-BINDING`，共 51 条记录断言全部通过。
3. **[事实]** 原 19 组 P3-001 / P3-003 / P3-005 验证全部保留；统一命令现为 23 PASS / 0 FAIL，P0 失败 0、P1 遗留 0。全部 136 条机器记录断言与测试日志一致。
4. **[事实]** Evidence manifest、机器结果、回归断言、内容快照及分项证据均已由统一命令重建；fixture 更新为 `lifeos-p3-007-synthetic-v4`。
5. **[推断]** 在当前合成、单进程、受控测试包边界内，四项 P0 的根执行路径已被关闭，具备提交 PM 验收及进入下一轮独立工程复评的条件。
6. **[建议]** 独立复评仍应从实现外部变换字段、Project 组合、授权状态和 generation 顺序重放，避免由本执行会话自证。P3-001 在复评通过前继续保持 Rework，R-0041 继续保持 Open。

## 2. 修改文件清单

### 工程与测试

- `lifeos/engineering/LIFEOS-P3-001/src/lifeos_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/tests/test_vertical_slice.py`
- `lifeos/engineering/LIFEOS-P3-001/run_validation.py`
- `lifeos/engineering/LIFEOS-P3-001/fixtures/synthetic_v1.json`
- `lifeos/engineering/LIFEOS-P3-001/README.md`

### Evidence 与报告

- `lifeos/engineering/LIFEOS-P3-001/evidence/` 下 manifest、测试结果、回归断言、快照和分项证据由统一命令更新。
- 本报告：`lifeos/deliverables/LIFEOS-P3-007_third_p0_narrow_remediation_and_regression_report.md`。

未修改 Stitch、PRD、原型、项目账本、冻结资产、风险状态或外部系统。

## 3. 四项 P0：根因、修复与覆盖

| P0 | 根因 | 根因级修复 | 自动回归与结果 |
|---|---|---|---|
| 恢复包载荷自证 | 恢复门虽读取当前资格状态，却把旧包中的 Artifact、Derivation、Feedback、Link 字典直接返回 | `restore_candidates()` 仅把包当候选 ID 集；Artifact 由 `read_artifact()` 读取当前权威投影，Derivation 由完整当前依赖投影生成，Feedback / Link 必须读取当前数据库真实行；不存在的注入 Link 被排除。公开 checksum 仅保留未重算损坏检测，不作为真实性或防伪证明 | 重算 checksum 后同时篡改 Artifact 原文/title/category/source、Derivation output/rule/status/generation、Feedback kind/user_text、Link relation/source/status，并注入 Link；7 / 7 断言证明恢复结果来自权威行或被排除 |
| Feedback / Link 写入口绕过 | 两个公共写方法未要求 Project 和授权上下文，也未验证完整候选证据或两端 Artifact | `add_feedback()` 要求显式 Project 与全部证据对象上下文，并通过 `_derivation_projection()` 重检版本、Artifact/Source generation、当前唯一 Authorization、purpose/location/processor/now、Source、tombstone；`add_important_link()` 对两端执行同一当前门并要求同 Project。失败在写入前发生 | 覆盖缺失上下文、deny、revoked、expired、allow/deny 冲突、purpose/location/processor 错配、跨 Project、删除、撤权、断源、旧 generation，以及合法 happy path；22 / 22 断言通过，失败时记录数为 0、候选状态不变 |
| 导出 state 跨 Project 泄漏 | `rows_for_project` 用“任一输入版本属于当前 Project”选中混合派生，之后无条件写入 `derivation_states` / `feedback_states` | 导出派生前读取其完整依赖；只要任一依赖不属于目标 Project，Derivation 及其 Feedback 从活跃列表和 state 列表整体省略。Artifact 相关 `control_states`、`excluded`、`partial_failures`、tombstone 原有查询继续限制在目标 Project | 构造 A+B 混合 Derivation、Feedback 与 Link，分别导出 A、B；对方 version、混合 Derivation ID、Feedback ID/user_text、Link 均零出现，同时合法单 Project 状态保留；12 / 12 断言通过 |
| Derivation generation 漏绑 | `derivation_input` 与候选 ID 只绑定 ArtifactVersion ID；同 version 下 Artifact/Source generation 改变不会形成新身份 | `derivation_input` 增加 Artifact / Source generation 快照；候选哈希包含完整 `{version_id, artifact_generation, source_generation}`；消费投影逐输入对照当前代际；建议入口把代际错配旧未确认候选标为 stale，并生成新身份 | 分别递增 Artifact generation（同步 Authorization）和 Source generation；验证旧候选 stale、新候选 ID 变化，旧候选在建议、导出、恢复、Feedback、Link、搜索中被阻断，未变化新代际 happy path 可确认；10 / 10 断言通过 |

## 4. 历史 P0 与基础合同回归

- **[事实] P3-002 四项历史 P0：** 普通双 Project 导出闭包、控制命令后旧包不复活、确认状态不回退、Authorization 多维错配均继续通过；本轮还扩大到所有 state 字段和写入口。
- **[事实] P3-004 三项 P0：** 当前权威恢复门、完整 ArtifactVersion 证据依赖、显式上下文与冲突 Authorization 回归继续通过。
- **[事实] P3-005 三项修复：** 原三组对抗回归保留，未删除、重命名或弱化。
- **[事实] 基础合同：** H1-H9 与 `T-ARCH` 对应 23 个测试组均通过；真实 Vault、Tauri / IPC、文件导出扩权、云 / 第三方模型、向量、同步、多设备、L3、外部用户保持不可达。

## 5. 复跑命令与结果

```bash
python3 -m py_compile lifeos/engineering/LIFEOS-P3-001/run_validation.py lifeos/engineering/LIFEOS-P3-001/src/*.py lifeos/engineering/LIFEOS-P3-001/tests/*.py
cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py
```

- `py_compile`：PASS；本环境无需设置临时 `PYTHONPYCACHEPREFIX`。
- `run_validation.py`：23 PASS / 0 FAIL；P0=0；P1=0；退出码 0。
- 记录断言：136 / 136 PASS；P3-007 四组 51 / 51 PASS。
- 环境：macOS arm64；Python 3.9.6；SQLite 3.51.0。
- 内容快照：`ff526a340443057ad56abec75e30f44a387b4cdb3e3850464cc2890b9ff173fd`，7 个非 evidence 工程文件逐文件 SHA-256 已记录。

## 6. Evidence 更新

- 入口：`lifeos/engineering/LIFEOS-P3-001/evidence/MANIFEST.md`
- 机器结果：`evidence/test_results.json`
- 真实断言：`evidence/regression_assertions.json`
- 内容快照：`evidence/snapshot_manifest.json`
- 恢复权威投影 / 不复活：`evidence/revocation_delete_e2e.json`
- 写入口当前门：`evidence/consumption_gate.json`
- generation 绑定：`evidence/identity_trace.json`
- 全 state Project 闭包：`evidence/ux_export_report.md`
- 架构合同：`evidence/architecture_conformance.md`

一致性核对确认：23 个机器测试记录全部 PASS；`test_results.json` 与 `regression_assertions.json` 的断言内容相同；全部 `passed=true`；测试结果与快照 ID 一致。Manifest 已明确 checksum 只检测未重算损坏。

## 7. P0 / P1 / P2 清单

- **P0：无（本专项合成工程自检范围内）。** 是否真正关闭仍须 PM 验收和不同 Agent 的独立复评。
- **P1：无。**
- **P2：两项继承观察项，未由本任务扩大或关闭。** `DISABLED_CAPABILITIES` 仍是可变类字典；隐私扫描仍只覆盖指定合成 fixture 与有限正则。二者在当前无适配器、纯合成边界下不构成 P0/P1，也不得外推到真实能力。

## 8. 角色检查点与评审关卡

- 工程 / 技术架构：四项修复进入共同根路径，并有负测、变形反例与合法路径；权威 / 派生 / outbox 分责未改变。
- AI 信任与安全：用户原文不由包载荷自证；Feedback 确认前重检完整证据与授权；Link 不能跨 Project 或连接失效对象。
- 数据 / 领域模型：ArtifactVersion、Artifact generation、Source generation、DerivationInput、Feedback、Authorization、Link 身份关系可追踪；新增列是合成切片实现，不冻结生产 Schema。
- 质量 / 测试：历史 19 组全保留，新增 4 组、51 条记录断言；覆盖负测、字段变形、Project 双向零泄漏、代际变化与 happy path。
- PM 范围：仅合成数据和既有工程目录；未启用真实能力，未外推 Gate 5、Beta、商业化、生产安全或工程基线恢复。

专项自检建议：Gate 1、Gate 2、Gate 3、Gate 4 在本次合成工程证据层通过；仍须 PM 验收及后续独立复评。Gate 5 只确认未被错误外推，不做结果层验证。

## 9. 不得外推的结论

本报告不证明正式恢复 / 导出协议、密码学真实性、真实数据、真实 Vault、真实 Tauri / IPC、文件系统权限、云 / 第三方模型、向量、同步、多设备、L3、外部用户、Gate 5、Beta、商业化或生产安全通过；不冻结 Schema、API、UI、Tauri capability、正式导出格式、SLA 或最终工程目录。23 PASS 不等于 P3-001 已恢复工程基线，也不等于 R-0041 可由本会话关闭。

## 10. 需 PM 确认与后续建议

- **[需 PM 确认]** 是否接受 P3-007 专项交付与 evidence，并判断 Gate 1-4 的任务级验收结论。
- **[需 PM 确认]** 是否在用户确认后启动由不同 Agent 执行的下一轮独立工程复评；本会话不启动后续任务。
- **[建议]** 独立复评应重新构造分字段重签载荷、对象 ID 变形、Feedback / Link 每一授权维度、混合 Project 多输入排列、Artifact / Source generation 多次滚动及旧上下文组合。
- **[建议]** 在独立复评和 PM 决策前，P3-001 保持 Rework，R-0041 保持 Open；本专项会话不更新项目账本、不恢复基线、不关闭风险。
