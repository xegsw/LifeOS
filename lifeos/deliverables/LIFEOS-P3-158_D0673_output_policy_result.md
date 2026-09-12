# P3-158 D0673 输出配置增量

状态：Partial / Closure Cycle；Codex工程自检通过，在线语义待用户确认发送及实际结果，未声明任务完成。无需新增范围决策；最终验收仍交PM，独立评审暂停。

事实：截图中dto_rejected对应已修复的前端失败终态展示问题；当前实际App展示原始provider_response_truncated。原失败保留且计数不回退。

仅v8 online-synthetic请求省略max_tokens，离线保留1024；model仍deepseek-v4-pro，未添加thinking或reasoning_effort。当前官方文档规定缺省为非思考8K、思考64K（max effort128K），默认思考enabled/high。因此本请求采用厂商默认思考输出容量，未固定8192或最大393216。
来源（2026-09-10核验）：https://api-docs.deepseek.com/api/create-chat-completion/ 。并不保证不再截断；请求60秒、活动180秒、响应体65536字节、文本16000字符与字段限制均保留。思考文本也占响应体时仍可能达到解析边界，届时报告实际错误，不自动扩容。

诊断只保存输出参数/缺省标记、固定finish_reason枚举及有界usage整数，缺失为Unknown；未知字符串归一化，不记录原始响应、思考文本、凭据或真实内容。截断仍失败关闭，无Action，重复确认不再次发送。

验证：完整Rust190通过后增加一项网关元数据/重复确认测试，最终D0673定向4项通过；不是声称全量191项重跑。实际IPC7项、前端回执20项及Flow竞态检查通过。在线目标离线构建与同D0672身份完整包严格签名通过；未重复无关历史重建。候选182文件与构建身份逐文件零差异。

当前App：/private/tmp/lifeos-p3-158-main-chain-v1/build/signing-v1/D0673/LifeOS P3-158 Online Test.app，直接启动PID20703，CUA绑定此精确App显示Online Synthetic窗口及tauri页面；CUA不暴露原始AX PID，不夸大绑定证据。未访问157或C。

公开合成日程新预览已准备，模型请求字段messages/model/response_format/stream，请求3987字节，无max_tokens或思考覆盖；本回合模型0/查询0，Agent模型确认0。新开发累计turn4/query1/model4，未见0，旧B14保持。窗口等待用户点击“确认发送给DeepSeek”，后续查询结果的第二次发送也须用户确认。预览5分钟过期后需刷新，不视为发送授权。

证据：evidence/D0673-preview.json、D0673-build-identity.json、D0673-launch.json、D0673-signing.log、D0673-checks.log、D0673-metadata-final-checks.log；完整回归D0670-run-20260910T123438625005，最终定向D0670-run-20260910T123610417673。增量Manifest为evidence/D0673-increment-manifest.json；包Manifest位于上述D0673阶段目录manifest.json。

复跑入口：tools/run_v8_checks.py --steps build,rust,coordination-ipc,coordination-receipt,flow-races；定向可加--rust-filter d0673。tools/package_D0673.py默认仅计划，签名执行须同一已授权精确身份并选新独占build-tag，不能覆盖历史包。
