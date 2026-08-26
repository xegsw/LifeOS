# LIFEOS-P3-123 Acceptance Basis Freeze｜P3-122 组合候选全新隔离独立复评

## 冻结信息

- 任务 ID：`LIFEOS-P3-123`
- ABF ID／版本：`ABF-P3-123-v1`
- 生效决策：`D-0495`
- 创建与冻结时间：2026-08-26 CST (+0800)
- ABF 文件 SHA-256：冻结后由 PM 记录；本文件不使用自指 hash。
- 状态：Frozen / Awaiting Task-card Delivery
- 本文件是否在专项会话开始前冻结：Yes
- 正式 Rework：0/2

## 本轮唯一用户结果

- 由与 P3-122 工程执行和 PM 验收均隔离的全新 Codex 评审会话，使用自写独立 runner 和全新合成 DB，对 P3-122 最终候选的 P3-116 视觉直接继承、三档 native/WebView/DOM 逻辑视口、三 IPC Runtime 生命周期、失败关闭、禁止能力、Evidence 语义和完整 lineage 做一次全新隔离独立复评，并给出 Pass、Rework 或 Blocked。
- 不冻结产品需求、视觉、Runtime、架构、Schema/API 或工程基线。
- 非范围：真实使用、Pilot、真实 DB／路径／文本、网络、产品模型、新 IPC、clear/export/权限/恢复、风险关闭、Stage 4。

## 授权和能力边界

- 允许目录：`lifeos/reviews/LIFEOS-P3-123/`、指定独立评审交付物、P3-123 本地预检报告、`/private/tmp/lifeos-p3-123-independent-review-v1`。
- 允许数据：全新固定非敏感合成 DB 与最多两条任务内固定短文本；不得复用 P3-122 DB。
- 允许入口／接口：P3-122 final candidate/build 的只读副本；仅 `capture_record`、`get_today`、`runtime_status`。
- 允许工具／环境：本地离线 Rust/Cargo/Tauri、SQLite、原生窗口／WebView/DOM geometry、实际 App screenshot、只读 hash 与独立 mutation。
- 严格只读：P3-116/P3-120/P3-121/P3-122 全部 task、ABF、candidate、delivery、Review、Evidence、Manifest 与账本。
- 禁止：修改或调用 P3-122 runner 作为独立判断逻辑；Pilot、真实 DB／路径／文本；网络、模型、云／第三方；新 IPC/capability/Schema/API；系统显示缩放或辅助功能变更；风险／冻结／阶段变化。
- 投递前额外用户确认：Completed。用户已确认两个新根、全新合成 DB、P3-122 candidate/Evidence/Review 全部只读、仅三 IPC 的 offline actual-Tauri 独立复评，以及禁止 Pilot／真实 DB／路径／文本／网络／产品模型。授权 Manifest：`lifeos/reviews/LIFEOS-P3-122/pm_evidence/p3-123-authorization/MANIFEST.md`，SHA-256 `c8c804de0c596e2ca210a46a81618716a8b9589ec99b46d0ab0e75a3519f3b21`。

## 引用的 L1 长期原则

- L1-1 数据主权：仅 P3-123 review root、唯一 temp root 与全新合成 DB。
- L1-3 生命周期完整：首次、幂等、刷新、关闭重开与失败路径必须一致。
- L1-4 失败关闭：失败不得改变 DB、sentinel、页面成功态或历史资产。
- L1-6 审计可信：逻辑 geometry、物理截图、build、DB 与 audit 语义一致。
- L1-7 Evidence 诚实：不得复用执行侧自证或用截图替代 geometry。
- L1-8 历史保全：P3-122 与上游全部只读。
- L1-9 授权不漂移：P3-122 授权不得自动延续。
- L1-10 可复核性：独立 runner、逐行结果、hash、Manifest、mutation 与 cleanup 可复跑。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 新会话、新 runner、新根与授权独立 | P0 | 不导入／调用／复制 P3-122 runner；固定输入匹配后才创建 | Blocked/Not Pass |
| ABF-I-02 | P3-116 actual visual 直接继承真实成立 | P0 | 8/8 source 与 candidate 映射、DOM/CSS/Token、页面专属结构独立复算 | Rework |
| ABF-I-03 | P3-121 UI 未污染视觉层 | P0 | visual positive set 与 P3-121 `ui/` 不相交 | Rework |
| ABF-I-04 | 三档逻辑视口与宿主截图语义分离 | P0 | native content、WebView/DOM、DPR、display、screenshot 分栏一致 | Rework/Unknown |
| ABF-I-05 | 六个页面／状态在三档均真实可达 | P1 | 18/18 actual-App 独立动作与截图/geometry | Rework |
| ABF-I-06 | 三 IPC 生命周期未退化 | P0 | first/repeat/refresh/reopen 与 DB/audit/UI 一致 | Rework |
| ABF-I-07 | 失败关闭与禁能边界成立 | P0 | failure before change；仅三 IPC，无 network/model/new capability | Rework |
| ABF-I-08 | Final Manifest 和历史谱系完整 | P0 | current/history/auth/PM/delivery/cleanup 全覆盖且 hash 匹配 | Rework |
| ABF-I-09 | 独立 mutation fail closed | P0 | pristine PASS；至少 9 类对应变异全部拒绝 | Rework |
| ABF-I-10 | 精确清理 | P0 | 唯一 temp root absent；无越界删除 | Rework |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | preflight | 两根不存在 | 复算授权、ABF、P3-122 final hashes、模型与只读输入 | 全匹配后才创建 | P3-122 history | P123-M001 | preflight.json |
| ABF-M-002 | independence | fresh review root | 静态及运行时证明 runner 未导入／调用 P3-122 tool | 独立实现 | P3-122 tools | P123-M002 | independence.json |
| ABF-M-003 | source lineage | read-only candidate | 独立复算 visual 8/8、Runtime 65/65、candidate tree | 分层一致 | all sources | P123-M003 | source-lineage.json |
| ABF-M-004 | build | isolated copy | locked offline test/build/bundle | exit 0、无网／外部写 | history | P123-M004 | build logs |
| ABF-M-005 | pages | actual Tauri | 六页面在三档逐一导航／展开 | 18/18 可达且忠实 | candidate | P123-M005 | page matrix/screenshots |
| ABF-M-006 | geometry | actual Tauri | 独立采集 native/content/WebView/DOM/DPR/display | 三档逻辑尺寸与语义一致 | DB/history | P123-M006 | geometry traces |
| ABF-M-007 | host adaptation | current display | 验证裁剪、overflow、主操作、Rail、Global AI | 应用适配且诚实披露 | system scaling | P123-M007 | responsive results |
| ABF-M-008 | Runtime | fresh DB | status、first、repeat、refresh、close/reopen | 三 IPC/DB/audit/UI 一致 | source/history | P123-M008 | runtime results |
| ABF-M-009 | failures | disposable DB/sentinel | path/type/DB/atomic failure | 失败先于变更 | DB/sentinel/UI | P123-M009 | negatives |
| ABF-M-010 | prohibited | candidate/review roots | 独立 inventory 与静态/运行态扫描 | 无禁能或越界 | all roots | P123-M010 | boundary.json |
| ABF-M-011 | lineage | completed evidence | 独立重算 Engineering Final Manifest 与 PM inputs | 无遗漏／错绑／自指 | history | P123-M011 | lineage.json |
| ABF-M-012 | mutations | pristine pass | visual drift、UI contamination、auth/PM omission、viewport/screenshot/candidate/history/extra-file mutations | 每类 fail closed | pristine copy | P123-M012 | mutation-results.json |
| ABF-M-013 | cleanup | app closed | 精确删除固定 temp files/root并复算 history | root absent、history unchanged | review evidence | P123-M013 | cleanup.json |
| ABF-M-014 | final review | all rows complete | 生成独立 Review、Manifest 与五类计数 | 可复核结论 | P3-122 assets | P123-M014 | independent_review.md/manifest |

## Evidence 合同

- runner：P3-123 自写，保存完整源码；禁止复制、import、subprocess 调用 P3-122 `build_evidence.py`。
- 每行独立记录 frozen action、test ID、实际 Evidence、hash 与结论；不得用汇总 PASS 批量代替。
- 三档各保存 native trace、renderer geometry、六页面 actual-App screenshot/AX、candidate/build hash。
- Runtime 使用全新 DB；保存 before/after DB、audit、sentinel、UI 与重启状态。
- Final Manifest 非自指，覆盖授权、ABF、inputs、runner、results、screenshots、review、cleanup；对遗漏／漂移 fail closed。
- 复跑及临时清理只使用拟确认的固定根；不得使用 glob、`find` 或宽前缀删除。

## 计数与 Pass 公式

- P0：独立性失败、视觉/Runtime source 错绑、逻辑/物理语义混淆、越界、历史修改、失败后变更、谱系遗漏或错误清理。
- P1：三档适配或关键页面／交互退化。
- P2：不影响完成定义的轻微差异；本轮 Pass 仍要求 0。
- Unknown：任一独立状态、geometry、Runtime、lineage、history、cleanup 无法复核。
- Not Implemented：任一不变量、矩阵行、runner、Evidence、mutation 或 cleanup 缺失。
- Pass 公式：I-01～I-10、M-001～M-014 全部 PASS；五类计数全零；silent N/A 为 0。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0/2。
- 同任务 Rework：仅 P3-123 自有 runner、Evidence、Manifest 或 Review；P3-122 candidate/ABF 和本 ABF 不变。
- 必须新建任务：需修改 P3-122 candidate、改变 ABF、目录、数据、IPC/capability、架构、真实边界、风险／冻结／阶段，或两轮 Rework 耗尽。
- Blocked：离线工具链或 actual Tauri 无法在已确认边界启动，且不能安全替代；不得退回浏览器／静态自证。

## 候选基线与只读保全

- P3-122 PM Review：`1f921a55dec6ebb9b518a1ee3a8bf83ae6ec450a9d78d399e533abedb8f55efe`。
- P3-122 Engineering Final Manifest：`b555e657ba3b44d855b7885c24714face84e640daee73525be98003506f69a6c`。
- P3-122 PM acceptance Manifest：`c8fac52c00df7fa1308bb6f6143c8a13fec83568e19b31afb6bd17dd9b1a7966`。
- P3-122 final adoption Manifest：`fc65335b73280b64888c5803bcacf4402771c5b9cb69eaeac7117c20076adecc`。
- P3-122 candidate source allowlist 75/75：`lifeos/tasks/LIFEOS-P3-123_candidate_source_allowlist.md`，SHA-256 `a5b8bd56114fd1091996b2fb0094ebb7a7f5c9ee4f9e3ddbfbe11780f9e437b7`；tree hash `ece442bb7cae7adb00232d672fae60fda2f1f3728f993b5d63d6e8c9fd676742`。
- 允许变化：仅待确认的 P3-123 review root、P3-123 delivery/local precheck 与唯一 temp root。

## 启动前质疑窗口

- 执行方是否提出歧义：N/A；尚未投递。
- PM 处理：用户已完成精确边界确认；PM 已复算候选 75/75、关键 PM/Engineering 输入，确认两个执行根不存在并冻结本 ABF。
- 最终冻结版本：`ABF-P3-123-v1`。
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
