# P3-148 离线验收与一次真实阶段批准清单

当前全表 **Not Run / 设计阶段**。不是失败，也不是工程通过。合成工程启动、关键API/存储合同批准及独立评审安排由PM决定。不得执行被平台拒绝的旧测试、改写其名称或更换执行方绕过；验证入口仅未来在许可范围内实现。

## 合成夹具合同

唯一拟工程根 `/private/tmp/lifeos-p3-148-source-ai-v1`，本轮没有创建/探测。未来根采用148独立marker、0700/0600、固定编译profile，拒绝runtime任意路径注入；所有源、DB、OS模拟材料、日志及App都限此根。不得复制真实DB/文本/缓存或复用147根。评审自有根须由PM另行精确指定，本设计不自行创造/访问。

F01：纯虚构中文“纸鹤项目星期四整理图纸”、英文paper-crane资料，以及完全不相关园艺段落；长度/版本/locator固定，包含4个匹配候选证明Top3、中文双字/英文词及稳定排序。

F02：同段v1/v2、旧grant、撤权、不同connector、不同epoch、missing/restricted/unparsed附件、外链子connector、虚构密钥赋值与私钥头、来源内“忽略此前规则”文字。全部新造字符串，不读真实秘密；不运行文件逃逸/网络攻击。

F03：边界长度0/2000/2001 scalar、UTF-8上限、3/4片段、800/801窗口、总2400、序列化字节刚好/超限、多条纠正超预算、零词项/零匹配。

F04：从固定147建表文本生成的空合成SQLite及虚构rows；不运行旧App、不复制旧DB。另造缺表/缺索引/未知schema、prepared/committed/dispatching/succeeded/cleanup_pending状态供恢复。全部故障注入为进程内Adapter可控失败。

F05：MemoryCredentialPort记录精确service/reference调用；虚构API Key，只在内存有OS key；测试AES-GCM nonce/tag/AAD错误、OS缺失/锁定、DB提交失败、替换/删除各崩溃窗口。旧144/145前缀仅作为字符串送入纯验证器，断言OS调用数0，不访问旧Keychain。

F06：RecordingModelPort脚本化success/401/空列表/无效模型/超限/timeout/响应后DB失败；记录虚构完整body、调用次数、选定目标/参数。同步屏障覆盖重复点击、配置/撤权与提交竞态；没有真实DNS/socket/curl。

F07：合成会话多轮、答案C1/C99/HTML/远程图片引用、纠正后重启、50/51条分页、草稿失败；桌面与窄屏沿用固定UI样式，数据完全虚构。

## A01–A09 完整矩阵

| 检查ID | 合同 | 正/负/重复/恢复与Pass断言 | 夹具/证据 |
|---|---|---|---|
| T01 | A01 | 草稿写入→提问原子一次保存；失败保留编辑器文本；未成功不显示已存 | F03/04，事务计数与UI状态 |
| T02 | A01 | 同request同payload、同turn跨request回放；异文/跨会话/旧revision拒绝，无覆盖；保存后重启不重复 | F04/07，rows/receipt |
| T03 | A02 | 中英文相关命中/稳定Top3，预算裁切准确定位；零匹配明确no_match，零模型调用 | F01/03，选段与调用数 |
| T04 | A02 | 旧version/grant/epoch、撤权、配置、未解析、外链目标、疑似秘密不进入包 | F02，输出集合为空或受限 |
| T05 | A02/A03 | 多字节/边界预算、JSON开销计入；相关纠正溢出明确失败；无后台加载全库原文 | F03，字节预算/查询边界 |
| T06 | A03 | 预览显示全部系统/问题/片段/纠正/目标/模型/预算；Transport收到逐字同bodyJson | F01/06，合成字节相等 |
| T07 | A03 | 编辑/移除/取消/过期/重启/来源或配置变更，旧token均零发送 | F02/06，代数/调用数 |
| T08 | A03/A04 | 伪造token、UI自填prompt/path/provider、未知/重复字段、混版本严格拒绝且副作用零 | F06，typed契约拒绝；不执行外部攻击 |
| T09 | A04 | 保存凭据零网络；用户test仅models；select/enable无发送；确认仅固定DeepSeek chat | F05/06，分阶段调用轨迹 |
| T10 | A04 | other provider/model、未test/未enable、旧凭据revision均拒绝；NoNetwork构建不能靠env开真实路由 | F05/06，纯模式检查 |
| T11 | A05 | 两次点击/两个request共用preview只一次调用；dispatch事务失败零调用 | F04/06，屏障+调用计数 |
| T12 | A05 | 超时/断网/崩溃点/回答落库失败为outcome_unknown；重启/轮询零重发；人工新预览才可新尝试 | F04/06，恢复轨迹 |
| T13 | A05 | 成功/401/模型错误/空响应/超限状态可见，错误不返回正文，答案不丢在后台 | F06/07，UI+结构错误 |
| T14 | A06 | C1只映射提交集；C99不做证据；HTML/远程图片纯文本；未知引用计数可见 | F07，转义与引用集合 |
| T15 | A06 | citation点开同版本本地段；新版/撤权拒绝冒充原引用；回答仍confirmed=false | F02/07，版本关系 |
| T16 | A07 | helpful/reject非必填不变用户事实；correct原文/feedback/失效原子提交，只影响对应依赖 | F04/07，依赖前后对比 |
| T17 | A07 | 纠正后重启不复活旧理解、下次预览带对应纠正；旧revision/他人citation拒绝且不部分写入 | F07，跨进程恢复 |
| T18 | A08 | 8云+4本地目录/导航/来源检索/详情/高保真样式不回退；真实148扫描禁用准确标注 | F07，静态目录及合成App |
| T19 | A08 | AES-GCM跨重启持久；独立OS模拟key；tag/nonce/AAD/旧service失配失败，不降级 | F05，密码学与Port调用轨迹 |
| T20 | A08 | replace/delete各崩溃点保留待处理；仅用户明确recover_credentials/保存/删除后按已知148引用恢复；recover_credentials回放不再调OS；Secret不入receipt/log/snapshot；cleanup_pending诚实 | F05，纯模拟Port，含新operation严格DTO与用户动作轨迹 |
| T21 | A08 | 只打开已有结构库无DDL/seed/扫描；缺库不CREATE；新provider库只在明确保存动作后创建 | F04，SQL/Port调用轨迹 |
| T22 | A08 | 旧25IPC注册/可达操作回归，第26副作用入口单独契约；新旧kind隔离，分页不全量暴露 | F04/07，契约清单 |
| T23 | A03/A04 | 148协调器内撤权先于许可消费点零调用；晚于消费点结果stale，不承诺召回；多个遵守锁的148实例冲突拒绝打开；不证明与147互斥 | F06，确定性屏障/148实例模拟；不运行或探测147 |
| T24 | A09 | 结果分别记录synthetic/GUI/user/security；无真实正文hash/截图/Evidence；缺项保留Unknown/Not Run | 全包元数据结构自检 |
| T25 | A05/A08 | 新App启动、会话恢复、read_settings均零OS查询/创建/删除及零网络/扫描；本地激活后仅显示待恢复，禁止后台OS清理；准备中失败不丢已存问题，busy结束可继续 | F04/05/07，含prepared/cleanup_pending的启动及被动读取轨迹；显式OS恢复另见T20 |

T01–T25均由工程自检形成实际结果，当前不写PASS。独立评审需自有设计/夹具/证据和新边界授权，不能以这张矩阵或工程PASS替代。旧安全测试遭平台限制的事实仍保留，不在此表重包装运行。

## 拟复跑入口（尚不存在，不是现在可执行的命令）

未来 `lifeos/engineering/LIFEOS-P3-148/tools/verify_design_contract.py`：校验26IPC与DTO/矩阵覆盖、固定来源代码谱系，不接数据根。

未来 `tools/verify_source_conversation.py --phase contracts|storage|credentials_mock|transport_mock|restart|ui_synthetic`：固定148合成root，无任意root参数；按T01–T25执行，完整日志留148/evidence，各阶段输出结果JSON。不从CI调用真实profile、OS凭据、Provider或GUI。

未来 `tools/run_synthetic_app.py --viewport desktop|narrow`：仅构建好的合成App，建立新launch返回PID→准确窗口→AXWebArea→截图/geometry，不能按前台App或旧窗口替代。GUI由有前台会话的人工阶段完成，不在无人CI承诺通过。

未来 `tools/resume.py --checkpoint <148 evidence内白名单checkpoint>`：校验合同/候选/基线与已有合成Evidence摘要、禁止接触=false、marker与写入者安全，按resume_from定向恢复。阶段：preflight、contracts、storage、credentials_mock、transport_mock、restart、synthetic_gui、cleanup、manifest。禁止根据环境恢复重新发送真实请求。

使用实际发现的工具链，Rust `--locked --offline`、task-local target/TMP/cache；共享fixture串行。CI注册文件由后续任务合同明确授权后才改，本阶段不写。真实文本/DB/Key永不进入CI或Synthetic Candidate Package。普通代码失败在同任务Closure Cycle；锁屏/截图失败Paused — Resumable；越界或历史污染才按治理判断Invalidated。

## 给 PM 的一次整包批准内容

以下是可向用户完整展示的**拟授权清单**，并非已获准。PM应先审核01–04精确方案、对齐过期CURRENT_STATUS和任务登记，再集中提交；不要把技术选型逐条抛给用户。

1. **API/存储**：接受25→26的独立发送命令及11项v3分支；批准v3问题/预览/派生/纠正JSON语义和148专用快照投影；旧147保持只读。批准未来148新candidate工程/合成根，不允许在147修补。无旧业务库DDL，真实结构不符即暂停，不自动迁移或复制备份。
2. **真实本地范围**：只由用户在148 App点击后打开已有`/Users/xxe/Documents/LifeOS-Source-Pilot-1/capture.sqlite`，读取已导入段/权限/版本，在其中保存问题、草稿、精确披露包、答案、反馈、操作状态；允许SQLite必要副文件、显式`p3-148-session.lock`及准确147 marker只读验证。该锁只防多个148实例，147不遵守，不能自动阻止147重开或证明跨版本互斥；用户先关闭147且使用148期间不重开147是操作前提，跨版本并发安全仍未证明。不为此修改147或扩大进程探测。不重扫`/Users/xxe/IT-obstain`、不读缓存原件、不接其他Pilot/DB、不覆盖旧资产、不自动清理。
3. **新凭据文件/OS范围**：创建唯一`p3-148-provider.sqlite`及副文件，采用02两表；OS唯一新service `com.lifeos.p3-148.aead-key.v1`与本任务随机引用的创建/读取/替换/精确删除/失败清理。用户在App输入Key；AES-GCM密文跨重启保留；不枚举或借旧144/145凭据。不把明文、Key hash、密钥材料写Git/Evidence。数据库正文仍未加密，必须如实展示。

   本项同时明确批准拟新增`save_ai_provider_credential`的v3 `recover_credentials` operation（01精确DTO），总IPC仍26、受影响既有命令仍11。启动和被动读取不访问OS；遗留操作仅本地显示待恢复。任何OS恢复/清理须在用户明确恢复/保存/删除动作后按获准148引用执行，禁止后台清理；test/send按需解密不隐式恢复。
4. **真实网络**：用户单击测试才GET `https://api.deepseek.com/models`，发送Key但不含问题/资料；每次预览确认后才POST该authority的`/chat/completions`，只发送可见问题/最多3个最小片段/相关纠正/固定说明及模型参数。可能产生服务费用；不声明具体价格。没有重定向、代理、fallback、其他Provider、后台发送、自动重试、工具调用或来源抓取。明确超时结果可能未知，重新发送需新预览确认。
5. **验证与风险**：合成包与允许的新安全验证先完成，PM安排新增真实网络/凭据/存储边界的独立评审及用户亲验。147 waiver不自动覆盖148；不能规避平台拒绝。真实亲验由用户操作，Agent只接收非内容状态/固定码/版本/是否通过，禁正文日志、截图、AX、内容hash、数据库/秘密导出。安全评审不可执行时保留Unknown并交PM/用户决定，不称Pass。
6. **保留与退出**：问题/答案/反馈、密文和新OS key保留跨重启；不自动删除真实资料或旧147资产。凭据删除为用户在App单独明确动作；退出/禁用只停用发送。未包含push/merge、冻结、风险关闭、Stage变化、OCR/转写/真实外链/目录外文件/健康持续同步。

PM批准此设计阶段不等于真实授权或完整任务Pass；用户对完整边界的一次批准不替代每次具体披露的“确认并发送”。若后续发现需要迁移、改根、放宽网络或安全策略，停止该变化并按合同变更规则处理。
