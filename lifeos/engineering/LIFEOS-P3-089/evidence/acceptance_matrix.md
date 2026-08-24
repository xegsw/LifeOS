# LIFEOS-P3-089 验收标准 → 测试 → Evidence

| 任务卡验收标准 | 测试用例 | Evidence | 结果 |
|---|---|---|---|
| 三页、相对本地资源、明确合成标签 | 静态 D-01 至 D-07 | `static_results.json` | PASS |
| 原文／用户确认／合成状态／AI 未启用区分 | 静态与 Chrome D-02 | `static_results.json`、`01-preflight-wide.png` | PASS |
| 空输入拒绝、确认、重复幂等 | Chrome D-03 至 D-05 | `dynamic_results.json`、`02-confirmed-recovery.png` | PASS |
| 默认拒绝、grant、撤回 fail-closed | Chrome D-06、D-07、D-09 | `dynamic_results.json`、`03-failure-cleared.png` | PASS |
| 预览→CONFIRM→重复回执 | Chrome D-07、D-08 | `dynamic_results.json`、`02-confirmed-recovery.png` | PASS |
| 失败清理与披露 | Chrome D-10 | `dynamic_results.json`、`03-failure-cleared.png` | PASS |
| 刷新及关闭重开清除 | Chrome D-13、D-14 | `dynamic_results.json`、`06-refresh-cleared.png`、`07-close-reopen-cleared.png` | PASS |
| 三态导航、键盘、焦点、缩放、reduced motion | 静态 CSS、Chrome D-11、D-12、D-15 | `static_results.json`、`04-no-suggestion.png`、`05-restricted-offline.png`、`08-keyboard-focus.png`、`09-narrow-responsive.png` | PASS |
| 禁止能力静态关闭 | 静态 closed:* | `static_results.json` | PASS |
| 历史只读资产未被覆盖 | SHA-256 核对 | `historical_input_hashes.txt` | PASS |
