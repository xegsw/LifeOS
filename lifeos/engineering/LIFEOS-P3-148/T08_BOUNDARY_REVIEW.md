# T08 框架解析边界与最小修正提案

状态：Closure Cycle；当前 T08 不满足合同。无需 Key，与锁屏无关。本文为工程事实及待 PM 决策提案，不是独立评审。

## 已确认事实

封存01第2节明确要求每层重复JSON键拒绝，禁止Value最后值覆盖。当前 source_ui.ts:6 使用 `invoke(command,{request})`，main.rs:25 直接接收 serde Request。

锁定依赖 Tauri 2.11.5 的两条 JSON 入口都提前消解业务对象重复键：custom protocol 在 `src/ipc/protocol.rs:527` 执行 `serde_json::from_slice::<serde_json::Value>`；postMessage 在同文件242行定义 `payload: Value`，294行反序列化 Message。serde_json 1.0.151 的 `value/de.rs:139–141` 对 map 执行 insert，后值覆盖前值。随后 Tauri `command.rs:97` 只从该 Value 取 request，再交给 Deserialize。应用此时无法恢复原始键序列。

新增 `strict_json::boundary_tests::p148_tauri_value_boundary_loses_duplicate_keys_before_request` 已离线运行：1通过，43过滤。四例覆盖 request 外包装、version、operation、payload 内字段重复。相同原始串被严格解析器拒绝，却能经框架所用 Value 解析、真实 InvokeBody::Json 和应用真实 Request 反序列化。重新序列化不能找回重复信息。

这证明缺陷可在锁定框架源码对应的解析原语中重现；**没有声称运行了实际 WebView 的原始 IPC 注入，也不是 T08 Pass**。普通测试只能暴露缺陷，不能在不修正入口的情况下补成满足合同。stdio不作为Tauri证据。源码绝对路径、行段、SHA256见 `evidence/t08-framework-source-chain.json`，执行结果见 `evidence/t08-framework-boundary.log`。新增内容只在cfg(test)，未改生产行为，也未重新构建/启动GUI。

## 需 PM 确认的最小 E02 提案（尚未实施）

保留26命令名、11项v3逻辑DTO、所有业务字段/错误码/表/权限。仅为这11项v3及第26发送入口明确二进制传输封装：前端把完整逻辑 Request 序列化为UTF-8字节，以 `Uint8Array` 调用既有 Tauri invoke；Host使用 `tauri::ipc::Request` 获取 `InvokeBody::Raw`，先逐层严格JSON解析，再反序列化现有 Request 并校验版本/operation，之后才进入原分派。

新v3/发送入口拒绝普通 InvokeBody::Json，禁止其绕过严格解析；非UTF-8/非对象/缺字段仍以现有固定错误拒绝。保留旧v2与来源v1对象通道及离线边界。Tauri已提供 Raw 分支（protocol.rs:522）和 Request::body（ipc/mod.rs:155），不需要新增协议、命令或修改框架依赖。若平台退回JSON通道，应失败关闭；不得自动退回不严格的业务JSON解析。

这改变传输封装，按PM当前指示先交PM确认；不修改原五份封存材料，不以降标替代。批准后应另存E02及摘要，补普通Raw入口正负测试、旧通道不旁路及副作用零计数，再完成同一候选实际Tauri正常调用验证。新的入口缺陷失败证据保留，受影响构建与GUI绑定更新，无关历史阶段不机械重跑。

本轮没有访问真实根/DB/OS凭据、发起网络或运行此前被平台拒绝的测试。真实Gate继续暂停。
