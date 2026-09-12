# P3-152 合成阶段交付

唯一允许动态根：/private/tmp/lifeos-p3-152-health-conversation-v1。真实模式硬关闭，所有健康输入和凭据均为虚构测试数据；无需也不得输入真实 API Key。

- 包核验：`python3 tools/verify_package.py`、`python3 tools/verify_inputs.py`。
- 离线自动复跑：`bash tools/rerun.sh`。先校验根 marker、历史输入及包，再运行 Host、driver集成和App构建；日志写入本任务临时根新 rerun 目录，不改历史 Evidence。
- 必要mutation复跑：`python3 tools/mutations.py`。只复制本任务候选到新临时子目录，移除三条守卫并运行指定反例；输出JSON，非零编译失败不能当作检出。完成后正常rerun恢复target内最终候选二进制。运行中的App使用独立bundle不受影响。
- GUI：已有证据按exact launch PID采集；不要自动操作真实App。launch.py 初次创建或 `--restart` 必须先精确停止本任务synthetic实例；`--restart --update`可在停止后装入新构建。capture_synthetic.py只接受receipt对应的合成PID/二进制/标题。禁止对其他运行根执行这些脚本。
- build_ui.mjs是TS产物构建工具。setup_modules.py/extend_ui.py仅保留初始工程改造过程，不是复跑入口，不应重复执行。
- 目录中保留的未编译历史模块是技术输入，活动模块以main.rs/driver声明为准，不表示这些功能已启用。

未执行清理。合成根、测试/变异隔离副本和最终App保留；旧151及更早根未修改。本任务无push/merge、账本、冻结、风险关闭或后继任务动作。
