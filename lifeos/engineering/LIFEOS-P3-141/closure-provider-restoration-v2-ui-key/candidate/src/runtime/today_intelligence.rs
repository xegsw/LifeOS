//! P3-140's synthetic, local-only Today intelligence contract.
//!
//! This module is intentionally reachable only through the already-existing
//! `get_today` IPC.  It neither enables a Provider nor creates a durable-memory
//! fact: all outputs are evidence-linked, revisable candidates.

use super::{memory_context, now, read, write, Error, Paths};
use rusqlite::{params, Connection, OptionalExtension, TransactionBehavior};
use serde::{Deserialize, Serialize};

const AUTH_PERSON: &str = "p3-140-synthetic-person-granted";
const AUTH_CROSS_DOMAIN: &str = "p3-140-synthetic-cross-domain-granted";
const MAX_REQUEST_ID: usize = 96;
const MAX_DETAIL: usize = 120;

const SCHEMA: &str = r#"
CREATE TABLE IF NOT EXISTS p3140_state(
    state_key TEXT PRIMARY KEY,
    state_value INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS p3140_runs(
    request_id TEXT PRIMARY KEY,
    scenario TEXT NOT NULL,
    health_included INTEGER NOT NULL,
    generation INTEGER NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('active','superseded')),
    response_json TEXT NOT NULL,
    created_at_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS p3140_results(
    result_id TEXT PRIMARY KEY,
    request_id TEXT NOT NULL,
    state TEXT NOT NULL CHECK(state IN ('candidate','stale')),
    evidence_refs_json TEXT NOT NULL,
    FOREIGN KEY(request_id) REFERENCES p3140_runs(request_id)
);
CREATE TABLE IF NOT EXISTS p3140_feedback(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    idempotency_key TEXT NOT NULL UNIQUE,
    result_id TEXT NOT NULL,
    decision TEXT NOT NULL,
    detail TEXT NOT NULL,
    created_at_ms INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS p3140_understandings(
    understanding_id TEXT PRIMARY KEY,
    result_id TEXT NOT NULL UNIQUE,
    state TEXT NOT NULL CHECK(state IN ('candidate','stale')),
    identity TEXT NOT NULL CHECK(identity='system_suggestion'),
    promotion TEXT NOT NULL CHECK(promotion='none'),
    generation INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS p3140_audit(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event TEXT NOT NULL,
    target_id TEXT NOT NULL,
    detail TEXT NOT NULL,
    created_at_ms INTEGER NOT NULL
);
INSERT OR IGNORE INTO p3140_state(state_key,state_value) VALUES('generation',0);
"#;

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct TodayRequest {
    pub scenario: Option<String>,
    pub counterfactual_case: Option<String>,
    pub request_id: Option<String>,
    pub health_included: Option<bool>,
    pub authorization: Option<String>,
    pub feedback: Option<TodayFeedback>,
    pub expected_generation: Option<i64>,
    pub fault: Option<String>,
}

impl TodayRequest {
    pub(crate) fn is_p3140(&self) -> bool {
        self.scenario.is_some()
            || self.counterfactual_case.is_some()
            || self.request_id.is_some()
            || self.health_included.is_some()
            || self.authorization.is_some()
            || self.feedback.is_some()
            || self.expected_generation.is_some()
            || self.fault.is_some()
    }
}

#[derive(Debug, Deserialize)]
#[serde(deny_unknown_fields)]
pub(crate) struct TodayFeedback {
    pub result_id: String,
    pub decision: FeedbackDecision,
    pub detail: Option<String>,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize, PartialEq, Eq)]
#[serde(rename_all = "snake_case")]
pub(crate) enum FeedbackDecision {
    Confirm,
    Edit,
    Reject,
    Ignore,
    Correct,
}

impl FeedbackDecision {
    fn value(self) -> &'static str {
        match self {
            Self::Confirm => "confirm",
            Self::Edit => "edit",
            Self::Reject => "reject",
            Self::Ignore => "ignore",
            Self::Correct => "correct",
        }
    }

    fn invalidates(self) -> bool {
        matches!(self, Self::Reject | Self::Correct)
    }
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) struct TodayIntelligence {
    pub status: String,
    pub scenario: String,
    pub request_id: String,
    pub snapshot_generation: i64,
    pub cross_domain_limited: bool,
    pub counterfactual_case: Option<String>,
    pub context_receipt_ref: String,
    pub question: Option<Question>,
    pub results: Vec<ResultCard>,
    pub explanation: String,
    pub disclosure_refs: Vec<String>,
    pub feedback: FeedbackState,
    pub recomputation: Recomputation,
    pub dispatch: DispatchBoundary,
    pub durable_memory_promoted: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) struct Question {
    pub identity: String,
    pub text: String,
    pub purpose: String,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) struct ResultCard {
    pub result_id: String,
    pub identity: String,
    pub title: String,
    pub why_today: String,
    pub domains: Vec<String>,
    pub evidence_refs: Vec<String>,
    pub uncertainty: String,
    pub stop_condition: Option<String>,
    pub feedback_options: Vec<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) struct FeedbackState {
    pub decision: Option<String>,
    pub target_result_id: Option<String>,
    pub candidate_only: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) struct Recomputation {
    pub invalidated_refs: Vec<String>,
    pub recomputed_slices: Vec<String>,
    pub unaffected_slices_recomputed: bool,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub(crate) struct DispatchBoundary {
    pub provider_dispatch_count: u32,
    pub model_dispatch_count: u32,
    pub network_dispatch_count: u32,
    pub external_tool_dispatch_count: u32,
}

fn rejected(code: &'static str, message: &'static str) -> Error {
    Error::blocked(code, message)
}

fn valid_request_id(value: &str) -> bool {
    value.starts_with("p3-140:")
        && value.len() <= MAX_REQUEST_ID
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b':' | b'-' | b'_'))
}

fn validate_request(request: &TodayRequest) -> Result<(String, String, bool, Option<String>), Error> {
    let scenario = request.scenario.as_deref().unwrap_or("normal");
    if !matches!(
        scenario,
        "normal" | "counterfactual" | "missing_health" | "missing_health_skip" | "health_stop" | "insufficient"
    ) {
        return Err(rejected(
            "today_scenario_rejected",
            "Today 合成场景不在 P3-140 固定合同内；未读取或写入。",
        ));
    }
    let request_id = request
        .request_id
        .as_deref()
        .ok_or_else(|| rejected("today_request_rejected", "Today 请求缺少固定请求标识；未写入。"))?;
    if !valid_request_id(request_id) {
        return Err(rejected(
            "today_request_rejected",
            "Today 请求标识不符合固定合成边界；未写入。",
        ));
    }
    let health_included = request.health_included.unwrap_or(true);
    let required_authorization = if health_included {
        AUTH_CROSS_DOMAIN
    } else {
        AUTH_PERSON
    };
    if request.authorization.as_deref() != Some(required_authorization) {
        return Err(rejected(
            "today_authorization_rejected",
            "Today 跨域或 Person 授权不完整；未读取、组装或写入。",
        ));
    }
    if let Some(fault) = request.fault.as_deref() {
        let (code, message) = match fault {
            "authorization_revoked" => (
                "today_authorization_rejected",
                "合成授权已撤销；未读取、组装或写入。",
            ),
            "stale_generation" => (
                "today_generation_stale",
                "Today 快照代次已过期；未写入。",
            ),
            "over_budget" => (
                "context_budget_rejected",
                "跨域 Context 超出固定预算；未静默删减、未写入。",
            ),
            "malformed" => (
                "today_request_rejected",
                "Today 请求字段不完整；未写入。",
            ),
            "database_failure" => (
                "database_unavailable",
                "合成数据库不可用；未显示成功。",
            ),
            "recompute_failure" => (
                "today_recompute_rejected",
                "反馈后的重算未完成；旧候选保持可追溯且未提升。",
            ),
            _ => {
                return Err(rejected(
                    "today_fault_rejected",
                    "故障注入标识不在固定合成合同内；未写入。",
                ));
            }
        };
        return Err(rejected(code, message));
    }
    if let Some(feedback) = &request.feedback {
        if !feedback.result_id.starts_with("result:p3-140:")
            || feedback.result_id.len() > 180
            || feedback.detail.as_deref().is_some_and(|value| {
                value.trim().is_empty() || value.chars().count() > MAX_DETAIL
            })
        {
            return Err(rejected(
                "today_feedback_rejected",
                "Today 反馈不符合固定对象级边界；未写入。",
            ));
        }
        if request.expected_generation.is_none() {
            return Err(rejected(
                "today_generation_rejected",
                "对象级反馈必须携带当前快照代次；未写入。",
            ));
        }
    }
    let counterfactual_case = match (scenario, request.counterfactual_case.as_deref()) {
        ("counterfactual", None) => Some("sleep_fatigue".to_owned()),
        ("counterfactual", Some(value @ ("long_term_constraint" | "sleep_fatigue" | "recent_training" | "pain" | "available_time"))) => Some(value.to_owned()),
        ("counterfactual", Some(_)) => return Err(rejected("today_counterfactual_rejected", "反事实变量不在固定合成矩阵内；未写入。")),
        (_, Some(_)) => return Err(rejected("today_counterfactual_rejected", "非反事实请求不可携带反事实变量；未写入。")),
        (_, None) => None,
    };
    Ok((scenario.to_owned(), request_id.to_owned(), health_included, counterfactual_case))
}

fn init(conn: &Connection) -> Result<(), Error> {
    conn.execute_batch(SCHEMA).map_err(|_| {
        rejected(
            "database_unavailable",
            "Today 合成状态无法初始化；未显示成功。",
        )
    })
}

fn fixture_ready(paths: &Paths) -> bool {
    if !paths.db.is_file() {
        return false;
    }
    let Ok(connection) = read(paths) else { return false; };
    let count = connection.query_row(
        "SELECT count(*) FROM sqlite_master WHERE type='table' AND name IN ('durable_memories','current_state_events')",
        [],
        |row| row.get::<_, i64>(0),
    );
    if count.ok() != Some(2) {
        return false;
    }
    let memories = connection.query_row(
        "SELECT count(*) FROM durable_memories WHERE memory_id IN (?1,?2,?3) AND confirmation='confirmed' AND validity='active'",
        params![fixture_memory_id(paths,"person"),fixture_memory_id(paths,"work"),fixture_memory_id(paths,"health")],
        |row| row.get::<_, i64>(0),
    );
    let states = connection.query_row(
        "SELECT count(*) FROM current_state_events WHERE state_id IN (?1,?2) AND validity='active'",
        params![fixture_state_id(paths,"load"),fixture_state_id(paths,"fatigue")],
        |row| row.get::<_, i64>(0),
    );
    memories.ok() == Some(3) && states.ok() == Some(2)
}

fn fixture_memory_id(paths: &Paths, suffix: &str) -> String {
    if paths.mode == super::InputMode::Real { format!("memory:p3-141:real:fixture-{suffix}") } else { format!("memory:synthetic:{suffix}") }
}
fn fixture_state_id(paths: &Paths, suffix: &str) -> String {
    if paths.mode == super::InputMode::Real { format!("state:p3-141:real:fixture-{suffix}") } else { format!("state:synthetic:{suffix}") }
}
fn fixture_source(paths: &Paths) -> &'static str {
    if paths.mode == super::InputMode::Real { "source:synthetic:controlled-fixture" } else { "source:synthetic:memory-fixture" }
}
fn fixture_key(paths: &Paths, action: &str, id: &str) -> String {
    if paths.mode == super::InputMode::Real { format!("p3-141-real-ui-fixture-{action}-{id}") } else { format!("p3-140-{action}-{id}") }
}

fn create_memory(paths: &Paths, id: &str, domain: memory_context::Domain, statement: &str, kind: &str) -> Result<(), Error> {
    let created = memory_context::upsert(paths, memory_context::DurableMemoryRequest {
        operation: memory_context::MemoryOperation::Create,
        memory_id: id.to_owned(), replacement_id: None, statement: Some(statement.to_owned()),
        memory_type: Some(kind.to_owned()), source_refs: Some(vec![fixture_source(paths).to_owned()]),
        observed_at_ms: None, domain, scope: "person".to_owned(), expected_generation: None,
        idempotency_key: fixture_key(paths,"seed",id),
    })?;
    memory_context::upsert(paths, memory_context::DurableMemoryRequest {
        operation: memory_context::MemoryOperation::Confirm,
        memory_id: id.to_owned(), replacement_id: None, statement: None, memory_type: None,
        source_refs: None, observed_at_ms: None, domain, scope: "person".to_owned(),
        expected_generation: Some(created.generation), idempotency_key: fixture_key(paths,"confirm",id),
    })?;
    Ok(())
}

fn create_state(paths: &Paths, id: &str, key: &str, value: &str, domain: memory_context::Domain) -> Result<(), Error> {
    memory_context::update_state(paths, memory_context::CurrentStateRequest {
        operation: memory_context::StateOperation::Set,
        state_id: id.to_owned(), replacement_id: None, state_key: Some(key.to_owned()), value: Some(value.to_owned()),
        domain, source_refs: Some(vec![fixture_source(paths).to_owned()]),
        expires_at_ms: Some(now()? + 86_400_000), expected_generation: None,
        idempotency_key: fixture_key(paths,"state",id),
        structured_health: None,
    })?;
    Ok(())
}

fn ensure_p3139_fixture(paths: &Paths) -> Result<(), Error> {
    if fixture_ready(paths) {
        return Ok(());
    }
    if paths.db.exists() && !super::controlled_fixture_evidence(paths) {
        return Err(rejected("today_fixture_rejected", "P3-139 合成 Memory／State fixture 不完整；未组装 Today。"));
    }
    create_memory(paths, &fixture_memory_id(paths,"person"), memory_context::Domain::Person, "Synthetic Person: prefers concise daily planning.", "identity")?;
    create_memory(paths, &fixture_memory_id(paths,"work"), memory_context::Domain::Work, "Synthetic Work: weekday focus block supports review planning.", "preference")?;
    create_memory(paths, &fixture_memory_id(paths,"health"), memory_context::Domain::Health, "Synthetic Health: low-impact recovery only when explicitly authorized.", "constraint")?;
    create_state(paths, &fixture_state_id(paths,"load"), "work_load", "synthetic_work_load_high", memory_context::Domain::Work)?;
    create_state(paths, &fixture_state_id(paths,"fatigue"), "fatigue", "synthetic_fatigue_moderate", memory_context::Domain::Health)?;
    if fixture_ready(paths) { Ok(()) } else { Err(rejected("today_fixture_rejected", "P3-139 合成 fixture 无法完整验证；未组装 Today。")) }
}

fn receipt_id(request_id: &str) -> String {
    format!("request:synthetic:{}", request_id.replace(':', "-"))
}

fn resolve_disclosure(paths: &Paths, request_id: &str, health_included: bool) -> Result<(Vec<String>, String), Error> {
    let request_id = receipt_id(request_id);
    let resolved = memory_context::resolve(paths, memory_context::ResolveRequest {
        request_id: request_id.clone(),
        task_type: if health_included { memory_context::TaskType::CrossDomain } else { memory_context::TaskType::Work },
        query_text: if health_included { "recovery".to_owned() } else { "planning".to_owned() },
        authorization_id: if health_included { "AUTH-SYN-CROSS-GRANTED".to_owned() } else { "AUTH-SYN-PERSON-GRANTED".to_owned() },
        health_necessary: health_included,
        removed_domains: None,
        top_k: Some(3),
        token_budget: Some(256),
    })?;
    if resolved.model_dispatch_count != 0 {
        return Err(rejected("today_dispatch_rejected", "Context Resolver dispatch 计数异常；未组装 Today。"));
    }
    let receipt = memory_context::receipt(paths, memory_context::ReceiptRequest { request_id: request_id.clone() })?;
    if receipt.model_dispatch_count != 0 {
        return Err(rejected("today_dispatch_rejected", "Context disclosure receipt dispatch 计数异常；未组装 Today。"));
    }
    let refs = receipt.included.into_iter().map(|item| item.reference).collect::<Vec<_>>();
    if refs.is_empty() || (!health_included && refs.iter().any(|item| item.contains("health") || item.contains("fatigue"))) {
        return Err(rejected("today_disclosure_rejected", "Context disclosure 与 Today 范围不一致；未组装 Today。"));
    }
    Ok((refs, request_id))
}

fn generation(conn: &Connection) -> Result<i64, Error> {
    conn.query_row(
        "SELECT state_value FROM p3140_state WHERE state_key='generation'",
        [],
        |row| row.get(0),
    )
    .map_err(|_| rejected("database_unavailable", "Today 代次不可验证；未显示成功。"))
}

fn card(
    request_id: &str,
    suffix: &str,
    title: &str,
    why_today: &str,
    domains: Vec<&str>,
    evidence_refs: Vec<String>,
    uncertainty: &str,
    stop_condition: Option<&str>,
) -> ResultCard {
    ResultCard {
        result_id: format!("result:p3-140:{request_id}:{suffix}"),
        identity: "system_suggestion".to_owned(),
        title: title.to_owned(),
        why_today: why_today.to_owned(),
        domains: domains.into_iter().map(str::to_owned).collect(),
        evidence_refs,
        uncertainty: uncertainty.to_owned(),
        stop_condition: stop_condition.map(str::to_owned),
        feedback_options: vec![
            "confirm".to_owned(),
            "edit".to_owned(),
            "reject".to_owned(),
            "ignore".to_owned(),
            "correct".to_owned(),
        ],
    }
}

fn model(
    scenario: &str,
    request_id: &str,
    health_included: bool,
    generation: i64,
    recomputed: bool,
    counterfactual_case: Option<&str>,
    refs: Vec<String>,
    context_receipt_ref: String,
) -> TodayIntelligence {
    let (question, results, explanation) = match scenario {
        "counterfactual" => {
            let (title, why, domains, stop_condition) = match counterfactual_case.unwrap_or("sleep_fatigue") {
                "long_term_constraint" => ("遵守长期节奏：只保留一个 25 分钟 Work 聚焦块", "长期约束改变了排序，避免把临时冲刺提升为默认节奏。", vec!["Work"], None),
                "sleep_fatigue" => ("睡眠／疲劳较高时先缩小 Work 范围", "睡眠与疲劳变化改变了可执行性；不推断它们与 Work 的因果。", vec!["Work", "Health"], Some("若不适或疲劳加重，停止并改为人工核对。")),
                "recent_training" => ("近期训练负荷较高时不叠加训练建议", "近期训练变化只压低负荷建议，仍保留低风险 Work 候选。", vec!["Health", "Work"], Some("若负荷继续上升，停止训练类候选。")),
                "pain" => ("出现疼痛线索时停止训练负荷建议", "疼痛反事实改变安全门；只给停止与专业评估提示。", vec!["Health"], Some("持续疼痛、无法负重或症状加重时，停止并寻求专业评估。")),
                "available_time" => ("可用时间较短时改为一个 10 分钟 Work 起步块", "可用时间变化改变排序和粒度，不引入新的健康判断。", vec!["Work"], None),
                _ => unreachable!(),
            };
            (
                None,
                vec![card(request_id, "primary", title, why, domains, refs.clone(), "这是固定合成反事实，不作真实个人因果推断。", stop_condition)],
                "同一合成 Work 情境只改变一个可解释变量；结果仍保持 Person-first、候选和可停止。".to_owned(),
            )
        },
        "missing_health" => (
            Some(Question {
                identity: "system_question".to_owned(),
                text: "是否存在持续疼痛或无法负重？".to_owned(),
                purpose: "仅用于判断是否应停止给出训练或恢复建议；不作诊断。".to_owned(),
            }),
            vec![card(
                request_id,
                "work-only",
                "完成一个 25 分钟 Work 聚焦块",
                "Health 证据不完整，因此仅保留不依赖 Health 的 Work 候选。",
                vec!["Work"],
                refs.clone(),
                "Health 证据缺失；未生成训练、治疗或诊断建议。",
                None,
            )],
            "缺失 Health 时先提出一条最小澄清问题，并停止健康行动建议。".to_owned(),
        ),
        "missing_health_skip" => (
            None,
            vec![card(
                request_id,
                "work-only-after-skip",
                "跳过 Health 澄清后，只保留一个 25 分钟 Work 聚焦块",
                "用户跳过关键问题后，Today 降级为不涉及训练负荷的 Work 候选。",
                vec!["Work"],
                refs.clone(),
                "Health 状态仍未知；未生成训练、治疗或诊断建议。",
                None,
            )],
            "问题可以跳过；跳过不会被解释为健康状态正常。".to_owned(),
        ),
        "health_stop" => (
            None,
            vec![ResultCard {
                result_id: format!("result:p3-140:{request_id}:safety-stop"),
                identity: "health_safety_stop".to_owned(),
                title: "先暂停训练类建议，必要时寻求专业帮助".to_owned(),
                why_today: "固定合成红旗条件触发了安全停止，而不是诊断或处方。".to_owned(),
                domains: vec!["Health".to_owned()],
                evidence_refs: refs.clone(),
                uncertainty: "这不是医疗诊断；只表达停止条件。".to_owned(),
                stop_condition: Some("持续疼痛、无法负重或症状加重时，不继续给训练建议。".to_owned()),
                feedback_options: vec!["confirm".to_owned(), "correct".to_owned()],
            }],
            "Health 安全停止不会夹带治疗建议，也不会把它写成事实。".to_owned(),
        ),
        "insufficient" => (
            None,
            Vec::new(),
            "暂无足够证据形成 Today 候选；没有用编造的建议填补空白。".to_owned(),
        ),
        _ if !health_included => (
            None,
            vec![card(
                request_id,
                "work-only",
                "完成一个 25 分钟 Work 聚焦块",
                "Health 已由本次请求移除，因此建议只使用 Work 与页面状态。",
                vec!["Work"],
                refs.clone(),
                "未使用 Health Context；不推断恢复状态。",
                None,
            )],
            "Health 从本次 Context 移除，不会改动任何持久事实。".to_owned(),
        ),
        _ => {
            let primary_title = if recomputed {
                "根据你的纠正，改为先完成一个更小的 Work 聚焦块"
            } else {
                "完成一个 25 分钟 Work 聚焦块"
            };
            (
                None,
                vec![
                    card(
                        request_id,
                        if recomputed { "recomputed" } else { "primary" },
                        primary_title,
                        "Work 负载与恢复线索同时出现，只提出低风险、可停止的推进候选。",
                        vec!["Work", "Health"],
                        refs.clone(),
                        "没有足够证据判断 Work 与疲劳的因果关系。",
                        Some("若出现不适或负荷上升，停止并改为休息或人工核对。"),
                    ),
                    card(
                        request_id,
                        "recovery-check",
                        "在开始前做一次低成本恢复自检",
                        "这是可选的自检，不是训练、治疗或医疗结论。",
                        vec!["Health", "Work"],
                        refs.clone(),
                        "Health 线索为固定合成证据，不能外推到真实个人状态。",
                        Some("若自检不适，停止此候选并不要自动替换为其他健康建议。"),
                    ),
                ],
                "跨域建议显示证据、限制和停止条件；它们全部仍是可反馈候选。".to_owned(),
            )
        }
    };
    TodayIntelligence {
        status: "ready".to_owned(),
        scenario: scenario.to_owned(),
        request_id: request_id.to_owned(),
        snapshot_generation: generation,
        cross_domain_limited: !health_included || matches!(scenario, "missing_health" | "missing_health_skip" | "insufficient"),
        counterfactual_case: counterfactual_case.map(str::to_owned),
        context_receipt_ref,
        question,
        results,
        explanation,
        disclosure_refs: refs,
        feedback: FeedbackState {
            decision: None,
            target_result_id: None,
            candidate_only: true,
        },
        recomputation: Recomputation {
            invalidated_refs: Vec::new(),
            recomputed_slices: Vec::new(),
            unaffected_slices_recomputed: false,
        },
        dispatch: DispatchBoundary {
            provider_dispatch_count: 0,
            model_dispatch_count: 0,
            network_dispatch_count: 0,
            external_tool_dispatch_count: 0,
        },
        durable_memory_promoted: false,
    }
}

fn cache(conn: &Connection, request_id: &str) -> Result<Option<TodayIntelligence>, Error> {
    let raw: Option<String> = conn
        .query_row(
            "SELECT response_json FROM p3140_runs WHERE request_id=?1 AND state='active'",
            params![request_id],
            |row| row.get(0),
        )
        .optional()
        .map_err(|_| rejected("database_unavailable", "Today 缓存不可验证；未显示成功。"))?;
    raw.map(|value| {
        serde_json::from_str(&value).map_err(|_| {
            rejected(
                "today_cache_rejected",
                "Today 缓存不符合固定响应合同；未显示成功。",
            )
        })
    })
    .transpose()
}

fn persist(
    conn: &mut Connection,
    response: &TodayIntelligence,
    scenario: &str,
    health_included: bool,
    feedback: Option<&TodayFeedback>,
    generation_before: i64,
) -> Result<(), Error> {
    let tx = conn
        .transaction_with_behavior(TransactionBehavior::Immediate)
        .map_err(|_| rejected("database_unavailable", "Today 写入事务不可用；未显示成功。"))?;
    let timestamp = now()?;
    if let Some(feedback) = feedback {
        let active: Option<i64> = tx
            .query_row(
                "SELECT 1 FROM p3140_results WHERE result_id=?1 AND state='candidate'",
                params![feedback.result_id],
                |row| row.get(0),
            )
            .optional()
            .map_err(|_| rejected("database_unavailable", "Today 反馈对象不可验证；未显示成功。"))?;
        if active.is_none() {
            return Err(rejected(
                "today_feedback_target_rejected",
                "反馈目标不存在、已失效或不是候选；未写入。",
            ));
        }
        tx.execute(
            "INSERT INTO p3140_feedback(idempotency_key,result_id,decision,detail,created_at_ms) VALUES(?1,?2,?3,?4,?5)",
            params![response.request_id, feedback.result_id, feedback.decision.value(), feedback.detail.as_deref().unwrap_or(""), timestamp],
        )
        .map_err(|_| rejected("today_feedback_rejected", "重复或无效的 Today 反馈未写入。"))?;
        tx.execute(
            "INSERT INTO p3140_audit(event,target_id,detail,created_at_ms) VALUES(?1,?2,?3,?4)",
            params![format!("feedback_{}", feedback.decision.value()), feedback.result_id, "candidate_only", timestamp],
        )
        .map_err(|_| rejected("database_unavailable", "Today 反馈审计未写入。"))?;
        if feedback.decision.invalidates() {
            tx.execute(
                "UPDATE p3140_results SET state='stale' WHERE result_id=?1",
                params![feedback.result_id],
            )
            .map_err(|_| rejected("database_unavailable", "旧 Today 候选无法失效；未显示成功。"))?;
            tx.execute(
                "UPDATE p3140_understandings SET state='stale' WHERE result_id=?1",
                params![feedback.result_id],
            )
            .map_err(|_| rejected("database_unavailable", "旧 Today 理解无法失效；未显示成功。"))?;
            tx.execute(
                "UPDATE p3140_runs SET state='superseded' WHERE request_id=(SELECT request_id FROM p3140_results WHERE result_id=?1)",
                params![feedback.result_id],
            )
            .map_err(|_| rejected("database_unavailable", "旧 Today 运行无法标记失效；未显示成功。"))?;
            tx.execute(
                "UPDATE p3140_state SET state_value=?1 WHERE state_key='generation'",
                params![response.snapshot_generation],
            )
            .map_err(|_| rejected("database_unavailable", "Today 代次无法更新；未显示成功。"))?;
        }
    }
    let encoded = serde_json::to_string(response)
        .map_err(|_| rejected("today_serialization_rejected", "Today 响应无法安全序列化；未写入。"))?;
    tx.execute(
        "INSERT INTO p3140_runs(request_id,scenario,health_included,generation,state,response_json,created_at_ms) VALUES(?1,?2,?3,?4,'active',?5,?6)",
        params![response.request_id, scenario, if health_included { 1i64 } else { 0i64 }, response.snapshot_generation, encoded, timestamp],
    )
    .map_err(|_| rejected("today_request_rejected", "Today 请求重复或不可写入。"))?;
    for result in &response.results {
        let refs = serde_json::to_string(&result.evidence_refs)
            .map_err(|_| rejected("today_serialization_rejected", "Today 证据引用无法序列化；未写入。"))?;
        tx.execute(
            "INSERT INTO p3140_results(result_id,request_id,state,evidence_refs_json) VALUES(?1,?2,'candidate',?3)",
            params![result.result_id, response.request_id, refs],
        )
        .map_err(|_| rejected("database_unavailable", "Today 候选无法写入；未显示成功。"))?;
        tx.execute(
            "INSERT INTO p3140_understandings(understanding_id,result_id,state,identity,promotion,generation) VALUES(?1,?2,'candidate','system_suggestion','none',?3)",
            params![format!("understanding:p3-140:{}", result.result_id), result.result_id, response.snapshot_generation],
        )
        .map_err(|_| rejected("database_unavailable", "Today 候选理解无法写入；未显示成功。"))?;
    }
    tx.execute(
        "INSERT INTO p3140_audit(event,target_id,detail,created_at_ms) VALUES('today_response',?1,?2,?3)",
        params![response.request_id, format!("generation_before={generation_before};candidate_only"), timestamp],
    )
    .map_err(|_| rejected("database_unavailable", "Today 审计无法写入；未显示成功。"))?;
    tx.commit()
        .map_err(|_| rejected("database_unavailable", "Today 写入事务无法提交；未显示成功。"))
}

pub(crate) fn respond(paths: &Paths, request: &TodayRequest) -> Result<TodayIntelligence, Error> {
    let (scenario, request_id, health_included, counterfactual_case) = validate_request(request)?;
    ensure_p3139_fixture(paths)?;
    let (cached, current_generation) = write(paths, |conn| {
        init(conn)?;
        let current_generation = generation(conn)?;
        if let Some(cached) = cache(conn, &request_id)? { return Ok((Some(cached), current_generation)); }
        if let Some(expected) = request.expected_generation {
            if expected != current_generation {
                return Err(rejected(
                    "today_generation_stale",
                    "Today 快照代次已过期；未写入。",
                ));
            }
        }
        if let Some(feedback) = &request.feedback {
            let active: Option<i64> = conn.query_row("SELECT 1 FROM p3140_results WHERE result_id=?1 AND state='candidate'", params![feedback.result_id], |row| row.get(0)).optional().map_err(|_| rejected("database_unavailable", "Today 反馈对象不可验证；未显示成功。"))?;
            if active.is_none() { return Err(rejected("today_feedback_target_rejected", "反馈目标不存在、已失效或不是候选；未写入。")); }
        }
        Ok((None, current_generation))
    })?;
    if let Some(cached) = cached { return Ok(cached); }
    let health_in_context = health_included && !matches!(scenario.as_str(), "missing_health" | "missing_health_skip" | "insufficient");
    let (refs, context_receipt_ref) = resolve_disclosure(paths, &request_id, health_in_context)?;
    write(paths, |conn| {
        init(conn)?;
        if generation(conn)? != current_generation { return Err(rejected("today_generation_stale", "Today 快照代次在 Context 组装期间变化；未写入。")); }
        let recomputed = request
            .feedback
            .as_ref()
            .is_some_and(|feedback| feedback.decision.invalidates());
        let next_generation = if recomputed {
            current_generation + 1
        } else {
            current_generation
        };
        let mut response = model(
            &scenario,
            &request_id,
            health_in_context,
            next_generation,
            recomputed,
            counterfactual_case.as_deref(),
            refs.clone(),
            context_receipt_ref.clone(),
        );
        if let Some(feedback) = &request.feedback {
            response.feedback = FeedbackState {
                decision: Some(feedback.decision.value().to_owned()),
                target_result_id: Some(feedback.result_id.clone()),
                candidate_only: true,
            };
            if feedback.decision.invalidates() {
                response.recomputation = Recomputation {
                    invalidated_refs: vec![feedback.result_id.clone()],
                    recomputed_slices: vec!["today_primary".to_owned()],
                    unaffected_slices_recomputed: false,
                };
            }
        }
        persist(
            conn,
            &response,
            &scenario,
            health_included,
            request.feedback.as_ref(),
            current_generation,
        )?;
        Ok(response)
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use super::super::{mode, paths, read, InputMode, Paths, DB};
    use std::fs;
    use std::sync::atomic::{AtomicUsize, Ordering};

    static TEST_SEQUENCE: AtomicUsize = AtomicUsize::new(0);

    fn test_paths(label: &str) -> Paths {
        let base = paths().unwrap().root;
        let sequence = TEST_SEQUENCE.fetch_add(1, Ordering::SeqCst);
        let root = base.join(format!("p3140-unit-{label}-{}-{sequence}", now().unwrap()));
        fs::create_dir(&root).unwrap();
        Paths { db: root.join(DB), root, mode: InputMode::Synthetic }
    }

    fn clean(paths: &Paths) {
        fs::remove_dir_all(&paths.root).unwrap();
    }

    fn request(id: &str, scenario: &str, health_included: bool) -> TodayRequest {
        TodayRequest {
            scenario: Some(scenario.to_owned()),
            counterfactual_case: None,
            request_id: Some(format!("p3-140:{id}")),
            health_included: Some(health_included),
            authorization: Some(
                if health_included { AUTH_CROSS_DOMAIN } else { AUTH_PERSON }.to_owned(),
            ),
            feedback: None,
            expected_generation: None,
            fault: None,
        }
    }

    fn counts(paths: &Paths) -> [i64; 5] {
        let connection = read(paths).unwrap();
        [
            "p3140_runs",
            "p3140_results",
            "p3140_feedback",
            "p3140_understandings",
            "p3140_audit",
        ]
        .map(|table| connection.query_row(&format!("SELECT count(*) FROM {table}"), [], |row| row.get(0)).unwrap())
    }

    #[test]
    fn fixed_scenarios_are_evidence_linked_and_have_no_dispatch() {
        for (index, scenario, health, expected_results, expected_question) in [
            (0, "normal", true, 2, false),
            (1, "counterfactual", true, 1, false),
            (2, "missing_health", true, 1, true),
            (3, "missing_health_skip", true, 1, false),
            (4, "health_stop", true, 1, false),
            (5, "insufficient", true, 0, false),
            (6, "normal", false, 1, false),
        ] {
            let paths = test_paths(&format!("scenario-{index}"));
            let response = respond(&paths, &request(&format!("scenario-{index}"), scenario, health)).unwrap();
            assert_eq!(response.results.len(), expected_results);
            assert_eq!(response.question.is_some(), expected_question);
            assert_eq!(response.dispatch.provider_dispatch_count, 0);
            assert_eq!(response.dispatch.model_dispatch_count, 0);
            assert_eq!(response.dispatch.network_dispatch_count, 0);
            assert!(!response.durable_memory_promoted);
            if scenario == "health_stop" {
                assert_eq!(response.results[0].identity, "health_safety_stop");
                assert!(response.results[0].stop_condition.is_some());
            }
            if !health || matches!(scenario, "missing_health" | "missing_health_skip" | "insufficient") {
                assert!(response.cross_domain_limited);
                assert!(!response.disclosure_refs.iter().any(|value| value.contains("health")));
            }
            clean(&paths);
        }
    }

    #[test]
    fn five_single_variable_counterfactuals_and_receipts_are_deterministic() {
        let mut titles = Vec::new();
        for case in ["long_term_constraint", "sleep_fatigue", "recent_training", "pain", "available_time"] {
            let paths = test_paths(case);
            let mut value = request(&format!("counterfactual-{case}"), "counterfactual", true);
            value.counterfactual_case = Some(case.to_owned());
            let response = respond(&paths, &value).unwrap();
            assert_eq!(response.counterfactual_case.as_deref(), Some(case));
            assert_eq!(response.results.len(), 1);
            titles.push(response.results[0].title.clone());
            let connection = read(&paths).unwrap();
            let receipt_refs = connection.prepare("SELECT reference FROM context_receipt_items WHERE request_id=?1 AND decision='included' ORDER BY ordinal").unwrap().query_map(params![response.context_receipt_ref], |row| row.get::<_, String>(0)).unwrap().collect::<Result<Vec<_>, _>>().unwrap();
            assert_eq!(response.disclosure_refs, receipt_refs);
            clean(&paths);
        }
        titles.sort();
        titles.dedup();
        assert_eq!(titles.len(), 5);
    }

    #[test]
    fn repeated_request_is_stable_and_feedback_invalidates_only_target_slice() {
        let paths = test_paths("repeat-feedback");
        let original_request = request("repeat", "normal", true);
        let original = respond(&paths, &original_request).unwrap();
        let repeated = respond(&paths, &original_request).unwrap();
        assert_eq!(serde_json::to_string(&original).unwrap(), serde_json::to_string(&repeated).unwrap());
        let before = counts(&paths);
        let target = original.results[0].result_id.clone();
        let feedback_request = TodayRequest {
            scenario: Some("normal".to_owned()),
            counterfactual_case: None,
            request_id: Some("p3-140:feedback-recompute".to_owned()),
            health_included: Some(true),
            authorization: Some(AUTH_CROSS_DOMAIN.to_owned()),
            feedback: Some(TodayFeedback { result_id: target.clone(), decision: FeedbackDecision::Correct, detail: Some("缩小范围".to_owned()) }),
            expected_generation: Some(original.snapshot_generation),
            fault: None,
        };
        let recomputed = respond(&paths, &feedback_request).unwrap();
        assert_eq!(recomputed.snapshot_generation, original.snapshot_generation + 1);
        assert_eq!(recomputed.recomputation.invalidated_refs, vec![target.clone()]);
        assert!(!recomputed.recomputation.unaffected_slices_recomputed);
        assert!(recomputed.results[0].title.contains("更小"));
        assert!(counts(&paths)[2] > before[2]);
        let connection = read(&paths).unwrap();
        let state: String = connection.query_row("SELECT state FROM p3140_results WHERE result_id=?1", params![target], |row| row.get(0)).unwrap();
        let promoted: i64 = connection.query_row("SELECT count(*) FROM p3140_understandings WHERE promotion <> 'none'", [], |row| row.get(0)).unwrap();
        assert_eq!(state, "stale");
        assert_eq!(promoted, 0);
        clean(&paths);
    }

    #[test]
    fn rejected_inputs_fail_closed_without_new_rows() {
        let paths = test_paths("fail-closed");
        let good = request("good", "normal", true);
        let initial = respond(&paths, &good).unwrap();
        let before = counts(&paths);
        let unauthorized = TodayRequest { authorization: Some("wrong".to_owned()), ..request("bad-auth", "normal", true) };
        assert_eq!(respond(&paths, &unauthorized).unwrap_err().code, "today_authorization_rejected");
        let stale = TodayRequest { expected_generation: Some(initial.snapshot_generation + 1), ..request("stale", "normal", true) };
        assert_eq!(respond(&paths, &stale).unwrap_err().code, "today_generation_stale");
        for (index, fault_name, expected) in [
            (0, "authorization_revoked", "today_authorization_rejected"),
            (1, "stale_generation", "today_generation_stale"),
            (2, "over_budget", "context_budget_rejected"),
            (3, "malformed", "today_request_rejected"),
            (4, "database_failure", "database_unavailable"),
            (5, "recompute_failure", "today_recompute_rejected"),
        ] {
            let fault = TodayRequest { fault: Some(fault_name.to_owned()), ..request(&format!("fault-{index}"), "normal", true) };
            assert_eq!(respond(&paths, &fault).unwrap_err().code, expected);
        }
        let revoked = TodayRequest {
            scenario: Some("normal".to_owned()), counterfactual_case: None, request_id: Some("p3-140:revoked-result".to_owned()), health_included: Some(true), authorization: Some(AUTH_CROSS_DOMAIN.to_owned()),
            feedback: Some(TodayFeedback { result_id: "result:p3-140:missing:primary".to_owned(), decision: FeedbackDecision::Reject, detail: None }), expected_generation: Some(initial.snapshot_generation), fault: None,
        };
        assert_eq!(respond(&paths, &revoked).unwrap_err().code, "today_feedback_target_rejected");
        assert_eq!(before, counts(&paths));
        clean(&paths);
    }

    #[test]
    fn all_feedback_decisions_stay_candidate_only() {
        for (index, decision) in [FeedbackDecision::Confirm, FeedbackDecision::Edit, FeedbackDecision::Reject, FeedbackDecision::Ignore, FeedbackDecision::Correct].into_iter().enumerate() {
            let paths = test_paths(&format!("feedback-{index}"));
            let original = respond(&paths, &request(&format!("feedback-base-{index}"), "normal", true)).unwrap();
            let target = original.results[if matches!(decision, FeedbackDecision::Correct) { 1 } else { 0 }].result_id.clone();
            let feedback = TodayRequest {
                scenario: Some("normal".to_owned()), counterfactual_case: None, request_id: Some(format!("p3-140:feedback-{index}")), health_included: Some(true), authorization: Some(AUTH_CROSS_DOMAIN.to_owned()),
                feedback: Some(TodayFeedback { result_id: target.clone(), decision, detail: (decision == FeedbackDecision::Edit).then(|| "保留为更小范围".to_owned()) }), expected_generation: Some(original.snapshot_generation), fault: None,
            };
            let output = respond(&paths, &feedback).unwrap();
            assert_eq!(output.feedback.decision.as_deref(), Some(decision.value()));
            let connection = read(&paths).unwrap();
            let promoted: i64 = connection.query_row("SELECT count(*) FROM p3140_understandings WHERE promotion <> 'none'", [], |row| row.get(0)).unwrap();
            let core: i64 = connection.query_row("SELECT count(*) FROM understandings", [], |row| row.get(0)).unwrap();
            assert_eq!(promoted, 0);
            assert_eq!(core, 0);
            if decision.invalidates() {
                let stale: String = connection.query_row("SELECT state FROM p3140_results WHERE result_id=?1", params![target], |row| row.get(0)).unwrap();
                assert_eq!(stale, "stale");
            }
            clean(&paths);
        }
    }

    #[test]
    fn synthetic_mode_is_required_by_this_test_contract() {
        assert!(mode().unwrap() == InputMode::Synthetic);
    }
}
