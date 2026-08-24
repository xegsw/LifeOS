import { createHash } from "node:crypto";
import { DatabaseSync } from "node:sqlite";
import type { CaptureInput } from "./types.ts";

export class AuthorityStore {
  readonly db: DatabaseSync;

  constructor(path = ":memory:") {
    this.db = new DatabaseSync(path);
    this.db.exec("PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL;");
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS source(
        id TEXT PRIMARY KEY, kind TEXT NOT NULL, locator TEXT NOT NULL,
        generation INTEGER NOT NULL DEFAULT 1, tombstoned INTEGER NOT NULL DEFAULT 0
      );
      CREATE TABLE IF NOT EXISTS artifact(
        id TEXT PRIMARY KEY, source_id TEXT NOT NULL REFERENCES source(id), project_id TEXT NOT NULL,
        title TEXT NOT NULL, category TEXT NOT NULL, current_version_id TEXT NOT NULL,
        generation INTEGER NOT NULL DEFAULT 1, tombstoned INTEGER NOT NULL DEFAULT 0
      );
      CREATE TABLE IF NOT EXISTS artifact_version(
        id TEXT PRIMARY KEY, artifact_id TEXT NOT NULL REFERENCES artifact(id), version_no INTEGER NOT NULL,
        original_text TEXT NOT NULL, content_hash TEXT NOT NULL, content_kind TEXT NOT NULL,
        UNIQUE(artifact_id, version_no)
      );
      CREATE TRIGGER IF NOT EXISTS artifact_version_no_update BEFORE UPDATE ON artifact_version
      BEGIN SELECT RAISE(ABORT, 'artifact versions are immutable'); END;
      CREATE TRIGGER IF NOT EXISTS artifact_version_no_delete BEFORE DELETE ON artifact_version
      BEGIN SELECT RAISE(ABORT, 'artifact versions are immutable'); END;
      CREATE TABLE IF NOT EXISTS authorization(
        id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, purpose TEXT NOT NULL, location TEXT NOT NULL,
        processor TEXT NOT NULL, decision TEXT NOT NULL, generation INTEGER NOT NULL DEFAULT 1,
        expires_at_ms INTEGER
      );
      CREATE TABLE IF NOT EXISTS derivation(
        id TEXT PRIMARY KEY, project_id TEXT NOT NULL, kind TEXT NOT NULL, output_text TEXT NOT NULL,
        -- Legacy compatibility/display pointer only; derivation_input is the complete authority set.
        status TEXT NOT NULL, evidence_version_id TEXT NOT NULL, artifact_generation INTEGER NOT NULL,
        source_generation INTEGER NOT NULL
      );
      CREATE TABLE IF NOT EXISTS derivation_input(
        derivation_id TEXT NOT NULL REFERENCES derivation(id),
        evidence_version_id TEXT NOT NULL REFERENCES artifact_version(id),
        artifact_id TEXT NOT NULL REFERENCES artifact(id), source_id TEXT NOT NULL REFERENCES source(id),
        artifact_generation INTEGER NOT NULL, source_generation INTEGER NOT NULL,
        PRIMARY KEY(derivation_id, evidence_version_id)
      );
      CREATE TABLE IF NOT EXISTS feedback(
        id TEXT PRIMARY KEY, derivation_id TEXT NOT NULL, kind TEXT NOT NULL, user_text TEXT,
        status TEXT NOT NULL DEFAULT 'active'
      );
      CREATE TABLE IF NOT EXISTS important_link(
        id TEXT PRIMARY KEY, project_id TEXT NOT NULL,
        from_artifact_id TEXT NOT NULL REFERENCES artifact(id), from_version_id TEXT NOT NULL REFERENCES artifact_version(id),
        from_source_id TEXT NOT NULL REFERENCES source(id),
        to_artifact_id TEXT NOT NULL REFERENCES artifact(id), to_version_id TEXT NOT NULL REFERENCES artifact_version(id),
        to_source_id TEXT NOT NULL REFERENCES source(id),
        link_identity TEXT NOT NULL, confirmation_status TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS important_link_evidence(
        link_id TEXT NOT NULL REFERENCES important_link(id),
        evidence_version_id TEXT NOT NULL REFERENCES artifact_version(id),
        artifact_id TEXT NOT NULL REFERENCES artifact(id), source_id TEXT NOT NULL REFERENCES source(id),
        artifact_generation INTEGER NOT NULL, source_generation INTEGER NOT NULL,
        PRIMARY KEY(link_id, evidence_version_id)
      );
      CREATE TABLE IF NOT EXISTS tombstone(
        subject_type TEXT NOT NULL, subject_id TEXT NOT NULL, generation INTEGER NOT NULL, reason TEXT NOT NULL,
        PRIMARY KEY(subject_type, subject_id)
      );
      CREATE TABLE IF NOT EXISTS outbox_job(
        id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, generation INTEGER NOT NULL,
        status TEXT NOT NULL, lease_generation INTEGER NOT NULL DEFAULT 0,
        idempotency_key TEXT NOT NULL UNIQUE
      );
      CREATE TABLE IF NOT EXISTS submission(
        idempotency_key TEXT PRIMARY KEY, artifact_id TEXT NOT NULL, version_id TEXT NOT NULL
      );
      CREATE VIRTUAL TABLE IF NOT EXISTS artifact_fts USING fts5(artifact_id UNINDEXED, version_id UNINDEXED, body);
    `);
  }

  close(): void { this.db.close(); }

  capture(input: CaptureInput): { saved: boolean; deduplicated: boolean; artifactId?: string } {
    const duplicate = this.db.prepare("SELECT artifact_id FROM submission WHERE idempotency_key=?").get(input.idempotencyKey) as any;
    if (duplicate) return { saved: true, deduplicated: true, artifactId: duplicate.artifact_id };
    const versionId = `${input.artifactId}:v1`;
    try {
      this.db.exec("BEGIN IMMEDIATE");
      this.db.prepare("INSERT INTO source(id,kind,locator) VALUES(?,?,?)").run(input.sourceId, "user_capture", `synthetic://${input.sourceId}`);
      this.db.prepare("INSERT INTO artifact(id,source_id,project_id,title,category,current_version_id) VALUES(?,?,?,?,?,?)")
        .run(input.artifactId, input.sourceId, input.projectId, input.title, input.category, versionId);
      this.db.prepare("INSERT INTO artifact_version VALUES(?,?,?,?,?,?)").run(
        versionId, input.artifactId, 1, input.originalText,
        createHash("sha256").update(input.originalText).digest("hex"), "user_original",
      );
      this.db.prepare(`INSERT INTO authorization(
        id,subject_id,purpose,location,processor,decision,generation,expires_at_ms
      ) VALUES(?,?,?,?,?,?,?,NULL)`).run(
        `auth:${input.artifactId}`, input.artifactId, "lifeos_local_recovery", "local", "local_rules", "allow", 1,
      );
      this.db.prepare("INSERT INTO submission VALUES(?,?,?)").run(input.idempotencyKey, input.artifactId, versionId);
      this.db.prepare("INSERT INTO outbox_job VALUES(?,?,?,?,?,?)").run(
        `index:${input.artifactId}:1`, input.artifactId, 1, "pending", 0, `index:${input.artifactId}:1`,
      );
      if (input.failBeforeCommit) throw new Error("injected authoritative failure");
      this.db.exec("COMMIT");
      return { saved: true, deduplicated: false, artifactId: input.artifactId };
    } catch {
      this.db.exec("ROLLBACK");
      return { saved: false, deduplicated: false };
    }
  }

  processIndexJobs(injectFailure = false): { processed: number; failed: number } {
    const jobs = this.db.prepare("SELECT * FROM outbox_job WHERE status='pending'").all() as any[];
    let processed = 0, failed = 0;
    for (const job of jobs) {
      const current = this.db.prepare("SELECT generation,tombstoned,current_version_id FROM artifact WHERE id=?").get(job.subject_id) as any;
      if (!current || current.tombstoned || current.generation !== job.generation) {
        this.db.prepare("UPDATE outbox_job SET status='cancelled' WHERE id=?").run(job.id); continue;
      }
      const lease = job.lease_generation + 1;
      this.db.prepare("UPDATE outbox_job SET status='leased',lease_generation=? WHERE id=? AND lease_generation=?").run(lease, job.id, job.lease_generation);
      if (injectFailure) {
        this.db.prepare("UPDATE outbox_job SET status='failed' WHERE id=? AND lease_generation=?").run(job.id, lease); failed++; continue;
      }
      const version = this.db.prepare("SELECT original_text FROM artifact_version WHERE id=?").get(current.current_version_id) as any;
      this.db.prepare("INSERT INTO artifact_fts(artifact_id,version_id,body) VALUES(?,?,?)").run(job.subject_id, current.current_version_id, version.original_text);
      this.db.prepare("UPDATE outbox_job SET status='complete' WHERE id=? AND lease_generation=?").run(job.id, lease); processed++;
    }
    return { processed, failed };
  }
}
