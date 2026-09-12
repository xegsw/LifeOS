# P3-158 D0672：活动预算持久化与离线业务增量

2026-09-10。专项执行：Codex，复用原工程会话。状态：Partial / 待 PM 核对 B 恢复门槛。合同：D0670 approved addendum、两份固定提案（Revision 1优先）、D0672 login identity signing；原 ABF 和历史证据只读。不是独立评审、整体 Complete、C 授权或风险关闭。

## 本轮结果

Host 开始工作前持久化活动阶段和剩余预算预留；崩溃无法可信计时的预留转为已用额度，同草稿重试不能清零。原生凭据等待前结束活动段及数据库事务，返回后重新验证并进入新活动段。最终业务事务中结算 Host 时间，预算不足使条件与 Action 一并回滚。

清空草稿改用每次唯一的取消 nonce，重复清空后重启不恢复旧文字；晚到的旧协议取消不能覆盖已提交 v8 草稿。另补当前用户明确“仅记录／不要执行”等约束的拒绝守卫，拦住与之冲突的模型行动候选。该守卫不解析句子为 Action，不替代模型，也不声称证明开放域语言含义；未覆盖语义仍须真实模型开发与 PM 未见样本检验。

最新候选 182 文件，相对 D0672 已签名输入新增1项、修改6项、删除0项；完整历史输入保留。最终完整 App 已用获准登录钥匙串单一身份签名；主程序及 helper 严格验证通过，DR 与先前重建包一致。未改变信任、ACL、搜索列表或密钥缓存，未导出私钥。最终包尚未启动或发送模型请求。

## 验收矩阵（工程自检，非 Independent Pass）

以下路径均相对 `lifeos/engineering/LIFEOS-P3-158/`。

| 合同要求 | 本轮及继承证据 | 结果／限制 |
|---|---|---|
| 完整累积继承、旧协议兼容 | 最新全 Rust 187项；原完整17步骤日志保留 | Pass，非从旧 main 重建 |
| v8闭合联合及非法字段 | `tests/coordination_union_contract.rs`；`evidence/D0672-union-contract-fc34bef9-6035-4b79-b304-c8553c866814/` | 八类候选正路径及缺失/null/未知/重复字段、文本边界通过；外部测试仅追加在一次性副本，原候选不改 |
| 14 IPC及版本/操作拒绝 | Host固定映射、v8严格DTO测试、现有命令测试 | 未新增公共命令；query确认组合拒绝 |
| 三 Adapter同协调实现 | `v8_three_public_adapters_share_one_query_and_second_confirmation` | note/schedule/forecast正路径；均公开fixture，不是真实接口 |
| 查询与模型权限分离 | 工具许可与第二次披露测试、实际IPC二阶段流程 | 自动一次本机读取；二次模型未确认不发 |
| 三值、record_only及单向条件 | v8条件测试与condition反例 | true可原子条件+Action；false/unknown/record_only不执行Action |
| 当前意图、引用及工具注入 | 引用拒绝、工具结果结构/来源校验、当前非执行约束测试和mutation | 有界拒绝守卫通过；开放域语义待 B，不把合法JSON/跨度当充分证明 |
| 条件/Action原子与来源目标版本 | 事务故障回滚、当前条件版本、伪造refs测试 | 零半提交，最新条件投影校验 |
| Host活动预算及崩溃 | 4项新Host测试、3个Host mutation | 预留先落盘；崩溃保守扣账；耗尽回滚；同草稿不重置 |
| 人工/凭据等待与恢复 | v8等待、过期、凭据取消和无事务测试 | 人工180秒不耗活动；预览仍5分钟；恢复新预览并复核 |
| 传输预算 | bounded transport测试与mutation | 剩余预算进入Adapter；本轮零真实网络调用 |
| 查询结果过期、撤权、在途未知 | 结果结构/时效、撤权、在途重启测试 | 不刷新旧结果时间，不自动重发 |
| 幂等、重复、晚到回执 | v8重放、实际IPC重启、晚到取消测试 | 原operation/Action identity保留，无重复事件 |
| 中文回执与假成功拒绝 | 前端19项；receipt mutation；实际App AX/截图 | success依结构化真实回执，condition-only不冒称Action执行 |
| 完整离线 App 业务 | `evidence/D0672-v8-gui-*.ax.txt/.png`、`D0672-v8-gui-business-receipt.json` | 创建→调整同Action；查询→第二确认→正常重启→条件+Action；共一次查询、两个离线模型替身调用 |
| GUI身份与修正影响 | `D0672-v8-offline-launch.json`、`D0672-v8-offline-restart.json`、`D0672-v8-offline-bundle.json` | 直接PID16244→16324，精确App路径/AXWeb内容；CUA不暴露原始AX PID字段；截图1036×768。GUI包早于最后非执行守卫，后者由全Rust/IPC及mutation覆盖，不假称旧截图来自最终包 |
| 持久签名与重建DR | 既有D0672签名报告；`D0672-final-signature-comparison.json`、`D0672-final-signing.log` | 完整签名Pass；凭据免密码体验Unknown |
| 真实模型、未见集和C | 分离预算/检查点 | 新模型0次；待PM恢复B及用户逐次发送。C v8和真实外部接口未授权 |

最新检查：187 Rust（含28项v8）、实际IPC7、前端回执19均通过；12个有效mutation均被检出（原8个在最新候选复跑，新增Host3个、非执行约束1个）。外部闭合联合测试另计1组，不计mutation。完整索引 `evidence/D0672-offline-increment-checks.json`。历史失败编译/签名解析/资源标签/占锁尝试保留；不计正证据。首版外部合同测试运行器沿用了mutation字段名，其日志不作为mutation数量依据，已修正为validTest/passed并复跑。

## 固定交付身份与复跑

- 候选／差异 Manifest：`evidence/D0672-offline-increment-manifest.json`，SHA256 `29ba080c235c76949f543d9733dc19922b27dfdf3f2c20aedb467bd8362127c9`。
- 最终构建身份：`evidence/D0672-final-build-identity.json`。
- 最终签名包：`/private/tmp/lifeos-p3-158-main-chain-v1/build/signing-v1/D0672-final/LifeOS P3-158 Online Test.app`。
- 确定性复跑：`python3 tools/run_v8_checks.py`；Host/意图/原v8反例入口分别为 `tools/mutations_host_activity.py`、`tools/mutations_intent_constraint.py`、`tools/mutations_v8.py`；闭合联合为 `tools/verify_union_contract.py`。均离线，保留每次独占目录。
- 检查点：`checkpoint.json`，`resume_from=PM_B_resume_then_user_confirmed_public_synthetic_preview`。无需重做已通过签名稳定性或无关历史测试。

## 预算与后续门槛

旧 B 开发14/24、未见0/16、总14/40原样保留；新增v8开发0/8回合、0/8查询、0/16模型，PM未见0/4回合、0/4查询、0/8模型。准备新在线预览会消耗新turn额度；每次实际模型请求仍须用户亲点。没有访问旧157真实App或真实内容；离线App正常退出，旧签名B App不自动关闭或替换。

需 PM：核对本增量及B恢复门槛；固定候选后由PM提供未见样本。工程不得自造未见集。真实模型语义、凭据系统交互体验、真实接口和终局范围缺口保留，不能从离线结果推导真实通用查询或整体验收完成。未更新PM账本，未创建后继任务，未自动合并。
