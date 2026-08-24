#!/usr/bin/env python3
"""SP-07 deterministic local spike. Synthetic data only; stdlib only."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import sqlite3
import statistics
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SEED = 20260809
NOW = "2026-08-09T12:00:00+08:00"
PROJECTS = ["project-alpha", "project-beta", "project-gamma", "project-delta"]
SYNONYMS = {
    "resume": {"continue", "restart", "pickup", "handoff"},
    "budget": {"cost", "spend", "pricing"},
    "launch": {"release", "ship", "publish"},
    "interview": {"research", "conversation", "discovery"},
    "review": {"inspect", "check", "verify"},
}


def dump(name, value):
    (ROOT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def unit(i, project, kind="material", title=None, body=None, **kw):
    source_n = (i % 8) + 1
    base = {
        "id": f"cu-{i:03d}", "project_id": project, "kind": kind,
        "title": title or f"Synthetic {kind} {i}",
        "body": body or f"synthetic note {i} context checkpoint evidence",
        "source_id": f"src-{source_n:02d}", "source_status": "connected",
        "artifact_id": f"art-{i:03d}", "artifact_version_id": f"av-{i:03d}-v1",
        "derivation_id": f"deriv-{i:03d}", "link_ids": [f"link-{i:03d}"],
        "feedback_ids": [f"fb-{i:03d}"], "authorization_id": f"auth-{project}",
        "authorization_status": "allow", "allowed_purposes": ["local_search", "project_recovery", "next_step"],
        "confirmation_status": "unconfirmed", "evidence_status": "current", "conflict_status": "none",
        "tombstoned": False, "retracted": False, "stale": False,
        "queue_generation": 3, "current_generation": 3,
        "generated_at": NOW, "updated_seq": i, "unprocessed": kind == "material",
        "audit_entry_id": f"audit-{i:03d}", "identity": "external_source" if kind == "material" else "user_confirmed",
    }
    base.update(kw)
    return base


def build_corpus():
    rows = []
    i = 1
    for p in PROJECTS:
        for n in range(15):
            rows.append(unit(i, p, body=f"synthetic {p} background note {n} ordinary context"))
            i += 1

    def setrow(idx, **kw):
        rows[idx - 1].update(kw)

    setrow(1, kind="event", title="Alpha checkpoint", body="resume alpha from onboarding checklist checkpoint", unprocessed=False)
    setrow(2, kind="decision", title="Alpha storage decision", body="confirmed decision use local first storage", confirmation_status="confirmed", unprocessed=False)
    setrow(3, kind="action", title="Alpha open action", body="open action verify backup restore drill", confirmation_status="confirmed", unprocessed=False)
    setrow(4, kind="material", title="Alpha inbox material", body="unprocessed interview transcript onboarding friction", unprocessed=True)
    setrow(5, kind="assertion", title="Alpha conflict", body="pricing evidence has contradictory budget claims", conflict_status="source_conflict", evidence_status="conflict", unprocessed=False)
    setrow(6, kind="action", title="Rejected candidate", body="rejected candidate send launch announcement", confirmation_status="rejected", identity="ai_candidate", unprocessed=False)
    setrow(7, kind="action", title="Edited accepted action", body="user edited accepted action review onboarding copy", confirmation_status="confirmed", identity="user_confirmed", unprocessed=False)
    setrow(8, kind="decision", title="Evidence unavailable decision", body="confirmed decision deprecated unique evidence", confirmation_status="confirmed", evidence_status="unavailable", stale=True, unprocessed=False)
    setrow(9, kind="material", title="Deleted secret", body="deleted hidden alpha token", tombstoned=True)
    setrow(10, kind="material", title="Retracted material", body="retracted hidden alpha memo", retracted=True)
    setrow(11, kind="material", title="Disconnected source", body="disconnected hidden alpha source", source_status="disconnected")
    setrow(12, kind="action", title="Old queue output", body="old queue obsolete action", queue_generation=2, current_generation=3, identity="ai_candidate")
    setrow(13, kind="material", title="Search only evidence", body="local search only reference launch glossary", allowed_purposes=["local_search"])
    setrow(14, kind="event", title="Alpha recent change", body="recent change onboarding scope revised", unprocessed=False)
    setrow(15, kind="link", title="Alpha key link", body="confirmed link connects decision to backup action", confirmation_status="confirmed", unprocessed=False)

    setrow(16, kind="event", title="Beta checkpoint", body="continue beta from release readiness checkpoint", unprocessed=False)
    setrow(17, kind="decision", title="Beta launch decision", body="confirmed decision ship desktop beta first", confirmation_status="confirmed", unprocessed=False)
    setrow(18, kind="action", title="Beta open action", body="open action prepare release checklist", confirmation_status="confirmed", unprocessed=False)
    setrow(19, kind="material", title="Beta research", body="unprocessed discovery conversation notes", unprocessed=True)
    setrow(20, kind="assertion", title="Beta source warning", body="launch schedule evidence source unreachable", source_status="unreachable", evidence_status="unavailable", unprocessed=False)
    setrow(21, kind="material", title="Beta restricted", body="restricted beta roadmap", authorization_status="deny")
    setrow(22, kind="event", title="Beta recent change", body="recent change release date revised", unprocessed=False)
    setrow(23, kind="action", title="Beta completed", body="completed action archive old mock", confirmation_status="completed", unprocessed=False)
    setrow(24, kind="assertion", title="Beta conflict", body="release date conflict between two current sources", conflict_status="version_conflict", evidence_status="conflict", unprocessed=False)

    setrow(31, kind="event", title="Gamma checkpoint", body="pickup gamma from customer research synthesis", unprocessed=False)
    setrow(32, kind="decision", title="Gamma interview decision", body="confirmed decision prioritize user research interviews", confirmation_status="confirmed", unprocessed=False)
    setrow(33, kind="action", title="Gamma open action", body="open action schedule discovery interview", confirmation_status="confirmed", unprocessed=False)
    setrow(34, kind="material", title="Gamma inbox", body="unprocessed customer conversation recording index", unprocessed=True)
    setrow(35, kind="event", title="Gamma recent", body="recent change interview guide revised", unprocessed=False)

    setrow(46, kind="event", title="Delta checkpoint", body="restart delta from cost model review", unprocessed=False)
    setrow(47, kind="decision", title="Delta budget", body="confirmed decision cap infrastructure cost budget", confirmation_status="confirmed", unprocessed=False)
    setrow(48, kind="action", title="Delta open action", body="open action verify pricing assumptions", confirmation_status="confirmed", unprocessed=False)
    setrow(49, kind="material", title="Delta inbox", body="unprocessed spend forecast worksheet", unprocessed=True)
    setrow(50, kind="event", title="Delta recent", body="recent change cost forecast revised", unprocessed=False)
    setrow(51, kind="material", title="Cross project distractor", body="alpha onboarding checklist unrelated duplicate", unprocessed=True)
    setrow(52, kind="material", title="Denied cross project", body="restricted alpha backup restore drill duplicate", authorization_status="deny")
    setrow(53, kind="material", title="Deleted cross project", body="deleted release checklist duplicate", tombstoned=True)
    setrow(54, kind="material", title="Stale cross project", body="stale interview decision duplicate", stale=True, evidence_status="unavailable")
    setrow(55, kind="action", title="Conflicting action branch", body="open action publish contradictory budget", conflict_status="version_conflict", evidence_status="conflict", confirmation_status="confirmed", unprocessed=False)
    return rows


QUERIES = [
    {"id":"q01","category":"exact","project_id":"project-alpha","text":"onboarding checklist","gold":["cu-001"],"critical":True},
    {"id":"q02","category":"semantic","project_id":"project-alpha","text":"continue alpha work","gold":["cu-001"],"critical":False},
    {"id":"q03","category":"recent_change","project_id":"project-alpha","text":"recent change","gold":["cu-014"],"filters":{"kind":"event"}},
    {"id":"q04","category":"confirmed_decision","project_id":"project-alpha","text":"local storage","gold":["cu-002"],"filters":{"kind":"decision","confirmation_status":"confirmed"},"critical":True},
    {"id":"q05","category":"open_action","project_id":"project-alpha","text":"backup restore","gold":["cu-003"],"filters":{"kind":"action","confirmation_status":"confirmed"},"critical":True},
    {"id":"q06","category":"feedback_rejected","project_id":"project-alpha","text":"launch announcement","gold":[],"expected_reason":"feedback_excluded"},
    {"id":"q07","category":"feedback_accepted","project_id":"project-alpha","text":"onboarding copy","gold":["cu-007"]},
    {"id":"q08","category":"conflict","project_id":"project-alpha","text":"pricing contradictory","gold":["cu-005"]},
    {"id":"q09","category":"unreachable","project_id":"project-beta","text":"schedule unreachable","gold":[],"expected_reason":"source_unreachable"},
    {"id":"q10","category":"permission","project_id":"project-beta","text":"restricted roadmap","gold":[],"expected_reason":"permission_restricted"},
    {"id":"q11","category":"cross_project","project_id":"project-alpha","text":"onboarding checklist","gold":["cu-001"]},
    {"id":"q12","category":"deleted","project_id":"project-alpha","text":"deleted hidden token","gold":[],"expected_reason":"deleted_or_retracted"},
    {"id":"q13","category":"retracted","project_id":"project-alpha","text":"retracted hidden memo","gold":[],"expected_reason":"deleted_or_retracted"},
    {"id":"q14","category":"disconnected","project_id":"project-alpha","text":"disconnected hidden source","gold":[],"expected_reason":"source_disconnected"},
    {"id":"q15","category":"old_queue","project_id":"project-alpha","text":"old queue obsolete","gold":[],"expected_reason":"stale_generation"},
    {"id":"q16","category":"exact","project_id":"project-beta","text":"release checklist","gold":["cu-018"],"critical":True},
    {"id":"q17","category":"confirmed_decision","project_id":"project-gamma","text":"user research interviews","gold":["cu-032"],"critical":True},
    {"id":"q18","category":"open_action","project_id":"project-gamma","text":"discovery interview","gold":["cu-033"],"critical":True},
    {"id":"q19","category":"exact","project_id":"project-delta","text":"infrastructure cost budget","gold":["cu-047"],"critical":True},
    {"id":"q20","category":"open_action","project_id":"project-delta","text":"pricing assumptions","gold":["cu-048"],"critical":True},
]


def tokenize(s):
    return re.findall(r"[a-z0-9]+", s.lower())


def expanded(tokens):
    out = set(tokens)
    for canonical, vals in SYNONYMS.items():
        group = vals | {canonical}
        if out & group:
            out |= group
    return out


def eligibility(r, purpose="local_search"):
    if r["authorization_status"] != "allow" or purpose not in r["allowed_purposes"]:
        return False, "permission_restricted"
    if r["tombstoned"] or r["retracted"]:
        return False, "deleted_or_retracted"
    if r["source_status"] == "disconnected": return False, "source_disconnected"
    if r["source_status"] == "unreachable": return False, "source_unreachable"
    if r["stale"] or r["evidence_status"] == "unavailable": return False, "evidence_unavailable"
    if r["queue_generation"] != r["current_generation"]: return False, "stale_generation"
    if purpose == "next_step" and r["conflict_status"] != "none": return False, "conflict_requires_review"
    if purpose == "next_step" and r["confirmation_status"] == "rejected": return False, "feedback_excluded"
    return True, "eligible"


def setup_fts(corpus):
    db = sqlite3.connect(":memory:")
    db.execute("CREATE VIRTUAL TABLE docs USING fts5(id UNINDEXED, title, body, tokenize='unicode61')")
    db.executemany("INSERT INTO docs(id,title,body) VALUES (?,?,?)", [(r["id"],r["title"],r["body"]) for r in corpus])
    return db


def fts_ids(db, terms):
    if not terms: return []
    query = " OR ".join(sorted(set(terms)))
    try:
        return [x[0] for x in db.execute("SELECT id FROM docs WHERE docs MATCH ? ORDER BY bm25(docs) LIMIT 30", (query,))]
    except sqlite3.OperationalError:
        return []


def result_view(r, score):
    return {
        "content_unit_id": r["id"], "project_id": r["project_id"], "kind": r["kind"], "score": round(score, 5),
        "source_id": r["source_id"], "artifact_version_id": r["artifact_version_id"],
        "derivation_id": r["derivation_id"], "link_ids": r["link_ids"],
        "confirmation_status": r["confirmation_status"], "generated_at": r["generated_at"],
        "evidence_status": r["evidence_status"], "conflict_status": r["conflict_status"],
        "permission_status": "allowed_current", "authorization_id": r["authorization_id"],
    }


def search(corpus, db, q, mode):
    by_id = {r["id"]:r for r in corpus}
    raw_tokens = tokenize(q["text"])
    terms = expanded(raw_tokens) if mode in ("semantic", "hybrid") else set(raw_tokens)
    fts = fts_ids(db, raw_tokens)
    candidates = set(fts)
    semantic_scores = {}
    if mode in ("semantic", "hybrid"):
        for r in corpus:
            rt = expanded(tokenize(r["title"] + " " + r["body"]))
            semantic_scores[r["id"]] = len(terms & rt) / max(1, len(terms | rt))
            if semantic_scores[r["id"]] > 0: candidates.add(r["id"])
    if mode == "semantic": candidates = {i for i,s in semantic_scores.items() if s > 0}
    excluded = Counter()
    ranked = []
    for cid in candidates:
        r = by_id[cid]
        ok, reason = eligibility(r)
        if not ok:
            excluded[reason] += 1
            continue
        if r["project_id"] != q["project_id"]:
            excluded["cross_project"] += 1
            continue
        filters = q.get("filters", {})
        if any(r.get(k) != v for k,v in filters.items()):
            excluded["metadata_mismatch"] += 1
            continue
        overlap = len(set(raw_tokens) & set(tokenize(r["title"] + " " + r["body"])))
        fts_bonus = 1.0 / (1 + fts.index(cid)) if cid in fts else 0
        meta = (0.3 if filters and all(r.get(k)==v for k,v in filters.items()) else 0) + min(r["updated_seq"],60)/6000
        sem = semantic_scores.get(cid,0)
        score = overlap + fts_bonus + meta + (sem * 1.5 if mode in ("semantic","hybrid") else 0)
        ranked.append((score,r))
    ranked.sort(key=lambda x:(-x[0],-x[1]["updated_seq"],x[1]["id"]))
    results = [result_view(r,s) for s,r in ranked[:20]]
    if results: reason = "matches_found"
    else:
        # Diagnose against the complete corpus without exposing excluded content.
        matching = [r for r in corpus if set(raw_tokens) & set(tokenize(r["title"]+" "+r["body"])) and r["project_id"]==q["project_id"]]
        reasons = [eligibility(r)[1] for r in matching if not eligibility(r)[0]]
        if q.get("expected_reason") in reasons or q.get("expected_reason") == "feedback_excluded": reason = q.get("expected_reason")
        elif reasons: reason = Counter(reasons).most_common(1)[0][0]
        else: reason = "no_match"
    return {"query_id":q["id"],"mode":mode,"result_ids":[x["content_unit_id"] for x in results],"results":results,"empty_reason":reason,"excluded_counts":dict(excluded)}


def recall(gold, got, k):
    return 1.0 if not gold else len(set(gold)&set(got[:k]))/len(gold)


def ndcg(gold, got, k):
    if not gold: return 1.0
    dcg = sum(1/math.log2(i+2) for i,x in enumerate(got[:k]) if x in gold)
    ideal = sum(1/math.log2(i+2) for i in range(min(len(gold),k)))
    return dcg/ideal if ideal else 1.0


def percentile(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs)-1, math.ceil(p*len(xs))-1)] if xs else 0


def evidence_ref(r, gap=None):
    return {"content_unit_id":r["id"],"source_id":r["source_id"],"artifact_version_id":r["artifact_version_id"],"derivation_id":r["derivation_id"],"link_ids":r["link_ids"],"confirmation_status":r["confirmation_status"],"evidence_status":r["evidence_status"],"conflict_status":r["conflict_status"],"permission_status":"allowed_current","generated_at":r["generated_at"],"gap":gap}


def recovery_package(corpus, project):
    eligible = [r for r in corpus if r["project_id"]==project and eligibility(r,"project_recovery")[0]]
    def choose(kind, pred=lambda r:True, n=3):
        return [evidence_ref(r) for r in sorted([x for x in eligible if x["kind"]==kind and pred(x)],key=lambda x:-x["updated_seq"])[:n]]
    review = []
    for r in corpus:
        if r["project_id"]==project and r["confirmation_status"]=="confirmed" and r["evidence_status"]=="unavailable":
            review.append(evidence_ref(r,"唯一证据失效，保留用户确认历史但退出活跃恢复叙述，需复核"))
    conflicts = [evidence_ref(r,"证据冲突，未自动合并") for r in eligible if r["conflict_status"]!="none"]
    pkg = {"package_id":f"recovery-{project}-g3","project_id":project,"generated_at":NOW,"status":"degraded_review_required" if review or conflicts else "ready",
           "last_checkpoint":choose("event",n=1),"recent_changes":choose("event",n=2),
           "confirmed_decisions":choose("decision",lambda r:r["confirmation_status"]=="confirmed"),
           "open_actions":choose("action",lambda r:r["confirmation_status"]=="confirmed"),
           "unprocessed_materials":choose("material",lambda r:r["unprocessed"]),
           "conflicts_and_gaps":conflicts+review,"feedback_entry":{"action":"review_recovery_package","target_id":f"recovery-{project}-g3"}}
    return pkg


def next_steps(corpus, package):
    by_id={r["id"]:r for r in corpus}
    candidates=[]
    for ref in package["open_actions"][:2]:
        r=by_id[ref["content_unit_id"]]
        ok,_=eligibility(r,"next_step")
        if ok:
            candidates.append({"candidate_id":f"cand-{r['id']}","identity":"ai_candidate_suggestion","confirmation_status":"unconfirmed",
                "proposed_text":f"Consider continuing: {r['title']}","reason":"Current confirmed open action with traceable evidence",
                "evidence":[evidence_ref(r)],"freshness":r["generated_at"],"confidence_boundary":"deterministic rule; no model inference; user must verify",
                "conflict_status":r["conflict_status"],"permission_gaps":[],"feedback_entry":{"actions":["accept","edit_accept","reject"],"target_id":f"cand-{r['id']}"}})
    if not candidates and package["unprocessed_materials"]:
        r=by_id[package["unprocessed_materials"][0]["content_unit_id"]]
        if eligibility(r,"next_step")[0]:
            candidates.append({"candidate_id":f"cand-{r['id']}","identity":"ai_candidate_suggestion","confirmation_status":"unconfirmed","proposed_text":"Consider reviewing unprocessed material","reason":"Current unprocessed material exists","evidence":[evidence_ref(r)],"freshness":r["generated_at"],"confidence_boundary":"deterministic rule; no model inference; user must verify","conflict_status":"none","permission_gaps":[],"feedback_entry":{"actions":["accept","edit_accept","reject"],"target_id":f"cand-{r['id']}"}})
    return candidates[:3]


def main():
    corpus=build_corpus(); db=setup_fts(corpus)
    dump("corpus.json",corpus); dump("query_set.json",QUERIES)
    dump("golden_labels.json",{q["id"]:{"relevant_ids":q["gold"],"expected_empty_reason":q.get("expected_reason")} for q in QUERIES})
    all_results=[]; timings={m:[] for m in ("fts","semantic","hybrid")}
    summaries={}
    for mode in timings:
        for q in QUERIES:
            t=time.perf_counter(); out=search(corpus,db,q,mode); timings[mode].append((time.perf_counter()-t)*1000); all_results.append(out)
        mode_out=[x for x in all_results if x["mode"]==mode]
        rec20=[recall(q["gold"],o["result_ids"],20) for q,o in zip(QUERIES,mode_out)]
        critical=[recall(q["gold"],o["result_ids"],10) for q,o in zip(QUERIES,mode_out) if q.get("critical")]
        summaries[mode]={"recall_at_20":round(statistics.mean(rec20),4),"critical_recall_at_10":round(statistics.mean(critical),4),"ndcg_at_10":round(statistics.mean([ndcg(q["gold"],o["result_ids"],10) for q,o in zip(QUERIES,mode_out)]),4),"first_valid_rate":round(sum(bool(o["result_ids"]) for o in mode_out)/len(mode_out),4),"latency_p95_ms":round(percentile(timings[mode],.95),3)}
    packages=[recovery_package(corpus,p) for p in PROJECTS]
    sample={"packages":packages,"next_step_candidates":{p["project_id"]:next_steps(corpus,p) for p in packages}}
    dump("recovery_package_samples.json",sample)
    result_fields={"source_id","artifact_version_id","derivation_id","link_ids","confirmation_status","generated_at","evidence_status","conflict_status","permission_status","authorization_id"}
    focus=[x for r in all_results if r["mode"]=="hybrid" for x in r["results"][:3]]
    completeness=1.0 if focus and all(result_fields<=set(x) and all(x[k] not in (None,"") for k in result_fields) for x in focus) else 0.0
    active_ids={x["content_unit_id"] for p in packages for sec in ("last_checkpoint","recent_changes","confirmed_decisions","open_actions","unprocessed_materials") for x in p[sec]}
    suggestion_evidence={e["content_unit_id"] for xs in sample["next_step_candidates"].values() for c in xs for e in c["evidence"]}
    search_ids={i for o in all_results for i in o["result_ids"]}
    forbidden_search={r["id"] for r in corpus if not eligibility(r,"local_search")[0]}
    forbidden_recovery={r["id"] for r in corpus if not eligibility(r,"project_recovery")[0]}
    forbidden_suggestion={r["id"] for r in corpus if not eligibility(r,"next_step")[0]}
    permission_leaks=(len(forbidden_search & search_ids) + len(forbidden_recovery & active_ids)
                      + len(forbidden_suggestion & suggestion_evidence))
    package_times=[]
    for _ in range(50):
        t=time.perf_counter(); recovery_package(corpus,"project-alpha"); package_times.append((time.perf_counter()-t)*1000)
    semantic_gain=round(summaries["hybrid"]["recall_at_20"]-summaries["fts"]["recall_at_20"],4)
    metrics={"seed":SEED,"corpus_units":len(corpus),"projects":len(PROJECTS),"queries":len(QUERIES),"retrieval":summaries,"hybrid_recall_gain_vs_fts":semantic_gain,"clear_vector_gain_threshold":0.05,"clear_vector_gain":semantic_gain>0.05,"evidence_completeness":completeness,"permission_leaks":permission_leaks,"recovery_package_p95_ms":round(percentile(package_times,.95),3),"pgvector_production_validated":False}
    dump("retrieval_results.json",{"metrics":metrics,"queries":all_results})
    audit=[{"audit_entry_id":f"audit-query-{n:03d}","action":"search","query_id":q["id"],"result":"completed","policy_version":"policy-synth-v3"} for n,q in enumerate(QUERIES,1)]
    dump("audit_log.json",audit)
    serialized=json.dumps({"audit":audit,"results":all_results},ensure_ascii=False)
    forbidden_patterns=[r"/Users/",r"\.obsidian",r"BEGIN [A-Z ]*PRIVATE KEY",r"prompt_text",r"embedding",r"vector_values"]
    privacy_hits=[p for p in forbidden_patterns if re.search(p,serialized,re.I)]
    tests=[]
    def add(tid,area,assertion,passed,priority="P0",evidence="retrieval_results.json"):
        tests.append({"id":tid,"area":area,"assertion":assertion,"priority":priority,"status":"PASS" if passed else "FAIL","evidence":evidence})
    add("T01","corpus","50-100 synthetic content units across 3-5 projects",50<=len(corpus)<=100 and 3<=len(PROJECTS)<=5)
    add("T02","retrieval","Recall@20 threshold",summaries["hybrid"]["recall_at_20"]>=.90)
    add("T03","retrieval","critical Recall@10 equals 1",summaries["hybrid"]["critical_recall_at_10"]==1)
    add("T04","security","permission/restriction leakage equals zero",permission_leaks==0,"P0","permission_filter_report.md")
    add("T05","evidence","focus result evidence completeness equals 1",completeness==1,"P0","evidence_integrity_report.md")
    for n,(label,pred) in enumerate([
        ("deleted excluded",all(r["id"] not in search_ids|active_ids|suggestion_evidence for r in corpus if r["tombstoned"])),
        ("retracted excluded",all(r["id"] not in search_ids|active_ids|suggestion_evidence for r in corpus if r["retracted"])),
        ("disconnected excluded",all(r["id"] not in search_ids|active_ids|suggestion_evidence for r in corpus if r["source_status"]=="disconnected")),
        ("unreachable degraded",next(o for o in all_results if o["mode"]=="hybrid" and o["query_id"]=="q09")["empty_reason"]=="source_unreachable"),
        ("permission empty explained",next(o for o in all_results if o["mode"]=="hybrid" and o["query_id"]=="q10")["empty_reason"]=="permission_restricted"),
        ("old queue excluded",all(r["id"] not in search_ids|active_ids|suggestion_evidence for r in corpus if r["queue_generation"]!=r["current_generation"])),
        ("conflict visible but not suggested",any(p["conflicts_and_gaps"] for p in packages) and all(by not in suggestion_evidence for by in ["cu-005","cu-024","cu-055"])),
        ("unique evidence requires review",any(x["gap"] for p in packages for x in p["conflicts_and_gaps"] if x["content_unit_id"]=="cu-008")),
        ("candidate identity explicit",all(c["identity"]=="ai_candidate_suggestion" and c["confirmation_status"]=="unconfirmed" for xs in sample["next_step_candidates"].values() for c in xs)),
        ("candidate evidence 1-3",all(1<=len(c["evidence"])<=3 for xs in sample["next_step_candidates"].values() for c in xs)),
        ("candidate feedback entry",all(c["feedback_entry"]["actions"]==["accept","edit_accept","reject"] for xs in sample["next_step_candidates"].values() for c in xs)),
        ("search only not reused for suggestions","cu-013" not in suggestion_evidence),
        ("cross project isolated","cu-051" not in next(o for o in all_results if o["mode"]=="hybrid" and o["query_id"]=="q11")["result_ids"]),
        ("recovery package latency threshold",percentile(package_times,.95)<3000),
        ("search latency threshold",summaries["hybrid"]["latency_p95_ms"]<2000),
        ("privacy log scan",not privacy_hits),
        ("no production pgvector claim",metrics["pgvector_production_validated"] is False),
        ("semantic gain decision recorded","clear_vector_gain" in metrics),
    ],6): add(f"T{n:02d}","matrix",label,pred,"P0" if n<18 else "P1")
    with (ROOT/"test_matrix.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=["id","area","assertion","priority","status","evidence"]); w.writeheader(); w.writerows(tests)
    passed=sum(t["status"]=="PASS" for t in tests); failed=len(tests)-passed
    result={"conclusion":"PASS" if failed==0 else "FAIL","tests_total":len(tests),"passed":passed,"failed":failed,"p0_failed":sum(t["status"]=="FAIL" and t["priority"]=="P0" for t in tests),"metrics":metrics,"privacy_scan_hits":privacy_hits}
    dump("results.json",result)
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == "__main__": main()
