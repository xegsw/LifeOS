import type { AuthorizationContext } from "./types.ts";
import { AuthorityStore } from "./store.ts";

export function authorizationContext(store: AuthorityStore, artifactId: string, projectId?: string): AuthorizationContext {
  const row = store.db.prepare(`SELECT a.project_id,a.current_version_id,a.generation artifact_generation,
    s.generation source_generation FROM artifact a JOIN source s ON s.id=a.source_id WHERE a.id=?`).get(artifactId) as any;
  if (!row) throw new Error("unknown artifact");
  return {
    subjectId: artifactId, projectId: projectId ?? row.project_id, versionId: row.current_version_id,
    artifactGeneration: row.artifact_generation, sourceGeneration: row.source_generation,
    purpose: "lifeos_local_recovery", location: "local", processor: "local_rules",
  };
}

export function canConsume(store: AuthorityStore, ctx: AuthorizationContext, nowMs = Date.now()): boolean {
  const row = store.db.prepare(`SELECT a.project_id,a.current_version_id,a.generation artifact_generation,
    a.tombstoned artifact_tombstoned,s.generation source_generation,s.tombstoned source_tombstoned
    FROM artifact a JOIN source s ON s.id=a.source_id WHERE a.id=?`).get(ctx.subjectId) as any;
  if (!row || row.artifact_tombstoned || row.source_tombstoned) return false;
  if (row.project_id !== ctx.projectId || row.current_version_id !== ctx.versionId) return false;
  if (row.artifact_generation !== ctx.artifactGeneration || row.source_generation !== ctx.sourceGeneration) return false;
  if (ctx.purpose !== "lifeos_local_recovery" || ctx.location !== "local" || ctx.processor !== "local_rules") return false;
  const auth = store.db.prepare(`SELECT COUNT(*) total,
    SUM(CASE WHEN decision='allow' AND (expires_at_ms IS NULL OR expires_at_ms>?) THEN 1 ELSE 0 END) allow_count
    FROM authorization WHERE subject_id=? AND purpose=? AND location=?
    AND processor=? AND generation=?`).get(
      nowMs, ctx.subjectId, ctx.purpose, ctx.location, ctx.processor, ctx.artifactGeneration,
    ) as any;
  return auth.total === 1 && auth.allow_count === 1;
}
