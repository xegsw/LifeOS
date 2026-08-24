from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional


FIXED_NOW = "2030-01-01T00:00:00+00:00"


class DisabledCapability(RuntimeError):
    pass


class LifeOSSlice:
    """A deliberately small semantic implementation; its schema is not a product freeze."""

    DISABLED_CAPABILITIES = {
        "real_vault": False,
        "tauri_ipc": False,
        "filesystem_export": False,
        "cloud_or_third_party_model": False,
        "vector_index": False,
        "sync_or_multi_device": False,
        "l3_actions": False,
        "external_users": False,
    }

    def __init__(self, database: str = ":memory:") -> None:
        self.database = database
        self.db = sqlite3.connect(database)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA foreign_keys=ON")
        self._create_schema()

    def close(self) -> None:
        self.db.close()

    def _create_schema(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS source(
              id TEXT PRIMARY KEY, kind TEXT NOT NULL, locator TEXT NOT NULL,
              connected INTEGER NOT NULL DEFAULT 1, generation INTEGER NOT NULL DEFAULT 1,
              tombstoned INTEGER NOT NULL DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS artifact(
              id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source(id),
              project_id TEXT, title TEXT NOT NULL, category TEXT NOT NULL,
              current_version_id TEXT, deleted INTEGER NOT NULL DEFAULT 0,
              generation INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS artifact_version(
              id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL REFERENCES artifact(id),
              version_no INTEGER NOT NULL, original_text TEXT NOT NULL,
              content_hash TEXT NOT NULL, created_at TEXT NOT NULL,
              UNIQUE(artifact_id, version_no)
            );
            CREATE TRIGGER IF NOT EXISTS artifact_version_immutable_update
            BEFORE UPDATE ON artifact_version BEGIN SELECT RAISE(ABORT, 'artifact versions are immutable'); END;
            CREATE TRIGGER IF NOT EXISTS artifact_version_immutable_delete
            BEFORE DELETE ON artifact_version BEGIN SELECT RAISE(ABORT, 'artifact versions are immutable'); END;
            CREATE TABLE IF NOT EXISTS authorization(
              id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, purpose TEXT NOT NULL,
              location TEXT NOT NULL, processor TEXT NOT NULL, decision TEXT NOT NULL,
              expires_at TEXT, generation INTEGER NOT NULL DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS derivation(
              id TEXT PRIMARY KEY, kind TEXT NOT NULL, input_version_id TEXT NOT NULL,
              output_text TEXT NOT NULL, status TEXT NOT NULL,
              generation INTEGER NOT NULL, rule_id TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS derivation_input(
              derivation_id TEXT NOT NULL REFERENCES derivation(id),
              version_id TEXT NOT NULL REFERENCES artifact_version(id),
              ordinal INTEGER NOT NULL, artifact_generation INTEGER NOT NULL DEFAULT 1,
              source_generation INTEGER NOT NULL DEFAULT 1,
              PRIMARY KEY(derivation_id, version_id), UNIQUE(derivation_id, ordinal)
            );
            CREATE TABLE IF NOT EXISTS feedback(
              id TEXT PRIMARY KEY, derivation_id TEXT NOT NULL, kind TEXT NOT NULL,
              user_text TEXT, status TEXT NOT NULL DEFAULT 'active', created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS important_link(
              id TEXT PRIMARY KEY, from_artifact_id TEXT NOT NULL, to_artifact_id TEXT NOT NULL,
              relation TEXT NOT NULL, source_kind TEXT NOT NULL, confirmation_status TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_entry(
              id INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL, subject_type TEXT NOT NULL,
              subject_id TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS outbox_job(
              id TEXT PRIMARY KEY, job_kind TEXT NOT NULL, subject_type TEXT NOT NULL,
              subject_id TEXT NOT NULL, generation INTEGER NOT NULL, status TEXT NOT NULL,
              lease_generation INTEGER NOT NULL DEFAULT 0, idempotency_key TEXT NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS tombstone(
              subject_type TEXT NOT NULL, subject_id TEXT NOT NULL,
              generation INTEGER NOT NULL, reason TEXT NOT NULL,
              PRIMARY KEY(subject_type, subject_id)
            );
            CREATE TABLE IF NOT EXISTS submission(
              idempotency_key TEXT PRIMARY KEY, artifact_id TEXT NOT NULL, version_id TEXT NOT NULL
            );
            CREATE VIRTUAL TABLE IF NOT EXISTS artifact_fts USING fts5(
              artifact_id UNINDEXED, version_id UNINDEXED, body
            );
            """
        )
        columns = {row["name"] for row in self.db.execute("PRAGMA table_info(derivation_input)")}
        if "artifact_generation" not in columns:
            self.db.execute(
                "ALTER TABLE derivation_input ADD COLUMN artifact_generation INTEGER NOT NULL DEFAULT 1"
            )
        if "source_generation" not in columns:
            self.db.execute(
                "ALTER TABLE derivation_input ADD COLUMN source_generation INTEGER NOT NULL DEFAULT 1"
            )
        self.db.commit()

    @staticmethod
    def _hash(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def capture(
        self,
        *,
        source_id: str,
        artifact_id: str,
        project_id: Optional[str],
        title: str,
        category: str,
        original_text: str,
        idempotency_key: str,
        fail_authoritative: bool = False,
        _crash_at_for_test: Optional[str] = None,
    ) -> Dict[str, Any]:
        existing = self.db.execute(
            "SELECT artifact_id, version_id FROM submission WHERE idempotency_key=?",
            (idempotency_key,),
        ).fetchone()
        if existing:
            return {"saved": True, "deduplicated": True, **dict(existing)}

        version_id = f"{artifact_id}:v1"
        try:
            self.db.execute("BEGIN IMMEDIATE")
            self.db.execute(
                "INSERT INTO source(id,kind,locator) VALUES(?,?,?)",
                (source_id, "user_capture", f"synthetic://{source_id}"),
            )
            self.db.execute(
                "INSERT INTO artifact(id,source_id,project_id,title,category,current_version_id) VALUES(?,?,?,?,?,?)",
                (artifact_id, source_id, project_id, title, category, version_id),
            )
            self.db.execute(
                "INSERT INTO artifact_version VALUES(?,?,?,?,?,?)",
                (version_id, artifact_id, 1, original_text, self._hash(original_text), FIXED_NOW),
            )
            self.db.execute(
                "INSERT INTO authorization VALUES(?,?,?,?,?,?,?,?)",
                (f"auth:{artifact_id}", artifact_id, "lifeos_local_recovery", "local", "local_rules", "allow", None, 1),
            )
            self.db.execute(
                "INSERT INTO submission VALUES(?,?,?)",
                (idempotency_key, artifact_id, version_id),
            )
            self.db.execute(
                "INSERT INTO outbox_job VALUES(?,?,?,?,?,?,?,?)",
                (f"job:index:{artifact_id}", "index", "artifact", artifact_id, 1, "pending", 0, f"index:{artifact_id}:1"),
            )
            self._audit("captured", "artifact", artifact_id, {"version_id": version_id})
            if fail_authoritative:
                raise sqlite3.OperationalError("injected authoritative write failure")
            if _crash_at_for_test == "before_commit":
                os._exit(86)
            self.db.commit()
            if _crash_at_for_test == "after_commit":
                os._exit(87)
            return {"saved": True, "deduplicated": False, "artifact_id": artifact_id, "version_id": version_id}
        except Exception as exc:
            self.db.rollback()
            return {"saved": False, "deduplicated": False, "error": str(exc)}

    def _audit(self, event: str, subject_type: str, subject_id: str, detail: Dict[str, Any]) -> None:
        self.db.execute(
            "INSERT INTO audit_entry(event,subject_type,subject_id,detail,created_at) VALUES(?,?,?,?,?)",
            (event, subject_type, subject_id, json.dumps(detail, sort_keys=True), FIXED_NOW),
        )

    def process_index_jobs(self, *, inject_failure: bool = False) -> Dict[str, int]:
        rows = self.db.execute("SELECT * FROM outbox_job WHERE status='pending' AND job_kind='index'").fetchall()
        processed = failed = skipped = 0
        for job in rows:
            if not self._job_is_current(job):
                self.db.execute("UPDATE outbox_job SET status='cancelled' WHERE id=?", (job["id"],))
                skipped += 1
                continue
            lease_token = self.claim_job(job["id"], job["lease_generation"])
            if lease_token is None:
                skipped += 1
                continue
            if inject_failure:
                self.db.execute(
                    "UPDATE outbox_job SET status='failed' WHERE id=? AND lease_generation=?",
                    (job["id"], lease_token),
                )
                failed += 1
                continue
            if not self.complete_index_job(job["id"], lease_token):
                skipped += 1
                continue
            processed += 1
        self.db.commit()
        return {"processed": processed, "failed": failed, "skipped": skipped}

    def claim_job(self, job_id: str, expected_lease: int) -> Optional[int]:
        cursor = self.db.execute(
            """UPDATE outbox_job SET status='processing',lease_generation=lease_generation+1
               WHERE id=? AND status='pending' AND lease_generation=?""",
            (job_id, expected_lease),
        )
        self.db.commit()
        return expected_lease + 1 if cursor.rowcount == 1 else None

    def complete_index_job(self, job_id: str, lease_token: int) -> bool:
        job = self.db.execute(
            "SELECT * FROM outbox_job WHERE id=? AND status='processing' AND lease_generation=?",
            (job_id, lease_token),
        ).fetchone()
        if not job or not self._job_is_current(job):
            if job:
                self.db.execute(
                    "UPDATE outbox_job SET status='cancelled' WHERE id=? AND lease_generation=?",
                    (job_id, lease_token),
                )
                self.db.commit()
            return False
        artifact = self._current_artifact(job["subject_id"])
        if artifact is None or not self.can_consume(
            artifact["id"], project_id=artifact["project_id"],
            expected_version_id=artifact["current_version_id"], expected_generation=artifact["generation"],
            expected_source_generation=self.db.execute(
                "SELECT generation FROM source WHERE id=?", (artifact["source_id"],)
            ).fetchone()["generation"],
            purpose="lifeos_local_recovery", location="local", processor="local_rules", now=FIXED_NOW,
        ):
            return False
        version = self.db.execute("SELECT * FROM artifact_version WHERE id=?", (artifact["current_version_id"],)).fetchone()
        self.db.execute("DELETE FROM artifact_fts WHERE artifact_id=?", (artifact["id"],))
        self.db.execute(
            "INSERT INTO artifact_fts(artifact_id,version_id,body) VALUES(?,?,?)",
            (artifact["id"], version["id"], version["original_text"]),
        )
        cursor = self.db.execute(
            "UPDATE outbox_job SET status='done' WHERE id=? AND lease_generation=? AND status='processing'",
            (job_id, lease_token),
        )
        self.db.commit()
        return cursor.rowcount == 1

    def _job_is_current(self, job: sqlite3.Row) -> bool:
        artifact = self._current_artifact(job["subject_id"])
        return bool(artifact and artifact["generation"] == job["generation"] and not artifact["deleted"])

    def _current_artifact(self, artifact_id: str) -> Optional[sqlite3.Row]:
        return self.db.execute("SELECT * FROM artifact WHERE id=?", (artifact_id,)).fetchone()

    def can_consume(
        self,
        artifact_id: str,
        *,
        project_id: Optional[str],
        expected_version_id: Optional[str] = None,
        expected_generation: Optional[int] = None,
        expected_source_generation: Optional[int] = None,
        purpose: Optional[str] = None,
        location: Optional[str] = None,
        processor: Optional[str] = None,
        now: Optional[str] = None,
    ) -> bool:
        if (
            not project_id or not expected_version_id or expected_generation is None
            or expected_source_generation is None
            or not purpose or not location or not processor or not now
        ):
            return False
        # FIXED_NOW is the deterministic trusted clock for this synthetic slice;
        # callers may declare it explicitly but cannot move policy evaluation backward.
        if now != FIXED_NOW:
            return False
        row = self.db.execute(
            """
            SELECT a.*, s.connected, s.tombstoned AS source_tombstoned, s.generation AS source_generation
            FROM artifact a JOIN source s ON s.id=a.source_id
            WHERE a.id=?
            """,
            (artifact_id,),
        ).fetchone()
        if not row or row["deleted"] or not row["connected"] or row["source_tombstoned"]:
            return False
        if row["project_id"] != project_id:
            return False
        if (
            row["current_version_id"] != expected_version_id or row["generation"] != expected_generation
            or row["source_generation"] != expected_source_generation
        ):
            return False
        authorizations = self.db.execute(
            "SELECT * FROM authorization WHERE subject_id=? ORDER BY id", (artifact_id,)
        ).fetchall()
        if len(authorizations) != 1:
            return False
        authorization = authorizations[0]
        if (
            authorization["purpose"] != purpose
            or authorization["location"] != location
            or authorization["processor"] != processor
            or authorization["decision"] != "allow"
            or authorization["generation"] != row["generation"]
        ):
            return False
        if authorization["expires_at"] and authorization["expires_at"] <= now:
            return False
        tombstone = self.db.execute(
            "SELECT generation FROM tombstone WHERE subject_type='artifact' AND subject_id=?",
            (artifact_id,),
        ).fetchone()
        return not tombstone or tombstone["generation"] < row["generation"]

    def read_artifact(
        self, artifact_id: str, project_id: str, *, authorization_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        artifact = self._current_artifact(artifact_id)
        context = authorization_context or {}
        if (
            not artifact or context.get("subject_id") != artifact_id or context.get("project_id") != project_id
            or not self.can_consume(artifact_id, project_id=project_id, **{
                key: context.get(key) for key in (
                    "expected_version_id", "expected_generation", "expected_source_generation",
                    "purpose", "location", "processor", "now"
                )
            })
        ):
            return None
        row = self.db.execute(
            """SELECT a.id artifact_id,a.source_id,a.project_id,a.title,a.category,a.generation,
                      v.id version_id,v.version_no,v.original_text,v.content_hash
               FROM artifact a JOIN artifact_version v ON v.id=a.current_version_id WHERE a.id=?""",
            (artifact_id,),
        ).fetchone()
        return dict(row)

    def search(
        self, query: str, project_id: str, *, authorization_contexts: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        hits = self.db.execute(
            "SELECT artifact_id,version_id FROM artifact_fts WHERE artifact_fts MATCH ? ORDER BY artifact_id",
            (query,),
        ).fetchall()
        result = []
        for hit in hits:
            item = self.read_artifact(
                hit["artifact_id"], project_id,
                authorization_context=(authorization_contexts or {}).get(hit["artifact_id"]),
            )
            if item and item["version_id"] == hit["version_id"]:
                result.append(item)
        return result

    def recovery_package(
        self, project_id: str, *, authorization_contexts: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        package: Dict[str, Any] = {
            "project_id": project_id,
            "stopping_point": [], "changes": [], "decisions": [], "unprocessed": [], "evidence_gaps": [],
        }
        mapping = {"stopping_point": "stopping_point", "change": "changes", "decision": "decisions", "unprocessed": "unprocessed"}
        rows = self.db.execute("SELECT id,category FROM artifact WHERE project_id=? ORDER BY id", (project_id,)).fetchall()
        for row in rows:
            item = self.read_artifact(
                row["id"], project_id, authorization_context=(authorization_contexts or {}).get(row["id"])
            )
            if item:
                package[mapping.get(row["category"], "unprocessed")].append(item)
            else:
                package["evidence_gaps"].append({"artifact_id": row["id"], "reason": "unavailable_or_unauthorized"})
        return package

    def suggest_next_step(
        self, project_id: str, *, authorization_contexts: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        self._invalidate_generation_mismatches(project_id)
        package = self.recovery_package(project_id, authorization_contexts=authorization_contexts)
        evidence = package["decisions"] + package["unprocessed"]
        if len(evidence) < 2:
            return {"candidate": None, "message": "暂无可靠建议", "reason": "insufficient_current_evidence"}
        evidence = sorted(evidence, key=lambda x: x["version_id"])
        evidence_versions = [x["version_id"] for x in evidence]
        input_version = package["unprocessed"][0]["version_id"]
        evidence_identity = [
            {
                "version_id": item["version_id"],
                "artifact_generation": item["generation"],
                "source_generation": self.db.execute(
                    "SELECT generation FROM source WHERE id=?", (item["source_id"],)
                ).fetchone()["generation"],
            }
            for item in evidence
        ]
        evidence_key = self._hash(json.dumps(evidence_identity, sort_keys=True))[:16]
        derivation_id = f"derivation:next:{project_id}:{evidence_key}"
        text = "核对恢复候选的来源、版本与确认状态"
        self.db.execute(
            "INSERT OR IGNORE INTO derivation VALUES(?,?,?,?,?,?,?,?)",
            (derivation_id, "candidate_next_step", input_version, text, "unconfirmed", 1, "deterministic-rule-v1", FIXED_NOW),
        )
        for ordinal, item in enumerate(evidence_identity):
            self.db.execute(
                "INSERT OR IGNORE INTO derivation_input VALUES(?,?,?,?,?)",
                (
                    derivation_id, item["version_id"], ordinal,
                    item["artifact_generation"], item["source_generation"],
                ),
            )
        self.db.commit()
        current = self.db.execute("SELECT status FROM derivation WHERE id=?", (derivation_id,)).fetchone()
        status = current["status"]
        labels = {
            "unconfirmed": "规则 / AI 建议·未确认",
            "confirmed": "规则 / AI 建议·已确认",
            "edited_confirmed": "规则 / AI 建议·编辑后确认",
        }
        return {
            "candidate": {
                "id": derivation_id,
                "text": text,
                "label": labels.get(status, f"规则 / AI 建议·{status}"),
                "status": status,
                "evidence_version_id": input_version,
                "evidence_version_ids": evidence_versions,
                "evidence_identity": evidence_identity,
            },
            "message": None,
        }

    def _invalidate_generation_mismatches(self, project_id: str) -> None:
        self.db.execute(
            """UPDATE derivation SET status='stale'
                 WHERE status='unconfirmed' AND id IN (
                   SELECT DISTINCT i.derivation_id
                     FROM derivation_input i
                     JOIN artifact_version v ON v.id=i.version_id
                     JOIN artifact a ON a.id=v.artifact_id
                     JOIN source s ON s.id=a.source_id
                    WHERE a.project_id=? AND (
                      a.current_version_id<>i.version_id
                      OR a.generation<>i.artifact_generation
                      OR s.generation<>i.source_generation
                    )
                 )""",
            (project_id,),
        )
        self.db.commit()

    def _derivation_projection(
        self,
        derivation_id: str,
        project_id: str,
        authorization_contexts: Optional[Dict[str, Dict[str, Any]]],
        *,
        allowed_statuses: Iterable[str] = ("unconfirmed", "confirmed", "edited_confirmed"),
    ) -> Optional[Dict[str, Any]]:
        derivation = self.db.execute("SELECT * FROM derivation WHERE id=?", (derivation_id,)).fetchone()
        if not derivation or derivation["status"] not in set(allowed_statuses):
            return None
        inputs = self.db.execute(
            """SELECT i.version_id,i.artifact_generation,i.source_generation,
                      a.id artifact_id,a.project_id,a.current_version_id
                 FROM derivation_input i
                 JOIN artifact_version v ON v.id=i.version_id
                 JOIN artifact a ON a.id=v.artifact_id
                WHERE i.derivation_id=? ORDER BY i.ordinal""",
            (derivation_id,),
        ).fetchall()
        if not inputs:
            return None
        for item in inputs:
            context = (authorization_contexts or {}).get(item["artifact_id"])
            if (
                item["project_id"] != project_id
                or item["current_version_id"] != item["version_id"]
                or not context
                or context.get("expected_generation") != item["artifact_generation"]
                or context.get("expected_source_generation") != item["source_generation"]
                or self.read_artifact(
                    item["artifact_id"], project_id, authorization_context=context
                ) is None
            ):
                return None
        result = dict(derivation)
        result["evidence_version_ids"] = [item["version_id"] for item in inputs]
        result["evidence_identity"] = [
            {
                "version_id": item["version_id"],
                "artifact_generation": item["artifact_generation"],
                "source_generation": item["source_generation"],
            }
            for item in inputs
        ]
        return result

    def add_feedback(
        self,
        derivation_id: str,
        kind: str,
        user_text: Optional[str] = None,
        *,
        project_id: Optional[str] = None,
        authorization_contexts: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        allowed = {"confirm", "edit_confirm", "reject", "correct", "ignore"}
        if kind not in allowed:
            raise ValueError("unsupported feedback kind")
        if not project_id or self._derivation_projection(
            derivation_id, project_id, authorization_contexts, allowed_statuses=("unconfirmed",)
        ) is None:
            self.db.rollback()
            raise ValueError("candidate unavailable")
        count = self.db.execute("SELECT COUNT(*) n FROM feedback WHERE derivation_id=?", (derivation_id,)).fetchone()["n"]
        feedback_id = f"feedback:{derivation_id}:{count + 1}"
        self.db.execute("INSERT INTO feedback VALUES(?,?,?,?,?,?)", (feedback_id, derivation_id, kind, user_text, "active", FIXED_NOW))
        if kind == "confirm":
            self.db.execute("UPDATE derivation SET status='confirmed' WHERE id=?", (derivation_id,))
        elif kind == "edit_confirm":
            self.db.execute("UPDATE derivation SET status='edited_confirmed' WHERE id=?", (derivation_id,))
        elif kind in {"reject", "correct"}:
            self.db.execute("UPDATE derivation SET status='invalid' WHERE id=?", (derivation_id,))
        self._audit("feedback_added", "feedback", feedback_id, {"kind": kind, "derivation_id": derivation_id})
        self.db.commit()
        return {"feedback_id": feedback_id, "kind": kind, "status": "active"}

    def add_important_link(
        self,
        link_id: str,
        from_id: str,
        to_id: str,
        relation: str,
        confirmed: bool,
        *,
        project_id: Optional[str] = None,
        authorization_contexts: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> None:
        if not project_id or from_id == to_id:
            raise ValueError("link endpoints unavailable")
        contexts = authorization_contexts or {}
        if (
            self.read_artifact(from_id, project_id, authorization_context=contexts.get(from_id)) is None
            or self.read_artifact(to_id, project_id, authorization_context=contexts.get(to_id)) is None
        ):
            raise ValueError("link endpoints unavailable")
        self.db.execute(
            "INSERT INTO important_link VALUES(?,?,?,?,?,?)",
            (link_id, from_id, to_id, relation, "user_explicit", "confirmed" if confirmed else "unconfirmed"),
        )
        self.db.commit()

    def control(self, command: str, subject_id: str) -> Dict[str, Any]:
        allowed = {"revoke_processing", "disconnect_source", "delete_content", "retract_feedback"}
        if command not in allowed:
            raise ValueError("unknown control command")
        self.db.execute("BEGIN IMMEDIATE")
        generation = 1
        if command == "revoke_processing":
            artifact = self._current_artifact(subject_id)
            generation = artifact["generation"] + 1
            self.db.execute("UPDATE artifact SET generation=? WHERE id=?", (generation, subject_id))
            self.db.execute("UPDATE authorization SET decision='revoked',generation=? WHERE subject_id=?", (generation, subject_id))
            self._invalidate_dependents(subject_id)
        elif command == "disconnect_source":
            source = self.db.execute("SELECT generation FROM source WHERE id=?", (subject_id,)).fetchone()
            generation = source["generation"] + 1
            self.db.execute("UPDATE source SET connected=0,generation=? WHERE id=?", (generation, subject_id))
            artifacts = self.db.execute("SELECT id FROM artifact WHERE source_id=?", (subject_id,)).fetchall()
            for artifact in artifacts:
                self._invalidate_dependents(artifact["id"])
        elif command == "delete_content":
            artifact = self._current_artifact(subject_id)
            generation = artifact["generation"] + 1
            self.db.execute("UPDATE artifact SET deleted=1,generation=? WHERE id=?", (generation, subject_id))
            self.db.execute(
                "INSERT OR REPLACE INTO tombstone VALUES('artifact',?,?,?)",
                (subject_id, generation, "user_delete"),
            )
            self.db.execute("UPDATE authorization SET decision='revoked',generation=? WHERE subject_id=?", (generation, subject_id))
            self._invalidate_dependents(subject_id)
        else:
            self.db.execute("UPDATE feedback SET status='retracted' WHERE id=?", (subject_id,))
            derivation = self.db.execute("SELECT derivation_id FROM feedback WHERE id=?", (subject_id,)).fetchone()
            if derivation:
                self.db.execute("UPDATE derivation SET status='stale' WHERE id=?", (derivation["derivation_id"],))
        self._audit(command, "control_subject", subject_id, {"generation": generation, "cleanup": "logical_block_complete_physical_not_claimed"})
        self.db.commit()
        return {"accepted": True, "command": command, "subject_id": subject_id, "active_block": True, "physical_cleanup": "not_claimed"}

    def _invalidate_dependents(self, artifact_id: str) -> None:
        row = self._current_artifact(artifact_id)
        if not row:
            return
        self.db.execute("DELETE FROM artifact_fts WHERE artifact_id=?", (artifact_id,))
        self.db.execute("UPDATE outbox_job SET status='cancelled' WHERE subject_id=? AND status IN ('pending','failed')", (artifact_id,))
        versions = [x["id"] for x in self.db.execute("SELECT id FROM artifact_version WHERE artifact_id=?", (artifact_id,)).fetchall()]
        if versions:
            marks = ",".join("?" for _ in versions)
            self.db.execute(
                f"""UPDATE derivation SET status='stale' WHERE id IN (
                        SELECT derivation_id FROM derivation_input WHERE version_id IN ({marks})
                    )""",
                versions,
            )

    def export_test_package(
        self, project_id: str, *, authorization_contexts: Optional[Dict[str, Dict[str, Any]]] = None,
        fail_artifact_ids: Iterable[str] = (),
    ) -> Dict[str, Any]:
        failures = set(fail_artifact_ids)
        package: Dict[str, Any] = {
            "format": "lifeos-controlled-test-v1-not-frozen",
            "project_id": project_id,
            "artifacts": [], "artifact_versions": [], "sources": [], "authorizations": [],
            "derivations": [], "feedback": [], "links": [], "excluded": [],
            "partial_failures": [], "tombstones": [], "control_states": [],
            "derivation_states": [], "feedback_states": [],
        }
        rows = self.db.execute(
            """SELECT a.id,a.source_id,a.current_version_id,a.deleted,a.generation,
                      s.connected,s.tombstoned AS source_tombstoned,s.generation AS source_generation
               FROM artifact a JOIN source s ON s.id=a.source_id
               WHERE a.project_id=? ORDER BY a.id""",
            (project_id,),
        ).fetchall()
        project_artifact_ids = {row["id"] for row in rows}
        project_version_ids = {
            x["id"] for x in self.db.execute(
                "SELECT v.id FROM artifact_version v JOIN artifact a ON a.id=v.artifact_id WHERE a.project_id=?",
                (project_id,),
            ).fetchall()
        }
        for row in rows:
            auth_rows = self.db.execute(
                "SELECT * FROM authorization WHERE subject_id=? ORDER BY id", (row["id"],)
            ).fetchall()
            auth = auth_rows[0] if len(auth_rows) == 1 else None
            package["control_states"].append({
                "artifact_id": row["id"], "source_id": row["source_id"],
                "current_version_id": row["current_version_id"], "artifact_generation": row["generation"],
                "deleted": bool(row["deleted"]), "source_connected": bool(row["connected"]),
                "source_tombstoned": bool(row["source_tombstoned"]), "source_generation": row["source_generation"],
                "purpose": auth["purpose"] if auth else None, "location": auth["location"] if auth else None,
                "processor": auth["processor"] if auth else None, "decision": auth["decision"] if auth else None,
                "expires_at": auth["expires_at"] if auth else None,
                "auth_generation": auth["generation"] if auth else None,
                "authorization_record_count": len(auth_rows),
            })
            if row["id"] in failures:
                package["partial_failures"].append({"artifact_id": row["id"], "reason": "injected_export_failure"})
                continue
            item = self.read_artifact(
                row["id"], project_id, authorization_context=(authorization_contexts or {}).get(row["id"])
            )
            if item:
                package["artifacts"].append(item)
            else:
                package["excluded"].append({"artifact_id": row["id"], "reason": "current_gate_denied"})
        allowed_artifact_ids = {x["artifact_id"] for x in package["artifacts"]}
        allowed_version_ids = {x["version_id"] for x in package["artifacts"]}
        allowed_source_ids = {x["source_id"] for x in package["artifacts"]}
        if allowed_artifact_ids:
            marks = ",".join("?" for _ in allowed_artifact_ids)
            package["artifact_versions"] = [dict(x) for x in self.db.execute(
                f"SELECT * FROM artifact_version WHERE artifact_id IN ({marks}) AND id IN ({','.join('?' for _ in allowed_version_ids)}) ORDER BY id",
                (*sorted(allowed_artifact_ids), *sorted(allowed_version_ids)),
            )]
            package["authorizations"] = [dict(x) for x in self.db.execute(
                f"SELECT * FROM authorization WHERE subject_id IN ({marks}) AND purpose='lifeos_local_recovery' AND location='local' AND processor='local_rules' AND decision='allow' ORDER BY id",
                tuple(sorted(allowed_artifact_ids)),
            )]
        if allowed_source_ids:
            marks = ",".join("?" for _ in allowed_source_ids)
            package["sources"] = [dict(x) for x in self.db.execute(
                f"SELECT * FROM source WHERE id IN ({marks}) AND connected=1 AND tombstoned=0 ORDER BY id",
                tuple(sorted(allowed_source_ids)),
            )]
        all_derivation_rows = []
        if project_version_ids:
            marks = ",".join("?" for _ in project_version_ids)
            rows_for_project = self.db.execute(
                f"""SELECT DISTINCT d.* FROM derivation d JOIN derivation_input i ON i.derivation_id=d.id
                    WHERE i.version_id IN ({marks}) ORDER BY d.id""", tuple(sorted(project_version_ids))
            ).fetchall()
            for row in rows_for_project:
                item = dict(row)
                inputs = self.db.execute(
                    """SELECT i.version_id,i.artifact_generation,i.source_generation,a.project_id
                         FROM derivation_input i
                         JOIN artifact_version v ON v.id=i.version_id
                         JOIN artifact a ON a.id=v.artifact_id
                        WHERE i.derivation_id=? ORDER BY i.ordinal""",
                    (row["id"],),
                ).fetchall()
                # State/debug fields are export payload too. A mixed-Project
                # dependency is omitted entirely instead of being disclosed as state.
                if not inputs or any(x["project_id"] != project_id for x in inputs):
                    continue
                item["evidence_version_ids"] = [x["version_id"] for x in inputs]
                item["evidence_identity"] = [
                    {
                        "version_id": x["version_id"],
                        "artifact_generation": x["artifact_generation"],
                        "source_generation": x["source_generation"],
                    }
                    for x in inputs
                ]
                all_derivation_rows.append(item)
        package["derivation_states"] = all_derivation_rows
        package["derivations"] = []
        for item in all_derivation_rows:
            if not set(item["evidence_version_ids"]).issubset(allowed_version_ids):
                continue
            current = self._derivation_projection(
                item["id"], project_id, authorization_contexts,
            )
            if current is not None:
                package["derivations"].append(current)
        allowed_derivation_ids = {x["id"] for x in package["derivations"]}
        all_feedback_rows = [dict(x) for x in self.db.execute(
            f"SELECT * FROM feedback WHERE derivation_id IN ({','.join('?' for _ in {x['id'] for x in all_derivation_rows})}) ORDER BY id",
            tuple(sorted({x["id"] for x in all_derivation_rows})),
        )] if all_derivation_rows else []
        package["feedback_states"] = all_feedback_rows
        package["feedback"] = [x for x in all_feedback_rows if x["derivation_id"] in allowed_derivation_ids and x["status"] == "active"]
        package["links"] = [dict(x) for x in self.db.execute(
            "SELECT * FROM important_link ORDER BY id"
        ) if x["from_artifact_id"] in allowed_artifact_ids and x["to_artifact_id"] in allowed_artifact_ids]
        package["tombstones"] = [dict(x) for x in self.db.execute(
            "SELECT * FROM tombstone ORDER BY subject_type,subject_id"
        ) if x["subject_type"] == "artifact" and x["subject_id"] in project_artifact_ids]
        package["status"] = "partial" if package["partial_failures"] else "complete"
        package["checksum"] = self._hash(json.dumps(package, ensure_ascii=False, sort_keys=True))
        return package

    def restore_candidates(
        self, stale_package: Dict[str, Any], *,
        authorization_contexts: Optional[Dict[str, Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        def checksum_valid(package: Dict[str, Any]) -> bool:
            supplied = package.get("checksum")
            if not supplied:
                return False
            content = {key: value for key, value in package.items() if key != "checksum"}
            return supplied == self._hash(json.dumps(content, ensure_ascii=False, sort_keys=True))

        if not checksum_valid(stale_package):
            return {"restored": [], "excluded": [], "conflicts": [{"reason": "package_checksum_invalid"}], "status": "candidate_only"}
        project_id = stale_package.get("project_id")
        restored, excluded = [], []
        for artifact in stale_package.get("artifacts", []):
            current = self._current_artifact(artifact["artifact_id"])
            context = (authorization_contexts or {}).get(artifact["artifact_id"])
            projection = self.read_artifact(
                artifact["artifact_id"], project_id, authorization_context=context
            ) if current and current["project_id"] == project_id else None
            if projection is not None:
                restored.append(projection)
            else:
                excluded.append({"artifact_id": artifact["artifact_id"], "reason": "authoritative_current_gate_denied"})
        restored_ids = {x["artifact_id"] for x in restored}
        version_to_artifact = {x["version_id"]: x["artifact_id"] for x in restored}
        restored_derivations, excluded_derivations = [], []
        for item in stale_package.get("derivations", []):
            projection = self._derivation_projection(
                item.get("id", ""), project_id, authorization_contexts,
            )
            parents = {
                version_to_artifact.get(version_id)
                for version_id in (projection or {}).get("evidence_version_ids", [])
            }
            if projection is None or not parents or None in parents or not parents.issubset(restored_ids):
                excluded_derivations.append({"id": item["id"], "reason": "derivation_not_current_or_parent_denied"})
            else:
                restored_derivations.append(projection)
        restored_derivation_ids = {x["id"] for x in restored_derivations}
        restored_feedback, excluded_feedback = [], []
        for item in stale_package.get("feedback", []):
            state = self.db.execute("SELECT * FROM feedback WHERE id=?", (item["id"],)).fetchone()
            if item["derivation_id"] not in restored_derivation_ids or state is None or state["status"] != "active":
                excluded_feedback.append({"id": item["id"], "reason": "feedback_retracted_or_parent_denied"})
            else:
                restored_feedback.append(dict(state))
        restored_links, excluded_links = [], []
        for item in stale_package.get("links", []):
            state = self.db.execute("SELECT * FROM important_link WHERE id=?", (item.get("id"),)).fetchone()
            if (
                state is None or state["from_artifact_id"] not in restored_ids
                or state["to_artifact_id"] not in restored_ids
            ):
                excluded_links.append({"id": item.get("id"), "reason": "link_not_authoritative_or_parent_denied"})
            else:
                restored_links.append(dict(state))
        return {
            "restored": restored, "excluded": excluded, "conflicts": [],
            "restored_derivations": restored_derivations, "excluded_derivations": excluded_derivations,
            "restored_feedback": restored_feedback, "excluded_feedback": excluded_feedback,
            "restored_links": restored_links, "excluded_links": excluded_links,
            "status": "candidate_only",
        }

    def backup_to_connection(self, target: sqlite3.Connection) -> None:
        """SQLite-aware controlled backup; callers provide the test-only target."""
        self.db.backup(target)

    def capability_call(self, capability: str) -> None:
        if capability not in self.DISABLED_CAPABILITIES or self.DISABLED_CAPABILITIES[capability] is False:
            raise DisabledCapability(f"{capability} is disabled and has no runtime adapter")

    def ux_contract(self, state: str) -> Dict[str, Any]:
        valid = {"normal", "empty", "saving_failed", "restricted", "evidence_gap", "confirmed", "rejected", "corrected", "revoked", "deleted"}
        if state not in valid:
            raise ValueError("unknown UX state")
        return {
            "state": state,
            "announced": True,
            "keyboard_only": True,
            "focus_order": ["project_selector", "context_items", "candidate", "feedback_controls"],
            "focus_return": "trigger",
            "reduced_motion": "no_required_animation",
            "candidate_identity_visible": True,
            "source_or_gap_visible": True,
        }

    def semantic_counts(self) -> Dict[str, int]:
        tables = ["source", "artifact", "artifact_version", "derivation", "derivation_input", "feedback", "authorization", "audit_entry", "important_link"]
        return {table: self.db.execute(f"SELECT COUNT(*) n FROM {table}").fetchone()["n"] for table in tables}
