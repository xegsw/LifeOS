export type ContentKind = "user_original" | "ai_generated" | "ai_inference" | "ai_suggestion" | "external_reference";

export type AuthorizationContext = {
  subjectId: string;
  projectId: string;
  versionId: string;
  artifactGeneration: number;
  sourceGeneration: number;
  purpose: "lifeos_local_recovery";
  location: "local";
  processor: "local_rules";
};

export type CaptureInput = {
  sourceId: string;
  artifactId: string;
  projectId: string;
  title: string;
  category: string;
  originalText: string;
  idempotencyKey: string;
  failBeforeCommit?: boolean;
};

export type ImportantLinkInput = {
  id: string;
  projectId: string;
  from: AuthorizationContext;
  to: AuthorizationContext;
  evidence: AuthorizationContext[];
  linkIdentity: "user_confirmed" | "ai_inference" | "external_reference";
  confirmationStatus: "confirmed" | "unconfirmed";
};
