# P3-147 内部合成工程复跑

当前不是终局工程Pass。新增公共API尚待用户批准；未接线原生来源UI。所有以下动作只使用唯一合成根，不触及真实来源、Provider、Keychain或网络。

```sh
python3 -B /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/candidate/tools/run_internal_checks.py
```

runner校验/初始化固定marker，只写新的时间戳日志目录，显式离线locked Cargo及task-local target/TMP，执行11项Rust、10项parser、14项Web替身、30项继承测试。依赖采用本机已存在的Cargo和Codex bundled Python/Node，不安装依赖。当前精确路径为本机复跑入口；CI注册及跨runner依赖定位仍由PM集成，不能称已经在GitHub CI执行。

当前持久状态：合成根有marker及合成测试DB/原件/缓存，保留续跑；未启动App，没有后台worker或真实socket。所有parser子进程被测试等待退出。禁止用本包继承的146旧验证器宣称147全量通过。

恢复：核对evidence/checkpoint.json、当前合同和候选digest；公共API获准后从source_lifecycle接线阶段继续。不要重建已通过且无变化的内部模块。原件恢复使用内部recover，仅对相应DB/connector命名空间隔离未引用原件，不覆盖、不清理真实资产。

限制：RSS watchdog和完成后peak检查不等于操作系统硬地址空间隔离；本机RLIMIT_AS设置失败，资源安全能力仍须补强验证。WebSourceAdapter没有真实Transport实现。目录符号链接、平台别名、外部文件授权后的目标读取及外链结果同库持久化/撤权还未完整闭环；普通文件、内部文件符号链接、根内直接引用已实现内部测试。
