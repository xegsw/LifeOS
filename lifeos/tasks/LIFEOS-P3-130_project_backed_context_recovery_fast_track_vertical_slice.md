# LIFEOS-P3-130｜Project-backed Context Recovery Fast Track 垂直切片

## 任务信息

- 任务 ID：`LIFEOS-P3-130`
- 风险等级：`L2`
- 优先级／缺陷严重性：`P0`
- 状态：`Ready / User Boundary Confirmed / Awaiting Task-card Delivery`
- 主责 Agent／会话类型：Codex 工程执行会话；完成后由另一个全新隔离会话在同一任务号下独立复评
- 所需执行能力：本地文件、Rust／JavaScript、SQLite、离线 actual Tauri、五项严格 IPC、合成数据、结构化 Evidence
- 是否需要独立评审：`Mandatory within the same task, separate session`
- 触发理由：候选新增两项 Tauri IPC 并形成首个 Context／Memory 持久闭环；不拆出新的微型评审任务号
- 适用治理：Governance V2 结果级任务；L2 内嵌 Acceptance Contract，不另建 ABF
- 用户边界确认：2026-08-26，用户明确确认并启动P3-130，同意任务卡内合成离线actual-Tauri、固定五IPC、唯一工程／临时根及全部禁止边界

## 授权与安全语境

> LifeOS 是用户本人拥有并授权维护的本地项目。本任务只使用工作区任务根、唯一固定 `/private/tmp` 根、全新合成 DB 与固定非敏感文本；不访问 Pilot、真实个人数据、真实 DB／路径／文件、网络、云、第三方、凭据、Vault、模型或 Agent，不扩大攻击能力。

本任务卡只等待一次合并边界确认。确认后即覆盖：候选复制、实现、构建、actual Tauri 动态验证、五项 IPC、SQLite／audit 核对、同范围修正、Evidence／Manifest、PM 验收以及同任务号下的全新隔离独立复评；合同内不再拆分确认。

## Task Contract

### 1. 唯一用户结果

在保持现有 Person-centered Tauri Shell 与三项 Runtime IPC 兼容的前提下，用固定合成数据完成第一个可重启恢复的 Context Recovery 闭环：

`捕获不可变原文 → 显式确认关联预置 Work / Project-backed Context → 关闭重开 → Today／Context／Memory 查看可追溯链路 → Context Inspector 临时移除且不改变持久事实`

用户必须能看见关联尚未确认、已确认、证据不足或权限失效等真实状态；系统不得静默创建 Context、替用户确认或用 UI fixture 冒充领域持久化。

### 2. 固定输入

- Frozen 架构权威：`lifeos/architecture/LifeOS架构基线V1.0.md`，SHA-256 `1d7d82d2afcf7ac52b15730f4f8d3effc08f8965d0b085c6a53bbd2611ad7236`
- P3-128 Fast Track handoff：`lifeos/architecture/LIFEOS-P3-128/fast_track_handoff.json`，SHA-256 `4e15c8006275b10058d6c307a35ac4e04ebcb63e59a249ed0eaf09962eefd3fd`
- P3-126 当前合成候选与历史 Evidence：全部只读；Final Manifest SHA-256 `9b9df14db36eee2d31b9869527a46368de1b3e66e65e90b78eb893c6a86342c8`
- 物理多行 source allowlist：`lifeos/tasks/LIFEOS-P3-130_source_allowlist.md`，75行，SHA-256 `71dc5675d153c8a240ff59b7dcbcc17576e6eed41c6ceb969a44378be9aaad80`
- P3-129候选、独立评审、PM Review和最终promotion Evidence：全部只读

任一固定输入 hash、物理行数或路径不一致时，在复制或工程动作前 fail closed 回报 PM；不得自行改写 allowlist 或换用其他 UI／Runtime 来源。

### 3. 允许范围

- 工程会话允许写入：
  - `lifeos/engineering/LIFEOS-P3-130/`
  - `lifeos/deliverables/LIFEOS-P3-130_project_backed_context_recovery_fast_track_vertical_slice.md`
  - `/private/tmp/lifeos-p3-130-context-recovery-v1`
- 独立复评会话仅允许写入：`lifeos/reviews/LIFEOS-P3-130/independent-review/`
- PM 会话允许写入：P3-130 PM Review／PM Evidence及项目账本。
- 候选根：`lifeos/engineering/LIFEOS-P3-130/candidate/`
- Evidence根：`lifeos/engineering/LIFEOS-P3-130/evidence/`
- 唯一临时根：`/private/tmp/lifeos-p3-130-context-recovery-v1`
- Runtime根由构建时`LIFEOS_RUNTIME_ROOT`显式绑定到唯一临时根下的每个全新 run 子目录；不得存在默认、回退或历史根。
- 允许actual Tauri离线启动、UI导航／点击／输入固定合成文本、五项IPC、SQLite／audit只读核对、关闭重开和任务内构建缓存。
- 仅可从P3-130 source allowlist复制75个P3-126候选文件；P3-126及此前资产保持只读。

### 4. 固定合成数据

- Person ref：`person:synthetic-owner`
- Domain view：`work`
- Project ID：`synthetic-lifeos-product`
- Context ID：`ctx:project:synthetic-lifeos-product`
- 捕获文本：`整理 LifeOS Context Recovery 合成验收记录。`
- capture key：`p3-130-capture-001`
- confirm idempotency key：`p3-130-confirm-001`
- DB：每个 run 使用全新 `capture.sqlite`，仅位于对应 task-local Runtime 根内

不得增加或替换真实文本、真实标识、真实路径或其他数据集。

### 5. IPC与实现边界

候选实际暴露的Tauri command必须恰好为以下五项：

1. `capture_record`：保持现有严格`{text,key}`请求和响应兼容。
2. `get_today`：保持严格空请求和既有字段兼容；只允许兼容追加Context Recovery摘要。
3. `runtime_status`：保持严格空请求和现有离线／拒绝字段；只允许追加固定feature flags。
4. `confirm_capture_context`：严格`{capture_id,context_id,decision:confirm|reject,idempotency_key}`；只处理显式关联反馈。
5. `get_context_recovery`：严格`{context_id}`；返回一个Project-backed Context及Memory provenance DTO。

实现必须遵循Frozen V1.0的`UI → Application → Domain → Ports → Adapters`：UI／Orchestrator不得直连SQL、文件系统、网络、ModelPort或AgentPort。Context ID由Project投影得到，不新增通用Context核心实体或表；MemoryItem只返回引用、状态与provenance，不复制成第二份原文。

允许在候选内部新增或调整未冻结的SQLite实现细节：一个合成Project backing、typed capture-project link、append-only confirmation Feedback和最小Audit事件；这些变化不得被声明为Schema/API冻结。

### 6. 禁止范围

- 禁止任何第六项IPC、generic SQL／path command、`create_context`、clear/delete、export、recovery、sync、网络、模型或Agent调用。
- 禁止Pilot、真实DB／路径／文本／文件、Vault、外部Source、云／第三方、凭据、向量／FTS、健康推断或新Domain激活。
- 禁止通用Context表、Person Profile表、Domain ACL、Memory正文副本或AI画像。
- 禁止重新设计P3-126 Shell：保持纯图标Rail、现有DOM/CSS/Token、留白、字号、色彩和Global AI空间关系；只做闭环所需的最小状态与交互接入。
- 禁止修改P3-126/P3-127/P3-128/P3-129及更早任务、候选、Review、Evidence、Manifest或历史临时根。
- 禁止冻结Schema/API、IPC签名、Runtime、工程基线、产品IA、风险或Stage；禁止进入Stage 4或自动创建后继任务。
- 禁止调整macOS显示缩放、辅助功能或其他系统设置。

### 7. Acceptance Contract

| ID | 不变量／验收结果 | 验证方式 | 必须Evidence |
|---|---|---|---|
| AC-01 | 75个源文件按物理allowlist复制且历史只读 | before/after SHA-256 | source lineage + history integrity |
| AC-02 | 既有三IPC、root fail-closed和零renderer plugin permission保持兼容 | strict DTO、配置负例、现有生命周期重放 | structured results + logs |
| AC-03 | capture保存不可变合成原文和Source身份；重复key幂等 | actual Tauri IPC + adapter读取 + audit | action row + DB/audit snapshot |
| AC-04 | 关联在显式决定前保持candidate；不得静默创建／确认Context | UI→IPC→DB/audit正负路径 | before/after state chain |
| AC-05 | 只有`confirm_capture_context`可产生confirmed typed Link与append-only Feedback；confirm/reject幂等且冲突关闭 | actual Tauri与三类冲突测试 | action rows + mutation results |
| AC-06 | 关闭重开后Today／Context／Memory恢复同一Project-backed链路 | actual App close/reopen，不以refresh替代 | PID/run log + UI/IPC/DB/audit correlation |
| AC-07 | Memory detail回链Source、Artifact/version、Link、Feedback、Audit；不复制原文权威 | DTO及持久状态核对 | provenance JSON + visible state |
| AC-08 | Context Inspector只预览Person+Page+Selection；临时移除不持久化、不调用Model/Agent | before/remove/reopen | resolver rows + unchanged durable hash |
| AC-09 | Source／版本／generation／tombstone／Authorization／Evidence任一失效均显示缺口且不返回可靠建议 | 至少三类独立mutation | no-write DB/audit/sentinel proof |
| AC-10 | unknown字段、非法ContextId、capture不匹配、duplicate-key conflict在任何DB／audit变化前停止 | pristine disposable negative controls | before/after hash + structured errors |
| AC-11 | 实际command恰好五项；UI／resolver无SQL、filesystem、network、Model或Agent路径 | source scan + runtime/capability assertion | inventory + runtime_status |
| AC-12 | actual Tauri关键动作具有逐行Evidence，不以静态截图或单元测试替代 | capture→candidate→confirm→reopen→provenance | dynamic closure matrix |
| AC-13 | 唯一临时根精确清理，工程Evidence保留，历史资产不变，Manifest非自指 | pre/post inventory + exact path check | cleanup.json + Final Manifest |

Pass公式：AC-01～AC-13全部PASS；P0/P1/Unknown/Not Implemented为0；P2只能是有明确理由且不影响唯一用户结果的非阻断项；独立复评Pass；无越权路径、真实数据、隐藏IPC、历史漂移或未解释状态。

### 8. Evidence合同

- Evidence等级：`L2+ actual Tauri`。
- 必须保留：可运行runner、单元／集成测试、actual-app action log、逐行dynamic closure、严格DTO结果、DB／audit快照、失败前后hash、mutation results、source lineage、history integrity、cleanup和非自指Final Manifest。
- actual App证据必须关联同一run中的UI状态、IPC请求／响应、SQLite／audit事实与关闭重开；截图仅证明可见状态，不单独证明持久化。
- 至少覆盖：首次、重复／幂等、confirm、reject／冲突、关闭重开、临时移除、三类失效mutation、非法字段／Context、空白全新DB和精确清理。
- 执行侧提交前必须自检并报告`P0/P1/P2/Unknown/Not Implemented`。

### 9. 清理与历史保全

- `/private/tmp/lifeos-p3-130-context-recovery-v1`在Evidence完成后必须按精确绝对路径清理并确认absent；不得使用glob、`find`或宽前缀删除。
- 只清理本任务自己创建的临时根；不访问、stat、hash、create或cleanup任何历史Runtime根。
- `lifeos/engineering/LIFEOS-P3-130/`、交付物、Evidence和Manifest保留供PM验收；不得覆盖工程Evidence。

### 10. 新任务／停止触发器

以下任一情况立即停止并回PM，不在P3-130内扩大：需要新增Frozen核心对象或通用Context表；改变Project语义；改变Frozen V1.0、产品IA、AI授权或V1范围；冻结Schema/API；使用真实数据／路径／能力；增加IPC；访问网络／模型／Agent；无法建立actual App的UI→IPC→SQLite/audit→UI关联。

同一合同内的实现缺陷、测试、Evidence、Manifest、视觉接线和文案一致性直接包内修正；不拆微型任务、不重复授权。

## 一次性确认与投递

用户只需一次确认以下整体边界：P3-130仅使用`lifeos/engineering/LIFEOS-P3-130/`、指定交付物、`lifeos/reviews/LIFEOS-P3-130/independent-review/`及`/private/tmp/lifeos-p3-130-context-recovery-v1`；只读复制P3-126 allowlist 75文件；仅使用固定合成DB／文本和上述五项IPC进行离线actual Tauri闭环；禁止所有真实数据／路径、历史Runtime根、网络、模型、Agent及其他能力。

确认后，向工程专项会话投递本任务卡绝对路径即构成完整执行授权，不再需要逐项确认。独立复评由另一个新会话执行，但沿用同一任务号与已确认边界。

## 输入与最小启动包

必须完整读取：

- 根目录`AGENTS.md`
- `lifeos/CURRENT_STATUS.md`
- 本任务卡
- `lifeos/tasks/LIFEOS-P3-130_source_allowlist.md`
- `lifeos/architecture/LifeOS架构基线V1.0.md`
- `lifeos/architecture/LIFEOS-P3-128/fast_track_handoff.json`
- `lifeos/architecture/LIFEOS-P3-128/application_port_contract.json`
- `lifeos/architecture/LIFEOS-P3-128/context_resolver_contract.json`
- `lifeos/architecture/LIFEOS-P3-128/memory_provenance.json`
- `lifeos/architecture/LIFEOS-P3-128/negative_cases.json`
- `lifeos/deliverables/LIFEOS-P3-128_person_context_memory_core_domain_mapping_and_fast_track_engineering_contract.md`
- `lifeos/reviews/LIFEOS-P3-128_pm_review.md`
- `lifeos/deliverables/LIFEOS-P3-126_p3_125_current_candidate_clean_start_acceptance_lineage_rebuild.md`
- `lifeos/reviews/LIFEOS-P3-127_pm_review.md`
- `lifeos/templates/UI_DYNAMIC_EVIDENCE_CLOSURE_TEMPLATE.md`

只在发现直接冲突时定向补读P3-126／P3-127结构化Evidence；不得全文扫描无关历史。

## 交付物

- 主交付物：`lifeos/deliverables/LIFEOS-P3-130_project_backed_context_recovery_fast_track_vertical_slice.md`
- 候选：`lifeos/engineering/LIFEOS-P3-130/candidate/`
- Evidence：`lifeos/engineering/LIFEOS-P3-130/evidence/`
- 独立复评：`lifeos/reviews/LIFEOS-P3-130/independent-review/`
- PM Review：由PM主会话在提交后创建
- 复跑：执行侧与独立评审侧各提供一条不写入历史资产的task-local命令

## PM验收与关闭

- PM同时验收候选、actual Tauri Evidence和独立复评。
- 通过后按Governance V2自动`Accepted / Complete / Not Frozen`，无需再次逐任务采纳。
- 任务Pass不恢复工程基线、不关闭风险、不启用真实能力、不准入Stage 4；后继任务由PM另行规划。
