# P3-150 健康只读展示与历史趋势

状态：工程、合成验证及真实只读启动完成；等待 PM 验收及用户自行查看。主责 Codex 工程，复用原任务会话；P3-149 已结束并保持只读。L3 独立评审依用户指示暂停，不宣称 Independent Pass、安全风险关闭、产品冻结或 Stage 切换。

## 交付结果

独立 App 的“我”页面展示已导入的睡眠区间、步数、Apple 运动时间，支持 7/30/90 天和截至日期筛选、来源名称组及 offset 选择、每日明细、观察时间和最近成功导入时间。默认截至该指标最近有数据的一天，空范围可以返回最近记录。多来源分别查看，null/缺失保持断点，合法零值保留；估算明确说明。原始观察中尚未形成日投影的内容不绘制趋势。

保留 116 Shell / Rail 与 142 设置基础样式。Today/Contexts/Memory 禁用，Settings 只解释本模式；不提供写入、导入、导出、AI 或网络入口。运行模块只编译专用只读 Reader、严格 JSON 解析和一个 get_today 命令；复制候选中的历史模块不参与该入口编译。

唯一真实目标和授权见任务卡。真实数据只由本机 App 读取展示，Agent 不读取行值、不抓真实界面、不对真实库或内容做 hash。无重新导入、迁移、复制真实库或修改 journal 模式。

## 合同与实现边界

Task Contract：`/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/tasks/LIFEOS-P3-150_health_import_readonly_view.md`；包内副本 `contract-inputs/task.md`。PM 已确认 get_today 的专用 v2 health_view DTO，设计见 `design/readonly-contract.md`。本卡是 PM 下发的完整结果合同；未另行新建 ABF，也不声称 Frozen ABF。

- DTO 使用原始 UTF-8，最多 4096 字节；拒绝 JSON fallback、重复键、未知字段、旧版本/旧操作、非法指标/日数/日期/offset 和单边来源参数。
- 查询参数化；来源+offset 完全匹配，未知组不回退。来源最多 32 项/页，稳定二进制排序；最多 90 个日点、128 KiB 响应；SQLite 查询合计设置 3 秒 progress deadline 和 150ms busy timeout。后台线程执行，UI 显示加载/失败，旧请求结果不能覆盖新选择。
- 固定目标按目录组件 O_NOFOLLOW 验证；持有目录/文件 fd，检查 UID、0700/0600、单链接和 inode/时间戳。每次查询前后验证，文件变化即拒绝。SQLite 仅 READ_ONLY/NOFOLLOW + query_only，不运行通用仓储初始化。
- 保守拒绝 WAL 格式及已有 wal/shm/journal 旁文件；不尝试修复。使用非持久 WebView；启动预查成功后才创建窗口，stdout 只有固定状态和错误码，其余输出及 core dump 禁用。
- 当前查看期间若外部修改数据库，需重新打开查看器。来源名称组并不证明独立设备，覆盖范围未知，观察不作为医学结论。

## Acceptance Evidence

所有路径以下均相对 `/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-150/`。

| ID | 结果与证据 |
|---|---|
| A1 | 三指标 × 7/30/90 Rust 查询通过；实际窗口正常、未来空范围、返回最近数据和 busy 错误/恢复。`evidence/rust-tests.log`、`empty-range.*`、`readonly-busy-error.*`、`exercise-90-confirmed.*` |
| A2 | null/缺失断点、真实零、offset 隔离、未知来源、重复投影拒绝通过。前端 9 断言，Rust 有针对性负例；`narrow-sleep-30-confirmed.*`、`daily-details.*` |
| A3 | 自建 250000 条合成观察；查询只传有界投影和 32 来源/页。大库窗口、稳定分页、deadline/busy 检查通过。`tools/create_synthetic.py`、Rust large_fixture_bounded 等 |
| A4 | 数据库写入/DDL 失败，退出/重开数据库完整字节及旁文件保持不变；live busy 错误可恢复。`evidence/lifecycle.json`。仅一个已注册读命令由静态入口审计证明；未宣称对所有历史 IPC 逐个进行了实时攻击。`static-boundaries.json` |
| A5 | actual Tauri 直接 PID 11766、重启 PID 13093，绑定精确窗口名、AXWebArea 与 CG 窗口；1280×949 和 700×760 正常。CUA Tab/空格实际切换指标并进入 Settings；日期输入与明细滚动可达。`gui-checks.json`、`keyboard-metric-confirmed.*`。四个基础 CSS 与149候选完全相同 |
| A6 | 固定真实只读启动成功：`readonly_view_started / real`，PID 13316。`evidence/real-launch.json` 仅含进程/构建身份和固定状态；启动后未抓窗口或读取行值。用户亲验仍待确认 |
| A7 | 本报告、检查点、差异 Manifest、最终 Manifest 与合成复跑入口齐备。旧149七份 Manifest 的 161/129/188/135/131/137/139 项全部原样复算通过；不操作旧进程。`history-preservation.json` |

Rust 16/16 通过；前端 9/9 断言通过。检查属于当前合同受影响范围，不代替历史全套回归或独立评审。工程自检 P0=0、P1=0、P2=0、Unknown=0、Not Implemented=0；真实启动成功，用户亲验为独立待确认项，不伪装验收完成。

## 实际窗口证据说明

初始 AXWebArea 尚未就绪时未采图，后续同一 PID 就绪后补取。一次 CG 边界比 AX 多 1 像素，截图绑定加入最多 1 像素的边缘取整容差，仍要求精确 PID/标题和唯一尺寸匹配；原始两种 geometry 均保留。未截取其他 App。

部分操作后过早抓取未确认新筛选，相关标签在 `gui-checks.json` 中明确排除，不作为正证据。后续 `*-confirmed` 的 AX 筛选值与日期范围一致。早期 Swift 键盘尝试未确认焦点，改用 CUA 完成真实 Tab/空格操作，不把发出按键视为验证通过。

## 复跑与运行

`tools/rerun.sh` 只运行合成 Rust/前端测试与历史完整性校验，不启动真实 App、不访问真实库。要求已有本任务 0700 临时根和正确 0600 marker；新环境按 `tools/create_synthetic.py` 构建合成库，文件存在时拒绝覆盖。

`tools/launch.py synthetic|real` 从对应离线构建目录创建独立 App；已有包拒绝覆盖。构建须显式 `LIFEOS_P3_150_MODE=synthetic|real`，`cargo build --locked --offline`，target 和 TMPDIR 位于本任务临时根。真实运行必须沿用当前授权固定目标，不能将其作为无人值守 CI。`capture_synthetic.py` 在 real-launch receipt 出现后拒绝执行。

App 根 `/private/tmp/lifeos-p3-150-health-view-v1/`。合成包 `LifeOS P3-150 Synthetic.app`；真实包 `LifeOS P3-150 Real.app`（已启动并保留给用户）。保留本任务构建和合成证据以支持复核；不删除历史或真实资产。

## PM 与用户检查点

PM 需要验收 A1–A7 和本任务结果。用户只需在真实只读窗口自行确认显示符合预期，无需将健康数值、来源或截图发送给 Agent。用户亲验前不标记 User Accepted。独立评审仍按原用户决定暂停，无后继任务或自动提交/推送/合并。
