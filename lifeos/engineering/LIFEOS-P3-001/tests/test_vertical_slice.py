import json
import re
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from src.lifeos_slice import FIXED_NOW, DisabledCapability, LifeOSSlice


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = ROOT / "fixtures" / "synthetic_v1.json"


def load_fixture():
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def populate(engine: LifeOSSlice):
    fixture = load_fixture()
    project_id = fixture["project"]["id"]
    for capture in fixture["captures"]:
        result = engine.capture(
            source_id=capture["source_id"], artifact_id=capture["artifact_id"], project_id=project_id,
            title=capture["title"], category=capture["category"], original_text=capture["original_text"],
            idempotency_key=capture["id"],
        )
        assert result["saved"]
    engine.process_index_jobs()
    return project_id


def populate_secondary(engine: LifeOSSlice):
    fixture = load_fixture()
    project_id = fixture["secondary_project"]["id"]
    for capture in fixture["secondary_captures"]:
        result = engine.capture(
            source_id=capture["source_id"], artifact_id=capture["artifact_id"], project_id=project_id,
            title=capture["title"], category=capture["category"], original_text=capture["original_text"],
            idempotency_key=capture["id"],
        )
        assert result["saved"]
    engine.process_index_jobs()
    return project_id


def authorization_context(engine: LifeOSSlice, artifact_id: str, project_id=None, **overrides):
    row = engine.db.execute(
        """SELECT a.project_id,a.current_version_id,a.generation,s.generation source_generation
           FROM artifact a JOIN source s ON s.id=a.source_id WHERE a.id=?""", (artifact_id,)
    ).fetchone()
    context = {
        "subject_id": artifact_id,
        "project_id": project_id if project_id is not None else row["project_id"],
        "expected_version_id": row["current_version_id"],
        "expected_generation": row["generation"],
        "expected_source_generation": row["source_generation"],
        "purpose": "lifeos_local_recovery", "location": "local", "processor": "local_rules", "now": FIXED_NOW,
    }
    context.update(overrides)
    return context


def authorization_contexts(engine: LifeOSSlice, project_id: str):
    ids = engine.db.execute("SELECT id FROM artifact WHERE project_id=? ORDER BY id", (project_id,)).fetchall()
    return {row["id"]: authorization_context(engine, row["id"], project_id) for row in ids}


def can_consume(engine: LifeOSSlice, artifact_id: str, project_id: str, **overrides):
    context = authorization_context(engine, artifact_id, project_id, **overrides)
    context.pop("subject_id")
    context.pop("project_id")
    return engine.can_consume(artifact_id, project_id=project_id, **context)


def read_artifact(engine: LifeOSSlice, artifact_id: str, project_id: str):
    return engine.read_artifact(
        artifact_id, project_id, authorization_context=authorization_context(engine, artifact_id, project_id)
    )


def search(engine: LifeOSSlice, query: str, project_id: str):
    return engine.search(query, project_id, authorization_contexts=authorization_contexts(engine, project_id))


def recovery_package(engine: LifeOSSlice, project_id: str):
    return engine.recovery_package(project_id, authorization_contexts=authorization_contexts(engine, project_id))


def suggest_next_step(engine: LifeOSSlice, project_id: str):
    return engine.suggest_next_step(project_id, authorization_contexts=authorization_contexts(engine, project_id))


def export_test_package(engine: LifeOSSlice, project_id: str, **kwargs):
    return engine.export_test_package(
        project_id, authorization_contexts=authorization_contexts(engine, project_id), **kwargs
    )


def restore_candidates(engine: LifeOSSlice, stale_package):
    return engine.restore_candidates(
        stale_package, authorization_contexts=authorization_contexts(engine, stale_package["project_id"])
    )


def add_feedback(engine: LifeOSSlice, project_id: str, derivation_id: str, kind: str, user_text=None):
    return engine.add_feedback(
        derivation_id, kind, user_text, project_id=project_id,
        authorization_contexts=authorization_contexts(engine, project_id),
    )


def add_important_link(engine: LifeOSSlice, project_id: str, link_id: str, from_id: str, to_id: str):
    return engine.add_important_link(
        link_id, from_id, to_id, "supports", True, project_id=project_id,
        authorization_contexts=authorization_contexts(engine, project_id),
    )


class VerticalSliceTests(unittest.TestCase):
    maxDiff = None
    evidence_assertions = {}

    def record_equal(self, case, actual, expected):
        def serializable(value):
            return sorted(value) if isinstance(value, set) else value

        test_id = self._testMethodName.replace("test_", "").replace("_", "-")
        self.evidence_assertions.setdefault(test_id, []).append({
            "case": case, "actual": serializable(actual), "expected": serializable(expected), "passed": actual == expected,
        })
        self.assertEqual(actual, expected)

    def test_T_SCOPE(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        package = recovery_package(engine, project_id)
        self.assertEqual(project_id, "project-synth-orbit")
        self.assertEqual(sum(len(package[k]) for k in ("stopping_point", "changes", "decisions", "unprocessed")), 4)
        self.assertFalse(any(engine.DISABLED_CAPABILITIES.values()))
        engine.close()

    def test_T_ID(self):
        for kind in ("confirm", "edit_confirm", "reject", "correct", "ignore"):
            engine = LifeOSSlice()
            project_id = populate(engine)
            candidate = suggest_next_step(engine, project_id)["candidate"]
            before = read_artifact(engine, "artifact-unprocessed", project_id)["original_text"]
            feedback = add_feedback(engine, project_id, candidate["id"], kind, "SYNTH_USER_EDIT" if kind in {"edit_confirm", "correct"} else None)
            after = read_artifact(engine, "artifact-unprocessed", project_id)["original_text"]
            self.assertEqual(before, after)
            self.assertEqual(feedback["kind"], kind)
            if kind == "edit_confirm":
                add_important_link(engine, project_id, "link-1", "artifact-decision", "artifact-unprocessed")
                counts = engine.semantic_counts()
                self.assertTrue(all(counts[key] > 0 for key in counts))
                with self.assertRaises(sqlite3.DatabaseError):
                    engine.db.execute("UPDATE artifact_version SET original_text='changed' WHERE id='artifact-unprocessed:v1'")
                engine.db.rollback()
                self.assertIsNone(engine.read_artifact("artifact-unprocessed", "another-project"))
            engine.close()

    def test_T_ID_CONFIRMATION_REGRESSION(self):
        for kind, expected_status in (("confirm", "confirmed"), ("edit_confirm", "edited_confirmed")):
            engine = LifeOSSlice()
            project_id = populate(engine)
            first = suggest_next_step(engine, project_id)["candidate"]
            feedback = add_feedback(engine, project_id, first["id"], kind, "SYNTH_EDIT" if kind == "edit_confirm" else None)
            repeated = suggest_next_step(engine, project_id)["candidate"]
            self.record_equal(f"{kind}:same_identity", repeated["id"], first["id"])
            self.record_equal(f"{kind}:status_preserved", repeated["status"], expected_status)
            row = engine.db.execute("SELECT * FROM feedback WHERE id=?", (feedback["feedback_id"],)).fetchone()
            self.record_equal(f"{kind}:feedback_trace_preserved", row["status"], "active")
            engine.capture(
                source_id=f"source-new-{kind}", artifact_id=f"artifact-new-{kind}", project_id=project_id,
                title="新增证据", category="decision", original_text=f"SYNTH_NEW_{kind}", idempotency_key=f"new-{kind}",
            )
            changed = suggest_next_step(engine, project_id)["candidate"]
            self.record_equal(f"{kind}:new_evidence_new_identity", changed["id"] != first["id"], True)
            old = engine.db.execute("SELECT status FROM derivation WHERE id=?", (first["id"],)).fetchone()
            self.record_equal(f"{kind}:old_confirmation_traceable", old["status"], expected_status)
            engine.close()

    def test_T_SAVE(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = str(Path(tmp) / "slice.sqlite3")
            engine = LifeOSSlice(db_path)
            failed = engine.capture(source_id="source-fail", artifact_id="artifact-fail", project_id="p", title="失败", category="change", original_text="SYNTH_FAIL", idempotency_key="fail", fail_authoritative=True)
            self.assertFalse(failed["saved"])
            self.assertEqual(engine.db.execute("SELECT COUNT(*) n FROM artifact WHERE id='artifact-fail'").fetchone()["n"], 0)
            ok = engine.capture(source_id="source-ok", artifact_id="artifact-ok", project_id="p", title="成功", category="change", original_text="SYNTH_SAVE", idempotency_key="ok")
            self.assertTrue(ok["saved"])
            self.assertEqual(engine.process_index_jobs(inject_failure=True)["failed"], 1)
            duplicate = engine.capture(source_id="source-other", artifact_id="artifact-other", project_id="p", title="重复", category="change", original_text="SYNTH_OTHER", idempotency_key="ok")
            self.assertTrue(duplicate["saved"] and duplicate["deduplicated"])
            engine.close()
            reopened = LifeOSSlice(db_path)
            self.assertEqual(read_artifact(reopened, "artifact-ok", "p")["original_text"], "SYNTH_SAVE")
            reopened.close()

    def test_T_SAVE_CRASH_BOUNDARY(self):
        with tempfile.TemporaryDirectory() as tmp:
            for boundary, return_code, should_exist in (("before_commit", 86, False), ("after_commit", 87, True)):
                db_path = str(Path(tmp) / f"{boundary}.sqlite3")
                script = (
                    "from src.lifeos_slice import LifeOSSlice; "
                    f"e=LifeOSSlice({db_path!r}); "
                    f"e.capture(source_id='s',artifact_id='a',project_id='p',title='t',category='change',"
                    f"original_text='SYNTH_CRASH',idempotency_key='k',_crash_at_for_test={boundary!r})"
                )
                completed = subprocess.run([sys.executable, "-c", script], cwd=ROOT, check=False)
                self.record_equal(f"{boundary}:process_exit", completed.returncode, return_code)
                reopened = LifeOSSlice(db_path)
                count = reopened.db.execute("SELECT COUNT(*) n FROM artifact WHERE id='a'").fetchone()["n"]
                self.record_equal(f"{boundary}:authoritative_visibility", count, 1 if should_exist else 0)
                submissions = reopened.db.execute("SELECT COUNT(*) n FROM submission WHERE artifact_id='a'").fetchone()["n"]
                self.record_equal(f"{boundary}:submission_atomicity", submissions, 1 if should_exist else 0)
                if should_exist:
                    self.record_equal(f"{boundary}:restart_read", read_artifact(reopened, "a", "p")["original_text"], "SYNTH_CRASH")
                    result = reopened.process_index_jobs(inject_failure=True)
                    self.record_equal(f"{boundary}:fts_failure_isolated", result["failed"], 1)
                    self.record_equal(f"{boundary}:authority_survives_fts_failure", read_artifact(reopened, "a", "p")["original_text"], "SYNTH_CRASH")
                reopened.close()
            derivation_engine = LifeOSSlice(str(Path(tmp) / "derivation-failure.sqlite3"))
            project_id = populate(derivation_engine)
            derivation_engine.db.execute(
                "CREATE TRIGGER fail_derivation_for_test BEFORE INSERT ON derivation "
                "BEGIN SELECT RAISE(ABORT, 'injected derivation failure'); END"
            )
            derivation_failed = False
            try:
                suggest_next_step(derivation_engine, project_id)
            except sqlite3.DatabaseError:
                derivation_failed = True
                derivation_engine.db.rollback()
            self.record_equal("derivation_failure_injected", derivation_failed, True)
            self.record_equal(
                "authority_survives_derivation_failure",
                read_artifact(derivation_engine, "artifact-unprocessed", project_id)["original_text"],
                "SYNTH_NOTE_004：待核对恢复候选是否保留来源与版本。",
            )
            derivation_engine.close()

    def test_T_GATE(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        self.assertTrue(can_consume(engine, "artifact-stop", project_id))
        self.assertFalse(can_consume(engine, "artifact-stop", "wrong-project"))
        engine.db.execute("UPDATE authorization SET expires_at='2020-01-01T00:00:00+00:00' WHERE subject_id='artifact-change'")
        engine.db.commit()
        self.assertFalse(can_consume(engine, "artifact-change", project_id))
        engine.db.execute("UPDATE authorization SET decision='deny' WHERE subject_id='artifact-decision'")
        engine.db.commit()
        self.assertFalse(can_consume(engine, "artifact-decision", project_id))
        engine.db.execute("UPDATE outbox_job SET status='pending',lease_generation=99 WHERE subject_id='artifact-stop'")
        engine.db.execute("UPDATE artifact SET generation=2 WHERE id='artifact-stop'")
        engine.db.commit()
        self.assertEqual(engine.process_index_jobs()["skipped"], 1)
        self.assertEqual(len(recovery_package(engine, project_id)["evidence_gaps"]), 3)
        engine.close()

    def test_T_GATE_AUTH_CONTEXT(self):
        mutations = (
            ("location_mismatch", "UPDATE authorization SET location='cloud' WHERE subject_id='artifact-stop'"),
            ("processor_mismatch", "UPDATE authorization SET processor='third_party' WHERE subject_id='artifact-stop'"),
            ("both_mismatch", "UPDATE authorization SET location='cloud',processor='third_party' WHERE subject_id='artifact-stop'"),
            ("unknown_location", "UPDATE authorization SET location='unknown' WHERE subject_id='artifact-stop'"),
            ("unknown_processor", "UPDATE authorization SET processor='unknown' WHERE subject_id='artifact-stop'"),
            ("missing_authorization", "DELETE FROM authorization WHERE subject_id='artifact-stop'"),
        )
        for case, sql in mutations:
            engine = LifeOSSlice()
            project_id = populate(engine)
            engine.db.execute(sql)
            engine.db.commit()
            self.record_equal(case, can_consume(engine, "artifact-stop", project_id), False)
            engine.close()
        engine = LifeOSSlice()
        project_id = populate(engine)
        self.record_equal("legal_exact_match", can_consume(engine, "artifact-stop", project_id), True)
        self.record_equal("missing_context", can_consume(engine, "artifact-stop", project_id, location=None), False)
        self.record_equal("missing_processor_context", can_consume(engine, "artifact-stop", project_id, processor=None), False)
        self.record_equal("missing_purpose_context", can_consume(engine, "artifact-stop", project_id, purpose=None), False)
        self.record_equal("wrong_exact_version", can_consume(engine, "artifact-stop", project_id, expected_version_id="artifact-stop:v0"), False)
        self.record_equal("right_exact_version", can_consume(engine, "artifact-stop", project_id), True)
        engine.close()

    def test_T_DEL(self):
        commands = [
            ("revoke_processing", "artifact-stop", "artifact-stop"),
            ("disconnect_source", "source-change", "artifact-change"),
            ("delete_content", "artifact-decision", "artifact-decision"),
        ]
        for command, subject, artifact_id in commands:
            engine = LifeOSSlice()
            project_id = populate(engine)
            suggest_next_step(engine, project_id)
            result = engine.control(command, subject)
            self.assertTrue(result["active_block"])
            self.assertIsNone(read_artifact(engine, artifact_id, project_id))
            self.assertFalse(any(x["artifact_id"] == artifact_id for x in search(engine, "SYNTH_NOTE", project_id)))
            self.assertFalse(any(x.get("artifact_id") == artifact_id for x in export_test_package(engine, project_id)["artifacts"]))
            self.assertFalse(any(x.get("artifact_id") == artifact_id for k in ("stopping_point", "changes", "decisions", "unprocessed") for x in recovery_package(engine, project_id)[k]))
            next_step = suggest_next_step(engine, project_id).get("candidate")
            self.assertTrue(next_step is None or next_step["evidence_version_id"] != f"{artifact_id}:v1")
            self.assertEqual(engine.db.execute("SELECT COUNT(*) n FROM outbox_job WHERE subject_id=? AND status IN ('pending','failed')", (artifact_id,)).fetchone()["n"], 0)
            engine.close()
        engine = LifeOSSlice()
        project_id = populate(engine)
        candidate = suggest_next_step(engine, project_id)["candidate"]
        feedback = add_feedback(engine, project_id, candidate["id"], "confirm")
        engine.control("retract_feedback", feedback["feedback_id"])
        self.assertEqual(engine.db.execute("SELECT status FROM feedback WHERE id=?", (feedback["feedback_id"],)).fetchone()["status"], "retracted")
        self.assertFalse(any(x["id"] == feedback["feedback_id"] for x in export_test_package(engine, project_id)["feedback"]))
        engine.close()

    def test_T_DEL_OLD_PACKAGE_CONTROLS(self):
        commands = (
            ("revoke_processing", "artifact-unprocessed", "artifact-unprocessed"),
            ("disconnect_source", "source-unprocessed", "artifact-unprocessed"),
            ("delete_content", "artifact-unprocessed", "artifact-unprocessed"),
        )
        for command, subject, artifact_id in commands:
            engine = LifeOSSlice()
            project_id = populate(engine)
            candidate = suggest_next_step(engine, project_id)["candidate"]
            feedback = add_feedback(engine, project_id, candidate["id"], "confirm")
            stale = export_test_package(engine, project_id)
            engine.control(command, subject)
            restored = restore_candidates(engine, stale)
            self.record_equal(f"{command}:artifact_not_restored", artifact_id in {x["artifact_id"] for x in restored["restored"]}, False)
            self.record_equal(f"{command}:derivation_not_restored", candidate["id"] in {x["id"] for x in restored["restored_derivations"]}, False)
            self.record_equal(f"{command}:feedback_not_restored", feedback["feedback_id"] in {x["id"] for x in restored["restored_feedback"]}, False)
            self.record_equal(f"{command}:search_zero", any(x["artifact_id"] == artifact_id for x in search(engine, "SYNTH_NOTE", project_id)), False)
            pending = engine.db.execute("SELECT COUNT(*) n FROM outbox_job WHERE subject_id=? AND status IN ('pending','failed')", (artifact_id,)).fetchone()["n"]
            self.record_equal(f"{command}:queue_zero", pending, 0)
            engine.close()
        engine = LifeOSSlice()
        project_id = populate(engine)
        candidate = suggest_next_step(engine, project_id)["candidate"]
        feedback = add_feedback(engine, project_id, candidate["id"], "confirm")
        stale = export_test_package(engine, project_id)
        engine.control("retract_feedback", feedback["feedback_id"])
        restored = restore_candidates(engine, stale)
        self.record_equal("retract_feedback:feedback_not_restored", feedback["feedback_id"] in {x["id"] for x in restored["restored_feedback"]}, False)
        self.record_equal("retract_feedback:derivation_not_restored", candidate["id"] in {x["id"] for x in restored["restored_derivations"]}, False)
        engine.close()

    def test_T_RESTORE_AUTHORITATIVE_CURRENT_GATE(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        stale_contexts = authorization_contexts(engine, project_id)
        stale = engine.export_test_package(project_id, authorization_contexts=stale_contexts)
        engine.control("delete_content", "artifact-stop")

        restored_with_stale_context = engine.restore_candidates(stale, authorization_contexts=stale_contexts)
        self.record_equal(
            "old_context_cannot_self_attest",
            "artifact-stop" in {x["artifact_id"] for x in restored_with_stale_context["restored"]}, False,
        )

        forged = json.loads(json.dumps(stale))
        for state in forged["control_states"]:
            if state["artifact_id"] == "artifact-stop":
                state.update({"deleted": False, "decision": "allow", "artifact_generation": 1, "auth_generation": 1})
        unsigned = {key: value for key, value in forged.items() if key != "checksum"}
        forged["checksum"] = LifeOSSlice._hash(json.dumps(unsigned, ensure_ascii=False, sort_keys=True))
        restored_forged = engine.restore_candidates(forged, authorization_contexts=stale_contexts)
        self.record_equal(
            "rehashed_forged_control_state_cannot_restore",
            "artifact-stop" in {x["artifact_id"] for x in restored_forged["restored"]}, False,
        )
        self.record_equal(
            "authoritative_tombstone_still_wins",
            engine.db.execute(
                "SELECT generation FROM tombstone WHERE subject_type='artifact' AND subject_id='artifact-stop'"
            ).fetchone()["generation"], 2,
        )
        engine.close()

    def test_T_DERIVATION_COMPLETE_EVIDENCE_REVOCATION(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        candidate = suggest_next_step(engine, project_id)["candidate"]
        feedback = add_feedback(engine, project_id, candidate["id"], "confirm")
        add_important_link(engine, project_id, "link-evidence", "artifact-decision", "artifact-unprocessed")
        dependencies = [
            row["version_id"] for row in engine.db.execute(
                "SELECT version_id FROM derivation_input WHERE derivation_id=? ORDER BY ordinal", (candidate["id"],)
            ).fetchall()
        ]
        self.record_equal("full_evidence_persisted", dependencies, candidate["evidence_version_ids"])

        engine.control("revoke_processing", "artifact-decision")
        status = engine.db.execute("SELECT status FROM derivation WHERE id=?", (candidate["id"],)).fetchone()["status"]
        self.record_equal("non_primary_evidence_makes_candidate_stale", status, "stale")
        package = export_test_package(engine, project_id)
        self.record_equal("stale_derivation_export_zero", candidate["id"] in {x["id"] for x in package["derivations"]}, False)
        self.record_equal("dependent_feedback_export_zero", feedback["feedback_id"] in {x["id"] for x in package["feedback"]}, False)
        self.record_equal("dependent_link_export_zero", "link-evidence" in {x["id"] for x in package["links"]}, False)
        self.record_equal("suggestion_consumption_blocked", suggest_next_step(engine, project_id)["candidate"], None)
        engine.close()

    def test_T_GATE_EXPLICIT_CONTEXT_AND_CONFLICTS(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        self.record_equal("read_missing_context", engine.read_artifact("artifact-stop", project_id), None)
        self.record_equal("search_missing_context", engine.search("SYNTH_NOTE", project_id), [])
        missing_recovery = engine.recovery_package(project_id)
        self.record_equal("recovery_missing_context_active_items", sum(
            len(missing_recovery[key]) for key in ("stopping_point", "changes", "decisions", "unprocessed")
        ), 0)
        self.record_equal("recovery_missing_context_gaps", len(missing_recovery["evidence_gaps"]), 4)
        self.record_equal("export_missing_context", engine.export_test_package(project_id)["artifacts"], [])

        allow_context = authorization_context(engine, "artifact-stop", project_id)
        engine.db.execute(
            "INSERT INTO authorization VALUES(?,?,?,?,?,?,?,?)",
            ("auth:artifact-stop:conflict", "artifact-stop", "lifeos_local_recovery", "local", "local_rules", "deny", None, 1),
        )
        engine.db.commit()
        consume_kwargs = dict(allow_context)
        consume_kwargs.pop("subject_id")
        consume_kwargs.pop("project_id")
        self.record_equal(
            "conflicting_allow_deny_can_consume", engine.can_consume("artifact-stop", project_id=project_id, **consume_kwargs), False
        )
        self.record_equal(
            "conflicting_allow_deny_read", engine.read_artifact(
                "artifact-stop", project_id, authorization_context=allow_context
            ), None,
        )
        conflict_contexts = authorization_contexts(engine, project_id)
        self.record_equal(
            "conflicting_allow_deny_search",
            "artifact-stop" in {x["artifact_id"] for x in engine.search(
                "SYNTH_NOTE", project_id, authorization_contexts=conflict_contexts
            )}, False,
        )
        self.record_equal(
            "conflicting_allow_deny_recovery",
            "artifact-stop" in {
                x["artifact_id"] for key in ("stopping_point", "changes", "decisions", "unprocessed")
                for x in engine.recovery_package(project_id, authorization_contexts=conflict_contexts)[key]
            }, False,
        )
        self.record_equal(
            "conflicting_allow_deny_export",
            "artifact-stop" in {x["artifact_id"] for x in engine.export_test_package(
                project_id, authorization_contexts=conflict_contexts
            )["artifacts"]}, False,
        )
        engine.close()

        duplicate = LifeOSSlice()
        duplicate_project = populate(duplicate)
        duplicate.db.execute(
            "INSERT INTO authorization VALUES(?,?,?,?,?,?,?,?)",
            ("auth:artifact-stop:duplicate", "artifact-stop", "lifeos_local_recovery", "local", "local_rules", "allow", None, 1),
        )
        duplicate.db.commit()
        self.record_equal("duplicate_allow_fails_closed", can_consume(duplicate, "artifact-stop", duplicate_project), False)
        self.record_equal(
            "generation_context_mismatch_fails_closed",
            can_consume(duplicate, "artifact-change", duplicate_project, expected_generation=99), False,
        )
        self.record_equal(
            "source_generation_context_mismatch_fails_closed",
            can_consume(duplicate, "artifact-change", duplicate_project, expected_source_generation=99), False,
        )
        duplicate.close()

        time_engine = LifeOSSlice()
        time_project = populate(time_engine)
        time_engine.db.execute(
            "UPDATE authorization SET expires_at='2020-01-01T00:00:00+00:00' WHERE subject_id='artifact-stop'"
        )
        time_engine.db.commit()
        self.record_equal(
            "caller_cannot_move_policy_clock_backward",
            can_consume(time_engine, "artifact-stop", time_project, now="2010-01-01T00:00:00+00:00"), False,
        )
        time_engine.close()

    def test_T_RESTORE_AUTHORITATIVE_PAYLOAD_PROJECTION(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        candidate = suggest_next_step(engine, project_id)["candidate"]
        feedback = add_feedback(engine, project_id, candidate["id"], "confirm", "SYNTH_FEEDBACK")
        add_important_link(engine, project_id, "link-authoritative", "artifact-decision", "artifact-unprocessed")
        package = export_test_package(engine, project_id)

        def rehash(value):
            unsigned = {key: item for key, item in value.items() if key != "checksum"}
            value["checksum"] = LifeOSSlice._hash(json.dumps(unsigned, ensure_ascii=False, sort_keys=True))
            return value

        forged = json.loads(json.dumps(package))
        forged["artifacts"][0].update({
            "original_text": "FORGED_ORIGINAL", "title": "FORGED_TITLE", "category": "decision",
            "source_id": "source-forged",
        })
        forged["derivations"][0].update({
            "output_text": "FORGED_DERIVATION", "rule_id": "forged-rule", "generation": 999,
            "status": "confirmed",
        })
        forged["feedback"][0].update({"kind": "correct", "user_text": "FORGED_FEEDBACK"})
        forged["links"][0].update({
            "relation": "forged", "source_kind": "forged", "confirmation_status": "unconfirmed",
        })
        forged["links"].append({
            "id": "link-injected", "from_artifact_id": "artifact-decision",
            "to_artifact_id": "artifact-unprocessed", "relation": "forged",
            "source_kind": "forged", "confirmation_status": "confirmed",
        })
        restored = restore_candidates(engine, rehash(forged))
        authoritative_artifact = read_artifact(engine, package["artifacts"][0]["artifact_id"], project_id)
        authoritative_derivation = dict(engine.db.execute(
            "SELECT * FROM derivation WHERE id=?", (candidate["id"],)
        ).fetchone())
        authoritative_feedback = dict(engine.db.execute(
            "SELECT * FROM feedback WHERE id=?", (feedback["feedback_id"],)
        ).fetchone())
        authoritative_link = dict(engine.db.execute(
            "SELECT * FROM important_link WHERE id='link-authoritative'"
        ).fetchone())
        restored_artifact = next(x for x in restored["restored"] if x["artifact_id"] == authoritative_artifact["artifact_id"])
        restored_derivation = next(x for x in restored["restored_derivations"] if x["id"] == candidate["id"])
        restored_feedback = next(x for x in restored["restored_feedback"] if x["id"] == feedback["feedback_id"])
        restored_link = next(x for x in restored["restored_links"] if x["id"] == "link-authoritative")
        self.record_equal("artifact_payload_from_authority", restored_artifact, authoritative_artifact)
        self.record_equal("derivation_output_from_authority", restored_derivation["output_text"], authoritative_derivation["output_text"])
        self.record_equal("derivation_rule_from_authority", restored_derivation["rule_id"], authoritative_derivation["rule_id"])
        self.record_equal("derivation_generation_from_authority", restored_derivation["generation"], authoritative_derivation["generation"])
        self.record_equal("feedback_payload_from_authority", {k: restored_feedback[k] for k in authoritative_feedback}, authoritative_feedback)
        self.record_equal("link_payload_from_authority", restored_link, authoritative_link)
        self.record_equal("injected_link_not_restored", "link-injected" in {x["id"] for x in restored["restored_links"]}, False)
        engine.close()

    def test_T_WRITE_GATES_FEEDBACK_AND_LINK(self):
        feedback_mutations = (
            ("deny", "UPDATE authorization SET decision='deny' WHERE subject_id='artifact-decision'", None),
            ("revoked", "UPDATE authorization SET decision='revoked' WHERE subject_id='artifact-decision'", None),
            ("expired", "UPDATE authorization SET expires_at='2020-01-01T00:00:00+00:00' WHERE subject_id='artifact-decision'", None),
            ("conflict", "INSERT INTO authorization VALUES('auth:artifact-decision:deny','artifact-decision','lifeos_local_recovery','local','local_rules','deny',NULL,1)", None),
            ("location_context", None, {"location": "cloud"}),
            ("processor_context", None, {"processor": "third_party"}),
            ("purpose_context", None, {"purpose": "other"}),
        )
        for case, sql, override in feedback_mutations:
            engine = LifeOSSlice()
            project_id = populate(engine)
            candidate = suggest_next_step(engine, project_id)["candidate"]
            contexts = authorization_contexts(engine, project_id)
            if sql:
                engine.db.execute(sql)
                engine.db.commit()
            if override:
                contexts["artifact-decision"].update(override)
            with self.assertRaises(ValueError):
                engine.add_feedback(
                    candidate["id"], "confirm", project_id=project_id,
                    authorization_contexts=contexts,
                )
            self.record_equal(f"{case}:feedback_zero", engine.db.execute(
                "SELECT COUNT(*) n FROM feedback WHERE derivation_id=?", (candidate["id"],)
            ).fetchone()["n"], 0)
            self.record_equal(f"{case}:status_unchanged", engine.db.execute(
                "SELECT status FROM derivation WHERE id=?", (candidate["id"],)
            ).fetchone()["status"], "unconfirmed")
            engine.close()

        legal = LifeOSSlice()
        project_a = populate(legal)
        project_b = populate_secondary(legal)
        candidate = suggest_next_step(legal, project_a)["candidate"]
        with self.assertRaises(ValueError):
            legal.add_feedback(candidate["id"], "confirm")
        self.record_equal("feedback_missing_context_zero", legal.db.execute(
            "SELECT COUNT(*) n FROM feedback WHERE derivation_id=?", (candidate["id"],)
        ).fetchone()["n"], 0)
        with self.assertRaises(ValueError):
            legal.add_important_link(
                "link-missing-context", "artifact-decision", "artifact-unprocessed", "supports", True
            )
        self.record_equal("link_missing_context_zero", legal.db.execute(
            "SELECT COUNT(*) n FROM important_link WHERE id='link-missing-context'"
        ).fetchone()["n"], 0)
        self.record_equal("feedback_happy_path", add_feedback(
            legal, project_a, candidate["id"], "confirm"
        )["kind"], "confirm")
        add_important_link(legal, project_a, "link-happy", "artifact-decision", "artifact-unprocessed")
        self.record_equal("link_happy_path", legal.db.execute(
            "SELECT COUNT(*) n FROM important_link WHERE id='link-happy'"
        ).fetchone()["n"], 1)
        before = legal.db.execute("SELECT COUNT(*) n FROM important_link").fetchone()["n"]
        with self.assertRaises(ValueError):
            add_important_link(legal, project_a, "link-cross-denied", "artifact-decision", "artifact-b-unprocessed")
        self.record_equal("cross_project_link_zero", legal.db.execute(
            "SELECT COUNT(*) n FROM important_link"
        ).fetchone()["n"], before)
        legal.control("delete_content", "artifact-unprocessed")
        with self.assertRaises(ValueError):
            add_important_link(legal, project_a, "link-deleted-denied", "artifact-decision", "artifact-unprocessed")
        self.record_equal("deleted_endpoint_link_zero", legal.db.execute(
            "SELECT COUNT(*) n FROM important_link WHERE id='link-deleted-denied'"
        ).fetchone()["n"], 0)
        legal.close()

        for case, command, subject in (
            ("revoked", "revoke_processing", "artifact-decision"),
            ("disconnected", "disconnect_source", "source-decision"),
        ):
            engine = LifeOSSlice()
            scoped_project = populate(engine)
            engine.control(command, subject)
            with self.assertRaises(ValueError):
                add_important_link(
                    engine, scoped_project, f"link-{case}-denied",
                    "artifact-decision", "artifact-unprocessed",
                )
            self.record_equal(f"{case}_endpoint_link_zero", engine.db.execute(
                "SELECT COUNT(*) n FROM important_link WHERE id=?", (f"link-{case}-denied",)
            ).fetchone()["n"], 0)
            engine.close()

    def test_T_EXPORT_ALL_STATE_PROJECT_CLOSURE(self):
        engine = LifeOSSlice()
        project_a = populate(engine)
        project_b = populate_secondary(engine)
        legal_candidate = suggest_next_step(engine, project_a)["candidate"]
        legal_feedback = add_feedback(engine, project_a, legal_candidate["id"], "confirm", "SYNTH_A_FEEDBACK")
        mixed_id = "derivation:mixed:a-b"
        engine.db.execute(
            "INSERT INTO derivation VALUES(?,?,?,?,?,?,?,?)",
            (mixed_id, "candidate_next_step", "artifact-decision:v1", "SYNTH_MIXED", "unconfirmed", 1, "mixed-rule", FIXED_NOW),
        )
        engine.db.execute(
            "INSERT INTO derivation_input VALUES(?,?,?,?,?)",
            (mixed_id, "artifact-decision:v1", 0, 1, 1),
        )
        engine.db.execute(
            "INSERT INTO derivation_input VALUES(?,?,?,?,?)",
            (mixed_id, "artifact-b-unprocessed:v1", 1, 1, 1),
        )
        engine.db.execute(
            "INSERT INTO feedback VALUES(?,?,?,?,?,?)",
            ("feedback:mixed", mixed_id, "correct", "SYNTH_MIXED_FEEDBACK", "active", FIXED_NOW),
        )
        engine.db.execute(
            "INSERT INTO important_link VALUES(?,?,?,?,?,?)",
            ("link-mixed", "artifact-decision", "artifact-b-unprocessed", "supports", "user_explicit", "confirmed"),
        )
        engine.db.commit()
        for project_id, other_version in (
            (project_a, "artifact-b-unprocessed:v1"),
            (project_b, "artifact-decision:v1"),
        ):
            serialized = json.dumps(export_test_package(engine, project_id), ensure_ascii=False, sort_keys=True)
            for forbidden in (mixed_id, "feedback:mixed", "SYNTH_MIXED_FEEDBACK", "link-mixed", other_version):
                self.record_equal(f"{project_id}:zero_leak:{forbidden}", forbidden in serialized, False)
        package_a = export_test_package(engine, project_a)
        self.record_equal("legal_state_present", legal_candidate["id"] in {
            x["id"] for x in package_a["derivation_states"]
        }, True)
        self.record_equal("legal_feedback_state_present", legal_feedback["feedback_id"] in {
            x["id"] for x in package_a["feedback_states"]
        }, True)
        engine.close()

    def test_T_DERIVATION_GENERATION_BINDING(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        first = suggest_next_step(engine, project_id)["candidate"]
        stale_package = export_test_package(engine, project_id)
        old_contexts = authorization_contexts(engine, project_id)
        engine.db.execute("UPDATE artifact SET generation=2 WHERE id='artifact-decision'")
        engine.db.execute("UPDATE authorization SET generation=2 WHERE subject_id='artifact-decision'")
        engine.db.commit()
        new_contexts = authorization_contexts(engine, project_id)
        second = engine.suggest_next_step(project_id, authorization_contexts=new_contexts)["candidate"]
        self.record_equal("artifact_generation_new_identity", second["id"] != first["id"], True)
        self.record_equal("artifact_generation_old_stale", engine.db.execute(
            "SELECT status FROM derivation WHERE id=?", (first["id"],)
        ).fetchone()["status"], "stale")
        exported = engine.export_test_package(project_id, authorization_contexts=new_contexts)
        self.record_equal("old_generation_export_zero", first["id"] in {x["id"] for x in exported["derivations"]}, False)
        restored = engine.restore_candidates(stale_package, authorization_contexts=new_contexts)
        self.record_equal("old_generation_restore_zero", first["id"] in {
            x["id"] for x in restored["restored_derivations"]
        }, False)
        with self.assertRaises(ValueError):
            engine.add_feedback(first["id"], "confirm", project_id=project_id, authorization_contexts=new_contexts)
        self.record_equal("old_generation_feedback_zero", engine.db.execute(
            "SELECT COUNT(*) n FROM feedback WHERE derivation_id=?", (first["id"],)
        ).fetchone()["n"], 0)
        with self.assertRaises(ValueError):
            engine.add_important_link(
                "link-old-generation", "artifact-decision", "artifact-unprocessed", "supports", True,
                project_id=project_id, authorization_contexts=old_contexts,
            )
        self.record_equal("old_generation_link_zero", engine.db.execute(
            "SELECT COUNT(*) n FROM important_link WHERE id='link-old-generation'"
        ).fetchone()["n"], 0)
        self.record_equal("old_generation_search_zero", "artifact-decision" in {
            x["artifact_id"] for x in engine.search("SYNTH_NOTE", project_id, authorization_contexts=old_contexts)
        }, False)

        source_first = second
        engine.db.execute("UPDATE source SET generation=2 WHERE id='source-unprocessed'")
        engine.db.commit()
        source_contexts = authorization_contexts(engine, project_id)
        source_second = engine.suggest_next_step(project_id, authorization_contexts=source_contexts)["candidate"]
        self.record_equal("source_generation_new_identity", source_second["id"] != source_first["id"], True)
        self.record_equal("source_generation_old_stale", engine.db.execute(
            "SELECT status FROM derivation WHERE id=?", (source_first["id"],)
        ).fetchone()["status"], "stale")
        self.record_equal("unchanged_generation_happy_path", add_feedback(
            engine, project_id, source_second["id"], "confirm"
        )["kind"], "confirm")
        engine.close()

    def test_T_IPC_OFF(self):
        engine = LifeOSSlice()
        for capability in ("tauri_ipc", "filesystem_export", "real_vault"):
            with self.assertRaises(DisabledCapability):
                engine.capability_call(capability)
        self.assertNotIn("path", engine.export_test_package("none", authorization_contexts={}))
        engine.close()

    def test_T_DATA(self):
        raw = FIXTURE_PATH.read_text(encoding="utf-8")
        fixture = json.loads(raw)
        self.assertEqual(fixture["classification"], "synthetic-disposable")
        forbidden = [r"-----BEGIN [A-Z ]+PRIVATE KEY-----", r"AKIA[0-9A-Z]{16}", r"(?i)password\s*[:=]", r"(?i)api[_-]?key\s*[:=]", r"/Users/[^/\s]+", r"[A-Za-z]:\\Users\\", r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}"]
        self.assertEqual([pattern for pattern in forbidden if re.search(pattern, raw)], [])
        self.assertTrue(all(x["original_text"].startswith("SYNTH_NOTE_") for x in fixture["captures"]))

    def test_T_OFF(self):
        engine = LifeOSSlice()
        self.assertTrue(engine.DISABLED_CAPABILITIES)
        self.assertFalse(any(engine.DISABLED_CAPABILITIES.values()))
        for capability in engine.DISABLED_CAPABILITIES:
            with self.assertRaises(DisabledCapability):
                engine.capability_call(capability)
        engine.close()

    def test_T_UX(self):
        engine = LifeOSSlice()
        states = ["normal", "empty", "saving_failed", "restricted", "evidence_gap", "confirmed", "rejected", "corrected", "revoked", "deleted"]
        contracts = [engine.ux_contract(state) for state in states]
        self.assertTrue(all(x["announced"] and x["keyboard_only"] for x in contracts))
        self.assertTrue(all(x["focus_return"] == "trigger" and x["reduced_motion"] == "no_required_animation" for x in contracts))
        self.assertEqual(engine.suggest_next_step("empty-project", authorization_contexts={})["message"], "暂无可靠建议")
        engine.close()

    def test_T_EXPORT(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        add_important_link(engine, project_id, "link-export", "artifact-decision", "artifact-unprocessed")
        stale = export_test_package(engine, project_id)
        self.assertEqual(stale["status"], "complete")
        self.assertEqual(len(stale["artifacts"]), 4)
        partial = export_test_package(engine, project_id, fail_artifact_ids=["artifact-change"])
        self.assertEqual(partial["status"], "partial")
        self.assertEqual(partial["partial_failures"][0]["reason"], "injected_export_failure")
        engine.control("delete_content", "artifact-decision")
        restored = restore_candidates(engine, stale)
        self.assertIn("artifact-decision", [x["artifact_id"] for x in restored["excluded"]])
        self.assertNotIn("artifact-decision", [x["artifact_id"] for x in restored["restored"]])
        self.assertTrue(all("version_id" in x and "source_id" in x for x in stale["artifacts"]))
        self.assertEqual(stale["links"][0]["confirmation_status"], "confirmed")
        engine.close()

    def test_T_EXPORT_PROJECT_CLOSURE(self):
        engine = LifeOSSlice()
        project_a = populate(engine)
        project_b = populate_secondary(engine)
        candidate_a = suggest_next_step(engine, project_a)["candidate"]
        candidate_b = suggest_next_step(engine, project_b)["candidate"]
        feedback_a = add_feedback(engine, project_a, candidate_a["id"], "confirm")
        feedback_b = add_feedback(engine, project_b, candidate_b["id"], "confirm")
        add_important_link(engine, project_a, "link-a", "artifact-decision", "artifact-unprocessed")
        add_important_link(engine, project_b, "link-b", "artifact-b-decision", "artifact-b-unprocessed")
        with self.assertRaises(ValueError):
            add_important_link(engine, project_a, "link-cross", "artifact-decision", "artifact-b-unprocessed")
        package = export_test_package(engine, project_a)
        serialized = json.dumps(package, ensure_ascii=False, sort_keys=True)
        for forbidden in ("artifact-b-decision", "artifact-b-unprocessed", feedback_b["feedback_id"], "link-b", "link-cross", project_b):
            self.record_equal(f"zero_leak:{forbidden}", forbidden in serialized, False)
        self.record_equal("a_feedback_included", feedback_a["feedback_id"] in {x["id"] for x in package["feedback"]}, True)
        self.record_equal("a_link_included", {x["id"] for x in package["links"]}, {"link-a"})
        artifact_ids = {x["artifact_id"] for x in package["artifacts"]}
        self.record_equal("artifact_versions_closed", {x["artifact_id"] for x in package["artifact_versions"]}, artifact_ids)
        self.record_equal("authorizations_closed", {x["subject_id"] for x in package["authorizations"]}, artifact_ids)
        self.record_equal("sources_closed", {x["id"] for x in package["sources"]}, {x["source_id"] for x in package["artifacts"]})
        tampered = json.loads(json.dumps(package))
        tampered["artifacts"][0]["title"] = "TAMPERED"
        rejected = engine.restore_candidates(tampered, authorization_contexts=authorization_contexts(engine, project_a))
        self.record_equal("tampered_package_fail_closed", rejected["conflicts"][0]["reason"], "package_checksum_invalid")
        engine.close()

    def test_T_ARCH(self):
        engine = LifeOSSlice()
        project_id = populate(engine)
        tables = {x["name"] for x in engine.db.execute("SELECT name FROM sqlite_master")}
        self.assertTrue({"artifact_version", "authorization", "outbox_job", "tombstone", "artifact_fts"}.issubset(tables))
        self.assertFalse(any(engine.DISABLED_CAPABILITIES.values()))
        # Use the fixture's deterministic ASCII marker so this contract test does
        # not accidentally freeze a Chinese tokenizer choice.
        self.assertEqual(len(search(engine, "SYNTH_NOTE", project_id)), 4)
        lease_engine = LifeOSSlice()
        lease_engine.capture(source_id="lease-source", artifact_id="lease-artifact", project_id="lease-project", title="租约", category="change", original_text="SYNTH_LEASE", idempotency_key="lease")
        token = lease_engine.claim_job("job:index:lease-artifact", 0)
        self.assertEqual(token, 1)
        self.assertIsNone(lease_engine.claim_job("job:index:lease-artifact", 0))
        lease_engine.control("delete_content", "lease-artifact")
        self.assertFalse(lease_engine.complete_index_job("job:index:lease-artifact", token))
        lease_engine.close()
        backup = sqlite3.connect(":memory:")
        engine.backup_to_connection(backup)
        self.assertEqual(backup.execute("SELECT COUNT(*) FROM artifact").fetchone()[0], 4)
        backup.close()
        engine.db.execute("DELETE FROM artifact_fts")
        engine.db.execute("UPDATE outbox_job SET status='pending' WHERE job_kind='index'")
        engine.db.commit()
        result = engine.capture(source_id="source-during-maintenance", artifact_id="artifact-during-maintenance", project_id=project_id, title="维护期间捕获", category="change", original_text="SYNTH_NOTE_005：权威捕获不依赖索引维护。", idempotency_key="during-maintenance")
        self.assertTrue(result["saved"])
        self.assertEqual(engine.process_index_jobs()["failed"], 0)
        self.assertEqual(read_artifact(engine, "artifact-during-maintenance", project_id)["original_text"], "SYNTH_NOTE_005：权威捕获不依赖索引维护。")
        engine.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
