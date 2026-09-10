# P3-155 资料更新与日常恢复闭环

状态Ready / Execution Authorized（2026-09-09，D-0656）。用户在完整合同展示后回复“确认”，一次授权本合同内实现、测试、动态验证、安全切换及同范围修复。真实更新/导入仅限下列精确目标及动作；真实模型发送仍用户逐次确认，不机械继承154权限。

## 唯一用户结果

用户在现有App内更新已连接资料或选定健康导出文件后，能看清处理结果；中断后无需从头配置，重复操作不重复写入；后续对话只使用仍有效且获准的新资料。不是数据看板，不新建来源系统，不重做设置或对话。

主责Codex工程，建议顺序复用b3f6工程会话，154停止写入后执行；PM负责合同与验收。风险L3。实现、回归、动态验证、安全切换、真实用户结果、同范围修复作为一个任务。独立评审继续按用户指示暂停，不代表免除安全自检或Independent Pass。

## 已有事实与最小增量

PM只读核对最终154源码：source_store.rs已支持pause/resume/cancel/refresh/disconnect及幂等/epoch；文件fingerprint与version已有增量判断；sources_view.ts已展示发现/解析/待处理和继续处理，apple_health_api.rs已有重试测试。故上述不得重新实现一套。当前来源页仍有通用catch提示，来源读取和健康状态请求共用错误边界，优先验证一个来源失败是否遮蔽另一个正常来源，再按事实修补。

工程先补齐existing-capability-map，复用已覆盖能力和Evidence；只有实际缺口才改。候选必须整体继承，不因没改CSS就省掉行为接线回归。

154工程终局补充报告`lifeos/deliverables/LIFEOS-P3-154_final_closeout.md`仅为非内容收尾：已有Apple导入包含ambiguousDuplicate处理，不能将重复语义泛化为任意文件自动无损去重；遇到歧义必须保留现有资料并明确提示，不擅自覆盖或猜测重复。

## 累积基线与直接输入

最终完整基线：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-154/closure-1/flow-stage/candidate`（165文件，Cargo.toml构建入口），其上级FINAL_MANIFEST SHA256 `3cd103ab8b4b6c3142036b79a9c03a33cbe75c6d0f52ed1c1c906f32c6dee4e7`。先复算候选文件；最终App必须来自完整累积候选，不回退153离线版或154初版。

输入：5ed8树`lifeos/reviews/LIFEOS-P3-154_pm_final_review.md`；b3f6树154原报告及`LIFEOS-P3-154_closure_1_flow_error_ownership.md`、最终完整包。直接代码包括source-engine/src/source_store.rs、source_worker.rs、apple_health_api.rs、health_ingestion.rs和Application sources_view/health_context/controlled_conversation。历史均只读。

继承不变量：Shell/设置页面不重绘；Provider列表和选择方式不缩减；Key加密持久、无TTL、保存/测试/选择/启用分离；154最终错误归属与只读恢复修复保留；资料/健康/对话/草稿/记忆及单次披露链路不能漏接。模型选择由用户，真实仍限DeepSeek。

## 拟授权允许范围

工程根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-155/`；独立合成/构建根`/private/tmp/lifeos-p3-155-source-update-v1`，0700、0600唯一marker；未知既有根不得接管。先全部合成验证，后正常切换新完整App。旧154精确身份正常退出，保留旧bundle、数据、凭据，禁止强杀模糊PID；失败按原锁和身份约束恢复旧App，不迁移库。

真实动作仅App内部处理，Agent不读取个人正文/值/截图/AX/真实日志或内容hash：

| 精确目标 | 允许动作 |
|---|---|
| `/Users/xxe/IT-obstain` | 用户点击刷新后只读检查已授权根内变化；不改原件，不跟随根外目标/网络外链，不启动后台监视 |
| `/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/source-engine-v1/` | 复用sources.sqlite、artifacts/tmp/.runtime及既有marker/锁；按既有Schema事务更新索引、版本、处理进度、派生失效，不新建并行库、不物理清理历史缓存 |
| `/Users/xxe/Downloads/导出.zip` | 用户点击选择后只读导入此精确文件，不枚举Downloads。不同导出路径另需一次确认，不宣称已覆盖 |
| `/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite` | 复用已验证导入事务、去重/投影合同更新已有库。完整历史原文不覆盖，去重元数据按既有算法维护；不迁移/重建/清空，不擅自增加健康类型或将局部快照解释为全量删除 |
| `/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/conversation.sqlite` | 沿既有协议保存用户对话/反馈及派生失效，禁止写入来源全库复制，不新增Schema |
| 同父目录provider.sqlite、既有`.lifeos-p3-152-owner.json`、`.runtime`与SQLite副文件 | 保留现有密文、非敏感配置、marker与锁合同，不改名/重建/迁移；SQLite必要事务副文件限原目录 |
| 既有OS Credential Port | 只复用service `com.lifeos.p3-152.aead-key.v1`与严格`p3-152-key-[0-9a-f]{32}`旧account；不枚举、不回退144、不覆盖密钥或要求重新录Key |

真实网络仅用户手动/models测试和每次确认后的DeepSeek chat/completions（https://api.deepseek.com）；来源更新/健康导入本身绝不触发模型、同步云端或自动重发。上次请求结果不明也不得自动重试。最多3来源+2状态/确认记忆及4096字节既有预算保持，权限和时效二验不放宽。

## 交互与数据规则

沿现有Settings二级页面和来源区域增量处理；不新增主导航/通知中心/卡片墙。已有进度展示改准确，不做装饰性假百分比：总量未知时显示已处理数及阶段；暂停/取消/失败/待手动恢复/成功必须区分。每个来源独立显示结果，不能因健康读取失败把正常工作来源显示为全部失败。

更新摘要仅必要数量/结果，详情按需展开；新增/变化/未变化/未解析/缺失/失败必须由真实运行结果或合成断言支撑，不猜成功。未变化内容复用已有版本与解析成果；元数据枚举不冒称完全不扫描。失败保留已有可用资料和历史，中断恢复不从零配置；进程重启不得自动采集、导入或联网，只恢复状态并提供手动继续。重复点击、并发刷新、旧worker晚到或重复ZIP不得重复落库。

来源发生变化时相关引用/预览/回答按原版本与授权规则失效；不把撤权、过期、原件缺失或删除混为物理清理。有效的无关资料保持可用。不把导入来源升级为用户确认长期事实；当前健康数据仅睡眠、步数、Apple运动时间等已有真实范围，非医疗建议。

复用UI→Application→Domain/Capability→Ports→Adapters；UI不直连SQL/网络/Keychain。不新增公共IPC、关键DTO/Schema、采集权限或迁移；若确有必要，提交最小差异后等待批准，继续独立可做部分。不新增语音、手机App或新Provider。

## 验收与Evidence

任务级L3依据见`LIFEOS-P3-155_acceptance_basis.md`，用户确认后锁定。先代码/接线差异→合成行为/反例→最小视觉补充，未受影响证据可复用，禁止全量截图代替行为。保留154最终错误归属回归。

必须覆盖已有资料不变/有变/原件缺失/受限解析、重复ZIP、部分失败、DB忙锁/进程退出、同幂等ID重试、旧worker迟到、授权变化、更新后最小上下文/预览失效、凭据和设置不退化。提供结构化矩阵、关键守卫mutation、Manifest与历史保全、单命令离线复跑。真实操作只收用户成功声明/固定码，不收正文截图。当前未执行工程/真实操作，不能提前写Pass。

环境锁屏/GUI/runner问题Paused—Resumable，checkpoint保存身份及resume_from，恢复只重跑受影响阶段；同范围失败留本任务Closure，不拆微任务。不可分离越权污染按原治理处理，不能用后来补证掩盖。

## 交付、审批与不变项

启动必读AGENTS、CURRENT_STATUS、本卡、验收依据、SESSION_REPORT_TEMPLATE；154最终PM Review及上述直接输入。定向读PM_OPERATING_MODEL/ROLE_MATRIX/STAGE_GATES/ACCEPTANCE_GOVERNANCE的L3真实数据/权限/同步边界及暂停例外，CI_CD_GOVERNANCE的累积产品/可恢复执行；架构V1.0 Ports/权限、IA Settings/Global AI章节，文件均位于5ed8树lifeos。

主交付：b3f6树`lifeos/deliverables/LIFEOS-P3-155_source_update_and_recovery.md`；工程根内完整candidate、existing-capability-map、impact-map、矩阵、Manifest、checkpoint和复跑入口。先自检修复后交PM，再用户最少真实验收：手动刷新、同ZIP重复导入不增量重复、中断恢复/重启与对话使用有效资料。用户不必故意制造数据丢失、编辑原件或发正文；危险反例全由合成覆盖。

本合同通过不关闭风险、不冻结产品/架构、不切Stage、不清理任何真实/历史数据、不自动合并main或启动后继。安全代码文档同步任务分支，真实资产不上传。不同真实目标/新权限/不可逆动作/关键Schema/API才另确认，已展示并批准范围不重复确认。
