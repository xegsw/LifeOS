use super::*;
pub(super) const CAPABILITIES: [&str; 3] = [
    "fixture.note.lookup.v1",
    "fixture.schedule.lookup.v1",
    "fixture.forecast.lookup.v1",
];
pub(super) fn fields(v: &Value, required: &[&str], optional: &[&str]) -> R<()> {
    let o = v.as_object().ok_or_else(|| error("dto_rejected"))?;
    if !no_null(v)
        || required.iter().any(|k| !o.contains_key(*k))
        || o.keys()
            .any(|k| !required.contains(&k.as_str()) && !optional.contains(&k.as_str()))
    {
        return Err(error("dto_rejected"));
    }
    Ok(())
}
pub(super) fn string(v: &Value, k: &str, min: usize, max: usize) -> R<String> {
    let s = v[k].as_str().ok_or_else(|| error("dto_rejected"))?;
    let n = s.chars().count();
    if n < min || n > max || min > 0 && s.trim().is_empty() {
        return Err(error("dto_rejected"));
    }
    Ok(s.into())
}
pub(super) fn number(v: &Value, k: &str, min: u64, max: u64) -> R<u64> {
    v[k].as_u64()
        .filter(|n| *n >= min && *n <= max)
        .ok_or_else(|| error("dto_rejected"))
}
pub(super) fn ident(v: &Value, k: &str) -> R<String> {
    let s = string(v, k, 1, 120)?;
    id(&s)?;
    Ok(s)
}
pub(super) const MAX: u64 = 9007199254740991;
pub(super) fn references(v: &Value, max: usize) -> R<Vec<String>> {
    let a = v.as_array().ok_or_else(|| error("dto_rejected"))?;
    if a.len() > max {
        return Err(error("dto_rejected"));
    }
    let mut seen = std::collections::HashSet::new();
    a.iter()
        .map(|v| {
            let s = v.as_str().ok_or_else(|| error("dto_rejected"))?;
            id(s)?;
            if !seen.insert(s) {
                return Err(error("dto_rejected"));
            }
            Ok(s.into())
        })
        .collect()
}
pub(super) fn arguments(cap: &str, a: &Value, facts: &Value) -> R<()> {
    let names = references(facts, 4)?;
    if names.is_empty() {
        return Err(error("argument_rejected"));
    }
    match cap {
        "fixture.note.lookup.v1" => {
            fields(a, &["query", "limit"], &[])?;
            string(a, "query", 1, 100)?;
            number(a, "limit", 1, 3)?;
            if names != ["matches"] {
                return Err(error("argument_rejected"));
            }
        }
        "fixture.schedule.lookup.v1" | "fixture.forecast.lookup.v1" => {
            let forecast = cap == CAPABILITIES[2];
            fields(
                a,
                if forecast {
                    &["start", "end", "fields"]
                } else {
                    &["start", "end"]
                },
                &[],
            )?;
            let start = number(a, "start", 0, MAX)?;
            let end = number(a, "end", 0, MAX)?;
            if end <= start || end - start > if forecast { 172800000 } else { 604800000 } {
                return Err(error("argument_rejected"));
            }
            if forecast {
                if a["fields"] != json!(["rainExpected"]) || names != ["rainExpected"] {
                    return Err(error("argument_rejected"));
                }
            } else if names.iter().any(|s| s != "entries" && s != "available") {
                return Err(error("argument_rejected"));
            }
        }
        _ => return Err(error("capability_unavailable")),
    }
    Ok(())
}
pub(super) fn scalar(v: &Value) -> R<()> {
    let kind = string(v, "type", 1, 20)?;
    fields(
        v,
        if kind == "unknown" {
            &["type"]
        } else {
            &["type", "value"]
        },
        &[],
    )?;
    match kind.as_str() {
        "unknown" => (),
        "boolean" if v["value"].is_boolean() => (),
        "number" if v["value"].as_f64().is_some_and(f64::is_finite) => (),
        "text" => {
            string(v, "value", 1, 200)?;
        }
        _ => return Err(error("condition_basis_invalid")),
    }
    Ok(())
}
pub(super) fn evaluate(condition: &Value, facts: &Value) -> R<&'static str> {
    fields(condition, &["join", "atoms"], &[])?;
    let join = condition["join"].as_str().unwrap_or("");
    if !["all", "any"].contains(&join) {
        return Err(error("condition_basis_invalid"));
    }
    let atoms = condition["atoms"]
        .as_array()
        .filter(|a| !a.is_empty() && a.len() <= 4)
        .ok_or_else(|| error("condition_basis_invalid"))?;
    let mut values = vec![];
    for atom in atoms {
        fields(atom, &["factRef", "operator", "expected"], &[])?;
        let rf = ident(atom, "factRef")?;
        let fact = facts
            .as_array()
            .and_then(|a| a.iter().find(|f| f["ref"] == rf))
            .ok_or_else(|| error("condition_basis_invalid"))?;
        scalar(&atom["expected"])?;
        if atom["expected"]["type"] == "unknown" {
            return Err(error("condition_basis_invalid"));
        }
        let op = atom["operator"].as_str().unwrap_or("");
        if !["eq", "neq", "gt", "gte", "lt", "lte"].contains(&op) {
            return Err(error("condition_basis_invalid"));
        }
        let actual = &fact["value"];
        scalar(actual)?;
        if actual["type"] == "unknown" || fact["validUntil"].as_i64().unwrap_or(0) <= now() {
            values.push(None);
            continue;
        }
        if actual["type"] != atom["expected"]["type"] {
            return Err(error("condition_basis_invalid"));
        }
        let lhs = &actual["value"];
        let rhs = &atom["expected"]["value"];
        let result = match op {
            "eq" => lhs == rhs,
            "neq" => lhs != rhs,
            _ => {
                let l = lhs
                    .as_f64()
                    .ok_or_else(|| error("condition_basis_invalid"))?;
                let r = rhs
                    .as_f64()
                    .ok_or_else(|| error("condition_basis_invalid"))?;
                match op {
                    "gt" => l > r,
                    "gte" => l >= r,
                    "lt" => l < r,
                    _ => l <= r,
                }
            }
        };
        values.push(Some(result));
    }
    Ok(if join == "all" {
        if values.contains(&Some(false)) {
            "false"
        } else if values.iter().all(|v| *v == Some(true)) {
            "true"
        } else {
            "unknown"
        }
    } else if values.contains(&Some(true)) {
        "true"
    } else if values.iter().all(|v| *v == Some(false)) {
        "false"
    } else {
        "unknown"
    })
}
pub(super) fn spans(t: &Value, v: &Value) -> R<()> {
    let a = v
        .as_array()
        .filter(|a| !a.is_empty() && a.len() <= 4)
        .ok_or_else(|| error("operation_response_rejected"))?;
    let mut current = false;
    for x in a {
        fields(x, &["messageRef", "start", "end"], &[])?;
        let rf = ident(x, "messageRef")?;
        let msg = t["messageMap"]
            .get(&rf)
            .ok_or_else(|| error("operation_response_rejected"))?;
        let start = number(x, "start", 0, 1200)?;
        let end = number(x, "end", 1, 1200)?;
        if start >= end || end > msg["text"].as_str().unwrap_or("").chars().count() as u64 {
            return Err(error("operation_response_rejected"));
        }
        current |= rf == "current";
    }
    if !current {
        return Err(error("operation_response_rejected"));
    }
    Ok(())
}
pub(super) fn action(t: &Value, c: &Value) -> R<()> {
    let op = c["operation"].as_str().unwrap_or("");
    fields(
        c,
        match op {
            "create" => &["operation", "content", "evidenceSpans", "sourceRefs"],
            "adjust" => &[
                "operation",
                "targetRef",
                "expectedVersion",
                "content",
                "evidenceSpans",
                "sourceRefs",
            ],
            "complete" | "cancel" => {
                &["operation", "targetRef", "expectedVersion", "evidenceSpans"]
            }
            _ => return Err(error("operation_response_rejected")),
        },
        &[],
    )?;
    spans(t, &c["evidenceSpans"])?;
    if op == "create" || op == "adjust" {
        string(c, "content", 1, 500)?;
        for rf in references(&c["sourceRefs"], 5)? {
            if t["sourceMap"].get(&rf).is_none() && t["queryResult"]["sourceRef"] != rf {
                return Err(error("operation_response_rejected"));
            }
        }
    }
    if op != "create" {
        let rf = ident(c, "targetRef")?;
        let target = t["targetMap"]
            .get(&rf)
            .ok_or_else(|| error("target_rejected"))?;
        if target["version"] != c["expectedVersion"] || target["status"] != "planned" {
            return Err(error("action_version_conflict"));
        }
        number(c, "expectedVersion", 1, MAX)?;
    }
    Ok(())
}
pub(super) fn response(t: &Value, v: Value, phase: &str) -> R<Value> {
    fields(&v, &["schemaVersion", "answerText", "candidate"], &[])?;
    if v["schemaVersion"] != 8 {
        return Err(error("operation_response_rejected"));
    }
    string(&v, "answerText", 0, 2000)?;
    let c = &v["candidate"];
    match c["operation"].as_str().unwrap_or("") {
        "none" => fields(c, &["operation"], &[])?,
        "clarify" => {
            fields(c, &["operation", "question", "targetRefs", "intent"], &[])?;
            string(c, "question", 1, 200)?;
            if ![
                "create",
                "adjust",
                "complete",
                "cancel",
                "query",
                "conditional",
                "unknown",
            ]
            .contains(&c["intent"].as_str().unwrap_or(""))
            {
                return Err(error("operation_response_rejected"));
            }
            for r in references(&c["targetRefs"], 4)? {
                if t["targetMap"].get(&r).is_none() {
                    return Err(error("target_rejected"));
                }
            }
        }
        "query_need" => {
            if phase != "first" {
                return Err(error("query_limit"));
            }
            fields(
                c,
                &[
                    "operation",
                    "capabilityId",
                    "capabilityVersion",
                    "targetRef",
                    "arguments",
                    "neededFacts",
                ],
                &[],
            )?;
            let cap = string(c, "capabilityId", 1, 80)?;
            if c["capabilityVersion"] != 1
                || t["capabilityTargets"]
                    .get(c["targetRef"].as_str().unwrap_or(""))
                    .is_none_or(|v| v != &cap)
            {
                return Err(error("target_rejected"));
            }
            arguments(&cap, &c["arguments"], &c["neededFacts"])?;
        }
        "conditional_action" => {
            fields(
                c,
                &[
                    "operation",
                    "content",
                    "evidenceSpans",
                    "condition",
                    "intent",
                    "consequence",
                ],
                &["priorConditionRef", "expectedConditionVersion"],
            )?;
            string(c, "content", 1, 500)?;
            spans(t, &c["evidenceSpans"])?;
            fields(&c["intent"], &["kind", "evidenceSpans"], &[])?;
            if !["apply_if_true", "record_only"]
                .contains(&c["intent"]["kind"].as_str().unwrap_or(""))
            {
                return Err(error("operation_response_rejected"));
            }
            spans(t, &c["intent"]["evidenceSpans"])?;
            action(t, &c["consequence"])?;
            evaluate(&c["condition"], &t["queryResult"]["facts"])?;
            match (
                c.get("priorConditionRef"),
                c.get("expectedConditionVersion"),
            ) {
                (None, None) => (),
                (Some(r), Some(n)) => {
                    let prior = t["conditionMap"]
                        .get(r.as_str().unwrap_or(""))
                        .ok_or_else(|| error("condition_basis_invalid"))?;
                    if prior["version"] != *n {
                        return Err(error("revision_conflict"));
                    }
                }
                _ => return Err(error("dto_rejected")),
            }
        }
        _ => action(t, c)?,
    }
    Ok(v)
}
