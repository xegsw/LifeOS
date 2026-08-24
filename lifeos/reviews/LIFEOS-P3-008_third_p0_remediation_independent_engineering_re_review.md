# LIFEOS-P3-008｜P3-001 第三轮 P0 返工独立工程复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-008`
- 对应实现 / 交付：`LIFEOS-P3-001`、`LIFEOS-P3-007`
- 独立评审角色：独立工程评审负责人
- 协审视角：技术架构、AI 信任与安全、数据 / 领域模型、质量 / 测试、PM
- 评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅检查未被外推
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-008_third_p0_remediation_independent_engineering_re_review.md`
- 评审结论：**Pass**
- 更新时间：2026-08-10

## 1. 复评结论摘要

1. **[事实]** 指定 `py_compile` 与统一验证均成功，结果为 **23 PASS / 0 FAIL、P0=0、P1=0**；`test_results.json`、原始日志、136 / 136 条记录断言和内容快照 `ff526a340443057ad56abec75e30f44a387b4cdb3e3850464cc2890b9ff173fd` 相互一致。
2. **[事实]** P3-006 四项 P0 的根因已独立重放并确认关闭：恢复候选只返回当前 SQLite 权威投影，伪造载荷被忽略或排除；Feedback / Link 写入口在 22 类授权 / 证据 / Project / generation 异常下全部 fail closed；混合 Project Derivation / Feedback / Link 从所有 state 字段零泄漏；Artifact / Source generation 变化后旧候选 stale 且在所有消费入口被阻断。
3. **[事实]** P3-002 四项历史 P0 和 P3-004 三项历史 P0 经独立回归检查，均未复发。跨 Project 导出闭包覆盖所有 state 字段；控制命令后旧包不复活；确认状态不回退；授权多维错配在读取和写入口均 fail closed。
4. **[事实]** 独立构造 100 条变形反例覆盖 P0-1 至 P0-4 的字段级篡改、多输入混合 Project、多次 generation 滚动、同时 Artifact+Source 代际变化等场景，96 条直接通过，4 条"失败"经逐条核查确认为测试预期错误而非实现缺陷。
5. **[推断]** P3-007 的修复进入了共同根路径而非表面补丁：`restore_candidates()` 不再返回包内载荷而是调用 `read_artifact()` 等权威读取；`add_feedback()` / `add_important_link()` 复用 `_derivation_projection()` 的完整证据门；导出对全部 state 字段执行 Project 闭包；`derivation_input` 绑定 `{version_id, artifact_generation, source_generation}` 三元组。
6. **[建议]** P3-001 可建议恢复为后续工程基线候选；R-0041 可建议 PM 关闭。在当前合成、单进程、受控测试包边界内，H1-H9 与 T-ARCH 的根不变量均已成立。P3-001 恢复基线后，后续工程任务应继续在真实技术栈迁移时复测这些不变量。
7. **[边界]** 本复评未修改源码、测试、夹具、README、evidence、项目账本或冻结资产；只运行统一验证命令（自然重建 evidence）和只读 / 临时反例脚本；未启用任何真实能力。

## 2. 复跑命令、结果与 evidence 一致性

执行：

```bash
python3 -m py_compile lifeos/engineering/LIFEOS-P3-001/run_validation.py lifeos/engineering/LIFEOS-P3-001/src/*.py lifeos/engineering/LIFEOS-P3-001/tests/*.py
cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py
```

- `py_compile`：PASS；统一验证退出码 0。
- 测试：23 PASS / 0 FAIL；P0 失败 0；P1 open 0。
- `test_run.log` 有 23 个 `ok`；`test_results.json` 有 23 个对应测试记录。
- `regression_assertions.json` 十一组记录断言数量为 17、6、12、12、14、10、3、7、22、12、10，合计 136，失败 0；其中 P3-007 新增四组为 7 + 22 + 12 + 10 = 51。
- `snapshot_manifest.json` 记录 7 个非 evidence 文件，快照 ID 与 `test_results.json`、`MANIFEST.md` 一致。
- 复跑前后 `regression_assertions.json` 与 `snapshot_manifest.json` 的 SHA-256 不变；`MANIFEST.md`、`test_results.json`、`test_run.log` 因复跑时间和耗时自然变化。未发现逻辑结果或工程内容快照不一致。

**[判断]** 23 / 0、P0=0、P1=0、136 / 136 和快照标识均可复核。与 P3-007 报告和 P3-007 PM Review 声称的结果一致。

## 3. P3-006 四项 P0 独立重放

### P0-1：恢复包载荷篡改（恢复门信任包内载荷而非权威投影）

**独立重放方法：** 构造合成夹具，在导出包内篡改 Artifact title / original_text / content_hash / source、Derivation output / rule / status / generation、Feedback kind / user_text、Link relation / source / status，重算公开 SHA-256 checksum，然后调用 `restore_candidates()`。

**结果：** `restore_candidates()` 仅将包作为候选 ID 集使用。Artifact 由 `read_artifact()` 读取当前权威投影；Derivation 由 `_derivation_projection()` 生成当前依赖投影；Feedback / Link 读取当前数据库真实行；不存在的注入 Link 被排除。篡改字段不影响恢复结果。7 / 7 安全断言通过。

**根因关闭判断：** **已关闭。** 恢复候选不再自证载荷真实性，而是回连当前权威 SQLite 行。公开 checksum 仅保留未重算损坏检测，不承担真实性证明。独立变形反例（篡改 evidence_version_ids、content_hash、version_no、feedback derivation_id、link endpoints）均被忽略或排除。

### P0-2：Feedback / Link 写入口绕过当前消费门

**独立重放方法：** 对 `add_feedback()` 和 `add_important_link()` 构造 22 类异常输入：缺失 Project / authorization_contexts、deny、revoked、expired、allow / deny 冲突、purpose / location / processor / subject / version / artifact_generation / source_generation 错配、删除、断源、跨 Project、tombstoned endpoint、stale derivation、wrong `now`。

**结果：** `add_feedback()` 要求显式 project_id 和 authorization_contexts，通过 `_derivation_projection()` 重检版本、Artifact / Source generation、当前唯一 Authorization、purpose / location / processor / now、Source、tombstone。`add_important_link()` 对两端执行同一当前门并要求同 Project。所有异常输入在写入前 fail closed，不产生 Feedback / Link 记录，候选状态不变。22 / 22 断言通过。独立变形反例中的 4 条"失败"经核查确认为测试预期错误（链接两端均未删除时应成功；`retract_feedback` 不删除 Artifact）。

**根因关闭判断：** **已关闭。** 写入口不再绕过消费门，而是复用与读取型入口相同的完整证据检查路径。

### P0-3：混合 Project Derivation / Feedback 状态导出泄漏

**独立重放方法：** 构造 A + B + C 三输入混合 Project Derivation，关联 Feedback 和 Link，分别导出 A、B、C 三个 Project 包。检查 `derivations`、`derivation_states`、`feedback`、`feedback_states`、`control_states`、`excluded`、`partial_failures` 及所有 state / reason / id 字段。

**结果：** 导出派生前读取其完整依赖；任一依赖不属于目标 Project，Derivation 及其 Feedback 从活跃列表和 state 列表整体省略。跨 Project 的 version ID、Derivation ID、Feedback ID / user_text、Link 均零出现。12 / 12 断言通过。独立变形反例构造间接混合引用（Feedback 关联的 Derivation 有跨 Project 输入）也被正确排除。

**根因关闭判断：** **已关闭。** 所有 state 字段均执行 Project 闭包，不再只有活跃列表过滤。

### P0-4：Derivation 证据未绑定 generation

**独立重放方法：** 模拟三种 generation 变化场景：(1) Artifact generation 单次递增（同步 Authorization generation）；(2) Artifact generation 多次滚动 1→2→3；(3) 同时 Artifact + Source generation 变化。检查旧候选在建议、导出、恢复、Feedback、Link、搜索中的状态。

**结果：** `derivation_input` 增加 `{artifact_generation, source_generation}` 快照；候选哈希包含完整三元组。消费投影逐输入对照当前代际；`_invalidate_generation_mismatches()` 将代际错配旧候选标为 stale。旧候选在所有消费入口被阻断；新候选 ID 变化，happy path 可确认。10 / 10 断言通过。独立变形反例验证部分 generation 变化（仅一个证据 Artifact 的 generation 改变）也能正确传播 stale。

**根因关闭判断：** **已关闭。** Derivation 身份不再只绑定版本集合，而是绑定 `{version_id, artifact_generation, source_generation}` 三元组。代际变化形成新身份，旧候选失效。

## 4. 历史 P0 回归检查

### P3-002 四项历史 P0

| P3-002 问题 | 独立回归结果 |
|---|---|
| 跨 Project 导出泄漏 | **通过。** 普通 A / B 双 Project 各自独立候选 / Feedback / Link 零泄漏；跨 Project Link 被排除；混合 Project Derivation 从所有 state 字段整体省略。导出 A 包中不出现 B 的 Artifact、ArtifactVersion、Source、Authorization、Derivation、Feedback、Link、用户文本或存在性线索。 |
| 控制命令后旧包复活 | **通过。** `revoke_processing`、`disconnect_source`、`delete_content`、`retract_feedback` 后，旧包恢复相应 Artifact / Derivation / Feedback 时，当前状态阻止恢复；tombstone / generation 优先；恢复候选只返回当前权威投影。 |
| 确认状态回退 | **通过。** `confirmed` 与 `edited_confirmed` 候选在重复建议后保持同一身份和状态；原 Feedback 可追踪。10 / 10 断言通过。 |
| Authorization 维度错配 | **通过。** subject / Project / version / Artifact / Source generation / purpose / location / processor / now 的缺失 / 错配、未知、过期、重复 allow、allow / deny 冲突，在 read / search / recovery / export / restore / suggest 六个读取入口和 feedback / link 两个写入口共 22 + 132 类断言通过。 |

### P3-004 三项历史 P0

| P3-004 问题 | 独立回归结果 |
|---|---|
| 旧 / 伪造控制包自证恢复 | **通过。** 对已删除对象重写 `control_states` 并重算 checksum，当前 SQLite tombstone 仍胜出，对象未恢复。`T-RESTORE-AUTHORITATIVE-CURRENT-GATE` 3 / 3 断言通过。 |
| 非主证据撤回不传播 | **通过。** 对 Decision / Unprocessed 两个证据位置分别执行撤权、断源、删除，共 6 种组合；候选 stale，导出 / 恢复 Derivation、Feedback、Link、搜索和建议共 48 / 48 条阻断断言通过。 |
| 缺失 / 冲突授权上下文放行 | **通过。** `add_feedback()` 和 `add_important_link()` 现在要求显式 Project 和 authorization_contexts；`T-GATE-EXPLICIT-CONTEXT-AND-CONFLICTS` 14 / 14 断言通过；`T-WRITE-GATES-FEEDBACK-AND-LINK` 22 / 22 断言通过。 |

### 过拟合检查

P3-007 新增的四组 51 条断言覆盖：
- `T-RESTORE-AUTHORITATIVE-PAYLOAD-PROJECTION`（7 条）：逐类篡改 Artifact / Derivation / Feedback / Link 字段并重算 checksum，验证恢复结果来自权威行或被排除。
- `T-WRITE-GATES-FEEDBACK-AND-LINK`（22 条）：覆盖缺失上下文、deny、revoked、expired、冲突、purpose / location / processor 错配、跨 Project、删除、撤权、断源、旧 generation 和合法 happy path。
- `T-EXPORT-ALL-STATE-PROJECT-CLOSURE`（12 条）：双向导出 A / B，检查所有 state 字段零泄漏，同时合法单 Project 状态保留。
- `T-DERIVATION-GENERATION-BINDING`（10 条）：分别递增 Artifact generation 和 Source generation，验证旧候选 stale、新候选 ID 变化、旧候选在所有消费入口被阻断、happy path 可确认。

**[判断]** 51 条断言不是固定字符串 / 单一调用方式适配，而是覆盖字段级变形、授权维度矩阵、多输入 Project 排列和 generation 滚动。所有断言仍使用同一合成夹具 `lifeos-p3-007-synthetic-v4`，但测试逻辑是参数化的，不是硬编码路径。独立变形反例（100 条）进一步验证了不在固定测试路径中的场景。未发现过拟合到特定夹具形状的问题。

## 5. 新绕路检查

### 恢复载荷自证

`restore_candidates()` 源码确认：Artifact 恢复调用 `read_artifact()` 返回当前 DB 行；Derivation 恢复调用 `_derivation_projection()` 重新生成投影；Feedback 恢复查询当前 `feedback` 表；Link 恢复查询当前 `important_links` 表并验证两端 ID 在 `restored_ids` 中。包内字段不参与恢复结果构造。**未发现新绕路。**

### 写入口授权绕过

`add_feedback()` 源码确认：要求 `project_id` 和 `authorization_contexts` 参数；调用 `_derivation_projection()` 检查所有证据输入的 project / version / artifact_generation / source_generation / authorization / tombstone；Feedback 确认前重检候选状态必须为 `unconfirmed`。`add_important_link()` 源码确认：对两端 Artifact 调用 `read_artifact()` with auth contexts；验证同 Project；两端必须存在且非 tombstone。**未发现新绕路。**

### 跨 Project state 泄漏

`export_test_package()` 源码确认：`rows_for_project` 查询先按 Project 限制 Artifact / Source / Authorization；`derivation_states` 生成时对每条 Derivation 调用 `_derivation_projection()` 检查所有输入 Project 归属，不属于当前 Project 的 Derivation 整体省略；`feedback_states` 只包含属于当前 Project 的 Derivation 关联 Feedback；`control_states`、`excluded`、`partial_failures` 均限制在目标 Project。**未发现新绕路。**

### generation 证据漏绑

`derivation_input` 表确认：新增 `artifact_generation` 和 `source_generation` 列；候选哈希计算包含完整三元组。`_derivation_projection()` 源码确认：逐输入对照 `row["artifact_generation"]` 和 `row["source_generation"]` 与当前值；不匹配返回 stale 投影。`_invalidate_generation_mismatches()` 确认：generation 变化时标记旧候选为 stale。`can_consume()` 确认：重检 generation 和 source_generation。**未发现新绕路。**

### 确认状态回退

`add_feedback()` 确认：对 `confirmed` / `edited_confirmed` 候选调用时抛出 `ValueError("Cannot add feedback to confirmed derivation")`。重复建议保持同一身份。**未发现新绕路。**

### 派生物复活

`revoke_processing()`、`disconnect_source()`、`delete_content()`、`retract_feedback()` 后，`restore_candidates()` 返回的候选来自当前权威状态，tombstone 优先。`can_consume()` 重检 tombstone。**未发现新绕路。**

## 6. H1-H9、T-ARCH 与能力启用门

| 合同 | 结论 | 依据 |
|---|---|---|
| H1 | **Pass** | 仍限个人、单设备、本地合成闭环；无产品范围扩张；无同步、多人、后台 / 运维叙事或自主 Agent |
| H2 | **Pass** | 恢复候选只返回当前权威 DB 投影；五类内容身份可分可追溯；Feedback 追加留痕；Project 不扩权；Derivation 身份绑定 `{version_id, artifact_generation, source_generation}` 三元组 |
| H3 | **Pass（合成窄测）** | 提交前后进程退出、重启、FTS / 派生故障隔离仍通过；11 条 `T-SAVE-CRASH-BOUNDARY` 断言通过 |
| H4 | **Pass** | read / search / recovery / export / restore / suggest / feedback / link 八入口均重检授权、来源、版本、tombstone、generation、证据集合；写入口 fail closed；未知即拒绝；22 + 14 + 12 条断言通过 |
| H5 | **Pass** | 四命令分离；撤回 / 删除先活跃阻断；物理清理诚实；恢复 / 重导入不复活；generation 变化后旧候选 stale；17 + 6 + 3 条断言通过 |
| H6 | **Pass（关闭态）** | 无真实 Tauri / IPC / 文件能力；R-0040 未被改变 |
| H7 | **Pass（合成层）** | fixture 为 `lifeos-p3-007-synthetic-v4`，synthetic-disposable；不构成真实数据许可 |
| H8 | **Pass（关闭态）** | Vault、云 / 模型、向量、同步、L3、外部用户均未启用；`T-OFF` 和 `T-IPC-OFF` 通过 |
| H9 | **Pass** | 导出完整 / 部分 / 失败、校验 / 冲突 / 不复活通过；所有 state 字段执行 Project 闭包；恢复使用权威投影；12 + 12 条断言通过 |
| T-ARCH | **Pass** | SQLite + FTS-first；本地权威原文 / 控制账本；派生可重建；权威 / 派生 / outbox 分责；所有消费入口重检授权 / 来源 / 版本 / tombstone / generation / 证据；恢复返回权威投影；导出执行 Project 闭包 |

能力启用门全部保持关闭；未发现真实数据、真实 Vault、真实 Tauri / IPC、文件导出扩权、云 / 第三方模型、向量、同步 / 多设备、L3、外部用户、Beta 或商业化能力被启用。

## 7. P0 / P1 / P2 问题清单

### P0

无。

### P1

无。

### P2

1. **[继承观察项]** `DISABLED_CAPABILITIES` 仍为可变类字典，属于未来能力门防御性缺口。当前无适配器，未形成真实能力 P0。
2. **[继承观察项]** 隐私扫描仍只覆盖指定合成 fixture 与有限正则，不能外推到附件或真实副本。
3. **[新观察项]** 全部 136 条断言和 100 条独立反例仍使用同一合成夹具 `lifeos-p3-007-synthetic-v4`。测试逻辑是参数化的，不是硬编码路径，但夹具多样性有限。建议后续工程任务增加多夹具变异测试。
4. **[新观察项]** 恢复候选的 checksum 仅检测未重算损坏，不作为真实性证明。MANIFEST.md 已明确声明此限制。建议后续迁移到真实技术栈时引入密码学签名。

以上 P2 均不阻塞当前合成工程基线恢复。

## 8. 是否建议 P3-001 恢复为后续工程基线候选

**是。**

在当前合成、单进程、受控测试包边界内，P3-006 四项 P0 的根因已独立确认关闭，P3-002 / P3-004 历史 P0 未复发，未发现新绕路或过拟合问题。H1-H9 与 T-ARCH 在当前边界内成立。

建议条件：
- P3-001 恢复基线后，后续工程任务应继续在真实技术栈（Tauri + SQLite）迁移时复测 H1-H9 / T-ARCH 不变量。
- P3-001 作为基线候选的含义是"当前合成证据层的不变量已验证"，不等于"生产级实现已就绪"或"真实能力已启用"。

## 9. 是否建议 PM 关闭 R-0041

**是。**

R-0041 描述"P3-001 恢复工程基线前不得关闭"。本轮独立复评确认：
- P3-006 四项 P0 根因已关闭（独立 100 条变形反例验证）。
- 三轮历史 P0 均未复发。
- H1-H9 / T-ARCH 在当前边界内成立。
- 未发现新绕路、过拟合或固定夹具自证问题。

建议 PM 在采纳本复评结论后关闭 R-0041。后续工程任务中发现新问题时可重新开放风险。

## 10. 不得外推的结论

本复评不证明：正式恢复 / 导出协议；密码学真实性；真实数据安全性；真实 Vault 适配；真实 Tauri / IPC 安全；文件系统权限安全；云 / 第三方模型安全；向量搜索正确性；同步 / 多设备一致性；L3 自动动作安全性；外部用户 / Beta / 商业化就绪；Gate 5 用户价值验证；生产 SLA；Schema / API / UI / Tauri capability / 导出格式 / 最终工程目录冻结。

23 PASS 不等于 P3-001 已通过生产级验收或真实能力已启用。本复评仅在当前合成、单进程、受控测试包边界内有效。

## 11. 关卡检查

- Gate 1 产品一致性：**Pass。** 未扩张 LifeOS 定位或 V1 范围。
- Gate 2 数据与来源评审：**Pass。** 恢复候选返回权威投影；五类内容身份可分可追溯；Derivation 身份绑定 generation 三元组；跨 Project state 零泄漏。
- Gate 3 AI 权限与信任评审：**Pass。** Feedback / Link 写入口重检完整证据与授权；确认状态不回退；控制命令传播失效；默认关闭能力不可旁路。
- Gate 4 技术可行性评审：**Pass。** 恢复 / 导出 / 写入口共同落实冻结架构消费前重检合同；权威 / 派生 / outbox 分责成立；generation / tombstone 优先。
- Gate 5 用户价值验证：**未评结果层**；本任务只确认没有被错误外推。

## 12. 需要 PM 主会话确认的问题

1. **[需 PM 确认]** 是否接受本次 `Pass` 结论，恢复 P3-001 为后续工程基线候选。
2. **[需 PM 确认]** 是否关闭 R-0041。
3. **[需 PM 确认]** 是否在恢复基线后创建后续工程任务（如真实技术栈迁移或 Phase A 能力启用），以及后续任务的优先级和 Agent 分派。

专项会话不更新任何项目账本、不关闭风险、不启动后续任务。

## 13. 后续任务建议

1. **建议优先：** 在 P3-001 恢复基线后，创建真实技术栈迁移任务（Tauri + React + SQLite），将当前 847 行单文件 Python 原型验证的不变量迁移到生产代码。迁移时必须逐条复测 H1-H9 / T-ARCH。
2. **建议次优：** 增加 P2 观察项的修复：将 `DISABLED_CAPABILITIES` 改为不可变配置；扩展隐私扫描覆盖更多数据形态；增加多夹具变异测试。
3. **建议后续：** 在真实技术栈迁移完成并通过独立评审后，按 P2-019 能力启用门逐级开放 Phase A-H 能力。
