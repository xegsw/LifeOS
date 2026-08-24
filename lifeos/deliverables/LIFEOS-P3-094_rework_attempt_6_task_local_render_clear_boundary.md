# LIFEOS-P3-094 Rework attempt-6｜Task-local render／clear 路径边界 P0 整改交付物

## 任务信息与授权

- 任务 ID：LIFEOS-P3-094（Rework attempt-6）
- 任务类型：P0 受控真实本地能力包窄整改
- 执行 Agent：Codex；实际路由按当前状态索引为 `gpt-5.6-terra` + `high`，未降级
- 任务卡：`lifeos/tasks/LIFEOS-P3-094_real_local_capture_persistence_today_view_controlled_capability_package.md`
- 执行授权证据：用户于 2026-08-22 将上述任务卡路径投递至本专项工程会话；任务卡 D-0392 明确规定重新投递即授权 attempt-6。
- 会话类型：新的隔离 Codex 工程会话；未承担 P3-095 独立评审。
- 用户确认范围：仅收紧 render 唯一 task-local `today.html`、render／clear 完整目录组件链接链与最终文件类型，并补固定非敏感回归。

## 整改结论

**执行侧包内自检通过，提交 PM 验收。** attempt-5 的两个 P0 反例已在当前实现和 19 项干净副本矩阵中关闭：

1. `render_today()` 不再接受调用方输出目标，只生成 `db_path.parent / "today.html"`；CLI 已移除 `render --output`。
2. render 与 clear 共用目录边界门：从绝对路径根开始以 `openat`／`O_NOFOLLOW` 逐级打开完整父目录链，并以不跟随链接的文件状态检查确认 DB 为普通文件。
3. 最终 `today.html` 必须不存在或为普通文件；符号链接、目录、FIFO／特殊文件和无法确认类型均在文件、DB 变更前拒绝。
4. render 通过同目录独占临时文件、`fsync` 和基于已打开目录句柄的 `os.replace` 原子发布，不跟随最终页面链接；clear 通过同一目录句柄先精确失效页面，再清理 SQLite。
5. 相对 DB 路径、含 `..` 路径、规范化后不等价路径、DB 最终链接以及任一祖先目录链接均 fail closed。

事实：本轮未改 capture/list 数据模型、SQLite Schema/API；未触达既有个人文件／DB、真实用户文本、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-094/src/local_capture.py`：共用路径边界验证、无链接目录句柄、render 原子发布和 clear 精确失效。
- `lifeos/engineering/LIFEOS-P3-094/scripts/operator_cli.py`：移除 `render --output`。
- `lifeos/engineering/LIFEOS-P3-094/tests/test_runtime.py`：更新唯一 render 路径并增加链接链、最终类型、相对／`..`、CLI 负向回归。
- `lifeos/engineering/LIFEOS-P3-094/README.md`：对齐唯一内部页面与完整目录链语义。
- `lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/`：新增 runner、README 和 Evidence。
- 本交付物。

attempt-1／2／3／4／5、P3-095、既有 PM Review 与全部 PM Evidence 均按只读资产核对；runner 前后 104 个历史文件 hash 一致。

## 测试与 Evidence

复跑命令：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/scripts/run_attempt_6.py
```

干净 `/private/tmp` 副本结果：**19 PASS / 0 FAIL**，退出码 0。核心覆盖：

- 唯一内部 render 路径、API 越界哨兵拒绝、CLI 输出能力移除；
- render 最终符号链接、目录、FIFO 拒绝且目标 hash、DB 均不变；
- render／clear 祖先目录链接链拒绝，真实页面 hash／存在状态和 DB 记录不变；
- 相对路径、`..`、规范化绕路与 DB 最终链接拒绝；
- 合法 render → clear 页面先失效 → DB 清空 → 重渲染失败；
- 页面失效注入失败时页面和 DB 不变；
- render 原子发布注入失败时旧页面 hash 和 DB 不变，临时半成品为零；
- 首次、幂等、跨进程复读、原子写入失败、损坏 DB fail-closed、禁止能力静态关闭；
- 15 项干净副本单元测试通过，运行前后 attempt-6 临时残留均为 0。

补充工具披露：一次 `python3 -m py_compile` 因 macOS Python 试图写入受限的用户缓存目录而返回权限错误；未写入项目或任务临时目录。随后使用不落盘的内置 `compile()` 对 runtime、CLI 与 attempt-6 runner 完成语法核对，结果 PASS；该工具限制不参与 19 项通过计数。

Evidence：

- Manifest：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/evidence/MANIFEST.md`
- 逐项结果：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/evidence/results.json`
- 哨兵／页面 hash：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/evidence/sentinel_hashes.json`
- 源码 hash：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/evidence/source_hashes.json`
- 历史只读 hash：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-6/evidence/historical_read_only_hashes.json`
- 日志与追溯矩阵：`test_run.log`、`operation_log.md`、`acceptance_matrix.md`、`rerun.md`

## 问题计数与未覆盖项

- P0：0（attempt-5 的两个 P0 在提交矩阵中均有正向与负向证据）
- P1：0
- P2：0
- Unknown：0
- Not Implemented：0
- 未覆盖项：并发恶意替换、真实磁盘故障和生产级耐久性不在本 attempt-6 任务卡范围；未把这些范围写成已验证。

本轮未生成新的 Chrome 动态／视觉 Evidence：D-0392 的唯一整改和强制回归是文件／DB 边界与干净副本工程矩阵，未要求变更今日页视觉或重新执行动态闭环；attempt-3 的历史动态 Evidence 保持只读，本轮不以其替代路径安全主证据。

## 角色与关卡

- 主责角色：技术架构负责人／Codex 工程执行。
- 协审视角：数据与来源、AI 信任与安全、PM 范围控制。
- Gate 2：执行侧窄范围通过；用户原文数据模型未改，拒绝路径 DB 内容保持不变，自动 Evidence 仅用固定非敏感文本。
- Gate 3：执行侧静态关闭态通过；未新增网络、云、AI、Tauri/IPC、Vault、导出或外部处理。
- Gate 4：执行侧窄范围通过；唯一页面、完整无链接目录链、最终文件类型、原子发布／先失效后清理均有回归。
- Gate 1：仅核对未扩大产品与 V1 范围；不构成新产品冻结。
- Gate 5：未覆盖真实用户价值验证。
- 尚需关卡：正式 PM 验收；PM Pass 与用户采纳后，必须由另一全新隔离会话完成独立复评。

## 风险、预检与 PM 决策

R-0051 继续保持 **P0 / Open**；本执行会话不关闭风险、不恢复工程基线、不冻结资产或 Schema/API、不进入 Stage 4。

本地模型预检按任务卡明确允许跳过：本轮涉及真实本地文件写入／删除与 DB 边界的 P0 高风险判断，本地模型不得替代人工工程反例和 PM 复核。

需要 PM 决策：Yes。请 PM 按当前 source hash、19 项 runner 与 Evidence Manifest 验收 attempt-6；本会话不自行启动独立复评或下一任务。
