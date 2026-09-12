# P3-152 最小 IPC/存储差异提案

保留151 version4 draft_turn/prepare_turn/conversation_snapshot/clarification_decision/local state commit的严格Raw边界；合成离线回答模式继续明确synthetic。新增受控发送复用148既有command名字，version5用于152绑定语义，拒绝未知/重复字段/null及超限。

- resolve_request_context / prepare_disclosure：requestId,turnId,packetId,modelId,inputRefs。Host从保存的draft与获准packet重建实际body；只接受唯一、同版本、同授权且预算内refs。返回previewId、revision、confirmationToken、recipient、modelId、instructions、question、items、exactBody、expiresAt；无需用户手工拼装。create/update不发送。
- send_source_ai_request / confirm_send：requestId,previewId,expectedPreviewRevision,confirmationToken。Host再次验证草稿/模型/凭据revision/权限/健康只读来源/上下文、单次原子消费；再进入ModelPort.generate_with_receipt。在App用户点击后才可调用，Agent绝不操作real确认。
- resolve_request_context / cancel_preview：requestId,previewId。未交付前禁止该preview进入Adapter；已交付则状态准确表示停止等待/不保证远端撤销。新问题不被旧结果覆盖。
- get_ai_provider_settings / read_local：仅本地配置；save_ai_provider_settings / select_model（requestId,modelId）或save_credential（requestId,expectedCredentialRevision,apiKey）、delete_credential（requestId,expectedCredentialRevision）。user-local读取/选择不联网，不调用test/models；凭据路径授权到位才可启用real。
- 151既有draft/edit/cancel和clarification身份继续复用；本地能澄清则不创建网络preview。commit_turn不得接收客户端伪造真实模型answer；真实answer仅ModelPort返回后Host写入。

存储沿用records/states/memories/drafts/questions/packets/derivations/feedback/sources/requests/audit/meta。新增preview/dispatch JSON kind/version，不新增核心表/实体；provider独立加密配置沿148两表。网络请求的确认/尝试状态在packets原子记录，失败手动重试生成新preview且重新确认，重复confirm只返回原状态，不二次send。启动遇dispatching只记结果未知，不重发。真实正文不进入日志或Evidence/hash，内部绑定比较实际不可变内容，不导出内容摘要。

合成测试允许Fake ModelPort捕获确切请求用于相等性测试；真实构建此capture接口不可用。错误必须固定分类，不包含服务端body/Key；无后台/重定向/fallback或models调用。待PM批准本差异后实现路由；原151关键合同保持只读。
