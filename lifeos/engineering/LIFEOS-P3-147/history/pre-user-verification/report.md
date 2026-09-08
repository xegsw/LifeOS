# LIFEOS-P3-147｜固定本地来源 App 工程交付

## 当前结论

普通工程接线与合成验证完成，专用App已打包，等待PM核对后由用户亲自点击真实连接。任务卡最新增补已批准唯一来源、非加密保存边界及source-pilot-1固定编译profile；不再等待或重复请求这些批准。工程会话没有启动专用真实App、访问/探测真实来源或真实输出根，也没有真实导入。

**User-directed review waiver / No Independent Pass**。原IR-P0-147-001、工程修正、Rework与独立未完成8行保留；未运行或改写被平台拦截的安全评审。普通验证不等于独立通过、风险关闭、L3终局或Stage提升。

## 用户操作步骤

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

当前普通验证共10组：合成UI/导入生命周期6组、真实入口UI合成stub3组、source-pilot-1分支的Rust普通生命周期1组。Rust测试仅在cfg(test)把源和输出绑定工程fixtures，实际真实路径零接触；覆盖点击初始化、6文件导入、capture.sqlite权限、暂停/重新打开/继续、检索、刷新和断开。23个其他Rust测试被过滤，未运行安全反例或独立review runner。

最终普通结果：evidence/checks-20260908T072044412392Z/；UI生成：checks-20260908T071937035501Z/；Rust真实分支合成测试：pilot-normal-20260908T072104Z/。中间UI stub语法失败及修正记录保留，不计为最终通过。

合成App最终binary ac9c5c381635abc7a9260060835b5f7bd7aec0407bacbeb51a2554f3484d9c9b。实际桌面PID54593及窄屏54991形成同PID AXMainWindow→AXWindow→AXWebArea→截图/geometry，3份app-wire证据核对最终入口与合成状态；窄屏已视觉查看。两PID已停止，合成根与App保留。

专用真实App最终binary（本地签名后）86243cac5c41abe04596662201f717dd765c04017bfd2d0ce3c1074e9832672a。打包记录evidence/pilot-package-20260908T072127Z/result.json，构建/cache/App均在工程自有根；仅编译/打包，未启动、未采集真实App AX/截图、未创建真实DB。

## 角色、交付与剩余事项

主责工程执行；普通功能和交付完整性可复核，独立安全无Pass。工程基线f53ea563及前序801e478a/640ebb6历史完整保留；本轮前报告/Manifest/检查点在history/pre-real-wiring。当前FINAL_MANIFEST只绑定代码、合成证据及App打包hash，不包含真实数据。

当前没有需要用户重复批准的同路径/存储问题。剩余步骤是PM核对普通工程交付后，用户亲自打开专用App点击连接；真实来源是否存在、实际权限/容量/格式分布尚未验证，不能假称真实闭环已经成功。最终PM验收及L3合并未完成，未push/merge。原独立评审未确认风险持续记录。

工程根：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/。设计/接线说明：design/real-wiring.md；全量diff：evidence/real-wiring-diff.json；当前校验入口：candidate/tools/verify_entry_release.py；checkpoint resume_from=user_click_real_source_in_app。
