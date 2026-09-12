# A ASR producer 联合增量

完整候选新增 Host VoiceProducer：串行消费 NativeAudio Input，复核 Host session/policy 与独立worker epoch，只对Utterance发起一次原 Gateway ASR；最终SSE转原 interaction submit_user_turn，部分文本不交业务。原对话预览与Action事务仍由Host持有。NativeTransport终端/错误释放request，其他用途frame原requestId交回speech owner，不冒充ASR；NativeAudio健康失败/设备停止清理，打断先停止native播放并将事件交回Host。

两个新生产Store联合fake测试：wake/音频分段→ASR→部分文本不落库→最终只产生一份待授权预览；过期ID不取消当前请求，撤权/设备丢失取消ASR且预算不退。完整24步回归、329 Rust、同App Rust→Swift3项、双模式构建通过。当前329包含元数据绑定修正的忠实Store/FFI对照。

局限：该适配器已编译入同候选，但App顶层统一audio/ASR/TTS循环及启用/关闭生命周期组合仍待接入。音频端口仍A硬禁用，真实麦克风/声学KWS/MiMo/播放0；不宣称可用语音或真实联合验收。当前producer未自动向模型提交任何真实资料，也未绕过原预览确认。

真实元数据检查已结束，无第二次读取。首次绑定代码缺陷与离线修正见B-metadata-binding-fix.md，不把修正外推为-25293根因已解决。
