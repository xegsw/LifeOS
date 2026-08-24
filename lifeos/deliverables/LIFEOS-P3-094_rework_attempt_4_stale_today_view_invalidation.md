# LIFEOS-P3-094 Rework attempt-4｜旧今日页失效 P1 窄整改交付物

## 任务信息

- 任务 ID：LIFEOS-P3-094（Rework attempt-4）
- 执行 Agent：Codex，任务卡路由 `gpt-5.6-terra` + `high`，未降级
- 任务类型：P0 受控真实本地能力包内 P1 窄整改
- 更新时间：2026-08-22
- 执行授权证据：用户于 2026-08-22 将 `lifeos/tasks/LIFEOS-P3-094_real_local_capture_persistence_today_view_controlled_capability_package.md` 投递至本新建、未承担 P3-095 独立评审的 Codex 工程会话；接收时间 2026-08-22 18:00 CST。本次授权仅覆盖 D-0387 attempt-4：修复清理后旧 `today.html` 未失效、补正负回归和保全型 Evidence。

## 修复目标与事实结论

本轮已修复 P3-095 发现的 P1：清理不再先删除 SQLite 行后遗留旧页面。`delete_all()` 现在先对调用方明确指定的内部 `today.html` 做精确删除并确认路径不存在，随后才打开数据库并执行事务清理。若页面删除或失效核对失败，操作明确失败，数据库保持原记录且不得报告成功。

若页面已失效而后续数据库操作失败，运行时仍以失败披露结束，不报告清理成功；展示工件已不可见、SQLite 数据仍保留，可在诊断后重试。这是本单进程 task-local 边界内的 fail-closed 次序，不外推为并发或生产文件事务保证。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-094/src/local_capture.py`：新增精确页面失效门；清理事务后记录不含原文的审计状态；数据库错误明确失败。
- `lifeos/engineering/LIFEOS-P3-094/scripts/operator_cli.py`：`clear` 支持明确 `--output`；未提供时仅使用同一 DB 父目录的 `today.html`。
- `lifeos/engineering/LIFEOS-P3-094/tests/test_runtime.py`：新增正向清理与页面失效失败负向回归；每项测试用 `tearDown` 精确清理自建目录。
- `lifeos/engineering/LIFEOS-P3-094/README.md`：对齐清理命令和 fail-closed 次序。
- `lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/`：新增保全型 runner、结果、日志、hash、Manifest 与验收追溯矩阵。

## 非范围

- 未读取、导入或写入任何既有个人文件／DB；未使用用户真实文本。
- 未启用网络、HTTP、云／第三方、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 未覆盖 attempt-1／2／3、P3-095 Review／Evidence 或项目账本；`/private/tmp/lifeos-p3-095-pycache` 未被本会话创建、访问或处理。
- 未关闭 R-0051，未恢复工程基线，未冻结 Schema/API 或资产，未进入 Stage 4。
- 本执行会话未替代后续全新隔离独立复评的 Chrome `file:` 动态矩阵。

## 测试与包内自检

复跑命令：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/scripts/run_attempt_4.py
```

结果为 **13 PASS / 0 FAIL**：首次捕获、幂等重复、同键冲突、真实新进程复读、渲染前置、正向“页面先失效→DB 清空→旧页面不存在→重渲染失败”、负向“页面失效失败→DB 保留→操作失败”、原子写入失败、损坏 DB fail-closed、禁止能力关闭态、干净副本单元回归、task-local 残留为零、56 个历史只读文件前后 hash 相同。

另以独立 `/private/tmp` Evidence 输出路径完整复跑，仍为 13 PASS / 0 FAIL；核对后已精确移除该复跑目录。Manifest 所列 14 个非自指文件 hash 已逐项复算一致。未保存 SQLite、HTML、缓存、记录 ID 或原文至 Evidence。

问题计数：P0=0；P1=0；P2=0；Unknown=0；Not Implemented=0。未覆盖项仅为任务卡明确保留给 PM Pass、用户采纳后全新隔离独立复评的 Chrome `file:` 完整动态矩阵，不属于本 attempt-4 执行侧缺项。

## Evidence

- Manifest：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/evidence/MANIFEST.md`
- 结构化结果：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/evidence/results.json`
- 验收追溯：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/evidence/acceptance_matrix.md`
- 历史保全：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-4/evidence/historical_read_only_hashes.json`
- 操作日志／复跑：`operation_log.md`、`test_run.log`、`rerun.md`

本地模型预检已跳过：本任务卡明确禁止网络与模型，且本轮属于真实本地数据清理边界的 P0/P1 高风险判断；按项目允许跳过场景，不让局域网模型介入或替代人工复核。

## 角色与关卡

- 主责角色：技术架构负责人／Codex 工程执行。
- 协审视角：数据与来源、AI 信任与安全、体验设计。
- Gate 2：执行侧范围内通过；清理成功后旧展示工件不可继续暴露原文，失效失败时 DB 不变。
- Gate 3：执行侧关闭态通过；无 AI 或外部处理，显式 `DELETE` 确认保持不变。
- Gate 4：执行侧包内回归通过；P3-095 P1 正负路径与零残留已覆盖。
- Gate 1：仅做范围一致性核对；Gate 5 未覆盖且未写成通过。
- 尚需关卡：PM 验收、用户采纳、另一全新隔离会话完整离线与 Chrome `file:` 独立复评。

## 风险、推断与建议

事实：本轮固定非敏感、单进程、task-local SQLite／HTML 范围内的 P1 已由当前 Evidence 关闭；历史资产 hash 未变化。

推断：当前次序消除了已知“DB 已清空但旧页面仍可展示”的中间与最终状态；它不证明多进程竞争、任意外部文件系统故障或生产级事务语义。

建议：提交 PM 按 attempt-4 当前 hash 验收。PM Pass 与用户采纳后，按任务卡创建另一全新隔离独立评审会话，完整重跑离线与 Google Chrome `file:` 动态矩阵。本执行会话不自行启动后续任务。

## 是否触发用户／PM确认

- 当前是否需要 PM 决策：Yes；仅需 PM 验收本次 attempt-4 是否 Pass。
- 是否需要后续独立复评：Yes；P0 能力包与 D-0387 明确要求。
- 是否请求扩大范围：No。
