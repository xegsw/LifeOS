# P3-155 既有能力与最小增量

基线：P3-154 flow-stage 完整165文件，逐项SHA一致后复制。已完成154终局，不重开旧工程。

| 能力 | 已有实现 | 本轮实际缺口/验证 |
|---|---|---|
| 源刷新、暂停、取消、epoch/幂等 | source-engine source_store/source_api/source_worker | 复用；验证重启后的手动恢复与旧worker，补准确阶段和计数 |
| 未变化文件与解析复用 | source_worker::import_one 的identity快速路径 | 需覆盖元数据变化但内容相同的fingerprint路径 |
| 文件缺失、撤权、失效 | finalize_scan、validate_reference、send_fence | 合成反例复用并回归，原件零写入 |
| 健康既有ZIP导入事务/重复/歧义 | apple_health::import_bound、health_target::import_fixed | 154总入口主动拒绝真实导入；155授权恢复既有精确入口，并把status表CREATE改为existing-only验证 |
| 健康重启状态/手动重试 | apple_health_api status/start/statusPersistenceWarning | 保留；补缺表不迁移和失败保留，绝不自动导入 |
| 单来源失败 | SourcesController.start 共用try/catch | 已定位串行短路及全页错误；先复现再隔离两类状态与手动重试 |
| 对话恢复与错误归属 | ControlledFlow最终修正 | 保持字节或仅合成根变化，完整8项回归 |
| 设置、Key持久、14 IPC | 完整Host/Application链 | 无功能重绘，保留组合回归与负路径 |

非关键状态汇总仅派生于既有表/字段，不新增公共命令、输入DTO、Schema或权限。真实数据由App处理，Agent只验证合成；暂不切换App。
