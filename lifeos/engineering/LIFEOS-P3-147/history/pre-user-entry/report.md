# LIFEOS-P3-147｜Obsidian只读来源接入与对话记忆集成

## 当前结论

**IR-P0-147-001 同合同工程修正与受影响验证完成；原独立评审 Rework 保留，等待 Independent Delta、原未完成8行、真实亲验与PM终局。** 本报告不宣布真实能力、Frozen Schema、风险关闭或Stage提升。

任务卡：`/Users/xxe/.codex/worktrees/5ed8/No.2/lifeos/tasks/LIFEOS-P3-147_obsidian_readonly_source_and_conversation_memory_integration.md`，顶部公共接口批准及Revision4优先。原待批准报告/候选/Manifest在`lifeos/engineering/LIFEOS-P3-147/history/pre-public-api/`保全。当前不再等待五项接口批准。

## 实现与边界

原20项IPC保持version2；新增获准的连接、任务控制、状态、目标授权、依据详情/搜索5项version1，共25项。未知/混合字段、不安全整数和非法ID拒绝；UI不能提交任意路径/URL。目录、目标grant与worker epoch、幂等回执及投影使用同一合成仓储，授权和回执原子提交。没有旧库迁移。

Settings → 数据与隐私 → 来源可连接本任务合成目录，自动扫描/导入、显示部分失败、暂停/继续、取消/刷新与断开。Memory提供最多8个相关片段、完整原文分页及标题/时间/版本/定位。详情自动定位到正文，避免Global AI浮层遮住初始阅读位置。自然表达仍一次保存并保护草稿，随后把有限匹配来源送入既有预算和权限检查；原始文件不自动成为确认长期事实。

原件流式保存在自有根的artifacts，解析临时文件在.runtime；配置受限，未进入普通records、snapshot或模型上下文。根/目录0700、文件0600不等于加密。读取用根内逐组件FD、no-follow、类型与前后身份复核。内部目录链接防循环；bookmark别名仅读归档元数据后再次做根边界校验。扫描分页256、无总篇数/深度旧上限、事务最多50；目录导入串行且不超过并发2上限。解析64MiB采用RSS/峰值/输出监测与失败关闭，**不声称macOS硬内存沙箱**；30秒时限，DOCX展开预算128MiB。

直接外链经独立目标授权后读取两类明确合成目标；Web复用注入Transport，最多2并发、连接10秒/总30秒、5跳、解压后20MiB，每跳目标/IP复检，无递归。没有真实HTTP/DNS/socket实现；无Provider、Keychain、真实目录/DB或旧Pilot接触。固定合成映射不是开放真实目录选择器或任意网址访问能力。

## PM预评审后的双根Closure

原交付把根分散硬编码到engineering root，无法在原卡允许的independent-review root运行未修改候选。PM要求留在同合同修正；不新增IPC或真实权限。原259项工程文件与报告由固定提交`e5cb31a3072b8fd36b28e462404adde193128a55`保全到`history/pre-root-closure/`，不改写旧Manifest/Evidence。

`candidate/root_profiles.json`为唯一精确根清单；显式构建profile `engineering`或`independent-review`，编译后根固定。运行时profile不符、根override、marker身份/权限不符、runtime/fixtures链接或权限不符均失败关闭。原engine marker保留，新review marker使用独立owner，不能互换。Repository、FileGrant、worker、target、parser临时文件、Python/Node/Swift及App启动器统一接线；`--profile-info`为无文件访问的编译身份诊断，不是新增IPC。UI、25 IPC、Schema、Cargo.lock及Provider源码无语义变化。

本会话仅使用工程根动态验证；review profile只纯配置和编译，不访问、stat、创建或清理实际review根。REPLAY提供固定40位Git提交→逐blob/hash验证→review-owned源码/helper/缓存/DB/App/Evidence的独立运行入口。该入口的review根动态执行留给独立会话，不借本工程自检宣称独立通过。

## IR-P0-147-001 artifact安全Closure

原固定提交 `640ebb6fe8d87398a05940b30f1263dad157dfa0` 的target artifact子目录链接可被字符串路径create/chmod跟随，导致哨兵0750变0700并写入，仍报fetched。这是有效候选P0，不是环境或Key问题。原566项工程文件逐Git blob归档在 `history/pre-artifact-closure/snapshot.tar.gz`，附旧Manifest、旧报告、lineage及原review/runner/results；旧历史不改写。

新增 `artifact_io.rs` 持有从根逐组件打开的目录FD链；mkdirat/openat相对FD创建，O_NOFOLLOW、O_EXCL、0700/0600及inode/owner/mode检查，不chmod既有目录。Web与local target、worker staging、parser stdin/stdout和缓存读取、最终发布与recovery均使用持有FD；发布从staging FD复制到排他新文件，sync及验证后才提交数据库，不按路径重开staging。恢复使用两个目录FD间排他renameatx_np，不覆盖既有文件。

确定性TOCTOU测试在生产检查与操作之间替换祖先/文件：FD操作至多作用于原持有inode，随后边界拒绝，不跟随替换链接或修改哨兵。10项Web/local控制、目录链接、最终文件链接、staging链接、DB回执故障覆盖内容和权限不变、失败无fetched；7项Rust新增覆盖祖先替换、parser、发布与隔离。原review反例2项仅适配到工程自有根执行，不能作为Independent Pass。

失败发布或DB失败可保留无数据库引用的孤儿文件，待已有recovery处理；不声称文件系统与SQLite间有对任意同UID并发进程的全局原子事务。测试哨兵和所有写入仅在工程自有合成根；实际review根及真实根未访问。UI、25IPC、Schema、Provider和root配置未变。详细修正与限制见 `design/artifact-safety-closure.md`。

## 实际格式支持

| 格式 | 当前行为 |
|---|---|
| Markdown/UTF-8文本 | 完整原件、连续分段、链接及定位；未知编码明确未解析 |
| JSON/YAML/TOML/INI等配置 | 受限原件；正文不通过检索/上下文自动披露，不执行配置 |
| HTML | 本地正文/标题/直接链接；不运行脚本、iframe、表单或远端资源 |
| PDF | 本机pypdf离线正文及页码；无文本层标需要OCR，加密不破解 |
| DOCX | 本地段落；拒绝穿越、实体及展开超限，不执行宏/嵌入对象 |
| 图片/音视频/其他二进制/可执行文件 | 不可执行原件保留；明确正文未解析，不做OCR/转写/模型推断 |
| 符号链接/bookmark别名 | 根内实际目标复核、防循环；不安全、损坏或不可读目标失败/待授权，不猜测或越界 |

合成夹具有意包含坏编码和不可解析附件；界面的未解析/失败计数是预期负路径，不可描述成全量正文解析成功。

## 验证与原生App

本次artifact安全Closure实际复跑65项通过：Rust23、Application/继承31、目标边界10、公共IPC生命周期1；另用原review runner在工程根适配复现2例，正常与攻击均符合预期。显式复用未改解析11、Web策略14、根profile4，共29项历史结果；组合自动回归94项，原反例2例另计，不能称96项新测。当前review profile只做 `cargo check --tests --locked --offline`，通过且未接触review运行根；原四项构建门证据复用。格式和当前离线构建通过。证据路径见AC矩阵。

覆盖规模越旧上限、暂停/取消/恢复、原件身份替换/缺失、配置诱饵、预算失败、receipt故障回滚、目标父版本/撤权、旧packet重放、刷新后旧cursor拒绝。检索是有限词项匹配，不宣称语义向量检索或通用模型理解。

最终运行二进制SHA256：`82d3de671bfbe855ab642daca8c8c9d1d4942f890bd7afdf4e43c2b22a236a64`。直接启动PID47688（1280×949桌面）和47780（700×760窄窗口）形成最终同名AXWindow→AXWebArea→窗口截图/几何链；窗口从**该PID的AXMainWindow**读取，没有借用系统前台或别的PID。最后截图见`app-artifact-desktop-detail.*`、`app-artifact-desktop-disconnected.*`、`app-artifact-narrow-restart.*`、`app-artifact-narrow-empty-search.*`。

早期原生步骤已验证自动导入、保存自然表达后3条依据、具体合成网页目标正文、暂停/继续及取消/刷新。此次artifact Closure重新验证新binary接入、两类目标正文获取、检索、原文、断开和重启，不重跑未改的全部早期视觉矩阵。原先空白/AX无窗口及CUA noWindowsAvailable等记录保留；恢复后补取最终构建证据，未借环境失败重写历史或虚报通过。CUA自动重启的PID33031未用于正证据，已核对自身可执行路径后停止。

所有已知本任务App PID已停止；合成根及可操作App保留供PM复现，没有执行物理删除。App：`/private/tmp/lifeos-p3-147-obsidian-source-v1/LifeOS P3-147.app`。启动、首次夹具准备、离线复跑与marker清理入口见`lifeos/engineering/LIFEOS-P3-147/REPLAY.md`。

## 角色、关卡及未关闭事项

主责技术工程；数据/来源、AI信任安全、体验为执行侧检查视角。Gate2/3/4的合成工程自检证据已提交；原独立安全评审已发现有效P0并判Rework；本工程不能覆盖其结论。PM需将原Frozen ABF绑定新固定候选，安排Independent Delta和原未完成8行；真实亲验Gate5及PM终局仍Pending。本执行报告不冻结资产。

IR-P0-147-001的工程修正自检通过，但独立关闭仍待确认；原评审P0=1及Not Implemented=8保持历史事实，不将未执行的独立行计为通过。已声明的不支持格式、未启用OCR/转写/真实网络是合同边界，不包装为已实现。非阻断P2：继承SPA切页时可能保留滚动位置；可滚回页首，新详情入口已自动定位，此既有导航体验可进入Backlog，非本次来源授权/正文正确性缺口。

需PM：核对修正包、完整diff与逐行矩阵，绑定新固定候选并安排Independent Delta及原未完成8行；独立Pass后再按用户授权安排真实亲验。当前无需Key，不启动后继任务，不修改PM账本，不推送或合并L3分支。

## 交付与溯源

工程根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/`。固定146来源commit `f56223ad92f5b86c42f4bd60303ca6c892c3f9c1`，219项原Manifest和原报告hash已按Git blob验证；凭据生产文件保持逐字一致且不链接执行。

包内包括candidate、实施检查点及release说明、原始失败/成功Evidence、AC矩阵、checkpoint和非自指FINAL_MANIFEST。`verify_release.py`及内存内Manifest反例只验证完整性/证据关联，不自授PM/独立评审结论。当前工程输出与历史快照分开保全。
