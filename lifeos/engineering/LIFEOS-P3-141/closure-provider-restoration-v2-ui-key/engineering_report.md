# LIFEOS-P3-141 Provider Restoration v2 UI Key Closure

## 结论

同一 Task Contract 内窄修正。修复实际 Tauri 独立复评发现的 UI→Runtime 合成 Capture 键不一致：UI 不再发送历史 `p3-130-capture-001`，改为与 P3-141 Runtime 固定合同一致的 `p3-141-synthetic-capture-001`。

## 范围

- 基线：`closure-provider-restoration-v2-gate/candidate/`。
- 唯一产品代码变化：`candidate/ui/runtime-adapter.js` 的 `SYN_KEY` 常量。
- 五类 Provider、Custom OpenAI-compatible、20 IPC、v2 Phase-C build gate、视觉与其他 Runtime 语义均未改变。
- 未访问 Pilot-6、真实 DB、真实文本、真实 Provider、凭据或网络。

## 验证

- `test_ui_runtime_key_contract.js`：UI 与 Runtime key 必须相等，且 UI 中不得残留旧 P3-130 key。
- Key contract：1/1 Pass。
- Cargo：54/54 Pass（50 个 Runtime/unit + 4 个 v2 Phase-C gate）。
- actual-Tauri 动态结论仍必须由后续全新隔离独立评审给出，本工程报告不以静态测试替代。

## 严重级别

- P0: 0
- P1: 0
- P2: 0
- Unknown: 0
- Not Implemented: 0（本窄修正范围）

本报告仅为工程候选结论，不构成 PM Accepted、真实 Provider 启用、R-0056 关闭、冻结或 Stage 4。
