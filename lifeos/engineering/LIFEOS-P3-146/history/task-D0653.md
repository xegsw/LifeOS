# LIFEOS-P3-146｜自然对话、记忆更新与授权来源合成集成闭环

状态：Authorized / Engineering Start（D-0653）。风险：L2合成离线实现；含已批准版本化API/全新合成库Schema增量，不包含真实安全能力启用或架构冻结。用户已在完整准备报告与接口/存储增量展示后回复“同意”，授权同任务实现、测试、集成、Evidence、包内修正和PM验收。不继承Pilot授权。

## D-0653执行合同定稿（取代下文准备阶段禁止工程条款）

已批准精确方案：/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/deliverables/LIFEOS-P3-146_natural_conversation_memory_and_source_integration.md，第6–10节，准备版本SHA-256 98b151d3b30908079c6e76cc236a93d03f0a6cbdba5796ab0739a54cbddfd6b5。启动前保全该准备版本为任务内只读历史，后续更新交付物不得覆盖唯一合同依据。D146-01～10、六项V2 DTO、持久化唯一约束及三种事务、问题处置/草稿/来源预算均纳入本卡。允许机械命名对齐，不允许静默删减语义或扩权。

单一执行负责人：P3-146原准备会话01a07e77-dba3-7bc0-a2a7-e69f01c51347；在自身/Users/xxe/.codex/worktrees/5ed8/No.2创建codex/l2-p3-146-conversation-source分支（现有同名分支不得覆盖），只写lifeos/engineering/LIFEOS-P3-146/、本任务交付物；准备报告只读历史亦置于该工程根。唯一临时根/private/tmp/lifeos-p3-146-conversation-source-v1，任务所有权marker普通0600、根0700，先确认未被占用；异常不补造所有权或清理。构建/夹具/测试缓存限定新根；旧145根与所有Pilot零接触。

按架构V1.0以TypeScript Application/Ports协调、Rust受控仓储/IPC适配复用历史算法；单一Memory权威。保持20 IPC名称，明确V2语义是新合同，不伪称API未变。只初始化全新合成库，不迁移旧库。生产凭据实现只读继承、不可执行；本地编译profile与NoNetwork/NoCredential隔离在任何设置/凭据读取前生效，禁止运行旧全量测试/runner。未知输入、任意root、真实profile和隐式发送均失败关闭。

本轮不要求另开独立评审：当前验收为新合成离线实现、非生产Schema迁移/冻结，使用本卡L2正负例与PM定向核验。若实现必须改变真实授权/凭据/删除安全边界或拟冻结核心实体，停止该增量交PM，不能借本次同意免除适用高风险关卡。145安全Delta仍暂缓，真实Gate仍暂停。

执行侧交付task-local CI runner和注册建议，不改全局CI/PM账本。不自动提交推送或合并包含145高风险祖先的分支；终局PM核对独立变更范围后再依治理决定。GUI阻碍按checkpoint恢复，不重跑无关阶段。原卡以下准备阶段说明保留历史，当前以本定稿执行授权为准。

## 唯一用户结果

用户自然记录或回答一个有价值的澄清，LifeOS结合已有来源形成可追溯、可纠正的当前理解；后续建议解释变化，关闭重开和更换测试模型后资产保持一致。把实现、交互、测试、集成、Evidence和同范围修正放在一个任务，不拆治理微任务。

## 固定事实与依赖

- Source Port规范固定输入：仓库/Users/xxe/.codex/worktrees/d510/No.2，commit 2bd2fb43792ae7de67bc764d8eed063f1ec22824，Git路径lifeos/architecture/LifeOS架构基线V1.0.md，第100–103行及所属架构边界章节。使用git show读取固定blob；不要假定PM工作树存在同文件。该规范定义职责与SourceItem候选字段，并非已冻结的完整DTO/Schema；所需精确字段增量应在本次准备报告明确提出，交PM确认，不自行当成已有实现。

- 产品为以人为主体的个人操作系统；架构V1.0不变。直接依据：/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb/lifeos/architecture/自然对话与记忆治理增量说明.md（D-0651）。
- 139/140复用核验输入（全文）：/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-139_pm_final_review.md；/Users/xxe/Documents/No.2/lifeos/reviews/LIFEOS-P3-140_pm_final_review.md。这里只证明报告声明的历史能力，当前代码实现从固定145候选定向核对，不要求重建或重跑历史。
- 最新145 PM Review输入（全文）：/private/tmp/lifeos-p3-145-pm-worktree-DZGZJb/lifeos/reviews/LIFEOS-P3-145_pm_review.md；该Review截至a55窗口增量，后续2bd2fb43凭据工程修复及安全复核暂缓状态以本卡和D-0652为准，不把旧Review外推到新凭据实现。
- P3-145候选只读输入：/Users/xxe/.codex/worktrees/d510/No.2，commit 2bd2fb43792ae7de67bc764d8eed063f1ec22824。不得称为最终Accepted；凭据兼容工程完成，安全Delta按用户决定暂缓，Phase C暂停，真实闭环未关闭。
- 新任务不能依赖该候选的真实凭据/Provider能力已通过。离线复用须验证接口和合成基线；缺失输入报告PM，不以旧main替换。
- 历史139/140能力复用，不重建第二套Memory、Relationship Engine或World Model。

## 完整范围

1. 一次保存原始表达，保存失败保留草稿，重复/超时重试幂等。
2. 本地自动准备有限、有效、获准上下文，移除日常手动组装负担；保留真实云端逐次披露合同，当前零网络。
3. 只对实质影响建议的缺口提出最多一个问题；已有有效来源能回答不问。回答、暂缓、忽略、拒绝、沉默状态分离，跨重启抑制无意义重问。
4. 保存回答的来源、时间、类型；Current State、确认Durable Memory、AI候选理解、原始记录、请求上下文分离。明确长期保存动作不叠加同义勾选；AI推断长期化仍需确认。普通回答不强制反馈。
5. 纠正保留历史并更新受影响投影；过期/归档/删除语义不混淆，不新增实际删除能力。
6. 同一SourcePort合同接入任务内合成Obsidian Markdown和模拟健康数据，验证来源/时间/版本/去重/撤权排除。不得读取实际Vault或iPhone数据；健康采集方式给出可行性合同与未验证项，不能宣称持续同步。此项与对话共用Memory/Context，不等待对话全部完成再设计。
7. 两个离线ModelAdapter验证资产/反馈连续性，不要求回答逐字一致。

## 允许与禁止

准备阶段只读指定代码、治理和合成Evidence，可在新任务自己的工作树写计划及交付草案。工程拟定唯一写入根lifeos/engineering/LIFEOS-P3-146/，交付lifeos/deliverables/LIFEOS-P3-146_natural_conversation_memory_and_source_integration.md；合成临时根/private/tmp/lifeos-p3-146-conversation-source-v1，启用前必须纳入最终合同并做marker所有权校验，不使用旧根。

禁止访问任何Pilot、真实DB/正文/Vault/健康数据/Keychain/凭据；禁止网络、Provider、模型服务、录音、通知、后台采集、真实来源同步、云端自动补齐/发送、迁移或清理个人资产。P3-145和历史候选只读。不得改Frozen架构、Settings/Provider基线、权限、风险、Stage或自动合并高风险祖先。

UI→Application→Domain/Capability→Ports→Adapters；UI不直连SQL/网络/凭据。单一执行负责人管理共享DTO、Schema、Migration、IPC。优先既有接口；需要关键合同变化时提出精确delta交PM，不私自修改或降级功能。

## Acceptance Contract

- 一次保存成功；失败草稿不丢；重复重试只写一条。
- 已有获准来源可回答不问；无价值不问；最多一个问题；暂缓/忽略/拒绝/已答跨重启有效，沉默不改变事实。
- 回答更新正确类型并影响下一建议；纠正后旧理解退出当前使用，历史和来源可追溯，无关投影不变。
- 长期确认与AI候选分离；临时状态不永久化；有效时间明确。
- 自动本地Context有权限/有效性/预算过滤，过期/撤权不复活，网络次数为0。
- 合成Markdown与健康SourceItem版本/去重/来源关系正确；不把导入当用户确认或持续同步。
- 重启和两个测试Adapter切换，资产、反馈与有效上下文保持一致。
- Settings、窄图标Rail、Global AI及已确认凭据合同无静默回退；关键操作在实际Tauri可达。
- P0/P1/Unknown/合同内Not Implemented为0；非阻断P2逐项披露。合成通过不外推真实能力。

Evidence为L2正负路径、幂等/重启、来源及Adapter切换矩阵、定向actual-App关键流程。确定性检查进CI，GUI环境问题checkpoint恢复，截图错误只补相应Evidence。独立评审不默认触发；权限、凭据、删除或关键Schema实质变化先交PM判断，不能将P3-145待复核写成已通过。

## 准备阶段交付与后继

先核实新工作树/分支、完整最小启动包、139/140既有能力、145准确输入和接口约束；提交可执行完整合同delta与缺口表，暂不工程。主责会话只维护专项产物，不更新PM账本。禁止自行转派。

最终结果仍是一项完整实现任务；真实Obsidian目录、健康采集机制/字段/时间窗/传输权限与真实模型启用另按精确授权处理，不自动创建后继。用户不需要再从GitHub/Linear重新选来源。
