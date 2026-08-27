# LIFEOS-P3-133｜受控真实输入 Work 自用 Runtime 闭环

## 任务信息

- 任务 ID：`LIFEOS-P3-133`
- 风险等级：`L3`
- 优先级／缺陷严重性：`P0`
- 状态：`Ready / User Task Contract Confirmed / ABF Frozen / Awaiting Task-card Delivery`
- 主责 Agent／会话类型：Codex 工程执行会话；可复用已结束且边界仍清楚的 P3-132 工程线会话
- 所需执行能力：本地文件、Rust／JavaScript、SQLite、离线 actual Tauri、十一项严格 IPC、用户手工操作、隐私保护 Evidence
- 是否需要独立评审：`Mandatory`
- 独立评审触发理由：首次把 P3-132 合成候选扩展到真实个人短文本、真实专用目录和真实本地 DB，属于真实数据与真实能力启用边界
- 适用治理：Governance V2 结果级 L3 任务；`ABF-P3-133-v1` 已冻结
- 用户一次性确认：2026-08-26；确认精确真实根、全新 DB、最多 3 条／每条最多 200 字符的低敏感 Work 短文本、真实文本零 Evidence／日志／截图／hash／模型、独立评审先行、首轮保留且任何清理另行确认

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务仅允许用户在离线 actual Tauri 中手工输入最多 3 条低敏感 Work 短文本，并只写入一个全新专用目录和全新 DB。工程、合成测试和独立评审不得读取或复制这些真实文本。禁止访问既有 Pilot、真实个人文件、既有 DB、其他真实路径、网络、云、第三方、凭据、Vault、真实模型或 Agent。

用户已在看到完整合同后一次确认专用目录 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-3`、其中全新 `capture.sqlite`、最多 3 条用户手工输入的低敏感 Work 短文本、首轮保留目录和 DB。本授权覆盖创建、实现、构建、合成预检、强制独立评审、actual Tauri 真实自用运行、隐私保护 Evidence、同范围 Closure Cycle 与 PM 验收；合同内不再重复询问。确认原文保存在 `lifeos/tasks/LIFEOS-P3-133_user_confirmation.md`。

## Task Contract

### 1. 唯一用户结果

用户获得一个基于 P3-132 已通过候选的、可在 macOS actual Tauri 中实际自用的第一版 Work 闭环：

`手工输入低敏感短文本 → 本地持久化 → 用户显式确认 Context／Next Action → Today 展示已确认 Action → 关闭重开后保持一致`

Global AI、Context Inspector、Memory provenance 和 Today 页面继续可见，但真实文本不得交给 `OfflineSyntheticModelAdapter`。真实输入模式下，Evidence-backed Understanding／LifeOS noticed 默认关闭并明确显示“真实模型未启用；暂时没有足够证据判断”。本任务验证本地真实输入、持久化、用户控制和重启闭环，不宣称真实 AI 已启用。

### 2. 固定只读输入

- Frozen 前向架构权威：`lifeos/architecture/LifeOS架构基线V1.0.md`
- P3-132 accepted candidate：`lifeos/engineering/LIFEOS-P3-132/candidate/`
- P3-132 Engineering Final Manifest：`lifeos/engineering/LIFEOS-P3-132/evidence/FINAL_MANIFEST.json`
- P3-132 PM Review：`lifeos/reviews/LIFEOS-P3-132_pm_review.md`
- P3-132 PM Evidence：`lifeos/reviews/LIFEOS-P3-132/pm_evidence/reacceptance/`

执行前必须按 P3-132 Final Manifest 核验候选相对路径、bytes、SHA-256 和普通文件类型；任一 mismatch、额外文件、链接或历史冲突均在复制及真实目录访问前 fail closed。P3-132 及此前全部任务资产只读。

### 3. 允许范围

- 工程写入根：`lifeos/engineering/LIFEOS-P3-133/`
- 交付物：`lifeos/deliverables/LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop.md`
- 唯一工程临时根：`/private/tmp/lifeos-p3-133-real-self-use-v1`
- 唯一真实自用根：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-3`
- 唯一真实 DB：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-3/capture.sqlite`
- 允许真实数据：用户在 App 内手工输入最多 3 条低敏感 Work 短文本；每条不超过 200 个 Unicode 字符
- 允许真实入口：actual Tauri 的 Capture、Contexts、Today、Memory、Global AI 可见界面；仅由用户本人操作真实文本
- 允许 IPC：保持 P3-132 恰好十一项 IPC，不新增第十二项
- 允许工程动作：复制已核验候选到 P3-133、实现受控真实输入模式、自动测试、全新合成 DB 动态验证、强制独立评审、独立评审 Pass 后的真实自用运行、关闭重开和隐私保护状态核对
- 真实自用根和 DB 首轮保留；本任务不清理、不迁移、不覆盖。任何后续清理另行确认。

### 4. 真实文本与 Evidence 隔离

- 用户直接在 App 中输入真实文本；不得要求用户把文本粘贴到聊天、任务卡、日志或 Evidence。
- 工程和独立评审只使用固定非敏感合成文本；不得打开、查询、导出、截图、复制、hash 或记录真实文本内容。
- 真实运行 Evidence 仅允许记录：App/bundle 身份、授权根、DB 文件存在性与普通文件类型、记录数量、非内容型状态计数、错误码、时间、重启一致性和用户操作确认。
- 不得把真实文本、文本片段、文本 hash、页面截图、SQL row dump、audit payload、console payload 或派生摘要写入工程／评审 Evidence。
- 如任何诊断、日志、截图或异常可能包含真实文本，必须在生成前停止；不得事后以删除替代事前禁止。

### 5. 实现与产品边界

- Runtime root 必须由构建时 `LIFEOS_RUNTIME_ROOT` 唯一绑定到真实自用根；缺失、相对路径、非规范路径、链接链、非目录、越界 DB、已有非空 DB 或回退默认根均在任何写入前 fail closed。
- 首次真实启动只允许在专用根原先不存在或为空且 `capture.sqlite` 不存在时创建；不得接管既有目录或 DB。
- 真实输入模式必须通过明确的 build/runtime mode 与合成模式分离；真实文本不得到达 OfflineSyntheticModelAdapter、ModelPort、网络、AgentPort 或外部进程。
- Context、Candidate Next Action、Action、Today Focus 均保持用户显式确认语义；系统不得把 Capture、Observation、Suggestion 或未确认候选直接写成用户事实或已确认 Action。
- 用户拒绝、忽略或证据不足时不得生成 Today Focus 或 noticed；Today 允许为空。
- 关闭重开不得复制记录、改变内容身份、自动确认 Action 或产生隐藏 sidecar／页面／staging 文件。

### 6. 固定 IPC

候选 actual Tauri command 必须仍恰好为：

1. `capture_record`
2. `get_today`
3. `runtime_status`
4. `confirm_capture_context`
5. `get_context_recovery`
6. `get_context_next_action`
7. `decide_context_next_action`
8. `record_action_result`
9. `assemble_global_ai_context`
10. `get_evidence_backed_understanding`
11. `decide_understanding_feedback`

真实输入模式下，第 10、11 项可以返回固定的“真实模型未启用／不可用”状态，但不得消费真实文本、创建 Understanding／Feedback 或调用 synthetic adapter；前九项不得扩大 DTO、路径或通用查询能力。

### 7. 禁止范围

- 禁止读取或接触 `LifeOS-Self-Use-Pilot-1`、`LifeOS-Self-Use-Pilot-2`、其他 Pilot、真实文件、既有 DB、其他目录或历史 Runtime 根。
- 禁止 clear/delete、export、权限设置、恢复、迁移、备份、搜索／FTS、网络、同步、多设备、云／第三方、真实模型、Agent、Vault、凭据、外部 Source、Health 真实数据或跨领域推断。
- 禁止第十二项 IPC、generic SQL/path command、任意路径选择器、通用文件读取、shell bridge 或调试导出。
- 禁止工程／评审 Agent 代替用户输入、查看、转录、截图或复述真实文本。
- 禁止修改 P3-132 及历史资产、关闭／重开现有风险、冻结候选／Runtime／Schema/API／产品资产、恢复工程基线或进入 Stage 4。

### 8. Acceptance Contract

| ID | 不变量／验收结果 | 验证方式 | 必须 Evidence |
|---|---|---|---|
| AC-01 | P3-132 候选和历史资产精确只读继承 | Manifest 路径／bytes／hash／类型重算 | source lineage + history integrity |
| AC-02 | 工程根、临时根、真实自用根三类写入边界互不混淆 | preflight + write inventory | boundary inventory |
| AC-03 | 真实根仅允许精确规范目录；链接链、相对路径、父目录、已有 DB、非普通文件均写前停止 | 独立合成 mutation | per-case no-write proof |
| AC-04 | actual Tauri 恰好十一 IPC，无 generic path/SQL/file/network 能力 | source/capability/runtime inventory | command inventory |
| AC-05 | 真实模式下最多 3 条、每条不超过 200 字符；超限或第 4 条写前拒绝 | 合成等价负例；真实运行仅记计数 | structured limit results |
| AC-06 | 真实文本不进入日志、Evidence、截图、hash、audit payload、ModelPort、synthetic adapter 或外部进程 | taint marker 合成测试 + source/runtime assertions | leak scan + adapter-call count |
| AC-07 | Capture 持久化后仅由用户显式确认进入 Context／Action；无静默确认 | actual Tauri 合成预评 + 用户操作收据 | lifecycle chain |
| AC-08 | Today Focus 为 0 或 1，且只来自已确认开放 Action；真实模型未启用时无 noticed | UI/IPC/DB 非内容状态核对 | Today state receipt |
| AC-09 | 关闭重开后记录数、内容身份、Context／Action／Today 状态一致且不复制 | pre/post non-content state | restart receipt |
| AC-10 | 失败路径在 DB／文件／日志变化前停止，哨兵与状态不变 | mutation + before/after hash | fail-closed matrix |
| AC-11 | 独立评审只用全新合成 DB，覆盖实际 bundle、路径边界、隐私和重启；不得访问真实根 | fresh isolated review | independent review + Manifest |
| AC-12 | 只有独立评审 Pass 后才允许真实自用运行；真实根和 DB 首轮保留且不清理 | ordered action log + exact inventory | gate receipt + retained-state receipt |

Pass 公式：AC-01～AC-12 全部 PASS；P0/P1/Unknown/Not Implemented 为 0；真实文本零泄露；独立评审 Pass；没有合同外目录、DB、IPC、网络、模型、删除或导出动作。非阻断 P2 必须有明确事实和不影响唯一用户结果的理由。

### 9. Evidence 与独立评审

- 本任务采用 `L3`。
- 工程 Evidence：逐行结果、Manifest、P3-132 history hash、路径与文件类型 mutation、taint-marker 泄露测试、失败前后 hash、实际 bundle/run 身份、合成 DB 生命周期、精确临时清理。
- 独立评审：在同一 P3-133 任务号下由全新隔离评审会话执行，只读候选与工程 Evidence，仅使用 `lifeos/reviews/LIFEOS-P3-133/`、`/private/tmp/lifeos-p3-133-independent-review-v1` 和全新合成 DB；不得访问或检测真实自用根。
- 真实运行 Evidence：只记录非内容型收据；真实目录和 DB 保留，不进入工程或独立评审 Manifest。
- PM 必须先验收独立评审，再允许合同内已授权的真实运行步骤继续；这不是新的用户授权门。

### 10. 清理、停止与新任务触发器

- 工程临时根和独立评审临时根分别按精确绝对路径清理；禁止 glob、`find` 和宽前缀删除。
- 真实自用根和 DB 首轮必须保留；不得清理。
- 任一真实文本泄露可能性、候选/history mismatch、独立评审非 Pass、真实根预先存在且非空、DB 已存在、需要真实模型／网络／新 IPC／导出／删除／权限／恢复时立即停止。
- 同合同实现、测试、Evidence、Manifest、视觉接线和失败关闭缺陷留在 P3-133 Closure Cycle，不拆微任务、不重复授权。
- 只有用户结果、真实目录、数据类型、入口、权限、风险、架构、Schema/API、核心语义或冻结合同变化，或历史污染无法可信恢复时关闭并新建任务。

## 输入与最小启动包

必须读取：

- 根目录 `AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/architecture/LifeOS架构基线V1.0.md`
- `lifeos/engineering/LIFEOS-P3-132/evidence/FINAL_MANIFEST.json`
- `lifeos/reviews/LIFEOS-P3-132_pm_review.md`
- `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`
- Frozen 后的 `lifeos/tasks/LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop_acceptance_basis_freeze.md`

独立评审会话另需读取 `lifeos/PM_OPERATING_MODEL.md`、`lifeos/ROLE_MATRIX.md`、`lifeos/STAGE_GATES.md` 中真实能力启用、独立性、风险和 Stage 相关章节。仅在冲突时定向补读历史，不全文扫描无关资产。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop.md`
- 候选：`lifeos/engineering/LIFEOS-P3-133/candidate/`
- 工程 Evidence：`lifeos/engineering/LIFEOS-P3-133/evidence/`
- 独立评审：`lifeos/reviews/LIFEOS-P3-133/independent_review.md`
- PM Review：`lifeos/reviews/LIFEOS-P3-133_pm_review.md`
- 真实运行目录：首轮保留，不作为交付物或 Evidence 资产

## PM 验收与用户关卡

- PM 只按长期质量原则、本 Task Contract 和 Frozen ABF 验收，不移动终点。
- P3-133 是 L3 真实能力启用任务：必须完成强制独立评审；PM Pass 后仍等待用户最终关卡确认，不能自动 Complete。
- Pass 不等于真实模型、网络、Health、同步、导出、删除、风险关闭、资产冻结或 Stage 4 准入。

## 一次性授权方式

Task Contract 已获一次性确认，`ABF-P3-133-v1` 已冻结，任务为 Ready。当前尚未创建真实目录、DB、工程候选、Evidence 或独立评审。将本最终任务卡绝对路径投递至工程会话即执行，不再重复确认合同内边界。
