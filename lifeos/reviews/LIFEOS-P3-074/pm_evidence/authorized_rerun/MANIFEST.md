# LIFEOS-P3-074 授权重跑 PM Evidence Manifest

## PM 独立核验

- 授权依据：D-0311。
- PM 复跑命令：

```sh
python3 lifeos/engineering/LIFEOS-P3-074/evidence/authorized_rerun/clarity_runner.py \
  --document lifeos/deliverables/LIFEOS-P3-074_alpha_usage_guide_controlled_draft_and_internal_clarity_package_authorized_rerun.md \
  --evidence-dir /private/tmp/lifeos-p3-074-pm-authorized-rerun
```

- 结果：退出码 0；22 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0。
- PM 临时结构化结果与执行侧 `authorized_rerun/clarity_results.json` 逐字一致；复跑输出仅写入系统临时目录，未覆盖授权重跑 Evidence。

## Hash 核验

- `input_hashes.sha256`：25 项直接输入均通过 `shasum -a 256 -c`。
- `historical_readonly_hashes.sha256`：既有未授权 P3-074 交付物、Evidence 及其 PM Evidence 均通过核验，未被覆盖。
- `artifact_hashes.sha256`：授权重跑交付物、runner、结构化结果及日志均通过核验。

## 结论边界

该核验仅支持 P3-074 文档型受控能力包的 PM 验收。它不构成 Alpha 启动、真实用户分发、真实能力、风险关闭、工程基线恢复、资产冻结或 Stage 4 准入。
