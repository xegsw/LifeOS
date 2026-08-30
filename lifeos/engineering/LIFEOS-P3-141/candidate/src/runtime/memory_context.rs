//! P3-139 local-only Durable Memory, Current State and Context Resolver.
//!
//! This module intentionally has no Provider, ModelPort, socket, filesystem
//! selection or generic-path surface.  It receives only fixed synthetic DTOs,
//! stores local authority separately, and records non-content disclosures.

use super::{now, read, write, Error, Paths};
use rusqlite::{params, Connection, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};

const RESOLVER_VERSION: &str = "p3-139-context-resolver-v1";
const SOURCE_REF: &str = "source:synthetic:memory-fixture";
const AUTH_PERSON: &str = "AUTH-SYN-PERSON-GRANTED";
const AUTH_CROSS: &str = "AUTH-SYN-CROSS-GRANTED";

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum MemoryOperation { Create, Confirm, Correct, Supersede, Expire, DeleteTombstone }

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum StateOperation { Set, Correct, Expire, Clear }

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum Domain { Person, Work, Health }
impl Domain { fn value(self) -> &'static str { match self { Self::Person => "person", Self::Work => "work", Self::Health => "health" } } }

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum TaskType { Work, Health, CrossDomain }
impl TaskType { fn value(self) -> &'static str { match self { Self::Work => "work", Self::Health => "health", Self::CrossDomain => "cross_domain" } } }

/// A deliberately small, non-diagnostic Health/Fitness state.  It contains
/// no free-text field and represents only the five frozen P3-141 signals.
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum SleepDurationRange { UnderFiveHours, FiveToSevenHours, SevenToNineHours, OverNineHours }
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum TrainingLoad { Low, Medium, High }
#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum AvailableTime { UnderThirtyMinutes, ThirtyToSixtyMinutes, SixtyToOneHundredTwentyMinutes, OverOneHundredTwentyMinutes }
#[derive(Clone, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(deny_unknown_fields)]
pub(crate) struct StructuredHealthState {
    pub sleep_duration_range: SleepDurationRange,
    pub energy: u8,
    pub soreness_or_pain: bool,
    pub training_load: TrainingLoad,
    pub available_time: AvailableTime,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct DurableMemoryRequest {
    pub operation: MemoryOperation,
    pub memory_id: String,
    pub replacement_id: Option<String>,
    pub statement: Option<String>,
    pub memory_type: Option<String>,
    pub source_refs: Option<Vec<String>>,
    pub observed_at_ms: Option<i64>,
    pub domain: Domain,
    pub scope: String,
    pub expected_generation: Option<i64>,
    pub idempotency_key: String,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct CurrentStateRequest {
    pub operation: StateOperation,
    pub state_id: String,
    pub replacement_id: Option<String>,
    pub state_key: Option<String>,
    pub value: Option<String>,
    pub domain: Domain,
    pub source_refs: Option<Vec<String>>,
    pub expires_at_ms: Option<i64>,
    pub expected_generation: Option<i64>,
    pub idempotency_key: String,
    pub structured_health: Option<StructuredHealthState>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct ResolveRequest {
    pub request_id: String,
    pub task_type: TaskType,
    pub query_text: String,
    pub authorization_id: String,
    pub health_necessary: bool,
    pub removed_domains: Option<Vec<Domain>>,
    pub top_k: Option<usize>,
    pub token_budget: Option<usize>,
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct ReceiptRequest { pub request_id: String }

#[derive(Debug, Serialize)]
pub(crate) struct MemoryMutationResponse {
    pub status: &'static str,
    pub memory_id: String,
    pub operation: MemoryOperation,
    pub validity: String,
    pub generation: i64,
    pub audit_ref: String,
}

#[derive(Debug, Serialize)]
pub(crate) struct StateMutationResponse {
    pub status: &'static str,
    pub state_id: String,
    pub operation: StateOperation,
    pub validity: String,
    pub generation: i64,
    pub invalidated_slice: String,
    pub audit_ref: String,
}

#[derive(Debug, Serialize)]
pub(crate) struct DisclosureItem { pub layer: String, pub reference: String, pub reason: String }

#[derive(Debug, Serialize)]
pub(crate) struct ResolvedContext {
    pub status: &'static str,
    pub request_id: String,
    pub resolver_version: &'static str,
    pub authorization_id: String,
    pub task_type: String,
    pub included: Vec<DisclosureItem>,
    pub excluded: Vec<DisclosureItem>,
    pub top_k: usize,
    pub token_budget: usize,
    pub used_token_estimate: usize,
    pub l2_scanned_rows: usize,
    pub l2_recomputed_slices: Vec<String>,
    pub receipt_ref: String,
    pub model_dispatch_count: u8,
}

#[derive(Debug, Serialize)]
pub(crate) struct DisclosureReceipt {
    pub status: &'static str,
    pub request_id: String,
    pub resolver_version: String,
    pub authorization_id: String,
    pub top_k: usize,
    pub token_budget: usize,
    pub used_token_estimate: usize,
    pub included: Vec<DisclosureItem>,
    pub excluded: Vec<DisclosureItem>,
    pub model_dispatch_count: u8,
}

fn blocked(code: &'static str, message: &'static str) -> Error { Error::blocked(code, message) }
fn valid_id(value: &str, prefix: &str) -> bool { value.starts_with(prefix) && value.len() <= 120 && value.bytes().all(|b| b.is_ascii_alphanumeric() || matches!(b, b':' | b'-' | b'_')) }
fn valid_memory_statement(value: &str) -> bool { matches!(value,
    "Synthetic Person: prefers concise daily planning." |
    "Synthetic Work: weekday focus block supports review planning." |
    "Synthetic Health: low-impact recovery only when explicitly authorized." |
    "Synthetic Work: corrected planning preference is a 25-minute focus block." |
    "Synthetic Candidate: unconfirmed preference.") }
fn valid_state_value(value: &str) -> bool { matches!(value,
    "synthetic_work_load_high" |
    "synthetic_fatigue_moderate" |
    "synthetic_sleep_short" |
    "synthetic_health_clear" |
    "synthetic_fatigue_low") }
fn valid_memory_type(value: &str) -> bool { matches!(value, "identity" | "preference" | "constraint" | "decision") }
fn valid_state_key(value: &str) -> bool { matches!(value, "work_load" | "fatigue" | "sleep" | "health_gate") }
fn valid_query(value: &str) -> bool { matches!(value, "planning" | "focus" | "recovery") }
fn mode_prefix(paths: &Paths, kind: &str) -> String {
    if paths.mode == super::InputMode::Real { format!("{kind}:p3-141:real:") } else { format!("{kind}:synthetic:") }
}
fn valid_mode_id(paths: &Paths, value: &str, kind: &str) -> bool { valid_id(value, &mode_prefix(paths, kind)) }
fn source_refs(paths: &Paths, value: &Option<Vec<String>>) -> Result<(), Error> {
    let expected = if paths.mode == super::InputMode::Real {
        if super::controlled_fixture_evidence(paths) { "source:synthetic:controlled-fixture" } else { "source:local:user-confirmed" }
    } else { SOURCE_REF };
    if value.as_deref() == Some(&[expected.to_string()]) { Ok(()) } else { Err(blocked("source_refs_rejected", "Memory 与 State 只能引用当前模式的最小来源引用。")) }
}
fn ensure_schema(conn: &Connection) -> Result<(), Error> {
    conn.execute_batch(r#"
        CREATE TABLE IF NOT EXISTS durable_memories(
          memory_id TEXT PRIMARY KEY, statement TEXT NOT NULL, memory_type TEXT NOT NULL,
          source_refs_json TEXT NOT NULL, recorded_at_ms INTEGER NOT NULL, observed_at_ms INTEGER NOT NULL,
          confirmation TEXT NOT NULL CHECK(confirmation IN ('candidate','confirmed')),
          validity TEXT NOT NULL CHECK(validity IN ('candidate','active','expired','superseded','tombstoned')),
          scope TEXT NOT NULL, domain TEXT NOT NULL, supersedes TEXT, superseded_by TEXT,
          generation INTEGER NOT NULL, expires_at_ms INTEGER, tombstoned INTEGER NOT NULL DEFAULT 0
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS durable_memory_fts USING fts5(memory_id UNINDEXED, statement);
        CREATE TABLE IF NOT EXISTS current_state_events(
          state_id TEXT PRIMARY KEY, state_key TEXT NOT NULL, value_summary TEXT NOT NULL,
          domain TEXT NOT NULL, source_refs_json TEXT NOT NULL, recorded_at_ms INTEGER NOT NULL,
          expires_at_ms INTEGER NOT NULL, validity TEXT NOT NULL CHECK(validity IN ('active','corrected','expired','cleared')),
          generation INTEGER NOT NULL, corrects TEXT
        );
        CREATE INDEX IF NOT EXISTS current_state_active_idx ON current_state_events(state_key, validity, expires_at_ms, generation);
        CREATE TABLE IF NOT EXISTS structured_health_states(
          state_id TEXT PRIMARY KEY, sleep_duration_range TEXT NOT NULL CHECK(sleep_duration_range IN ('under_five_hours','five_to_seven_hours','seven_to_nine_hours','over_nine_hours')),
          energy INTEGER NOT NULL CHECK(energy BETWEEN 1 AND 5), soreness_or_pain INTEGER NOT NULL CHECK(soreness_or_pain IN (0,1)),
          training_load TEXT NOT NULL CHECK(training_load IN ('low','medium','high')),
          available_time TEXT NOT NULL CHECK(available_time IN ('under_thirty_minutes','thirty_to_sixty_minutes','sixty_to_one_hundred_twenty_minutes','over_one_hundred_twenty_minutes')),
          recorded_at_ms INTEGER NOT NULL, expires_at_ms INTEGER NOT NULL,
          validity TEXT NOT NULL CHECK(validity IN ('active','corrected','expired','cleared')), generation INTEGER NOT NULL, corrects TEXT
        );
        CREATE INDEX IF NOT EXISTS structured_health_active_idx ON structured_health_states(validity, expires_at_ms, generation);
        CREATE TABLE IF NOT EXISTS snapshot_slices(slice_name TEXT PRIMARY KEY, state_generation INTEGER NOT NULL, snapshot_generation INTEGER NOT NULL, updated_at_ms INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS context_requests(
          request_id TEXT PRIMARY KEY, task_type TEXT NOT NULL, authorization_id TEXT NOT NULL,
          resolver_version TEXT NOT NULL, top_k INTEGER NOT NULL, token_budget INTEGER NOT NULL,
          used_token_estimate INTEGER NOT NULL, created_at_ms INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS context_receipt_items(
          request_id TEXT NOT NULL, ordinal INTEGER NOT NULL, layer TEXT NOT NULL,
          reference TEXT NOT NULL, decision TEXT NOT NULL CHECK(decision IN ('included','excluded')),
          reason TEXT NOT NULL, PRIMARY KEY(request_id, ordinal)
        );
        CREATE TABLE IF NOT EXISTS memory_context_audit(
          audit_id TEXT PRIMARY KEY, event TEXT NOT NULL, target_ref TEXT NOT NULL, created_at_ms INTEGER NOT NULL
        );
    "#).map_err(|_| blocked("memory_schema_unavailable", "Memory／State 本地 schema 无法验证；未显示成功。"))
}
fn audit(conn: &Connection, event: &str, target: &str, time: i64) -> Result<String, Error> {
    let id = format!("audit:p3-139:{time:x}:{event}:{target}");
    conn.execute("INSERT INTO memory_context_audit(audit_id,event,target_ref,created_at_ms) VALUES(?1,?2,?3,?4)", params![id,event,target,time]).map_err(|_| blocked("database_unavailable", "审计写入失败；变更未提交。"))?;
    Ok(id)
}
fn memory_row(conn: &Connection, memory_id: &str) -> Result<(i64, String), Error> {
    conn.query_row("SELECT generation,validity FROM durable_memories WHERE memory_id=?1", params![memory_id], |row| Ok((row.get(0)?,row.get(1)?))).optional().map_err(|_| blocked("database_unavailable", "Memory 读取失败。"))?.ok_or_else(|| blocked("memory_not_found", "Memory 不存在；未写入。"))
}
fn state_row(conn: &Connection, state_id: &str) -> Result<(i64, String, String), Error> {
    conn.query_row("SELECT generation,validity,state_key FROM current_state_events WHERE state_id=?1", params![state_id], |row| Ok((row.get(0)?,row.get(1)?,row.get(2)?))).optional().map_err(|_| blocked("database_unavailable", "Current State 读取失败。"))?.ok_or_else(|| blocked("state_not_found", "Current State 不存在；未写入。"))
}
fn expected(actual: i64, provided: Option<i64>) -> Result<(), Error> { if provided == Some(actual) { Ok(()) } else { Err(blocked("stale_generation", "对象 generation 已变化；未写入。")) } }
fn memory_create_valid(paths: &Paths, request: &DurableMemoryRequest) -> Result<(), Error> {
    if !valid_mode_id(paths, &request.memory_id, "memory") || request.scope != "person" { return Err(blocked("memory_schema_rejected", "Memory 标识或范围不符合当前合同。")); }
    let statement=request.statement.as_deref().ok_or_else(||blocked("memory_schema_rejected", "Memory 缺少固定合成陈述。"))?;
    let kind=request.memory_type.as_deref().ok_or_else(||blocked("memory_schema_rejected", "Memory 缺少类型。"))?;
    let valid_statement = if paths.mode == super::InputMode::Real { !statement.trim().is_empty() && statement.chars().count() <= 200 } else { valid_memory_statement(statement) };
    if !valid_statement || !valid_memory_type(kind) { return Err(blocked("memory_schema_rejected", "Memory 字段不符合当前模式合同。")); }
    source_refs(paths, &request.source_refs)?;
    if request.idempotency_key == "synthetic-persist-fail" || (paths.mode == super::InputMode::Real && !request.idempotency_key.starts_with("p3-141-real-ui-")) { return Err(blocked("persistence_failed", "受控持久化失败；未写入。")); }
    Ok(())
}
fn state_create_valid(paths: &Paths, request: &CurrentStateRequest) -> Result<(), Error> {
    if !valid_mode_id(paths, &request.state_id, "state") { return Err(blocked("state_schema_rejected", "State 标识不符合当前模式合同。")); }
    if request.structured_health.is_some() { return Err(blocked("state_schema_rejected", "结构化 Health 必须使用专用原子路径。")); }
    let key=request.state_key.as_deref().ok_or_else(||blocked("state_schema_rejected", "State 缺少键。"))?;
    let value=request.value.as_deref().ok_or_else(||blocked("state_schema_rejected", "State 缺少固定合成值。"))?;
    if !valid_state_key(key) || !valid_state_value(value) || request.expires_at_ms.unwrap_or(0) <= 0 { return Err(blocked("state_schema_rejected", "State 字段不符合固定合成合同。")); }
    source_refs(paths, &request.source_refs)?;
    if request.idempotency_key == "synthetic-persist-fail" { return Err(blocked("persistence_failed", "受控持久化失败；未写入。")); }
    Ok(())
}

pub(crate) fn upsert(paths: &Paths, request: DurableMemoryRequest) -> Result<MemoryMutationResponse, Error> {
    match request.operation { MemoryOperation::Create => memory_create_valid(paths, &request)?, _ => {
        if !valid_mode_id(paths, &request.memory_id, "memory") || request.idempotency_key == "synthetic-persist-fail" || (paths.mode == super::InputMode::Real && !request.idempotency_key.starts_with("p3-141-real-ui-")) { return Err(blocked("memory_schema_rejected", "Memory 变更不符合当前模式合同。")); }
    }};
    write(paths, move |conn| {
        ensure_schema(conn)?;
        let tx=conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(|_|blocked("database_unavailable", "Memory 事务无法开始；未写入。"))?;
        let time=now()?;
        let (memory_id, validity, generation, event) = match request.operation {
            MemoryOperation::Create => {
                if paths.mode == super::InputMode::Real {
                    let confirmed_active: i64 = tx.query_row("SELECT count(*) FROM durable_memories WHERE confirmation='confirmed' AND validity='active' AND tombstoned=0", [], |row| row.get(0)).map_err(|_|blocked("database_unavailable","Memory 容量检查失败。"))?;
                    if confirmed_active >= 3 { return Err(blocked("durable_memory_limit_rejected", "最多保留三条已确认 Durable Memory；第 4 条在写入前已拒绝。")); }
                }
                let exists:Option<String>=tx.query_row("SELECT memory_id FROM durable_memories WHERE memory_id=?1",params![request.memory_id],|r|r.get(0)).optional().map_err(|_|blocked("database_unavailable","Memory 检查失败。"))?;
                if exists.is_some() { return Err(blocked("memory_exists", "Memory 已存在；未覆盖历史。")); }
                let statement=request.statement.as_deref().unwrap(); let kind=request.memory_type.as_deref().unwrap();
                tx.execute("INSERT INTO durable_memories(memory_id,statement,memory_type,source_refs_json,recorded_at_ms,observed_at_ms,confirmation,validity,scope,domain,generation,tombstoned) VALUES(?1,?2,?3,?4,?5,?6,'candidate','candidate',?7,?8,1,0)",params![request.memory_id,statement,kind,serde_json::to_string(request.source_refs.as_ref().unwrap()).unwrap(),time,request.observed_at_ms.unwrap_or(time),request.scope,request.domain.value()]).map_err(|_|blocked("database_unavailable","Memory 创建失败；未写入。"))?;
                tx.execute("INSERT INTO durable_memory_fts(memory_id,statement) VALUES(?1,?2)",params![request.memory_id,statement]).map_err(|_|blocked("memory_fts_unavailable","Memory FTS 创建失败；未写入。"))?;
                (request.memory_id.clone(),"candidate".into(),1,"memory_created")
            }
            MemoryOperation::Confirm => {
                let (generation,validity)=memory_row(&tx,&request.memory_id)?; expected(generation,request.expected_generation)?;
                if validity!="candidate" { return Err(blocked("memory_lifecycle_rejected","只有候选 Memory 可确认。")); }
                if paths.mode == super::InputMode::Real {
                    let confirmed_active: i64 = tx.query_row("SELECT count(*) FROM durable_memories WHERE confirmation='confirmed' AND validity='active' AND tombstoned=0", [], |row| row.get(0)).map_err(|_|blocked("database_unavailable","Memory 容量检查失败。"))?;
                    if confirmed_active >= 3 { return Err(blocked("durable_memory_limit_rejected", "最多保留三条已确认 Durable Memory；第 4 条在写入前已拒绝。")); }
                }
                tx.execute("UPDATE durable_memories SET confirmation='confirmed',validity='active',generation=generation+1 WHERE memory_id=?1",params![request.memory_id]).map_err(|_|blocked("database_unavailable","Memory 确认失败；未写入。"))?;
                (request.memory_id.clone(),"active".into(),generation+1,"memory_confirmed")
            }
            MemoryOperation::Correct | MemoryOperation::Supersede => {
                let (generation,validity)=memory_row(&tx,&request.memory_id)?; expected(generation,request.expected_generation)?;
                if validity!="active" { return Err(blocked("memory_lifecycle_rejected","只有有效 Memory 可更正或取代。")); }
                let replacement=request.replacement_id.as_deref().ok_or_else(||blocked("memory_schema_rejected","更正需要新 Memory 标识。"))?;
                let statement=request.statement.as_deref().ok_or_else(||blocked("memory_schema_rejected","更正需要固定合成陈述。"))?;
                let kind=request.memory_type.as_deref().ok_or_else(||blocked("memory_schema_rejected","更正需要类型。"))?;
                let statement_valid = if paths.mode == super::InputMode::Real { !statement.trim().is_empty() && statement.chars().count() <= 200 } else { valid_memory_statement(statement) };
                if !valid_mode_id(paths,replacement,"memory") || !statement_valid || !valid_memory_type(kind) { return Err(blocked("memory_schema_rejected","更正字段不符合当前模式合同。")); }
                source_refs(paths, &request.source_refs)?;
                tx.execute("UPDATE durable_memories SET validity='superseded',superseded_by=?2,generation=generation+1 WHERE memory_id=?1",params![request.memory_id,replacement]).map_err(|_|blocked("database_unavailable","Memory 谱系更新失败；未写入。"))?;
                tx.execute("INSERT INTO durable_memories(memory_id,statement,memory_type,source_refs_json,recorded_at_ms,observed_at_ms,confirmation,validity,scope,domain,supersedes,generation,tombstoned) VALUES(?1,?2,?3,?4,?5,?6,'confirmed','active',?7,?8,?9,1,0)",params![replacement,statement,kind,serde_json::to_string(request.source_refs.as_ref().unwrap()).unwrap(),time,request.observed_at_ms.unwrap_or(time),request.scope,request.domain.value(),request.memory_id]).map_err(|_|blocked("database_unavailable","更正 Memory 创建失败；未写入。"))?;
                tx.execute("INSERT INTO durable_memory_fts(memory_id,statement) VALUES(?1,?2)",params![replacement,statement]).map_err(|_|blocked("memory_fts_unavailable","Memory FTS 更新失败；未写入。"))?;
                (replacement.into(),"active".into(),1,if request.operation==MemoryOperation::Correct{"memory_corrected"}else{"memory_superseded"})
            }
            MemoryOperation::Expire | MemoryOperation::DeleteTombstone => {
                let (generation,validity)=memory_row(&tx,&request.memory_id)?; expected(generation,request.expected_generation)?;
                if validity!="active" { return Err(blocked("memory_lifecycle_rejected","只有有效 Memory 可到期或墓碑删除。")); }
                let (new_validity,tombstone,event)=if request.operation==MemoryOperation::Expire {("expired",0,"memory_expired")} else {("tombstoned",1,"memory_tombstoned")};
                tx.execute("UPDATE durable_memories SET validity=?2,tombstoned=?3,expires_at_ms=?4,generation=generation+1 WHERE memory_id=?1",params![request.memory_id,new_validity,tombstone,time]).map_err(|_|blocked("database_unavailable","Memory 生命周期更新失败；未写入。"))?;
                (request.memory_id.clone(),new_validity.into(),generation+1,event)
            }
        };
        let audit_ref=audit(&tx,event,&memory_id,time)?; tx.commit().map_err(|_|blocked("database_unavailable","Memory 提交失败；未显示成功。"))?;
        Ok(MemoryMutationResponse{status:"saved",memory_id,operation:request.operation,validity,generation,audit_ref})
    })
}

fn health_label(value: SleepDurationRange) -> &'static str { match value { SleepDurationRange::UnderFiveHours => "under_five_hours", SleepDurationRange::FiveToSevenHours => "five_to_seven_hours", SleepDurationRange::SevenToNineHours => "seven_to_nine_hours", SleepDurationRange::OverNineHours => "over_nine_hours" } }
fn load_label(value: TrainingLoad) -> &'static str { match value { TrainingLoad::Low => "low", TrainingLoad::Medium => "medium", TrainingLoad::High => "high" } }
fn time_label(value: AvailableTime) -> &'static str { match value { AvailableTime::UnderThirtyMinutes => "under_thirty_minutes", AvailableTime::ThirtyToSixtyMinutes => "thirty_to_sixty_minutes", AvailableTime::SixtyToOneHundredTwentyMinutes => "sixty_to_one_hundred_twenty_minutes", AvailableTime::OverOneHundredTwentyMinutes => "over_one_hundred_twenty_minutes" } }
fn health_create_valid<'a>(paths: &Paths, request: &'a CurrentStateRequest) -> Result<&'a StructuredHealthState, Error> {
    let health=request.structured_health.as_ref().ok_or_else(||blocked("health_schema_rejected","Health 必须包含全部五项结构化字段。"))?;
    if request.domain != Domain::Health || request.state_key.as_deref()!=Some("health_fitness_structured_v1") || request.value.is_some() || !valid_mode_id(paths,&request.state_id,"state") || request.expires_at_ms.unwrap_or(0)<=0 || health.energy==0 || health.energy>5 { return Err(blocked("health_schema_rejected","Health/Fitness 只能使用五项最小非诊断结构化合同；未写入。")); }
    source_refs(paths,&request.source_refs)?;
    if request.idempotency_key=="synthetic-persist-fail" || (paths.mode==super::InputMode::Real && !request.idempotency_key.starts_with("p3-141-real-ui-")) { return Err(blocked("health_schema_rejected","Health/Fitness 幂等键不符合当前合同；未写入。")); }
    Ok(health)
}
fn insert_health(tx: &rusqlite::Transaction<'_>, state_id: &str, health: &StructuredHealthState, time: i64, expires_at: i64, validity: &str, corrects: Option<&str>) -> Result<(), Error> {
    tx.execute("INSERT INTO structured_health_states(state_id,sleep_duration_range,energy,soreness_or_pain,training_load,available_time,recorded_at_ms,expires_at_ms,validity,generation,corrects) VALUES(?1,?2,?3,?4,?5,?6,?7,?8,?9,1,?10)",params![state_id,health_label(health.sleep_duration_range),health.energy as i64,if health.soreness_or_pain {1} else {0},load_label(health.training_load),time_label(health.available_time),time,expires_at,validity,corrects]).map_err(|_|blocked("database_unavailable","Health/Fitness 状态写入失败；未提交。"))?;
    Ok(())
}
fn update_structured_health(paths: &Paths, request: CurrentStateRequest) -> Result<StateMutationResponse, Error> {
    let health=health_create_valid(paths,&request)?.clone();
    write(paths, move |conn| {
        ensure_schema(conn)?;
        let tx=conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(|_|blocked("database_unavailable","Health/Fitness 事务无法开始；未写入。"))?;
        let time=now()?; let expires_at=request.expires_at_ms.unwrap();
        let (state_id,generation,event)=match request.operation {
            StateOperation::Set => {
                let exists:Option<String>=tx.query_row("SELECT state_id FROM current_state_events WHERE state_id=?1",params![request.state_id],|row|row.get(0)).optional().map_err(|_|blocked("database_unavailable","Health/Fitness 状态检查失败。"))?;
                let active:Option<String>=tx.query_row("SELECT state_id FROM current_state_events WHERE state_key='health_fitness_structured_v1' AND validity='active' LIMIT 1",[],|row|row.get(0)).optional().map_err(|_|blocked("database_unavailable","Health/Fitness 状态检查失败。"))?;
                if exists.is_some() || active.is_some() { return Err(blocked("health_state_exists","已有有效的结构化 Health/Fitness State；请使用更正路径。")); }
                tx.execute("INSERT INTO current_state_events(state_id,state_key,value_summary,domain,source_refs_json,recorded_at_ms,expires_at_ms,validity,generation) VALUES(?1,'health_fitness_structured_v1','structured_five_fields_v1','health',?2,?3,?4,'active',1)",params![request.state_id,serde_json::to_string(request.source_refs.as_ref().unwrap()).unwrap(),time,expires_at]).map_err(|_|blocked("database_unavailable","Health/Fitness State 创建失败；未提交。"))?;
                insert_health(&tx,&request.state_id,&health,time,expires_at,"active",None)?;
                (request.state_id.clone(),1,"structured_health_set")
            }
            StateOperation::Correct => {
                let replacement=request.replacement_id.as_deref().ok_or_else(||blocked("health_schema_rejected","Health/Fitness 更正需要新的 State 标识。"))?;
                if !valid_mode_id(paths,replacement,"state") { return Err(blocked("health_schema_rejected","Health/Fitness 更正标识不符合当前合同。")); }
                let (generation,validity,key)=state_row(&tx,&request.state_id)?; expected(generation,request.expected_generation)?;
                if validity!="active" || key!="health_fitness_structured_v1" { return Err(blocked("state_lifecycle_rejected","只有有效结构化 Health/Fitness State 可更正。")); }
                let exists:Option<String>=tx.query_row("SELECT state_id FROM current_state_events WHERE state_id=?1",params![replacement],|row|row.get(0)).optional().map_err(|_|blocked("database_unavailable","Health/Fitness 更正检查失败。"))?;
                if exists.is_some() { return Err(blocked("state_exists","Health/Fitness 更正标识已存在；未覆盖历史。")); }
                tx.execute("UPDATE current_state_events SET validity='corrected',generation=generation+1 WHERE state_id=?1",params![request.state_id]).map_err(|_|blocked("database_unavailable","Health/Fitness 旧 State 更新失败；未提交。"))?;
                tx.execute("UPDATE structured_health_states SET validity='corrected',generation=generation+1 WHERE state_id=?1",params![request.state_id]).map_err(|_|blocked("database_unavailable","Health/Fitness 旧值更新失败；未提交。"))?;
                tx.execute("INSERT INTO current_state_events(state_id,state_key,value_summary,domain,source_refs_json,recorded_at_ms,expires_at_ms,validity,generation,corrects) VALUES(?1,'health_fitness_structured_v1','structured_five_fields_v1','health',?2,?3,?4,'active',1,?5)",params![replacement,serde_json::to_string(request.source_refs.as_ref().unwrap()).unwrap(),time,expires_at,request.state_id]).map_err(|_|blocked("database_unavailable","Health/Fitness 更正创建失败；未提交。"))?;
                insert_health(&tx,replacement,&health,time,expires_at,"active",Some(&request.state_id))?;
                (replacement.into(),1,"structured_health_corrected")
            }
            _ => return Err(blocked("health_schema_rejected","结构化 Health/Fitness 只允许设置或更正五字段状态。")),
        };
        let slice="state:health_fitness_structured_v1";
        tx.execute("INSERT INTO snapshot_slices(slice_name,state_generation,snapshot_generation,updated_at_ms) VALUES(?1,0,0,?2) ON CONFLICT(slice_name) DO UPDATE SET state_generation=0,updated_at_ms=excluded.updated_at_ms",params![slice,time]).map_err(|_|blocked("database_unavailable","Health/Fitness Snapshot 失效标记失败；未提交。"))?;
        let audit_ref=audit(&tx,event,&state_id,time)?; tx.commit().map_err(|_|blocked("database_unavailable","Health/Fitness 提交失败；未显示成功。"))?;
        Ok(StateMutationResponse{status:"saved",state_id,operation:request.operation,validity:"active".into(),generation,invalidated_slice:slice.into(),audit_ref})
    })
}

pub(crate) fn update_state(paths: &Paths, request: CurrentStateRequest) -> Result<StateMutationResponse, Error> {
    if request.structured_health.is_some() { return update_structured_health(paths,request); }
    match request.operation { StateOperation::Set => state_create_valid(paths,&request)?, _ => {
        if !valid_mode_id(paths,&request.state_id,"state") || request.idempotency_key=="synthetic-persist-fail" || (paths.mode==super::InputMode::Real && !request.idempotency_key.starts_with("p3-141-real-ui-")) { return Err(blocked("state_schema_rejected","State 变更不符合当前模式合同。")); }
    }};
    write(paths, move |conn| {
        ensure_schema(conn)?;
        let tx=conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(|_|blocked("database_unavailable","State 事务无法开始；未写入。"))?;
        let time=now()?;
        let (state_id,validity,generation,slice,event) = match request.operation {
            StateOperation::Set => {
                let key=request.state_key.as_deref().unwrap(); let value=request.value.as_deref().unwrap();
                let exists:Option<String>=tx.query_row("SELECT state_id FROM current_state_events WHERE state_id=?1",params![request.state_id],|r|r.get(0)).optional().map_err(|_|blocked("database_unavailable","State 检查失败。"))?;
                if exists.is_some() { return Err(blocked("state_exists","State 已存在；未覆盖历史。")); }
                tx.execute("INSERT INTO current_state_events(state_id,state_key,value_summary,domain,source_refs_json,recorded_at_ms,expires_at_ms,validity,generation) VALUES(?1,?2,?3,?4,?5,?6,?7,'active',1)",params![request.state_id,key,value,request.domain.value(),serde_json::to_string(request.source_refs.as_ref().unwrap()).unwrap(),time,request.expires_at_ms.unwrap()]).map_err(|_|blocked("database_unavailable","State 创建失败；未写入。"))?;
                (request.state_id.clone(),"active".into(),1,format!("state:{}",key),"state_set")
            }
            StateOperation::Correct => {
                let (generation,validity,key)=state_row(&tx,&request.state_id)?; expected(generation,request.expected_generation)?;
                if validity!="active" { return Err(blocked("state_lifecycle_rejected","只有有效 State 可更正。")); }
                let replacement=request.replacement_id.as_deref().ok_or_else(||blocked("state_schema_rejected","State 更正需要新标识。"))?;
                let value=request.value.as_deref().ok_or_else(||blocked("state_schema_rejected","State 更正需要固定合成值。"))?;
                if !valid_mode_id(paths,replacement,"state") || !valid_state_value(value) { return Err(blocked("state_schema_rejected","State 更正字段不符合当前模式合同。")); }
                source_refs(paths,&request.source_refs)?;
                tx.execute("UPDATE current_state_events SET validity='corrected',generation=generation+1 WHERE state_id=?1",params![request.state_id]).map_err(|_|blocked("database_unavailable","State 更正谱系更新失败；未写入。"))?;
                tx.execute("INSERT INTO current_state_events(state_id,state_key,value_summary,domain,source_refs_json,recorded_at_ms,expires_at_ms,validity,generation,corrects) VALUES(?1,?2,?3,?4,?5,?6,?7,'active',1,?8)",params![replacement,key,value,request.domain.value(),serde_json::to_string(request.source_refs.as_ref().unwrap()).unwrap(),time,request.expires_at_ms.unwrap_or(time+86_400_000),request.state_id]).map_err(|_|blocked("database_unavailable","State 更正创建失败；未写入。"))?;
                (replacement.into(),"active".into(),1,format!("state:{}",key),"state_corrected")
            }
            StateOperation::Expire | StateOperation::Clear => {
                let (generation,validity,key)=state_row(&tx,&request.state_id)?; expected(generation,request.expected_generation)?;
                if validity!="active" { return Err(blocked("state_lifecycle_rejected","只有有效 State 可到期或清除。")); }
                let new_validity=if request.operation==StateOperation::Expire{"expired"}else{"cleared"};
                tx.execute("UPDATE current_state_events SET validity=?2,generation=generation+1 WHERE state_id=?1",params![request.state_id,new_validity]).map_err(|_|blocked("database_unavailable","State 生命周期更新失败；未写入。"))?;
                (request.state_id.clone(),new_validity.into(),generation+1,format!("state:{}",key),if request.operation==StateOperation::Expire{"state_expired"}else{"state_cleared"})
            }
        };
        tx.execute("INSERT INTO snapshot_slices(slice_name,state_generation,snapshot_generation,updated_at_ms) VALUES(?1,0,0,?2) ON CONFLICT(slice_name) DO UPDATE SET state_generation=0,updated_at_ms=excluded.updated_at_ms",params![slice,time]).map_err(|_|blocked("database_unavailable","Snapshot 失效标记失败；未写入。"))?;
        let audit_ref=audit(&tx,event,&state_id,time)?; tx.commit().map_err(|_|blocked("database_unavailable","State 提交失败；未显示成功。"))?;
        Ok(StateMutationResponse{status:"saved",state_id,operation:request.operation,validity,generation,invalidated_slice:slice,audit_ref})
    })
}

fn auth_valid(request: &ResolveRequest) -> bool {
    match request.task_type { TaskType::CrossDomain => request.authorization_id==AUTH_CROSS && request.health_necessary, _ => request.authorization_id==AUTH_PERSON }
}
fn allow_domain(task: TaskType, health_necessary: bool, authorization: &str, domain: &str) -> bool {
    match domain { "person" => true, "work" => !matches!(task,TaskType::Health), "health" => matches!(task,TaskType::Health) || (matches!(task,TaskType::CrossDomain) && health_necessary && authorization==AUTH_CROSS), _ => false }
}
fn item(layer: &str, reference: String, reason: &str) -> DisclosureItem { DisclosureItem{layer:layer.into(),reference,reason:reason.into()} }
fn token_for(reference: &str) -> usize { 8 + reference.len()/4 }
fn checked_budget_after(used: usize, token_budget: usize, reference: &str) -> Result<Option<usize>, Error> {
    let next=used.checked_add(token_for(reference)).ok_or_else(||blocked("context_budget_rejected","Context 预算计算溢出；未披露。"))?;
    Ok((next<=token_budget).then_some(next))
}
fn reserve_required_budget(used: &mut usize, token_budget: usize, reference: &str) -> Result<(), Error> {
    *used=checked_budget_after(*used,token_budget,reference)?.ok_or_else(||blocked("context_budget_rejected","必需 L1 或 L2 超出 Context 预算；未披露。"))?;
    Ok(())
}
pub(crate) fn resolve(paths: &Paths, request: ResolveRequest) -> Result<ResolvedContext, Error> {
    if !valid_id(&request.request_id,"request:synthetic:") || !valid_query(&request.query_text) || !auth_valid(&request) { return Err(blocked("authorization_rejected","请求目的、Authorization 或合成查询无效；未披露。")); }
    let top_k=request.top_k.unwrap_or(3); let token_budget=request.token_budget.unwrap_or(256);
    if top_k==0 || top_k>8 || token_budget<32 || token_budget>1_200 { return Err(blocked("context_budget_rejected","Context Top-K 或预算超出合同；未披露。")); }
    let removed=request.removed_domains.unwrap_or_default();
    let time=now()?;
    write(paths, move |conn| {
        ensure_schema(conn)?;
        let tx=conn.transaction_with_behavior(TransactionBehavior::Immediate).map_err(|_|blocked("database_unavailable","Resolver 事务无法开始；未披露。"))?;
        let previous:Option<String>=tx.query_row("SELECT request_id FROM context_requests WHERE request_id=?1",params![request.request_id],|r|r.get(0)).optional().map_err(|_|blocked("database_unavailable","请求谱系读取失败。"))?;
        if previous.is_some() { return Err(blocked("request_exists","request_id 已存在；不会覆盖披露收据。")); }
        let mut included=Vec::new(); let mut excluded=Vec::new(); let mut used=0usize;
        let mut profile=tx.prepare("SELECT memory_id FROM durable_memories WHERE domain='person' AND confirmation='confirmed' AND validity='active' AND tombstoned=0 AND (expires_at_ms IS NULL OR expires_at_ms>?1) ORDER BY recorded_at_ms,memory_id LIMIT 12").map_err(|_|blocked("database_unavailable","L1 查询失败。"))?;
        for row in profile.query_map(params![time],|r|r.get::<_,String>(0)).map_err(|_|blocked("database_unavailable","L1 查询失败。"))? { let reference=row.map_err(|_|blocked("database_unavailable","L1 读取失败。"))?; if removed.iter().any(|d|*d==Domain::Person) { excluded.push(item("L1",reference,"removed_for_request")); } else { reserve_required_budget(&mut used,token_budget,&reference)?; included.push(item("L1",reference,"confirmed_active_profile")); } }
        drop(profile);
        let domains:Vec<&str>=match request.task_type { TaskType::Work=>vec!["work"],TaskType::Health=>vec!["health"],TaskType::CrossDomain=>vec!["work","health"] };
        let mut snapshot_plan=Vec::new(); let mut l2_scanned=0usize;
        for domain in &domains {
            let generation:i64=tx.query_row("SELECT COALESCE(MAX(generation),0) FROM current_state_events WHERE domain=?1 AND validity='active' AND expires_at_ms>?2",params![domain,time],|r|r.get(0)).map_err(|_|blocked("database_unavailable","Snapshot 读取失败。"))?;
            let slice=format!("domain:{domain}");
            let previous_generation:Option<i64>=tx.query_row("SELECT state_generation FROM snapshot_slices WHERE slice_name=?1",params![&slice],|r|r.get(0)).optional().map_err(|_|blocked("database_unavailable","Snapshot 读取失败。"))?;
            if previous_generation!=Some(generation) { snapshot_plan.push((slice,generation)); }
            let mut states=tx.prepare("SELECT state_id FROM current_state_events WHERE domain=?1 AND validity='active' AND expires_at_ms>?2 ORDER BY state_key,generation DESC LIMIT 10").map_err(|_|blocked("database_unavailable","L2 查询失败。"))?;
            for row in states.query_map(params![domain,time],|r|r.get::<_,String>(0)).map_err(|_|blocked("database_unavailable","L2 查询失败。"))? { let reference=row.map_err(|_|blocked("database_unavailable","L2 读取失败。"))?; l2_scanned+=1; if removed.iter().any(|d|d.value()==*domain) { excluded.push(item("L2",reference,"removed_for_request")); } else { reserve_required_budget(&mut used,token_budget,&reference)?; included.push(item("L2",reference,"current_snapshot_slice")); } }
            drop(states);
        }
        let mut candidates=tx.prepare("SELECT memory_id,domain,confirmation,validity,tombstoned FROM durable_memories ORDER BY memory_id").map_err(|_|blocked("database_unavailable","L3 元数据过滤失败。"))?;
        let mut allowed_ids=Vec::new();
        for row in candidates.query_map([],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?,r.get::<_,String>(2)?,r.get::<_,String>(3)?,r.get::<_,i64>(4)?))).map_err(|_|blocked("database_unavailable","L3 元数据过滤失败。"))? {
            let (id,domain,confirmation,validity,tombstoned)=row.map_err(|_|blocked("database_unavailable","L3 元数据读取失败。"))?;
            let reason=if confirmation!="confirmed" {Some("unconfirmed")} else if validity!="active" || tombstoned!=0 {Some("invalid_or_superseded")} else if !allow_domain(request.task_type,request.health_necessary,&request.authorization_id,&domain) {Some("domain_not_necessary")} else if removed.iter().any(|d|d.value()==domain) {Some("removed_for_request")} else {None};
            if let Some(reason)=reason { excluded.push(item("L3",id,reason)); } else { allowed_ids.push(id); }
        }
        drop(candidates);
        let mut fts=tx.prepare("SELECT memory_id FROM durable_memory_fts WHERE durable_memory_fts MATCH ?1 ORDER BY rank LIMIT 8").map_err(|_|blocked("memory_fts_unavailable","FTS 召回不可用；未披露。"))?;
        let mut l3_added=0usize;
        for row in fts.query_map(params![request.query_text],|r|r.get::<_,String>(0)).map_err(|_|blocked("memory_fts_unavailable","FTS 召回不可用；未披露。"))? {
            let reference=row.map_err(|_|blocked("memory_fts_unavailable","FTS 读取失败；未披露。"))?;
            if !allowed_ids.contains(&reference) { continue; }
            if l3_added>=top_k { excluded.push(item("L3",reference,"top_k_pruned")); continue; }
            match checked_budget_after(used,token_budget,&reference)? { Some(next) => { used=next; l3_added+=1; included.push(item("L3",reference,"fts_after_authority_filter")); }, None => excluded.push(item("L3",reference,"budget_pruned")) }
        }
        drop(fts);
        if used>token_budget { return Err(blocked("context_budget_rejected","最终 Context packet 超出预算；未披露。")); }
        let mut recomputed=Vec::new();
        for (slice,generation) in snapshot_plan {
            tx.execute("INSERT INTO snapshot_slices(slice_name,state_generation,snapshot_generation,updated_at_ms) VALUES(?1,?2,1,?3) ON CONFLICT(slice_name) DO UPDATE SET state_generation=excluded.state_generation,snapshot_generation=snapshot_generation+1,updated_at_ms=excluded.updated_at_ms",params![&slice,generation,time]).map_err(|_|blocked("database_unavailable","Snapshot 更新失败；未显示成功。"))?;
            recomputed.push(slice);
        }
        let ordinal_items=included.iter().map(|x|(x,"included")).chain(excluded.iter().map(|x|(x,"excluded"))).collect::<Vec<_>>();
        tx.execute("INSERT INTO context_requests(request_id,task_type,authorization_id,resolver_version,top_k,token_budget,used_token_estimate,created_at_ms) VALUES(?1,?2,?3,?4,?5,?6,?7,?8)",params![request.request_id,request.task_type.value(),request.authorization_id,RESOLVER_VERSION,top_k as i64,token_budget as i64,used as i64,time]).map_err(|_|blocked("database_unavailable","披露收据写入失败；未显示成功。"))?;
        for (ordinal,(entry,decision)) in ordinal_items.iter().enumerate() { tx.execute("INSERT INTO context_receipt_items(request_id,ordinal,layer,reference,decision,reason) VALUES(?1,?2,?3,?4,?5,?6)",params![request.request_id,ordinal as i64,entry.layer,entry.reference,decision,entry.reason]).map_err(|_|blocked("database_unavailable","披露条目写入失败；未显示成功。"))?; }
        let receipt_ref=audit(&tx,"context_resolved",&request.request_id,time)?;
        tx.commit().map_err(|_|blocked("database_unavailable","Resolver 提交失败；未显示成功。"))?;
        Ok(ResolvedContext{status:"resolved",request_id:request.request_id,resolver_version:RESOLVER_VERSION,authorization_id:request.authorization_id,task_type:request.task_type.value().into(),included,excluded,top_k,token_budget,used_token_estimate:used,l2_scanned_rows:l2_scanned,l2_recomputed_slices:recomputed,receipt_ref,model_dispatch_count:0})
    })
}

pub(crate) fn receipt(paths: &Paths, request: ReceiptRequest) -> Result<DisclosureReceipt, Error> {
    if !valid_id(&request.request_id,"request:synthetic:") { return Err(blocked("receipt_request_rejected","披露收据标识不受支持。")); }
    let conn=read(paths)?; ensure_schema(&conn)?;
    let row:Option<(String,String,i64,i64,i64)>=conn.query_row("SELECT resolver_version,authorization_id,top_k,token_budget,used_token_estimate FROM context_requests WHERE request_id=?1",params![request.request_id],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?,r.get(3)?,r.get(4)?))).optional().map_err(|_|blocked("database_unavailable","披露收据读取失败。"))?;
    let (resolver_version,authorization_id,top_k,token_budget,used)=row.ok_or_else(||blocked("receipt_not_found","请求不存在；没有披露收据。"))?;
    let mut included=Vec::new(); let mut excluded=Vec::new();
    let mut items=conn.prepare("SELECT layer,reference,decision,reason FROM context_receipt_items WHERE request_id=?1 ORDER BY ordinal").map_err(|_|blocked("database_unavailable","披露条目读取失败。"))?;
    for item_row in items.query_map(params![request.request_id],|r|Ok((r.get::<_,String>(0)?,r.get::<_,String>(1)?,r.get::<_,String>(2)?,r.get::<_,String>(3)?))).map_err(|_|blocked("database_unavailable","披露条目读取失败。"))? { let (layer,reference,decision,reason)=item_row.map_err(|_|blocked("database_unavailable","披露条目读取失败。"))?; if decision=="included" {included.push(item(&layer,reference,&reason));}else{excluded.push(item(&layer,reference,&reason));} }
    Ok(DisclosureReceipt{status:"ready",request_id:request.request_id,resolver_version,authorization_id,top_k:top_k as usize,token_budget:token_budget as usize,used_token_estimate:used as usize,included,excluded,model_dispatch_count:0})
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    fn paths_for(name:&str)->Paths { let base=super::super::paths().unwrap().root; fs::create_dir_all(&base).unwrap(); let root=base.join(format!("p3-139-{name}-{}",super::super::now().unwrap())); fs::create_dir(&root).unwrap(); Paths{db:root.join("capture.sqlite"),root,mode:super::super::InputMode::Synthetic} }
    fn clean(paths:&Paths){fs::remove_dir_all(&paths.root).unwrap();}
    fn memory(id:&str,domain:Domain,statement:&str,kind:&str)->DurableMemoryRequest{DurableMemoryRequest{operation:MemoryOperation::Create,memory_id:id.into(),replacement_id:None,statement:Some(statement.into()),memory_type:Some(kind.into()),source_refs:Some(vec![SOURCE_REF.into()]),observed_at_ms:None,domain,scope:"person".into(),expected_generation:None,idempotency_key:format!("key-{id}")}}
    fn state(id:&str,key:&str,value:&str,domain:Domain)->CurrentStateRequest{CurrentStateRequest{operation:StateOperation::Set,state_id:id.into(),replacement_id:None,state_key:Some(key.into()),value:Some(value.into()),domain,source_refs:Some(vec![SOURCE_REF.into()]),expires_at_ms:Some(now().unwrap()+86_400_000),expected_generation:None,idempotency_key:format!("key-{id}"),structured_health:None}}
    fn resolver_counts(paths:&Paths)->(i64,i64,i64,i64,i64,i64){let conn=read(paths).unwrap();(conn.query_row("SELECT count(*) FROM context_requests",[],|r|r.get(0)).unwrap(),conn.query_row("SELECT count(*) FROM context_receipt_items",[],|r|r.get(0)).unwrap(),conn.query_row("SELECT count(*) FROM snapshot_slices",[],|r|r.get(0)).unwrap(),conn.query_row("SELECT count(*) FROM memory_context_audit",[],|r|r.get(0)).unwrap(),conn.query_row("SELECT count(*) FROM durable_memories",[],|r|r.get(0)).unwrap(),conn.query_row("SELECT count(*) FROM current_state_events",[],|r|r.get(0)).unwrap())}
    fn request(id:&str,task_type:TaskType,authorization_id:&str,health_necessary:bool,top_k:usize,token_budget:usize)->ResolveRequest{ResolveRequest{request_id:id.into(),task_type,query_text:if matches!(task_type,TaskType::CrossDomain){"recovery".into()}else{"planning".into()},authorization_id:authorization_id.into(),health_necessary,removed_domains:None,top_k:Some(top_k),token_budget:Some(token_budget)}}
    fn confirm(paths:&Paths,id:&str,generation:i64){let r=upsert(paths,DurableMemoryRequest{operation:MemoryOperation::Confirm,memory_id:id.into(),replacement_id:None,statement:None,memory_type:None,source_refs:None,observed_at_ms:None,domain:Domain::Person,scope:"person".into(),expected_generation:Some(generation),idempotency_key:format!("confirm-{id}")}).unwrap();assert_eq!(r.validity,"active");}
    fn seed(paths:&Paths){let p=upsert(paths,memory("memory:synthetic:person",Domain::Person,"Synthetic Person: prefers concise daily planning.","identity")).unwrap();confirm(paths,"memory:synthetic:person",p.generation);let w=upsert(paths,memory("memory:synthetic:work",Domain::Work,"Synthetic Work: weekday focus block supports review planning.","preference")).unwrap();confirm(paths,"memory:synthetic:work",w.generation);let h=upsert(paths,memory("memory:synthetic:health",Domain::Health,"Synthetic Health: low-impact recovery only when explicitly authorized.","constraint")).unwrap();confirm(paths,"memory:synthetic:health",h.generation);upsert(paths,memory("memory:synthetic:candidate",Domain::Work,"Synthetic Candidate: unconfirmed preference.","preference")).unwrap();update_state(paths,state("state:synthetic:load","work_load","synthetic_work_load_high",Domain::Work)).unwrap();update_state(paths,state("state:synthetic:fatigue","fatigue","synthetic_fatigue_moderate",Domain::Health)).unwrap();}
    #[test] fn memory_and_state_lifecycle_preserve_lineage(){let p=paths_for("lifecycle");let created=upsert(&p,memory("memory:synthetic:work",Domain::Work,"Synthetic Work: weekday focus block supports review planning.","preference")).unwrap();confirm(&p,"memory:synthetic:work",created.generation);let corrected=upsert(&p,DurableMemoryRequest{operation:MemoryOperation::Correct,memory_id:"memory:synthetic:work".into(),replacement_id:Some("memory:synthetic:work-corrected".into()),statement:Some("Synthetic Work: corrected planning preference is a 25-minute focus block.".into()),memory_type:Some("preference".into()),source_refs:Some(vec![SOURCE_REF.into()]),observed_at_ms:None,domain:Domain::Work,scope:"person".into(),expected_generation:Some(2),idempotency_key:"correct-work".into()}).unwrap();assert_eq!(corrected.memory_id,"memory:synthetic:work-corrected");let st=update_state(&p,state("state:synthetic:fatigue","fatigue","synthetic_fatigue_moderate",Domain::Health)).unwrap();let cleared=update_state(&p,CurrentStateRequest{operation:StateOperation::Clear,state_id:st.state_id,replacement_id:None,state_key:None,value:None,domain:Domain::Health,source_refs:None,expires_at_ms:None,expected_generation:Some(1),idempotency_key:"clear-fatigue".into(),structured_health:None}).unwrap();assert_eq!(cleared.validity,"cleared");let conn=read(&p).unwrap();assert_eq!(conn.query_row("SELECT count(*) FROM durable_memories",[],|r|r.get::<_,i64>(0)).unwrap(),2);assert_eq!(conn.query_row("SELECT count(*) FROM current_state_events",[],|r|r.get::<_,i64>(0)).unwrap(),1);clean(&p);}
    #[test] fn resolver_filters_authority_budgets_and_domain(){let p=paths_for("resolver");seed(&p);let r=resolve(&p,ResolveRequest{request_id:"request:synthetic:work-1".into(),task_type:TaskType::Work,query_text:"planning".into(),authorization_id:AUTH_PERSON.into(),health_necessary:false,removed_domains:None,top_k:Some(3),token_budget:Some(256)}).unwrap();assert!(r.included.iter().any(|x|x.reference=="memory:synthetic:person"));assert!(r.included.iter().any(|x|x.reference=="memory:synthetic:work"));assert!(r.excluded.iter().any(|x|x.reference=="memory:synthetic:health"&&x.reason=="domain_not_necessary"));assert!(r.excluded.iter().any(|x|x.reference=="memory:synthetic:candidate"&&x.reason=="unconfirmed"));assert_eq!(r.model_dispatch_count,0);let receipt=receipt(&p,ReceiptRequest{request_id:"request:synthetic:work-1".into()}).unwrap();assert_eq!(receipt.included.len(),r.included.len());assert!(!format!("{:?}",receipt.excluded).contains("Synthetic Work"));clean(&p);}
    #[test] fn cross_domain_authorization_and_request_removal_are_scoped(){let p=paths_for("cross");seed(&p);let removed=resolve(&p,ResolveRequest{request_id:"request:synthetic:cross-removed".into(),task_type:TaskType::CrossDomain,query_text:"recovery".into(),authorization_id:AUTH_CROSS.into(),health_necessary:true,removed_domains:Some(vec![Domain::Health]),top_k:Some(3),token_budget:Some(256)}).unwrap();assert!(removed.excluded.iter().any(|x|x.reference=="memory:synthetic:health"&&x.reason=="removed_for_request"));let normal=resolve(&p,ResolveRequest{request_id:"request:synthetic:cross-normal".into(),task_type:TaskType::CrossDomain,query_text:"recovery".into(),authorization_id:AUTH_CROSS.into(),health_necessary:true,removed_domains:None,top_k:Some(3),token_budget:Some(256)}).unwrap();assert!(normal.included.iter().any(|x|x.reference=="memory:synthetic:health"));clean(&p);}
    #[test] fn failure_paths_do_not_write_receipts_or_mutate_authority(){let p=paths_for("failclosed");seed(&p);let conn=read(&p).unwrap();let before:(i64,i64)=(conn.query_row("SELECT count(*) FROM durable_memories",[],|r|r.get(0)).unwrap(),conn.query_row("SELECT count(*) FROM context_requests",[],|r|r.get(0)).unwrap());drop(conn);let err=resolve(&p,ResolveRequest{request_id:"request:synthetic:bad".into(),task_type:TaskType::Work,query_text:"planning".into(),authorization_id:"AUTH-SYN-REVOKED".into(),health_necessary:false,removed_domains:None,top_k:Some(3),token_budget:Some(256)}).unwrap_err();assert_eq!(err.code,"authorization_rejected");let err=upsert(&p,DurableMemoryRequest{operation:MemoryOperation::Expire,memory_id:"memory:synthetic:work".into(),replacement_id:None,statement:None,memory_type:None,source_refs:None,observed_at_ms:None,domain:Domain::Work,scope:"person".into(),expected_generation:Some(999),idempotency_key:"stale".into()}).unwrap_err();assert_eq!(err.code,"stale_generation");let after=read(&p).unwrap();assert_eq!(before.0,after.query_row("SELECT count(*) FROM durable_memories",[],|r|r.get::<_,i64>(0)).unwrap());assert_eq!(before.1,after.query_row("SELECT count(*) FROM context_requests",[],|r|r.get::<_,i64>(0)).unwrap());clean(&p);}
    #[test] fn receipt_reopens_deterministically_and_snapshots_incrementally(){let p=paths_for("restart");seed(&p);let first=resolve(&p,ResolveRequest{request_id:"request:synthetic:restart".into(),task_type:TaskType::Work,query_text:"planning".into(),authorization_id:AUTH_PERSON.into(),health_necessary:false,removed_domains:None,top_k:Some(3),token_budget:Some(256)}).unwrap();let reopened=receipt(&p,ReceiptRequest{request_id:"request:synthetic:restart".into()}).unwrap();assert_eq!(first.used_token_estimate,reopened.used_token_estimate);assert!(!first.l2_recomputed_slices.is_empty());let second=resolve(&p,ResolveRequest{request_id:"request:synthetic:again".into(),task_type:TaskType::Work,query_text:"planning".into(),authorization_id:AUTH_PERSON.into(),health_necessary:false,removed_domains:None,top_k:Some(3),token_budget:Some(256)}).unwrap();assert!(second.l2_recomputed_slices.is_empty());clean(&p);}
    #[test] fn complete_memory_and_state_operations_preserve_history(){let p=paths_for("operations");let first=upsert(&p,memory("memory:synthetic:work",Domain::Work,"Synthetic Work: weekday focus block supports review planning.","preference")).unwrap();confirm(&p,"memory:synthetic:work",first.generation);let replacement=upsert(&p,DurableMemoryRequest{operation:MemoryOperation::Supersede,memory_id:"memory:synthetic:work".into(),replacement_id:Some("memory:synthetic:work-corrected".into()),statement:Some("Synthetic Work: corrected planning preference is a 25-minute focus block.".into()),memory_type:Some("preference".into()),source_refs:Some(vec![SOURCE_REF.into()]),observed_at_ms:None,domain:Domain::Work,scope:"person".into(),expected_generation:Some(2),idempotency_key:"supersede-work".into()}).unwrap();let expired=upsert(&p,DurableMemoryRequest{operation:MemoryOperation::Expire,memory_id:replacement.memory_id,replacement_id:None,statement:None,memory_type:None,source_refs:None,observed_at_ms:None,domain:Domain::Work,scope:"person".into(),expected_generation:Some(1),idempotency_key:"expire-work".into()}).unwrap();assert_eq!(expired.validity,"expired");let health=upsert(&p,memory("memory:synthetic:health",Domain::Health,"Synthetic Health: low-impact recovery only when explicitly authorized.","constraint")).unwrap();confirm(&p,"memory:synthetic:health",health.generation);let tombstone=upsert(&p,DurableMemoryRequest{operation:MemoryOperation::DeleteTombstone,memory_id:"memory:synthetic:health".into(),replacement_id:None,statement:None,memory_type:None,source_refs:None,observed_at_ms:None,domain:Domain::Health,scope:"person".into(),expected_generation:Some(2),idempotency_key:"tombstone-health".into()}).unwrap();assert_eq!(tombstone.validity,"tombstoned");let fatigue=update_state(&p,state("state:synthetic:fatigue","fatigue","synthetic_fatigue_moderate",Domain::Health)).unwrap();let corrected=update_state(&p,CurrentStateRequest{operation:StateOperation::Correct,state_id:fatigue.state_id,replacement_id:Some("state:synthetic:fatigue-corrected".into()),state_key:None,value:Some("synthetic_fatigue_low".into()),domain:Domain::Health,source_refs:Some(vec![SOURCE_REF.into()]),expires_at_ms:Some(now().unwrap()+86_400_000),expected_generation:Some(1),idempotency_key:"correct-fatigue".into(),structured_health:None}).unwrap();let expired_state=update_state(&p,CurrentStateRequest{operation:StateOperation::Expire,state_id:corrected.state_id,replacement_id:None,state_key:None,value:None,domain:Domain::Health,source_refs:None,expires_at_ms:None,expected_generation:Some(1),idempotency_key:"expire-fatigue".into(),structured_health:None}).unwrap();assert_eq!(expired_state.validity,"expired");let load=update_state(&p,state("state:synthetic:load","work_load","synthetic_work_load_high",Domain::Work)).unwrap();let cleared=update_state(&p,CurrentStateRequest{operation:StateOperation::Clear,state_id:load.state_id,replacement_id:None,state_key:None,value:None,domain:Domain::Work,source_refs:None,expires_at_ms:None,expected_generation:Some(1),idempotency_key:"clear-load".into(),structured_health:None}).unwrap();assert_eq!(cleared.validity,"cleared");let conn=read(&p).unwrap();assert_eq!(conn.query_row("SELECT count(*) FROM durable_memories",[],|r|r.get::<_,i64>(0)).unwrap(),3);assert_eq!(conn.query_row("SELECT count(*) FROM current_state_events",[],|r|r.get::<_,i64>(0)).unwrap(),3);clean(&p);}
    #[test] fn format_budget_and_missing_receipt_fail_closed(){
        let p=paths_for("budget-minimum");seed(&p);let before=resolver_counts(&p);
        let minimum=resolve(&p,request("request:synthetic:budget-32",TaskType::CrossDomain,AUTH_CROSS,true,3,32)).unwrap_err();assert_eq!(minimum.code,"context_budget_rejected");assert_eq!(before,resolver_counts(&p));
        let repeated=resolve(&p,request("request:synthetic:budget-32",TaskType::CrossDomain,AUTH_CROSS,true,3,32)).unwrap_err();assert_eq!(repeated.code,"context_budget_rejected");assert_eq!(before,resolver_counts(&p));drop(read(&p).unwrap());assert_eq!(receipt(&p,ReceiptRequest{request_id:"request:synthetic:budget-32".into()}).unwrap_err().code,"receipt_not_found");clean(&p);
        let exact=paths_for("budget-exact");seed(&exact);let resolved=resolve(&exact,request("request:synthetic:budget-exact",TaskType::Work,AUTH_PERSON,false,1,39)).unwrap();assert_eq!(resolved.used_token_estimate,39);assert_eq!(resolved.used_token_estimate,resolved.token_budget);assert!(resolved.included.iter().any(|entry|entry.layer=="L3"));let reopened=receipt(&exact,ReceiptRequest{request_id:"request:synthetic:budget-exact".into()}).unwrap();assert_eq!(reopened.used_token_estimate,39);clean(&exact);
        let p=paths_for("budget-plus-one");seed(&p);let before=resolver_counts(&p);let plus_one=resolve(&p,request("request:synthetic:budget-38",TaskType::CrossDomain,AUTH_CROSS,true,3,38)).unwrap_err();assert_eq!(plus_one.code,"context_budget_rejected");assert_eq!(before,resolver_counts(&p));clean(&p);
        let p=paths_for("budget-multi");seed(&p);let extra=upsert(&p,memory("memory:synthetic:person-two",Domain::Person,"Synthetic Person: prefers concise daily planning.","identity")).unwrap();confirm(&p,"memory:synthetic:person-two",extra.generation);update_state(&p,state("state:synthetic:sleep","sleep","synthetic_sleep_short",Domain::Health)).unwrap();let required=token_for("memory:synthetic:person")+token_for("memory:synthetic:person-two")+token_for("state:synthetic:load")+token_for("state:synthetic:fatigue")+token_for("state:synthetic:sleep");let before=resolver_counts(&p);let multi=resolve(&p,request("request:synthetic:budget-multi",TaskType::CrossDomain,AUTH_CROSS,true,3,required-1)).unwrap_err();assert_eq!(multi.code,"context_budget_rejected");assert_eq!(before,resolver_counts(&p));clean(&p);
        let p=paths_for("boundaries");seed(&p);let before=resolver_counts(&p);let bad_query=resolve(&p,ResolveRequest{request_id:"request:synthetic:bad-query".into(),task_type:TaskType::Work,query_text:"everything".into(),authorization_id:AUTH_PERSON.into(),health_necessary:false,removed_domains:None,top_k:Some(3),token_budget:Some(256)}).unwrap_err();assert_eq!(bad_query.code,"authorization_rejected");let bad_budget=resolve(&p,request("request:synthetic:bad-budget",TaskType::Work,AUTH_PERSON,false,9,256)).unwrap_err();assert_eq!(bad_budget.code,"context_budget_rejected");assert_eq!(receipt(&p,ReceiptRequest{request_id:"request:synthetic:missing".into()}).unwrap_err().code,"receipt_not_found");assert_eq!(before,resolver_counts(&p));clean(&p);
    }
    #[test] fn inactive_authority_is_excluded_from_l1_and_l3(){let p=paths_for("inactive");let person=upsert(&p,memory("memory:synthetic:person",Domain::Person,"Synthetic Person: prefers concise daily planning.","identity")).unwrap();confirm(&p,"memory:synthetic:person",person.generation);let work=upsert(&p,memory("memory:synthetic:work",Domain::Work,"Synthetic Work: weekday focus block supports review planning.","preference")).unwrap();confirm(&p,"memory:synthetic:work",work.generation);upsert(&p,DurableMemoryRequest{operation:MemoryOperation::Expire,memory_id:"memory:synthetic:person".into(),replacement_id:None,statement:None,memory_type:None,source_refs:None,observed_at_ms:None,domain:Domain::Person,scope:"person".into(),expected_generation:Some(2),idempotency_key:"expire-person".into()}).unwrap();upsert(&p,DurableMemoryRequest{operation:MemoryOperation::DeleteTombstone,memory_id:"memory:synthetic:work".into(),replacement_id:None,statement:None,memory_type:None,source_refs:None,observed_at_ms:None,domain:Domain::Work,scope:"person".into(),expected_generation:Some(2),idempotency_key:"remove-work".into()}).unwrap();let resolved=resolve(&p,ResolveRequest{request_id:"request:synthetic:inactive".into(),task_type:TaskType::Work,query_text:"planning".into(),authorization_id:AUTH_PERSON.into(),health_necessary:false,removed_domains:None,top_k:Some(3),token_budget:Some(256)}).unwrap();assert!(!resolved.included.iter().any(|entry|entry.reference=="memory:synthetic:person"||entry.reference=="memory:synthetic:work"));assert!(resolved.excluded.iter().any(|entry|entry.reference=="memory:synthetic:work"&&entry.reason=="invalid_or_superseded"));clean(&p);}
    #[test] fn understanding_is_not_created_by_resolver(){let p=paths_for("non-promotion");seed(&p);resolve(&p,ResolveRequest{request_id:"request:synthetic:no-promotion".into(),task_type:TaskType::Work,query_text:"planning".into(),authorization_id:AUTH_PERSON.into(),health_necessary:false,removed_domains:None,top_k:Some(3),token_budget:Some(256)}).unwrap();let conn=read(&p).unwrap();let before:i64=conn.query_row("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='understandings'",[],|r|r.get(0)).unwrap();assert_eq!(before,1);let rows:i64=conn.query_row("SELECT count(*) FROM understandings",[],|r|r.get(0)).unwrap();assert_eq!(rows,0);clean(&p);}
}
