# LIFEOS-P3-120 复跑说明

本包只可在空的 `lifeos/engineering/LIFEOS-P3-120/` 副本与空的 `/private/tmp/lifeos-p3-120-runtime-mvp-v1` 中复跑。不得把本说明用于 Pilot、真实目录、真实 DB、网络或模型。

## 前置条件

- macOS、Rust `1.98.0`、Cargo/Tauri `2.11.4`，且依赖已在本机 cache 中；全程离线。
- P3-120 Frozen ABF 与 14 个输入的 SHA-256 未漂移。
- P3-111 只按 `lifeos/tasks/LIFEOS-P3-120_source_allowlist.md` 逐文件正向复制；不得递归复制其 Evidence、target、tests、tools 或任意 Pilot 资产。
- 允许启动图形 app 时，实际启动测试仅验证进程启动/重开与页面非空，不进行 GUI 注入、AppleScript、AX、CDP、WebDriver 或浏览器自动化。

## 命令

在工作区根目录运行（Cargo 路径按本机工具链调整）：

```bash
python3 lifeos/engineering/LIFEOS-P3-120/tools/verify_preflight.py
python3 lifeos/engineering/LIFEOS-P3-120/tools/verify_static.py
python3 lifeos/engineering/LIFEOS-P3-120/tools/verify_ui_state_contract.py
python3 lifeos/engineering/LIFEOS-P3-120/tools/build_bundle.py
python3 lifeos/engineering/LIFEOS-P3-120/tools/run_runtime_evidence.py
P3_120_TEMP_ROOT=/private/tmp/lifeos-p3-120-runtime-mvp-v1 zsh lifeos/engineering/LIFEOS-P3-120/tests/actual_app_replay.sh
python3 lifeos/engineering/LIFEOS-P3-120/tools/collect_actual_app_evidence.py
python3 lifeos/engineering/LIFEOS-P3-120/tools/collect_negative_results.py
python3 lifeos/engineering/LIFEOS-P3-120/tools/cleanup_temp_root.py
python3 lifeos/engineering/LIFEOS-P3-120/tools/build_matrix.py
```

`actual-app` 进程会在 5 秒启动存活检查后被精确终止。所有结果必须为 `PASS`；任何 `FAIL`、缺失的结果或未删除的唯一临时根都是 `Not Pass`。
