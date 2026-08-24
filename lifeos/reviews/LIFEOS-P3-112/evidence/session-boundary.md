# LIFEOS-P3-112 会话边界检查

- ABF：`ABF-P3-112-v1`，Frozen；计算 SHA-256 与任务卡记录一致。
- 临时根 `/private/tmp/lifeos-p3-112-review-v1`：启动前不存在；未删除任何既有路径。
- 工作区存在 P3-111 相关未提交／未跟踪资产，视为被评审方只读输入；本评审不修改它们。
- Pilot-2：零路径查找、零 metadata、零打开、零读取、零 hash、零复制、零清理。
- 真实 app：零启动。
- 工程 verifier／mutation 源码和结果：在 test design 冻结前零读取／零导入／零执行。
