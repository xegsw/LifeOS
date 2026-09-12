//! Deterministic backend network lifecycle; injected host ports own grants/keys/HTTP.
use super::{
    audio::Audio,
    budget::{self, BudgetStore, Phase, Purpose, Reservation},
    mimo::{self, Mode, Part, RequestBody, Sse},
};
#[derive(Clone, Debug, PartialEq, Eq)]
pub struct Binding {
    pub request_id: String,
    pub session_id: String,
    pub generation: u64,
    pub policy_revision: u64,
}
/// Cannot be constructed from an IPC permission flag. The host implementation rechecks
/// its registry, grants, source revisions and session on EVERY send/chunk/final boundary.
pub trait Authority {
    fn check(&self, b: &Binding, p: Purpose) -> Result<(), &'static str>;
    fn projection(&self, b: &Binding) -> Result<String, &'static str>;
    fn now(&self) -> (u64, u64);
}
pub enum Frame {
    Connecting,
    Headers(u16),
    Data(Vec<u8>),
    Eof,
    Failure,
}
pub trait Transport {
    /// Implementation MUST use original CredentialPort and fixed endpoint, no redirects,
    /// no proxy, no retries, RAM-only request/response. A uses ContractTransportFake only.
    fn start(&mut self, id: &str, endpoint: &str, body: RequestBody) -> Result<(), &'static str>;
    fn cancel(&mut self, id: &str);
}
pub enum Outcome {
    Parts(Vec<Part>),
    Final(String),
    Complete,
    Pending,
}
struct Inflight {
    binding: Binding,
    purpose: Purpose,
    parser: Sse,
    started: u64,
    last_data: u64,
    headers: bool,
    received_audio: bool,
}
pub struct Gateway {
    asr: Option<Inflight>,
    tts: Option<Inflight>,
}
impl Gateway {
    pub fn new() -> Self {
        Self {
            asr: None,
            tts: None,
        }
    }
    pub fn begin_asr(
        &mut self,
        b: Binding,
        a: Audio,
        phase: Phase,
        authority: &dyn Authority,
        store: &mut dyn BudgetStore,
        net: &mut dyn Transport,
    ) -> Result<(), &'static str> {
        let duration = ((a.0.len() as u64) * 1000 + 15999) / 16000;
        authority.check(&b, Purpose::Asr)?;
        let body = mimo::asr_request(&a)?;
        drop(a);
        self.begin(
            b,
            Purpose::Asr,
            body,
            duration,
            phase,
            authority,
            store,
            net,
        )
    }
    pub fn begin_tts(
        &mut self,
        b: Binding,
        phase: Phase,
        authority: &dyn Authority,
        store: &mut dyn BudgetStore,
        net: &mut dyn Transport,
    ) -> Result<(), &'static str> {
        authority.check(&b, Purpose::Tts)?;
        let text = authority.projection(&b)?;
        let units = text.chars().count() as u64;
        let body = mimo::tts_request(&text)?;
        self.begin(b, Purpose::Tts, body, units, phase, authority, store, net)
    }
    fn begin(
        &mut self,
        b: Binding,
        p: Purpose,
        body: RequestBody,
        units: u64,
        phase: Phase,
        auth: &dyn Authority,
        store: &mut dyn BudgetStore,
        net: &mut dyn Transport,
    ) -> Result<(), &'static str> {
        let slot = if p == Purpose::Asr {
            &mut self.asr
        } else {
            &mut self.tts
        };
        if slot.is_some() {
            return Err("voice_concurrency");
        }
        auth.check(&b, p)?;
        let (now, day) = auth.now();
        budget::reserve(
            store,
            Reservation {
                id: b.request_id.clone(),
                purpose: p,
                phase,
                at_ms: now,
                day,
                units,
            },
        )?;
        // Reservation survives any failure or cancellation from this point.
        auth.check(&b, p)?;
        net.start(&b.request_id, mimo::ENDPOINT, body)?;
        *slot = Some(Inflight {
            binding: b,
            purpose: p,
            parser: Sse::new(if p == Purpose::Asr {
                Mode::Asr
            } else {
                Mode::Tts
            }),
            started: now,
            last_data: now,
            headers: false,
            received_audio: false,
        });
        Ok(())
    }
    pub fn cancel(&mut self, p: Purpose, net: &mut dyn Transport) {
        let slot = if p == Purpose::Asr {
            &mut self.asr
        } else {
            &mut self.tts
        };
        if let Some(r) = slot.take() {
            net.cancel(&r.binding.request_id);
        }
    }
    pub fn cancel_all(&mut self, net: &mut dyn Transport) {
        self.cancel(Purpose::Asr, net);
        self.cancel(Purpose::Tts, net);
    }
    /// Called also by the host timer with Connecting, so silence cannot evade timeout.
    pub fn poll(
        &mut self,
        p: Purpose,
        id: &str,
        f: Frame,
        auth: &dyn Authority,
        net: &mut dyn Transport,
    ) -> Result<Outcome, &'static str> {
        let slot = if p == Purpose::Asr {
            &mut self.asr
        } else {
            &mut self.tts
        };
        let Some(r) = slot.as_mut() else {
            return Err("stale_response");
        };
        if r.binding.request_id != id {
            return Err("stale_response");
        }
        let result = (|| {
            auth.check(&r.binding, r.purpose)?;
            let (now, _) = auth.now();
            if now < r.started || now < r.last_data {
                return Err("clock_rollback");
            }
            if !r.headers && now - r.started >= mimo::CONNECT_TIMEOUT_MS {
                return Err("connect_timeout");
            }
            if p == Purpose::Asr && now - r.started >= mimo::ASR_TIMEOUT_MS {
                return Err("asr_timeout");
            }
            if p == Purpose::Tts
                && (now - r.started >= mimo::TTS_TOTAL_MS
                    || (!r.received_audio && now - r.started >= mimo::TTS_FIRST_IDLE_MS)
                    || (r.received_audio && now - r.last_data >= mimo::TTS_FIRST_IDLE_MS))
            {
                return Err("tts_timeout");
            }
            match f {
                Frame::Connecting => Ok(Outcome::Pending),
                Frame::Failure => Err("voice_network_failed"),
                Frame::Headers(code) => {
                    if r.headers {
                        return Err("duplicate_headers");
                    }
                    if code != 200 {
                        return Err(mimo::error_code(code));
                    }
                    r.headers = true;
                    Ok(Outcome::Pending)
                }
                Frame::Data(bytes) => {
                    if !r.headers {
                        return Err("missing_headers");
                    }
                    let parts = r.parser.push(&bytes)?;
                    if parts
                        .iter()
                        .any(|p| matches!(p,Part::Pcm(b) if !b.is_empty()))
                    {
                        r.received_audio = true;
                        r.last_data = now;
                    }
                    Ok(Outcome::Parts(parts))
                }
                Frame::Eof => {
                    if let Some(text) = r.parser.finish()? {
                        Ok(Outcome::Final(text.to_owned()))
                    } else {
                        Ok(Outcome::Complete)
                    }
                }
            }
        })();
        if result.is_err() {
            if let Some(r) = slot.take() {
                net.cancel(&r.binding.request_id);
            }
        } else if matches!(result, Ok(Outcome::Final(_) | Outcome::Complete)) {
            slot.take();
        }
        result
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    use std::cell::Cell;
    struct Auth {
        allowed: Cell<bool>,
        time: Cell<u64>,
    }
    impl Authority for Auth {
        fn check(&self, _: &Binding, _: Purpose) -> Result<(), &'static str> {
            if self.allowed.get() {
                Ok(())
            } else {
                Err("purpose_denied")
            }
        }
        fn projection(&self, _: &Binding) -> Result<String, &'static str> {
            Ok("合成的已核准回复".into())
        }
        fn now(&self) -> (u64, u64) {
            (self.time.get(), 1)
        }
    }
    #[derive(Default)]
    struct Store {
        l: budget::Ledger,
    }
    impl BudgetStore for Store {
        fn load(&self) -> Result<budget::Ledger, &'static str> {
            Ok(self.l.clone())
        }
        fn compare_save(&mut self, p: u64, n: budget::Ledger) -> Result<(), &'static str> {
            assert_eq!(p, self.l.revision);
            self.l = n;
            Ok(())
        }
    }
    #[derive(Default)]
    struct ContractTransportFake {
        starts: usize,
        cancels: usize,
        fail: bool,
    }
    impl Transport for ContractTransportFake {
        fn start(&mut self, _: &str, url: &str, _: RequestBody) -> Result<(), &'static str> {
            assert_eq!(url, mimo::ENDPOINT);
            self.starts += 1;
            if self.fail {
                Err("unknown_send")
            } else {
                Ok(())
            }
        }
        fn cancel(&mut self, _: &str) {
            self.cancels += 1;
        }
    }
    fn b() -> Binding {
        Binding {
            request_id: "r1".into(),
            session_id: "s1".into(),
            generation: 1,
            policy_revision: 1,
        }
    }
    #[test]
    fn zero_transport_calls_when_denied() {
        let a = Auth {
            allowed: Cell::new(false),
            time: Cell::new(0),
        };
        let mut g = Gateway::new();
        let mut s = Store::default();
        let mut n = ContractTransportFake::default();
        assert!(g
            .begin_asr(
                b(),
                Audio(vec![1; 1600]),
                Phase::BDevelopment,
                &a,
                &mut s,
                &mut n
            )
            .is_err());
        assert!(g
            .begin_tts(b(), Phase::BDevelopment, &a, &mut s, &mut n)
            .is_err());
        assert_eq!(n.starts, 0);
        assert!(s.l.reservations.is_empty());
    }
    #[test]
    fn timeout_revocation_and_late_result_no_retry() {
        let a = Auth {
            allowed: Cell::new(true),
            time: Cell::new(0),
        };
        let mut g = Gateway::new();
        let mut s = Store::default();
        let mut n = ContractTransportFake::default();
        g.begin_tts(b(), Phase::BDevelopment, &a, &mut s, &mut n)
            .unwrap();
        g.poll(Purpose::Tts, "r1", Frame::Headers(200), &a, &mut n)
            .unwrap();
        a.time.set(15001);
        assert!(g
            .poll(Purpose::Tts, "r1", Frame::Connecting, &a, &mut n)
            .is_err());
        assert!(g.poll(Purpose::Tts, "r1", Frame::Eof, &a, &mut n).is_err());
        assert_eq!(n.starts, 1);
        assert_eq!(n.cancels, 1);
        assert_eq!(s.l.reservations.len(), 1);
    }
    #[test]
    fn parallel_asr_tts_but_not_two_of_each() {
        let a = Auth {
            allowed: Cell::new(true),
            time: Cell::new(0),
        };
        let mut g = Gateway::new();
        let mut s = Store::default();
        let mut n = ContractTransportFake::default();
        g.begin_asr(
            b(),
            Audio(vec![1; 1600]),
            Phase::BDevelopment,
            &a,
            &mut s,
            &mut n,
        )
        .unwrap();
        let mut t = b();
        t.request_id = "tts1".into();
        g.begin_tts(t.clone(), Phase::BDevelopment, &a, &mut s, &mut n)
            .unwrap();
        t.request_id = "tts2".into();
        assert!(g
            .begin_tts(t, Phase::BDevelopment, &a, &mut s, &mut n)
            .is_err());
        a.allowed.set(false);
        assert!(g
            .poll(Purpose::Asr, "r1", Frame::Headers(200), &a, &mut n)
            .is_err());
        g.cancel_all(&mut n);
        assert_eq!(n.cancels, 2);
        assert_eq!(n.starts, 2);
    }
    #[test]
    fn provider_errors_consume_reserved_budget() {
        for code in [401, 429, 302, 500] {
            let a = Auth {
                allowed: Cell::new(true),
                time: Cell::new(0),
            };
            let mut g = Gateway::new();
            let mut s = Store::default();
            let mut n = ContractTransportFake::default();
            g.begin_tts(b(), Phase::BDevelopment, &a, &mut s, &mut n)
                .unwrap();
            assert!(g
                .poll(Purpose::Tts, "r1", Frame::Headers(code), &a, &mut n)
                .is_err());
            assert_eq!(s.l.reservations.len(), 1);
            assert_eq!(n.starts, 1);
        }
    }
}
