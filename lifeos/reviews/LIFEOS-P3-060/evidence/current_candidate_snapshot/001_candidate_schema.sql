-- LIFEOS-P3-031 candidate SQLite migration.
-- CANDIDATE ONLY: not a production migration and not a frozen Schema/API.
-- Synthetic empty databases only. SQLite >= 3.38 with JSON1 and FTS5 is assumed.

PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

CREATE TABLE schema_migration_meta (
  version INTEGER PRIMARY KEY CHECK (version >= 1),
  migration_name TEXT NOT NULL UNIQUE,
  candidate_only INTEGER NOT NULL CHECK (candidate_only = 1),
  schema_checksum TEXT NOT NULL,
  applied_at_ms INTEGER NOT NULL
);

CREATE TABLE project (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  purpose TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft','active','paused','completed','archived','cancelled')),
  generation INTEGER NOT NULL CHECK (generation >= 1),
  last_focused_at_ms INTEGER,
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
);

CREATE TABLE source (
  id TEXT PRIMARY KEY,
  kind TEXT NOT NULL,
  stable_key TEXT NOT NULL,
  display_locator TEXT NOT NULL,
  access_status TEXT NOT NULL CHECK (access_status IN ('available','disconnected','blocked')),
  license_status TEXT NOT NULL CHECK (license_status IN ('allowed','restricted','unknown')),
  generation INTEGER NOT NULL CHECK (generation >= 1),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  UNIQUE (kind, stable_key)
);

CREATE TABLE artifact (
  id TEXT PRIMARY KEY,
  primary_source_id TEXT REFERENCES source(id),
  current_version_id TEXT,
  kind TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft','active','archived','blocked','deleted')),
  generation INTEGER NOT NULL CHECK (generation >= 1),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
);

CREATE TABLE artifact_version (
  id TEXT PRIMARY KEY,
  artifact_id TEXT NOT NULL REFERENCES artifact(id),
  version_no INTEGER NOT NULL CHECK (version_no >= 1),
  source_id TEXT REFERENCES source(id),
  content_blob TEXT NOT NULL,
  content_hash TEXT NOT NULL CHECK (content_hash GLOB 'sha256:*'),
  content_time_ms INTEGER,
  captured_at_ms INTEGER NOT NULL,
  created_at_ms INTEGER NOT NULL,
  UNIQUE (artifact_id, version_no)
);

CREATE TABLE semantic_object (
  id TEXT PRIMARY KEY,
  object_type TEXT NOT NULL CHECK (object_type IN ('assertion','decision','action','event')),
  project_id TEXT REFERENCES project(id),
  current_version_no INTEGER,
  origin_identity TEXT NOT NULL CHECK (origin_identity IN ('user','external','ai_generated','ai_inference','ai_suggestion')),
  business_status TEXT NOT NULL,
  evidence_status TEXT NOT NULL,
  generation INTEGER NOT NULL CHECK (generation >= 1),
  status TEXT NOT NULL CHECK (status IN ('draft','active','migration_required','blocked','deleted')),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
);

CREATE TABLE semantic_object_version (
  id TEXT PRIMARY KEY,
  object_id TEXT NOT NULL REFERENCES semantic_object(id),
  version_no INTEGER NOT NULL CHECK (version_no >= 1),
  payload_schema TEXT NOT NULL,
  schema_major INTEGER NOT NULL CHECK (schema_major = 1),
  schema_minor INTEGER NOT NULL CHECK (schema_minor >= 0),
  payload_json TEXT NOT NULL CHECK (json_valid(payload_json) AND json_type(payload_json) = 'object'),
  content_hash TEXT NOT NULL CHECK (content_hash GLOB 'sha256:*'),
  migrated_from_version_no INTEGER,
  migrator_version TEXT,
  migrator_hash TEXT,
  created_at_ms INTEGER NOT NULL,
  UNIQUE (object_id, version_no),
  CHECK ((migrated_from_version_no IS NULL AND migrator_version IS NULL AND migrator_hash IS NULL)
      OR (migrated_from_version_no IS NOT NULL AND migrator_version IS NOT NULL AND migrator_hash IS NOT NULL))
);

CREATE TABLE authorization (
  id TEXT PRIMARY KEY,
  logical_key TEXT NOT NULL,
  grantor_ref TEXT NOT NULL,
  processor TEXT NOT NULL,
  purpose TEXT NOT NULL,
  location TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('proposed','granted','active','expired','revoked','superseded')),
  version_no INTEGER NOT NULL CHECK (version_no >= 1),
  generation INTEGER NOT NULL CHECK (generation >= 1),
  valid_from_ms INTEGER NOT NULL,
  expires_mode TEXT NOT NULL CHECK (expires_mode IN ('at','indefinite')),
  expires_at_ms INTEGER,
  revoked_at_ms INTEGER,
  policy_version TEXT NOT NULL,
  supersedes_id TEXT REFERENCES authorization(id),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL,
  UNIQUE (logical_key, version_no),
  CHECK ((expires_mode = 'at' AND expires_at_ms IS NOT NULL AND expires_at_ms > valid_from_ms)
      OR (expires_mode = 'indefinite' AND expires_at_ms IS NULL))
);

CREATE TABLE authorization_scope (
  id TEXT PRIMARY KEY,
  authorization_id TEXT NOT NULL REFERENCES authorization(id),
  effect TEXT NOT NULL CHECK (effect IN ('allow','deny')),
  project_id TEXT REFERENCES project(id),
  source_id TEXT REFERENCES source(id),
  artifact_id TEXT REFERENCES artifact(id),
  CHECK ((project_id IS NOT NULL) + (source_id IS NOT NULL) + (artifact_id IS NOT NULL) = 1)
);

CREATE TABLE authorization_action (
  id TEXT PRIMARY KEY,
  authorization_id TEXT NOT NULL REFERENCES authorization(id),
  action TEXT NOT NULL CHECK (action IN ('read','parse','index','derive','export_candidate','restore_evaluate','create_candidate','internal_write')),
  UNIQUE (authorization_id, action)
);

CREATE TABLE authorization_policy (
  authorization_id TEXT PRIMARY KEY REFERENCES authorization(id),
  retention_mode TEXT CHECK (retention_mode IN ('until','indefinite','none')),
  retention_deadline_ms INTEGER,
  sensitivity_rank INTEGER CHECK (sensitivity_rank BETWEEN 0 AND 5),
  training_allowed INTEGER CHECK (training_allowed IN (0,1)),
  external_send_allowed INTEGER CHECK (external_send_allowed IN (0,1)),
  recipients_json TEXT CHECK (recipients_json IS NULL OR json_valid(recipients_json)),
  regions_json TEXT CHECK (regions_json IS NULL OR json_valid(regions_json)),
  disclosure_json TEXT CHECK (disclosure_json IS NULL OR json_valid(disclosure_json)),
  source_license_json TEXT CHECK (source_license_json IS NULL OR json_valid(source_license_json)),
  quantity_ceiling INTEGER CHECK (quantity_ceiling IS NULL OR quantity_ceiling >= 0),
  frequency_ceiling INTEGER CHECK (frequency_ceiling IS NULL OR frequency_ceiling >= 0),
  CHECK (retention_mode != 'until' OR retention_deadline_ms IS NOT NULL)
);

CREATE TABLE derivation (
  id TEXT PRIMARY KEY,
  project_id TEXT REFERENCES project(id),
  kind TEXT NOT NULL,
  output_artifact_version_id TEXT REFERENCES artifact_version(id),
  status TEXT NOT NULL CHECK (status IN ('draft','active','stale','invalid')),
  purpose TEXT NOT NULL,
  location TEXT NOT NULL,
  processor TEXT NOT NULL,
  workflow_version TEXT NOT NULL,
  model_version TEXT,
  authorization_id TEXT NOT NULL REFERENCES authorization(id),
  authorization_generation INTEGER NOT NULL CHECK (authorization_generation >= 1),
  constraint_hash TEXT NOT NULL,
  rebuildable INTEGER NOT NULL CHECK (rebuildable IN (0,1)),
  generated_at_ms INTEGER NOT NULL,
  stale_reason TEXT,
  supersedes_id TEXT REFERENCES derivation(id),
  generation INTEGER NOT NULL CHECK (generation >= 1),
  created_at_ms INTEGER NOT NULL,
  updated_at_ms INTEGER NOT NULL
);

CREATE TABLE content_identity (
  artifact_version_id TEXT PRIMARY KEY REFERENCES artifact_version(id),
  identity_kind TEXT NOT NULL CHECK (identity_kind IN ('user_original','user_edited','external_original','external_reference','quoted_excerpt','ai_generated','ai_inference','ai_suggestion')),
  author_kind TEXT NOT NULL,
  origin_actor_ref TEXT,
  derivation_id TEXT REFERENCES derivation(id),
  CHECK (
    (identity_kind IN ('user_original','user_edited') AND derivation_id IS NULL)
    OR (identity_kind IN ('external_original','external_reference') AND origin_actor_ref IS NOT NULL AND derivation_id IS NULL)
    OR (identity_kind = 'quoted_excerpt' AND origin_actor_ref IS NOT NULL)
    OR (identity_kind IN ('ai_generated','ai_inference','ai_suggestion') AND origin_actor_ref IS NULL AND derivation_id IS NOT NULL)
  )
);

CREATE TABLE derivation_constraint (
  derivation_id TEXT PRIMARY KEY REFERENCES derivation(id),
  allowed_projects_json TEXT NOT NULL CHECK (json_valid(allowed_projects_json)),
  allowed_purposes_json TEXT NOT NULL CHECK (json_valid(allowed_purposes_json)),
  allowed_locations_json TEXT NOT NULL CHECK (json_valid(allowed_locations_json)),
  allowed_processors_json TEXT NOT NULL CHECK (json_valid(allowed_processors_json)),
  sensitivity_rank INTEGER NOT NULL CHECK (sensitivity_rank BETWEEN 0 AND 5),
  disclosure TEXT NOT NULL,
  retention_until_ms INTEGER,
  training_allowed INTEGER NOT NULL CHECK (training_allowed IN (0,1)),
  source_license_rule TEXT NOT NULL,
  constraint_hash TEXT NOT NULL
);

CREATE TABLE feedback (
  id TEXT PRIMARY KEY,
  actor_ref TEXT NOT NULL,
  event_seq INTEGER NOT NULL UNIQUE CHECK (event_seq >= 1),
  target_type TEXT NOT NULL CHECK (target_type IN ('artifact','semantic_object','derivation','important_link')),
  target_id TEXT NOT NULL,
  target_version INTEGER NOT NULL CHECK (target_version >= 1),
  kind TEXT NOT NULL CHECK (kind IN ('confirm','reject','correct','ignore','complete','defer','retract')),
  user_text TEXT,
  basis_feedback_id TEXT REFERENCES feedback(id),
  retracts_feedback_id TEXT REFERENCES feedback(id),
  idempotency_key TEXT NOT NULL UNIQUE,
  canonical_request_hash TEXT NOT NULL,
  applied_at_ms INTEGER NOT NULL,
  CHECK ((kind = 'retract' AND retracts_feedback_id IS NOT NULL) OR (kind != 'retract' AND retracts_feedback_id IS NULL)),
  CHECK ((kind IN ('complete','defer') AND basis_feedback_id IS NOT NULL) OR (kind NOT IN ('complete','defer')))
);

CREATE TABLE feedback_dependency (
  feedback_id TEXT NOT NULL REFERENCES feedback(id),
  basis_feedback_id TEXT NOT NULL REFERENCES feedback(id),
  dependency_kind TEXT NOT NULL CHECK (dependency_kind IN ('requires_confirmation','explicit_basis')),
  PRIMARY KEY (feedback_id, basis_feedback_id),
  CHECK (feedback_id <> basis_feedback_id)
);

CREATE TABLE artifact_project_link (
  id TEXT PRIMARY KEY,
  artifact_id TEXT NOT NULL REFERENCES artifact(id),
  project_id TEXT NOT NULL REFERENCES project(id),
  link_identity TEXT NOT NULL,
  confirmation_status TEXT NOT NULL CHECK (confirmation_status IN ('candidate','confirmed','rejected')),
  generation INTEGER NOT NULL CHECK (generation >= 1),
  UNIQUE (artifact_id, project_id, link_identity)
);

CREATE TABLE important_link (
  id TEXT PRIMARY KEY,
  project_id TEXT REFERENCES project(id),
  from_type TEXT NOT NULL,
  from_id TEXT NOT NULL,
  from_version INTEGER NOT NULL,
  to_type TEXT NOT NULL,
  to_id TEXT NOT NULL,
  to_version INTEGER NOT NULL,
  relation_type TEXT NOT NULL,
  link_identity TEXT NOT NULL,
  confirmation_status TEXT NOT NULL CHECK (confirmation_status IN ('candidate','confirmed','rejected')),
  generation INTEGER NOT NULL CHECK (generation >= 1),
  derivation_id TEXT REFERENCES derivation(id),
  status TEXT NOT NULL CHECK (status IN ('active','stale','blocked')),
  CHECK (NOT (from_type = to_type AND from_id = to_id AND from_version = to_version))
);

CREATE TABLE link_evidence (
  link_id TEXT NOT NULL REFERENCES important_link(id),
  artifact_version_id TEXT NOT NULL REFERENCES artifact_version(id),
  source_id TEXT NOT NULL REFERENCES source(id),
  artifact_generation INTEGER NOT NULL CHECK (artifact_generation >= 1),
  source_generation INTEGER NOT NULL CHECK (source_generation >= 1),
  evidence_role TEXT NOT NULL,
  PRIMARY KEY (link_id, artifact_version_id, evidence_role)
);

CREATE TABLE tombstone (
  subject_type TEXT NOT NULL CHECK (subject_type IN ('artifact','source','semantic_object','derivation','important_link','authorization')),
  subject_id TEXT NOT NULL,
  generation INTEGER NOT NULL CHECK (generation >= 1),
  command_id TEXT NOT NULL,
  reason_code TEXT NOT NULL,
  blocked_at_ms INTEGER NOT NULL,
  cleanup_status TEXT NOT NULL CHECK (cleanup_status IN ('accepted','active_blocked','cleanup_pending','cleanup_failed','vendor_limited','cleaned','no_cleanup_required')),
  updated_at_ms INTEGER NOT NULL,
  PRIMARY KEY (subject_type, subject_id)
);

CREATE TABLE audit_entry (
  id TEXT PRIMARY KEY,
  action_code TEXT NOT NULL,
  scoped_actor_ref TEXT NOT NULL,
  scoped_subject_ref TEXT NOT NULL,
  authorization_version INTEGER,
  result_code TEXT NOT NULL,
  occurred_at_ms INTEGER NOT NULL,
  correlation_id TEXT NOT NULL UNIQUE
);

CREATE TABLE submission (
  namespace TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  canonical_request_hash TEXT NOT NULL CHECK (
    length(canonical_request_hash) = 71
    AND substr(canonical_request_hash, 1, 7) = 'sha256:'
    AND substr(canonical_request_hash, 8) NOT GLOB '*[^0-9a-f]*'
  ),
  command TEXT NOT NULL,
  result_subject_id TEXT NOT NULL,
  result_version_id TEXT,
  committed_at_ms INTEGER NOT NULL,
  PRIMARY KEY (namespace, idempotency_key)
);

-- Non-core, append-only transaction intent. Actor is an application claim,
-- not a database/OS/cryptographic identity assertion. Generated result fields
-- bind a one-shot command to the exact terminal transition it requests.
CREATE TABLE authorization_lifecycle_command (
  id TEXT PRIMARY KEY,
  idempotency_key TEXT NOT NULL UNIQUE,
  authorization_id TEXT NOT NULL REFERENCES authorization(id),
  expected_generation INTEGER NOT NULL CHECK (expected_generation >= 1),
  target_status TEXT NOT NULL CHECK (target_status IN ('revoked','expired','superseded')),
  scoped_actor_claim TEXT NOT NULL CHECK (length(scoped_actor_claim) > 0),
  canonical_request_hash TEXT NOT NULL CHECK (
    length(canonical_request_hash) = 71
    AND substr(canonical_request_hash, 1, 7) = 'sha256:'
    AND substr(canonical_request_hash, 8) NOT GLOB '*[^0-9a-f]*'
  ),
  requested_at_ms INTEGER NOT NULL,
  processed_at_ms INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER) * 1000),
  result_generation INTEGER GENERATED ALWAYS AS (expected_generation + 1) STORED,
  correlation_id TEXT GENERATED ALWAYS AS (
    'authorization-state:' || authorization_id || ':' || (expected_generation + 1) || ':' || target_status
  ) STORED,
  UNIQUE (authorization_id, result_generation)
);

CREATE TABLE outbox_job (
  id TEXT PRIMARY KEY,
  job_type TEXT NOT NULL,
  subject_type TEXT NOT NULL,
  subject_id TEXT NOT NULL,
  subject_generation INTEGER NOT NULL CHECK (subject_generation >= 1),
  payload_ref TEXT,
  status TEXT NOT NULL CHECK (status IN ('pending','leased','completed','cancelled','dead_letter')),
  attempts INTEGER NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  available_at_ms INTEGER NOT NULL,
  lease_owner TEXT,
  lease_generation INTEGER NOT NULL DEFAULT 0 CHECK (lease_generation >= 0),
  lease_expires_at_ms INTEGER,
  idempotency_key TEXT NOT NULL UNIQUE,
  last_error_code TEXT
);

-- Non-core, append-only worker intent. Direct runtime UPDATE is forbidden;
-- this command binds the caller's expected full lease state before applying
-- one enumerated transition. It is not business authority or an identity.
CREATE TABLE outbox_runtime_command (
  id TEXT PRIMARY KEY,
  job_id TEXT NOT NULL,
  operation TEXT NOT NULL CHECK (operation IN (
    'claim','renew','retry','cancel','dead_letter','complete'
  )),
  expected_status TEXT NOT NULL CHECK (expected_status IN ('pending','leased')),
  expected_available_at_ms INTEGER NOT NULL,
  expected_lease_owner TEXT,
  expected_lease_generation INTEGER NOT NULL CHECK (expected_lease_generation >= 0),
  expected_lease_expires_at_ms INTEGER,
  requested_lease_owner TEXT,
  requested_lease_expires_at_ms INTEGER,
  requested_available_at_ms INTEGER,
  error_code TEXT,
  requested_at_ms INTEGER NOT NULL,
  processed_at_ms INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER) * 1000)
);

-- Candidate-only retention parameter. Production duration is deliberately not
-- frozen: absence means Authorization lifecycle jobs cannot be deleted.
CREATE TABLE outbox_retention_policy (
  scope TEXT PRIMARY KEY CHECK (scope = 'authorization_lifecycle'),
  retention_ms INTEGER NOT NULL CHECK (retention_ms >= 0),
  configured_at_ms INTEGER NOT NULL DEFAULT (CAST(strftime('%s','now') AS INTEGER) * 1000)
);

-- Per-job immutable snapshot created with the lifecycle outbox row. A policy
-- configured later cannot retroactively make an existing job deletable.
CREATE TABLE outbox_retention_binding (
  job_id TEXT PRIMARY KEY,
  lifecycle_correlation_id TEXT NOT NULL UNIQUE,
  scope TEXT NOT NULL CHECK (scope = 'authorization_lifecycle'),
  retention_ms INTEGER NOT NULL CHECK (retention_ms >= 0),
  bound_at_ms INTEGER NOT NULL
);

CREATE TABLE search_index_state (
  artifact_version_id TEXT PRIMARY KEY REFERENCES artifact_version(id),
  artifact_generation INTEGER NOT NULL CHECK (artifact_generation >= 1),
  source_generation INTEGER NOT NULL CHECK (source_generation >= 1),
  indexed_hash TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('fresh','stale','degraded','blocked')),
  updated_at_ms INTEGER NOT NULL
);

CREATE VIRTUAL TABLE artifact_fts USING fts5(
  artifact_version_id UNINDEXED,
  artifact_id UNINDEXED,
  body
);

CREATE INDEX idx_artifact_current_status ON artifact(current_version_id, status);
CREATE INDEX idx_artifact_version_parent ON artifact_version(artifact_id, version_no DESC);
CREATE INDEX idx_artifact_version_hash ON artifact_version(content_hash);
CREATE INDEX idx_source_generation ON source(generation);
CREATE INDEX idx_project_link_project ON artifact_project_link(project_id, confirmation_status);
CREATE INDEX idx_authorization_match ON authorization(processor, purpose, location, status, expires_at_ms);
CREATE UNIQUE INDEX uq_authorization_active_logical ON authorization(logical_key) WHERE status = 'active';
CREATE INDEX idx_scope_project ON authorization_scope(project_id, effect) WHERE project_id IS NOT NULL;
CREATE INDEX idx_scope_source ON authorization_scope(source_id, effect) WHERE source_id IS NOT NULL;
CREATE INDEX idx_scope_artifact ON authorization_scope(artifact_id, effect) WHERE artifact_id IS NOT NULL;
CREATE INDEX idx_derivation_project ON derivation(project_id, status, generated_at_ms);
CREATE UNIQUE INDEX uq_feedback_retract_child ON feedback(retracts_feedback_id) WHERE retracts_feedback_id IS NOT NULL;
CREATE INDEX idx_feedback_target ON feedback(target_type, target_id, target_version, event_seq);
CREATE INDEX idx_tombstone_generation ON tombstone(subject_type, subject_id, generation);
CREATE INDEX idx_outbox_ready ON outbox_job(status, available_at_ms, lease_expires_at_ms);
CREATE INDEX idx_lifecycle_command_authorization ON authorization_lifecycle_command(authorization_id, result_generation);
CREATE INDEX idx_outbox_runtime_command_job ON outbox_runtime_command(job_id, processed_at_ms);

-- derivation_input is created after all referenced parents so its exact-one contract is visible.
CREATE TABLE derivation_input (
  id TEXT PRIMARY KEY,
  derivation_id TEXT NOT NULL REFERENCES derivation(id),
  input_type TEXT NOT NULL CHECK (input_type IN ('artifact_version','semantic_object','feedback','source')),
  artifact_version_id TEXT REFERENCES artifact_version(id),
  semantic_object_id TEXT REFERENCES semantic_object(id),
  feedback_id TEXT REFERENCES feedback(id),
  source_id TEXT REFERENCES source(id),
  artifact_generation INTEGER CHECK (artifact_generation IS NULL OR artifact_generation >= 1),
  source_generation INTEGER CHECK (source_generation IS NULL OR source_generation >= 1),
  input_content_hash TEXT NOT NULL,
  CHECK ((artifact_version_id IS NOT NULL) + (semantic_object_id IS NOT NULL) + (feedback_id IS NOT NULL) + (source_id IS NOT NULL) = 1),
  CHECK ((input_type = 'artifact_version' AND artifact_version_id IS NOT NULL)
      OR (input_type = 'semantic_object' AND semantic_object_id IS NOT NULL)
      OR (input_type = 'feedback' AND feedback_id IS NOT NULL)
      OR (input_type = 'source' AND source_id IS NOT NULL))
);

-- The four partial indexes follow derivation_input creation.
CREATE UNIQUE INDEX uq_derivation_artifact_input ON derivation_input(derivation_id, artifact_version_id) WHERE artifact_version_id IS NOT NULL;
CREATE UNIQUE INDEX uq_derivation_semantic_input ON derivation_input(derivation_id, semantic_object_id) WHERE semantic_object_id IS NOT NULL;
CREATE UNIQUE INDEX uq_derivation_feedback_input ON derivation_input(derivation_id, feedback_id) WHERE feedback_id IS NOT NULL;
CREATE UNIQUE INDEX uq_derivation_source_input ON derivation_input(derivation_id, source_id) WHERE source_id IS NOT NULL;

CREATE TRIGGER artifact_version_immutable_update
BEFORE UPDATE ON artifact_version BEGIN SELECT RAISE(ABORT, 'artifact_version_immutable'); END;
CREATE TRIGGER artifact_version_no_delete
BEFORE DELETE ON artifact_version BEGIN SELECT RAISE(ABORT, 'artifact_version_delete_requires_controlled_cleanup'); END;
CREATE TRIGGER semantic_object_version_immutable_update
BEFORE UPDATE ON semantic_object_version BEGIN SELECT RAISE(ABORT, 'semantic_object_version_immutable'); END;
CREATE TRIGGER semantic_object_version_no_delete
BEFORE DELETE ON semantic_object_version BEGIN SELECT RAISE(ABORT, 'semantic_object_version_delete_requires_controlled_cleanup'); END;
CREATE TRIGGER feedback_immutable_update
BEFORE UPDATE ON feedback BEGIN SELECT RAISE(ABORT, 'feedback_append_only'); END;
CREATE TRIGGER feedback_immutable_delete
BEFORE DELETE ON feedback BEGIN SELECT RAISE(ABORT, 'feedback_append_only'); END;

CREATE TRIGGER artifact_current_pointer_insert
BEFORE INSERT ON artifact WHEN NEW.current_version_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM artifact_version v WHERE v.id = NEW.current_version_id AND v.artifact_id = NEW.id
) BEGIN SELECT RAISE(ABORT, 'artifact_current_pointer_not_owned'); END;
CREATE TRIGGER artifact_current_pointer_update
BEFORE UPDATE OF current_version_id, status ON artifact WHEN NEW.current_version_id IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM artifact_version v WHERE v.id = NEW.current_version_id AND v.artifact_id = NEW.id
) BEGIN SELECT RAISE(ABORT, 'artifact_current_pointer_not_owned'); END;

CREATE TRIGGER semantic_payload_contract
BEFORE INSERT ON semantic_object_version
BEGIN
  SELECT CASE WHEN NEW.payload_schema <> (SELECT object_type || '@1.' || NEW.schema_minor FROM semantic_object WHERE id = NEW.object_id)
    THEN RAISE(ABORT, 'semantic_payload_schema_mismatch') END;
  SELECT CASE WHEN EXISTS (
    SELECT 1 FROM json_each(NEW.payload_json) j
    WHERE
      ((SELECT object_type FROM semantic_object WHERE id = NEW.object_id) = 'assertion'
        AND j.key NOT IN ('statement','valid_from','valid_until','qualification')) OR
      ((SELECT object_type FROM semantic_object WHERE id = NEW.object_id) = 'decision'
        AND j.key NOT IN ('decision_text','question','options_considered','rationale','validity_window')) OR
      ((SELECT object_type FROM semantic_object WHERE id = NEW.object_id) = 'action'
        AND j.key NOT IN ('action_text','due_at','defer_until','commitment_to','result_ref')) OR
      ((SELECT object_type FROM semantic_object WHERE id = NEW.object_id) = 'event'
        AND j.key NOT IN ('event_type','description','occurrence'))
  ) THEN RAISE(ABORT, 'semantic_payload_unknown_top_level_key') END;
  SELECT CASE WHEN (SELECT object_type FROM semantic_object WHERE id = NEW.object_id) = 'assertion'
      AND json_type(NEW.payload_json, '$.statement') <> 'text' THEN RAISE(ABORT, 'assertion_statement_required') END;
  SELECT CASE WHEN (SELECT object_type FROM semantic_object WHERE id = NEW.object_id) = 'decision'
      AND json_type(NEW.payload_json, '$.decision_text') <> 'text' THEN RAISE(ABORT, 'decision_text_required') END;
  SELECT CASE WHEN (SELECT object_type FROM semantic_object WHERE id = NEW.object_id) = 'action'
      AND json_type(NEW.payload_json, '$.action_text') <> 'text' THEN RAISE(ABORT, 'action_text_required') END;
  SELECT CASE WHEN (SELECT object_type FROM semantic_object WHERE id = NEW.object_id) = 'event'
      AND (json_type(NEW.payload_json, '$.event_type') <> 'text' OR json_type(NEW.payload_json, '$.description') <> 'text'
           OR json_type(NEW.payload_json, '$.occurrence') IS NULL) THEN RAISE(ABORT, 'event_fields_required') END;
END;

CREATE TRIGGER semantic_current_pointer
BEFORE UPDATE OF current_version_no, status ON semantic_object
WHEN NEW.current_version_no IS NOT NULL AND NOT EXISTS (
  SELECT 1 FROM semantic_object_version v WHERE v.object_id = NEW.id AND v.version_no = NEW.current_version_no AND v.schema_major = 1
) BEGIN SELECT RAISE(ABORT, 'semantic_current_pointer_invalid'); END;

-- Active Derivations require child input/constraint rows, so direct active INSERT
-- is structurally unsafe. Enforce the two-step draft -> complete -> active flow.
CREATE TRIGGER derivation_no_direct_active_insert
BEFORE INSERT ON derivation WHEN NEW.status = 'active'
BEGIN SELECT RAISE(ABORT, 'derivation_must_start_inactive'); END;

CREATE TRIGGER derivation_activation_complete
BEFORE UPDATE OF status ON derivation WHEN NEW.status = 'active' AND OLD.status <> 'active'
BEGIN
  SELECT CASE WHEN NOT EXISTS (SELECT 1 FROM derivation_input i WHERE i.derivation_id = NEW.id)
    THEN RAISE(ABORT, 'derivation_has_no_inputs') END;
  SELECT CASE WHEN NOT EXISTS (SELECT 1 FROM derivation_constraint c WHERE c.derivation_id = NEW.id)
    THEN RAISE(ABORT, 'derivation_has_no_constraint') END;
END;

CREATE TRIGGER content_identity_ai_derivation_complete
BEFORE INSERT ON content_identity
WHEN NEW.identity_kind IN ('ai_generated','ai_inference','ai_suggestion')
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM derivation d WHERE d.id = NEW.derivation_id AND d.status = 'active'
      AND EXISTS (SELECT 1 FROM derivation_input i WHERE i.derivation_id = d.id)
      AND EXISTS (SELECT 1 FROM derivation_constraint c WHERE c.derivation_id = d.id)
  ) THEN RAISE(ABORT, 'ai_identity_requires_active_complete_derivation') END;
END;

CREATE TRIGGER feedback_retract_contract
BEFORE INSERT ON feedback WHEN NEW.kind = 'retract'
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM feedback old
    WHERE old.id = NEW.retracts_feedback_id AND old.actor_ref = NEW.actor_ref
      AND old.target_type = NEW.target_type AND old.target_id = NEW.target_id
      AND old.target_version = NEW.target_version AND old.event_seq < NEW.event_seq
  ) THEN RAISE(ABORT, 'feedback_retract_target_invalid') END;
END;

CREATE TRIGGER feedback_complete_basis_contract
BEFORE INSERT ON feedback WHEN NEW.kind IN ('complete','defer')
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM feedback old WHERE old.id = NEW.basis_feedback_id AND old.kind = 'confirm'
      AND old.actor_ref = NEW.actor_ref AND old.target_type = NEW.target_type
      AND old.target_id = NEW.target_id AND old.target_version = NEW.target_version
      AND old.event_seq < NEW.event_seq
  ) THEN RAISE(ABORT, 'feedback_basis_invalid') END;
END;

CREATE TRIGGER feedback_dependency_contract
BEFORE INSERT ON feedback_dependency
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM feedback f JOIN feedback b ON b.id = NEW.basis_feedback_id
    WHERE f.id = NEW.feedback_id AND b.event_seq < f.event_seq
      AND b.target_type = f.target_type AND b.target_id = f.target_id AND b.target_version = f.target_version
      AND (NEW.dependency_kind <> 'requires_confirmation' OR b.kind = 'confirm')
  ) THEN RAISE(ABORT, 'feedback_dependency_invalid') END;
END;

-- Audit rows are minimum non-sensitive evidence and are append-only. The
-- BEFORE INSERT guard also blocks REPLACE before conflict resolution can
-- implicitly delete an existing row.
CREATE TRIGGER audit_entry_no_reinsert
BEFORE INSERT ON audit_entry WHEN EXISTS (
  SELECT 1 FROM audit_entry old
  WHERE old.id = NEW.id OR old.correlation_id = NEW.correlation_id
)
BEGIN SELECT RAISE(ABORT, 'audit_entry_reinsert_forbidden'); END;

CREATE TRIGGER audit_entry_no_update
BEFORE UPDATE ON audit_entry
BEGIN SELECT RAISE(ABORT, 'audit_entry_append_only'); END;

CREATE TRIGGER audit_entry_no_delete
BEFORE DELETE ON audit_entry
BEGIN SELECT RAISE(ABORT, 'audit_entry_append_only'); END;

-- Outbox identity/business payload is immutable. Only runtime state may move
-- through the explicit state machine below; the queue is never authoritative.
CREATE TRIGGER outbox_job_insert_contract
BEFORE INSERT ON outbox_job
BEGIN
  SELECT CASE WHEN EXISTS (
    SELECT 1 FROM outbox_job old
    WHERE old.id = NEW.id OR old.idempotency_key = NEW.idempotency_key
  ) THEN RAISE(ABORT, 'outbox_job_reinsert_forbidden') END;
  SELECT CASE WHEN NOT (
    NEW.status = 'pending' AND NEW.attempts = 0
    AND NEW.lease_owner IS NULL AND NEW.lease_generation = 0
    AND NEW.lease_expires_at_ms IS NULL AND NEW.last_error_code IS NULL
  ) THEN RAISE(ABORT, 'outbox_job_must_start_pending') END;
  -- authorization_state_change is a reserved lifecycle evidence type.  The
  -- canonical id/idempotency values make the lifecycle trigger its sole
  -- producer: command application atomically creates the terminal parent,
  -- audit entry and this one job.  A later direct INSERT cannot recreate the
  -- same canonical identity because either the live job or its replay fence
  -- already exists.
  SELECT CASE WHEN NEW.job_type = 'authorization_state_change'
    AND NEW.subject_type <> 'authorization'
    THEN RAISE(ABORT, 'authorization_outbox_subject_invalid') END;
  SELECT CASE WHEN EXISTS (
    SELECT 1 FROM outbox_retention_binding fence
    WHERE fence.job_id = NEW.id
       OR fence.lifecycle_correlation_id = NEW.idempotency_key
  ) THEN RAISE(ABORT, 'authorization_outbox_replay_fence') END;
  SELECT CASE WHEN NEW.job_type = 'authorization_state_change'
    AND NEW.subject_type = 'authorization'
    AND NOT EXISTS (
      SELECT 1
      FROM authorization_lifecycle_command lifecycle
      JOIN authorization a ON a.id = lifecycle.authorization_id
      JOIN audit_entry audit ON audit.correlation_id = lifecycle.correlation_id
      JOIN submission submission
        ON submission.namespace = 'destruct@1'
       AND submission.idempotency_key = lifecycle.idempotency_key
       AND submission.canonical_request_hash = lifecycle.canonical_request_hash
      WHERE NEW.id = 'outbox:' || lifecycle.correlation_id
        AND NEW.idempotency_key = lifecycle.correlation_id
        AND NEW.subject_id = lifecycle.authorization_id
        AND NEW.subject_generation = lifecycle.result_generation
        AND NEW.payload_ref = lifecycle.target_status
        AND NEW.available_at_ms = lifecycle.processed_at_ms
        AND a.status = lifecycle.target_status
        AND a.generation = lifecycle.result_generation
        AND a.updated_at_ms = lifecycle.processed_at_ms
        AND ((lifecycle.target_status = 'revoked'
              AND a.revoked_at_ms = lifecycle.processed_at_ms)
          OR (lifecycle.target_status IN ('expired','superseded')
              AND a.revoked_at_ms IS NULL))
        AND audit.id = 'audit:' || lifecycle.correlation_id
        AND audit.scoped_actor_ref = lifecycle.scoped_actor_claim
        AND audit.scoped_subject_ref = lifecycle.authorization_id
        AND audit.authorization_version = a.version_no
        AND audit.result_code = 'ok'
        AND audit.occurred_at_ms = lifecycle.processed_at_ms
        AND audit.action_code = CASE lifecycle.target_status
          WHEN 'revoked' THEN 'authorization.revoke'
          WHEN 'expired' THEN 'authorization.expire'
          WHEN 'superseded' THEN 'authorization.supersede'
        END
    ) THEN RAISE(ABORT, 'authorization_outbox_provenance_required') END;
END;

CREATE TRIGGER outbox_job_payload_immutable
BEFORE UPDATE OF id, job_type, subject_type, subject_id, subject_generation,
                 payload_ref, idempotency_key ON outbox_job
WHEN NEW.id IS NOT OLD.id
  OR NEW.job_type IS NOT OLD.job_type
  OR NEW.subject_type IS NOT OLD.subject_type
  OR NEW.subject_id IS NOT OLD.subject_id
  OR NEW.subject_generation IS NOT OLD.subject_generation
  OR NEW.payload_ref IS NOT OLD.payload_ref
  OR NEW.idempotency_key IS NOT OLD.idempotency_key
BEGIN SELECT RAISE(ABORT, 'outbox_job_payload_immutable'); END;

CREATE TRIGGER outbox_job_runtime_state_machine
BEFORE UPDATE OF status, attempts, available_at_ms, lease_owner,
                 lease_generation, lease_expires_at_ms, last_error_code ON outbox_job
WHEN NEW.status IS NOT OLD.status
  OR NEW.attempts IS NOT OLD.attempts
  OR NEW.available_at_ms IS NOT OLD.available_at_ms
  OR NEW.lease_owner IS NOT OLD.lease_owner
  OR NEW.lease_generation IS NOT OLD.lease_generation
  OR NEW.lease_expires_at_ms IS NOT OLD.lease_expires_at_ms
  OR NEW.last_error_code IS NOT OLD.last_error_code
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM outbox_runtime_command cmd
    WHERE cmd.job_id = OLD.id
      AND cmd.expected_status = OLD.status
      AND cmd.expected_available_at_ms = OLD.available_at_ms
      AND cmd.expected_lease_owner IS OLD.lease_owner
      AND cmd.expected_lease_generation = OLD.lease_generation
      AND cmd.expected_lease_expires_at_ms IS OLD.lease_expires_at_ms
      AND (
        (cmd.operation = 'claim'
          AND OLD.status = 'pending' AND NEW.status = 'leased'
          AND NEW.attempts = OLD.attempts + 1
          AND NEW.available_at_ms = OLD.available_at_ms
          AND NEW.lease_owner = cmd.requested_lease_owner
          AND NEW.lease_generation = OLD.lease_generation + 1
          AND NEW.lease_expires_at_ms = cmd.requested_lease_expires_at_ms
          AND NEW.last_error_code IS NULL)
        OR
        (cmd.operation = 'renew'
          AND OLD.status = 'leased' AND NEW.status = 'leased'
          AND NEW.attempts = OLD.attempts
          AND NEW.available_at_ms = OLD.available_at_ms
          AND NEW.lease_owner = OLD.lease_owner
          AND NEW.lease_generation = OLD.lease_generation
          AND NEW.lease_expires_at_ms = cmd.requested_lease_expires_at_ms
          AND NEW.last_error_code IS OLD.last_error_code)
        OR
        (cmd.operation = 'retry'
          AND OLD.status = 'leased' AND NEW.status = 'pending'
          AND NEW.attempts = OLD.attempts
          AND NEW.available_at_ms = cmd.requested_available_at_ms
          AND NEW.lease_owner IS NULL
          AND NEW.lease_generation = OLD.lease_generation
          AND NEW.lease_expires_at_ms IS NULL
          AND NEW.last_error_code = cmd.error_code)
        OR
        (cmd.operation = 'cancel'
          AND OLD.status IN ('pending','leased') AND NEW.status = 'cancelled'
          AND NEW.attempts = OLD.attempts
          AND NEW.available_at_ms = OLD.available_at_ms
          AND NEW.lease_owner IS NULL
          AND NEW.lease_generation = OLD.lease_generation
          AND NEW.lease_expires_at_ms IS NULL
          AND NEW.last_error_code IS cmd.error_code)
        OR
        (cmd.operation = 'dead_letter'
          AND OLD.status = 'leased' AND NEW.status = 'dead_letter'
          AND NEW.attempts = OLD.attempts
          AND NEW.available_at_ms = OLD.available_at_ms
          AND NEW.lease_owner IS NULL
          AND NEW.lease_generation = OLD.lease_generation
          AND NEW.lease_expires_at_ms IS NULL
          AND NEW.last_error_code = cmd.error_code)
        OR
        (cmd.operation = 'complete'
          AND OLD.status = 'leased' AND NEW.status = 'completed'
          AND NEW.attempts = OLD.attempts
          AND NEW.available_at_ms = OLD.available_at_ms
          AND NEW.lease_owner IS NULL
          AND NEW.lease_generation = OLD.lease_generation
          AND NEW.lease_expires_at_ms IS NULL
          AND NEW.last_error_code IS NULL)
      )
  ) THEN RAISE(ABORT, 'outbox_job_runtime_command_required') END;
END;

-- Generic non-authoritative jobs retain their pre-existing terminal cleanup
-- route. Authorization lifecycle jobs add audit and parameterized retention.
CREATE TRIGGER outbox_job_generic_delete_contract
BEFORE DELETE ON outbox_job
WHEN NOT (OLD.job_type = 'authorization_state_change' AND OLD.subject_type = 'authorization')
 AND NOT (
  OLD.status IN ('completed','cancelled','dead_letter')
  AND OLD.lease_owner IS NULL AND OLD.lease_expires_at_ms IS NULL
)
BEGIN SELECT RAISE(ABORT, 'outbox_job_delete_requires_terminal'); END;

CREATE TRIGGER outbox_job_authorization_delete_contract
BEFORE DELETE ON outbox_job
WHEN OLD.job_type = 'authorization_state_change'
 AND OLD.subject_type = 'authorization'
 AND NOT (
  OLD.status IN ('completed','cancelled','dead_letter')
  AND OLD.lease_owner IS NULL AND OLD.lease_expires_at_ms IS NULL
  AND EXISTS (
    SELECT 1 FROM audit_entry e
    WHERE e.correlation_id = OLD.idempotency_key
      AND e.scoped_subject_ref = OLD.subject_id
      AND e.result_code = 'ok'
  )
  AND EXISTS (
    SELECT 1 FROM outbox_retention_binding binding
    JOIN outbox_runtime_command cmd ON cmd.job_id = OLD.id
      AND ((OLD.status = 'completed' AND cmd.operation = 'complete')
        OR (OLD.status = 'cancelled' AND cmd.operation = 'cancel')
        OR (OLD.status = 'dead_letter' AND cmd.operation = 'dead_letter'))
    WHERE binding.job_id = OLD.id
      AND binding.scope = 'authorization_lifecycle'
      AND binding.lifecycle_correlation_id = OLD.idempotency_key
      AND cmd.processed_at_ms + binding.retention_ms
          <= CAST(strftime('%s','now') AS INTEGER) * 1000
  )
)
BEGIN SELECT RAISE(ABORT, 'authorization_outbox_delete_retention_not_satisfied'); END;

CREATE TRIGGER outbox_runtime_command_no_reinsert
BEFORE INSERT ON outbox_runtime_command WHEN EXISTS (
  SELECT 1 FROM outbox_runtime_command old WHERE old.id = NEW.id
)
BEGIN SELECT RAISE(ABORT, 'outbox_runtime_command_replay_forbidden'); END;

CREATE TRIGGER outbox_runtime_command_insert_contract
BEFORE INSERT ON outbox_runtime_command
BEGIN
  SELECT CASE WHEN NEW.processed_at_ms <> CAST(strftime('%s','now') AS INTEGER) * 1000
    THEN RAISE(ABORT, 'outbox_runtime_command_db_time_required') END;
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM outbox_job job
    WHERE job.id = NEW.job_id
      AND job.status = NEW.expected_status
      AND job.available_at_ms = NEW.expected_available_at_ms
      AND job.lease_owner IS NEW.expected_lease_owner
      AND job.lease_generation = NEW.expected_lease_generation
      AND job.lease_expires_at_ms IS NEW.expected_lease_expires_at_ms
  ) THEN RAISE(ABORT, 'outbox_runtime_command_cas_mismatch') END;
  SELECT CASE WHEN NOT (
    (NEW.operation = 'claim'
      AND NEW.expected_status = 'pending'
      AND NEW.expected_lease_owner IS NULL
      AND NEW.expected_lease_expires_at_ms IS NULL
      AND NEW.expected_available_at_ms <= NEW.processed_at_ms
      AND NEW.requested_lease_owner IS NOT NULL
      AND NEW.requested_lease_expires_at_ms > NEW.processed_at_ms
      AND NEW.requested_available_at_ms IS NULL
      AND NEW.error_code IS NULL)
    OR
    (NEW.operation = 'renew'
      AND NEW.expected_status = 'leased'
      AND NEW.expected_lease_owner IS NOT NULL
      AND NEW.expected_lease_expires_at_ms > NEW.processed_at_ms
      AND NEW.requested_lease_owner IS NEW.expected_lease_owner
      AND NEW.requested_lease_expires_at_ms > NEW.expected_lease_expires_at_ms
      AND NEW.requested_available_at_ms IS NULL
      AND NEW.error_code IS NULL)
    OR
    (NEW.operation = 'retry'
      AND NEW.expected_status = 'leased'
      AND NEW.expected_lease_owner IS NOT NULL
      AND NEW.requested_lease_owner IS NULL
      AND NEW.requested_lease_expires_at_ms IS NULL
      AND NEW.requested_available_at_ms >= NEW.processed_at_ms
      AND NEW.error_code IS NOT NULL)
    OR
    (NEW.operation = 'cancel'
      AND NEW.expected_status IN ('pending','leased')
      AND ((NEW.expected_status = 'pending'
            AND NEW.expected_lease_owner IS NULL
            AND NEW.expected_lease_expires_at_ms IS NULL)
        OR (NEW.expected_status = 'leased'
            AND NEW.expected_lease_owner IS NOT NULL))
      AND NEW.requested_lease_owner IS NULL
      AND NEW.requested_lease_expires_at_ms IS NULL
      AND NEW.requested_available_at_ms IS NULL)
    OR
    (NEW.operation = 'dead_letter'
      AND NEW.expected_status = 'leased'
      AND NEW.expected_lease_owner IS NOT NULL
      AND NEW.requested_lease_owner IS NULL
      AND NEW.requested_lease_expires_at_ms IS NULL
      AND NEW.requested_available_at_ms IS NULL
      AND NEW.error_code IS NOT NULL)
    OR
    (NEW.operation = 'complete'
      AND NEW.expected_status = 'leased'
      AND NEW.expected_lease_owner IS NOT NULL
      AND NEW.expected_lease_expires_at_ms > NEW.processed_at_ms
      AND NEW.requested_lease_owner IS NULL
      AND NEW.requested_lease_expires_at_ms IS NULL
      AND NEW.requested_available_at_ms IS NULL
      AND NEW.error_code IS NULL
      AND EXISTS (
        SELECT 1 FROM outbox_job job
        WHERE job.id = NEW.job_id
          AND (job.subject_type <> 'authorization' OR EXISTS (
            SELECT 1 FROM authorization a
            WHERE a.id = job.subject_id AND a.generation = job.subject_generation
          ))
      ))
  ) THEN RAISE(ABORT, 'outbox_runtime_command_invalid') END;
END;

CREATE TRIGGER outbox_runtime_command_apply
AFTER INSERT ON outbox_runtime_command
BEGIN
  UPDATE outbox_job
  SET status = CASE NEW.operation
        WHEN 'claim' THEN 'leased'
        WHEN 'renew' THEN 'leased'
        WHEN 'retry' THEN 'pending'
        WHEN 'cancel' THEN 'cancelled'
        WHEN 'dead_letter' THEN 'dead_letter'
        WHEN 'complete' THEN 'completed'
      END,
      attempts = attempts + CASE WHEN NEW.operation = 'claim' THEN 1 ELSE 0 END,
      available_at_ms = CASE WHEN NEW.operation = 'retry'
                             THEN NEW.requested_available_at_ms ELSE available_at_ms END,
      lease_owner = CASE WHEN NEW.operation = 'claim' THEN NEW.requested_lease_owner
                         WHEN NEW.operation = 'renew' THEN lease_owner ELSE NULL END,
      lease_generation = lease_generation + CASE WHEN NEW.operation = 'claim' THEN 1 ELSE 0 END,
      lease_expires_at_ms = CASE WHEN NEW.operation IN ('claim','renew')
                                 THEN NEW.requested_lease_expires_at_ms ELSE NULL END,
      last_error_code = CASE WHEN NEW.operation IN ('retry','cancel','dead_letter')
                             THEN NEW.error_code ELSE NULL END
  WHERE id = NEW.job_id
    AND status = NEW.expected_status
    AND available_at_ms = NEW.expected_available_at_ms
    AND lease_owner IS NEW.expected_lease_owner
    AND lease_generation = NEW.expected_lease_generation
    AND lease_expires_at_ms IS NEW.expected_lease_expires_at_ms;

  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM outbox_job job
    WHERE job.id = NEW.job_id
      AND job.status = CASE NEW.operation
        WHEN 'claim' THEN 'leased' WHEN 'renew' THEN 'leased'
        WHEN 'retry' THEN 'pending' WHEN 'cancel' THEN 'cancelled'
        WHEN 'dead_letter' THEN 'dead_letter' WHEN 'complete' THEN 'completed' END
      AND job.lease_generation = NEW.expected_lease_generation
          + CASE WHEN NEW.operation = 'claim' THEN 1 ELSE 0 END
  ) THEN RAISE(ABORT, 'outbox_runtime_command_apply_failed') END;
END;

CREATE TRIGGER outbox_runtime_command_no_update
BEFORE UPDATE ON outbox_runtime_command
BEGIN SELECT RAISE(ABORT, 'outbox_runtime_command_append_only'); END;

CREATE TRIGGER outbox_runtime_command_no_delete
BEFORE DELETE ON outbox_runtime_command
BEGIN SELECT RAISE(ABORT, 'outbox_runtime_command_append_only'); END;

CREATE TRIGGER outbox_retention_policy_no_reinsert
BEFORE INSERT ON outbox_retention_policy WHEN EXISTS (
  SELECT 1 FROM outbox_retention_policy old WHERE old.scope = NEW.scope
)
BEGIN SELECT RAISE(ABORT, 'outbox_retention_policy_reinsert_forbidden'); END;

CREATE TRIGGER outbox_retention_policy_db_time
BEFORE INSERT ON outbox_retention_policy
WHEN NEW.configured_at_ms <> CAST(strftime('%s','now') AS INTEGER) * 1000
BEGIN SELECT RAISE(ABORT, 'outbox_retention_policy_db_time_required'); END;

CREATE TRIGGER outbox_retention_policy_no_update
BEFORE UPDATE ON outbox_retention_policy
BEGIN SELECT RAISE(ABORT, 'outbox_retention_policy_append_only'); END;

CREATE TRIGGER outbox_retention_policy_no_delete
BEFORE DELETE ON outbox_retention_policy
BEGIN SELECT RAISE(ABORT, 'outbox_retention_policy_append_only'); END;

CREATE TRIGGER outbox_retention_binding_insert_contract
BEFORE INSERT ON outbox_retention_binding
BEGIN
  SELECT CASE WHEN EXISTS (
    SELECT 1 FROM outbox_retention_binding old WHERE old.job_id = NEW.job_id
       OR old.lifecycle_correlation_id = NEW.lifecycle_correlation_id
  ) THEN RAISE(ABORT, 'outbox_retention_binding_replay_forbidden') END;
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM outbox_job job
    JOIN authorization_lifecycle_command lifecycle
      ON job.idempotency_key = lifecycle.correlation_id
    JOIN outbox_retention_policy policy ON policy.scope = NEW.scope
    WHERE job.id = NEW.job_id
      AND job.job_type = 'authorization_state_change'
      AND job.subject_type = 'authorization'
      AND job.status = 'pending'
      AND job.subject_id = lifecycle.authorization_id
      AND job.subject_generation = lifecycle.result_generation
      AND NEW.lifecycle_correlation_id = lifecycle.correlation_id
      AND job.idempotency_key = lifecycle.correlation_id
      AND NEW.retention_ms = policy.retention_ms
      AND NEW.bound_at_ms = lifecycle.processed_at_ms
      AND policy.configured_at_ms <= lifecycle.processed_at_ms
  ) THEN RAISE(ABORT, 'outbox_retention_binding_invalid') END;
END;

CREATE TRIGGER outbox_retention_binding_no_update
BEFORE UPDATE ON outbox_retention_binding
BEGIN SELECT RAISE(ABORT, 'outbox_retention_binding_append_only'); END;

CREATE TRIGGER outbox_retention_binding_no_delete
BEFORE DELETE ON outbox_retention_binding
BEGIN SELECT RAISE(ABORT, 'outbox_retention_binding_append_only'); END;

CREATE TRIGGER submission_no_reinsert
BEFORE INSERT ON submission WHEN EXISTS (
  SELECT 1 FROM submission old
  WHERE old.namespace = NEW.namespace AND old.idempotency_key = NEW.idempotency_key
)
BEGIN SELECT RAISE(ABORT, 'submission_replay_forbidden'); END;

CREATE TRIGGER submission_no_update
BEFORE UPDATE ON submission
BEGIN SELECT RAISE(ABORT, 'submission_append_only'); END;

CREATE TRIGGER submission_no_delete
BEFORE DELETE ON submission
BEGIN SELECT RAISE(ABORT, 'submission_append_only'); END;

CREATE TRIGGER authorization_lifecycle_command_no_reinsert
BEFORE INSERT ON authorization_lifecycle_command WHEN EXISTS (
  SELECT 1 FROM authorization_lifecycle_command old
  WHERE old.id = NEW.id OR old.idempotency_key = NEW.idempotency_key
     OR (old.authorization_id = NEW.authorization_id
         AND old.result_generation = NEW.result_generation)
)
BEGIN SELECT RAISE(ABORT, 'authorization_lifecycle_command_replay_forbidden'); END;

CREATE TRIGGER authorization_lifecycle_command_insert_contract
BEFORE INSERT ON authorization_lifecycle_command
BEGIN
  SELECT CASE WHEN NEW.processed_at_ms <> CAST(strftime('%s','now') AS INTEGER) * 1000
    THEN RAISE(ABORT, 'authorization_lifecycle_command_db_time_required') END;
  SELECT CASE WHEN NEW.target_status = 'expired' AND NEW.scoped_actor_claim <> 'system:local'
    THEN RAISE(ABORT, 'authorization_expiry_requires_local_system_claim') END;
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM submission s
    WHERE s.namespace = 'destruct@1'
      AND s.idempotency_key = NEW.idempotency_key
      AND s.canonical_request_hash = NEW.canonical_request_hash
      AND s.command = CASE NEW.target_status
        WHEN 'revoked' THEN 'revoke_authorization'
        WHEN 'expired' THEN 'expire_authorization'
        WHEN 'superseded' THEN 'supersede_authorization' END
      AND s.result_subject_id = NEW.authorization_id
      AND s.result_version_id IS NULL
  ) THEN RAISE(ABORT, 'authorization_lifecycle_submission_binding_required') END;
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM authorization a
    WHERE a.id = NEW.authorization_id AND a.status = 'active'
      AND a.generation = NEW.expected_generation
  ) THEN RAISE(ABORT, 'authorization_lifecycle_command_precondition_failed') END;
END;

CREATE TRIGGER authorization_lifecycle_command_no_update
BEFORE UPDATE ON authorization_lifecycle_command
BEGIN SELECT RAISE(ABORT, 'authorization_lifecycle_command_append_only'); END;

CREATE TRIGGER authorization_lifecycle_command_no_delete
BEFORE DELETE ON authorization_lifecycle_command
BEGIN SELECT RAISE(ABORT, 'authorization_lifecycle_command_append_only'); END;

-- Authorization scope/action/policy rows cannot precede their parent because of
-- FKs. Reject direct active INSERT and require the proposed -> complete -> active flow.
CREATE TRIGGER authorization_no_direct_active_insert
BEFORE INSERT ON authorization
WHEN NEW.status NOT IN ('proposed','granted') AND NOT EXISTS (
  SELECT 1 FROM authorization old
  WHERE old.status = 'active' AND (
    old.id = NEW.id OR
    (old.logical_key = NEW.logical_key AND old.version_no = NEW.version_no)
  )
)
BEGIN SELECT RAISE(ABORT, 'authorization_must_start_inactive'); END;

-- Every Authorization starts from the same lifecycle fence.  These checks
-- run for INSERT and INSERT OR REPLACE before conflict resolution; activation
-- repeats them below so an incomplete proposed/granted record cannot bypass
-- the initial contract through a multi-column UPDATE.
CREATE TRIGGER authorization_initial_lifecycle_contract
BEFORE INSERT ON authorization
BEGIN
  SELECT CASE WHEN NEW.generation <> 1
    THEN RAISE(ABORT, 'authorization_initial_generation_must_be_one') END;
  SELECT CASE WHEN NEW.status <> 'revoked' AND NEW.revoked_at_ms IS NOT NULL
    THEN RAISE(ABORT, 'authorization_nonrevoked_initial_revoked_time_forbidden') END;
END;

-- Conflict resolution must not replace an existing active parent. This check
-- runs on INSERT before SQLite can perform REPLACE's implicit delete and covers
-- both identity dimensions without depending on FK or recursive trigger state.
CREATE TRIGGER authorization_no_replace_while_active
BEFORE INSERT ON authorization WHEN EXISTS (
  SELECT 1 FROM authorization old
  WHERE old.status = 'active' AND (
    old.id = NEW.id OR
    (old.logical_key = NEW.logical_key AND old.version_no = NEW.version_no)
  )
)
BEGIN SELECT RAISE(ABORT, 'active_authorization_replace_forbidden'); END;

CREATE TRIGGER authorization_no_replace_while_terminal
BEFORE INSERT ON authorization WHEN EXISTS (
  SELECT 1 FROM authorization old
  WHERE old.status IN ('revoked','expired','superseded') AND (
    old.id = NEW.id OR
    (old.logical_key = NEW.logical_key AND old.version_no = NEW.version_no)
  )
)
BEGIN SELECT RAISE(ABORT, 'terminal_authorization_replace_forbidden'); END;

-- Directly deleting an active parent would permit a DELETE + INSERT rebuild
-- when foreign keys are disabled. Terminal cleanup/history remains a separate
-- contract and is deliberately not expanded here.
CREATE TRIGGER authorization_no_delete_while_active
BEFORE DELETE ON authorization WHEN OLD.status = 'active'
BEGIN SELECT RAISE(ABORT, 'active_authorization_delete_forbidden'); END;

CREATE TRIGGER authorization_no_delete_while_terminal
BEFORE DELETE ON authorization WHEN OLD.status IN ('revoked','expired','superseded')
BEGIN SELECT RAISE(ABORT, 'terminal_authorization_delete_forbidden'); END;

CREATE TRIGGER authorization_activation_complete
BEFORE UPDATE OF status ON authorization WHEN NEW.status = 'active' AND OLD.status <> 'active'
BEGIN
  SELECT CASE WHEN NEW.generation <> 1
    THEN RAISE(ABORT, 'authorization_activation_generation_must_be_one') END;
  SELECT CASE WHEN NEW.revoked_at_ms IS NOT NULL
    THEN RAISE(ABORT, 'authorization_activation_revoked_time_forbidden') END;
  SELECT CASE WHEN NOT EXISTS (SELECT 1 FROM authorization_scope s WHERE s.authorization_id = NEW.id)
    THEN RAISE(ABORT, 'authorization_has_no_scope') END;
  SELECT CASE WHEN NOT EXISTS (SELECT 1 FROM authorization_action a WHERE a.authorization_id = NEW.id)
    THEN RAISE(ABORT, 'authorization_has_no_action') END;
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM authorization_policy p WHERE p.authorization_id = NEW.id
      AND p.retention_mode IS NOT NULL AND p.sensitivity_rank IS NOT NULL
      AND p.training_allowed IS NOT NULL AND p.external_send_allowed IS NOT NULL
      AND p.recipients_json IS NOT NULL AND p.regions_json IS NOT NULL
      AND p.disclosure_json IS NOT NULL AND p.source_license_json IS NOT NULL
      AND p.quantity_ceiling IS NOT NULL AND p.frequency_ceiling IS NOT NULL
  ) THEN RAISE(ABORT, 'authorization_policy_incomplete') END;
  SELECT CASE WHEN NEW.version_no > 1 AND NEW.supersedes_id IS NULL
    THEN RAISE(ABORT, 'authorization_new_version_requires_supersedes') END;
  SELECT CASE WHEN NEW.version_no = 1 AND NEW.supersedes_id IS NOT NULL
    THEN RAISE(ABORT, 'authorization_first_version_cannot_supersede') END;
  SELECT CASE WHEN NEW.supersedes_id IS NOT NULL AND NOT EXISTS (
    SELECT 1 FROM authorization old WHERE old.id = NEW.supersedes_id
      AND old.logical_key = NEW.logical_key AND old.status = 'superseded'
      AND old.version_no = NEW.version_no - 1
  ) THEN RAISE(ABORT, 'authorization_old_version_not_superseded') END;
END;

-- Authorization lifecycle is forward-only. Leaving active is possible only
-- while the one-shot lifecycle command row is being inserted.
CREATE TRIGGER authorization_status_transition
BEFORE UPDATE OF status ON authorization WHEN NEW.status <> OLD.status
BEGIN
  SELECT CASE WHEN NOT (
    (OLD.status = 'proposed' AND NEW.status IN ('granted','active')) OR
    (OLD.status = 'granted' AND NEW.status = 'active') OR
    (OLD.status = 'active' AND NEW.status IN ('revoked','expired','superseded'))
  ) THEN RAISE(ABORT, 'authorization_status_transition_invalid') END;
END;

CREATE TRIGGER authorization_active_retirement_contract
BEFORE UPDATE OF status ON authorization
WHEN OLD.status = 'active' AND NEW.status IN ('revoked','expired','superseded')
BEGIN
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM authorization_lifecycle_command cmd
    WHERE cmd.authorization_id = OLD.id
      AND cmd.expected_generation = OLD.generation
      AND cmd.result_generation = NEW.generation
      AND cmd.target_status = NEW.status
      AND cmd.processed_at_ms = NEW.updated_at_ms
  ) THEN RAISE(ABORT, 'authorization_retirement_requires_lifecycle_command') END;
  SELECT CASE WHEN NEW.generation <> OLD.generation + 1
    THEN RAISE(ABORT, 'authorization_retirement_generation_invalid') END;
  SELECT CASE WHEN NEW.created_at_ms <> OLD.created_at_ms
    THEN RAISE(ABORT, 'authorization_created_at_immutable') END;
  SELECT CASE WHEN NOT (
    (NEW.status = 'revoked' AND NEW.revoked_at_ms = NEW.updated_at_ms)
    OR (NEW.status IN ('expired','superseded') AND NEW.revoked_at_ms IS NULL)
  ) THEN RAISE(ABORT, 'authorization_terminal_time_invalid') END;
END;

CREATE TRIGGER authorization_generation_lifecycle_only
BEFORE UPDATE OF generation ON authorization WHEN NEW.generation <> OLD.generation
BEGIN
  SELECT CASE WHEN NOT (
    OLD.status = 'active' AND NEW.status IN ('revoked','expired','superseded')
    AND NEW.generation = OLD.generation + 1
    AND EXISTS (
      SELECT 1 FROM authorization_lifecycle_command cmd
      WHERE cmd.authorization_id = OLD.id
        AND cmd.expected_generation = OLD.generation
        AND cmd.result_generation = NEW.generation
        AND cmd.target_status = NEW.status
        AND cmd.processed_at_ms = NEW.updated_at_ms
    )
  ) THEN RAISE(ABORT, 'authorization_generation_requires_lifecycle_command') END;
END;

CREATE TRIGGER authorization_created_at_immutable
BEFORE UPDATE OF created_at_ms ON authorization
WHEN NEW.created_at_ms <> OLD.created_at_ms
BEGIN SELECT RAISE(ABORT, 'authorization_created_at_immutable'); END;

CREATE TRIGGER authorization_revoked_time_contract
BEFORE UPDATE OF revoked_at_ms ON authorization
WHEN NEW.revoked_at_ms IS NOT OLD.revoked_at_ms
BEGIN
  SELECT CASE WHEN NOT (
    OLD.status = 'active' AND NEW.status = 'revoked'
    AND NEW.generation = OLD.generation + 1
    AND NEW.revoked_at_ms = NEW.updated_at_ms
    AND EXISTS (
      SELECT 1 FROM authorization_lifecycle_command cmd
      WHERE cmd.authorization_id = OLD.id
        AND cmd.expected_generation = OLD.generation
        AND cmd.target_status = 'revoked'
        AND cmd.result_generation = NEW.generation
        AND cmd.processed_at_ms = NEW.updated_at_ms
    )
  ) THEN RAISE(ABORT, 'authorization_revoked_time_requires_lifecycle_command') END;
END;

CREATE TRIGGER authorization_terminal_immutable
BEFORE UPDATE ON authorization WHEN OLD.status IN ('revoked','expired','superseded')
BEGIN SELECT RAISE(ABORT, 'terminal_authorization_immutable'); END;

CREATE TRIGGER authorization_version_identity_immutable
BEFORE UPDATE OF logical_key, version_no, supersedes_id ON authorization
WHEN NEW.logical_key <> OLD.logical_key
  OR NEW.version_no <> OLD.version_no
  OR NEW.supersedes_id IS NOT OLD.supersedes_id
BEGIN SELECT RAISE(ABORT, 'authorization_version_identity_immutable'); END;

-- Once active, the parent security envelope is immutable. Any envelope change
-- must be expressed by retiring this version and activating a complete successor.
-- IS NOT is intentional: expires_at_ms is nullable and must compare NULL safely.
CREATE TRIGGER authorization_security_envelope_immutable_while_active
BEFORE UPDATE OF grantor_ref, processor, purpose, location, valid_from_ms,
                 expires_mode, expires_at_ms, policy_version ON authorization
WHEN OLD.status = 'active' AND (
  NEW.grantor_ref IS NOT OLD.grantor_ref OR
  NEW.processor IS NOT OLD.processor OR
  NEW.purpose IS NOT OLD.purpose OR
  NEW.location IS NOT OLD.location OR
  NEW.valid_from_ms IS NOT OLD.valid_from_ms OR
  NEW.expires_mode IS NOT OLD.expires_mode OR
  NEW.expires_at_ms IS NOT OLD.expires_at_ms OR
  NEW.policy_version IS NOT OLD.policy_version
)
BEGIN SELECT RAISE(ABORT, 'active_authorization_security_envelope_immutable'); END;

-- The command INSERT is the single SQLite statement that owns retirement.
-- Its nested UPDATE is authorized by the matching command row; audit/outbox
-- conflicts abort the whole INSERT statement, including the parent update.
CREATE TRIGGER authorization_lifecycle_command_apply
AFTER INSERT ON authorization_lifecycle_command
BEGIN
  UPDATE authorization
  SET status = NEW.target_status,
      generation = NEW.result_generation,
      revoked_at_ms = CASE WHEN NEW.target_status = 'revoked'
                           THEN NEW.processed_at_ms ELSE NULL END,
      updated_at_ms = NEW.processed_at_ms
  WHERE id = NEW.authorization_id
    AND status = 'active'
    AND generation = NEW.expected_generation;

  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM authorization a
    WHERE a.id = NEW.authorization_id
      AND a.status = NEW.target_status
      AND a.generation = NEW.result_generation
      AND a.updated_at_ms = NEW.processed_at_ms
      AND ((NEW.target_status = 'revoked' AND a.revoked_at_ms = NEW.processed_at_ms)
        OR (NEW.target_status IN ('expired','superseded') AND a.revoked_at_ms IS NULL))
  ) THEN RAISE(ABORT, 'authorization_lifecycle_command_apply_failed') END;

  INSERT INTO audit_entry(
    id, action_code, scoped_actor_ref, scoped_subject_ref,
    authorization_version, result_code, occurred_at_ms, correlation_id
  )
  SELECT 'audit:' || NEW.correlation_id,
         CASE NEW.target_status
           WHEN 'revoked' THEN 'authorization.revoke'
           WHEN 'expired' THEN 'authorization.expire'
           WHEN 'superseded' THEN 'authorization.supersede'
         END,
         NEW.scoped_actor_claim, NEW.authorization_id, a.version_no,
         'ok', NEW.processed_at_ms, NEW.correlation_id
  FROM authorization a WHERE a.id = NEW.authorization_id;

  INSERT INTO outbox_job(
    id, job_type, subject_type, subject_id, subject_generation, payload_ref,
    status, attempts, available_at_ms, lease_owner, lease_generation,
    lease_expires_at_ms, idempotency_key, last_error_code
  ) VALUES (
    'outbox:' || NEW.correlation_id, 'authorization_state_change',
    'authorization', NEW.authorization_id, NEW.result_generation,
    NEW.target_status, 'pending', 0, NEW.processed_at_ms,
    NULL, 0, NULL, NEW.correlation_id, NULL
  );

  INSERT INTO outbox_retention_binding(
    job_id, lifecycle_correlation_id, scope, retention_ms, bound_at_ms
  )
  SELECT 'outbox:' || NEW.correlation_id, NEW.correlation_id, policy.scope,
         policy.retention_ms, NEW.processed_at_ms
  FROM outbox_retention_policy policy
  WHERE policy.scope = 'authorization_lifecycle';
END;

-- Active Authorization children are part of an immutable authorization
-- envelope. INSERT/UPDATE/DELETE checks both OLD and NEW parents so rebinds
-- cannot move a child out of or into active. BEFORE INSERT also rejects
-- INSERT OR REPLACE before SQLite performs conflict resolution.
CREATE TRIGGER authorization_scope_no_insert_while_active
BEFORE INSERT ON authorization_scope WHEN EXISTS (
  SELECT 1 FROM authorization a WHERE a.id = NEW.authorization_id AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_scope_insert_forbidden'); END;

CREATE TRIGGER authorization_scope_no_update_while_active
BEFORE UPDATE ON authorization_scope WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id IN (OLD.authorization_id, NEW.authorization_id) AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_scope_update_forbidden'); END;

CREATE TRIGGER authorization_scope_no_delete_while_active
BEFORE DELETE ON authorization_scope WHEN EXISTS (
  SELECT 1 FROM authorization a WHERE a.id = OLD.authorization_id AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_scope_delete_forbidden'); END;

CREATE TRIGGER authorization_action_no_insert_while_active
BEFORE INSERT ON authorization_action WHEN EXISTS (
  SELECT 1 FROM authorization a WHERE a.id = NEW.authorization_id AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_action_insert_forbidden'); END;

CREATE TRIGGER authorization_action_no_update_while_active
BEFORE UPDATE ON authorization_action WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id IN (OLD.authorization_id, NEW.authorization_id) AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_action_update_forbidden'); END;

CREATE TRIGGER authorization_action_no_delete_while_active
BEFORE DELETE ON authorization_action WHEN EXISTS (
  SELECT 1 FROM authorization a WHERE a.id = OLD.authorization_id AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_action_delete_forbidden'); END;

CREATE TRIGGER authorization_policy_no_insert_while_active
BEFORE INSERT ON authorization_policy WHEN EXISTS (
  SELECT 1 FROM authorization a WHERE a.id = NEW.authorization_id AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_policy_insert_forbidden'); END;

CREATE TRIGGER authorization_policy_no_update_while_active
BEFORE UPDATE ON authorization_policy WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id IN (OLD.authorization_id, NEW.authorization_id) AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_policy_update_forbidden'); END;

CREATE TRIGGER authorization_policy_no_delete_while_active
BEFORE DELETE ON authorization_policy WHEN EXISTS (
  SELECT 1 FROM authorization a WHERE a.id = OLD.authorization_id AND a.status = 'active'
) BEGIN SELECT RAISE(ABORT, 'active_authorization_policy_delete_forbidden'); END;

-- Terminal authorization history is immutable. The only mutation exception is
-- one-way deletion of sensitive child projections behind an Authorization
-- tombstone at cleanup_pending with a matching minimum append-only audit.
CREATE TRIGGER authorization_scope_no_insert_while_terminal
BEFORE INSERT ON authorization_scope WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id = NEW.authorization_id AND a.status IN ('revoked','expired','superseded')
) BEGIN SELECT RAISE(ABORT, 'terminal_authorization_scope_insert_forbidden'); END;

CREATE TRIGGER authorization_scope_no_update_while_terminal
BEFORE UPDATE ON authorization_scope WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id IN (OLD.authorization_id, NEW.authorization_id)
    AND a.status IN ('revoked','expired','superseded')
) BEGIN SELECT RAISE(ABORT, 'terminal_authorization_scope_update_forbidden'); END;

CREATE TRIGGER authorization_scope_delete_terminal_contract
BEFORE DELETE ON authorization_scope WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id = OLD.authorization_id AND a.status IN ('revoked','expired','superseded')
) AND NOT EXISTS (
  SELECT 1 FROM authorization a
  JOIN tombstone t ON t.subject_type = 'authorization'
    AND t.subject_id = a.id AND t.generation = a.generation
  JOIN audit_entry e ON e.scoped_subject_ref = a.id
    AND e.authorization_version = a.version_no
    AND e.action_code = 'authorization.cleanup'
    AND e.result_code = 'redacted_by_user'
    AND e.correlation_id = 'authorization-cleanup:' || a.id || ':' || a.generation
  WHERE a.id = OLD.authorization_id
    AND a.status IN ('revoked','expired','superseded')
    AND t.cleanup_status = 'cleanup_pending'
)
BEGIN SELECT RAISE(ABORT, 'terminal_authorization_scope_delete_requires_cleanup'); END;

CREATE TRIGGER authorization_action_no_insert_while_terminal
BEFORE INSERT ON authorization_action WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id = NEW.authorization_id AND a.status IN ('revoked','expired','superseded')
) BEGIN SELECT RAISE(ABORT, 'terminal_authorization_action_insert_forbidden'); END;

CREATE TRIGGER authorization_action_no_update_while_terminal
BEFORE UPDATE ON authorization_action WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id IN (OLD.authorization_id, NEW.authorization_id)
    AND a.status IN ('revoked','expired','superseded')
) BEGIN SELECT RAISE(ABORT, 'terminal_authorization_action_update_forbidden'); END;

CREATE TRIGGER authorization_action_delete_terminal_contract
BEFORE DELETE ON authorization_action WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id = OLD.authorization_id AND a.status IN ('revoked','expired','superseded')
) AND NOT EXISTS (
  SELECT 1 FROM authorization a
  JOIN tombstone t ON t.subject_type = 'authorization'
    AND t.subject_id = a.id AND t.generation = a.generation
  JOIN audit_entry e ON e.scoped_subject_ref = a.id
    AND e.authorization_version = a.version_no
    AND e.action_code = 'authorization.cleanup'
    AND e.result_code = 'redacted_by_user'
    AND e.correlation_id = 'authorization-cleanup:' || a.id || ':' || a.generation
  WHERE a.id = OLD.authorization_id
    AND a.status IN ('revoked','expired','superseded')
    AND t.cleanup_status = 'cleanup_pending'
)
BEGIN SELECT RAISE(ABORT, 'terminal_authorization_action_delete_requires_cleanup'); END;

CREATE TRIGGER authorization_policy_no_insert_while_terminal
BEFORE INSERT ON authorization_policy WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id = NEW.authorization_id AND a.status IN ('revoked','expired','superseded')
) BEGIN SELECT RAISE(ABORT, 'terminal_authorization_policy_insert_forbidden'); END;

CREATE TRIGGER authorization_policy_no_update_while_terminal
BEFORE UPDATE ON authorization_policy WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id IN (OLD.authorization_id, NEW.authorization_id)
    AND a.status IN ('revoked','expired','superseded')
) BEGIN SELECT RAISE(ABORT, 'terminal_authorization_policy_update_forbidden'); END;

CREATE TRIGGER authorization_policy_delete_terminal_contract
BEFORE DELETE ON authorization_policy WHEN EXISTS (
  SELECT 1 FROM authorization a
  WHERE a.id = OLD.authorization_id AND a.status IN ('revoked','expired','superseded')
) AND NOT EXISTS (
  SELECT 1 FROM authorization a
  JOIN tombstone t ON t.subject_type = 'authorization'
    AND t.subject_id = a.id AND t.generation = a.generation
  JOIN audit_entry e ON e.scoped_subject_ref = a.id
    AND e.authorization_version = a.version_no
    AND e.action_code = 'authorization.cleanup'
    AND e.result_code = 'redacted_by_user'
    AND e.correlation_id = 'authorization-cleanup:' || a.id || ':' || a.generation
  WHERE a.id = OLD.authorization_id
    AND a.status IN ('revoked','expired','superseded')
    AND t.cleanup_status = 'cleanup_pending'
)
BEGIN SELECT RAISE(ABORT, 'terminal_authorization_policy_delete_requires_cleanup'); END;

-- A Tombstone is append-created from the honest accepted state and cannot be
-- removed/reinserted under the same subject. The duplicate check also blocks
-- INSERT OR REPLACE before SQLite can resolve the primary-key conflict.
CREATE TRIGGER tombstone_insert_contract
BEFORE INSERT ON tombstone
BEGIN
  SELECT CASE WHEN NEW.cleanup_status <> 'accepted'
    THEN RAISE(ABORT, 'tombstone_must_start_accepted') END;
  SELECT CASE WHEN EXISTS (
    SELECT 1 FROM tombstone old
    WHERE old.subject_type = NEW.subject_type AND old.subject_id = NEW.subject_id
  ) THEN RAISE(ABORT, 'tombstone_reinsert_forbidden') END;
  SELECT CASE WHEN NEW.subject_type = 'authorization' AND NOT EXISTS (
    SELECT 1 FROM authorization a
    WHERE a.id = NEW.subject_id
      AND a.status IN ('revoked','expired','superseded')
      AND a.generation = NEW.generation
  ) THEN RAISE(ABORT, 'authorization_tombstone_requires_terminal_generation') END;
END;

CREATE TRIGGER tombstone_no_delete
BEFORE DELETE ON tombstone
BEGIN SELECT RAISE(ABORT, 'tombstone_delete_forbidden'); END;

CREATE TRIGGER authorization_tombstone_control_envelope_immutable
BEFORE UPDATE OF subject_type, subject_id, generation, command_id,
                 reason_code, blocked_at_ms ON tombstone
-- Both sides are intentional: a generic row cannot enter the Authorization
-- namespace, and an Authorization row cannot leave it or change identity.
WHEN (OLD.subject_type = 'authorization' OR NEW.subject_type = 'authorization') AND (
  NEW.subject_type IS NOT OLD.subject_type
  OR NEW.subject_id IS NOT OLD.subject_id
  OR NEW.generation IS NOT OLD.generation
  OR NEW.command_id IS NOT OLD.command_id
  OR NEW.reason_code IS NOT OLD.reason_code
  OR NEW.blocked_at_ms IS NOT OLD.blocked_at_ms
)
BEGIN SELECT RAISE(ABORT, 'authorization_tombstone_control_envelope_immutable'); END;

CREATE TRIGGER authorization_tombstone_updated_time_contract
BEFORE UPDATE OF cleanup_status, updated_at_ms ON tombstone
WHEN OLD.subject_type = 'authorization'
BEGIN
  SELECT CASE WHEN NEW.cleanup_status = OLD.cleanup_status
      AND NEW.updated_at_ms IS NOT OLD.updated_at_ms
    THEN RAISE(ABORT, 'authorization_tombstone_time_requires_status_change') END;
  SELECT CASE WHEN NEW.cleanup_status <> OLD.cleanup_status
      AND NEW.updated_at_ms < OLD.updated_at_ms
    THEN RAISE(ABORT, 'authorization_tombstone_time_must_not_decrease') END;
END;

CREATE TRIGGER tombstone_generation_monotonic
BEFORE UPDATE OF generation ON tombstone WHEN NEW.generation < OLD.generation
BEGIN SELECT RAISE(ABORT, 'tombstone_generation_must_not_decrease'); END;

-- Status enforcement hierarchy: CHECK enumerates values; this trigger enforces transitions;
-- application transaction guard proves all consumer gates before entering active_blocked.
CREATE TRIGGER tombstone_status_transition
BEFORE UPDATE OF cleanup_status ON tombstone WHEN NEW.cleanup_status <> OLD.cleanup_status
BEGIN
  SELECT CASE WHEN NOT (
    (OLD.cleanup_status = 'accepted' AND NEW.cleanup_status = 'active_blocked') OR
    (OLD.cleanup_status = 'active_blocked' AND NEW.cleanup_status IN ('cleanup_pending','no_cleanup_required')) OR
    (OLD.cleanup_status = 'cleanup_pending' AND NEW.cleanup_status IN ('cleanup_failed','vendor_limited','cleaned')) OR
    (OLD.cleanup_status IN ('cleanup_failed','vendor_limited') AND NEW.cleanup_status IN ('cleanup_pending','cleaned'))
  ) THEN RAISE(ABORT, 'tombstone_status_transition_invalid') END;
  SELECT CASE WHEN NEW.subject_type = 'authorization'
      AND NEW.cleanup_status IN ('active_blocked','cleanup_pending','cleaned')
      AND NOT EXISTS (
        SELECT 1 FROM authorization a
        JOIN audit_entry e ON e.scoped_subject_ref = a.id
          AND e.authorization_version = a.version_no
          AND e.action_code = 'authorization.cleanup'
          AND e.result_code = 'redacted_by_user'
          AND e.correlation_id = 'authorization-cleanup:' || a.id || ':' || a.generation
        WHERE a.id = NEW.subject_id
          AND a.status IN ('revoked','expired','superseded')
          AND a.generation = NEW.generation
      ) THEN RAISE(ABORT, 'authorization_cleanup_audit_required') END;
  SELECT CASE WHEN NEW.subject_type = 'authorization'
      AND NEW.cleanup_status = 'cleaned'
      AND (
        EXISTS (SELECT 1 FROM authorization_scope s WHERE s.authorization_id = NEW.subject_id)
        OR EXISTS (SELECT 1 FROM authorization_action x WHERE x.authorization_id = NEW.subject_id)
        OR EXISTS (SELECT 1 FROM authorization_policy p WHERE p.authorization_id = NEW.subject_id)
      ) THEN RAISE(ABORT, 'authorization_cleanup_sensitive_projection_remains') END;
END;

INSERT INTO schema_migration_meta(version, migration_name, candidate_only, schema_checksum, applied_at_ms)
VALUES (1, '001_candidate_schema', 1, 'candidate:sha256-computed-by-test-harness', 1786550400000);

COMMIT;
