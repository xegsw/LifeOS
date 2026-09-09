# P3-148 工程包

当前交付：来源支撑的对话合成工程候选。只使用本包 `tools/verify_source_conversation.py`；复制自147的旧 runner、打包和安全测试脚本仅作为谱系保留，不是148复跑入口，不得运行。旧27项Rust测试未执行，未绕过此前平台限制。

```sh
LIFEOS_P3_148_BUILD_PROFILE=engineering python3 -B lifeos/engineering/LIFEOS-P3-148/tools/verify_source_conversation.py --phase all
```

`--phase contracts|build|storage|credentials_mock|transport_mock|restart` 可定向复跑。固定离线工具链、唯一148合成根；没有共享CI改动，没有下载、真实OS凭据或Provider访问。每次日志独立命名。GUI不能放无人值守CI；仅使用本包launch返回PID及record_app_evidence绑定窗口，环境失败写checkpoint并定向继续。

`tools/resume.py --check` 验证封存合同、当前candidate摘要、marker与已记录PID均停止。`resume.py`只自动运行合同内合成阶段；遇到GUI/PM边界只报告，不打开真实App或自动发送。

`source-pilot-1` 是供后续安全Gate审阅的编译期接线，本轮没有构建/启动。合成二进制不能通过运行时环境变量改成真实模式。不能把合成App交给用户输入真实Key。真实发布仍需PM安排独立安全评审及用户在App亲验；使用前用户关闭147并在148期间不重开，148锁不证明跨版本互斥。

业务表无新DDL；明确的 `--init-synthetic-fixture` 是仅合成CLI的造数工具，不是App打开库路径。provider两表只在显式保存新凭据后创建。旧来源扫描入口被拒绝；已导入来源仍可读取/检索/查看和断开。

合成UI跨进程凭据使用明确标为不安全的SyntheticKeyPort模拟OS服务；密码学故障独立使用MemoryCredentialPort。它们不是OS Keychain安全证明，更不能用合成文件保护真实Key。真实接线使用148独立service和随机引用，没有旧service回退。

精确清理入口为 `candidate/tools/task_root.py cleanup`，它要求正确marker、所有记录PID停止且无开放WAL。本次保留唯一合成根中的构建与夹具供复跑，已停止App；没有清理真实资料或旧任务根。
