# P3-057 执行日志摘要

## 隔离与输入

- 在读取 P3-044 攻击 runner / 场景表前，已封存 `00_attack_plan_and_independence.md`。
- 新 runner 是 `fresh_independent_runner.py`；仅以当前 P3-031 候选 SQL 路径为输入，不 import、调用或复制 P3-044 攻击函数或场景表。
- 实际测试数据库由 Python `tempfile.TemporaryDirectory` 在系统临时目录中新建；每个案例独立建库。没有在工程目录、历史 evidence 或项目账本写入。

## 执行命令与结果

1. P3-057 独立反例矩阵：

   ```text
   python3 lifeos/reviews/LIFEOS-P3-057/evidence/fresh_independent_runner.py \
     --project-root /Users/xxe/Documents/No.2 \
     --schema /Users/xxe/Documents/No.2/lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql \
     --results /Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-057/evidence/fresh_independent_results.json
   ```

   退出码 `0`；P1 312 PASS / 0 FAIL，P2 2 PASS / 0 FAIL，Not Implemented 0，Unknown 0。八个配置均已执行：memory/file × `foreign_keys` ON/OFF × `recursive_triggers` ON/OFF。

2. P3-031 合同入口隔离复跑：将整个 `lifeos/engineering/LIFEOS-P3-031/` 复制至 `mktemp -d /private/tmp/lifeos-p3-057-contract.XXXXXX` 创建的临时目录后执行其复制品的 `tests/run_contract_tests.py`，结果写入本任务 evidence。

   退出码 `0`；P0 18 PASS、P1 29 PASS、P2 27 PASS，全部 0 FAIL / 0 Not Implemented。该执行没有运行或修改原工程入口。

## 输入快照

- P3-057 runner 记录候选 SQL 的运行前/后 SHA-256 均为 `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1`。
- 历史 P3-044 SQL 快照为 `0b7f33930c97f3b268e6ccca2d9b2f3fac4242d95e358b3edcf77f3d5aa0d376`；差异来自后续已记录的生命周期/终态整改，而非该历史快照被改写。
- P3-043 原始失败 evidence 的 4 项以及 P3-044 快照/runner/7 项 evidence 的 SHA-256 均与其 Manifest 期望值相符，详情见 `fresh_independent_results.json`。
