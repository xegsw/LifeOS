# LIFEOS-P3-081 Evidence Manifest

## 范围

- 任务：Stage 3 整合能力收口与 Stage 4 候选就绪复核。
- 方式：新隔离、只读阶段治理／独立复核会话。
- 未修改：工程代码、历史 Review／Evidence、风险、冻结、工程基线、Schema/API、项目账本；未执行真实能力。
- 结论：本 Manifest 仅支持输入谱系与本任务发现，不支持 Stage 4、冻结、风险关闭／重开、基线恢复或真实能力启用。

## 核验输入（当前 SHA-256）

| 输入 | SHA-256 | 核验 |
|---|---|---|
| `lifeos/engineering/LIFEOS-P3-079/evidence/rework/MANIFEST.md` | `358f668855608fdd72f0cd8fc14934fd92f7aeaf2d637912d632bea7dc9cd8dd` | 与 P3-079 PM Rework Manifest 一致 |
| `lifeos/engineering/LIFEOS-P3-079/src/integrated_runtime.py` | `19d337a560cfa3e6098571b29a71fc121e059db1c0914e3e3f58f3f740905788` | 与 P3-080 independent Manifest 一致 |
| `lifeos/engineering/LIFEOS-P3-079/scripts/operator_cli.py` | `a2fda42bcabfb409fa28f05d383f8308cefae496de4a2465295e4284325ae45a` | 与 P3-080 independent Manifest 一致 |
| `lifeos/reviews/LIFEOS-P3-080/evidence/MANIFEST.md` | `4114715cc5277842bb20e636ab2121c3bee41d72e75f1c3a34feef54c2a0b98e` | 与 P3-080 PM Evidence Manifest 对此文件的记录一致 |
| `lifeos/reviews/LIFEOS-P3-080/pm_evidence/MANIFEST.md` | `61fea8050b19c2118abb0dc14bece4b397a1aaec01cc2d24b4cc23dd9b8c6a2a` | **与该文件记录的自身 hash `4114715c…a0b98e` 不一致** |

## 已读取的定向证据

- P3-062 交付物、PM Review 与 Manifest。
- P3-063／064、P3-065／066、P3-067／069、P3-070／071、P3-072／073、P3-074、P3-075／076、P3-077／078、P3-079／080 的最终 PM Review、独立 Review（适用时）与 Evidence Manifest。
- `TASK_REGISTRY.md`、`FREEZE_STATUS.md`、`RISK_LOG.md` 指定风险、`DECISION_LOG.md` D-0325–D-0332，以及 `STAGE_GATES.md` 的 Stage 3→4 与 Gate 1／3／4／5。

## 可复查命令

```bash
shasum -a 256 \
  lifeos/reviews/LIFEOS-P3-080/evidence/MANIFEST.md \
  lifeos/reviews/LIFEOS-P3-080/pm_evidence/MANIFEST.md \
  lifeos/engineering/LIFEOS-P3-079/src/integrated_runtime.py \
  lifeos/engineering/LIFEOS-P3-079/scripts/operator_cli.py
```

## 发现

P0=0，P1=1（P3-080 PM Evidence Manifest 自指 hash 不一致），P2=0，Unknown=0，Not Implemented=0。依据 P3-081 任务卡，Evidence 冲突使本任务结论为 Blocked；本会话无权修改冲突源。
