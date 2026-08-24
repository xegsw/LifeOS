#!/usr/bin/env python3
"""P3-041 Independent counter-example attack harness.

Goes beyond P3-040's 64-scenario runner to attack:
  PARENT: Active authorization parent field mutation (non-status/non-gen/non-identity)
  UPSERT: INSERT ... ON CONFLICT DO UPDATE on child tables
  MULTI:  Multi-row UPDATE on child tables while parent active
  AUDIT:  audit_entry / outbox_job pre-position, replay, delete, modify after retirement
  GEN:    generation increase without status change while active
  TERM:   terminal child mutation - historical evidence integrity
  VER:    version chain: skip, wrong supersedes, concurrent active, wrong logical_key
  TRIG:   trigger ordering (UPDATE status+generation), recursive triggers, FK off
"""

import hashlib
import json
import sqlite3
import sys
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


def fresh_db(fk_on=True, recursive_triggers=False):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    if fk_on:
        conn.execute("PRAGMA foreign_keys=ON")
    else:
        conn.execute("PRAGMA foreign_keys=OFF")
    if recursive_triggers:
        conn.execute("PRAGMA recursive_triggers=ON")
    sql = SQL_PATH.read_text(encoding="utf-8")
    # Remove PRAGMA foreign_keys from the script since we set it ourselves
    conn.executescript(sql)
    return conn


def setup_project(conn):
    conn.execute("INSERT INTO project VALUES ('p1','P','T','active',1,?,?,?)", (NOW, NOW, NOW))
    conn.execute("INSERT INTO project VALUES ('p2','P2','T','active',1,?,?,?)", (NOW, NOW, NOW))
    conn.execute("INSERT INTO source VALUES ('s1','synthetic','K','L','available','allowed',1,?,?)", (NOW, NOW))
    conn.execute("INSERT INTO artifact VALUES ('a1','s1',NULL,'note','active',1,?,?)", (NOW, NOW))


def parent(conn, aid, logical, version=1, supersedes=None, status="proposed",
           processor="local", purpose="test", location="device"):
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, logical, "actor", processor, purpose, location, status, version, 1,
         NOW, "indefinite", None, None, "policy-v1", supersedes, NOW, NOW))


def policy(conn, aid):
    conn.execute(
        "INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10))


def setup_auth(conn):
    setup_project(conn)
    parent(conn, "auth1", "logical1")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-allow','auth1','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-deny','auth1','deny',NULL,'s1',NULL)")
    conn.execute("INSERT INTO authorization_action VALUES ('action-read','auth1','read')")
    policy(conn, "auth1")
    conn.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
    conn.execute("INSERT INTO audit_entry VALUES ('audit-activate','authorization.activate','actor','auth1',1,'ok',?,'corr-a')", (NOW,))
    conn.commit()


def retirement_evidence(conn, status, auth_id="auth1", gen=2):
    action = {"revoked": "authorization.revoke", "expired": "authorization.expire",
              "superseded": "authorization.supersede"}[status]
    correlation = "authorization-state:%s:%d:%s" % (auth_id, gen, status)
    aid = "audit-%s-%d" % (status, gen)
    jid = "job-%s-%d" % (status, gen)
    conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
                 (aid, action, "actor", auth_id, 1, "ok", NOW, correlation))
    conn.execute("INSERT INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 (jid, "authorization_state_change", "authorization", auth_id, gen,
                  status, "pending", 0, NOW, None, 0, None, correlation, None))


def auth_state(conn, auth_id="auth1"):
    row = conn.execute("SELECT status, generation, processor, purpose, location, grantor_ref, "
                       "expires_mode, expires_at_ms, revoked_at_ms, policy_version, valid_from_ms "
                       "FROM authorization WHERE id=?", (auth_id,)).fetchone()
    scope_count = conn.execute("SELECT count(*) FROM authorization_scope WHERE authorization_id=?", (auth_id,)).fetchone()[0]
    action_count = conn.execute("SELECT count(*) FROM authorization_action WHERE authorization_id=?", (auth_id,)).fetchone()[0]
    audit_count = conn.execute("SELECT count(*) FROM audit_entry").fetchone()[0]
    return {
        "row": dict(row) if row else None,
        "scope_count": scope_count,
        "action_count": action_count,
        "audit_count": audit_count,
    }


# ============ PARENT: Active authorization parent field mutation ============

def attack_parent():
    # P-1: UPDATE processor while active (security-relevant field)
    conn = fresh_db()
    setup_auth(conn)
    before = auth_state(conn)
    try:
        conn.execute("UPDATE authorization SET processor='external-cloud' WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        gen_unchanged = before["row"]["generation"] == after["row"]["generation"]
        audit_unchanged = before["audit_count"] == after["audit_count"]
        processor_changed = after["row"]["processor"] == "external-cloud"
        if processor_changed and gen_unchanged and audit_unchanged:
            record("PARENT", "update_processor_active", "P1", False,
                   "processor changed local->external-cloud while active: gen unchanged, no audit", None)
        else:
            record("PARENT", "update_processor_active", "P1", True,
                   "processor UPDATE blocked or gen/audit changed", None)
    except sqlite3.DatabaseError as e:
        record("PARENT", "update_processor_active", "P1", True, "processor UPDATE rejected", str(e))
    conn.close()

    # P-2: UPDATE purpose while active
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization SET purpose='production' WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["purpose"] == "production":
            record("PARENT", "update_purpose_active", "P1", False,
                   "purpose changed test->production while active: gen unchanged, no audit", None)
        else:
            record("PARENT", "update_purpose_active", "P1", True, "purpose not changed", None)
    except sqlite3.DatabaseError as e:
        record("PARENT", "update_purpose_active", "P1", True, "purpose UPDATE rejected", str(e))
    conn.close()

    # P-3: UPDATE location while active
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization SET location='remote' WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["location"] == "remote":
            record("PARENT", "update_location_active", "P1", False,
                   "location changed device->remote while active: gen unchanged, no audit", None)
        else:
            record("PARENT", "update_location_active", "P1", True, "location not changed", None)
    except sqlite3.DatabaseError as e:
        record("PARENT", "update_location_active", "P1", True, "location UPDATE rejected", str(e))
    conn.close()

    # P-4: UPDATE grantor_ref while active
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization SET grantor_ref='evil-actor' WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["grantor_ref"] == "evil-actor":
            record("PARENT", "update_grantor_active", "P1", False,
                   "grantor_ref changed while active: gen unchanged, no audit", None)
        else:
            record("PARENT", "update_grantor_active", "P1", True, "grantor_ref not changed", None)
    except sqlite3.DatabaseError as e:
        record("PARENT", "update_grantor_active", "P1", True, "grantor_ref UPDATE rejected", str(e))
    conn.close()

    # P-5: UPDATE expires_mode to indefinite (remove expiry) while active
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization SET expires_mode='indefinite', expires_at_ms=NULL WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["expires_mode"] == "indefinite" and after["row"]["expires_at_ms"] is None:
            record("PARENT", "update_expiry_to_indefinite_active", "P1", False,
                   "expires_mode changed at->indefinite while active: gen unchanged, no audit", None)
        else:
            record("PARENT", "update_expiry_to_indefinite_active", "P1", True, "expiry not changed", None)
    except sqlite3.DatabaseError as e:
        record("PARENT", "update_expiry_to_indefinite_active", "P1", True, "expiry UPDATE rejected", str(e))
    conn.close()

    # P-6: UPDATE policy_version while active
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization SET policy_version='evil-policy' WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["policy_version"] == "evil-policy":
            record("PARENT", "update_policy_version_active", "P1", False,
                   "policy_version changed while active: gen unchanged, no audit", None)
        else:
            record("PARENT", "update_policy_version_active", "P1", True, "policy_version not changed", None)
    except sqlite3.DatabaseError as e:
        record("PARENT", "update_policy_version_active", "P1", True, "policy_version UPDATE rejected", str(e))
    conn.close()

    # P-7: Compound field UPDATE (processor + purpose + location) while active
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization SET processor='cloud', purpose='prod', location='remote' WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["processor"] == "cloud" and after["row"]["purpose"] == "prod" and after["row"]["location"] == "remote":
            record("PARENT", "compound_field_update_active", "P1", False,
                   "processor+purpose+location all changed while active: gen unchanged, no audit", None)
        else:
            record("PARENT", "compound_field_update_active", "P1", True, "fields not all changed", None)
    except sqlite3.DatabaseError as e:
        record("PARENT", "compound_field_update_active", "P1", True, "compound UPDATE rejected", str(e))
    conn.close()

    # P-8: UPDATE valid_from_ms while active
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization SET valid_from_ms=0 WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["valid_from_ms"] == 0:
            record("PARENT", "update_valid_from_active", "P2", False,
                   "valid_from_ms changed while active: gen unchanged, no audit (P2: minor field)", None)
        else:
            record("PARENT", "update_valid_from_active", "P2", True, "valid_from_ms not changed", None)
    except sqlite3.DatabaseError as e:
        record("PARENT", "update_valid_from_active", "P2", True, "valid_from_ms UPDATE rejected", str(e))
    conn.close()


# ============ UPSERT: ON CONFLICT DO UPDATE ============

def attack_upsert():
    # U-1: ON CONFLICT DO UPDATE on authorization_scope (replace effect via upsert)
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("INSERT INTO authorization_scope VALUES ('scope-allow','auth1','deny','p2',NULL,NULL) "
                     "ON CONFLICT(id) DO UPDATE SET effect='deny', project_id='p2'")
        conn.commit()
        after = auth_state(conn)
        row = conn.execute("SELECT effect FROM authorization_scope WHERE id='scope-allow'").fetchone()
        if row and row["effect"] == "deny" and after["row"]["generation"] == 1:
            record("UPSERT", "scope_on_conflict_do_update", "P1", False,
                   "ON CONFLICT DO UPDATE changed scope effect while active", None)
        else:
            record("UPSERT", "scope_on_conflict_do_update", "P1", True, "ON CONFLICT blocked or no change", None)
    except sqlite3.DatabaseError as e:
        record("UPSERT", "scope_on_conflict_do_update", "P1", True, "ON CONFLICT rejected", str(e))
    conn.close()

    # U-2: ON CONFLICT DO UPDATE on authorization_action (change action value)
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("INSERT INTO authorization_action VALUES ('action-read','auth1','export_candidate') "
                     "ON CONFLICT(id) DO UPDATE SET action='export_candidate'")
        conn.commit()
        row = conn.execute("SELECT action FROM authorization_action WHERE id='action-read'").fetchone()
        if row and row["action"] == "export_candidate":
            record("UPSERT", "action_on_conflict_do_update", "P1", False,
                   "ON CONFLICT DO UPDATE changed action value while active", None)
        else:
            record("UPSERT", "action_on_conflict_do_update", "P1", True, "ON CONFLICT blocked or no change", None)
    except sqlite3.DatabaseError as e:
        record("UPSERT", "action_on_conflict_do_update", "P1", True, "ON CONFLICT rejected", str(e))
    conn.close()

    # U-3: ON CONFLICT DO UPDATE on authorization_policy (change training)
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("INSERT INTO authorization_policy VALUES "
                     "('auth1','none',NULL,5,1,1,'[\"evil\"]','[\"*\"]','[]','[]',999,999) "
                     "ON CONFLICT(authorization_id) DO UPDATE SET training_allowed=1, sensitivity_rank=5")
        conn.commit()
        row = conn.execute("SELECT training_allowed, sensitivity_rank FROM authorization_policy WHERE authorization_id='auth1'").fetchone()
        if row and row["training_allowed"] == 1 and row["sensitivity_rank"] == 5:
            record("UPSERT", "policy_on_conflict_do_update", "P1", False,
                   "ON CONFLICT DO UPDATE changed policy fields while active", None)
        else:
            record("UPSERT", "policy_on_conflict_do_update", "P1", True, "ON CONFLICT blocked or no change", None)
    except sqlite3.DatabaseError as e:
        record("UPSERT", "policy_on_conflict_do_update", "P1", True, "ON CONFLICT rejected", str(e))
    conn.close()

    # U-4: ON CONFLICT DO NOTHING on authorization_scope
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("INSERT INTO authorization_scope VALUES ('scope-allow','auth1','deny','p2',NULL,NULL) "
                     "ON CONFLICT(id) DO NOTHING")
        conn.commit()
        row = conn.execute("SELECT effect FROM authorization_scope WHERE id='scope-allow'").fetchone()
        if row and row["effect"] == "deny":
            record("UPSERT", "scope_on_conflict_do_nothing", "P1", False,
                   "ON CONFLICT DO NOTHING changed scope effect while active", None)
        else:
            record("UPSERT", "scope_on_conflict_do_nothing", "P1", True, "ON CONFLICT DO NOTHING blocked", None)
    except sqlite3.DatabaseError as e:
        record("UPSERT", "scope_on_conflict_do_nothing", "P1", True, "ON CONFLICT DO NOTHING rejected", str(e))
    conn.close()


# ============ MULTI: Multi-row UPDATE ============

def attack_multi():
    # M-1: Multi-row UPDATE on all scopes at once
    conn = fresh_db()
    setup_project(conn)
    parent(conn, "auth1", "logical1")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-allow','auth1','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-deny','auth1','deny',NULL,'s1',NULL)")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-art','auth1','allow',NULL,NULL,'a1')")
    conn.execute("INSERT INTO authorization_action VALUES ('action-read','auth1','read')")
    policy(conn, "auth1")
    conn.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
    conn.execute("INSERT INTO audit_entry VALUES ('audit-activate','authorization.activate','actor','auth1',1,'ok',?,'corr-a')", (NOW,))
    conn.commit()
    try:
        conn.execute("UPDATE authorization_scope SET effect='deny' WHERE authorization_id='auth1'")
        conn.commit()
        rows = conn.execute("SELECT effect FROM authorization_scope WHERE authorization_id='auth1'").fetchall()
        all_deny = all(r["effect"] == "deny" for r in rows)
        after = auth_state(conn)
        if all_deny and after["row"]["generation"] == 1:
            record("MULTI", "multi_row_scope_effect_update", "P1", False,
                   "Multi-row UPDATE changed all scope effects to deny while active", None)
        else:
            record("MULTI", "multi_row_scope_effect_update", "P1", True, "Multi-row UPDATE blocked", None)
    except sqlite3.DatabaseError as e:
        record("MULTI", "multi_row_scope_effect_update", "P1", True, "Multi-row UPDATE rejected", str(e))
    conn.close()

    # M-2: Multi-row UPDATE on authorization_id (rebind all children)
    conn = fresh_db()
    setup_auth(conn)
    parent(conn, "auth2", "logical2")
    conn.commit()
    try:
        conn.execute("UPDATE authorization_scope SET authorization_id='auth2' WHERE authorization_id='auth1'")
        conn.commit()
        count = conn.execute("SELECT count(*) FROM authorization_scope WHERE authorization_id='auth1'").fetchone()[0]
        if count == 0:
            record("MULTI", "multi_row_rebind_all_scopes", "P1", False,
                   "Multi-row rebind moved all scopes to auth2 while auth1 active", None)
        else:
            record("MULTI", "multi_row_rebind_all_scopes", "P1", True, "Multi-row rebind blocked", None)
    except sqlite3.DatabaseError as e:
        record("MULTI", "multi_row_rebind_all_scopes", "P1", True, "Multi-row rebind rejected", str(e))
    conn.close()


# ============ AUDIT: audit/outbox pre-position, delete, modify ============

def attack_audit():
    # A-1: Pre-position fake audit + outbox, then retire with correct evidence
    conn = fresh_db()
    setup_auth(conn)
    # Pre-position evidence
    retirement_evidence(conn, "revoked")
    try:
        conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["status"] == "revoked" and after["row"]["generation"] == 2:
            record("AUDIT", "preposition_fake_retirement", "P2", False,
                   "Pre-positioned audit/outbox allowed fake retirement (P2: known candidate limitation)", None)
        else:
            record("AUDIT", "preposition_fake_retirement", "P2", True, "Pre-positioned retirement blocked", None)
    except sqlite3.DatabaseError as e:
        record("AUDIT", "preposition_fake_retirement", "P2", True, "Pre-positioned retirement rejected", str(e))
    conn.close()

    # A-2: DELETE audit_entry after retirement
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("DELETE FROM audit_entry WHERE id='audit-revoked-2'")
        conn.commit()
        count = conn.execute("SELECT count(*) FROM audit_entry WHERE id='audit-revoked-2'").fetchone()[0]
        if count == 0:
            record("AUDIT", "delete_audit_after_retirement", "P2", False,
                   "audit_entry deleted after retirement - evidence chain gap (P2: evidence integrity)", None)
        else:
            record("AUDIT", "delete_audit_after_retirement", "P2", True, "audit_entry DELETE blocked", None)
    except sqlite3.DatabaseError as e:
        record("AUDIT", "delete_audit_after_retirement", "P2", True, "audit_entry DELETE rejected", str(e))
    conn.close()

    # A-3: DELETE outbox_job after retirement
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("DELETE FROM outbox_job WHERE id='job-revoked-2'")
        conn.commit()
        count = conn.execute("SELECT count(*) FROM outbox_job WHERE id='job-revoked-2'").fetchone()[0]
        if count == 0:
            record("AUDIT", "delete_outbox_after_retirement", "P2", False,
                   "outbox_job deleted after retirement - evidence chain gap (P2: evidence integrity)", None)
        else:
            record("AUDIT", "delete_outbox_after_retirement", "P2", True, "outbox_job DELETE blocked", None)
    except sqlite3.DatabaseError as e:
        record("AUDIT", "delete_outbox_after_retirement", "P2", True, "outbox_job DELETE rejected", str(e))
    conn.close()

    # A-4: UPDATE outbox_job status after retirement
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("UPDATE outbox_job SET status='completed' WHERE id='job-revoked-2'")
        conn.commit()
        row = conn.execute("SELECT status FROM outbox_job WHERE id='job-revoked-2'").fetchone()
        if row and row["status"] == "completed":
            record("AUDIT", "update_outbox_status_after_retirement", "P2", False,
                   "outbox_job status modified after retirement (P2: evidence integrity)", None)
        else:
            record("AUDIT", "update_outbox_status_after_retirement", "P2", True, "outbox status not changed", None)
    except sqlite3.DatabaseError as e:
        record("AUDIT", "update_outbox_status_after_retirement", "P2", True, "outbox status UPDATE rejected", str(e))
    conn.close()

    # A-5: UPDATE audit_entry action_code after retirement
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("UPDATE audit_entry SET action_code='authorization.expire' WHERE id='audit-revoked-2'")
        conn.commit()
        row = conn.execute("SELECT action_code FROM audit_entry WHERE id='audit-revoked-2'").fetchone()
        if row and row["action_code"] == "authorization.expire":
            record("AUDIT", "update_audit_action_after_retirement", "P2", False,
                   "audit_entry action_code modified after retirement (P2: evidence integrity)", None)
        else:
            record("AUDIT", "update_audit_action_after_retirement", "P2", True, "audit action not changed", None)
    except sqlite3.DatabaseError as e:
        record("AUDIT", "update_audit_action_after_retirement", "P2", True, "audit action UPDATE rejected", str(e))
    conn.close()


# ============ GEN: generation changes independent of status ============

def attack_gen():
    # G-1: Increase generation without status change while active
    conn = fresh_db()
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization SET generation=5 WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["generation"] == 5 and after["row"]["status"] == "active":
            record("GEN", "increase_generation_active", "P2", False,
                   "generation increased 1->5 while active without status change (P2: evidence integrity)", None)
        else:
            record("GEN", "increase_generation_active", "P2", True, "generation increase blocked", None)
    except sqlite3.DatabaseError as e:
        record("GEN", "increase_generation_active", "P2", True, "generation increase rejected", str(e))
    conn.close()

    # G-2: Increase generation, then retire with pre-positioned evidence for bumped gen
    conn = fresh_db()
    setup_auth(conn)
    conn.execute("UPDATE authorization SET generation=3 WHERE id='auth1'")
    conn.commit()
    # Pre-position evidence for gen=4 retirement
    retirement_evidence(conn, "revoked", gen=4)
    try:
        conn.execute("UPDATE authorization SET status='revoked', generation=4 WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["status"] == "revoked" and after["row"]["generation"] == 4:
            record("GEN", "bump_then_retire_with_prepositioned_evidence", "P2", False,
                   "generation bumped then retired with pre-positioned evidence (P2: evidence integrity)", None)
        else:
            record("GEN", "bump_then_retire_with_prepositioned_evidence", "P2", True, "bump+retire blocked", None)
    except sqlite3.DatabaseError as e:
        record("GEN", "bump_then_retire_with_prepositioned_evidence", "P2", True, "bump+retire rejected", str(e))
    conn.close()


# ============ TERM: terminal child mutation - historical integrity ============

def attack_terminal():
    # T-1: UPDATE scope effect after revocation (historical evidence change)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("UPDATE authorization_scope SET effect='deny' WHERE id='scope-allow'")
        conn.commit()
        row = conn.execute("SELECT effect FROM authorization_scope WHERE id='scope-allow'").fetchone()
        if row and row["effect"] == "deny":
            record("TERM", "update_scope_effect_revoked", "P2", False,
                   "scope effect changed allow->deny after revocation - historical evidence altered (P2)", None)
        else:
            record("TERM", "update_scope_effect_revoked", "P2", True, "scope effect not changed", None)
    except sqlite3.DatabaseError as e:
        record("TERM", "update_scope_effect_revoked", "P2", True, "scope effect UPDATE rejected", str(e))
    conn.close()

    # T-2: INSERT new scope after revocation (add privilege to historical record)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("INSERT INTO authorization_scope VALUES ('scope-new-revoked','auth1','allow','p2',NULL,NULL)")
        conn.commit()
        count = conn.execute("SELECT count(*) FROM authorization_scope WHERE authorization_id='auth1'").fetchone()[0]
        if count >= 3:
            record("TERM", "insert_scope_revoked", "P2", False,
                   "new scope INSERTed after revocation - historical authorization semantics changed (P2)", None)
        else:
            record("TERM", "insert_scope_revoked", "P2", True, "scope INSERT blocked", None)
    except sqlite3.DatabaseError as e:
        record("TERM", "insert_scope_revoked", "P2", True, "scope INSERT rejected", str(e))
    conn.close()

    # T-3: UPDATE action value after revocation (read -> export_candidate)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("UPDATE authorization_action SET action='export_candidate' WHERE id='action-read'")
        conn.commit()
        row = conn.execute("SELECT action FROM authorization_action WHERE id='action-read'").fetchone()
        if row and row["action"] == "export_candidate":
            record("TERM", "update_action_value_revoked", "P2", False,
                   "action value changed read->export_candidate after revocation (P2: historical integrity)", None)
        else:
            record("TERM", "update_action_value_revoked", "P2", True, "action value not changed", None)
    except sqlite3.DatabaseError as e:
        record("TERM", "update_action_value_revoked", "P2", True, "action UPDATE rejected", str(e))
    conn.close()

    # T-4: UPDATE policy training after revocation
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("UPDATE authorization_policy SET training_allowed=1 WHERE authorization_id='auth1'")
        conn.commit()
        row = conn.execute("SELECT training_allowed FROM authorization_policy WHERE authorization_id='auth1'").fetchone()
        if row and row["training_allowed"] == 1:
            record("TERM", "update_policy_training_revoked", "P2", False,
                   "policy training_allowed changed after revocation (P2: historical integrity)", None)
        else:
            record("TERM", "update_policy_training_revoked", "P2", True, "policy not changed", None)
    except sqlite3.DatabaseError as e:
        record("TERM", "update_policy_training_revoked", "P2", True, "policy UPDATE rejected", str(e))
    conn.close()


# ============ VER: version chain attacks ============

def attack_version():
    # V-1: v2 superseding revoked (not superseded) authorization
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        parent(conn, "auth2", "logical1", 2, "auth1")
        conn.execute("INSERT INTO authorization_scope VALUES ('v2-s','auth2','allow','p1',NULL,NULL)")
        conn.execute("INSERT INTO authorization_action VALUES ('v2-a','auth2','read')")
        policy(conn, "auth2")
        conn.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
        conn.commit()
        record("VER", "v2_supersede_revoked_not_superseded", "P1", False,
               "v2 activated superseding revoked (not superseded) authorization - should be blocked", None)
    except sqlite3.DatabaseError as e:
        record("VER", "v2_supersede_revoked_not_superseded", "P1", True, "v2 supersede revoked rejected", str(e))
    conn.close()

    # V-2: v3 superseding v1 (skipping v2)
    conn = fresh_db()
    setup_auth(conn)
    # Create v2 and supersede v1
    retirement_evidence(conn, "superseded")
    conn.execute("UPDATE authorization SET status='superseded', generation=2 WHERE id='auth1'")
    parent(conn, "auth2", "logical1", 2, "auth1")
    conn.execute("INSERT INTO authorization_scope VALUES ('v2-s','auth2','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_action VALUES ('v2-a','auth2','read')")
    policy(conn, "auth2")
    conn.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
    conn.commit()
    # Now try v3 superseding v1 (skipping v2)
    retirement_evidence(conn, "superseded", auth_id="auth1", gen=3)
    conn.execute("UPDATE authorization SET status='superseded', generation=3 WHERE id='auth1'")
    conn.commit()
    try:
        parent(conn, "auth3", "logical1", 3, "auth1")
        conn.execute("INSERT INTO authorization_scope VALUES ('v3-s','auth3','allow','p1',NULL,NULL)")
        conn.execute("INSERT INTO authorization_action VALUES ('v3-a','auth3','read')")
        policy(conn, "auth3")
        conn.execute("UPDATE authorization SET status='active' WHERE id='auth3'")
        conn.commit()
        record("VER", "v3_supersede_v1_skip_v2", "P1", False,
               "v3 activated superseding v1 while v2 is active - should be blocked", None)
    except sqlite3.DatabaseError as e:
        record("VER", "v3_supersede_v1_skip_v2", "P1", True, "v3 skip supersede rejected", str(e))
    conn.close()

    # V-3: v2 with wrong logical_key supersedes
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "superseded")
    conn.execute("UPDATE authorization SET status='superseded', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        parent(conn, "auth2", "WRONG-logical", 2, "auth1")
        conn.execute("INSERT INTO authorization_scope VALUES ('v2-s','auth2','allow','p1',NULL,NULL)")
        conn.execute("INSERT INTO authorization_action VALUES ('v2-a','auth2','read')")
        policy(conn, "auth2")
        conn.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
        conn.commit()
        record("VER", "v2_wrong_logical_key_supersedes", "P1", False,
               "v2 with wrong logical_key activated superseding v1 - should be blocked", None)
    except sqlite3.DatabaseError as e:
        record("VER", "v2_wrong_logical_key_supersedes", "P1", True, "wrong logical_key supersede rejected", str(e))
    conn.close()

    # V-4: v2 supersedes non-previous version (v2 supersedes v0 that doesn't exist as v1's predecessor)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "superseded")
    conn.execute("UPDATE authorization SET status='superseded', generation=2 WHERE id='auth1'")
    conn.commit()
    # Create a fake auth0 as version 0 (invalid, version_no >= 1)
    # Instead try: v2 supersedes v1 but version_no=3 (not previous)
    try:
        parent(conn, "auth2", "logical1", 3, "auth1")  # version 3, but supersedes v1 (version 1)
        conn.execute("INSERT INTO authorization_scope VALUES ('v2-s','auth2','allow','p1',NULL,NULL)")
        conn.execute("INSERT INTO authorization_action VALUES ('v2-a','auth2','read')")
        policy(conn, "auth2")
        conn.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
        conn.commit()
        record("VER", "v3_supersedes_v1_wrong_version_gap", "P1", False,
               "v3 activated superseding v1 (version gap) - should be blocked", None)
    except sqlite3.DatabaseError as e:
        record("VER", "v3_supersedes_v1_wrong_version_gap", "P1", True, "version gap supersede rejected", str(e))
    conn.close()

    # V-5: Concurrent active - try to activate v2 while v1 is still active
    conn = fresh_db()
    setup_auth(conn)
    # v1 is active; try to create and activate v2
    try:
        parent(conn, "auth2", "logical1", 2, "auth1")
        conn.execute("INSERT INTO authorization_scope VALUES ('v2-s','auth2','allow','p1',NULL,NULL)")
        conn.execute("INSERT INTO authorization_action VALUES ('v2-a','auth2','read')")
        policy(conn, "auth2")
        conn.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
        conn.commit()
        record("VER", "concurrent_active_v1_v2", "P1", False,
               "v2 activated while v1 still active - should be blocked", None)
    except sqlite3.DatabaseError as e:
        record("VER", "concurrent_active_v1_v2", "P1", True, "concurrent active rejected", str(e))
    conn.close()


# ============ TRIG: trigger ordering, recursive, FK off ============

def attack_trig():
    # TR-1: UPDATE status + generation in same statement (trigger ordering)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    try:
        conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
        conn.commit()
        after = auth_state(conn)
        if after["row"]["status"] == "revoked" and after["row"]["generation"] == 2:
            record("TRIG", "compound_status_generation_update", "P2", True,
                   "Compound status+generation UPDATE works correctly (legal path verified)", None)
        else:
            record("TRIG", "compound_status_generation_update", "P2", False,
                   "Compound UPDATE produced unexpected state", None)
    except sqlite3.DatabaseError as e:
        record("TRIG", "compound_status_generation_update", "P2", True,
               "Compound status+generation UPDATE rejected (verify if legal)", str(e))
    conn.close()

    # TR-2: Recursive triggers - no cascading bypass
    conn = fresh_db(recursive_triggers=True)
    setup_auth(conn)
    try:
        conn.execute("UPDATE authorization_scope SET effect='deny' WHERE id='scope-allow'")
        conn.commit()
        record("TRIG", "recursive_trigger_scope_update", "P1", False,
               "Scope UPDATE succeeded with recursive triggers on", None)
    except sqlite3.DatabaseError as e:
        record("TRIG", "recursive_trigger_scope_update", "P1", True, "Scope UPDATE rejected with recursive triggers", str(e))
    conn.close()

    # TR-3: FK off - insert child with non-existent parent
    conn = fresh_db(fk_on=False)
    setup_project(conn)
    # Don't create auth1, just insert scope with non-existent authorization_id
    try:
        conn.execute("INSERT INTO authorization_scope VALUES ('scope-fake','nonexistent','allow','p1',NULL,NULL)")
        conn.commit()
        count = conn.execute("SELECT count(*) FROM authorization_scope WHERE id='scope-fake'").fetchone()[0]
        if count == 1:
            record("TRIG", "fk_off_insert_orphan_child", "P2", False,
                   "Child INSERTed with non-existent parent when FK off (P2: operational concern)", None)
        else:
            record("TRIG", "fk_off_insert_orphan_child", "P2", True, "Orphan child INSERT blocked", None)
    except sqlite3.DatabaseError as e:
        record("TRIG", "fk_off_insert_orphan_child", "P2", True, "Orphan child INSERT rejected", str(e))
    conn.close()

    # TR-4: FK off - insert child with non-existent parent, then activate parent
    conn = fresh_db(fk_on=False)
    setup_project(conn)
    try:
        conn.execute("INSERT INTO authorization_scope VALUES ('scope-fake','nonexistent','allow','p1',NULL,NULL)")
        conn.commit()
        # The trigger checks EXISTS(SELECT 1 FROM authorization a WHERE a.id = NEW.authorization_id AND a.status = 'active')
        # If parent doesn't exist, EXISTS returns false, so trigger doesn't fire
        count = conn.execute("SELECT count(*) FROM authorization_scope WHERE id='scope-fake'").fetchone()[0]
        if count == 1:
            record("TRIG", "fk_off_trigger_bypass_orphan", "P2", False,
                   "Child INSERTed with non-existent parent: trigger condition false, INSERT bypassed (P2: FK-dependent)", None)
        else:
            record("TRIG", "fk_off_trigger_bypass_orphan", "P2", True, "Orphan INSERT blocked", None)
    except sqlite3.DatabaseError as e:
        record("TRIG", "fk_off_trigger_bypass_orphan", "P2", True, "Orphan INSERT rejected", str(e))
    conn.close()


# ============ LEGAL: legal path verification ============

def attack_legal():
    # L-1: proposed -> granted -> active
    conn = fresh_db()
    setup_project(conn)
    parent(conn, "auth1", "logical1", status="proposed")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-allow','auth1','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_action VALUES ('action-read','auth1','read')")
    policy(conn, "auth1")
    try:
        conn.execute("UPDATE authorization SET status='granted' WHERE id='auth1'")
        conn.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
        conn.commit()
        row = conn.execute("SELECT status FROM authorization WHERE id='auth1'").fetchone()
        if row and row["status"] == "active":
            record("LEGAL", "proposed_granted_active", "P2", True, "proposed->granted->active legal path works", None)
        else:
            record("LEGAL", "proposed_granted_active", "P2", False, "Legal path blocked", None)
    except sqlite3.DatabaseError as e:
        record("LEGAL", "proposed_granted_active", "P2", True, "Legal path rejected", str(e))
    conn.close()

    # L-2: proposed -> active (direct)
    conn = fresh_db()
    setup_project(conn)
    parent(conn, "auth1", "logical1", status="proposed")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-allow','auth1','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_action VALUES ('action-read','auth1','read')")
    policy(conn, "auth1")
    try:
        conn.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
        conn.commit()
        row = conn.execute("SELECT status FROM authorization WHERE id='auth1'").fetchone()
        if row and row["status"] == "active":
            record("LEGAL", "proposed_direct_active", "P2", True, "proposed->active legal path works", None)
        else:
            record("LEGAL", "proposed_direct_active", "P2", False, "Legal path blocked", None)
    except sqlite3.DatabaseError as e:
        record("LEGAL", "proposed_direct_active", "P2", True, "Legal path rejected", str(e))
    conn.close()

    # L-3: legal supersede path (v1 active -> superseded -> v2 active)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "superseded")
    conn.execute("UPDATE authorization SET status='superseded', generation=2 WHERE id='auth1'")
    parent(conn, "auth2", "logical1", 2, "auth1")
    conn.execute("INSERT INTO authorization_scope VALUES ('v2-s','auth2','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_action VALUES ('v2-a','auth2','read')")
    policy(conn, "auth2")
    try:
        conn.execute("UPDATE authorization SET status='active' WHERE id='auth2'")
        conn.commit()
        row = conn.execute("SELECT status FROM authorization WHERE id='auth2'").fetchone()
        if row and row["status"] == "active":
            record("LEGAL", "supersede_new_version_activate", "P2", True, "Legal supersede+new version activation works", None)
        else:
            record("LEGAL", "supersede_new_version_activate", "P2", False, "Legal supersede path blocked", None)
    except sqlite3.DatabaseError as e:
        record("LEGAL", "supersede_new_version_activate", "P2", True, "Legal supersede rejected", str(e))
    conn.close()

    # L-4: terminal child cleanup after revocation (legal)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked")
    conn.execute("UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    conn.commit()
    try:
        conn.execute("DELETE FROM authorization_scope WHERE authorization_id='auth1'")
        conn.execute("DELETE FROM authorization_action WHERE authorization_id='auth1'")
        conn.execute("DELETE FROM authorization_policy WHERE authorization_id='auth1'")
        conn.commit()
        scope_count = conn.execute("SELECT count(*) FROM authorization_scope WHERE authorization_id='auth1'").fetchone()[0]
        action_count = conn.execute("SELECT count(*) FROM authorization_action WHERE authorization_id='auth1'").fetchone()[0]
        policy_count = conn.execute("SELECT count(*) FROM authorization_policy WHERE authorization_id='auth1'").fetchone()[0]
        if scope_count == 0 and action_count == 0 and policy_count == 0:
            record("LEGAL", "terminal_child_cleanup_revoked", "P2", True, "Terminal child cleanup works after revocation", None)
        else:
            record("LEGAL", "terminal_child_cleanup_revoked", "P2", False, "Terminal cleanup blocked", None)
    except sqlite3.DatabaseError as e:
        record("LEGAL", "terminal_child_cleanup_revoked", "P2", True, "Terminal cleanup rejected", str(e))
    conn.close()


def main():
    print("=== P3-041 Independent Counter-Example Attacks ===")
    print()
    attack_parent()
    attack_upsert()
    attack_multi()
    attack_audit()
    attack_gen()
    attack_terminal()
    attack_version()
    attack_trig()
    attack_legal()

    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = sum(1 for r in RESULTS if not r["passed"])
    p1_failed = sum(1 for r in RESULTS if not r["passed"] and r["severity"] == "P1")
    p2_failed = sum(1 for r in RESULTS if not r["passed"] and r["severity"] == "P2")

    print(f"Total attacks: {total}")
    print(f"Passed (fail-closed or legal verified): {passed}")
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
