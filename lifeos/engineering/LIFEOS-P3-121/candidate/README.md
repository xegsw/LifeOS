# LIFEOS-P3-121 设计忠实与 Runtime 组合闭环（合成数据）

此候选是 P3-121 的受控、合成数据组合闭环，不是生产、Pilot、真实个人数据或 Stage 4 能力。renderer 仅可调用 `capture_record`、`get_today`、`runtime_status`；没有路径参数、网络、模型、外部来源、Vault、导出、同步、Shell、进程、直接文件/数据库或通用路径 API。

唯一运行时数据库是临时根目录内的 `capture.sqlite`：`/private/tmp/lifeos-p3-121-combined-v1/capture.sqlite`。它只接收两个固定、非敏感合成 capture，并以原子发布与 SQLite 校验保持失败关闭。每次 Evidence 重放均删除这一精确临时根目录。

页面中的 Me、Contexts、Memory 及其 Detail 都是 P3-121 固定 fixture 的只读呈现；Today 是唯一会读取 P3-121 Runtime 合成记录的页面。Global AI Panel 和 AI Workspace 明确显示模型、联网、执行、持久化均未启用。

测试夹具只会在 `evidence/test-fixtures/` 里临时创建并清理。它们不会访问、写入或声称任何真实个人数据、Pilot、Vault 或历史 P3-111 资产。
