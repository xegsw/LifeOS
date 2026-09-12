# P3-160 离线 worker 包内修正

状态：Technical Partial / A3 Pending。按 PM 同任务继续指令执行，未改变接口、共享业务或真实授权。

事实：两个新增反例在 0d8a5345 的 worker 实现上均失败。短噪声片段未达到最低有效语音长度时，Segmenter 返回 None 并清空音频，Worker 原先未复位 utterance_active，随后 TTS 播放期间的新语音无法触发 Interrupted。另一个反例在宿主 suspend/ready 后未经过禁用态回调，旧的100采样残帧进入下一唤醒帧。

修正仅在 candidate/src/voice/worker.rs：分段结束即清除活动标记，包括无有效音频的分段；检测 Session generation 变化时清除旧残帧并重置本地检测器。同步本 Worker 的正常 wake/release generation，保留首个唤醒后帧。Segmenter 错误也按已有 Error 事件释放，不静默吞掉。公共端口未变，不新增 Voice App，不实现 host 持久业务。

验证：evidence/worker-closure-red.log 保存旧实现的2条失败断言；evidence/worker-closure-green.log 保存修复后完整30项 Rust测试全通过，含5项 Worker 场景。此前7 TS、2 native测试与真实模型合成音频证据保持历史归属，本次未重复声明它们在新快照复跑。旧UI18过2失败保持待159对账；本次不改旧记录。真实麦克风、扬声器、凭据访问与 Provider POST仍0。

交接：delta_since_0d8a5345.json 仅1修改，无新增/删除/共享文件变动；先校验 before hash，再应用 after blob。delta_manifest_v3.json 给出17文件完整身份。旧 f5a64094、0d8a5345及v1/v2 Manifest只读保留。182基底文件不打包，不覆盖159最新候选。

复跑：CARGO_TARGET_DIR=/private/tmp/lifeos-p3-160-voice-v1/worker-closure-target /Users/xxe/.cargo/bin/cargo test --offline --locked --manifest-path lifeos/engineering/LIFEOS-P3-160/tools/rust-tests/Cargo.toml。

角色/关卡：专项工程自检通过上述30项；未独立评审、未宣称A Pass。PM继续协调159的A3联合接线，B/C仍待真实授权。本次修正无需新增Task Contract。
