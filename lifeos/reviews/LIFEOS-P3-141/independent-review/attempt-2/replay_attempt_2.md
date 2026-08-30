# Attempt-2 Replay Entry

在本 worktree 根目录执行。所有写入只会落在本 Attempt 根和任务卡指定的临时根；候选目录始终只读。先确保临时根不存在或由本次运行创建。

```bash
python3 -B lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/check_fixed_inputs.py /Users/xxe/Documents/No.2 /Users/xxe/Documents/No.2/lifeos/tasks/LIFEOS-P3-141_fixed_input_inventory.json lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/evidence/fixed_input_replay.json
python3 -B lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/verify_p3_140_lineage.py /Users/xxe/.codex/worktrees/a2e2/No.2/lifeos/engineering/LIFEOS-P3-140/closure-1/evidence/FINAL_MANIFEST.json lifeos/engineering/LIFEOS-P3-141/candidate lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/evidence/p3_140_lineage_replay.json
python3 -B lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/snapshot_candidate.py lifeos/engineering/LIFEOS-P3-141/candidate lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/evidence/candidate_replay.json
python3 -B lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/run_independent_regression.py lifeos/engineering/LIFEOS-P3-141/candidate
python3 -B lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/run_path_boundary_cases.py lifeos/engineering/LIFEOS-P3-141/candidate
python3 -B lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/run_semantic_mutations.py lifeos/engineering/LIFEOS-P3-141/candidate
python3 -B lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/verify_static_contract.py lifeos/engineering/LIFEOS-P3-141/candidate
```

重新取得 actual-Tauri 三档图之前，使用相同合成 build 环境编译候选和 Accessibility helper；每档必须重新直接启动进程并只将该返回 PID 交给 helper。不得复用本 Attempt 的旧 PID、旧窗口或旧截图，也不得运行任何真实模式。

```bash
mkdir -p /private/tmp/lifeos-p3-141-controlled-pilot-v1/runtime
LIFEOS_RUNTIME_ROOT=/private/tmp/lifeos-p3-141-controlled-pilot-v1/runtime LIFEOS_INPUT_MODE=synthetic CARGO_NET_OFFLINE=true CARGO_TARGET_DIR=/private/tmp/lifeos-p3-141-controlled-pilot-v1/app-target /Users/xxe/.cargo/bin/cargo build --manifest-path lifeos/engineering/LIFEOS-P3-141/candidate/Cargo.toml --locked --offline
swiftc -O lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/pid_ax_attest.swift -o /private/tmp/lifeos-p3-141-controlled-pilot-v1/pid_ax_attest
python3 -B lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/tools/run_pid_viewport.py /private/tmp/lifeos-p3-141-controlled-pilot-v1/app-target/debug/lifeos-p3-141 /private/tmp/lifeos-p3-141-controlled-pilot-v1/pid_ax_attest /private/tmp/lifeos-p3-141-controlled-pilot-v1 desktop lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/evidence/screenshots lifeos/reviews/LIFEOS-P3-141/independent-review/attempt-2/evidence/desktop_replay.json
```

最后仅用 `tools/cleanup_temp.py` 对任务卡指定的那个 literal 临时根进行精确清理，并重新生成内容排除与最终 Manifest 验证。Phase C 的 M-008、M-009、M-017 不包含在本入口中。
