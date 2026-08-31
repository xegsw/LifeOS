# LifeOS GitHub Engineering Model

状态：Initial operating baseline  
适用仓库：`xegsw/LifeOS`  
当前临时产品候选：`lifeos/engineering/LIFEOS-P3-134/candidate`

## 1. 目的

GitHub 用于管理版本、协作和自动化执行；现有 LifeOS 文件治理系统继续负责产品事实、任务合同、证据、验收、冻结、风险和阶段决策。

这是一层工程执行覆盖，不是对现有治理账本的替换，也不改变任何既有 Accepted、Frozen、Complete、Blocked 或 Stage 结论。

## 2. 双层系统

| LifeOS 治理对象 | GitHub 工程对象 | 作用 |
|---|---|---|
| Task ID / Task Card | Issue | 工作入口、讨论和责任追踪 |
| 当前执行状态 | Project status | 日常流转视图 |
| 阶段或版本目标 | Milestone | 一组 Issue / PR 的目标边界 |
| 任务候选与变更 | Branch | 隔离实施 |
| PM / 独立评审输入 | Pull Request | 可审查差异、讨论和检查 |
| 本地 verifier / precheck | GitHub Actions | 自动重复执行 |
| Evidence / Manifest | PR artifacts and repository evidence | 可复核证明 |
| Freeze / release decision | Tag and GitHub Release | 已批准产品版本的不可变引用 |
| Decision Log | Linked Issue / PR plus ledger entry | 决策上下文与权威记录 |

GitHub 状态不能覆盖权威账本。若两者不一致，应停止推进并对账。

## 3. 推荐工作流

```text
Idea / finding
  → GitHub Issue
  → LifeOS task contract
  → Ready
  → short-lived branch
  → implementation + tests + evidence
  → Pull Request
  → CI
  → review / PM decision
  → merge
  → ledger synchronization
  → milestone completion
  → version tag and release when separately authorized
```

## 4. Project 状态

建议 GitHub Project 使用以下状态：

1. **Inbox**：尚未分类的新事项。
2. **Backlog**：有效但尚未承诺。
3. **Ready**：合同、输入和依赖已具备。
4. **In Progress**：已有唯一执行责任和工作分支。
5. **In Review**：已创建 PR，等待代码或治理复核。
6. **Verification**：实现完成，正在运行 CI、证据复算或 PM 验收。
7. **Done**：GitHub 执行已结束，并已同步权威账本。

`Done` 不自动等于产品 `Accepted`、资产 `Frozen` 或版本已发布。

建议增加字段：

- Task ID
- Governance Level
- Priority
- Area
- Risk
- Milestone
- Evidence Status
- PM Result

## 5. Milestone 建议

### M0 — GitHub Engineering Foundation

包含 issue forms、PR 模板、CI、分支规则、标签和 Project 基线。

### M1 — Stable Product Root

把经批准的任务候选晋升到稳定代码目录，例如：

```text
apps/desktop/
```

任务目录继续保存历史候选、证据、评审和 Manifest，但不再作为持续开发主目录。

### v0.1 — Self-use MVP

只收纳构成第一个可安装、可恢复、可验证的自用版本所必需的工作。是否进入该 Milestone 不构成 Stage 4 或外部用户准入。

## 6. 标签体系

建议按维度使用标签，不用标签重复状态机：

### Type

- `type: feature`
- `type: bug`
- `type: task`
- `type: research`
- `type: decision`

### Area

- `area: product`
- `area: ui`
- `area: runtime`
- `area: data`
- `area: architecture`
- `area: governance`
- `area: engineering`

### Priority / risk

- `priority: p0`
- `priority: p1`
- `priority: p2`
- `risk: trust`
- `risk: privacy`
- `risk: migration`
- `risk: release`

### Resolution

- `blocked`
- `needs-evidence`
- `needs-decision`
- `skip-changelog`
- `breaking`

权威严重度仍以正式 PM 结论和账本记录为准。

## 7. 分支与合并

`main` 是唯一长期分支。所有正常变更使用短期分支和 PR。

默认采用 squash merge。启用分支保护后，至少要求：

- PR 才能合并；
- CI 必须通过；
- conversation resolved；
- 禁止 force push 和删除 `main`；
- 管理员也遵守规则，除非紧急恢复且留下决策记录。

当前私有仓库套餐若不支持所需规则，应在套餐或可见性允许后启用；在此之前以流程和 PR 自律执行。

## 8. 当前 CI 绑定

第一版 CI 直接绑定：

```text
lifeos/engineering/LIFEOS-P3-134/candidate
```

检查内容：

- Python 语法；
- 当前候选 JSON；
- 权威入口文件存在性；
- Rust 格式；
- Cargo check；
- Cargo test。

该绑定是过渡方案。稳定产品根建立后，CI、Dependabot 和发布流程必须改指稳定目录。

## 9. 版本模型

以下对象不可混用：

| 对象 | 示例 | 含义 |
|---|---|---|
| 任务 ID | `LIFEOS-P3-134` | 一次治理或实施工作 |
| 架构版本 | `Architecture V1.0` | 规范基线 |
| 产品版本 | `v0.1.0` | 可交付软件版本 |
| Git commit | SHA | 仓库状态 |
| Git tag | `v0.1.0` | 对一个批准 commit 的不可变名字 |
| GitHub Release | `v0.1.0` | 面向安装或交付的版本记录 |

建议在稳定产品根建立前不创建正式产品 Release。

## 10. 初始迁移边界

本基线只新增工程管理文件，不：

- 移动 P3-134 候选；
- 修改 CURRENT_STATUS、DECISION_LOG、FREEZE_STATUS 或 TASK_REGISTRY；
- 重写历史任务、证据或评审；
- 宣布 Stage 4；
- 创建产品版本；
- 启用自动部署生产环境。

后续结构迁移必须作为独立、可回滚、可验收的 LifeOS 任务执行。
