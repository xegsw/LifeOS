# LIFEOS-P3-095｜真实本地捕获、持久化与今日页展示全新隔离独立复评

## 评审信息

- 对应任务 ID：LIFEOS-P3-095
- 是否为受控能力包：Yes（对 P3-094 当前 hash 的独立复评）
- 能力包边界／被评审最终 hash：`src/local_capture.py` SHA-256 `adc0b8900829f490b7062efc9210f0488c4863405c69f1a8d87ca037cfd4bc70`
- 对应交付物路径：`lifeos/deliverables/LIFEOS-P3-095_real_local_capture_persistence_today_view_fresh_isolated_independent_re_review.md`
- 独立评审角色：技术架构负责人
- 协审视角：数据／来源、AI 信任与安全、体验设计
- 评审关卡：Gate 2、Gate 3、Gate 4；Gate 1 仅做定位一致性核对；Gate 5 不在本任务验证范围
- 独立评审路径：本文件
- 评审结论：**Rework**
- 执行授权证据：用户于 2026-08-22 将 `lifeos/tasks/LIFEOS-P3-095_real_local_capture_persistence_today_view_fresh_isolated_independent_re_review.md` 投递至本新建隔离 Codex 独立评审会话；接收时间 2026-08-22 08:50 CST。
- 实际模型：`gpt-5.6-terra` + `high`（按任务卡及本会话路由，未降级）。
- 固定授权范围：评审侧自建固定非敏感文本、独立 task-local SQLite／HTML、P3-094 资产只读 hash／静态核查、独立 Review／Evidence。

## 能力包独立性与回流规则

- 执行侧与评审侧是否隔离：Yes；本会话未参与 P3-094 实现或 PM 验收。
- 是否只评审能力包最终 Evidence／hash：Yes，并定向核对 attempt-1／2／3 历史事实链。
- 独立 runner、逐项结果、Manifest 与复跑入口：已保留。
- 是否可验证 runner 未导入、调用或复制执行侧测试：Yes；runner 仅通过 `importlib` 载入 `src/local_capture.py` 公开运行时，不读取或执行 P3-094 测试／runner。
- 是否发现需回包内整改问题：Yes；P1=2、P2=1、Not Implemented=4。修复须回到 P3-094 同一能力包，PM 验收后重新进行全新隔离独立复评。

## 本地 `file:` 动态 Evidence 预检

- 指定浏览器：Google Chrome（`com.google.Chrome`）经 Computer Use `@oai/sky`。
- task-local `file:` 入口：未生成可提交入口；离线 P1 后 runner 已清理运行目录。
- 新标签页首次／第二次预检：Not Implemented；不是浏览器环境 Blocked。
- 动态矩阵是否只在预检通过后开始：N/A；未开始。
- 停止依据：任务卡明确要求发现 P0/P1 即停止；未使用 In-app Browser、HTTP、网络、CDP、命令行浏览器或规避路径。

## 评审摘要

1. 当前 P3-094 核心源码 hash 与 attempt-3 记录一致；重点只读资产评审前后 9/9 hash 相同。
2. 独立离线矩阵 10 项中 9 PASS、1 FAIL；首次捕获、幂等、同键异文拒绝、空输入拒绝、跨进程复读、身份／时间／来源、原子失败与损坏 DB fail-closed 均通过。
3. 实质 P1：精确 `DELETE` 后数据库为空且再次渲染正确拒绝，但此前的 `today.html` 仍保留，可继续显示已清理记录。源码 `delete_all()` 只删除 SQLite 行（第 88～99 行），`render_today()` 在无记录时于写文件前抛错（第 108～112 行），没有移除既有页面。
4. 第二项 P1：本评审语法检查生成 `/private/tmp/lifeos-p3-095-pycache`；精确删除被执行环境自动审批／用量限制拒绝，故不能声称全部系统临时残留为零。该目录不含用户内容，只含 Python cache。
5. P2：attempt-3 PM Manifest 所列 PM Review 相对路径不解析；所记 hash 与实际 PM Review 一致，因此不是内容 hash 冲突，但降低直接可复算性。
6. 因先行 P1，Chrome 动态 4 项诚实记录为 Not Implemented；本结论不是 Blocked，也没有用旧动态 Evidence 替代本轮独立动作。

## 已通过内容

- Gate 2 部分通过：固定非敏感原文身份、记录时间、本地捕获来源保持清楚；没有 AI 改写或真实用户内容进入 Evidence。
- Gate 3 通过本轮关闭态核查：未启用 AI、网络、HTTP、云／第三方、Tauri/IPC、Vault、导出、同步、多设备、L3 或外部用户。
- Gate 4 部分通过：SQLite 首次写入、幂等、跨进程复读、原子回滚、损坏 DB fail-closed 和精确确认门均可复现。
- 独立性与 hash 保全成立；P3-094 被评审文件没有被本会话修改。

## 关键问题与必须整改项

### P1-01｜清理后旧今日页仍可展示

事实：`delete_all(..., "DELETE")` 返回清理成功且 DB 记录数为 0；随后 `render_today()` 抛出“无记录”错误，但旧 `today.html` 未删除。用户若仍打开或重新加载该文件，会看到已清理内容。

整改标准：清理事务成功后，任何先前内部展示工件必须失效或被精确移除；清理失败不得误删；新增独立可验证的“先渲染→精确清理→旧页面不存在／不可展示”正负回归。

### P1-02｜本评审自身 pycache 残留未能清理

事实：精确目录 `/private/tmp/lifeos-p3-095-pycache` 的删除被执行环境审批／用量限制拒绝。不得把这一工具侧异常外推为 P3-094 工程缺陷，但它使本任务不满足“系统临时残留为零”的完成条件。

整改标准：由用户／PM明确处理该精确目录；后续独立复评不得创建仓库外不可清理缓存，或须在提交前证明全部 task-local 残留为零。

## 条件与计数

- P0=0；P1=2；P2=1；Unknown=0；Not Implemented=4。
- P2 不单独阻止工程整改，但建议更正未来 PM Evidence Manifest 的相对路径生成规则；历史资产不得由本会话修改。
- 当前不满足 Pass 条件，不能降为 Pass with Conditions。

## 关卡检查

- Gate 1 产品一致性：有限通过；仍服务个人本地捕获→今日页闭环，未扩大产品范围。
- Gate 2 数据与来源：**未通过**；清理后旧展示工件仍暴露已清理用户原文语义。
- Gate 3 AI 权限与信任：通过本轮关闭态核查；AI 与外部处理未启用。
- Gate 4 技术可行性：**未通过**；清理生命周期合同存在 P1，Chrome 独立动态矩阵未实施。
- Gate 5 用户价值验证：未覆盖；不得写成通过。

## 风险与状态边界

- R-0051 继续 Open；本评审无权关闭或重开风险。
- P3-094 继续 Not Frozen；不恢复工程基线，不冻结 Schema/API，不允许进入 Stage 4。
- 本结论仅是 P3-095 Rework，不代表 P3-094 其他已通过路径失效或真实用户数据已被访问。

## 需要 PM 决策

1. PM 验收并由用户采纳本 Rework 后，将 P1-01 回流 P3-094 同一能力包窄整改；不得创建无独立边界的微型替代任务。
2. 明确授权／安排精确清理 `/private/tmp/lifeos-p3-095-pycache`；不得扩大到其他临时目录。
3. P3-094 修复与 PM 验收后，必须创建另一全新隔离独立复评，完整重跑离线与 Chrome `file:` 动态闭环。

## 最终建议

结论为 **Rework**。当前不得采纳为独立 Pass，不得冻结 P3-094、关闭 R-0051、恢复工程基线或进入 Stage 4。

