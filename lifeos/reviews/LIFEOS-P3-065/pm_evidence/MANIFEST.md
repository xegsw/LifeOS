# LIFEOS-P3-065 PM Evidence Manifest

## PM 隔离复跑与 P1 反例

- 复跑方式：将 `lifeos/engineering/LIFEOS-P3-065/` 复制到 `/private/tmp/lifeos-p3065-pm-review.A1ku87/LIFEOS-P3-065/` 后运行；未覆盖执行侧或历史 Evidence。
- 执行侧回归：`scripts/run_tests.sh` 退出码 0，14 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0。交付物“13 项回归”表述与结构化结果不一致，属 P2 文档不一致，不影响下述 P1。
- PM 新增反例：同一受控 Project／category／purpose／location／processor 先以不同幂等键创建 `grant`，再创建 `deny`，两者均未过期；随后 `consume()` 返回 `{'allowed': True, 'reason': 'allowed_local_synthetic', ...}`。
- 根因：`PermissionSettings.consume()` 仅以有效 `granted` 数量决定 allow，不让同一精确绑定上的 `denied` 条目取得阻断优先级。
- 结论：违反任务卡“明确 deny 阻断”和默认拒绝的 fail-closed 要求，判为 P1。P3-065 不得进入独立复评、真实能力、风险关闭、冻结、基线恢复或 Stage 4。

## Rework PM 隔离复跑（D-0281）

- 复跑方式：将更新后的工程目录复制到 `/private/tmp/lifeos-p3065-rework-review.sBXWEM/LIFEOS-P3-065/`；未覆盖当前、初版或历史 Evidence。
- 当前回归：`scripts/run_tests.sh` 退出码 0，23 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0。
- PM 独立反例：同一精确绑定先 grant、再 deny 后，`consume()` 返回 `allowed=false`、`reason=explicit_deny_current`、`ai_consumption=none` 与 `external_action=none`；原 P1 不再复现。
- hash：`permissions.py` `29e33624b7988e3b18b9ec6451d1e76c97f43ae2189f65636e51d66460dca57a`、`permission_cli.py` `342ef7bc918cb062090ad8d03866d4798822d83440818cfce14fd04f8ecb47d1`、`test_permissions.py` `fb25ba02488d3ba6f686a89f7352341c853b90db4ae5a4c01baa94d73ab0619c`、冲突快照 `daa6347de0c0b933ce79a7fbf0fe76558b9b474298e8d8d7d04f5d58d49b6ed2` 和结果 `33dead70755c262e3529abb9c2cf207515cb092bafd51b3e784e0bcdd234b7cf` 均与执行侧 Manifest 一致。
- 结论：D-0279 P1 已解决；P3-065 可作为全新隔离独立安全／体验复评输入，仍严格限于合成 SQLite 受控边界。
