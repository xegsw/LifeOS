import { OperationApplication, IpcOperationRepository } from './action_application.js';
import { ActionApplication, IpcActionRepository } from './action_application.js';
import { withFailureStage } from './health_errors.js';
import { HealthConversation } from './health_conversation.js';
import { chooseContext, interpretation } from './health_context.js';
export class LegacyControlledConversation extends HealthConversation {
    actions = new ActionApplication(new IpcActionRepository((c, o, p)=>withFailureStage(o, ()=>this.repo.invoke(c, {
                version: 6,
                operation: o,
                payload: p
            }))));
    async read() {
        const legacy = await super.read();
        const actions = await this.actions.read();
        return {
            ...legacy,
            revision: Math.max(legacy.revision, actions.revision),
            actions: actions.actions,
            actionFocus: actions.focus,
            turns: [
                ...legacy.turns,
                ...actions.turns
            ].sort((a, b)=>a.createdAt - b.createdAt).slice(-30)
        };
    }
    call5(command, operation, payload = {}) {
        return withFailureStage(operation, ()=>this.repo.invoke(command, {
                version: 5,
                operation,
                payload
            }));
    }
    saveCatalog(settings, revision) {
        return this.call5('save_ai_provider_settings', 'save_local_catalog', {
            requestId: crypto.randomUUID(),
            expectedRevision: revision,
            settings
        });
    }
    settings() {
        return this.call5('get_ai_provider_settings', 'read_local');
    }
    async lifecycle(operation, extra = {}) {
        const s = await this.read(), p = s.provider;
        return this.call5('save_ai_provider_settings', operation, {
            requestId: crypto.randomUUID(),
            expectedCredentialRevision: p.credentialRevision,
            expectedProfileRevision: p.profileRevision,
            expectedCatalogRevision: s.catalog.revision,
            expectedSettingsRevision: p.settingsRevision,
            ...operation === 'test_models' ? {} : {
                testReceiptId: p.testReceiptId || 'missing'
            },
            ...extra
        });
    }
    testModels() {
        return this.lifecycle('test_models');
    }
    selectModel(modelId) {
        return this.lifecycle('select_model', {
            modelId
        });
    }
    setEnabled(enabled) {
        return this.lifecycle('set_enabled', {
            enabled
        });
    }
    saveCredential(apiKey, revision) {
        return this.call5('save_ai_provider_settings', 'save_credential', {
            requestId: crypto.randomUUID(),
            expectedCredentialRevision: revision,
            apiKey
        });
    }
    deleteCredential(revision) {
        return this.call5('save_ai_provider_settings', 'delete_credential', {
            requestId: crypto.randomUUID(),
            expectedCredentialRevision: revision
        });
    }
    cancelPreview(previewId) {
        return this.call5('resolve_request_context', 'cancel_preview', {
            requestId: crypto.randomUUID(),
            previewId
        });
    }
    confirm(v) {
        return this.call5('send_source_ai_request', 'confirm_send', {
            requestId: 'send:' + v.previewId,
            previewId: v.previewId,
            expectedPreviewRevision: v.revision,
            confirmationToken: v.confirmationToken
        });
    }
    async prepare(d, current) {
        await this.draft(d);
        const actionResult = await this.actions.submit(d, current);
        if (actionResult.kind !== 'chat') return actionResult;
        const packet = await this.call('resolve_request_context', 'prepare_turn', {
            requestId: crypto.randomUUID(),
            turnId: d.turnId,
            expectedDraftRevision: d.revision
        });
        const context = chooseContext(packet), decision = interpretation(packet, context);
        if (!current()) {
            await this.cancel(d.turnId);
            throw {
                code: 'turn_cancelled'
            };
        }
        if (decision.state || decision.answerTo || decision.clarification) {
            await this.answer(d, current);
            return {
                kind: 'local'
            };
        }
        const settings = await this.settings();
        if (settings.credentialState !== 'stored' || !settings.modelId || !settings.enabled) throw {
            code: 'credential_missing'
        };
        const preview = await this.call5('resolve_request_context', 'prepare_disclosure', {
            requestId: crypto.randomUUID(),
            turnId: d.turnId,
            packetId: packet.id,
            modelId: settings.modelId,
            inputRefs: context.inputRefs
        });
        if (!current()) {
            await this.cancelPreview(preview.previewId);
            throw {
                code: 'turn_cancelled'
            };
        }
        return {
            kind: 'preview',
            preview
        };
    }
}
export class V7ControlledConversation extends LegacyControlledConversation {
    operationApp = new OperationApplication(new IpcOperationRepository((command, operation, payload)=>withFailureStage(operation, ()=>this.repo.invoke(command, {
                version: 7,
                operation,
                payload
            }))));
    async read() {
        const legacy = await HealthConversation.prototype.read.call(this);
        const actions = await this.operationApp.snapshot();
        return {
            ...legacy,
            revision: Math.max(legacy.revision, actions.revision),
            actions: actions.actions,
            actionFocus: actions.focus,
            turns: [
                ...legacy.turns,
                ...actions.turns
            ].sort((a, b)=>a.createdAt - b.createdAt).slice(-30)
        };
    }
    async prepare(d, current) {
        await this.draft(d);
        if (!current()) throw {
            code: 'turn_cancelled'
        };
        const preview = await this.operationApp.prepare(d);
        if (!current()) {
            await this.operationApp.cancel(preview);
            throw {
                code: 'turn_cancelled'
            };
        }
        return {
            kind: 'preview',
            preview
        };
    }
    confirm(v) {
        return this.operationApp.confirm(v);
    }
    cancelPreview(previewId, revision = 1) {
        return this.operationApp.cancel({
            previewId,
            revision
        });
    }
    operationStatus(requestId) {
        return this.operationApp.status(requestId);
    }
}
export function validateCoordinationReceipt(t, requestId) {
    const reject = ()=>{
        throw {
            code: 'dto_rejected'
        };
    };
    const object = (v, keys)=>{
        if (!v || Array.isArray(v) || typeof v !== 'object' || Object.keys(v).length !== keys.length || keys.some((k)=>!(k in v)) || Object.keys(v).some((k)=>!keys.includes(k))) reject();
    };
    const ref = (v)=>typeof v === 'string' && /^[A-Za-z0-9_:-]{1,120}$/.test(v);
    const revision = (v)=>Number.isSafeInteger(v) && v >= 1;
    const entity = (v)=>{
        object(v, [
            'id',
            'version'
        ]);
        if (!ref(v.id) || !revision(v.version)) reject();
    };
    const applied = (v)=>{
        object(v, [
            'action',
            'eventRef',
            'operation'
        ]);
        entity(v.action);
        if (!ref(v.eventRef) || ![
            'create',
            'adjust',
            'complete',
            'cancel'
        ].includes(v.operation)) reject();
    };
    const r = t.receipt;
    object(r, [
        'operationId',
        'turnRequestId',
        'turnId',
        'state',
        'committedAt',
        'reply',
        'result'
    ]);
    if (t.state !== 'committed' || r.state !== 'committed' || r.turnRequestId !== requestId || r.turnRequestId !== t.turnRequestId || r.turnId !== t.turnId || !ref(r.operationId) || !ref(r.turnId) || !Number.isSafeInteger(r.committedAt) || r.committedAt < 0 || typeof r.reply !== 'string' || Array.from(r.reply).length > 2000) reject();
    const result = r.result, k = result?.kind;
    switch(k){
        case 'none':
            object(result, [
                'kind',
                'businessChanged'
            ]);
            break;
        case 'clarify':
            object(result, [
                'kind',
                'businessChanged',
                'question'
            ]);
            if (typeof result.question !== 'string' || !result.question.trim() || Array.from(result.question).length > 200) reject();
            break;
        case 'action':
            object(result, [
                'kind',
                'businessChanged',
                'applied'
            ]);
            applied(result.applied);
            break;
        case 'condition_only':
            object(result, [
                'kind',
                'businessChanged',
                'condition',
                'truth',
                'reason'
            ]);
            entity(result.condition);
            if (![
                'true',
                'false',
                'unknown'
            ].includes(result.truth) || ![
                'condition_unknown',
                'condition_false',
                'record_only'
            ].includes(result.reason) || result.reason === 'condition_unknown' && result.truth !== 'unknown' || result.reason === 'condition_false' && result.truth !== 'false') reject();
            break;
        case 'condition_and_action':
            object(result, [
                'kind',
                'businessChanged',
                'condition',
                'truth',
                'applied'
            ]);
            entity(result.condition);
            applied(result.applied);
            if (result.truth !== 'true') reject();
            break;
        default:
            reject();
    }
    if (result.businessChanged !== ![
        'none',
        'clarify'
    ].includes(k) || t.businessChanged !== result.businessChanged) reject();
    return r;
}
export class ControlledConversation extends V7ControlledConversation {
    hostDrafts = new Map();
    active = new Map();
    previews = new Map();
    async call8(command, operation, payload) {
        const out = await withFailureStage(operation, ()=>this.repo.invoke(command, {
                version: 8,
                operation,
                payload
            }));
        if (out?.version !== 8 || out.operation !== operation || !out.result) throw {
            code: 'dto_rejected'
        };
        return out.result;
    }
    async read() {
        const snapshot = await super.read();
        const d = snapshot.pendingDraft;
        if (d?.status === 'cancelled') snapshot.pendingDraft = null;
        else if (d && !this.hostDrafts.has(d.turnId)) this.hostDrafts.set(d.turnId, {
            revision: d.revision,
            text: d.text
        });
        return snapshot;
    }
    async draft(d) {
        const old = this.hostDrafts.get(d.turnId);
        if (!d.text.trim()) return;
        if (old?.text === d.text) return;
        const r = await this.call8('capture_record', 'save_coordination_draft', {
            requestId: d.requestId,
            turnId: d.turnId,
            expectedDraftRevision: old?.revision || 0,
            text: d.text
        });
        this.hostDrafts.set(d.turnId, {
            revision: r.draftRevision,
            text: d.text
        });
    }
    view(p, t) {
        if (!p?.id || p.turnRequestId !== t.turnRequestId || ![
            'first',
            'second'
        ].includes(p.phase) || !Number.isInteger(p.revision)) throw {
            code: 'dto_rejected'
        };
        this.active.set(t.turnId, t);
        this.previews.set(p.id, t);
        return {
            ...p,
            version: 8,
            previewId: p.id,
            requestId: t.turnRequestId,
            question: p.disclosure.currentUser.text,
            items: p.disclosure.sources.map((x)=>({
                    citationId: x.ref,
                    identity: x.kind,
                    text: x.text
                })),
            instructions: p.systemPolicy,
            recipient: 'https://api.deepseek.com/chat/completions'
        };
    }
    async prepare(d, current) {
        await this.draft(d);
        if (!current()) throw {
            code: 'turn_cancelled'
        };
        const out = await this.call8('resolve_request_context', 'prepare_coordination_turn', {
            requestId: 'coord8-prepare:' + d.turnId,
            turnId: d.turnId,
            expectedDraftRevision: this.hostDrafts.get(d.turnId).revision
        });
        let t = await this.operationStatus(out.turn.turnRequestId), p = t.sendPreview;
        if ([
            'paused',
            'result_ready',
            'first_ready',
            'second_ready'
        ].includes(t.state) && (t.state === 'paused' || t.state === 'result_ready' || p?.expiresAt <= Date.now())) {
            const r = await this.call8('resolve_request_context', 'resume_coordination_turn', {
                requestId: crypto.randomUUID(),
                turnRequestId: t.turnRequestId,
                expectedTurnRevision: t.revision
            });
            t = r.turn;
            p = t.sendPreview;
        }
        if (!current()) {
            this.active.set(t.turnId, t);
            await this.cancel(d.turnId);
            throw {
                code: 'turn_cancelled'
            };
        }
        return {
            kind: 'preview',
            preview: this.view(p, t)
        };
    }
    async operationStatus(requestId) {
        return this.call8('get_context_recovery', 'coordination_turn_status', {
            turnRequestId: requestId
        });
    }
    async confirm(v) {
        let t;
        try {
            t = await this.call8('send_source_ai_request', 'confirm_coordination_model', {
                requestId: 'confirm:' + v.previewId,
                sendPreviewId: v.previewId,
                expectedRevision: v.revision
            });
        } catch (e) {
            t = await this.operationStatus(v.requestId).catch(()=>{
                throw e;
            });
            if (t.state === 'first_ready' || t.state === 'second_ready') throw e;
        }
        if (t.turnRequestId !== v.requestId) throw {
            code: 'identity_rejected'
        };
        this.active.set(t.turnId, t);
        if (t.state === 'result_ready') {
            const r = await this.call8('resolve_request_context', 'prepare_coordination_second_send', {
                requestId: crypto.randomUUID(),
                turnRequestId: t.turnRequestId,
                expectedTurnRevision: t.revision
            });
            return {
                state: 'awaiting-second-confirmation',
                preview: this.view(r.preview, r.turn)
            };
        }
        if (t.state === 'committed') {
            const r = validateCoordinationReceipt(t, v.requestId);
            this.active.delete(t.turnId);
            return {
                ...t,
                state: 'succeeded',
                reply: r.reply
            };
        }
        return t;
    }
    async cancelPreview(previewId) {
        const old = this.previews.get(previewId);
        if (!old) throw {
            code: 'preview_stale'
        };
        let t = old;
        let r;
        try {
            r = await this.call8('resolve_request_context', 'cancel_coordination_turn', {
                requestId: crypto.randomUUID(),
                turnRequestId: t.turnRequestId,
                expectedTurnRevision: t.revision
            });
        } catch (e) {
            if (e?.code !== 'revision_conflict') throw e;
            t = await this.operationStatus(old.turnRequestId);
            r = await this.call8('resolve_request_context', 'cancel_coordination_turn', {
                requestId: crypto.randomUUID(),
                turnRequestId: t.turnRequestId,
                expectedTurnRevision: t.revision
            });
        }
        this.active.delete(t.turnId);
        return r;
    }
    async cancel(turnId) {
        const old = this.active.get(turnId);
        if (old) {
            const t = await this.operationStatus(old.turnRequestId);
            if (t.state !== 'committed' && t.state !== 'cancelled') await this.call8('resolve_request_context', 'cancel_coordination_turn', {
                requestId: crypto.randomUUID(),
                turnRequestId: t.turnRequestId,
                expectedTurnRevision: t.revision
            });
            this.active.delete(turnId);
        }
        return super.cancel(turnId);
    }
}
export class ControlledFlow {
    app;
    changed;
    draft;
    snapshot = null;
    preview = null;
    opened = false;
    busy = false;
    phase = 'restoring';
    error = null;
    notice = '';
    readSerial = 0;
    serial = 0;
    queue = Promise.resolve();
    timer;
    token = null;
    preparedTurn = null;
    starting = null;
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
        const read = ++this.readSerial;
        try {
            const s = await this.app.read();
            if (read !== this.readSerial) return;
            if (!this.snapshot || s.revision >= this.snapshot.revision) this.snapshot = s;
            this.changed();
        } catch (e) {
            if (read === this.readSerial) throw e;
        }
    }
    failure(e, d) {
        return {
            code: e?.code,
            stage: e?.stage,
            turnId: d.turnId,
            draftRevision: d.revision
        };
    }
    async refreshResult(current, d) {
        try {
            await this.reload();
        } catch (e) {
            if (current()) {
                this.error = this.failure(e, d);
                this.phase = 'refresh-failed';
            }
        }
    }
    async restore() {
        if (!this.opened) return this.start();
        if (this.busy) return;
        const serial = this.serial;
        this.busy = true;
        this.phase = 'refreshing';
        this.changed();
        try {
            await this.reload();
            if (serial === this.serial) {
                this.error = null;
                this.notice = '';
                if (this.snapshot?.turns?.some((t)=>t.turnId === this.draft.turnId)) {
                    this.draft = this.newDraft();
                    this.preparedTurn = null;
                }
                this.phase = 'idle';
            }
        } catch (e) {
            if (serial === this.serial) {
                this.error = this.failure(e, this.draft);
                this.phase = 'refresh-failed';
            }
        } finally{
            this.busy = false;
            if (this.phase === 'refreshing') this.phase = 'idle';
            this.changed();
        }
    }
    start() {
        if (this.opened) return Promise.resolve();
        if (this.starting) return this.starting;
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
                this.error = null;
                this.notice = '';
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
        if (this.notice.startsWith('这句还没有记入安排') || this.notice.startsWith('没有取消任何已记下的安排')) this.notice = '';
        if (this.preparedTurn === this.draft.turnId) {
            if (this.preview) void this.app.cancelPreview(this.preview.previewId).catch(()=>{});
            void this.app.cancel(this.draft.turnId).catch(()=>{});
            this.preview = null;
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
        if (!this.busy) {
            this.phase = 'idle';
            this.error = null;
            this.changed();
        }
    }
    persist() {
        if (!this.opened) return;
        const d = {
            ...this.draft
        }, serial = this.serial;
        this.queue = this.queue.then(()=>this.app.draft(d)).catch((e)=>{
            if (serial === this.serial && d.turnId === this.draft.turnId && !this.busy) {
                this.error = this.failure(e, d);
                this.changed();
            }
        });
    }
    async prepare() {
        if (this.busy || !this.opened || !this.draft.text.trim()) return;
        const d = {
            ...this.draft
        }, serial = this.serial, token = crypto.randomUUID();
        this.token = token;
        this.preparedTurn = d.turnId;
        this.busy = true;
        this.phase = 'preparing';
        this.error = null;
        this.notice = '';
        clearTimeout(this.timer);
        this.changed();
        const current = ()=>this.token === token && this.serial === serial;
        try {
            await this.queue;
            const out = await this.app.prepare(d, current);
            if (current()) {
                this.error = null;
                if (out.kind === 'local') {
                    this.draft = this.newDraft();
                    this.preparedTurn = null;
                    this.preview = null;
                    this.phase = 'idle';
                    await this.refreshResult(current, d);
                } else if (out.kind === 'unsupported') {
                    this.preview = null;
                    this.notice = out.notice || '这句还没有记入安排。';
                    this.phase = 'idle';
                } else {
                    this.preview = out.preview;
                    this.phase = 'awaiting-confirmation';
                }
            }
        } catch (e) {
            if (current()) {
                this.error = this.failure(e, d);
                this.phase = e?.stage === 'commit_action_turn' ? 'refresh-failed' : 'failed';
            }
        } finally{
            if (this.token === token) {
                this.busy = false;
                this.token = null;
                if (this.phase === 'preparing') this.phase = 'idle';
                this.changed();
            }
        }
    }
    async confirm() {
        if (this.busy || !this.preview) return;
        const v = this.preview, d = {
            ...this.draft
        }, serial = this.serial, token = crypto.randomUUID();
        this.token = token;
        this.busy = true;
        this.phase = 'sending';
        this.error = null;
        this.changed();
        const current = ()=>this.token === token && this.serial === serial;
        try {
            const result = await this.app.confirm(v);
            if (current()) {
                this.preview = null;
                if (result.state === 'awaiting-second-confirmation') {
                    this.preview = result.preview;
                    this.phase = 'awaiting-confirmation';
                    this.notice = '已读取公开合成资料。请核对本次查询结果的发送内容。';
                } else if (result.state === 'paused') {
                    this.phase = 'paused';
                    this.notice = '发送预览已失效，继续时将重新核对并生成新预览。';
                } else if (result.state === 'succeeded') {
                    this.draft = this.newDraft();
                    this.preparedTurn = null;
                    this.phase = 'idle';
                } else if (result.state?.startsWith('cancel')) {
                    this.phase = 'cancelled';
                    this.notice = '已停止等待；已发出的内容无法保证撤回。';
                } else {
                    this.error = this.failure({
                        code: result.errorCode || 'dispatch_outcome_unknown',
                        stage: 'confirm_send'
                    }, d);
                    this.phase = 'failed';
                }
                if (this.phase === 'idle') await this.refreshResult(current, d);
                else {
                    try {
                        await this.reload();
                    } catch  {}
                }
            }
        } catch (e) {
            if (current()) {
                this.error = this.failure(e, d);
                this.preview = null;
                this.phase = 'failed';
            }
        } finally{
            if (this.token === token) {
                this.busy = false;
                this.token = null;
                this.changed();
            }
        }
    }
    async cancel() {
        const turn = this.preparedTurn, v = this.preview;
        this.token = null;
        const serial = ++this.serial;
        this.busy = false;
        this.phase = 'cancelled';
        this.error = null;
        this.preview = null;
        this.preparedTurn = null;
        this.notice = '已取消，草稿保留。';
        if (turn && this.draft.turnId === turn) this.draft = this.newDraft(this.draft.text);
        this.changed();
        if (v) {
            const r = await this.app.cancelPreview(v.previewId);
            if (serial === this.serial) {
                if (r.state === 'cancel_requested_after_dispatch' || r.state === 'cancelled_after_dispatch') this.notice = '已停止等待；已发出的内容无法保证撤回。';
                if (r.alreadyCompleted) {
                    this.notice = '回答已完成。';
                    this.draft = this.newDraft();
                }
            }
        }
        if (turn) await this.app.cancel(turn);
        if (serial === this.serial) {
            this.persist();
            await this.refreshResult(()=>serial === this.serial, this.draft);
        }
    }
    async settingsMutation(operation) {
        try {
            await operation();
        } catch (e) {
            try {
                await this.reload();
            } catch  {}
            throw e;
        }
        await this.reload();
    }
    async saveCatalog(settings, saved = ()=>{}) {
        if (this.preparedTurn) await this.cancel();
        await this.settingsMutation(async ()=>{
            await this.app.saveCatalog(settings, this.snapshot?.catalog?.revision || 0);
            saved();
        });
    }
    async selectModel(modelId) {
        if (this.preparedTurn) await this.cancel();
        let result;
        await this.settingsMutation(async ()=>{
            result = await this.app.selectModel(modelId);
        });
        return result;
    }
    async testModels() {
        if (this.preparedTurn) await this.cancel();
        let result;
        await this.settingsMutation(async ()=>{
            result = await this.app.testModels();
        });
        return result;
    }
    async setEnabled(enabled) {
        if (this.preparedTurn) await this.cancel();
        await this.settingsMutation(async ()=>{
            await this.app.setEnabled(enabled);
        });
    }
    async saveCredential(key, saved = ()=>{}) {
        if (this.preparedTurn) await this.cancel();
        await this.settingsMutation(async ()=>{
            await this.app.saveCredential(key, this.snapshot?.provider?.credentialRevision || 0);
            saved();
        });
    }
    async deleteCredential() {
        if (this.preparedTurn) await this.cancel();
        await this.settingsMutation(async ()=>{
            await this.app.deleteCredential(this.snapshot?.provider?.credentialRevision || 0);
        });
    }
    async decide(id, d) {
        await this.app.decision(id, d);
        await this.reload();
    }
    dispose() {
        clearTimeout(this.timer);
    }
}
