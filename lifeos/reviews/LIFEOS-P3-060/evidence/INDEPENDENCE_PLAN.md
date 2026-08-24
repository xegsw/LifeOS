# LIFEOS-P3-060 独立性声明与反例计划

封存时间：2026-08-21（在读取 P3-039 / P3-058 历史攻击实现之前）

## 独立性声明

本任务由新的隔离 Codex 会话执行。计划形成后，才会读取历史 Review、Evidence 和攻击实现；本任务的 runner 不会 import、调用、复制 P3-039 或 P3-058 的攻击函数、场景表或结构化结果。历史材料仅用于核对谱系、hash 和结论差异，不能作为本次结论的唯一证据。

本任务只写入 `lifeos/reviews/LIFEOS-P3-060/`、`lifeos/deliverables/`、`lifeos/local_prechecks/` 和系统临时目录；候选 SQL、P3-031 历史 Evidence、历史交付物/评审、工程代码及项目账本保持只读。

## 自建最小反例计划

以全新 Python/SQLite runner 在临时目录创建每个数据库，不复用历史攻击脚本。每个组合运行下列场景，并记录预期阻断、实际事务结果和关键行状态：

1. Tombstone generation 降级：已有高 generation Tombstone 后尝试更低 generation successor。
2. DELETE/reinsert：删除 Tombstone 后以同身份重新插入 active Authorization。
3. 普通 Tombstone 改绑：将普通 Tombstone 改为 Authorization Tombstone，或以改绑字段伪造其身份。
4. 伪造 generation / command / reason / time：尝试伪造 Authorization Tombstone 所需审计字段或非单调 generation。
5. 合法单调 successor：以完整审计字段创建 generation 增长的 successor，验证正向路径。
6. 事务回滚与保存点：在显式事务和 savepoint 内执行受阻写入，验证失败不会留下残留写入，且回滚后可继续受控写入。

配置矩阵：`:memory:` 与临时 file DB；每种均覆盖 `PRAGMA foreign_keys` ON/OFF 与 `PRAGMA recursive_triggers` ON/OFF，共 8 个配置。无法运行或无法判定的情形会明确标为 `Unknown` 或 `Not Implemented`，不静默省略。

## 判定约束

任何 P0/P1、明确合同 P2 bypass、Unknown、Not Implemented、hash/Evidence 冲突、历史保留失败或独立性不足，均停止扩大结论并判为 Rework 或 Blocked。即使所有测试通过，本包也只作为 PM 对 R-0043 的后续风险决策输入，不关闭或重开风险，不冻结资产或工程基线。
