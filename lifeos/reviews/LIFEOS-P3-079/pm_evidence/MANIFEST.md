# LIFEOS-P3-079 PM Evidence Manifest

## PM 定向反例

- 核验日期：2026-08-21。
- 位置：新建系统临时副本；不修改候选源文件。
- 步骤：创建两个 current grant；以 `same-revoke-key` 撤回第一个，再以相同键撤回第二个。
- 结果：第一次返回 `revoked`；第二次错误返回 `ok: true`、`reason: idempotent_repeat`、所请求的第二个 permission ID，但该第二个 permission 的持久状态仍为 `current`。
- 判定：**P1**。冲突幂等键未被可见拒绝，且回执把未执行的第二次撤回表述为成功，违反任务卡“重复命令幂等且冲突可见”及 fail-closed／审计可信要求。

## 原 Evidence 完整性观察

- PM 在一次完整复跑中错误将 P3-079 runner 的输出写回工程侧 `evidence/`；该操作未触及候选源码或历史 P3-063／067／075／077 资产，但改变了 `self_check_results.json`、`self_check.log` 与 `operator_snapshot.json`，使提交时的工程 Evidence Manifest 不再匹配。
- 该失误已在 PM Review 透明记录，不将变动后的工程 Evidence 用作通过依据；原提交 Manifest 所列 hash 与当前文件的漂移记为 **P2 Evidence 完整性问题**。
- 后续获授权的同包 Rework 必须保留当前提交为只读历史，并在独立的新 Evidence 子目录重新生成 runner、逐项结果、日志、快照、hash 与 Manifest。

## 结论

P0=0、P1=1、P2=1、Unknown=0、Not Implemented=0。P3-079 判定 Rework；不得进入独立复评、冻结、风险关闭、基线恢复、真实能力或 Stage 4。
