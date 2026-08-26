# LIFEOS-P3-124 Acceptance Basis Freeze｜P3-122 组合候选独立复评最终后继

## 冻结信息

- 任务 ID：`LIFEOS-P3-124`
- ABF ID／版本：`ABF-P3-124-v1`
- 生效决策：D-0499。
- 创建时间：2026-08-26 CST (+0800)
- 状态：Frozen / Executable only after final task-card delivery
- 本文件是否在专项会话开始前冻结：是。
- 正式 Rework：0/2。

## 本轮唯一用户结果

- 由与 P3-122 工程、P3-123 评审和 PM 验收隔离的全新 Codex 会话，使用自写 runner 与全新合成 DB，对 P3-122 最终候选完成一次 offline actual-Tauri 独立复评，并给出 Pass、Rework 或 Blocked。
- 不冻结产品需求、视觉、Runtime、架构、Schema/API 或工程基线。
- 非范围：真实使用、Pilot、真实 DB／路径／文本、网络、产品模型、新 IPC、clear/export/权限/恢复、风险关闭和 Stage 4。

## 授权和能力边界

- 允许目录：`lifeos/reviews/LIFEOS-P3-124/`、指定交付物、P3-124 本地预检、`/private/tmp/lifeos-p3-124-independent-review-v1`。
- 允许数据：全新固定非敏感合成 DB，最多两条任务内固定短文本。
- 允许入口：P3-122 final candidate/build 的只读副本；仅 `capture_record`、`get_today`、`runtime_status`。
- 允许工具：本地离线 Rust/Cargo/Tauri、SQLite、native/WebView/DOM geometry、实际 App screenshot、只读 hash 与 disposable mutation。
- 严格只读：P3-116～P3-123 全部 task、ABF、candidate、delivery、Review、Evidence、Manifest 与账本。
- 禁止：历史 runner 复用；Pilot、真实 DB／路径／文本；网络、模型、云／第三方；新 IPC/capability/Schema/API；系统显示缩放或辅助功能变更；风险、冻结或阶段变化。
- 投递前额外用户确认：Completed in PM main session on 2026-08-26；证据见 `lifeos/tasks/LIFEOS-P3-124_authorization/user_confirmation.md`。

## 引用的 L1 长期原则

- L1-1 数据主权：仅新 review root、唯一 temp root 与全新合成 DB。
- L1-3 生命周期完整：首次、幂等、刷新、关闭重开与失败路径一致。
- L1-4 失败关闭：失败不得改变 DB、sentinel、页面或历史资产。
- L1-6 审计可信：geometry、截图、build、DB 与 audit 语义一致。
- L1-7 Evidence 诚实：不得复用执行侧自证或以截图替代 geometry。
- L1-8 历史保全：P3-122/P3-123 及上游全部只读。
- L1-9 授权不漂移：P3-123 授权不自动延续。
- L1-10 可复核性：逐行结果、hash、Manifest、mutation 与 cleanup 可复跑。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 | 新会话、新 runner、新根、授权与物理多行 allowlist 独立 | P0 | 75 个物理数据行可直接解析，固定输入匹配后才创建执行根 | Blocked |
| ABF-I-02 | P3-116 actual visual 直接继承成立 | P0 | 8/8 source 映射、DOM/CSS/Token、专属结构独立复算 | Rework |
| ABF-I-03 | P3-121 UI 未污染视觉层 | P0 | visual positive set 与 P3-121 `ui/` 不相交 | Rework |
| ABF-I-04 | 三档逻辑视口与宿主截图语义分离 | P0 | native content、WebView/DOM、DPR、display、screenshot 分栏一致 | Rework/Unknown |
| ABF-I-05 | 六页面／状态在三档均真实可达 | P1 | 18/18 actual-App 动作、截图与 geometry | Rework |
| ABF-I-06 | 三 IPC 生命周期未退化 | P0 | first/repeat/refresh/reopen 与 DB/audit/UI 一致 | Rework |
| ABF-I-07 | 失败关闭与禁能边界成立 | P0 | failure before change；仅三 IPC且无网络/模型/新能力 | Rework |
| ABF-I-08 | Final Manifest 与历史谱系完整 | P0 | current/history/auth/PM/delivery/cleanup 全覆盖 | Rework |
| ABF-I-09 | 独立 mutation fail closed | P0 | pristine PASS，至少 9 类变异全部拒绝 | Rework |
| ABF-I-10 | 精确清理 | P0 | 唯一 temp root absent且无越界删除 | Rework |

## 冻结验收矩阵

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 | preflight | 两根不存在 | 直接解析新 allowlist；复算授权、ABF 与固定 hashes | 75 个物理数据行且全匹配后才创建 | P3-122/P3-123 history | P124-M001 | preflight.json |
| ABF-M-002 | independence | fresh review root | 证明 runner 未导入／复制／调用历史 tool | 独立实现 | historical tools | P124-M002 | independence.json |
| ABF-M-003 | source lineage | read-only candidate | 独立复算 visual 8/8、Runtime 65/65、candidate tree | 分层一致 | all sources | P124-M003 | source-lineage.json |
| ABF-M-004 | build | isolated copy | locked offline test/build/bundle | exit 0且无网／外部写 | history | P124-M004 | build logs |
| ABF-M-005 | pages | actual Tauri | 六页面在三档逐一导航／展开 | 18/18 可达且忠实 | candidate | P124-M005 | page matrix/screenshots |
| ABF-M-006 | geometry | actual Tauri | 采集 native/content/WebView/DOM/DPR/display | 三档逻辑尺寸与语义一致 | DB/history | P124-M006 | geometry traces |
| ABF-M-007 | host adaptation | current display | 验证裁剪、overflow、主操作、Rail、Global AI | 应用适配并诚实披露 | system settings | P124-M007 | responsive results |
| ABF-M-008 | Runtime | fresh DB | status、first、repeat、refresh、close/reopen | 三 IPC/DB/audit/UI 一致 | source/history | P124-M008 | runtime results |
| ABF-M-009 | failures | disposable DB/sentinel | path/type/DB/atomic failure | 失败先于变更 | DB/sentinel/UI | P124-M009 | negatives |
| ABF-M-010 | prohibited | fixed roots | inventory 与静态/运行态扫描 | 无禁能或越界 | all roots | P124-M010 | boundary.json |
| ABF-M-011 | lineage | completed evidence | 重算 Engineering Final Manifest 与 PM inputs | 无遗漏／错绑／自指 | history | P124-M011 | lineage.json |
| ABF-M-012 | mutations | pristine pass | 9 类视觉、授权、视口、谱系等变异 | 每类 fail closed | pristine copy | P124-M012 | mutation-results.json |
| ABF-M-013 | cleanup | app closed | 精确删除固定 temp root并复算 history | root absent、history unchanged | review evidence | P124-M013 | cleanup.json |
| ABF-M-014 | final review | all rows complete | 生成 Review、Manifest 与五类计数 | 可复核结论 | historical assets | P124-M014 | independent_review.md/manifest |

## Evidence 合同

- 保存 P3-124 自写 runner；禁止复制、import 或 subprocess 调用历史 runner。
- 每行独立记录 frozen action、test ID、实际 Evidence、hash 与结论。
- 三档保存 native trace、renderer geometry、actual-App screenshot 与 candidate/build hash。
- Runtime 保存全新 DB 的 before/after、audit、sentinel、UI 与重启状态。
- Final Manifest 非自指并覆盖授权、ABF、inputs、runner、results、screenshots、review、cleanup。
- 仅精确清理拟确认的唯一 temp root；禁止 glob、`find` 或宽前缀删除。

## 计数与 Pass 公式

- P0：独立性、source 绑定、授权、失败关闭、谱系、历史保全或清理失败。
- P1：三档适配或关键页面/交互退化。
- P2：不影响完成定义的轻微差异；Pass 仍要求 0。
- Unknown：任一实际状态、geometry、Runtime、lineage、history 或 cleanup 无法复核。
- Not Implemented：任一不变量、矩阵行、runner、Evidence、mutation 或 cleanup 缺失。
- Pass：I-01～I-10、M-001～M-014 全 PASS；五类计数全零；silent N/A 为 0。
- 模型路由：首报声明实际 model/effort；平台元数据可见时一并记录。平台未暴露元数据本身不进入产品五类计数；声明配置不合规则在工程动作前 Blocked。

## Rework 预算与退出规则

- 正式 Rework 上限：2；当前 0/2。
- 同任务 Rework：仅 P3-124 自有 runner、Evidence、Manifest 或 Review，且 Frozen ABF 和候选不变。
- 必须新建任务：需修改 P3-122 candidate、Frozen ABF、目录、数据、IPC、架构、真实边界、风险/冻结/阶段，或两轮耗尽。
- Blocked：固定输入、授权或离线 actual Tauri 无法在确认边界启动且无授权替代；不得退回浏览器或静态自证。

## 候选基线与只读保全

- P3-122 PM Review：`1f921a55dec6ebb9b518a1ee3a8bf83ae6ec450a9d78d399e533abedb8f55efe`。
- P3-122 Engineering Final Manifest：`b555e657ba3b44d855b7885c24714face84e640daee73525be98003506f69a6c`。
- P3-122 PM acceptance Manifest：`c8fac52c00df7fa1308bb6f6143c8a13fec83568e19b31afb6bd17dd9b1a7966`。
- P3-122 final adoption Manifest：`fc65335b73280b64888c5803bcacf4402771c5b9cb69eaeac7117c20076adecc`。
- Frozen physical multiline allowlist：`lifeos/tasks/LIFEOS-P3-124_candidate_source_allowlist.md`；87 个物理行、75 个 candidate 数据行，SHA-256 `198875e445c15469f4d02e7799368ac7d5ca05f7da1f672b356969a46dd593f5`，tree hash `ece442bb7cae7adb00232d672fae60fda2f1f3728f993b5d63d6e8c9fd676742`。
- P3-123 全部资产作为失败历史只读保全。
- 允许变化：冻结后仅 P3-124 review root、指定 delivery/local precheck 与唯一 temp root。

## 启动前质疑窗口

- 执行方是否提出歧义：N/A；尚未投递。
- PM 处理：用户已完成精确 Tauri/IPC 边界确认；PM 已复算格式、75 行、hash、roots 与授权并冻结。
- 最终冻结版本：`ABF-P3-124-v1`，D-0499。
- 专项会话开始后不得实质修改 Frozen ABF；如需修改，当前任务关闭并新建任务。
