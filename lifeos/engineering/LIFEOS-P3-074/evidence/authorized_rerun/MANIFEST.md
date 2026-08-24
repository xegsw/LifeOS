# LIFEOS-P3-074 授权重跑 Evidence Manifest

## 授权与范围

- 授权依据：任务卡 D-0311；仅新增本目录和授权重跑版交付物。
- 运行类型：文档型受控能力包自检；不执行 Alpha、不访问真实数据/路径/文件、不启用网络、Tauri/IPC、云、外部用户或真实导出。
- 历史 P3-074 未授权交付物与 `lifeos/engineering/LIFEOS-P3-074/evidence/` 既有文件为只读保留；本次不覆盖它们。

## 可复跑入口

```sh
python3 lifeos/engineering/LIFEOS-P3-074/evidence/authorized_rerun/clarity_runner.py \
  --document lifeos/deliverables/LIFEOS-P3-074_alpha_usage_guide_controlled_draft_and_internal_clarity_package_authorized_rerun.md \
  --evidence-dir lifeos/engineering/LIFEOS-P3-074/evidence/authorized_rerun
```

运行会在系统临时目录创建并删除三份文档副本：首次阅读、重复阅读、带非语义版本标记的复读。它只覆盖本 Evidence 目录中的运行结果和日志。

## 产物与结果

| 文件 | 用途 |
| --- | --- |
| `clarity_runner.py` | Python 标准库 runner；检查 required boundary phrases、肯定式越界声明、三轮临时副本复读和静态关闭态。 |
| `clarity_results.json` | 逐项结构化结果：22 PASS / 0 FAIL；P0/P1/P2/Unknown/Not Implemented 均为 0。 |
| `clarity_runner.log` | 本次运行摘要。 |
| `input_hashes.sha256` | 本次只读直接输入锚点的 SHA-256。 |
| `historical_readonly_hashes.sha256` | 未授权 P3-074 历史 Evidence 的只读 hash 锚点。 |
| `artifact_hashes.sha256` | 授权重跑版交付物、runner、结果和日志的 SHA-256。 |

## SHA-256 快照

以下命令在本次最终 runner 完成后执行；产物 hash 供 PM 复算：

```sh
shasum -a 256 \
  lifeos/deliverables/LIFEOS-P3-074_alpha_usage_guide_controlled_draft_and_internal_clarity_package_authorized_rerun.md \
  lifeos/engineering/LIFEOS-P3-074/evidence/authorized_rerun/clarity_runner.py \
  lifeos/engineering/LIFEOS-P3-074/evidence/authorized_rerun/clarity_results.json \
  lifeos/engineering/LIFEOS-P3-074/evidence/authorized_rerun/clarity_runner.log
```

输入锚点的实际 hash 在 `input_hashes.sha256`。本 Manifest 不对其自身列 hash，避免自引用；PM 可单独复算本文件。

## 验收矩阵

完整“验收标准 → 场景/检查项 → Evidence”矩阵位于授权重跑版交付物的“验收—场景—Evidence 矩阵”章节；逐项 ID 与本 runner 的 JSON 结果一一对应。

## 适用性与未覆盖项

- 本地预检：Skipped。统一脚本只能向 `lifeos/local_prechecks/` 新增报告，而 D-0311 将本次新增写入严格限于授权重跑版交付物与本目录；为不越权写入，未调用该脚本。该跳过不替代 PM 人工复核。
- 首次／幂等／版本更新后复读：已覆盖；任务无运行时重启，版本更新后复读是任务卡批准的等价替代。
- 原子失败、半成品清理、拒绝和审计追溯：本次只核对文案没有外推 P3-063/P3-067/P3-072 的合成证据；不把它们误报为本任务的真实运行时证明。
- 未覆盖项：无（限任务卡所定义的文档草案与内部可理解性验证）。
- 本任务不构成 Alpha 启动、真实能力、风险关闭、工程基线恢复、资产冻结或 Stage 4 准入。
