# Attempt-8 PM 操作日志

- 复算 attempt-8 提交 Manifest 16 项、源码 5 项、历史只读资产 155 项，写入 PM 结论前全部一致。
- 使用提交 runner 在全新 `/private/tmp/lifeos-p3-094-attempt-8-*` 固定非敏感夹具中复跑；attempt-8 18 PASS / 0 FAIL，attempt-6 回归 19 PASS / 0 FAIL。
- 独立创建两个固定 SQLite 反例：同列同类型但缺全部约束并含 `source=external_fixture`；仅缺 `idem_key UNIQUE`。两者均被成功 render，结果为 0 PASS / 2 FAIL。
- 反例 DB bytes 均保持不变；第一个新页面包含固定夹具并声称“来源：本地捕获”，证明错误接受及来源误标。
- PM 复跑和反例均未读取真实个人文件、既有个人 DB、凭据或外部目标，未联网；全部 `/private/tmp` 夹具已精确清理。
- PM 未修改工程代码或工程 Evidence。本轮仅写 PM Review、PM Evidence 和授权的项目账本。
- 本地模型预检因本轮属于本地 DB Schema 完整性、来源标注和页面生命周期的高风险最终判断而跳过。
