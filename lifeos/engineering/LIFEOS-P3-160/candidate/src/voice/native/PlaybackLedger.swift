// Device-free accounting shared by the real native engine and synthetic tests.
// Caller serializes access. No host authority, registry, or business state here.
struct PlaybackFeedback: Equatable {
    let generation: UInt64
    let token: UInt64 // 0 only for the one stream-drained event
    let consumedSamples: UInt64 // cumulative actually played buffers in this generation
    let queuedSamples: Int
    let drained: Bool
}
struct PlaybackLedger {
    static let capacity = 48000 // 2 seconds, mono 24 kHz
    private(set) var generation: UInt64 = 0
    private(set) var queued = 0
    private(set) var consumed: UInt64 = 0
    private(set) var sealed = false
    private(set) var drained = false
    private var nextToken: UInt64 = 1
    private var accepted: UInt64 = 0
    private var pending: [UInt64: Int] = [:]
    mutating func reset() {
        precondition(generation < UInt64.max, "playback generation exhausted")
        generation += 1
        queued = 0; consumed = 0; accepted = 0; sealed = false; drained = false
        pending.removeAll()
    }
    mutating func reserve(_ samples: Int, generation expected: UInt64) -> UInt64? {
        guard expected == generation, !sealed, samples > 0,
              samples <= Self.capacity - queued, nextToken < UInt64.max,
              accepted <= UInt64.max - UInt64(samples) else { return nil }
        let token = nextToken; nextToken += 1
        pending[token] = samples; queued += samples; accepted += UInt64(samples)
        return token
    }
    mutating func seal(generation expected: UInt64) -> [PlaybackFeedback]? {
        guard expected == generation, !sealed, accepted > 0 else { return nil }
        sealed = true
        return drainIfReady()
    }
    mutating func complete(generation expected: UInt64, token: UInt64) -> [PlaybackFeedback] {
        guard expected == generation, let samples = pending.removeValue(forKey: token) else { return [] }
        queued -= samples; consumed += UInt64(samples)
        let played = PlaybackFeedback(generation: generation, token: token,
            consumedSamples: consumed, queuedSamples: queued, drained: false)
        return [played] + drainIfReady()
    }
    private mutating func drainIfReady() -> [PlaybackFeedback] {
        guard sealed, !drained, pending.isEmpty else { return [] }
        drained = true
        return [PlaybackFeedback(generation: generation, token: 0,
            consumedSamples: consumed, queuedSamples: 0, drained: true)]
    }
}
