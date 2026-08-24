# LIFEOS-P3-112 Acceptance Basis Freeze｜P3-111 可真实使用 MVP 全新隔离独立复评

## 冻结信息

- 任务 ID：`LIFEOS-P3-112`
- ABF ID／版本：`ABF-P3-112-v1`
- 生效决策：`D-0453`
- 冻结时间：2026-08-24（Asia/Shanghai）
- ABF 文件 SHA-256：冻结后记录在任务卡与决策日志；本文件不自指。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 单一结果：由未参与 P3-104 至 P3-111 工程、评审或 PM 验收的全新独立 Codex 会话，只读判断固定 P3-111 candidate、初次／Rework Evidence 与 PM Evidence，是否在不访问 retained Pilot-2 的条件下，足以支持“三页 UI + 本地 Runtime 有限本人真实使用 MVP 闭环”的独立 Pass。
- 明确不冻结：产品长期需求、candidate、Schema/API、工程基线、风险或 Stage 4。
- 明确非范围：再次 capture；启动会访问 Pilot-2 的真实 app；读取、打开、hash、复制、覆盖或清理 Pilot-2／`capture.sqlite`；clear、export、权限、恢复、网络、Vault、云／第三方、同步、多设备、L3、外部用户、风险关闭／重开、冻结、基线恢复或阶段切换。

## 授权和能力边界

- 项目写入仅允许：
  - `lifeos/deliverables/LIFEOS-P3-112_p3_111_real_usable_mvp_fresh_isolated_independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-112/independent_review.md`
  - `lifeos/reviews/LIFEOS-P3-112/evidence/`
- 唯一临时写入根：`/private/tmp/lifeos-p3-112-review-v1`；其全部工作副本、Cargo target、固定非敏感夹具和 mutation 必须位于该根内。执行前必须不存在，结束时必须精确删除并证明不存在。
- 允许数据：项目工作区内 P3-111 脱敏 Evidence；全新临时副本中的固定短 ASCII 非敏感夹具、哨兵和 SQLite。
- 允许入口：只读文件／hash／静态扫描；临时 candidate 副本的 `cargo test --locked --offline`、`cargo build --locked --offline`；评审自有 runner；提交 verifier 的只读重放。
- 严格禁止：启动 P3-111 Tauri app／binary；访问 `/Users/xxe/Documents/LifeOS-Self-Use-Pilot-2` 的任何 metadata 或内容；联网；修改 P3-111 candidate、tools、Evidence、交付物、PM Review／PM Evidence、ABF 或账本。
- 投递前额外用户确认：None。用户已授权创建本只读后继任务；任务不访问真实目录／DB。任务卡投递至合格全新会话即授权执行本 Frozen 边界。

## 固定输入与候选身份

| 输入 | SHA-256 |
|---|---|
| P3-111 任务卡 | `5b5ed1211647747e34518e1b7de02b8693e01923e09dd76a7d212a9ff5dde59e` |
| `ABF-P3-111-v1` | `24afdb1db547f69eb5160868e1b413fdc7c1b1f0f10cb762969fa6336e289395` |
| P3-111 初次交付物 | `a84a5778bf689f63c044e53aa3d6cf644289610b5bfb1ab607fdc603ceb8ddfe` |
| P3-111 Rework 1 交付物 | `6f6bb1dcf5aed2b4e9e660fb30971af1f9b6e5adbccd9a75519b70c80bac9e75` |
| `candidate_provenance.md` | `f97f1e0f5edbbe8f562b4287e5544ffd17560a4ac5da736b95e990a232f0d6cc` |
| `product_gap_matrix.md` | `e1451c258ec18cc57895580f4a02c04747d62b476a225cec632272d024254ff6` |
| P3-111 初次 Engineering Manifest | `e70f70b96e4aa1bfce2158d3e81f708b7fbc457b0348a632ade1ff4b0f4b835b` |
| P3-111 Rework 1 Engineering Manifest | `3f677fd533ce4ca902552e7aad661ba343070d517b9c03f9e3b4dcc89dc62ed4` |
| P3-111 PM Review | `e8fc44bcd79b7a2d6fb0ec29f3ff23b22ece0c08fdc260236fb8113f60bb0c10` |
| P3-111 Rework 1 PM Evidence Manifest | `38c868b2d901af11092f8bcbb05bf2d3f3d7f58f73838fe7b31febde9796ee85` |
| `semantic_verifier.py` | `1537c9daa9730cb35618c71af443fafbef2a4ef1d3f6fa3457406e932873db73` |
| `run_disposable_mutations.py` | `8576247e54ba2fb46994e9cd55a4d77550762020ca80a78a32d10a4bdc7f7e27` |

- Candidate 固定身份：72 个普通文件。按相对路径排序，对每个文件生成 `<relative-path><TAB><sha256><LF>` 后再 SHA-256，结果必须为 `cc1ff0f05d5d3993c8b113dae80a043b3d7f535a05a8236771b980a4892718a3`。
- 全部固定输入和 candidate tree 任一漂移：Blocked；不得用新 hash 追认或修复。

## 引用的 L1

L1-1 至 L1-10 全部适用，重点为数据主权、内容身份、生命周期完整、失败关闭、用户控制、审计可信、Evidence 诚实、历史保全、授权不漂移与可复核性。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---:|---|---|
| ABF-I-01 | 独立性与读序 | P0 | 全新合格会话；独立 test design/hash 先于工程 verifier／mutation 源码和结果阅读 | Blocked/Rework |
| ABF-I-02 | 固定身份与历史 | P0 | 12 项固定输入、72-file candidate tree 全匹配；历史零写入 | Blocked/Rework |
| ABF-I-03 | 真实数据零访问 | P0 | Pilot-2 路径／DB metadata 与内容访问 0；真实 app 启动 0 | Blocked/Rework |
| ABF-I-04 | Candidate／能力最小化 | P0 | 仅三 IPC；Schema/API/依赖/network/capability 漂移 0 | Rework |
| ABF-I-05 | 独立合成生命周期 | P0 | 临时副本 offline locked test/build；8 tests 与失败关闭成立 | Rework |
| ABF-I-06 | 三页产品／体验 Evidence | P1 | 三态、导航、刷新、关闭重开、Tab/Enter 的脱敏资产逐行可复核，无动作替代 | Rework |
| ABF-I-07 | 内容身份与隐私 | P0 | Evidence 无原文／key／DB 内容；本地来源、AI／网络关闭态可辨 | Rework |
| ABF-I-08 | 独立 verifier | P0 | 评审自有 runner 从 raw／Manifest 重算，不导入或调用工程 runner 作为 Pass 主证据 | Rework |
| ABF-I-09 | Mutation specificity | P0 | 未篡改祖先含 `/disposable/` 副本 exit 0；六类 mutation 分别因唯一预期原因失败 | Rework |
| ABF-I-10 | Manifest／清理 | P0 | Review payload 可复算；唯一临时根、fixture、target、mutation 残留 0 | Rework |
| ABF-I-11 | 风险／冻结／阶段 | P0 | R-0040/R-0052 Open；R-0051 原有限关闭；Not Frozen；Stage 4 未进入 | Rework |

## 冻结验收矩阵

| 行 ID | 独立动作 | 预期结果 | Evidence |
|---|---|---|---|
| M-001 | 核对任务投递、模型、全新会话、ABF 与隔离历史 | 全匹配 | authorization／session-boundary |
| M-002 | 在读取工程 verifier／mutation 源码和结果前冻结独立 `test_design.md` 与 hash | 读序成立；旧 runner 未导入／执行 | test-design／read-order |
| M-003 | 复算 12 项固定输入及 72-file candidate tree | 全匹配 | fixed-inputs／candidate-manifest |
| M-004 | 正向复制 candidate 到唯一临时根并扫描禁项 | 历史 Evidence／tools／target 未进入 candidate copy | copy-inventory |
| M-005 | 临时副本 offline locked test/build | 命令 exit 0；8 tests；network 0 | raw logs／structured result |
| M-006 | 独立静态 IPC／capability／依赖／路径扫描 | 仅三 IPC；禁止能力 0 | static-results |
| M-007 | 独立解析初次／Rework dynamic closure 的 12 行和全部 hash | 逐动作完整；刷新≠关闭重开；Tab≠Enter | dynamic-audit |
| M-008 | 独立核对脱敏 JSON、AX、截图与 Manifest | 不含用户原文／key／DB 内容；状态、来源可辨 | privacy／identity audit |
| M-009 | 评审自有 verifier 重算初次与 Rework payload | 初次 37/37、Rework 38/38；missing/extra/drift/semantic error 0 | independent-verifier |
| M-010 | 未篡改完整副本置于祖先 `/disposable/noop` 后运行自有 verifier | exit 0、findings 0 | unchanged-control |
| M-011 | 在六个独立副本实施缺文件、hash、cleanup、negative、lifecycle、geometry mutation | 每项 exit 1，且仅匹配冻结预期原因 | mutation-matrix |
| M-012 | 只读重放提交 verifier，与自有结果交叉比较 | baseline/control/mutations 一致；提交 runner 不作为主证据 | cross-check |
| M-013 | 复核 PM finding、Rework 修复、历史与 candidate 不变 | `PM-CE-001` 可独立关闭 | closure-matrix |
| M-014 | 清理唯一临时根并生成 Review Manifest | 临时残留 0；Review Evidence 可复算 | cleanup／Manifest |
| M-015 | 核对风险、冻结、Stage 4 和外推边界 | 状态不变；无自动推进 | governance-result |

## Evidence 合同

- 独立 runner 源码必须保存在 `lifeos/reviews/LIFEOS-P3-112/evidence/tools/`，不得导入、复制或调用工程测试／verifier 作为 Pass 主证据。
- `test_design.md`、read-order、fixed-inputs、candidate manifest、copy inventory、offline logs、static、dynamic/privacy audit、independent verifier、control、六 mutation、cross-check、cleanup、逐行结果与顶层非自指 `MANIFEST.md` 全部必需。
- Review Evidence 禁止包含用户原文、key、DB 内容、Pilot-2 metadata 或任何可逆真实内容。
- PM 必须能在新的 `/private/tmp` 副本复算 Review payload 与关键反例。

## 计数与 Pass 公式

- P0：独立性、固定身份、真实数据零访问、能力边界、生命周期、隐私、verifier、mutation、历史、清理、风险／阶段。
- P1：三页体验／动态动作 Evidence 不完整或不可信。
- P2：非阻断清洁项；Pass 仍要求 0。
- Unknown：有 Evidence 但关键事实不可复核。
- Not Implemented：任一矩阵行、子动作或必需 Evidence 缺失。
- Pass：I-01–I-11、M-001–M-015 与全部子动作通过；P0/P1/P2/Unknown/Not Implemented 全 0；Pilot-2 访问 0；历史写入 0；临时残留 0；Manifest 可独立复算。
- N/A：不得用于独立性、固定输入、真实数据零访问、test/build、动态／隐私、verifier、control、mutation、清理或历史保全。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0。
- 同任务 Rework：仅 P3-112 自有 Review／runner／Evidence 缺陷，ABF、固定输入和边界不变。
- 必须新建任务：候选／固定输入、ABF、目录、数据、真实 app、入口、能力、授权、Schema/API、风险、冻结、阶段变化，或两轮用尽／独立性污染。
- Blocked：正确模型／离线工具不可用；固定输入漂移；唯一临时根预存；无法证明新会话独立；任务需要访问 Pilot-2 或启动真实 app。

## 启动前质疑窗口

- 在任何 copy、test、build、工程 verifier／mutation 源码或结果阅读前，核对模型、会话独立性、固定输入、candidate tree、唯一临时根不存在、Pilot-2 零访问和读序。
- 有歧义立即停止；专项不得修改本 ABF。
- 最终冻结版本：`ABF-P3-112-v1`。
