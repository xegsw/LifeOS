# LIFEOS-P3-147｜连接入口准备交付

## 当前状态

Partial — 本轮普通产品入口准备完成，真实连接尚未激活。主责为工程执行；需PM确认固定真实profile方案，并由用户明确批准新增非加密保存边界。不能将本阶段称为P3-147完整完成或L3 Pass。

PM于2026-09-08转达用户停止独立复评并继续正常产品工程的决定：**User-directed review waiver / No Independent Pass**。没有重新运行、改写被平台拦截的安全评审，也没有换会话绕过检查。原Rework与安全未获独立确认的剩余风险保留。

## 用户可操作入口

实际App：/private/tmp/lifeos-p3-147-obsidian-source-v1/LifeOS P3-147.app。

Settings → 数据与隐私 → 来源 → 查看连接说明。展示唯一拟定来源及未加密的SQLite保存位置，可收起；“连接此目录（未激活）”明确禁用。打开说明零IPC，不检查目录或创建DB。下方“连接合成目录”能自动导入示例文件、显示进度与格式状态，支持暂停/继续/取消/刷新和Memory本地检索。

本轮仅UI及其生成产物、普通功能验证与交付元数据变化。Rust后端、25IPC、两个固定root profile、Schema、配置受限、附件状态、FD边界及Provider保护保持不变。真实文件/网页/目录外目标获取没有启用。

## 验证事实

UI生成与锁定离线构建通过：evidence/checks-20260908T065434468999Z/。6组普通合成检查通过：evidence/checks-20260908T065600195699Z/entry_flow.log，覆盖说明零IPC与禁用、自动导入、暂停跨重启/恢复、检索、刷新、断开后重启；外部目标授权调用为0。本轮不复跑安全攻击或将旧94项安全/回归历史改标成当前复评。

当前binary SHA256：dcf8979b337a641c5ffeb3f2e0b7e9f4dc6dbc40a142a941e7644f6555747bfe。直接PID52563（1280×949）、52729（700×760）绑定同PID AXMainWindow→AXWindow→AXWebArea→截图/geometry；桌面与窄屏连接说明均已视觉检查。暂停重启后仍暂停，继续后能检索合成原文。App显示6项已处理、3解析、2未解析/受限、1失败；既有坏编码夹具失败被保留，不称所有格式成功。两个PID已停止，工程根和App保留，没有物理删除。

旧801e478a工程计数为65当前自动测试+29复用历史，原review反例2例另计；这是先前工程修正事实，不是本轮独立安全结论。旧Manifest、报告、检查点和校验结果保留在history/pre-user-entry，原640ebb6及更早历史继续不变。

## 精确激活条件

当前真正需要决定的是：用户批准唯一新输出根中的未加密capture.sqlite、原件缓存和解析临时文件保存；PM批准固定source-pilot-1编译profile及现有连接IPC的固定源映射。完整方案见design/real-entry-activation-proposal.md，**本轮未实施该关键合同调整**。

批准后仍需完成惰性仓储初始化与真实模式日志/诊断限制等接线，用户点击连接才允许校验和访问。不能仅改root字符串或把普通点击视为未展示保存边界的授权。真实目录和输出根本轮均未访问或探测，未接触任何Pilot、旧真实库、Provider/Keychain/凭据/真实网络；无需Key。

## 角色与关卡

工程执行侧普通功能验证通过；独立复评由用户停止，No Independent Pass。原独立未完成8行和安全剩余风险未被补齐或关闭；真实亲验与PM终局未通过。没有冻结、推送、合并或启动后继任务。

## 交付

工程根：/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-147/。当前Manifest只声明本轮入口准备、普通合成检查与文件完整性；使用candidate/tools/verify_entry_release.py，旧verify_release.py按历史801e478a合同保留，不用于当前阶段。完整diff见evidence/user-entry-diff.json，checkpoint的resume_from为pm_profile_decision_and_user_storage_approval。
