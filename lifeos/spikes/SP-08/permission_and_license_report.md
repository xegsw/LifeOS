# 授权与许可检查报告

## 判定顺序

导出前分别检查当前 Authorization、Source 状态、tombstone / restriction generation、证据有效性和外部内容再分发许可。用户拥有自己的数据，不等于用户或 LifeOS 自动拥有第三方全文的再分发许可。

## 样例结果

- LifeOS 用户原文：当前未删除且 Authorization 允许本地导出时包含正文与版本 checksum。
- 外部可缓存快照：只有 `export_allowed` 时包含许可内快照，并继续标为 external，不转成用户原文。
- 外部 pointer-only：只导出合成 locator、Source 身份、许可状态与缺口，不包含全文。
- 已删除：只保留 tombstone generation 与不可复活说明。
- 已撤回 / 已断源：保留 restriction、Authorization / Source 状态和缺口；旧读取结果不作为新正文。
- 唯一证据失效：保留用户确认历史与 `review_required` 语义，不导出为当前可活跃证据。

## 限制

本次没有制定法律条款或正式许可政策，也没有验证真实网站、Vault、供应商或附件。若许可未知，候选默认是 pointer-only / fail closed；正式政策与用户文案需另行评审。

