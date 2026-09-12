# P3-160 A 增量逐行矩阵

依据：inputs/LIFEOS-P3-160_acceptance_basis.md Revision1。执行自检，非Independent Pass。A整体未通过，B/C未批准。PASS仅限明确列出的离线事实。

| ID | 当前证据和结果 | 完整判据状态 |
|---|---|---|
| V01 | 精确commit/identity/182逐hash一致，voice-only提交未包含旧基底覆盖 | A继承PASS；合并后待核 |
| V02 | 原样保留182；旧UI回归18通过2失败原日志保全，PM已交159核对 | Partial，不能称旧能力全通过 |
| V03 | consumer final幂等/改ID/晚到；SSE合法stop+DONE；28项Rust与7项TS子集 | Partial；host持久映射/真ASR待联合 |
| V04 | voice原样传上下文快照，无关键词业务匹配 | Unknown；159模型语义联合待验 |
| V05 | 真模型加载，静音/噪声无唤醒；Worker不上传wake frame；无POST能力A构建 | Technical Partial；实际App关闭/唤醒待B |
| V06 | 作者模型许可、固定版本/hash、词表、真实检测器合成正负样本 | A资产与离线检测PASS；真实声学未验 |
| V07 | 原生A开麦拒绝、锁屏/设备回调stop代码与编译；RAM释放测试 | Partial；真实撤权/设备场景待B |
| V08 | VAD模型合成speech/噪声，Segmenter静音800ms/60s/首帧测试 | Partial；真人/混合声学待B |
| V09 | 官方ASR单wav上传adapter、逐字节SSE、断流/不合法终止拒绝 | A协议PASS；真实MiMo待B |
| V10 | output只接受host引用；Gateway Authority每边界复核，拒绝工具/改写模态 | Partial；原host registry接线待A3 |
| V11 | PCM分片在流终局前交付、24kHz队列背压，Swift实时调度可编译 | Partial；实际出声/首音未测 |
| V12 | worker先interrupt，再保留插话首帧；晚到generation mutation被杀 | Partial；硬件20次p95<=250ms未测 |
| V13 | AVAudioEngine voice processing代码；监听不因stopPlayback停止 | Unknown；AEC自回声正负样本未测 |
| V14 | interruption只报告不submitUserTurn、不改业务状态，保留等待标志 | A模块PASS；事务联合待验 |
| V15 | idle不打断处理中/录音/播放；旧键盘恢复测试通过 | Partial；完整多轮/重启待A3/B |
| V16 | unwoken/隐藏主动请求被拒，未订阅AssistantTurn自动播报 | Partial；159surface/silence真接线待A3 |
| V17 | 每chunk Authority复核、取消在途测试与mutation通过 | Partial；host来源/业务失效连接待A3 |
| V18 | 默认关闭3用途；A本地编译阻止开麦/HTTP，FFI在凭据读取前拒绝 | A拒绝PASS；真实用途持久grant待集成 |
| V19 | 仅CredentialAccess瞬态注入，无第二凭据存储/前端Key回读 | Partial；原加密保存/重启接线未验 |
| V20 | Audio释放/RAM ring、原生ephemeral HTTP无磁盘cache；不新增voice DB | A局部PASS；实际全链生命周期待验 |
| V21 | B开发/未见/总量、C速率/时长、失败不退款、重启/回拨/CAS故障测试 | Partial；原Store持久适配与每POST接线待A3 |
| V22 | 401/429/重定向/超时/断流/错格式真实代码fake注入，无自动重试 | A故障PASS；真实服务错误待B |
| V23 | CredentialAccess错误一次向既有status；A完全不取凭据 | Partial；真实平台后台解锁体验未验 |
| V24 | voice不实现周末业务；输入原样交InteractionPort | Unknown；完整真实联合链未验 |
| V25 | 没有另造Action/Memory/业务脑 | Unknown；未见自然语义与真实事务未验 |
| V26 | requestID重复不重播；无AssistantTurn隐式朗读、无响应不提交 | Partial；host同turn恢复去重待A3 |
| V27 | 两协议hash一致、范围单写入；中间delta已经PM逐blob核对 | Partial；完整同App联合构建未验 |
| V28 | A真实麦克风/扬声器/凭据访问/Provider POST均0；证据全合成/公开模型元数据 | A边界PASS；B/C仍待批准 |
| V29 | 仅原设置折叠片段/状态入口，无新导航；转义/关闭默认测试 | Partial；真实容器窄窗口/焦点待A3 |
| V30 | 报告Technical Partial，157失败/159未完成/Independent Paused均保留 | PASS（状态诚实），非产品完成 |

已知旧UI失败：AppleImportController导出与旧测试不匹配；health status spoof分支旧断言1!==0。不能先认定只是测试过时，也不因其存在把voice写成回归来源。共享所有者需以现行合同核验。verify_voice --offline仍返回1以保留未关闭失败，不删测试、不放宽断言。
