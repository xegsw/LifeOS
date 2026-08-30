# attempt-6 review-owned mutation 与负路径结果

review-owned source：`../../tools/independent_runtime_tests.rs`。它仅被写入唯一临时 clone 编译；没有修改候选。

| 反例／mutation | 独立操作 | 结果 | 写前不变量 |
|---|---|---|---|
| 四 Profile 闭集 | 枚举 OpenAI、Anthropic、Ollama、LM Studio；反序列化 `custom` | PASS；`custom` 拒绝 | 不启用、不发送 |
| 20 IPC | review-owned test 读取候选常量 | PASS；恰好20 | 不新增 IPC |
| Health 合法 DTO | 受控 real fixture 的唯一 `source:synthetic:controlled-fixture`、五字段 | PASS；写入 `structured_health_states` | 不含自由文本 |
| Health 非法 energy | `energy=0` | PASS；`health_schema_rejected` | DB/audit/Memory/State 计数不变 |
| Health 多来源 | fixture source + `source:other` | PASS；`source_refs_rejected` | DB/audit/Memory/State 计数不变 |
| Health 缺字段／free_text | 反序列化缺 `sleep_duration_range`、加入 `free_text` | PASS；DTO 入站拒绝 | 进入 runtime 前无写入 |
| Work 日额度与幂等 | 第一条 Work、第二条不同 key、第一条同 key | PASS；第二条 `daily_work_limit_rejected`，同 key 返回相同 record | 计数不变／未复用错误 record |
| 根为普通文件 | 使用 review 创建的 file root | PASS；`runtime_root_type_rejected` | 根/DB 未转化 |
| stale viewport | `[desktop,compact,compact]` | PASS；`evidence_viewport_unstable` | 不生成 receipt |

`candidate_synthetic_suite.log` 另有 52/52 通过，覆盖 root/DB/link/type、budget/authorization/minimal disclosure、Memory cap、Provider 失败关闭、feedback stale/recompute、restart 和五字段 Health。该候选 suite 仅为交叉证据；上表的 review-owned tests 才是独立反例来源。

真实 fixture UI 补测（不含真实数据）：在 direct bundled app 中点击“保存五项状态”后，accessibility receipt 显示“已在本地保存五项结构化状态”；受控临时 SQLite 仅有 `source:synthetic:controlled-fixture` 和五个合法枚举／数值字段。随后点击“确认”产生 `feedback_confirm` 与新的 Today request；无 Provider dispatch。

发现的 review-side噪声均保留但未归因候选：首次 review test 编译的局部变量遮蔽，以及错误地运行全量 `real_self_use` suite。修正后，限定 review suite 的 replay 4/4 PASS，见 `attempt6_real_mode_tests_replay.log`。
