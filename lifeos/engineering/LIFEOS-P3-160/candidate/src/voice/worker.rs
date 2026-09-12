//! Serialized audio worker. Native tap only enqueues bounded frames to this worker.
//! Detector flags are acoustic outputs, never text/keyword-based business actions.
use super::{
    audio::{Audio, VadDetector, WakeDetector, FRAME},
    session::{Session, State},
};
use zeroize::Zeroize;
pub enum AudioEvent {
    Woke { generation: u64 },
    Interrupted,
    Utterance { generation: u64, audio: Audio },
    Error(&'static str),
}
pub struct Worker<W: WakeDetector, V: VadDetector> {
    pub session: Session,
    wake: W,
    vad: V,
    pending: Vec<f32>,
    utterance_active: bool,
    observed_generation: u64,
}
impl<W: WakeDetector, V: VadDetector> Worker<W, V> {
    pub fn new(wake: W, vad: V) -> Self {
        Self {
            session: Session::new(),
            wake,
            vad,
            pending: Vec::new(),
            utterance_active: false,
            observed_generation: 0,
        }
    }
    pub fn release(&mut self) {
        self.pending.zeroize();
        self.pending.clear();
        self.utterance_active = false;
        self.wake.reset();
        self.vad.reset();
        self.session.suspend();
        self.observed_generation = self.session.generation;
    }
    pub fn accept(&mut self, pcm: &[f32], now: u64) -> Vec<AudioEvent> {
        // Host may reset/revoke the public session between callbacks, even without
        // an intervening disabled callback. Old partial frames must not cross it.
        if self.observed_generation != self.session.generation {
            self.pending.zeroize();
            self.pending.clear();
            self.utterance_active = false;
            self.wake.reset();
            self.vad.reset();
            self.observed_generation = self.session.generation;
        }
        if matches!(self.session.state, State::Disabled | State::Recovering) {
            self.pending.zeroize();
            self.pending.clear();
            return vec![];
        }
        if pcm.len() > 8192 || pcm.iter().any(|f| !f.is_finite() || *f < -1.0 || *f > 1.0) {
            self.release();
            return vec![AudioEvent::Error("invalid_pcm")];
        }
        self.pending.extend_from_slice(pcm);
        let mut result = Vec::new();
        while self.pending.len() >= FRAME {
            let mut frame: Vec<f32> = self.pending.drain(..FRAME).collect();
            let mut i16frame: Vec<i16> = frame
                .iter()
                .map(|f| (*f * 32767.0).round() as i16)
                .collect();
            if self.session.state == State::WakeListening {
                self.session.wake_ring.push(&i16frame);
                match self.wake.accept(&frame) {
                    Ok(true) => {
                        if let Ok(g) = self.session.wake(now) {
                            self.observed_generation = g;
                            self.wake.reset();
                            self.vad.reset();
                            self.utterance_active = false;
                            result.push(AudioEvent::Woke { generation: g });
                        }
                    }
                    Ok(false) => {}
                    Err(e) => {
                        self.release();
                        result.push(AudioEvent::Error(e));
                    }
                }
                // The complete frame which contained wake stays local. Upload begins next frame.
            } else if matches!(
                self.session.state,
                State::Capturing | State::Speaking | State::AwaitingAssistant
            ) {
                match self.vad.speech(&frame) {
                    Ok(speech) => {
                        if speech && !self.utterance_active {
                            self.utterance_active = true;
                            if self.session.state == State::Speaking {
                                self.session.interrupt(now);
                                result.push(AudioEvent::Interrupted);
                            }
                        }
                        // Segmenter buffers post-wake onset; no pre-wake ring is ever passed to ASR.
                        match self.session.segmenter.accept(&i16frame, speech) {
                            Ok(audio) => {
                                // A short/noise segment can end without producing audio.
                                if self.session.segmenter.buffered() == 0 {
                                    self.utterance_active = false;
                                }
                                if let Some(audio) = audio {
                                    result.push(AudioEvent::Utterance {
                                        generation: self.session.generation,
                                        audio,
                                    });
                                }
                            }
                            Err(e) => {
                                self.release();
                                result.push(AudioEvent::Error(e));
                            }
                        }
                    }
                    Err(e) => {
                        self.release();
                        result.push(AudioEvent::Error(e));
                    }
                }
            }
            frame.zeroize();
            i16frame.zeroize();
        }
        result
    }
}
impl<W: WakeDetector, V: VadDetector> Drop for Worker<W, V> {
    fn drop(&mut self) {
        self.release();
    }
}
#[cfg(test)]
mod tests {
    use super::super::session::Policy;
    use super::*;
    // Explicit deterministic acoustic flag fakes. These do NOT prove wake or VAD models.
    struct ContractWakeFake {
        fires: bool,
    }
    impl WakeDetector for ContractWakeFake {
        fn accept(&mut self, _: &[f32]) -> Result<bool, &'static str> {
            let f = self.fires;
            self.fires = false;
            Ok(f)
        }
        fn reset(&mut self) {}
    }
    struct ContractVadFake {
        speech: bool,
    }
    impl VadDetector for ContractVadFake {
        fn speech(&mut self, _: &[f32]) -> Result<bool, &'static str> {
            Ok(self.speech)
        }
        fn reset(&mut self) {}
    }
    fn worker() -> Worker<ContractWakeFake, ContractVadFake> {
        let mut w = Worker::new(
            ContractWakeFake { fires: true },
            ContractVadFake { speech: true },
        );
        w.session.policy(
            Policy {
                enabled: true,
                asr: true,
                tts: true,
                session_turn: true,
                revision: 1,
            },
            0,
        );
        w.session.ready(true, true, true).unwrap();
        w
    }
    #[test]
    fn wake_frame_never_enters_upload_and_first_postwake_frame_kept() {
        let mut w = worker();
        assert!(matches!(
            w.accept(&[0.9; 320], 0)[0],
            AudioEvent::Woke { .. }
        ));
        assert_eq!(w.session.segmenter.buffered(), 0);
        for _ in 0..5 {
            w.accept(&[0.2; 320], 20);
        }
        w.vad.speech = false;
        let mut out = Vec::new();
        for _ in 0..40 {
            out.extend(w.accept(&[0.0; 320], 40));
        }
        let AudioEvent::Utterance { audio, .. } = out.pop().unwrap() else {
            panic!()
        };
        assert!(audio.0.iter().all(|v| *v < 7000));
        assert_eq!(audio.0[0], 6553);
    }
    #[test]
    fn barge_in_stops_before_utterance_and_preserves_opening() {
        let mut w = worker();
        w.accept(&[0.1; 320], 0);
        let g = w.session.generation;
        let pg = w.session.speak(g, 1, false, true).unwrap();
        w.session.playback.push(pg, &[0, 0, 1, 0]).unwrap();
        let e = w.accept(&[0.3; 320], 10);
        assert!(matches!(e[0], AudioEvent::Interrupted));
        assert_eq!(w.session.playback.queued(), 0);
        assert_eq!(w.session.segmenter.buffered(), 320);
        assert_eq!(w.session.generation, g);
    }
    #[test]
    fn invalid_float_fails_closed_and_releases_pending() {
        let mut w = worker();
        w.accept(&[0.1; 100], 0);
        assert_eq!(w.pending.len(), 100);
        assert!(matches!(w.accept(&[f32::NAN], 1)[0], AudioEvent::Error(_)));
        assert!(w.pending.is_empty());
        assert_eq!(w.session.state, State::Recovering);
    }
    #[test]
    fn discarded_short_noise_does_not_disable_next_barge_in() {
        let mut w = worker();
        w.accept(&[0.1; FRAME], 0);
        w.accept(&[0.2; FRAME], 20);
        w.vad.speech = false;
        for _ in 0..40 {
            assert!(w.accept(&[0.0; FRAME], 40).is_empty());
        }
        assert_eq!(w.session.segmenter.buffered(), 0);
        let g = w.session.generation;
        let pg = w.session.speak(g, 1, false, true).unwrap();
        w.session.playback.push(pg, &[1, 0]).unwrap();
        w.vad.speech = true;
        let events = w.accept(&[0.3; FRAME], 1000);
        assert!(matches!(events.first(), Some(AudioEvent::Interrupted)));
        assert_eq!(w.session.playback.queued(), 0);
        assert_eq!(w.session.segmenter.buffered(), FRAME);
    }
    #[test]
    fn external_session_reset_discards_partial_old_frame() {
        let mut w = worker();
        w.accept(&[0.1; FRAME], 0);
        w.accept(&[0.9; 100], 20);
        assert_eq!(w.pending.len(), 100);
        w.session.suspend();
        w.session.ready(true, true, true).unwrap();
        w.wake.fires = true;
        assert!(w.accept(&[0.0; FRAME - 100], 40).is_empty());
        assert_eq!(w.session.state, State::WakeListening);
        assert_eq!(w.pending.len(), FRAME - 100);
        assert!(matches!(w.accept(&[0.0; 100], 60).first(), Some(AudioEvent::Woke { .. })));
        assert_eq!(w.session.segmenter.buffered(), 0);
    }

}
