# LIFEOS-P3-106 三张冻结 Stitch 页面高保真 Tauri UI／路径合同后继任务报告

## 任务信息

- 任务 ID：LIFEOS-P3-106
- 执行 Agent：Codex 工程执行专项会话
- 当前状态：**Blocked — Acceptance Not Met candidate；需 PM 确认**
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_acceptance_basis_freeze.md`
- ABF ID：`ABF-P3-106-v1`
- 启动前 ABF SHA-256：`1aa076a289173eb0dbd4e17ccfd3a1af89cbd9f815ad656d31d9318a5172a5c4`
- 正式 Rework：0 / 2
- 执行授权证据：用户于 2026-08-23 将本任务卡绝对路径投递到新的 Codex 工程执行专项会话；按 D-0319 构成任务卡窄范围执行授权。

## 结论先行

本轮已在全新 `lifeos/engineering/LIFEOS-P3-106/` 中完成三页真实 HTML/CSS/JS 与不可变 P3-104 Tauri/runtime 的整合，离线 locked unit test 为 7/7 PASS，真实 `.app` 可完成三页导航、本地 capture、幂等重复、冲突阻断、注入失败、刷新、关闭重开、未实现入口披露、unknown IPC／额外字段拒绝、实际键盘焦点、窄窗和 reduced-motion。四类 dangling、父目录链接与篡改读取也得到 fail-closed 结果；本轮创建的八个精确 `/private/tmp` 夹具已全部清理，旧 temp metadata 未变。

但 ABF-M-004 至 M-006 要求三张**真实 app 1280×1024 全画布**。当前本机逻辑显示工作区将 1280×1024 Tauri 窗口夹紧为 1160×768；Computer Use 取得的三张实际截图均为 1160×768。执行侧没有缩放、补边、拼接、浏览器替代、DOM 截图或 mock 冒充 1280×1024。因此三行均为 BLOCKED，ABF Pass 公式不成立。按任务卡停止条件，本轮不提交 PM Pass 候选。

## 事实、推断、建议与待确认

### 事实

- 启动前固定输入 22/22 hash 与 ABF hash 匹配；P3-104 `Cargo.toml`、`Cargo.lock`、`src/main.rs`、`src/runtime.rs`、`capabilities/main.json` 在 P3-106 中保持字节一致。
- `write_path_inventory.json` 在任何复制、构建或测试前创建；runtime unit 路径名静态枚举与 ABF 一致。
- `python3 tests/verify_preflight.py`：39/39 PASS。
- `CARGO_NET_OFFLINE=true ... cargo test --locked`：7/7 PASS；离线 build 与 Tauri debug app bundle 成功。
- 真实 app 的默认、无可靠建议、权限受限／离线三页均可导航；实际截图源是构建后的 Tauri `.app`，不是浏览器或 file/HTTP 页面。
- dangling final、journal、wal、shm 四个独立夹具均以非零退出 fail-closed；链接、缺失 target 和 sentinel 保持不变。
- 篡改内容在启动后的自动 `get_today` 读取中显示“backend 拒绝读取；未展示缓存或部分记录”与“启动读取失败；未显示缓存成功态”。
- reduced-motion 临时开启后，重启 app 的诊断面板报告“系统已启用”；系统设置随后恢复为原先关闭状态。
- 清理台账列出的八个精确夹具残留为 0；`/private/tmp/lifeos-p3-104-rework-static-results.json` 的 size、mtime、ctime 未变。
- 三张要求截图的实际尺寸均为 1160×768，详见 `evidence/visual_environment_constraint.json`。

### 推断

- 视觉尺寸失败来自当前逻辑显示工作区对窗口的系统级夹紧，不是 Tauri 配置缺少 1280×1024；静态配置仍声明 1280×1024。
- 若允许临时切换到可容纳 1280×1024 客户区的显示缩放并在完成后恢复，可能在不改 runtime、IPC、依赖或 ABF 的前提下补齐三张真实全画布；该动作尚未获独立明确授权，也尚未验证可行。

### 建议

- PM 先确认本轮 `Blocked — Acceptance Not Met` 候选，不得 Accepted、Frozen、关闭风险或进入 Stage 4。
- 如用户愿意继续同任务包内整改，需先明确授权临时改变并恢复本机显示缩放；随后必须从空 Evidence／全新精确夹具重跑全部 18 行，而不是只补三张图。

### 待确认

- 是否允许执行侧临时修改本机显示缩放以获得真实 1280×1024 app 画布，并在取证后恢复原设置？

## 修改范围

- 新建工程：`lifeos/engineering/LIFEOS-P3-106/`
- 新建 UI：三页 HTML、共享 CSS、Tauri IPC 绑定 JS。
- 新建／调整 P3-106 runner、路径验证、清理与阻塞态 Manifest。
- 新建本报告。

未修改 P3-104、P3-105、任务卡、ABF、项目账本、风险、冻结状态或历史 Evidence。未读取 retained pilot，未联网、安装依赖、启用远程资源、扩充 IPC/capability、访问真实数据或外部目标。

## 自检与关卡

- P0：0 个已知问题。
- P1：3 个（ABF-M-004、M-005、M-006 的 1280×1024 全画布均未成立）。
- P2：0。
- Unknown：0；失败尺寸已精确测得并留存。
- Not Implemented：10 个矩阵行仍未形成可提交的完整逐动作／side-by-side／clean replay Evidence（M007–M013、M015、M017、M018）；这是命中停止条件后的诚实未完成状态，不得批量继承观察结果为 PASS。
- 体验、技术架构、数据、AI 信任安全、独立 QA 检查点：执行侧完成静态与局部动态自检；PM 验收未开始，独立复评不得由本会话启动。
- 风险／冻结／阶段：R-0040、R-0052 应继续 Open；R-0051 不变；Not Frozen；未进入 Stage 4。

## Evidence

- Blocked Manifest：`lifeos/engineering/LIFEOS-P3-106/evidence/MANIFEST.md`
- 视觉环境约束：`lifeos/engineering/LIFEOS-P3-106/evidence/visual_environment_constraint.json`
- 固定输入与静态结果：`lifeos/engineering/LIFEOS-P3-106/evidence/fixed_input_hashes.json`、`static_results.json`
- 构建与测试：`cargo_test.log`、`cargo_build.log`、`cargo_tauri_bundle.log`
- 真实 app 截图：`lifeos/engineering/LIFEOS-P3-106/evidence/screenshots/`
- 负向实际二进制结果：`lifeos/engineering/LIFEOS-P3-106/evidence/negative_actual_results.json`
- 精确清理结果：`lifeos/engineering/LIFEOS-P3-106/evidence/cleanup_results.json`
- Local Precheck：`lifeos/local_prechecks/LIFEOS-P3-106_LIFEOS-P3-106_three_frozen_stitch_pages_high_fidelity_tauri_ui_path_contract_successor_local_precheck.md`（Local Model Unavailable，按规则跳过，不阻塞本报告）

注意：`negative_actual_results.json` 中 tamper 的“进程启动即退出”探针诚实记录为 timeout；随后真实 UI 自动读取证明 fail-closed，截图为 `actual-tamper-failclosed.jpg`。两项不能互相替换，也未将前者改写成 PASS。

## PM 处理建议

本报告仅提交 PM 判断。建议结论为 `Blocked — Acceptance Not Met`，除非用户另行明确授权临时显示缩放并由执行侧完成全量干净复跑。不得基于现有 1160×768 截图豁免或追溯修改 ABF，也不得把真实 app 可运行等同于本任务 Accepted。
