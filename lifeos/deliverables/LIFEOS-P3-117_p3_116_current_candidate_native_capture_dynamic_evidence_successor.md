# LIFEOS-P3-117｜P3-116 当前候选隔离原生截图动态 Evidence 后继收口：执行报告

## 任务信息

- 任务 ID：`LIFEOS-P3-117`
- 任务名称：P3-116 当前候选隔离原生截图动态 Evidence 后继收口
- 执行 Agent：Codex
- 当前状态：**Blocked**
- 需要 PM 决策：**Yes**
- 任务类型：P0 受控 Evidence／隐私边界能力包；仅限 P3-116 当前候选的只读取证，不是产品实现、冻结、风险关闭或阶段准入。
- Acceptance Basis Freeze 路径：`lifeos/tasks/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor_acceptance_basis_freeze.md`
- ABF ID／版本／SHA-256：`ABF-P3-117-v1`／`57d6016e338103f4f53b5e979d3ec2d5eca708e7622ade33c3ccfd8be1c2b0e0`
- ABF 是否在工程动作前核对为 Frozen：Yes；文件哈希与任务卡冻结值一致。
- 是否在启动前发现验收依据歧义：启动前未识别；交付前复核发现 ABF 内部固定输入哈希与当前只读 PM Review 不一致，见“阻塞或异常”。该遗漏不应被表述为通过。
- 当前正式 Rework 次数／上限：`0/2`；本报告不是 Rework 结论，亦不改变计数。
- 模型／推理强度：任务卡要求 `gpt-5.6-terra + xhigh`；当前执行接口未提供可独立保存的实际模型标签，故实际配置为 **Unknown**。未使用或请求降级／后备模型。
- 交付物篇幅是否在建议范围内：Yes。

## 执行摘要

1. 已按投递授权读取最小启动包、P3-117 任务卡／ABF、动态 Evidence 模板、P3-116 的定向历史输入及要求的高风险治理章节；P3-116、账本、风险、冻结、Pilot 与工程目录均未写入。
2. ABF 文件与任务卡本身的 SHA-256 均匹配；P3-116 八项候选／合同、两个停止 Manifest、attempt-2 assessment 和治理文件的实测哈希均与 ABF 固定值一致。P3-116 PM Review 的当前实测 SHA-256 为 `09d810885f72b3d58e12487acfa754fda9c56380f74e39f8d8deaf5eb022f8aa`，与 ABF 表中的固定值不一致。
3. 在最初一次预检中，唯一临时根曾创建只读副本和离线、无存储的 P3-117 probe；复制前八项候选／合同未漂移，probe 仅进入临时副本。交付前发现 runner 错将当前 PM Review 哈希写为预期值；已改为 ABF 的真实固定值并复跑，准确的 fail-closed 预检为 `BLOCKED_ABF_FIXED_INPUT_MISMATCH`，且该复跑未创建临时根。此纠正不把先前静态复制记录升级为有效通过 Evidence。
4. 按冻结的 `open -na`、新 profile、单一 `file:` app-mode 参数实际启动 Chrome 后，Computer Use 的 Google Chrome 选择器却返回一个既有普通 Chrome 窗口，而不是唯一的 P3-117 app-mode 窗口。显示的 URL 不是临时候选精确 `file:` URL，且普通窗口带有现有浏览器界面与既有标签组元数据。
5. 这同时触发 ABF-I-02／I-03 及任务卡的立即停止条件。未对该窗口点击、输入、导航、截屏、导出或摘录任何现有浏览器内容；没有写入 raw／proof／clean 图、geometry、动作闭环、AX/browser export 或动态结果。
6. 进程核验仅确认一个带精确临时 profile 与精确 app URL 参数的独立 P3-117 Chrome 主进程曾启动；它不能证明 Computer Use 可唯一、安全地识别并操作该窗口。为避免接触现有 Chrome，会话只终止该已核验的独立进程，随后核验同一临时 profile 已无存活进程。
7. 进一步复核发现 Frozen ABF 的固定输入表列出 P3-116 PM Review 哈希 `f698ade8695fc966034031129d271f25fcb35f2dd714acd3ba85a04cb3acef0d`，但当前只读文件为上述 `09d810…f8aa`。ABF 文件自身哈希仍匹配，因此这是 ABF 内部固定输入与现行历史资产的冲突；不能以本任务脚本中的当前值覆盖或修正冻结依据。
8. 精确清理已完成：唯一 `/private/tmp/lifeos-p3-117-native-capture-v1` 根、临时候选与 profile 均不存在。当前结论仅为 **Blocked**，不是 Candidate Ready、PM Pass、Accepted、Frozen、风险关闭或 Stage 4 结论。

## 范围、授权与只读保全

执行授权证据为用户投递的绝对任务卡路径：`/Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-117_p3_116_current_candidate_native_capture_dynamic_evidence_successor.md`；会话类型为新建 Codex 本地视觉 Evidence 会话，接收日期为 2026-08-25 CST。本会话未复用 P3-116 执行或评审会话，未发现旧任务授权被作为写入授权继承。

允许写入严格限于 P3-117 原型目录、本报告、任务本地预检位置及唯一临时根。实际写入仅发生在 `lifeos/prototypes/LIFEOS-P3-117/`、本报告及已删除的唯一临时根。P3-116 目录、P3-113 至 P3-115、历史 Evidence、PM Review、账本、风险与冻结文件均保持只读。没有访问真实数据、网络、HTTP(S)、localhost、CDP、DevTools、headless、WebDriver、扩展、DB、Tauri/IPC、Vault、同步或外部服务。

本地模型预检：Skipped。该任务的冻结边界禁止网络，而本地预检工具需要访问局域网模型；同时本报告属于浏览器隔离／P0 Evidence 阻断的事实记录，不适合由本地模型替代或影响判断。此跳过不改变 PM 的独立复核责任。

## 已保留的预检与清理 Evidence

| Evidence | 事实 | 结论 |
|---|---|---|
| `evidence/preflight/fixed_inputs.json` | 13 项按 ABF 固定值实测；仅当前 PM Review 为 `09d810…f8aa`，不等于 ABF 的 `f698…` | `BLOCKED_ABF_FIXED_INPUT_MISMATCH`；复跑未创建临时根 |
| `evidence/preflight/prepare_result.json` | 是发现该 ABF 内部冲突前的静态复制记录；八项候选／合同复制前哈希一致，临时 index 仅附加 task-local probe | 历史静态记录，不能作为有效的启动通过或动态／视觉闭环 |
| `evidence/preflight/probe_audit.json` | probe 固定 ID、所需 runtime 标签和禁止网络／存储 token 的静态审计 | 仅静态 probe 审计，不证明 GUI 行为 |
| `evidence/cleanup.json` | cleanup 前根、candidate、profile 存在；cleanup 后均不存在 | 精确清理 PASS |

`test_plan.json`、capture、record、render、verify、mutation、Manifest 与 cleanup runner 为 P3-117 自有可审计脚本／计划。由于停止条件，计划中的 46 个动作从未执行；这些文件不能被当作动作级 Evidence 或通过结论。

## 冻结矩阵的实际状态

| ABF 行 | 实际 Evidence | 结论 |
|---|---|---|
| M-001 启动前核对 | 任务卡／ABF 文件哈希正确；但交付前发现 ABF 内部 PM Review 固定哈希与当前文件不一致，且实际模型标签不可独立读取 | **Not Pass / Unknown** |
| M-002 临时复制、专用 app-mode | 临时复制与 probe 静态审计完成；独立进程参数存在，但 Computer Use 未绑定唯一 app-mode 窗口，精确 URL／无 ambient 不能安全证明 | **Not Pass** |
| M-003 原生图像链 | 未取得 raw、proof、clean、geometry 或 capture ID | **Not Implemented** |
| M-004 至 M-010 页面／状态／权限动作 | 未操作，未记录任何动态状态 | **Not Implemented** |
| M-011 三 viewport | 未调整或证明 viewport／DPR | **Not Implemented** |
| M-012 键盘／motion | 未操作 Tab、Shift+Tab、Enter、Escape 或 reduced-motion | **Not Implemented** |
| M-013 verifier baseline | 缺少 canonical 图像链与逐行动作结果，不能运行为通过依据 | **Not Implemented** |
| M-014 12 类 mutation | 缺少先行 clean baseline，未运行 mutation | **Not Implemented** |
| M-015 结束复算 | 临时根精确清理已 PASS；但完整 Evidence、版本绑定和全部计数不能复算 | **Not Pass** |

ABF-I-01 的八项候选／合同静态哈希未见漂移；ABF-I-12 的临时根精确清理可复核。其余 I-02 至 I-11，特别是专用窗口身份、真实本地入口、原生截图来源、裁剪链、viewport、动作语义、非复用图像、完整 GUI 执行与 fail-closed baseline，均未达到可独立证明的门槛。静态脚本、启动命令或进程参数不能替代这些要求。

## 隔离停止事实与影响

事实：启动命令严格采用 Frozen 的 `/usr/bin/open -na "Google Chrome"`、唯一 `--user-data-dir=/private/tmp/lifeos-p3-117-native-capture-v1/chrome-profile`、单一 `--app=file:///private/tmp/lifeos-p3-117-native-capture-v1/candidate/index.html`，以及全部五个关闭网络／同步／扩展／首次启动参数。随后，Computer Use 以 Google Chrome 应用标识读取到的是既有普通 Chrome 窗口，且 URL 并非该临时 `file:` 副本。为保护隐私，本报告不重述任何既有标签、账户、页面标题或其内容。

推断：当前冻结的 Computer Use 入口按应用标识无法保证选中由 `open -na` 产生的独立 P3-117 实例；因此不能安全满足“唯一窗口”“无 ambient metadata”“实际 GUI 操作”和“原生窗口截图仅限已唯一确认窗口”。即使独立进程参数存在，也不能弥补窗口身份和前台 GUI 绑定缺失。

结论：这是 ABF 定义的 Blocked 条件，不能改用其他浏览器、全屏截图、已有 Chrome、browser export、自动化入口或其它取证路径。尝试这些替代将扩大入口或记录现有浏览器状态，违反 L1-1、L1-6、L1-7、L1-9 与 ABF-I-02 至 I-05。

## 计数与角色／关卡

本包自检通过：**No（Blocked）**。保守计数为：`P0=2`（ABF 固定输入与当前 PM Review 冲突；Computer Use 错误识别既有浏览器窗口，无法维持冻结隔离）；`P1=0`；`P2=0`；`Unknown=2`（实际模型标签、唯一 app-mode 窗口身份）；`Not Implemented=12`（M-003 至 M-014 的必要闭环，M-004 至 M-012 的所有子动作均未执行）。该计数是本次执行／Evidence 状态披露，不对 P3-116 候选产品作缺陷归因。

- 主责角色：Evidence QA／技术执行。
- 协审检查点：体验动态闭环、隐私／安全隔离、可访问性、技术可复核性。
- 已覆盖关卡：任务／ABF 文件哈希、静态候选副本与 probe 审计、精确清理、停止条件披露。
- 未覆盖且不得虚报通过的关卡：实际 GUI 动态／视觉闭环、唯一 app-mode 窗口与原生截图、三 viewport、键盘／motion、语义／隐私 verifier baseline、mutation、完整 Manifest-Evidence 映射和 PM 验收。

## 需要 PM 决策

1. 确认本次 `Blocked` 事实：冻结 Computer Use 入口无法唯一操作 P3-117 独立 app-mode 窗口，因而不得继续在本 ABF 下取证。
2. 确认 ABF 内部 P3-116 PM Review 固定哈希 `f698…` 与当前只读文件 `09d810…` 的治理处理。任何修正 Frozen ABF、改变固定输入或更换 GUI 入口都超出本任务，须由 PM 按治理规则决定关闭／保全及是否新建任务与新 ABF。
3. 不将本报告或其静态预检视为 P3-116 Candidate Ready、PM Pass、Accepted、Frozen、风险关闭或 Stage 4 的依据。

## 后续任务建议

无。本专项会话不创建后续任务。若 PM 认为仍需取证，应先在 PM 主会话处理 ABF 固定输入冲突，并定义一个能够由 Computer Use 唯一、安全识别且不接触现有浏览器的入口；这不是当前任务可自行扩大或修复的事项。

## 阻塞或异常

存在两项独立且均为 fail-closed 的阻塞：

1. **冻结输入冲突**：ABF 固定表中的 P3-116 PM Review 哈希为 `f698…`, 当前只读文件实测为 `09d810…f8aa`。初始 P3-117 runner 错以当前值作为预期；已在交付前改为 ABF 值并复跑为 fail-closed。不能将当前文件悄然重哈希成 ABF 的通过输入，也不能改写 ABF。
2. **专用 GUI 隔离失配**：实际 Chrome 独立进程已按参数启动，但 Computer Use 读取到既有普通 Chrome 窗口，未能唯一证明或操作 P3-117 app-mode 窗口。根据 ABF 的 Blocked 规则，未使用任何替代截图或自动化路径。

清理例外：无。唯一临时根已精确删除，profile 与候选副本均不存在；未对任何现有 Chrome 会话实施关闭或操作。
