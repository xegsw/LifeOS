# LIFEOS-P3-006｜P3-001 第二轮 P0 返工独立工程复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-006`
- 对应实现 / 交付：`LIFEOS-P3-001`、`LIFEOS-P3-005`
- 独立评审角色：独立工程评审负责人
- 协审视角：技术架构、AI 信任与安全、数据 / 领域模型、质量 / 测试、PM
- 评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅检查未被外推
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-006_second_p0_remediation_independent_engineering_re_review.md`
- 评审结论：**Rework**
- 更新时间：2026-08-11

## 1. 复评结论摘要

1. **[事实]** 指定 `py_compile` 与统一验证均成功，结果为 **19 PASS / 0 FAIL、P0=0、P1=0**；`test_results.json`、原始日志、85 / 85 条记录断言和内容快照 `3779cd5efe2d55a5bafe7e78cef4bd8eac230df52b394c14be69fe189965f3a3` 相互一致。
2. **[事实]** P3-004 三项原失败反例的固定形态已经关闭：旧 / 伪造控制字段不能覆盖当前删除状态；两项候选证据在控制命令下均能传播失效；22 类授权缺失、冲突或错配在六个主要读取型消费入口共 132 / 132 条独立断言通过。
3. **[事实]** 独立变形反例发现四项 P0：重算 checksum 后篡改实际恢复载荷仍被当作 `restored` 返回；Feedback / Link 写入口完全绕过当前授权和证据门；混合 Project Derivation 及其 Feedback 状态从导出旁路泄漏；证据只绑定版本、不绑定 Artifact / Source generation，代际变化后旧候选仍以同一身份保持 `unconfirmed`。
4. **[推断]** P3-005 修复了 P3-004 指定调用方式，但尚未关闭 H2、H4、H5、H9 与 `T-ARCH` 的根不变量；19 个测试组和 85 条记录断言是真实执行结果，但覆盖仍过拟合固定夹具与读取型入口。
5. **[建议]** P3-001 不应恢复为后续工程基线候选，R-0041 应继续保持 `Open`；下一步应继续做一次窄范围 P0 返工与补测，之后再次独立复评。
6. **[边界]** 本复评未修改源码、测试、夹具、README、项目账本或冻结资产；只允许统一验证命令自然重建 evidence，并运行内存 SQLite / 临时进程反例；未启用任何真实能力。

## 2. 复跑命令、结果与 evidence 一致性

执行：

```bash
python3 -m py_compile lifeos/engineering/LIFEOS-P3-001/run_validation.py lifeos/engineering/LIFEOS-P3-001/src/*.py lifeos/engineering/LIFEOS-P3-001/tests/*.py
cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py
```

- `py_compile`：PASS；统一验证退出码 0。
- 测试：19 PASS / 0 FAIL；P0 失败 0；P1 open 0。
- `test_run.log` 有 19 个 `ok`；`test_results.json` 有 19 个对应测试记录。
- `regression_assertions.json` 八组记录断言数量为 17、6、12、12、14、10、3、11，合计 85，失败 0；其中 P3-005 新增三组为 3 + 6 + 14 = 23。
- `snapshot_manifest.json` 记录 7 个非 evidence 文件，快照 ID 与 `test_results.json`、`MANIFEST.md` 一致。
- 复跑前后 `regression_assertions.json` 与 `snapshot_manifest.json` 的 SHA-256 不变；`MANIFEST.md`、`test_results.json`、`test_run.log` 因复跑时间和耗时自然变化。未发现逻辑结果或工程内容快照不一致。

**[判断]** 19 / 0、P0=0、P1=0、85 / 85 和快照标识均可复核；但 85 只统计八个使用 `record_equal()` 的回归组，另外 11 个测试组虽有真实 unittest 断言，却在 manifest 中显示记录断言为 0。Evidence 能证明已列断言通过，不能证明所有消费入口与变形状态已覆盖。

## 3. P3-004 三项新增 P0 独立重放

| P3-004 问题 | 独立重放结果 | 根因关闭判断 |
|---|---|---|
| 旧控制包 / 重算控制字段自证恢复 | 对已删除对象重写 `control_states` 并重算 checksum，当前 SQLite tombstone 仍胜出，对象未恢复 | **固定资格门已关闭；恢复载荷完整性未关闭** |
| 非主证据撤回不传播 | 对 Decision / Unprocessed 两个证据位置分别执行撤权、断源、删除，共 6 种组合；候选 stale，导出 / 恢复 Derivation、Feedback、Link、搜索和建议共 48 / 48 条阻断断言通过 | **控制命令路径通过；generation 变形与写入口仍未关闭** |
| 缺失 / 冲突授权上下文放行 | 对 subject、Project、version、Artifact / Source generation、purpose、location、processor、now 的缺失 / 错配，以及未知、过期、重复 allow、allow / deny 冲突，在 read / search / recovery / export / restore / suggest 六入口共 132 / 132 条断言通过 | **六个读取型入口通过；Feedback / Link 写入口未纳入门** |

因此不能把“三条固定反例通过”等同于“三项根不变量全部关闭”。

## 4. P3-002 四项历史 P0 回归

- **跨 Project 导出：部分通过后被新反例击穿。** 普通双 Project、各自独立候选 / Feedback / Link 以及跨 Project Link 的既有形态零泄漏；但混合 Project Derivation 只要任一输入属于 Project A，就会进入 A 包的 `derivation_states`，其 Project B 证据版本和关联 `feedback_states` 同时泄漏。
- **四控制命令后旧包复活：固定对象资格路径通过。** 撤权、断源、删除、撤回 Feedback 后，当前状态能阻止旧包恢复相应 Artifact / Derivation / Feedback；但恢复函数仍返回包内而非权威库内载荷，见 P0-1。
- **确认状态回退：通过。** `confirmed`、`edited_confirmed` 重复建议保持同一身份和状态，原 Feedback 可追踪；独立 6 / 6 断言通过。
- **Authorization 维度错配：六个读取型入口通过。** location / processor 等维度及歧义状态均 fail closed；但 `add_feedback()` 与 `add_important_link()` 不接受授权上下文，也不做当前证据重检，历史授权 P0 在新增入口形态下仍有绕路。

## 5. 新绕路与过拟合检查

### P0-1：恢复门重检“能否恢复”，却直接信任包内“恢复什么”

`restore_candidates()` 对 Artifact 只比较 ID、version、generation 并调用当前读取门，随后把旧包的 Artifact 字典直接加入 `restored`；Derivation 只比较当前 status 和输入 ID；Feedback 只比较当前 active；Link 只检查两端 ID。它没有将包内 title / original_text / content_hash / source、Derivation output / rule / generation、Feedback kind / user_text、Link 身份与当前权威行逐项对照，也没有改为返回当前权威投影。

独立反例修改这些载荷并重算公开 SHA-256：伪造用户原文、伪造派生文本、伪造 Feedback、注入数据库中不存在的 Link 均被返回为已恢复。共 4 / 4 安全断言失败。该问题使公开 checksum 继续承担了它不具备的真实性作用，击穿用户原文保护、身份追踪和安全恢复，归类 H2 / H4 / H9 / `T-ARCH` P0。

### P0-2：Feedback 与 Link 写入口绕过当前消费门

`add_feedback()` 只检查 Derivation 为 `unconfirmed`；`add_important_link()` 无 Project、Authorization、Source、version、tombstone、generation 或证据检查。独立反例在候选证据 Authorization 已改为 deny 后，仍可确认候选并创建 Link；还可通过公共方法直接创建跨 Project Link。3 / 3 安全断言失败。

这不是导出过滤可以补救的问题：非法确认或关系已经进入权威 Feedback / Link 账本。它违反“反馈、Link 等入口也必须消费前重检”的任务要求，归类 H2 / H4 / H5 / `T-ARCH` P0。

### P0-3：混合 Project Derivation 的状态导出旁路

导出查询以“任一 `derivation_input` 属于当前 Project”选取 `rows_for_project`，随后无条件写入 `derivation_states`；关联 Feedback 也无条件写入 `feedback_states`。只有活跃 `derivations` / `feedback` 列表要求证据全集属于 allowed closure。

独立构造 A + B 混合证据 Derivation 后导出 A：Derivation ID、B 的版本 ID 和关联 Feedback ID / 用户文本均出现在序列化包中，3 / 3 零泄漏断言失败。即使字段名带 `states`，它们仍是导出载荷，不能绕过 Project 闭包。归类 H4 / H9 P0。

### P0-4：Derivation 证据未绑定 generation，代际变化后旧候选继续活跃

`derivation_input` 只保存 ArtifactVersion ID；候选 ID 也只由版本 ID 集合计算。独立模拟当前 Artifact generation 与唯一 allow Authorization generation 同步递增后，Decision 与 Unprocessed 两种证据位置都返回原 Derivation ID，状态仍为 `unconfirmed`，而非失效、拒绝或生成绑定新代际的新身份。

这证明“完整证据”仍只完整到版本集合，没有覆盖冻结合同要求的 Artifact / Source generation。控制命令恰好调用 `_invalidate_dependents()` 不能代替消费时的代际绑定。归类 H2 / H4 / H5 / `T-ARCH` P0。

### P1 / P2

**P1：**（1）新增 23 条断言只覆盖固定控制字段篡改、固定两项证据中的一次非主撤权和读取型授权入口，未覆盖恢复载荷篡改、写入口、混合 Project Derivation、generation rollover；（2）`tampered_package_fail_closed` 仅修改包后不重算 checksum，命名和摘要容易被误读为有真实性 / 防伪能力。

**P2：**（1）`DISABLED_CAPABILITIES` 仍为可变类字典，属于未来能力门防御性缺口；当前无适配器，未形成真实能力 P0；（2）隐私扫描仍只覆盖指定合成 fixture 与有限正则，不能外推到附件或真实副本。

## 6. H1-H9、T-ARCH 与能力启用门

| 合同 | 结论 | 依据 |
|---|---|---|
| H1 | Pass | 仍限个人、单设备、本地合成闭环，无产品范围扩张 |
| H2 | **Fail / P0** | 包内原文 / 派生 / Feedback 可被重签篡改；Feedback 写门和 generation 证据身份不成立 |
| H3 | Pass（合成窄测） | 提交前后进程退出、重启、FTS / 派生故障隔离仍通过 |
| H4 | **Fail / P0** | Feedback / Link 无授权门；混合 Project 状态泄漏；generation 未绑定；恢复载荷不回连权威 |
| H5 | **Fail / P0** | 固定控制命令传播通过，但代际变化与非法 Feedback / Link 仍可保留可信状态 |
| H6 | Pass（关闭态） | 无真实 Tauri / IPC / 文件能力；R-0040 未被改变 |
| H7 | Pass（合成层） | fixture 为 synthetic-disposable；不构成真实数据许可 |
| H8 | Pass（关闭态） | Vault、云 / 模型、向量、同步、L3、外部用户均未启用 |
| H9 | **Fail / P0** | 重签载荷可被“恢复”，Project 状态导出泄漏，安全恢复 / 导出合同不成立 |
| T-ARCH | **Fail** | SQLite / FTS-first、权威 / 派生 / outbox 分责局部成立；所有消费入口重检、权威恢复投影、证据 generation 与 Project 闭包未成立 |

能力启用门全部保持关闭；未发现真实数据、真实 Vault、真实 Tauri / IPC、文件导出扩权、云 / 第三方模型、向量、同步 / 多设备、L3、外部用户、Beta 或商业化能力被启用。

## 7. 问题清单与最终建议

### P0

1. 重算 checksum 后篡改 Artifact / Derivation / Feedback / Link 恢复载荷仍被返回为 `restored`。
2. Feedback / Link 写入口不重检授权、证据、Project、版本、tombstone 与 generation。
3. 混合 Project Derivation / Feedback 状态通过导出 state 字段泄漏。
4. Derivation 证据与身份未绑定 Artifact / Source generation，代际变化后旧候选仍活跃。

### P1

1. 23 条新增断言和 85 条记录断言仍过拟合固定夹具、固定字段与读取型入口。
2. checksum 相关测试命名 / evidence 摘要超过其“仅检测未重算损坏”的真实能力。

### P2

1. 可变关闭能力字典缺少未来不可绕过启用门。
2. 隐私扫描只支持当前合成夹具边界。

**是否建议 P3-001 恢复为后续工程基线候选：否。** 任何 P0 存在时不得判 Pass 或 Pass with Conditions。

**是否建议 PM 关闭 R-0041：否。** 本轮再次证明固定回归通过后仍有调用方式与状态空间过拟合，R-0041 应继续保持 `Open`。

**建议下一步：** 继续一个窄范围 P0 返工任务，而不是恢复基线、散开开发或暂停整条工程线：恢复候选只返回当前权威投影并逐类验证包内身份 / 内容；为 Feedback / Link 增加对象级当前门和 Project 闭包；导出所有 state / excluded / control 字段也执行 Project 与最小披露闭包；将 Artifact / Source generation 纳入 Derivation 依赖身份和消费重检；把本次 10 条失败反例及两条 generation 反例纳入统一自动回归。返工后再次独立复评。

## 8. 关卡、不得外推与 PM 决策

- Gate 1：**Pass**，未扩张 LifeOS 定位或 V1 范围。
- Gate 2：**Fail**，恢复载荷身份、跨 Project 派生状态和 generation 证据关系存在 P0。
- Gate 3：**Fail**，Feedback / Link 可绕过当前授权与证据门，用户确认可信度不成立。
- Gate 4：**Fail**，恢复 / 导出 / 写入口未共同落实冻结架构消费前重检合同。
- Gate 5：**未评结果层**；本任务只确认没有被错误外推。

不得把本复评或现有 19 PASS 外推为真实数据、真实 Vault、真实 Tauri / IPC、正式文件导出、云 / 第三方模型、向量、同步、多设备、L3、外部用户、Gate 5、Beta、商业化或生产安全通过；不冻结 Schema、API、UI、Tauri capability、正式导出格式、生产 SLA 或最终目录。

**需 PM 主会话确认：** 是否接受本次 `Rework` 结论，继续保持 P3-001 非基线与 R-0041 Open，并决定是否创建上述窄范围 P0 返工任务。专项会话不更新任何项目账本、不关闭风险、不启动后续任务。

