# LIFEOS-P3-064 Independent Evidence Manifest

更新时间：2026-08-21

## 隔离与只读证明

- 本评审在全新 Codex 会话中进行，未复用 P3-063 执行或 Rework 会话。
- 被评审目录仅以 `cp -R lifeos/engineering/LIFEOS-P3-063 /private/tmp/lifeos-p3064-final.8kvPed/LIFEOS-P3-063` 复制到临时目录后运行；原工程、P3-009、P3-031、历史 Review/Evidence 与项目账本均未写入。
- P3-063 当前实现 hash 已与执行侧和 PM Evidence 对齐：`src/mvp.py` `f35f…632f`、`scripts/run_demo.py` `8eaf…e04e`、`scripts/run_demo.sh` `82e3…a694`、`tests/test_mvp.py` `dd0e…dcf8`。
- `readonly_anchor_hashes.sha256` 记录 P3-009、P3-031、P3-063 三个原始 Evidence Manifest 的读取锚点；本任务只在本目录下新建证据。

## 独立方法与命令

`independent_runner.py` 是本任务新写的黑盒 runner；它不导入、不调用、也不复制 `P3-063/tests/test_mvp.py`。它在临时副本中直接调用候选 CLI，并以 SQLite 查询与快照断言验证结果：

```sh
python3 lifeos/reviews/LIFEOS-P3-064/evidence/independent_runner.py \
  /private/tmp/lifeos-p3064-final.8kvPed/LIFEOS-P3-063 \
  lifeos/reviews/LIFEOS-P3-064/evidence/independent_results.json
```

退出码 `0`；结构化结果为 9 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0。独立断言涵盖：操作者新参数的正路径、原文／来源／内容身份、显式确认和无外部动作；同键同文本幂等；同键不同文本拒绝；空输入、缺失 `--synthetic-only`、非法 `--run-id`、提交前注入失败、未知 Project 拒绝；以及 Python 导入/URL 的静态网络边界检查。

补充运行使用候选 shell 入口（退出码 `0`）：

```sh
/private/tmp/lifeos-p3064-final.8kvPed/LIFEOS-P3-063/scripts/run_demo.sh \
  --synthetic-only --text '独立 shell 合成原文' \
  --idempotency-key 'independent-shell-001' \
  --next-step '独立 shell 明确确认' --run-id independent-shell
```

该输出快照显示 `saved=true`、`user_original`、`user_local_entry`、`user_confirmed`、`external_action=none`、`ai_features=disabled`、`network=disabled` 与 `tauri_ipc=not_used`。

候选自身回归在另一临时副本复跑，退出码 `0`，为 11 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0；仅作补充，不是主要结论依据。

## Evidence 文件与 SHA-256

| 文件 | 用途 | SHA-256 |
|---|---|---|
| `independent_runner.py` | 新建独立 runner | `a2acdd8831f28ad23bcc76998e116d90f9c1ce56ca0c3e67946320f2b03b5c43` |
| `independent_results.json` | 独立结构化 9 项结果 | `b889483e23b2ab65f52d3ad8c342ddeaaa68dc8b28005fdaf5c5df7d9bf06bbf` |
| `independent_runner.log` | 独立 runner 完整输出 | `7d2a166753e5a07ed1a95f6a11ba3eefcecbb0a303ec701b12b2b274aa0a9c27` |
| `independent_shell_positive_snapshot.json` | 独立 shell 正路径输出快照 | `4d531b99c3f3460e79fc73e36cb9169979c0c9d3b0629d715f1bea49ffe87b8a` |
| `candidate_regression.log` | 候选 11 项回归补充日志 | `dd490e22f892e09f394b7e63d4345dfe04df55a3ad9358d8b231278ee5ae2d0b` |
| `readonly_anchor_hashes.sha256` | 历史 Evidence 只读锚点 | `174a2ec5edb7e360a8efdcc72d9bfcc2806d4bb93aa8053e29e91a9ae03ac90b` |

`evidence_hashes.sha256` 保存完整清单。临时副本路径仅用于本地可复核，不是持久工程资产；它不含真实个人数据、真实路径接入、Tauri/IPC、Vault、网络、导出、云、同步、多设备、外部用户或 L3。

## 结论边界

本 Evidence 只证明当前 hash 的受控合成 SQLite CLI 在上述路径可运行。静态审查和合成 CLI 不能证明真实 Tauri/IPC、真实路径、磁盘满/断电耐久、备份恢复、导出、基础权限设置、Alpha 使用或 Stage 4；R-0019、R-0040 和其他风险状态不因此改变。
