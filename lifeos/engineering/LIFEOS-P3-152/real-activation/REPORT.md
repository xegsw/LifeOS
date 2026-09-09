# P3-152 真实适配与安全切换增量

2026-09-09。状态：In progress — 技术接线与启动完成，真实用户操作结果待反馈。L3；独立评审继续暂停。工程主责Codex，PM验收待进行，不报Complete、Independent Pass、风险关闭或产品冻结。

## 授权与关闭旧实例

依据 `../real-activation-proposal/real-activation-delta.md`（SHA256 `60c5853c7e5d589e0019dc5d7b68fd593931ac2f9ce3e02b1a94d9ae135ce39c`）及PM转交用户回复“同意，旧app你关闭吧”。`design/authorization.json`记录精确路径/读写/有限片段发送许可，以及允许Agent核对后正常请求退出的窄补充。独立评审未恢复，旧交付包与原提案未改写。

实际按固定可执行路径筛选进程，再由NSRunningApplication核验同一PID的executableURL：命中PID25223。正常terminate请求后进程退出；未使用宽泛pkill、强杀、锁文件删除、AX/截图或强制丢草稿。证据为 `evidence/old-instance-identity.json` 和 `old-instance-normal-quit.json`，不是仅凭历史PID操作。

## 同一候选的真实接线

当前候选160文件，本轮新增1文件、修改20、删除0；逐文件差异见 `evidence/difference-manifest.json`。保留14个IPC及现有设置、对话、草稿、健康查看和来源检索交互。新增真实路径均固定于编译候选，不允许UI传入任意路径或切换模式。

| 范围 | 本轮落实 |
|---|---|
| 原始来源 | `/Users/xxe/IT-obstain`。只有用户手动连接/刷新才启动有限worker，原件只读；不跟随目录外目标或网络外链。alias helper只解码bookmark路径元数据，不解析/挂载目标，根外引用拒绝。 |
| 私有来源库 | `/Users/xxe/Documents/LifeOS-Health-Conversation-Pilot-1/source-engine-v1/sources.sqlite`，同名SQLite副文件限于子根。`.owner.json`固定任务/owner/root/kind/version，目录0700、文件0600。首次创建叶目录必须原子create-new，外来目录或标记不被接管；保留目录描述符，拒绝目录/锁文件替换。 |
| 缓存与工作文件 | 仅新子根的artifacts/tmp/.runtime。来源副本/片段归私有库；不迁入conversation或健康库的私有来源表，不改原文为长期记忆。父root只增加唯一source-engine-v1 allowlist项，不放宽为任意目录。 |
| 生命周期 | 启动不激活来源引擎或恢复worker；进入管理页只查询状态。重启后需手动连接/继续。导入list在真实模式返回固定“导出.zip”选项，不枚举Downloads或预读ZIP。 |
| 健康导入 | 用户手动选择 `/Users/xxe/Downloads/导出.zip`，写入既有 `/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite`。不创建目标库、不迁移Schema；只复用既有records/sources/states/meta合同，事务内去重追加及原规则投影。历史原始row不重写，既有批次归属等去重元数据按原算法维护。 |
| 写入边界 | ZIP和目标库用目录/文件描述符绑定、nofollow、单链接/owner等检查；目标库SQLite HAS_MOVED复核到提交前；数据库必须有既有表与meta行。忙锁/解析/身份/Schema失败关闭、事务回滚。导入状态单独保存在新私有库；进程重启后未完任务显示待手动重试，不自动续跑。 |
| 并发 | 先获得既有父根 `.runtime/conversation.lock` 才打开App数据库；新私有根另有source-engine.lock，导入另有health-import.lock并依赖SQLite写事务锁。外部不遵守任务锁的程序仍受SQLite锁约束，不宣称新任务锁控制一切外部进程。App健康Reader在本App导入运行期间拒绝新读取。 |
| 有限真实对话 | 接回真实SourcePort，保留store/root/source/file/version/grant/epoch/range/hash。目录中原件metadata变化即拒绝旧引用，不要求先刷新；每次实际派发前再次校验并保持App来源变更互斥。最多3来源片段+2状态/确认记忆，既有4096字节披露预算和用户逐次确认不变；固定DeepSeek端点，不自动获取模型列表或发送。 |

原件外部编辑不能被App进程内互斥锁物理禁止；这里提供的是派发前原件身份再校验，以及App内来源授权/刷新与派发的互斥。没有宣称对任意外部编辑程序持有强制全局锁。

## 验证结果

- 65/65 Host：`evidence/host-tests-authority.log`。包括保留回归、9类引用篡改与派发互斥、原件未刷新即修改失效、新健康写入适配器的合成去重/回滚/busy/错误Schema/不存在目标/符号链接拒绝，以及外来目录create-new拒绝与锁互斥。
- 12/12保留集成：`evidence/integration-final.json`。
- 11/11组合集成：`evidence/combined-final.json`。来源生命周期、原文分页与失效cursor、实际有限引用回答、旧确认拒绝、合成外链目标、XML/ZIP重复及失败保持等。
- 17/17 UI：`evidence/ui-final.log`。含真实固定目标入口渲染不触发任务、来源页面迟到结果与轮询退出。总105项，通过的是合成工程验证，不是整个历史仓库全量套件或真实用户结果。
- synthetic与controlled-real均 `--locked --offline` 构建成功。真实测试feature与synthetic-driver组合编译禁止，未运行会触及真实目标的测试。
- 沿用上一完整恢复包的合成actual-Tauri功能链；本轮未用真实AX/截图补证，也不把旧GUI截图伪称新真实GUI验证。真实界面可用性与真实扫描/导入/发送结果仍由用户在App核验。

健康适配的错误路径测试仅对新合成根内测试数据库执行；Agent没有直接读取、hash或导出真实正文、健康库内容或凭据。真实App按授权读取自身对话/配置；来源读取与ZIP导入由用户手动触发，Agent未代点。

## 最终App与启动

`/private/tmp/lifeos-p3-152-health-conversation-v1/LifeOS P3-152 Unified Real.app`

二进制SHA256 `45c228cf5944e97206658188578c9e38791df421dd9917798f20b5ae3acd5290`。最终PID39248。`evidence/real-bundle.json`记录构建产物，`evidence/real-launch.json`记录单次直接启动及 `controlled_conversation_started`。此启动标记仅在Store::open成功之后产生，因此依实现顺序推断已取得共享对话库租约；没有另起同库实例来探测锁。

`tools/launch_real_once.py`在启动前再次检查精确旧路径/新路径无现有进程，并以create-new尝试记录防止该入口自动重启。真实stdout只有有界启动状态/固定错误码；标准输出、错误和core dump采取已有隔离方式。之后只按精确PID/可执行路径请求前台激活，没有取真实AX或截图。

此为本机受控开发bundle，仍依赖当前候选工作区解析脚本，不宣称任意机器可分发安装器。旧bundle没有被覆盖，现有真实库没有被清空或迁移。

## 准确操作入口及待反馈

1. 设置 → 数据与隐私 → **连接资料目录**，开始读取唯一已批准目录。状态/检索/查看原文在同页；新增文件后可手动刷新。
2. 同页 **导入苹果健康文件** → 核对原件/目标说明 → **导出.zip**，开始去重追加；失败只由用户点击重试。
3. **我 → 查看健康来源 → 查看已导入数据**，核对观察及日期。
4. 在来源检索结果点 **在对话中询问**，准备后核对实际披露，再点 **确认发送给DeepSeek**。不需要把Key或正文发给Agent。

真实来源扫描/检索、真实ZIP追加、非健康真实DeepSeek回答目前均Unknown，等待用户仅反馈成功/错误码；用户尚未反馈不能推断为成功或失败。整体任务保持进行中，PM验收和真实用户结果尚未完成，独立评审仍暂停。

## 保全与复跑

旧synthetic189、real-stage332、ui-restoration172、inheritance-audit3、health-view-restoration167、complete-restoration229，共1092项旧文件hash一致（`evidence/preservation.json`）。本增量没有改旧Manifest、PM账本或冻结/风险状态；没有提交、推送或合并。

`tools/rerun.sh`仅复跑合成验证，先检查本包与12个固定合成输入文件，输出到task-root内唯一新目录，不覆写本包Evidence、不启动真实App或任何真实动作。首次 `setup_engine.py` 遇已有根拒绝覆盖。合成测试目录遇身份/同名冲突也应失败关闭，不能挪用或清空其他历史运行根。
