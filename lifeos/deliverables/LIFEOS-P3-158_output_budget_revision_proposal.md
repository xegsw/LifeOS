# P3-158 单次输出容量修订建议（未授权实施）

2026-09-10。状态：Proposal / Execution Not Authorized。本轮只核查代码、公开合成持久元数据及官方资料；未发业务/诊断模型请求，未改候选参数。停止继续压缩提示碰运气或让用户重试1024配置。

## 已确认事实与未知

App在coordination.rs组装请求时显式max_tokens=1024；该值来自本任务已批准合同的单次输出预算，不是DeepSeek账户余额或调用次数。供应商返回finish_reason=length后，transport严格映射provider_response_truncated；不是前端schema拒绝，也不是本地64KiB/16000字符上限（另有response_too_large）。本回合持久failed/modelCalls1/queryCalls0，Action和condition事件均0。新开发累计turn3/query1/model4；旧B14保持。收据evidence/D0672-B-schedule-truncation.json。

DeepSeek官方Chat Completions文档说明max_tokens是单次最大生成token数，可取1..393216，缺省值按模式不同；JSON输出在length时仍可能不完整。当前请求明确传1024，因此不会使用供应商缺省容量。官方也说明默认启用thinking且默认high；当前App未显式设置这些参数。只能据文档推断请求沿用默认，不能据此证明本次思考占满额度：旧usage/reasoning数量未保存，精确消耗、截断前正文均Unknown。没有账户余额读取，不归因用户欠费或用完额度。

来源：[官方请求参数](https://api-docs.deepseek.com/api/create-chat-completion/)、[思考模式](https://api-docs.deepseek.com/guides/thinking_mode/)。2026-09-10在线查阅。

## 一次明确的最小修订建议

仅将本任务v8 B公开合成请求的max_tokens由1024改为8192；不换deepseek-v4-pro、不增加thinking/reasoning_effort等模式参数。8192是建议的有界工程容量，不是测得的“绝对最小值”或保证成功；目前无历史token数据证明任何精确最小值。候选含引用、跨度、条件和一项Action，其JSON输出需要容量余量，1024又须承担该请求的整体生成上限。停止无证据地逐级自动加码。

保持：每回合最多2次模型、1次公开fixture查询、1个最终事务/至多1项Action；开发8/8/16、未见4/4/8及旧历史计数不变；个人披露4096 UTF8字节、请求体24576字节、响应体65536字节/正文16000字符限制和闭合schema不变。连接15秒、请求60秒、累计活动180秒及5分钟预览TTL不变。增容量不延长时限，达到任一上限仍失败关闭；不拼补半JSON、不用截断候选执行、不自动重发，不提高披露量。若8192仍length/超时/超大，保留具体失败及安全元数据，再基于证据决定，不自动升至模型最大容量。

建议同次纳入有限非内容诊断：仅对新请求记录请求max_tokens、finish_reason固定枚举、供应商usage整数（缺失为Unknown）和是否存在reasoning_content的布尔值；不保存reasoning正文/原始错误body/Key/真实文本及hash。不追溯补造旧请求。诊断由现有Host按模型子请求ID绑定，不能成为模型权限或新自动请求。

## 费用与验收边界

按当前官方V4-Pro输出峰/谷价3.96/1.98美元每百万token，8192输出token的费用上限约0.03244/0.01622美元每次，实际按已生成量收费；同回合2次约0.06488/0.03244美元。以上仅输出部分，不含输入费用、汇率或未来调价。当前新增额度已用4模型、剩余最多20模型；若未来全部用满8192，输出部分合计最多约0.64881美元（按峰价），不代表授权自动跑20次。较1024是单次输出费用上限8倍，并非每次必然多花8倍。价格来源：[官方价格表](https://api-docs.deepseek.com/quick_start/pricing/)。

实施前需要用户采纳这一精确合同差异；PM汇总一次批准即可。获准后做离线请求构造/上限/截断失败关闭/诊断不含内容测试，保持同签名身份生成新包及新Manifest；准备必要新开发回合预览，仍由用户亲点每次模型发送。旧失败计数与Evidence保留，不把历史改成功。未见集仍待开发稳定固定候选后由PM提供；C/真实接口/旧157均不开放。
