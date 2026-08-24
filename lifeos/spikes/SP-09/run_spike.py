#!/usr/bin/env python3
"""SP-09 deterministic SQLite/FTS5 capacity benchmark.

Synthetic only.  The schema is a benchmark mapping, not a product schema.
"""
import argparse
import csv
import hashlib
import json
import os
import platform
import resource
import re
import shutil
import sqlite3
import statistics
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
WORK = ROOT / "work"
SEED = 20260809


def now():
    return time.perf_counter()


def percentile(values, p):
    values = sorted(values)
    if not values:
        return None
    pos = (len(values) - 1) * p / 100
    lo, hi = int(pos), min(int(pos) + 1, len(values) - 1)
    return values[lo] + (values[hi] - values[lo]) * (pos - lo)


def latency_summary(values):
    return {
        "samples": len(values),
        "p50_ms": round(percentile(values, 50), 3),
        "p95_ms": round(percentile(values, 95), 3),
        "p99_ms": round(percentile(values, 99), 3),
        "max_ms": round(max(values), 3),
    }


def timed(fn):
    start_wall, start_cpu = now(), time.process_time()
    result = fn()
    return result, round(now() - start_wall, 3), round(time.process_time() - start_cpu, 3)


def connect(path):
    db = sqlite3.connect(str(path), timeout=60)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=60000")
    db.execute("PRAGMA temp_store=FILE")
    db.execute("PRAGMA cache_size=-131072")
    return db


SCHEMA = """
CREATE TABLE project(id INTEGER PRIMARY KEY, stable_id TEXT UNIQUE NOT NULL, name TEXT NOT NULL);
CREATE TABLE source(
  id INTEGER PRIMARY KEY, stable_id TEXT UNIQUE NOT NULL, project_id INTEGER NOT NULL,
  connected INTEGER NOT NULL, authorization_version INTEGER NOT NULL,
  FOREIGN KEY(project_id) REFERENCES project(id));
CREATE TABLE content_unit(
  id INTEGER PRIMARY KEY, stable_id TEXT UNIQUE NOT NULL, project_id INTEGER NOT NULL,
  source_id INTEGER NOT NULL, version INTEGER NOT NULL, created_day INTEGER NOT NULL,
  kind TEXT NOT NULL, original_text TEXT NOT NULL, content_hash TEXT NOT NULL,
  authorization_state TEXT NOT NULL, evidence_state TEXT NOT NULL,
  active INTEGER NOT NULL, generation INTEGER NOT NULL, deleted_generation INTEGER,
  FOREIGN KEY(project_id) REFERENCES project(id), FOREIGN KEY(source_id) REFERENCES source(id));
CREATE TABLE chunk(
  id INTEGER PRIMARY KEY, content_id INTEGER NOT NULL, project_id INTEGER NOT NULL,
  source_id INTEGER NOT NULL, ordinal INTEGER NOT NULL, body TEXT NOT NULL,
  active INTEGER NOT NULL, generation INTEGER NOT NULL,
  FOREIGN KEY(content_id) REFERENCES content_unit(id));
CREATE VIRTUAL TABLE chunk_fts USING fts5(
  body, content='chunk', content_rowid='id', tokenize='unicode61 remove_diacritics 2');
CREATE TABLE link(id INTEGER PRIMARY KEY, from_content_id INTEGER NOT NULL, to_content_id INTEGER NOT NULL, state TEXT NOT NULL);
CREATE TABLE derivation(id INTEGER PRIMARY KEY, input_content_id INTEGER NOT NULL, output_content_id INTEGER NOT NULL, state TEXT NOT NULL, generation INTEGER NOT NULL);
CREATE TABLE feedback(id INTEGER PRIMARY KEY, content_id INTEGER NOT NULL, event_type TEXT NOT NULL, current_effect INTEGER NOT NULL);
CREATE TABLE audit_entry(id INTEGER PRIMARY KEY, event_code TEXT NOT NULL, scope_digest TEXT NOT NULL, generation INTEGER NOT NULL);
CREATE TABLE tombstone(content_id INTEGER PRIMARY KEY, generation INTEGER NOT NULL, reason_code TEXT NOT NULL);
CREATE INDEX idx_content_project_state ON content_unit(project_id, active, authorization_state, evidence_state, created_day DESC);
CREATE INDEX idx_content_source_state ON content_unit(source_id, active, generation);
CREATE INDEX idx_content_generation ON content_unit(generation, active);
CREATE INDEX idx_chunk_content ON chunk(content_id);
CREATE INDEX idx_chunk_project_active ON chunk(project_id, active, content_id);
CREATE INDEX idx_link_from ON link(from_content_id, state);
CREATE INDEX idx_derivation_input ON derivation(input_content_id, state);
CREATE INDEX idx_feedback_content ON feedback(content_id, current_effect);
"""


def create_db(path):
    for suffix in ("", "-wal", "-shm"):
        p = Path(str(path) + suffix)
        if p.exists():
            p.unlink()
    db = connect(path)
    db.executescript(SCHEMA)
    db.commit()
    return db


def content_state(i):
    # Mutually exclusive deterministic control populations.
    r = i % 200
    if r in (0, 1):
        return "allowed", "valid", 0, 2, 2  # deleted / old generation
    if r == 2:
        return "allowed", "valid", 0, 3, None  # retracted
    if r in (3, 4, 5, 6):
        return "denied", "valid", 1, 3, None
    if r == 7:
        return "allowed", "unavailable", 1, 3, None
    return "allowed", "valid", 1, 3, None


def generate(db, units, batch=2000):
    projects = max(16, min(128, units // 2500))
    sources = max(64, min(4096, units // 500))
    db.executemany("INSERT INTO project VALUES(?,?,?)", [
        (i, f"prj-syn-{i:04d}", f"Synthetic Project {i:04d}") for i in range(1, projects + 1)])
    db.executemany("INSERT INTO source VALUES(?,?,?,?,?)", [
        (i, f"src-syn-{i:06d}", (i % projects) + 1, 0 if i % 100 == 0 else 1, 3)
        for i in range(1, sources + 1)])
    db.commit()
    start = now()
    for first in range(1, units + 1, batch):
        last = min(units + 1, first + batch)
        contents, chunks, links, derivations, feedback, audits, tombstones = [], [], [], [], [], [], []
        for i in range(first, last):
            project_id = (i % projects) + 1
            source_id = (i % sources) + 1
            auth, evidence, active, generation, deleted_generation = content_state(i)
            kind = ("artifact", "action", "decision", "event", "assertion")[i % 5]
            topic = i % 257
            original = f"synthetic unit {i} topic{topic} project{project_id} source{source_id} checkpoint next action evidence"
            digest = hashlib.sha256(original.encode()).hexdigest()
            contents.append((i, f"cnt-syn-{i:09d}", project_id, source_id, 1 + i % 4,
                             i % 3650, kind, original, digest, auth, evidence,
                             active, generation, deleted_generation))
            if deleted_generation is not None:
                tombstones.append((i, deleted_generation, "synthetic_deleted"))
            for ordinal in range(3):
                cid = (i - 1) * 3 + ordinal + 1
                body = (f"topic{topic} project{project_id} synthetic chunk {ordinal} unit {i} "
                        f"context decision action source evidence day{i % 3650}")
                chunks.append((cid, i, project_id, source_id, ordinal, body, active, generation))
            if i % 5 == 0:
                links.append((i // 5, i, max(1, i - 17), "confirmed" if i % 10 else "candidate"))
            if i % 7 == 0:
                derivations.append((i // 7, i, max(1, i - 1), "active" if active else "invalid", generation))
            if i % 11 == 0:
                feedback.append((i // 11, i, ("confirm", "reject", "correct", "defer")[i % 4], 1))
            if i % 20 == 0:
                audits.append((i // 20, "SYNTHETIC_STATE", hashlib.sha256(f"scope:{i}".encode()).hexdigest()[:24], generation))
        with db:
            db.executemany("INSERT INTO content_unit VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", contents)
            db.executemany("INSERT INTO chunk VALUES(?,?,?,?,?,?,?,?)", chunks)
            db.executemany("INSERT INTO link VALUES(?,?,?,?)", links)
            db.executemany("INSERT INTO derivation VALUES(?,?,?,?,?)", derivations)
            db.executemany("INSERT INTO feedback VALUES(?,?,?,?)", feedback)
            db.executemany("INSERT INTO audit_entry VALUES(?,?,?,?)", audits)
            db.executemany("INSERT INTO tombstone VALUES(?,?,?)", tombstones)
    return round(now() - start, 3), projects, sources


def build_fts(db):
    db.execute("INSERT INTO chunk_fts(chunk_fts) VALUES('rebuild')")
    db.commit()


def query_latency(db, sql, params_factory, repetitions=120):
    values, samples = [], []
    for i in range(repetitions + 10):
        params = params_factory(i)
        t = now()
        rows = db.execute(sql, params).fetchall()
        elapsed = (now() - t) * 1000
        if i >= 10:
            values.append(elapsed)
            if len(samples) < 3:
                samples.append(len(rows))
    return latency_summary(values), samples


def benchmark_queries(db, projects):
    keyword_sql = """
      SELECT c.id, bm25(chunk_fts) score FROM chunk_fts
      JOIN chunk ch ON ch.id=chunk_fts.rowid
      JOIN content_unit c ON c.id=ch.content_id
      JOIN source s ON s.id=c.source_id
      WHERE chunk_fts MATCH ? AND c.project_id=? AND c.active=1
        AND ch.active=1 AND c.authorization_state='allowed'
        AND c.evidence_state='valid' AND s.connected=1
        AND c.generation >= COALESCE(c.deleted_generation+1, 0)
      ORDER BY score LIMIT 20"""
    meta_sql = """SELECT id FROM content_unit WHERE project_id=? AND active=1
      AND authorization_state='allowed' AND evidence_state='valid'
      AND created_day BETWEEN ? AND ? ORDER BY created_day DESC LIMIT 100"""
    high_auth_sql = """SELECT id FROM content_unit WHERE source_id=? AND active=1
      AND authorization_state='allowed' AND evidence_state='valid' LIMIT 100"""
    low_auth_sql = """SELECT id FROM content_unit WHERE active=1
      AND authorization_state='allowed' AND evidence_state='valid' ORDER BY id DESC LIMIT 100"""
    recovery_sql = """
      SELECT kind, id, created_day FROM content_unit
      WHERE project_id=? AND active=1 AND authorization_state='allowed'
        AND evidence_state='valid' AND kind IN ('action','decision','event','artifact')
      ORDER BY CASE kind WHEN 'action' THEN 1 WHEN 'decision' THEN 2 WHEN 'event' THEN 3 ELSE 4 END,
               created_day DESC LIMIT 240"""
    return {
        "keyword_project_permission": query_latency(db, keyword_sql,
            lambda i: (f"topic{i % 257}", (i % projects) + 1)),
        "metadata_project_time": query_latency(db, meta_sql,
            lambda i: ((i % projects) + 1, i % 3400, (i % 3400) + 250)),
        "authorization_high_selectivity": query_latency(db, high_auth_sql,
            lambda i: ((i % max(64, projects * 8)) + 1,)),
        "authorization_low_selectivity": query_latency(db, low_auth_sql, lambda i: ()),
        "project_recovery_package": query_latency(db, recovery_sql,
            lambda i: ((i % projects) + 1,), repetitions=80),
    }


def capture_latency(db, next_id, projects, sources, repetitions=100):
    values = []
    for offset in range(repetitions):
        i = next_id + offset
        project_id, source_id = (i % projects) + 1, (i % sources) + 1
        original = f"synthetic capture {i} topic{i % 257} checkpoint"
        t = now()
        with db:
            db.execute("INSERT INTO content_unit VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (i, f"capture-syn-{i}", project_id, source_id, 1, i % 3650, "artifact",
                        original, hashlib.sha256(original.encode()).hexdigest(), "allowed", "valid", 1, 3, None))
            for ordinal in range(3):
                cid = (i - 1) * 3 + ordinal + 1
                body = f"synthetic capture topic{i % 257} chunk {ordinal} checkpoint"
                db.execute("INSERT INTO chunk VALUES(?,?,?,?,?,?,?,?)",
                           (cid, i, project_id, source_id, ordinal, body, 1, 3))
                db.execute("INSERT INTO chunk_fts(rowid,body) VALUES(?,?)", (cid, body))
        values.append((now() - t) * 1000)
    return latency_summary(values)


def logical_block(db, where_sql, params, reason, generation=4):
    ids = [r[0] for r in db.execute(f"SELECT id FROM content_unit WHERE {where_sql}", params)]
    t = now()
    with db:
        db.executemany("INSERT INTO tombstone(content_id,generation,reason_code) VALUES(?,?,?) "
                       "ON CONFLICT(content_id) DO UPDATE SET generation=excluded.generation, reason_code=excluded.reason_code",
                       [(i, generation, reason) for i in ids])
        db.executemany("UPDATE content_unit SET active=0, deleted_generation=? WHERE id=?", [(generation, i) for i in ids])
        db.executemany("UPDATE chunk SET active=0 WHERE content_id=?", [(i,) for i in ids])
        db.executemany("INSERT INTO audit_entry(event_code,scope_digest,generation) VALUES(?,?,?)",
                       [(reason, hashlib.sha256(f"scope:{i}".encode()).hexdigest()[:24], generation) for i in ids])
    return ids, round(now() - t, 3)


def rebuild_fts(db):
    t = now()
    db.execute("DROP TABLE chunk_fts")
    db.execute("CREATE VIRTUAL TABLE chunk_fts USING fts5(body, content='chunk', content_rowid='id', tokenize='unicode61 remove_diacritics 2')")
    db.execute("INSERT INTO chunk_fts(chunk_fts) VALUES('rebuild')")
    db.commit()
    return round(now() - t, 3)


def create_backup(db, backup):
    if backup.exists(): backup.unlink()
    def do_backup():
        out = sqlite3.connect(str(backup))
        db.backup(out)
        out.close()
    _, elapsed, _ = timed(do_backup)
    return elapsed, backup.stat().st_size


def backup_restore(tier_dir, tombstone_ids, backup_s, backup_bytes):
    backup = tier_dir / "backup.db"
    restored = tier_dir / "restored.db"
    if restored.exists(): restored.unlink()
    restore_copy_s = round((lambda t=now(): (shutil.copy2(backup, restored), now()-t)[1])(), 3)
    rdb = connect(restored)
    integrity = rdb.execute("PRAGMA integrity_check").fetchone()[0]
    replay_start = now()
    with rdb:
        rdb.executemany("INSERT INTO tombstone(content_id,generation,reason_code) VALUES(?,4,'replayed') "
                        "ON CONFLICT(content_id) DO UPDATE SET generation=4, reason_code='replayed'",
                        [(i,) for i in tombstone_ids])
        rdb.executemany("UPDATE content_unit SET active=0, deleted_generation=4 WHERE id=?", [(i,) for i in tombstone_ids])
        rdb.executemany("UPDATE chunk SET active=0 WHERE content_id=?", [(i,) for i in tombstone_ids])
    replay_s = round(now() - replay_start, 3)
    leaked = rdb.execute("SELECT count(*) FROM content_unit c JOIN tombstone t ON t.content_id=c.id WHERE c.active=1").fetchone()[0]
    rdb.close()
    return {
        "backup_s": backup_s, "backup_bytes": backup_bytes,
        "restore_copy_s": restore_copy_s, "integrity": integrity,
        "tombstone_replay_s": replay_s, "post_replay_active_leaks": leaked,
    }


def checksum_scan(db):
    h, count, bytes_seen = hashlib.sha256(), 0, 0
    t = now()
    for stable_id, digest in db.execute("SELECT stable_id, content_hash FROM content_unit ORDER BY id"):
        payload = f"{stable_id}:{digest}\n".encode()
        h.update(payload); count += 1; bytes_seen += len(payload)
    elapsed = now() - t
    return {"rows": count, "manifest_bytes": bytes_seen, "seconds": round(elapsed, 3),
            "rows_per_s": round(count / elapsed, 1), "digest": h.hexdigest()}


def concurrent_rebuild_capture_probe(path, next_id):
    """Measure writer delay while a full FTS rebuild owns the SQLite writer lock."""
    locked = threading.Event()
    state = {}
    def maintenance():
        mdb = connect(path)
        mdb.execute("BEGIN IMMEDIATE")
        locked.set()
        t = now()
        mdb.execute("INSERT INTO chunk_fts(chunk_fts) VALUES('rebuild')")
        mdb.commit()
        state["rebuild_s"] = round(now() - t, 3)
        mdb.close()
    thread = threading.Thread(target=maintenance, daemon=True)
    thread.start()
    locked.wait(10)
    cdb = connect(path)
    t = now()
    text = f"synthetic concurrent capture {next_id}"
    with cdb:
        cdb.execute("INSERT INTO content_unit VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                    (next_id, f"concurrent-syn-{next_id}", 1, 1, 1, 1, "artifact", text,
                     hashlib.sha256(text.encode()).hexdigest(), "allowed", "valid", 1, 3, None))
    state["capture_wait_s"] = round(now() - t, 3)
    cdb.close()
    thread.join()
    state["capture_under_1s"] = state["capture_wait_s"] <= 1.0
    return state


def vector_estimates(chunks):
    rows = []
    for dim in (384, 768, 1536):
        for coverage in (1.0, 0.25, 0.10):
            count = int(chunks * coverage)
            for precision, width in (("float32", 4), ("float16", 2)):
                raw = count * dim * width
                pgvalue = count * (dim * width + 8)
                rows.append({"dimension": dim, "coverage": coverage, "precision": precision,
                             "vectors": count, "raw_bytes": raw, "pgvalue_bytes_estimate": pgvalue})
    return rows


def db_sizes(tier_dir):
    result = {}
    for name in ("sp09.db", "sp09.db-wal", "sp09.db-shm", "backup.db", "restored.db"):
        p = tier_dir / name
        result[name] = p.stat().st_size if p.exists() else 0
    return result


def run_tier(units, keep_work):
    tier = f"u{units}"
    tier_dir = WORK / tier
    tier_dir.mkdir(parents=True, exist_ok=True)
    db_path = tier_dir / "sp09.db"
    db = create_db(db_path)
    phase = {}
    (gen_data, gen_s, gen_cpu) = timed(lambda: generate(db, units))
    import_s, projects, sources = gen_data
    phase["generate_import"] = {"wall_s": gen_s, "cpu_s": gen_cpu, "inner_import_s": import_s,
                                 "units_per_s": round(units / gen_s, 1)}
    (_, fts_s, fts_cpu) = timed(lambda: build_fts(db))
    phase["fts_initial_build"] = {"wall_s": fts_s, "cpu_s": fts_cpu,
                                  "chunks_per_s": round(units * 3 / fts_s, 1)}
    checkpoint_start = now()
    checkpoint = db.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
    phase["wal_checkpoint"] = {"wall_s": round(now() - checkpoint_start, 3), "result": list(checkpoint)}
    integrity_start = now()
    integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
    phase["integrity_check"] = {"wall_s": round(now() - integrity_start, 3), "result": integrity}
    counts = {table: db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
              for table in ("project", "source", "content_unit", "chunk", "link", "derivation", "feedback", "audit_entry", "tombstone")}
    queries = benchmark_queries(db, projects)
    capture = capture_latency(db, units + 1, projects, sources)
    db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    backup_s, backup_bytes = create_backup(db, tier_dir / "backup.db")
    # One-item block must take effect before FTS cleanup.
    single_target = units // 2 + 1
    single_ids, single_block_s = logical_block(db, "id=?", (single_target,), "DELETE_SINGLE")
    blocked_visible = db.execute("SELECT count(*) FROM content_unit WHERE id=? AND active=1", (single_target,)).fetchone()[0]
    source_target = max(1, sources // 3)
    source_ids, source_block_s = logical_block(db, "source_id=? AND active=1", (source_target,), "DISCONNECT_SOURCE")
    db.execute("UPDATE source SET connected=0 WHERE id=?", (source_target,))
    db.commit()
    one_percent_ids, batch_block_s = logical_block(db, "id<=? AND id%100=50 AND active=1", (units,), "DELETE_BATCH_1PCT")
    # Current active view remains safe even with stale FTS postings; rebuild removes them physically.
    stale_active_leaks = db.execute("SELECT count(*) FROM content_unit c JOIN tombstone t ON t.content_id=c.id WHERE c.active=1").fetchone()[0]
    controls = sorted(set(single_ids + source_ids + one_percent_ids))
    cleanup_start = now()
    empty_digest = hashlib.sha256(b"").hexdigest()
    with db:
        db.execute("UPDATE content_unit SET original_text='', content_hash=? WHERE active=0", (empty_digest,))
        db.execute("DELETE FROM chunk WHERE active=0")
    physical_cleanup_s = round(now() - cleanup_start, 3)
    remaining_recoverable = db.execute("SELECT count(*) FROM content_unit WHERE id IN (SELECT content_id FROM tombstone) AND original_text!=''").fetchone()[0]
    fts_rebuild_s = rebuild_fts(db)
    fts_integrity_start = now()
    db.execute("INSERT INTO chunk_fts(chunk_fts) VALUES('integrity-check')")
    db.commit()
    fts_integrity_s = round(now() - fts_integrity_start, 3)
    fts_deleted_hits = db.execute("""SELECT count(*) FROM chunk_fts JOIN chunk ch ON ch.id=chunk_fts.rowid
                                      JOIN tombstone t ON t.content_id=ch.content_id WHERE chunk_fts MATCH 'synthetic' AND ch.active=1""").fetchone()[0]
    db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    checksum = checksum_scan(db)
    backup = backup_restore(tier_dir, controls, backup_s, backup_bytes)
    maintenance_probe = concurrent_rebuild_capture_probe(tier_dir / "restored.db", units + 500_000)
    query_plan = [list(row) for row in db.execute("EXPLAIN QUERY PLAN SELECT id FROM content_unit WHERE project_id=1 AND active=1 AND authorization_state='allowed' AND evidence_state='valid' ORDER BY created_day DESC LIMIT 100")]
    fts_plan = [list(row) for row in db.execute("EXPLAIN QUERY PLAN SELECT c.id FROM chunk_fts JOIN chunk ch ON ch.id=chunk_fts.rowid JOIN content_unit c ON c.id=ch.content_id WHERE chunk_fts MATCH 'topic42' AND c.project_id=1 AND c.active=1 LIMIT 20")]
    db.commit()
    sizes = db_sizes(tier_dir)
    assertions = {
        "integrity_ok": integrity == "ok",
        "content_count": counts["content_unit"] == units,
        "chunk_count": counts["chunk"] == units * 3,
        "single_delete_immediate_block": blocked_visible == 0,
        "tombstone_active_leaks_zero": stale_active_leaks == 0,
        "physical_cleanup_removed_controlled_originals": remaining_recoverable == 0,
        "restore_replay_active_leaks_zero": backup["post_replay_active_leaks"] == 0,
        "restored_integrity_ok": backup["integrity"] == "ok",
        "wal_checkpoint_ok": checkpoint[0] == 0,
        "keyword_p95_under_spike_budget": queries["keyword_project_permission"][0]["p95_ms"] <= 500,
        "recovery_p95_under_spike_budget": queries["project_recovery_package"][0]["p95_ms"] <= 4000,
        "capture_p95_under_one_second": capture["p95_ms"] <= 1000,
        "capture_during_full_fts_rebuild_under_one_second": maintenance_probe["capture_under_1s"],
        "audit_minimal_shape": db.execute("SELECT count(*) FROM audit_entry WHERE length(scope_digest)!=24").fetchone()[0] == 0,
        "old_generation_not_active": db.execute("SELECT count(*) FROM content_unit WHERE generation<3 AND active=1").fetchone()[0] == 0,
    }
    result = {
        "tier": tier, "units": units, "chunks": units * 3, "seed": SEED,
        "projects": projects, "sources": sources, "counts_before_mutation": counts,
        "phase": phase, "queries": queries, "capture_incremental": capture,
        "deletion": {"single_count": len(single_ids), "single_block_s": single_block_s,
                     "source_count": len(source_ids), "source_block_s": source_block_s,
                     "batch_1pct_count": len(one_percent_ids), "batch_1pct_block_s": batch_block_s,
                     "active_leaks": stale_active_leaks, "physical_cleanup_s": physical_cleanup_s,
                     "recoverable_controlled_originals_after_cleanup": remaining_recoverable,
                     "fts_rebuild_s": fts_rebuild_s, "fts_integrity_s": fts_integrity_s,
                     "active_deleted_fts_hits_after_rebuild": fts_deleted_hits},
        "backup_restore": backup, "concurrent_maintenance_probe": maintenance_probe,
        "export_checksum_scan": checksum, "sizes": sizes,
        "peak_rss_bytes_process": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "query_plans": {"metadata": query_plan, "fts": fts_plan},
        "assertions": assertions, "pass": all(assertions.values()),
    }
    db.close()
    if not keep_work:
        for name in ("sp09.db", "sp09.db-wal", "sp09.db-shm", "backup.db", "restored.db", "restored.db-wal", "restored.db-shm"):
            p = tier_dir / name
            if p.exists(): p.unlink()
    return result


def environment():
    def cmd(args):
        try:
            return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
        except Exception:
            return "unavailable"
    mem = cmd(["sysctl", "-n", "hw.memsize"])
    disk = shutil.disk_usage(ROOT)
    return {
        "platform": platform.platform(), "machine": platform.machine(), "processor": cmd(["sysctl", "-n", "machdep.cpu.brand_string"]),
        "cpu_count": os.cpu_count(), "memory_bytes": int(mem) if mem.isdigit() else None,
        "disk_total_bytes": disk.total, "disk_free_bytes_at_start": disk.free,
        "python": sys.version.split()[0], "sqlite": sqlite3.sqlite_version,
        "fts5": sqlite3.connect(":memory:").execute("select sqlite_compileoption_used('ENABLE_FTS5')").fetchone()[0] == 1,
        "postgresql": "not tested: docker, psql and local PostgreSQL service unavailable",
        "data_policy": "deterministic synthetic identifiers/text only; no real paths, Vaults, prompts, outputs, vectors or user data",
    }


def write_outputs(results, env):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    payload = {"run_at_local": time.strftime("%Y-%m-%d %H:%M:%S %z"), "environment": env,
               "tiers": results, "vector_cost_estimates": vector_estimates(3_000_000),
               "overall_pass": all(r["pass"] for r in results)}
    (EVIDENCE / "results.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    with (EVIDENCE / "test_matrix.csv").open("w", newline="") as f:
        w = csv.writer(f); w.writerow(["tier", "assertion", "result"])
        for r in results:
            for name, passed in r["assertions"].items(): w.writerow([r["tier"], name, "PASS" if passed else "FAIL"])
    with (EVIDENCE / "vector_costs.csv").open("w", newline="") as f:
        rows = payload["vector_cost_estimates"]
        w = csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    evidence_text = (EVIDENCE / "results.json").read_text()
    checked_patterns = {
        "absolute_user_path": r"/Users/[^\s\"']+",
        "private_key": r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY",
        "raw_original_text_field": r'\"original_text\"\s*:',
        "raw_prompt_field": r'\"(?:prompt|model_output|embedding)\"\s*:',
    }
    privacy_matches = [{"category": name, "match": m.group(0)[:80]}
                       for name, pattern in checked_patterns.items()
                       for m in re.finditer(pattern, evidence_text, re.IGNORECASE)]
    privacy = {
        "files_scanned": ["results.json", "test_matrix.csv", "vector_costs.csv"],
        "forbidden_categories": ["real user text", "real absolute path", "real Vault name", "complete prompt/output", "embedding values"],
        "patterns": checked_patterns, "match_count": len(privacy_matches), "matches": privacy_matches,
        "note": "Generator emits controlled synthetic labels and aggregate metrics only. Absolute script path is omitted from evidence payload."
    }
    (EVIDENCE / "privacy_scan.json").write_text(json.dumps(privacy, indent=2) + "\n")
    failures = []
    for r in results:
        for name, passed in r["assertions"].items():
            if not passed: failures.append({"tier": r["tier"], "assertion": name})
    (EVIDENCE / "failure_samples.json").write_text(json.dumps({"failures": failures}, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tiers", default="10000,100000", help="comma-separated content-unit counts")
    parser.add_argument("--full", action="store_true", help="append 1,000,000 content / 3,000,000 chunk tier")
    parser.add_argument("--keep-work", action="store_true", help="retain generated DB, backup and restore files")
    args = parser.parse_args()
    units = [int(x) for x in args.tiers.split(",") if x.strip()]
    if args.full and 1_000_000 not in units: units.append(1_000_000)
    EVIDENCE.mkdir(parents=True, exist_ok=True); WORK.mkdir(parents=True, exist_ok=True)
    env = environment()
    if not env["fts5"]: raise SystemExit("SQLite FTS5 unavailable")
    results = []
    for count in units:
        print(f"SP-09 tier start: {count} units / {count*3} chunks", flush=True)
        result = run_tier(count, args.keep_work)
        results.append(result)
        print(f"SP-09 tier done: {count}; pass={result['pass']}; db={result['sizes']['sp09.db']}", flush=True)
        write_outputs(results, env)
    return 0 if all(r["pass"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
