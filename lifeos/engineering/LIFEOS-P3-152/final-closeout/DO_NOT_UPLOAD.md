# 不应上传清单（声明，未枚举或读取这些目标）

- 真实来源目录、原文、检索缓存、导入原件、导出.zip及任何用户附件；不得通过全盘/整个Documents目录打包获取。
- 真实健康库、conversation.sqlite、provider.sqlite、sources.sqlite及所有journal/WAL/SHM/备份/导出、真实runtime/source-engine-v1、锁文件、owner文件和个人派生数据。
- Keychain项、API Key、凭据密文及可用引用、解密材料、环境变量/本机凭据配置；不得上传真实内容hash作为替代。
- /private/tmp/lifeos-p3-152-health-conversation-v1 整个运行目录：真实App bundle、Cargo target、临时库/fixture、启动缓存均不纳入Git。最终App二进制只保留本机身份记录，不能把整个临时目录同步。
- 真实App截图/AX/正文/模型列表响应/HTTP原始错误/聊天正文、个人附件和系统诊断转储。
- 本机.Codex状态、工具会话、工作树Git内部metadata、其他任务目录和未列入清单的文件。

允许清单唯一PNG是版本内产品图标candidate/icons/icon.png，不是用户附件。代码中的固定授权路径字面量、合成测试数据及固定非内容启动收据属于工程材料，不能据此复制或探测对应真实目标。这里只列排除规则，没有读取上述对象。
