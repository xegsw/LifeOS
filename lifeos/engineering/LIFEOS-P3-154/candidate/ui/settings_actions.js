const messages = {
    runtime_target_rejected: '本地存储目录未通过检查，保存已停止。',
    database_path_rejected: '本地凭据存储未通过检查，保存已停止。',
    database_unavailable: '本地存储暂不可用。',
    store_contract_mismatch: '本地存储结构未通过检查。',
    credential_invalid: 'API Key 格式不正确，请检查输入。',
    credential_missing: '尚未保存 API Key。',
    credential_unavailable: '系统钥匙串暂不可用，请检查系统授权后重试。',
    credential_revision_conflict: '凭据状态已变化，请核对后再次保存。',
    credential_authentication_failed: '本地凭据无法解密，请重新保存。',
    credential_reference_rejected: '本地凭据引用未通过检查。',
    credential_cleanup_pending: '凭据清理尚未完成。',
    catalog_rejected: '请填写有效的模型名称和配置。',
    catalog_revision_conflict: '配置已变化，请核对后再次保存。',
    model_rejected: '模型名称格式不正确。',
    model_limit_reached: '已保存的模型数量达到上限。',
    settings_revision_conflict: '设置已变化，请核对后重新操作。',
    model_not_tested: '请先手动测试并读取模型列表。',
    model_selection_required: '请先确认选择模型。',
    provider_authentication: '服务拒绝了凭据，请检查 API Key。',
    provider_timeout: '本次请求超时，请手动重试；API Key 不会因此过期。',
    provider_protocol: '模型列表未通过检查，请手动重试。',
    provider_not_enabled: '当前服务尚未接入测试。',
    settings_save_failed: '保存未完成，请重试。'
};
export function settingsError(e) {
    const code = Object.hasOwn(messages, e?.code) ? e.code : 'settings_save_failed';
    return `${messages[code]}（${code}）`;
}
export class SettingsActions {
    flow;
    changed;
    busy = false;
    notice = '';
    constructor(flow, changed){
        this.flow = flow;
        this.changed = changed;
    }
    async lifecycle(kind, model = '') {
        if (this.busy) return;
        this.busy = true;
        this.notice = kind === 'test' ? '正在测试并读取模型列表…' : '正在保存…';
        this.changed();
        try {
            if (kind === 'test') {
                const out = await this.flow.testModels();
                this.notice = out.state === 'succeeded' ? '测试成功，请选择模型并确认。' : settingsError({
                    code: this.flow.snapshot?.provider?.testErrorCode || 'model_not_tested'
                });
            }
            if (kind === 'select') {
                const out = await this.flow.selectModel(model);
                this.notice = out.state === 'retest_required' ? '更换模型需要重新测试，请点击“测试并读取模型”。' : '模型已选择，尚未启用。';
            }
            if (kind === 'enable' || kind === 'disable') {
                await this.flow.setEnabled(kind === 'enable');
                this.notice = kind === 'enable' ? '所选模型已显式启用。' : '模型已停用。';
            }
        } catch (e) {
            this.notice = settingsError(e);
        } finally{
            this.busy = false;
            this.changed();
        }
    }
    async save(kind, input, settings) {
        if (this.busy) return;
        this.busy = true;
        this.notice = '正在保存…';
        let credentialSaved = false, catalogSaved = false;
        const key = input?.value || '';
        const clear = ()=>{
            credentialSaved = true;
            if (input && input.value === key) input.value = '';
        };
        this.changed();
        try {
            if (kind === 'delete') {
                await this.flow.deleteCredential();
                this.notice = '凭据已移除。';
                return;
            }
            if (kind === 'catalog') {
                await this.flow.saveCatalog(settings, ()=>{
                    catalogSaved = true;
                });
                if (key && settings.primary.mode === 'cloud' && settings.primary.providerId === 'deepseek') await this.flow.saveCredential(key, clear);
            } else await this.flow.saveCredential(key, clear);
            this.notice = credentialSaved ? catalogSaved ? '配置和 API Key 已保存。' : 'API Key 已保存。' : '配置已保存。';
        } catch (e) {
            this.notice = (credentialSaved ? 'API Key 已保存，后续配置未完成。' : catalogSaved ? '配置已保存，后续保存未完成。' : '') + settingsError(e);
        } finally{
            this.busy = false;
            this.changed();
        }
    }
}
