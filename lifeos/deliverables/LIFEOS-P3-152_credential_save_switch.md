# P3-152 API Key 修复版安全切换

状态：切换完成，任务仍待用户真实保存验证与 PM 验收，非 Complete。独立评审仍暂停。

用户明确允许正常关闭当前旧版并打开修复版、保留草稿且不清理数据凭据；授权由 PM 任务 01a0290d-4255-7c52-8e62-6b888d2d678a 转达。

NSRunningApplication 实时核对旧实例路径及 bundle id 得到 PID 39248，再次核对后调用正常 terminate，收到 exited=true。无强杀、锁文件删除、真实 AX/截图或正文读取。未直接验证草稿正文，未执行清理或覆盖。

固定修复版 binary SHA256 7f61c4919ec6728d806322221f34c0c83bcf723365c0563d9d879f4f34b01ccf 校验通过。旧实例退出且精确实例清单为空后启动一次，PID 40787，固定启动状态 controlled_conversation_started，NSRunningApplication 路径与 bundle id 再核对，activation_requested=true。候选代码在此启动状态前必须取得共享 conversation.lock 的排他锁，未绕过门禁。

窗口名（由匹配二进制的候选代码确认，未读真实 AX）：LifeOS P3-152 - Controlled Conversation。

修复版路径：/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Credential Fix.app。

用户可在 设置 → 模型设置 手动填写 Key 并保存。Agent 未代保存 Key、发送、扫描或导入；真实 Keychain/DB 内容没有进入 Evidence。若失败只需固定错误码，无需 Key 正文。

旧修复包184项 Manifest 校验通过，原包未修改。本切换 receipt 独立保留于本目录 evidence/。角色：Codex 执行；PM 待确认用户结果。无需新的切换授权。

Receipt目录：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-152/credential-save-switch-v1
