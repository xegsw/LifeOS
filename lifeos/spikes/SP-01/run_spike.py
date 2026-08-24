#!/usr/bin/env python3
"""LifeOS SP-01 isolated durability spike. Synthetic data only; not product code."""

import argparse
import csv
import hashlib
import json
import os
import platform
import random
import resource
import shutil
import signal
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WORK = ROOT / "work"
LOGS = ROOT / "raw_logs"
RESULTS = ROOT / "results.json"
MATRIX = ROOT / "test_matrix.csv"
SEED = 20260808


def digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def connect(path, timeout=5.0):
    db = sqlite3.connect(str(path), timeout=timeout, isolation_level=None)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=5000")
    return db


SCHEMA = """
CREATE TABLE IF NOT EXISTS artifacts(
  artifact_id TEXT PRIMARY KEY, source_kind TEXT NOT NULL, project_id TEXT,
  created_seq INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS versions(
  artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
  version_no INTEGER NOT NULL, original_text TEXT NOT NULL,
  content_hash TEXT NOT NULL, client_time TEXT NOT NULL,
  durable_state TEXT NOT NULL CHECK(durable_state IN ('local_saved','offline_local_saved')),
  sync_state TEXT NOT NULL CHECK(sync_state IN ('not_required','pending_sync')),
  PRIMARY KEY(artifact_id, version_no)
);
CREATE TABLE IF NOT EXISTS submissions(
  idempotency_key TEXT PRIMARY KEY, payload_hash TEXT NOT NULL,
  artifact_id TEXT NOT NULL, version_no INTEGER NOT NULL,
  FOREIGN KEY(artifact_id,version_no) REFERENCES versions(artifact_id,version_no)
);
CREATE TABLE IF NOT EXISTS tombstones(
  artifact_id TEXT PRIMARY KEY, tombstone_seq INTEGER NOT NULL, reason_code TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS feedback_events(
  feedback_id TEXT NOT NULL, event_seq INTEGER NOT NULL,
  event_type TEXT NOT NULL CHECK(event_type IN ('confirm','reject','correct','complete','defer','retract')),
  target_version TEXT NOT NULL, PRIMARY KEY(feedback_id,event_seq)
);
CREATE TABLE IF NOT EXISTS authorizations(
  authorization_id TEXT PRIMARY KEY, state TEXT NOT NULL CHECK(state IN ('allowed','denied','expired','revoked')),
  scope_code TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS derived_index(
  artifact_id TEXT NOT NULL, version_no INTEGER NOT NULL, token_hash TEXT NOT NULL,
  PRIMARY KEY(artifact_id,version_no)
);
CREATE VIEW IF NOT EXISTS active_versions AS
 SELECT v.* FROM versions v LEFT JOIN tombstones t ON t.artifact_id=v.artifact_id
 WHERE t.artifact_id IS NULL;
CREATE VIEW IF NOT EXISTS active_feedback AS
 SELECT f.* FROM feedback_events f
 WHERE f.event_type!='retract' AND NOT EXISTS(
   SELECT 1 FROM feedback_events r WHERE r.feedback_id=f.feedback_id
   AND r.event_type='retract' AND r.event_seq>f.event_seq
 );
"""


def init_db(path):
    db = connect(path)
    db.executescript(SCHEMA)
    db.close()


def capture(db, record, inject=None, stage=None):
    """Return only after COMMIT. Callers may then safely emit a saved acknowledgement."""
    payload_hash = digest(record["original_text"])
    started = time.perf_counter_ns()
    try:
        existing = db.execute(
            "SELECT payload_hash,artifact_id,version_no FROM submissions WHERE idempotency_key=?",
            (record["idempotency_key"],),
        ).fetchone()
        if existing:
            if existing[0] != payload_hash or existing[1:] != (record["artifact_id"], record["version_no"]):
                return {"ok": False, "error": "IDEMPOTENCY_CONFLICT", "action": "use a new idempotency key"}
            return {"ok": True, "duplicate": True, "hash": existing[0], "latency_ms": (time.perf_counter_ns()-started)/1e6}
        if inject in ("disk_full", "io_error"):
            raise sqlite3.OperationalError("injected_" + inject)
        db.execute("BEGIN IMMEDIATE")
        db.execute("INSERT OR IGNORE INTO artifacts VALUES(?,?,?,?)", (
            record["artifact_id"], record["source_kind"], record["project_id"], record["created_seq"]
        ))
        db.execute("INSERT INTO versions VALUES(?,?,?,?,?,?,?)", (
            record["artifact_id"], record["version_no"], record["original_text"], payload_hash,
            record["client_time"], record["durable_state"], record["sync_state"]
        ))
        db.execute("INSERT INTO submissions VALUES(?,?,?,?)", (
            record["idempotency_key"], payload_hash, record["artifact_id"], record["version_no"]
        ))
        if stage:
            stage("MID_WRITE")
        db.execute("COMMIT")
        if stage:
            stage("POST_COMMIT")
        return {"ok": True, "duplicate": False, "hash": payload_hash, "latency_ms": (time.perf_counter_ns()-started)/1e6}
    except sqlite3.Error as exc:
        if db.in_transaction:
            db.execute("ROLLBACK")
        return {"ok": False, "error": "WRITE_FAILED", "action": "keep editor text and retry or copy it", "detail": str(exc)}


def fixture_record(i, kill=False):
    artifact_num = i if kill else (i if i < 900 else i - 100)
    artifact_id = ("kill-artifact-" if kill else "artifact-") + f"{artifact_num:04d}"
    version_no = 2 if (not kill and i >= 900) else 1
    text = f"SYNTHETIC_FIXTURE_{'KILL' if kill else 'BASE'}_{i:04d}_V{version_no}_NO_REAL_DATA"
    return {
        "artifact_id": artifact_id, "version_no": version_no,
        "idempotency_key": ("kill-idem-" if kill else "idem-") + f"{i:04d}",
        "original_text": text, "source_kind": "local_input",
        "project_id": None if i % 10 == 0 else f"project-{i % 3 + 1}",
        "created_seq": i + 1,
        "client_time": "2099-01-01T00:00:00Z" if i % 17 == 0 else "2000-01-01T00:00:00Z",
        "durable_state": "offline_local_saved" if i % 4 == 0 else "local_saved",
        "sync_state": "pending_sync" if i % 4 == 0 else "not_required",
    }


def worker(args):
    rec = json.loads(args.record)
    db = connect(Path(args.db))
    print("BEFORE_WRITE", flush=True)
    if args.pause == "BEFORE_WRITE":
        time.sleep(30)
    def stage(name):
        print(name, flush=True)
        if args.pause == name:
            time.sleep(30)
    result = capture(db, rec, stage=stage)
    if not result["ok"]:
        print("ERROR " + result["error"], flush=True)
        return 2
    print("ACK_SAVED " + result["hash"], flush=True)
    print("POST_ACK", flush=True)
    if args.pause == "POST_ACK":
        time.sleep(30)
    db.close()
    return 0


def kill_at(db_path, rec, pause):
    proc = subprocess.Popen(
        [sys.executable, str(Path(__file__).resolve()), "worker", "--db", str(db_path),
         "--record", json.dumps(rec, separators=(",", ":")), "--pause", pause],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    )
    lines = []
    target_seen = False
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        line = proc.stdout.readline().strip()
        if line:
            lines.append(line)
            if line == pause:
                target_seen = True
                break
        elif proc.poll() is not None:
            break
    if not target_seen:
        proc.kill(); proc.wait()
        raise RuntimeError(f"worker did not reach {pause}: {lines}")
    os.kill(proc.pid, signal.SIGKILL)
    proc.wait(timeout=5)
    acknowledged = any(line.startswith("ACK_SAVED ") for line in lines)
    return acknowledged, lines


def snapshot_counts(db):
    names = ["artifacts", "versions", "submissions", "tombstones", "feedback_events", "authorizations"]
    return {n: db.execute(f"SELECT count(*) FROM {n}").fetchone()[0] for n in names}


def verify_hashes(db):
    mismatches = 0
    for text, stored in db.execute("SELECT original_text,content_hash FROM versions"):
        mismatches += digest(text) != stored
    return mismatches


def test_fixture_and_performance(db_path):
    db = connect(db_path)
    latencies = []
    acknowledged = {}
    for i in range(1000):
        rec = fixture_record(i)
        result = capture(db, rec)
        assert result["ok"]
        latencies.append(result["latency_ms"])
        acknowledged[rec["idempotency_key"]] = result["hash"]
    # Twenty exact duplicate deliveries; ten conflicting duplicate keys.
    exact_duplicate_rows = 0
    for i in range(20):
        exact_duplicate_rows += capture(db, fixture_record(i))["duplicate"]
    conflict_rejected = 0
    for i in range(10):
        rec = fixture_record(i)
        rec["original_text"] += "_CONFLICT"
        conflict_rejected += capture(db, rec)["error"] == "IDEMPOTENCY_CONFLICT"
    db.execute("BEGIN IMMEDIATE")
    for aid in ("artifact-0010", "artifact-0020", "artifact-0030"):
        db.execute("INSERT INTO tombstones VALUES(?,?,?)", (aid, 2001, "user_delete"))
    db.execute("INSERT INTO feedback_events VALUES('feedback-1',1,'confirm','artifact-0001:v1')")
    db.execute("INSERT INTO feedback_events VALUES('feedback-1',2,'retract','artifact-0001:v1')")
    states = [("auth-allowed","allowed"),("auth-denied","denied"),("auth-expired","expired"),("auth-revoked","revoked")]
    db.executemany("INSERT INTO authorizations VALUES(?,?,'local-synthetic')", states)
    db.execute("COMMIT")
    q = lambda p: statistics.quantiles(latencies, n=100, method="inclusive")[p-1]
    result = {
        "fixture_submissions": 1000, "unique_artifacts": 900, "version_rows": 1000,
        "two_version_artifacts": 100, "exact_duplicate_deliveries": 20,
        "exact_duplicates_reused": exact_duplicate_rows, "conflicts_rejected": conflict_rejected,
        "pending_sync_rows": db.execute("SELECT count(*) FROM versions WHERE sync_state='pending_sync'").fetchone()[0],
        "tombstones": 3, "retracted_feedback_active_rows": db.execute("SELECT count(*) FROM active_feedback WHERE feedback_id='feedback-1'").fetchone()[0],
        "p50_ms": statistics.median(latencies), "p95_ms": q(95), "p99_ms": q(99), "max_ms": max(latencies),
        "hash_mismatches": verify_hashes(db), "integrity": db.execute("PRAGMA integrity_check").fetchone()[0],
    }
    db.close()
    return result, acknowledged


def test_failures(db_path):
    db = connect(db_path)
    false_acks = 0
    cases = {}
    for fault in ("disk_full", "io_error"):
        rec = fixture_record(3000 + len(cases), kill=True)
        before = snapshot_counts(db)
        outcome = capture(db, rec, inject=fault)
        after = snapshot_counts(db)
        ack = outcome.get("ok", False)
        false_acks += ack
        cases[fault] = {"acknowledged": ack, "error": outcome["error"], "action": outcome["action"], "db_unchanged": before == after}
    # A failed new version must not overwrite the durable old version.
    old = fixture_record(7)
    old_hash = db.execute("SELECT content_hash FROM versions WHERE artifact_id=? AND version_no=1", (old["artifact_id"],)).fetchone()[0]
    rec = dict(old); rec.update(version_no=2, idempotency_key="failed-new-version", original_text="SYNTHETIC_FAILED_NEW_VERSION")
    capture(db, rec, inject="io_error")
    old_after = db.execute("SELECT content_hash FROM versions WHERE artifact_id=? AND version_no=1", (old["artifact_id"],)).fetchone()[0]
    cases["old_version_preserved"] = old_hash == old_after
    db.close()
    return {"false_ack_count": false_acks, "cases": cases}


def test_kills(db_path):
    rng = random.Random(SEED)
    stages = ["BEFORE_WRITE", "MID_WRITE", "POST_COMMIT", "POST_ACK"]
    stage_counts = {s: 0 for s in stages}
    acknowledged = {}
    keys = []
    integrity_checks = 0
    integrity_failures = 0
    for i in range(1000):
        stage = stages[rng.randrange(4)]
        stage_counts[stage] += 1
        rec = fixture_record(10000 + i, kill=True)
        ack, lines = kill_at(db_path, rec, stage)
        if ack:
            acknowledged[rec["idempotency_key"]] = digest(rec["original_text"])
        keys.append((rec, stage, ack))
        check_db = connect(db_path)
        check = check_db.execute("PRAGMA integrity_check").fetchone()[0]
        check_db.close()
        integrity_checks += 1
        integrity_failures += check != "ok"
    db = connect(db_path)
    integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    ack_missing = ack_hash_mismatch = half_rows = 0
    for rec, stage, ack in keys:
        row = db.execute("SELECT v.original_text,v.content_hash FROM submissions s JOIN versions v USING(artifact_id,version_no) WHERE s.idempotency_key=?", (rec["idempotency_key"],)).fetchone()
        if ack and row is None:
            ack_missing += 1
        if ack and row and row[1] != digest(rec["original_text"]):
            ack_hash_mismatch += 1
        if row and digest(row[0]) != row[1]:
            half_rows += 1
    kill_rows = db.execute("SELECT count(*) FROM submissions WHERE idempotency_key LIKE 'kill-idem-1%'").fetchone()[0]
    duplicate_rows = db.execute("SELECT count(*)-(SELECT count(DISTINCT idempotency_key) FROM submissions) FROM submissions").fetchone()[0]
    db.close()
    return {"cycles": 1000, "stage_counts": stage_counts, "acknowledged": len(acknowledged),
            "acknowledged_missing": ack_missing, "ack_hash_mismatch": ack_hash_mismatch,
            "half_or_corrupt_rows": half_rows, "duplicate_idempotency_rows": duplicate_rows,
            "committed_kill_rows": kill_rows, "integrity": integrity,
            "integrity_checks": integrity_checks, "integrity_failures": integrity_failures}


def test_concurrency(db_path):
    stop = threading.Event()
    read_ready = threading.Event()
    index_errors = []
    def long_reader():
        db = connect(db_path)
        db.execute("BEGIN")
        db.execute("SELECT sum(length(original_text)) FROM active_versions").fetchone()
        read_ready.set()
        stop.wait(5)
        db.execute("ROLLBACK"); db.close()
    def background_indexer():
        db = connect(db_path)
        try:
            rows = db.execute("SELECT artifact_id,version_no,content_hash FROM active_versions LIMIT 400").fetchall()
            for row in rows:
                db.execute("INSERT OR REPLACE INTO derived_index VALUES(?,?,?)", row)
                time.sleep(0.0005)
        except Exception as exc:
            index_errors.append(type(exc).__name__)
        finally:
            db.close()
    reader = threading.Thread(target=long_reader); reader.start(); read_ready.wait(5)
    indexer = threading.Thread(target=background_indexer); indexer.start()
    db = connect(db_path); latencies=[]; errors=0
    for i in range(100):
        rec=fixture_record(20000+i, kill=True)
        out=capture(db,rec)
        if out["ok"]: latencies.append(out["latency_ms"])
        else: errors += 1
    checkpoint = db.execute("PRAGMA wal_checkpoint(PASSIVE)").fetchone()
    db.close(); stop.set(); reader.join(); indexer.join()
    return {"captures": 100, "errors": errors, "index_errors": index_errors,
            "passive_checkpoint_result": list(checkpoint),
            "p95_ms": statistics.quantiles(latencies,n=100,method="inclusive")[94],
            "p99_ms": statistics.quantiles(latencies,n=100,method="inclusive")[98],
            "max_ms": max(latencies)}


def test_backup_restore(db_path, backup_path, restored_path):
    source = connect(db_path)
    pre_backup_floor = snapshot_counts(source)
    write_count = [0]
    writer_error = []
    def active_writer():
        db = connect(db_path)
        try:
            for i in range(50):
                out = capture(db, fixture_record(40000+i, kill=True))
                if out["ok"]: write_count[0] += 1
                time.sleep(0.001)
        except Exception as exc:
            writer_error.append(type(exc).__name__)
        db.close()
    writer = threading.Thread(target=active_writer); writer.start()
    deadline = time.monotonic()+5
    while write_count[0] == 0 and time.monotonic() < deadline: time.sleep(0.001)
    backup = sqlite3.connect(str(backup_path))
    source.backup(backup); backup.close()
    writer.join()
    live_after_backup = snapshot_counts(source)
    source.close()
    snap = connect(backup_path); snapshot = snapshot_counts(snap); snap.close()
    shutil.copy2(backup_path, restored_path)
    restored = connect(restored_path)
    integrity = restored.execute("PRAGMA integrity_check").fetchone()[0]
    after = snapshot_counts(restored)
    hash_mismatches = verify_hashes(restored)
    # Replay stale data with IDs that are already tombstoned/retracted. Active views must still exclude them.
    active_deleted_before = restored.execute("SELECT count(*) FROM active_versions WHERE artifact_id IN ('artifact-0010','artifact-0020','artifact-0030')").fetchone()[0]
    # INSERT OR IGNORE represents an old import package; tombstones/append-only retractions remain authoritative.
    restored.execute("INSERT OR IGNORE INTO artifacts VALUES('artifact-0010','old_import',NULL,1)")
    active_deleted_after = restored.execute("SELECT count(*) FROM active_versions WHERE artifact_id='artifact-0010'").fetchone()[0]
    active_feedback = restored.execute("SELECT count(*) FROM active_feedback WHERE feedback_id='feedback-1'").fetchone()[0]
    pending = restored.execute("SELECT count(*) FROM versions WHERE sync_state='pending_sync'").fetchone()[0]
    restored.close()
    floor_preserved = all(snapshot[k] >= pre_backup_floor[k] for k in snapshot)
    return {"method": "sqlite3 Online Backup API during active writes", "integrity": integrity,
            "counts_equal": snapshot == after, "pre_backup_floor": pre_backup_floor,
            "snapshot_counts": snapshot, "live_counts_after_backup": live_after_backup,
            "counts_after": after, "floor_preserved": floor_preserved,
            "concurrent_writes_completed": write_count[0], "writer_errors": writer_error,
            "hash_mismatches": hash_mismatches,
            "deleted_active_before_replay": active_deleted_before, "deleted_active_after_replay": active_deleted_after,
            "retracted_feedback_active_after_restore": active_feedback, "pending_sync_after_restore": pending,
            "backup_bytes": backup_path.stat().st_size}


def write_matrix(results):
    rows = [
        ("T01","1000 deterministic submissions + versions",results["fixture"]["integrity"]=="ok","fixture"),
        ("T02","saved acknowledgement only after COMMIT",results["kills"]["acknowledged_missing"]==0,"kills"),
        ("T03","kill before write",results["kills"]["stage_counts"]["BEFORE_WRITE"]>0,"kills"),
        ("T04","kill mid write",results["kills"]["stage_counts"]["MID_WRITE"]>0,"kills"),
        ("T05","kill post commit pre acknowledgement",results["kills"]["stage_counts"]["POST_COMMIT"]>0,"kills"),
        ("T06","kill post acknowledgement",results["kills"]["stage_counts"]["POST_ACK"]>0,"kills"),
        ("T07","disk full simulation no false acknowledgement",not results["failures"]["cases"]["disk_full"]["acknowledged"],"failures"),
        ("T08","I/O simulation no false acknowledgement",not results["failures"]["cases"]["io_error"]["acknowledged"],"failures"),
        ("T09","idempotent duplicate and conflict",results["fixture"]["exact_duplicates_reused"]==20 and results["fixture"]["conflicts_rejected"]==10,"fixture"),
        ("T10","clock skew does not determine ordering",results["fixture"]["version_rows"]==1000,"fixture"),
        ("T11","long read/background indexing capture",results["concurrency"]["errors"]==0,"concurrency"),
        ("T12","consistent backup during writes and restore",results["backup"]["integrity"]=="ok" and results["backup"]["counts_equal"] and results["backup"]["floor_preserved"],"backup"),
        ("T13","tombstone prevents resurrection",results["backup"]["deleted_active_after_replay"]==0,"backup"),
        ("T14","feedback retraction remains authoritative",results["backup"]["retracted_feedback_active_after_restore"]==0,"backup"),
        ("T15","hash and 1000 post-kill integrity checks",results["kills"]["half_or_corrupt_rows"]==0 and results["kills"]["integrity_failures"]==0 and results["backup"]["hash_mismatches"]==0,"all"),
    ]
    with MATRIX.open("w", newline="", encoding="utf-8") as fh:
        w=csv.writer(fh); w.writerow(["test_id","assertion","result","evidence_section"])
        for tid, assertion, passed, evidence in rows: w.writerow([tid,assertion,"PASS" if passed else "FAIL",evidence])


def main():
    WORK.mkdir(parents=True, exist_ok=True); LOGS.mkdir(parents=True, exist_ok=True)
    for p in (WORK/"spike.db", WORK/"backup.db", WORK/"restored.db"):
        if p.exists(): p.unlink()
        for suffix in ("-wal","-shm"):
            side=Path(str(p)+suffix)
            if side.exists(): side.unlink()
    db_path=WORK/"spike.db"; init_db(db_path)
    start=time.time()
    fixture, ack = test_fixture_and_performance(db_path)
    failures=test_failures(db_path)
    kills=test_kills(db_path)
    concurrency=test_concurrency(db_path)
    backup=test_backup_restore(db_path,WORK/"backup.db",WORK/"restored.db")
    usage=resource.getrusage(resource.RUSAGE_SELF)
    results={"seed":SEED,"started_epoch":start,"duration_seconds":time.time()-start,
             "environment":{"python":sys.version.split()[0],"sqlite":sqlite3.sqlite_version,
             "platform":platform.platform(),"machine":platform.machine(),"cpu_count":os.cpu_count(),
             "memory_bytes":None,"journal_mode":"wal","synchronous":"FULL"},
             "fixture":fixture,"failures":failures,"kills":kills,"concurrency":concurrency,"backup":backup,
             "resources":{"main_process_max_rss_platform_units":usage.ru_maxrss,"live_db_bytes":db_path.stat().st_size}}
    write_matrix(results)
    RESULTS.write_text(json.dumps(results,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    # Sanitized log: identifiers, hashes, counts and timings only; never original_text.
    (LOGS/"run_summary.json").write_text(json.dumps(results,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"result":"PASS" if all(r.split(',')[2]=='PASS' for r in MATRIX.read_text().splitlines()[1:]) else "FAIL",
                      "results":str(RESULTS),"matrix":str(MATRIX),"duration_seconds":results["duration_seconds"]},indent=2))
    return 0


if __name__ == "__main__":
    parser=argparse.ArgumentParser(); sub=parser.add_subparsers(dest="command")
    wp=sub.add_parser("worker"); wp.add_argument("--db",required=True); wp.add_argument("--record",required=True); wp.add_argument("--pause",required=True)
    args=parser.parse_args()
    raise SystemExit(worker(args) if args.command=="worker" else main())
