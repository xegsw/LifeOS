# LIFEOS-P2-015｜Tauri / IPC 最小安全边界窄测报告

- 任务类型：研究型任务（技术 Spike 执行）
- 主责角色：技术架构负责人
- 协审角色：AI 信任与安全、数据 / 领域模型、体验设计负责人、PM
- 验证日期：2026-08-09
- 证据入口：`lifeos/spikes/P2-015-tauri-ipc-boundary/README.md`
- 最终结论：**Pass with Conditions**

## 1. 执行摘要

1. **[实测]** 标准库等价可执行 harness 连续复跑通过，末次 42/42 PASS、0 FAIL、P0 失败 0；越权成功、Vault 写 / 删 / 改名、导出越界、身份丢失均为 0。
2. **[实测]** Renderer 直接 capability 为空，仅有三个窄命令；任意文件 / 路径 / 数据库 / shell / 进程 / 网络命令不存在，未知 IPC 默认拒绝。
3. **[实测]** 后端拒绝 `..`、绝对路径、异常/双重编码、NUL、反斜杠、symlink、scope 外 token、隐藏 / 排除项、`.obsidian` 和未授权附件；Vault 前后树与 hash 一致。
4. **[实测]** 导出只进入授权目录，静默覆盖 / 合并和执行导出内容被拒；读取和导出执行前重检授权、来源 / 版本、generation 与租约。
5. **[实测]** IPC 包络保留用户原文、外部来源、AI 派生、AI 推断 / 建议、用户确认五类身份，以及 Source、版本、Derivation、Feedback、Authorization 引用。
6. **[推断]** 后端最小安全合同已获可执行证据；但未验证真实 Tauri capability、插件、WebView、CSP、打包和目标平台配置，故只能 `Pass with Conditions`。是否关闭 R-0040 需 PM 验收。

## 2. 测试环境与最小 harness

**[事实]** 环境为 macOS arm64、Python 3.9.6，本机无 Rust/Tauri 工具链；未安装依赖、联网或调用外部资源。任务卡允许等价可执行 harness，因此验证可移植后端合同，不冒充真实框架配置。

**[实测]** `run_harness.py` 实现默认拒绝 dispatcher、授权与路径 gate、只读来源、受控导出、最小审计及测试 runner。能力合同声明 Renderer 零直接 capability、三命令白名单及危险通用能力全关闭。二者均非正式 API 或 capability 冻结。

## 3. 合成目录与攻击样例

**[实测]** harness 仅重建本 Spike 下 `work/`，夹具含模拟 Vault、授权导出根、边界外目录、合法 Markdown、隐藏/排除项、附件、读取/导出 symlink 和已有导出文件。攻击样例含 traversal、绝对/异常编码、NUL、分隔符、越界、错误 token、未知命令、冲突和过期快照。未扫描 Home、连接真实 Vault 或处理真实内容。

## 4. 验证方案与证据入口

复现：`python3 lifeos/spikes/P2-015-tauri-ipc-boundary/run_harness.py`。入口 `README.md` 记录环境、源码 hash、证据地图、边界和实际 Tauri 复测触发器；`evidence/results.json` 为机器结果，`test_matrix.csv` 为逐项矩阵，`audit_log.jsonl` 与 `privacy_scan.json` 为审计及隐私证据。

## 5. P0 断言结果矩阵

| P0 | 结果 | 关键证据 |
|---|---|---|
| 1 Renderer 无通用能力 | PASS | direct capabilities 为空；白名单无危险通用命令 |
| 2 未知 IPC 默认拒绝 | PASS | 任意读、通用写均 `IPC_UNKNOWN` |
| 3 规范化 + 真实根核对 | PASS | 解码后校验；existing path / export parent 均核对真实根 |
| 4 攻击路径与 scope 拒绝 | PASS | traversal、绝对、编码、NUL、分隔符、symlink、错误 token 全拒绝 |
| 5 隐藏 / 排除 / 附件拒绝 | PASS | `.obsidian`、`.hidden`、`excluded`、非 Markdown 附件拒绝 |
| 6 Vault 写 / 删 / 改名为 0 | PASS | 命令与计数 0；前后树/hash 相同 |
| 7 通用写不能写 Vault | PASS | 通用写不存在；export token/根与 Vault 分离 |
| 8 导出边界与确认 | PASS | 越界、静默冲突、未确认覆盖/合并、执行均拒绝 |
| 9 内容身份与来源版本 | PASS | 五类身份及 Source/版本/Derivation/Feedback/Auth 齐全 |
| 10 执行前重检 | PASS | auth/source/artifact/tombstone/restriction/lease/active 失配均拒绝 |
| 11 日志隐私 | PASS | 13 类禁止标记 0 命中；日志字段 allowlist 通过 |

合计：42 PASS、0 FAIL；网络、shell / 进程、越权成功、身份丢失均为 0。

## 6. 边界与内容身份结果

**[实测]** Renderer 只调用窄命令；source token 只读 Vault Markdown，export token 只写独立根且冲突需确认，输出不执行。路径在异常语法、隐藏/排除/symlink 拒绝后核对真实根。每次执行前核对 Authorization、来源/版本、generation、active 和租约。响应保留五类身份及来源、Derivation、Feedback 引用；确认不洗掉 AI 来源。

## 7. 日志隐私扫描

**[实测]** 审计仅含 `seq`、`command_class`、`outcome`、`reason_code`。对任务路径、Home 路径、合成 Vault 名、受限/导出正文、prompt、model output、embedding 共 13 类扫描，命中 0。该结果只证明固定夹具字段最小化，不外推为生产崩溃转储或反关联安全证明。

## 8. 结论：Pass with Conditions

**[结论]** 全部 P0 通过，后端合同达到 Pass 数值门槛。实际 Tauri / Rust 工具链、capability/plugin、WebView/CSP、debug/release bundle 和其他平台未验证，属于任务卡允许的非目标平台/打包缺口，故项目级结论为 **Pass with Conditions**；条件不包含任何 P0 豁免。

**[需 PM 确认]** 可选择：接受本证据并将 R-0040 记为“等价 harness 条件关闭”；或要求实际 Tauri 包证据前保持 Open。无论选择哪种，真实桌面壳首次引入、capability/plugin/IPC/scope 变更、启用 Obsidian/文件导出、debug/release 打包或增加平台时，均须移植本矩阵复测，复测前相关能力关闭。

## 9. 可冻结输入、不可外推与降级建议

**[建议｜仅作为冻结输入]** 可继承 Renderer 零通用 OS 能力、IPC 白名单/默认拒绝、后端路径/scope/授权重检、Vault 零写、导出隔离与确认、内容身份包络和最小审计。

**[不可外推]** 不冻结 Tauri、capability 名、插件、IPC 签名、API、Schema、字段、目录、路径库、桌面壳、跨平台行为或生产日志；不授权真实 Vault、真实数据、云、模型、第三方，也不准入 MVP。

**[建议]** 实际壳失败时关闭失败命令；Vault 失败则 Obsidian 保持关闭；导出失败则关闭文件导出；收窄 capability/IPC 后复测，必要时更换桌面壳候选，但不得放宽领域合同。

## 10. 风险、角色与待确认

- **[风险]** 等价 harness 不能发现真实 Tauri 插件默认权限、invoke 注册、WebView/CSP、release 配置、updater/sidecar 或 OS 路径差异。
- **[需 PM 确认]** 是否接受 `Pass with Conditions`，及 R-0040 采用条件关闭还是保持 Open 至实际集成复测。
- **[需 PM 持续确认]** 本结果不代表技术架构 Frozen 或 Stage 3 / 正式 MVP 准入。

角色检查：技术架构负责人 `Pass with Conditions`；AI 信任与安全检查默认拒绝、导出确认、重检、身份和日志隐私通过；数据 / 领域模型检查 Source、Artifact、Version、Derivation、Feedback、Authorization、generation 包络通过；体验设计确认原因码可转译为权限不足、来源变化、目标冲突、只读限制和重新确认，UI 不在范围；PM 检查未偷渡冻结或准入。

关卡自检：Gate 2 **Pass（测试语义层）**；Gate 3 **Pass（等价后端合同层）**；Gate 4 **Pass with Conditions**，仅待实际 Tauri/打包/平台复测。最终关卡和风险状态由 PM 验收。

## 范围与变更声明

仅创建本 Spike 资产和报告；未修改产品代码、Stitch、PM 台账、PRD、V1 范围、领域模型、AI 权限模型或其他 Spike；未处理真实数据 / Vault、调用真实模型/云/第三方/付费资源、冻结技术架构或准入 MVP。
