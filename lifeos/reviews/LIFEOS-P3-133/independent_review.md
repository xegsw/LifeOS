# LIFEOS-P3-133 强制 L3 合成独立评审

## 评审信息

- 对应任务 ID：`LIFEOS-P3-133`
- 是否为受控能力包：Yes
- 能力包边界／被评审最终 hash：P3-133 候选 75/75 文件与 closure-1 参考 inventory 一致；独立 Evidence Final Manifest SHA-256：`7f705540032ae18c2c4118014dc679ee875553ec39c0abf5c98c6d37b08305e4`。
- 对应交付物路径：`lifeos/engineering/LIFEOS-P3-133/candidate/`、`lifeos/engineering/LIFEOS-P3-133/evidence/closure-1/FINAL_MANIFEST.json`（均只读）。
- 独立评审角色：技术可行性／受控 Runtime 独立评审。
- 协审视角：数据与来源、AI 权限与信任、真实用户入口与 Evidence 完整性。
- 评审关卡：P3-133 强制 L3 独立评审；真实能力启用前置关卡。
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-133/independent_evidence/`。
- 评审结论：**Rework / Closure Cycle Required（非独立 Pass，非 Blocked）**。
- 风险等级：L3。
- 独立评审触发事实：首次从 P3-132 合成候选扩展到受控真实个人短文本、专用真实目录与 DB；任务卡指定强制独立评审。

## 独立性与回流规则

- 执行侧与评审侧是否隔离：Yes。评审先写入自己的 `test_design.md`，再只读读取候选／工程 Evidence；动态编译、bundle 与 DB 都从候选的临时副本和全新合成 DB 产生。
- 是否只评审能力包的最终 Evidence／hash：Yes。冻结 Task Contract、ABF、用户确认、P3-132 固定输入以及 closure-1 candidate inventory 均逐项 hash 通过，结果见 `source-lineage.json`。
- 独立 runner 源码、逐项结构化结果、Manifest 与可复跑入口是否已保留且可查：Yes。保留 `independent_runner.py`、`independent-matrix.json`、`verification.json`、`FINAL_MANIFEST.json` 和只读 `independent_readonly_replay.py`。
- 是否可验证 runner 未导入、调用或复制执行侧测试：Yes。独立 runner 不导入或执行任何工程 verifier；仅运行任务卡允许的 `verify_closure_readonly.py` 默认只读模式，并以工程目录前后全量 hash 一致证明零写入。该 closure 输出只是 lineage corroboration，不是本评审的正 Evidence。
- 是否发现需回包内整改的 P0/P1、明确 P2 bypass、Unknown／Not Implemented、Evidence 冲突或独立性不足：发现 P0=1、P1=0、P2=1（D-0540 历史事故保全）、Unknown=0、Not Implemented=7。没有独立性不足；D-0540 的原 `verification.json` 与 `FINAL_MANIFEST.json` 继续隔离，未作为正 Evidence。
- 若需整改：不得创建微型整改任务；回到同一 P3-133 能力包 Closure Cycle，完成后必须用新的隔离临时根再次独立复评。
- 更新时间：2026-08-27。

## 本地 `file:` 动态 Evidence 预检（仅适用时）

- 指定浏览器与 bundle id：N/A。本任务是 native actual Tauri bundle，不使用 `file:` 或 Chrome。
- task-local `file:` 入口／副本 hash：N/A。
- 新 Chrome 标签页首次／第二次预检：N/A。
- In-app Browser 结果：N/A。
- 动态矩阵是否只在 Chrome 预检通过后开始：N/A。
- 若候选 Blocked：N/A；本结论为 Rework，不是环境 Blocked。
- 若本任务来自 Closure Cycle：Yes。D-0540 事故相关原 Review／Evidence 只读保留；本轮仅写入 `lifeos/reviews/LIFEOS-P3-133/`。

## 评审摘要

1. 启动前 Frozen Task Contract、ABF、Freeze Manifest 固定输入和写入边界均匹配；没有在此阶段访问候选、临时根或 actual Tauri 前发现冲突。
2. 候选静态面满足严格十一项 IPC、空 renderer capability、`connect-src ipc:`、无网络／shell／通用 path/SQL 入口，以及真实模式 model adapter 禁用；这不足以替代动态通过。
3. 独立合成 actual Tauri 已完成 Capture → 显式 Context 确认 → 显式 Action 接受 → Today Focus → 关闭重开；该路径仅证明合成模式。
4. 真实模式 actual Tauri 在输入一条固定、非敏感合成短文本后，始终显示 `real_input_rejected` 且保持 0/3；未创建合成 DB。根因是 UI 先 busy-render 清空 textarea，后读取输入。
5. 因此受控真实模式的唯一用户 Capture 入口不可用，`ABF-M-005` 为 P0 Fail；后续真实模式的限额、Context、Candidate、Action、Today 与隐私 UI 链均不能在 actual Tauri 层成立。
6. 独立 Rust probe 仍确认了链接／非空根、非 SQLite 已有 DB、3 条／200 字符、第四条拒绝、真实模型禁用和 taint 不进入 audit／Understanding 的后端 fail-closed 行为；这不抵消 UI P0。
7. AC-12 真实自用没有执行；没有访问、检测、创建、hash 或清理真实自用根。专用评审临时根已按精确路径清理并验证不存在。

## 已通过内容

- Frozen 输入和 P3-132／P3-133 candidate lineage 均完整，候选文件数为 75，固定哈希均匹配。
- 严格 IPC 与受限 surface 的独立静态检查通过，且真实模式披露模型已禁用。
- 缺失、相对和链接 Runtime 根在 build 输出前 fail closed；非空根、已有非 SQLite DB、201 字符和第四条写入在 review-only 实验中均在保护状态改变前拒绝。
- 合成 actual Tauri 的显式确认、Action 接受、Today Focus 与关闭重开可复现。
- 固定合成 taint 未被保留在本评审 Evidence，且独立 byte scan 无命中。
- 工程 closure 默认只读 verifier 复跑退出 0，运行前后工程文件全量 digest 均为 `6959428cc30737efb5ae849cff05a2f6dd1f5665da605ef5c6a4b6b276d33db7`；这只证明本次评审零写入工程资产。

## 关键问题

### P0-IR-01：真实模式 Capture UI 在读取输入前清空 textarea

事实：`candidate/ui/app.js` 的 `act()` 在第 92 行先设置 busy 并 `render()`，第 96 行才读取 `#real-capture-text`。重渲染替换了 textarea，所以实际 Tauri 收到空字符串；两次键入和一次 set-value 提交都返回 `real_input_rejected`，计数保持 `0/3`。截图 `actual-real-capture-rejected.jpeg`、结构化 `actual-tauri.json` 和独立 bundle identity 均已保留，未保留任何输入内容。

影响：本任务唯一用户结果的真实模式 Capture 入口不可达。不是安全拒绝本身的缺陷；安全拒绝是正确的，但 UI 接线使合法受控输入永远无法抵达该边界。

## Closure List

1. **CL-IR-01（P0，候选修正）**：在同一 P3-133 能力包中修正 `capture-real` 的操作顺序，必须在 busy render 前安全读取 textarea 值；新增真实模式 UI 回归，证明非空固定合成文本实际传入 `capture_record`、保存后计数从 0/3 变为 1/3。不得改变十一项 IPC、真实模型禁用、路径／DB 边界或隐私规则。
2. **CL-IR-02（P0 收敛 Evidence）**：修正后在全新合成 DB、全新精确临时根的 actual Tauri 中独立覆盖 `ABF-M-005` 至 `ABF-M-011`，特别是 3 条／200 字符、第四条拒绝、显式 Context／Action、Today Focus、关闭重开和零 taint。不得运行 AC-12，不得访问任何真实根。
3. **CL-IR-03（强制复评）**：工程 Closure 完成后，新建隔离独立评审临时根与新合成 DB，复算 Frozen 输入并重做 affected rows；不得沿用本轮 P0 后的 actual Tauri Pass 作为补证。

合同和边界不需要改变，因此这三项必须回到同一 P3-133 Closure Cycle，不创建微型任务。

## 条件通过项

不适用。本评审不是 Pass with Conditions；P0 存在时不能以条件通过替代实际 Closure。

## 关卡检查

- Gate 1 产品一致性评审：**Not Pass**。唯一真实模式用户结果无法从 Capture 开始。
- Gate 2 数据与来源评审：合成路径／后端边界 **Pass（有限）**；真实模式 actual UI 未建立，故不能形成整体通过。
- Gate 3 AI 权限与信任评审：真实模式 model adapter 禁用与 taint 后端检查 **Pass（有限）**；不对整体任务签发通过。
- Gate 4 技术可行性评审：**Not Pass**。actual Tauri UI 存在 P0 接线缺陷。
- Gate 5 用户价值验证评审：**Not Executed**。AC-12 真实自用仍被独立评审非 Pass 前置条件阻止。

## 风险

- `R-0053` 仍为 Open；本评审不关闭、重开或更新风险账本。
- P0-IR-01 是需由 PM 纳入同一 P3-133 Closure Cycle 的工程／Evidence 问题；在 Closure 和新独立 Pass 前，真实运行必须继续禁止。
- P2=1：D-0540 工程 Evidence 覆盖事故作为历史事实保全。closure-1 已将原 summaries 隔离，本评审亦未将其当作正 Evidence；该 P2 不是本轮 P0 的抵消项。
- Unknown=0：受限范围内的行为都已有独立观察；未把未执行的 AC-12 误标为 Unknown。
- Not Implemented=7：`ABF-M-006` 至 `ABF-M-011` 的真实模式 actual-UI 链因 P0 前置 Capture 失败未能执行，以及 `ABF-M-013`／AC-12 按合同保持未执行。

## 需要 PM 决策

1. 接收本结论为 **Rework / Closure Cycle Required**，将 P0-IR-01 至 CL-IR-03 回派至同一 P3-133 能力包。
2. 在新的工程 Closure 和新的独立 Pass 前，继续禁止真实自用运行；不需要为同合同修正重复取得用户授权。
3. 不冻结产品／Runtime／IPC／Schema/API，不关闭 R-0053，不进入 Stage 4。上述事项不在本独立评审权限内。

## 最终建议

不建议 PM Pass、风险关闭、Freeze、真实自用或 Stage 推进。建议在同一 P3-133 Closure Cycle 修正 UI 输入读取时序，重新产出受控合成 actual-Tauri Evidence，再进行新的隔离独立评审。独立 Evidence Final Manifest 与只读复跑入口位于 `lifeos/reviews/LIFEOS-P3-133/independent_evidence/`；其 `verification_pass=false` 是预期且正确的 P0 记录，不是 verifier 故障。
