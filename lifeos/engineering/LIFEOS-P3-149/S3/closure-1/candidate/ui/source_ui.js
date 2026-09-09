import { SourceConversation } from './source_conversation.js';
import { ConversationFlow } from './conversation_flow.js';
import { healthView, healthSettings } from './health_view.js';
import { AppleImportController, appleImportView } from './apple_import.js';
import { icon } from './source_icons.js';
const real = window.__LIFEOS_REAL_SOURCE__ === true;
const testLabel = real ? '测试连接' : '测试连接（合成）';
const invoke = window.__TAURI__.core.invoke;
const app = new SourceConversation({
    invoke: (command, request)=>invoke(command, new TextEncoder().encode(JSON.stringify(request)))
});
const esc = (s)=>String(s ?? '').replace(/[&<>"']/g, (c)=>({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[c]);
const cloud = [
    'OpenAI',
    'Anthropic',
    'Google Gemini',
    'DeepSeek',
    'Kimi',
    'OpenRouter',
    '其他 OpenAI-compatible 服务',
    '自定义兼容接口'
];
const local = [
    'Ollama',
    'LM Studio',
    'OpenAI-compatible 本地接口',
    '自定义本地服务'
];
let page = 'Today', settingsSection = '模型设置', aiOpen = false, busy = false, notice = '', turns = [], settings = null, detail = null, correction = null, correctionText = '', excluded = [];
let nextCursor, sourceStatus = null, sourceRows = [], sourceQuery = '', localSnapshot = null;
const flow = new ConversationFlow(app, ()=>render(), refresh);
const apple = new AppleImportController(invoke, ()=>{
    if (page === 'Settings' && settingsSection === '数据与隐私') render();
}, refresh);
async function sourceCall(command, payload = {}) {
    return invoke(command, {
        request: {
            version: 1,
            payload
        }
    });
}
const button = (a, text, id = '', secondary = false)=>`<button type="button" class="button ${secondary ? 'secondary' : 'primary'}" data-action="${a}" data-id="${esc(id)}" ${busy || flow.busy ? 'disabled' : ''}>${text}</button>`;
const messages = {
    provider_not_enabled: 'AI 服务尚未启用，请先配置AI服务。',
    context_stale: '来源已变化，请重新准备发送内容。',
    preview_stale: '发送内容已失效，请重新准备。',
    preview_expired: '发送内容已过期，请重新准备。',
    database_unavailable: '无法打开已有本地会话。当前编辑内容仍保留。',
    confirmation_rejected: '确认已失效，本次未发送。',
    credential_invalid: real ? 'API Key 格式不正确，请在设置中检查。' : '请输入虚构的合成测试凭据。',
    dispatch_outcome_unknown: '可能已发送，结果未确认；不会自动重发。',
    context_budget_rejected: '相关内容过长，请收窄问题。',
    sensitive_content_rejected: '内容可能包含秘密，请编辑后再试。',
    credential_unavailable: '凭据暂不可用，请配置AI服务。'
};
function error(e) {
    const code = e?.code || e?.message || 'operation_failed';
    return messages[code] || `当前操作未完成（${String(code)}）。`;
}
const mark = ()=>real ? '本地会话' : '合成演练，未联网';
function header(title, sub) {
    return `<header class="page-head"><div><h1>${title}</h1><p class="subhead">${sub}</p></div><span class="synthetic-mark">${mark()}</span></header>`;
}
function today() {
    return `<section class="today-page"><div class="today-hero"><div><h1>你好。</h1><p class="today-subhead">给今天留一点从容。</p></div><div class="today-chrome"><span>${new Intl.DateTimeFormat('zh-CN', {
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    }).format(new Date())}</span><span class="header-icon">${icon('calendar')}</span></div></div><span class="synthetic-mark">${mark()}</span><div class="today-grid"><div class="today-main stack"><section class="panel reference-card"><div class="section-head"><h2>今日重点</h2>${icon('target')}</div><p class="quiet">当前没有可展示的今日重点。</p><p class="tiny">你可以从下方问一个问题，理清下一步。</p></section><section class="panel"><h2>一天概览</h2><p class="quiet">${(localSnapshot?.states || []).filter((s)=>s.status === 'active').map((s)=>`${esc(s.stateKey)} · ${esc(s.value)}`).join('<br>') || '当前没有有效状态。'}</p></section></div><aside class="today-aside stack"><section class="panel"><h2>最近对话</h2><p class="quiet">${turns.length ? esc(turns[turns.length - 1].text) : '还没有问题。想到什么，就从这里开始。'}</p>${turns.length ? button('open-ai', '继续对话', '', true) : ''}</section><section class="panel recent-card"><h2>已有资料</h2><p class="quiet">${sourceStatus ? `已解析 ${esc(sourceStatus.parsed)} 份正文` : '还没有已导入资料。'}</p><button class="button ghost" data-page="Memory">找回原文依据</button></section></aside></div></section>`;
}
function settingsPanel() {
    const configured = settings?.credentialState === 'stored';
    return `<div class="settings-shell"><nav class="settings-nav" aria-label="设置导航"><p>设置</p>${[
        '通用',
        '模型设置',
        '数据与隐私',
        '备份与导出',
        '关于'
    ].map((s)=>`<button data-settings="${s}" aria-current="${settingsSection === s ? 'page' : 'false'}">${s}</button>`).join('')}</nav><div class="settings-content">${settingsSection === '模型设置' ? `${header('模型设置', '为 LifeOS 配置你选择的 AI 服务。')}<section class="service-card ${configured ? '' : 'empty'}"><div><p class="eyebrow">主要 AI 服务</p><h2>DeepSeek</h2><p>${configured ? '凭据已保存 · ••••' + esc(settings.maskedTail) : settings?.credentialState === 'cleanup_pending' ? '凭据操作待恢复' : settings?.credentialState === 'unavailable' ? '凭据暂不可用' : '尚未配置凭据'}</p></div><span class="state-dot ${settings?.enabled ? 'success' : ''}">${settings?.enabled ? '已启用' : '未启用'}</span></section><div class="settings-grid"><div class="main-stack"><section class="config-card"><div class="section-heading"><h2>服务配置</h2><span class="microcopy">${mark()}</span></div><details data-keep="catalog"><summary>添加或更换服务</summary><div class="provider-directory"><h3>云端服务</h3>${cloud.map((s)=>`<p>${s}<small> · ${s === 'DeepSeek' ? '本轮可配置' : '目录保留，未连接'}</small></p>`).join('')}<h3>本地服务</h3>${local.map((s)=>`<p>${s}<small> · 目录保留，未连接</small></p>`).join('')}</div></details><div class="form-grid"><label class="wide">${real ? 'API Key' : '合成 API Key'}<input type="password" id="key" autocomplete="off" placeholder="${real ? '仅在此 App 输入' : '仅输入虚构演练值'}"></label><label class="wide">已测试的模型<select id="model">${(settings?.models || []).map((m)=>`<option ${settings.modelId === m ? 'selected' : ''}>${esc(m)}</option>`).join('')}</select></label></div><div class="form-actions">${button('save-key', '保存凭据')}${button('test', testLabel, '', true)}${button('select', '选择模型', '', true)}${button('enable', settings?.enabled ? '停用模型' : '启用此模型')}</div></section><section class="routing-card"><h2>使用策略</h2><p class="quiet">每次发送前由你确认。</p><div class="policy-list"><p>自动切换备用服务 <strong>关闭</strong></p><p>自动云端补充 <strong>关闭</strong></p></div><div class="fallback">备用服务未启用</div></section><details class="advanced config-card" data-keep="advanced"><summary>高级设置与凭据管理</summary><p>来源最多3段、每段800字符；实际请求上限24 KiB，输出上限1024 token。</p><p>${real ? '凭据加密保存在本机；业务库未加密。' : '模拟凭据存储，不访问 OS Keychain 或 Provider。'}</p><div class="form-actions">${button('recover', '恢复凭据操作', '', true)}${button('delete-key', '删除凭据', '', true)}</div></details></div><aside class="capability-card"><h2>当前能力</h2><div class="capability-list"><div><strong>文字对话</strong><small>${settings?.enabled ? '已启用，逐次确认后发送' : '配置并启用后可用'}</small></div><div><strong>来源引用</strong><small>仅使用已导入、当前有效的相关片段。</small></div><div><strong>其他能力</strong><small>图片、语音、联网搜索和工具调用未启用。</small></div></div></aside></div>` : settingsSection === '数据与隐私' ? header('数据与隐私', '你的资料由你掌控。') + appleImportView(apple.state) + healthSettings(localSnapshot) + sourcePanel() : header(settingsSection, '本版本暂无可调整的选项。')}<details class="usage-help"><summary>使用说明</summary><p>本版本仅演练手动选择合成苹果健康文件导入，非自动同步。来源笔记不重新扫描。</p></details><button class="button ghost" data-action="return-ai">返回对话</button></div></div>`;
}
function disclosure() {
    const p = flow.preview;
    if (!p) return '';
    const n = p.items.filter((i)=>i.kind === 'source').length, m = p.items.length - n;
    return `<section class="confirmation" aria-label="本次披露预览"><p><strong>将把你的问题和${n}段相关笔记${m ? `，以及${m}条用户纠正` : ''}发送给DeepSeek</strong></p><small>${esc(p.provider)} · ${esc(p.modelId)} · ${mark()}</small><details data-keep="disclosure:${esc(p.previewId)}"><summary>查看发送内容</summary><h3>你的问题</h3><p class="verbatim">${esc(p.question)}</p>${p.items.map((i)=>`<article class="disclosed-item"><strong>${esc(i.citationId)} · ${i.kind === 'source' ? '相关笔记' : '用户纠正'}</strong><p class="verbatim">${esc(i.text)}</p><small>${esc(i.source?.locator || '用户表达')}</small>${i.source ? button('remove', '本次移除', i.source.segmentId, true) : ''}</article>`).join('')}<h3>固定模型说明</h3><p class="verbatim">${esc(p.instructions)}</p><details><summary>实际请求 JSON</summary><pre class="source-original">${esc(p.bodyJson)}</pre></details></details>${p.state === 'no_match' ? '<p>没有找到相关依据，本次不会生成回答。</p>' : p.state !== 'ready' ? '<p>内容已失效，请重新准备。</p>' : ''}<div class="form-actions">${p.state === 'ready' ? button('send', '确认发送') : ''}${button('cancel-preview', '取消', '', true)}</div></section>`;
}
function conversation() {
    return `${!turns.length ? '<p class="quiet">问一个问题，连接已有资料。</p>' : ''}${turns.map((t)=>`<article class="turn"><div class="ai-question"><small>你的问题</small><p class="verbatim">${esc(t.text)}</p></div>${t.answer?.text ? `<div class="ai-answer"><small>AI 回答 · ${t.answer.validity === 'stale' ? '已失效，保留历史' : '供你参考'}</small><p class="verbatim">${esc(t.answer.text)}</p><div class="citations">${t.answer.citations.map((c)=>c.availability && c.availability !== 'available' ? `<span class="identity warning">${esc(c.citationId)} · 来源已失效</span>` : button('citation', c.citationId, JSON.stringify(c.source), true)).join('')}</div>${t.answer.invalidCitationCount ? '<p class="tiny">部分引用无法核实。</p>' : ''}<details data-keep="feedback:${esc(t.answer.answerId)}"><summary>反馈或纠正（可选）</summary><div class="form-actions">${button('helpful', '有帮助', t.answer.answerId, true)}${button('correct', '纠正', t.answer.answerId, true)}${button('reject', '不适合', t.answer.answerId, true)}</div></details></div>` : t.answer ? `<p>${esc(error({
            code: t.answer.errorCode || 'dispatch_outcome_unknown'
        }))}</p>` : '<p class="tiny">问题已保存在本地。</p>'}${!t.answer?.text ? button('preview', '重新准备', t.turnId, true) : ''}</article>`).join('')}${nextCursor ? button('next-page', '查看更多对话', '', true) : ''}${disclosure()}${correction ? `<section class="confirmation"><h2>纠正这条回答</h2><label>你的纠正<textarea id="correction" maxlength="2000">${esc(correctionText)}</textarea></label><div class="form-actions">${button('save-correction', '保存纠正')}${button('cancel-correction', '取消', '', true)}</div></section>` : ''}${detail ? `<section class="confirmation"><h2>已导入来源 · v${detail.version}</h2>${detail.segments.map((s)=>`<small>${esc(s.locator)}</small><pre class="source-original">${esc(s.text)}</pre>`).join('')}</section>` : ''}`;
}
const composer = document.createElement('form');
composer.className = 'question-form';
composer.innerHTML = `<button type="button" class="ai-launch" data-action="open-ai" aria-label="Global AI">${icon('spark')}</button><label class="sr-only" for="conversation">自然提问</label><textarea id="conversation" rows="1" maxlength="2000" placeholder="问 LifeOS…"></textarea><button type="submit" class="button primary" id="prepare-button">发送</button>`;
composer.addEventListener('submit', (e)=>{
    e.preventDefault();
    aiOpen = true;
    excluded = [];
    void flow.prepare().then(scrollEnd);
    render();
});
const editor = composer.querySelector('textarea');
editor.addEventListener('input', ()=>flow.edit(editor.value));
editor.addEventListener('keydown', (e)=>{
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
        e.preventDefault();
        composer.requestSubmit();
    }
});
function render() {
    const focused = document.activeElement;
    const focusId = focused?.id;
    const start = focused?.selectionStart, end = focused?.selectionEnd;
    const mainScroll = document.getElementById('main')?.scrollTop;
    const scroll = document.getElementById('chat-scroll')?.scrollTop;
    const kept = [
        ...document.querySelectorAll('details[data-keep][open]')
    ].map((n)=>n.dataset.keep);
    const model = document.getElementById('model')?.value;
    composer.remove();
    document.getElementById('app').innerHTML = `<div class="app-shell"><nav class="icon-rail" aria-label="主导航"><span class="brand-mark">${icon('spark')}</span>${[
        'Today',
        'Me',
        'Contexts',
        'Memory'
    ].map((p)=>`<button class="rail-button" data-page="${p}" aria-label="${p}" data-tooltip="${p}" ${page === p ? 'aria-current="page"' : ''}>${icon(p.toLowerCase())}</button>`).join('')}<span class="rail-spacer"></span><button class="rail-button settings-button" data-page="Settings" aria-label="Settings" data-tooltip="Settings" ${page === 'Settings' ? 'aria-current="page"' : ''}>${icon('settings')}</button></nav><main id="main" tabindex="-1" class="workspace">${page === 'Settings' ? settingsPanel() : `<div class="page-wrap">${page === 'Today' ? today() : page === 'Memory' ? sourceMemory() : page === 'Me' ? header('我', '查看最近观察与已确认的长期信息。') + healthView(localSnapshot) + personalMemory() : header('上下文', '连接已有资料。') + sourcePanel()}</div>`}</main><aside id="ai-panel" class="ai-panel ${aiOpen ? 'open' : ''}" ${aiOpen ? '' : 'hidden'} aria-label="Global AI 对话"><div class="ai-panel-head"><div><h2>Global AI</h2><small>${mark()}</small></div><button class="close" data-action="close-ai" aria-label="关闭对话">${icon('close')}</button></div><div id="chat-scroll" class="chat-scroll">${conversation()}<div id="chat-status"></div></div><div id="panel-composer" class="ai-panel-composer"></div></aside><div class="composer" id="bottom-composer"></div></div>`;
    document.getElementById(aiOpen ? 'panel-composer' : 'bottom-composer').append(composer);
    if (editor.value !== flow.draft.text) editor.value = flow.draft.text;
    const prepare = composer.querySelector('button[type="submit"]');
    prepare.disabled = !flow.opened || flow.busy || busy;
    const status = flow.phase === 'restoring' ? '正在恢复本地会话…' : flow.phase === 'preparing' ? '准备发送内容…' : flow.phase === 'checking' ? '正在核对发送内容…' : flow.phase === 'sending' ? `发送中${real ? '' : '（合成）'}，请等待。` : flow.error ? error(flow.error) : notice;
    const statusHtml = `<p class="notice" role="status">${esc(status)}</p>${flow.phase === 'open-failed' ? button('open', '重试') : ''}${flow.opened && (!settings?.enabled || settings?.credentialState !== 'stored') ? '<button class="button ghost" data-action="configure">配置AI服务</button>' : ''}`;
    if (aiOpen) document.getElementById('chat-status').innerHTML = statusHtml;
    else document.getElementById('bottom-composer').insertAdjacentHTML('afterbegin', `<div class="composer-status">${statusHtml}</div>`);
    for (const n of document.querySelectorAll('details[data-keep]'))if (kept.includes(n.dataset.keep)) n.open = true;
    if (model) {
        const el = document.getElementById('model');
        if (el && [
            ...el.options
        ].some((o)=>o.value === model)) el.value = model;
    }
    if (scroll !== undefined && document.getElementById('chat-scroll')) document.getElementById('chat-scroll').scrollTop = scroll;
    if (mainScroll !== undefined && document.getElementById('main')) document.getElementById('main').scrollTop = mainScroll;
    if (focusId) {
        const target = document.getElementById(focusId);
        if (target) {
            target.focus({
                preventScroll: true
            });
            if (start != null && end != null && typeof target.setSelectionRange === 'function') try {
                target.setSelectionRange(start, end);
            } catch  {}
        }
    }
}
async function refresh() {
    const data = await app.read('source-chat');
    turns = data.turns;
    nextCursor = data.nextCursor;
    settings = await app.settings();
    sourceStatus = (await sourceCall('get_source_status')).connectors[0] || null;
    localSnapshot = await invoke('get_today', {
        request: {
            version: 2,
            operation: 'snapshot',
            payload: {}
        }
    });
}
async function act(a, id) {
    if (a === 'apple-open') {
        await apple.open();
        return;
    }
    if (a === 'apple-close') {
        apple.close();
        return;
    }
    if (a === 'apple-select') {
        await apple.choose(id);
        return;
    }
    if (a === 'apple-retry') {
        await apple.choose(apple.state.status.file);
        return;
    }
    if (a === 'open') {
        await flow.start();
        return;
    }
    if (a === 'preview') {
        aiOpen = true;
        excluded = [];
        await flow.prepareTurn(id);
        scrollEnd();
        return;
    }
    if (a === 'remove') {
        await flow.remove(id);
        return;
    }
    if (a === 'send') {
        await flow.confirm();
        scrollEnd();
        return;
    }
    if (a === 'cancel-preview') {
        await flow.cancel();
        return;
    }
    if (busy || flow.busy) return;
    const key = document.getElementById('key')?.value;
    const model = document.getElementById('model')?.value;
    const correctionText = document.getElementById('correction')?.value;
    busy = true;
    notice = '';
    render();
    try {
        if (a === 'next-page') {
            const data = await app.read('source-chat', nextCursor);
            turns.push(...data.turns);
            nextCursor = data.nextCursor;
        } else if (a === 'source-search') {
            if (sourceStatus) {
                sourceQuery = sourceQuery.trim();
                sourceRows = (await sourceCall('get_source_evidence', {
                    mode: 'search',
                    connectorId: sourceStatus.connectorId,
                    query: sourceQuery,
                    expectedGeneration: sourceStatus.grantGeneration
                })).results;
            }
        } else if (a === 'source-detail') {
            detail = await sourceCall('get_source_evidence', {
                mode: 'detail',
                connectorId: sourceStatus.connectorId,
                sourceRef: id,
                expectedVersion: sourceRows.find((r)=>r.sourceRef === id)?.version || sourceStatus.files.find((f)=>f.sourceRef === id).version
            });
        } else if (a === 'source-disconnect') {
            await sourceCall('control_source_job', {
                requestId: crypto.randomUUID(),
                connectorId: sourceStatus.connectorId,
                expectedGeneration: sourceStatus.grantGeneration,
                action: 'disconnect'
            });
            sourceRows = [];
            flow.invalidate();
            detail = null;
            await refresh();
        } else if (a === 'citation') {
            const s = JSON.parse(id);
            detail = await invoke('get_source_evidence', {
                request: {
                    version: 1,
                    payload: {
                        mode: 'detail',
                        connectorId: s.connectorId,
                        sourceRef: s.sourceRef,
                        expectedVersion: s.version
                    }
                }
            });
        } else if (a === 'correct') {
            correction = turns.find((t)=>t.answer?.answerId === id)?.answer;
        } else if (a === 'cancel-correction') {
            correction = null;
        } else if ([
            'save-correction',
            'helpful',
            'reject'
        ].includes(a)) {
            const target = a === 'save-correction' ? correction : turns.find((t)=>t.answer?.answerId === id)?.answer;
            const p = {
                requestId: crypto.randomUUID(),
                answerId: target.answerId,
                expectedAnswerRevision: target.revision,
                decision: a === 'save-correction' ? 'correct' : a
            };
            if (a === 'save-correction') {
                p.correctionText = correctionText;
                p.affectedCitationIds = [];
            }
            await app.call('decide_understanding_feedback', 'answer_feedback', p);
            correction = null;
            flow.invalidate();
            await refresh();
            notice = '反馈已保存。';
        } else {
            const p = {
                requestId: crypto.randomUUID(),
                profileId: 'deepseek-default'
            };
            if (a === 'save-key') {
                Object.assign(p, {
                    expectedCredentialRevision: settings.credentialRevision,
                    apiKey: key
                });
                await app.call('save_ai_provider_credential', 'replace_credential', p);
            } else if (a === 'test') {
                Object.assign(p, {
                    expectedCredentialRevision: settings.credentialRevision,
                    confirmation: 'test_deepseek_models_once'
                });
                const tested = await app.call('test_ai_provider_connection', 'test_connection', p);
                if (tested.state !== 'succeeded') throw {
                    code: tested.errorCode
                };
            } else if (a === 'recover') {
                Object.assign(p, {
                    expectedCredentialRevision: settings.credentialRevision,
                    confirmation: 'recover_owned_credential_operations'
                });
                await app.call('save_ai_provider_credential', 'recover_credentials', p);
            } else if (a === 'delete-key') {
                if (!confirm(real ? '删除此凭据并停用发送？' : '删除本任务合成凭据？')) return;
                Object.assign(p, {
                    expectedCredentialRevision: settings.credentialRevision,
                    confirmation: 'delete_this_credential'
                });
                await app.call('save_ai_provider_credential', 'delete_credential', p);
            } else if (a === 'select') {
                Object.assign(p, {
                    expectedProfileRevision: settings.profileRevision,
                    testReceiptId: settings.testReceiptId,
                    modelId: model
                });
                await app.call('save_ai_provider_settings', 'select_model', p);
            } else if (a === 'enable') {
                Object.assign(p, {
                    expectedProfileRevision: settings.profileRevision,
                    enabled: !settings.enabled
                });
                await app.call('set_ai_provider_enabled', 'set_enabled', p);
            }
            await refresh();
            notice = settings?.credentialState === 'cleanup_pending' ? '凭据操作尚未完成，请明确恢复；不会后台清理。' : '设置已保存。';
            flow.invalidate();
        }
    } catch (e) {
        notice = error(e);
    } finally{
        busy = false;
        render();
    }
}
function sourcePanel() {
    return `<section class="config-card"><p class="eyebrow">数据与隐私</p><h2>来源</h2><p>仅使用已导入资料；本地检索不会发送到云端。</p><p>${sourceStatus ? esc(sourceStatus.status) + ' · 正文已解析 ' + sourceStatus.parsed : '尚无已导入来源'}</p><button class="button secondary" disabled>重新扫描（本次会话未启用）</button>${sourceStatus?.status === 'active' ? button('source-disconnect', '断开来源', '', true) : ''}<p>断开保留历史，旧预览失效。不会获取目录外文件、网页或未解析附件。</p></section>`;
}
function sourceMemory() {
    return `<header><div><p class="eyebrow">Memory · 来源与引用</p><h1>找回原文依据</h1><p>检索结果是已导入原文，不等于AI理解或用户确认事实。</p></div></header><section class="config-card"><label>本地检索<input id="source-query" value="${esc(sourceQuery)}" placeholder="例如：纸鹤项目"></label>${button('source-search', '检索来源')}${sourceRows.map((r)=>`<article class="record"><div><p>${esc(r.text)}</p><small>原始来源 · v${r.version} · ${esc(r.locator)}</small></div>${button('source-detail', '查看原文依据', r.sourceRef, true)}</article>`).join('') || '<p>当前没有检索结果。</p>'}</section>${detail ? `<section class="config-card"><h2>${esc(detail.title || '已导入来源')} · v${detail.version}</h2>${detail.segments.map((s)=>`<small>${esc(s.locator)}</small><pre class="source-original">${esc(s.text)}</pre>`).join('')}</section>` : ''}${healthView(localSnapshot, true)}${personalMemory()}`;
}
function personalMemory() {
    return `<section class="config-card"><h2>已确认长期信息</h2>${(localSnapshot?.memories || []).filter((m)=>m.status === 'active').map((m)=>`<p>${esc(m.statement)} · 用户明确确认</p>`).join('') || '<p>还没有已确认长期信息。</p>'}<h2>当前状态</h2>${(localSnapshot?.states || []).filter((s)=>s.status === 'active').map((s)=>`<p>${esc(s.stateKey)} · ${esc(s.value)}</p>`).join('') || '<p>没有当前有效状态。</p>'}<p>问题、模型回答和纠正不会自动写成长期事实。</p></section>`;
}
function scrollEnd() {
    requestAnimationFrame(()=>{
        const el = document.getElementById('chat-scroll');
        if (el) el.scrollTop = el.scrollHeight;
    });
}
document.addEventListener('input', (e)=>{
    const t = e.target;
    if (t.id === 'source-query') sourceQuery = t.value;
    if (t.id === 'correction') correctionText = t.value;
});
document.addEventListener('click', (e)=>{
    const b = e.target.closest('button');
    if (!b) return;
    if (b.dataset.page) {
        page = b.dataset.page;
        aiOpen = false;
        render();
        window.scrollTo(0, 0);
    } else if (b.dataset.settings) {
        settingsSection = b.dataset.settings;
        render();
    } else if (b.dataset.action === 'open-ai' || b.dataset.action === 'return-ai') {
        aiOpen = true;
        render();
        editor.focus();
        scrollEnd();
    } else if (b.dataset.action === 'close-ai') {
        aiOpen = false;
        render();
        document.getElementById('main')?.focus();
    } else if (b.dataset.action === 'configure') {
        page = 'Settings';
        settingsSection = '模型设置';
        aiOpen = false;
        render();
    } else if (b.dataset.action) void act(b.dataset.action, b.dataset.id || '');
});
document.addEventListener('keydown', (e)=>{
    if (e.key === 'Escape' && aiOpen) {
        aiOpen = false;
        render();
        document.getElementById('main')?.focus();
    }
});
render();
void flow.start().then(()=>apple.restore()).then(()=>render());
setInterval(()=>void apple.poll(), 500);
let healthPolling = false, healthSignature = '';
setInterval(async ()=>{
    if (real || healthPolling || !flow.opened || apple.state.status.status === 'running') return;
    healthPolling = true;
    try {
        const next = await invoke('get_today', {
            request: {
                version: 2,
                operation: 'snapshot',
                payload: {}
            }
        });
        const signature = JSON.stringify([
            next.states,
            next.sources,
            Math.floor(Date.now() / 60000)
        ]);
        localSnapshot = next;
        if (signature !== healthSignature && !aiOpen && !busy && !flow.busy && (page === 'Me' || page === 'Memory' || page === 'Settings' && settingsSection === '数据与隐私')) {
            healthSignature = signature;
            render();
        }
    } catch  {} finally{
        healthPolling = false;
    }
}, 3000);
