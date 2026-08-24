# fixture-pack-v1（SP-01 子集）

## 生成规则

`run_spike.py` 以固定种子 `20260808` 生成 1,000 次基线提交：900 个 Artifact、1,000 个 Version，其中 100 个 Artifact 有第二版本。原文均为 `SYNTHETIC_FIXTURE_..._NO_REAL_DATA` 格式，报告与日志只记录计数、状态和 SHA-256，不记录原文。

夹具覆盖：

- 3 个个人 Project，并每 10 条包含 1 条未归属 Project；
- 250 条 `offline_local_saved + pending_sync`；其余为本地耐久保存且无需同步；
- 20 次同 payload、同幂等键重复投递，另有 10 次同键异 payload 冲突；
- 3 个删除墓碑；
- 1 条 Feedback 确认及其追加式撤回；
- `allowed / denied / expired / revoked` 四种 Authorization 状态；
- 客户端时间有未来与过去偏移，服务端 `created_seq` 与版本主键维持顺序；
- 1,000 次额外强杀提交、100 次并发捕获、50 次备份期间写入。

## 语义边界

- `Artifact` 与 `Version` 分离；版本只追加，不覆盖旧版本。
- `idempotency_key` 同 payload 返回原结果；不同 payload 返回 `IDEMPOTENCY_CONFLICT`。
- `local_saved / offline_local_saved` 是耐久状态；`pending_sync` 是独立同步状态。
- 墓碑和 Feedback 撤回是用户权威的追加记录；活跃视图先排除它们。
- Authorization 仅是最小状态样本，本 Spike 不验证完整六维运行时授权；该责任仍属于后续 Spike。

