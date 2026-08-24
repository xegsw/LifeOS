# LIFEOS-P3-110｜P3-104 + P3-106 组合候选全新隔离独立复评路径授权后继

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。用户已采纳 P3-109 的关闭结论并授权创建 P3-110。本任务只读评估固定 P3-106 Tauri candidate 与 P3-104 runtime 安全底座，只在项目工作区、Frozen ABF 的 14 个 P3-110 精确路径和候选既有三条 unit-test 路径正则内使用固定非敏感夹具；不访问 retained pilot、真实个人文件／DB、网络、云、第三方、凭据或外部目标，不扩展通用文件／数据库／进程能力。

## 任务信息

- 任务 ID：`LIFEOS-P3-110`
- 优先级：P0
- 任务类型：全新隔离独立工程／安全／视觉／响应式／可访问性复评
- 单一结果：独立判断固定 P3-104 + P3-106 组合候选是否满足 Frozen ABF 的完整 16 行矩阵。
- 与 P3-109 的唯一治理变化：授权候选不可变 unit tests 已声明的三条精确路径正则及可归属本轮的新路径清理；其余结果、候选、标准和边界不变。
- 是否为受控能力包：Yes；只读复评，不修复候选。
- 包内允许工作：独立测试设计、正向 allowlist 副本、离线 locked test/build/bundle、actual app、固定视觉比较、native geometry、生命周期／路径反例、语义 verifier、Evidence／Manifest／Review。
- 包内整改授权：仅 P3-110 自身 runner、Evidence、Review 和交付文案；不得修改候选、ABF、账本、风险或冻结。
- 是否适用 P3 Engineering Fast Lane：No。
- 推荐 Agent：全新 Codex 独立评审会话。
- 推荐模型：`gpt-5.6-terra`
- 推荐推理强度：`xhigh`
- 选择理由：P0 路径归属、独立性、runtime／IPC、失败关闭、native geometry 与 Evidence 语义需联合判断。
- 允许降级模型：None。
- 禁止降级条件：全部范围。
- 必须升级条件／后备模型：N/A / None；首选配置不可用时 Blocked。
- 是否需要后续独立评审：No；本任务自身即独立复评，之后仍须 PM 验收和用户采纳。
- 是否允许修改工程／账本：No / No。
- 主责角色：独立 QA／安全与数据生命周期评审。
- 协审角色：体验、可访问性、技术架构、数据／领域、AI 信任安全。
- 必须通过关卡：Gate 1–4；Gate 5 仅固定非敏感内部理解，不作阶段 Pass。
- 状态：`Ready / Acceptance Basis Frozen / Awaiting Task-card Delivery`
- 验收治理：`lifeos/ACCEPTANCE_GOVERNANCE.md`
- Frozen ABF：`lifeos/tasks/LIFEOS-P3-110_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_path_authorization_successor_acceptance_basis_freeze.md`
- ABF ID／版本：`ABF-P3-110-v1`
- ABF SHA-256：`8324c9e847bafdfeebb022affffb372c0ce032a326009990bb3740e0310f1570`
- 正式 Rework：0/2。
- 生效决策：D-0445。
- 执行授权：向合格全新会话投递本任务卡绝对路径即启动；无需重复“授权”。
- 投递前额外用户确认：None。越出本 ABF 的真实数据、系统设置、候选、风险、冻结或阶段变化仍需新确认。

## 会话隔离和读序

- 必须新建会话，不得复用 P3-104 至 P3-109 工程／评审会话或 PM 主会话。
- 先只依据任务卡、Frozen ABF 与 L1 创建 `test_design.md` 并固定 SHA-256；之后才可读取 P3-109 runner／结果。
- P3-107/P3-108/P3-109 runner、tools、动态结果不得复制、导入、执行或作为当前 PASS 输入。
- 前任务全部结束；旧任务授权不继承，只有本任务卡与 `ABF-P3-110-v1` 有效。

## 最小启动包与定向补读

必须完整读取：

1. `AGENTS.md`
2. `lifeos/CURRENT_STATUS.md`
3. 本任务卡
4. Frozen ABF
5. `lifeos/ACCEPTANCE_GOVERNANCE.md`
6. `lifeos/templates/INDEPENDENT_REVIEW_TEMPLATE.md`
7. `lifeos/templates/SESSION_REPORT_TEMPLATE.md`
8. `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
9. P3-104 任务卡、最新 PM Review、Engineering／PM Evidence Manifest
10. P3-106 任务卡、ABF、rework-1 交付物、PM Review、Engineering／PM Evidence Manifest
11. `lifeos/engineering/LIFEOS-P3-106/write_path_inventory.json`
12. P3-109 任务卡、ABF、交付物、独立 Review、PM Review 与 PM Evidence Manifest
13. ABF 固定的三张 Stitch 和三张 P3-106 1280×1024 Evidence

定向补读：

- `lifeos/PM_OPERATING_MODEL.md`：任务投递、模型、独立评审、动态 Evidence、两层验收。
- `lifeos/ROLE_MATRIX.md`：PM／独立 QA／体验／架构／数据／AI 信任职责。
- `lifeos/STAGE_GATES.md`：Gate 1–5、Stage 3→4。
- `lifeos/DECISION_LOG.md`：D-0401、D-0433 至 D-0445。
- `lifeos/RISK_LOG.md`：R-0019、R-0040、R-0051、R-0052。

只在冲突时补读无关历史，不得全文翻阅代替定向核对。

## 启动前 unit-test 路径关卡

在任何 copy／test／build 前必须：

1. 复算 `write_path_inventory.json` hash。
2. 从该文件逐字读取并与 ABF 三条 unit regex 比对。
3. 仅枚举 `/private/tmp` 直接子项名称并立即过滤；不读取非匹配项 metadata／内容。
4. 三条 regex 的执行前匹配集合必须为空；否则 Blocked，禁止删除。
5. 建立 cargo／test PID、时间与新匹配路径台账。

执行后候选 tests 应自行清理。只有本轮新出现、精确匹配且能以 PID／时间／台账归属的路径可以逐条补充清理；禁止 wildcard、broad prefix、删除预存项或无法归属项。最终匹配集合必须为空。

## 验收范围

完整执行 Frozen ABF 的 M-001 至 M-016：

- 10 项固定输入、授权、模型、独立性与读序；
- allowlist clean copy、unit path ledger、离线 locked test/build/bundle、静态 provenance；
- 固定 P3-106 三张 1280×1024 Evidence 与 Stitch 的逐态比较；
- current actual app 原窗口与 macOS native outer frame 精确 700×760；
- saved、repeat、conflict、failure、refresh、navigation、close/reopen；
- 未实现控件、unknown IPC、多余字段；
- 目录／软链／硬链／类型／悬挂 final／外部路径／dangling sidecars／tamper；
- Tab／Enter／skip／focus、current reduced-motion 披露、隐私／网络 scan；
- raw semantic verifier、六类 mutation、payload hash、P3-110 与 unit-test 精确清理、顶层 Manifest。

不得以旧动态 Evidence、CUA 缩放尺寸、配置文件、矩阵状态或 Markdown 自述替代当前实际动作与 raw Evidence。700×760 的定义、verifier 输入、mutation、Pass 公式和 Blocked 条件以 Frozen ABF 为准。

## 允许修改与交付

只允许：

- `lifeos/deliverables/LIFEOS-P3-110_p3_104_p3_106_combined_candidate_fresh_isolated_independent_review_path_authorization_successor.md`
- `lifeos/reviews/LIFEOS-P3-110/independent_review.md`
- `lifeos/reviews/LIFEOS-P3-110/evidence/`
- ABF 明列的 P3-110 精确临时路径与三条 unit-test regex 匹配的本轮可归属路径

Evidence 必须包含 16 行独立结果、10 项 fixed inputs、read order、test design、copy inventory、unit pre／during／post ledger、build logs、static、固定视觉、native geometry raw output、actual app／DB／fixture before/after、boundary／negative／a11y／scan、semantic verifier、六类 mutation、payload manifest、cleanup、顶层非自指 Manifest和复跑命令。

## 结论与退出

- 专项结论：Pass / Rework / Blocked；PM 独立裁决。
- Pass：Frozen I-01–I-14、M-001–M-016 与全部子动作通过；P0/P1/P2/Unknown/Not Implemented 全 0；unit baseline／归属／cleanup、语义 verifier／mutation、历史保全和 Manifest 全成立。
- 同任务 Rework：仅 P3-110 自身 runner／Evidence／Review 缺陷，ABF 不变且未达两轮上限。
- 候选 P0/P1：独立评审不得修复，交 PM 决定新任务。
- 固定输入漂移、unit pre-baseline 非空／归属不明、正确模型／离线工具／actual app／两种 native geometry 查询不可用：Blocked。
- 即使 Pass，也不改变 R-0040／R-0051／R-0052，不冻结、不连接 retained pilot、不恢复基线、不进入 Stage 4。

## 本地预检与聊天回复

- 可跳过本地模型预检：本任务涉及 P0 独立性、真实 Tauri/IPC、路径授权和 Evidence 真实性最终判断；Review 须说明。
- 聊天严格使用 `SESSION_REPORT_TEMPLATE.md`，只输出结论、ABF/hash、Evidence 摘要、五类计数、资产／风险、下一步、Review／Evidence 路径和需 PM 确认事项。
