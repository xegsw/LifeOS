# LIFEOS-P3-104｜三页 UI→本地 Runtime 与受控 Tauri/IPC 整合能力包交付

## 任务信息

- 任务 ID：`LIFEOS-P3-104`
- 当前状态：`Completed — Rework 1/2 Remediation PASS / Awaiting PM Re-review`
- 任务类型：P0 受控 UI／本地持久化／桌面 IPC 工程能力包
- 执行 Agent：Codex，新建隔离专项会话
- 主责：桌面 UI／本地 runtime／IPC 工程
- 协审检查点：技术架构、AI 信任安全、数据／领域、独立 QA、产品体验与可访问性
- 执行授权证据：用户于 `2026-08-23T12:28:01+0800` 将任务卡绝对路径投递到本专项会话；任务卡同时记录 D-0423、D-0424 和一次受控官方 Rust/Tauri bootstrap 授权。
- Frozen ABF：`lifeos/tasks/LIFEOS-P3-104_three_page_ui_local_runtime_tauri_ipc_integration_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-104-v1`
- ABF SHA-256：`2672adc56174f89088c95a7909f36307b3d51add0c6fc0a6fd84e6eb7ebf8d8b`
- ABF 启动前状态：已在任何工程动作前核对为 Frozen；标准质疑窗口未发现歧义。
- 正式 Rework：`1/2`（PM Review 已使用第 1 轮；本次为同一 Frozen ABF 下的整改提交）
- Rework 授权证据：用户于 `2026-08-23` 将 `lifeos/reviews/LIFEOS-P3-104_pm_review.md` 绝对路径投递到本专项会话；该 Review 明确授权在原任务、原 ABF 与原允许目录内执行 Rework 1/2。
- 需要 PM 决策：`Yes`，需对 Rework 1/2 做正式复验；执行侧不得自定 Accepted。

## 执行摘要

1. 在唯一允许目录 `lifeos/engineering/LIFEOS-P3-104/` 新建真实 Tauri 2 桌面候选，三页静态前端直接嵌入应用，无 npm、dev server、localhost 或远程资源。
2. Renderer 只调用 `capture_record`、`get_today`、`runtime_status`；Tauri capability 权限列表为空，未知 IPC 默认拒绝，严格请求 schema 拒绝 `path`／`sql`／`shell` 等额外字段。
3. Backend 独占固定 task-local SQLite 路径；固定非敏感 capture 支持首次 saved、同 key 同文本幂等、同 key 异文本 conflict、真实关闭重开恢复、审计和用户原文身份。
4. 保存采用 shadow candidate、完整校验和原子 rename；注入失败、sidecar、陈旧 shadow、symlink、hardlink、路径越界和内容篡改均 fail closed。
5. 真实 unsigned debug `.app` 通过 computer-use 完成 17 项逐行动作；首次、重复、冲突、失败、刷新、三页、未知 IPC、参数拒绝、Tab、Enter、宽窄窗口、reduced motion、关闭重开和清理全部 PASS。
6. 最终离线干净锁定重建 PASS；静态 44/44、Rust unit 6/6、动态 17/17、ABF 矩阵 12/12，P0/P1/P2/Unknown/Not Implemented 均为 0。
7. 历史 14 项只读资产与 Frozen ABF 哈希复核不变；retained pilot、真实个人数据和项目账本零访问／零修改；task-local 临时残留为 0。
8. PM 首轮验收发现 `PM-P3-104-CE-01`（dangling 最终 DB symlink 可被替换，P1）与 `PM-P3-104-EV-01`（缺少精确离线实际 `.app` bundle／回放入口，P2）；两项已在 Rework 1/2 内整改并通过执行侧复核。
9. Rework 后 `symlink_metadata`／lstat 明确区分缺失与 dangling 对象，最终 DB 及 `-journal`／`-wal`／`-shm` 均 fail closed；新增精确离线 `.app` runner 覆盖 clean bundle、首次启动、关闭重启、dangling 负向退出与清理。
10. Rework 权威结果：原静态套件 44/44、Rework 定向检查 19/19、Rust unit 7/7、实际 `.app` 离线回放 PASS；P0/P1/P2/Unknown/Not Implemented 均为 0，仍待 PM 正式复验。

## 事实、推断、建议与待确认

### 事实

- Rust `1.98.0`、Cargo `1.98.0`、Tauri CLI `2.11.4`、Tauri crate `2.11.5` 与全部直接依赖均精确锁定；`Cargo.lock` 含 438 包，哈希全程为 `430583c26b3104ff384c7ab539b0ebe79d90509a957701a2fb1ebd3b4c2026f1`。
- 依赖闭包完成后，所有编译、测试、runner 和应用 Evidence 均设置 `CARGO_NET_OFFLINE=true`；Cargo runner 使用 `--locked`，Tauri runner 使用 `-- --locked` 透传。
- SQLite 最终固定夹具为 1 条 `local_capture` 用户原文、1 条 `capture_saved`、1 条 `capture_repeat`，`quick_check=ok`、`user_version=104`；失败、冲突和 schema probes 未改变该状态。
- `lsof -nP -a -c lifeos-p3-104 -i` 在应用运行时返回无匹配 socket；CSP 无远程源、localhost 或通用网络入口。
- macOS Reduce Motion 初始为 off；验收时临时切为 on，实际 App 显示“系统已启用”，随后恢复为 off。
- 真实 App 退出并确认进程停止后重新启动，首屏从 backend 恢复 1 条记录与 2 条审计事件。

### 推断

- 在 Frozen 固定夹具、隔离 task-local DB 和本机 debug 配置范围内，候选满足 ABF 的失败关闭、数据主权、身份展示、权限最小化和可复核性原则。
- 此结论不外推到 retained pilot、真实个人输入、发布签名、多设备、同步、云服务或 Stage 4。

### 建议

- PM 按同一 Frozen ABF 对 Rework 1/2 候选做正式复验；若 Pass，再由用户作采纳决定，并创建全新隔离独立复评会话。
- PM 复验应优先复跑 `scripts/offline_actual_app_replay.sh`、`tests/rework_checks.py` 和 attempt-1 Manifest 校验，并核对首轮 Engineering／PM Evidence Manifest 未改变。

### 待确认

- 需 PM 确认：Rework 1/2 后候选是否正式 Pass。
- 需后续用户确认：PM Pass 后是否采纳，并授权全新隔离独立复评。
- 无产品定位、V1 范围、架构冻结、Schema/API 冻结、风险关闭或 Stage 4 请求。

## 实现范围

### 桌面壳与前端

- `tauri.conf.json`：本地嵌入三页资源、单窗口、最小宽度 360、无生产 bundle 声明、严格 CSP。
- `capabilities/main.json`：`permissions: []`；未启用 Tauri plugin。
- `ui/default-recovery.html`：固定非敏感明确保存、幂等、冲突与原子失败入口；today 显示用户原文／本地捕获／AI 未启用。
- `ui/no-reliable-suggestion.html`：同一 backend 状态；`选择 Project` 与 `记录停点` 只更新本地停点说明，不生成建议或新记录。
- `ui/restricted-offline.html`：显示 runtime 关闭态、实际未知 IPC 与额外字段 denial probes。
- `ui/styles.css`：继承三页视觉层级、响应式、skip link、可见 focus 和 `prefers-reduced-motion`。

### Backend 与 IPC

- `capture_record`：只接受 strict `{text,key}`；仅冻结文本／key；首次原子发布、重复审计、冲突拒绝、注入失败拒绝。
- `get_today`：只接受 strict 空对象；校验 schema、记录、审计和序列后返回最小 today 结构；身份固定为 `user_original`。
- `runtime_status`：只接受 strict 空对象；返回 offline、AI disabled、空 renderer capability、三项 allowlist、未知命令 deny 与全部外部能力关闭。
- 路径边界：仅 `/private/tmp/lifeos-p3-104-*` 的直接子文件 `capture.sqlite`；拒绝 lexical traversal、symlink、hardlink、sidecar 和 stale shadow。
- 原子边界：候选 DB 完整 copy／transaction／quick-check／合同校验后才 rename 发布；任何失败移除候选且不显示成功。

## 工具链与供应链

- 官方 bootstrap 详情：`lifeos/engineering/LIFEOS-P3-104/evidence/bootstrap_record.md`。
- `rustup-init.sh` SHA-256：`6c30b75a75b28a96fd913a037c8581b580080b6ee9b8169a3c0feb1af7fe8caf`。
- `cargo-tauri` SHA-256：`da2bd22945b356fa4d8e4d5b7eaab0b2e26df81b63d1a17a63b90d2f61c37ca7`。
- `rusqlite` 使用精确锁定的 `bundled` SQLite feature，已在 `Cargo.toml` 与 bootstrap record 披露。
- 诚实异常：一次并发 rustup 重试产生 component-cache rename 失败，后以同一官方 1.98.0 cargo component 修复并复核；官方 locked tauri-cli 含 yanked transitive `spin 0.9.8`；crates.io 出现可恢复 HTTP/2 错误；最终 fetch 静默后以 exit 130 中止，但完整性由随后无网干净编译全部 438 locked 包确认，未据 exit 130 冒充成功。

## 验收与 Evidence

### Rework 1/2 权威结果（当前候选）

| 类别 | 结果 | 权威 Evidence |
|---|---:|---|
| `PM-P3-104-CE-01` dangling DB／sidecar 关闭态 | PASS | `evidence/rework/attempt-1/results.json`、`cargo_test.log` |
| `PM-P3-104-EV-01` 精确离线实际 `.app` bundle／回放 | PASS | `evidence/rework/attempt-1/offline_actual_app_replay_pass.log` |
| 原静态边界回归 | 44/44 PASS | `evidence/rework/attempt-1/static_results.json` |
| Rework 定向静态检查 | 19/19 PASS | `evidence/rework/attempt-1/rework_results.json` |
| Rust runtime unit | 7/7 PASS | `evidence/rework/attempt-1/cargo_test.log` |
| Rework 文件哈希 | 16/16 校验 OK | `evidence/rework/attempt-1/MANIFEST.md` |

Rework 执行侧计数：P0 `0`、P1 `0`、P2 `0`、Unknown `0`、Not Implemented `0`。`cargo fmt --check` 因 Frozen 最小 Rust toolchain 未安装 `rustfmt` 而未执行；该项不是 ABF 验收项，未下载或扩大工具链，编译与 7 项 unit test 均通过。

### 首次提交历史结果（只读保全）

| 类别 | 结果 | 权威 Evidence |
|---|---:|---|
| Frozen ABF 矩阵 | 12/12 PASS | `evidence/abf_matrix.json` |
| 实际 App 动态闭环 | 17/17 PASS | `evidence/dynamic_closure.json`、`evidence/dynamic_closure_verification.json` |
| 静态边界 | 44/44 PASS | `evidence/static_results.json` |
| Rust runtime unit | 6/6 PASS | `evidence/offline_verify_final_clean_pass.log` |
| 锁清单 | 438/438 可离线解析 | `evidence/cargo_lock_inventory.json` |
| 历史／ABF 哈希 | 15/15 不变 | `evidence/frozen_hash_verification.log` |
| App network socket | 0 | `evidence/network_probe.log` |
| DB 最终状态 | 1 record / 2 audit / quick_check ok | `evidence/db_final_state_pass.log` |
| task-local 清理 | residual 0 | `evidence/cleanup.log` |
| 文件哈希 | 全部清单校验 OK | `evidence/MANIFEST.md` |

### 动态闭环计数

- PASS：17
- N/A：0
- NOT IMPLEMENTED：0
- P0：0
- P1：0
- P2：0
- Unknown：0

每行均含前置状态、实际操作、可观察结果、唯一结构化 ID、Evidence 路径及 SHA-256。刷新没有替代关闭重开；AX 暴露没有替代实际 Tab／Enter；所有截图均来自真实 Tauri `.app`，没有使用 Chrome、In-app Browser、HTTP 或 mock renderer。

## 复跑命令

```bash
cd /Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-104
scripts/offline_verify.sh
scripts/offline_actual_app_replay.sh
python3 tests/rework_checks.py
python3 tests/lock_inventory.py
python3 tests/verify_dynamic_closure.py
sed -n '/^```text$/,/^```$/p' evidence/MANIFEST.md | sed '1d;$d' | shasum -a 256 -c -
cd evidence/rework/attempt-1
sed -n '/^```text$/,/^```$/p' MANIFEST.md | sed '1d;$d' | shasum -a 256 -c -
```

`scripts/offline_verify.sh` 自行设置 task-local `CARGO_TARGET_DIR`、`CARGO_NET_OFFLINE=true`，执行原始静态与 Rust 回归。`scripts/offline_actual_app_replay.sh` 执行 task-local clean、精确 offline locked `.app` bundle、正常首次启动／关闭重启、dangling 最终 DB symlink 负向退出及精确清理；不会访问 retained pilot。

## 历史、隐私与关闭态

- P3-091 五项资产、attempt-2 Manifest、P3-092 Review、P3-093 交付／Review、P3-097 实现／CLI、P2-015 合同、P3-103 Review／Manifest 的 14 个哈希全部与 Frozen 值一致。
- 未访问 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1`；未读取、复制、迁移或清理 retained DB／页面；固定非敏感夹具之外真实数据为 0。
- clear、delete、export、generic path/read/write、raw SQL、shell、process、network、Vault、模型、同步、多设备、遥测、updater 和外部 URL 均未注册或不可达。
- R-0040、R-0052 继续 Open；R-0051 未扩大；本任务不改变任何风险、冻结或阶段结论。
- 工程仍为 `Not Frozen`；Gate 5 仅固定非敏感内部可用性检查，不构成 Gate 5 Pass 或 Stage 4 准入。

## 角色与关卡

- 桌面 UI／本地 runtime／IPC 工程：Rework 1/2 执行侧完成，包内自检 PASS。
- 技术架构检查点：三项 allowlist、strict schema、renderer 零 capability、CSP、无 network、SQLite 原子发布均有静态／动态证据。
- AI 信任安全检查点：AI 未启用；用户原文／本地捕获／系统状态清晰区分；无伪建议和重大行动。
- 数据／领域检查点：source、identity、idempotency、audit、restart today 一致；派生或真实数据未接入。
- 产品体验与可访问性检查点：三页、空态、失败披露、实际 Tab／Enter、focus、宽窄窗口、reduced motion 均有逐项 Evidence。
- Gate 1–4：Rework 执行侧所需工程证据已覆盖，仍待 PM 正式复验。
- Gate 5：只验证固定非敏感内部候选可用性；未宣称通过。
- 独立 QA：未由执行会话自证替代；PM Pass 与用户采纳后必须新建隔离会话复评。

## 异常日志说明

- `evidence/offline_verify.log`：首次 Tauri runner 将 `--locked` 放在 CLI 选项位置而失败；已改为 `-- --locked`。
- `evidence/offline_verify_final_clean.log`：Tauri CLI 规范化空 features 后，旧静态字符串断言产生 1 个假阴性；runner 改为核验规范化后的同一精确版本表达，最终干净日志 PASS。
- `evidence/db_final_state.log`：首次诊断查询错误假定 DB 存在 identity 列；实现合同实际在 today response 中派生 identity。后续只读查询按冻结 schema 修正，`db_final_state_pass.log` PASS。
- 上述失败均保留，不覆盖为成功；最终权威通过日志和对应 Manifest 哈希独立存在。

## 完成定义与后续边界

- 执行侧 Rework 1/2 完成定义：满足。没有未覆盖项或 N/A。
- PM 首轮正式验收：结论为 Rework；`PM-P3-104-CE-01` 与 `PM-P3-104-EV-01` 已整改。
- PM Rework 复验：未执行，需 PM 主会话决定。
- 用户采纳：未执行，必须在 PM Pass 后单独决定。
- 全新隔离独立复评：未启动，必须在 PM Pass 与用户采纳后执行。
- 不自动启用 retained 数据，不创建下一任务，不修改项目账本，不冻结任何资产，不关闭任何风险，不进入 Stage 4。
