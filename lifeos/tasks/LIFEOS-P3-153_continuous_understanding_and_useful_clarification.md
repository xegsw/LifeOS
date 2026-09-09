# LIFEOS-P3-153 持续理解与必要澄清闭环

状态：Ready — 用户在完整合同展示后明确回复“启动吧”，一次性授权合同内离线工程、测试、动态验证、修复及PM验收。2026-09-09。P3-152已结束，不重新打开；新增真实权限与关键Schema/API仍不在授权内。

## 任务信息

唯一结果：用户直接提问，LifeOS复用已有相关资料；确实存在影响建议的信息缺口时，在对话中提出一个必要问题。用户回答或纠正后，后续建议使用更新后的状态，重启与更换测试ModelAdapter后仍保持来源和状态连续。

主责：Codex工程，单一执行会话；PM负责合同与验收。建议复用已停止写入的P3-152工程会话，避免重复上下文与双写；若执行环境不可用，由PM另行指定，执行侧不自行转派。不指定模型。能力要求：Rust/Tauri、TypeScript、SQLite合成数据、离线测试、按需原生App验证。

风险：L2，仅离线合成增量，不修改真实权限、凭据或数据。独立评审及复核按用户指示继续暂停；保留包内测试与PM验收，不宣称Independent Pass。真实启用不在本轮Pass内，不能把合成闭环称为真实用户闭环。

## 累积基线与直接输入

- 工程基线：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-152/settings-baseline-restoration/candidate`，163项完整本地候选；只读继承，不修改原件。
- 文件身份：上级FINAL_MANIFEST.json的SHA256为`21fc8b8e31ea15191deaf01f228c206d38fc1f60c88cacd08646725370132b81`；工程启动先验证所列候选文件，不能只凭目录名。
- Git代码文档快照：`2ee77475795b9c33ce2799be08043544ac462e63`，分支`codex/p3-147-152-source-sync`。快照未包含完整Evidence，不用其代替本地完整输入。
- 构建入口：候选Cargo.toml与现有工具；交付必须由完整累积源码构建，不提供单项样机冒充产品。
- PM验收：`/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/reviews/LIFEOS-P3-152_pm_final_review.md`。
- 工程说明：b3f6树`lifeos/deliverables/LIFEOS-P3-152_settings_baseline_restoration.md`及`LIFEOS-P3-152_final_closeout.md`。

| 必须继承 | 本轮回归要求 |
|---|---|
| Shell/Settings/既有中文视觉 | 不换导航、配色、页面结构；设置入口与可用功能不变 |
| Provider与凭据生命周期 | 保存/测试目录/选择/启用分离，掩码尾号、加密持久化、无Key TTL；仅合成验证，不接触Keychain |
| 来源与健康导入/查看/检索 | 完整接线保留；合成导入重复处理、来源版本、有限披露验证 |
| 对话/草稿/保存 | 草稿失败保留、幂等重试；普通回答不要求逐条反馈 |
| 云端披露守卫 | 保留现有真实实现，本轮不启用；合成验证预览失效、确认绑定、无自动重发/fallback |

## 允许范围与架构

工程输出拟定为`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-153/`；仅在该目录复制完整候选、增量实现及合成测试，不修改P3-152历史。唯一合成运行根拟定`/private/tmp/lifeos-p3-153-continuous-understanding-v1`，0700根、0600所有权marker与合成文件；若目标已存在且所有权不明，不读取内容、不覆盖，回PM处理。合同获批准前不创建运行根。

复用现有Source、Memory、Context Resolver、Feedback、ModelPort与协调层。UI → Application → Domain/Capability → Ports → Adapters；UI不访问SQL、凭据、厂商SDK或网络。不新增Relationship Engine、第二套记忆库或全仓重构。

先完成现有能力/接线映射，只补缺口：原始表达、短期状态、已确认长期信息、AI候选理解、单次上下文身份分离。复用现有持久化结构和命令；任何新增公共IPC、关键DTO或持久化Schema需求先提交最小差异与兼容方案给PM，不偷偷新建表或改协议。可继续不依赖该变更的测试和实现。

澄清仅在用户当前交互中触发：先检查已有获准信息，再判断缺口是否影响建议；每次最多一个问题。回答、暂缓、忽略、明确拒绝分别记录；沉默不写作确认、拒绝或状态变化。已解决问题不重复问；暂缓需满足记录的重试时间/条件，忽略本次不继续追问，拒绝不主动再问，除非用户明确重开。不得因定时器自动联网。

用户明确保存一次即可，不加同义勾选框；回答更新正确的短期状态或候选理解，AI推断不得自动成为长期事实/决定/行动。重要记录有来源、时间、有效性与纠正关系；纠正使受影响投影/上下文缓存失效，不覆盖全部历史。保留既有删除/撤权不复活语义，不新增删除权限。

本地确定性过滤优先，按授权、领域、时效、版本及预算选择少量相关信息；沿用现有预算，不全库总结、不全量历史发送。FTS按已有实现复用；不要求向量库。正常请求不增加一次模型预总结。ModelAdapter替换仅保证系统资产连续，不保证回答内容相同。

## 禁止范围

不访问任何真实Pilot、来源目录、ZIP、健康/对话/配置数据库、附件或Keychain，包括exists/stat/hash；不调用真实Provider、网络或局域网模型。不关闭或替换用户当前App，不迁移、清理或覆盖真实数据。新App仅在合成根演示，明确离线测试身份，不冒充真实启用产品。

不改模型列表选择方式、Provider集合、凭据TTL、设置保存行为或全局视觉；不做看板、卡片墙、通知中心、麦克风、后台采集、多Agent或新来源接入。不改变Frozen资产、风险状态或Stage，不自动合并高风险分支，不启动后继。

## Acceptance Contract

| ID | 必须结果 | 验证 |
|---|---|---|
| AC-01 | 全量继承既有产品，不丢Settings/来源/健康/对话接线 | 基线文件差异、接线矩阵、组合回归 |
| AC-02 | 用户直接提问，无手工组装上下文入口要求 | UI/Application/Host合成端到端 |
| AC-03 | 已有获准来源可回答时不重复询问 | 正负fixture；未授权来源不得被使用 |
| AC-04 | 有价值缺口才提问，每次最多一个 | 不影响建议/已答/已拒绝/暂缓/忽略反例 |
| AC-05 | 回答改变正确状态及后续建议依据，不自动长期化 | 原始表达/Current State/Understanding身份与来源断言 |
| AC-06 | 纠正后不继续使用旧理解，历史有效时间可区分 | 纠正谱系、受影响缓存失效与未受影响投影保持 |
| AC-07 | 保存一次、失败保留草稿、重试不重复写入 | 故障注入、并发/重复操作与幂等断言 |
| AC-08 | 关闭重开后状态/来源/问题抑制一致 | 独立进程重启合成数据库，不用同进程模拟替代 |
| AC-09 | 切换两种测试ModelAdapter后资产及授权连续 | 同一合成数据集、上下文refs与权限结果对比 |
| AC-10 | 主动澄清零未授权网络，披露预算和确认守卫不退化 | 拒绝网络适配器、请求计数、stale/撤权/版本变化反例 |
| AC-11 | 保持既有美观简便，不遮挡输入与动作 | 代码/布局差异优先；桌面和窄窗合成关键状态按需检查 |
| AC-12 | 完整候选可构建、有单命令复跑与诚实报告 | 构建、回归、检查点、变更影响矩阵与五类计数 |

Pass：AC全部完成；范围内P0/P1/Unknown/Not Implemented为0，P2逐项解释是否不阻断。独立评审暂停单列，不写成通过；真实闭环尚未启用是显式范围外，不假报完成。

## Evidence、CI与恢复

L2结构化正负路径、重复/重启及失败关闭Evidence。基线差异→影响面→行为测试→必要视觉，禁止截图代替功能测试。重跑原设置127项中可用回归并逐项说明变更或不适用原因，不按数字凑数。新增确定性用例提供CI可用入口；在未确认CI实际运行前不声称CI全绿。

`checkpoint.json`记录候选摘要、阶段、resume_from；锁屏/截图/runner暂不可用为Paused—Resumable，只恢复受影响阶段。候选变化从最早受影响测试阶段继续；只有越权接触、历史修改或不可分离污染才触发不可恢复失效。同范围缺陷、Evidence修补、Manifest、复跑均在本任务收口，不拆微任务。

## 输入补读和交付

启动读最新AGENTS、CURRENT_STATUS、本卡、SESSION_REPORT_TEMPLATE；直接输入如上。定向读取ACCEPTANCE_GOVERNANCE/CI_CD_GOVERNANCE的累积产品、风险分级和可恢复执行；架构V1.0的Memory/Context/Source/ModelPort及授权章节、IA的全局对话；PM_OPERATING_MODEL/ROLE_MATRIX/STAGE_GATES关于公共Schema/API与权限变更的审批边界。相关路径或合同缺失交PM，不自行扫真实目录或重读全历史。

交付：b3f6树`lifeos/deliverables/LIFEOS-P3-153_continuous_understanding_and_useful_clarification.md`；工程目录内candidate、tests/evidence、inheritance-map、impact-map、checkpoint与复跑入口。最后一次完整交付，已知同范围缺口先包内处理。

真实接入需另行明确复用目标、读写动作和兼容性；不自动继承P3-152运行权限。新增用户结果/真实目标/权限/关键Schema/API或冻结变化才触发重新确认，不将普通测试修复拆成新任务。

## 一次性确认

### 已批准协议增量（D-0652）

用户明确回复“允许协议补充”。同任务授权`decide_understanding_feedback` version 4的`clarification_decision.decision`新增`reject/reopen`，questions既有JSON状态新增`rejected`、显式重开回`pending`，使用既有feedback记录动作和时间。问题ID加入basisTurn实例后缀，仍兼容旧字符串ID读取及决策，不覆盖旧问题。按领域/字段获取最新有效生命周期，不能因固定八条历史窗口使拒绝失效，公开响应预算不扩大。现有对话内可增加“不要再问”及拒绝态“重新讨论”；不改Shell/Settings。

不新增IPC、请求字段、SQL表或迁移；旧ignore/defer兼容，普通问题不能隐式重开。拒绝不写为个人状态或长期记忆。离线边界、真实资产禁触、冻结/Stage不变。从工程checkpoint恢复，仅重跑受影响阶段。依据：b3f6工程树P3-153/design/protocol-delta.md；该文件原待决记录可保留，由工程新增批准状态说明。

### 精确补读定位（PM澄清，不扩大合同）

- `/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/architecture/LifeOS架构基线V1.0.md`：§2、§3、§5、§6、§7、§9、§10。
- `/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/architecture/LifeOS高保真原型IA-V1.0.md`：§4、§8、§9、§11 Flow B/C/E、§12。
- 上述原则不授权重绘已验收UI或恢复历史手工组装负担；具体增量以本合同为准，实质冻结冲突须披露。

用户已确认本合同，授权上述离线工程、合成动态验证、测试、同范围修复及PM验收；不授权本卡明确排除的真实操作。PM派发至原工程会话顺序执行，不与P3-152混合写入。
