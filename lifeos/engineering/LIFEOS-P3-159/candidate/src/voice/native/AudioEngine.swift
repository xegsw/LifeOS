import AVFoundation
import AppKit
import Foundation

public typealias VoiceSamples = @convention(c) (UnsafeMutableRawPointer?, UnsafePointer<Float>?, Int32) -> Void
public typealias VoiceEvent = @convention(c) (UnsafeMutableRawPointer?, Int32) -> Void
public typealias VoicePlayback = @convention(c) (UnsafeMutableRawPointer?, UInt64, UInt64, UInt64, Int32, Int32) -> Void
// A library loaded into the existing Tauri process; no executable or HTTP service.
final class VoiceAudioEngine {
    let lock = NSRecursiveLock()
    var engine: AVAudioEngine?
    var player: AVAudioPlayerNode?
    var converter: AVAudioConverter?
    var observer: NSObjectProtocol?
    var lockObserver: NSObjectProtocol?
    var active = false
    var playback = PlaybackLedger()
    var generation: UInt64 { playback.generation }
    var buffers: [ObjectIdentifier: AVAudioPCMBuffer] = [:]
    let context: UnsafeMutableRawPointer?
    let samples: VoiceSamples
    let event: VoiceEvent
    let playbackEvent: VoicePlayback?
    init(_ context: UnsafeMutableRawPointer?, _ samples: @escaping VoiceSamples, _ event: @escaping VoiceEvent, _ playbackEvent: VoicePlayback? = nil) {
        self.context = context; self.samples = samples; self.event = event; self.playbackEvent = playbackEvent
    }
    func start() -> Int32 {
        #if !LIFEOS_VOICE_REAL
        return 1 // A build cannot start a microphone, regardless of caller values.
        #else
        lock.lock(); defer { lock.unlock() }
        guard !active else { return 0 }
        // Never invoke requestAccess. The user grants permission in system UI.
        guard AVCaptureDevice.authorizationStatus(for: .audio) == .authorized else { return 2 }
        let e = AVAudioEngine()
        do {
            try e.inputNode.setVoiceProcessingEnabled(true)
            guard e.inputNode.isVoiceProcessingEnabled else { return 3 }
            let input = e.inputNode.outputFormat(forBus: 0)
            guard input.sampleRate > 0, input.channelCount > 0,
                  let target = AVAudioFormat(standardFormatWithSampleRate: 16000, channels: 1),
                  let convert = AVAudioConverter(from: input, to: target) else { return 4 }
            let p = AVAudioPlayerNode()
            e.attach(p)
            e.connect(p, to: e.mainMixerNode, format: AVAudioFormat(standardFormatWithSampleRate: 24000, channels: 1))
            converter = convert; engine = e; player = p; active = true
            e.inputNode.installTap(onBus: 0, bufferSize: 1024, format: input) { [weak self] buffer, _ in
                guard let self = self else { return }
                // Do not block the audio callback on control operations.
                guard self.lock.try() else { return }
                defer { self.lock.unlock() }
                guard self.active, let c = self.converter else { return }
                let capacity = AVAudioFrameCount(ceil(Double(buffer.frameLength) * 16000 / input.sampleRate) + 64)
                guard capacity <= 8192, let output = AVAudioPCMBuffer(pcmFormat: target, frameCapacity: capacity) else { return }
                var supplied = false
                var error: NSError?
                let status = c.convert(to: output, error: &error) { _, state in
                    if supplied { state.pointee = .noDataNow; return nil }
                    supplied = true; state.pointee = .haveData; return buffer
                }
                if error == nil && status != .error, let pcm = output.floatChannelData?[0] {
                    self.samples(self.context, pcm, Int32(output.frameLength))
                    pcm.update(repeating: 0, count: Int(output.frameLength))
                }
            }
            try e.start(); p.play()
            observer = NotificationCenter.default.addObserver(forName: .AVAudioEngineConfigurationChange, object: e, queue: nil) { [weak self] _ in self?.suspend(5) }
            lockObserver = DistributedNotificationCenter.default().addObserver(forName: NSNotification.Name("com.apple.screenIsLocked"), object: nil, queue: nil) { [weak self] _ in self?.suspend(6) }
            return 0
        } catch { stop(); return 7 }
        #endif
    }
    func suspend(_ reason: Int32) { lock.lock();defer {lock.unlock()};guard active else{return};stop();event(context, reason) }
    func stopPlayback() {
        lock.lock(); defer { lock.unlock() }
        playback.reset(); player?.stop()
        for b in buffers.values { b.floatChannelData?[0].update(repeating: 0, count: Int(b.frameLength)) }
        buffers.removeAll()
        if active { player?.play() } // microphone stays live for barge-in
    }
    func stop() {
        lock.lock(); defer { lock.unlock() }
        active = false; stopPlayback()
        if let o = observer { NotificationCenter.default.removeObserver(o) }; observer = nil
        if let o = lockObserver { DistributedNotificationCenter.default().removeObserver(o) }; lockObserver = nil
        if let e = engine { e.inputNode.removeTap(onBus: 0); e.stop(); e.reset() }
        converter = nil; player = nil; engine = nil
    }
    func enqueue(_ bytes: UnsafePointer<UInt8>, _ size: Int, _ expected: UInt64, _ tokenOut: UnsafeMutablePointer<UInt64>? = nil) -> Int32 {
        lock.lock(); defer { lock.unlock() }
        guard active, expected == generation, let p = player else { return 8 }
        guard size > 0, size % 2 == 0, !playback.sealed, size / 2 <= PlaybackLedger.capacity - playback.queued else { return 9 }
        guard let f = AVAudioFormat(standardFormatWithSampleRate: 24000, channels: 1), let b = AVAudioPCMBuffer(pcmFormat: f, frameCapacity: AVAudioFrameCount(size / 2)), let dst = b.floatChannelData?[0] else { return 4 }
        b.frameLength = b.frameCapacity
        for i in 0..<(size/2) { dst[i] = Float(Int16(bitPattern: UInt16(bytes[i*2]) | UInt16(bytes[i*2+1]) << 8)) / 32768 }
        guard let token = playback.reserve(size / 2, generation: expected) else { return 9 }
        tokenOut?.pointee = token
        let id = ObjectIdentifier(b); buffers[id] = b
        p.scheduleBuffer(b, completionCallbackType: .dataPlayedBack) { [weak self] _ in
            guard let self = self else { return }; self.lock.lock(); defer { self.lock.unlock() }
            let feedback = self.playback.complete(generation: expected, token: token)
            // Ignore stale or duplicate completion BEFORE accessing a possibly reused buffer ID.
            guard !feedback.isEmpty else { return }
            if let done = self.buffers.removeValue(forKey: id) { done.floatChannelData?[0].update(repeating: 0, count: Int(done.frameLength)) }
            self.emit(feedback)
        }
        return 0
    }
    func emit(_ feedback: [PlaybackFeedback]) {
        for f in feedback { playbackEvent?(context, f.generation, f.token, f.consumedSamples, Int32(f.queuedSamples), f.drained ? 2 : 1) }
    }
    func finishStream(_ expected: UInt64) -> Int32 {
        lock.lock(); defer { lock.unlock() }
        guard active, let feedback = playback.seal(generation: expected) else { return 8 }
        emit(feedback); return 0
    }
    func snapshot(_ expected: UInt64, _ queued: UnsafeMutablePointer<Int32>, _ consumed: UnsafeMutablePointer<UInt64>, _ state: UnsafeMutablePointer<Int32>) -> Int32 {
        lock.lock(); defer { lock.unlock() }
        guard expected == generation else { return 8 }
        queued.pointee = Int32(playback.queued); consumed.pointee = playback.consumed
        state.pointee = playback.drained ? 2 : (playback.sealed ? 1 : 0)
        return 0
    }
    deinit { stop() }
}
@_cdecl("lifeos_voice_audio_create") public func createAudio(_ c: UnsafeMutableRawPointer?, _ s: @escaping VoiceSamples, _ e: @escaping VoiceEvent) -> UnsafeMutableRawPointer { Unmanaged.passRetained(VoiceAudioEngine(c,s,e)).toOpaque() }
@_cdecl("lifeos_voice_audio_start") public func startAudio(_ p: UnsafeMutableRawPointer) -> Int32 { Unmanaged<VoiceAudioEngine>.fromOpaque(p).takeUnretainedValue().start() }
@_cdecl("lifeos_voice_audio_stop") public func stopAudio(_ p: UnsafeMutableRawPointer) { Unmanaged<VoiceAudioEngine>.fromOpaque(p).takeUnretainedValue().stop() }
@_cdecl("lifeos_voice_audio_interrupt") public func interruptAudio(_ p: UnsafeMutableRawPointer) -> UInt64 { let e = Unmanaged<VoiceAudioEngine>.fromOpaque(p).takeUnretainedValue(); e.stopPlayback(); return e.generation }
@_cdecl("lifeos_voice_audio_push") public func pushAudio(_ p: UnsafeMutableRawPointer, _ b: UnsafePointer<UInt8>, _ n: Int32, _ g: UInt64) -> Int32 { Unmanaged<VoiceAudioEngine>.fromOpaque(p).takeUnretainedValue().enqueue(b,Int(n),g) }
@_cdecl("lifeos_voice_audio_destroy") public func destroyAudio(_ p: UnsafeMutableRawPointer) { Unmanaged<VoiceAudioEngine>.fromOpaque(p).release() }

// Additive ABI: existing create/push remain available; v2 reports played buffers.
@_cdecl("lifeos_voice_audio_create_v2") public func createAudioV2(_ c: UnsafeMutableRawPointer?, _ s: @escaping VoiceSamples, _ e: @escaping VoiceEvent, _ f: @escaping VoicePlayback) -> UnsafeMutableRawPointer { Unmanaged.passRetained(VoiceAudioEngine(c,s,e,f)).toOpaque() }
@_cdecl("lifeos_voice_audio_push_v2") public func pushAudioV2(_ p: UnsafeMutableRawPointer, _ b: UnsafePointer<UInt8>, _ n: Int32, _ g: UInt64, _ token: UnsafeMutablePointer<UInt64>) -> Int32 { Unmanaged<VoiceAudioEngine>.fromOpaque(p).takeUnretainedValue().enqueue(b,Int(n),g,token) }
@_cdecl("lifeos_voice_audio_finish_stream") public func finishAudioStream(_ p: UnsafeMutableRawPointer, _ g: UInt64) -> Int32 { Unmanaged<VoiceAudioEngine>.fromOpaque(p).takeUnretainedValue().finishStream(g) }
@_cdecl("lifeos_voice_audio_playback_status") public func playbackStatus(_ p: UnsafeMutableRawPointer, _ g: UInt64, _ q: UnsafeMutablePointer<Int32>, _ c: UnsafeMutablePointer<UInt64>, _ s: UnsafeMutablePointer<Int32>) -> Int32 { Unmanaged<VoiceAudioEngine>.fromOpaque(p).takeUnretainedValue().snapshot(g,q,c,s) }

@_cdecl("lifeos_voice_audio_generation") public func audioGeneration(_ p: UnsafeMutableRawPointer) -> UInt64 { let e = Unmanaged<VoiceAudioEngine>.fromOpaque(p).takeUnretainedValue(); e.lock.lock(); defer { e.lock.unlock() }; return e.generation }
