import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { DisabledCapability } from "../src/capability-policy.ts";
import { CONTENT_IDENTITIES, contentEnvelope } from "../src/content-identity.ts";
import { LifeOS } from "../src/lifeos.ts";

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const fixture = JSON.parse(readFileSync(join(root, "fixtures/synthetic_v1.json"), "utf8"));

function populated(nowMs: () => number = Date.now) {
  const app = new LifeOS(":memory:", nowMs);
  for (const c of fixture.captures) app.capture({
    sourceId: c.source_id, artifactId: c.artifact_id, projectId: c.project_id,
    title: c.title, category: c.category, originalText: c.original_text, idempotencyKey: c.id,
  });
  app.processIndexJobs();
  return app;
}
function contexts(app: LifeOS, projectId: string) {
  return fixture.captures.filter((c: any) => c.project_id === projectId).map((c: any) => app.context(c.artifact_id, projectId));
}

test("H1 T-SCOPE remains personal local single-device", () => {
  const app = populated();
  assert.equal(app.recovery("project-orbit", contexts(app, "project-orbit")).length, 2);
  assert.ok(Object.values(app.capabilities).every(v => v === false)); app.close();
});

test("H2 T-ID preserves immutable user original and distinct identities", () => {
  const app = populated(); const ctx = app.context("artifact-2"); const before = app.read(ctx).original_text;
  const suggestion = app.suggest("project-orbit", contexts(app, "project-orbit"));
  assert.equal(suggestion.kind, "ai_suggestion");
  const feedback = app.feedback("project-orbit", suggestion.id, "correct", "SYNTH_USER_CORRECTION", contexts(app, "project-orbit"));
  assert.equal(feedback.contentKind, "user_original"); assert.equal(app.read(ctx).original_text, before);
  for (const kind of Object.keys(CONTENT_IDENTITIES) as (keyof typeof CONTENT_IDENTITIES)[]) {
    const evidence = kind === "user_original" ? [] : [ctx.versionId];
    const envelope = contentEnvelope(kind, `SYNTH_${kind}`, evidence);
    assert.equal(envelope.kind, kind); assert.equal(envelope.authority, kind === "user_original");
  }
  assert.throws(() => contentEnvelope("external_reference", "SYNTH_EXTERNAL", []));
  assert.throws(() => app.store.db.prepare("UPDATE artifact_version SET original_text='x'").run()); app.close();
});

test("H3 T-SAVE authoritative transaction survives derivative failure", () => {
  const app = new LifeOS();
  assert.equal(app.capture({sourceId:"s-fail",artifactId:"a-fail",projectId:"p",title:"x",category:"change",originalText:"SYNTH_FAIL",idempotencyKey:"fail",failBeforeCommit:true}).saved, false);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM artifact WHERE id='a-fail'").get().n, 0);
  assert.equal(app.capture({sourceId:"s-ok",artifactId:"a-ok",projectId:"p",title:"x",category:"change",originalText:"SYNTH_SAVE",idempotencyKey:"ok"}).saved, true);
  assert.equal(app.processIndexJobs(true).failed, 1); assert.equal(app.read(app.context("a-ok")).original_text, "SYNTH_SAVE"); app.close();
});

test("H4 T-GATE all consumption entries fail closed on context mismatch", () => {
  const app = populated(); const good = app.context("artifact-1");
  const corruptions: any[] = [
    {...good,projectId:"project-lumen"},{...good,versionId:"old"},{...good,artifactGeneration:99},
    {...good,sourceGeneration:99},{...good,purpose:"other"},{...good,location:"cloud"},{...good,processor:"external"},
  ];
  for (const c of corruptions) assert.equal(app.read(c), null);
  assert.deepEqual(app.search("SYNTH", corruptions), []); assert.deepEqual(app.recovery("project-orbit", corruptions), []);
  assert.equal(app.suggest("project-orbit", corruptions), null); assert.equal(app.exportMemory("project-orbit", corruptions).artifacts.length, 0); app.close();
});

test("P0 T-GATE allow+deny conflict blocks every consumption entry", () => {
  const app = populated(); const conflicted = app.context("artifact-2");
  app.store.db.prepare("INSERT INTO authorization VALUES(?,?,?,?,?,?,?,NULL)").run(
    "auth:artifact-2:deny", conflicted.subjectId, conflicted.purpose, conflicted.location,
    conflicted.processor, "deny", conflicted.artifactGeneration,
  );
  assert.equal(app.read(conflicted), null);
  assert.deepEqual(app.search("SYNTH_ORIGINAL_NEXT", [conflicted]), []);
  assert.deepEqual(app.recovery("project-orbit", [conflicted]), []);
  assert.equal(app.suggest("project-orbit", [conflicted]), null);
  const exported = app.exportMemory("project-orbit", [conflicted]);
  assert.deepEqual(exported.artifacts, []); assert.deepEqual(exported.derivations, []);
  assert.doesNotMatch(JSON.stringify(exported), /SYNTH_ORIGINAL_NEXT/); app.close();
});

test("P0 T-GATE missing duplicate or unknown authorization fails closed", () => {
  for (const mutation of ["missing", "duplicate_allow", "unknown"] as const) {
    const app = populated(); const ctx = app.context("artifact-1");
    if (mutation === "missing") app.store.db.prepare("DELETE FROM authorization WHERE subject_id=?").run(ctx.subjectId);
    if (mutation === "duplicate_allow") app.store.db.prepare("INSERT INTO authorization VALUES(?,?,?,?,?,?,?,NULL)").run(
      "auth:artifact-1:duplicate", ctx.subjectId, ctx.purpose, ctx.location, ctx.processor, "allow", ctx.artifactGeneration,
    );
    if (mutation === "unknown") app.store.db.prepare("INSERT INTO authorization VALUES(?,?,?,?,?,?,?,NULL)").run(
      "auth:artifact-1:unknown", ctx.subjectId, ctx.purpose, ctx.location, ctx.processor, "unknown", ctx.artifactGeneration,
    );
    assert.equal(app.read(ctx), null, mutation); app.close();
  }
});

test("P1 T-ID repeated suggestion preserves confirmation and feedback trace", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const first = app.suggest("project-orbit", evidence); assert.equal(first.status, "candidate");
  const feedback = app.feedback("project-orbit", first.id, "confirm", null, evidence); assert.ok(feedback);
  const repeated = app.suggest("project-orbit", evidence);
  assert.equal(repeated.id, first.id); assert.equal(repeated.status, "confirmed");
  assert.equal(app.store.db.prepare("SELECT status FROM feedback WHERE id=?").get(feedback.id).status, "active");
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM derivation WHERE id=?").get(first.id).n, 1); app.close();
});

test("P1-8 suggestion ID is stable across complete evidence order", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const first = app.suggest("project-orbit", evidence); assert.ok(first);
  const reversed = app.suggest("project-orbit", [...evidence].reverse()); assert.ok(reversed);
  assert.equal(reversed.id, first.id);
  assert.match(first.id, /^suggestion:v2:[0-9a-f]{64}$/);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM derivation WHERE id=?").get(first.id).n, 1);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM derivation_input WHERE derivation_id=?").get(first.id).n, 2);
  app.close();
});

for (const mismatch of ["artifact", "source"] as const) {
  test(`P1-8 non-primary ${mismatch} generation changes suggestion ID and stales old derivation`, () => {
    const app = populated(); const evidence = contexts(app, "project-orbit");
    const oldSuggestion = app.suggest("project-orbit", evidence); assert.ok(oldSuggestion);
    const oldInput = app.store.db.prepare(`SELECT artifact_id,source_id FROM derivation_input
      WHERE derivation_id=? AND artifact_id='artifact-1'`).get(oldSuggestion.id) as any;
    if (mismatch === "artifact") {
      app.store.db.prepare("UPDATE artifact SET generation=generation+1 WHERE id=?").run(oldInput.artifact_id);
      app.store.db.prepare("UPDATE authorization SET generation=generation+1 WHERE subject_id=?").run(oldInput.artifact_id);
    } else {
      app.store.db.prepare("UPDATE source SET generation=generation+1 WHERE id=?").run(oldInput.source_id);
    }
    const refreshed = contexts(app, "project-orbit");
    const newSuggestion = app.suggest("project-orbit", refreshed); assert.ok(newSuggestion);
    assert.notEqual(newSuggestion.id, oldSuggestion.id);
    assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(oldSuggestion.id).status, "stale");
    assert.equal(app.feedback("project-orbit", oldSuggestion.id, "confirm", null, refreshed), null);
    assert.ok(!app.exportMemory("project-orbit", refreshed).derivations.some((x:any) => x.id === oldSuggestion.id));
    assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM derivation_input WHERE derivation_id=?").get(newSuggestion.id).n, 2);
    app.close();
  });
}

test("P1-8 complete evidence set change cannot reuse suggestion ID", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const complete = app.suggest("project-orbit", evidence); assert.ok(complete);
  const primaryOnlyEvidence = evidence.filter((ctx: any) => ctx.subjectId === "artifact-2");
  const reduced = app.suggest("project-orbit", primaryOnlyEvidence); assert.ok(reduced);
  assert.notEqual(reduced.id, complete.id);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM derivation_input WHERE derivation_id=?").get(complete.id).n, 2);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM derivation_input WHERE derivation_id=?").get(reduced.id).n, 1);
  app.close();
});

test("P1 T-WRITE-GATE feedback rejects non-candidate derivation explicitly", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence);
  app.store.db.prepare("UPDATE derivation SET status='stale' WHERE id=?").run(suggestion.id);
  assert.equal(app.feedback("project-orbit", suggestion.id, "confirm", null, evidence), null);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM feedback WHERE derivation_id=?").get(suggestion.id).n, 0); app.close();
});

test("P2-CLEAN-1 duplicate feedback fails closed and preserves the original record", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
  const first = app.feedback("project-orbit", suggestion.id, "note", "SYNTH_ORIGINAL_FEEDBACK", evidence);
  assert.ok(first);
  assert.equal(app.feedback("project-orbit", suggestion.id, "note", "SYNTH_ORIGINAL_FEEDBACK", evidence), null);
  const stored = app.store.db.prepare("SELECT * FROM feedback WHERE id=?").get(first.id) as any;
  assert.equal(stored.user_text, "SYNTH_ORIGINAL_FEEDBACK"); assert.equal(stored.status, "active");
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM feedback WHERE id=?").get(first.id).n, 1); app.close();
});

test("P2-CLEAN-1 conflicting feedback cannot replace user text or status", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
  const first = app.feedback("project-orbit", suggestion.id, "note", "SYNTH_FIRST_USER_TEXT", evidence);
  assert.ok(first);
  assert.equal(app.feedback("project-orbit", suggestion.id, "note", "SYNTH_CONFLICTING_USER_TEXT", evidence), null);
  const stored = app.store.db.prepare("SELECT user_text,status FROM feedback WHERE id=?").get(first.id) as any;
  assert.equal(stored.user_text, "SYNTH_FIRST_USER_TEXT"); assert.equal(stored.status, "active"); app.close();
});

test("P2-CLEAN-1 retracted feedback cannot be revived by a repeated write", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
  const first = app.feedback("project-orbit", suggestion.id, "note", "SYNTH_RETRACTED_USER_TEXT", evidence);
  assert.ok(first); assert.equal(app.retractFeedback(first.id, "user").status, "retracted");
  assert.equal(app.feedback("project-orbit", suggestion.id, "note", "SYNTH_REVIVE_ATTEMPT", evidence), null);
  const stored = app.store.db.prepare("SELECT user_text,status FROM feedback WHERE id=?").get(first.id) as any;
  assert.equal(stored.user_text, "SYNTH_RETRACTED_USER_TEXT"); assert.equal(stored.status, "retracted"); app.close();
});

test("P1-3 derivation records every evidence version and generation", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
  const inputs = app.store.db.prepare("SELECT * FROM derivation_input WHERE derivation_id=? ORDER BY artifact_id").all(suggestion.id) as any[];
  assert.equal(inputs.length, 2);
  assert.deepEqual(inputs.map(x => x.artifact_id), ["artifact-1", "artifact-2"]);
  assert.ok(inputs.every(x => x.evidence_version_id && x.source_id && x.artifact_generation === 1 && x.source_generation === 1));
  app.close();
});

test("P1-3 non-primary revoke or delete stales derivation and blocks feedback export suggest", () => {
  for (const command of ["revoke", "delete"] as const) {
    const app = populated(); const evidence = contexts(app, "project-orbit");
    const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
    app.control(command, "artifact-1");
    assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "stale");
    assert.equal(app.feedback("project-orbit", suggestion.id, "confirm", null, evidence), null);
    assert.ok(!app.exportMemory("project-orbit", evidence).derivations.some((x:any) => x.id === suggestion.id));
    assert.equal(app.suggest("project-orbit", evidence), null); app.close();
  }
});

test("P3-015 direct deny of non-primary input blocks existing suggestion feedback and export", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
  const oldPackage = app.exportMemory("project-orbit", evidence);
  app.store.db.prepare("UPDATE authorization SET decision='deny' WHERE subject_id='artifact-1'").run();
  assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "candidate");
  assert.equal(app.suggest("project-orbit", evidence), null);
  assert.equal(app.feedback("project-orbit", suggestion.id, "confirm", null, evidence), null);
  assert.ok(!app.exportMemory("project-orbit", evidence).derivations.some((x:any) => x.id === suggestion.id));
  const restore = app.restoreCandidates(oldPackage);
  assert.equal(restore.artifacts.find((x:any) => x.artifactId === "artifact-1").status, "blocked");
  assert.equal(restore.derivations.find((x:any) => x.derivationId === suggestion.id).status, "blocked");
  app.close();
});

for (const mismatch of ["artifact", "source"] as const) {
  test(`P1-4 ${mismatch} generation mismatch independently stales derivation at every consumption entry`, () => {
    for (const trigger of ["suggest", "feedback", "export"] as const) {
      const app = populated(); const evidence = contexts(app, "project-orbit");
      const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
      const input = app.store.db.prepare(`SELECT artifact_id,source_id FROM derivation_input
        WHERE derivation_id=? AND artifact_id='artifact-1'`).get(suggestion.id) as any;
      if (mismatch === "artifact") {
        app.store.db.prepare("UPDATE artifact SET generation=generation+1 WHERE id=?").run(input.artifact_id);
      } else {
        app.store.db.prepare("UPDATE source SET generation=generation+1 WHERE id=?").run(input.source_id);
      }
      assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "candidate");
      if (trigger === "suggest") assert.equal(app.suggest("project-orbit", evidence), null);
      if (trigger === "feedback") assert.equal(app.feedback("project-orbit", suggestion.id, "confirm", null, evidence), null);
      if (trigger === "export") assert.ok(!app.exportMemory("project-orbit", evidence).derivations.some((x:any) => x.id === suggestion.id));
      assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "stale", trigger);
      assert.equal(app.suggest("project-orbit", evidence), null);
      assert.equal(app.feedback("project-orbit", suggestion.id, "confirm", null, evidence), null);
      assert.ok(!app.exportMemory("project-orbit", evidence).derivations.some((x:any) => x.id === suggestion.id));
      assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM tombstone").get().n, 0);
      assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM authorization WHERE decision='deny'").get().n, 0);
      app.close();
    }
  });
}

test("P1-5 important_link writes an explicit confirmed project/source/version/evidence binding", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const link = app.createImportantLink({id:"link:orbit:1",projectId:"project-orbit",from:evidence[0],to:evidence[1],
    evidence,linkIdentity:"user_confirmed",confirmationStatus:"confirmed"});
  assert.ok(link); assert.equal(link.project_id, "project-orbit"); assert.equal(link.link_identity, "user_confirmed");
  assert.equal(link.confirmation_status, "confirmed"); assert.equal(link.from_source_id, "source-1"); assert.equal(link.to_source_id, "source-2");
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM important_link_evidence WHERE link_id=?").get(link.id).n, 2);
  assert.equal(app.createImportantLink({id:"link:identity-mismatch",projectId:"project-orbit",from:evidence[0],to:evidence[1],
    evidence,linkIdentity:"ai_inference",confirmationStatus:"confirmed"}), null);
  assert.equal(app.createImportantLink({id:"link:unconfirmed",projectId:"project-orbit",from:evidence[0],to:evidence[1],
    evidence,linkIdentity:"user_confirmed",confirmationStatus:"unconfirmed"}), null); app.close();
});

test("P1-5 important_link fails closed on deny missing generation cross-project and tombstone", () => {
  for (const failure of ["deny", "missing", "artifact_generation", "source_generation", "cross_project", "tombstone"] as const) {
    const app = populated(); const orbit = contexts(app, "project-orbit"); let from = orbit[0], to = orbit[1];
    if (failure === "deny") app.store.db.prepare("UPDATE authorization SET decision='deny' WHERE subject_id=?").run(from.subjectId);
    if (failure === "missing") app.store.db.prepare("DELETE FROM authorization WHERE subject_id=?").run(from.subjectId);
    if (failure === "artifact_generation") from = {...from, artifactGeneration: 99};
    if (failure === "source_generation") from = {...from, sourceGeneration: 99};
    if (failure === "cross_project") to = app.context("artifact-3", "project-lumen");
    if (failure === "tombstone") app.control("delete", from.subjectId);
    const link = app.createImportantLink({id:`link:blocked:${failure}`,projectId:"project-orbit",from,to,
      evidence:[from,to],linkIdentity:"user_confirmed",confirmationStatus:"confirmed"});
    assert.equal(link, null, failure);
    assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM important_link WHERE id=?").get(`link:blocked:${failure}`).n, 0, failure); app.close();
  }
});

test("H5 T-DEL revoke/delete blocks revival through read search recovery export", () => {
  for (const command of ["revoke", "delete"] as const) {
    const app = populated(); const stale = app.context("artifact-2"); const before = app.exportMemory("project-orbit", contexts(app,"project-orbit"));
    app.control(command, "artifact-2"); assert.equal(app.read(stale), null); assert.deepEqual(app.search("SYNTH", [stale]), []);
    assert.deepEqual(app.recovery("project-orbit", [stale]), []); assert.equal(app.exportMemory("project-orbit", [stale]).artifacts.length, 0);
    assert.ok(before.artifacts.some((x:any) => x.id === "artifact-2")); assert.equal(app.suggest("project-orbit", [stale]), null); app.close();
  }
});

test("P1-6 export carries authority projection and restore candidates are read-only", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
  const pkg = app.exportMemory("project-orbit", evidence);
  assert.equal(pkg.authorityProjection.projectId, "project-orbit");
  assert.equal(pkg.authorityProjection.artifacts.length, 2);
  for (const artifact of pkg.authorityProjection.artifacts) {
    assert.equal(artifact.project_id, "project-orbit");
    assert.ok(artifact.artifact_id && artifact.version_id && artifact.source_id);
    assert.ok(artifact.title && artifact.category && artifact.content_hash && artifact.content_kind === "user_original");
    assert.equal(artifact.artifact_generation, 1); assert.equal(artifact.source_generation, 1);
    assert.equal(artifact.artifact_tombstoned, 0); assert.equal(artifact.source_tombstoned, 0);
    assert.deepEqual(artifact.authorization.map((x:any) => [x.decision, x.generation]), [["allow", 1]]);
  }
  const projected = pkg.authorityProjection.derivations.find((x:any) => x.id === suggestion.id);
  assert.equal(projected.status, "candidate"); assert.equal(projected.inputs.length, 2);
  assert.equal(projected.primary_evidence_role, "legacy_compatibility_display_only");
  assert.equal(projected.inputs_authority, "derivation_input_complete_set");
  assert.ok(projected.inputs.some((x:any) => x.evidence_version_id === projected.primary_evidence_version_id));
  assert.ok(projected.inputs.every((x:any) => x.evidence_version_id && x.artifact_id && x.source_id
    && x.artifact_generation === 1 && x.source_generation === 1));
  const tables = ["artifact","artifact_version","source","authorization","derivation","derivation_input",
    "feedback","important_link","important_link_evidence","tombstone","outbox_job","submission","artifact_fts"];
  const before = Object.fromEntries(tables.map(name => [name, app.store.db.prepare(`SELECT COUNT(*) n FROM ${name}`).get().n]));
  const candidates = app.restoreCandidates(pkg);
  assert.ok(candidates.artifacts.every((x:any) => x.status === "restorable"));
  assert.ok(candidates.derivations.every((x:any) => x.status === "restorable"));
  const changedPrimaryDisplay = structuredClone(pkg);
  changedPrimaryDisplay.authorityProjection.derivations[0].primary_evidence_version_id = "legacy-display-only";
  assert.ok(app.restoreCandidates(changedPrimaryDisplay).derivations.every((x:any) => x.status === "restorable"));
  const removedNonPrimaryInput = structuredClone(pkg);
  removedNonPrimaryInput.authorityProjection.derivations[0].inputs =
    removedNonPrimaryInput.authorityProjection.derivations[0].inputs.slice(1);
  assert.notEqual(app.restoreCandidates(removedNonPrimaryInput).derivations[0].status, "restorable");
  const tamperedArtifact = structuredClone(pkg); tamperedArtifact.artifacts[0].original_text = "SYNTH_TAMPERED";
  assert.notEqual(app.restoreCandidates(tamperedArtifact).artifacts[0].status, "restorable");
  const tamperedDerivation = structuredClone(pkg); tamperedDerivation.derivations[0].output_text = "SYNTH_TAMPERED";
  assert.notEqual(app.restoreCandidates(tamperedDerivation).derivations[0].status, "restorable");
  const after = Object.fromEntries(tables.map(name => [name, app.store.db.prepare(`SELECT COUNT(*) n FROM ${name}`).get().n]));
  assert.deepEqual(after, before); app.close();
});

test("P1-6 old package cannot revive revoked or deleted artifact and derivation", () => {
  for (const command of ["revoke", "delete"] as const) {
    const app = populated(); const evidence = contexts(app, "project-orbit");
    const suggestion = app.suggest("project-orbit", evidence); const pkg = app.exportMemory("project-orbit", evidence);
    app.control(command, "artifact-2");
    const candidates = app.restoreCandidates(pkg);
    assert.notEqual(candidates.artifacts.find((x:any) => x.artifactId === "artifact-2").status, "restorable", command);
    assert.notEqual(candidates.derivations.find((x:any) => x.derivationId === suggestion.id).status, "restorable", command);
    app.close();
  }
});

for (const mismatch of ["artifact", "source"] as const) {
  test(`P1-6 old package cannot revive old ${mismatch} generation content or derivation`, () => {
    const app = populated(); const evidence = contexts(app, "project-orbit");
    const suggestion = app.suggest("project-orbit", evidence); const pkg = app.exportMemory("project-orbit", evidence);
    if (mismatch === "artifact") {
      app.store.db.prepare("UPDATE artifact SET generation=generation+1 WHERE id='artifact-1'").run();
      app.store.db.prepare("UPDATE authorization SET generation=generation+1 WHERE subject_id='artifact-1'").run();
    } else {
      app.store.db.prepare("UPDATE source SET generation=generation+1 WHERE id='source-1'").run();
    }
    const candidates = app.restoreCandidates(pkg);
    assert.equal(candidates.artifacts.find((x:any) => x.artifactId === "artifact-1").status, "stale");
    assert.equal(candidates.derivations.find((x:any) => x.derivationId === suggestion.id).status, "stale");
    assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "candidate");
    app.close();
  });
}

test("P1-6 stale or invalid derivation is never a restorable AI suggestion", () => {
  for (const status of ["stale", "invalid"] as const) {
    const app = populated(); const evidence = contexts(app, "project-orbit");
    const suggestion = app.suggest("project-orbit", evidence); const pkg = app.exportMemory("project-orbit", evidence);
    app.store.db.prepare("UPDATE derivation SET status=? WHERE id=?").run(status, suggestion.id);
    assert.equal(app.exportMemory("project-orbit", evidence).derivations.some((x:any) => x.id === suggestion.id), false);
    const candidate = app.restoreCandidates(pkg).derivations.find((x:any) => x.derivationId === suggestion.id);
    assert.notEqual(candidate.status, "restorable", status); app.close();
  }
});

test("P1-7 authorization without expiry or before deterministic expiry remains consumable", () => {
  let now = 1_000;
  const app = populated(() => now); const ctx = app.context("artifact-1");
  const legacy = app.store.db.prepare("SELECT expires_at_ms FROM authorization WHERE subject_id=?").get(ctx.subjectId) as any;
  assert.equal(legacy.expires_at_ms, null);
  assert.ok(app.read(ctx));
  app.store.db.prepare("UPDATE authorization SET expires_at_ms=? WHERE subject_id=?").run(2_000, ctx.subjectId);
  now = 1_999;
  assert.ok(app.read(ctx));
  assert.equal(app.search("SYNTH", [ctx]).length, 1);
  assert.equal(app.recovery("project-orbit", [ctx]).length, 1);
  app.close();
});

test("P1-7 expired authorization blocks every implemented consume and write entry", () => {
  let now = 1_000;
  const app = populated(() => now); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
  const pkg = app.exportMemory("project-orbit", evidence);
  app.store.db.prepare("UPDATE authorization SET expires_at_ms=2_000 WHERE subject_id IN ('artifact-1','artifact-2')").run();
  now = 2_000;
  assert.equal(app.read(evidence[0]), null);
  assert.deepEqual(app.search("SYNTH", evidence), []);
  assert.deepEqual(app.recovery("project-orbit", evidence), []);
  assert.equal(app.suggest("project-orbit", evidence), null);
  assert.equal(app.feedback("project-orbit", suggestion.id, "confirm", null, evidence), null);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM feedback WHERE derivation_id=?").get(suggestion.id).n, 0);
  const exported = app.exportMemory("project-orbit", evidence);
  assert.deepEqual(exported.artifacts, []); assert.deepEqual(exported.derivations, []);
  const restored = app.restoreCandidates(pkg);
  assert.ok(restored.artifacts.every((x:any) => x.status !== "restorable"));
  assert.ok(restored.derivations.every((x:any) => x.status !== "restorable"));
  assert.equal(app.createImportantLink({id:"link:expired",projectId:"project-orbit",from:evidence[0],to:evidence[1],
    evidence,linkIdentity:"user_confirmed",confirmationStatus:"confirmed"}), null);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM important_link WHERE id='link:expired'").get().n, 0);
  app.close();
});

test("P1-7 explicit feedback retraction is idempotent preserved and removes confirmation authority", () => {
  const app = populated(); const evidence = contexts(app, "project-orbit");
  const suggestion = app.suggest("project-orbit", evidence); assert.ok(suggestion);
  const feedback = app.feedback("project-orbit", suggestion.id, "confirm", null, evidence); assert.ok(feedback);
  const pkg = app.exportMemory("project-orbit", evidence);
  assert.equal((app as any).retractFeedback(feedback.id, "ai"), null);
  const first = app.retractFeedback(feedback.id, "user");
  const second = app.retractFeedback(feedback.id, "user");
  assert.equal(first.status, "retracted"); assert.deepEqual(second, first);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM feedback WHERE id=?").get(feedback.id).n, 1);
  assert.equal(app.store.db.prepare("SELECT COUNT(*) n FROM feedback WHERE id=? AND status='active'").get(feedback.id).n, 0);
  assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "feedback_retracted");
  assert.equal(app.suggest("project-orbit", evidence), null);
  assert.equal(app.exportMemory("project-orbit", evidence).derivations.some((x:any) => x.id === suggestion.id), false);
  assert.notEqual(app.restoreCandidates(pkg).derivations.find((x:any) => x.derivationId === suggestion.id).status, "restorable");
  app.close();
});

test("P1-7 retracting correction stale or expired feedback never revives derivation", () => {
  {
    const app = populated(); const evidence = contexts(app, "project-orbit");
    const suggestion = app.suggest("project-orbit", evidence);
    const feedback = app.feedback("project-orbit", suggestion.id, "correct", "SYNTH_CORRECTION", evidence);
    assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "invalid");
    assert.equal(app.retractFeedback(feedback.id, "user").status, "retracted");
    assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "invalid");
    app.close();
  }
  {
    let now = 1_000;
    const app = populated(() => now); const evidence = contexts(app, "project-orbit");
    const suggestion = app.suggest("project-orbit", evidence);
    const feedback = app.feedback("project-orbit", suggestion.id, "confirm", null, evidence);
    app.control("revoke", "artifact-1");
    assert.equal(app.retractFeedback(feedback.id, "user").status, "retracted");
    assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "stale");
    assert.equal(app.suggest("project-orbit", evidence), null);
    app.close();
  }
  {
    let now = 1_000;
    const app = populated(() => now); const evidence = contexts(app, "project-orbit");
    const suggestion = app.suggest("project-orbit", evidence);
    const feedback = app.feedback("project-orbit", suggestion.id, "confirm", null, evidence);
    app.store.db.prepare("UPDATE authorization SET expires_at_ms=2_000 WHERE subject_id IN ('artifact-1','artifact-2')").run();
    now = 2_000;
    assert.equal(app.retractFeedback(feedback.id, "user").status, "retracted");
    assert.equal(app.store.db.prepare("SELECT status FROM derivation WHERE id=?").get(suggestion.id).status, "feedback_retracted");
    assert.equal(app.suggest("project-orbit", evidence), null);
    assert.equal(app.exportMemory("project-orbit", evidence).derivations.some((x:any) => x.id === suggestion.id), false);
    app.close();
  }
});

test("H6 T-IPC-OFF rejects real Tauri and file capabilities", () => {
  const app = populated(); for (const c of ["tauri_ipc","real_vault","filesystem_export"] as const) assert.throws(() => app.callCapability(c), DisabledCapability); app.close();
});

test("H7 T-DATA fixture is deterministic synthetic-disposable", () => {
  const raw = readFileSync(join(root,"fixtures/synthetic_v1.json"),"utf8");
  assert.equal(fixture.data_class,"synthetic-disposable"); assert.doesNotMatch(raw, /-----BEGIN .*PRIVATE KEY-----|AKIA[0-9A-Z]{16}|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\/Users\/|[A-Z]:\\Users\\/);
});

test("H8 T-OFF denies every non-slice capability", () => {
  const app = populated(); for (const c of Object.keys(app.capabilities) as (keyof typeof app.capabilities)[]) assert.throws(() => app.callCapability(c), DisabledCapability); app.close();
});

test("H9 T-EXPORT enforces project closure and identity", () => {
  const app = populated(); const mixed = [...contexts(app,"project-orbit"), ...contexts(app,"project-lumen")];
  const out = app.exportMemory("project-orbit", mixed); assert.ok(out.artifacts.length > 0);
  assert.ok(out.artifacts.every((x:any) => x.project_id === "project-orbit" && x.content_kind === "user_original"));
  assert.ok(out.derivations.every((x:any) => x.project_id === "project-orbit")); app.close();
});

test("T-ARCH SQLite FTS outbox generations and authority projection execute", () => {
  const app = populated(); const tables = app.store.db.prepare("SELECT name FROM sqlite_master WHERE type IN ('table','trigger')").all().map((x:any)=>x.name);
  for (const required of ["artifact_version","authorization","derivation","derivation_input","important_link","important_link_evidence","outbox_job","tombstone","artifact_fts","artifact_version_no_update"]) assert.ok(tables.includes(required));
  assert.equal(app.search("SYNTH", contexts(app,"project-orbit")).length, 2);
  const old = app.context("artifact-1"); app.control("revoke","artifact-1"); assert.equal(app.read(old),null); app.close();
});
