# 清理首次调用失败

`tools/cleanup_temp.sh` 在没有可执行位时被直接调用，shell 在脚本开始前返回 `permission denied`（exit 126）。因此没有 marker 读取、PID 检查或删除动作发生；随后使用 `zsh tools/cleanup_temp.sh` 执行同一受保护脚本。
