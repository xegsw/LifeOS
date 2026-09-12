export class VoiceConsumer {
    disposeCallbacks = [];
    disposed = false;
    consumed = new Map();
    played = new Set();
    pending = false;
    interaction;
    voice;
    constructor(interaction, voice){
        this.interaction = interaction;
        this.voice = voice;
        this.disposeCallbacks = [
            voice.onFinal((t)=>{
                void this.final(t);
            }),
            voice.onInterrupted((e)=>{
                void this.interrupted(e);
            }),
            interaction.onSpeechOutputRequest((r)=>{
                void this.output(r);
            })
        ];
    }
    async final(turn) {
        if (this.disposed) return;
        const s = this.voice.status();
        if (turn.schemaVersion !== 'interaction-v1' || turn.origin.kind !== 'voice' || !turn.text.trim() || turn.origin.sessionId !== s.sessionId || !this.voice.canSubmit(turn)) {
            this.voice.failure('voice_turn_denied');
            return;
        }
        const key = turn.origin.sessionId + '\u0000' + turn.origin.segmentId;
        const fingerprint = JSON.stringify(turn);
        const old = this.consumed.get(key);
        if (old) {
            if (old.fingerprint !== fingerprint) this.voice.failure('voice_segment_conflict');
            return;
        }
        if (this.pending) {
            this.voice.failure('voice_submission_busy');
            return;
        }
        if (this.consumed.size >= 4096) {
            this.voice.failure('voice_session_capacity');
            return;
        }
        this.consumed.set(key, {
            fingerprint,
            turnId: turn.turnId
        });
        this.pending = true;
        try {
            const r = await this.interaction.submitUserTurn(turn);
            this.voice.receipt(r);
        } catch  {
            this.voice.receipt({
                turnId: turn.turnId,
                status: 'unknown',
                code: 'voice_submission_unknown'
            });
        } finally{
            this.pending = false;
        }
    }
    async output(request) {
        if (this.disposed) return;
        const s = this.voice.status();
        if (request.schemaVersion !== 'interaction-v1' || request.sessionId !== s.sessionId || request.sessionGeneration !== s.generation || request.policyRevision !== s.policyRevision || [
            'disabled',
            'wake_listening',
            'recovering'
        ].includes(s.state)) return;
        const key = request.requestId;
        if (this.played.has(key)) return;
        if (this.played.size >= 4096) {
            this.voice.failure('voice_session_capacity');
            return;
        }
        this.played.add(key);
        try {
            await this.voice.speak(request);
        } catch  {
            this.voice.failure('voice_playback_unavailable');
        }
    }
    async interrupted(event) {
        if (this.disposed) return;
        this.voice.stopPlayback();
        try {
            await this.interaction.reportSpeechInterrupted(event);
        } catch  {
            this.voice.failure('voice_interrupt_report_failed');
        }
    }
    dispose() {
        if (this.disposed) return;
        this.disposed = true;
        this.voice.stopPlayback();
        for (const f of this.disposeCallbacks)f();
        this.disposeCallbacks = [];
        this.consumed.clear();
        this.played.clear();
    }
}
