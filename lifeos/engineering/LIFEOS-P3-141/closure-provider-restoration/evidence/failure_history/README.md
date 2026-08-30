# 保留的失败历史

这些文件均不用于正 Evidence，且没有被覆盖或删除。

- `desktop_pre_activation_wrong_foreground.png`：按 AX frame 的首次抓图时前台仍为 Codex，不是本次直接 PID；因此无效。
- `desktop_focus_helper_invocation_failed.png`：PID 已退出后尝试前台激活，不能证明本次 app；因此无效。
- `desktop_focus_after_exited_pid.png`：同一已退出 PID 的后续抓图，无效。
- `desktop_settings_helper_build_failed.png`：首次点击辅助程序因 AppKit 常量编译错误而未执行，抓图无效。
- `cargo_test_wrapper_status_variable_error.log`：测试结果包装使用 zsh 保留变量 `status` 失败；随后以新变量名从头运行并得到 50/50 通过。
- `cleanup_direct_exec_permission_denied.md`：无执行位的直接脚本调用在任何删除前被拒绝。
- `cleanup_marker_newline_rejected.md`：首次 marker 换行处理在删除前拒绝。
- `cleanup_escaped_normalizer_rejected.md`：转义错误的 marker 规范化在删除前拒绝。
- `cleanup_marker_token_rejected.md`：字节核对后发现完整 marker token 与脚本早期假定不同；在删除前拒绝。

有效三档截图仅为 `evidence/screenshots/desktop.png`、`compact.png`、`narrow.png`；它们均在本次 PID→AX 验证和直接 PID 前台激活后取得。
