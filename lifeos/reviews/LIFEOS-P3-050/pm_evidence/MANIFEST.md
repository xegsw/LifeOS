# LIFEOS-P3-050 PM Evidence Manifest

## 授权与边界

本 Evidence 仅复跑用户本人拥有并授权维护的 LifeOS 本地代码与合成 SQLite 测试数据；无外部目标、真实凭据、网络扫描或真实能力启用。P3-031/P3-046/P3-047/P3-048/P3-049 原工程、评审与 Evidence 未写入；P3-048 总入口仅在隔离临时副本执行。

## PM 核验项目

| 项目 | 路径 / 结果 | 退出码 |
|---|---|---:|
| P3-050 自建独立攻击复跑 | `independent_attack_rerun/independent_attack_results.json`：832 PASS / 0 BYPASS / 0 FAIL / 0 Not Implemented / 0 Unknown；八种 backend/FK/recursive 配置 | 0 |
| P3-048 总入口隔离复跑 | `p3_048_total_rerun.log`：552 PASS；P3-047 等价 297 PASS；P3-031 exit 0；`READ_ONLY_PRESERVED True` | 0 |
| 隔离副本定位 | `isolated_copy_path.txt`；仅供可复核性定位，不得作为工程基线或后续任务输入 | 0 |

## Hash

| 文件 | SHA-256 |
|---|---|
| `independent_attack_rerun/independent_attack_results.json` | `16372161d0992cc1aca6b09b73307e187f51bfd68b2b006cefeefaad4cfbc6ce` |
| `p3_048_total_rerun.log` | `01729149ba61be7293aae67e6f2b898d78314898f2e47a5febae7222ef48c92e` |
| P3-050 原攻击计划（只读核对） | `3ac78f53bc50eea102d9ae40021b9beffa4c26ba5aa863ce5daae084fc1680dc` |
| P3-050 原攻击脚本（只读核对） | `dbdb8855077aedfcc28d6e406f864a008948b16546653f8ef61115081fd9a42f` |
| P3-050 原结构化结果（只读核对） | `38d10b07ddd1a4b3a9981352d4871edd172a06851a72273a7527c76937297405` |

## 结论边界

- PM 复跑支持独立报告的技术统计及 P3-048/P3-047/P3-031 回归结论。
- PM Evidence 不替代 P3-050 的新建会话证明；该证明由任务卡与 `pm_dispatch_evidence/MANIFEST.md` 共同提供。
- 本 Manifest 不关闭 R-0048/R-0049，不冻结资产，不恢复工程基线，也不授权下一阶段。
