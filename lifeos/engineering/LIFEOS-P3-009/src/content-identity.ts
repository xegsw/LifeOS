import type { ContentKind } from "./types.ts";

export const CONTENT_IDENTITIES: Readonly<Record<ContentKind, { authority: boolean; requiresEvidence: boolean }>> = Object.freeze({
  user_original: { authority: true, requiresEvidence: false },
  ai_generated: { authority: false, requiresEvidence: true },
  ai_inference: { authority: false, requiresEvidence: true },
  ai_suggestion: { authority: false, requiresEvidence: true },
  external_reference: { authority: false, requiresEvidence: true },
});

export function contentEnvelope(kind: ContentKind, text: string, evidenceIds: string[]) {
  const policy = CONTENT_IDENTITIES[kind];
  if (policy.requiresEvidence && evidenceIds.length === 0) throw new Error(`${kind} requires evidence`);
  return Object.freeze({ kind, text, evidenceIds: Object.freeze([...evidenceIds]), authority: policy.authority });
}
