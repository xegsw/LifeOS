# P3-152 有界代码继承对账

状态：本次静态对账完成；累积接回方案待 PM 确认，P3-152 整体仍 Partial。主责为原工程会话，不是独立评审。依据 PM 本轮指示及 D-0648/D-0649，对照142/143、147、148、149 closure-3、150 R1、151；116只作视觉/交互依据。未修改候选、历史包、bundle或运行App，未读取真实窗口、数据、凭据或发起网络。

**结论：当前修正版是健康对话候选，尚不是这些历史能力的累积产品。** 设置配置保存已修复；资料目录接入/管理、通用来源检索与对话、健康导入、只读辅助查看仍未接入当前入口。这些历史实现不能降格为原型，但也不能直接把其旧运行权限移入152。

## 版本与证据口径

所有下列工程相对路径以 `/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/` 为根。精确绝对路径、完整SHA256及所属Manifest在本目录 `input-identity.json`：42个定向代码/设计/测试文件全部与各自历史Manifest记录相符。该核验只证明输入身份；未重跑历史真实执行，不据此宣布历史PM验收或当前功能通过。

当前候选固定为 `LIFEOS-P3-152/ui-restoration/candidate`，Manifest SHA256 `e53f50df8cdf7c813fcd64327162db1ae4645059b7b63f7908267618cbf5d6f8`。构建入口该目录Cargo.toml；它是本次比较对象，不被指定为完整产品权威。116原型文件也单独记录hash，不冒充生产实现。

## 继承矩阵

| 能力与精确代码锚点 | 历史实际实现 / 占位 / 未知 | 当前入口与回退归因 | 最小接回方案及影响 |
|---|---|---|---|
| **142/143 模型设置**：142 `candidate/ui/app.js:134` 主服务、`:141` 云/本地、`:145` 配置、`:169`策略、`:179`高级；142 `candidate/src/runtime.rs:595`、143同文件`:976`校验后persist | 非敏感SettingsDto确实持久保存，不只是Provider菜单。高级覆盖原本disabled、数值只展示；fallback原本没有编辑器。其他Provider目录/设置不等于已真实接通 | 当前 `152/ui-restoration/candidate/application/settings_view.ts:6` DTO、`:9`恢复、`:17`选择；`controlled_conversation.ts:5`、`:40`保存。此前148/151/152简化页丢失完整本地配置，本次UI修复已接回。数据与隐私不能因142当年占位而忽略147/149后来的实际内容 | 现有修复已获PM批准、已有44 Host/10集成/7能力检查。此轮未发现需另改的设置保存缺口；不新增Provider网络、自动路由、fallback或参数编辑权限 |
| **147 来源目录接入、生命周期和目标授权**：`candidate/application/ui.ts:26–37`调用；`candidate/src/main.rs:150`注册25命令；`source_api.rs:185`严格dispatch、`:225`真实模式限制；`source_worker.rs:55/82/237/442/519`任务/扫描/导入/恢复/完成 | 有具体代码与事务/worker接线。合成外链授权与真实来源规则不同：真实模式明确禁止authorize_source_target，不能说历史支持任意外链。实时导入体验本次未复验 | 当前main仅7命令，无connect/control/status/authorize/evidence。Settings“数据与隐私”暂未开放。148页面已不提供147完整接入控制；149尚注册旧命令；150独立只读入口收缩为1命令，151改为5命令。不是本次UI修复新删，但属于累积产品缺口 | 恢复一个Settings来源管理入口和既有严格SourcePort适配；先明确来源身份、独立存储/worker和权限代际。不能直接把147 repository.open与旧运行根链接到152；涉及来源存储表、真实目录和后台任务边界，需PM方案确认 |
| **147/148 来源原文检索、详情与来源对话**：148 `candidate/application/source_ui.ts:45/55–58`检索/详情/断开/引用；`source_conversation.ts:6–13`对话保存、预览、确认、取消；`candidate/src/main.rs:185`注册26命令 | 原文检索详情和逐次来源对话是实际接线，非116静态原型。版本3对话请求与version1确认发送接口；不能只靠相同命令名兼容当前DTO | 当前Memory仅列确认记忆；Context只是说明/打开对话。`health_ui.ts:17–21`显示当前健康引用，但没有通用资料检索、原文分页、来源移除入口。152是v4/v5健康对话，不能直接加载source_ui.js恢复 | 优先接只读来源搜索/详情及引用，再接统一披露流水线，保留权限/版本/撤权失效。需适配148 packet/sourceRef到152 typed refs和最终确认，不向152导入旧库或自动授权资料；跨来源能力/接口需PM确认 |
| **149 苹果健康XML/ZIP导入**：closure-3 `candidate/application/source_ui.ts:16/24`、`apple_import.ts:8/11`；`candidate/src/main.rs:86/91`；`apple_health_api.rs:46`；`controlled_health.rs:64/84` | **两条不同历史入口**：App文件列表/进度/导入IPC仅合成模式（API拒绝real）；真实受控导入是独立 `--controlled-health-import` 入口，非已经做好的真实App文件选择器。事务、重复、semantic skip、projection实现存在；不能混称“真实App导入完整可用” | 当前无import命令、AppleImportController或受控导入启动分支。代码文件被复制也不执行。151 reuse-map明确无ZIP/import；152继承该缺口。健康库只读对话不能代替导入链路 | 复用解析/事务/批次逻辑，先定义用户入口如何调用受控导入，接入进度/结果并区分合成与真实。真实写入健康库、原ZIP访问、导入次数/目标守卫均超出152只读授权，不能仅加按钮后执行；需PM精确delta |
| **149健康观察语义 → 150读取 → 152对话**：149 `design/semantic-contract.md:5–11`；150 R1 `candidate/src/health_reader.rs:39–44`；当前 `health_source.rs:4/8–10`、`health_reader.rs:41–46` | 历史按来源名称组、metric、日界线offset、null、estimated保存读取；未知不当零。150是真实只读Reader实现，非看板原型 | 当前Reader真实只读查询被`health_source::read`用于问题相关有限投影，保留单位/来源/日期/估算说明；不是读取完全丢失。当前只取选择组/最近或今天昨天观察，不能冒充完整历史趋势或来源全覆盖 | 已接回的健康对话读取保留。扩大问题日期表达、全历史聚合或跨来源归并需另列语义/预算，不能据辅助页曾能查询90天就默认模型可收全量 |
| **150 R1 辅助来源检查页**：`candidate/ui/index.html:1`加载readonly.js；`readonly.js:17–24`有指标/7、30、90天/截至日期/来源组/趋势/逐日详情；`candidate/src/main.rs:14/26`仅get_today | 实际独立只读辅助窗口，设计明确不提供聊天或AI。不是完整产品Shell基线，也不是未实现占位 | 当前未加载readonly.js，未注册get_today；Me显示用户短期状态。内部Reader存在不代表辅助查看入口存在。151已改入口；本次修复未新删除 | 优先方案：在统一App“我/来源”按需打开辅助区，复用Reader有界query与原UI；不恢复默认看板。需要新增/适配只读查询IPC（当前无该命令）；可沿现有三指标/同只读目标，禁止扩大写权限。请PM确认接口兼容后实施 |
| **151 对话、澄清/纠正、短期状态、草稿生命周期**：`candidate/src/main.rs:9–16`五命令，`application/health_conversation.ts`；`design/reuse-map.md:9–15` | 151是合成自然对话实现；真实Reader/Provider未接，不能说151曾有真实健康AI。长期记忆显示不证明完整记忆编辑器 | 当前`controlled_conversation.ts:1–17`继承HealthConversation；本地澄清/明确状态仍走原链路，真实回答走必要披露/确认；UI`:16–23`呈现状态、记忆与引用。取消、迟到、草稿和失败路径已有增量集成证据 | 保留已接线行为，无需再次全历史重跑。独立记忆增删、完整Context管理不能由当前只读列表推定；本有界检查不额外扩展这些产品功能 |
| **116视觉/交互原型**：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/prototypes/LIFEOS-P3-116/app.js:61–78`及styles.css；对应原型交付报告 | 固定合成原型，无生产DB/IPC/网络；完整Me/Context Detail/Memory Detail/AI Workspace/Quick Capture不能整体计为历史已实现生产功能 | 当前继承基础视觉、Icon Rail、空状态和全局输入，不等于完整116交互已落地。本次表格不以116菜单数量制造回归缺陷 | 已授权视觉结构继续继承。是否将其余原型交互做成生产能力，需逐项找到实际工程与确认依据；没有依据即“原型/未证明”，不自动扩大本轮 |

## 紧凑处置清单

1. **已修复并保留**：142/143非敏感设置选择/保存/重启，不同Provider本地配置不能因仅DeepSeek发送而删除。
2. **优先接回提案**：150辅助只读查看。已有Reader和精确只读目标，主要缺UI入口与查询IPC；不必重构健康存储。
3. **需先统一SourcePort与DTO**：147来源管理、148原文检索/来源对话。不要把旧Repository直接接到新真实库；先确定只读检索与来源更新的存储、授权及撤权失效映射。
4. **明确真实写入delta**：149导入。历史真实入口是受控导入器，当前152只读；UI接回不能顺带取得写库/ZIP权限。

断点归因用于确定修复位置，**不以“151已缺”豁免累积产品回归，也不据当前缺口自动改变旧PM裁决**。本表4组待接回链路（来源管理、来源检索/对话、健康导入、辅助查看）是静态确认的当前不可达能力，不是四个全新业务需求。具体严重级别及接回合同由PM结合历史确认裁定；不得沿用UI修复小范围0/0/0/2/0作为整产品总计。

## 验证与边界

本轮只读源码与入口对账；无候选更改，故未重跑行为测试或新增截图。已核对既有增量日志44/44 Host与10/10集成及其文件身份，支持原测试覆盖的设置/对话行为，**不支持尚未接回的四组链路**。三阶段189/332/172项历史包逐项hash未变化，结果在preservation.json；bundle与真实App未接触。原报告、Manifest不追溯改写。

PM需决策：确认上述接回顺序及每项接口/存储/权限delta。对账交付已完成，不等于完整产品Pass、安全切换许可、独立评审恢复、风险关闭或Stage切换。当前无需再次解锁或追加真实截图。
