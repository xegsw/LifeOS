# LIFEOS-P3-129 V1.0 架构权威冻结候选包

## 候选状态

本目录是 `LIFEOS-P3-129` 的冻结候选与静态 Evidence，不是 promotion 结果。

- 当前 V1.0 canonical 仍为 `Architecture Baseline Draft`；本包不得将其解释为 Frozen。
- `canonical_promotion_patch.json` 只描述独立评审、PM Pass 与最终用户 Gate 均通过后可由 PM 执行的一行元数据替换；它没有被执行。
- V0.1 的历史文件、Review、Evidence 与此前的 Freeze Status 均只读保全。V1.0 仅在最终 promotion 后取得前向技术架构权威；它不删除或追溯改写 V0.1。
- P3-126/P3-127 记录的是合成、离线、受控 Runtime/Evidence 事实，并不冻结产品 Runtime、Schema/API、IPC 签名或工程基线。

## 文件职责与复跑

| 文件 | 职责 |
| --- | --- |
| `fixed_inputs.json` | 本候选唯一固定输入及 SHA-256 |
| `v0_to_v1_reconciliation.json` | V0.1 每项可操作规范到 V1.0 的无遗漏分类 |
| `cross_baseline_compatibility.json` | 产品宪法、核心领域、AI 信任、Runtime 与 Gate 兼容检查 |
| `freeze_scope.json` | V1.0 的固定项、显式不冻结项与越界负例 |
| `runtime_transition.json` | P3-126/P3-127/P3-128 保留、适配、后置规则 |
| `canonical_promotion_patch.json` | 唯一允许的、未执行的 canonical promotion 方案 |
| `verifier.py` | 只读静态 verifier；含 pristine 和四类内存 mutation |

在仓库根目录复跑：

```bash
python3 -B lifeos/architecture/LIFEOS-P3-129/verifier.py verify
python3 -B lifeos/architecture/LIFEOS-P3-129/verifier.py mutations
```

两条命令不启动产品 Runtime、不访问网络、数据库、浏览器、模型或外部系统，也不创建临时目录。

## 评审交接

执行侧仅交付候选。另一个全新隔离会话必须从固定输入自行创建独立 runner、Manifest 和 Review；不得导入、调用或复制本目录的 `verifier.py` 作为独立性证明。
