# SP-03 合成夹具清单

## 版本

- 夹具版本：`fixture-pack-v1-sp03`
- 固定种子：`20260808`
- 全部内容均为合成标识和不可用于真实决策的测试文本。

## 语义覆盖

- 3 个 Source：模拟 Obsidian Vault、外部材料、本地输入通道。
- 4 个 Artifact / 4 个精确版本：外部 Obsidian 原文、外部材料、LifeOS 用户原文、排除输入。
- 3 组六维 Authorization：本地 Project A、跨 Project 但更严格的外部材料、已撤回排除授权；均含强制政策包络。
- 4 个 Derivation：恢复包、候选下一步、Decision 证据、多输入整理。
- 8 个输出/业务对象：AI 整理、AI 候选 Action、用户编辑确认 Action、外部主张、AI 候选 Decision、用户确认 Decision、多输入输出、Feedback 派生输出。
- 7 条 Feedback：编辑确认、完成、延期、确认、拒绝、纠正、撤回；另在重导入场景加入当前撤回控制。
- 4 条重要或候选 Link：用户确认 Project Link、文件夹候选、标签候选、双链候选。
- 2 条最小 AuditEntry。

## 两条主证据链

1. 模拟 Obsidian 外部版本 → 恢复包 → AI 候选下一步 → 用户编辑确认的新对象/版本 → 完成 Feedback。
2. 外部材料版本 → Decision 候选 → 用户确认 Decision → 输入删除/不可达/撤权 → 证据不可用、待复核、退出自动依据。

## 异常与控制夹具

- 输入版本修改、来源不可达、断开来源、删除内容、撤回处理许可、Feedback 撤回。
- 跨 Project 与外部文件夹/标签/双链候选关系。
- 多输入最严格约束、合法子集新 Derivation、无合法交集拒绝生成。
- 部分导出：成功、政策排除、授权失败。
- 删除前旧包重导入：当前墓碑和 Feedback 撤回优先。

## 原文保护说明

脚本只在内存里短暂构造 `SYNTHETIC_*_NO_REAL_DATA` 字符串以计算版本 hash；证据 JSON、AuditEntry 和日志不写入这些正文。hash 仅用于合成版本完整性定位，不用作 AuditEntry 标识。
