# LifeOS 架构文档

本目录用于集中存放 LifeOS 的架构基线、架构演进记录与接口/契约设计。

## 文档结构

- `LifeOS架构基线V1.0.md`：当前已确认的 MVP 1.0、逻辑架构、技术架构与第一批核心 Ports 基线。

## 使用原则

1. 本目录描述 LifeOS 的目标架构与当前已确认架构决策。
2. 已冻结的项目主账本、风险、任务和历史决策仍以 `lifeos/DECISION_LOG.md`、`lifeos/FREEZE_STATUS.md`、`lifeos/TASK_REGISTRY.md` 等现有治理文件为准。
3. 本目录新增内容不得自动改变既有 Frozen / Accepted / Risk 状态。
4. 架构实现允许演进，但核心边界应优先保持稳定；外部供应商、数据库、Agent、设备和 UI 应通过 Ports / Adapters 与核心解耦。
