# SP-03 技术证据报告

## 结论

**PASS（仅限本 Spike 合成映射与本机环境）**。共运行 22 项断言，Pass 22、Fail 0；P0 失败 0。依赖失效漏报 0、误报 0、扩权 0、旧包重导入复活 0、审计禁止模式命中 0。

## 最小映射

本候选使用内存字典 / JSON 包络和显式 `Derivation.inputs` 边验证语义：Source 与 Artifact 分离；ArtifactVersion 追加且由 hash 定位；AI/规则输出由 Derivation 指向精确输入、Authorization、目的、位置、处理者和版本；Feedback 追加；重要 Link 自带来源、确认和有效性；AuditEntry 只保留不可还原最小元数据。这是测试映射，不是数据库 Schema、API、图模型或技术架构冻结。

## 已验证重点

- 两条主链均可由一个调试查询返回完整证据包。
- 用户原文、外部原文、AI 整理、AI 候选和用户确认对象身份 / 权威字段分离。
- 修改、不可达、断源、删除、撤权与 Feedback 撤回的显式依赖闭包可判定。
- 多输入取最严格约束；合法子集必须新建 Derivation 并披露缺口；空交集拒绝生成。
- Project、文件夹、标签、双链与候选 Link 不产生 Authorization。
- 用户确认历史在唯一证据失效后保留，但退出自动依据并待复核。
- 部分导出如实披露；重导入控制事件优先，复活为 0。

## 复跑

```bash
python3 lifeos/spikes/SP-03/run_spike.py
```

脚本只改写本 Spike 目录内的证据文件，不访问网络、真实 Vault、用户文档、云、第三方 API 或模型。
