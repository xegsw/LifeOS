# T-ARCH 架构合同符合性

- 单设备、本地优先：符合。
- SQLite + FTS-first：符合；查询命中回连权威门。
- 权威 / 派生 / outbox-job 分责：符合；必要 index job 与捕获同事务登记。
- 队列非权威、幂等与 generation / lease fencing：符合。
- FTS 可重建且故障不伪造保存：符合；维护期间权威捕获测试通过。
- 授权、来源、版本、artifact/source generation、tombstone、证据、租约在读取及 Feedback/Link 写入前重检：符合；上下文缺失、重复或冲突 Authorization fail closed。
- 恢复候选在引擎可信边界读取当前 SQLite 权威投影；包内可变载荷、控制快照与公开 SHA-256 不作为真实性或当前性证明。
- Derivation 以 derivation_input 持久化完整证据版本与 Artifact/Source generation；任一证据失效或代际变化传播到候选身份及消费闭包。
- 导出活跃列表、state、excluded、partial failure 与 control 字段共同遵守 Project 最小披露闭包；混合 Project Derivation/Feedback 整体不导出。
- 派生可失效 / 重建，向量后置：符合。
- Obsidian 与真实 Tauri：关闭态；未触发 R-0040 真实集成复测。
- SQLite-aware 受控备份、基础导出、恢复候选与不复活：符合。
- 模型可替换：仅确定性规则接口语义；无供应商绑定。
- 偏离冻结合同：0。Schema/API/UI/正式格式/SLA/最终目录未冻结。
