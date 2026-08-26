# LIFEOS-P3-120 PM Evidence｜Initial

- PM 复算任务卡、Frozen ABF、source allowlist、交付物、Engineering Manifest 与 matrix hash，均与提交记录一致。
- Engineering Manifest 逐行复算 `101/101` bytes 与 SHA-256 匹配；P3-111 positive source allowlist `72/72` 匹配。
- PM 使用 `/Users/xxe/.cargo/bin/cargo 1.98.0`、`rustc 1.98.0`，在唯一 `/private/tmp/lifeos-p3-120-runtime-mvp-v1` 根执行 `cargo test --locked --offline`：`9 passed / 0 failed`。
- PM 临时根结束后已按精确路径删除，并确认不存在；未覆盖 Engineering Evidence，未访问 Pilot、真实 DB、真实路径、网络或模型。
- `actual_app_replay.sh` 仅启动进程、等待五秒、终止并重开；`collect_actual_app_evidence.py` 只核对进程、启动日志、`runtime_status` 与一张 Today screenshot。
- `ui-state-contract-results.json` 明确是 source-state contract；`run_runtime_evidence.py` 调用 Rust unit test。它们不能证明 Frozen ABF 要求的实际 App 页面导航，以及 renderer→Tauri IPC→DB→UI 的 capture／repeat／second／refresh／reopen 闭环。
- 专项报告只记录“全新 Codex 工程会话”，未记录实际 `gpt-5.6-terra + xhigh`，`fixed-inputs.json` 也没有模型／推理强度字段；PM 无法从保留资产独立确认 Frozen 模型路由，故 `ABF-M-001` 为 Unknown／Not Implemented。
- PM 结论：`Rework 1/2`；`P0=1、P1=1、P2=0、Unknown=1、Not Implemented=7`。
- P3-120 当前视觉与 P3-116 参考存在明显差异，但 `ABF-P3-120-v1` 明确“不冻结视觉”，没有像素或精确布局公式；该差异不追溯计入本轮失败，可由用户决定是否作为后继产品任务候选。
