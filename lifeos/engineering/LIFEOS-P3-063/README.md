# LIFEOS-P3-063 受控本地 MVP 最小闭环

本目录是一次性、隔离的本地验证资产。仅使用 Python 标准库、SQLite 和非敏感合成记录；不使用网络、Tauri/IPC、文件选择器、Vault、真实路径、云服务或 AI 模型。

## 运行

```sh
./scripts/run_demo.sh --synthetic-only \
  --text '合成记录：整理研究问题' \
  --idempotency-key 'synthetic-demo-001' \
  --next-step '人工确认：明天阅读此合成记录'
./scripts/run_tests.sh
```

`run_demo.sh` 要求操作者提供合成原文、幂等键和下一步确认文本，并显式传入 `--synthetic-only`。它只会在本目录 `runtime/` 中按 `--run-id`（默认 `operator-session`）创建 SQLite 文件，完成「捕获 → 提交后已保存 → 来源可见 → 项目恢复 → 用户确认下一步」并写入结构化快照。参数不接受路径，`--run-id` 也只允许字母、数字和连字符。测试脚本会清理并重新创建自己的临时数据库，所有输出均在本目录内。

## 语义边界

- 只有 SQLite `COMMIT` 成功后，`capture()` 才返回 `saved: true` 和“已保存”。
- 记录的 `content_identity` 固定为 `user_original`，来源固定为 `user_local_entry`。不存在 AI 生成、推断或建议；界面状态明确标记 `ai_features: disabled`。
- Project 恢复只接受预置的受控合成 Project `project-synthetic-001`；下一步必须通过 `confirm_next_step()` 显式确认，仅记录本地确认事实，不创建外部动作或 L3 行为。
- 本资产不声称生产级耐久、断电保证、备份恢复、真实桌面运行、导出或 Stage 4 准入。
