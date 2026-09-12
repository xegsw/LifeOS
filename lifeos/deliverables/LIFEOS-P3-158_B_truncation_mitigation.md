# P3-158 B输出截断定位与合同内缓解

状态：Partial，待真实请求验证，不宣称截断已解决。

唯一transport错误映射证明此前provider_response_truncated对应供应商finish_reason=length；本地大小超限是response_too_large，错误JSON为provider_protocol，空正文为provider_response_empty。旧响应未留token/思考元数据，因此思考输出占预算、供应商实际用量等原因Unknown，不补造原响应。

本轮只将通用v8提示去冗余，并要求query/action候选answerText为空、普通回答简短、仅输出选定候选JSON。不新增固定句式生产分支，不放宽schema、权限、截断守卫；max_tokens=1024、模型deepseek-v4-pro、每回合最多2模型及调用预算不变，未设置thinking参数。POLICY声明文本2792→2632 UTF8字节，不据字节数声称token用量或保证消除截断。

187 Rust、7实际IPC、20前端回执通过；额外离线分类测试覆盖length即便完整正文也拒绝、空/超大/错误JSON及正常stop区分，并确认请求额度/参数不变。工具verify_truncation_contract.py，日志evidence/D0672-truncation-contract.log。完整同身份签名通过，新包D0672-B-compact，实际PID18430。唯一候选代码变化为coordination.rs的POLICY，相对上个terminal包；新身份evidence/D0672-B-compact-build-identity.json，检查D0672-B-compact-checks.log。

已准备必要新回合，原失败不重发、不退额度；新开发turn2/8、query0/8、model1/16，旧B14/40保持，未见0。精确预览收据evidence/D0672-B-compact-preview.json。用户亲点后才能验证此缓解是否有效。若仍截断，继续保留失败，不盲循环；任何max_tokens/模型参数模式或预算变化先提精确差异。C/真实接口和157未触及。
