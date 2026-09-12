# P3-154 Closure-1：确认发送后失败的定向诊断

**Partial / 安全诊断增量已完成并切换，实际业务根因仍未知，ABF-10未通过。** Codex单Agent；L3；独立评审依用户例外暂停。用户只提供非内容事实：点击确认发送后报错。没有读取截图、个人问题、真实DB/日志/响应或Keychain，也没有真实重发。

## 已完成的排查

固定通用文案可由多个确认后分支触发，不能证明请求已到Provider。以下使用合成旧152兼容库、注入的CredentialPort和真实生产响应解析代码验证：

|分支|底层结果|模型调用/重放|
|---|---|---|
|确认前库锁|confirmation_storage_failed|0次、未消费令牌|
|凭据端口不可用|credential_unavailable|0次、旧密文字节不变|
|生产解析器收到合成非JSON/null/空content|provider_protocol或response_too_large|1次、重复确认及重启不重发|
|模型调用后本地库锁|response_storage_failed|1次、重启为outcome_unknown，不重发|
|结果事务写入失败|dispatch_outcome_unknown|1次、回滚，无半条回答，草稿保留|

令牌、来源/状态时效及模型/凭据版本变化沿原守卫测试。此前准备阶段旧库反例仍为历史参考，不再用作当前用户故障的主要解释。

## 修正与验证

补全确认后白名单错误码，在原状态栏显示固定阶段与code；Host仅将确认前与模型调用后两类存储错误区分，未改变发送、重试、事务或权限行为。原始异常message/body、未知code不显示、不记录。凭据失败不提示重置旧密文。没有改设置/UI设计、Schema、路径、导入、预算或重试权限。

将生产响应解析提取为无I/O函数供合成测试，解析行为不放宽；凭据失败注入仅cfg(test)，不暴露生产覆盖入口。100项受影响检查通过：Host39、披露28、Application集成14、连续性8、时效6、诊断UI5。3个mutation被检出：隐藏code、原始错误泄露、将调用后存储失败错标为调用前。完整真实版构建成功。

这些测试区分潜在分支，**不等于其中任何一个已被确认是用户根因**。实际固定code尚未知，不能将诊断文案修复宣称为真实故障修好。

## 当前App及历史

App：`/private/tmp/lifeos-p3-154-real-continuity-v1/LifeOS P3-154 C1 Confirm Diagnostic.app`。

Binary SHA256：`a2924b4cb326ae0a7b06feb423a79597be5a656fba96b25219107649ccbd946c`。

先核对旧C1 binary与实例身份，正常退出后单次启动本版并激活；精确PID与固定状态见evidence/launch.json。没有强杀、覆盖旧bundle、迁移、清理、重新导入或代点真实发送。所有历史App保留。

原P154的270项包、C1初诊断216项包及对应报告保持只读；本次在同一Closure内新增`lifeos/engineering/LIFEOS-P3-154/closure-1/confirmation-stage/`，完整165文件candidate、测试、逐行分支矩阵、Manifest及checkpoint。不是后继任务。

## 下一必要动作与判断

由于旧版未显示固定code且禁止读取真实日志，静态/合成不能唯一还原实际失败。需要用户在本版亲自阅读披露并确认一次，只反馈状态栏固定阶段＋错误码，或成功；不索取正文/截图/Key/原始响应。Agent不会自动发送。若返回具体code，继续本任务同范围根因修复；本包未收口业务失败。

当前执行侧计数：P0=0 / P1=1（真实用户失败未关闭）/ P2=0 / Unknown=1（实际底层分支）/ Not Implemented=0。独立评审暂停单列。需PM继续保持ABF-10未通过，并据固定code推进，当前无需新增权限或Key。

复跑：`python3 lifeos/engineering/LIFEOS-P3-154/closure-1/confirmation-stage/tools/rerun.py --affected`；校验同目录tools/verify.py。checkpoint.resume_from=fixed_post_confirmation_code。未提交/推送，不改PM账本/风险/冻结/Stage；无后台Agent读取或发送。
