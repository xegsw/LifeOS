# LIFEOS-P3-146｜自然对话、记忆更新与授权来源合成集成闭环

当前结论：Engineering Completed / Awaiting PM Review。L2合成离线范围内，23项自动测试通过，16份最终actual-Tauri截图绑定直接启动PID、准确标题、AXWebArea及窗口几何；26项证据一致性断言通过。P0=0、P1=0、非阻断P2=1、合同内Unknown=0、合同内Not Implemented=0。以上为执行侧自检，不是PM Pass、独立评审或真实能力放行。

## 1. 授权、范围与历史

执行负责人Codex专项会话 `01a07e77-dba3-7bc0-a2a7-e69f01c51347`。D-0653已批准同任务实现、DTO/新合成库、测试、GUI与包内修正；分支 `codex/l2-p3-146-conversation-source`，起点 `9d4dac3c016edec2acacfcda7f966effb860804c`。未提交、推送或合并，未改PM账本/全局CI。

完整批准合同保存在 `../engineering/LIFEOS-P3-146/history/task-D0653.md`；批准的准备报告保存在 `history/preparation-D0653.md`，只读且SHA-256仍为 `98b151d3b30908079c6e76cc236a93d03f0a6cbdba5796ab0739a54cbddfd6b5`。当前报告替换准备阶段正文，原历史没有覆盖。

唯一工程根 `lifeos/engineering/LIFEOS-P3-146/`，下文相对路径均指该根。唯一临时根 `/private/tmp/lifeos-p3-146-conversation-source-v1` 已经marker/权限/属主校验并清理。所有8个已知App启动PID均已退出。未接入Pilot、真实DB/正文/Vault/健康数据、Keychain、Provider或模型服务；P2中的意外进程元数据观察单列，不声称全过程所有禁止元数据观察均为零。

最小启动包、任务卡、回复模板、验收/CI治理、checkpoint模板、D-0651增量、139/140全文Review与145指定Review已读取。固定架构SourcePort章节和候选均来自 `2bd2fb43792ae7de67bc764d8eed063f1ec22824`。准备期路径缺口已由PM校正，本工程没有拿旧main替代。未调用本地模型、未转派Agent。

## 2. 用户行为与架构落点

用户在Global AI自然表达一次，原文按原始字节保留，成功后自动本地准备Context；保存失败保留草稿。草稿的requestId、observedAt随同修订持久化，重试复用同一请求；记录、类型投影、草稿提交、审计和回执同事务。Context后续失败不会伪报原文保存失败。

Today只对真实Work记录且缺少有效可用时间时问一个问题；已有获准State/Markdown答案不问。回答更新available_time并改变下一建议。暂缓明确为一小时；忽略/拒绝在同一日窗口同一缺口内抑制，沉默不产生事实。问题状态与建议反馈分开，均跨进程重启持久化。

原始记录、Current State、确认Durable Memory、AI derivation、请求Context分别存储在单一Repository。普通回答不强制反馈，AI输出不会自动升级长期记忆；“保存并记住这条偏好”是一个明确确认动作。纠正保留旧版本与supersedes，只失效相关引用，提交纠正时关闭其草稿，重启不复活旧编辑。

`candidate/application/core.ts` 提供Application、RepositoryPort、SourcePort/FixtureSource、ModelPort及历史生命周期/预算语义；`application/ui.ts`只经Application调用受控IPC，不接SQL、网络或凭据。`src/repository.rs`为Rust SQLite事务/校验适配器，`src/main.rs`接线20个原IPC名称。历史139/140文件在145入口未接线这一事实保持原样；本轮复用其生命周期、分层预算、引用失效与反馈规则并重新接线，不宣称原历史模块直接编译或重跑历史测试。

## 3. 已批准delta的实际协议映射

所有新请求外层 `{version:2, operation, payload}`，未知字段/operation/真实profile/root覆盖失败关闭。20 IPC名称未增减，但语义明确是V2增量，不能称API未变。

| 批准项 | 当前落点与约束 |
|---|---|
| D146-01/02 ConversationSave与草稿 | capture_record/save、draft；requestId与完整payload原样相等比较，异payload冲突；requests主键和turn身份唯一；用户有意再次保存相同文字使用新turn，因此允许形成不同原文。草稿revision递增；事务提交后status=committed。 |
| D146-03 单一类型权威 | records只保存原始层；memories仅明确确认；states有validUntil；derivations保存AI身份/refs/model；不双写平行Memory。仅初始化新合成库，不迁移旧库。 |
| D146-04 LocalPrepare | assemble_global_ai_context/local_prepare接收requestId、expectedGeneration及packet。conversation/purpose/budget/removedRefs由Application构造有界packet；返回included/excluded、预算、版本/授权generation。Rust复核实际内容/状态/引用，拒绝篡改及过时revision。无云端确认回执。 |
| D146-05 QuestionDecision | assemble_global_ai_context/surface_question持久化稳定缺口身份；decide_understanding_feedback/question_decision区分defer/ignore/refuse；answer通过ConversationSave同事务写原文、State、answerRef和answered。 |
| D146-06 纠正 | update_current_state或upsert_durable_memory/correct；expectedGeneration绑定旧记录版本，事务创建新版本/替代关系并失效相关packet/derivation。无实际删除入口。 |
| D146-07 SourceItem/IngestionEnvelope | capture_record/ingest；sourceId/externalId/type/version/content/mime与authorizationRef、observedAt、validUntil或无期限原因。仓储计算contentHash/ingestedAt，复核授权；UNIQUE(sourceId,externalId,version)。导入不允许confirmed。 |
| D146-08 OfflineModelCall | resolve_request_context/offline_generate仅OfflineA/B；ModelPort接收同一有限packet，不接DB。output带inputRefs、时间及usage；仓储保存modelId/outputId并重新检查来源/版本/授权。措辞可变，资产不变。 |
| D146-09 离线隔离 | 本轮main只链接repository；生产secure_credentials/deepseek源件逐字保留但不链接、不执行。设置/凭据命令在打开DB之前拒绝；NoNetwork/NoCredential端口触达即抛错。证据不只依赖显示的零counter，还检查入口接线和调用路径。 |
| D146-10 CI | tools/run_p3_146_checks.mjs只运行审查过的23项integration测试；显式任务target/TMP，locked/offline build。无旧全量Cargo tests。全局注册由PM处理。 |

requests保存完整规范payload用于相等验证，而不是只存其摘要；审计时间在audit中。JSON body表通过主键、JSON有效性和source/turn唯一索引维持持久约束，事务中同时写回执。这些是已批准语义的机械存储映射，不新增实体冻结。

预算估算为每项 `8 + ceil(Unicode字符数 / 4)`，先L1确认记忆、L2有效状态，再L3相关来源Top-K，最后复核总预算。必需层不足写前拒绝，完整原文不截断。当前是受控小集合的领域过滤/Top-K，不宣称实现了新的通用全文检索或生产语义召回。单表达200字符，用户活跃场景Work/Health各3条及1条确认长期记忆边界保留。

## 4. Source、健康与模型连续性

两个合成来源使用相同SourceItem/Ingestion/Repository/Context链。FixtureSource提供synthetic_fixture状态、discover/read与明确unsupported的sync；UI两版按钮构造内联受控SourceItem交给相同Ingestion，不提供文件选择器或任意路径读取。Markdown固定两段短文；健康固定两版睡眠时长6/8小时，使用显式合成区间与hours单位。真实Vault、图片/链接跟随和iPhone读取不可达。

版本相同且相同内容去重，异内容冲突，乱序旧版本拒绝；新版本替代旧引用。健康区间/单位/字段异常拒绝，不推测energy/pain等未知值。撤权保存来源generation并失效依赖，后续Context/Model消费都排除旧内容；重启不能复活。

实际App显示Markdown v2与健康v1的来源依据，睡眠6小时使建议加入降低负荷说明；撤权后该说明与健康依据退出。OfflineA→OfflineB→重启→OfflineA，原始7条（含历史）、4条State（含历史）、1条确认Memory、1条反馈保持一致。测试另覆盖双Adapter逐次重启及撤权/过期排除，不要求回答逐字一致。

健康可行性合同仍为：设备明确授权→字段/时间窗/单位/时区→明确导出/传输→SourcePort归一→去重/撤权过滤。真实设备可用字段、权限粒度、采集机制、后台频率、补传、断连恢复、传输安全和持续同步均未验证且未实现，属于本合同外待另行精确授权项。本轮未联网查证采集API，不宣称健康设备已连接。

## 5. L2验收矩阵

| AC | 本轮证据与实际结果 |
|---|---|
| 一次保存/失败草稿/幂等 | integration：原文字节、ack丢失后重启重试同ID、异payload拒绝、相同文本新turn、新写失败回滚；actual final-save→final-failure→final-answer，失败记录/State/审计/回执计数不变，重试只有1条新增回答。 |
| 0～1有用问题 | integration：空/无Work不问、有效答案不问、Markdown填缺口不问；actual保存项目计划问1条，回答后消失。 |
| 回答/暂缓/忽略/拒绝/沉默 | integration分别覆盖处置/重启/暂缓到期与沉默；actual final-answer、final-defer→restart、final-refuse→restart状态正确，无重问。 |
| 类型/长期确认 | integration无自动durable promotion；actual final-memory一个明确动作形成1条确认记忆，普通回答Memory仍为0。 |
| 纠正/受影响投影 | integration故障回滚、历史、无关健康State不变、旧packet拒绝、新state使旧缓存失效；actual10→18分钟，旧原文corrected，新建议18分钟；重启无待提交旧草稿。 |
| 有界有效Context | integration预算边界/不足不写/过期/请求移除/撤权/篡改文本失败；static入口不链接凭据网络模块；本地App自动组装。 |
| Source版本/去重 | integration两种Source、身份隔离、版本冲突/乱序/新版本、健康异常、撤权；actual final-sources/provenance/revoke-b来源及建议变化可见。 |
| Adapter/重启 | integration A→重启→B→A资产/反馈不变；actual最终主场景counts跨重启相等，设置保持B并可切回A。 |
| Settings/Rail/Global AI | 原styles/viewport-adapter与生产凭据源hash相等；云目录8项、本地4项可见；本轮真实路由/凭据只读隔离且明确标注，未宣称可用。桌面/窄窗口关键操作可达。 |
| 动态证据/清理 | 最终同一二进制hash，16截图+原生AX/CG几何+合成快照；26断言通过；根marker校验、已知App退出、无WAL后精确清理。 |

## 6. Evidence与复跑

- 最终自动结果：`evidence/checks-1788831561777.json`，4步exit=0；详细23/23在 `evidence/logs/1788831561777-integration.log`。Node内置TypeScript转译+执行验证，不宣称tsc类型检查。
- 最终二进制SHA-256：`ea80364e1afb2bdfdf2704a6bf77c03b27fa234ed4d46467a96d5302e371c635`。主场景PID17299、窄窗口恢复PID17984；问题场景PID18208/18332及18462/18617。launch JSON与最终app JSON绑定。后续仅新增复跑/证据工具与报告，没有改应用源或已验证二进制。
- `evidence/actual-app-validation.json`：16个final截图、26断言；`app-final-*.json/png`为当前正证据。宽窗口请求1280×1024，被桌面约束为1280×949；窄窗口700×760；PNG为2×像素。未改变显示缩放。
- `evidence/source-lineage.json`18项固定源件及 `baseline-validation.json`；`baseline/`只读留存，不参与生产代码执行。`FINAL_MANIFEST.json`为本包完整性清单，不是Frozen ABF或产品冻结。
- 复跑说明 `REPLAY.md`；只读复核 `candidate/tools/verify_manifest.py`；初始化/精确清理 `candidate/tools/task_root.py`；checkpoint记录恢复边界。
- 终局清理：`evidence/cleanup-20260908T015659.json`，全部已知App停止、专属根已删除。构建缓存与合成DB均清理，日志和截图留存工程包。

## 7. 异常、修正与限制

P2-01（已向PM披露、非阻断）：首次cargo check遗漏显式target/TMP，失败后将任务candidate内构建缓存移到批准根；一次仅进程名诊断意外返回其他运行App可执行路径元数据，未继续访问/读取/操作/清理那些路径。`evidence/build-start-deviation.json`保留事实，首次失败不作正证据。不将该观察伪写为全过程零接触，也不将其当候选P0。

包内已关闭：首次缺图标/构建环境错误、Source旧版本重放顺序、失败测试子进程清理、草稿重试时间/请求身份、纠正草稿提交状态。旧失败日志完整保留，当前23项通过；旧App截图列入 `provisional-app-history.json`排除，没有覆盖失败历史或用旧图宣称最终通过。

GUI环境恢复：PID17773原生AX列表为空但App仍可操作，标记Paused — Resumable；相同二进制和DB重新启动PID17984，完成窄窗口证据，只补受影响阶段。拒绝场景曾CUA管道中断，重连确认草稿尚未保存后继续。无代码/合同漂移，未据此判候选失败。最终无待恢复GUI缺口。

本轮是合成规则提取与离线Adapter，不宣称通用自然语言理解质量、真实模型推理、生产安全验证、真实来源接入或持续同步。145凭据工程/安全Delta暂缓/Phase C暂停保持原结论。

## 8. 角色、关卡与PM所需决定

主责Codex完成范围内实现、测试、actual-App、Evidence与精确清理。D-0653明确本L2新合成实现不默认独立评审；本任务没有自评为Independent Pass。若未来改变真实授权/凭据/删除边界或拟冻结核心实体，须由PM按新边界判断关卡。

需PM：对本完整交付作L2终局验收；核对P2-01及独立变更范围；处理task-local CI注册。执行侧不自动提交推送或合并145高风险祖先，不改架构冻结、风险或Stage。无需Key、真实数据或健康样本；不自行创建后继任务。
