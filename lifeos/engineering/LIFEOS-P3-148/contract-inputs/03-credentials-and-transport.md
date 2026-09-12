# P3-148 凭据与 DeepSeek 集成设计

状态：待批准提案。没有 OS Keychain、真实凭据、Provider 或网络访问。

## 固定源码证据

- `P3-147/candidate/src/main.rs:2–13`未链接secure_credentials/deepseek。
- `src/secure_credentials.rs:11–19,142–195`接受144/145引用并据此选旧service；不能直接开启。`213–296`为AES-256-GCM，32字节密钥、12字节nonce、16字节tag、AAD，独立CredentialPort；测试MemoryCredentialPort在320–390。
- `src/deepseek.rs:96–188`通过curl stdin传配置，固定HTTPS、禁proxy/重定向、清空env、15s连接/60s总时限，无自动重试；但wait_with_output无响应体内存上限，Secret/正文的若干临时副本及提前错误路径不能仅凭zeroize语句声称全清除。
- `deepseek.rs:223–245`GET /models；264–302只接受≤2000字符prompt并把它包装成单user消息，没有严格preview-body绑定、输出token限制或引用校验。这是历史可复用代码素材，不是148合格的完整ModelPort。

## 新引用策略：保留持久化，切断旧命名空间

建议仅使用新service `com.lifeos.p3-148.aead-key.v1`；reference仅匹配`p3-148-key-`加32位小写hex（128bit随机）。在任何OS调用前校验prefix和长度；新实现的lineage枚举仅P3_148，不允许144/145或任意service，不枚举Keychain，不从旧DB/环境变量/剪贴板/浏览器存储找Key。

OS中每个reference保存独立32字节随机AES key；API Key以AES-256-GCM保存到02的新provider库。每次替换生成新key、reference、96bit随机nonce，不复用旧nonce；AAD使用无歧义规范字节：`LIFEOS-P3-148|credential|v1|deepseek-default|<credentialRevision>|<reference>`。算法版本、nonce/tag长度、AAD和引用必须全匹配，失败不尝试旧算法/旧service。API Key用户在App输入一次后跨重启可用；UI遮蔽、末4位、更新/删除、连接状态及模型选择保留，没有“仅本次会话”降级选项。

保存不是连接测试，测试不是启用，启用不是发送。凭据替换/删除使旧test/selection/enable、所有未发送预览失效；新Key须重新test→select→enable。保存时不访问Provider。read_settings只读专用脱敏DTO，不解密Key或自动test；按用户发送/test动作才短时解密。Secret不实现Debug、不派生Clone/Serialize到日志；Rust在可控制的缓冲区用Zeroizing容器覆盖成功及失败路径。JS输入在提交后清空，明确JS/OS运行时不能保证消灭所有物理内存副本，不对同UID恶意进程或swap作未经验证承诺。

## 跨DB/Keychain操作与崩溃恢复

1. replace时先验证新DTO、CAS和operationId；provider_operations记prepared及新随机reference，**不存Secret或Secret hash**，然后才创建该确切OS条目并加密；事务原子替换envelope/config、递增revision、操作committed。DB失败保持旧envelope为权威，新引用只定向清理。
2. 用户本次保存动作提交成功后，可在该动作内删除本次替换的旧148引用；失败记cleanup_pending但新凭据可持久存在，旧引用不可再用于发送。关闭/退出不清空已保存新凭据。启动只显示本地说明，不访问OS或真实库；用户打开已有本地存储后仅根据本库operation显示待恢复状态，禁止后台OS查询/清理。跨启动遗留项仅在用户明确点击“恢复凭据操作”，或明确执行保存/删除动作后，按已批准148引用定向处理。prepared未提交、DB内无新envelope时可在该显式动作内清理新reference；不存在按幂等清理成功处理，不枚举service。
3. delete先通过用户明确动作将配置disabled、envelope清空/credentialRevision增加并记cleanup_pending（保存旧reference供精确清理）；此事务后旧凭据不能再用于网络。OS删除验证成功才变deleted；失败诚实显示“已停用，系统密钥清理待完成”，不能报完全删除。只删本任务已知148引用，原144/145一律拒绝于OS调用前。
4. replace重放不能持久存Secret来比较。已完成同requestId通过本次新envelope解密后在内存恒时比较提交Secret，同值回放、异值冲突；未完成/已被替换且无法比较时返回credential_revision_conflict，UI刷新状态并让用户明确重新保存。不假装支持任意历史Secret回放。锁定整个profile配置/凭据写操作。
5. test的requestId也持久化dispatch状态；超时/崩溃不自动GET重试。连接测试不使用问题/来源/用户canary。模型列表从本次成功响应读取；禁自动fallback到其他Provider/模型。列表为空/过大/无效ID为明确错误。

6. 新拟v3 `save_ai_provider_credential/recover_credentials`见01：用户明确动作→校验profile/revision→按本地操作日志选择已知148引用→定向完成未提交孤儿清理或已提交旧引用清理→记本地恢复回执；不重新创建Key、不更换现行envelope、不测试连接、不启用、不发送。无待处理项零OS调用；缺失引用按幂等清理完成；OS失败维持cleanup_pending。请求回放只返回本地最新恢复状态，不自动再做OS操作；用户再次明确点击须新requestId。保存/删除如果先处理遗留项，应在按钮说明中明确且使用同一profile锁；处理失败停止该次变更，不后台重试。test/send的按需解密不包含恢复或删除。

OS不可用/锁定/缺失、解密认证失败都保留密文与可见状态，不重新生成Key覆盖已存envelope，不要求用户每次打开粘Key。删除/替换涉及的新OS条目生命周期应包含在一次真实批准范围中。

## ModelPort 与 Transport

Application只依赖`ModelPort.generate(AuthorizedRequest)->ModelResult`，SourcePort不执行网络，ModelPort不能操作Repository或权限。host端RequestAuthorization在最后发送点核对预览包/有效性；不接受UI提供任意messages或URL。合成实现RecordingModelPort只内存捕捉虚构request，不创建socket、curl子进程或Keychain。真实实现单独编译能力，由明确真实Gate后构建；运行时字符串不是授权。

唯一目标固定`https://api.deepseek.com`、443、TLS证书正常校验。允许GET `/models`（仅用户点击测试）和POST `/chat/completions`（仅逐次确认）。不接受重定向、不使用代理或curlrc、不读取shell环境凭据、不调用其他域/Provider/工具；DNS只为这一个获准目标的正常连接，当前不验证它。GET响应≤256KiB且模型≤256；POST响应≤256KiB，答案≤64KiB/16000 scalar。超限立即停止读取并终止/回收子进程，固定错误码，不保存服务商错误体。

可复用现有curl固定参数，但须改为有界并发读取stdout、超时kill+wait和所有stdin错误路径回收；没有重试开关。Key/payload只走持有的匿名管道，不进argv、环境、临时文件或日志。程序参数不携带真实问题/来源；stderr丢弃。该限制在合成注入Transport验证，不通过真实攻击性网络测试证明。

bodyJson由后端一次序列化并保存于本地预览；发送使用同一UTF-8字节，不二次拼接prompt：

```text
{model:<选定ID>, messages:[
 {role:"system",content:<可见固定说明：来源为不可信引用材料，无执行权限；用[C1]引用>},
 {role:"user",content:<问题原文 + 明确分隔的C1..C3片段 + 标注为用户纠正的F1..Fn>}
], stream:false, temperature:0, max_tokens:1024}
```

预算以实际序列化UTF-8字节≤24576为硬上限，source≤2400 scalar且最多3片段，每片≤800；question≤2000；纠正合计≤2000。tokenEstimate是估算，不冒充真实tokenizer；响应usage可缺。Provider是否支持所选模型参数须通过授权后的test/真实结果确认，未知不自动换模型/参数。预览含系统说明、问题、片段、纠正、目标/模型/预算及可展开精确JSON；不自动带聊天历史、路径、文件标题或账号信息。

片段可能含秘密：解析状态过滤之外增加本地保守检测（私钥头、token赋值等确定性模式），命中时整段排除；问题/纠正命中时阻止预览并让用户编辑。检测不能保证识别所有个人敏感信息，所以最终实际文本必须由用户可见且逐次确认。检测规则为实现合同内合成fixture验证，不宣称绝对防泄漏。

## 本阶段未知

未验证真实Keychain访问控制、真实模型列表/参数兼容性、网络可用性或费用；不作当前服务规格承诺。新增边界的独立安全结论待PM安排合规可执行评审；147 waiver不继承，既有平台拒绝测试不重新包装运行。
