# P3-057 攻击计划与独立性声明（封存）

- 任务：`LIFEOS-P3-057`
- 封存顺序：在读取 P3-044 的任务、交付物、PM Review、Evidence Manifest 或任何攻击 runner / 场景表之前创建。
- 适用边界：仅在本地隔离临时目录、合成 SQLite 数据库与只读候选 SQL 上进行防御性负向验证。

## 独立性声明

本文件由本次新建隔离 Codex 会话独立拟定。封存时，评审者尚未读取 P3-044 攻击资产的正文，也未导入、调用、复制或改写其中的函数、场景表、测试数据、预期值或结果。后续若读取 P3-044 历史资产，仅用于核验其输入 hash、整改声明和 Evidence 保留；本次 runner 保持独立实现，结果不以既有攻击 runner 的通过结果为证据。

## 预注册攻击矩阵

1. 建立候选 SQL 的全新 SQLite 合成库，并分别验证内存库与临时文件库。
2. 对 active Authorization 构造主键 `id` 与业务版本键 `(logical_key, version_no)` 的冲突：普通 `INSERT`、`INSERT OR REPLACE`、`REPLACE INTO`、以及带冲突目标的 `INSERT ... ON CONFLICT ... DO UPDATE` / `DO NOTHING`。
3. 构造 DELETE 后再 INSERT 的重建序列，分别考察相同 `id`、相同逻辑版本键和已有关联子记录时的安全结果。
4. 对 active 子表分别尝试 INSERT、UPDATE、DELETE、父键改绑和冲突替换，观察是否能绕开 audit / outbox / generation / 时间等必要关联约束。
5. 对父 Authorization 的状态、授权范围、时间、generation、撤回及关联安全包络字段做单字段与多字段更新，并覆盖 replace / upsert 语义。
6. 在八种 PRAGMA 组合（memory/file × foreign_keys ON/OFF × recursive_triggers ON/OFF）下逐一执行等价断言；所有测试在各自新建库中运行，避免状态泄漏。
7. 覆盖事务 rollback、嵌套保存点 rollback/release 及多行 `INSERT ... SELECT` / `UPDATE` 语义，验证失败是否原子且不可留下 active 旁路。
8. 另行执行明确合法路径：合法 successor 创建、合法 terminal 迁移及相应受控子记录写入，确认不存在过度阻断。

## 预注册判定规则

- 任何未经合法路径而得到或保留 active Authorization、可消费 active 子记录，或破坏父/子安全包络的结果记为 P1；若可越过明确用户授权 / 撤回的根本边界则记为 P0。
- 明确合同要求的可复核行为缺失、测试不能运行或证据 hash 不一致，至少记为 P2；若使独立结论不可成立，结论为 Blocked。
- 只有在全部预注册测试可复核、当前输入与历史保留证据一致且没有 P0/P1/明确合同 P2 时，才可给出 Pass；否则为 Rework 或 Blocked。

## 实现约束

- 新 runner 仅使用 Python 标准库 `sqlite3`、`hashlib`、`json`、`pathlib`、`tempfile` 和 `subprocess`（若需要），不会 import、调用或复制 P3-044 的攻击函数 / 场景表。
- 不修改候选 SQL、工程测试、历史 Evidence 或任何项目账本；所有新文件限于 P3-057 输出目录和本地预检目录。
