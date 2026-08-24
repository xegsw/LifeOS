# LIFEOS-P3-024｜真实 Tauri / IPC 集成前置验证任务规划

## 任务信息

- 任务 ID：LIFEOS-P3-024
- 任务名称：真实 Tauri / IPC 集成前置验证任务规划
- 任务类型：技术验证规划 / 决策型任务
- 主责角色：技术架构负责人 / 安全验证规划
- 协审角色：AI 信任与安全负责人、数据 / 领域模型负责人、QA / Evidence Reviewer
- 评审关卡：Gate 3 AI 权限与信任、Gate 4 技术可行性
- 日期：2026-08-13
- 状态：Completed

---

## 1. 结论摘要

1. **[事实]** P2-015 以等价可执行 harness 验证了后端安全合同（42/42 PASS、P0=0），但未验证真实 Tauri capability/plugin、invoke 注册、WebView/CSP、debug/release 包或目标平台路径行为。这是 R-0040 保持 Open / Conditional 的核心原因。
2. **[事实]** P3-009 至 P3-022 在合成、单进程、受控测试包内证明了领域门禁和证据链正确性（37 PASS / 0 FAIL、63 条反例全通过），但没有 Renderer、真实 IPC、真实文件出口或真实 Vault，不能外推为真实集成层安全。
3. **[建议]** 建议立即创建实际验证任务，但前置条件是：安装 Rust/Tauri 工具链、构建最小 Tauri 壳（Renderer + 后端 IPC）、使用合成临时目录和模拟 Vault（不接入真实用户文件）。
4. **[建议]** 不建议在 Schema/API 设计和 UI 壳规划完成前启动验证。建议顺序：先完成最小 Tauri 壳搭建 → 再执行 P2-015 矩阵迁移验证。
5. **[事实]** 本任务完成后 R-0040 状态不变化，仍为 Open / Conditional。规划完成不等于验证通过，不等于能力可启用，不等于风险可关闭。

---

## 2. 已验证 / 未验证边界

### 2.1 已验证（P2-015 等价 harness 层）

| 验证项 | 状态 | 证据 |
|---|---|---|
| Renderer 零通用 OS 能力 | PASS | direct capabilities 为空；白名单无危险通用命令 |
| 未知 IPC 默认拒绝 | PASS | 任意读、通用写均 `IPC_UNKNOWN` |
| 路径规范化 + 真实根核对 | PASS | 解码后校验；existing path / export parent 核对真实根 |
| 攻击路径拒绝（traversal/绝对/编码/NUL/分隔符/symlink） | PASS | 全部拒绝 |
| 隐藏 / 排除 / 附件拒绝 | PASS | `.obsidian`、`.hidden`、`excluded`、非 Markdown 附件拒绝 |
| Vault 零写 / 零删 / 零改名 | PASS | 命令与计数 0；前后树/hash 一致 |
| 导出边界与确认 | PASS | 越界、静默冲突、未确认覆盖/合并、执行均拒绝 |
| 内容身份与来源版本 | PASS | 五类身份及 Source/版本/Derivation/Feedback/Auth 齐全 |
| 执行前重检 | PASS | auth/source/artifact/tombstone/restriction/lease/active 失配均拒绝 |
| 日志隐私 | PASS | 13 类禁止标记 0 命中 |

### 2.2 未验证（真实 Tauri 集成层缺口）

| 缺口 | 风险 | 来源 |
|---|---|---|
| 真实 Tauri capability/permission 白名单 | Renderer 可能通过未声明的 capability 获得文件/网络/shell 能力 | P2-015 §6, P3-021 §证据边界 |
| 真实 plugin/invoke 注册面 | 插件默认权限可能超出领域合同允许范围 | P2-015 §9 风险, P2-016 §5 R-0040 |
| WebView/Renderer CSP | CSP 配置不当可能允许 XSS 或 Renderer 侧越权 | P2-015 §8 条件, P2-016 §4 不冻结范围 |
| debug/release 包差异 | debug 配置可能暴露 devtools、宽松 CSP 或额外权限 | P2-015 §8, P3-021 §后续验证 |
| 目标平台路径行为 | macOS/Windows/Linux 路径规范化、symlink、大小写行为不同 | P2-015 §9 风险, P2-016 §5 |
| 真实 OS 路径攻击面 | 真实文件系统可能暴露 harness 未覆盖的边缘 case | P3-021 §后续验证 4 |
| IPC 参数校验端到端 | Renderer 到后端的 IPC 参数在真实序列化/反序列化中可能被篡改 | P3-021 §后续验证 3 |
| 进程杀死耐久 | H3 未迁移；真实进程崩溃/掉电时 SQLite 数据完整性未验证 | P3-023 §6 冻结前硬条件 |

---

## 3. 最小验证矩阵

未来真实 Tauri / IPC 验证任务必须覆盖以下矩阵。每行至少一个正测 + 若干反例。

### 3.1 Capability / Permission 白名单

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-01 | Renderer capability 声明只含三窄命令 | capability JSON 只含 read/export/control | 任意文件/数据库/shell/进程/网络命令不存在 | P0 |
| M-02 | 未声明 capability 默认拒绝 | 已声明命令可调用 | 未声明命令返回 `IPC_UNKNOWN` | P0 |
| M-03 | capability 变更触发复测 | — | 修改 capability.json 后未复测则能力关闭 | P1 |

### 3.2 Plugin / Invoke 注册面

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-04 | 只注册三窄命令的 invoke handler | read/export/control 可调用 | 任意未注册 invoke 返回拒绝 | P0 |
| M-05 | 插件默认权限不超出领域合同 | — | 安装默认插件后检查是否有额外文件/网络/shell 权限 | P0 |
| M-06 | updater/sidecar 默认关闭 | — | updater/sidecar 配置为 disabled 或不存在 | P1 |

### 3.3 Renderer / WebView / CSP

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-07 | CSP 只允许同源和必要资源 | 页面正常加载 | inline script、外部 CDN、eval 均被 CSP 阻断 | P0 |
| M-08 | Renderer 无 `eval`/`Function`/`require` | — | 尝试在 Renderer 中调用 eval/Function/require 失败 | P0 |
| M-09 | devtools 在 release 中关闭 | — | release 包中 devtools 不可用 | P1 |

### 3.4 Debug / Release 包差异

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-10 | debug 和 release 均通过全矩阵 | debug 包全矩阵 PASS | release 包同样全矩阵 PASS | P0 |
| M-11 | release 不暴露 debug 接口 | — | release 包中无 devtools、无 debug log、无宽松 CSP | P0 |

### 3.5 目标平台路径行为

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-12 | macOS 路径规范化与攻击拒绝 | 合法路径可读写 | traversal/绝对/编码/NUL/symlink 全拒绝 | P0 |
| M-13 | Windows 路径规范化与攻击拒绝 | 合法路径可读写 | 反斜杠、UNC、交替流、大小写不敏感碰撞拒绝 | P0 |
| M-14 | Linux 路径规范化与攻击拒绝 | 合法路径可读写 | symlink、procfs、/dev 拒绝 | P0 |

### 3.6 合成临时目录 / 模拟 Vault

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-15 | 模拟 Vault 只读访问 | 合法 Markdown 可读 | Vault 写/删/改名为 0 | P0 |
| M-16 | 合成临时目录隔离 | 验证在临时目录内运行 | 临时目录外文件不可访问 | P0 |

### 3.7 Path Scope 与文件能力默认关闭

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-17 | scope 外 token 拒绝 | scope 内 token 可访问 | scope 外 token 返回拒绝 | P0 |
| M-18 | 文件系统导出默认关闭 | — | 导出能力未启用时 invoke 返回关闭 | P0 |
| M-19 | 导出只进入授权目录 | 导出到授权目录成功 | 越界、静默覆盖、合并、执行均拒绝 | P0 |

### 3.8 IPC 参数校验、项目边界、授权、tombstone、generation、证据重检

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-20 | IPC 参数端到端校验 | 合法参数通过 | 篡改参数（project_id、artifact_id、version）被拒绝 | P0 |
| M-21 | 跨 Project 隔离 | 同 Project 可访问 | 跨 Project 数据泄漏为 0 | P0 |
| M-22 | 执行前重检（auth/source/version/generation/tombstone/lease） | 匹配时通过 | 任一失配均 fail closed | P0 |
| M-23 | 撤回/删除不复活 | — | tombstone 后通过导出/恢复/ID 复用复活为 0 | P0 |

### 3.9 禁用能力的负测

| 编号 | 验证项 | 正测 | 反例 | P0? |
|---|---|---|---|---|
| M-24 | 八类默认关闭能力全部关闭 | 配置检查 false + 运行时 throw | 尝试调用每类关闭能力均被拒绝 | P0 |
| M-25 | 真实 Vault 未接入 | — | 无真实 Vault 路径配置 | P1 |
| M-26 | 真实数据/云/模型未接入 | — | 无真实 API key、无云连接、无第三方模型调用 | P1 |

---

## 4. P0 / P1 / P2 判定标准

### P0（阻断一切，必须修复后才能继续）

- Renderer 通过未声明 capability、plugin、invoke 或 WebView 获得任意文件/数据库/shell/进程/网络能力。
- 未知 IPC 命令未被默认拒绝。
- 路径 traversal、绝对路径、编码攻击、symlink 攻击在真实 OS 上成功。
- Vault 写/删/改名计数不为 0。
- 导出越界、静默覆盖或执行导出内容成功。
- 执行前重检（auth/source/version/generation/tombstone/lease）任一失配未被拒绝。
- 跨 Project 数据泄漏。
- 撤回/删除后通过任何路径复活。
- 八类默认关闭能力中有任何一类可被调用。
- debug 或 release 包任一 P0 断言失败。

### P1（阻断对应能力，但不阻断规划继续）

- updater/sidecar 默认未关闭。
- release 包暴露 devtools 或 debug log。
- capability 变更未触发复测提醒。
- 真实 Vault/数据/云/模型连接存在但未授权。
- 进程杀死耐久未验证（H3 未迁移）。

### P2（清洁项，不阻断）

- 日志格式或字段命名不一致。
- capability JSON 注释或格式不规范。
- CSP 策略有冗余允许项但不构成安全风险。

---

## 5. Evidence 包结构建议

```
lifeos/engineering/LIFEOS-P3-XXX-tauri-ipc-validation/
├── README.md                    # 环境、工具链版本、复跑命令、证据地图
├── evidence/
│   ├── MANIFEST.md              # 总览：PASS/FAIL、snapshot、scope
│   ├── test_results.json        # 机器可读结果 + 文件 hash + snapshot
│   ├── test_run.log             # 原始测试输出
│   ├── test_matrix.csv          # 逐项矩阵（编号/验证项/正测/反例/结果）
│   ├── debug_results.json       # debug 包独立结果
│   ├── release_results.json     # release 包独立结果
│   ├── platform_results/        # 分平台结果
│   │   ├── macos.json
│   │   ├── windows.json
│   │   └── linux.json
│   ├── audit_log.jsonl          # 最小审计日志
│   ├── privacy_scan.json        # 隐私扫描结果
│   └── capability_snapshot.json # Tauri capability 配置快照
├── fixtures/
│   ├── synthetic_vault/         # 模拟 Vault
│   ├── export_root/             # 授权导出根
│   └── attack_samples/          # 攻击样例
└── src/
    └── validation_harness.ts    # 可复跑验证脚本
```

---

## 6. 失败处理与降级策略

| 失败类型 | 降级措施 | 恢复条件 |
|---|---|---|
| Renderer capability 越权 | 关闭越权 capability，收窄到三窄命令 | 复测 P0=0 |
| Plugin 默认权限过宽 | 禁用问题插件或显式收窄权限 | 复测 P0=0 |
| CSP 策略不安全 | 收紧 CSP 到只允许同源 | 复测 P0=0 |
| 路径攻击在真实 OS 上成功 | 关闭受影响路径能力，修复规范化逻辑 | 复测 P0=0 |
| Vault 写/删/改名不为 0 | 关闭 Vault 访问能力 | 复测 P0=0 |
| 导出越界 | 关闭文件导出能力 | 复测 P0=0 |
| debug/release 差异导致 P0 | 以 release 为准，关闭 debug 额外权限 | 双包复测 P0=0 |
| 进程杀死数据损坏 | 启用 WAL + 定期 checkpoint + SQLite-aware backup | 耐久测试通过 |

**[原则]** 修复不得放宽领域安全合同。如果无法在 Tauri 安全模型内修复，考虑更换桌面壳候选，但不得放宽 H1-H9 / T-ARCH 不变量。

---

## 7. 是否建议启动实际验证任务

**[建议] 建议启动，但需先完成前置条件。**

### 前置条件

1. **安装 Rust/Tauri 工具链**：当前本机无 Rust/Tauri 工具链（P2-015 已记录），需要先安装。
2. **构建最小 Tauri 壳**：包含 Renderer（静态 HTML + CSP）、后端 IPC handler（三窄命令）、SQLite 持久化。
3. **使用合成临时目录和模拟 Vault**：不接入真实用户文件、不连接真实 Vault。
4. **生产 Schema/API 初步设计**：当前 P3-009 的 Schema 仅为不变量落点，验证前需至少定义 IPC 命令签名和参数结构。

### 不建议立即启动的情况

- 如果 PM 认为应先完成 UI 壳规划或生产 Schema/API 设计，可以推迟验证任务。
- 如果用户希望先看到 UI 原型验证，可以并行推进 UI 规划和 Tauri 壳搭建。

### 建议顺序

1. 生产 Schema/API 设计任务（不执行，只设计）
2. 最小 Tauri 壳搭建任务（工程实现，Codex）
3. P2-015 矩阵迁移验证任务（独立评审，WorkBuddy）
4. R-0040 关闭评估任务（需用户确认）

---

## 8. 角色检查点结果

### 主责角色：技术架构负责人 / 安全验证规划

- **最小安全矩阵是否充分**：[判断] 是。矩阵覆盖 9 个攻击面、26 个验证项，每项至少一个正测 + 若干反例，覆盖 P2-015 全部 11 个 P0 断言并扩展到真实 Tauri 层。
- **P2-015 后端合同如何迁移**：[判断] P2-015 的 42/42 PASS 矩阵可直接迁移为 M-01 至 M-23 的正测和反例脚本，但执行环境从 Python harness 迁移到真实 Tauri debug/release 包。迁移时需保持攻击样例和夹具语义一致。
- **哪些条件满足前不得关闭 R-0040**：[判断] 以下条件全部满足前不得关闭：M-01 至 M-24 全部 P0=0（debug 和 release 双包、所有目标平台）；进程杀死耐久测试通过；PM 验收 + 独立反例复核 + 用户确认。

### 协审角色：AI 信任与安全负责人

- **[检查]** IPC/path scope/Renderer/debug-release 差异是否可能绕过用户授权、证据链、tombstone、generation 和 Project 边界：是，M-04/M-05/M-07/M-08/M-10/M-11/M-20/M-22 直接覆盖这些旁路。
- **[检查]** 规划是否误把"验证计划完成"写成"真实能力可启用"：否。本规划明确声明不启用真实能力、不关闭 R-0040、不冻结工程基线。
- **[检查]** Evidence 设计是否足以让 PM 判断 P0/P1/P2：是。分 debug/release/平台独立结果 + 逐项矩阵 + 审计日志 + 隐私扫描 + capability 快照。

### 协审角色：数据 / 领域模型负责人

- **[检查]** IPC 参数校验是否覆盖五类内容身份、Source/Artifact/Derivation/Feedback/Authorization 引用：是，M-20 和 M-22 覆盖。
- **[检查]** 撤回/删除不复活在真实 Tauri 层是否仍成立：是，M-23 覆盖。

### 协审角色：QA / Evidence Reviewer

- **[检查]** Evidence 包结构是否支持独立复跑：是，README.md 含复跑命令、test_results.json 含 hash 和 snapshot、test_matrix.csv 含逐项结果。
- **[检查]** 是否存在自证循环风险：建议验证任务由独立 Agent（WorkBuddy）执行反例复核，工程实现 Agent（Codex）不评审自己的验证结果。

---

## 9. 关卡结论

- **Gate 3 AI 权限与信任评审：Pass with Conditions。** 矩阵覆盖 Renderer/IPC/path scope/debug-release 对 AI 授权边界的旁路风险；条件是实际验证任务须经独立反例复核。
- **Gate 4 技术可行性评审：Pass with Conditions。** 矩阵在技术可行；条件是前置条件（工具链、Tauri 壳、Schema/API）满足后才能执行。

---

## 10. 需要 PM / 用户确认的问题

1. **[需 PM 确认]** 是否接受本规划作为未来真实 Tauri/IPC 验证任务的设计输入。
2. **[需 PM 确认]** 是否建议先完成生产 Schema/API 设计任务，再启动 Tauri 壳搭建和验证。
3. **[需 PM / 用户确认]** 是否启动实际验证任务（需安装工具链、构建 Tauri 壳），还是先推进 UI 壳规划。
4. **[需 PM 确认]** 验证任务的目标平台范围：仅 macOS（当前开发机），还是 macOS + Windows + Linux。
5. **[需用户确认]** R-0040 关闭仍需用户确认，本规划不改变 R-0040 状态。

---

## 11. 后续任务建议

1. **[建议，需 PM 确认后另立任务]** 生产 Schema/API 设计：定义 IPC 命令签名、参数结构、错误码、SQLite Schema 面向生产的设计。这是 Tauri 壳搭建的前置依赖。
2. **[建议，需 PM 确认后另立任务]** 最小 Tauri 壳搭建（Codex 工程实现）：Renderer + 后端 IPC handler + SQLite 持久化，使用合成临时目录。
3. **[建议，需 PM 确认后另立任务]** P2-015 矩阵迁移验证（WorkBuddy 独立评审）：在真实 Tauri debug/release 包上执行 M-01 至 M-26 全矩阵。
4. **[建议，需 PM 确认后另立任务]** UI 实现规划：从冻结的三张 Stitch 原型到 React 前端的实现规划，可与 Tauri 壳搭建并行。
5. **[建议，需 PM 确认后另立任务]** 进程杀死耐久 / SQLite-aware backup 验证：H3 未迁移的进程杀死、fsync/掉电、SQLite-aware backup 需独立验证。

---

## 12. 范围与变更声明

本任务仅创建本规划报告；未修改代码、测试、evidence、Stitch、项目账本或冻结状态；未安装、配置或运行真实 Tauri；未关闭 R-0040；未启用真实数据、真实 Vault、真实 Tauri/IPC、真实文件导出、云/第三方模型、向量、同步、多设备、L3 或外部用户；未恢复或冻结工程基线；未进入下一阶段；未自行启动后续任务。本规划仅为 PM/用户决策输入，不替代 PM 验收和用户确认。
