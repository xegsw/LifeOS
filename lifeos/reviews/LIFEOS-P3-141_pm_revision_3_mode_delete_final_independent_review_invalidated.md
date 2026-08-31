# LIFEOS-P3-141 Revision 3 Mode Delete Closure — PM Independent Review

## 验收信息

- 任务 ID：LIFEOS-P3-141 / CL-MODE-DELETE-01
- 风险等级：L3 / Gate
- Task Contract／ABF：P3-141 Revision 3；`ABF-P3-141-v3` Frozen
- 独立评审提交：`6b25e5536de4624cfa4a867b0c1c619f4463b3a5`
- 独立评审路径：`lifeos/reviews/LIFEOS-P3-141/revision-3-mode-delete-final-independent-review/`
- PM 结论：**Rework；本次独立评审 attempt 程序性失效，不构成 Independent Pass。**

## 结论摘要

- 预接触 seal、固定输入复算、静态核对、52/52 离线测试、六项 mutation、直接 PID→精确标题 AXWindow→AXWebArea 和精确 cleanup 均有留痕，但不能抵消后续 P0。
- 实际 Tauri Settings 画面被记录为仍显示“本次会话 API Key／仅保留本次会话／清除本次会话 API Key”。这与 Frozen 的 encrypted-SQLite 持久化、重启保留、更新／删除和禁止 session/env 产品选项直接冲突。
- 当前候选 `ui/runtime-adapter.js` 已包含正确的 SQLite 持久化文案，但 `ui/interaction_contract.md` 与 `ui/ia_reconciliation.md` 仍保留旧 session 语义；实际 Bundle 又呈现旧画面。该组合证明源码、前端资源、Bundle 与实际 PID 窗口之间的终局谱系尚不可信，不能以静态源码正确代替实际产品正确。
- 评审截图 helper 在无法取得 `AXWindowNumber` 后回退到整屏 capture，包含任务外桌面信息。PNG 已精确删除，但触达不可撤销，本 attempt 必须失效；不得复用其正向结论。
- 唯一评审临时根已按 marker 精确清理并证明 absent；未访问 Pilot-6、真实 DB／文本、真实 Provider／凭据或网络。

## 五类计数

- P0：2（实际 Bundle／冻结凭据语义冲突线索；评审整屏截图越界并使 attempt 失效）
- P1：0
- P2：2（评审自身 task-local TMPDIR 与 cleanup 参数失败历史；均未进入正 Evidence）
- Unknown：0
- Not Implemented：0

## PM Closure List（同一任务，一次性全部列明）

1. `CL-BUNDLE-LINEAGE-01`：清除候选中所有 session／environment credential 产品语义，包括产品交互合同；从 source `runtime-adapter.js` 到 Bundle resource 再到直接 PID 实际 Settings DOM／画面建立 byte-exact 可复算谱系，禁止 stale cache、错误候选目录或历史资源进入 Bundle。
2. `CL-BUNDLE-LINEAGE-02`：实际 Settings 只能显示本地加密 SQLite 持久化、重启保留、更新和删除语义；不得出现“本次会话 API Key”、环境变量凭据或相应清除动作。
3. `CL-NATIVE-CAPTURE-01`：工程和后续独立评审只允许目标窗口范围的 native capture；无法获得目标窗口 capture authority 时必须 fail closed，禁止回退整屏／桌面 capture。
4. `CL-EVIDENCE-01`：工程侧重做合成离线 lifecycle、六项 mutation、source/resource/binary/PID/AX/Settings 三档 Evidence、错误 marker 拒绝、正确 marker 精确 cleanup 与非自指 Manifest；历史 attempt 全部只读保全。
5. 工程 Gate Pass 后必须由另一全新隔离会话、新 precontact seal、新 review root 完整复评；不得复用本 attempt 的 PID、DB、截图、root、测试结果或结论。

## 状态与边界

- 当前状态：P3-141 Revision 3 Same-task Closure Cycle / Independent Review Invalidated / Phase C Paused。
- 用户原完整合同继续覆盖本次包内修正、测试、Evidence、复跑和 PM 验收；无需重复授权或新任务。
- R-0056 保持 Open；ABF-P3-141-v3 保持 Frozen；产品未冻结。
- 不恢复 Phase C，不进入 Pilot-6，不启用真实 Provider／凭据，不关闭风险，不进入 Stage 4。

