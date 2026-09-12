# P3-160 语音交互离线增量报告

2026-09-12。Codex新建专项。当前 **Partial / In Progress（Technical Partial，A整体未通过）**，整体L3、A离线Evidence按L2；需PM协调A3接线/旧回归对账，B/C仍待用户完整合同一次批准。主责技术/音频可靠性，协审数据/AI信任/体验。独立评审按用户例外保持Paused，非Independent Pass，不关闭风险/冻结/Stage。

## 已实现的结果

在完整LifeOS共同基底上增加语音模块：Rust会话/有界音频worker、唤醒/VAD端口、800ms分句和60s段上界、MiMo ASR/TTS官方协议与SSE流解析、播放队列/插话generation、独立用途预算、每边界权限复核、原生AVAudioEngine和MiMo HTTP、Rust原生FFI连接、InteractionPort consumer与原设置折叠子组件。真实构建分支只编译检查；A原生入口硬拒绝开麦与POST，网络拒绝在CredentialPort读取前发生。

没有另建Voice App、业务脑、Action/Memory/Provider/凭据库。ASR final原样交宿主分配的UserTurn；partial不提交。SpeechInterrupted仅反映播放中断，不用“周末/取消”等关键词修改业务。键盘草稿与逐次发送确认由原入口保持。音频与HTTP仅RAM；模型文件是公开依赖，可位于打包资源，不能与用户录音缓存混淆。

## 继承与交接身份

- 工作树：`/Users/xxe/.codex/worktrees/0142/No.2`，分支`codex/p3-160-voice-offline`。
- 精确共同祖先：`46829c74eeb83c270a3258949c5d27db5bdea296`。提交中的P3-159 baseline/candidate全部182文件逐blob吻合PM identity；清单SHA256 `27e0dbc86579157fbf148c3959fdb3e6beb4f73de77b9bf03e56e7747b719879`。
- 本线candidate完整继承182文件且未改任一继承文件。它是共同祖先加voice delta，不包含159正在开发的最新主动增量。不访问b3f6实时修改、不修改159或PM账本。
- 中间不可变提交`f5a64094943c72701625f77f74c2064d81a1745d`含14个voice源文件及输入/工具，PM已逐blob核对。后续修正单独提交，清单见`delta_manifest_v2.json`及`delta_since_f5a64094.json`；前一commit不改写。
- 协议TS SHA256 `8234e7eb9523f5b8ea7114f50ef24acece5cbadfce8b98d92cdcc6b14b2bbafc`；MD `8dfdda556dfc05274d1cdf155614023122601f17d765725e56fd163a48a547f7`。
- 所有集成仅取manifest列出的`src/voice/`、`application/voice/`，由159应用到其最新完整候选。共享主入口、Rust交互mirror、registry/权限/原Store事务/CredentialPort和构建注册仍归159。不得整体覆盖candidate，不推送或合并main。

为了不在增量提交中重复182旧基底，继承文件保留在本工作树但不进入voice-only提交。新的检出可运行`tools/materialize_baseline.py`从精确Git对象补齐；遇已有不同内容直接拒绝，不覆盖。

## 测试事实与未通过项

- 最新普通Rust测试28项通过，前端contract fake测试7项通过，原生Rust→Swift开麦/HTTP拒绝2项通过；三种安全mutation均被断言检出。测试fake不代表生产联调。
- Swift音频/HTTP离线library编译通过、真实分支typecheck通过；C sherpa adapter编译链接官方arm64库；Rust NativeAudio/NativeTransport/Wake/VAD绑定已编译，A凭据入口负测通过。
- 真实KWS/VAD模型已加载：10秒合成静音和10秒确定性噪声无wake/VAD speech；本机Tingting合成“你好，小欧”触发1次、非唤醒合成话语触发0次。仅本地合成文件，不开扬声器、不用用户录音、不冒充MiMo或真人唤醒，不打包系统合成音频。
- 模型作者仓库单独声明Apache-2.0，固定Revision/hash先核后下载；Silero v5.1为作者MIT固定Git对象。详见`dependencies.md`、`assets.lock.json`、模型metadata与下载证据；不能以代码Apache许可替代模型许可。
- 旧UI回归18项通过、2项失败：AppleImportController旧导出测试与当前模块不匹配；health status spoof旧断言1!==0。182字节未变，不能先称voice引入回退，也不能先认定单纯测试过时。PM已交159以现行合同核对，未删除测试/放宽断言/改共享业务。`verify_voice.py --offline`仍exit1保留这些失败。
- **没有完整同App联合构建/真实GUI、实际麦克风/扬声器、AEC自回声、至少20次p95插话、真MiMo ASR/TTS、真实普通会话免点击发送或用户联合验收证据。** 这些保持Pending/Unknown，不能由上述计数抵消。

关键日志：`evidence/voice-final-rust-tests.log`、`native-no-credentials-final.log`、`real-detector-synthetic-speech.json`、`real-detector-negative.json`、`mutations-*.json`及初始`20260912T103703627457Z/legacy-ui.log`。初次Rust类型错误、Node strip-only参数属性错误已包内修复；初始命令错误不计正证据。旧UI失败全部保留，不能作为产品PASS证据。

## 角色与关卡

Gate1：方向继承、无第二App；待PM联合产品裁决。Gate2：音频易失、final走原记录链设计与离线测试成立，生产持久化待159接线。Gate3：关闭默认/权限撤回/拒绝调用离线覆盖，真实用途不生效。Gate4：协议/原生编译/合成模型证据Technical Partial，声学/同App尚缺。Gate5：用户无键盘价值未验证。逐行V01～V30见`acceptance_matrix.md`。

P3-157真实失败、P3-159自身未完成项和原独立评审暂停事实均保留。语音技术子集通过不等于完整LifeOS完成。

## 复跑与恢复

主入口：`python3 lifeos/engineering/LIFEOS-P3-160/tools/verify_voice.py --offline`。仅离线、每次独立日志目录，完整保留旧回归失败。原生/模型离线入口`tools/verify_native.py`；模型离线完整性`tools/prepare_voice_assets.py`；显式`--download-public`才允许从锁定公开URL取缺失依赖；mutation入口`tools/test_mutations.py`。

测试根唯一`/private/tmp/lifeos-p3-160-voice-v1/`，marker标记synthetic-only；仅有模型公开依赖/合成fixtures/构建测试缓存，无DB写入者或运行App。工具退出，不杀现有App、不删锁/旧包/历史。保留task-local资产用于可恢复复跑，不把模型下载/编译缓存放进产品delta。

检查点`engineering/LIFEOS-P3-160/checkpoint.json`包含合同/基底/协议/候选摘要、已完成/未完成、计数、排除失败和resume_from。A3需要159阶段边界的生产InteractionPort/完整候选接线回执；收到后只重跑受影响联合测试。B/C新真实麦克风/MiMo/凭据/会话自动发送/真实联合切换未批准，继续保持ASR/TTS/DeepSeek实际POST=0，无真实数据/凭据访问，无真实App切换。

需PM：接收固定增量并继续协调159同App联合验证与两项旧回归判定；真实阶段沿当前完整合同取得一次批准。无需重复A开工授权，无新任务建议。

## 同任务增量：离线 worker 修正

原交付快照保持只读。本次修复短噪声后打断失效及会话重置后旧残帧复用，旧实现2反例失败，修复后30 Rust测试通过；仅worker.rs修改，无公共端口变更。详见 `lifeos/engineering/LIFEOS-P3-160/worker_closure_report.md`、`delta_since_0d8a5345.json`、`delta_manifest_v3.json`。A3/B/C状态不变。

## A3 同任务协作：native producer / TTS 端口

已核验159的3份稳定接口拷贝，仅在inputs保留，不读活跃源码。最小接线建议与4项纯fake测试见 `lifeos/engineering/LIFEOS-P3-160/A3_native_playback_adapter.md`。本次生产源码增量为空；TTS registry/投影尚未由159实现，A3与真实验收仍Pending。

## A3 native播放完成与背压增量

按159端口需求新增generation/token消费反馈、2秒队列快照、显式finish_stream与仅实际buffer完成后的drained信号。相对93c98bb0仅1新增2修改。详见 `lifeos/engineering/LIFEOS-P3-160/native_playback_report.md` 和 `delta_manifest_v4.json`。纯fake/原生A拒绝与3项mutation通过，真实播放和联合验收仍未通过。
