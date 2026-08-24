# Restore limitations

- 先合并当前 tombstone、restriction generation 和 Authorization version，再接纳内容。
- 来源指针可恢复，但不会自动恢复读取、云处理或第三方授权。
- 用户原文不可覆盖；同 ID 异内容形成显式冲突分支。
- 向量、FTS posting、缓存和重排特征未包含，可从合法且当前可用内容重建。
