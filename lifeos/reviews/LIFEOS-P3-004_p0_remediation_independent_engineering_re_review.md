# LIFEOS-P3-004｜P3-001 四项 P0 返工独立工程复评

## 评审信息

- 对应任务 ID：`LIFEOS-P3-004`
- 对应实现 / 交付：`LIFEOS-P3-001`、`LIFEOS-P3-003`
- 独立评审角色：独立工程评审负责人
- 协审视角：技术架构、AI 信任与安全、数据 / 领域模型、质量 / 测试、PM
- 评审关卡：Gate 1、Gate 2、Gate 3、Gate 4；Gate 5 仅检查未被外推
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-004_p0_remediation_independent_engineering_re_review.md`
- 评审结论：**Rework**
- 更新时间：2026-08-09

## 1. 复评结论摘要

1. **[事实]** 指定 `py_compile` 通过；统一验证复跑为 **16 PASS / 0 FAIL、P0=0、P1=0**。机器结果包含 16 个测试组，新增五组共 **62 / 62** 条记录断言通过，快照仍为 `285c74ac96f2ea978c91baaf8d526c61fbbb944407f21e221aabe1556a21860c`。
2. **[事实]** P3-002 的四个原始反例按 P3-003 预设调用方式独立重放均通过：双 Project 闭包零泄漏；四控制命令配合新生成的当前控制包不复活；`confirmed` / `edited_confirmed` 不回退；显式授权维度错配均拒绝。
3. **[事实]** 新绕路检查共执行 40 条独立断言，原始反例及显式矩阵 34 条符合预期，但 6 条新的 fail-closed 断言失败，归并为三项 P0：恢复门不读取权威当前状态；候选未保存完整证据依赖；授权上下文可被函数默认值静默补齐且冲突授权不拒绝。
4. **[推断]** P3-003 修复了固定反例的表面入口，但没有关闭 H4、H5、H9 与 `T-ARCH` 的根不变量；62 条断言是真实执行结果，却不足以证明不存在绕路，存在明显夹具与调用方式过拟合。
5. **[建议]** P3-001 不应恢复为后续工程基线候选；R-0041 应继续保持 `Open`。下一步应是窄范围 P0 返工与再次独立复评，不应散开工程线或启用能力。
6. **[边界]** 本复评未修改实现、测试、夹具、README 或项目账本；只由指定验证命令自然重建 evidence，未启用真实数据、真实 Vault、真实 Tauri / IPC、文件导出、云 / 第三方模型、向量、同步、L3 或外部用户能力，也未冻结生产资产。

## 2. 复跑命令、结果与 evidence 一致性

执行命令：

```bash
python3 -m py_compile lifeos/engineering/LIFEOS-P3-001/run_validation.py lifeos/engineering/LIFEOS-P3-001/src/*.py lifeos/engineering/LIFEOS-P3-001/tests/*.py
cd lifeos/engineering/LIFEOS-P3-001 && python3 run_validation.py
```

- `py_compile`：PASS。
- `run_validation.py`：16 PASS / 0 FAIL；P0 失败 0；P1 open 0；退出码 0。
- `test_results.json`：16 个测试组，与 `test_run.log` 的 16 个 `ok` 一致。
- `regression_assertions.json`：五组断言数量分别为 17、12、12、10、11，合计 62，失败 0。
- `snapshot_manifest.json` 与 `test_results.json` 的快照标识一致；7 个非 evidence 文件纳入逐文件 SHA-256。
- 复跑前后 `regression_assertions.json` 与 `snapshot_manifest.json` 哈希不变；`MANIFEST.md`、`test_results.json` 和 `test_run.log` 因运行时间与测试耗时自然重建而变化，未发现逻辑结果不一致。

抽查范围包括 `MANIFEST.md`、`test_results.json`、`regression_assertions.json`、`snapshot_manifest.json`、`test_run.log`，以及核心代码、测试、合成夹具和验证器。**一致性判断：报告中的 16 / 0、62 / 62 与快照标识可复核；但 evidence 只能证明已列断言通过，不能证明根合同已覆盖。**

## 3. 四个原始 P0 反例独立重放

| 原始问题 | 独立结果 | 判断 |
|---|---|---|
| Project A 导出混入 B 的 Artifact、Version、Source、Authorization、Derivation、Feedback、Link 或跨 Project Link | PASS；所列 B 身份均零命中，A 的 Version / Source / Authorization 集合闭合 | 固定双 Project 夹具入口已修复 |
| 四控制命令后旧包恢复对象、派生、Feedback、搜索或队列 | PASS；前提是调用方另行生成并传入真实当前控制包 | 固定调用方式通过，但恢复门本身不具权威重检能力 |
| `confirmed` / `edited_confirmed` 重复建议回退 | PASS；身份、状态与 Feedback 均保留 | 原静默覆盖路径已修复 |
| purpose、location、processor、Project、精确版本、generation、时效、decision 错配 | PASS；显式传入完整上下文时均 fail closed | 显式矩阵通过，但实际消费入口仍省略上下文 |

## 4. 新绕路与过拟合检查

### P0-A：恢复门接受旧或可重算的“控制包”自证

`restore_candidates()` 是静态函数，只比较两个包；所谓当前状态完全来自调用者传入的 `control_package`，没有数据库、当前控制账本或可信快照锚点。撤回后调用 `restore_candidates(stale, stale)`，已撤回 Artifact 仍进入 `restored`。进一步将撤回后的控制包字段替换为旧状态并重算公开 SHA-256，校验仍通过、删除对象仍恢复。现有篡改测试只改内容但不重算校验和，证明的是偶然损坏检测，不是当前性或防篡改。

该问题使“旧包 + 当前包”happy path 通过，却不能保证旧 generation、旧授权或伪造控制状态无法绕过，属于 H4 / H5 / H9 / `T-ARCH` P0。

### P0-B：候选只保存一个输入版本，其他证据撤回不传播

`suggest_next_step()` 用“Decision + Unprocessed”的完整版本集合计算候选 ID，但 `derivation` 只持久化一个 `input_version_id`（Unprocessed）。`_invalidate_dependents()` 也只按该单一字段失效。独立反例先生成候选，再对参与证据的 `artifact-decision` 执行 `revoke_processing`：候选仍为 `unconfirmed`，并继续出现在当前导出包的 `derivations` 中。

这不是确认状态回退，但同样破坏 AI 候选证据与授权撤回边界：候选身份声称依赖完整证据集，实际失效图只认识一个输入。属于 H2 / H4 / H5 / `T-ARCH` P0。

### P0-C：授权上下文缺失被默认值补齐，冲突记录可被任取一行

`can_consume()` 的 purpose、location、processor 带允许值默认参数；`read_artifact()`、索引完成等消费入口未显式传入这些上下文。因此“调用方缺失上下文”实际返回 `True`，新增测试只有显式传 `None` 才得到拒绝，未覆盖真实入口。另插入同 subject、同维度但 `decision='deny'` 的冲突 Authorization 后，`LEFT JOIN ... fetchone()` 仍可能选中 allow 行并返回 `True`；未知 / 冲突状态未 fail closed。

这说明 P3-003 只修复了字段比较，没有落实“所有消费入口完整传入上下文”和“歧义拒绝”，属于 H4 / `T-ARCH` P0。

### 过拟合判断

- 62 条断言均由真实测试生成，不是固定摘要伪造；快照可唯一定位当前非 evidence 内容。
- 但旧包测试固定把被控对象设为候选唯一持久化输入，未撤回候选的其他证据；恢复测试固定提供新生成的当前包；篡改测试不重算校验和；授权测试用默认参数验证“合法匹配”，与真实消费入口的缺失上下文混为一谈。
- 因此 evidence 在“真实性”上通过，在“覆盖充分性”上未通过。

## 5. H1-H9、T-ARCH 与能力启用门

| 合同 | 结论 | 依据 |
|---|---|---|
| H1 | Pass | 仍限个人、单设备、本地合成闭环，无范围扩张 |
| H2 | **Fail / P0** | 完整证据集合未持久化，证据撤回后候选仍活跃可导出 |
| H3 | Pass（合成窄测） | 提交前 / 后强杀、重启、FTS / 派生故障隔离通过 |
| H4 | **Fail / P0** | 实际入口缺失授权上下文；冲突 Authorization 不拒绝；恢复不重检权威当前状态 |
| H5 | **Fail / P0** | 非主输入证据撤回不传播；旧控制快照仍可恢复 |
| H6 | Pass（关闭态） | 无真实 Tauri / IPC / 文件能力；R-0040 未被本任务改变 |
| H7 | Pass（合成层） | fixture 为 synthetic-disposable；不构成真实数据许可 |
| H8 | Pass（关闭态） | 真实 Vault、云 / 模型、向量、同步、L3、外部用户均未启用 |
| H9 | **Fail / P0** | 恢复候选可由旧 / 伪造控制快照绕过，不复活合同不成立 |
| T-ARCH | **Fail** | 权威 / 派生 / outbox 分责与 FTS-first 局部成立，但消费前重检、证据依赖和当前控制账本不成立 |

能力启用门：全部保持原状态；本任务没有能力启用请求。Gate 1 **Pass**；Gate 2、Gate 3、Gate 4 **Fail**；Gate 5 结果层未评，且未被错误外推。

## 6. P0 / P1 / P2 问题清单

### P0

1. 恢复门不读取权威当前状态，旧控制快照或重算校验和的伪造控制包可使对象复活。
2. 候选未持久化完整证据依赖，撤回非 `input_version_id` 证据后非法派生仍活跃并可导出。
3. 消费入口以默认值代替缺失授权上下文，且冲突 Authorization 可被非确定性选行后放行。

### P1

1. 五组新增回归对“控制包可信、候选只有一个关键输入、默认参数等于显式上下文”作了隐含假设，覆盖不足。
2. 包校验和是无密钥内容哈希，只能发现未重算的损坏；evidence 将其概括为“包篡改拒绝”过宽。

### P2

1. `DISABLED_CAPABILITIES` 仍是可变类字典，属于未来启用门的防御性缺口；当前无适配器，未形成真实能力 P0。
2. 隐私扫描仍只覆盖指定夹具与有限正则，只能支持本次合成数据边界，不能支持附件或真实副本能力门。

## 7. 基线、风险、不得外推与 PM 决策

- **是否建议 P3-001 恢复为后续工程基线候选：否。** 任何 P0 存在时不得判 Pass / Pass with Conditions。
- **是否建议 PM 关闭 R-0041：否。** 风险应继续保持 `Open`，直至上述 P0 返工并再次独立复评通过。
- **建议下一步：** 创建一个窄范围返工任务：让恢复候选在可信执行边界读取权威当前控制状态；持久化并遍历完整 Derivation 证据依赖；移除允许值默认上下文并让所有消费入口显式传入；对多授权记录定义唯一当前决策或歧义拒绝；将本次 6 条反例纳入自动回归。返工后再次独立复评。
- **不得外推：** 本复评不证明真实数据、真实 Vault、真实 Tauri / IPC、文件导出、云 / 第三方模型、向量、同步、L3、外部用户、Beta、商业化或 Gate 5 通过；不冻结 Schema、API、UI、Tauri capability、正式导出格式、SLA 或最终目录。
- **需 PM 主会话确认：** 是否接受本次 `Rework` 结论、保持 P3-001 非基线与 R-0041 Open，并授权创建上述窄范围返工任务。项目账本状态只能由 PM 主会话更新。

## 8. 角色检查点与范围声明

- 独立工程 / 技术架构：未通过；当前状态重检和证据依赖存在 P0 绕路。
- AI 信任与安全：未通过；授权上下文缺失可被默认值补齐，撤回证据不使候选失效。
- 数据 / 领域模型：未通过；Derivation 与完整 ArtifactVersion 证据集合的身份关系未持久化，Authorization 冲突语义不明确。
- 质量 / 测试：未通过；结果与快照可信，但反例维度不足以支撑根不变量。
- PM 范围检查：通过；无真实能力、Gate 5、Beta、商业化或生产冻结外推。

本任务只创建本独立复评文件，并由任务指定命令自然重建 evidence；未修改 P3-001 源码、测试、夹具、README、Stitch、PRD、冻结资产或项目账本，未连接外部服务或启用真实能力。
