# 可重建派生产物报告

FTS posting、向量、缓存和重排特征被显式列入 `excluded_rebuildable_artifacts`，不作为用户业务资产进入导出包。原因是它们依赖具体分词器、embedding 模型、索引版本、缓存策略或排序实现，会扩大包体并锁定供应商 / 技术栈。

重建必须以“当前合法且可消费的原始版本集合”为输入，并在重建时重新检查 Authorization、Source、tombstone、restriction generation 与证据状态。删除、撤回、断源、不可再分发或失效证据不能因为重建再次进入索引；来源指针恢复也不能触发自动抓取。

本次仅验证“可从合法 manifest 内容枚举重建输入”的合同，没有构建真实 FTS、向量、缓存或重排器，也没有验证规模、成本、模型替换或 SP-09 性能。

