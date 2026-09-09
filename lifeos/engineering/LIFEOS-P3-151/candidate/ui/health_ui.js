import { HealthConversation, HealthFlow } from './health_conversation.js';
import { icon } from './source_icons.js';
const invoke = window.__TAURI__.core.invoke;
const app = new HealthConversation({
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
const flow = new HealthFlow(app, ()=>render());
const button = (action, label, id = '')=>`<button type="button" class="button secondary" data-action="${action}" data-id="${esc(id)}">${label}</button>`;
const title = (name, sub)=>`<header class="page-head"><div><h1>${name}</h1><p class="subhead">${sub}</p></div></header>`;
const label = (s)=>s.stateKey === 'available_time' ? `可用时间 · ${s.value} 分钟` : `自述睡眠 · ${s.value} 小时`;
const date = (v)=>new Date(v).toLocaleDateString('zh-CN');
function body() {
    const s = flow.snapshot;
    if (page === 'Settings') return `<div class="settings-shell"><nav class="settings-nav" aria-label="设置导航"><p>设置</p><button aria-current="page">模型设置</button></nav><div class="settings-content">${title('模型设置', '选择这次合成演练使用的离线测试模型。')}<section class="service-card"><div><p class="eyebrow">当前模型</p><h2>离线测试 ${s?.modelId === 'OfflineB' ? 'B' : 'A'}</h2><p>合成演练 · 本机运行</p></div><span class="state-dot success">可用</span></section><section class="config-card"><h2>测试模型</h2><p class="quiet">两种适配器共用已有来源、对话和记忆。切换后可以继续提问。</p><div class="form-actions">${button('model', '使用离线测试 A', 'OfflineA')}${button('model', '使用离线测试 B', 'OfflineB')}</div></section><p class="usage-help">此模式用有限规则验证交互与数据链路，不具备开放域推理能力。所有内容均为合成资料。</p>${button('open-ai', '返回对话')}</div></div>`;
    if (page === 'Me') return `<div class="page-wrap">${title('我', '你的明确表达，形成有时效的当前状态。')}<section class="panel"><h2>当前状态</h2>${s?.states?.length ? s.states.map((st)=>`<article class="record"><strong>${esc(label(st))}</strong><p class="quiet">${st.domain === 'health' ? '健康' : '工作'} · 用户${st.identity === 'user_self_report' ? '自述' : '明确表达'} · 有效至 ${new Date(st.validUntil).toLocaleString('zh-CN')}</p><p class="verbatim">${esc(st.rawText)}</p></article>`).join('') : '<p class="quiet">还没有当前状态。你可以在对话中说明或纠正。</p>'}<p class="tiny">这些短期状态不会自动成为长期记忆；自述不替代来源中的观察。</p></section></div>`;
    if (page === 'Memory') return `<div class="page-wrap">${title('记忆', '已确认的长期信息，与临时对话分开保留。')}<section class="panel">${(s?.memories || []).map((m)=>`<article class="record"><small>已确认记忆 · 合成资料</small><p>${esc(m.text)}</p></article>`).join('')}<p class="tiny">普通回答只作为 AI 候选内容保存，不会自动写入这里。</p></section></div>`;
    if (page === 'Contexts') return `<div class="page-wrap">${title('上下文', '相关资料随问题进入对话。')}<section class="panel"><p>直接提问即可。回答下的“查看依据”会展示本次用到的合成来源和用户表达。</p><p class="quiet">此演练没有独立的上下文编辑功能。</p>${button('open-ai', '开始对话')}</section></div>`;
    return `<div class="page-wrap"><section class="today-page"><div class="today-hero"><div><h1>你好。</h1><p class="today-subhead">给今天留一点从容。</p></div><div class="today-chrome"><span>${new Intl.DateTimeFormat('zh-CN', {
        month: 'long',
        day: 'numeric',
        weekday: 'long'
    }).format(new Date())}</span>${icon('calendar')}</div></div><span class="synthetic-mark">合成演练 · 未联网</span><div class="today-grid"><section class="panel"><div class="section-head"><h2>从一个问题开始</h2>${icon('spark')}</div><p class="quiet">理清下一步，也给自己的状态留一点空间。</p><p>你可以问“根据我的健康记录，怎么安排活动？”</p><p class="tiny">直接输入问题，相关依据会在回答中按需展开。</p>${button('open-ai', '打开对话')}</section></div><p class="usage-help">这里使用合成来源和离线测试模型，验证有限的对话流程。</p></section></div>`;
}
function chat() {
    const s = flow.snapshot;
    return `${s?.hasMore ? '<p class="tiny">显示最近的有限对话，较早记录仍在本地保留。</p>' : ''}${!s?.turns?.length ? '<p class="quiet">说说你想了解什么。</p>' : ''}${(s?.turns || []).map((t)=>{
        const q = s.questions.find((q)=>q.id === t.clarificationId && q.status === 'pending');
        return `<article class="turn"><div class="ai-question"><small>你的原始表达</small><p class="verbatim">${esc(t.text)}</p></div><div class="ai-answer"><small>AI 候选回答${t.status === 'stale' ? ' · 旧依据已失效，保留历史' : ''}</small><p class="verbatim">${esc(t.answer)}</p>${t.refs.length ? `<details data-keep="${esc(t.turnId)}"><summary>查看依据 · ${t.refs.length} 条</summary>${t.refs.map((r)=>`<article class="record"><small>${r.identity === 'source_projection' ? '合成来源' : r.identity === 'health_conversation_expression' ? '用户明确表达' : '已确认记忆'}${r.observedAt ? ` · ${date(r.observedAt)}` : ''}${r.estimated ? ' · 估计值' : ''}</small><p class="verbatim">${esc(r.text)}</p></article>`).join('')}</details>` : ''}${q ? `<div class="form-actions">${button('defer', '稍后再说', q.id)}${button('ignore', '忽略这个问题', q.id)}</div>` : ''}</div></article>`;
    }).join('')}`;
}
const composer = document.createElement('form');
composer.className = 'question-form';
composer.innerHTML = `<button type="button" class="ai-launch" data-action="open-ai" aria-label="Global AI">${icon('spark')}</button><label class="sr-only" for="conversation">自然提问</label><textarea id="conversation" maxlength="2000" rows="1" placeholder="问 LifeOS…"></textarea><button type="submit" class="button primary">发送</button>`;
const editor = composer.querySelector('textarea');
composer.addEventListener('submit', (e)=>{
    e.preventDefault();
    aiOpen = true;
    void flow.send().then(scrollEnd);
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
    ].map((p)=>`<button class="rail-button" data-page="${p}" aria-label="${p}" ${page === p ? 'aria-current="page"' : ''}>${icon(p.toLowerCase())}</button>`).join('')}<span class="rail-spacer"></span><button class="rail-button settings-button" data-page="Settings" aria-label="Settings">${icon('settings')}</button></nav><main id="main" tabindex="-1" class="workspace">${body()}</main><aside class="ai-panel ${aiOpen ? 'open' : ''}" ${aiOpen ? '' : 'hidden'} aria-label="Global AI 对话"><div class="ai-panel-head"><div><h2>Global AI</h2><small>合成演练 · 离线测试 ${flow.snapshot?.modelId === 'OfflineB' ? 'B' : 'A'}</small></div><button class="close" data-action="close-ai" aria-label="关闭对话">${icon('close')}</button></div><div class="chat-scroll" id="chat-scroll">${chat()}<div id="chat-status"></div></div><div class="ai-panel-composer" id="panel-composer"></div></aside><div class="composer" id="bottom-composer"></div></div>`;
    document.getElementById(aiOpen ? 'panel-composer' : 'bottom-composer').append(composer);
    if (editor.value !== flow.draft.text) editor.value = flow.draft.text;
    composer.querySelector('[type=submit]').disabled = !flow.opened || flow.busy;
    const status = flow.phase === 'restoring' ? '正在恢复本地会话…' : flow.busy ? '正在生成合成回答…' : flow.phase === 'cancelled' ? '已取消，草稿保留。' : flow.error ? flow.error.code === 'offline_test_failure' ? '这次合成生成失败，草稿已保留。' : '这次操作未完成，草稿已保留。' : notice;
    const html = `<p class="notice" role="status">${esc(status)}</p>${flow.busy ? button('cancel', '取消') : flow.phase === 'failed' ? button('retry', '重试') : flow.phase === 'open-failed' ? button('restore', '重试恢复') : ''}`;
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
    if (!b) return;
    const p = b.dataset.page, a = b.dataset.action, id = b.dataset.id || '';
    try {
        if (p) {
            page = p;
            aiOpen = false;
        }
        if (a === 'open-ai') {
            aiOpen = true;
        }
        if (a === 'close-ai') aiOpen = false;
        if (a === 'cancel') await flow.cancel();
        if (a === 'retry') await flow.send();
        if (a === 'restore') await flow.start();
        if (a === 'model') await flow.select(id);
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
render();
void flow.start();
