import { chooseContext, interpretation, OfflineAdapter } from './health_context.js';
export class HealthConversation {
    repo;
    models = {
        OfflineA: new OfflineAdapter('OfflineA'),
        OfflineB: new OfflineAdapter('OfflineB')
    };
    constructor(repo){
        this.repo = repo;
    }
    call(command, operation, payload = {}) {
        return this.repo.invoke(command, {
            version: 4,
            operation,
            payload
        });
    }
    read() {
        return this.call('get_context_recovery', 'conversation_snapshot');
    }
    draft(d) {
        return this.call('capture_record', 'draft_turn', {
            requestId: d.requestId,
            turnId: d.turnId,
            revision: d.revision,
            text: d.text
        });
    }
    cancel(turnId) {
        return this.call('resolve_request_context', 'cancel_turn', {
            requestId: 'cancel:' + turnId,
            turnId
        });
    }
    decision(questionId, decision) {
        return this.call('decide_understanding_feedback', 'clarification_decision', {
            requestId: crypto.randomUUID(),
            questionId,
            decision
        });
    }
    select(modelId) {
        return this.call('save_ai_provider_settings', 'select_offline_adapter', {
            requestId: crypto.randomUUID(),
            modelId
        });
    }
    async answer(d, current) {
        await this.draft(d);
        const args = {
            turnId: d.turnId,
            expectedDraftRevision: d.revision
        };
        const packet = await this.call('resolve_request_context', 'prepare_turn', {
            requestId: 'prepare:' + d.turnId + ':' + d.revision,
            ...args
        });
        let context = chooseContext(packet);
        const decision = interpretation(packet, context);
        if (decision.state) {
            const old = packet.snapshot.states.filter((s)=>s.domain === decision.state.domain && s.stateKey === decision.state.key).map((s)=>s.rawId);
            context.included = context.included.filter((r)=>!old.includes(r.id));
            context.inputRefs = context.inputRefs.filter((r)=>!old.includes(r.id));
            context.states = context.states.filter((s)=>!old.includes(s.rawId));
            context.usedBytes = new TextEncoder().encode(JSON.stringify(context.included)).length;
        }
        const fresh = await this.call('resolve_request_context', 'prepare_turn', {
            requestId: crypto.randomUUID(),
            ...args
        });
        if (!current()) {
            await this.cancel(d.turnId);
            throw {
                code: 'turn_cancelled'
            };
        }
        if (fresh.id !== packet.id || fresh.modelId !== packet.modelId || fresh.domain !== packet.domain || fresh.expiresAt <= Date.now() || context.usedBytes > 4096) throw {
            code: 'context_stale'
        };
        const model = this.models[packet.modelId];
        if (!model) throw {
            code: 'adapter_rejected'
        };
        const output = await model.generate(fresh, context, decision);
        if (!current()) {
            await this.cancel(d.turnId);
            throw {
                code: 'turn_cancelled'
            };
        }
        const payload = {
            requestId: 'commit:' + d.turnId,
            turnId: d.turnId,
            packetId: packet.id,
            modelId: model.id,
            text: output.text,
            inputRefs: output.inputRefs
        };
        for (const k of [
            'state',
            'corrects',
            'answerTo',
            'clarification'
        ])if (decision[k] !== undefined) payload[k] = decision[k];
        return this.call('resolve_request_context', 'commit_turn', payload);
    }
}
export class HealthFlow {
    app;
    changed;
    draft;
    snapshot = null;
    opened = false;
    busy = false;
    phase = 'restoring';
    error = null;
    serial = 0;
    starting = null;
    queue = Promise.resolve();
    timer;
    token = null;
    preparedTurn = null;
    constructor(app, changed){
        this.app = app;
        this.changed = changed;
        this.draft = this.newDraft();
    }
    newDraft(text = '') {
        return {
            requestId: crypto.randomUUID(),
            turnId: crypto.randomUUID(),
            revision: 1,
            text
        };
    }
    async reload() {
        const s = await this.app.read();
        if (!this.snapshot || s.revision >= this.snapshot.revision) this.snapshot = s;
        this.changed();
    }
    start() {
        if (this.opened) return Promise.resolve();
        if (this.starting) return this.starting;
        this.phase = 'restoring';
        this.changed();
        this.starting = (async ()=>{
            try {
                const s = await this.app.read();
                this.snapshot = s;
                this.opened = true;
                if (this.serial === 0 && s.pendingDraft) {
                    const d = s.pendingDraft;
                    this.draft = d.status === 'cancelled' ? this.newDraft(d.text) : {
                        requestId: crypto.randomUUID(),
                        turnId: d.turnId,
                        revision: d.revision,
                        text: d.text
                    };
                }
                this.phase = 'idle';
                if (this.serial) this.persist();
            } catch (e) {
                this.error = e;
                this.phase = 'open-failed';
            } finally{
                this.starting = null;
                this.changed();
            }
        })();
        return this.starting;
    }
    edit(text) {
        if (this.preparedTurn === this.draft.turnId) {
            void this.app.cancel(this.draft.turnId).catch(()=>{});
            this.draft = this.newDraft(this.draft.text);
            this.preparedTurn = null;
        }
        this.draft = {
            ...this.draft,
            text,
            revision: this.draft.revision + 1,
            requestId: crypto.randomUUID()
        };
        this.serial++;
        clearTimeout(this.timer);
        this.timer = setTimeout(()=>this.persist(), 200);
    }
    persist() {
        if (!this.opened) return;
        const d = {
            ...this.draft
        };
        this.queue = this.queue.then(()=>this.app.draft(d)).catch((e)=>{
            this.error = e;
            this.changed();
        });
    }
    async send() {
        if (this.busy || !this.opened || !this.draft.text.trim()) return;
        const d = {
            ...this.draft
        }, serial = this.serial, token = crypto.randomUUID();
        this.token = token;
        this.preparedTurn = d.turnId;
        this.busy = true;
        this.phase = 'sending';
        this.error = null;
        clearTimeout(this.timer);
        this.changed();
        const current = ()=>this.token === token && this.serial === serial;
        try {
            await this.queue;
            await this.app.answer(d, current);
            if (current()) {
                this.draft = this.newDraft();
                this.preparedTurn = null;
                this.phase = 'idle';
            }
            await this.reload();
        } catch (e) {
            if (current()) {
                this.error = e;
                this.phase = e?.code === 'turn_cancelled' ? 'cancelled' : 'failed';
            }
        } finally{
            if (this.token === token) {
                this.busy = false;
                this.token = null;
                if (this.phase === 'sending') this.phase = 'idle';
                this.changed();
            }
        }
    }
    async cancel() {
        const turn = this.preparedTurn;
        if (!turn) return;
        this.token = null;
        this.serial++;
        this.busy = false;
        this.phase = 'cancelled';
        this.error = null;
        this.preparedTurn = null;
        if (this.draft.turnId === turn) this.draft = this.newDraft(this.draft.text);
        this.changed();
        await this.app.cancel(turn);
        this.persist();
        await this.reload();
    }
    async select(modelId) {
        if (this.preparedTurn) await this.cancel();
        await this.app.select(modelId);
        await this.reload();
    }
    async decide(questionId, decision) {
        await this.app.decision(questionId, decision);
        await this.reload();
    }
    dispose() {
        clearTimeout(this.timer);
    }
}
