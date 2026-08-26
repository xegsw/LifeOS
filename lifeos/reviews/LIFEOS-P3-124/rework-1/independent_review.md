# LIFEOS-P3-124 Rework 1｜独立评审

## 评审信息

- 对应任务 ID：`LIFEOS-P3-124`；同一任务的正式 Rework `1/2`。
- Frozen ABF：`ABF-P3-124-v1`，SHA-256 `b8504298cdc20dd3425eb519f556d27a3867640de3f8fb5a4476f81095356efc`；本轮未修改。
- 被评审对象：P3-122 75-file candidate 的 task-local、byte-exact 离线副本；候选与所有初始资产只读。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-124/rework-1/`。
- 主审角色：技术架构／Tauri-IPC／Evidence QA。
- 协审视角：体验设计、数据来源、AI 信任与安全。
- 评审关卡：Gate 4 实际 Tauri 技术复评；Gate 1/2/3/5 只作受限关闭态检查。
- 实际模型／推理：`gpt-5.6-terra + xhigh`，平台可见元数据见 `evidence/model-routing.json`。
- 初始 P3-124 Review/Evidence 是否只读保留：是；初始 PM Manifest 的 13/13 hash 在启动和 cleanup 后均匹配。
- 评审结论：**Blocked / Not Pass**。

## 结论摘要

1. `P124R-M001`、`M002`、`M003`、`M004`、`M011`、`M013` 已实际完成：75 条物理 allowlist、独立 runner、visual 8/8、runtime 65/65、离线 test/build/bundle、245 条 Engineering Manifest、历史保全和精确 cleanup 均有本轮 Evidence。
2. 本轮修复了初次 Review 的方法缺口：先绑定 task-local bundle 的 hash／`local.lifeos.p3-122`，自写 AppKit/CoreGraphics native helper，再以 Computer Use 对同一 bundle identifier 查询；没有以旧 P3-122 Evidence、缩略图、静态扫描或其他 LifeOS 应用替代实际 App。
3. 实际结果是 task-local bundle 在 `open -n` 后没有可绑定的进程或窗口：native helper 为同 bundle identifier 与精确 bundle 均报告 0 PID／0 native window；Computer Use target query 为 `timeoutReached`，运行 App inventory 不含目标。页面、IPC 或 UI 动作因此一个也没有执行。
4. 静态 source contract 显示 candidate 在 setup 阶段调用 native geometry 写入，且 `RUNTIME_ROOT`、`RUNTIME_DB`、viewport-request 全部固定为 `/private/tmp/lifeos-p3-122-native-evidence-v1`。这不在 P3-124 唯一获授权的 `/private/tmp/lifeos-p3-124-independent-review-v1` 内，且 candidate 只暴露 viewport 环境变量，不能重绑定 DB／geometry 根。
5. 第 3、4 点合在一起，是“在当前 Frozen ABF 与授权内无法取得实际 App PID/window”的可复核事实；“启动时因旧根的 geometry write 而退出”是由 source 与零 PID/window 形成的强推断，未将它写成未取得的 crash-log 事实。
6. 解决该冲突必须修改 candidate 的固定 runtime root，或修改 ABF／允许目录；两者均为当前 ABF 的实质变化，不能作为 P3-124 再次同任务 Rework 处理。

## P0／P1／P2／Unknown／Not Implemented

| 类别 | 数量 | 事实 |
|---|---:|---|
| P0 | 1 | Frozen candidate 的 setup geometry/DB root 与本轮唯一临时根冲突；为取得实际 App 必须越权写旧 P3-122 root，或变更 candidate/ABF/目录。映射 L1-1、L1-7、L1-9、ABF-I-01/I-04/I-10。|
| P1 | 0 | 初次“未穷尽 native target 路径”的 P1 已通过自写 native helper 与 Computer Use 同目标查询关闭；当前问题不是页面体验退化。|
| P2 | 0 | M-001 的三段根时间语义已分开记录，未再把当前 rework root 写作 absent。|
| Unknown | 1 | ABF-M-006 的实际 native/WebView/DOM/DPR/display geometry 不能在无 PID/window 下复核。|
| Not Implemented | 7 | ABF-M-005～M-010 与 M-012 的 actual-App 页面、geometry、生命周期、失败、运行态边界及 mutation 行没有开始；没有伪写 PASS。|

## 冻结矩阵逐行结果

| ABF 行 | 测试 ID | 实际 Evidence | 结论 |
|---|---|---|---|
| M-001 | P124R-M001 | `evidence/preflight.json` | PASS；allowlist 75/75，固定输入匹配；freeze/session/preflight-write 三个时间点分栏。|
| M-002 | P124R-M002 | `evidence/independence.json` | PASS；本轮 runner/helper 无历史 runner import、调用或动态 Python import。|
| M-003 | P124R-M003 | `evidence/source-lineage.json` | PASS；visual 8/8、runtime 65/65、当前 candidate 75/75 hash。|
| M-004 | P124R-M004 | `evidence/build-result.json`、`evidence/logs/` | PASS；locked/offline tests 和 App bundle 成功。|
| M-005 | P124R-UI-01..18 | `evidence/native-post-launch.json`、`evidence/computer-use-target.json`、`evidence/boundary-runtime-root.json` | NOT IMPLEMENTED；先决 PID/唯一 native window 未绑定，未导航任一页面。|
| M-006 | P124R-NATIVE-* | 同上 | UNKNOWN / NOT IMPLEMENTED；没有 native/WebView/DOM/DPR/display 实际 geometry。|
| M-007 | P124R-UI adaptation | 同上 | NOT IMPLEMENTED；未以静态布局替代实际主机适配。|
| M-008 | P124R-IPC-01..05 | 同上 | NOT IMPLEMENTED；未调用三 IPC，避免旧 P3-122 根写入。|
| M-009 | P124R-NEG-01..04 | 同上 | NOT IMPLEMENTED；未构造 DB/sentinel failure fixture。|
| M-010 | P124R-BND-ROOT-01 | `evidence/boundary-runtime-root.json` | NOT IMPLEMENTED；静态根冲突已证明，但运行态 prohibited-boundary 行不能在无 App 下声称 PASS。|
| M-011 | P124R-M011 | `evidence/lineage.json` | PASS；Engineering Final Manifest 245/245，PM/P3-123 输入按时间语义复核。|
| M-012 | P124R-MUT-01..09 | `evidence/boundary-runtime-root.json` | NOT IMPLEMENTED；无 pristine dynamic control，因此未执行九类 mutation。|
| M-013 | P124R-M013 | `evidence/cleanup.json` | PASS；同 bundle identifier 无进程/窗口，唯一 temp root 精确删除，初始 13/13 hash 未变。|
| M-014 | P124R-FIN-01 | 本 Review、`FINAL_MANIFEST.json` | BLOCKED / NOT PASS；Review/Manifest 已生成，但 Pass 公式不成立。|

## 关键 Evidence 与推断边界

- 事实：`evidence/native-post-launch.json` 保存 task-local executable SHA-256、bundle ID、native helper 以及零精确 PID/window。
- 事实：`evidence/computer-use-target.json` 仅保留目标 query timeout 与“target 未在 inventory 中”；没有保留环境中其他应用资料。
- 事实：`evidence/boundary-runtime-root.json` 从 byte-exact candidate 和 task-local copy 独立读取固定 old root，确认它不在授权 root 内，并记录 setup geometry write 合同。
- 推断：app 未能保持可绑定状态与 setup write root 不可用相符；未取得 task-specific crash log，故不把该因果写成直接 log 事实。

## 角色与关卡检查

- Gate 1 产品一致性：未裁决；没有实际页面状态，且本轮不冻结产品。
- Gate 2 数据与来源：部分通过；source lineage 与历史保全可复核，但实际 fresh DB lifecycle 未执行。
- Gate 3 AI 权限与信任：未裁决；静态关闭态不能替代实际 runtime 边界。
- Gate 4 技术可行性：未通过；actual Tauri 无法在 Frozen 目录边界内取得 PID/window。
- Gate 5 用户价值验证：未裁决；本任务不含用户验证。

## 风险与 PM 决策

- 不修改 `RISK_LOG.md`、`FREEZE_STATUS.md`、`CURRENT_STATUS.md` 或任何任务卡。
- 需 PM 确认：按两层验收治理把本轮 `Blocked / Not Pass` 收口为当前任务的正确治理状态；若要继续 actual-Tauri 独立复评，必须新建任务、新授权与新 ABF，明确允许的 fresh runtime/geometry root 或候选的可配置 root。
- 不建议：在 P3-124 追加同 ABF 的 Rework、创建旧 P3-122 temp root、修改 task-local candidate copy 来伪装原 candidate、以 P3-122 旧截图/trace 替代当前实际 App。

## 最终建议

不建议 Pass、冻结、风险关闭、下一任务或 Stage 4。本轮已诚实完成可执行的静态、build、source-lineage、native target discovery 与 cleanup；动态缺口不是可在当前 Frozen 目录中补齐的普通 Evidence 缺口。
