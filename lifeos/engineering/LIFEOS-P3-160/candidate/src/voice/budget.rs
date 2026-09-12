use serde::{Deserialize, Serialize};
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Purpose {
    Asr,
    Tts,
    SessionTurn,
}
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)]
pub enum Phase {
    BDevelopment,
    BUnseen,
    C,
}
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Reservation {
    pub id: String,
    pub purpose: Purpose,
    pub phase: Phase,
    pub at_ms: u64,
    pub day: u64,
    pub units: u64,
}
#[derive(Clone, Default, Debug, Serialize, Deserialize)]
pub struct Ledger {
    pub revision: u64,
    pub high_water_ms: u64,
    pub high_water_day: u64,
    pub reservations: Vec<Reservation>,
}
/// Implement within the EXISTING Store transaction; never a second voice database.
/// Read failure, missing/corrupt existing ledger, and CAS failure deny sending.
pub trait BudgetStore {
    fn load(&self) -> Result<Ledger, &'static str>;
    fn compare_save(&mut self, previous: u64, next: Ledger) -> Result<(), &'static str>;
}
pub fn reserve(store: &mut dyn BudgetStore, r: Reservation) -> Result<(), &'static str> {
    let mut l = store.load()?;
    if r.id.is_empty() || l.reservations.iter().any(|x| x.id == r.id) {
        return Err("reservation_reused");
    }
    if r.at_ms < l.high_water_ms || r.day < l.high_water_day {
        return Err("clock_rollback");
    }
    // Host supplies local day from trusted clock, not an IPC caller.
    if l.high_water_day != 0 && r.day > l.high_water_day && r.at_ms <= l.high_water_ms {
        return Err("day_untrusted");
    }
    let all: Vec<_> = l
        .reservations
        .iter()
        .filter(|x| x.purpose == r.purpose)
        .collect();
    let same: Vec<_> = all.iter().filter(|x| x.phase == r.phase).collect();
    let segment_max = match r.purpose {
        Purpose::Asr => 60000,
        Purpose::Tts => 4000,
        Purpose::SessionTurn => 1,
    };
    if r.units == 0 || r.units > segment_max {
        return Err("request_units");
    }
    match r.phase {
        Phase::BDevelopment | Phase::BUnseen => {
            let cap = if r.phase == Phase::BDevelopment {
                32
            } else {
                16
            };
            if same.len() >= cap {
                return Err("b_post_budget");
            }
            let b: Vec<_> = all.iter().filter(|x| x.phase != Phase::C).collect();
            let sum: u64 = b.iter().map(|x| x.units).sum();
            let cap = match r.purpose {
                Purpose::Asr => 1200000,
                Purpose::Tts => 24000,
                Purpose::SessionTurn => 48,
            };
            if b.len() >= 48 || sum + r.units > cap {
                return Err("b_total_budget");
            }
        }
        Phase::C => {
            let day: Vec<_> = same.iter().filter(|x| x.day == r.day).collect();
            let cap = if r.purpose == Purpose::SessionTurn {
                60
            } else {
                300
            };
            if day.len() >= cap {
                return Err("daily_post_budget");
            }
            if r.purpose != Purpose::SessionTurn
                && same
                    .iter()
                    .filter(|x| r.at_ms.saturating_sub(x.at_ms) < 60000)
                    .count()
                    >= 10
            {
                return Err("minute_budget");
            }
            if r.purpose == Purpose::Asr
                && day.iter().map(|x| x.units).sum::<u64>() + r.units > 3600000
            {
                return Err("daily_audio_budget");
            }
        }
    }
    let rev = l.revision;
    l.revision += 1;
    l.high_water_ms = r.at_ms;
    l.high_water_day = r.day;
    l.reservations.push(r);
    store.compare_save(rev, l)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[derive(Default)]
    struct Store {
        l: Ledger,
        fail: bool,
    }
    impl BudgetStore for Store {
        fn load(&self) -> Result<Ledger, &'static str> {
            Ok(self.l.clone())
        }
        fn compare_save(&mut self, p: u64, n: Ledger) -> Result<(), &'static str> {
            if self.fail || p != self.l.revision {
                Err("storage_failed")
            } else {
                self.l = n;
                Ok(())
            }
        }
    }
    fn r(i: u64) -> Reservation {
        Reservation {
            id: i.to_string(),
            purpose: Purpose::Asr,
            phase: Phase::BDevelopment,
            at_ms: i * 1000,
            day: 1,
            units: 1000,
        }
    }
    #[test]
    fn failed_unknown_never_refunded_across_restart() {
        let mut s = Store::default();
        for i in 1..=32 {
            reserve(&mut s, r(i)).unwrap();
        }
        let persisted = serde_json::to_string(&s.l).unwrap();
        let mut reopened = Store {
            l: serde_json::from_str(&persisted).unwrap(),
            fail: false,
        };
        assert_eq!(reserve(&mut reopened, r(33)), Err("b_post_budget"));
        assert_eq!(reserve(&mut reopened, r(1)), Err("reservation_reused"));
    }
    #[test]
    fn clock_and_storage_fail_closed() {
        let mut s = Store::default();
        reserve(&mut s, r(20)).unwrap();
        assert_eq!(reserve(&mut s, r(19)), Err("clock_rollback"));
        s.fail = true;
        assert_eq!(reserve(&mut s, r(21)), Err("storage_failed"));
        assert_eq!(s.l.reservations.len(), 1);
    }
    #[test]
    fn purpose_and_unseen_are_separate() {
        let mut s = Store::default();
        for i in 1..=32 {
            reserve(&mut s, r(i)).unwrap();
        }
        let mut x = r(33);
        x.phase = Phase::BUnseen;
        reserve(&mut s, x).unwrap();
        let mut x = r(34);
        x.purpose = Purpose::Tts;
        reserve(&mut s, x).unwrap();
    }
    #[test]
    fn rolling_minute_and_day() {
        let mut s = Store::default();
        for i in 1..=10 {
            let mut x = r(i);
            x.phase = Phase::C;
            reserve(&mut s, x).unwrap();
        }
        let mut x = r(11);
        x.phase = Phase::C;
        assert_eq!(reserve(&mut s, x), Err("minute_budget"));
        let mut x = r(71);
        x.phase = Phase::C;
        reserve(&mut s, x).unwrap();
    }
}
