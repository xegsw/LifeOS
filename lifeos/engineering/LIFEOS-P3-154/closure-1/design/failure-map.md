# P3-154 Closure-1 固定错误分支定位

原UI的`errorText`只映射部分code，其余返回完全相同的“操作未完成，草稿已保留。”。`ControlledFlow.prepare`与`confirm`的catch都转failed，failed统一展示“重新准备披露”。这两条UI文本不能确定失败发生于网络，也不能确定实际执行了确认。

|执行位置|合成复现/已知分支|修复前显示|
|---|---|---|
|prepare_turn→health_source→Reader|已有合成健康库存在journal→readonly_sidecar_required；来源字节不变|通用提示|
|prepare_turn→health_source→Reader|合成旧库缺states表→store_operation_failed；不建表/迁移|通用提示|
|commit_turn|clarification_rejected/state_claim_rejected/real_answer_requires_model_port|通用提示|
|Application本地Adapter|adapter_rejected|通用提示|
|confirm_send→响应解析|provider_protocol/response_too_large|通用提示|

实际用户底层code尚未取得；表中是区分反例，不认定某个等于用户根因。不读取真实DB/日志/正文来缩小范围，不重放网络。

最小诊断修复：仅已有状态栏显示固定阶段与白名单错误码。错误对象的message/body/未知code不进入展示或Evidence；未改变重试/网络/DB/设置/布局/CSS。已知真实权限与失败关闭守卫不放宽。为测试生产本地提交策略，私有commit_with_policy接受内部编译模式，公开IPC和生产路径/时钟接口不变；合成测试走true策略并保留旧152 marker/旧问题ID，完整提交与重启通过，任意离线模型回答仍拒绝。

95项受影响检查：Host39（新增4）、披露23、集成14、连续性8、时效6、诊断5。2个诊断mutation检出（隐藏错误码、泄漏raw message）。首次旧Schema测试错误地预期database_unavailable，实际Host适配层固定映射store_operation_failed；日志保留，不作为正证据。原子crate等原包历史全部保持只读。

仍待非内容事实：披露前/确认后阶段，以及修复版显示的固定code。真正业务失败尚未宣称关闭；ABF-10未通过。
