import { createHash } from "node:crypto";
import { CAPABILITIES, requireCapability, type Capability } from "./capability-policy.ts";
import { authorizationContext, canConsume } from "./consumption-gate.ts";
import { AuthorityStore } from "./store.ts";
import type { AuthorizationContext, CaptureInput, ContentKind, ImportantLinkInput } from "./types.ts";

export class LifeOS {
  readonly store: AuthorityStore;
  readonly capabilities = CAPABILITIES;
  private readonly nowMs: () => number;
  constructor(path = ":memory:", nowMs: () => number = Date.now) {
    this.store = new AuthorityStore(path);
    this.nowMs = nowMs;
  }
  close(): void { this.store.close(); }
  capture(input: CaptureInput) { return this.store.capture(input); }
  processIndexJobs(fail = false) { return this.store.processIndexJobs(fail); }
  context(id: string, project?: string) { return authorizationContext(this.store, id, project); }

  read(ctx: AuthorizationContext): any | null {
    if (!canConsume(this.store, ctx, this.nowMs())) return null;
    return this.store.db.prepare(`SELECT a.id,a.project_id,a.title,a.category,v.id version_id,
      v.original_text,v.content_hash,v.content_kind,s.id source_id FROM artifact a JOIN artifact_version v
      ON v.id=a.current_version_id JOIN source s ON s.id=a.source_id WHERE a.id=?`).get(ctx.subjectId) ?? null;
  }

  search(query: string, contexts: AuthorizationContext[]): any[] {
    const rows = this.store.db.prepare("SELECT artifact_id FROM artifact_fts WHERE artifact_fts MATCH ?").all(query) as any[];
    const byId = new Map(contexts.map(c => [c.subjectId, c]));
    return rows.map(r => byId.get(r.artifact_id)).filter(Boolean).map(c => this.read(c!)).filter(Boolean);
  }

  recovery(projectId: string, contexts: AuthorizationContext[]): any[] {
    return contexts.filter(c => c.projectId === projectId).map(c => this.read(c)).filter(Boolean);
  }

  suggest(projectId: string, evidence: AuthorizationContext[]): any | null {
    this.staleGenerationMismatches();
    if (evidence.some(ctx => ctx.projectId === projectId && !canConsume(this.store, ctx, this.nowMs()))) return null;
    const usable = this.recovery(projectId, evidence);
    const boundInputs = new Map<string, { artifact: any; context: AuthorizationContext; binding: object }>();
    for (const artifact of usable) {
      const context = evidence.find(c => c.subjectId === artifact.id && c.versionId === artifact.version_id);
      if (!context) continue;
      const binding = {
        evidenceVersionId: context.versionId,
        artifactId: artifact.id,
        sourceId: artifact.source_id,
        artifactGeneration: context.artifactGeneration,
        sourceGeneration: context.sourceGeneration,
      };
      boundInputs.set(JSON.stringify(binding), { artifact, context, binding });
    }
    const inputs = [...boundInputs.entries()].sort(([a], [b]) => a < b ? -1 : a > b ? 1 : 0).map(([, value]) => value);
    const primary = inputs.find(x => x.artifact.category === "unprocessed") ?? inputs[0];
    if (!primary) return null;
    const idPayload = JSON.stringify({ projectId, inputs: inputs.map(x => x.binding) });
    const id = `suggestion:v2:${createHash("sha256").update(idPayload).digest("hex")}`;
    const exists = this.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(id) as any;
    if (!exists) {
      this.store.db.exec("BEGIN IMMEDIATE");
      try {
        this.store.db.prepare("INSERT INTO derivation VALUES(?,?,?,?,?,?,?,?)").run(
          id, projectId, "ai_suggestion", "SYNTH_CANDIDATE_NEXT_STEP", "candidate", primary.context.versionId,
          primary.context.artifactGeneration, primary.context.sourceGeneration,
        );
        const insertInput = this.store.db.prepare("INSERT INTO derivation_input VALUES(?,?,?,?,?,?)");
        for (const input of inputs) {
          insertInput.run(id, input.context.versionId, input.context.subjectId, input.artifact.source_id,
            input.context.artifactGeneration, input.context.sourceGeneration);
        }
        this.store.db.exec("COMMIT");
      } catch (error) {
        this.store.db.exec("ROLLBACK");
        throw error;
      }
    }
    const current = this.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(id) as any;
    if (!["candidate", "confirmed", "edited_confirmed"].includes(current.status)
      || !this.derivationInputsConsumable(id, evidence)) return null;
    return {
      id,
      projectId,
      kind: "ai_suggestion" as ContentKind,
      outputText: "SYNTH_CANDIDATE_NEXT_STEP",
      status: current.status,
      primaryEvidenceVersionId: primary.context.versionId,
      primaryEvidenceRole: "legacy_compatibility_display_only",
      inputs: inputs.map(input => input.binding),
    };
  }

  private derivationInputsConsumable(derivationId: string, contexts: AuthorizationContext[]): boolean {
    const inputs = this.store.db.prepare("SELECT * FROM derivation_input WHERE derivation_id=?").all(derivationId) as any[];
    return inputs.length > 0 && inputs.every(input => {
      const ctx = contexts.find(c => c.subjectId === input.artifact_id && c.versionId === input.evidence_version_id
        && c.artifactGeneration === input.artifact_generation && c.sourceGeneration === input.source_generation);
      return Boolean(ctx && canConsume(this.store, ctx, this.nowMs()));
    });
  }

  private staleGenerationMismatches(): void {
    this.store.db.prepare(`UPDATE derivation SET status='stale' WHERE id IN (
      SELECT di.derivation_id FROM derivation_input di
      LEFT JOIN artifact a ON a.id=di.artifact_id
      LEFT JOIN source s ON s.id=di.source_id
      WHERE a.id IS NULL OR s.id IS NULL
        OR di.artifact_generation<>a.generation OR di.source_generation<>s.generation
    )`).run();
  }

  feedback(projectId: string, derivationId: string, kind: string, userText: string | null, contexts: AuthorizationContext[]): any | null {
    this.staleGenerationMismatches();
    const d = this.store.db.prepare("SELECT * FROM derivation WHERE id=?").get(derivationId) as any;
    if (!d || d.project_id !== projectId || d.status !== "candidate") return null;
    if (!this.derivationInputsConsumable(derivationId, contexts)) return null;
    const id = `feedback:${derivationId}:${kind}`;
    const inserted = this.store.db.prepare(`INSERT INTO feedback VALUES(?,?,?,?,?)
      ON CONFLICT(id) DO NOTHING`).run(id, derivationId, kind, userText, "active");
    if (inserted.changes !== 1) return null;
    if (kind === "confirm") this.store.db.prepare("UPDATE derivation SET status='confirmed' WHERE id=?").run(derivationId);
    else if (kind === "edit_confirm") this.store.db.prepare("UPDATE derivation SET status='edited_confirmed' WHERE id=?").run(derivationId);
    else if (kind === "reject" || kind === "correct") this.store.db.prepare("UPDATE derivation SET status='invalid' WHERE id=?").run(derivationId);
    return { id, kind, userText, contentKind: "user_original" as ContentKind };
  }

  retractFeedback(feedbackId: string, actor: "user"): any | null {
    if (actor !== "user") return null;
    const feedback = this.store.db.prepare("SELECT * FROM feedback WHERE id=?").get(feedbackId) as any;
    if (!feedback) return null;
    if (feedback.status === "retracted") return feedback;
    this.store.db.exec("BEGIN IMMEDIATE");
    try {
      this.store.db.prepare("UPDATE feedback SET status='retracted' WHERE id=? AND status='active'").run(feedbackId);
      const derivation = this.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(feedback.derivation_id) as any;
      if (derivation && ["confirmed", "edited_confirmed"].includes(derivation.status)) {
        this.store.db.prepare("UPDATE derivation SET status='feedback_retracted' WHERE id=?").run(feedback.derivation_id);
      }
      this.store.db.exec("COMMIT");
    } catch (error) {
      this.store.db.exec("ROLLBACK");
      throw error;
    }
    return this.store.db.prepare("SELECT * FROM feedback WHERE id=?").get(feedbackId) ?? null;
  }

  control(command: "revoke" | "delete", artifactId: string): void {
    const row = this.store.db.prepare("SELECT source_id,generation FROM artifact WHERE id=?").get(artifactId) as any;
    if (!row) return;
    const next = row.generation + 1;
    this.store.db.exec("BEGIN IMMEDIATE");
    this.store.db.prepare("UPDATE artifact SET tombstoned=1,generation=? WHERE id=?").run(next, artifactId);
    this.store.db.prepare("UPDATE authorization SET decision='deny',generation=? WHERE subject_id=?").run(next, artifactId);
    this.store.db.prepare("INSERT OR REPLACE INTO tombstone VALUES('artifact',?,?,?)").run(artifactId, next, command);
    this.store.db.prepare(`UPDATE derivation SET status='stale' WHERE id IN
      (SELECT derivation_id FROM derivation_input WHERE artifact_id=?)`).run(artifactId);
    this.store.db.exec("COMMIT");
  }

  createImportantLink(input: ImportantLinkInput): any | null {
    if (input.linkIdentity !== "user_confirmed" || input.confirmationStatus !== "confirmed") return null;
    if (input.evidence.length === 0) return null;
    const allContexts = [input.from, input.to, ...input.evidence];
    if (allContexts.some(ctx => ctx.projectId !== input.projectId || !canConsume(this.store, ctx, this.nowMs()))) return null;
    const uniqueEvidence = new Map(input.evidence.map(ctx => [ctx.versionId, ctx]));
    if (uniqueEvidence.size !== input.evidence.length) return null;
    const rows = allContexts.map(ctx => this.store.db.prepare(`SELECT a.id artifact_id,a.current_version_id version_id,
      a.project_id,s.id source_id FROM artifact a JOIN source s ON s.id=a.source_id WHERE a.id=?`).get(ctx.subjectId) as any);
    if (rows.some((row, index) => !row || row.project_id !== input.projectId || row.version_id !== allContexts[index].versionId)) return null;
    this.store.db.exec("BEGIN IMMEDIATE");
    try {
      if (allContexts.some(ctx => !canConsume(this.store, ctx, this.nowMs()))) throw new Error("link gate changed");
      this.store.db.prepare("INSERT INTO important_link VALUES(?,?,?,?,?,?,?,?,?,?)").run(
        input.id, input.projectId, rows[0].artifact_id, rows[0].version_id, rows[0].source_id,
        rows[1].artifact_id, rows[1].version_id, rows[1].source_id, input.linkIdentity, input.confirmationStatus,
      );
      const insertEvidence = this.store.db.prepare("INSERT INTO important_link_evidence VALUES(?,?,?,?,?,?)");
      input.evidence.forEach((ctx, index) => {
        const row = rows[index + 2];
        insertEvidence.run(input.id, ctx.versionId, ctx.subjectId, row.source_id, ctx.artifactGeneration, ctx.sourceGeneration);
      });
      this.store.db.exec("COMMIT");
      return this.store.db.prepare("SELECT * FROM important_link WHERE id=?").get(input.id) ?? null;
    } catch {
      this.store.db.exec("ROLLBACK");
      return null;
    }
  }

  exportMemory(projectId: string, contexts: AuthorizationContext[]): any {
    this.staleGenerationMismatches();
    const artifacts = this.recovery(projectId, contexts);
    const derivations = (this.store.db.prepare("SELECT * FROM derivation WHERE project_id=?").all(projectId) as any[])
      .filter(d => ["candidate", "confirmed", "edited_confirmed"].includes(d.status)
        && this.derivationInputsConsumable(d.id, contexts));
    const artifactAuthority = artifacts.map(artifact => {
      const current = this.store.db.prepare(`SELECT a.id artifact_id,a.project_id,a.title,a.category,
        a.current_version_id version_id,a.source_id,a.generation artifact_generation,
        a.tombstoned artifact_tombstoned,s.generation source_generation,s.tombstoned source_tombstoned,
        v.content_hash,v.content_kind FROM artifact a JOIN source s ON s.id=a.source_id
        JOIN artifact_version v ON v.id=a.current_version_id WHERE a.id=?`).get(artifact.id) as any;
      const authorization = this.store.db.prepare(`SELECT purpose,location,processor,decision,generation,expires_at_ms
        FROM authorization WHERE subject_id=? ORDER BY id`).all(artifact.id) as any[];
      return { ...current, authorization };
    });
    const derivationAuthority = derivations.map(derivation => ({
      id: derivation.id,
      project_id: derivation.project_id,
      kind: derivation.kind,
      output_text: derivation.output_text,
      status: derivation.status,
      primary_evidence_version_id: derivation.evidence_version_id,
      primary_evidence_role: "legacy_compatibility_display_only",
      inputs_authority: "derivation_input_complete_set",
      inputs: (this.store.db.prepare(`SELECT evidence_version_id,artifact_id,source_id,
        artifact_generation,source_generation FROM derivation_input WHERE derivation_id=?
        ORDER BY artifact_id,evidence_version_id`).all(derivation.id) as any[]),
    }));
    return {
      format: "p3-009-in-memory-test-package",
      projectId,
      artifacts,
      derivations,
      authorityProjection: { projectId, artifacts: artifactAuthority, derivations: derivationAuthority },
    };
  }

  restoreCandidates(pkg: any): any {
    const result = {
      format: "p3-009-restore-candidates-v1",
      sourcePackageFormat: pkg?.format ?? null,
      projectId: pkg?.projectId ?? null,
      artifacts: [] as any[],
      derivations: [] as any[],
    };
    const projection = pkg?.authorityProjection;
    if (pkg?.format !== "p3-009-in-memory-test-package" || !projection
      || projection.projectId !== pkg.projectId || !Array.isArray(projection.artifacts)
      || !Array.isArray(projection.derivations)) return result;

    const artifactStatus = new Map<string, string>();
    for (const snapshot of projection.artifacts) {
      const reasons: string[] = [];
      let status = "restorable";
      const current = this.store.db.prepare(`SELECT a.id artifact_id,a.project_id,a.title,a.category,
        a.current_version_id version_id,a.source_id,a.generation artifact_generation,
        a.tombstoned artifact_tombstoned,s.generation source_generation,s.tombstoned source_tombstoned,
        v.content_hash,v.content_kind FROM artifact a JOIN source s ON s.id=a.source_id
        JOIN artifact_version v ON v.id=a.current_version_id WHERE a.id=?`).get(snapshot.artifact_id) as any;
      const packaged = Array.isArray(pkg.artifacts) ? pkg.artifacts.find((artifact: any) =>
        artifact.id === snapshot.artifact_id && artifact.version_id === snapshot.version_id) : null;
      if (!current) {
        status = "blocked"; reasons.push("missing_current_authority");
      } else if (current.project_id !== pkg.projectId || snapshot.project_id !== pkg.projectId) {
        status = "blocked"; reasons.push("project_mismatch");
      } else if (current.version_id !== snapshot.version_id || current.source_id !== snapshot.source_id) {
        status = "stale"; reasons.push("version_or_source_changed");
      } else if (!packaged || current.title !== snapshot.title || packaged.title !== snapshot.title
        || current.category !== snapshot.category || packaged.category !== snapshot.category
        || current.content_hash !== snapshot.content_hash || packaged.content_hash !== snapshot.content_hash
        || createHash("sha256").update(packaged.original_text ?? "").digest("hex") !== snapshot.content_hash
        || current.content_kind !== snapshot.content_kind || packaged.content_kind !== snapshot.content_kind) {
        status = "blocked"; reasons.push("package_content_or_identity_mismatch");
      } else if (current.artifact_generation !== snapshot.artifact_generation
        || current.source_generation !== snapshot.source_generation) {
        status = "stale"; reasons.push("generation_changed");
      } else if (current.artifact_tombstoned || current.source_tombstoned
        || snapshot.artifact_tombstoned || snapshot.source_tombstoned) {
        status = "blocked"; reasons.push("tombstoned");
      } else {
        const authorizations = this.store.db.prepare(`SELECT purpose,location,processor,decision,generation,expires_at_ms
          FROM authorization WHERE subject_id=? ORDER BY id`).all(snapshot.artifact_id) as any[];
        const exportedAuth = Array.isArray(snapshot.authorization) ? snapshot.authorization : [];
        const authMatches = authorizations.length === 1 && exportedAuth.length === 1
          && authorizations[0].purpose === exportedAuth[0].purpose
          && authorizations[0].location === exportedAuth[0].location
          && authorizations[0].processor === exportedAuth[0].processor
          && authorizations[0].decision === "allow" && exportedAuth[0].decision === "allow"
          && authorizations[0].generation === current.artifact_generation
          && exportedAuth[0].generation === snapshot.artifact_generation
          && authorizations[0].expires_at_ms === exportedAuth[0].expires_at_ms;
        const ctx: AuthorizationContext = {
          subjectId: snapshot.artifact_id, projectId: snapshot.project_id, versionId: snapshot.version_id,
          artifactGeneration: snapshot.artifact_generation, sourceGeneration: snapshot.source_generation,
          purpose: exportedAuth[0]?.purpose, location: exportedAuth[0]?.location,
          processor: exportedAuth[0]?.processor,
        };
        if (!authMatches || !canConsume(this.store, ctx, this.nowMs())) {
          status = "blocked"; reasons.push("authorization_not_current_allow");
        }
      }
      artifactStatus.set(snapshot.artifact_id, status);
      result.artifacts.push({ artifactId: snapshot.artifact_id, versionId: snapshot.version_id, status, reasons });
    }

    for (const snapshot of projection.derivations) {
      const reasons: string[] = [];
      let status = "restorable";
      const current = this.store.db.prepare("SELECT * FROM derivation WHERE id=?").get(snapshot.id) as any;
      const packaged = Array.isArray(pkg.derivations)
        ? pkg.derivations.find((derivation: any) => derivation.id === snapshot.id) : null;
      const currentInputs = current ? this.store.db.prepare(`SELECT evidence_version_id,artifact_id,source_id,
        artifact_generation,source_generation FROM derivation_input WHERE derivation_id=?
        ORDER BY artifact_id,evidence_version_id`).all(snapshot.id) as any[] : [];
      const snapshotInputs = Array.isArray(snapshot.inputs) ? snapshot.inputs : [];
      const inputKey = (input: any) => JSON.stringify([
        input.evidence_version_id, input.artifact_id, input.source_id,
        input.artifact_generation, input.source_generation,
      ]);
      if (!current || current.project_id !== pkg.projectId || snapshot.project_id !== pkg.projectId) {
        status = "blocked"; reasons.push("missing_or_wrong_project_derivation");
      } else if (!packaged || current.kind !== snapshot.kind || packaged.kind !== snapshot.kind
        || current.output_text !== snapshot.output_text || packaged.output_text !== snapshot.output_text) {
        status = "blocked"; reasons.push("package_derivation_content_mismatch");
      } else if (!["candidate", "confirmed", "edited_confirmed"].includes(snapshot.status)
        || !["candidate", "confirmed", "edited_confirmed"].includes(current.status)) {
        status = current.status === "stale" || snapshot.status === "stale" ? "stale" : "excluded";
        reasons.push("derivation_not_active");
      } else if (current.status !== snapshot.status) {
        status = "blocked"; reasons.push("derivation_authority_changed");
      } else if (snapshotInputs.length === 0
        || JSON.stringify(currentInputs.map(inputKey)) !== JSON.stringify(snapshotInputs.map(inputKey))) {
        status = "blocked"; reasons.push("derivation_inputs_mismatch");
      } else {
        const inputStatuses = snapshotInputs.map((input: any) => artifactStatus.get(input.artifact_id));
        if (inputStatuses.some((inputStatus: string | undefined) => inputStatus === "stale")) {
          status = "stale"; reasons.push("input_generation_or_version_changed");
        } else if (inputStatuses.some((inputStatus: string | undefined) => inputStatus !== "restorable")) {
          status = "blocked"; reasons.push("input_not_authorized");
        }
      }
      result.derivations.push({ derivationId: snapshot.id, status, reasons });
    }
    return result;
  }

  callCapability(name: Capability): never { return requireCapability(name); }
}
