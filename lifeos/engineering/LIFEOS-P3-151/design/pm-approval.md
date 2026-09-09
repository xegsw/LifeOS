# PM同范围批准记录

PM任务01a0290d-4255-7c52-8e62-6b888d2d678a已全文核对复用映射及IPC差异，批准151固定合成构建的5个既有IPC名称v4封闭分支、既有表schemaVersion4语义及所列预算。无需用户重复确认，不是旧冻结合同改变或真实权限扩展。

必须双侧校验领域/授权/有效期/packet/Adapter/取消/草稿revision；commit唯一refs为packet有效子集且Host重算3来源+2状态/记忆、4096bytes。snapshot总条数/字节有界且不通过snapshot绕过Health授权。原始表达从草稿取，commit.text只表示AI候选回答，绝不兼作原文。state/answerTo/corrects均从原文可核对，绑定当前问题和同域状态；sleep_hours明确用户自述，不替代传感器投影。无自动长期Memory，ignore/defer/沉默不写状态，重启抑制可复核。

Adapter前必须检查预算及packet仍有效：Application在选好上下文后再次调用prepare_turn（新requestId、同turn和draftRevision），Host复验并返回原packet，不静默换来源/Adapter；变更即拒绝，随后才调用本地ModelPort。commit继续复验，取消先于commit则无写入。新旧输入隔离沿148 serial语义。

实际测试覆盖raw重复未知、幂等冲突/同turn、取消竞态、纠正失效、预算、未授权与跨域伪造。TS业务/ModelPort、Host边界/持久化保持分层。离线未知问题诚实无答案，不声明通用推理或真实安全能力。继续实现和actual App验证，150真实窗口及所有真实库均禁止接触。
