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
  subject_type TEXT NOT NULL CHECK (subject_type IN ('artifact','source','semantic_object','derivation','important_link')),
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
  correlation_id TEXT NOT NULL
);

CREATE TABLE submission (
  namespace TEXT NOT NULL,
  idempotency_key TEXT NOT NULL,
  canonical_request_hash TEXT NOT NULL,
  command TEXT NOT NULL,
  result_subject_id TEXT NOT NULL,
  result_version_id TEXT,
  committed_at_ms INTEGER NOT NULL,
  PRIMARY KEY (namespace, idempotency_key)
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

-- Authorization scope/action/policy rows cannot precede their parent because of
-- FKs. Reject direct active INSERT and require the proposed -> complete -> active flow.
CREATE TRIGGER authorization_no_direct_active_insert
BEFORE INSERT ON authorization
WHEN NEW.status = 'active' AND NOT EXISTS (
  SELECT 1 FROM authorization old
  WHERE old.status = 'active' AND (
    old.id = NEW.id OR
    (old.logical_key = NEW.logical_key AND old.version_no = NEW.version_no)
  )
)
BEGIN SELECT RAISE(ABORT, 'authorization_must_start_inactive'); END;

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

-- Directly deleting an active parent would permit a DELETE + INSERT rebuild
-- when foreign keys are disabled. Terminal cleanup/history remains a separate
-- contract and is deliberately not expanded here.
CREATE TRIGGER authorization_no_delete_while_active
BEFORE DELETE ON authorization WHEN OLD.status = 'active'
BEGIN SELECT RAISE(ABORT, 'active_authorization_delete_forbidden'); END;

CREATE TRIGGER authorization_activation_complete
BEFORE UPDATE OF status ON authorization WHEN NEW.status = 'active' AND OLD.status <> 'active'
BEGIN
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

-- Authorization lifecycle is forward-only. Leaving active is an audited,
-- generation-fenced terminal transition; terminal rows cannot be reactivated.
-- The audit/outbox rows are prepared first in the same transaction, so a failed
-- status UPDATE can roll the whole unit back without a false retirement record.
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
  SELECT CASE WHEN NEW.generation <> OLD.generation + 1
    THEN RAISE(ABORT, 'authorization_retirement_generation_invalid') END;
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM audit_entry e
    WHERE e.scoped_subject_ref = NEW.id
      AND e.authorization_version = NEW.version_no
      AND e.action_code = CASE NEW.status
        WHEN 'revoked' THEN 'authorization.revoke'
        WHEN 'expired' THEN 'authorization.expire'
        WHEN 'superseded' THEN 'authorization.supersede'
      END
      AND e.correlation_id = 'authorization-state:' || NEW.id || ':' || NEW.generation || ':' || NEW.status
  ) THEN RAISE(ABORT, 'authorization_retirement_audit_required') END;
  SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM outbox_job j
    WHERE j.job_type = 'authorization_state_change'
      AND j.subject_type = 'authorization'
      AND j.subject_id = NEW.id
      AND j.subject_generation = NEW.generation
      AND j.payload_ref = NEW.status
      AND j.status = 'pending'
      AND j.idempotency_key = 'authorization-state:' || NEW.id || ':' || NEW.generation || ':' || NEW.status
  ) THEN RAISE(ABORT, 'authorization_retirement_outbox_required') END;
END;

CREATE TRIGGER authorization_generation_monotonic
BEFORE UPDATE OF generation ON authorization WHEN NEW.generation < OLD.generation
BEGIN SELECT RAISE(ABORT, 'authorization_generation_must_not_decrease'); END;

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
END;

CREATE TRIGGER tombstone_no_delete
BEFORE DELETE ON tombstone
BEGIN SELECT RAISE(ABORT, 'tombstone_delete_forbidden'); END;

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
END;

INSERT INTO schema_migration_meta(version, migration_name, candidate_only, schema_checksum, applied_at_ms)
VALUES (1, '001_candidate_schema', 1, 'candidate:sha256-computed-by-test-harness', 1786550400000);

COMMIT;
