# 已批准接口的工程接线说明

任务卡顶部五项公共接口批准是当前依据。`implementation-checkpoint.md`和`history/pre-public-api/`保留原待批准文字，不追溯改写。

- 五项严格输入、version1、detail/search判别联合已接线。原20项version2及凭据生产文件保持既有语义；凭据/Provider代码不链接执行。详情返回来源标题、格式标识、时间、版本、状态、定位和分段；配置不返回正文。状态结果补充本地显示用的文件/直接引用状态列表，各最多256项，并明确这不是导入范围上限。搜索返回最多8个匹配记录及仓储已有来源元数据，供Application组装原有packet；客户端不能提交路径、URL、SQL或自称授权。
- 授权变动和public receipt在同一SQLite事务。新增内部辅助表source_api_requests、source_runtime_errors、scan_identities、source_cursors/source_cursor_epochs、connector_requests；无旧库迁移。cursor同时绑定source/version/grant/scan epoch，刷新也失效。
- 目录授予固定自有夹具，逐组件no-follow文件描述符、打开前特殊类型检查、读取前后身份校验。内部目录链接归一去重防循环；bookmark别名仅读取归档路径元数据，后端再次做根边界验证，不调用目标解析/挂载API。无法读取的格式/别名/越界目标保持失败或待授权，不猜测目标。
- 原件先独占写入并fsync，无覆盖发布后事务引用。孤儿隔离保留。解析临时文件迁到`.runtime/`；相应恢复测试的artifacts目录数量从3改为2（原件和staging），旧失败日志保留。解析进程64MiB预算通过父进程RSS/输出监测及子进程峰值校验失败关闭；这是监测式预算，不宣称macOS RLIMIT_AS硬内存沙箱。实际进程超预算反例不返回正文。解析30秒、DOCX声明展开128MiB。目录导入串行，不超过2并发上限；外链最多2并发。
- 外链父版本、目标grant generation和worker epoch在消费/提交处复核，父版本更新使目标依赖失效。内容与fetched状态/时间在同一事务。网页复用注入WebSourceAdapter，目标经stdin传递，不进入命令行；无HTTP/DNS/socket实现。目录外文件当前只执行明确合成映射。
- 新来源正文不进入普通snapshot。有限词项匹配（中文双字/英文词）最多8项，再经过既有L1/L2/L3、TopK和预算；这不是语义向量检索或通用模型理解。原文中的指令仅为来源内容，不成为系统指令或确认事实。
- Settings保留既有目录及布局骨架；来源位于数据与隐私，Memory提供检索/详情。内部链接不再展示外部授权按钮。来源错误中文化；详情自动定位，保留标题、时间、版本与全文分页入口。

工程不冻结Schema/ABF、不关闭风险、不启用真实数据或网络。正式独立安全Gate和真实亲验仍由PM与用户按任务卡处理。
