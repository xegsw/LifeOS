# LIFEOS-P3-094｜PM 验收 Review

## 验收信息

- 任务 ID：LIFEOS-P3-094
- 是否为受控能力包：Yes（真实本地 SQLite／用户主动输入窄边界）
- 专项交付物路径：`lifeos/deliverables/LIFEOS-P3-094_final_invariant_closure.md`
- PM Review 路径：本文件
- 执行授权证据核验：交付物记录 D-0398 最终收口任务卡于 2026-08-22 20:20:51 CST 投递至新的隔离 Codex 工程会话；该会话未承担 P3-095 独立评审，授权范围、精确接收时间、模型与修改目录均符合任务卡。
- 任务验收状态：Closed — Acceptance Not Met / Superseded by LIFEOS-P3-096
- 资产冻结状态：Not Applicable / Not Frozen
- 是否允许进入下一任务：Yes，仅允许 P3-096；P3-094 不得继续 attempt-10
- 是否允许进入下一阶段：No
- 实际执行 Agent：Codex；匹配度：Medium（完成统一路径与 canonical Schema 主体，但遗漏 post-commit cleanup 原子性、审计语义和逐行 Evidence 实际执行）
- 更新时间：2026-08-22

## 最新 PM 总结（Final Invariant Closure / D-0399）

1. attempt-9 提交 Manifest 24/24、源码 6/6、历史只读资产 185/185 hash 一致；PM 在全新 `/private/tmp` 复跑提交 runner 为 107 PASS / 0 FAIL，unit 41 PASS，适配回归 attempt-6／7／8 为 19／13／18 PASS，临时夹具已清理。
2. attempt-8 的 Schema 约束／非法来源 P1 已关闭，统一路径 gate、canonical Schema、行级来源与主体生命周期实现均可复核。
3. PM 反例发现 P1-1：capture 已 commit／发布 DB 后清理旧页面 staging 持续失败时返回 `CaptureError`，但既有 DB 已从 1 条变 2 条并留下 staging；新 DB 场景也会在报告失败后留下已提交 DB。
4. PM 反例发现 P1-2：未来 `capture_saved`、早于保存的 `capture_repeat` 和伪造 clear count 均被接受，审计时间与清理计数只满足格式、未满足语义一致性。
5. P1-3 为 Evidence 冲突：runner 以整个 unit suite 退出码批量把多个强制矩阵行标 PASS；来源全变体、重复身份、capture／clear commit 与 post-commit cleanup 等必测行未独立执行，却报告 107/107、Not Implemented=0。PM 记一个聚合 Not Implemented。
6. 结论仍为同一 P3-094 能力包 Rework；P0=0、P1=3、P2=0、Unknown=0、Not Implemented=1。不进入独立复评，R-0051 保持 P0 / Open，资产继续 Not Frozen。本地模型预检因高风险最终判断跳过。

## Attempt-1 历史 PM 总结（D-0380）

1. 离线实现、固定非敏感自检、Manifest hash 与历史只读资产核对可复核；PM 在隔离副本复跑 14 PASS / 0 FAIL、退出码 0。
2. 交付物如实报告 Chrome 将本地页面输入解析为 Google 搜索 URL，并按任务卡立即停止；这是外部访问边界事件，不能视为动态验证通过。
3. PM 另发现测试夹具泄露 task-local 残留：当前系统临时目录可见 15 个 `lifeos-p3-094-test-*` 目录，均含 SQLite，4 个另含 `today.html`。内容为固定非敏感测试文本，但“全部 task-local DB／页面清理”的合同未满足。
4. 这两个问题均在原任务卡允许的目录、能力、数据与验收矩阵内修复；不得新建微型任务，也不得扩大到既有个人数据、网络、云、Tauri/IPC、导出或外部用户。

## 受控能力包关卡

- 交付前自检：不通过。执行侧离线 14 PASS，但未检出单元测试残留，且动态 Chrome 验证在边界事件后停止。
- 首次／幂等／重启：离线自检通过。
- 原子失败／拒绝／fail-closed：离线自检通过；真实残留清理验证不通过。
- 验收矩阵、runner、结构化结果、日志、hash 与 Manifest：离线部分完整；动态浏览器项未实现。
- 历史只读资产与禁止能力关闭态：执行侧 hash 可复核；源码静态检查未发现禁用集成。
- P0/P1/P2/Unknown/Not Implemented：0 / 2 / 0 / 0 / 1。
- 独立评审：尚不得进入；原任务完成后仍需一次全新隔离独立复评。

## 整改要求（同一 P3-094，不新建任务号）

1. 修复测试夹具，确保每次测试与自检均清理其创建的 SQLite、HTML 与父目录；以可复核结果证明运行前后不存在 `lifeos-p3-094-*` 残留。
2. 在用户确认后，仅删除已核验为固定非敏感 P3-094 测试产物的 15 个精确临时目录；不得使用宽泛删除命令，亦不得触碰既有文件或数据库。
3. 以任务卡已指定的 Google Chrome Computer Use 合规 `file:` 入口完成预检和动态验证；不得输入搜索查询、不得联网、不得使用 HTTP/CDP/替代浏览器或规避路径。若两次正常直接 `file:` 预检均失败，保留记录并按任务卡判断 Blocked。
4. 将本次事件 Evidence 只读保留；新 Evidence 写入同一任务的 `rework/attempt-2/`，不得覆盖 attempt-1。

## 资产、风险与关卡

- 不冻结 P3-094 资产；不关闭或重开既有风险，不恢复工程基线，不进入 Stage 4。
- 新增 R-0051 为 Open，记录真实本地能力中“临时数据残留与本地浏览器误导航”风险；其关闭须在未来独立任务、独立复评与用户确认中判断，不能由本 Rework 自动关闭。
- P3 Engineering Fast Lane 不适用：任务涉及真实本地 DB／数据边界。

## 需要用户确认

请确认是否采纳本次 Rework，并允许在**同一 P3-094 任务**内仅处理上述 15 个已核验的固定非敏感测试临时目录、修复清理逻辑并以任务卡允许的 Chrome `file:` 路径重跑。该确认不扩大数据、文件、网络、云、Tauri/IPC、导出、风险、冻结或阶段范围。

---

## Attempt-2 PM 复核（D-0382）

### 验收结论

`Rework / Awaiting User Confirmation`。attempt-2 的离线清理整改可复核：结构化 runner 13 PASS / 0 FAIL，当前未见 `lifeos-p3-094-*` 临时残留，attempt-1 Evidence 未被覆盖。但 Chrome 动态 Evidence 不可采纳。

### 原因

- `dynamic_blocked.md` 与 `README.md` 均写明动态矩阵为 `NOT IMPLEMENTED / Blocked`；交付物、`dynamic_closure.md` 与 Manifest 却写 PASS，形成直接 Evidence 冲突。
- 无可运行的动态 Chrome runner、会话／时间链或完整操作日志，无法将三张截图可靠绑定到声称的合规步骤。
- Manifest 漏列 `dynamic_blocked.md`、`visual/01-today-page.png` 及多项实际 Evidence；`run_attempt_2.py` 重跑还会删除 attempt-2 Evidence 目录，不能作为保全型复跑入口。

### 计数与边界

- P0=0；P1=1（Evidence 冲突／不可复核）；P2=0；Unknown=0；Not Implemented=1（动态闭环）。
- 不得进入独立复评、用户采纳、冻结、风险关闭、基线恢复或 Stage 4。R-0051 继续 Open。

### 同一能力包的后续整改（须用户确认）

不新建任务号。只允许在新隔离工程会话内，保留 attempt-1 和 attempt-2 全部现有资产，只新增 `rework/attempt-3/`：使用不会覆盖既有 Evidence 的可运行动态 runner，逐项记录 Chrome `file:` 预检、操作、时间、结构化结果、截图／日志和全量 Manifest hash；动态未实际完成时必须报告 Blocked，不得同时保留相互矛盾的 PASS 文案。

---

## Attempt-3 PM 复核（D-0384）

### 验收结论

`Accepted / PM Pass / Awaiting User Adoption`。

### 测试与 Evidence

- 离线前置 7 PASS / 0 FAIL、退出码 0；首次捕获、幂等、重启复读、今日页渲染、空输入拒绝与运行前残留为零均成立。
- Chrome 动态闭环 5 PASS / 0 FAIL；PM 逐张抽查 `file:` 预检、成功今日页、空输入拒绝页和关闭标签截图，内容与结构化结果一致。
- attempt-3 的 14 个非 Manifest 文件全部纳入清单，PM 复算 SHA-256 全部一致；source、attempt-1 Manifest、attempt-2 Manifest hash 保持一致。
- attempt-3 runtime 已删除，系统临时 `lifeos-p3-094-*` 残留为零。P0/P1/P2/Unknown/Not Implemented 均为 0。

### 状态边界

- P3-094 当前 hash 在固定非敏感文本、新建 task-local SQLite、Chrome 本地 `file:` 展示和清理范围内通过 PM 验收。
- P3-094 资产继续 Not Frozen；R-0051 保持 Open；不恢复工程基线、不关闭风险、不进入 Stage 4。
- 等待用户是否采纳 PM Pass。用户采纳后，才可创建一次全新隔离独立复评；不得自动创建。
- 本地预检未调用：本轮是涉及真实本地数据边界的 P0 最终 PM 判断，且局域网调用不应替代人工 Evidence 复核。

### 用户采纳与后续（D-0385）

用户已采纳 attempt-3 PM Pass，并授权继续创建 P3-095 全新隔离独立复评。该采纳不冻结 P3-094、不关闭 R-0051、不恢复工程基线，也不构成 Stage 4 准入。

---

## Attempt-4 PM 复核（D-0388）

### 验收结论

`Accepted / PM Adjusted to Rework / Awaiting User Confirmation`。

### 测试与 Evidence

- PM 使用独立 `/private/tmp` Evidence 目录复跑 attempt-4 runner：13 PASS / 0 FAIL、退出码 0；临时目录已精确清理。
- attempt-4 Manifest 的 14 个非自指文件及历史只读清单的 56 个文件 hash 全部一致；attempt-1／2／3 与 P3-095 资产未被覆盖。
- 正常 task-local 正向和失败注入路径成立：旧页面先失效，随后清空 DB；页面删除失败时 DB 保持一条记录。
- PM 反例通过运行时 API 与公开 CLI 稳定证明：把 DB 父目录外的固定非敏感哨兵文件作为 `output_path`／`clear --output` 后，哨兵被删除、DB 被清空、操作返回 `cleared`。

### 计数与关卡

- P0=1；P1=0；P2=0；Unknown=0；Not Implemented=0。
- Gate 2、Gate 4：不通过；存在越出 task-local 授权范围的不可逆文件删除能力。
- Gate 3：禁止网络／AI／外部处理的静态关闭态未见变化，但不能抵消删除边界 P0。
- 不得进入新的独立复评、冻结、风险关闭、基线恢复或 Stage 4。

### 同一能力包整改要求

如用户采纳，不创建新任务号，仅回到 P3-094：

1. `delete_all()` 的页面目标必须被强制绑定为 DB 同一父目录下的精确 `today.html`；任何其他文件名、父目录、绝对／相对绕路或解析后不等价路径均须在文件与 DB 变更前拒绝。
2. CLI 应移除 `clear --output` 的任意路径能力，或只接受并验证与上述唯一内部路径完全等价的值；不得依赖调用者自觉遵守范围。
3. 增加 DB 外固定非敏感哨兵反例：操作必须失败，哨兵仍存在且内容不变，DB 记录保持不变；同时覆盖相对路径规范化与符号链接边界。
4. 新 Evidence 必须保全 attempt-1／2／3／4 和 P3-095，只记录固定非敏感内容；完成后重新 PM 验收。PM Pass 与用户采纳后，仍须另一全新隔离独立复评。

### 状态边界

- P3-094 继续 Not Frozen；R-0051 保持 Open，并纳入本次 task-local 删除目标失界事实。
- 不恢复工程基线、不冻结 Schema/API、不进入 Stage 4，不扩大到既有个人文件／DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 用户已采纳本次 Rework；后续仅执行 D-0389 授权的同一 P3-094 attempt-5，不得扩大范围。

### 用户采纳与后续（D-0389）

用户已采纳 D-0388 Rework。P3-094 继续同一任务号执行 attempt-5：只允许把页面删除目标强制绑定到 DB 同目录的精确 `today.html`，拒绝 DB 外路径、非标准文件名、规范化绕路、符号链接与特殊文件，并补文件和 DB 均保持不变的负向回归。该采纳不关闭 R-0051、不冻结资产、不恢复工程基线、不进入 Stage 4，也不授权真实文件、既有个人 DB、网络、云、Tauri/IPC、Vault、导出或外部用户。

---

## Attempt-5 PM 复核（D-0390）

### 验收结论

`Accepted / PM Adjusted to Rework / Awaiting User Confirmation`。

### 授权、会话与修改范围

- attempt-5 的任务卡重新投递、接收时间和实际会话复用记录完整；复用的是已结束 attempt-4 且未承担 P3-095 独立评审的工程会话，符合 D-0389。
- 工程修改仅落在任务卡允许的运行时、CLI、测试、README 与 attempt-5 runner／Evidence；PM 未修改工程代码，也未覆盖 attempt-1／2／3／4、P3-095 或既有工程 Evidence。
- 在写入本次 PM 结论前，attempt-5 提交 Manifest 15 项、source hash 5 项与 historical read-only hash 80 项均由 PM 复算一致。完成授权的 PM Review／账本更新后再次复算为 79/80；唯一差异是本次必须更新的 `reviews/LIFEOS-P3-094_pm_review.md`，其提交前 hash 为 `d43d2e...eae56`，更新后 hash 见 PM Evidence；其余 79 项（含 attempt-1／2／3／4、P3-095 与既有 PM Evidence）保持一致。

### 测试与 Evidence

- PM 使用提交 runner 在全新 `/private/tmp/lifeos-p3-094-attempt-5-*` 工作目录、固定非敏感文本与哨兵复跑：18 PASS / 0 FAIL、退出码 0；运行期 DB、HTML、哨兵、链接、FIFO、缓存与父目录均已清理，工程 Evidence 未覆盖。
- PM 反例入口：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-5/pm_boundary_counterexamples.py`；结构化结果：同目录 `pm_boundary_counterexamples.json`；反例 0 PASS / 4 FAIL。
- P0-1（render 本地目录／文件类型边界）：运行时 API 与 CLI 均成功把 DB 目录外固定哨兵覆盖为今日页；同目录输出文件为符号链接时，运行时跟随链接并改写目标。三条路径均未在文件变更前拒绝。
- P0-2（clear 目录链接链）：DB 的直接父目录为普通目录、但更上层祖先为目录符号链接时，`delete_all()` 返回 `cleared`，真实目标页面被删除且 DB 记录由 1 变为 0。当前检查不覆盖完整路径组件链。
- PM 临时夹具均位于新建 `/private/tmp` 目录，反例结束后精确清理；未读取真实文件内容、既有个人 DB、凭据或外部目标，未联网。

### 计数与关卡

- P0=2；P1=0；P2=0；Unknown=0；Not Implemented=0。
- Gate 2、Gate 4：不通过。生命周期文件边界仍可越出 task-local 目录，且目录链接链未在文件／DB 变更前 fail closed。
- Gate 3：网络、云、Tauri/IPC、Vault、导出及外部处理关闭态未见变化；该关闭态不能抵消两个 P0。
- P3 Engineering Fast Lane：不适用，任务涉及真实本地 DB、文件写入／删除边界与 P0 最终判断。
- 不允许进入下一任务、全新隔离独立复评、风险关闭、工程基线恢复、资产／Schema/API 冻结或 Stage 4。

### 同一能力包整改建议（须用户采纳后另行授权）

1. 将 `render_today()` 的展示目标与 clear 一样由运行时强制绑定为 `db_path.parent / "today.html"`；CLI 移除任意 `render --output`，或仅接受经完整边界验证的唯一等价值。
2. 在 render 写入前验证 DB 路径和页面路径的完整目录组件链、最终文件类型与链接状态；拒绝任何祖先目录符号链接、最终符号链接、目录或特殊文件，不得跟随链接覆盖目标。
3. clear 必须验证从允许的 task-local 根到 DB／页面的完整目录组件链，而不只是直接父目录；任何路径组件为链接或无法确认时，在页面和 DB 变更前拒绝。
4. 补 API／CLI render 外部哨兵、render 最终链接、render 祖先目录链接链、clear 祖先目录链接链负向回归；每项证明返回失败、哨兵／页面 hash 不变、DB 记录不变，并继续保全历史资产和零残留。

### 资产、风险与用户确认

- P3-094 继续 Not Frozen；R-0051 保持 P0 / Open，并补充 render 越界覆盖／链接跟随和 clear 祖先目录链接链事实。
- 不恢复工程基线、不冻结资产或 Schema/API、不进入 Stage 4，不扩大到真实个人文件／既有 DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 需要用户确认：是否采纳 attempt-5 Rework；如采纳，是否授权同一 P3-094 能力包仅按上述四项做下一轮窄整改。确认前不得执行整改或创建独立复评。

### 用户采纳（D-0391）

用户已采纳 attempt-5 Rework 结论。该采纳仅确认 PM 的 P0=2 判断与同一 P3-094 能力包回退状态；未单独明确授权下一轮工程整改。P3-094 保持 Not Frozen，R-0051 保持 P0 / Open；不得修改工程、创建独立复评、关闭风险、恢复基线、冻结或进入 Stage 4。下一轮窄整改须等待用户另行明确授权。

### 用户整改授权（D-0392）

用户已明确授权同一 P3-094 能力包继续窄整改。授权仅覆盖 attempt-6：把 render 绑定到 DB 同目录唯一 `today.html`，为 render／clear 验证完整目录组件链接链与最终文件类型，并补固定非敏感负向回归。不得新建任务号、复用 P3-095 独立评审会话、覆盖历史 Evidence、关闭 R-0051、恢复基线、冻结或进入 Stage 4。任务卡重新投递至符合隔离条件的工程会话即授权执行。

---

## Attempt-6 PM 复核（D-0393）

### 验收结论

`Accepted / PM Adjusted to Rework / Awaiting User Confirmation`。

### 授权、会话与修改范围

- D-0392 已明确授权同一 P3-094 能力包 attempt-6；交付物记录任务卡已投递至新的隔离 Codex 工程会话，且该会话未承担 P3-095 独立评审。执行目录与工程修改范围符合任务卡。
- 交付物仅记录 2026-08-22，未按任务卡记录任务卡投递的精确接收时间，记 P2=1；该元数据缺口不否定 D-0392 已存在的执行授权，但必须在下一轮首份报告补齐。
- PM 未修改工程代码或工程 Evidence；attempt-1／2／3／4／5、P3-095 与既有 PM Evidence 在写入本次 PM 结论前按 104 项历史 hash 全部一致。

### 测试与 Evidence

- PM 使用提交 runner 在全新 `/private/tmp/lifeos-p3-094-attempt-6-*` 工作目录、固定非敏感文本与哨兵复跑：19 PASS / 0 FAIL、退出码 0；运行期 DB、HTML、哨兵、链接、FIFO、缓存与父目录均已清理。
- PM 独立反例入口：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-6/pm_boundary_counterexamples.py`；结构化结果：同目录 `pm_boundary_counterexamples.json`；结果 2 PASS / 2 FAIL。
- 已关闭 P0：render API 越界目标被拒绝且哨兵／页面／DB 不变；render 与 clear 经祖先目录符号链接访问 DB 时均拒绝且真实页面 hash、DB 记录不变。
- P1：固定非敏感旧页面已存在时，直接把 DB 清空或损坏 DB 后调用 render，均返回 `CaptureError`，但旧 `today.html` 仍存在且 hash 不变。失败披露没有让不可验证的旧页面失效，旧内容仍可通过 `file:` 展示。
- P2：执行侧披露一次 `python3 -m py_compile` 尝试写入 task-local 之外的用户缓存目录；操作被权限拒绝且未发现项目／临时残留，但该命令选择越出 attempt-6 允许的写入边界。下一轮只能使用 `-B`、内置 `compile()` 或显式位于 `/private/tmp` 的缓存路径。
- 所有 PM 复跑与反例均只使用新建 `/private/tmp` 固定非敏感夹具；未读取真实个人文件、既有个人 DB、凭据或外部目标，未联网；PM 临时目录已精确清理。

### 计数与关卡

- P0=0；P1=1；P2=2；Unknown=0；Not Implemented=0。
- Gate 2：路径越界和目录链接链整改通过，但旧页面生命周期仍不通过。
- Gate 3：网络、云、Tauri/IPC、Vault、导出及外部处理关闭态未见变化。
- Gate 4：不通过。空／损坏 DB 的 render 失败仍保留可展示旧页面，包内自检矩阵未覆盖该状态组合。
- P3 Engineering Fast Lane：不适用，任务涉及真实本地 DB、文件写入／删除与旧内容展示的高风险最终判断。
- 不允许进入下一任务、全新隔离独立复评、风险关闭、工程基线恢复、资产／Schema/API 冻结或 Stage 4。

### 同一能力包整改建议（须用户采纳后另行授权）

1. 当 render 无法确认 DB 内容有效（包括空 DB、损坏／不可读 DB）时，必须在返回失败前使既有 task-local `today.html` 不可展示；不得留下可继续显示旧内容的页面。
2. 失效操作必须继续使用 attempt-6 已建立的完整目录组件链和最终文件类型门，不得重新引入链接跟随、越界目标或调用方输出路径。
3. 增加空 DB + 旧页面、损坏 DB + 旧页面的固定非敏感回归，证明 render 失败、旧页面不存在或不可展示、DB 状态不被 render 改写；继续保留合法 render、原子发布失败保留当前有效页面、clear 与路径边界回归。
4. 下一轮首份报告记录任务卡投递精确接收时间；所有语法检查和缓存仅限项目目录或新建 `/private/tmp`，不得再次尝试用户缓存目录。

### 资产、风险与用户确认

- P3-094 继续 Not Frozen；R-0051 保持 P0 / Open，并补充“空／损坏 DB 时 render 失败但旧页面继续可展示”的生命周期事实。
- 不恢复工程基线、不冻结资产或 Schema/API、不进入 Stage 4，不扩大到真实个人文件／既有 DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 需要用户确认：是否采纳 attempt-6 Rework。若采纳，下一轮仍返回同一 P3-094 能力包；工程整改须另行明确授权，不自动创建任务或独立复评。

### 用户采纳与整改授权（D-0394）

用户已同时采纳 attempt-6 Rework 并明确授权同一 P3-094 能力包 attempt-7 窄整改。授权仅覆盖空／损坏／不可读 DB 时 render 失败前使旧页面不可展示、保留 attempt-6 路径边界和合法发布语义，并补齐精确接收时间与 task-local 缓存卫生。不得新建任务号、覆盖历史 Evidence、关闭 R-0051、恢复基线、冻结或进入 Stage 4。任务卡重新投递至符合隔离条件的工程会话即授权执行。

---

## Attempt-7 PM 复核（D-0395）

### 验收结论

`Accepted / PM Adjusted to Rework / Awaiting User Confirmation`。

### 授权、会话与修改范围

- D-0394 已同时完成用户采纳和 attempt-7 工程授权；交付物记录任务卡完整路径、2026-08-22 19:39:14 CST 精确接收时间、复用已结束 attempt-6 的工程会话及未承担 P3-095 独立评审。授权和复用条件成立。
- 工程修改仅落在 render 失败旧页面生命周期相关 runtime、测试、README 与 attempt-7 runner／Evidence；CLI 未实质修改。PM 未修改工程代码或工程 Evidence。
- 在写入本次 PM 结论前，attempt-7 Manifest 16 项、source hash 5 项与 historical read-only hash 128 项全部一致。

### 测试与 Evidence

- PM 使用提交 runner 在全新 `/private/tmp/lifeos-p3-094-attempt-7-*` 工作目录、固定非敏感文本与页面复跑：attempt-7 为 13 PASS / 0 FAIL；内嵌 attempt-6 全回归为 19 PASS / 0 FAIL；退出码 0，缓存与临时残留为零。
- PM 独立反例入口：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-7/pm_lifecycle_counterexamples.py`；结构化结果：同目录 `pm_lifecycle_counterexamples.json`；结果 2 PASS / 2 FAIL。
- 已关闭原 P1：已初始化空 DB 与损坏 DB 均在 render 失败前删除旧页面且 DB hash 不变；查询失败、权限不可读与页面失效失败路径由提交矩阵覆盖。
- P1-1（DB 缺失）：同目录仅保留固定非敏感旧页面、DB 文件完全不存在时，render 返回失败，但旧页面仍存在且 hash 不变，DB 保持缺失。该状态仍可通过 `file:` 展示不可验证旧内容。
- P1-2（未初始化空 SQLite）：零字节普通文件通过边界门后，`list_today()` 调用会经 `_connect()` 创建 Schema；render 随后因无记录返回失败并删除旧页面，但 DB 从 0 字节变为 24576 字节。失败路径静默改写 DB，违反 D-0394 的明确 DB 不变合同。
- 精确接收时间已记录；runner 全程 `python3 -B` + 内置 `compile()`，未尝试用户缓存目录，attempt-6 的两个 P2 均已关闭。
- 所有 PM 复跑与反例只使用新建 `/private/tmp` 固定非敏感夹具；未读取真实个人文件、既有个人 DB、凭据或外部目标，未联网；临时目录已精确清理。

### 计数与关卡

- P0=0；P1=2；P2=0；Unknown=0；Not Implemented=0。
- Gate 2：不通过。DB 缺失时旧页面未 fail closed，未初始化空 SQLite 在失败 render 中被改写。
- Gate 3：网络、云、Tauri/IPC、Vault、导出及外部处理关闭态未见变化。
- Gate 4：不通过。包内矩阵未覆盖 DB 缺失和无 Schema 空文件两个完成定义状态。
- P3 Engineering Fast Lane：不适用，任务涉及真实本地 DB、页面生命周期与失败写入的高风险最终判断。
- 不允许进入下一任务、全新隔离独立复评、风险关闭、工程基线恢复、资产／Schema/API 冻结或 Stage 4。

### 同一能力包整改建议（须用户采纳后另行授权）

1. DB 文件缺失但安全 task-local 父目录与普通旧页面可确认时，render 必须先使旧页面不可展示，再返回 DB 缺失失败；不得创建 DB。
2. render 的读取路径必须是只读且不初始化 Schema。零字节、无 Schema 或 Schema 不完整的 SQLite 应返回失败、使旧页面不可展示，并保持 DB bytes／大小／hash 不变。不得通过 `_connect()` 的建表副作用完成读取。
3. 保留 attempt-6／7 已成立的完整目录组件链、文件类型、不跟随链接、合法 render 原子发布、发布失败保留有效页面、clear 顺序和失效失败披露。
4. 增加 DB 缺失 + 旧页面、零字节 SQLite + 旧页面、无 captures/audit Schema SQLite + 旧页面回归；证明 render 失败、旧页面不可展示、DB 不被创建或改写，并继续全量回归与零残留。

### 资产、风险与用户确认

- P3-094 继续 Not Frozen；R-0051 保持 P0 / Open，并补充“DB 缺失旧页面保留”和“失败 render 初始化空 SQLite”的生命周期事实。
- 不恢复工程基线、不冻结资产或 Schema/API、不进入 Stage 4，不扩大到真实个人文件／既有 DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 需要用户确认：是否采纳 attempt-7 Rework。若采纳，下一轮仍返回同一 P3-094 能力包；工程整改须另行明确授权，不自动创建任务或独立复评。

### 用户采纳与整改授权（D-0396）

用户已同时采纳 attempt-7 Rework 并明确授权同一 P3-094 能力包 attempt-8 窄整改。授权仅覆盖 DB 缺失时旧页面失效，以及 render 使用严格只读、不创建／补写 Schema 的读取路径；必须保留 attempt-6／7 全部已成立边界。不得新建任务号、覆盖历史 Evidence、关闭 R-0051、恢复基线、冻结或进入 Stage 4。任务卡重新投递至符合隔离条件的工程会话即授权执行。

---

## Attempt-8 PM 复核（D-0397）

### 验收结论

`Accepted / PM Adjusted to Rework / Awaiting User Confirmation`。

### 授权、会话与修改范围

- D-0396 已同时完成用户采纳和 attempt-8 工程授权；交付物记录任务卡完整路径、2026-08-22 19:56:40 CST 精确接收时间、复用已结束 attempt-7 的工程会话及未承担 P3-095 独立评审。授权和复用条件成立。
- 工程修改仅落在 render 严格只读读取相关 runtime、测试、README 与 attempt-8 runner／Evidence；CLI 未实质修改。PM 未修改工程代码或工程 Evidence。
- 写入本次 PM 结论前，attempt-8 Manifest 16 项、source hash 5 项与 historical read-only hash 155 项全部复算一致；attempt-1 至 attempt-7、P3-095 及既有 PM Evidence 未被覆盖。

### 测试与 Evidence

- PM 使用提交 runner 在全新 `/private/tmp/lifeos-p3-094-attempt-8-*` 工作目录、固定非敏感 DB／页面夹具复跑：attempt-8 为 18 PASS / 0 FAIL；内嵌 attempt-6 全回归为 19 PASS / 0 FAIL；退出码 0，缓存与临时残留为零。
- PM 独立反例入口：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-8/pm_schema_constraint_counterexamples.py`；结构化结果：同目录 `pm_schema_constraint_counterexamples.json`；结果 0 PASS / 2 FAIL。
- 已关闭 D-0395 两个 P1：DB 缺失时旧页面失效且 DB／副文件不创建；零字节 SQLite 的 bytes、大小、hash 与对象清单保持不变。无表、缺表／缺列、空、损坏、不可读及查询失败路径继续 fail closed。
- P1（Schema 完整性与来源）：`_list_today_read_only()` 仅比较 `sqlite_master` 表类型以及 `PRAGMA table_info` 的列名／声明类型，未验证既定 `PRIMARY KEY`、`NOT NULL`、`UNIQUE`、`CHECK(source='local_capture')` 约束或读取行的 `source`。缺全部约束且含外部来源值的 DB、以及仅缺幂等唯一约束的 DB 均被成功 render；前者被静态页面错误标成“来源：本地捕获”。这是任务卡“Schema 不完整必须失败”的明确合同违反，两个夹具归并为一个共同根因 P1。
- 两个 PM 反例的 DB bytes 均保持不变；问题是错误接受与发布，而非只读写入副作用。所有夹具均为本轮在 `/private/tmp` 新建的固定非敏感内容，未读取真实个人文件、既有个人 DB、凭据或外部目标，未联网，临时目录已精确清理。

### 计数与关卡

- P0=0；P1=1；P2=0；Unknown=0；Not Implemented=0。
- Gate 2：不通过。Schema 完整性和数据来源无法确认时仍发布内部页面，未 fail closed。
- Gate 3：网络、云、Tauri/IPC、Vault、导出及外部处理关闭态未见变化。
- Gate 4：不通过。提交矩阵把“Schema 不完整”缩减为缺表／缺列，未覆盖既定约束和来源一致性。
- P3 Engineering Fast Lane：不适用，任务涉及真实本地 DB、页面生命周期、Schema 完整性与数据来源标注的高风险最终判断。
- 不允许进入下一任务、全新隔离独立复评、风险关闭、工程基线恢复、资产／Schema/API 冻结或 Stage 4。

### 同一能力包整改建议（须用户采纳后另行授权）

1. render 只读入口必须验证当前既定 `SCHEMA` 的结构与约束完整性，至少覆盖 captures／audit 的表类型、列顺序／类型、主键、非空、`idem_key` 唯一约束、`source='local_capture'` 检查约束及所需自动索引；不得借整改改变 Schema/API。
2. 在发布页面前验证每条读取记录的必要字段和 `source == 'local_capture'`；无法证明来源一致时，先使旧页面不可展示，再返回失败，不得硬编码成“来源：本地捕获”发布。
3. 增加同列同类型但缺主键／非空／唯一／检查约束、伪造来源值、约束或索引被替换的固定非敏感回归；证明失败、旧页面失效、DB bytes／对象不变、无副文件与零残留。
4. 保留 attempt-6 至 attempt-8 已成立的完整路径链、文件类型、不跟随链接、缺失／零字节／缺表缺列 DB、合法 render 原子发布、clear 顺序、失败披露和全量历史 hash。

### 资产、风险与用户确认

- P3-094 继续 Not Frozen；R-0051 保持 P0 / Open，并补充“伪完整 Schema 与非法来源记录可被 render 且误标为本地捕获”的事实。
- 不恢复工程基线、不冻结资产或 Schema/API、不进入 Stage 4，不扩大到真实个人文件／既有 DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 需要用户确认：是否采纳 attempt-8 Rework。若采纳，下一轮仍返回同一 P3-094 能力包；工程整改须另行明确授权，不自动创建任务或独立复评。

### 用户采纳与最终收口授权（D-0398）

用户已同时采纳 attempt-8 PM Rework 并明确授权 `lifeos/tasks/LIFEOS-P3-094_final_invariant_closure_task_card.md` 的完整最终收口范围。该卡不再按单一症状补丁，而是一次覆盖 capture／list／snapshot／render／clear 与 CLI 的统一 task-local 路径能力、canonical SQLite Schema／约束／来源／审计完整性、全生命周期失败状态机及完整变异 Evidence 门。

本授权仍属于同一 P3-094 能力包，不创建新任务号；允许在已结束 attempt-8 且未承担 P3-095 独立评审的 Codex 工程会话或新隔离 Codex 工程会话执行。用户将最终收口卡路径投递至该会话即启动，无需再次授权。不得访问真实个人文件／既有 DB、网络、云、Tauri/IPC、Vault、导出或外部用户；不得覆盖历史 Evidence、关闭 R-0051、恢复基线、冻结或进入 Stage 4。

---

## Final Invariant Closure PM 复核（D-0399）

### 验收结论

`Accepted / PM Adjusted to Rework / Awaiting User Confirmation`。

### 授权、会话与修改范围

- D-0398 已完成 attempt-8 采纳和最终收口完整授权；交付物记录最终任务卡完整路径、2026-08-22 20:20:51 CST 接收时间、新隔离 Codex 工程会话、`gpt-5.6-terra + high`，且未承担 P3-095 独立评审。授权与隔离成立。
- 工程修改仅落在任务卡允许的 runtime、CLI、tests、README、attempt-9 runner／Evidence 与最终交付物。PM 未修改工程代码或工程 Evidence。
- 写入 PM 结论前，提交 Manifest 24 项、source hash 6 项和 historical read-only hash 185 项全部复算一致。

### 测试与 Evidence

- PM 在全新 `/private/tmp/lifeos-p3-094-attempt-9-*` 固定非敏感夹具复跑提交 runner：107 PASS / 0 FAIL；unit 41 PASS；attempt-6／7／8 适配行为回归分别 19／13／18 PASS；PM attempt-8 两个已知反例 2 PASS。退出码 0，最终临时残留为零。
- PM 独立反例入口：`lifeos/reviews/LIFEOS-P3-094/pm_evidence/attempt-9/pm_final_invariant_counterexamples.py`；结构化结果同目录 `pm_final_invariant_counterexamples.json`；结果 0 PASS / 6 FAIL。
- P1-1（post-commit cleanup 原子性）：既有 DB capture 第二条记录已 commit 后，固定注入 staging unlink 持续失败，API 返回 `CaptureError`，但 captures／audit 从 1／1 变为 2／2、页面消失且留下一个 `.stale`；新 DB 首次 capture 同样返回失败但留下 1 条 capture／audit 的已提交 DB。失败结果与持久化事实冲突。
- P1-2（审计语义）：canonical Schema 不变时，将 capture_saved 时间改到 2099 年，list 与 render 均接受并发布；插入早于保存时间的 capture_repeat、把 clear detail 改成 `count=999` 也分别被 list／snapshot 接受。当前校验只解析时间和 count 格式，未验证事件顺序、合理时间关系或实际清理计数。
- P1-3（Evidence 冲突／自动门失效）：`UNIT_MAPPINGS` 只依据整个 unit suite 的单一 `unit_pass` 布尔值，把 17 个聚合矩阵行全部标为 PASS。至少 source 大小写／空／NULL／BLOB 独立变体、重复 id／idem、capture commit、capture post-commit cleanup、clear commit 注入未在测试体中独立执行；这与任务卡“每行独立 fixture、缺一行即 NOT PASS”的自动阻断合同直接冲突。聚合记 Not Implemented=1。
- 所有 PM 反例仅使用新建 `/private/tmp` 固定非敏感 SQLite／页面夹具；未读取真实个人文件、既有个人 DB、凭据或外部目标，未联网；临时目录已精确清理。

### 计数与关卡

- P0=0；P1=3；P2=0；Unknown=0；Not Implemented=1。
- Gate 2：不通过。报告失败后仍持久化记录，且伪造审计语义仍可被读取／展示。
- Gate 3：网络、云、Tauri/IPC、Vault、导出及外部处理关闭态未见变化。
- Gate 4：不通过。强制逐行矩阵未实际闭环，runner 的自动阻断门把未独立执行项标为 PASS。
- P3 Engineering Fast Lane：不适用；不允许进入下一任务、全新隔离独立复评、风险关闭、工程基线恢复、冻结或 Stage 4。

### 同一最终收口卡内的修正要求

1. 重排 capture 完成点：任何可能失败的 staging 清理不得发生在不可回滚的 DB commit／发布之后；若确实无法原子合并，返回状态必须准确区分“数据已保存但页面清理失败”，且任务卡要求的失败不改 DB 合同必须由实现与测试一致解决，不能继续返回笼统失败。
2. 补齐审计语义：验证 capture_saved 与 capture 时间关系、repeat 不早于对应保存且事件顺序合法、clear count 与被清理集合一致；为未来时间、逆序 repeat 和错误 count 建立独立拒绝夹具。
3. 删除按全套 unit exit 批量造 PASS 的映射方式。每个任务卡矩阵行必须真正创建对应夹具、执行操作、断言状态并单独决定 PASS；补齐全部来源／类型／重复身份、commit、post-commit cleanup 与清理失败点。
4. runner 必须先验证每个 test ID 确实被执行，再汇总；任何必填行缺失时写 `NOT PASS — DO NOT SUBMIT` 和 Not Implemented，不得再次仅用总 suite 成功代替。

### 资产、风险与用户确认

- P3-094 继续 Not Frozen；R-0051 保持 P0 / Open，并补充失败返回后 DB 已提交／staging 残留及伪造审计语义被接受的事实。
- 不恢复工程基线、不冻结资产或 Schema/API、不进入 Stage 4，不扩大到真实个人文件／既有 DB、网络、云、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- 需要用户确认：是否采纳 D-0399 Rework。若采纳，整改仍在同一最终不变量收口任务卡内，D-0398 对完整卡内整改的授权继续有效，可在同一已结束工程会话完成上述三项修正并重新提交 PM，无需再次授权。

### 用户采纳（D-0400）

用户已采纳 D-0399 Rework。D-0398 对最终不变量收口任务卡完整范围的授权继续有效，不需要新的工程授权；可把更新后的 `lifeos/tasks/LIFEOS-P3-094_final_invariant_closure_task_card.md` 重新投递至同一已结束 attempt-9 工程会话，完成 post-commit cleanup 原子性、审计语义和逐行 Evidence 实际执行三项卡内修正。该采纳不关闭 R-0051、不冻结资产、不恢复基线、不创建独立复评或进入 Stage 4。

### 治理迁移与任务终止（D-0401）

用户采纳并要求立即应用两层验收治理。P3-094 已发生超过两轮正式 Rework，依 D-0401 不再进入 attempt-10，终止状态为 `Closed — Acceptance Not Met / Superseded by LIFEOS-P3-096`。本结论不追溯删除或改写 D-0380 至 D-0400 的历史事实；attempt-1 至 attempt-9、P3-095、全部工程／PM Evidence 和 Manifest 严格只读保留。

D-0399 的 P0=0、P1=3、P2=0、Unknown=0、Not Implemented=1 保持 P3-094 最终未通过计数；不虚假改为 Accepted。三项缺口由 `LIFEOS-P3-096` 接替，其冻结验收依据为 `ABF-P3-096-v1`，SHA-256 `2d4bdb676820e189211ee060eb13a58fc089facb660aec9c2a5a3b5f2a834c58`。R-0051 保持 P0 / Open，资产 Not Frozen；不进入独立复评、风险关闭、基线恢复、冻结或 Stage 4。

### D-0400 晚到提交保全与 ABF v2（D-0402）

D-0401 后完整性检查发现，D-0400 授权的卡内修正在治理规则生效前已于 20:59–21:04 CST 写入 P3-094 当前路径。初次 PM Manifest 因而出现 5 个 live candidate 路径漂移：交付物、README、runtime、tests 和 runner；CLI 未变。该变化属于 D-0400 已授权工程执行，不是越权，但未经过新的 PM 验收，不能改写 P3-094 的终止结论。

PM 已将当前候选与关键 Evidence hash 记录于 `lifeos/reviews/LIFEOS-P3-094/late_submission_d0400/MANIFEST.md`。工程 Evidence Manifest 当前 26/26 一致，执行侧自报 117 PASS / 0 FAIL、PM 六个旧反例 6 PASS，但这些只是 P3-096 的只读候选输入，不是 PM Pass。

P3-096 在启动前将 ABF 更新为 `ABF-P3-096-v2`；V2 只替换候选基线，完整继承 V1 的六个不变量、二十行矩阵、Pass 公式和两轮 Rework 上限，不改变任务范围或质量标准。P3-094 继续 `Closed — Acceptance Not Met / Superseded`，D-0401 后所有 P3-094／095 路径严格只读。
