import AVFoundation
import AppKit
import Foundation

public typealias VoiceSamples = @convention(c) (UnsafeMutableRawPointer?, UnsafePointer<Float>?, Int32) -> Void
public typealias VoiceEvent = @convention(c) (UnsafeMutableRawPointer?, Int32) -> Void
// A library loaded into the existing Tauri process; no executable or HTTP service.
final class VoiceAudioEngine {
    let lock = NSRecursiveLock()
    var engine: AVAudioEngine?
    var player: AVAudioPlayerNode?
    var converter: AVAudioConverter?
    var observer: NSObjectProtocol?
    var lockObserver: NSObjectProtocol?
    var active = false
    var generation: UInt64 = 0
    var queued = 0
    var buffers: [ObjectIdentifier: AVAudioPCMBuffer] = [:]
    let context: UnsafeMutableRawPointer?
    let samples: VoiceSamples
    let event: VoiceEvent
    init(_ context: UnsafeMutableRawPointer?, _ samples: @escaping VoiceSamples, _ event: @escaping VoiceEvent) {
        self.context = context; self.samples = samples; self.event = event
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
        generation &+= 1; player?.stop()
        for b in buffers.values { b.floatChannelData?[0].update(repeating: 0, count: Int(b.frameLength)) }
        buffers.removeAll(); queued = 0
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
    func enqueue(_ bytes: UnsafePointer<UInt8>, _ size: Int, _ expected: UInt64) -> Int32 {
        lock.lock(); defer { lock.unlock() }
        guard active, expected == generation, let p = player else { return 8 }
        guard size > 0, size % 2 == 0, size / 2 <= 48000 - queued else { return 9 }
        guard let f = AVAudioFormat(standardFormatWithSampleRate: 24000, channels: 1), let b = AVAudioPCMBuffer(pcmFormat: f, frameCapacity: AVAudioFrameCount(size / 2)), let dst = b.floatChannelData?[0] else { return 4 }
        b.frameLength = b.frameCapacity
        for i in 0..<(size/2) { dst[i] = Float(Int16(bitPattern: UInt16(bytes[i*2]) | UInt16(bytes[i*2+1]) << 8)) / 32768 }
        let id = ObjectIdentifier(b); queued += size / 2; buffers[id] = b
        p.scheduleBuffer(b, completionCallbackType: .dataPlayedBack) { [weak self] _ in
            guard let self = self else { return }; self.lock.lock(); defer { self.lock.unlock() }
            if let done = self.buffers.removeValue(forKey: id) { self.queued -= Int(done.frameLength); done.floatChannelData?[0].update(repeating: 0, count: Int(done.frameLength)) }
        }
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
