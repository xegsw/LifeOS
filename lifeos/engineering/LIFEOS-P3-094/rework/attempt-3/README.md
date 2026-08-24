# LIFEOS-P3-094 rework attempt-3

本目录只新增 attempt-3 的保全型 Chrome 动态 Evidence；attempt-1／attempt-2、工程实现、既有交付物、Review 与 Manifest 均保持只读。

唯一 runner：`scripts/run_attempt_3.py`。它只使用固定非敏感测试文本，按 `prepare → record × 4 → finalize` 运行；存在 attempt-3 输出时拒绝覆盖。`prepare` 生成 task-local SQLite／HTML 与离线结构化结果；Chrome 截图由 Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky` 产生；`finalize` 仅在四项浏览器动作齐备后清理运行期 DB／HTML，并生成闭环表、验收矩阵和完整非自指 Manifest。

复跑入口（必须在新的 attempt 目录或清空的独立副本使用，不能对本已提交 attempt-3 再执行 `prepare`）：

```bash
python3 -B scripts/run_attempt_3.py prepare
python3 -B scripts/run_attempt_3.py record --id D-01-chrome-preflight --screenshot <attempt-evidence-screenshot> --observed <observation> --entry-url-kind file
# 依次记录 D-02-success-today、D-03-empty-fail-closed、D-04-close-tab
python3 -B scripts/run_attempt_3.py finalize
```

最终结论：**PASS**。离线前置退出码 0；Chrome 动态闭环 5 PASS / 0 FAIL；P0/P1/P2/Unknown/Not Implemented 均为 0。该结论与 `evidence/dynamic_results.json`、`evidence/dynamic_closure.md` 和 `evidence/MANIFEST.md` 一致，仅表示 attempt-3 可提交 PM 验收，不代表独立复评、风险关闭、冻结、基线恢复或 Stage 4 准入。
