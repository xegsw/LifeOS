//! Durable host-stage journal. No transaction spans human or credential waiting.
use super::*;
pub(super) struct HostStage {
    id: String,
    turn_id: String,
    key: String,
    started: Instant,
    used: u64,
    reserved: u64,
}
#[cfg(test)]
impl HostStage {
    pub(super) fn simulate_elapsed(&mut self, ms: u64) {
        self.started = Instant::now() - std::time::Duration::from_millis(ms);
    }
}
fn key(turn_id: &str) -> String {
    format!("coord8:activity:{}", fp(&json!(turn_id)))
}
impl Store {
    fn v8_activity_turn(c: &Connection, turn_id: &str) -> R<Option<Value>> {
        let link = get(c, "sources", &format!("coord8:turn-link:{turn_id}"))?;
        match link {
            Some(v) => get(
                c,
                "packets",
                &turn_key(
                    v["turnRequestId"]
                        .as_str()
                        .ok_or_else(|| error("store_contract_rejected"))?,
                ),
            ),
            None => Ok(None),
        }
    }
    pub(super) fn v8_begin_host(&self, turn_id: &str) -> R<HostStage> {
        id(turn_id)?;
        if !self.c.is_autocommit() {
            return Err(error("store_operation_failed"));
        }
        let journal_key = key(turn_id);
        let prior = get(&self.c, "packets", &journal_key)?;
        if prior.as_ref().is_some_and(|v| v["state"] == "active") {
            return Err(error("turn_in_flight"));
        }
        let live = Self::v8_activity_turn(&self.c, turn_id)?;
        let used = prior
            .as_ref()
            .and_then(|v| v["usedMs"].as_u64())
            .unwrap_or(0)
            .max(
                live.as_ref()
                    .and_then(|t| t["activityBudget"]["usedMs"].as_u64())
                    .unwrap_or(0),
            );
        if live
            .as_ref()
            .is_some_and(|t| t["activityBudget"]["reservedMs"].as_u64().unwrap_or(0) > 0)
        {
            return Err(error("turn_in_flight"));
        }
        if used >= 180000 {
            return Err(error("activity_budget_exceeded"));
        }
        let stage = HostStage {
            id: uid("host-stage"),
            turn_id: turn_id.into(),
            key: journal_key,
            started: Instant::now(),
            used,
            reserved: 180000 - used,
        };
        put(
            &self.c,
            "packets",
            &stage.key,
            &json!({"kind":"coord8_host_activity","schemaVersion":8,"id":stage.id,"turnId":turn_id,"state":"active","activeStage":"host","usedMs":used,"reservedMs":stage.reserved,"startedAt":now()}),
        )?;
        Ok(stage)
    }
    pub(super) fn v8_initial_activity(stage: &HostStage) -> Value {
        json!({"limitMs":180000,"usedMs":stage.used,"reservedMs":0,"activeStage":"none"})
    }
    pub(super) fn v8_end_host(&self, stage: &HostStage, t: &mut Value) -> R<()> {
        let mut journal =
            get(&self.c, "packets", &stage.key)?.ok_or_else(|| error("store_contract_rejected"))?;
        if journal["id"] != stage.id || journal["state"] != "active" {
            return Err(error("revision_conflict"));
        }
        let elapsed = (stage.started.elapsed().as_millis() as u64).max(1);
        let used = stage
            .used
            .max(t["activityBudget"]["usedMs"].as_u64().unwrap_or(0));
        let reserved = t["activityBudget"]["reservedMs"].as_u64().unwrap_or(0);
        if elapsed > stage.reserved
            || used.saturating_add(elapsed).saturating_add(reserved) > 180000
        {
            return Err(error("activity_budget_exceeded"));
        }
        t["activityBudget"]["usedMs"] = json!(used + elapsed);
        journal["state"] = json!("settled");
        journal["activeStage"] = json!("none");
        journal["usedMs"] = json!(used + elapsed);
        journal["reservedMs"] = json!(0);
        journal["finishedAt"] = json!(now());
        put(&self.c, "packets", &stage.key, &journal)
    }
    pub(super) fn v8_close_host(&self, stage: &HostStage) -> R<()> {
        let journal =
            get(&self.c, "packets", &stage.key)?.ok_or_else(|| error("store_contract_rejected"))?;
        if journal["state"] != "active" {
            return Ok(());
        }
        let outcome=self.tx(&uid("host-close"),"coord8_host_close",&json!({"stageId":stage.id}),|c|{
            let live=Self::v8_activity_turn(c,&stage.turn_id)?;
            let mut t=live.clone().unwrap_or(json!({"activityBudget":Self::v8_initial_activity(stage)}));
            if let Err(e)=self.v8_end_host(stage,&mut t){
                if e.code!="activity_budget_exceeded"{return Err(e);}
                let mut exhausted=journal.clone();exhausted["state"]=json!("exhausted");exhausted["usedMs"]=json!(180000);exhausted["reservedMs"]=json!(0);exhausted["activeStage"]=json!("none");put(c,"packets",&stage.key,&exhausted)?;
                t["activityBudget"]=json!({"limitMs":180000,"usedMs":180000,"reservedMs":0,"activeStage":"none"});
                if live.is_some()&&t["state"]!="committed"{Self::v8_change(&mut t,"failed");t["errorCode"]=json!("activity_budget_exceeded");}
            }
            if live.is_some(){self.v8_put(&t)?;}
            Ok(json!({"settled":true,"exhausted":t["activityBudget"]["usedMs"].as_u64().unwrap()>=180000}))
        })?;
        if outcome["exhausted"] == true {
            return Err(error("activity_budget_exceeded"));
        }
        Ok(())
    }
    pub(super) fn v8_host_run<T>(
        &self,
        turn_id: &str,
        body: impl FnOnce(&HostStage) -> R<T>,
    ) -> R<T> {
        let stage = self.v8_begin_host(turn_id)?;
        let result = body(&stage);
        self.v8_close_host(&stage)?;
        result
    }
    pub(super) fn v8_recover_host(c: &Connection) -> R<()> {
        let mut s = c.prepare(
            "SELECT id,body FROM packets WHERE json_extract(body,'$.kind')='coord8_host_activity'",
        )?;
        let rows = s
            .query_map([], |r| Ok((r.get::<_, String>(0)?, r.get::<_, String>(1)?)))?
            .collect::<Result<Vec<_>, _>>()?;
        drop(s);
        for (key, raw) in rows {
            let mut journal: Value =
                serde_json::from_str(&raw).map_err(|_| error("store_contract_rejected"))?;
            let tid = journal["turnId"]
                .as_str()
                .ok_or_else(|| error("store_contract_rejected"))?
                .to_string();
            let active = journal["state"] == "active";
            let used = journal["usedMs"].as_u64().unwrap_or(180000);
            let reserved = if active {
                journal["reservedMs"].as_u64().unwrap_or(180000)
            } else {
                0
            };
            let total = used.saturating_add(reserved).min(180000);
            if active {
                journal["state"] = json!("recovered");
                journal["usedMs"] = json!(total);
                journal["reservedMs"] = json!(0);
                journal["activeStage"] = json!("none");
                put(c, "packets", &key, &journal)?;
            }
            if let Some(mut t) = Self::v8_activity_turn(c, &tid)? {
                let prior = t["activityBudget"]["usedMs"].as_u64().unwrap_or(0);
                t["activityBudget"]["usedMs"] = json!(prior.max(total));
                if active {
                    t["activityBudget"]["reservedMs"] = json!(0);
                    t["activityBudget"]["activeStage"] = json!("none");
                    if t["state"] != "committed" {
                        Self::v8_change(&mut t, "failed");
                        t["errorCode"] = json!("activity_budget_exceeded");
                    }
                }
                put(
                    c,
                    "packets",
                    &turn_key(t["turnRequestId"].as_str().unwrap()),
                    &t,
                )?;
            }
        }
        Ok(())
    }
}
