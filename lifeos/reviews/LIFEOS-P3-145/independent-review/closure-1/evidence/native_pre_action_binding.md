# Native pre-action PID → AX binding

- Actual App PID after closure-owned `open -n`: `62670`.
- Executable: `/private/tmp/lifeos-p3-145-independent-review-closure-1/target/debug/bundle/macos/LifeOS · Work 与健康状态.app/Contents/MacOS/lifeos-p3-145`
- Executable SHA-256: `52ad2bb2a4e4c26717b61d8bf6c03975e53d0e43255aa81945f11476297d5281`
- Pre-launch same-bundle competitor count: `0`.
- Accessibility read before any click, typing, screenshot copy or other UI action returned one exact `standard window LifeOS · Work 与健康状态` and focused `HTML content Description: LifeOS · Work 与健康状态, URL: tauri://localhost`.
- The app path supplied to Computer Use was the exact closure-owned `.app` bundle; no bundle identifier-only lookup was used.
- This binding differs from attempt-1: its PID resolved to a separate worktree; this PID resolves to the current closure-owned offline output under `/private/tmp/lifeos-p3-145-independent-review-closure-1`.
