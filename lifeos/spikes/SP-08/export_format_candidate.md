# 非冻结导出格式候选

## 人可读布局

`sample_export/README.md` 是入口；`content/{project}/{artifact_version}.md` 保存许可且当前可用的正文；`RESTORE_LIMITS.md` 说明恢复边界；`manifest.json` 保存机器身份、关系、控制状态、checksum 与缺口。

## manifest 最小合同

- 包级：`manifest_version`、`schema_version`、`export_metadata`、身份图例、隐私说明、恢复政策。
- 身份：Project、Source、Artifact、不可变 ArtifactVersion。
- 证据：Derivation 的精确输入 / 输出版本、Authorization、工作流与模型描述。
- 用户权威：Decision、Action、Feedback 和已确认 Link；AI 候选继续标为 unconfirmed。
- 控制面：Authorization version、tombstone generation、restriction generation、Source state、证据状态。
- 缺口：删除、撤回、断源、失效证据或许可限制时的 `gap`，必须说明不可还原原因与用户状态。
- 完整性：每个被包含正文版本使用 SHA-256；引用闭包必须能连接 Source / Artifact / Version / Derivation / Link / Feedback。

## 重导入顺序

1. 先校验 manifest 版本、必需字段、文件、checksum 和引用闭包。
2. 先加载目标环境当前 tombstone、restriction generation 与 Authorization version，再处理正文。
3. incoming generation 较低或未知时默认拒绝；来源指针只能恢复为未授权状态。
4. ArtifactVersion 按不可变身份插入；相同 ID / 相同 digest 幂等跳过，相同 ID / 不同 digest 形成显式冲突。
5. 已有用户原文不覆盖，不执行字段级 LWW；AI 候选不能建立用户确认状态。

该布局仅用于证明概念足够小且可校验，不冻结 JSON 字段、枚举、文件布局、压缩、签名、加密、迁移 API 或长期兼容策略。

