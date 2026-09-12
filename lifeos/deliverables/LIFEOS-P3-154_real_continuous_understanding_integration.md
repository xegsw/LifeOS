# P3-154 已有资料与持续理解的真实接线

**工程完成并安全切换，等待用户实际闭环与PM验收；任务未Complete。** Codex单Agent，L3；独立评审依用户例外暂停，不是Independent Pass。2026-09-09。

## 结果与继承

完整继承P3-153 Closure-1的163文件候选，按152最终真实接线恢复controlled-real；没有新建精简App。Shell、设置模型列表、保存/测试/选择/启用分离、密文持久/掩码、来源管理/检索/原文、健康查看、草稿、披露与对话均保留。持续理解沿153有限available_time/sleep_hours规则，不宣称开放域理解。

真实模式复用既有conversation/provider/source-engine库、旧152 marker、Schema、AAD及凭据引用，不迁移、不重置、不复制库。与旧152不同，缺根、缺库或来源缺表时明确拒绝，不自动新建/补表。App启动先验证现有存储结构；成功启动仅证明本次打开与结构守卫通过，不是用户内容正确性证明。

主动提问可使用现有授权来源，无需重启后再手动连接；既有授权/版本/时效仍逐次检查，不新增启动扫描。健康只读Reader不变，真实重新导入在本轮返回health_import_not_authorized；完整导入实现与合成回归保留。

凭据service固定`com.lifeos.p3-152.aead-key.v1`；account来自旧`provider_profile.envelope_json.keyReference`，严格`p3-152-key-[0-9a-f]{32}`。源码没有固定随机后缀，具体值仅App内部读取；工程不枚举Keychain或读取真实凭据引用，不回退144。缺密钥解密失败不会新增/删除密钥替换旧密文。没有要求用户重新录Key。

## 工程验证

- 152与153 Closure-1的398项历史Manifest文件复算通过；历史只读。
- 第二轮完整回归173项：Rust104、UI25、集成14、组合11、连续性8、澄清UI5、时效6。全部通过。
- 最终新增来源Schema内存夹具1项通过；合计174个检查。后续86项受影响复跑与11项组合复跑是重复验证，不追加到174，也不声称174项在单次命令中全部重新执行。
- 5个mutation均被检出：确认令牌、状态过期、Key回显、缺库守卫、144 account。真实+synthetic-driver组合构建被拒绝。
- 完整真实binary离线构建成功；不运行真实模式测试、不调用真实Provider。真实调用只允许用户手动/models及逐次披露确认chat/completions。
- UI布局/CSS/Settings/渲染未变；按D-0649复用153六态合成原生GUI，新增接线依赖行为测试。本轮不采真实AX/截图，不以旧GUI证明真实内容。

独立子crate测试入口曾因缺少历史测试模块/依赖而不能编译；原日志保留并排除。最终Schema测试使用现有boundary-tests隔离入口、主crate测试执行，真实编译禁止该入口。没有用编译失败冒充mutation检出。

## App及切换

App：`/private/tmp/lifeos-p3-154-real-continuity-v1/LifeOS P3-154 Continuous.app`。

Binary SHA256：`c59fcb8a795761dc6fc4dedcb25e153aa43666e54391c750b463b79d8c0c67c0`。

候选摘要（排序path→SHA映射的紧凑JSON SHA256）：`2a4dd169da38181036375985bd0b9407b208c5133032dd3448304226b47888ec`。

切换时旧152 PID43099及binary hash已实时匹配，正常退出成功；旧bundle保留。新154只启动一次，PID66104，固定状态`controlled_conversation_started`，已激活。启动获取既有单实例锁，无强杀、删锁、迁移、清理、真实数据hash/正文/截图/AX采集。PID是本次启动记录，不保证之后持续不变。

## 关卡与剩余项

ABF-01～09工程自检通过；逐行正负依据见engineering/LIFEOS-P3-154/design/acceptance-matrix.md。ABF-10等待用户：已有资料提问→必要澄清或有效依据→回答/纠正→后续变化→正常重启保持；每次实际发送由用户阅读披露后亲自确认。仅需成功声明或固定错误码，不索取正文或截图。

范围内P0=0、P1=0、P2=0、Unknown=1（ABF-10实际结果）、Not Implemented=0；这不是实际闭环已完成。独立评审暂停单列，不能写Independent Pass。PM仍须验收，本轮不关闭风险、不冻结产品/架构、不切Stage、不提交推送、不改PM账本。

## 复跑、保全与恢复

工程根：`/Users/xxe/.codex/worktrees/b3f6/No.2/lifeos/engineering/LIFEOS-P3-154/`。

```sh
python3 lifeos/engineering/LIFEOS-P3-154/tools/rerun.py
python3 lifeos/engineering/LIFEOS-P3-154/tools/verify.py
```

从b3f6仓库根执行；复跑只在154已拥有的合成根内建立新副本，不修改历史或真实库。新环境可使用`--init`独占创建固定根；已存在则拒绝，不接管外来根。mutation入口tools/mutations.py，真实切换入口tools/launch_once.py只接受一次claim，禁止重复启动；不是无人值守CI/CD。

checkpoint resume_from=user_real_validation。所有合成、历史和真实资产保留，无清理。若新App运行失败，先正常关闭新实例并确认退出，再使用保留的旧152；不迁移数据、不强杀、不同时打开两版。恢复旧版须先核对精确bundle身份，不能将此说明当成自动重试。
