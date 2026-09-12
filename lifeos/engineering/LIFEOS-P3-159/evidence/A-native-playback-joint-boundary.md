# 同一候选的原生播放端口与 Host 联合增量

固定输入 a38a90cf4f9a95bcec524c77cfb99985e75f108d：native_playback_manifest 所有artifact hash已核对，delta_since_93c98bb0的2个before/after和1个新增精确匹配；18项v4 voice身份与当前候选全部相同。未用输入覆盖Host/业务文件或复制旧182基底。

## 构建与作用域

build.rs现在编译PlaybackLedger.swift、AudioEngine.swift、MiMoHTTP.swift为静态A库并配置同候选链接；所有Rust模式均不定义LIFEOS_VOICE_REAL。仅单独typecheck real条件分支，不执行它。voice-native-tests仅开启3项Rust→Swift硬禁用/fake回调检查，不能开启音频或HTTP。可复跑 tools/verify_native_playback.py 已加入全量runner的native-playback步骤，总步骤24。Swift生产ledger假完成测试、同App Rust FFI测试均不打开设备、播放、读凭据或POST。

## Host接线

voice_playback.rs提供串行播放所有者与PlaybackPort；NativeAudio通过原有新API实现端口，fake仅替换设备端。

1. 已有voice_gateway_begin_tts执行一次后attach，不再次begin模型请求；重新核验Host登记，interrupt清旧native代次，保存request/local Playback epoch/native generation三者独立映射。
2. Store poll得到结果后调用receive，只有匹配request的PCM进入有界本地Playback；每次入队核验当前Host投影/许可/可见性、healthy和保存的native generation。按playback_status实际available容量分批enqueue_for；保留返回唯一token，迟到包不能重标新代次。
3. HTTP Complete意味着Host已经draining；只有所有本地待入队PCM已接受，才finish_stream。单纯EOF、seal或queued暂时为0均不是完成。
4. poll_with_host处理native反馈与背压释放。忽略旧代次，当前代次token、累计consumed、范围和快照须一致。最终只有drained token0、所有普通token已消费、当前Host draining、双方队列0、sealed/drained快照、consumed等于本次accepted且非零、healthy及再次Host校验同时成立，才能voice_playback_completed。重复完成不再次生效。
5. receive/poll_with_host错误先清逻辑/native队列，再调用既有Host中断并取消对应TTS，不影响ASR/Action。旧request错误不得取消新输出。低层accept_pcm/poll仅供内部测试/适配，串行所有者使用带Host收尾的包装；销毁/会话结束也须显式走stop_with_host后释放端口。

## 联合测试与未完成项

同一Store/Gateway/SpeechOutput注册到fake sink的SSE PCM、EOF、实际假消费回调走完整闭环；容量满保留待入队数据、消费后泵入/封闭；旧反馈、撤权、溢出、提前drained和旧request失败拒绝，错误收尾登记中断且不产生Action。NativeAudio真实实现的3项A FFI检查另跑；Swift生产ledger纯fake验证，二者不冒充实际dataPlayedBack或声学证据。

当前仍没有启用App内实时native音频/网络事件循环、真实设备/声学/KWS，也没有提供可用语音开关。Host串行适配组件已在同一候选编译和离线联测，但实际设备/前台生命周期端到端为Pending。B凭据阶段仍第5代暂停、预留5/回应0/POST0，不因此恢复。
