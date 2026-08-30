# attempt-6 复跑入口

仅允许在全新的任务临时根内运行；绝不自动运行真实 Pilot、真实 Provider 或网络发送。

```bash
TEMP_ROOT=/private/tmp/lifeos-p3-141-controlled-pilot-v1
LIFEOS_RUNTIME_ROOT="$TEMP_ROOT/runtime-synthetic" LIFEOS_INPUT_MODE=synthetic \
  CARGO_NET_OFFLINE=true CARGO_TARGET_DIR="$TEMP_ROOT/cargo-target" \
  cargo test --manifest-path "$TEMP_ROOT/candidate/Cargo.toml" --bin lifeos-p3-141 --locked --offline -- --test-threads=1
```

独立 review-owned tests（受控 fixture，非真实数据）：

```bash
LIFEOS_RUNTIME_ROOT="$TEMP_ROOT/runtime-real-replay" LIFEOS_INPUT_MODE=real_self_use \
  LIFEOS_P3_141_PHASE_B_RECEIPT=LIFEOS-P3-141-PHASE-B-INDEPENDENT-PASS \
  LIFEOS_P3_141_SYNTHETIC_FIXTURE_EVIDENCE=1 CARGO_NET_OFFLINE=true \
  CARGO_TARGET_DIR="$TEMP_ROOT/cargo-target" \
  cargo test --manifest-path "$TEMP_ROOT/candidate/Cargo.toml" --bin lifeos-p3-141 independent_runtime_tests --locked --offline -- --test-threads=1
```

actual-Tauri 仅可由新隔离评审按任务合同 direct-launch 重新取得 PID→exact-title AXWindow→AXWebView/WebArea 链；本 attempt 的 P0 不能通过重放旧 PID、窗口或截图关闭。
