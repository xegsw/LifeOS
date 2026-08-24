# LIFEOS-P3-094 Rework attempt-7｜旧页面 fail-closed P1 整改交付物

## 任务信息与授权

- 任务 ID：LIFEOS-P3-094（Rework attempt-7）
- 任务类型：受控真实本地能力包 P1 窄整改
- 任务卡完整路径：`/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-094_real_local_capture_persistence_today_view_controlled_capability_package.md`
- 执行授权证据：用户将上述任务卡投递至本会话；接收记录时间为 **2026-08-22 19:39:14 CST (+0800)**。任务卡 D-0394 明确规定本次投递即授权 attempt-7。
- 会话类型：复用已结束 attempt-6 的 Codex 工程执行会话；上一任务已完成，本会话未承担 P3-095 独立评审。
- 实际模型与推理强度：`gpt-5.6-terra` + `high`（最新 `CURRENT_STATUS.md` 实际模型路由）；未降级。
- D-0394 范围：仅修复空、损坏、不可读或查询失败 DB 下 render 失败仍保留可展示旧页面的问题；保留 attempt-6 路径边界、合法发布、原子失败与 clear 既有语义；补固定非敏感回归、接收时间和缓存卫生。

## 整改结论

**执行侧包内自检通过，提交 PM 验收。** render 在唯一内部页面与完整目录链边界验证通过后，如无法确认 DB 内容有效，会复用同一个基于已打开目录句柄、不跟随链接的页面失效函数，使 `db_path.parent / "today.html"` 不可展示，然后返回原 DB 读取失败。

具体行为：

1. `list_today()` 因损坏、不可读或查询错误抛出 `CaptureError` 时，render 先精确失效既有内部页面，再返回失败。
2. DB 有效但 captures 为空时，render 先失效旧页面，再返回“没有可展示记录”的明确失败。
3. 旧页面失效本身失败时，render 返回“数据库内容无法确认，且既有今日页无法失效”的明确阻断；不报告成功，也不修改 DB。
4. render 仅在 DB 非空且可完整读取后进入 HTML 构造和原子发布，因此原子发布失败仍保留当前有效页面，临时半成品为零。
5. clear 继续使用同一页面失效函数，保持“先页面失效、后 SQLite 清理”的顺序。

事实：本轮未修改 capture/list 数据模型、SQLite Schema/API、今日页视觉内容或 CLI 能力；未重新接受调用方输出路径，未改变 attempt-6 的完整无链接目录链、规范化路径、DB／页面最终类型门。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-094/src/local_capture.py`：新增 render DB 失败前的旧页面失效与失效失败披露。
- `lifeos/engineering/LIFEOS-P3-094/tests/test_runtime.py`：新增空／损坏／查询失败旧页面和失效失败注入回归。
- `lifeos/engineering/LIFEOS-P3-094/README.md`：补充 render 失败时旧页面生命周期口径。
- `lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/`：新增 runner、README 与 Evidence。
- 本交付物。

CLI 文件未发生实质修改，仅纳入当前 source hash 和 attempt-6 回归。attempt-1 至 attempt-6、P3-095、PM Review 与全部 PM Evidence 均为只读；runner 前后 **128 个历史文件 hash 一致**。

## 干净副本自检与 Evidence

复跑命令：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/scripts/run_attempt_7.py
```

attempt-7 结构化结果：**13 PASS / 0 FAIL**，退出码 0；其中：

- 空 DB + 旧页面：render 失败，页面由存在变为不存在；capture=0、audit=1、DB SHA-256 前后一致。
- 损坏 DB + 旧页面：render 失败，旧页面不存在；损坏 DB bytes、大小和 SHA-256 前后一致。
- 权限不可读 DB + 旧页面：`mode=0o0` 时 render 失败并失效页面；DB bytes hash 不变，测试后仅恢复夹具原权限以便精确清理。
- 注入查询失败 + 旧页面：render 失败并失效页面；capture、audit 和 DB SHA-256 前后一致。
- 注入旧页面失效失败：render 明确阻断；旧页面存在状态／SHA-256 与 DB 状态／SHA-256 前后一致。
- 合法非空 DB render：成功，DB 状态与 SHA-256 不变。
- 原子发布失败：当前有效页面 hash 与 DB 状态不变，临时半成品为零。
- clear：页面先失效，随后 capture 清零并返回成功。
- attempt-6 外置全矩阵：**19 PASS / 0 FAIL**，覆盖 render／clear 越界目标、最终链接、祖先目录链接链、相对／`..`、最终文件类型、首次、幂等、跨进程、原子失败和禁止能力关闭态。
- 当前干净副本单元测试：**19 tests / OK**。
- 内置 `compile()` 语法检查：3 个文件 PASS；全程 `python3 -B`，未调用 `py_compile`，未尝试用户缓存目录，`__pycache__` 为零。
- `/private/tmp` 中 `lifeos-p3-094-*` 运行前后残留均为零。

Evidence：

- Manifest：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/evidence/MANIFEST.md`
- 逐项结果：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/evidence/results.json`
- 旧页面与 DB 前后状态／hash：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/evidence/stale_page_states.json`
- attempt-6 全回归结果：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-7/evidence/attempt6_regression_results.json`
- 源码与历史资产 hash：`source_hashes.json`、`historical_read_only_hashes.json`
- 日志、复跑与追溯：`test_run.log`、`operation_log.md`、`rerun.md`、`acceptance_matrix.md`

## 问题计数与未覆盖项

- P0：0
- P1：0（D-0393 旧页面生命周期 P1 已有四类 DB 失败正向证据和失效失败负向证据）
- P2：0（精确接收时间已记录；未尝试用户缓存目录）
- Unknown：0
- Not Implemented：0
- 未覆盖项：并发恶意目录替换、真实磁盘硬件故障与生产级耐久性不在 D-0394 窄范围；未外推为已验证。

本轮未生成新的 Chrome 动态／视觉 Evidence：任务只整改 render 失败时的本地文件生命周期与 DB 不变性，未修改页面视觉或交互；逐项文件存在状态、hash、DB 状态和异常回执是本轮主证据。attempt-3 的历史 Chrome Evidence 保持只读。

## 角色、关卡与边界

- 主责角色：技术架构负责人／Codex 工程执行。
- 协审视角：数据与来源、AI 信任与安全、PM 范围控制。
- Gate 2：执行侧窄范围通过；失败 render 不修改 captures、audit 或 DB bytes，固定非敏感 Evidence 不含用户原文。
- Gate 3：执行侧静态关闭态通过；未新增网络、云、AI、Tauri/IPC、Vault、导出或外部处理。
- Gate 4：执行侧窄范围通过；四类 DB 无法确认状态、失效失败、合法发布、原子发布失败和 clear 顺序均有回归。
- Gate 1：仅核对未扩大产品与 V1 范围；不构成冻结。
- Gate 5：未覆盖真实用户价值验证。
- 尚需关卡：正式 PM 验收；PM Pass 与用户采纳后，仍须另一全新隔离会话完成独立复评。

本轮未读取真实个人文件、既有个人 DB、真实用户文本、凭据或外部目标；未联网。R-0051 继续保持 **P0 / Open**；不关闭风险、不恢复工程基线、不冻结资产或 Schema/API、不创建独立复评、不进入 Stage 4。

本地模型预检按任务卡跳过：本轮涉及真实本地页面与 DB 生命周期的高风险判断，本地模型不得替代人工反例和 PM 复核。

## 需要 PM 决策

请 PM 按当前 source hash、13 项 attempt-7 结果、attempt-6 19 项全回归和 Evidence Manifest 验收。本执行会话不自行启动独立复评或下一任务。
