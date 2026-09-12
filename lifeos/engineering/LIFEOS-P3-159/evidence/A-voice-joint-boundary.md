# P3-159 / P3-160 A 联合接线增量

本增量仅修改P3-159 Host voice_host.rs，未改导入的P3-160固定Gateway/worker/native资产，也未新增设备或网络授权。

新增离线内部Adapter：voice_gateway_begin_asr通过既有Host生成asrRequestId/segmentId，voice_gateway_poll_asr仅在Gateway::Outcome::Final后交voice_final_turn生成canonical UserTurn。Authority每次send/chunk/final重新读取A_contract_fake policy、active session、generation/policyRevision、conversation许可和pending registry。旧线程/撤权/代次变化在Gateway下一边界拒绝并取消，既有预算CAS的预留保留；最终文字仍走原对话预览，不执行Action。

实际原生入口仍不可用；voice_control不能创建会话/授权。Adapter只接受离线A合同fake策略，network_enabled模式拒绝。纯假Transport的start计数不是网络POST；测试PCM不是麦克风采样。

范围内测试：完整SSE仅到EOF时产生一轮UserTurn；partial和DONE数据段不提交；原对话产生一个待授权preview，无Action；重复EOF无第二轮；session generation/policy/conversation撤权各自取消fake传输，无预算退款。

仍未实现或未证明：SpeechOutput registry、TTS Host Authority与projection、真实AudioEngine producer接入、真实设备/声学/KWS和MiMo端到端。不能把本离线Adapter标为语音可用、真实通过、B/C Pass或整体完成。
