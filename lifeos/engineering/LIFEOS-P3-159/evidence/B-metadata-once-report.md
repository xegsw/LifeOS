# 单次元数据检查结果（2026-09-12）

批准提案 SHA256 d912f5f1175e0f609475dd484dac4d1bf7e28427a641df8b032a4ccf6591294a 已核对；同完整候选、同原签名身份的 B Host，专用一次诊断入口在 UI/调度器启动前运行并正常退出。此入口未作独立小工具替换，完整产品代码仍在同包；没有实际 GUI 验证声明。

实际 PID68518，754ms，exit0。固定结果 configuration_binding / OSStatus null：online_provider 或只读SQL字段投影拒绝，未进入 inspect 的系统条目查询。现有固定错误清洗不进一步区分这两个配置失败点，不能猜测具体 profile 字段。没有取得 ACL/提示标志，两个 App 匹配 Unknown；没有证明后台恢复或 -25293 根因。一旦本次执行失败即停止，不补第二次检查。单次claim保留，不删除或重置。

分析预留5、反馈0、generation5、B预算不存在，前后不变。密码读取0、POST0、后台未启动、C/麦克风/播放未启用。进程已正常退出并确认不存在。未读取真实正文、未导出完整envelope，SQL仅reference/版本结果；不声称SQLite物理页零接触。

离线：完整24步回归、325 Rust测试、公开C代码fake（成功/拒绝/不限/空/受限列表）、3项C mutation检出（密码出参/description释放/空列表语义），两模式构建通过。最初synthetic-driver模块路径编译失败已原位修正，失败日志保留；最终receipt来源稳定。元数据C只使用公开SDK，NULL passwordLength/passwordData，opaque description立即释放，没有trusted app导出/匹配SPI。

没有新的真实重试计划。本次能力边界交PM评估，继续原授权的离线语音producer工程。
