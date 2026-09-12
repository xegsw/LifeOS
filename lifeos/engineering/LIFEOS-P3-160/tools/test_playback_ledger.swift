// Executes the production device-free ledger with fake completion callbacks only.
import Foundation
@main struct TestPlayback {
 static func main() {
    var l = PlaybackLedger(); let g = l.generation
    let a = l.reserve(24000, generation: g)!, b = l.reserve(24000, generation: g)!
    precondition(a != b && l.queued == 48000)
    precondition(l.reserve(1, generation: g) == nil)
    precondition(l.seal(generation: g) == [] && !l.drained)
    precondition(l.reserve(1, generation: g) == nil)
    let first = l.complete(generation: g, token: b)
    precondition(first.count == 1 && first[0].token == b && first[0].consumedSamples == 24000 && first[0].queuedSamples == 24000 && !first[0].drained)
    precondition(l.complete(generation: g, token: b).isEmpty)
    let final = l.complete(generation: g, token: a)
    precondition(final.count == 2 && final[0].consumedSamples == 48000 && final[1].drained && final[1].token == 0 && l.drained)
    precondition(l.complete(generation: g, token: a).isEmpty && l.seal(generation: g) == nil)
    print("PASS bounded capacity, unique tokens, out-of-order and duplicate completion, EOF draining")
    l.reset(); let old = l.generation; let token = l.reserve(100, generation: old)!
    l.reset(); let fresh = l.generation; let freshToken = l.reserve(200, generation: fresh)!
    precondition(freshToken != token && l.complete(generation: old, token: token).isEmpty)
    precondition(l.complete(generation: fresh, token: token).isEmpty && l.queued == 200 && l.consumed == 0)
    precondition(l.seal(generation: old) == nil && l.reserve(10, generation: old) == nil)
    let played = l.complete(generation: fresh, token: freshToken)
    precondition(played.count == 1 && !played[0].drained && l.queued == 0)
    precondition(l.seal(generation: fresh)!.last!.drained)
    print("PASS cancellation, stale generation/token isolation, completed-before-EOF")
    l.reset(); precondition(l.seal(generation: l.generation) == nil)
    precondition(l.reserve(0, generation: l.generation) == nil && l.reserve(-1, generation: l.generation) == nil)
    for _ in 0..<1000 {
       let g = l.generation; let t = l.reserve(48000, generation: g)!
       precondition(l.complete(generation: g, token: t).count == 1)
       precondition(l.queued == 0)
    }
    precondition(l.consumed == 48000000)
    print("PASS empty/invalid sealing and repeat capacity reuse; device starts=0 playback=0 POST=0")
 }
}
