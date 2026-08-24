# LIFEOS-P3-075 PM Evidence Manifest

## 验证授权与范围

- 依据：D-0316，用户授权 PM 直接验证已提交的 P3-075 当前资产，无需重跑。
- 范围：仅 P3-075 task-local 目录、隔离系统临时副本和非敏感测试文本；不触达个人数据、真实用户路径／文件、Tauri/IPC、网络、云或外部用户。

## PM 隔离复跑

PM 将执行侧 runner 的 Evidence 输出重定向至 `/private/tmp/lifeos-p3-075-pm-evidence/`，不覆盖提交的 `lifeos/engineering/LIFEOS-P3-075/evidence/`：

```sh
python3 -c '…加载 run_self_check.py，并将 EVIDENCE 定向到 PM 临时目录…'
```

- 结果：17 PASS / 0 FAIL / P0=0 / P1=0 / P2=0 / Unknown=0 / Not Implemented=0；退出码 0。
- PM 临时结构化结果与执行侧 `self_check_results.json` 逐字一致。
- 静态边界检查未发现网络、云、Tauri/IPC、导出 API 或外部通道；历史只读输入 hash 在前后保持一致。

## Hash 核验

Manifest 所列 README、运行时、CLI、runner、Manifest 生成脚本、测试、结构化结果与日志 SHA-256 均由 PM 重新计算并一致。

## 结论边界

该 Evidence 仅支持当前 P3-075 的 PM 验收和后续独立复评输入。它不关闭 R-0019／R-0040，不授权个人数据、真实路径／文件、真实导出／恢复、Alpha、冻结、工程基线恢复或 Stage 4。
