# LifeOS Local Prechecks

本目录用于保存由局域网本地模型生成的 `Local Precheck / 本地预检` 报告。

本地预检只用于辅助 PM 或专项会话降低阅读成本，不是 PM Review，不是 Independent Review，不代表任务验收通过、资产冻结或 MVP 开发准入。

默认生成方式：

```bash
python3 lifeos/tools/local_precheck.py <交付物或评审文件路径>
```

默认本地模型：

- Ollama 地址：`http://192.168.5.17:11434`
- 模型：`qwen3:14b`

如果本地模型不可用，应跳过本地预检，按原项目流程继续，不得阻塞任务。
