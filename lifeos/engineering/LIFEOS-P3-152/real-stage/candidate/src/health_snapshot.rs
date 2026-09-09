//! S1: batch-level synthetic window observations, never fabricated sample identity.
use crate::{
    health_domain as domain,
    health_ingestion::{put, rows},
    repository::Error,
};
use rusqlite::{Connection, TransactionBehavior};
use serde::{Deserialize, Serialize};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
type R<T> = Result<T, Error>;
#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Source {
    key: String,
    name: String,
    identity_strategy: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Query {
    key: String,
    interval_rule: String,
    sleep_category: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Sample {
    start_ms: i64,
    end_ms: i64,
    value: f64,
    unit: String,
}
#[derive(Clone, Serialize, Deserialize)]
#[serde(rename_all = "camelCase", deny_unknown_fields)]
struct Snapshot {
    schema: String,
    batch_id: String,
    captured_at_ms: i64,
    window_start_ms: i64,
    window_end_ms: i64,
    timezone_offset_minutes: i32,
    metric: String,
    source: Source,
    query: Query,
    completeness: String,
    pagination: String,
    completeness_evidence: String,
    samples: Vec<Sample>,
}
fn fail(s: &str) -> Error {
    Error::new(s)
}
fn key(s: &str) -> bool {
    !s.is_empty()
        && s.len() <= 80
        && s.bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"_-".contains(&b))
}
fn hash(v: &Value) -> String {
    format!("{:x}", Sha256::digest(v.to_string().as_bytes()))
}
fn parse(bytes: &[u8]) -> R<Snapshot> {
    if bytes.len() > domain::LIMIT {
        return Err(fail("health_batch_limit"));
    }
    let v = crate::strict_json::parse(
        std::str::from_utf8(bytes).map_err(|_| fail("health_snapshot_rejected"))?,
    )?;
    let mut s: Snapshot =
        serde_json::from_value(v).map_err(|_| fail("health_snapshot_rejected"))?;
    if s.schema != "health-window-snapshot-v1"
        || !key(&s.source.key)
        || !key(&s.query.key)
        || s.source.identity_strategy != "configured-name-group"
        || s.query.interval_rule != "fully-contained"
        || s.query.sleep_category
            != if s.metric == "sleep" {
                "explicit-asleep"
            } else {
                "not-applicable"
            }
        || !["complete", "partial", "unknown"].contains(&s.completeness.as_str())
        || !["complete", "incomplete", "unknown"].contains(&s.pagination.as_str())
        || s.completeness_evidence != "synthetic-fixture"
    {
        return Err(fail("health_snapshot_rejected"));
    }
    // Reuse validated units/time/budget only. Transient indices do not enter storage/provenance.
    let validation = json!({"schema":"health-envelope-v1","batchId":s.batch_id,"exportedAtMs":s.captured_at_ms,"windowStartMs":s.window_start_ms,"windowEndMs":s.window_end_ms,"timezoneOffsetMinutes":s.timezone_offset_minutes,"source":{"id":s.source.key,"name":s.source.name},"samples":s.samples.iter().enumerate().map(|(i,x)|json!({"sampleId":format!("validation-{i}"),"revision":1,"metric":s.metric,"startMs":x.start_ms,"endMs":x.end_ms,"value":x.value,"unit":x.unit})).collect::<Vec<_>>()});
    domain::parse(&serde_json::to_vec(&validation).unwrap())?;
    s.samples.sort_by(|a, b| {
        a.start_ms
            .cmp(&b.start_ms)
            .then(a.end_ms.cmp(&b.end_ms))
            .then(a.value.total_cmp(&b.value))
            .then(a.unit.cmp(&b.unit))
    });
    Ok(s)
}
fn overlaps(a: i64, b: i64, c: i64, d: i64) -> bool {
    a < d && c < b
}
pub fn reject_v1_mixing(c: &Connection, keys: &std::collections::BTreeSet<domain::Key>) -> R<()> {
    for state in rows(c, "states", "health_current_state")? {
        if state["protocol"] == "snapshot-v1" {
            for k in keys {
                let start = k.day * domain::DAY - k.offset as i64 * 60000;
                if state["metric"] == k.metric
                    && overlaps(
                        start,
                        start + domain::DAY,
                        state["windowStartMs"].as_i64().unwrap(),
                        state["windowEndMs"].as_i64().unwrap(),
                    )
                {
                    return Err(fail("health_protocol_overlap"));
                }
            }
        }
    }
    Ok(())
}
fn projection(
    s: &Snapshot,
    scope: &str,
    batch: &str,
    generation: u64,
    received: i64,
    prior: &Value,
) -> Value {
    let mut end = i64::MIN;
    let mut union = 0;
    let mut overlap = false;
    for x in &s.samples {
        overlap |= x.start_ms < end;
        union += x.end_ms - x.start_ms.max(end).min(x.end_ms);
        end = end.max(x.end_ms);
    }
    let value = if s.metric == "sleep" {
        json!(union as f64 / 60000.0)
    } else if overlap {
        Value::Null
    } else {
        json!(s.samples.iter().map(|x| x.value).sum::<f64>())
    };
    json!({"id":format!("health-window:{scope}"),"kind":"health_current_state","status":"observed","domain":"Health","modelEligible":false,"protocol":"snapshot-v1","scope":scope,"sourceId":format!("health-source:{}",s.source.key),"dayIndex":(s.window_end_ms-1+s.timezone_offset_minutes as i64*60000).div_euclid(domain::DAY),"offsetMinutes":s.timezone_offset_minutes,"metric":s.metric,"unit":if s.metric=="steps"{"count"}else{"minutes"},"value":value,"estimated":false,"method":if s.metric=="sleep"{"sleep_interval_union"}else if overlap{"overlap_uncertain"}else{"window_nonoverlapping_samples"},"sources":[{"sourceId":s.source.key,"name":s.source.name,"identityStrategy":s.source.identity_strategy,"value":value,"uncertain":overlap&&s.metric!="sleep"}],"refs":[{"id":batch,"sourceId":s.source.key,"version":generation,"snapshot":true}],"windowStartMs":s.window_start_ms,"windowEndMs":s.window_end_ms,"query":s.query,"completeness":"synthetic_complete_only","observedAt":end,"capturedAt":s.captured_at_ms,"receivedAt":received,"generation":generation,"supersedesBatch":prior})
}
pub fn receive(c: &mut Connection, bytes: &[u8], received: i64) -> R<Value> {
    if crate::runtime_root::is_real() {
        return Err(fail("health_synthetic_only"));
    }
    let s = parse(bytes)?;
    let envelope = serde_json::to_value(&s).unwrap();
    let batch_hash = hash(&envelope);
    let scope = hash(
        &json!({"source":s.source,"metric":s.metric,"start":s.window_start_ms,"end":s.window_end_ms,"offset":s.timezone_offset_minutes,"query":s.query}),
    );
    let mut content = envelope.clone();
    content.as_object_mut().unwrap().remove("batchId");
    content.as_object_mut().unwrap().remove("capturedAtMs");
    let content_hash = hash(&content);
    let batch_id = format!("health-snapshot:{}:{}", s.source.key, s.batch_id);
    let tx = c.transaction_with_behavior(TransactionBehavior::Immediate)?;
    if rows(&tx,"states","health_current_state")?.iter().any(|s|s["protocol"]=="apple-file-v1"){return Err(fail("health_protocol_overlap"));}
    let history = rows(&tx, "records", "health_batch")?;
    if let Some(old) = history.iter().find(|b| b["id"] == batch_id) {
        return if old["batchHash"] == batch_hash {
            Ok(json!({"state":"duplicate","changed":0}))
        } else {
            Err(fail("health_batch_conflict"))
        };
    }
    for source in rows(&tx, "sources", "health_source")? {
        if source["id"] == format!("health-source:{}", s.source.key)
            && (source["name"] != s.source.name
                || source["identityStrategy"] != s.source.identity_strategy)
        {
            return Err(fail("health_source_policy_conflict"));
        }
    }
    let prior = history
        .iter()
        .filter(|b| b["scope"] == scope && b["accepted"] == true)
        .max_by_key(|b| b["capturedAt"].as_i64().unwrap_or(0));
    let mut disposition = if s.completeness != "complete" || s.pagination != "complete" {
        "waiting_incomplete"
    } else if s.samples.is_empty() {
        "waiting_empty"
    } else {
        "accepted"
    };
    let mut generation = prior.and_then(|p| p["generation"].as_u64()).unwrap_or(0);
    let mut supersedes = prior
        .map(|p| p["projectionBatch"].clone())
        .unwrap_or(Value::Null);
    if disposition == "accepted" {
        if history.iter().any(|p| {
            p["scope"] == scope
                && p["accepted"] == true
                && p["capturedAt"] == s.captured_at_ms
                && p["contentHash"] != content_hash
        }) {
            return Err(fail("health_snapshot_time_conflict"));
        }
        if let Some(p) = prior {
            let time = p["capturedAt"].as_i64().unwrap();
            if s.captured_at_ms == time && p["contentHash"] != content_hash {
                return Err(fail("health_snapshot_time_conflict"));
            }
            if s.captured_at_ms < time {
                disposition = "ignored_older";
            } else if p["contentHash"] == content_hash {
                disposition = "unchanged";
            }
        }
        if disposition == "accepted" || disposition == "unchanged" {
            for state in rows(&tx, "states", "health_current_state")? {
                if state["metric"] != s.metric {
                    continue;
                }
                if state["protocol"] == "snapshot-v1" {
                    if state["scope"] != scope
                        && overlaps(
                            s.window_start_ms,
                            s.window_end_ms,
                            state["windowStartMs"].as_i64().unwrap(),
                            state["windowEndMs"].as_i64().unwrap(),
                        )
                    {
                        return Err(fail("health_snapshot_overlap"));
                    }
                } else {
                    let start = state["dayIndex"].as_i64().unwrap() * domain::DAY
                        - state["offsetMinutes"].as_i64().unwrap() * 60000;
                    if overlaps(
                        start,
                        start + domain::DAY,
                        s.window_start_ms,
                        s.window_end_ms,
                    ) {
                        return Err(fail("health_protocol_overlap"));
                    }
                }
            }
        }
        if disposition == "accepted" {
            generation += 1;
            put(
                &tx,
                "states",
                &projection(&s, &scope, &batch_id, generation, received, &supersedes),
            )?;
            supersedes = json!(batch_id);
        }
    }
    put(
        &tx,
        "records",
        &json!({"id":batch_id,"kind":"health_batch","protocol":"snapshot-v1","status":"observed","modelEligible":false,"scope":scope,"sourceId":format!("health-source:{}",s.source.key),"batchHash":batch_hash,"contentHash":content_hash,"capturedAt":s.captured_at_ms,"receivedAt":received,"disposition":disposition,"accepted":disposition=="accepted"||disposition=="unchanged","generation":generation,"projectionBatch":supersedes,"envelope":envelope}),
    )?;
    put(
        &tx,
        "sources",
        &json!({"id":format!("health-source:{}",s.source.key),"kind":"health_source","name":s.source.name,"externalSourceId":s.source.key,"identityStrategy":s.source.identity_strategy,"authorized":false,"ingestAuthorized":true,"modelEligible":false,"generation":1,"receivedAt":received,"snapshotStatus":disposition,"protocol":"snapshot-v1"}),
    )?;
    tx.execute("UPDATE meta SET revision=revision+1 WHERE id=1", [])?;
    tx.commit()?;
    Ok(
        json!({"state":disposition,"changed":if disposition=="accepted"{1}else{0},"generation":generation}),
    )
}
#[cfg(test)]
mod tests;
