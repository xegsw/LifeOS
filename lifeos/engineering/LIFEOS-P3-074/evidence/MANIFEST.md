# LIFEOS-P3-074 Evidence Manifest

## 边界与只读输入

本 Evidence 只验证内部 Markdown 草案的清晰度与禁止表述，不启动 Alpha，不发送或处理真实数据，也不运行、修改或重建任何历史工程能力。`input_hashes.sha256` 记录 `CURRENT_STATUS`、冻结／风险／关卡文件，以及 P3-063/064、065/066、067/069、070/071、072/073 的最终 PM Review 与独立 Review 输入 hash。历史输入均只读。

## 可复跑入口

```sh
python3 lifeos/engineering/LIFEOS-P3-074/evidence/clarity_runner.py \
  lifeos/engineering/LIFEOS-P3-074/evidence/clarity_results.json
```

runner 会在 `/private/tmp/lifeos-p3-074-clarity-copy/` 创建一次性文档副本，完成首次阅读、重复阅读和版本更新后复读等价演练后清理该目录。退出码 0 表示所有检查通过。

## 结果

`clarity_results.json` 记录 19 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0 / uncovered=0。覆盖：

| 任务卡验收标准 | 内部场景／检查项 | Evidence |
|---|---|---|
| 合成能力不外推为真实能力 | IC-01、IC-05、IC-06、IC-08、FC-01 至 FC-04 | `clarity_results.json`；草案状态卡与限制章节 |
| 明确确认、拒绝／阻断与失败披露 | IC-02、IC-03、IC-04、IC-09 至 IC-12 | `clarity_results.json`；草案交互语言章节 |
| 首读、幂等校对、版本更新复读 | IC-13、IC-14、IC-15 | `clarity_results.json`；`clarity_runner.log` |
| 历史只读资产未被覆盖 | 输入 hash 清单与仅 task-local 新文件核对 | `input_hashes.sha256`；本 Manifest |
| 禁止能力保持关闭态 | 禁止真实 Alpha、Stage 4、真实导出、真实恢复的静态词条检查 | `clarity_results.json`；草案未实现能力表 |

运行时重启不适用于文档；任务卡规定以“版本更新后复读”作为已记录的等价替代。原子失败、半成品清理、拒绝／阻断与审计追溯在本任务中仅验证其**文案是否准确披露**，不重新执行历史工程验证，也不把它们写成真实能力。

## 文件 hash

| 文件 | SHA-256 | 用途 |
|---|---|---|
| `lifeos/deliverables/LIFEOS-P3-074_alpha_usage_guide_controlled_draft_and_internal_clarity_package.md` | `3f67630b41ee2c738698f75c0169eb433e4e4900cb27c3c760cc88ed6bafb2b0` | 受控 Alpha 使用说明草案 |
| `clarity_runner.py` | `b0d347a62c93ab1e17f5d81aae8270d3d666a6b4613e87143df39518eef078cf` | 可复查检查 runner |
| `clarity_results.json` | `3e6060c54ae7f7a29575a5bdfb4733d41067d34c90cf981a75b8d23ff64091b4` | 逐项结构化结果 |
| `clarity_runner.log` | `620e86df86d2a1c06853a82e081ca36223b6b939d124bf92b5b45cf5f3654152` | 复跑日志 |
| `input_hashes.sha256` | `1564239d22ace8ac9c1917abb627d5580eb0c53b059e001141a5f1b10260537b` | 只读输入 hash |

## 自检结论

通过。未发现 P0/P1/P2、Unknown、Not Implemented、Evidence 冲突、历史资产覆盖、越权范围或禁止能力默认关闭失效。没有包内整改遗留项。该结论仅允许提交 PM 验收；不构成 Alpha 启动、真实用户分发、风险状态变化、资产冻结、工程基线恢复、真实能力授权或 Stage 4 准入。
