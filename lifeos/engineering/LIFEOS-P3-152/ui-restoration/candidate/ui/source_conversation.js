export class SourceConversation {
    repository;
    constructor(repository){
        this.repository = repository;
    }
    call(command, operation, payload = {}) {
        return this.repository.invoke(command, {
            version: command === 'send_source_ai_request' ? 1 : 3,
            operation,
            payload
        });
    }
    open(conversationId) {
        return this.call('get_context_recovery', 'open_conversation', {
            requestId: crypto.randomUUID(),
            conversationId
        });
    }
    read(conversationId, cursor) {
        return this.call('get_context_recovery', 'read_conversation', {
            conversationId,
            ...cursor ? {
                cursor
            } : {}
        });
    }
    async ask(draft) {
        await this.call('capture_record', 'draft_question', draft);
        return this.call('capture_record', 'save_question', {
            requestId: 'commit:' + draft.requestId,
            draftId: draft.draftId,
            conversationId: draft.conversationId,
            turnId: draft.turnId,
            expectedDraftRevision: draft.revision
        });
    }
    preview(turnId, excludedSegmentIds = []) {
        return this.call('assemble_global_ai_context', 'prepare_source_preview', {
            requestId: crypto.randomUUID(),
            conversationId: 'source-chat',
            turnId,
            expectedQuestionVersion: 1,
            excludedSegmentIds
        });
    }
    send(preview) {
        return this.call('send_source_ai_request', 'confirm_send', {
            requestId: 'send:' + preview.previewId,
            previewId: preview.previewId,
            expectedPreviewRevision: preview.revision,
            confirmationToken: preview.confirmationToken
        });
    }
    cancel(preview) {
        return this.call('assemble_global_ai_context', 'cancel_source_preview', {
            requestId: crypto.randomUUID(),
            previewId: preview.previewId,
            expectedPreviewRevision: preview.revision
        });
    }
    settings() {
        return this.call('get_ai_provider_settings', 'read_settings');
    }
}
