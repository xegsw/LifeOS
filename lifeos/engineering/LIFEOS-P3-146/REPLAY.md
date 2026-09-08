# P3-146 合成离线复跑

只允许本包和唯一 `/private/tmp/lifeos-p3-146-conversation-source-v1`，不接入真实数据、网络、凭据或历史 runner。当前交付已清理临时运行根，不保留正在运行的 App。以下从本候选目录执行：

```bash
cd /Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/engineering/LIFEOS-P3-146/candidate
PYTHONDONTWRITEBYTECODE=1 python3 tools/task_root.py init
/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node tools/run_p3_146_checks.mjs
```

runner 依次：TypeScript 转译、Rust fmt、locked/offline build、仅 `tests/integration.mjs` 的30项测试。Node内置转译器不做 TypeScript 类型检查，本轮不宣称 tsc 通过。依赖使用现有本机缓存，不联网安装。CARGO_TARGET_DIR/TMPDIR由runner显式绑定任务根；不得手工省略这两个值运行Cargo。每轮时间戳日志先存任务根，检查摘要存evidence；封包后复跑会产生新证据，不能覆盖本轮最终Manifest。

实际 App 为有人值守阶段，不进无人值守CI。仅在桌面可用时：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 tools/launch_app.py replay1 desktop
```

参数只接受desktop/narrow（请求1280×1024或700×760），标签须使用未占用的新值。启动工具打印直接PID和二进制hash。不得同时复用应用包启动第二个实例；先用App退出并核对已知PID结束。UI路径：Global AI保存 → Today回答/暂缓/忽略/拒绝 → 当前记录纠正 → Memory明确记住偏好 → Contexts两种合成版本/撤权 → Settings OfflineA/B。中文通过系统粘贴输入，避免自动按键无法输入中文。

原生证据工具只读取指定PID；窗口/WebArea服务暂不可用时记录checkpoint并恢复，不替换成其他PID或旧截图：

```bash
/usr/bin/swiftc tools/native_evidence.swift -module-cache-path /private/tmp/lifeos-p3-146-conversation-source-v1/swift-cache -o /private/tmp/lifeos-p3-146-conversation-source-v1/native_evidence
PYTHONDONTWRITEBYTECODE=1 python3 tools/record_app_evidence.py replay1 <launch返回的PID>
```

完成后退出自己的App，保全本轮日志，再执行 `PYTHONDONTWRITEBYTECODE=1 python3 tools/task_root.py cleanup`。该工具校验字面根、普通marker、权限/属主、所有记录的App PID均已结束和无WAL；校验失败不删除、不补造marker、不自动杀进程。只会清理该一个根。

CI注册建议：PM核对独立变更后注册此runner为macOS合成确定性job，禁止将GUI、Provider、旧145 tests、Vault或健康采集加入job。本轮未改全局CI，不自动提交/推送/合并。`tools/verify_manifest.py`只读验证当前交付，不访问临时根或原候选。
