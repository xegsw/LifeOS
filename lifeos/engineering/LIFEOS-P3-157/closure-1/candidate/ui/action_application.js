import { actionCandidate, classifyAction, validateCandidate, transition } from './action_domain.js';
export class OfflineActionModel {
    id;
    constructor(id){
        this.id = id;
    }
    async parse(p) {
        return actionCandidate(p);
    }
}
export class ActionApplication {
    repo;
    model;
    constructor(repo, model = new OfflineActionModel('OfflineA')){
        this.repo = repo;
        this.model = model;
    }
    read() {
        return this.repo.snapshot();
    }
    async submit(d, current) {
        const p = await this.repo.prepare(d.turnId, d.revision);
        if (!current()) throw {
            code: 'turn_cancelled'
        };
        const classification = classifyAction(p);
        if (classification.kind === 'chat') return {
            kind: 'chat'
        };
        if (classification.kind === 'unsupported_action') return {
            kind: 'unsupported',
            notice: classification.notice
        };
        const c = await this.model.parse(p);
        if (!c) return {
            kind: 'unsupported',
            notice: '这句还没有记入安排，解析结果未能通过本地确认。'
        };
        validateCandidate(p, c);
        if (c.operation !== 'clarify') transition(p.actions.find((a)=>a.id === c.targetId), c, {
            id: 'validation',
            rawId: d.turnId,
            at: Date.now()
        });
        if (!current()) throw {
            code: 'turn_cancelled'
        };
        await this.repo.commit(d, p, c, this.model.id);
        return {
            kind: 'local'
        };
    }
}
export class IpcActionRepository {
    call;
    constructor(call){
        this.call = call;
    }
    prepare(turnId, revision) {
        return this.call('resolve_request_context', 'prepare_action_turn', {
            requestId: 'action-prepare:' + turnId + ':' + revision,
            turnId,
            expectedDraftRevision: revision
        });
    }
    commit(d, p, c, modelId) {
        return this.call('resolve_request_context', 'commit_action_turn', {
            requestId: 'action-commit:' + d.turnId,
            turnId: d.turnId,
            packetId: p.id,
            expectedDraftRevision: d.revision,
            candidate: c,
            modelId
        });
    }
    snapshot(offset = 0) {
        return this.call('get_context_recovery', 'action_snapshot', {
            offset
        });
    }
}
