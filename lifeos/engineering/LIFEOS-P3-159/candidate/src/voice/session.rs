use super::audio::{Playback, Segmenter, WakeRing};
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum State {
    Disabled,
    WakeListening,
    Capturing,
    Transcribing,
    AwaitingAssistant,
    Speaking,
    Recovering,
}
#[derive(Default, Clone, Copy)]
pub struct Policy {
    pub enabled: bool,
    pub asr: bool,
    pub tts: bool,
    pub session_turn: bool,
    pub revision: u64,
}
/// Policy comes from a host-owned, validated snapshot. Never deserialize as an IPC grant.
pub struct Session {
    pub state: State,
    pub generation: u64,
    pub playback: Playback,
    pub segmenter: Segmenter,
    pub wake_ring: WakeRing,
    policy: Policy,
    last_activity: u64,
    asr_busy: bool,
    turn_busy: bool,
}
impl Session {
    pub fn new() -> Self {
        Self {
            state: State::Disabled,
            generation: 0,
            playback: Playback::new(),
            segmenter: Segmenter::new(800).unwrap(),
            wake_ring: WakeRing::new(),
            policy: Policy::default(),
            last_activity: 0,
            asr_busy: false,
            turn_busy: false,
        }
    }
    pub fn policy(&mut self, p: Policy, now: u64) {
        self.release();
        self.policy = p;
        self.last_activity = now;
        self.state = if p.enabled {
            State::Recovering
        } else {
            State::Disabled
        };
    }
    pub fn ready(
        &mut self,
        microphone_granted: bool,
        model_ready: bool,
        unlocked: bool,
    ) -> Result<(), &'static str> {
        if !self.policy.enabled || !microphone_granted || !model_ready || !unlocked {
            self.suspend();
            return Err("local_voice_unavailable");
        }
        self.state = State::WakeListening;
        Ok(())
    }
    pub fn wake(&mut self, now: u64) -> Result<u64, &'static str> {
        if self.state != State::WakeListening {
            return Err("not_listening");
        }
        self.wake_ring.clear();
        self.segmenter.reset();
        self.generation += 1;
        self.last_activity = now;
        self.state = State::Capturing;
        Ok(self.generation)
    }
    pub fn begin_asr(&mut self) -> Result<u64, &'static str> {
        if self.state != State::Capturing || !self.policy.asr || self.asr_busy {
            return Err("asr_denied");
        }
        self.asr_busy = true;
        self.state = State::Transcribing;
        Ok(self.generation)
    }
    pub fn asr_final(&mut self, g: u64, nonempty: bool) -> Result<(), &'static str> {
        if g != self.generation || !self.asr_busy {
            return Err("stale_asr");
        }
        self.asr_busy = false;
        self.segmenter.reset();
        if !nonempty || !self.policy.session_turn || self.turn_busy {
            self.state = State::Capturing;
            return Err("turn_denied");
        }
        self.turn_busy = true;
        self.state = State::AwaitingAssistant;
        Ok(())
    }
    pub fn assistant_finished(&mut self, g: u64, now: u64) {
        if g == self.generation {
            self.turn_busy = false;
            self.last_activity = now;
            if self.state == State::AwaitingAssistant {
                self.state = State::Capturing;
            }
        }
    }
    pub fn may_speak(&self, g: u64, revision: u64, proactive: bool, visible: bool) -> bool {
        self.policy.enabled
            && self.policy.tts
            && g == self.generation
            && revision == self.policy.revision
            && (!proactive || visible)
            && matches!(self.state, State::Capturing | State::AwaitingAssistant)
    }
    pub fn speak(
        &mut self,
        g: u64,
        revision: u64,
        proactive: bool,
        visible: bool,
    ) -> Result<u64, &'static str> {
        if !self.may_speak(g, revision, proactive, visible) {
            return Err("speech_denied");
        }
        self.state = State::Speaking;
        Ok(self.playback.begin())
    }
    /// Stop playback first. No action, feedback, task cancellation or business mutation.
    pub fn interrupt(&mut self, now: u64) {
        self.playback.stop();
        self.last_activity = now;
        if self.state == State::Speaking {
            self.state = State::Capturing;
        }
    }
    pub fn idle(&mut self, now: u64) {
        if self.state == State::Capturing
            && !self.asr_busy
            && !self.turn_busy
            && self.segmenter.buffered() == 0
            && now.saturating_sub(self.last_activity) >= 60000
        {
            self.end();
        }
    }
    pub fn end(&mut self) {
        self.release();
        self.state = if self.policy.enabled {
            State::WakeListening
        } else {
            State::Disabled
        };
    }
    pub fn suspend(&mut self) {
        self.release();
        self.state = if self.policy.enabled {
            State::Recovering
        } else {
            State::Disabled
        };
    }
    pub fn fail(&mut self, now: u64) {
        self.release();
        self.last_activity = now;
        self.state = if self.policy.enabled {
            State::Recovering
        } else {
            State::Disabled
        };
    }
    fn release(&mut self) {
        self.generation += 1;
        self.playback.stop();
        self.segmenter.reset();
        self.wake_ring.clear();
        self.asr_busy = false;
        self.turn_busy = false;
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn active() -> Session {
        let mut s = Session::new();
        s.policy(
            Policy {
                enabled: true,
                asr: true,
                tts: true,
                session_turn: true,
                revision: 1,
            },
            0,
        );
        s.ready(true, true, true).unwrap();
        s.wake(0).unwrap();
        s
    }
    #[test]
    fn all_off_by_default() {
        let mut s = Session::new();
        assert_eq!(s.state, State::Disabled);
        assert!(s.wake(0).is_err());
        assert!(s.begin_asr().is_err());
        assert!(!s.may_speak(0, 0, false, true));
    }
    #[test]
    fn purpose_revocation_isolates_late_final() {
        let mut s = active();
        let g = s.begin_asr().unwrap();
        s.policy(Policy::default(), 0);
        assert_eq!(s.asr_final(g, true), Err("stale_asr"));
        assert_eq!(s.state, State::Disabled);
    }
    #[test]
    fn no_idle_timeout_during_processing_recording_playback() {
        let mut s = active();
        let g = s.begin_asr().unwrap();
        s.idle(999999);
        assert_eq!(s.state, State::Transcribing);
        s.asr_final(g, true).unwrap();
        s.idle(999999);
        assert_eq!(s.state, State::AwaitingAssistant);
        s.assistant_finished(g, 999999);
        s.segmenter.accept(&[1; 320], true).unwrap();
        s.idle(1999999);
        assert_eq!(s.state, State::Capturing);
        s.speak(g, 1, false, true).unwrap();
        s.idle(9999999);
        assert_eq!(s.state, State::Speaking);
    }
    #[test]
    fn end_and_lock_discard_late_voice_only() {
        let mut s = active();
        let g = s.generation;
        s.speak(g, 1, false, true).unwrap();
        s.suspend();
        assert_eq!(s.state, State::Recovering);
        assert_eq!(s.playback.queued(), 0);
        assert!(!s.may_speak(g, 1, false, true));
        assert!(s.ready(false, true, true).is_err());
    }
    #[test]
    fn interruption_keeps_business_wait() {
        let mut s = active();
        let g = s.begin_asr().unwrap();
        s.asr_final(g, true).unwrap();
        s.speak(g, 1, false, true).unwrap();
        s.interrupt(10);
        assert!(s.turn_busy);
        assert_eq!(s.generation, g);
    }
    #[test]
    fn proactive_hidden_and_unwoken_silent() {
        let mut s = active();
        assert!(!s.may_speak(s.generation, 1, true, false));
        s.end();
        assert!(!s.may_speak(s.generation, 1, false, true));
    }
}
