use super::*;
use contract::*;
/// Only public synthetic data. No file, URL, process, credential or network port.
pub(super) fn grants(c: &Connection) -> R<Value> {
    let key = "coord8:fixture-grants";
    if let Some(v) = get(c, "sources", key)? {
        return Ok(v);
    }
    if crate::runtime_root::is_real() {
        return Err(error("capability_unavailable"));
    }
    let v = json!({"revision":1,"generation":1,"read":true,"modelProcessing":true,"dataClass":"public_synthetic","contractRevision":"D0670","mode":crate::runtime_root::mode()});
    put(c, "sources", key, &v)?;
    Ok(v)
}
pub(super) fn validate_grant(c: &Connection, bound: &Value, model: bool) -> R<()> {
    if crate::runtime_root::is_real() {
        return Err(error("capability_unavailable"));
    }
    let current = grants(c)?;
    if current != *bound
        || current["read"] != true
        || current["dataClass"] != "public_synthetic"
        || current["contractRevision"] != "D0670"
        || current["mode"] != crate::runtime_root::mode()
    {
        return Err(error("source_not_authorized"));
    }
    if model && current["modelProcessing"] != true {
        return Err(error("model_processing_not_authorized"));
    }
    Ok(())
}
pub(super) fn run(t: &Value, q: &Value) -> R<Value> {
    if crate::runtime_root::is_real() {
        return Err(error("capability_unavailable"));
    }
    let cap = q["capabilityId"].as_str().unwrap_or("");
    arguments(cap, &q["arguments"], &q["neededFacts"])?;
    if t["capabilityTargets"]
        .get(q["targetRef"].as_str().unwrap_or(""))
        .is_none_or(|x| x != cap)
    {
        return Err(error("target_rejected"));
    }
    let at = now();
    let source = uid("source");
    let until = at
        + if cap == CAPABILITIES[2] {
            1800000
        } else {
            300000
        };
    let start = q["arguments"]["start"].as_i64().unwrap_or(at);
    let end = q["arguments"]["end"].as_i64().unwrap_or(until);
    let mut facts = vec![];
    let fact = |name: &str, value: Value| json!({"ref":uid("fact"),"name":name,"value":value,"sourceRef":source,"sourceVersion":1,"validFrom":start,"validUntil":until});
    let typed = match cap {
        "fixture.note.lookup.v1" => {
            let data = [
                ("公开合成设计笔记", "合成项目的评审地点是蓝色会议室。"),
                ("公开合成整理笔记", "合成资料建议先整理评审结论。"),
                ("公开合成阅读笔记", "合成阅读安排主题是资料检索。"),
            ];
            let needle = q["arguments"]["query"].as_str().unwrap();
            let limit = q["arguments"]["limit"].as_u64().unwrap() as usize;
            let matches=data.into_iter().filter(|(a,b)|needle.chars().any(|ch|ch.is_alphanumeric()&&(a.contains(ch)||b.contains(ch)))).take(limit).map(|(title,text)|json!({"ref":uid("note"),"title":title,"text":text,"version":1,"modifiedAt":at})).collect::<Vec<_>>();
            facts.push(fact(
                "matches",
                json!({"type":"number","value":matches.len()}),
            ));
            json!({"matches":matches})
        }
        "fixture.schedule.lookup.v1" => {
            let free = start / 3600000 % 2 == 0;
            let entries = if free {
                vec![]
            } else {
                vec![
                    json!({"ref":uid("entry"),"title":"公开合成评审会议","start":start,"end":end,"version":1}),
                ]
            };
            facts.push(fact("available", json!({"type":"boolean","value":free})));
            facts.push(fact(
                "entries",
                json!({"type":"number","value":entries.len()}),
            ));
            json!({"entries":entries,"available":free})
        }
        "fixture.forecast.lookup.v1" => {
            let rain = match start / 86400000 % 3 {
                0 => "yes",
                1 => "no",
                _ => "unknown",
            };
            facts.push(fact(
                "rainExpected",
                if rain == "unknown" {
                    json!({"type":"unknown"})
                } else {
                    json!({"type":"boolean","value":rain=="yes"})
                },
            ));
            json!({"windows":[{"ref":uid("window"),"start":start,"end":end,"rainExpected":rain}]})
        }
        _ => return Err(error("capability_unavailable")),
    };
    let mut result = json!({"queryId":q["queryId"],"capabilityId":cap,"capabilityVersion":1,"status":"ok","typedFacts":typed,"sourceRef":source,"sourceVersion":1,"observedAt":at,"fetchedAt":at,"validFrom":start,"validUntil":until,"timezone":"UTC","authorizationGeneration":t["fixtureGrant"]["generation"],"truncated":false,"facts":facts});
    if cap == CAPABILITIES[2] {
        result["issuedAt"] = json!(at)
    }
    if result.to_string().len() > 16384 {
        return Err(error("query_response_too_large"));
    }
    Ok(result)
}
fn result_contract(t: &Value) -> R<()> {
    let r = &t["queryResult"];
    let q = &t["queryDescriptor"];
    let cap = string(r, "capabilityId", 1, 80)?;
    fields(
        r,
        &[
            "queryId",
            "capabilityId",
            "capabilityVersion",
            "status",
            "typedFacts",
            "sourceRef",
            "sourceVersion",
            "observedAt",
            "fetchedAt",
            "validFrom",
            "validUntil",
            "timezone",
            "authorizationGeneration",
            "truncated",
            "facts",
        ],
        if cap == CAPABILITIES[2] {
            &["issuedAt"]
        } else {
            &[]
        },
    )?;
    if r.to_string().len() > 16384 {
        return Err(error("query_response_too_large"));
    }
    if r["queryId"] != q["queryId"]
        || r["capabilityId"] != q["capabilityId"]
        || r["capabilityVersion"] != 1
    {
        return Err(error("query_response_invalid"));
    }
    ident(r, "queryId")?;
    ident(r, "sourceRef")?;
    for name in ["observedAt", "fetchedAt", "validFrom", "validUntil"] {
        number(r, name, 0, MAX)?;
    }
    number(r, "sourceVersion", 1, MAX)?;
    number(r, "authorizationGeneration", 1, MAX)?;
    if r["observedAt"].as_u64().unwrap() > r["fetchedAt"].as_u64().unwrap()
        || r["fetchedAt"].as_i64().unwrap() > now()
    {
        return Err(error("query_result_stale"));
    }
    let mut refs = std::collections::HashSet::new();
    let mut expected = vec![];
    let typed = &r["typedFacts"];
    match cap.as_str() {
        "fixture.note.lookup.v1" => {
            fields(typed, &["matches"], &[])?;
            let matches = typed["matches"]
                .as_array()
                .filter(|a| {
                    a.len() <= q["arguments"]["limit"].as_u64().unwrap_or(0) as usize
                        && a.len() <= 3
                })
                .ok_or_else(|| error("query_response_invalid"))?;
            for m in matches {
                fields(m, &["ref", "title", "text", "version", "modifiedAt"], &[])?;
                if !refs.insert(ident(m, "ref")?) {
                    return Err(error("query_response_invalid"));
                }
                string(m, "title", 1, 200)?;
                string(m, "text", 1, 500)?;
                number(m, "version", 1, MAX)?;
                number(m, "modifiedAt", 0, MAX)?;
            }
            expected.push(("matches", json!({"type":"number","value":matches.len()})));
        }
        "fixture.schedule.lookup.v1" => {
            fields(typed, &["entries", "available"], &[])?;
            let available = typed["available"]
                .as_bool()
                .ok_or_else(|| error("query_response_invalid"))?;
            let entries = typed["entries"]
                .as_array()
                .filter(|a| a.len() <= 4)
                .ok_or_else(|| error("query_response_invalid"))?;
            for e in entries {
                fields(e, &["ref", "title", "start", "end", "version"], &[])?;
                if !refs.insert(ident(e, "ref")?) {
                    return Err(error("query_response_invalid"));
                }
                string(e, "title", 1, 200)?;
                number(e, "version", 1, MAX)?;
                let start = number(e, "start", 0, MAX)?;
                let end = number(e, "end", 0, MAX)?;
                if end <= start
                    || start < q["arguments"]["start"].as_u64().unwrap_or(MAX)
                    || end > q["arguments"]["end"].as_u64().unwrap_or(0)
                {
                    return Err(error("query_response_invalid"));
                }
            }
            if available != entries.is_empty() {
                return Err(error("query_response_invalid"));
            }
            expected.push(("available", json!({"type":"boolean","value":available})));
            expected.push(("entries", json!({"type":"number","value":entries.len()})));
        }
        "fixture.forecast.lookup.v1" => {
            fields(typed, &["windows"], &[])?;
            number(r, "issuedAt", 0, MAX)?;
            let windows = typed["windows"]
                .as_array()
                .filter(|a| !a.is_empty() && a.len() <= 4)
                .ok_or_else(|| error("query_response_invalid"))?;
            let mut covered = q["arguments"]["start"]
                .as_u64()
                .ok_or_else(|| error("query_response_invalid"))?;
            for w in windows {
                fields(w, &["ref", "start", "end", "rainExpected"], &[])?;
                if !refs.insert(ident(w, "ref")?) {
                    return Err(error("query_response_invalid"));
                }
                let start = number(w, "start", 0, MAX)?;
                let end = number(w, "end", 0, MAX)?;
                if start != covered || end <= start {
                    return Err(error("query_response_invalid"));
                }
                covered = end;
                let value = match w["rainExpected"].as_str() {
                    Some("yes") => json!({"type":"boolean","value":true}),
                    Some("no") => json!({"type":"boolean","value":false}),
                    Some("unknown") => json!({"type":"unknown"}),
                    _ => return Err(error("query_response_invalid")),
                };
                expected.push(("rainExpected", value));
            }
            if q["arguments"]["end"] != covered {
                return Err(error("query_response_invalid"));
            }
        }
        _ => return Err(error("capability_unavailable")),
    }
    let facts = r["facts"]
        .as_array()
        .filter(|a| a.len() == expected.len())
        .ok_or_else(|| error("query_response_invalid"))?;
    for (f, (name, value)) in facts.iter().zip(expected) {
        fields(
            f,
            &[
                "ref",
                "name",
                "value",
                "sourceRef",
                "sourceVersion",
                "validFrom",
                "validUntil",
            ],
            &[],
        )?;
        if !refs.insert(ident(f, "ref")?)
            || f["name"] != name
            || f["value"] != value
            || f["sourceRef"] != r["sourceRef"]
            || f["sourceVersion"] != r["sourceVersion"]
            || f["validFrom"] != r["validFrom"]
            || f["validUntil"] != r["validUntil"]
        {
            return Err(error("query_response_invalid"));
        }
    }
    Ok(())
}
pub(super) fn valid_result(t: &Value) -> R<()> {
    let r = &t["queryResult"];
    if r.is_null() || r["validUntil"].as_i64().unwrap_or(0) <= now() {
        return Err(error("query_result_stale"));
    }
    result_contract(t).map_err(|e| match e.code.as_str() {
        "query_response_too_large" | "query_result_stale" => e,
        _ => error("query_response_invalid"),
    })?;
    let cap = r["capabilityId"].as_str().unwrap_or("");
    let ttl = if cap == CAPABILITIES[2] {
        1800000
    } else {
        300000
    };
    if r["validUntil"].as_i64().unwrap() - r["fetchedAt"].as_i64().unwrap() != ttl {
        return Err(error("query_result_stale"));
    }
    if !CAPABILITIES.contains(&cap)
        || r["status"] != "ok"
        || r["truncated"] != false
        || r["timezone"] != "UTC"
        || r["validUntil"].as_i64().unwrap_or(0) <= now()
        || r["sourceVersion"] != 1
        || r["authorizationGeneration"] != t["fixtureGrant"]["generation"]
    {
        return Err(error("query_result_stale"));
    }
    if cap == CAPABILITIES[2] {
        let issued = r["issuedAt"]
            .as_i64()
            .ok_or_else(|| error("query_result_stale"))?;
        if issued > r["fetchedAt"].as_i64().unwrap_or(0) || now() - issued > 21600000 {
            return Err(error("query_result_stale"));
        }
    }
    Ok(())
}
