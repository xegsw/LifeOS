# ABF-P3-133-v1｜受控真实输入 Work 自用 Runtime 闭环验收依据

## 冻结信息

- 任务 ID：`LIFEOS-P3-133`
- ABF ID／版本：`ABF-P3-133-v1`
- 生效决策：`D-0539`
- 冻结时间：2026-08-26
- ABF 文件 SHA-256：冻结后记录；本文件不使用自指 hash
- 状态：`Frozen / Effective`
- 本文件是否在专项会话开始前冻结：`Yes`

## 本轮唯一用户结果

- 单一结果：P3-132 accepted candidate 在唯一新专用真实目录和全新 DB 中，完成最多 3 条低敏感 Work 短文本的 actual-Tauri Capture→用户确认 Context／Action→Today→重启闭环。
- 明确不冻结的产品需求：不冻结产品 IA、视觉、Runtime、IPC、Schema/API、ModelPort 或工程基线。
- 明确非范围：真实模型、网络、Health、跨领域智能、删除、导出、权限、恢复、同步、风险关闭和 Stage 4。

## 授权和能力边界

- 允许目录：`lifeos/engineering/LIFEOS-P3-133/`、`lifeos/deliverables/LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop.md`、`lifeos/reviews/LIFEOS-P3-133/`、`/private/tmp/lifeos-p3-133-real-self-use-v1`、`/private/tmp/lifeos-p3-133-independent-review-v1`、`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-3`。
- 允许数据与夹具：工程／评审使用全新非敏感合成 DB；真实根仅允许用户手工输入最多 3 条、每条最多 200 字符的低敏感 Work 短文本。
- 允许入口／接口：offline actual Tauri 和 P3-132 恰好十一 IPC；真实文本只由用户本人通过 UI 输入。
- 允许工具／环境：本地文件、Rust／JavaScript、SQLite、离线 Tauri、结构化测试与隐私保护 Evidence。
- 严格只读资产：P3-132 candidate、Final Manifest、交付物、PM Review／Evidence及此前全部历史资产。
- 禁止能力与外部目标：其他 Pilot／真实路径／DB／文件、真实文本读取或复制、网络、模型、Agent、云／第三方、Vault、凭据、删除、导出、权限、恢复、同步、第十二项 IPC。
- 投递前额外用户确认：已于2026-08-26完成；原文见`lifeos/tasks/LIFEOS-P3-133_user_confirmation.md`。

## 引用的长期原则

- 数据主权：全部写入限定于工程根、精确临时根和唯一真实自用根。
- 内容身份：用户原文、确认事实、Action 和系统不可用状态分离。
- 生命周期完整：Capture、确认、Today、关闭重开及失败路径一致。
- 失败关闭：路径、文件类型、额度、DTO、历史或授权失败均在写前停止。
- 用户控制：Context／Action 必须显式确认；真实文本仅由用户输入。
- 审计可信：使用非内容型计数、状态、run 身份和顺序收据，不制造内容 Evidence。
- Evidence 诚实：工程／独立正证据全部来自合成夹具；真实收据不冒充内容审查。
- 历史保全：P3-132及此前资产严格只读。
- 授权不漂移：禁止检测合同外真实路径和历史 Runtime 根。
- 可复核性：合成矩阵、Manifest、mutation和独立复评可重复复核。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 只有唯一真实根和其中全新 DB 可承载真实文本 | P0 | 规范路径、普通目录／文件、零回退、写入清单唯一 | fail closed，真实运行不启动 |
| ABF-I-02 | 真实文本不进入 Evidence、日志、截图、hash、模型或外部进程 | P0 | taint 合成测试与真实非内容收据均无内容字段 | fail closed，判 Not Pass |
| ABF-I-03 | 用户确认是 Context／Action 进入权威状态的唯一入口 | P0 | 未确认状态无 Action／Focus；确认后才出现 | fail closed，状态不变 |
| ABF-I-04 | 真实模式不运行 OfflineSyntheticModelAdapter | P0 | adapter call count=0，UI明确模型未启用 | fail closed，无 Understanding/noticed |
| ABF-I-05 | 关闭重开不复制、不改身份、不自动确认 | P1 | 非内容计数与opaque身份前后一致 | Not Pass，保留 DB 等待 PM |
| ABF-I-06 | 独立评审在真实运行前通过且永不访问真实根 | P0 | review Manifest、访问清单和Pass均成立 | Blocked，不启动真实运行 |
| ABF-I-07 | 真实根和 DB 首轮保留，不执行清理 | P0 | 结束时精确路径仍存在，未调用清理 | 停止并报告不可逆边界事故 |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | startup | P3-132固定输入 | history/hash/type核验 | 全部匹配才复制 | 历史全部只读 | P3-133-M001 | source-lineage.json |
| ABF-M-002 | startup | 合成空根 | 规范绝对根启动 | 只创建task-local DB | 其他路径零访问 | P3-133-M002 | root-positive.json |
| ABF-M-003 | startup | 链接／相对／父级／非目录根 | 启动 | 写前拒绝 | 哨兵与DB状态不变 | P3-133-M003 | root-mutations.json |
| ABF-M-004 | startup | 已有或非普通capture.sqlite | 启动 | 写前拒绝 | 原对象不变 | P3-133-M004 | db-type-mutations.json |
| ABF-M-005 | capture | 合成taint文本 | 记录、确认、刷新、重启 | 产品状态成立且Evidence零taint | 日志／截图／Manifest无内容 | P3-133-M005 | privacy-taint.json |
| ABF-M-006 | capture | 3条已存在 | 第4条或超200字符 | 写前拒绝 | 记录数和DB hash不变 | P3-133-M006 | input-limit.json |
| ABF-M-007 | context/action | 未确认Capture／Candidate | 查询Today | 无Action／Focus | 原文身份不变 | P3-133-M007 | unconfirmed-state.json |
| ABF-M-008 | context/action | 用户显式确认 | 确认Next Action | 创建一个确认Action | Capture不被改写 | P3-133-M008 | confirmed-action.json |
| ABF-M-009 | today | 零／一／多开放Action | 刷新Today | 0或1稳定Focus | 无领域配额、无noticed | P3-133-M009 | today-focus.json |
| ABF-M-010 | global-ai | 真实模式 | 请求Understanding／Feedback | 固定不可用、adapter零调用 | DB无Understanding／Feedback | P3-133-M010 | model-disabled.json |
| ABF-M-011 | app lifecycle | 已持久化确认状态 | quit/reopen | 计数、opaque IDs、状态一致 | 无复制、无sidecar | P3-133-M011 | restart.json |
| ABF-M-012 | independent review | 全新合成根 | actual-Tauri全矩阵 | 独立Pass | 真实根零访问 | P3-133-M012 | independent-review Manifest |
| ABF-M-013 | real use | 独立Pass、真实根不存在 | 用户手工输入并重启 | 最多3条、状态闭环、非内容收据 | 文本不出App/DB | P3-133-M013 | real-use-receipt.json |
| ABF-M-014 | cleanup | Evidence完成 | 精确清理两个临时根 | 临时根absent | 真实根／DB保留 | P3-133-M014 | cleanup.json |

## Evidence 合同

- 可运行 runner／测试源码：P3-133 task-local runner；真实操作只通过 actual Tauri UI。
- 逐行结构化结果：ABF-M-001～M-014 每行独立结果。
- before／after 状态：合成阶段使用完整 hash；真实阶段仅记录不含内容的计数、opaque ID 和状态。
- 日志／快照：合成日志可保留；真实阶段禁止任何含文本截图或payload日志。
- source／history hash：P3-132固定输入全量复算。
- Manifest：工程和独立评审分别非自指 Manifest；真实根不纳入 Manifest。
- 复跑命令：只写相应任务根和精确临时根；不得访问真实根，除用户真实运行阶段。
- 临时清理：只精确清理两个 `/private/tmp` 根；真实自用根保留。

## 计数与 Pass 公式

- P0：0
- P1：0
- P2：仅允许明确非阻断项
- Unknown：0
- Not Implemented：0
- Pass 公式：ABF-I-01～I-07和ABF-M-001～M-014全部PASS；独立评审Pass；真实文本零泄露；无合同外访问、IPC、网络、模型、删除或导出。
- 允许的 N/A：用户未选择创建Next Action时，Action／Focus可为空，但必须作为用户选择而非执行缺失；其余无N/A。

## Closure Cycle 与退出规则

- 首次 PM 不通过时：一次列明全部同合同缺口并进入P3-133 Closure Cycle。
- 同任务 Closure Cycle 条件：结果、风险、目录、数据、入口、权限、架构与本ABF均不变。
- 必须新建任务条件：真实根、数据类型、IPC、网络／模型、删除／导出／权限、架构／Schema/API或风险边界变化，或历史污染不可可信恢复。
- 不使用统一两轮Rework上限。
- Blocked条件：独立评审不可取得可信actual-Tauri Evidence、用户无法操作真实App、真实根预先存在且非空、或无法形成不读取真实文本的可复核收据。

## 候选基线与只读保全

- 候选输入：`lifeos/engineering/LIFEOS-P3-132/candidate/`
- 权威 Manifest：`lifeos/engineering/LIFEOS-P3-132/evidence/FINAL_MANIFEST.json`
- PM Review：`lifeos/reviews/LIFEOS-P3-132_pm_review.md`
- 冻结时由 PM 记录上述当前 hash、Task Contract hash和本ABF外部hash；冻结后不得原地改变范围或矩阵。
