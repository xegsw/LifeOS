# LIFEOS-P3-102 Acceptance Basis Freeze｜CLI-only 有限本人真实使用启用

## 冻结信息

- 任务 ID：`LIFEOS-P3-102`
- ABF ID／版本：`ABF-P3-102-v1`
- 生效决策：`D-0419`
- 冻结完成时间：2026-08-23 10:35:03 CST (+0800)
- 时间语义：以上时间是用户确认精确路径、入口和保留语义后，PM 开始完成本 ABF 时取得的已发生本地时间。最终 SHA-256 由写入后计算并记录在任务卡与 D-0419，本文件不使用自指 hash。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 在一个全新专用真实目录中，使用固定 P3-097 candidate 和用户主动手工输入的一条低敏感短文本，验证 CLI-only 的捕获、持久化、幂等、重启读取、今日页展示、失败关闭和首轮保留语义。
- 本任务只验证一条有限本人真实使用切片，不宣布生产可用、Stage 4、资产冻结、Schema/API 冻结或工程基线恢复。

## 精确授权边界

- 唯一目录：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1`
- 唯一 DB：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1/capture.sqlite`
- 唯一页面：`/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1/today.html`
- 允许 CLI：`capture`、`today`、`render`。
- 禁止 CLI：`clear` 以及任何未列入口；删除、覆盖或清理首轮 DB／页面必须另行逐次用户确认。
- 保留语义：首轮结束后保留精确目录、DB 和页面；PM／专项会话不得自动清理。
- 输入：仅用户在专项会话中主动手工提供的一条低敏感短文本及幂等 key。禁止凭据、密钥、身份号码、支付信息、健康／医疗、法律、财务、高敏感关系信息、第三方秘密或其他敏感材料。
- Evidence 隐私：不得把原文写入项目 Evidence、日志、截图或聊天摘要；只允许长度区间、用户确认的低敏感分类、SHA-256、记录／审计计数、时间、状态和文件 metadata。用户可在本地页面目视确认内容，但 PM 不读取原文。
- 固定非敏感负向夹具：只可新建 `/private/tmp/lifeos-p3-102-*`；不得复制用户原文，结束时精确清理。
- 禁止能力：既有个人 DB、任意路径扫描、Vault、Tauri/IPC、真实文件导出、网络、云／第三方、同步、多设备、L3、外部用户。

## 固定候选与只读输入

| 路径 | SHA-256 |
|---|---|
| `lifeos/engineering/LIFEOS-P3-097/src/local_capture.py` | `1535fd1fa45b581a042be73bdbfdde1905c2ea7ff10c3554952b53882f455453` |
| `lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py` | `ef7e6ba7f082e4a8b5d354dd5427835e054b188aab211c61c967174081155659` |
| `lifeos/engineering/LIFEOS-P3-097/evidence/MANIFEST.md` | `63301b8059231130b19bafb15d6761f6b5efa89417326d327380e8c7d5ff1311` |
| `lifeos/reviews/LIFEOS-P3-097/pm_evidence/initial/MANIFEST.md` | `90a1072dccc841eaecb6fe7cee51a6c175aff66cede6cc393d4ddc2da8a4e183` |
| `lifeos/reviews/LIFEOS-P3-098/evidence/MANIFEST.md` | `4f74f685d2ba5857c7fb9a469ae3397ddf06349bd9f9a34193b933773dfb6958` |
| `lifeos/reviews/LIFEOS-P3-098/pm_evidence/initial/MANIFEST.md` | `4ddf1158c63bbeecb0b2dd83fea44d19aa24d52b4bd2c33e25df966ba412c266` |

全部 P3-097/P3-098/P3-100/P3-101 工程、Review、Evidence 和 Manifest 严格只读。专项会话不得修改 candidate；发现代码缺陷必须停止，按新任务处理。

## 引用的 L1

- L1-1 数据主权；L1-2 内容身份；L1-3 生命周期完整；L1-4 失败关闭；L1-5 用户控制；L1-6 审计可信；L1-7 Evidence 诚实；L1-8 历史保全；L1-9 授权不漂移；L1-10 可复核性。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败状态 |
|---|---|---|---|---|
| ABF-I-01 | 授权、Frozen 先后与隔离 | P0 | 用户确认精确边界；ABF hash 匹配且早于任务投递；新隔离执行会话 | Blocked |
| ABF-I-02 | 目标新建且目录链稳定 | P0 | 执行前目标不存在；祖先均真实目录非链接；只创建精确目录、DB、页面 | Rework / Blocked |
| ABF-I-03 | 低敏感手工输入与 Evidence 脱敏 | P0 | 用户主动确认类别；Evidence 无原文，只留 hash／metadata | Rework |
| ABF-I-04 | 固定 candidate 与 CLI-only | P0 | 六项 hash 一致；仅 capture/today/render；clear 与禁止能力关闭 | Rework / Blocked |
| ABF-I-05 | 首次捕获准确完成 | P0 | 返回 saved；DB/Schema/source/audit/页面失效语义正确；无 sidecar/shadow | Rework |
| ABF-I-06 | 幂等与冲突关闭 | P0 | 同 key／同文本准确 repeat 且 capture 数不增；同 key／异文本失败且状态不变 | Rework |
| ABF-I-07 | 重启读取与页面展示 | P0 | 新进程 today 与 render 只读取精确 DB；用户目视确认页面；Evidence 不含原文 | Rework |
| ABF-I-08 | 失败原子性 | P0 | 注入失败不改变 live DB／页面，返回失败且零 shadow／sidecar | Rework |
| ABF-I-09 | 路径／类型与外部目标关闭 | P0 | 相对／dotdot、祖先／最终链接、hardlink、特殊文件、调用方输出目标均变更前拒绝 | Rework |
| ABF-I-10 | 禁止删除与首轮保留 | P0 | 不调用 clear；结束时精确 DB／页面保留，未发生删除或清理 | Rework |
| ABF-I-11 | 审计、来源与内容身份 | P0 | `local_capture`、canonical Schema、capture/audit 数量／顺序／时间一致；hash 对应用户输入 | Rework |
| ABF-I-12 | 风险、历史与阶段不漂移 | P0 | R-0052 保持 Open；R-0040/R-0051、历史、冻结、基线和阶段不变 | Rework |

## 冻结验收矩阵

| 行 ID | 独立动作 | 通过条件 | Evidence |
|---|---|---|---|
| ABF-M-001 | 核验投递、隔离、接收时间、ABF hash 和用户确认 | I-01 成立 | `session_start.json` |
| ABF-M-002 | 复算六项候选 hash，检查目标不存在及完整祖先链 | 6/6；目标不存在；祖先无链接 | `preflight.json` |
| ABF-M-003 | 用户主动提供低敏感短文本和 key；只在内存计算 hash | 类别确认；Evidence 无原文 | `input_attestation.json` |
| ABF-M-004 | 创建精确专用目录并首次 capture | saved；只生成允许资产；Schema/source/audit 正确 | `lifecycle_matrix.json` |
| ABF-M-005 | 同 key／同文本重复 capture | idempotent repeat；capture 数不增；audit 合法增加 | `lifecycle_matrix.json` |
| ABF-M-006 | 同 key／异固定非敏感文本 capture | 失败；DB/page bytes、计数和状态不变 | `lifecycle_matrix.json` |
| ABF-M-007 | 新进程执行 today | 只读成功；记录 hash／计数与输入一致；Evidence 脱敏 | `restart_matrix.json` |
| ABF-M-008 | 新进程执行 render 并由用户目视确认 | 只生成固定 today.html；用户确认内容正确；Evidence 无原文 | `restart_matrix.json` |
| ABF-M-009 | 以固定非敏感文本执行 inject-failure | 明确失败；DB/page hash 不变；零 shadow／sidecar | `failure_matrix.json` |
| ABF-M-010 | 在 `/private/tmp/lifeos-p3-102-*` 独立执行路径／类型负向矩阵 | 全部变更前拒绝；不使用用户原文 | `boundary_matrix.json` |
| ABF-M-011 | 静态／动态核对 clear 和禁止能力 | clear 未调用；Tauri/IPC/Vault/export/network 等均关闭 | `closed_capabilities.json` |
| ABF-M-012 | before/after 输入 hash、Evidence 脱敏扫描、临时清理与最终保留核对 | 历史 6/6 不变；Evidence 无原文；临时残留 0；精确 DB/page 保留 | `input_integrity.json`, `retention_state.json`, `temporary_residue.json` |

## Pass 公式与计数

- 12/12 矩阵行必须独立执行，具有唯一 test／fixture／execution ID；不得用汇总 PASS 替代。
- P3-102 执行基础与交付质量的 P0/P1/P2/Unknown/Not Implemented 必须分别全零。
- 六项固定候选 hash 6/6，历史只读 before/after 6/6，Evidence 原文扫描 0 命中，临时残留 0。
- 目录、DB、页面最终按用户确认保留；保留不是清理失败。不得把 retained 计为残留。
- 任一真实输入泄漏到 Evidence、越界路径、错误回执与持久化矛盾、clear 调用、禁止能力启用或历史 hash 变化均不得 Pass。
- R-0052 在任务 Pass 后仍保持 Open，直到后续全新隔离独立复评、PM 验收和用户风险决定；任务 Pass 不自动关闭风险或准入 Stage 4。

## Evidence 与隐私

- 必须保存：task-owned runner、12 行结构化矩阵、脱敏日志、hash／metadata、复跑说明、输入完整性、保留状态、临时清理和非自指 Manifest。
- 禁止保存：用户输入原文、包含原文的命令回显、页面截图、DB 副本、SQL dump 或 today 输出正文。
- 用户原文只允许存在于用户明确输入的命令参数、精确新 DB 和固定 today.html；专项聊天摘要不得复述。
- PM 验收只读取脱敏 Evidence，不打开 DB／页面或读取用户原文。

## Rework、退出与新任务

- 正式 Rework：0/2；仅本 ABF 完全不变、同一目录／数据类别／入口／保留语义时允许 Rework。
- 任何 candidate 代码修复、路径／数据／入口扩大、clear／删除、Tauri/IPC、导出、Vault、网络／外部能力、Schema/API、冻结、基线或阶段变化，必须停止并新建任务、新授权、新 ABF。
- 专项会话不得关闭 R-0052、创建独立复评、冻结资产、恢复基线或进入 Stage 4。

## 启动前质疑窗口

- 新会话在任何目录创建或真实文本请求前核对 ABF hash、任务卡状态、精确路径、允许入口和保留语义。
- 歧义必须在动作前停止；启动后不得修改本 ABF。
