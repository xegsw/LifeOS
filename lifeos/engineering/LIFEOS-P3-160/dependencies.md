# 语音依赖与官方协议核对

2026-09-12，仅公开技术输入，无模型POST、用户音频或凭据读取。

| 依赖/事实 | 固定对象与证据 | 状态 |
|---|---|---|
| MiMo ASR | [官方ASR](https://mimo.mi.com/docs/en-US/api/audio/Speech-Recognition)：mimo-v2.5-asr，单音频wav/base64，转写SSE；不发送背景包 | 纯协议与合成分片测试；真实服务未调用 |
| MiMo TTS | [官方TTS API](https://mimo.mi.com/docs/en-US/api/audio/tts)；[官方合成指南](https://mimo.mi.com/docs/en-US/quick-start/usage-guide/audio/speech-synthesis-v2.5)：24kHz mono PCM16LE，delta.audio.data；assistant目标文本，不开智能优化/设计/克隆 | 已实现backend adapter，真实首音/音质待B |
| sherpa代码 | [v1.13.7](https://github.com/k2-fsa/sherpa-onnx/releases/tag/v1.13.7)，Apache-2.0；header/license hashes见evidence/dependencies.json | 编译并链接官方arm64 no-tts库，未打包用户App |
| sherpa二进制 | sherpa-onnx-v1.13.7-osx-arm64-shared-no-tts-lib.tar.bz2；发布SHA256 b3a5484f071094d3a922062e6793aca3e0ccc7388bfa5797959fa51fabffc906，下载后吻合 | task-local公开代码依赖；evidence/sherpa-download.json |
| KWS模型 | [官方模型说明](https://k2-fsa.github.io/sherpa/onnx/kws/pretrained_models/index.html)直接指向[作者仓库](https://modelscope.cn/models/pkufool/sherpa-onnx-kws-zipformer-wenetspeech-3.3M-2024-01-01)；作者README单独声明Apache License 2.0。README字节hash与仓库元数据一致 | 不是以代码许可代替模型许可；Revision/SHA256见assets.lock.json及model-file-metadata.json |
| Silero VAD | [作者v5.1 MIT许可](https://raw.githubusercontent.com/snakers4/silero-vad/v5.1/LICENSE)，固定commit84768cefdf5a3852400e9d8237f7315d14b64a08；模型SHA2562623a2953f6ff3d2c1e61740c6cdb7168133479b267dfef114a4a3cc5bdd788f | SHA256是从固定Git对象下载后的本地值，不伪称有独立发布checksum |
| ONNX Runtime | [官方MIT](https://raw.githubusercontent.com/microsoft/onnxruntime/v1.17.1/LICENSE)；许可副本inputs/ONNXRuntime-LICENSE | 与官方sherpa依赖包一起仅测试使用；最终包完整third-party notices仍由集成者核验 |
| Rust依赖 | 沿完整基底serde1.0.229/serde_json1.0.151/zeroize1.8.1，独立测试lock列transitives | cargo --locked --offline，未更新共享Cargo |
| macOS | 系统AVFoundation/AppKit/Foundation，swiftc/clang原生库 | 无另外App/后台服务 |

模型下载前先读取作者许可与版本/hash元数据；未抓取官方示例录音。KWS的n ǐ h ǎo x iǎo ōu全部在tokens.txt中。10s合成静音/10s确定性噪声无唤醒；本机Tingting合成“你好，小欧”触发一次，合成非唤醒句触发零次。Tingting仅通过say -o输出task-local测试WAV，未发声、不打包/不再分发，不把系统语音资产当可商用再分发许可。

这是一组小型离线输入，不能证明真人无键盘可靠唤醒、AEC自回声隔离、自然多轮或p95。B/C未获批准，真实音频/费用/服务端保存政策仍需该阶段核验；未宣称零留存。

早期GitHub API 403元数据限流已通过同站公开release资产页取得官方hash，不绕过账号权限。最初模型许可Unknown的事实保留在中间交接；后续作者材料补齐不追溯改写f5a64094。
