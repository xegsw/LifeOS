# LIFEOS-P3-147｜Obsidian 只读来源接入与对话记忆集成

状态：**Partial / In Progress — 公共API批准待回传；不是Engineering Pass**。风险L3。已按Revision 4实际启动合成工程，未止于准备方案；任务整体未完成。工程和报告位于新隔离worktree `/Users/xxe/.codex/worktrees/b3f6/No.2`，未提交、推送、合并，未修改PM账本、历史或任务卡，未转派。

## 授权与固定输入

任务卡：`/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/tasks/LIFEOS-P3-147_obsidian_readonly_source_and_conversation_memory_integration.md`，Revision 4优先。固定146源commit `f56223ad92f5b86c42f4bd60303ca6c892c3f9c1` 已验证存在；从Git blob复制30个candidate文件，219项旧Manifest和报告hash全部一致。146只继承合成离线Pass，145真实Gate仍暂停。

已读根AGENTS、CURRENT_STATUS、指定PM状态/决策D-0651～0655、146 PM Review、D-0651增量说明、任务卡、回复/ABF/独立评审/checkpoint模板、验收和CI治理；定向读架构V1.0、IA Memory/Global AI/Settings关联、角色/关卡和PM规则。工作区与指定PM CURRENT_STATUS差异仅为已读头部增量，剩余相同内容按diff复核；工具截断段已补读。没有搜索替代个人资料。

工程临时根仅 `/private/tmp/lifeos-p3-147-obsidian-source-v1`，普通0600 marker和0700根初始化成功；未访问/探测任何禁止真实路径、Pilot、正文、DB、凭据、Keychain、真实网络或Provider。目录字面值未作为探测目标。无App启动、无后台任务、无真实HTTP或监听端口。测试使用的SQLite和文件均为本轮合成。

## 首次修改前检查点与批准状态

完整映射：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/design/implementation-checkpoint.md`。

事实：146的SourceItem只允许两类内联合成输入和200字符正文。原20个IPC不具备目录选择、授权目标、分页worker或来源证据查询能力。提案为新增5个IPC，保留原20个行为；不借无关IPC偷渡。

PM已回复“暂不批准公共接线，已授权内部模块继续”，公共API须待用户明确批准。已补入PM要求的游标所属/版本/generation、读授权、epoch隔离、严格ID/整数/幂等、原件和事务恢复及长文身份约束。后续补充get_source_evidence的detail/search判别联合字段也已发给PM，未接线。

## 实际代码

- `candidate/src/source_file.rs`：受限目录FD、逐组件no-follow读取、根内文件符号链接解析、越界/循环/特殊文件拒绝、分页256、读取前后identity复核、64KiB流式复制/0600原件。5,201文件、24层和300KiB原件测试通过；不设置旧总量/深度/正文截断。
- `candidate/src/source_store.rs`：复用同一Repository连接和records/sources/packets等权威；connector/grant/job/file/artifact/link/segment/FTS/cursor/内部回执表。版本唯一、批量最多50、事务故障回滚、旧worker拒绝、撤权后旧记录不复活、范围/版本绑定游标、FTS最多8结果、无结果为空。源片段不形成Memory或State；新版本解析失败保留旧有效版本并记录失败。
- `candidate/src/source_worker.rs`：持久扫描队列、分页扫描、单次一项有界导入、文件版本和原件发布、隐藏配置/附件处理、暂停恢复、手动刷新/缺失失效、根identity变化拒绝。原件以不可覆盖hard-link发布后再提交DB，回执故障产生的未引用原件可在本DB/connector命名空间隔离后重试，保留失败历史。
- `candidate/tools/parse_source.py`：UTF-8文本、配置受限、静态HTML、DOCX段落、PDF页码；解析子进程30秒、输入/输出预算和RSS/peak检查。PDF使用本机bundled pypdf，无联网安装；宏/脚本/页面资源均不执行。
- `candidate/application/web_source.ts`：注入式Transport；直接目标、独立授权、逐跳地址校验、固定连接地址复核、最大并发2、10秒解析/连接预算、总30秒、5跳、20MiB解压后响应。没有真实DNS/HTTP实现，不能误称真实Web接入通过。

实际格式状态：Markdown/UTF-8纯文本可完整切片；JSON/YAML/TOML/INI/CFG/CONF受限原件，正文不入records/FTS/Context；HTML可静态正文/标题/链接；DOCX正文和段落依据，穿越/实体/容器预算拒绝；PDF文本层及页码可解析，扫描PDF标OCR required，加密PDF不破解；图片/音频/视频/可执行/压缩/未知类型保留原件并标original_only。未知编码明确unparsed。

本轮新增的是内部合成候选，原生App尚未接来源入口；不是可供用户真实连接的完成品。

## 实际测试与包内修正

最新分组结果：11项Rust内部测试、10项解析测试、14项Web Transport替身测试、30项146继承测试，合计65项通过。合计只表示各命名测试通过，不能按总数批量映射所有AC为Pass。

- Rust：5,201分页/24层/300KiB；文件链接/特殊文件/读中变化；版本幂等/冲突/乱序/回执回滚；游标跨connector/版本/撤权拒绝；配置不泄露；长文不确认；暂停/取消/断开旧worker；127项实际导入（125笔记+隐藏配置+附件）关闭重开；刷新/缺失/根inode替换；原件发布后DB回执失败隔离恢复；失败新解析保留旧有效版本。
- parser：正文完整、受限配置、异常编码、静态HTML、wiki/Markdown链接、DOCX正常/穿越/实体/损坏/展开预算、PDF正常/扫描/加密、附件original-only。
- Web：正常目标正文与非递归；未授权、秘密query、私网、连接peer替换、执行中撤权、响应超量、404/认证/超时/MIME、每跳授权与重定向上限。
- 继承：原30项对话、草稿、幂等、Memory/State、纠正、反馈相关性、撤权、离线模型切换和边界测试。

失败历史：`internal-tests-3.log`真实发现暂停恢复时队列仍在旧epoch，遗漏隐藏目录；已修正pause/resume队列epoch同步，后续127项导入通过。日志没有覆盖。原件按DB/connector分命名空间，防止恢复误处理另一个合成DB的引用原件。

## AC矩阵与尚未通过部分

| AC | 当前可复核内部覆盖 | 当前结论 |
|---|---|---|
| 01 | 多格式、配置、附件、文件FD/越界/特殊文件/部分链接 | Partial；目录符号链接和macOS别名未完整实现 |
| 02 | 5,201分页、24层、300KiB、127导入、暂停重启、失败回滚 | Partial；原生连接/取消进度未接线，目录动态变动扫描的完整性仍需补强 |
| 03 | 原件、版本、片段locator、不提升确认事实 | Partial；原生依据展示待接线 |
| 04 | 幂等、乱序、唯一键、回执原子回滚、失败保留旧版本 | 内部测试通过；跨UI完整链待补 |
| 05 | FTS有效版本/授权/无结果、原预算继承 | Partial；查询→Application→原有packet组合未接线，不能把snapshot全量来源内容作为替代 |
| 06 | 暂停/撤权epoch、重连不复活、缺失/更新失效、重启 | Partial；外部目标grant及其依赖完整链待补 |
| 07 | 146全部30项回归 | Partial；当前新增UI尚未存在，未做原生视觉验证 |
| 08 | 生产凭据源不链接、真实网络零实现、Web注入反例 | Partial；外部文件/网页授权持久化尚未闭环 |
| 09 | 错误码、配置不进入普通内容、当前限定合成日志 | Partial；全链诱饵泄漏矩阵待公开接线后补 |
| 10 | 内部扫描/导入/刷新/断开/重启 | Not Implemented：原生完整操作、安全独立Gate和真实亲验 |
| 11 | 原始直接链接提取、根内目标原件关联、Web目标正文替身 | Partial；跨目标授权/获取结果入库/撤权谱系组合待补 |

额外资源缺口：本机设置RLIMIT_AS 64MiB失败；当前是子进程RSS watchdog与结束后peak检查，**不等于OS硬内存上限或完整解析沙箱**。此点保留Unknown，不能在独立安全Gate前假称资源隔离已完成。PDF等解析器也尚未以恶意多格式完整安全矩阵证明适合真实启用。

本任务整体不得计Unknown/Not Implemented为0，不出Engineering Pass或独立Pass。此处未用65项测试掩盖以上缺口。

## 恢复、交付与PM事项

工程根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/`。
复跑：该根`REPLAY.md`和`candidate/tools/run_internal_checks.py`；每次写独立时间戳日志，locked/offline；全局CI注册未改、未声称已跑GitHub CI。
检查点：该根`evidence/checkpoint.json`，从`source_lifecycle`继续公共接线及受影响组合检查；65项未受影响的内部正Evidence可保留，无需全量重建。原件/合成DB/构建缓存保留，writer已结束，尚未执行精确清理；不把“未清理”写成“已清理”。
Manifest：该根`FINAL_MANIFEST.json`，是当前Partial快照完整性清单，非Frozen ABF或终局通过凭据。

主责为Codex工程执行；协审视角为数据/来源、安全、技术与体验。Gate2/3/4尚未整体通过，独立安全评审由PM分派；Gate5真实亲验未启动。需PM回传5 IPC及detail/search字段的用户批准，并在工程完成后绑定安全ABF/评审。当前不需要Key、真实笔记或网络授权，不自行启动真实阶段，不创建后继任务。
