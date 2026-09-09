# LIFEOS-P3-147｜固定本地来源 App 工程交付

## 当前结论

**本地功能 User Verified，工程侧元数据收尾完成。** PM先核对固定候选e4b4aed9140e05541a23e7f871b89cfda8e71b85、已交付App二进制及签名，再打开专用App。用户报告“导入完成了”，随后对Memory检索/打开原文、关闭重开重新连接与无重复观察回复“正常”。本结论来自用户在PM会话中的陈述，不是Agent独立检查真实DB、全库完整性或实际格式覆盖。

本轮仅读取PM非内容回执并更新报告/终局元数据；代码与已交付App不变。未重跑App、未读取/探测真实源或DB、未截图/AX采集、未获取真实内容hash，未清理或退出用户App。其当前进程状态未检查。

**User-directed review waiver / No Independent Pass**。原IR-P0-147-001、工程修正、Rework与独立未完成8行保留；未运行或改写被平台拦截的安全评审。普通验证不等于独立通过、风险关闭、L3终局或Stage提升。

## 已交付操作说明（供用户日常使用，不要求重做亲验）

1. 打开 /private/tmp/lifeos-p3-147-obsidian-source-v1/LifeOS Local Source.app。窗口标题为“LifeOS · 本地来源”；不要使用标题带“合成离线”的演练App。
2. 初始显示Settings的来源说明。确认界面显示固定来源 /Users/xxe/IT-obstain 和已批准保存位置后，点击“连接此目录”。打开App和查看说明不探测来源、不建数据库。
3. 点击后才初始化或打开专用存储并自动导入。查看已发现/已处理/解析/未解析/失败/待处理计数；可暂停、继续、取消和手动刷新。首次处理未结束或存在未解析项时，不把计数解读为全部正文可用。
4. Memory → 本地检索 → 输入用户自己的关键词 → 查看原文依据。真实标题、正文、路径清单、截图或AX内容不发送给Agent。
5. 重启App后仍需点击“连接此目录”才打开已有数据和恢复来源；原暂停状态保留，点击“继续”才恢复处理。“断开来源”保留历史并退出活跃检索，不物理清理。

若报告保存位置所有权/权限不符、非任务资产或数据库不可用，停止该次接入，不覆盖、不补造所有权、不迁移。用户可向PM反馈非内容状态、计数、错误类别和版本，无需提供正文或截图。无需Key。

## 实现与保存范围

source-pilot-1只绑定唯一只读来源与唯一输出根 /Users/xxe/Documents/LifeOS-Source-Pilot-1。capture.sqlite为新非加密SQLite；artifacts为原件缓存，.runtime为解析临时文件。目录0700、文件0600；权限不等于加密。既有非任务资产拒绝接管；真实源不写标记、索引、缓存或日志。两个合成profile保持原根不变，仍为25IPC和原payload；真实profile仅将现有连接命令映射固定来源，UI不能提交任意路径。

真实启动跳过仓储open和worker自动恢复，UI初始化与说明开关零IPC。连接动作后启用进程内访问状态，检查固定源与持有FD，初始化/打开受控仓储；重启访问状态复位。现有仓储为paused时恢复显示但不自动继续。输出采用原FD链创建/读取/发布；新增初始化使用相对目录FD排他创建，不chmod已有目录。SQLite主文件预先FD创建/验证，SQLite使用NOFOLLOW；不承诺对任意同UID并发进程有跨文件系统/SQLite全局原子事务。

真实版本关闭repository-stdio内容通道、stdout/stderr与panic文本输出、开发者工具，WebView使用非持久会话。解析器通过stdin/stdout FD交换内容，stderr丢弃，argv只有白名单格式token；解析/别名helper随App打包。没有真实正文写入工程日志/Evidence的通道被新增。网页和目录外文件授权命令在真实profile直接拒绝；Provider/Keychain和网络禁用，未接旧库、未迁移或清理。

配置仍受限，不进入普通记忆/模型上下文。Markdown/UTF-8/HTML/PDF/DOCX等既有解析范围与预算保留；图片、音视频、二进制等保留原件并显示未解析，不启用OCR/转写。没有将来源全文送到模型，也不宣称通用AI理解。

## 验证与证据

此前工程普通验证共10组：合成UI/导入生命周期6组、真实入口UI合成stub3组、source-pilot-1分支的Rust普通生命周期1组。Rust测试仅在cfg(test)把源和输出绑定工程fixtures，实际真实路径零接触；覆盖点击初始化、6文件导入、capture.sqlite权限、暂停/重新打开/继续、检索、刷新和断开。23个其他Rust测试被过滤，未运行安全反例或独立review runner。

最终普通结果：evidence/checks-20260908T072044412392Z/；UI生成：checks-20260908T071937035501Z/；Rust真实分支合成测试：pilot-normal-20260908T072104Z/。中间UI stub语法失败及修正记录保留，不计为最终通过。

合成App最终binary ac9c5c381635abc7a9260060835b5f7bd7aec0407bacbeb51a2554f3484d9c9b。实际桌面PID54593及窄屏54991形成同PID AXMainWindow→AXWindow→AXWebArea→截图/geometry，3份app-wire证据核对最终入口与合成状态；窄屏已视觉查看。两PID已停止，合成根与App保留。

专用真实App最终binary（本地签名后）86243cac5c41abe04596662201f717dd765c04017bfd2d0ce3c1074e9832672a。打包记录evidence/pilot-package-20260908T072127Z/result.json，构建/cache/App均在工程自有根；上述打包记录是工程交付时“未启动”的历史事实；之后PM打开并由用户完成真实操作，如本报告当前结论所述。工程会话未采集真实App AX/截图，也未检查真实DB。

## 用户亲验非内容回执

PM原始回执：/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/reviews/LIFEOS-P3-147/pm-user-local-source-receipt.json；原样副本：evidence/pm-user-local-source-receipt.json。evidence_origin=user_statement_in_pm_conversation，local_functional_gate=User Verified；导入完成、检索/原文打开、重启重连/检索正常、未观察到重复四项均为用户陈述。

PM记录其在交互前核对并打开上述固定binary，未在用户交互后检查进程。personal_content_collected=false，real_data_screenshot_or_hash_collected=false；未关闭风险、未推进Stage、未授权Git合并。不得将这份回执扩张为全库完整性证明或Independent Pass。

## 角色、交付与剩余事项

主责工程执行；普通功能和交付完整性可复核，独立安全无Pass。工程基线f53ea563及前序801e478a/640ebb6历史完整保留；本轮前报告/Manifest/检查点在history/pre-real-wiring。当前FINAL_MANIFEST只绑定代码、合成证据及App打包hash，不包含真实数据。

本地普通功能已获用户亲验反馈，不再列为“等待用户首次点击”。尚未激活/验证的范围：真实网页和目录外文件获取、真实Provider/Keychain/模型发送、OCR/音视频转写、全格式语义理解；不把本地导入或原文检索描述成AI已理解全部资料。用户未观察到重复不等于机器证明全库去重/完整性，实际全库容量和格式分布没有独立核验。

需PM依据本非内容回执确认本地功能收尾；整体L3终局、风险/Stage和Git合并不由本报告改变。未push/merge，不提出自动后继或重复测试。原独立评审未确认风险持续记录。

工程根：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/。设计/接线说明：design/real-wiring.md；全量diff：evidence/real-wiring-diff.json；本次元数据完整性结果：evidence/user-verified-integrity.json；checkpoint resume_from=pm_local_functional_closeout。candidate/tools/verify_entry_release.py按e4b4aed9工程交付合同原样保留，本轮不运行它或访问App文件。
