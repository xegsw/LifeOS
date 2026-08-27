# P3-133 Closure-2 独立复评（re-review-1）

## 任务信息

- 任务：`LIFEOS-P3-133_controlled_real_input_work_self_use_runtime_loop`
- 评审轮次：Closure-2 的 mandatory independent re-review（全新隔离）
- 本轮结论：**Pass（仅指本轮独立复评范围）**
- 评审边界：固定的候选、Frozen 输入和 Closure-2 工程 Evidence 均只读；未修改工程、任务卡、历史 Review、账本、风险或冻结资产。
- 临时执行根：仅使用任务授权的全新合成根；已在结束时精确删除。未访问真实自用目录、真实文本、真实 DB 或真实路径。

## 独立性与前置设计

1. 在读取候选源码、工程 runner 或执行 Evidence 前，已自行写入并封存 `test_design.md`；其 SHA-256 为 `b0cd4c0ff9f65e2db0c9ed1d4ed4e9de4779d474c95a25641556f177b4fb038a`，封存见 `test_design_seal.json`。
2. 本轮没有导入、调用、复制或以工程测试/Manifest 作为正向通过证据；动态验证使用本轮自写的 `runtime_probe.py`、`privacy_scan.py` 和独立运行步骤。
3. 候选、Closure-2 Evidence 与 P3-132 历史候选在动态运行前后均由本轮 `independent_verify.py` 重新哈希。两次结果均为：候选 `75/75`、Closure stable Evidence `20/20`、P3-132 历史候选 `75/75`，无缺失、额外项或 hash 不匹配。

## 复评摘要

1. Frozen 任务、ABF、Freeze Manifest、P3-132 架构基线、候选和 Closure-2 Manifest 的固定输入/行数/hash 关系均由独立验证器复算通过。
2. 在新建的合成 DB 上构建并运行 actual Tauri bundle；Capture 的 real 输入在 busy/render 前读取。三条上限内输入可保存，记录数为 3，模型保持禁用、Understanding 为 0、未产生 `noticed`。
3. 明确确认 Context 不会自动创建 Action；只有显式接受 candidate 后才产生一个 Action 与 Today Focus。刷新和关闭重开后，合成 DB 中的 Capture、candidate、Action、Focus 关系保持一致。
4. 超长输入在 UI `maxlength=200` 控件层被阻止在提交前，且新合成 runtime 未创建 DB；已有三条后 Capture 入口不再提供，重开后仍为三条。因 UI 未派发被拒绝 IPC，本轮不把它误报为观察到后端 `real_input_rejected` 代码。
5. 相对/符号链接/普通文件 runtime 根均失败关闭；非空根保留哨兵且不创建 DB；既有非 SQLite 合成 DB 保持原文件、actual UI 显示 `database_unavailable`。没有执行未授权 IPC、网络、模型、Vault、导出或 clear。

## 覆盖与 Evidence

| 覆盖项 | 结论 | 本轮 Evidence |
| --- | --- | --- |
| Frozen、候选、历史、Closure-2 hash 复算 | Pass | `static-verification.json`、`static-verification-after-dynamic.json` |
| Capture 在 busy/render 前取值 | Pass | `actual-tauri-observations.json`、独立静态验证 |
| 三条上限内写入与重开一致性 | Pass | `runtime-positive-after-restart.json` |
| 201 字符、第四条的写前关闭 | Pass（UI 层） | `runtime-201-before.json`、`runtime-201check-after-201-entry.json`、`runtime-201check-after-explicit-launch.json` |
| Context / candidate / Action / Today 关系 | Pass | `runtime-positive-after-restart.json`、`actual-tauri-observations.json` |
| real mode 模型禁用、Understanding/notice 为零 | Pass | `runtime-positive-after-restart.json`、`actual-tauri-observations.json` |
| 路径、哨兵、既有 DB、链接链与写入边界 | Pass | `path-db-mutations.json`、`runtime-existingdb-after.json` |
| 输入正文/派生标识不进入 Review Evidence | Pass | `privacy-scan.json` |
| 精确清理唯一临时根 | Pass | `cleanup.json` |

完整逐行结果见 `independent-matrix.json`；本轮全部产物及 hash 索引见 `FINAL_MANIFEST.json`。

## 问题计数与裁决

- P0：0
- P1：0
- P2：1（历史 D-0540，仅记录为不阻塞的范围外遗留）
- Unknown：0
- Not Implemented：1（M013：真实自用闭环；按任务合同仍只能由用户在 PM 核对后手动执行）

本轮没有发现 Closure-2 候选在授权合成/actual-Tauri 复评范围内的 P0/P1 或需工程返工缺口，因此裁决为 **Pass**。这不是 P3-133 全任务 Final Pass，不能替代 PM 验收、用户真实自用、任何冻结、R-0053 关闭或 Stage 4 判定。

## 角色与关卡

- 独立评审：本轮隔离、只读、合成 actual-Tauri 复验已完成；结论为 Pass（有限范围）。
- PM：仍须复核本轮结论和 Evidence 后决定是否接受独立复评；本评审不更新 PM 账本。
- 风险/阶段：R-0053 保持 Open；真实自用 Gate 未执行；不得据此进入 Stage 4 或声称风险关闭。

## 需要 PM / 用户处理

1. PM 核对 `FINAL_MANIFEST.json`、逐行矩阵及本 Review 后，决定是否接受本轮独立复评。
2. 若 PM 接受，后续真实自用仍须严格按原任务合同由用户自行手动执行；本会话不参与、不访问且不记录真实输入。

