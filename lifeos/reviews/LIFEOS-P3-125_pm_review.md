# LIFEOS-P3-125 PM Review

## 验收信息

- 任务 ID：`LIFEOS-P3-125`
- Acceptance Basis Freeze：`lifeos/tasks/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure_acceptance_basis_freeze.md`
- ABF ID／版本／SHA-256：`ABF-P3-125-v1` / `4ab5ed8a0c1349041d1d9b13452be5059abf510f4d2ecae386e23283c1956057`
- ABF 是否在专项会话开始前 Frozen：Yes
- 本次反例是否全部映射到既有 L1/L2：Yes；L1-6、L1-7、L1-9、L1-10，ABF-I-01、I-02、I-06～I-08，ABF-M-001、M-010～M-012
- 正式 Rework 次数／上限：`1/1`
- 是否为受控能力包：Yes
- 能力包边界：仅 P3-125 单一构建时 Runtime root、三 IPC、合成 DB、task-local Evidence；候选、ABF、目录、数据与产品范围不扩大。
- 专项交付物：`lifeos/deliverables/LIFEOS-P3-125_runtime_root_configurable_fail_closed_closure.md`
- PM Review：`lifeos/reviews/LIFEOS-P3-125_pm_review.md`
- 执行授权证据核验：最终任务卡绝对路径、新工程会话及 D-0504 synthetic-only Tauri/IPC 边界已记录；授权有效。
- 任务验收状态：`Rework 1/1 / Awaiting User Adoption / Acceptance Basis Unchanged`
- 资产冻结状态：Not Frozen
- 是否允许进入下一任务：No
- 是否允许进入下一阶段：No
- 是否只是后续任务输入：No；当前 P0 与完成定义尚未关闭
- 实际执行 Agent：Codex
- Agent 与任务匹配度：Medium
- 更新时间：2026-08-26

## PM 总结

- PM 接受 75-file source lineage、仅 `build.rs`/`runtime.rs` 两个 candidate 文件变化、离线 4/4 unit tests、run-a/run-b/final actual-App 资产、三 IPC不变和固定 temp root 已清理等已完成事实。
- PM 不接受专项 `Completed / 31/31 PASS` 作为 ABF Pass：Frozen M-011 明确要求 pristine control 后对 root/fallback/derive/order/history/extra-file mutations 逐类 fail closed，但提交物没有 `mutation-results.json`，且把 M-011 改写成 Quick Capture 动作。
- Frozen M-012 要求独立 cleanup/final 行、`cleanup.json`、历史／授权／当前 Evidence 完整 Final Manifest；提交的动态闭环只有 7 个聚合行、没有 M-012，也没有 cleanup 结构化结果。
- Final Manifest 声明 104 项。PM 按声明路径复算时，103 项可解析且匹配；`../deliverables/...` 从 Engineering root 解析为不存在的 `lifeos/engineering/deliverables/...`。虽然其 hash/bytes 与真实 `lifeos/deliverables/...` 相同，但路径语义错误，Manifest 不能证明它声称的资产。
- Final Manifest 仅列 current engineering tree 和 deliverable，未覆盖 ABF 要求的 task、ABF、source allowlist、user confirmation、Freeze Manifest、P3-122/P3-124 history、cleanup 或 mutation，I-06/I-07/M-010～M-012 未闭合。
- `build.rs` 仍硬编码 `ALLOWED_PARENT=/private/tmp/lifeos-p3-125-runtime-root-config-v1`。这把原 P3-122 task-ID 固定根替换为 P3-125 task-ID 固定父根，`LIFEOS_RUNTIME_ROOT` 不是唯一路径权威；新隔离后继若采用自身根会再次无法构建。该问题映射 I-01/I-02 与本任务“可配置化”唯一结果，不是新增偏好。
- 实际 model/effort 仍为 Unknown；M-001 与 Pass 公式均不允许 Unknown。工程会话在最终 Rework 前必须提供平台实际配置记录，不能用任务卡推荐值代替。
- 本轮跳过本地模型预检：这是 P0 路径授权、Tauri/IPC 与 Evidence 最终判断，本地模型不得裁决。

## 两层验收治理核对

- 违反或未满足的 L1：L1-6 审计可信、L1-7 Evidence 诚实、L1-9 授权不漂移、L1-10 可复核性。
- 冻结 L2：I-01/I-02、I-06～I-08；M-001、M-010～M-012。
- PM 是否新增无法映射的标准：No。
- 新发现问题分类：当前任务失败／同任务唯一正式 Rework。
- 是否需要实质修改 ABF：No。
- 是否仍满足同任务 Rework全部条件：Yes；同一用户结果、目录、数据、三 IPC、风险和授权均不变。
- 是否达到两轮正式 Rework 上限：本任务上限为 1；本次正式进入唯一一轮 `1/1`，尚可执行一次窄整改。
- 终止状态：N/A；若 Rework-1 仍未满足，必须关闭为 `Closed — Acceptance Not Met`，不得再 Rework。
- 新任务触发理由：当前无；若需要新增路径入口、配置变量、目录、IPC、Schema/API 或授权边界则必须新建。

## P3 快车道 Review

不适用。本任务是 P0 Tauri/IPC 路径安全补丁。

## 角色与关卡验收

- 主责角色覆盖：候选实现与主要正负向测试已覆盖；Evidence/Manifest 与跨任务可配置性未闭合。
- 协审角色覆盖：数据主权与失败关闭有单测输入，但完整 history/mutation/cleanup 证据缺失。
- 已通过：75/75 source lineage、73 个候选文件无漂移、三 IPC静态合同、4/4 unit tests、submitted actual-App/SQLite/geometry payload hash、temp root 当前 absent。
- 未通过：Gate 2 的完整历史／来源 Evidence；Gate 4 的唯一配置权威、mutation、Final Manifest 和 model route；Gate 1/3 只完成静态无扩张检查；Gate 5 不适用。
- 是否需要独立评审：当前不创建。PM Pass 与用户采纳后才可创建 P3-126。
- 是否允许进入下一任务／阶段：No / No。

## P0／P1／P2／Unknown／Not Implemented

| 类别 | 数量 | PM 结论 |
|---|---:|---|
| P0 | 2 | ① 固定 `ALLOWED_PARENT` 使 root 配置仍绑定 P3-125 task ID；② M-011/M-012、history/authorization/cleanup/Manifest 证据链缺失且提交仍声明完成。 |
| P1 | 0 | 未确认新的 actual-App 功能退化。 |
| P2 | 0 | 无仅文案级阻断项。 |
| Unknown | 1 | 实际 model/effort 无可核验记录，M-001 未闭合。 |
| Not Implemented | 2 | Frozen M-011 mutation 与 M-012 cleanup/final 独立矩阵行未实现。 |

## Rework 1/1 最终窄整改边界

1. ABF、任务卡、P3-122/P3-124 历史、initial candidate/Evidence/delivery 全部只读；Rework 新资产写入 P3-125 自有 `rework-1/` 子目录或任务卡既有自有目录，不覆盖 initial Evidence。
2. 消除 production source 中 P3-125 task-ID 固定父根；仍只保留一个构建时 `LIFEOS_RUNTIME_ROOT`。构建器须验证绝对／规范／真实无链接根，但本轮 runner 只允许 ABF 已授权的 P3-125 子根；不得增加第二配置变量、运行时路径选择、设置页、CLI、IPC 或目录。
3. 为 M-001～M-012 各自产生独立结构化行，不聚合、不改写行义；补 `preflight.json`、`history-integrity.json`、`boundary.json`、`cleanup.json`。
4. M-011 必须先证明 pristine verifier PASS，再对 frozen root、fallback、DB/viewport/geometry derivation、验证顺序、history hash、extra file 与 Manifest path/omission 等变异逐类拒绝，生成 `mutation-results.json`。
5. 修复 Final Manifest 路径语义；Manifest 必须覆盖 task、ABF、allowlist、user confirmation、Freeze Manifest、P3-122/P3-124 history、initial/current candidate、initial/Rework Evidence、delivery、mutation 与 cleanup，且非自指。
6. verifier 必须实际解析每个 Manifest path 并复算 bytes/hash，验证无遗漏、错路径、extra file、history drift、self-inclusion；不能只读取 `verification_result` 字段。
7. 记录实际 model/effort 的平台可见配置。若仍无法获得，必须在任何 Rework 工程动作前停止回 PM，不得再次以 Unknown 提交完成。
8. 只使用原固定 P3-125 temp root和全新合成 DB；结束后精确清理。禁止访问旧 P3-122 root、Pilot、真实数据／路径、网络或模型。

## 风险与冻结

- R-0040、R-0052 及其他 Open 风险状态不变。
- R-0051 保持原有限关闭，不因本轮重开或扩大。
- P3-125 Not Frozen；不恢复工程基线，不冻结产品/runtime/Schema/API，不进入 Stage 4。
- `RISK_LOG.md`、`FREEZE_STATUS.md` 无需更新。

## 需要用户确认

- 是否采纳 `Rework 1/1` 并授权同一 P3-125 按上述不变 ABF 进行最终窄整改。
- PM 建议：采纳。整改只关闭已冻结的单根权威、逐行 Evidence、mutation、Manifest、model route 与 cleanup，不扩大产品能力。
- 若本轮再次不满足：关闭 P3-125，不允许第二轮 Rework；后续只能新任务、新授权、新 ABF。

## Agent 分派与适配度

- 推荐／实际 Agent：Codex / Codex。
- 匹配度：Medium。
- 优点：核心 Rust 路径补丁、actual-App 取证和失败关闭测试已形成可用基础。
- 问题：把冻结 mutation 行改写为 UI 动作，遗漏 final/cleanup 行，Manifest verifier 未验证 Manifest，且把固定 task parent误当成完全可配置。
- 建议复用原 P3-125 工程会话完成唯一 Rework；后续 P3-126 必须全新隔离。

## 最终结论

- `REWORK 1/1 / NOT PASS / AWAITING USER ADOPTION`
- P0/P1/P2/Unknown/Not Implemented：`2/0/0/1/2`
- 不允许 P3-126、P3-127、P3-128 或 Stage 4。
