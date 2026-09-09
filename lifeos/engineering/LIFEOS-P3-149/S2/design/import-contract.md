# S2 实施前设计与最小接口差异

仅合成离线，原/S1只读。独立运行根为已核验149根下 `/private/tmp/lifeos-p3-149-health-source-v1/S2`，新的app.sqlite和fixtures，不读父级旧DB。engineering编译根固定S2，保留父marker核验；无真实profile。用户通过来源设置选择固定合成输入列表中的ZIP/XML并触发导入，不打开系统真实目录。

## 唯一关键差异（设计时待确认，现已批准并实施）

现有五个source IPC只有目录连接/作业控制/状态/来源证据/目标授权；目录扫描已禁用，没有单文件选择导入语义。建议新增一个窄IPC `import_apple_health_file`，DTO `{version:1,payload:{action:"list"|"start"|"status",file?:string}}`：list仅枚举S2固定inputs中的普通合成zip/xml；start只接受单层文件名且属于该列表，拒绝任意路径；status返回进度和结果。不新增通用文件读写IPC，不复用已禁止目录扫描；UI选中文件即start，无逐记录操作。该差异原先等待确认，用户批准后已完成IPC注册和前端接线，授权记录见contract-inputs/ipc-authorization.json。

返回为有限任务状态/文件候选/新增、重复、不支持、失败计数/来源/导入与观察时间。存储继续既有records/sources/states JSON扩展，不新增表列或核心实体；需要PM确认新增IPC即可，非Schema冻结。异步后台线程仅在App打开且用户点击时运行；UI定时status，不在UI线程解析，不注册后台采集。

## Source adapter与资源

使用系统Python3标准库zipfile与expat流式读源、输出有限单行JSON的SourceItem；Rust Application负责校验、事务和Repository投影，UI不解析文件、不直连SQL。无新下载依赖。单文件默认磁盘256MiB、解压XML512MiB、ZIP4096项、压缩比200、记录200万、XML深度32、单标签/属性文本64KiB、单记录持续时间7天。上限通过task-local配置降低或在硬上限内调整，超限整批失败。读取分块、输出逐行、SQLite事务；不把整个XML/解压包或全部样本一次读入内存。工作超时120秒，异常/中断回滚；不会靠截断标成功。

ZIP只允许唯一export.xml或apple_health_export/export.xml，不落地解压。所有目录项先校验路径、重复/大小写歧义、加密、symlink/特殊类型及容量/比率；拒绝损坏CRC、非store/deflate算法。其他附件计未处理，绝不跟随引用。XML接受HealthData及常见内联DTD声明，但不执行外部实体或自定义实体扩展；外部DTD不加载，自定义实体引用/外部实体请求失败。属性中预定义XML转义安全解码。无网络/OS文件访问的解析resolver。

## 分类、身份和投影

仅HKQuantityTypeIdentifierStepCount(count)、HKQuantityTypeIdentifierAppleExerciseTime(min及s折算)、HKCategoryTypeIdentifierSleepAnalysis的苹果asleep/asleepUnspecified/asleepCore/asleepDeep/asleepREM标识可映射；inBed/awake保留类别观察而不算睡眠。其他Record类型和Workout/ActivitySummary等按类型计不支持，不声称导入整个健康库。未知睡眠类别不猜中文，保留不支持数量。无效已支持记录整包失败，不半导入。

批次用完整输入文件SHA256证明字节重放。标准化内容指纹只识别“相同观察内容”，不是样本UUID或修订身份；来源名称组不是设备唯一ID。重叠文件相同内容不重复计量；同批完全相同多行不能认定是一个物理样本，步数/运动投影保留不确定。不同值同区间或区间重叠同样不确定，无自动更正/删除。按内容保存观察证据与批次引用，旧文件缺行不删除旧证据。

来源/metric/offset/自然日分组；跨日睡眠裁剪后并集，步数/运动按区间比例且标估算。不同offset不混合；不同来源分别显示，不给个人权威总量。有冲突/重复歧义的数值null，明确“暂无法可靠合并”。所有投影标文件观察/非完整总量，observedAt用样本end，importedAt单列；旧数据不因导入变为当前新鲜观察。新旧v1/S1不共用投影ID或累计，不自动扫描旧inbox，新S2库不迁移旧库。

## 事务与失败

SourceItem逐条进入单一SQLite事务，最终end收据/完整文件摘要与进程成功同时成立才commit；失败、超限、CRC或尾部XML损坏全部回滚。状态失败数明确区分“文件失败1，整批未导入”和成功包的记录计数，不伪造无法读取文件的记录总数。重传成功文件不写入新记录或刷新观察。重启不会自动导入，仅显示已持久化成功历史；未完成工作可手动重试。

## 验证与保持

合成正负XML/ZIP均走同一应用服务；跨文件重叠、重复、乱序、冲突、单位/offset、跨日、DTD/实体、ZIP路径/CRC/加密/资源、尾部失败、事务中断重试/重启及模型拒绝。有限actual Tauri选文件→进度→结果/失败/重试→重启。Provider/凭据/116和142基础CSS逐字保留。无真实文件/模型/网络/后继/独立评审。当前唯一IPC及前端已按批准范围实施。

## PM首轮补充（保留当时设计；IPC后续已批准）

DTO按action严格区分：list/status只有action，禁止file；start必须file且只能字符串；顶层version/payload和payload均拒绝未知字段、错误类型、嵌套对象，重复JSON键按既有strict_json拒绝。列表仅为展示，不授予读取权限；start重新验证S2固定根marker、固定inputs、文件单层名和普通文件身份，O_NOFOLLOW/openat绑定描述符，拒绝hardlink/特殊文件，解析前后校验目录链/文件身份/修改时间。Python只接已打开描述符，固定/usr/bin/python3、固定脚本及受控限额参数，不使用shell；并发start返回busy，不串结果。文件内容hash仅用于本轮合成测试和导入幂等，不自动沿用为未来真实审计或存储授权。

资源补充：SQLite主库最多262144页（默认4KiB页约1GiB），缓存8MiB；最多128个来源名称组、10000个按日投影，超过整批回滚。默认snapshot不返回逐条苹果原始观察/成员关系，只返回批次摘要；苹果按日State最多展示最新256条，并在UI说明显示范围，库内历史不删除。大文件解析与投影整体120秒预算，超时终止解析/中断SQLite，不留半批有效数据。支持资源上限不是保证任意硬件在时限内完成最大包的性能承诺。

传输补充：新命令沿用既有raw UTF-8字节请求风格，直接承载上述version/payload DTO，单请求4096字节；拒绝已丢失重复键信息的Json通道，strict_json先于DTO和任何文件/DB动作。无第二IPC。内部请求模型、领域服务、Host和前端均已接通并验证。

构建配置位于candidate/apple_health_limits.json，可降低上述解析限额，不能通过UI/IPC输入任意上限。输入列表保留最多64个用户可选合成文件；`test-`前缀是内部测试夹具，不出现在选择列表（内部SourcePort负测仍可读取自己的这些夹具）。ZIP CRC验证仅覆盖选中的XML，附件仅校验目录元数据并显示未处理，不能声称附件内容已验证。

ZIP分配前检查：先读取最多65557字节尾部EOCD，拒绝多磁盘/ZIP64、声明条目超限及超过8MiB中央目录，再构造ZipInfo列表，避免先分配后检查。首版支持普通单磁盘store/deflate ZIP；ZIP64明确失败，不声称支持所有ZIP变体。日期要求1970–2100内、正长且不超过7天；同一记录起止offset不同（含跨DST）明确失败，不以单offset伪算，其他记录可各有不同offset并分组。上述是首版技术限制，真实导出兼容性仍未验证。
