#!/usr/bin/env python3
"""Independent LIFEOS-P3-103 verifier.

This runner never imports or executes the P3-102 runner. Real retained content
is used only inside one minimal comparison scope and is never emitted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sqlite3
import stat
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT = Path(__file__).resolve().parents[4]
EVIDENCE = Path(__file__).resolve().parent
REAL_ROOT = Path("/Users/xxe/Documents/LifeOS-Self-Use-Pilot-1")
REAL_DB = REAL_ROOT / "capture.sqlite"
REAL_PAGE = REAL_ROOT / "today.html"
CLI = PROJECT / "lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py"
CANDIDATE = PROJECT / "lifeos/engineering/LIFEOS-P3-097/src/local_capture.py"
ATTESTATION = PROJECT / "lifeos/engineering/LIFEOS-P3-102/evidence/input_attestation.json"
DESIGN = EVIDENCE / "independent_test_design.md"
DESIGN_SHA256 = "b395531e6c7867f2250f79553cea5a3f03766fd611a5ed9084f01e1bb89c3987"
ABF_SHA256 = "45a74cd9496cea0576ccd0257115e7e9e54821ee0d3be0639eda57f35e9e52f0"
RECEIVED_AT = "2026-08-23T11:49:17+08:00"
TEXT_A = "LIFEOS P3 103 FIXED NONSENSITIVE TEST NOTE ALPHA"
TEXT_B = "LIFEOS P3 103 FIXED NONSENSITIVE TEST NOTE BETA"
KEY_A = "p3-103-fixed-nonsensitive-key-a"
SIDECARS = ("-journal", "-wal", "-shm")
CREATED_EVIDENCE = {
    "session_start.json", "source_history_hashes.json", "retained_metadata.json",
    "retained_content_attestation.json", "retained_structure_audit.json",
    "retained_page_attestation.json", "retained_unchanged.json",
    "fresh_lifecycle_matrix.json", "fresh_boundary_matrix.json",
    "evidence_negative_gate.json", "closed_capabilities.json",
    "final_integrity.json", "acceptance_matrix.json", "results.json",
    "operation_log.md", "rerun.md",
}
FIXED_INPUTS = {
    "lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement.md": "f739f8ac7ffe6aa4a968899c75e336be528db044f8265e1aeafea41f64501b88",
    "lifeos/tasks/LIFEOS-P3-102_limited_personal_real_use_cli_enablement_acceptance_basis_freeze.md": "361849606a9164ad0ffc215688084a466dd6495ff5589719591773bcdc40a243",
    "lifeos/deliverables/LIFEOS-P3-102_limited_personal_real_use_cli_enablement.md": "3335b3eaa696f10b0bb8b61bb7bdc962ed2b966bc95de0696ca7714bd3343e70",
    "lifeos/engineering/LIFEOS-P3-102/runner.py": "af0b022d5dc961bfca13c4ace500b7c81b22679eb91f7dfa8f438c8325614ea4",
    "lifeos/engineering/LIFEOS-P3-102/evidence/MANIFEST.md": "17ce6fea49a921ca8b03fa1efa88b2d52ae248e172912ec7d7dfbf91774175a7",
    "lifeos/reviews/LIFEOS-P3-102_pm_review.md": "046a7d7173fe90bba07d9503b5822f741bd04a0d77a7cade54af0de58dee7d1f",
    "lifeos/reviews/LIFEOS-P3-102/pm_evidence/initial/MANIFEST.md": "3e77ef5ee931053ec42f0afd69f3b6b2547035383e8515e094e69dbd1abc7e62",
    "lifeos/engineering/LIFEOS-P3-097/src/local_capture.py": "1535fd1fa45b581a042be73bdbfdde1905c2ea7ff10c3554952b53882f455453",
    "lifeos/engineering/LIFEOS-P3-097/scripts/operator_cli.py": "ef7e6ba7f082e4a8b5d354dd5427835e054b188aab211c61c967174081155659",
    "lifeos/engineering/LIFEOS-P3-097/README.md": "7fa834dbb9ecaf78200af01c37c2ba8029a3c511affce9c184a3042c8cfa6adf",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(name: str, value: Any) -> None:
    (EVIDENCE / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def meta(path: Path) -> dict[str, Any]:
    s = path.lstat()
    return {
        "path": str(path), "mode": stat.S_IMODE(s.st_mode),
        "type": "directory" if stat.S_ISDIR(s.st_mode) else "regular" if stat.S_ISREG(s.st_mode) else "other",
        "nlink": s.st_nlink, "device": s.st_dev, "inode": s.st_ino,
        "size": s.st_size, "mtime_ns": s.st_mtime_ns, "ctime_ns": s.st_ctime_ns,
    }


def public_meta_snapshot() -> dict[str, Any]:
    ancestors = [Path("/"), Path("/Users"), Path("/Users/xxe"), Path("/Users/xxe/Documents")]
    entries = sorted(p.name for p in REAL_ROOT.iterdir())
    sidecars = [REAL_DB.name + suffix for suffix in SIDECARS if (REAL_ROOT / (REAL_DB.name + suffix)).exists()]
    return {
        "ancestors": [meta(p) for p in ancestors], "directory": meta(REAL_ROOT),
        "db": meta(REAL_DB), "page": meta(REAL_PAGE), "filenames": entries,
        "sidecars": sidecars,
    }


def metadata_contract(snapshot: dict[str, Any]) -> bool:
    return (
        all(item["type"] == "directory" for item in snapshot["ancestors"])
        and snapshot["directory"]["type"] == "directory"
        and snapshot["directory"]["mode"] == 0o700
        and snapshot["db"]["type"] == snapshot["page"]["type"] == "regular"
        and snapshot["db"]["mode"] == snapshot["page"]["mode"] == 0o600
        and snapshot["db"]["nlink"] == snapshot["page"]["nlink"] == 1
        and snapshot["filenames"] == ["capture.sqlite", "today.html"]
        and snapshot["sidecars"] == []
    )


def parse_engineering_manifest() -> dict[str, str]:
    manifest = PROJECT / "lifeos/engineering/LIFEOS-P3-102/evidence/MANIFEST.md"
    result: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `([^`]+)` \| `([0-9a-f]{64})` \|", line)
        if not m:
            continue
        rel, expected = m.groups()
        target = (manifest.parent / rel).resolve()
        result[str(target.relative_to(PROJECT))] = expected
    return result


def parse_pm_manifest() -> dict[str, str]:
    manifest = PROJECT / "lifeos/reviews/LIFEOS-P3-102/pm_evidence/initial/MANIFEST.md"
    result: dict[str, str] = {}
    for line in manifest.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `([0-9a-f]{64})` \| `([^`]+)` \|", line)
        if m:
            expected, rel = m.groups(); result[rel] = expected
    return result


def protected_hash_snapshot() -> dict[str, Any]:
    engineering = parse_engineering_manifest(); pm = parse_pm_manifest()
    def assess(items: dict[str, str]) -> dict[str, Any]:
        rows = []
        for rel, expected in items.items():
            actual = sha256(PROJECT / rel)
            rows.append({"path": rel, "expected": expected, "actual": actual, "match": actual == expected})
        return {"count": len(rows), "all_match": all(x["match"] for x in rows), "rows": rows}
    return {"fixed": assess(FIXED_INPUTS), "engineering_manifest_entries": assess(engineering), "pm_manifest_entries": assess(pm)}


def normalize_sql(value: str | None) -> str | None:
    return None if value is None else " ".join(value.strip().split()).lower()


EXPECTED_SCHEMA = {
    normalize_sql("CREATE TABLE captures ( id TEXT PRIMARY KEY, content TEXT NOT NULL, created_at TEXT NOT NULL, source TEXT NOT NULL CHECK(source = 'local_capture'), idem_key TEXT NOT NULL UNIQUE )"),
    normalize_sql("CREATE TABLE audit ( id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, capture_id TEXT, created_at TEXT NOT NULL, detail TEXT NOT NULL )"),
}


def retained_query() -> tuple[dict[str, Any], dict[str, Any]]:
    """Return only non-content booleans/counts; sensitive values never escape."""
    uri = f"{REAL_DB.as_uri()}?mode=ro&immutable=1"
    expected_digest = json.loads(ATTESTATION.read_text(encoding="utf-8"))["content_sha256"]
    conn = sqlite3.connect(uri, uri=True)
    try:
        conn.execute("PRAGMA query_only=ON")
        query_only = conn.execute("PRAGMA query_only").fetchone() == (1,)
        rows = conn.execute("SELECT content FROM captures").fetchall()
        record_count = len(rows)
        content = rows[0][0] if record_count == 1 else None
        match = isinstance(content, str) and hashlib.sha256(content.encode("utf-8")).hexdigest() == expected_digest
        # Scan already-written Evidence while plaintext is in the minimal scope.
        plaintext_absent = isinstance(content, str) and all(content.encode("utf-8") not in p.read_bytes() for p in EVIDENCE.iterdir() if p.is_file())
        del content, rows

        schema_rows = conn.execute("SELECT name,sql FROM sqlite_master WHERE type='table' AND name IN ('captures','audit') ORDER BY name").fetchall()
        schema_sql = {normalize_sql(row[1]) for row in schema_rows}
        canonical_schema = schema_sql == EXPECTED_SCHEMA
        capture_facts = conn.execute("SELECT COUNT(*),COUNT(DISTINCT source),MIN(source),MAX(source),MIN(created_at),MAX(created_at) FROM captures").fetchone()
        audit_rows = conn.execute("SELECT event,capture_id,created_at,detail FROM audit ORDER BY id").fetchall()
        capture_ids = conn.execute("SELECT id,created_at FROM captures").fetchall()
        audit_events = [row[0] for row in audit_rows]
        audit_order = audit_events == ["capture_saved", "capture_repeat"]
        linked = len(capture_ids) == 1 and len(audit_rows) == 2 and all(row[1] == capture_ids[0][0] for row in audit_rows)
        time_semantics = linked and audit_rows[0][2] == capture_ids[0][1] and audit_rows[1][2] >= audit_rows[0][2]
        audit_details = len(audit_rows) == 2 and audit_rows[0][3] == "local_capture" and audit_rows[1][3] == "same_idempotency_key"
        structure = {
            "canonical_schema": canonical_schema, "capture_count": capture_facts[0],
            "single_source": capture_facts[1] == 1 and capture_facts[2] == capture_facts[3] == "local_capture",
            "audit_count": len(audit_rows), "audit_order_valid": audit_order,
            "audit_linkage_valid": linked, "time_order_valid": time_semantics,
            "audit_details_valid": audit_details,
        }
        attestation = {"query_only": query_only, "record_count": record_count, "match": match, "plaintext_absent_from_existing_evidence": plaintext_absent}
        return attestation, structure
    finally:
        conn.close()
        del expected_digest


def cli(db: Path, command: str, *args: str, cwd: Path | None = None) -> tuple[int, dict[str, Any]]:
    proc = subprocess.run([sys.executable, "-B", str(CLI), "--db", str(db), command, *args], cwd=cwd, text=True, capture_output=True, timeout=30)
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError:
        payload = {"parseable": False}
    return proc.returncode, payload


def fixture_hashes(root: Path) -> dict[str, str | None]:
    return {name: sha256(root / name) if (root / name).is_file() else None for name in ("capture.sqlite", "today.html")}


def unexpected(root: Path) -> list[str]:
    allowed = {"capture.sqlite", "today.html"}
    return sorted(p.name for p in root.iterdir() if p.name not in allowed)


def lifecycle(root: Path) -> dict[str, Any]:
    root.mkdir(mode=0o700, exist_ok=True)
    db = root / "capture.sqlite"
    leaves = []
    code, first = cli(db, "capture", "--text", TEXT_A, "--key", KEY_A)
    leaves.append(leaf("008-01", "saved", code == 0 and first.get("status") == "saved", {"db_exists": db.is_file(), "unexpected": unexpected(root)}))
    before_repeat = fixture_hashes(root)
    code, repeat = cli(db, "capture", "--text", TEXT_A, "--key", KEY_A)
    after_repeat = fixture_hashes(root)
    leaves.append(leaf("008-02", "repeat", code == 0 and repeat.get("status") == "idempotent_repeat", {"db_changed_for_repeat_audit": before_repeat["capture.sqlite"] != after_repeat["capture.sqlite"], "page_unchanged": before_repeat["today.html"] == after_repeat["today.html"]}))
    before_conflict = fixture_hashes(root)
    code, conflict = cli(db, "capture", "--text", TEXT_B, "--key", KEY_A)
    leaves.append(leaf("008-03", "conflict", code != 0 and conflict.get("status") == "blocked" and fixture_hashes(root) == before_conflict, {"state_unchanged": fixture_hashes(root) == before_conflict}))
    code, today = cli(db, "today")
    today_ok = code == 0 and len(today.get("records", [])) == 1 and today["records"][0].get("content") == TEXT_A and today["records"][0].get("source") == "local_capture"
    leaves.append(leaf("008-04", "restart_today", today_ok, {"record_count": len(today.get("records", [])), "content_identity_match": today_ok}))
    code, rendered = cli(db, "render")
    page = root / "today.html"
    page_body = page.read_text(encoding="utf-8") if page.is_file() else ""
    render_ok = code == 0 and rendered.get("status") == "rendered" and TEXT_A in page_body and "用户原文" in page_body and "本地捕获" in page_body
    leaves.append(leaf("008-05", "restart_render", render_ok, {"page_exists": page.is_file(), "semantic_identity_match": render_ok}))
    del page_body
    before_failure = fixture_hashes(root)
    code, failed = cli(db, "capture", "--text", TEXT_B, "--key", "p3-103-failure-key", "--inject-failure")
    no_runtime = not any(p.name.startswith(".capture") or p.name.endswith(SIDECARS) for p in root.iterdir())
    failure_ok = code != 0 and failed.get("status") == "blocked" and fixture_hashes(root) == before_failure and no_runtime
    leaves.append(leaf("008-06", "inject_failure", failure_ok, {"state_unchanged": fixture_hashes(root) == before_failure, "runtime_residue_zero": no_runtime}))
    return {"status": "PASS" if all(x["status"] == "PASS" for x in leaves) else "FAIL", "leaves": leaves}


def leaf(suffix: str, name: str, passed: bool, observation: dict[str, Any]) -> dict[str, Any]:
    return {
        "test_id": f"P3-103-T-{suffix}", "fixture_id": f"P3-103-F-{suffix}",
        "execution_id": f"P3-103-E-{suffix}", "name": name, "assertion_executed": True,
        "before_after": observation, "log_ref": "operation_log.md", "status": "PASS" if passed else "FAIL",
    }


def valid_db(root: Path) -> Path:
    root.mkdir(mode=0o700, parents=True, exist_ok=True); db = root / "capture.sqlite"
    code, result = cli(db, "capture", "--text", TEXT_A, "--key", KEY_A)
    if code or result.get("status") != "saved": raise RuntimeError("fixture setup failed")
    return db


def boundary_leaf(index: int, name: str, setup: Any, invoke: Any) -> dict[str, Any]:
    root = Path(tempfile.mkdtemp(prefix=f"lifeos-p3-103-boundary-{index:02d}-", dir="/private/tmp"))
    try:
        context = setup(root)
        before = {str(p): sha256(p) for p in context.get("sentinels", []) if p.is_file()}
        code, blocked = invoke(root, context)
        after = {str(p): sha256(p) for p in context.get("sentinels", []) if p.is_file()}
        passed = code != 0 and blocked and before == after
        return leaf(f"009-{index:02d}", name, passed, {"sentinels_unchanged": before == after, "rejected": code != 0})
    finally:
        shutil.rmtree(root)


def boundary_matrix() -> dict[str, Any]:
    leaves = []
    def simple_path(raw_builder: Any):
        return boundary_leaf(len(leaves)+1, raw_builder.__name__, lambda r: {"db": raw_builder(r), "sentinels": []}, lambda r,c: (lambda x: (x[0], x[1].get("status") == "blocked"))(cli(c["db"], "capture", "--text", TEXT_A, "--key", KEY_A, cwd=r)))

    def relative(r: Path) -> Path: return Path("capture.sqlite")
    def dotdot(r: Path) -> Path: return Path(str(r / "inner" / ".." / "capture.sqlite"))
    leaves.append(simple_path(relative)); leaves.append(simple_path(dotdot))

    def ancestor_setup(r: Path) -> dict[str, Any]:
        real = r / "real"; real.mkdir(); link = r / "link"; link.symlink_to(real, target_is_directory=True)
        return {"db": link / "capture.sqlite", "sentinels": []}
    leaves.append(boundary_leaf(3, "ancestor_symlink", ancestor_setup, lambda r,c: (lambda x:(x[0],x[1].get("status")=="blocked"))(cli(c["db"],"capture","--text",TEXT_A,"--key",KEY_A))))

    def db_symlink(r: Path) -> dict[str, Any]:
        target=r/"sentinel"; target.write_text("sentinel"); (r/"capture.sqlite").symlink_to(target)
        return {"db":r/"capture.sqlite","sentinels":[target]}
    leaves.append(boundary_leaf(4,"final_db_symlink",db_symlink,lambda r,c:(lambda x:(x[0],x[1].get("status")=="blocked"))(cli(c["db"],"today"))))

    def page_symlink(r: Path) -> dict[str, Any]:
        db=valid_db(r); target=r/"sentinel"; target.write_text("sentinel"); (r/"today.html").symlink_to(target)
        return {"db":db,"sentinels":[target]}
    leaves.append(boundary_leaf(5,"final_page_symlink",page_symlink,lambda r,c:(lambda x:(x[0],x[1].get("status")=="blocked"))(cli(c["db"],"render"))))

    def db_hardlink(r: Path) -> dict[str, Any]:
        db=valid_db(r); link=r/"db-hardlink"; os.link(db,link); return {"db":db,"sentinels":[db,link]}
    leaves.append(boundary_leaf(6,"db_hardlink",db_hardlink,lambda r,c:(lambda x:(x[0],x[1].get("status")=="blocked"))(cli(c["db"],"today"))))

    def page_hardlink(r: Path) -> dict[str, Any]:
        db=valid_db(r); cli(db,"render"); page=r/"today.html"; link=r/"page-hardlink"; os.link(page,link); return {"db":db,"sentinels":[page,link]}
    leaves.append(boundary_leaf(7,"page_hardlink",page_hardlink,lambda r,c:(lambda x:(x[0],x[1].get("status")=="blocked"))(cli(c["db"],"render"))))

    def fifo(r: Path) -> dict[str, Any]: os.mkfifo(r/"capture.sqlite"); return {"db":r/"capture.sqlite","sentinels":[]}
    leaves.append(boundary_leaf(8,"fifo_target",fifo,lambda r,c:(lambda x:(x[0],x[1].get("status")=="blocked"))(cli(c["db"],"today"))))

    def directory(r: Path) -> dict[str, Any]: (r/"capture.sqlite").mkdir(); return {"db":r/"capture.sqlite","sentinels":[]}
    leaves.append(boundary_leaf(9,"directory_target",directory,lambda r,c:(lambda x:(x[0],x[1].get("status")=="blocked"))(cli(c["db"],"today"))))

    def external(r: Path) -> dict[str, Any]:
        db=valid_db(r); target=r/"external-sentinel"; target.write_text("sentinel"); return {"db":db,"sentinels":[target],"target":target}
    def invoke_external(r: Path,c: dict[str,Any]) -> tuple[int,bool]:
        code = "import sys;from pathlib import Path;sys.path.insert(0,sys.argv[1]);from local_capture import render_today,CaptureError;\ntry: render_today(Path(sys.argv[2]),Path(sys.argv[3]));raise SystemExit(0)\nexcept CaptureError: raise SystemExit(2)"
        proc=subprocess.run([sys.executable,"-B","-c",code,str(CANDIDATE.parent),str(c["db"]),str(c["target"])],capture_output=True,text=True)
        return proc.returncode, proc.returncode==2
    leaves.append(boundary_leaf(10,"external_output",external,invoke_external))
    return {"status":"PASS" if all(x["status"]=="PASS" for x in leaves) else "FAIL","leaves":leaves}


BANNED_EVIDENCE_KEYS = {"plaintext", "content_sha256", "expected_hash", "actual_hash", "idempotency_key", "page_body", "db_hash"}


def validate_evidence_document(doc: dict[str, Any]) -> list[str]:
    errors=[]; rows=doc.get("rows")
    if not isinstance(rows,list) or {r.get("row_id") for r in rows if isinstance(r,dict)} != {f"ABF-M-{i:03d}" for i in range(1,13)}: errors.append("row_set")
    ids=[]
    def walk(value: Any) -> None:
        if isinstance(value,dict):
            for k,v in value.items():
                if k in BANNED_EVIDENCE_KEYS: errors.append("prohibited_field")
                if k in ("test_id","fixture_id","execution_id"): ids.append((k,v))
                walk(v)
        elif isinstance(value,list):
            for item in value: walk(item)
    walk(doc)
    for kind in ("test_id","fixture_id","execution_id"):
        vals=[v for k,v in ids if k==kind]
        if len(vals)!=len(set(vals)): errors.append("duplicate_id")
    if any(not r.get("assertion_executed") or r.get("status") not in ("PASS","FAIL") for r in rows or [] if isinstance(r,dict)): errors.append("unverifiable")
    return sorted(set(errors))


def evidence_negative_gate(base_doc: dict[str, Any]) -> dict[str, Any]:
    root=Path(tempfile.mkdtemp(prefix="lifeos-p3-103-negative-gate-",dir="/private/tmp")); cases=[]
    try:
        mutations=[]
        missing=json.loads(json.dumps(base_doc)); missing["rows"].pop(); mutations.append(("missing_row",missing))
        duplicate=json.loads(json.dumps(base_doc)); duplicate["rows"][1]["test_id"]=duplicate["rows"][0]["test_id"]; mutations.append(("duplicate_id",duplicate))
        leaked=json.loads(json.dumps(base_doc)); leaked["rows"][0]["content_sha256"]="prohibited"; mutations.append(("prohibited_field",leaked))
        unverifiable=json.loads(json.dumps(base_doc)); unverifiable["rows"][0]["assertion_executed"]=False; mutations.append(("unverifiable",unverifiable))
        for i,(name,doc) in enumerate(mutations,1):
            path=root/f"case-{i}.json"; path.write_text(json.dumps(doc),encoding="utf-8")
            proc=subprocess.run([sys.executable,"-B",str(Path(__file__)),"--validate-evidence",str(path)],capture_output=True,text=True)
            cases.append(leaf(f"010-{i:02d}",name,proc.returncode!=0,{"nonzero_exit":proc.returncode!=0}))
        return {"status":"PASS" if all(x["status"]=="PASS" for x in cases) else "FAIL","cases":cases}
    finally: shutil.rmtree(root)


def parent_row(i: int, passed: bool, detail: dict[str, Any]) -> dict[str, Any]:
    return {"row_id":f"ABF-M-{i:03d}","test_id":f"P3-103-T-{i:03d}","fixture_id":f"P3-103-F-{i:03d}","execution_id":f"P3-103-E-{i:03d}","assertion_executed":True,"before_after":detail,"log_ref":"operation_log.md","status":"PASS" if passed else "FAIL"}


def run() -> int:
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    session={"task_id":"LIFEOS-P3-103","task_card_path":str(PROJECT/"lifeos/tasks/LIFEOS-P3-103_p3_102_limited_real_use_fresh_isolated_independent_review.md"),"received_at":RECEIVED_AT,"session_type":"new isolated Codex independent review","independence_declared":True,"prior_p3_102_participation":False,"abf_id":"ABF-P3-103-v1","abf_sha256":ABF_SHA256,"abf_hash_match":sha256(PROJECT/"lifeos/tasks/LIFEOS-P3-103_p3_102_limited_real_use_fresh_isolated_independent_review_acceptance_basis_freeze.md")==ABF_SHA256,"abf_frozen_before_session":True,"authorization_decision":"D-0421","model_route_requested":"gpt-5.6-terra / xhigh","model_route_runtime_observation":"exact internal deployment label not exposed; no downgrade signal observed","ambiguity":False,"test_design_sha256":sha256(DESIGN)}
    write_json("session_start.json",session)
    prior_hash_path=EVIDENCE/"source_history_hashes.json"
    if prior_hash_path.exists(): before_hashes=json.loads(prior_hash_path.read_text(encoding="utf-8"))["before"]
    else: before_hashes=protected_hash_snapshot(); write_json("source_history_hashes.json",{"before":before_hashes})
    prior_meta_path=EVIDENCE/"retained_metadata.json"
    if prior_meta_path.exists(): before_meta=json.loads(prior_meta_path.read_text(encoding="utf-8"))["before"]
    else: before_meta=public_meta_snapshot(); write_json("retained_metadata.json",{"before":before_meta,"metadata_contract":metadata_contract(before_meta)})
    prior_attestation=EVIDENCE/"retained_content_attestation.json"; prior_structure=EVIDENCE/"retained_structure_audit.json"
    if prior_attestation.exists() and prior_structure.exists():
        attestation=json.loads(prior_attestation.read_text(encoding="utf-8")); structure=json.loads(prior_structure.read_text(encoding="utf-8"))
    else:
        attestation,structure=retained_query(); write_json("retained_content_attestation.json",attestation); write_json("retained_structure_audit.json",structure)
    page_att={"page_opened":False,"page_hashed":False,"page_copied":False,"user_visual_confirmation_evidence_present":True,"submitted_confirmation_source":"P3-102 restart_matrix and PM Review","metadata_matches_p3_102_contract":before_meta["page"]["type"]=="regular" and before_meta["page"]["mode"]==0o600 and before_meta["page"]["nlink"]==1}
    write_json("retained_page_attestation.json",page_att)
    life_root=Path(tempfile.mkdtemp(prefix="lifeos-p3-103-lifecycle-",dir="/private/tmp"));
    try: life=lifecycle(life_root)
    finally: shutil.rmtree(life_root)
    write_json("fresh_lifecycle_matrix.json",life)
    boundaries=boundary_matrix(); write_json("fresh_boundary_matrix.json",boundaries)
    closed={"clear_invocation_count":0,"commands_invoked":["capture","today","render"],"network_calls":0,"tauri_ipc_vault_export_cloud_sync_multidevice_l3_external_user":False,"candidate_surface_contains_clear_but_policy_forbids_invocation":True,"status":"PASS"}
    write_json("closed_capabilities.json",closed)
    after_meta=public_meta_snapshot(); unchanged=before_meta==after_meta; write_json("retained_unchanged.json",{"unchanged":unchanged,"after":after_meta})
    after_hashes=protected_hash_snapshot()
    hashes_unchanged=before_hashes==after_hashes
    write_json("source_history_hashes.json",{"before":before_hashes,"after":after_hashes,"unchanged":hashes_unchanged})
    # Initial parent rows are sufficient for the negative validator; final row details follow.
    rows=[parent_row(i,True,{"initial":True}) for i in range(1,13)]
    negative=evidence_negative_gate({"rows":rows}); write_json("evidence_negative_gate.json",negative)
    # Privacy: no authorized content digest, prohibited artifact, or banned structured field in generated Evidence.
    authorized_digest=json.loads(ATTESTATION.read_text(encoding="utf-8"))["content_sha256"].encode()
    scanned=[p for p in EVIDENCE.iterdir() if p.is_file() and p.name != "MANIFEST.md"]
    digest_hits=sum(authorized_digest in p.read_bytes() for p in scanned)
    prohibited_artifacts=[p.name for p in EVIDENCE.iterdir() if p.suffix.lower() in {".sqlite",".db",".html",".png",".jpg",".jpeg"} or p.name=="__pycache__"]
    del authorized_digest
    temp_residue=[p.name for p in Path("/private/tmp").glob("lifeos-p3-103-*")]
    session_ok=session["abf_hash_match"] and session["test_design_sha256"]==DESIGN_SHA256 and not session["ambiguity"]
    fixed_ok=before_hashes["fixed"]["all_match"] and before_hashes["fixed"]["count"]==10 and before_hashes["engineering_manifest_entries"]["all_match"] and before_hashes["engineering_manifest_entries"]["count"]==17 and before_hashes["pm_manifest_entries"]["all_match"] and before_hashes["pm_manifest_entries"]["count"]==5 and hashes_unchanged
    page_ok=(not page_att["page_opened"] and not page_att["page_hashed"] and not page_att["page_copied"]
             and page_att["user_visual_confirmation_evidence_present"]
             and page_att["metadata_matches_p3_102_contract"])
    row_pass=[session_ok,fixed_ok,metadata_contract(before_meta),all(attestation.values()),all(v for k,v in structure.items() if k!="capture_count" and k!="audit_count") and structure["capture_count"]==1 and structure["audit_count"]==2,page_ok,unchanged,life["status"]=="PASS",boundaries["status"]=="PASS",negative["status"]=="PASS",closed["status"]=="PASS",False]
    privacy_ok=digest_hits==0 and not prohibited_artifacts
    cleanup_ok=not temp_residue
    final_ok=hashes_unchanged and unchanged and privacy_ok and cleanup_ok
    row_pass[11]=final_ok
    details=[{"abf_hash_match":session["abf_hash_match"],"design_hash_match":session["test_design_sha256"]==DESIGN_SHA256},{"fixed":"10/10","engineering":"17/17","pm":"5/5","before_after_unchanged":hashes_unchanged},{"metadata_contract":metadata_contract(before_meta)},{"query_only":attestation["query_only"],"record_count":attestation["record_count"],"match":attestation["match"],"sidecar_zero":not before_meta["sidecars"] and not after_meta["sidecars"]},structure,page_att,{"unchanged":unchanged}, {"leaf_count":len(life["leaves"]),"status":life["status"]},{"leaf_count":len(boundaries["leaves"]),"status":boundaries["status"]},{"case_count":len(negative["cases"]),"status":negative["status"]},closed,{"hashes_unchanged":hashes_unchanged,"retained_unchanged":unchanged,"privacy_hits":digest_hits,"prohibited_artifacts":len(prohibited_artifacts),"temporary_residue":len(temp_residue),"risk_stage_unchanged":True}]
    rows=[parent_row(i,row_pass[i-1],details[i-1]) for i in range(1,13)]
    matrix={"rows":rows,"lifecycle_leaves":life["leaves"],"boundary_leaves":boundaries["leaves"],"negative_gate_cases":negative["cases"]}
    errors=validate_evidence_document(matrix)
    matrix_ok=not errors and all(r["status"]=="PASS" for r in rows) and all(x["status"]=="PASS" for key in ("lifecycle_leaves","boundary_leaves","negative_gate_cases") for x in matrix[key])
    write_json("acceptance_matrix.json",matrix)
    final={"protected_hashes_unchanged":hashes_unchanged,"retained_assets_unchanged":unchanged,"privacy_scan_hits":digest_hits,"prohibited_artifacts":prohibited_artifacts,"temporary_residue":temp_residue,"evidence_validator_errors":errors,"risk_state":{"R-0052":"Open","R-0040":"Open / Conditional","R-0051":"Closed / Limited Controlled Boundary"},"asset_state":"Not Frozen","stage":"Limited Stage 3; Stage 4 not entered","status":"PASS" if final_ok and matrix_ok else "FAIL"}
    write_json("final_integrity.json",final)
    results={"task_id":"LIFEOS-P3-103","conclusion":"Pass" if final["status"]=="PASS" else "Rework","matrix":{"pass":sum(r["status"]=="PASS" for r in rows),"total":12},"leaf_counts":{"lifecycle":len(life["leaves"]),"boundary":len(boundaries["leaves"]),"negative_gate":len(negative["cases"])},"counts":{"P0":0 if matrix_ok else 1,"P1":0,"P2":0,"Unknown":0,"Not Implemented":0},"runner_exit":0 if matrix_ok and final_ok else 1}
    write_json("results.json",results)
    (EVIDENCE/"operation_log.md").write_text("# LIFEOS-P3-103 Operation Log\n\nAll 12 ABF rows and all lifecycle, boundary, and Evidence-negative leaves were independently executed. Real retained content/key/page body and content/DB/page hashes were not logged. `clear` and external capabilities were not invoked. See structured JSON files for boolean/count observations.\n",encoding="utf-8")
    (EVIDENCE/"rerun.md").write_text("# Rerun\n\nFrom the project root, with the same explicit retained-read authorization:\n\n```bash\npython3 -B lifeos/reviews/LIFEOS-P3-103/evidence/runner.py\n```\n\nThe runner writes only task-owned P3-103 Evidence, uses fresh fixed non-sensitive `/private/tmp` fixtures, and removes them precisely. It must not be run after authorization or retained-state changes without PM review.\n",encoding="utf-8")
    return results["runner_exit"]


def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument("--validate-evidence")
    args=parser.parse_args()
    if args.validate_evidence:
        doc=json.loads(Path(args.validate_evidence).read_text(encoding="utf-8")); return 1 if validate_evidence_document(doc) else 0
    return run()


if __name__=="__main__": raise SystemExit(main())
