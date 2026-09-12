# E02及有限合同补齐

PM已批准E02，准确任务卡和SHA256另存contract-inputs/E02-*。原五份封存输入、E01和T08失败源码链不修改。T08_BOUNDARY_REVIEW.md是修正前事实与提案，当前实现以本文及代码为准。

## 实现

UI将完整逻辑Request编码为UTF-8 Uint8Array。Host的ipc_boundary::dispatch_with为实际命令共享入口：Raw先检查32768字节上限、UTF-8、严格递归JSON、封闭外层/operation DTO，成功才调用业务分派。业务Request字段不变。32768为传输包上限，涵盖2000scalar的JSON转义开销；模型实际body仍受24576字节约束。新v3和第26发送拒绝Json旁路；旧v2对象与来源v1保留，非11项命令不能借Raw访问新operation。

凭据格式在业务存储前校验；Request去掉Debug派生；新分支错误统一封闭枚举，未知旧适配器错误不反射诊断内容。增加配置路径确定性过滤（.obsidian/.git/.config、.env、常见配置扩展名和已列配置JSON名），不宣称识别一切敏感内容。外链禁止错误按封存合同对齐external_targets_disabled。curl启动后异常退出统一结果未知，不把断网解释为安全可重试。

新的普通故障夹具证明反馈事务回滚、预览实际operation失效、相关纠正预算、分页/重启与受协调器约束的并发。测试私有ModelPort注入复用真实dispatch_using、COORDINATOR与send_handoff；生产公共dispatch固定None，不存在IPC/环境选择测试Port入口。provider生命周期的独立MemoryCredentialPort和故障点均cfg(test)，不进入App；不使用真实OS服务。

## 证据边界

`closure-rust-final-02.log`：35项通过、27个旧测试过滤；包括一个受控退出子进程辅助测试入口。`closure-restart-final.json`指向6组主集成、7组扩展和旧v2功能smoke。Raw入口包含19个批准operation/反馈分支的正例，以及缺字段/null/未知字段/混版本/整数等负例、Secret类型/长度拒绝；所有拒绝均在共享入口业务回调前。原Value消解测试只解释原缺陷，不冒充当前live攻击。

actual Tauri E02正常流程已在PID71919完成；后续有限修正的桌面PID73074完成保存失败后的准备故障恢复、失败/结果未知显示、HTML/图片纯文本、无效引用计数和新预览确认后的回答保存。GUI故障状态来自本任务虚构DB夹具，错误状态产生由独立Rust ModelPort用例支撑，未实际连接Provider。保存故障前后仅改本合成DB的临时故障触发器；触发器已移除，旧业务行和历史Evidence保留。

最新附加的Secret/错误边界修正已通过测试并构建，二进制d542d40e473b375f1bbb1405a6cf6d85adc03e46beb68adca584ca0e1d530139。尝试最终GUI时Mac再次锁屏；PID73403没有形成可用正GUI Evidence，已停止。其launch标签acceptednarrow仅历史文件标识，不代表Accepted/PM Pass。该锁屏检查点已保全。解锁后同一最终二进制由PID73617完成窄屏预览、合成确认、回答保存与Settings；PID73741完成桌面重启恢复与Settings，新回答对象跨进程一致。两个PID已停止，见evidence/final-gui-verification.json。工程侧补齐完成，待PM及独立安全评审。

live WebView负面注入、真实构建/DB/OS/网络及独立安全评审均未执行；不得改名重试平台已拒绝测试。当前不把工程测试或GUI组合证据写成这些未做关卡的通过。
