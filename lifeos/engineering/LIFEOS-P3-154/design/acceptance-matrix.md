# P3-154 Locked v1 逐行工程矩阵

状态：工程自检通过；ABF-10等待用户实际结果。独立评审暂停，不是Independent Pass。

|ABF|正路径|负路径/守卫|当前结论|
|---|---|---|---|
|01 完整累积|163完整文件、398历史文件复算；设置25/集成14/组合11|无文件删除、差异清单；14IPC保持|工程Pass|
|02 旧库兼容|旧152 owner/AAD/account/SQL保留；密文跨Port重开；现有真实库启动成功|缺根/缺库/错owner拒绝；来源缺表不迁移|工程Pass；未采真实内容|
|03 最小上下文|自动有限来源及状态；preview body与refs一致|权限/领域/预算3+2、4096字节、版本反例|工程Pass|
|04 追问生命周期|回答/忽略/暂缓30分钟/拒绝/重开，旧问题ID兼容|沉默不写；迟到/幂等/拒绝超过历史窗口|工程Pass|
|05 纠正时效|Closure-1状态/原文/替代有效来源；旧历史不覆盖|过期/撤权/墓碑、负数/小数/歧义|工程Pass|
|06 二次守卫|prepare/confirm/return检查；一次确认消费|令牌/过期/版本；late stale、失败不自动重发；mutation|工程Pass|
|07 凭据/Provider|原设置四阶段、持久加密/掩码、唯一DeepSeek|缺密钥0新增0删除；144格式0访问；Key回显mutation；real+driver构建拒绝|工程Pass；未操作真实Keychain|
|08 重启/模型|独立进程状态恢复/双离线Adapter；现有来源授权可重用|重启inflight=unknown不重发；无启动扫描/models调用|工程Pass，实际用户重启结果归ABF-10|
|09 完整App切换|实际完整controlled-real构建；旧152正常退出；新PID66104启动/激活|精确旧binary hash/单次launch claim/锁/根/Schema守卫|工程Pass；无真实GUI采集|
|10 实际用户闭环|已向用户发最小验证说明|只接受成功声明或固定错误码，禁止个人截图/正文|Pending，不能宣称真实闭环完成|

影响面：没有修改页面布局、CSS、Settings组件或对话渲染；App标题/标识更新。复用153六份合成native GUI及既有设置GUI；行为重新验证，不以CSS相同代替功能检查。本轮无受影响窄窗布局，未机械重拍。不是L3独立原生窗口证明。

正Evidence：evidence/regression（173项）；source-schema-pass.log（1项）；affected-final（86项重复受影响复跑，不叠加计数）；combined-final（11项重复，不叠加）；mutations（5/5被检出）；real-driver-negative；real-build/real-bundle/before-switch/normal-quit/launch/activation。

排除：initial-regression属于较早候选快照；source-schema.log/source-schema-retry.log/source-schema-final.log为独立子crate测试入口探索失败（历史子crate未携带父crate测试依赖），不作通过证明。最终通过由受控boundary-tests导出的内存Schema夹具及主crate测试完成，真实构建禁止boundary-tests。未修改历史以遮盖失败。
