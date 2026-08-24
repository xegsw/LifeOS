#!/usr/bin/env python3
"""P3-039 Independent counter-example attack harness.

Runs in an isolated temp copy of the candidate SQL. Attacks:
  P2-2: Tombstone DELETE / INSERT OR REPLACE / DELETE+INSERT (commit + rollback)
  P2-3: Tombstone non-accepted initial INSERT + illegal transitions
  P2-4: Active Authorization scope/action/policy DELETE + inactive cleanup
  ADJ-1: Active Authorization direct INSERT new scope/action/policy
  ADJ-2: Active Authorization UPDATE scope effect/target
  ADJ-3: Active Authorization authorization_id rebind
  ADJ-4: Active Authorization policy field direct UPDATE
  ADJ-5: Active Authorization scope UPDATE project_id/source_id/artifact_id target swap
  ADJ-6: Active Authorization action UPDATE action value
  ADJ-7: INSERT OR REPLACE on authorization_scope (effect change via PK replace)
  ADJ-8: Tombstone generation lower via UPDATE (existing trigger coverage check)
"""

import hashlib
import json
import os
import sqlite3
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SQL_PATH = SCRIPT_DIR / "candidate_schema.sql"
NOW = 1786550400000
RESULTS = []


def record(group, name, severity, passed, detail, error=None):
    RESULTS.append({
        "group": group,
        "name": name,
        "severity": severity,
        "passed": passed,
        "detail": detail,
        "sqlite_error": error,
    })


def fresh_db():
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    sql = SQL_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)
    return conn


def setup_tombstone_fixture(conn):
    """Create a tombstone in active_blocked state."""
    conn.execute("INSERT INTO project VALUES (?,?,?,?,?,?,?,?)",
        ("proj-1", "P", "TEST", "active", 1, NOW, NOW, NOW))
    conn.execute("INSERT INTO source VALUES (?,?,?,?,?,?,?,?,?)",
        ("src-1", "synthetic", "KEY1", "LOC1", "available", "allowed", 1, NOW, NOW))
    conn.execute("INSERT INTO artifact VALUES (?,?,?,?,?,?,?,?)",
        ("art-1", "src-1", None, "note", "active", 5, NOW, NOW))
    # Insert tombstone as accepted, then transition to active_blocked
    conn.execute("INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
        ("artifact", "art-1", 5, "cmd-1", "TEST", NOW, "accepted", NOW))
    conn.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_type='artifact' AND subject_id='art-1'")
    conn.commit()


def setup_auth_fixture(conn):
    """Create an active authorization with scope/action/policy children."""
    conn.execute("INSERT INTO project VALUES (?,?,?,?,?,?,?,?)",
        ("proj-1", "P", "TEST", "active", 1, NOW, NOW, NOW))
    conn.execute("INSERT INTO source VALUES (?,?,?,?,?,?,?,?,?)",
        ("src-1", "synthetic", "KEY1", "LOC1", "available", "allowed", 1, NOW, NOW))
    conn.execute("INSERT INTO artifact VALUES (?,?,?,?,?,?,?,?)",
        ("art-1", "src-1", None, "note", "active", 5, NOW, NOW))
    # Create authorization in proposed, add children, then activate
    conn.execute("INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("auth-1", "lk-1", "actor-1", "local", "test", "device", "proposed", 1, 1, NOW, "indefinite", None, None, "policy-v1", None, NOW, NOW))
    conn.execute("INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)",
        ("scope-allow", "auth-1", "allow", "proj-1", None, None))
    conn.execute("INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)",
        ("scope-deny", "auth-1", "deny", None, "src-1", None))
    conn.execute("INSERT INTO authorization_action VALUES (?,?,?)",
        ("action-read", "auth-1", "read"))
    conn.execute("INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        ("auth-1", "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10))
    conn.execute("UPDATE authorization SET status='active' WHERE id='auth-1'")
    conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
        ("audit-1", "authorization.activate", "actor-1", "auth-1", 1, "ok", NOW, "corr-1"))
    conn.commit()


def auth_state(conn, auth_id="auth-1"):
    row = conn.execute("SELECT status, generation FROM authorization WHERE id=?", (auth_id,)).fetchone()
    scope_count = conn.execute("SELECT count(*) FROM authorization_scope WHERE authorization_id=?", (auth_id,)).fetchone()[0]
    action_count = conn.execute("SELECT count(*) FROM authorization_action WHERE authorization_id=?", (auth_id,)).fetchone()[0]
    policy_count = conn.execute("SELECT count(*) FROM authorization_policy WHERE authorization_id=?", (auth_id,)).fetchone()[0]
    audit_count = conn.execute("SELECT count(*) FROM audit_entry").fetchone()[0]
    return {
        "status": dict(row) if row else None,
        "scope_count": scope_count,
        "action_count": action_count,
        "policy_count": policy_count,
        "audit_count": audit_count,
    }


# ============ P2-2: Tombstone DELETE / REPLACE / DELETE+INSERT ============

def attack_p2_2():
    # 1. Ordinary DELETE
    conn = fresh_db()
    setup_tombstone_fixture(conn)
    try:
        conn.execute("DELETE FROM tombstone WHERE subject_type='artifact' AND subject_id='art-1'")
        conn.commit()
        row = conn.execute("SELECT * FROM tombstone WHERE subject_id='art-1'").fetchone()
        record("P2-2", "ordinary_delete", "P1", False, "DELETE succeeded - tombstone removed", None)
    except sqlite3.DatabaseError as e:
        record("P2-2", "ordinary_delete", "P1", True, "DELETE rejected", str(e))
    conn.close()

    # 2. INSERT OR REPLACE with lower generation
    conn = fresh_db()
    setup_tombstone_fixture(conn)
    try:
        conn.execute("INSERT OR REPLACE INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "art-1", 4, "cmd-replace", "TEST", NOW, "accepted", NOW))
        conn.commit()
        record("P2-2", "insert_or_replace_lower_gen", "P1", False, "INSERT OR REPLACE succeeded - generation lowered", None)
    except sqlite3.DatabaseError as e:
        record("P2-2", "insert_or_replace_lower_gen", "P1", True, "INSERT OR REPLACE rejected", str(e))
    conn.close()

    # 3. INSERT OR REPLACE with same generation
    conn = fresh_db()
    setup_tombstone_fixture(conn)
    try:
        conn.execute("INSERT OR REPLACE INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "art-1", 5, "cmd-replace", "TEST", NOW, "accepted", NOW))
        conn.commit()
        record("P2-2", "insert_or_replace_same_gen", "P1", False, "INSERT OR REPLACE same gen succeeded", None)
    except sqlite3.DatabaseError as e:
        record("P2-2", "insert_or_replace_same_gen", "P1", True, "INSERT OR REPLACE same gen rejected", str(e))
    conn.close()

    # 4. INSERT OR REPLACE with higher generation
    conn = fresh_db()
    setup_tombstone_fixture(conn)
    try:
        conn.execute("INSERT OR REPLACE INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "art-1", 6, "cmd-replace", "TEST", NOW, "accepted", NOW))
        conn.commit()
        record("P2-2", "insert_or_replace_higher_gen", "P1", False, "INSERT OR REPLACE higher gen succeeded", None)
    except sqlite3.DatabaseError as e:
        record("P2-2", "insert_or_replace_higher_gen", "P1", True, "INSERT OR REPLACE higher gen rejected", str(e))
    conn.close()

    # 5. DELETE+INSERT in commit
    conn = fresh_db()
    setup_tombstone_fixture(conn)
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM tombstone WHERE subject_type='artifact' AND subject_id='art-1'")
        conn.execute("INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "art-1", 4, "cmd-reinsert", "TEST", NOW, "accepted", NOW))
        conn.commit()
        record("P2-2", "delete_insert_commit", "P1", False, "DELETE+INSERT commit succeeded - tombstone replaced", None)
    except sqlite3.DatabaseError as e:
        conn.rollback()
        record("P2-2", "delete_insert_commit", "P1", True, "DELETE+INSERT commit rejected", str(e))
    conn.close()

    # 6. DELETE+INSERT with rollback check
    conn = fresh_db()
    setup_tombstone_fixture(conn)
    baseline = conn.execute("SELECT * FROM tombstone WHERE subject_id='art-1'").fetchone()
    try:
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM tombstone WHERE subject_type='artifact' AND subject_id='art-1'")
        conn.execute("INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "art-1", 4, "cmd-rollback-test", "TEST", NOW, "accepted", NOW))
        record("P2-2", "delete_insert_rollback", "P1", False, "DELETE+INSERT succeeded in transaction", None)
    except sqlite3.DatabaseError as e:
        conn.rollback()
        after = conn.execute("SELECT * FROM tombstone WHERE subject_id='art-1'").fetchone()
        unchanged = dict(baseline) == dict(after)
        record("P2-2", "delete_insert_rollback", "P1", True and unchanged,
               f"DELETE+INSERT rejected and row unchanged after rollback: {unchanged}", str(e))
    conn.close()


# ============ P2-3: Tombstone initial status + transitions ============

def attack_p2_3():
    illegal_statuses = ["active_blocked", "cleaned", "cleanup_failed", "vendor_limited"]
    for status in illegal_statuses:
        conn = fresh_db()
        try:
            conn.execute("INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
                ("artifact", f"art-{status}", 1, "cmd-1", "TEST", NOW, status, NOW))
            conn.commit()
            record("P2-3", f"direct_insert_{status}", "P1", False, f"Non-accepted initial INSERT {status} succeeded", None)
        except sqlite3.DatabaseError as e:
            record("P2-3", f"direct_insert_{status}", "P1", True, f"Non-accepted initial INSERT {status} rejected", str(e))
        conn.close()

    # Legal: accepted start
    conn = fresh_db()
    try:
        conn.execute("INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
            ("artifact", "art-legal", 1, "cmd-1", "TEST", NOW, "accepted", NOW))
        conn.commit()
        record("P2-3", "accepted_start", "P1", True, "Accepted initial INSERT succeeded", None)
    except sqlite3.DatabaseError as e:
        record("P2-3", "accepted_start", "P1", False, "Accepted initial INSERT failed", str(e))
    conn.close()

    # Legal transitions: accepted -> active_blocked -> cleanup_pending -> cleaned
    conn = fresh_db()
    conn.execute("INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
        ("artifact", "art-trans", 1, "cmd-1", "TEST", NOW, "accepted", NOW))
    try:
        conn.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='art-trans'")
        conn.execute("UPDATE tombstone SET cleanup_status='cleanup_pending' WHERE subject_id='art-trans'")
        conn.execute("UPDATE tombstone SET cleanup_status='cleaned' WHERE subject_id='art-trans'")
        conn.commit()
        record("P2-3", "legal_transitions", "P1", True, "Legal transition chain succeeded", None)
    except sqlite3.DatabaseError as e:
        record("P2-3", "legal_transitions", "P1", False, "Legal transition chain failed", str(e))
    conn.close()

    # Illegal: accepted -> cleaned (skip)
    conn = fresh_db()
    conn.execute("INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
        ("artifact", "art-skip", 1, "cmd-1", "TEST", NOW, "accepted", NOW))
    try:
        conn.execute("UPDATE tombstone SET cleanup_status='cleaned' WHERE subject_id='art-skip'")
        conn.commit()
        record("P2-3", "illegal_skip_transition", "P1", False, "Illegal accepted->cleaned succeeded", None)
    except sqlite3.DatabaseError as e:
        record("P2-3", "illegal_skip_transition", "P1", True, "Illegal accepted->cleaned rejected", str(e))
    conn.close()

    # Illegal: generation decrease via UPDATE
    conn = fresh_db()
    conn.execute("INSERT INTO tombstone VALUES (?,?,?,?,?,?,?,?)",
        ("artifact", "art-gen", 5, "cmd-1", "TEST", NOW, "accepted", NOW))
    conn.execute("UPDATE tombstone SET cleanup_status='active_blocked' WHERE subject_id='art-gen'")
    try:
        conn.execute("UPDATE tombstone SET generation=3 WHERE subject_id='art-gen'")
        conn.commit()
        record("P2-3", "generation_decrease", "P1", False, "Generation decrease via UPDATE succeeded", None)
    except sqlite3.DatabaseError as e:
        record("P2-3", "generation_decrease", "P1", True, "Generation decrease via UPDATE rejected", str(e))
    conn.close()


# ============ P2-4: Active Authorization child DELETE ============

def attack_p2_4():
    # Active scope DELETE
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("DELETE FROM authorization_scope WHERE id='scope-allow'")
        conn.commit()
        record("P2-4", "active_scope_delete", "P1", False, "Active scope DELETE succeeded", None)
    except sqlite3.DatabaseError as e:
        after = auth_state(conn)
        unchanged = before == after
        record("P2-4", "active_scope_delete", "P1", True and unchanged,
               f"Active scope DELETE rejected, state unchanged: {unchanged}", str(e))
    conn.close()

    # Active action DELETE
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("DELETE FROM authorization_action WHERE id='action-read'")
        conn.commit()
        record("P2-4", "active_action_delete", "P1", False, "Active action DELETE succeeded", None)
    except sqlite3.DatabaseError as e:
        after = auth_state(conn)
        unchanged = before == after
        record("P2-4", "active_action_delete", "P1", True and unchanged,
               f"Active action DELETE rejected, state unchanged: {unchanged}", str(e))
    conn.close()

    # Active policy DELETE
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("DELETE FROM authorization_policy WHERE authorization_id='auth-1'")
        conn.commit()
        record("P2-4", "active_policy_delete", "P1", False, "Active policy DELETE succeeded", None)
    except sqlite3.DatabaseError as e:
        after = auth_state(conn)
        unchanged = before == after
        record("P2-4", "active_policy_delete", "P1", True and unchanged,
               f"Active policy DELETE rejected, state unchanged: {unchanged}", str(e))
    conn.close()

    # Inactive (revoked) scope DELETE should be ALLOWED
    conn = fresh_db()
    setup_auth_fixture(conn)
    conn.execute("UPDATE authorization SET status='revoked' WHERE id='auth-1'")
    conn.commit()
    try:
        conn.execute("DELETE FROM authorization_scope WHERE id='scope-allow'")
        conn.commit()
        record("P2-4", "inactive_scope_delete_allowed", "P2", True, "Inactive scope DELETE allowed (cleanup path)", None)
    except sqlite3.DatabaseError as e:
        record("P2-4", "inactive_scope_delete_allowed", "P2", False, "Inactive scope DELETE blocked - cleanup path locked", str(e))
    conn.close()


# ============ ADJ: Adjacent INSERT/UPDATE/rebind attacks ============

def attack_adjacent():
    # ADJ-1: Direct INSERT new scope while parent active
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("INSERT INTO authorization_scope VALUES (?,?,?,?,?,?)",
            ("scope-extra", "auth-1", "allow", None, None, "art-1"))
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "insert_new_scope_active", "P1", False,
                   "New allow scope INSERTed while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "insert_new_scope_active", "P2", True,
                   "New scope INSERTed but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "insert_new_scope_active", "P2", True, "New scope INSERT rejected", str(e))
    conn.close()

    # ADJ-1b: Direct INSERT new action while parent active
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("INSERT INTO authorization_action VALUES (?,?,?)",
            ("action-export", "auth-1", "export_candidate"))
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "insert_new_action_active", "P1", False,
                   "New action INSERTed while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "insert_new_action_active", "P2", True,
                   "New action INSERTed but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "insert_new_action_active", "P2", True, "New action INSERT rejected", str(e))
    conn.close()

    # ADJ-2: UPDATE scope effect from allow to deny while active
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("UPDATE authorization_scope SET effect='deny' WHERE id='scope-allow'")
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "update_scope_effect_active", "P1", False,
                   "Scope effect allow->deny UPDATE while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "update_scope_effect_active", "P2", True,
                   "Scope effect UPDATEed but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "update_scope_effect_active", "P2", True, "Scope effect UPDATE rejected", str(e))
    conn.close()

    # ADJ-2b: UPDATE scope target (project_id swap) while active
    conn = fresh_db()
    setup_auth_fixture(conn)
    conn.execute("INSERT INTO project VALUES (?,?,?,?,?,?,?,?)",
        ("proj-2", "P2", "TEST2", "active", 1, NOW, NOW, NOW))
    conn.commit()
    before = auth_state(conn)
    try:
        conn.execute("UPDATE authorization_scope SET project_id='proj-2' WHERE id='scope-allow'")
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "update_scope_target_active", "P1", False,
                   "Scope project_id swap while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "update_scope_target_active", "P2", True,
                   "Scope target UPDATEed but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "update_scope_target_active", "P2", True, "Scope target UPDATE rejected", str(e))
    conn.close()

    # ADJ-3: authorization_id rebind - move scope to different auth
    conn = fresh_db()
    setup_auth_fixture(conn)
    # Create a second authorization
    conn.execute("INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("auth-2", "lk-2", "actor-1", "local", "test2", "device", "proposed", 1, 1, NOW, "indefinite", None, None, "policy-v2", None, NOW, NOW))
    conn.commit()
    before = auth_state(conn)
    try:
        conn.execute("UPDATE authorization_scope SET authorization_id='auth-2' WHERE id='scope-allow'")
        conn.commit()
        after_auth1 = auth_state(conn, "auth-1")
        after_auth2 = auth_state(conn, "auth-2")
        # Check if auth-1 lost a scope without gen/audit change
        gen_unchanged = before["status"]["generation"] == after_auth1["status"]["generation"]
        audit_unchanged = before["audit_count"] == after_auth1["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "scope_rebind_active", "P1", False,
                   "Scope authorization_id rebind while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "scope_rebind_active", "P2", True,
                   "Scope rebind happened but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "scope_rebind_active", "P2", True, "Scope rebind rejected", str(e))
    conn.close()

    # ADJ-4: Policy field direct UPDATE while active
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("UPDATE authorization_policy SET training_allowed=1 WHERE authorization_id='auth-1'")
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "update_policy_training_active", "P1", False,
                   "Policy training_allowed UPDATE while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "update_policy_training_active", "P2", True,
                   "Policy UPDATEed but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "update_policy_training_active", "P2", True, "Policy UPDATE rejected", str(e))
    conn.close()

    # ADJ-4b: Policy sensitivity_rank UPDATE while active
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("UPDATE authorization_policy SET sensitivity_rank=5 WHERE authorization_id='auth-1'")
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "update_policy_sensitivity_active", "P1", False,
                   "Policy sensitivity_rank UPDATE while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "update_policy_sensitivity_active", "P2", True,
                   "Policy UPDATEed but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "update_policy_sensitivity_active", "P2", True, "Policy UPDATE rejected", str(e))
    conn.close()

    # ADJ-4c: Policy external_send_allowed UPDATE while active
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("UPDATE authorization_policy SET external_send_allowed=1 WHERE authorization_id='auth-1'")
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "update_policy_external_send_active", "P1", False,
                   "Policy external_send_allowed UPDATE while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "update_policy_external_send_active", "P2", True,
                   "Policy UPDATEed but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "update_policy_external_send_active", "P2", True, "Policy UPDATE rejected", str(e))
    conn.close()

    # ADJ-5: Action value UPDATE while active (read -> export_candidate)
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("UPDATE authorization_action SET action='export_candidate' WHERE id='action-read'")
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        if gen_unchanged and audit_unchanged:
            record("ADJ", "update_action_value_active", "P1", False,
                   "Action value read->export_candidate UPDATE while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "update_action_value_active", "P2", True,
                   "Action UPDATEed but gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "update_action_value_active", "P2", True, "Action value UPDATE rejected", str(e))
    conn.close()

    # ADJ-6: INSERT OR REPLACE on authorization_scope (PK replace to change effect)
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("INSERT OR REPLACE INTO authorization_scope VALUES (?,?,?,?,?,?)",
            ("scope-allow", "auth-1", "deny", "proj-1", None, None))
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        # Check if effect actually changed
        row = conn.execute("SELECT effect FROM authorization_scope WHERE id='scope-allow'").fetchone()
        effect_changed = row and row["effect"] == "deny"
        if effect_changed and gen_unchanged and audit_unchanged:
            record("ADJ", "insert_or_replace_scope_effect", "P1", False,
                   "INSERT OR REPLACE scope changed allow->deny while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "insert_or_replace_scope_effect", "P2", True,
                   "INSERT OR REPLACE scope did not silently change effect or gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "insert_or_replace_scope_effect", "P2", True, "INSERT OR REPLACE scope rejected", str(e))
    conn.close()

    # ADJ-7: INSERT OR REPLACE on authorization_policy (PK replace to change all fields)
    conn = fresh_db()
    setup_auth_fixture(conn)
    before = auth_state(conn)
    try:
        conn.execute("INSERT OR REPLACE INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            ("auth-1", "none", None, 5, 1, 1, "[\"evil\"]", "[\"*\"]", "[]", "[]", 999, 999))
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["status"]["generation"] == after["status"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        row = conn.execute("SELECT training_allowed, external_send_allowed, sensitivity_rank FROM authorization_policy WHERE authorization_id='auth-1'").fetchone()
        policy_changed = row and row["training_allowed"] == 1 and row["external_send_allowed"] == 1 and row["sensitivity_rank"] == 5
        if policy_changed and gen_unchanged and audit_unchanged:
            record("ADJ", "insert_or_replace_policy", "P1", False,
                   "INSERT OR REPLACE policy changed training/external_send/sensitivity while active: parent gen unchanged, no audit", None)
        else:
            record("ADJ", "insert_or_replace_policy", "P2", True,
                   "INSERT OR REPLACE policy did not silently change or gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("ADJ", "insert_or_replace_policy", "P2", True, "INSERT OR REPLACE policy rejected", str(e))
    conn.close()


def main():
    print("=== P3-039 Independent Counter-Example Attacks ===")
    print()
    attack_p2_2()
    attack_p2_3()
    attack_p2_4()
    attack_adjacent()

    # Summary
    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = sum(1 for r in RESULTS if not r["passed"])
    p1_failed = sum(1 for r in RESULTS if not r["passed"] and r["severity"] == "P1")
    p2_failed = sum(1 for r in RESULTS if not r["passed"] and r["severity"] == "P2")

    print(f"Total attacks: {total}")
    print(f"Passed (fail-closed): {passed}")
    print(f"Failed (bypass found): {failed}")
    print(f"P1 bypasses: {p1_failed}")
    print(f"P2 bypasses: {p2_failed}")
    print()

    for r in RESULTS:
        status = "PASS" if r["passed"] else "FAIL"
        print(f"  [{r['severity']}] {r['group']}/{r['name']}: {status}")
        if not r["passed"]:
            print(f"    DETAIL: {r['detail']}")
    print()

    # Write JSON results
    output = {
        "total_attacks": total,
        "passed": passed,
        "failed": failed,
        "p1_bypasses": p1_failed,
        "p2_bypasses": p2_failed,
        "results": RESULTS,
    }
    print("JSON_RESULTS:")
    print(json.dumps(output, ensure_ascii=False, indent=2))

    return 1 if p1_failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
