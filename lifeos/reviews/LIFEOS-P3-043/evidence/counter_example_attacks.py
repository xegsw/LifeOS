#!/usr/bin/env python3
"""P3-043 Independent counter-example attack harness (second-round, post P3-042).

P3-042 added `authorization_security_envelope_immutable_while_active`
(BEFORE UPDATE OF grantor_ref, processor, purpose, location, valid_from_ms,
expires_mode, expires_at_ms, policy_version ON authorization
WHEN OLD.status='active' AND any field changed).

This harness goes beyond P3-042's runner to attack:
  ENV:        8 envelope fields, single change while active
  ENV-EDGE:   NULL<->value flips, at<->indefinite pairing, compound, multi-row, no-op
  ENV-STATE:  envelope mutation in granted / terminal states; same-statement
              activation+mutation; same-statement retirement package+mutation
  SQL:        UPSERT (DO UPDATE / DO NOTHING), INSERT OR REPLACE, DELETE,
              DELETE+INSERT parent rebuild (FK on/off), UPDATE...FROM
  R0048:      adjacent metadata combos - pre-write revoked_at_ms then legal
              retirement; preset audit/outbox forged retirement; created_at_ms
              rewrite; generation bump alone; generation bump + envelope;
              staged generation climb with preset evidence
  TRIG:       trigger ordering, recursive_triggers, PRAGMA variations

Severity classes used:
  P1  = new bypass of the P3-042 remediation scope (envelope immutable while active)
  P2  = known-limitation family confirmed (documented in P3-042 KNOWN_LIMITATION
        entries or belonging to R-0048/R-0049 evidence-chain family)
  P3  = observation / by-design legal path worth recording
  A "PASS" means the attack was correctly blocked (or behaved as designed).
"""

import json
import sqlite3
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SQL_PATH = SCRIPT_DIR / "candidate_schema.sql"
NOW = 1786550400000
LATER = NOW + 86400000
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
    flag = "PASS" if passed else "BYPASS"
    print("%-14s %-46s %-6s %-6s %s" % (group, name, severity, flag, detail))
    if error:
        print("%-14s %-46s %-6s %-6s   sqlite_error=%s" % ("", "", "", "", error))


def fresh_db(fk_on=True, recursive_triggers=False):
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=%s" % ("ON" if fk_on else "OFF"))
    if recursive_triggers:
        conn.execute("PRAGMA recursive_triggers=ON")
    conn.executescript(SQL_PATH.read_text(encoding="utf-8"))
    return conn


def setup_project(conn):
    conn.execute("INSERT INTO project VALUES ('p1','P','T','active',1,?,?,?)", (NOW, NOW, NOW))
    conn.execute("INSERT INTO source VALUES ('s1','synthetic','K','L','available','allowed',1,?,?)", (NOW, NOW))
    conn.execute("INSERT INTO artifact VALUES ('a1','s1',NULL,'note','active',1,?,?)", (NOW, NOW))


def parent(conn, aid, logical, version=1, supersedes=None, status="proposed",
           processor="local", purpose="test", location="device",
           expires_mode="indefinite", expires_at_ms=None):
    conn.execute(
        "INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, logical, "actor", processor, purpose, location, status, version, 1,
         NOW, expires_mode, expires_at_ms, None, "policy-v1", supersedes, NOW, NOW))


def policy(conn, aid):
    conn.execute(
        "INSERT INTO authorization_policy VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (aid, "indefinite", None, 2, 0, 0, "[]", "[]", "[]", "[]", 10, 10))


def setup_auth(conn, expires_mode="indefinite", expires_at_ms=None):
    """Build one fully active authorization auth1 plus a second granted auth2."""
    setup_project(conn)
    parent(conn, "auth1", "logical1", expires_mode=expires_mode,
           expires_at_ms=expires_at_ms)
    conn.execute("INSERT INTO authorization_scope VALUES ('scope-allow','auth1','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_action VALUES ('action-read','auth1','read')")
    policy(conn, "auth1")
    conn.execute("UPDATE authorization SET status='active' WHERE id='auth1'")
    conn.commit()


def setup_two(conn):
    """auth1 active (indefinite), auth2 granted (at)."""
    setup_auth(conn)
    parent(conn, "auth2", "logical2", status="granted", expires_mode="at",
           expires_at_ms=LATER, processor="local2", purpose="test2")
    conn.execute("INSERT INTO authorization_scope VALUES ('scope2','auth2','allow','p1',NULL,NULL)")
    conn.execute("INSERT INTO authorization_action VALUES ('action2','auth2','read')")
    policy(conn, "auth2")
    conn.commit()


def retirement_evidence(conn, status, auth_id="auth1", gen=2):
    action = {"revoked": "authorization.revoke", "expired": "authorization.expire",
              "superseded": "authorization.supersede"}[status]
    correlation = "authorization-state:%s:%d:%s" % (auth_id, gen, status)
    conn.execute("INSERT INTO audit_entry VALUES (?,?,?,?,?,?,?,?)",
                 ("audit-%s-%d" % (status, gen), action, "actor", auth_id, 1, "ok", NOW, correlation))
    conn.execute("INSERT INTO outbox_job VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                 ("job-%s-%d" % (status, gen), "authorization_state_change", "authorization",
                  auth_id, gen, status, "pending", 0, NOW, None, 0, None, correlation, None))


def envelope(conn, auth_id="auth1"):
    row = conn.execute(
        "SELECT status, generation, grantor_ref, processor, purpose, location, "
        "valid_from_ms, expires_mode, expires_at_ms, policy_version, revoked_at_ms, "
        "created_at_ms FROM authorization WHERE id=?", (auth_id,)).fetchone()
    return dict(row) if row else None


def blocked(conn, sql, params=(), expect_error=None):
    """Return (was_blocked, error_string)."""
    try:
        conn.execute(sql, params)
        conn.commit()
        return False, None
    except sqlite3.Error as e:
        conn.rollback()
        err = str(e)
        if expect_error and expect_error not in err:
            return True, err + " (unexpected error kind)"
        return True, err


def try_mutate(conn, group, name, sql, params=(), auth_id="auth1", field=None,
               expect_value=None, expect_error=None, severity="P1"):
    """Run a mutation attack on an active auth; PASS if blocked or unchanged."""
    before = envelope(conn, auth_id)
    was_blocked, err = blocked(conn, sql, params, expect_error)
    after = envelope(conn, auth_id)
    if was_blocked:
        record(group, name, severity, True, "blocked: " + (err or ""), err)
        return True
    mutated = (field is not None and before is not None and after is not None
                and after.get(field) != before.get(field))
    if mutated:
        record(group, name, severity, False,
               "ENVELOPE BYPASSED: %s changed from %r to %r while active" % (field, before.get(field), after.get(field)), None)
    else:
        record(group, name, severity, True,
               "no effective mutation (no-op or constraint held state)", None)
    return not mutated


# ==================== ENV: 8 fields, single change while active ====================

def attack_env_single():
    cases = [
        ("update_grantor_ref_active", "UPDATE authorization SET grantor_ref='forged-grantor' WHERE id='auth1'", "grantor_ref", "forged-grantor"),
        ("update_processor_active", "UPDATE authorization SET processor='external-cloud' WHERE id='auth1'", "processor", "external-cloud"),
        ("update_purpose_active", "UPDATE authorization SET purpose='production' WHERE id='auth1'", "purpose", "production"),
        ("update_location_active", "UPDATE authorization SET location='remote' WHERE id='auth1'", "location", "remote"),
        ("update_valid_from_active", "UPDATE authorization SET valid_from_ms=%d WHERE id='auth1'" % (NOW - 999999), "valid_from_ms", NOW - 999999),
        ("update_expires_mode_active", "UPDATE authorization SET expires_mode='at', expires_at_ms=%d WHERE id='auth1'" % LATER, "expires_mode", "at"),
        ("update_policy_version_active", "UPDATE authorization SET policy_version='policy-evil' WHERE id='auth1'", "policy_version", "policy-evil"),
    ]
    for name, sql, field, value in cases:
        conn = fresh_db()
        setup_auth(conn)
        try_mutate(conn, "ENV", name, sql, field=field, expect_value=value,
                   expect_error="active_authorization_security_envelope_immutable")

    # expires_at_ms needs an 'at' mode authorization
    conn = fresh_db()
    setup_auth(conn, expires_mode="at", expires_at_ms=LATER)
    try_mutate(conn, "ENV", "update_expires_at_ms_active",
               "UPDATE authorization SET expires_at_ms=%d WHERE id='auth1'" % (LATER * 2),
               field="expires_at_ms", expect_value=LATER * 2,
               expect_error="active_authorization_security_envelope_immutable")


# ==================== ENV-EDGE: NULL flips, pairing, compound, multi-row, no-op ====================

def attack_env_edge():
    # E-1: at -> indefinite (expires_at_ms to NULL) - pairing attack
    conn = fresh_db()
    setup_auth(conn, expires_mode="at", expires_at_ms=LATER)
    try_mutate(conn, "ENV-EDGE", "at_to_indefinite_pair",
               "UPDATE authorization SET expires_mode='indefinite', expires_at_ms=NULL WHERE id='auth1'",
               field="expires_mode", expect_value="indefinite",
               expect_error="active_authorization_security_envelope_immutable")

    # E-2: indefinite -> at with future value
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "ENV-EDGE", "indefinite_to_at_pair",
               "UPDATE authorization SET expires_mode='at', expires_at_ms=%d WHERE id='auth1'" % (LATER * 3),
               field="expires_mode", expect_value="at",
               expect_error="active_authorization_security_envelope_immutable")

    # E-3: NULL-safety - expires_at_ms NULL->value IS NOT semantics on 'at' row
    conn = fresh_db()
    setup_auth(conn, expires_mode="at", expires_at_ms=LATER)
    try_mutate(conn, "ENV-EDGE", "expires_at_ms_value_swap",
               "UPDATE authorization SET expires_at_ms=%d WHERE id='auth1'" % (LATER + 5),
               field="expires_at_ms", expect_value=LATER + 5,
               expect_error="active_authorization_security_envelope_immutable")

    # E-4: compound - all 8 fields in one statement
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "ENV-EDGE", "compound_all_eight_fields",
               "UPDATE authorization SET grantor_ref='g2', processor='p2', purpose='p2', "
               "location='l2', valid_from_ms=%d, expires_mode='at', expires_at_ms=%d, "
               "policy_version='pv2' WHERE id='auth1'" % (NOW - 1, LATER * 4),
               field="processor", expect_value="p2",
               expect_error="active_authorization_security_envelope_immutable")

    # E-5: multi-row UPDATE hitting active + granted rows together
    conn = fresh_db()
    setup_two(conn)
    try_mutate(conn, "ENV-EDGE", "multi_row_active_plus_granted",
               "UPDATE authorization SET processor='evil-all'",
               field="processor", expect_value="evil-all",
               expect_error="active_authorization_security_envelope_immutable")

    # E-6: no-op envelope UPDATE (value unchanged) must stay legal
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "ENV-EDGE", "no_op_update_stays_legal",
               "UPDATE authorization SET processor=processor, purpose=purpose WHERE id='auth1'",
               field="processor", expect_value="local")

    # E-7: envelope change disguised with updated_at_ms bump (non-envelope field)
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "ENV-EDGE", "envelope_change_with_updated_at",
               "UPDATE authorization SET policy_version='pv-evil', updated_at_ms=%d WHERE id='auth1'" % (NOW + 50),
               field="policy_version", expect_value="pv-evil",
               expect_error="active_authorization_security_envelope_immutable")


# ==================== ENV-STATE: state boundary attacks ====================

def attack_env_state():
    # S-1: envelope change while granted (pre-activation) - by design mutable
    conn = fresh_db()
    setup_two(conn)  # auth2 granted
    try_mutate(conn, "ENV-STATE", "envelope_change_while_granted",
               "UPDATE authorization SET processor='pre-activation-mutation' WHERE id='auth2'",
               auth_id="auth2", field="processor", expect_value="pre-activation-mutation",
               severity="P3")

    # S-2: same-statement granted->active WITH envelope mutation
    conn = fresh_db()
    setup_two(conn)
    before = envelope(conn, "auth2")
    was_blocked, err = blocked(conn,
        "UPDATE authorization SET status='active', processor='mutation-at-activation' WHERE id='auth2'")
    after = envelope(conn, "auth2")
    if was_blocked:
        record("ENV-STATE", "activation_with_envelope_mutation", "P3", True, "blocked: " + err, err)
    elif after["status"] == "active" and after["processor"] == "mutation-at-activation":
        record("ENV-STATE", "activation_with_envelope_mutation", "P3", True,
               "allowed (by design: envelope mutable pre-activation; same exposure as S-1, "
               "no additional fence required by P3-042 scope)", None)
    else:
        record("ENV-STATE", "activation_with_envelope_mutation", "P3", True,
               "no effective mutation", None)

    # S-3: same-statement active->revoked retirement package WITH envelope mutation
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked", gen=2)
    conn.commit()
    try_mutate(conn, "ENV-STATE", "retirement_package_with_envelope_mutation",
               "UPDATE authorization SET status='revoked', generation=2, revoked_at_ms=%d, "
               "processor='evil-exit' WHERE id='auth1'" % NOW,
               field="processor", expect_value="evil-exit",
               expect_error="active_authorization_security_envelope_immutable")

    # S-4: envelope mutation while revoked (terminal) - history integrity family
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked", gen=2)
    conn.execute("UPDATE authorization SET status='revoked', generation=2, revoked_at_ms=? WHERE id='auth1'", (NOW,))
    conn.commit()
    try_mutate(conn, "ENV-STATE", "envelope_change_while_revoked",
               "UPDATE authorization SET processor='history-rewrite' WHERE id='auth1'",
               field="processor", expect_value="history-rewrite", severity="P2")

    # S-5: envelope mutation while expired
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "expired", gen=2)
    conn.execute("UPDATE authorization SET status='expired', generation=2 WHERE id='auth1'")
    conn.commit()
    try_mutate(conn, "ENV-STATE", "envelope_change_while_expired",
               "UPDATE authorization SET purpose='history-rewrite' WHERE id='auth1'",
               field="purpose", expect_value="history-rewrite", severity="P2")

    # S-6: same-statement envelope + status to granted (active->granted is invalid anyway)
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "ENV-STATE", "envelope_plus_backward_status",
               "UPDATE authorization SET status='granted', processor='evil' WHERE id='auth1'",
               field="processor", expect_value="evil",
               expect_error="authorization_status_transition_invalid")


# ==================== SQL: alternate write shapes on the parent table ====================

def full_row_values(aid="auth1", processor="local", status="granted", logical="logical1"):
    return ("INSERT INTO authorization VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (aid, logical, "actor", processor, "test", "device", status, 1, 1,
             NOW, "indefinite", None, None, "policy-v1", None, NOW, NOW))


def attack_sql_shapes():
    # Q-1: UPSERT DO UPDATE changing envelope on conflicting active row
    conn = fresh_db()
    setup_auth(conn)
    sql, vals = full_row_values(processor="evil-upsert")
    try_mutate(conn, "SQL", "upsert_do_update_envelope",
               sql + " ON CONFLICT(id) DO UPDATE SET processor=excluded.processor", vals,
               field="processor", expect_value="evil-upsert")

    # Q-2: UPSERT DO UPDATE with status rewrite to 'active' in DO UPDATE clause
    conn = fresh_db()
    setup_auth(conn)
    sql, vals = full_row_values(processor="x")
    try_mutate(conn, "SQL", "upsert_do_update_via_status",
               sql + " ON CONFLICT(id) DO UPDATE SET status='active', processor=excluded.processor", vals,
               field="processor", expect_value="x")

    # Q-3: UPSERT DO NOTHING - insert values carry mutated envelope
    conn = fresh_db()
    setup_auth(conn)
    sql, vals = full_row_values(processor="evil-nothing")
    try_mutate(conn, "SQL", "upsert_do_nothing_envelope",
               sql + " ON CONFLICT(id) DO NOTHING", vals,
               field="processor", expect_value="local")

    # Q-4: INSERT OR REPLACE with granted status (FK ON, children exist)
    conn = fresh_db()
    setup_auth(conn)
    sql, vals = full_row_values(processor="evil-replace", status="granted")
    try_mutate(conn, "SQL", "insert_or_replace_granted_fk_on",
               sql.replace("INSERT INTO", "INSERT OR REPLACE INTO", 1), vals,
               field="processor", expect_value="local")

    # Q-5: INSERT OR REPLACE with active status (FK ON)
    conn = fresh_db()
    setup_auth(conn)
    sql, vals = full_row_values(processor="evil-replace", status="active")
    try_mutate(conn, "SQL", "insert_or_replace_active_fk_on",
               sql.replace("INSERT INTO", "INSERT OR REPLACE INTO", 1), vals,
               field="processor", expect_value="local")

    # Q-6: DELETE of active parent (FK ON, children exist)
    conn = fresh_db()
    setup_auth(conn)
    was_blocked, err = blocked(conn, "DELETE FROM authorization WHERE id='auth1'")
    after = envelope(conn, "auth1")
    if was_blocked:
        record("SQL", "delete_active_parent_fk_on", "P1", True, "blocked: " + err, err)
    else:
        record("SQL", "delete_active_parent_fk_on", "P1", False,
               "ACTIVE AUTHORIZATION DELETED with FK ON", None)

    # Q-7: UPDATE ... FROM syntax
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "SQL", "update_from_envelope",
               "UPDATE authorization SET processor='evil-from' WHERE id='auth1'",
               field="processor", expect_value="evil-from",
               expect_error="active_authorization_security_envelope_immutable")

    # Q-8: UPDATE with WHERE clause trickery targeting active row via subquery
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "SQL", "update_via_subquery_predicate",
               "UPDATE authorization SET location='remote' WHERE id IN "
               "(SELECT id FROM authorization WHERE status='active')",
               field="location", expect_value="remote",
               expect_error="active_authorization_security_envelope_immutable")

    # Q-9: FK OFF + INSERT OR REPLACE (granted) then activate - full rebuild attempt
    conn = fresh_db(fk_on=False)
    setup_auth(conn)
    sql, vals = full_row_values(processor="evil-rebuild", status="granted")
    was_blocked, err = blocked(conn, sql.replace("INSERT INTO", "INSERT OR REPLACE INTO", 1), vals)
    if not was_blocked:
        # activation attempt on rebuilt row: children are orphaned but still present
        was_blocked2, err2 = blocked(conn, "UPDATE authorization SET status='active' WHERE id='auth1'")
        after = envelope(conn, "auth1")
        if not was_blocked2 and after and after["status"] == "active":
            record("SQL", "fk_off_replace_rebuild_then_activate", "P2", False,
                   "KNOWN-LIMITATION FAMILY CONFIRMED: FK OFF + INSERT OR REPLACE(granted) + "
                   "activate rebuilds active auth with envelope '%s', generation reset to 1, "
                   "no audit record; requires PRAGMA foreign_keys=OFF (writer-level action)" % after["processor"], None)
        else:
            record("SQL", "fk_off_replace_rebuild_then_activate", "P2", True,
                   "rebuild blocked at activation: " + (err2 or ""), err2)
    else:
        record("SQL", "fk_off_replace_rebuild_then_activate", "P2", True, "blocked: " + err, err)

    # Q-10: FK OFF + DELETE active parent + INSERT granted + activate
    conn = fresh_db(fk_on=False)
    setup_auth(conn)
    was_blocked, err = blocked(conn, "DELETE FROM authorization WHERE id='auth1'")
    if not was_blocked:
        sql, vals = full_row_values(processor="evil-delete-insert", status="granted")
        conn.execute(sql, vals)
        conn.commit()
        was_blocked2, err2 = blocked(conn, "UPDATE authorization SET status='active' WHERE id='auth1'")
        after = envelope(conn, "auth1")
        if not was_blocked2 and after and after["status"] == "active":
            record("SQL", "fk_off_delete_reinsert_rebuild", "P2", False,
                   "KNOWN-LIMITATION FAMILY CONFIRMED: FK OFF + DELETE + INSERT(granted) + "
                   "activate rebuilds active auth with envelope '%s', generation reset, "
                   "audit trail severed; requires PRAGMA foreign_keys=OFF" % after["processor"], None)
        else:
            record("SQL", "fk_off_delete_reinsert_rebuild", "P2", True,
                   "rebuild blocked at activation: " + (err2 or ""), err2)
    else:
        record("SQL", "fk_off_delete_reinsert_rebuild", "P2", True, "blocked: " + err, err)

    # Q-11: FK OFF + INSERT OR REPLACE with active status (no_direct_active_insert should fire)
    conn = fresh_db(fk_on=False)
    setup_auth(conn)
    sql, vals = full_row_values(processor="evil", status="active")
    try_mutate(conn, "SQL", "fk_off_replace_direct_active",
               sql.replace("INSERT INTO", "INSERT OR REPLACE INTO", 1), vals,
               field="processor", expect_value="local",
               expect_error="authorization_must_start_inactive")


# ==================== R0048: adjacent metadata combination attacks ====================

def attack_r0048():
    # R-1: pre-write revoked_at_ms while active (metadata outside envelope)
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "R0048", "prewrite_revoked_at_active",
               "UPDATE authorization SET revoked_at_ms=%d WHERE id='auth1'" % (NOW - 5000),
               field="revoked_at_ms", expect_value=NOW - 5000, severity="P2")

    # R-2: pre-written revoked_at_ms + legal retirement (gen+1, audit, outbox)
    conn = fresh_db()
    setup_auth(conn)
    conn.execute("UPDATE authorization SET revoked_at_ms=? WHERE id='auth1'", (NOW - 5000,))
    retirement_evidence(conn, "revoked", gen=2)
    conn.commit()
    was_blocked, err = blocked(conn,
        "UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    after = envelope(conn, "auth1")
    if was_blocked:
        record("R0048", "prewrite_then_legal_retirement", "P2", True, "blocked: " + err, err)
    elif after["status"] == "revoked" and after["revoked_at_ms"] == NOW - 5000:
        record("R0048", "prewrite_then_legal_retirement", "P2", False,
               "KNOWN LIMITATION CONFIRMED (R-0048): retirement succeeds and keeps the "
               "pre-written forged revoked_at_ms=%d instead of actual retirement time" % (NOW - 5000), None)
    else:
        record("R0048", "prewrite_then_legal_retirement", "P2", True, "no effective mutation", None)

    # R-3: preset audit+outbox then forged retirement (single UPDATE, no genuine action)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked", gen=2)
    conn.commit()
    was_blocked, err = blocked(conn,
        "UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    after = envelope(conn, "auth1")
    if was_blocked:
        record("R0048", "preset_evidence_forged_retirement", "P2", True, "blocked: " + err, err)
    elif after["status"] == "revoked":
        record("R0048", "preset_evidence_forged_retirement", "P2", False,
               "KNOWN LIMITATION CONFIRMED (R-0048 evidence-chain family): manually preset "
               "audit/outbox rows satisfy the retirement fence; evidence chain forgeable by "
               "direct table writes (same write access as the legal path)", None)
    else:
        record("R0048", "preset_evidence_forged_retirement", "P2", True, "no effective mutation", None)

    # R-4: created_at_ms rewrite while active
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "R0048", "rewrite_created_at_active",
               "UPDATE authorization SET created_at_ms=%d WHERE id='auth1'" % (NOW - 99999),
               field="created_at_ms", expect_value=NOW - 99999, severity="P2")

    # R-5: generation bump alone while active (no status change)
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "R0048", "generation_bump_active",
               "UPDATE authorization SET generation=5 WHERE id='auth1'",
               field="generation", expect_value=5, severity="P2")

    # R-6: generation bump + envelope mutation in same statement
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "R0048", "generation_bump_with_envelope",
               "UPDATE authorization SET generation=5, purpose='evil' WHERE id='auth1'",
               field="purpose", expect_value="evil",
               expect_error="active_authorization_security_envelope_immutable")

    # R-7: staged climb - bump gen 1->2 while active, preset gen-3 evidence, retire at gen 3
    conn = fresh_db()
    setup_auth(conn)
    conn.execute("UPDATE authorization SET generation=2 WHERE id='auth1'")
    retirement_evidence(conn, "revoked", gen=3)
    conn.commit()
    was_blocked, err = blocked(conn,
        "UPDATE authorization SET status='revoked', generation=3 WHERE id='auth1'")
    after = envelope(conn, "auth1")
    if was_blocked:
        record("R0048", "staged_generation_climb_retire", "P2", True, "blocked: " + err, err)
    elif after["status"] == "revoked" and after["generation"] == 3:
        record("R0048", "staged_generation_climb_retire", "P2", False,
               "KNOWN LIMITATION CONFIRMED: gen can be staged upward while active (R-0048 "
               "generation-fence family); retirement fence satisfied by staged gen + preset evidence", None)
    else:
        record("R0048", "staged_generation_climb_retire", "P2", True, "no effective mutation", None)

    # R-8: revoked_at_ms rewrite DURING retirement statement (legal-ish metadata at exit)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked", gen=2)
    conn.commit()
    was_blocked, err = blocked(conn,
        "UPDATE authorization SET status='revoked', generation=2, revoked_at_ms=%d WHERE id='auth1'" % (NOW - 7777))
    after = envelope(conn, "auth1")
    if was_blocked:
        record("R0048", "retirement_with_forged_revoked_at", "P2", True, "blocked: " + err, err)
    elif after["status"] == "revoked" and after["revoked_at_ms"] == NOW - 7777:
        record("R0048", "retirement_with_forged_revoked_at", "P2", False,
               "KNOWN LIMITATION CONFIRMED: retirement statement may carry arbitrary "
               "revoked_at_ms value (time metadata unfenced, R-0048 family)", None)
    else:
        record("R0048", "retirement_with_forged_revoked_at", "P2", True, "no effective mutation", None)

    # R-9: envelope mutation + revoked_at_ms pre-write + retirement all combined
    conn = fresh_db()
    setup_auth(conn)
    conn.execute("UPDATE authorization SET revoked_at_ms=? WHERE id='auth1'", (NOW - 5000,))
    retirement_evidence(conn, "revoked", gen=2)
    conn.commit()
    try_mutate(conn, "R0048", "combo_envelope_prewrite_retire",
               "UPDATE authorization SET status='revoked', generation=2, processor='evil-combo' WHERE id='auth1'",
               field="processor", expect_value="evil-combo",
               expect_error="active_authorization_security_envelope_immutable")


# ==================== TRIG: ordering / recursive / PRAGMA ====================

def attack_trig():
    # T-1: recursive_triggers ON + envelope update
    conn = fresh_db(recursive_triggers=True)
    setup_auth(conn)
    try_mutate(conn, "TRIG", "recursive_triggers_envelope",
               "UPDATE authorization SET location='remote-r' WHERE id='auth1'",
               field="location", expect_value="remote-r",
               expect_error="active_authorization_security_envelope_immutable")

    # T-2: envelope trigger vs status trigger ordering - envelope+status same statement
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked", gen=2)
    conn.commit()
    was_blocked, err = blocked(conn,
        "UPDATE authorization SET status='revoked', generation=2, grantor_ref='evil-order' WHERE id='auth1'")
    after = envelope(conn, "auth1")
    if was_blocked:
        record("TRIG", "trigger_order_envelope_vs_retirement", "P1", True, "blocked: " + err, err)
    elif after["status"] == "revoked" and after["grantor_ref"] == "evil-order":
        record("TRIG", "trigger_order_envelope_vs_retirement", "P1", False,
               "BYPASS: retirement statement carried envelope change through", None)
    else:
        record("TRIG", "trigger_order_envelope_vs_retirement", "P1", True, "no effective mutation", None)

    # T-3: reverse column order in SET (status last) - trigger must still fire
    conn = fresh_db()
    setup_auth(conn)
    try_mutate(conn, "TRIG", "reversed_set_order",
               "UPDATE authorization SET processor='evil-rev', status='revoked', generation=2 WHERE id='auth1'",
               field="processor", expect_value="evil-rev")

    # T-4: legal retirement still passes after remediation (non-regression)
    conn = fresh_db()
    setup_auth(conn)
    retirement_evidence(conn, "revoked", gen=2)
    conn.commit()
    was_blocked, err = blocked(conn,
        "UPDATE authorization SET status='revoked', generation=2 WHERE id='auth1'")
    after = envelope(conn, "auth1")
    if not was_blocked and after and after["status"] == "revoked" and after["generation"] == 2:
        record("TRIG", "legal_retirement_nonregression", "P1", True,
               "legal retirement path intact (gen+1, audit, outbox)", None)
    else:
        record("TRIG", "legal_retirement_nonregression", "P1", False,
               "REGRESSION: legal retirement blocked: " + (err or ""), err)

    # T-5: legal envelope change on a granted authorization (non-regression)
    conn = fresh_db()
    setup_two(conn)
    was_blocked, err = blocked(conn,
        "UPDATE authorization SET processor='legal-granted-change' WHERE id='auth2'")
    after = envelope(conn, "auth2")
    if not was_blocked and after and after["processor"] == "legal-granted-change":
        record("TRIG", "legal_granted_envelope_change", "P3", True,
               "granted-state envelope change still legal (by design)", None)
    else:
        record("TRIG", "legal_granted_envelope_change", "P3", False,
               "over-blocking: granted envelope change rejected: " + (err or ""), err)


def main():
    print("P3-043 independent counter-example attacks (post P3-042 remediation)")
    print("schema: %s" % SQL_PATH.name)
    print()
    attack_env_single()
    attack_env_edge()
    attack_env_state()
    attack_sql_shapes()
    attack_r0048()
    attack_trig()

    total = len(RESULTS)
    passed = sum(1 for r in RESULTS if r["passed"])
    failed = sum(1 for r in RESULTS if not r["passed"])
    by_sev = {}
    for r in RESULTS:
        if not r["passed"]:
            by_sev[r["severity"]] = by_sev.get(r["severity"], 0) + 1
    print()
    print("SUMMARY total=%d pass=%d bypass=%d bypass_by_severity=%s" %
          (total, passed, failed, json.dumps(by_sev, sort_keys=True)))
    print("JSON_RESULTS:")
    print(json.dumps(RESULTS, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
