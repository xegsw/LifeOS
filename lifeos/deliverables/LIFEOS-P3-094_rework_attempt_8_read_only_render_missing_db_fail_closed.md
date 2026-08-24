# LIFEOS-P3-094 Rework attempt-8｜Render 严格只读与缺失 DB 旧页面 fail-closed 交付物

## 任务信息与授权

- 任务 ID：LIFEOS-P3-094（Rework attempt-8）
- 任务类型：受控真实本地能力包 P1 窄整改
- 任务卡完整路径：`/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-094_real_local_capture_persistence_today_view_controlled_capability_package.md`
- 执行授权证据：用户于 **2026-08-22 19:56:40 CST (+0800)** 将上述任务卡投递至本会话；D-0396 规定本次投递即授权 attempt-8。
- 会话类型：复用已结束 attempt-7 的 Codex 工程执行会话；上一任务已完成，本会话未承担 P3-095 独立评审。
- 实际模型与推理强度：`gpt-5.6-terra` + `high`（最新 `CURRENT_STATUS.md` 实际模型路由）；未降级。
- D-0396 范围：仅修复 DB 完全缺失时旧页面失效，以及 render 使用严格只读、禁止创建和禁止 Schema 初始化／补写的数据库读取路径；完整保留 attempt-6／7 已成立边界。

## 整改结论

**执行侧包内自检通过，提交 PM 验收。** capture/list 的既有写入入口和 Schema 初始化语义未变；render 改用独立严格只读读取器：

1. 路径门先逐级、不跟随链接地打开完整父目录链，并验证唯一内部 `today.html` 的最终文件类型。
2. 对 render，安全父目录和页面已确认但 DB 文件缺失时，路径门返回“DB 不存在”状态；render 先精确失效旧页面，再返回失败，不调用 SQLite、不创建 DB 或副文件。
3. DB 存在时，render 使用 SQLite URI `mode=ro&immutable=1` 和连接级 `query_only`；不调用 `_connect()`，不执行 `SCHEMA`，不创建或补写表、索引、trigger、journal、WAL 或其他副文件。
4. 只读读取器要求 `captures`、`audit` 均为表，并核对两表的必需列名与类型；零字节、无必需 Schema、单表部分 Schema、双表均存在但缺列、损坏、不可读或查询失败全部 fail closed。
5. DB 内容无法确认时继续复用 attempt-7 的旧页面失效和失效失败披露；render 不修改 DB bytes、大小、hash、对象清单或捕获／审计记录。
6. 合法非空 DB render 继续原子发布；发布失败保留当前有效页面且无半成品；clear 继续先失效页面再清理 DB。

## 修改范围

- `lifeos/engineering/LIFEOS-P3-094/src/local_capture.py`：新增 render 严格只读读取器、Schema 最小完整性核对和缺失 DB 页面失效路径。
- `lifeos/engineering/LIFEOS-P3-094/tests/test_runtime.py`：新增缺失 DB、零字节、无 Schema、部分 Schema 与双表缺列回归。
- `lifeos/engineering/LIFEOS-P3-094/README.md`：对齐严格只读 render 语义。
- `lifeos/engineering/LIFEOS-P3-094/rework/attempt-8/`：新增 runner、README 与 Evidence。
- 本交付物。

CLI 未修改。attempt-1 至 attempt-7、P3-095、PM Review 与全部 PM Evidence 均只读；runner 前后 **155 个历史文件 hash 一致**。

## 干净副本自检与 Evidence

复跑命令：

```bash
python3 -B lifeos/engineering/LIFEOS-P3-094/rework/attempt-8/scripts/run_attempt_8.py
```

attempt-8 结构化结果：**18 PASS / 0 FAIL**，退出码 0：

- DB 缺失 + 旧页面：render 失败，旧页面不存在；DB 与 SQLite 副文件均未创建。
- 零字节 DB：页面失效；DB 保持 0 bytes，SHA-256 与对象清单前后一致，无副文件。
- 仅含无关表：页面失效；DB bytes／大小／hash 与对象清单不变。
- 仅含 captures 的部分 Schema：页面失效；DB 与对象清单不变。
- captures／audit 均存在但必需列不完整：页面失效；DB 与两个对象定义不变。
- 已初始化空 DB、损坏 DB、权限不可读 DB、注入查询失败：attempt-7 合同继续成立。
- 缺失 DB 下页面失效失败注入：明确阻断；页面 hash 不变，DB 未创建。
- 合法非空 DB render：成功；DB bytes、对象清单和记录计数不变。
- 原子发布失败：当前有效页面 hash 和 DB 不变，半成品为零。
- clear：继续先失效页面，再清空 captures。
- attempt-6 完整边界回归：**19 PASS / 0 FAIL**。
- 当前干净副本单元：**22 tests / OK**。
- 内置 `compile()`：3 个文件 PASS；全程 `python3 -B`，`__pycache__` 为零，未尝试用户缓存目录。
- `/private/tmp` 中 `lifeos-p3-094-*` 运行前后残留均为零。

Evidence：

- Manifest：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-8/evidence/MANIFEST.md`
- 逐项结果：`lifeos/engineering/LIFEOS-P3-094/rework/attempt-8/evidence/results.json`
- DB bytes／大小／hash、SQLite 对象清单与页面状态：`read_only_db_states.json`
- attempt-6 全回归：`attempt6_regression_results.json`
- 源码／历史资产 hash：`source_hashes.json`、`historical_read_only_hashes.json`
- 日志、复跑与追溯：`test_run.log`、`operation_log.md`、`rerun.md`、`acceptance_matrix.md`

## 问题计数与未覆盖项

- P0：0
- P1：0（D-0395 的 DB 缺失旧页与失败 render 初始化 SQLite 两个 P1 均有针对性证据）
- P2：0
- Unknown：0
- Not Implemented：0
- 未覆盖项：并发恶意目录替换、外部写进程、真实磁盘硬件故障和生产级耐久性不在 D-0396 窄范围；未外推为已验证。

本轮未生成 Chrome 动态／视觉 Evidence：整改对象是 render 的数据库打开模式、SQLite 对象不变性和本地页面失效，不修改页面视觉或交互；文件状态、hash、对象清单和错误回执为主证据。历史 Chrome Evidence 保持只读。

## 角色、关卡与边界

- 主责角色：技术架构负责人／Codex 工程执行。
- 协审视角：数据与来源、AI 信任与安全、PM 范围控制。
- Gate 2：执行侧窄范围通过；失败 render 不创建／补写 DB 或 Schema，现有 DB bytes、对象和记录不变。
- Gate 3：执行侧静态关闭态通过；未新增网络、云、AI、Tauri/IPC、Vault、导出或外部处理。
- Gate 4：执行侧窄范围通过；缺失、零字节、无／部分 Schema 和 attempt-7 全失败矩阵均有回归。
- Gate 1：仅核对未扩大产品与 V1 范围；不构成冻结。
- Gate 5：未覆盖真实用户价值验证。
- 尚需关卡：正式 PM 验收；PM Pass 与用户采纳后，仍须另一全新隔离会话完成独立复评。

本轮未读取真实个人文件、既有个人 DB、真实用户文本、凭据或外部目标；未联网。R-0051 继续保持 **P0 / Open**；不关闭风险、不恢复工程基线、不冻结资产或 Schema/API、不创建独立复评、不进入 Stage 4。

本地模型预检按任务卡跳过：本轮涉及真实本地页面与 DB 生命周期的高风险判断，本地模型不得替代人工反例和 PM 复核。

## 需要 PM 决策

请 PM 按当前 source hash、18 项 attempt-8 结果、attempt-6 19 项全回归和 Evidence Manifest 验收。本执行会话不自行启动独立复评或下一任务。
