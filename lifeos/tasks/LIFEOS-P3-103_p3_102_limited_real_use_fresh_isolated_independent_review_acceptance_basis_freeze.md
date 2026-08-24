# LIFEOS-P3-103 Acceptance Basis Freeze｜P3-102 有限真实使用全新隔离独立复评

## 冻结信息

- 任务 ID：`LIFEOS-P3-103`
- ABF ID／版本：`ABF-P3-103-v1`
- 生效决策：`D-0421`
- 冻结完成时间：2026-08-23 11:41:14 CST (+0800)
- 时间语义：以上为用户采纳 P3-102、授权创建独立复评并同意 retained DB 只读哈希核验边界后，PM 开始完成本 ABF 时取得的已发生本地时间。
- 状态：Frozen
- ABF 文件 SHA-256：由 PM 写入完成后计算并记录在任务卡与 D-0421；本文件不使用自指 hash。
- 本文件是否在专项会话开始前冻结：Yes。
- 正式 Rework：0/2。

## 本轮唯一用户结果

由未参与 P3-102 执行或 PM 验收的全新隔离 Codex 独立评审会话，判断 P3-102 是否在精确真实 pilot 边界内满足数据身份、生命周期、失败关闭、路径约束、保留、Evidence 脱敏和禁止能力关闭合同。

本轮冻结的是验收依据，不冻结产品需求、候选代码、真实 DB／页面、Schema/API、工程基线、风险或阶段。

## 精确授权与隐私边界

- 唯一真实目录：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1`。
- 唯一真实 DB：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1/capture.sqlite`。
- 唯一真实页面：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1/today.html`。
- 真实资产只读：不得 capture、render、clear、覆盖、迁移、复制、备份、导出、截图、修改权限或创建 sidecar；不得读取页面正文。
- DB 内容核验是唯一例外：仅可用 SQLite `mode=ro&immutable=1` 和 `PRAGMA query_only=ON` 读取唯一 capture 的原文字段，在内存中计算 SHA-256，并只输出是否等于 P3-102 `input_attestation.json` 已授权 hash；原文不得写入变量转储、日志、Evidence、异常、命令行、聊天或文件，计算后立即丢弃。
- 不得读取、输出或哈希幂等 key；不得制作 DB 副本、SQL dump、页面副本或页面截图。
- 可读取真实 DB 的非内容结构事实：Schema 名称、记录／审计计数、source、状态、时间顺序和约束；不得输出可能承载原文或 key 的字段。
- 页面正确性沿用 P3-102 已记录的用户目视确认；独立评审只核对页面 lstat metadata、文件类型、固定文件名、前后不变和关联 Evidence，不打开或哈希页面内容。
- 独立动态复跑只使用 `/private/tmp/lifeos-p3-103-*` 中新建的固定非敏感夹具；不得复制用户原文或 key；结束时精确清理。
- 全程离线；禁止网络、云／第三方、凭据、Vault、Tauri/IPC、导出、同步、多设备、L3、外部用户和任何外部目标。
- `clear` 在真实目标和固定夹具中均不得调用；任何真实资产清理继续需要新的逐次用户确认。

## 固定只读输入

| 路径 | SHA-256 |
|---|---|
| `lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement.md` | `f739f8ac7ffe6aa4a968899c75e336be528db044f8265e1aeafea41f64501b88` |
| `lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement_acceptance_basis_freeze.md` | `361849606a9164ad0ffc215688084a466dd6495ff5589719591773bcdc40a243` |
| `lifeos/deliverables/LIFEOS-P3-102_limited_personal_real_use_cli_enablement.md` | `3335b3eaa696f10b0bb8b61bb7bdc962ed2b966bc95de0696ca7714bd3343e70` |
| `lifeos/engineering/LIFEOS-P3-102/runner.py` | `af0b022d5dc961bfca13c4ace500b7c81b22679eb91f7dfa8f438c8325614ea4` |
| `lifeos/engineering/LIFEOS-P3-102/evidence/MANIFEST.md` | `17ce6fea49a921ca8b03fa1efa88b2d52ae248e172912ec7d7dfbf91774175a7` |
| `lifeos/reviews/LIFEOS-P3-102_pm_review.md` | `046a7d7173fe90bba07d9503b5822f741bd04a0d77a7cade54af0de58dee7d1f` |
| `lifeos/reviews/LIFEOS-P3-102/pm_evidence/initial/MANIFEST.md` | `3e77ef5ee931053ec42f0afd69f3b6b2547035383e8515e094e69dbd1abc7e62` |
| `lifeos/engineering/LIFEOS-P3-097/src/local_capture.py` | `1535fd1fa45b581a042be73bdbfdde1905c2ea7ff10c3554952b53882f455453` |
| `lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py` | `ef7e6ba7f082e4a8b5d354dd5427835e054b188aab211c61c967174081155659` |
| `lifeos/engineering/LIFEOS-P3-097/README.md` | `7fa834dbb9ecaf78200af01c37c2ba8029a3c511affce9c184a3042c8cfa6adf` |

还须前后复算 P3-102 Engineering Manifest 17 项、PM Evidence Manifest 5 项及其中引用的只读历史资产；任何 mismatch 不得在评审侧修复。

## 引用的 L1 长期原则

- L1-1 数据主权：真实资产仅按逐项授权读取，禁止复制、泄露、删除或扩大路径。
- L1-2 内容身份：唯一原文 hash 必须与已授权 attestation 相符，且不暴露原文／key。
- L1-3 生命周期完整：saved、repeat、restart、today、render 与保留终态一致。
- L1-4 失败关闭：失败必须在任何文件或 DB 变化前停止，哨兵与状态不变。
- L1-5 用户控制：禁止 clear，真实资产继续保留，任何清理另行确认。
- L1-6 审计可信：source、capture/audit 数量、顺序和时间语义一致。
- L1-7 Evidence 诚实：逐行结果、日志、hash、Manifest 可复核且不泄露内容。
- L1-8 历史保全：候选、Engineering/PM Evidence 和账本严格只读。
- L1-9 授权不漂移：仅限本 ABF 的路径、只读查询与固定非敏感临时夹具。
- L1-10 可复核性：独立 runner、fixture、ID、before/after、失败注入和残留清理完整。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败状态 |
|---|---|---|---|---|
| ABF-I-01 | 授权、Frozen 先后与独立性成立 | P0 | 用户授权早于冻结；新会话未参与 P3-102 执行／PM 验收；ABF hash 匹配 | Blocked |
| ABF-I-02 | 固定输入与历史只读完整 | P0 | 10 项固定输入、两个 Manifest 全量条目前后一致 | Rework / Blocked |
| ABF-I-03 | 真实目录、DB、页面路径与类型稳定 | P0 | 精确路径；祖先无链接；目录 0700、DB/page 0600、regular、nlink=1；仅两个文件 | Rework |
| ABF-I-04 | 真实 DB 最小只读核验不泄露 | P0 | immutable/query-only；唯一原文 hash 匹配 attestation；不读／哈希 key，不输出内容，不产生 sidecar | Rework |
| ABF-I-05 | 真实结构、来源与审计可信 | P0 | canonical Schema、单一 capture、预期 audit、source 与时间顺序满足 P3-102 合同 | Rework |
| ABF-I-06 | 页面核验不越权 | P0 | 不打开／哈希页面正文；沿用用户目视确认；metadata 与关联 Evidence 一致 | Rework |
| ABF-I-07 | 真实 retained 资产前后完全不变 | P0 | DB/page/目录 lstat metadata、文件名、非内容结构事实前后一致且零 sidecar；不得读取或哈希 DB 文件整体 | Rework |
| ABF-I-08 | 固定非敏感生命周期独立复跑成立 | P0 | 新 runner 覆盖首次、幂等、冲突、重启 today、render、失败注入；结果准确 | Rework |
| ABF-I-09 | task-local 路径／类型与失败关闭成立 | P0 | 链接、hardlink、特殊文件、非规范路径及外部输出全部变更前拒绝，哨兵不变 | Rework |
| ABF-I-10 | Evidence 隐私与完整性成立 | P0 | 无真实原文／key／页面正文／DB hash／副本；每行唯一 ID 和 before/after；Manifest 非自指 | Rework |
| ABF-I-11 | clear 与外部能力关闭 | P0 | clear 未调用；Tauri/IPC/Vault/export/network/cloud/sync 等均关闭 | Rework |
| ABF-I-12 | 风险、冻结、基线与阶段不漂移 | P0 | R-0052 保持 Open；R-0040/R-0051、冻结、基线、Stage 3/4 不变 | Rework |

## 冻结验收矩阵

| 行 ID | 独立动作 | 通过条件 | 必须保留 Evidence |
|---|---|---|---|
| ABF-M-001 | 核验任务投递、会话隔离、接收时间、ABF hash 与用户授权 | I-01 成立；无授权歧义 | `session_start.json` |
| ABF-M-002 | 前后复算固定输入及两个 Manifest 全量条目 | 固定 10/10、Engineering 17/17、PM 5/5，前后一致 | `source_history_hashes.json` |
| ABF-M-003 | lstat 精确真实目录／DB／页面及祖先链，只列固定文件名 | I-03 成立；不打开内容 | `retained_metadata.json` |
| ABF-M-004 | 使用 immutable/query-only 对唯一 capture 原文做内存 hash 比对 | 仅输出 match=true；不输出原文、key、内容 hash 或 DB hash；零 sidecar | `retained_content_attestation.json` |
| ABF-M-005 | 查询非内容 Schema/source/count/audit/time 事实 | 合同一致；不选择、输出或哈希 key | `retained_structure_audit.json` |
| ABF-M-006 | 核对用户页面目视确认 Evidence 与页面 metadata | 不读／哈希正文；确认链与 metadata 一致 | `retained_page_attestation.json` |
| ABF-M-007 | 真实资产核验前后比较 | lstat、固定文件名、非内容结构事实全部不变；不得读取或哈希 DB 文件整体 | `retained_unchanged.json` |
| ABF-M-008 | 在全新 `/private/tmp` 固定非敏感目录独立复跑 capture／repeat／conflict／restart today／render／inject-failure | 六类动作全部独立 PASS；不使用 P3-102 runner 或真实输入 | `fresh_lifecycle_matrix.json` |
| ABF-M-009 | 独立执行路径规范化、祖先／最终链接、hardlink、FIFO／目录、外部输出负向矩阵 | 全部变更前拒绝；哨兵和 DB/page 不变 | `fresh_boundary_matrix.json` |
| ABF-M-010 | 对故意缺行、重复 ID、泄密字段和不可复核结果执行 Evidence 负门 | 明确拒绝、退出非零；不得冒充 Pass | `evidence_negative_gate.json` |
| ABF-M-011 | 静态／动态核对 clear 和禁止能力关闭态 | clear 调用 0；禁止能力无调用／无网络 | `closed_capabilities.json` |
| ABF-M-012 | 前后保全、隐私扫描、临时清理及风险／阶段对账 | 所有真实／历史资产不变；敏感字段 0 命中；临时残留 0；风险／阶段不变 | `final_integrity.json` |

## 独立性与 Evidence 合同

- 必须新写独立 runner、fixture 和断言；不得导入、执行、复制或改写 P3-102 `runner.py`。
- 独立测试设计必须在读取 P3-102 runner 源码或 P3-097 candidate 实现细节前写入 Evidence 并固定 SHA-256；之后只可定向静态反查。
- P3-102 runner 只允许做 hash 保全，不得作为独立复跑入口。
- 每个父行与所有子项必须具有唯一 test／fixture／execution ID、before／after、实际断言、日志路径和结果；不得用提交侧 PASS 汇总代替独立动作。
- Evidence 只允许保存布尔匹配、计数、状态、允许的路径 metadata、固定非敏感夹具结果和源码／历史 hash；禁止真实原文、key、内容 hash、DB 文件 hash、页面正文／hash、DB／HTML 副本、SQL dump 或截图。
- 独立 Evidence 写入：`lifeos/reviews/LIFEOS-P3-103/evidence/`；不得覆盖任何 Engineering／PM Evidence。
- 本地模型预检可因 P0 真实数据最终判断跳过，但必须在 Review 中说明理由。

## Pass 公式、Rework 与退出

- Pass：ABF-I-01 至 I-12、M-001 至 M-012 及全部子项独立 PASS；P0/P1/P2/Unknown/Not Implemented 全零；runner 退出 0；临时残留 0；真实资产与历史前后不变；隐私扫描 0 命中。
- 允许 N/A：无。无法在授权边界内验证的项目必须计入 Unknown 或 Not Implemented，不得静默通过。
- 同任务 Rework：仅独立评审自身 runner／Evidence／文案可在不改变 ABF、真实读取边界、固定输入、候选、目录、数据、入口与独立性的前提下补正；上限 2。
- 返回 P3-102 Rework：独立发现映射 L1/本 ABF 的候选或真实执行 P0/P1、Evidence 冲突、隐私泄露、真实状态漂移或完成定义缺口；评审会话不得修候选或真实资产。
- 必须新建任务：需要修改 ABF、读取页面正文／key、扩大真实路径／数据／入口、修改 candidate、清理真实资产、启用 Tauri/IPC 或达到两轮 Rework 上限。
- Blocked：独立性无法证明、固定 hash 不明漂移、授权读取无法安全完成，或连续本地环境阻断使矩阵不可执行。
- 即使 Pass，R-0052 仍保持 Open，资产仍 Not Frozen，不恢复工程基线、不创建三页整合任务、不进入 Stage 4；后续仍需 PM 验收和用户采纳。

## 启动前质疑窗口

- 新会话在读取真实 DB 或创建临时夹具前，必须核对任务卡、ABF ID/hash、用户授权、独立性与精确读取方式。
- 任何歧义必须在动作前停止；专项会话不得解释扩张或修改本 ABF。
- 最终冻结版本：`ABF-P3-103-v1`。
