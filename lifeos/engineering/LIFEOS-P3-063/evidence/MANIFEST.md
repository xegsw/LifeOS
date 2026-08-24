# LIFEOS-P3-063 Evidence Manifest

更新时间：2026-08-21（D-0273 窄 Rework 后，本地受控运行）

## 边界

仅包含本目录内 Python 标准库 + SQLite 的非敏感合成数据运行证据。不使用网络、Tauri/IPC、Vault、真实路径、真实个人数据、云／第三方模型、导出、同步、多设备、外部用户或 L3。该 Manifest 不构成 Schema/API、工程基线或 Stage 4 冻结。

## 可复跑命令

```sh
lifeos/engineering/LIFEOS-P3-063/scripts/run_demo.sh --synthetic-only --text '合成记录：整理研究问题' --idempotency-key 'synthetic-demo-001' --next-step '人工确认：明天阅读此合成记录'
lifeos/engineering/LIFEOS-P3-063/scripts/run_tests.sh
```

两条命令均在本目录内创建或覆盖其运行输出。测试退出码为 0。

## 执行产物

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `src/mvp.py` | 事务提交、身份、恢复与确认逻辑 | `f35f5651477d1a6fd8cc6e16339b3c63d59ada23c7d00b10ad2954bf72bb632f` |
| `scripts/run_demo.py` | 操作者可输入、仅合成数据的最小闭环 CLI 入口 | `8eaff37b5b108f7046455e9752561a590f4ff7ffa27882dfd60245df9b5e04e4` |
| `scripts/run_demo.sh` | 参数转发的本地运行入口 | `82e3489a1e551573b17c2b40b230dc8767eae02f5a986aeb6cd5a2983d8da694` |
| `scripts/run_tests.sh` | 可复跑测试及日志入口 | `8d3620afd62840739eb79fccd96851bf140cc32aa5e8f839a8bb8bc67eb4b3ee` |
| `tests/test_mvp.py` | 11 项受控回归及端到端正／负测试 | `dd0e464cce7becefcd6959fc2768176c6e09516853c4059330bdcc2eb3ecdcf8` |
| `runtime/operator-rework_snapshot.json` | 操作者输入成功闭环结构化快照 | `7d42d3e1afc8a1f339fad5f2c58a9f274abd5ed0db0d0bceb34c279d56f4ddd2` |
| `evidence/test_results.json` | 结构化测试结果 | `f5b3fdbdbe0763f3ba6f074de596594425b2df0dbee8be520b0ea7e9ea08892e` |
| `evidence/test_run.log` | 完整测试日志 | `dd490e22f892e09f394b7e63d4345dfe04df55a3ad9358d8b231278ee5ae2d0b` |

## 只读输入锚点

| 文件 | 作用 | SHA-256 |
|---|---|---|
| `lifeos/reviews/LIFEOS-P3-062_pm_review.md` | 受控最小能力与不进入 Stage 4 的前提 | `be04b0d5339c05d98de21f05c59d7568ba641a9bae1a6c588fb0dc0bdf99b4f8` |
| `lifeos/deliverables/LIFEOS-P3-062_stage3_to_stage4_admission_baseline_and_minimum_capability_acceptance_package.md` | 闭环验收与停止条件 | `5bb16c7a1e040bc3e39858163ab13716fc25042322308ef22e745ed215ac0ef6` |
| `lifeos/engineering/LIFEOS-P3-009/src/lifeos.ts` | 历史受控骨架的身份与恢复语义参考（只读） | `d5aaef1cbfe795c03e48bf9adbefe42d6a88d2f6e5d1365ece16e4c1b935b471` |
| `lifeos/engineering/LIFEOS-P3-031/migrations/001_candidate_schema.sql` | 历史候选 SQL 的来源身份约束参考（只读） | `bda3e8dbf9ffce002ed0cb3371ccc58b3aea40f819488a21c890ed14382ed9b1` |

## 结果

`test_results.json` 记录 `PASS=11`、`FAIL=0`、`P0=0`、`P1=0`、`P2=0`、`Unknown=0`、`Not Implemented=0`。其中 4 项新增端到端用例直接调用操作者 CLI，覆盖正常输入／显式确认、空输入、幂等冲突与提交前失败。失败注入与其他预期拒绝已被测试捕获，不是失败结果。
