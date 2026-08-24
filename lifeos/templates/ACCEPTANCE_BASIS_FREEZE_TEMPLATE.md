# LifeOS Acceptance Basis Freeze Template

## 冻结信息

- 任务 ID：
- ABF ID／版本：
- 生效决策：
- 冻结时间：
- ABF 文件 SHA-256：由 PM 冻结后记录在任务卡／决策日志或外部 Manifest；本文件不得使用自指 hash。
- 状态：Draft / Frozen / Superseded
- 本文件是否在专项会话开始前冻结：Yes / No

## 本轮唯一用户结果

- 要完成的单一结果：
- 明确不冻结的产品需求：
- 明确非范围：

## 授权和能力边界

- 允许目录：
- 允许数据与夹具：
- 允许入口／接口：
- 允许工具／环境：
- 严格只读资产：
- 禁止能力与外部目标：
- 投递前额外用户确认：

## 引用的 L1 长期原则

逐项引用 `lifeos/ACCEPTANCE_GOVERNANCE.md` 的 L1 条款，并说明本任务如何适用。

## 冻结不变量

| ID | 不变量 | 严重级别 | 可观察通过条件 | 失败后置状态 |
|---|---|---|---|---|
| ABF-I-01 |  |  |  |  |

## 冻结验收矩阵

每行必须独立创建夹具、执行动作、断言结果并生成 Evidence；不得由总测试结果批量映射。

| 行 ID | 入口 | 前置状态 | 操作／失败点 | 预期结果 | 必须保持不变 | 测试 ID | Evidence |
|---|---|---|---|---|---|---|---|
| ABF-M-001 |  |  |  |  |  |  |  |

## Evidence 合同

- 可运行 runner／测试源码：
- 逐行结构化结果：
- before／after 状态：
- 日志／快照：
- source／history hash：
- Manifest：
- 复跑命令：
- 临时清理：

## 计数与 Pass 公式

- P0：
- P1：
- P2：
- Unknown：
- Not Implemented：
- Pass 公式：
- 允许的 N/A：

## Rework 预算与退出规则

- 正式 Rework 上限：2。
- 当前正式 Rework 次数：0。
- 同任务 Rework 条件：
- 必须新建任务条件：引用 `lifeos/ACCEPTANCE_GOVERNANCE.md`，并列本任务额外触发器。
- Blocked 条件：

## 候选基线与只读保全

- 候选输入 hash／Manifest：
- 历史只读 hash／Manifest：
- 允许发生变化的文件：

## 启动前质疑窗口

- 执行方是否提出歧义：
- PM 处理：
- 最终冻结版本：
- 专项会话开始后不得实质修改本 ABF；如需修改，当前任务关闭并新建任务。
