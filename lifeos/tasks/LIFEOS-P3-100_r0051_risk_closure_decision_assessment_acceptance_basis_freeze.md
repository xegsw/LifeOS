# LIFEOS-P3-100 Acceptance Basis Freeze｜R-0051 风险关闭决策评估后继

## 冻结信息

- 任务 ID：`LIFEOS-P3-100`
- ABF ID／版本：`ABF-P3-100-v1`
- 生效决策：`D-0412`
- 冻结完成时间：2026-08-22 23:43:47 CST (+0800)
- 时间语义：以上时间是 PM 在创建本 ABF 时取得的已发生本地时间；文件 SHA-256 由写入完成后计算并记录在任务卡／D-0412。专项会话只需核对该时间早于其任务卡接收时间，不得要求两者完全等同。
- ABF 文件 SHA-256：由 PM 冻结后记录；本文件不使用自指 hash。
- 状态：Frozen
- 本文件是否在专项会话开始前冻结：Yes

## 本轮唯一用户结果

- 单一结果：在新的独立会话中，基于固定 P3-097/P3-098 技术证据与 P3-099 Blocked 历史，形成 R-0051 的可复核三分风险建议：`Recommend Limited Closure`、`Keep Open` 或 `Blocked`。
- 不冻结：工程、Schema/API、技术架构、真实本地数据能力、生产 SLA、工程基线或 Stage 4。
- 非范围：不修改工程或账本；不直接关闭／重开风险；不访问真实个人文件／DB／路径；不验证并发、崩溃、网络文件系统、永久 OS 拒绝或生产部署；不启用网络、云、第三方、Vault、Tauri/IPC、导出、同步、多设备、L3 或外部用户。

## 授权与能力边界

- 允许写入：仅 P3-100 自身 deliverable、independent review、Evidence、local precheck，以及新建 `/private/tmp/lifeos-p3-100-*` 固定非敏感目录。
- 允许读取：任务卡列明的项目资产、源码、Review、Evidence、Manifest 和固定非敏感夹具。
- 允许入口：只读 hash／Manifest 复算、静态检查；可运行固定 P3-098 独立 runner，输出只能写入 P3-100 自身 Evidence／临时目录。
- 严格只读：P3-094 至 P3-099 全部任务、工程、Review、Evidence、Manifest 与 PM 账本。
- 禁止：真实个人数据／文件／DB／路径、网络或任何外部目标。
- 风险关闭授权：本任务只产生建议。真正关闭 R-0051 仍须 PM 验收和用户在任务完成后的再次明确确认。

## 模型路由的治理修正

- PM 推荐路由：`gpt-5.6-terra` / `xhigh`，不允许主动降级。
- 模型路由是 PM／系统派发元数据，不是产品风险 Evidence，也不是专项会话必须从不可观察接口反向证明的事实。
- 专项会话须诚实记录界面实际暴露的配置；若接口不暴露精确 SKU／推理档位，记录 `not exposed`，不构成 Unknown、Blocked 或降级证据。
- 只有界面明确显示实际配置与任务卡冲突，或专项会话主动更换配置，才触发停止并回报 PM。

## 引用的 L1

- L1-1 数据主权；L1-3 生命周期完整；L1-4 失败关闭；L1-6 审计可信；L1-7 Evidence 诚实；L1-8 历史保全；L1-9 授权不漂移；L1-10 可复核性。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败状态 |
|---|---|---|---|---|
| ABF-I-01 | 授权与新会话独立 | P0 | 任务卡由用户投递；新会话未参与 P3-094 至 P3-099 的工程、独立评审或 PM 验收；记录接收时间与可观察运行配置 | Blocked |
| ABF-I-02 | 冻结先后成立 | P0 | ABF hash 匹配，冻结完成时间早于新会话接收时间 | Blocked |
| ABF-I-03 | 固定输入完整 | P0 | 13 个技术根资产与 7 个 P3-099 历史根资产全部 hash 一致 | Keep Open 或 Blocked |
| ABF-I-04 | 四层 Manifest 完整 | P0 | P3-097 Engineering 16/16、P3-097 PM 23/23、P3-098 Independent 14/14、P3-098 PM 18/18 一致 | Keep Open |
| ABF-I-05 | 历史失败链闭环 | P0 | P3-094/095/096 每类已知缺陷映射到 P3-097/098 当前独立证据，无遗漏 | Keep Open |
| ABF-I-06 | 完成点与失败关闭 | P0 | live DB 原子发布是唯一不可逆点；发布前失败零公开变化，发布后资源释放错误不误报失败 | Keep Open |
| ABF-I-07 | task-local 生命周期边界 | P0 | 路径规范化、祖先／最终链接、hardlink、特殊文件、页面、SQLite、staging／sidecar 全部有当前证据 | Keep Open |
| ABF-I-08 | Schema、来源与审计 | P0 | canonical Schema、`local_capture`、数量／时间／顺序变异均 fail closed | Keep Open |
| ABF-I-09 | 决策诚实 | P0 | 缺陷→Keep Open，必要输入不可得→Blocked，全部关闭门满足→Recommend Limited Closure | Rework |
| ABF-I-10 | 有限范围与重开条件 | P0 | 建议列出固定 hash、单进程／离线／task-local 边界、全部非范围和可执行重开触发器 | Keep Open |
| ABF-I-11 | 无越权状态变化 | P0 | 不改工程、历史 Evidence、风险、冻结、基线或阶段；临时残留为零 | Rework 或 Blocked |

## 冻结矩阵

| 行 ID | 独立动作 | 通过条件 | 测试 ID | Evidence |
|---|---|---|---|---|
| ABF-M-001 | 核验投递、新会话、接收时间、可观察配置 | I-01/I-02 成立 | P3-100-AUTH-001 | `session_start.json` |
| ABF-M-002 | 复算 20 个固定根资产 | 20/20 一致 | P3-100-HASH-002 | `input_hashes.json` |
| ABF-M-003 | 复算 P3-097 Engineering Manifest | 16/16 | P3-100-MAN-003 | `manifest_results.json` |
| ABF-M-004 | 复算 P3-097 PM Manifest | 23/23 | P3-100-MAN-004 | `manifest_results.json` |
| ABF-M-005 | 复算 P3-098 Independent Manifest 与唯一 ID | 14/14，45 个 test/fixture/execution ID 唯一 | P3-100-IND-005 | `manifest_results.json` |
| ABF-M-006 | 复算 P3-098 PM Manifest | 18/18 | P3-100-MAN-006 | `manifest_results.json` |
| ABF-M-007 | 全新 `/private/tmp/lifeos-p3-100-*` 复跑 P3-098 runner | 45/45 PASS、退出 0、计数全零 | P3-100-RUN-007 | `rerun/`, `rerun.log` |
| ABF-M-008 | 逐项映射历史风险链 | 无未映射缺口 | P3-100-RISK-008 | `risk_coverage_matrix.json` |
| ABF-M-009 | 静态核对禁止能力与范围 | 关闭态成立 | P3-100-SCOPE-009 | `static_scope_scan.json` |
| ABF-M-010 | 应用三分结论公式 | 结论与证据一致 | P3-100-DEC-010 | `risk_decision.json` |
| ABF-M-011 | 核对关闭边界与重开条件 | 完整、无生产外推 | P3-100-BOUND-011 | `risk_decision.json` |
| ABF-M-012 | before/after hash 与临时清理 | 输入无变化、残留为零 | P3-100-CLEAN-012 | `input_hashes.json`, `temporary_residue.json` |

## Evidence 与 Pass 公式

- 必须提供：任务专属 runner、12 行结构化矩阵、input hash、Manifest 结果、风险覆盖矩阵、风险建议、静态扫描、复跑日志／结果、临时残留、复跑命令和非自指 Manifest。
- 任务完成：12/12 行实际执行；任务自身 P0/P1/P2/Unknown/Not Implemented 全零；Manifest、只读保全与清理成立；三分结论准确。
- `Recommend Limited Closure`：风险基础 P0/P1/P2/Unknown/Not Implemented 全零，全部关闭门满足。
- `Keep Open`：发现实质技术缺口或关闭门不满足；这是有效任务结果，不自动构成 Rework。
- `Blocked`：必要输入、授权、独立性或安全本地环境不可得。
- 不允许用汇总 PASS 批量替代矩阵行，不允许把 `not exposed` 的模型内部标签计为 Unknown。

## Rework、退出与新任务

- 正式 Rework：0/2；仅 P3-100 自身同范围 Evidence／方法／文案问题可 Rework。
- 工程缺陷、输入基线变化、新能力、真实数据／路径、并发／崩溃、风险边界、架构、Schema/API、冻结、基线、阶段变化或两轮 Rework 后仍失败，必须停止并触发新任务。
- 专项会话不得关闭风险或创建后续任务。

## 候选与历史保全

- 13 个技术根资产：沿用 P3-099 任务卡“固定根资产”表，必须逐项复算，不得只相信其叙述。
- 7 个 P3-099 历史根资产：由 P3-100 任务卡列明 hash。
- P3-098 `source_history_hashes.json` 的 310 项历史集合继续只读。
- 允许变化：仅 P3-100 自身 deliverable、Review、Evidence 和 local precheck。

## 启动前质疑窗口

- 新会话在任何 hash／复跑动作前核对 ABF hash、冻结完成时间与接收时间。
- 歧义须在动作前停止；启动后不得修改本 ABF。
