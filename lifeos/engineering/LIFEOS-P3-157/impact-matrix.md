# P3-157 影响与安全矩阵

工程主责：技术实现；数据/领域及AI信任安全作为自检视角，PM最终验收。独立评审依D-0661用户暂停例外，不冒称独立Pass。

| ABF | 实现/影响 | 自动与动态依据 | 状态 |
|---|---|---|---|
| 01 | 173完整基线累计；运行根/包身份换157，其余功能不精简 | candidate-diff；全量旧能力回归 | 工程已测，174文件包已绑定 |
| 02 | v6移除合成限定，复用真实existing-only；Store open与每次v6验证12张既有表的列/类型/主键，错误不修复 | existing_schema 5测试覆盖12表缺失/视图/错列/类型/主键/缺库；runtime root旧6；关键guard mutation | 合成Gate通过 |
| 03 | 156有限句式、原文/目标/版本不变；真实mode snapshot接回action | actions36；real_local_routing3 | 工程已测 |
| 04 | 继承事件/反馈/草稿/request事务与恢复 | actions原子故障/重复/重启、Flow竞态 | 工程已测 |
| 05 | 来源失效与行动分离，完整引用身份保留 | action来源独立失效例、stale建议拒绝、不复活 | 工程已测 |
| 06 | 本地ActionApplication不走ModelPort网络；普通v5 DeepSeek逐次披露和旧service/account不变 | real模式DTO double零云调用；旧transport/Key与披露回归；代码差异 | 工程已测，真实发送只由用户 |
| 07 | 新完整真实包及固定155→157正常切换 | 构建、源码/包hash、精确进程身份、单次claim | 非内容切换回执通过 |
| 08 | 正常聊天记录、更新和重启保持 | 用户最少亲验，仅通过或固定码 | 未执行 |

所有动态测试仅157合成根，real-mode DTO double只改返回mode标签，不访问真实库/Key。prepare_database_file(existing_only=true)真实策略函数在合成临时文件上执行；受控真实build只编译不运行，直到合成Gate通过。没有公开任意根参数或真实测试driver。

UI布局/Action Domain及短句识别原样继承156；唯一Application UI接线变化是让real快照也合并v6记录，real-local测试覆盖。既有156宽窄窗观察按代码影响复用，本任务严禁Agent读取真实AX/截图。真实结果必须用户确认。
