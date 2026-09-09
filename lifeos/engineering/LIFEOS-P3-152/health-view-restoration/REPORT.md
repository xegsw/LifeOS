# P3-152 健康辅助查看接回增量

状态：工程与影响面验证完成，待PM验收；真实用户验证未执行。主责Codex原工程会话，L3同任务增量，独立评审仍暂停。不宣称完整产品Pass、风险关闭或Stage变化。

## 结果与授权

当前App源码恢复“我 → 查看健康来源 → 查看已导入数据 → 查看历史趋势”的按需辅助链。默认Today仍是152自然对话入口；我保留短期状态，142设置及全局草稿保留。辅助区默认只有导入状态和逐指标最近日期，不改回健康看板。

PM批准的唯一公开增量是get_today Raw v2/health_view。精确提案与审批hash见design/ipc-proposal.md、approval.json；PM追加要求health-demo只作既有授权记录标识，不得作synthetic绕过，已在Store实现和测试中落实。完整复制ui-restoration候选后改动7文件、新增5文件，无删除；见evidence/difference-manifest.json。原候选和历史报告未改。

## 实现与边界

请求先纯解析校验，再由Store在同一锁内检查source_connected和既有health-demo授权记录，之后才解析固定目标、打开Reader。两种模式都执行授权检查；没有因标识名称带demo而豁免真实模式。界面展示不会生成AI packet，也不代表AI处理许可。

兼容原150R1 metric/7、30、90日/endDay/source+offset/groupPage DTO、日界线、来源分组、null和estimated、失败关闭。Raw≤4096字节，来源每页32组、日点≤90、响应≤128KiB；每次SQL最多3秒、busy150ms。沿用Reader::open的steps校验查询，所以一次请求包含至多初始化校验与实际查询两个有界阶段，不虚称整个IPC3秒。日期索引0..47481、来源名称组与offset、未知不当零、其他组不合并总量均保留。

Reader纯解析/已校验查询入口提取外，原查询SQL不变；固定真实目标常量、只读/query_only/no-follow/权限/文件身份/sidecar守卫沿用。没有写库、迁移、ZIP、初始化业务表、新健康类型、Provider/凭据访问或网络。无效请求在打开数据源前拒绝。旧七命令及v4/v5不变；本次只新增第八个命令。

UI复用150R1 Controller及内容，移除其独立Shell和自动挂载；按需进入才串行读取3指标概要，退出dispose后阻止后续查询和迟到发布。没有后台轮询。readonly.css全部限制在.health-aux内，避免原全局label/summary等规则影响142设置；辅助区增加140px底部留白，避免全局输入栏遮住说明。辅助与对话的retry事件按DOM区域隔离。原对话草稿没有被重建或提交。

## 差异到验证

| 影响 | 验证 | 结果 |
|---|---|---|
| Reader公开查询接回 | 150R1原15项Reader测试移植到本任务新合成目录；窗口/日期/null/缺失/零/分页/重复/身份/权限/sidecar/锁/SQL预算/DTO边界 | 15/15；未访问150历史临时根 |
| Store授权与无写入 | 新3项：两模式共用授权守卫的合成反例、先校验后缺失源打开、查询前后业务/健康DB字节相同且ModelPort spy不得调用 | 3/3 |
| main/gateway/Store共享依赖 | 原44项Host影响面回归与上述18项 | 62/62，evidence/host-tests.log |
| TS→实际Host | 原10项设置/对话回归，新2项get_today保留草稿设置且无凭据可用、错误operation/字段/类型拒绝 | 12/12，integration-tests.json |
| Controller/呈现 | 原9项R1内容/串行/迟到/空态测试，新3项未进入不读/退出停止/新实例及模式标签 | 12/12，ui-tests-final.log |
| 最少实际合成GUI | 1280×949最终概要，700×762最终详情/趋势；从我进入/退出草稿保留，设置仍为原Ollama local-config-demo | 两张最终截图及各自精确PID/AXWebArea/几何JSON；设置/草稿另仅AX确认 |
| 构建 | synthetic及controlled-real最终构建、UI语法 | 通过；真实仅打包未启动 |

旧18以外历史mutation/全历史截图未重做，不能说其覆盖了新get_today。当前无候选未修复缺陷；计数仅本辅助增量P0=0/P1=0/P2=0/Unknown=1/Not Implemented=0，Unknown为真实用户辅助查看结果。整个产品仍有下列三组已确认接线缺口，不被这个局部计数消除。

首次窄屏观察发现底部文字遮挡，已同包修正；早期overview及旧启动回执保留为过程证据，最终呈现仅使用auxiliary-overview-final、auxiliary-narrow-final。一次CUA调整大小后坐标过期无目标，重新读取合成状态后继续；没有获取其他窗口。搭建测试文件时曾缺子目录，补齐后实际62项通过；不将准备阶段当成测试通过。

## 继承矩阵更新

| 对账链路 | 本轮后状态 |
|---|---|
| 142/143非敏感设置选择/保存/重启 | 保留；共享回归和实际合成设置确认 |
| 147来源管理 | 未接回；集中方案第1项，仅方案 |
| 147/148原文检索与来源对话 | 未接回；集中方案第2项，仅方案 |
| 149健康导入 | 未接回；集中方案第3项，仅方案；真实受控导入与合成App入口区别保持 |
| 149语义/150Reader到152对话 | 保留，无SQL/日期/聚合语义变化 |
| 150R1辅助查看 | 本轮已接回组合App源码、合成IPC/交互及构建；真实未启动验证 |
| 151/152对话与116视觉基础 | 保留；未把116全原型宣称生产实现 |

另外三组集中工程/接口/存储/真实权限方案见design/remaining-inheritance-plan.md；没有自行实施或开启其真实权限。

## 身份、保全与交付

基线ui-restoration Manifest e53f50df8cdf7c813fcd64327162db1ae4645059b7b63f7908267618cbf5d6f8。原189/332/172项及继承审计3项均逐项未变，见evidence/preservation.json。新包FINAL_MANIFEST不自指，包含完整候选与本增量Evidence；tools/rerun.sh可复跑合成影响面，输出新临时结果目录。

最终合成预览PID28820、二进制SHA256 1fbc2c050fb72350dc66878f28e53594ea202a1b7ba43f9c9de8b545619cffb2，见synthetic-launch.json。此前合成预览经精确PID/路径/hash验证后关闭，真实25223始终未接触。

新真实bundle：/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Health View Restored.app；二进制SHA256 ed9bc3f7a06bbcbb100414951a80d129020d50a2a19154a0efca061307e639d5；源为本目录candidate controlled-real构建，evidence/restored-bundle.json记录launched=false。没有覆盖已有Controlled.app或Restored.app、没有并发打开真实同库。运行App保持原状，切换仍等用户保留草稿/退出及明确安排。

PM需确认：本增量验收，以及剩余三组接回方案的顺序与精确接口/真实权限delta。无推送/合并、账本更新、风险关闭或新任务。
