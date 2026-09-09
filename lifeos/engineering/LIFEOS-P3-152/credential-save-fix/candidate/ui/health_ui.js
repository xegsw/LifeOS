import { SettingsActions } from './settings_actions.js';
import { SourcesController, sourcesView } from './sources_view.js';
import { Controller as HealthView, content as healthContent } from './health_aux.js';
import { settingsView, settingView, proposedSettings, updatePolicy } from './settings_view.js';
import { ControlledConversation, ControlledFlow } from './controlled_conversation.js';
import { icon } from './source_icons.js';
const invoke = window.__TAURI__.core.invoke;
const app = new ControlledConversation({
    invoke: (c, r)=>invoke(c, new TextEncoder().encode(JSON.stringify(r)))
});
const esc = (s)=>String(s ?? '').replace(/[&<>"']/g, (c)=>({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[c]);
let page = 'Today', aiOpen = false, notice = '';
let healthView = null;
function closeHealth() {
    healthView?.dispose();
    healthView = null;
}
function openHealth() {
    closeHealth();
    page = 'HealthSource';
    const c = new HealthView((r)=>invoke('get_today', new TextEncoder().encode(JSON.stringify(r))), ()=>{
        if (page === 'HealthSource' && healthView === c) render();
    });
    c.real = flow.snapshot?.mode === 'real';
    healthView = c;
    void c.initialize();
}
const flow = new ControlledFlow(app, ()=>render());
const settingsActions = new SettingsActions(flow, ()=>render());
const sources = new SourcesController((c, r)=>invoke(c, new TextEncoder().encode(JSON.stringify(r))), ()=>render());
function openSources() {
    void sources.start();
}
const button = (action, label, id = '')=>`<button type="button" class="button secondary" data-action="${action}" data-id="${esc(id)}">${label}</button>`;
const title = (name, sub)=>`<header class="page-head"><div><h1>${name}</h1><p class="subhead">${sub}</p></div></header>`;
const label = (s)=>s.stateKey === 'available_time' ? `可用时间 · ${s.value} 分钟` : `自述睡眠 · ${s.value} 小时`;
const navLabel = (p)=>({
        Today: '今日',
        Me: '我',
        Contexts: '上下文',
        Memory: '记忆',
        Settings: '设置'
    })[p] || p;
const date = (v)=>new Date(v).toLocaleDateString('zh-CN');
function body() {
    const s = flow.snapshot;
    if (page === 'Sources') return '<div class="page-wrap">' + title('资料来源', '原文按需查看，引用在发送前由你确认。') + sourcesView(sources, s?.mode === 'real') + '</div>';
    if (page === 'HealthSource' && healthView) return '<div class="health-aux"><div class="page-wrap">' + button('health-back', '返回我') + healthContent(healthView) + '</div></div>';
    if (page === 'Settings') return settingsView(s, esc, button, sourcesView(sources, s?.mode === 'real'), settingsActions);
    if (page === 'Me') return `<div class="page-wrap">${title('我', '你的明确表达，形成有时效的当前状态。')}<section class="panel"><h2>当前状态</h2>${s?.states?.length ? s.states.map((st)=>`<article class="record"><strong>${esc(label(st))}</strong><p class="quiet">${st.domain === 'health' ? '健康' : '工作'} · 用户${st.identity === 'user_self_report' ? '自述' : '明确表达'} · 有效至 ${new Date(st.validUntil).toLocaleString('zh-CN')}</p><p class="verbatim">${esc(st.rawText)}</p></article>`).join('') : '<p class="quiet">还没有当前状态。你可以在对话中说明或纠正。</p>'}<p class="tiny">这些短期状态不会自动成为长期记忆；自述不替代来源中的观察。</p>${button('health-open', '查看健康来源')}</section></div>`;
    if (page === 'Memory') return `<div class="page-wrap">${title('记忆', '已确认的长期信息，与临时对话分开保留。')}${button('source-browser', '浏览来源原文')}<section class="panel">${(s?.memories || []).map((m)=>`<article class="record"><small>已确认记忆${s?.mode === 'real' ? '' : ' · 合成资料'}</small><p>${esc(m.text)}</p></article>`).join('')}<p class="tiny">普通回答只作为 AI 候选内容保存，不会自动写入这里。</p></section></div>`;
    if (page === 'Contexts') return `<div class="page-wrap">${title('上下文', '相关资料随问题进入对话。')}<section class="panel"><p>直接提问即可。回答下的“查看依据”会展示本次用到的${s?.mode === 'real' ? '健康来源' : '合成来源'}和用户表达。</p><p class="quiet">本页面没有独立的上下文编辑功能。</p>${button('open-ai', '开始对话')}${button('source-browser', '查看资料来源')}</section></div>`;
    return `<div class="page-wrap"><section class="today-page"><header class="today-hero"><div><h1>你好。</h1><p class="today-subhead">给今天留一点从容。</p></div><div class="today-chrome"><span>${new Intl.DateTimeFormat('zh-CN', {
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    }).format(new Date())}</span>${icon('calendar')}</div></header><section class="state-empty conversation-empty"><strong>从你现在想聊的事开始。</strong><span>一个想法，一件待办，或今天的感受。</span><div class="actions">${button('open-ai', '与 LifeOS 聊聊')}</div></section>${s?.mode === 'real' ? '' : '<p class="preview-label">合成预览 · 未联网</p>'}</section></div>`;
}
function chat() {
    const s = flow.snapshot;
    return `${s?.hasMore ? '<p class="tiny">显示最近的有限对话，较早记录仍在本地保留。</p>' : ''}${!s?.turns?.length ? '<p class="quiet">说说你想了解什么。</p>' : ''}${(s?.turns || []).map((t)=>{
        const q = s.questions.find((q)=>q.id === t.clarificationId && q.status === 'pending');
        return `<article class="turn"><div class="ai-question"><small>你的原始表达</small><p class="verbatim">${esc(t.text)}</p></div><div class="ai-answer"><small>${t.answer?.startsWith('本地') ? '本地处理' : 'AI 候选回答'}${t.status === 'stale' ? ' · 旧依据已失效，保留历史' : ''}</small><p class="verbatim">${esc(t.answer)}</p>${t.refs.length ? `<details data-keep="${esc(t.turnId)}"><summary>查看依据 · ${t.refs.length} 条</summary>${t.refs.map((r)=>`<article class="record"><small>${r.identity === 'source_projection' ? r.engineRef ? '资料来源' : s?.mode === 'real' ? '健康来源' : '合成来源' : r.identity === 'health_conversation_expression' ? '用户明确表达' : '已确认记忆'}${r.observedAt ? ` · ${date(r.observedAt)}` : ''}${r.estimated ? ' · 估计值' : ''}</small><p class="verbatim">${esc(r.text)}</p></article>`).join('')}</details>` : ''}${q ? `<div class="form-actions">${button('defer', '稍后再说', q.id)}${button('ignore', '忽略这个问题', q.id)}</div>` : ''}</div></article>`;
    }).join('')}`;
}
function errorText(e) {
    const messages = {
        source_context_stale: '来源已更新或撤权，请重新准备。',
        health_import_busy: '健康文件正在导入，请完成后再查看。',
        source_real_permission_required: '此版本尚未获准处理该来源，请先确认范围。',
        provider_not_enabled: '当前主服务尚未接入发送。请在模型设置中选择可用的服务。',
        catalog_model_conflict: '主服务与模型设置不一致，请重新保存配置。',
        catalog_revision_conflict: '设置已在其他操作中更改，请重新打开设置后保存。',
        credential_missing: '请先在模型设置中保存凭据并选择模型。',
        credential_invalid: '凭据格式不正确，请在设置中检查。',
        credential_authentication_failed: '本地凭据无法解密，请在设置中重新保存。',
        provider_authentication: '服务拒绝了凭据。草稿已保留，请检查设置。',
        provider_model: '服务不接受所选模型。请在设置中选择后重新准备。',
        provider_timeout: '请求超时，是否已发送无法确认。草稿保留；重试需要新的披露确认。',
        provider_network: '连接中断，是否已发送无法确认。草稿保留；重试需要新的披露确认。',
        dispatch_outcome_unknown: '结果尚未确认，不会自动重发。草稿已保留。',
        preview_stale: '内容或设置已变化，请重新准备披露。',
        context_stale: '来源或上下文已变化，请重新准备。',
        provider_unavailable: '服务暂不可用。草稿已保留，请手动重试。',
        context_budget_rejected: '相关内容过长，请收窄问题。',
        provider_response_rejected: '服务回答未通过本地检查，草稿已保留。'
    };
    return messages[e?.code] || '操作未完成，草稿已保留。';
}
function disclosure() {
    const v = flow.preview;
    if (!v) return '';
    return `<section class="confirmation" aria-label="本次发送预览"><h3>发送前，请看一下</h3><p>接收方：DeepSeek · ${esc(v.modelId)}</p><small>${flow.snapshot?.mode === 'real' ? '确认后发送给DeepSeek' : '合成演练，未联网'} · 本次只包含下方问题与 ${v.items.length} 条依据</small><h3>你的问题</h3><p class="verbatim">${esc(v.question)}</p>${!v.items.some((i)=>i.identity === '来源观察' && i.domain === 'health') ? '<p>本次没有健康来源观察，不会声称使用了健康依据。</p>' : ''}${v.items.map((i)=>`<article class="record"><small>${esc(i.citationId)} · ${esc(i.identity)}</small><p class="verbatim">${esc(i.text)}</p></article>`).join('')}<details data-keep="instructions"><summary>查看发送说明与完整内容</summary><p class="verbatim">${esc(v.instructions)}</p><small>${esc(v.recipient)}</small><pre class="source-original">${esc(v.exactBody)}</pre></details><div class="form-actions"><button class="button primary" data-action="confirm" ${flow.busy ? 'disabled' : ''}>${flow.snapshot?.mode === 'real' ? '确认发送给DeepSeek' : '确认演练发送'}</button>${button('cancel', '取消')}</div></section>`;
}
const composer = document.createElement('form');
composer.className = 'question-form';
composer.innerHTML = `<button type="button" class="ai-launch" data-action="open-ai" aria-label="与 LifeOS 对话">${icon('spark')}</button><label class="sr-only" for="conversation">自然提问</label><textarea id="conversation" maxlength="2000" rows="1" placeholder="问 LifeOS…"></textarea><button type="submit" class="button primary">发送</button>`;
const editor = composer.querySelector('textarea');
composer.addEventListener('submit', (e)=>{
    e.preventDefault();
    aiOpen = true;
    void flow.prepare().then(scrollEnd);
    render();
});
editor.addEventListener('input', ()=>flow.edit(editor.value));
editor.addEventListener('keydown', (e)=>{
    if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
        e.preventDefault();
        composer.requestSubmit();
    }
});
function scrollEnd() {
    const el = document.getElementById('chat-scroll');
    if (el) el.scrollTop = el.scrollHeight;
}
function render() {
    const key = document.getElementById('key');
    const keyFocused = document.activeElement === key;
    const focus = document.activeElement === editor, start = editor.selectionStart, end = editor.selectionEnd;
    const scroll = document.getElementById('chat-scroll')?.scrollTop;
    const kept = [
        ...document.querySelectorAll('details[data-keep][open]')
    ].map((v)=>v.dataset.keep);
    composer.remove();
    document.getElementById('app').innerHTML = `<div class="app-shell"><nav class="icon-rail" aria-label="主导航"><span class="brand-mark">${icon('spark')}</span>${[
        'Today',
        'Me',
        'Contexts',
        'Memory'
    ].map((p)=>`<button class="rail-button" data-page="${p}" aria-label="${navLabel(p)}" data-tooltip="${navLabel(p)}" ${page === p ? 'aria-current="page"' : ''}>${icon(p.toLowerCase())}</button>`).join('')}<span class="rail-spacer"></span><button class="rail-button settings-button" data-page="Settings" aria-label="设置" data-tooltip="设置">${icon('settings')}</button></nav><main id="main" tabindex="-1" class="workspace">${body()}</main><aside class="ai-panel ${aiOpen ? 'open' : ''}" ${aiOpen ? '' : 'hidden'} aria-label="Global AI 对话"><div class="ai-panel-head"><div><h2>与 LifeOS 对话</h2><small>${flow.snapshot?.mode === 'real' ? '' : '合成预览 · '}${esc(flow.snapshot?.provider?.modelId || '从一个问题开始')}</small></div><button class="close" data-action="close-ai" aria-label="关闭对话">${icon('close')}</button></div><div class="chat-scroll" id="chat-scroll">${chat()}${disclosure()}<div id="chat-status"></div></div><div class="ai-panel-composer" id="panel-composer"></div></aside><div class="composer" id="bottom-composer"></div></div>`;
    const nextKey = document.getElementById('key');
    if (key && nextKey && !key.disabled && !nextKey.disabled) {
        nextKey.replaceWith(key);
        if (keyFocused) key.focus();
    }
    document.getElementById(aiOpen ? 'panel-composer' : 'bottom-composer').append(composer);
    if (editor.value !== flow.draft.text) editor.value = flow.draft.text;
    composer.querySelector('[type=submit]').disabled = !flow.opened || flow.busy;
    const status = flow.phase === 'restoring' ? '正在恢复本地会话…' : flow.phase === 'preparing' ? '正在本地筛选相关内容…' : flow.busy ? flow.snapshot?.mode === 'real' ? '正在等待DeepSeek回答…' : '正在进行合成发送…' : flow.phase === 'cancelled' ? flow.notice : flow.error ? errorText(flow.error) : notice;
    const html = `<p class="notice" role="status">${esc(status)}</p>${flow.busy ? button('cancel', '取消') : flow.phase === 'failed' ? button('retry', '重新准备披露') : flow.phase === 'open-failed' ? button('restore', '重试恢复') : ''}`;
    if (aiOpen) document.getElementById('chat-status').innerHTML = html;
    else {
        const n = document.createElement('div');
        n.className = 'composer-status';
        n.innerHTML = html;
        document.getElementById('bottom-composer').prepend(n);
    }
    document.querySelectorAll('details[data-keep]').forEach((n)=>{
        n.open = kept.includes(n.dataset.keep);
    });
    if (scroll !== undefined) document.getElementById('chat-scroll').scrollTop = scroll;
    if (focus) {
        editor.focus();
        editor.setSelectionRange(start, end);
    }
}
document.addEventListener('click', async (e)=>{
    const b = e.target.closest('button');
    if (!b || b.disabled) return;
    const p = b.dataset.page, a = b.dataset.action, id = b.dataset.id || '';
    try {
        if (p) {
            closeHealth();
            sources.dispose();
            page = p;
            aiOpen = false;
            if (p === 'Settings' && settingView.section === '数据与隐私') openSources();
        }
        if (a === 'source-browser') {
            closeHealth();
            page = 'Sources';
            aiOpen = false;
            openSources();
            render();
            return;
        }
        if (a === 'source-ask') {
            sources.dispose();
            const question = '请根据我的来源资料，说明' + sources.query + '的相关内容。';
            flow.edit(flow.draft.text ? flow.draft.text + '\n' + question : question);
            aiOpen = true;
            render();
            editor.focus();
            return;
        }
        if (a?.startsWith('source-') || a?.startsWith('apple-')) {
            await sources.action(a, id);
            render();
            return;
        }
        if (a === 'health-open') {
            openHealth();
        }
        if (a === 'health-back') {
            closeHealth();
            page = 'Me';
        }
        if (page === 'HealthSource' && healthView && b.closest('.health-aux')) {
            const c = healthView;
            if (a === 'overview-retry') void c.initialize();
            if (a === 'details') {
                c.detailsOpen = !c.detailsOpen;
                if (!c.detailsOpen) c.trendOpen = false;
            }
            if (a === 'trend') c.trendOpen = !c.trendOpen;
            if (a === 'latest') void c.load({
                endDay: undefined
            });
            if (a === 'retry') {
                void c.load();
                render();
                return;
            }
            if (a === 'groups-prev') void c.load({
                groupPage: Math.max(0, c.data.groupPage - 1)
            });
            if (a === 'groups-next') void c.load({
                groupPage: c.data.nextGroupPage
            });
        }
        if (a === 'settings-mode') {
            settingView.mode = id;
        }
        if (a === 'settings-section') {
            sources.dispose();
            settingView.section = id;
            if (id === '数据与隐私') openSources();
        }
        if (a === 'open-ai') {
            aiOpen = true;
        }
        if (a === 'close-ai') aiOpen = false;
        if (a === 'cancel') await flow.cancel();
        if (a === 'retry') await flow.prepare();
        if (a === 'restore') await flow.start();
        if (a === 'confirm') await flow.confirm();
        if (a === 'save-catalog') await settingsActions.save('catalog', document.getElementById('key'), proposedSettings(flow.snapshot));
        if (a === 'select-model') await flow.selectModel(document.getElementById('model').value);
        if (a === 'save-key') await settingsActions.save('credential', document.getElementById('key'), null);
        if (a === 'delete-key') await settingsActions.save('delete', null, null);
        if (a === 'ignore' || a === 'defer') await flow.decide(id, a);
        render();
        if (a === 'open-ai') {
            editor.focus();
            scrollEnd();
        }
    } catch  {
        notice = '操作未完成，请重试。';
        render();
    }
});
document.addEventListener('change', (e)=>{
    const n = e.target;
    if (page === 'HealthSource' && healthView) {
        const c = healthView;
        if (n.id === 'metric') void c.load({
            metric: n.value,
            source: undefined,
            offset: undefined,
            endDay: undefined,
            groupPage: 0
        });
        if (n.id === 'days') void c.load({
            days: Number(n.value)
        });
        if (n.id === 'end-day' && n.value) void c.load({
            endDay: Math.floor(Date.parse(n.value + 'T00:00:00Z') / 86400000)
        });
        if (n.id === 'source' && n.value !== 'selected') {
            const g = c.data.groups[Number(n.value)];
            if (g) void c.load({
                source: g.source,
                offset: g.offset,
                endDay: undefined
            });
        }
    }
    if (n.dataset.policy) {
        updatePolicy(n.dataset.policy, n.checked, flow.snapshot);
        render();
    }
    if (n.id === 'provider-choice') {
        settingView.drafts[settingView.mode].provider = n.value;
        render();
    }
});
document.addEventListener('input', (e)=>{
    const n = e.target;
    if (n.id === 'source-query') sources.query = n.value;
    if (n.id === 'model') settingView.drafts[settingView.mode].model = n.value;
});
render();
void flow.start();
