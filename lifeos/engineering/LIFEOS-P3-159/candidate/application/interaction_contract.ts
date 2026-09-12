/**
 * LifeOS interaction-v1. PM-owned additive transport contract, 2026-09-12.
 * Not an execution/authorization schema; all IDs and links are untrusted on IPC.
 * Existing P3-159 Evaluation/Response and v8 Action schemas remain authoritative.
 * No raw audio, API key, SQL, filesystem target, or permission boolean here.
 */
export type Ref = Readonly<{ id: string; revision: number }>;
export type Origin =
  | Readonly<{ kind: "keyboard" }>
  | Readonly<{ kind: "voice"; sessionId: string; segmentId: string;
      asrRequestId: string; language: string }>;
export interface UserTurn {
  readonly schemaVersion: "interaction-v1";
  readonly turnId: string;
  readonly conversationRef: Ref;
  readonly text: string;
  readonly origin: Origin;
  readonly finalizedAt: string;
  // Captured when input begins; hints, not forced topic or authorized targets.
  readonly replyTo?: Ref;
  readonly presentedProactiveRef?: Ref;
  readonly interruptedSpeechRequestId?: string;
}
export type AssistantContent =
  | Readonly<{ kind: "response"; text: string }>
  | Readonly<{ kind: "question"; text: string }>
  | Readonly<{ kind: "suggestion"; text: string; whyNow: string;
      evidenceRefs: readonly Ref[]; inferenceFlags: readonly string[] }>
  | Readonly<{ kind: "receipt"; text: string; receiptRef: Ref }>
  | Readonly<{ kind: "error"; text: string; code: string }>;
export interface AssistantTurn {
  readonly schemaVersion: "interaction-v1";
  readonly turnRef: Ref;
  readonly conversationRef: Ref;
  readonly inReplyToTurnId?: string;
  readonly origin: "conversation" | "proactive" | "transaction";
  readonly proactiveRef?: Ref;
  readonly content: AssistantContent;
  // Only finalized, host-validated outputs cross this boundary.
  readonly finalizedAt: string;
}
// Generic is bound by integration owner to the EXISTING Evaluation union.
// Not a new model-response format and never accepted by the voice provider.
export interface ProactiveCandidate<ExistingEvaluation> {
  readonly schemaVersion: "interaction-v1";
  readonly evaluationId: string;
  readonly candidate: ExistingEvaluation;
}
export type ProactiveDecision =
  | Readonly<{ schemaVersion: "interaction-v1"; decisionRef: Ref;
      kind: "silence"; reasonCode: string }>
  | Readonly<{ schemaVersion: "interaction-v1"; decisionRef: Ref;
      kind: "surface"; proactiveRef: Ref; assistantTurn: AssistantTurn }>;
export interface SpeechOutputRequest {
  readonly schemaVersion: "interaction-v1";
  readonly requestId: string;
  readonly sessionId: string;
  readonly sessionGeneration: number;
  readonly assistantTurnRef: Ref;
  readonly proactiveDecisionRef?: Ref;
  // Local registry reference to an existing host-validated turn projection.
  // Voice resolves only this text via host, never arbitrary frontend text/URL.
  readonly projectionRef: Ref;
  readonly policyRevision: number;
  readonly voice: "mimo_default";
  readonly language: "zh-CN";
}
export interface SpeechInterrupted {
  readonly schemaVersion: "interaction-v1";
  readonly eventId: string;
  readonly sessionId: string;
  readonly sessionGeneration: number;
  readonly speechRequestId: string;
  readonly assistantTurnRef: Ref;
  readonly reason: "user_speech" | "user_stop" | "disabled" |
    "device_lost" | "session_closed" | "output_invalidated";
  readonly occurredAt: string;
  readonly playedMilliseconds?: number;
}
export type UserTurnReceipt =
  | Readonly<{ turnId: string; status: "accepted" | "duplicate";
      recordRef: Ref }>
  | Readonly<{ turnId: string; status: "pending_authorization" |
      "rejected" | "unknown"; code: string }>;
export interface InteractionPort {
  submitUserTurn(turn: UserTurn): Promise<UserTurnReceipt>;
  onAssistantTurn(listener: (turn: AssistantTurn) => void): () => void;
  onSpeechOutputRequest(listener: (request: SpeechOutputRequest) => void): () => void;
  reportSpeechInterrupted(event: SpeechInterrupted): Promise<void>;
}

