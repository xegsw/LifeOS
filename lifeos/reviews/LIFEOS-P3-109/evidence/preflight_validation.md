# P3-109 启动前 Evidence 自检

- 范围：仅检查本轮已生成的静态 Evidence；不执行 candidate runner、build、bundle、app 或 fixture。
- 方法：Python 标准库 JSON／SHA-256／AST 和 `lstat` 等价存在性检查，均为只读。
- 结果：
  - `STATIC_EVIDENCE_VALID=PASS`
  - `TEMP_PATHS_ABSENT=14/14`
  - `RUNNER_PARSE=PASS`

自检重新计算了六张固定图和两个历史输入的 SHA-256，重新核对 `test_design.md` hash 与 `read_order.json`，解析两份 JSON，并对未执行 runner 作 AST 语法解析。它不把任一矩阵 `status` 或 Markdown 结论作为候选通过输入。

这不是 ABF M-012 的 semantic verifier，也不是 M-005 build 结果；P3-109 在启动前路径冲突处停止，相关矩阵行保持未实施。
