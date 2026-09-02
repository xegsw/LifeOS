# P3-144 Phase B 独立评审可写／只读白名单

## 允许写入

1. `lifeos/reviews/LIFEOS-P3-144/independent-review/` 及其子路径；本轮先写入的 precontact 控制文件和之后的评审自有 Evidence、测试、报告、Manifest、checkpoint。
2. `/private/tmp/lifeos-p3-144-independent-review-v1` 及其子路径；仅全新合成 DB、review-owned 测试／build／App 运行时文件、普通 marker 和可抛弃 mutation。

## 允许只读（封存后）

1. 本任务卡、`ABF-P3-144-v1`、P3-144 Freeze Manifest、任务卡点名的治理规则和模板。
2. 固定候选 commit `f6c03b083efe4525005887dd1dd4dad423ca6d10` 的 Git objects 和由冻结输入明示的 P3-143 candidate／Task／ABF／Review／Manifest，以及 P3-144 工程 Evidence／Manifest；仅用于复算与只读谱系审计。
3. 任务卡点名的 Frozen Architecture V1.0、模型设置基线、P3-138 正式资产和 D-0595 至 D-0614 正式账本决策。

## 明确不在白名单

- 对任何未列出的目录、临时根、DB、凭据、网络 endpoint、浏览器／桌面目标或历史资产的读写、探测、复制、清理。
- 调用真实 DeepSeek、任何其他 Provider、代理、重定向目标或网络服务。
- 使用候选工程的测试／runner／verifier作为本评审独立正证据。

## 写入约束

- 临时根和 marker 均须在首次写入后被记录；marker 为普通 0600 文件，临时根为 0700。
- 不得以 shell redirect、合同外 stdout、全局 cache、共享 fixture 或 broad inventory 产生输出。
- 清理仅可针对上述精确临时根，并且仅在 marker 验证成功、writer/PID 已停止后执行。
