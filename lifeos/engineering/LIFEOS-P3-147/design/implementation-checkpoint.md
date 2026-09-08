# P3-147 首次代码修改前实施检查点

状态：内部方案已按Revision 4授权；下列公共接口增量等待PM批准。不是Frozen Schema/ABF。固定源f56223ad92f5b86c42f4bd60303ca6c892c3f9c1，146 Manifest的219项及报告hash按Git blob复算一致；工作区启动clean。

## DTO/IPC精确映射

146现有20 IPC及version:2请求不改变。现有capture_record/ingest只接受synthetic_markdown/health且正文200字符，不能承载目录授权与完整文件。禁止伪装成原ingest。

拟新增5个IPC，外层均为严格 `{version:1, payload:...}`，内外未知字段拒绝，后端拒绝真实profile和任意root；所有identity是不透明ID，不接受UI提交磁盘路径：

| 新IPC | payload | 返回 |
|---|---|---|
| connect_source_directory | requestId:string | connectorId, grantGeneration, jobId, status；当前仅后端固定合成目录，未来真实选择器须安全Gate |
| control_source_job | requestId:string, connectorId:string, expectedGeneration:u64, action:refresh/pause/resume/cancel/disconnect | connectorId, grantGeneration, jobId?, status |
| get_source_status | connectorId?:string | connectors:[{connectorId,grantGeneration,status,jobId,discovered,processed,parsed,unparsed,failed,pending,scanComplete}] |
| authorize_source_target | requestId:string, connectorId:string, expectedGeneration:u64, linkId:string, decision:grant/revoke | linkId, grantGeneration, status；目标来自后端直接引用表，不能提交URL/path扩大范围 |
| get_source_evidence | connectorId:string, sourceRef:string, expectedVersion:u64, cursor?:string | title,mimeType,version,status,reason?,sourceIdentity,observedAt,segments:[{text,locator}],nextCursor?；配置只返回restricted状态，原件不通过IPC自动传输 |

拟对本任务内部Application SourceConnector增加discover(cursor)、read(sourceRef,expectedVersion)、refresh、pause/resume、disconnect。NativeSourcePort通过上述新IPC承载；保留FixtureSource和原回归。新来源的SourceItem内部扩展sourceType为local_file/web_reference，保留sourceId/externalId/version/contentRef/mimeType/title/metadata/contentHash语义；完整原件受控保存，局部内容经Ingestion写既有Repository的records，配置不入普通records/Memory/Context。不更改原V2 SourceItem校验；无旧库migration。

本地检索新增内部Repository查询，分页片段与source版本/授权generation绑定，经现有local_prepare与offline_generate再次校验；若需要改变这两个公共payload，另向PM报告，不静默扩展。来源相关结果必须显示“已检索到来源”，不称AI已理解，不用离线固定建议代替正文理解。

## 新合成库内表

复用146同一Connection、records/sources/packets/derivations/requests/audit。新增：

- connectors(id PK, grant_generation, state, root_ref)：根引用只后端可解引用。
- connector_grants(id PK, connector_id FK, target_ref, generation, state)：目录和外链独立授权。
- scan_entries(id PK, connector_id FK, parent_ref, cursor, scan_epoch, state)：持久分页目录队列，无总数/深度截断。
- source_files(id PK, connector_id FK, external_ref, version, identity, fingerprint, artifact_ref, parse_state, reason, seen_epoch)：UNIQUE(connector_id,external_ref)。指纹仅受控库内。
- import_jobs(id PK, connector_id FK, epoch, state, counters, checkpoint)：暂停/取消/重启；单事务最多50文件。
- source_artifacts(id PK, opaque_ref UNIQUE, mime, bytes, version)：原件0700目录/0600文件；不可执行。
- source_links(id PK, parent_file FK, parent_version, target_ref, grant_id, state, fetched_at, final_ref, target_version)：直接引用谱系；不递归抓取。
- source_segments(id PK, file_id FK, version, ordinal, locator, text, record_id)：UNIQUE(file_id,version,ordinal)，只解析非受限内容；FTS5索引为可重建派生。

每批提交文件版本/segments/既有records/失效依赖/进度/回执同一事务；故障回滚保留旧有效版本。原件先流式写不可见staging，事务成功后引用；未引用文件不计成功，重启恢复。授权CAS、唯一键、幂等冲突及回执故障注入必须测试。新库识别P3-147，不打开或迁移任何旧库。

## 已授权内部实现与资源矩阵

文本严格UTF-8；配置受限；HTML静态提取不加载资源；PDF/DOCX仅本地解析，依赖不可用诚实标环境缺口；扫描/加密/损坏明确未解析。附件原件纳入，禁执行/OCR/转写。扫描256、并发2、事务50、解析64MiB/30秒、DOCX展开128MiB；不因预算裁掉队列。Rust逐组件no-follow受控FD访问，授权前不读正文，特殊文件拒绝；符号链接目标必须重新授权校验。

Web只注入Transport，禁真实socket/HTTP/DNS；并发2、连接10秒/总30秒、5跳、解压后20MiB；每跳和连接地址复验，阻断私网/重绑定/秘密URL，非递归。不得把合成Transport成功称为真实网络能力通过。

## 关卡与写入

主责技术工程，协审视角为数据/来源、安全和体验；Gate2/3/4待本轮工程证据及独立安全评审，Gate5真实亲验未启动。按Revision4工程后由PM绑定新ABF并分派一次独立安全评审。当前只写自身工程和主交付物，运行期唯一合成根/private/tmp/lifeos-p3-147-obsidian-source-v1；禁止路径只当合同字面值，未探测。无Key、真实数据或网络需求。

## PM实施约束补充（公共接线尚待用户批准）

所有ID为1–120字节ASCII字母数字及`-_:`；version/generation/epoch为1..=9007199254740991整数，offset为0..=9007199254740991。所有requestId与规范JSON完整相等比较，同ID异payload拒绝。状态详情也校验当前grant，断开仅提供不含来源信息的断开回执。evidence sourceRef必须属于connector；cursor由后端持久化不透明ID标识并绑定connector/source/version/grantGeneration，撤权、刷新或版本更替拒绝旧cursor。

pause/cancel/disconnect均递增worker epoch；disconnect同时递增grant generation并撤销来源。worker在每次读取前、每次事务提交前校验epoch与generation，旧worker不可提交。取消保留历史并使job停在可重新刷新状态，暂停允许resume新epoch。

原件先以独占0600写入本任务artifacts staging，flush+fsync后，以不透明内容版本ID无覆盖发布，最后数据库事务原子提交引用及相关投影；崩溃窗口只会产生未引用原件，不能产生指向未完成原件的已成功记录。恢复时只识别本任务marker下本进程创建的未引用staging/原件，记录孤儿并隔离，不触碰真实资产。DB提交后回执丢失由requestId回放；DB失败保留旧版本。长文完整原件保存，切片逐段可追溯且不套用200字限制；未解析计数单列，不形成确认事实/State。

## 检索接线的精确补充（待PM一起审阅，尚未实施公共接线）

内部FTS查询已实现按当前connector grant、文件版本、record活跃状态过滤并返回至多8片段。为避免snapshot全量正文进入UI，需要为原拟`get_source_evidence`补一个严格判别联合payload：

- `mode:detail, connectorId, sourceRef, expectedVersion, cursor?`：原详情；cursor绑定来源版本及grant。
- `mode:search, connectorId, query:string(1..1024 UTF-8字节), expectedGeneration:u53`：返回最多8项`{id,text,locator,version,authorizationGeneration}`，无匹配返回空数组；配置/未解析/旧版本/撤权排除。未知混合字段拒绝。

这仍是同一拟新增IPC，但属于原提案字段补充；等待PM转达用户批准后才公开接线。新增来源records不进入通用snapshot全量返回；Application按本次查询的有限结果准备原有packet，Rust按源文件/授权再复核。原20 IPC的老客户端行为保持，新来源的内部存储不等于自动向模型披露全量。
