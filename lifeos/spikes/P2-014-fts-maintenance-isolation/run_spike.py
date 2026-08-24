#!/usr/bin/env python3
"""LIFEOS-P2-014 deterministic FTS maintenance isolation spike.

This is a disposable validation harness, not product code or a frozen schema.
It uses only generated identifiers and synthetic text.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shutil
import sqlite3
import statistics
import threading
import time
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Tuple


SEED = 20260809
CHUNKS_PER_UNIT = 3
CAPTURE_THRESHOLD_MS = 1000.0
BASE_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = BASE_DIR / "evidence"
WORK_DIR = BASE_DIR / "work"


def percentile(values: Sequence[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def distribution(values: Sequence[float]) -> Dict[str, float]:
    return {
        "samples": len(values),
        "p50_ms": round(percentile(values, 0.50), 3),
        "p95_ms": round(percentile(values, 0.95), 3),
        "p99_ms": round(percentile(values, 0.99), 3),
        "max_ms": round(max(values) if values else 0.0, 3),
    }


def authority_connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=5.0, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def index_connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path), timeout=5.0, isolation_level=None)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def create_authority(path: Path, units: int) -> None:
    if path.exists():
        path.unlink()
    conn = authority_connect(path)
    conn.executescript(
        """
        CREATE TABLE content (
            id INTEGER PRIMARY KEY,
            source_id INTEGER NOT NULL,
            artifact_version INTEGER NOT NULL,
            body TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1,
            allowed INTEGER NOT NULL DEFAULT 1,
            restriction_generation INTEGER NOT NULL DEFAULT 1,
            tombstone_generation INTEGER NOT NULL DEFAULT 0
        );
        CREATE TABLE capture_receipt (
            receipt_id INTEGER PRIMARY KEY,
            content_id INTEGER NOT NULL UNIQUE,
            committed_at TEXT NOT NULL
        );
        """
    )
    batch: List[Tuple[int, int, str]] = []
    conn.execute("BEGIN IMMEDIATE")
    for content_id in range(1, units + 1):
        source_id = 1 + ((content_id * 17 + SEED) % max(10, units // 500))
        body = f"synthetic unit {content_id} token_{content_id % 997} project_{content_id % 127}"
        batch.append((content_id, source_id, body))
        if len(batch) >= 10000:
            conn.executemany(
                "INSERT INTO content(id, source_id, artifact_version, body) VALUES (?, ?, 1, ?)",
                batch,
            )
            batch.clear()
    if batch:
        conn.executemany(
            "INSERT INTO content(id, source_id, artifact_version, body) VALUES (?, ?, 1, ?)", batch
        )
    conn.execute("COMMIT")
    conn.close()


def create_index(path: Path) -> sqlite3.Connection:
    if path.exists():
        path.unlink()
    conn = index_connect(path)
    conn.executescript(
        """
        CREATE TABLE index_meta (
            singleton INTEGER PRIMARY KEY CHECK(singleton = 1),
            generation INTEGER NOT NULL,
            expected_chunks INTEGER NOT NULL,
            state TEXT NOT NULL,
            digest TEXT
        );
        CREATE VIRTUAL TABLE posting USING fts5(
            content_id UNINDEXED,
            indexed_restriction_generation UNINDEXED,
            chunk_no UNINDEXED,
            text
        );
        """
    )
    return conn


def chunks_for(row: Tuple[int, str, int]) -> Iterable[Tuple[int, int, int, str]]:
    content_id, body, restriction_generation = row
    for chunk_no in range(CHUNKS_PER_UNIT):
        yield (
            content_id,
            restriction_generation,
            chunk_no,
            f"{body} synthetic_chunk_{chunk_no}",
        )


def build_index(
    authority_path: Path,
    index_path: Path,
    units: int,
    generation: int,
    *,
    stop_after_chunks: int | None = None,
    failure_kind: str | None = None,
) -> Dict[str, object]:
    started = time.perf_counter()
    auth = authority_connect(authority_path)
    index = create_index(index_path)
    expected = units * CHUNKS_PER_UNIT
    index.execute(
        "INSERT INTO index_meta(singleton, generation, expected_chunks, state) VALUES (1, ?, ?, 'building')",
        (generation, expected),
    )
    inserted = 0
    batch: List[Tuple[int, int, int, str]] = []
    failed = False
    failure = None
    try:
        cursor = auth.execute(
            "SELECT id, body, restriction_generation FROM content WHERE id <= ? ORDER BY id", (units,)
        )
        index.execute("BEGIN IMMEDIATE")
        for row in cursor:
            batch.extend(chunks_for(row))
            if len(batch) >= 6000:
                if stop_after_chunks and inserted + len(batch) >= stop_after_chunks:
                    raise OSError(failure_kind or "simulated interruption")
                index.executemany(
                    "INSERT INTO posting(content_id, indexed_restriction_generation, chunk_no, text) VALUES (?, ?, ?, ?)",
                    batch,
                )
                inserted += len(batch)
                batch.clear()
        if batch:
            index.executemany(
                "INSERT INTO posting(content_id, indexed_restriction_generation, chunk_no, text) VALUES (?, ?, ?, ?)",
                batch,
            )
            inserted += len(batch)
        index.execute("COMMIT")
        digest = hashlib.sha256(f"{generation}:{inserted}:{SEED}".encode()).hexdigest()
        index.execute(
            "UPDATE index_meta SET state='built', digest=? WHERE singleton=1", (digest,)
        )
    except (OSError, sqlite3.Error) as exc:
        failed = True
        failure = str(exc)
        try:
            index.execute("ROLLBACK")
        except sqlite3.Error:
            pass
        index.execute("UPDATE index_meta SET state='failed' WHERE singleton=1")
    finally:
        auth.close()
        index.close()
    return {
        "seconds": round(time.perf_counter() - started, 3),
        "inserted_chunks": inserted if not failed else 0,
        "expected_chunks": expected,
        "failed": failed,
        "failure_kind": failure_kind if failed else None,
        "failure_reason": failure,
    }


def capture(authority_path: Path, content_id: int, *, inject_failure: bool = False) -> Tuple[bool, float]:
    conn = authority_connect(authority_path)
    started = time.perf_counter()
    acknowledged = False
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(
            "INSERT INTO content(id, source_id, artifact_version, body) VALUES (?, 999999, 1, ?)",
            (content_id, f"synthetic capture {content_id} token_capture"),
        )
        if inject_failure:
            raise sqlite3.OperationalError("simulated authority commit failure")
        conn.execute(
            "INSERT INTO capture_receipt(receipt_id, content_id, committed_at) VALUES (?, ?, 'synthetic-clock')",
            (content_id, content_id),
        )
        conn.execute("COMMIT")
        acknowledged = True
    except sqlite3.Error:
        try:
            conn.execute("ROLLBACK")
        except sqlite3.Error:
            pass
    finally:
        elapsed = (time.perf_counter() - started) * 1000.0
        conn.close()
    return acknowledged, elapsed


def capture_while(
    authority_path: Path,
    worker: threading.Thread,
    first_id: int,
    minimum_samples: int = 150,
) -> Dict[str, object]:
    waits: List[float] = []
    acknowledged = 0
    content_id = first_id
    while worker.is_alive() or len(waits) < minimum_samples:
        ack, elapsed = capture(authority_path, content_id)
        waits.append(elapsed)
        acknowledged += int(ack)
        content_id += 1
        time.sleep(0.001)
    worker.join()
    result: Dict[str, object] = distribution(waits)
    result.update(
        {
            "acknowledged": acknowledged,
            "failed": len(waits) - acknowledged,
            "_raw_waits_ms": waits,
        }
    )
    return result


def integrity(path: Path) -> str:
    conn = sqlite3.connect(str(path))
    value = conn.execute("PRAGMA integrity_check").fetchone()[0]
    conn.close()
    return value


def validate_index(path: Path, expected_chunks: int, generation: int) -> Dict[str, object]:
    started = time.perf_counter()
    conn = index_connect(path)
    row = conn.execute(
        "SELECT generation, expected_chunks, state, digest FROM index_meta WHERE singleton=1"
    ).fetchone()
    count = conn.execute("SELECT count(*) FROM posting").fetchone()[0]
    fts_check = "ok"
    try:
        conn.execute("INSERT INTO posting(posting) VALUES('integrity-check')")
    except sqlite3.Error as exc:
        fts_check = exc.__class__.__name__
    conn.close()
    valid = bool(
        row
        and row[0] == generation
        and row[1] == expected_chunks
        and row[2] == "built"
        and row[3]
        and count == expected_chunks
        and fts_check == "ok"
    )
    return {
        "valid": valid,
        "generation": row[0] if row else None,
        "chunks": count,
        "expected_chunks": expected_chunks,
        "fts_integrity": fts_check,
        "seconds": round(time.perf_counter() - started, 3),
    }


def create_registry(path: Path, initial_index: Path, generation: int) -> None:
    if path.exists():
        path.unlink()
    conn = sqlite3.connect(str(path), isolation_level=None)
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute(
        "CREATE TABLE active_index(singleton INTEGER PRIMARY KEY CHECK(singleton=1), generation INTEGER NOT NULL, relative_name TEXT NOT NULL)"
    )
    conn.execute(
        "INSERT INTO active_index(singleton, generation, relative_name) VALUES (1, ?, ?)",
        (generation, initial_index.name),
    )
    conn.close()


def switch_generation(registry_path: Path, expected_old: int, new_generation: int, new_index: Path) -> bool:
    conn = sqlite3.connect(str(registry_path), timeout=5.0, isolation_level=None)
    conn.execute("PRAGMA synchronous=FULL")
    conn.execute("BEGIN IMMEDIATE")
    cursor = conn.execute(
        "UPDATE active_index SET generation=?, relative_name=? WHERE singleton=1 AND generation=? AND ? > generation",
        (new_generation, new_index.name, expected_old, new_generation),
    )
    changed = cursor.rowcount == 1
    conn.execute("COMMIT")
    conn.close()
    return changed


def registry_state(path: Path) -> Tuple[int, str]:
    conn = sqlite3.connect(str(path))
    value = conn.execute("SELECT generation, relative_name FROM active_index WHERE singleton=1").fetchone()
    conn.close()
    return value[0], value[1]


def incremental_worker(index_path: Path, start_content_id: int, count: int) -> None:
    conn = index_connect(index_path)
    conn.execute("BEGIN IMMEDIATE")
    rows = []
    for offset in range(count):
        content_id = start_content_id + offset
        for chunk_no in range(CHUNKS_PER_UNIT):
            rows.append((content_id, 1, chunk_no, f"synthetic increment {content_id} chunk {chunk_no}"))
        if len(rows) >= 3000:
            conn.executemany(
                "INSERT INTO posting(content_id, indexed_restriction_generation, chunk_no, text) VALUES (?, ?, ?, ?)",
                rows,
            )
            rows.clear()
    if rows:
        conn.executemany(
            "INSERT INTO posting(content_id, indexed_restriction_generation, chunk_no, text) VALUES (?, ?, ?, ?)",
            rows,
        )
    conn.execute("COMMIT")
    conn.close()


def authoritative_filter(authority_path: Path, candidates: Sequence[Tuple[int, int]]) -> List[int]:
    conn = authority_connect(authority_path)
    accepted: List[int] = []
    for content_id, indexed_generation in candidates:
        row = conn.execute(
            "SELECT active, allowed, restriction_generation, tombstone_generation FROM content WHERE id=?",
            (content_id,),
        ).fetchone()
        if row and row[0] == 1 and row[1] == 1 and row[2] == indexed_generation and row[3] == 0:
            accepted.append(content_id)
    conn.close()
    return accepted


def leakage_probe(authority_path: Path, index_path: Path) -> Dict[str, int]:
    targets = {"permission": 11, "tombstone": 12, "restriction_generation": 13}
    conn = authority_connect(authority_path)
    conn.execute("BEGIN IMMEDIATE")
    conn.execute("UPDATE content SET allowed=0 WHERE id=?", (targets["permission"],))
    conn.execute(
        "UPDATE content SET active=0, tombstone_generation=2 WHERE id=?", (targets["tombstone"],)
    )
    conn.execute(
        "UPDATE content SET restriction_generation=restriction_generation+1 WHERE id=?",
        (targets["restriction_generation"],),
    )
    conn.execute("COMMIT")
    conn.close()

    idx = index_connect(index_path)
    leaks: Dict[str, int] = {}
    for kind, content_id in targets.items():
        candidates = idx.execute(
            "SELECT CAST(content_id AS INTEGER), CAST(indexed_restriction_generation AS INTEGER) FROM posting WHERE posting MATCH ? AND content_id=? LIMIT 10",
            (f'"unit {content_id}"', content_id),
        ).fetchall()
        leaks[kind] = len(authoritative_filter(authority_path, candidates))
    idx.close()
    return leaks


def failed_save_probe(authority_path: Path, first_id: int, attempts: int = 25) -> Dict[str, int]:
    acknowledged = 0
    for offset in range(attempts):
        ack, _ = capture(authority_path, first_id + offset, inject_failure=True)
        acknowledged += int(ack)
    conn = authority_connect(authority_path)
    committed = conn.execute(
        "SELECT count(*) FROM content WHERE id>=? AND id<?", (first_id, first_id + attempts)
    ).fetchone()[0]
    receipts = conn.execute(
        "SELECT count(*) FROM capture_receipt WHERE content_id>=? AND content_id<?",
        (first_id, first_id + attempts),
    ).fetchone()[0]
    conn.close()
    return {
        "attempts": attempts,
        "acknowledged": acknowledged,
        "committed": committed,
        "receipts": receipts,
        "false_saved": acknowledged if committed == 0 and receipts == 0 else attempts,
    }


def privacy_scan(paths: Sequence[Path]) -> Dict[str, object]:
    forbidden = ["/Users/", "/home/", "file://", "real-vault", "prompt_payload", "model_output"]
    hits: List[Dict[str, str]] = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for marker in forbidden:
            if marker in text:
                hits.append({"file": path.name, "marker": marker})
    return {"files_scanned": len(paths), "forbidden_hits": hits, "hit_count": len(hits)}


def run_tier(label: str, units: int) -> Dict[str, object]:
    tier_dir = WORK_DIR / label
    if tier_dir.exists():
        shutil.rmtree(tier_dir)
    tier_dir.mkdir(parents=True)
    authority_path = tier_dir / "authority.db"
    old_index = tier_dir / "index-g1.db"
    shadow_index = tier_dir / "index-g2.db"
    registry = tier_dir / "registry.db"

    tier_started = time.perf_counter()
    create_authority(authority_path, units)
    old_build = build_index(authority_path, old_index, units, 1)
    old_validation = validate_index(old_index, units * CHUNKS_PER_UNIT, 1)
    create_registry(registry, old_index, 1)

    incremental = threading.Thread(
        target=incremental_worker, args=(old_index, 1, max(2000, units // 100))
    )
    incremental.start()
    incremental_capture = capture_while(authority_path, incremental, units + 20_000_000)

    shadow_holder: Dict[str, object] = {}
    shadow = threading.Thread(
        target=lambda: shadow_holder.update(build_index(authority_path, shadow_index, units, 2))
    )
    shadow.start()
    shadow_capture = capture_while(authority_path, shadow, units + 30_000_000)

    validation_holder: Dict[str, object] = {}
    validator = threading.Thread(
        target=lambda: validation_holder.update(
            validate_index(shadow_index, units * CHUNKS_PER_UNIT, 2)
        )
    )
    validator.start()
    validation_capture = capture_while(authority_path, validator, units + 40_000_000)

    before_switch = registry_state(registry)
    switched = bool(validation_holder.get("valid")) and switch_generation(registry, 1, 2, shadow_index)
    after_switch = registry_state(registry)
    stale_task_overwrite = switch_generation(registry, 2, 1, old_index)
    after_stale_attempt = registry_state(registry)

    # A failed validation never attempts a switch, so the valid generation remains active.
    invalid_shadow = tier_dir / "index-g3-invalid.db"
    invalid_result = build_index(
        authority_path,
        invalid_shadow,
        min(units, 5000),
        3,
        stop_after_chunks=6000,
        failure_kind="simulated validation failure",
    )
    invalid_validation = validate_index(invalid_shadow, units * CHUNKS_PER_UNIT, 3)
    invalid_switch_attempted = bool(invalid_validation["valid"])
    state_after_invalid = registry_state(registry)

    # Simulated ENOSPC and interruption occur only in disposable shadow files.
    enospc_shadow = tier_dir / "index-g4-enospc.db"
    interruption_shadow = tier_dir / "index-g5-interrupted.db"
    enospc = build_index(
        authority_path,
        enospc_shadow,
        min(units, 5000),
        4,
        stop_after_chunks=6000,
        failure_kind="simulated ENOSPC",
    )
    interrupted = build_index(
        authority_path,
        interruption_shadow,
        min(units, 5000),
        5,
        stop_after_chunks=6000,
        failure_kind="simulated rebuild interruption",
    )
    recovery_ack, recovery_wait = capture(authority_path, units + 50_000_000)
    authority_integrity = integrity(authority_path)
    active_integrity = integrity(tier_dir / after_switch[1])

    leakages = leakage_probe(authority_path, shadow_index)
    failed_saves = failed_save_probe(authority_path, units + 60_000_000)

    all_capture_results = [incremental_capture, shadow_capture, validation_capture]
    combined_raw_waits: List[float] = []
    for capture_result in all_capture_results:
        combined_raw_waits.extend(capture_result.pop("_raw_waits_ms"))
    combined_capture = distribution(combined_raw_waits)
    max_capture_wait = float(combined_capture["max_ms"])
    assertions = {
        "authority_capture_does_not_wait_for_long_index_transaction": max_capture_wait <= CAPTURE_THRESHOLD_MS,
        "capture_max_wait_under_one_second": max_capture_wait <= CAPTURE_THRESHOLD_MS,
        "saved_only_after_durable_authority_commit": failed_saves["false_saved"] == 0,
        "permission_leaks_zero": leakages["permission"] == 0,
        "tombstone_leaks_zero": leakages["tombstone"] == 0,
        "restriction_generation_leaks_zero": leakages["restriction_generation"] == 0,
        "switch_only_after_validation": switched and bool(validation_holder.get("valid")),
        "failed_switch_keeps_valid_old_index": (not invalid_switch_attempted) and state_after_invalid == after_switch,
        "space_failure_does_not_damage_authority_or_active_index": enospc["failed"] and authority_integrity == "ok" and active_integrity == "ok" and recovery_ack,
        "interruption_does_not_damage_authority_or_active_index": interrupted["failed"] and authority_integrity == "ok" and active_integrity == "ok",
        "old_generation_cannot_overwrite_higher_generation": (not stale_task_overwrite) and after_stale_attempt[0] == 2,
    }
    return {
        "tier": label,
        "units": units,
        "chunks": units * CHUNKS_PER_UNIT,
        "seed": SEED,
        "authority_setup_s": None,
        "old_index_build": old_build,
        "old_index_validation": old_validation,
        "incremental_maintenance_capture": incremental_capture,
        "shadow_rebuild": shadow_holder,
        "shadow_rebuild_capture": shadow_capture,
        "index_validation": validation_holder,
        "index_validation_capture": validation_capture,
        "combined_capture": combined_capture,
        "generation_switch": {
            "before": before_switch,
            "switched": switched,
            "after": after_switch,
            "stale_task_overwrite_succeeded": stale_task_overwrite,
            "after_stale_attempt": after_stale_attempt,
        },
        "failed_validation_rollback": {
            "build": invalid_result,
            "validation": invalid_validation,
            "switch_attempted": invalid_switch_attempted,
            "active_state_after": state_after_invalid,
        },
        "faults": {
            "space_exhaustion": enospc,
            "interruption": interrupted,
            "capture_after_fault_acknowledged": recovery_ack,
            "capture_after_fault_ms": round(recovery_wait, 3),
            "authority_integrity": authority_integrity,
            "active_index_integrity": active_integrity,
        },
        "failed_save_injection": failed_saves,
        "leakage_probe": leakages,
        "capture_combined_max_ms": max_capture_wait,
        "assertions": assertions,
        "p0_pass": all(assertions.values()),
        "seconds": round(time.perf_counter() - tier_started, 3),
        "file_sizes": {
            item.name: item.stat().st_size
            for item in tier_dir.iterdir()
            if item.is_file() and not item.name.endswith(("-wal", "-shm"))
        },
    }


def write_evidence(results: Dict[str, object]) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    results_path = EVIDENCE_DIR / "results.json"
    results_path.write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    matrix_lines = ["tier,assertion,result"]
    for tier in results["tiers"]:
        for assertion, passed in tier["assertions"].items():
            matrix_lines.append(f"{tier['tier']},{assertion},{'PASS' if passed else 'FAIL'}")
    (EVIDENCE_DIR / "test_matrix.csv").write_text("\n".join(matrix_lines) + "\n", encoding="utf-8")

    summary = {
        "started_at": results["started_at"],
        "completed_at": results["completed_at"],
        "tiers": [
            {
                "tier": tier["tier"],
                "units": tier["units"],
                "chunks": tier["chunks"],
                "p0_pass": tier["p0_pass"],
                "max_capture_wait_ms": tier["capture_combined_max_ms"],
                "false_saved": tier["failed_save_injection"]["false_saved"],
                "leakage_probe": tier["leakage_probe"],
            }
            for tier in results["tiers"]
        ],
        "overall_pass": results["overall_pass"],
    }
    summary_path = EVIDENCE_DIR / "execution_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    privacy = privacy_scan([results_path, summary_path, EVIDENCE_DIR / "test_matrix.csv"])
    (EVIDENCE_DIR / "privacy_scan.json").write_text(
        json.dumps(privacy, indent=2) + "\n", encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tiers",
        default="100000,1000000",
        help="comma-separated unit counts; every unit generates three chunks",
    )
    parser.add_argument("--keep-work", action="store_true")
    args = parser.parse_args()
    units_list = [int(value.strip()) for value in args.tiers.split(",") if value.strip()]
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    started_wall = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    started = time.perf_counter()
    tiers = [run_tier(f"u{units}", units) for units in units_list]
    results: Dict[str, object] = {
        "spike": "LIFEOS-P2-014",
        "started_at": started_wall,
        "completed_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "elapsed_s": round(time.perf_counter() - started, 3),
        "environment": {
            "platform": platform.platform(),
            "python": platform.python_version(),
            "sqlite": sqlite3.sqlite_version,
            "fts5": bool(sqlite3.connect(":memory:").execute("SELECT sqlite_compileoption_used('ENABLE_FTS5')").fetchone()[0]),
            "cpu_count": os.cpu_count(),
        },
        "tiers": tiers,
        "overall_pass": all(tier["p0_pass"] for tier in tiers),
    }
    write_evidence(results)
    privacy = json.loads((EVIDENCE_DIR / "privacy_scan.json").read_text())
    results["privacy_scan"] = privacy
    results["overall_pass"] = bool(results["overall_pass"] and privacy["hit_count"] == 0)
    (EVIDENCE_DIR / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    if not args.keep_work:
        shutil.rmtree(WORK_DIR)
    print(json.dumps({"overall_pass": results["overall_pass"], "elapsed_s": results["elapsed_s"]}))
    return 0 if results["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
