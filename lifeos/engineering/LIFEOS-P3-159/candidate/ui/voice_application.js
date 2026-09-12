import { VoiceConsumer } from './voice/consumer.js';
import { voiceSettings } from './voice/settings.js';
export class OfflineVoiceApplication {
    call;
    snapshot = {
        state: 'disabled',
        sessionId: null,
        generation: 0,
        policyRevision: 0
    };
    settings = {
        enabled: false,
        asr: false,
        tts: false,
        sessionTurn: false,
        wakeWord: 'LifeOS',
        keyConfigured: false,
        usageLabel: '离线接线验证',
        available: false
    };
    consumer;
    constructor(call, interaction){
        this.call = call;
        this.consumer = new VoiceConsumer(interaction, this);
    }
    status() {
        return this.snapshot;
    }
    async refresh() {
        const r = await this.call('voice_status', {
            version: 1,
            payload: {}
        });
        if (r?.version !== 1 || r.settings?.available !== false || r.status?.state !== 'disabled') throw new Error('voice_offline_contract');
        this.snapshot = r.status;
        this.settings = r.settings;
    }
    html() {
        return voiceSettings(this.settings, this.snapshot);
    }
    canSubmit(_turn) {
        return false;
    }
    onFinal(_listener) {
        return ()=>{};
    }
    onInterrupted(_listener) {
        return ()=>{};
    }
    async speak(_request) {
        throw new Error('voice_offline_unavailable');
    }
    stopPlayback() {}
    receipt(_receipt) {}
    failure(_code) {}
    dispose() {
        this.consumer.dispose();
    }
}
