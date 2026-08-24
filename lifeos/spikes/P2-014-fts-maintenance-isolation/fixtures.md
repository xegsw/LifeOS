# 合成夹具

- 每个内容单元包含合成 `source_id`、`artifact_version`、原文占位文本、active、allowed、restriction generation 与 tombstone generation。
- 每个内容单元确定性生成 3 个 FTS 分块。
- 10 万档对应 30 万分块；100 万档对应 300 万分块。
- 权限、tombstone、restriction generation 各选择独立合成 ID，在 posting 建成后改变权威状态，以验证陈旧 posting 回连当前状态后零泄漏。
- 捕获样本使用独立合成 ID 空间，不包含个人内容或真实来源。
