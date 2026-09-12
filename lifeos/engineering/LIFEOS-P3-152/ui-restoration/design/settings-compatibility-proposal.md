# 设置功能差异与最小兼容接线提案

只读依据：P3-142 candidate/src/runtime.rs 595起保存完整SettingsDto；P3-143 candidate/src/runtime.rs 174–221定义、767起校验、976起保存。142不是只有菜单；143也保留非DeepSeek本地配置，真实凭据/网络独立限定DeepSeek。

| 功能 | 142/143事实 | 152遗漏 |
|---|---|---|
| Cloud/Local、8/4 Provider、模型标签 | DTO校验、本地保存、重启恢复 | 仅DeepSeek modelId持久化，其他仅目录 |
| endpoint/localRuntime | 非DeepSeek固定offline目录、Local固定synthetic-local-runtime-v1 | 非敏感配置仍应可保存，不代表真实网络已实现 |
| routingPolicy四项 | 本地DTO持久化，执行受授权门禁 | 没有字段/接线 |
| fallback configured/providerId | DTO形状校验可保存，原UI默认无备用 | 未接线 |
| advanced自动覆盖/数值 | DTO保存，原UI多数为固定合成偏好 | 配置展示/保留遗漏，不得静默扩大真实请求预算 |
| capabilities | 合成registry metadata/状态 | 应保留层级，不能冒称全部真实可用 |
| credential/models/test/enable | 143真实限定DeepSeek，其他仅合成目录 | 保持152加密/逐次发送，禁网络tests/models/fallback |

## 待PM核对接口

现有command/version5新增get_ai_provider_settings/read_local_catalog {}和save_ai_provider_settings/save_local_catalog {requestId,expectedRevision,settings}。
settings沿143字段：version、primary(mode/providerId/modelLabel/endpointUrl/localRuntime)、routingPolicy(preferLocal/allowCloudSupplement/allowAutomaticFailover/preferFastResponse)、fallback(configured/providerId)、advanced(expanded/capabilityOverrides/temperature/maxOutputTokens/timeoutSeconds/contextWindow)。
严格固定目录和范围校验，拒绝未知字段、secret、任意endpoint。非敏感配置及CAS revision存已授权conversation.sqlite的sources固定_provider_catalog记录，不新建表/库/路径，不读旧真实配置。

分模式草稿隔离，保存才持久化并重启恢复。非DeepSeek主服务阻断真实发送，不偷偷继续DeepSeek；DeepSeek模型仍用原端口。预览/确认绑定catalogRevision，更改配置旧预览失效。加密凭据和Keychain不改。

本地偏好保存不授权执行测试连接、自动路由/fallback、其他Provider网络，也不改变固定请求预算。UI区分已保存设置和实际可执行能力。当前只有视觉选项与层级，尚未执行兼容接线，不宣称完整恢复。批准后同任务完成；真实App25223不关闭或覆盖。
