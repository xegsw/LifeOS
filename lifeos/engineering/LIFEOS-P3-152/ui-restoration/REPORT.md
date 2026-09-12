# P3-152 UI 与设置兼容修复交付

状态：修复增量已构建/合成验证，待PM核对及安全切换。不是完整累积产品Pass；当前真实App25223未关闭、未重启、未覆盖，未读取其AX/截图/DB/Keychain或发送网络请求。

## 定位与基线

最初152的真实设置将142服务配置中心缩成DeepSeek表单及折叠目录，丢失Cloud/Local配置选择和非敏感设置保存；这是实际漏接，不是仅文案问题。151与152虽CSS相同，Today实际组成也只是简化教学卡，未使用116已确认空状态层级。已依据实际源码修复，不凭CSS或截图宣称功能完整。

直接工程基线为同任务real-stage/candidate，由real-stage/FINAL_MANIFEST.json记录未提交版本；此前332项清单是该阶段身份。本修复完整复制该候选后增量改动，不挑选单个模块生成另一产品。构建入口ui-restoration/candidate/Cargo.toml，主UI application/health_ui.ts与settings_view.ts，生成产物ui/*.js；最终用户修正版来自该目录controlled-real构建，见evidence/restored-bundle.json。它仍是P3-152修复候选，不能代替PM尚未指定的完整累积产品基线。

视觉权威绝对路径：
- /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/prototypes/LIFEOS-P3-116/app.js 和 styles.css：Icon Rail、空状态、全局输入和纸白留白。
- /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-142/candidate/ui/app.js：secondaryNav、serviceCard、modeControl、configForm、capabilityList、routing、advanced。
- /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-143/candidate/src/runtime.rs：SettingsDto、校验和本地保存。
- /Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-151/candidate/application/health_ui.ts：已交付自然对话行为。

已定向读取PM权威5ed8/No.2/lifeos/ACCEPTANCE_GOVERNANCE.md D-0648与D-0649相关章节，不修改治理账本。

## 继承、差异与验证映射

| 继承项 | 修复/保留 | 证据 |
|---|---|---|
| 116窄Icon Rail/中文提示/轻全局输入 | 保留原CSS材质与几何；补中文tooltip/aria；首页恢复空状态层级，移除强健康教学与传输横幅，不伪造Focus/日程/健康结论 | ui-today；源码结构对比 |
| 142设置二级结构 | 通用/模型/数据隐私/备份/关于恢复；原未开放项仍诚实未开放 | settings_view.ts、配置态/空态/窄屏 |
| 主AI服务槽位及Cloud/Local | 实际可选8云端+4本地，主槽位展示保存的Provider/模型；分模式页面草稿，保存/重启恢复 | Host catalog_cloud_local_persist_restart_and_cas，集成新增2项；ui-cloud-saved/local-saved/local-restart |
| 143本地SettingsDto | 严格version/primary/routing/fallback/advanced字段和原范围；固定offline/local标识、非法字段/secret/endpoint拒绝；CAS不默覆盖 | catalog_strict_secret_endpoint_and_range_rejected；44/44 |
| 能力目录 | 继承143 metadata声明规则，单独标运行状态，不全部删除也不伪称真实可用 | capability-tests 7/7；ui-final-capabilities |
| 运行策略/高级 | 偏好保存保留，原自动覆盖与固定数值展示恢复；明确本轮不执行自动路由，实际输出1024/超时60不扩大 | DTO校验、UI结构及纯函数测试；原fallback UI仍默认未配置，不新增编辑器 |
| 152真实披露/ModelPort/CredentialPort | 保留完整body/单次确认与加密端口；新增catalogRevision确认绑定，非DeepSeek主服务拒绝真实发送 | 既有集成回归+catalog_change_invalidates_old_confirmation；端口文件逐字节未改 |
| 151草稿/失败/取消/澄清/短期状态 | 复用不受影响实现与既有证据 | 集成10/10中原8项继续通过 |
| 116完整Me/Context Detail/Memory Detail/AI Workspace/Quick Capture及更早累积能力 | 本P3-152候选并非这些完整交互的累积接线证明；不能把现有简化页或菜单当作完整能力继承。需要PM指定完整累积基线及缺项接回范围，未在本补丁宣称已恢复 | 明确继承缺口，非整产品Pass |

## 经PM批准的兼容增量

新增现有command/version5 read_local_catalog/save_local_catalog，proposal见design/settings-compatibility-proposal.md。PM批准保留sources表私有固定行_settings_catalog，不迁移meta或增表；保存authorized=false、kind=private_settings_metadata，无用户record/state/memory链接。reserved '_'来源统一拒绝enabled；没有独立开放的来源枚举IPC，prepare仅由合法records解析sources，引用只能来自packet。测试直接伪造reserved ref与带reserved source的record，并将metadata.authorized恶意改true，仍不能进入packet/source列表/请求正文。

配置不成为领域Source，不参与健康失效。catalog变更旧确认失效，非DeepSeek主服务不回退到DeepSeek；路由偏好不是网络权限。API Key仍走原专用加密持久端口。没有旧库/旧Keychain、真实路径或权限新增。

本地配置先CAS保存，再在已有凭据且DeepSeek时同步既有模型选择。无凭据也可先保存非敏感配置；之后用户保存凭据时接回该模型。跨库同步失败保守阻断发送，不能绕过预览。

## 核验顺序与结果

先定位142/143与152源码/字段/持久化差异，再执行44项Host、10项集成，另7项能力metadata一致性检查。最后因页面结构变化取少量合成视觉：空态、配置态、Cloud/Local、窄屏操作和重启。截图只证明呈现/可达性；保存/重启/CAS/引用隔离以行为测试为主。

后续仅能力声明及固定错误文案变化，未改布局/交互/端口，复用先前空态与窄屏证据，只补最终能力区检查。不重拍全历史。已通过但未受影响的152 mutation/旧对话GUI证据继续保留，不宣称它们验证新增catalog逻辑。

修复增量测试均通过；五类计数P0=0/P1=0/P2=0/Unknown=2/Not Implemented=0。Unknown分别为完整累积产品基线/全能力继承尚未证明，以及修正版真实用户操作结果尚未验证。该计数不是整产品缺陷穷尽清单，也不代表已接回116所有交互。

## Bundle 与安全切换方案

新bundle：/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Restored.app。
来源：本目录candidate的controlled-real构建；SHA256及固定二进制路径见evidence/restored-bundle.json。仅打包，未启动，绝不覆盖当前Controlled.app。合成预览为另一个UI Preview.app，不能交作用户真实版本。

建议PM先核对继承矩阵和修复界面。切换时由用户先保留/完成草稿并正常退出当前真实App，再授权打开新Restored.app；Agent不自行关闭25223、不并发打开连接同库的第二实例。新App沿同一已授权数据库/Keychain，读取兼容配置，无迁移/删除/旧库复用；旧配置目录行不存在时沿用原DeepSeek配置，只有用户点保存才新增本地catalog记录。发生冲突停止，不清理外来内容。

本修复没有推送/合并、风险关闭、独立复评或后继任务。完整产品累积基线未获证明前，不自行把此bundle宣布为完整用户版本或直接替换运行App。
