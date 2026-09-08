import { Application, validRows, currentStates, uid } from './core.js';
const tauri = window.__TAURI__.core;
const app = new Application({
    invoke: async (ipc, request)=>{
        try {
            return await tauri.invoke(ipc, {
                request
            });
        } catch (e) {
            throw new Error(e.code || String(e));
        }
    }
});
let page = 'Today', snapshot, question, packet, notice = '', busy = false, model = 'OfflineA';
let draft = {
    id: 'draft:' + uid(),
    turnId: uid(),
    requestId: uid(),
    observedAt: Date.now(),
    text: '',
    revision: 0
};
let intent = 'record';
let editing = null;
let queue = Promise.resolve();
const escape = (s)=>String(s ?? '').replace(/[&<>"']/g, (c)=>({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[c]);
const icons = {
    Today: '◉',
    Me: '♙',
    Contexts: '▦',
    Memory: '◇',
    Settings: '⚙'
};
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
function btn(action, label, id = '', secondary = false) {
    return `<button class="button ${secondary ? 'secondary' : 'primary'}" data-action="${action}" data-id="${escape(id)}" ${busy ? 'disabled' : ''}>${label}</button>`;
}
let sourceStatus = null, sourceMatches = [], sourceDetail = null, sourceQuery = '', disconnectPending = false;
const stateLabels = {
    active: '已连接',
    paused: '已暂停，可继续',
    cancelled: '已取消，可刷新',
    disconnected: '已断开',
    parsed: '正文已解析',
    restricted: '配置受限，不参与上下文',
    unparsed: '原件已接入，正文未解析',
    pending: '待处理',
    awaiting_target_grant: '等待目标授权',
    fetch_pending: '正在获取',
    fetched: '目标正文已获取',
    revoked: '已撤权',
    missing: '原件已缺失',
    available: '原文可用',
    local_original_linked: '目录内原件已关联',
    parent_stale: '父来源已更新，需重新授权',
    target_missing: '目标已缺失'
};
const reasonLabels = {
    unsupported_encoding: '编码不受支持；请保留原件并改用 UTF-8 后刷新',
    original_only: '原件已保存；当前不提供正文解析',
    configuration_excluded: '配置内容仅受限保存在本地',
    parse_memory_budget: '解析超出内存预算，原件保留',
    parse_timeout: '解析超时，可稍后刷新',
    ocr_required: '需要 OCR，当前尚未启用',
    encrypted_document: '文档已加密，当前不解密',
    damaged_document: '文档损坏或格式不受支持',
    directory_changed_refresh_required: '扫描期间目录发生变化，请刷新',
    root_identity_changed: '来源目录身份变化，请断开后重新连接',
    cursor_stale: '依据已更新，请重新打开',
    authorization_rejected: '来源授权已失效',
    grant_or_worker_stale: '来源状态已变化，请重试'
};
function sourceReason(code) {
    return reasonLabels[code] || '当前无法完成，请刷新后重试。';
}
function sourceState(code) {
    return stateLabels[code] || (String(code).startsWith('unavailable:') ? '目标暂不可用，请核对授权后重试' : '待处理');
}
function sourcePanel() {
    const c = sourceStatus;
    return `<section class="config-card"><p class="eyebrow">数据与隐私</p><h2>来源</h2><p>连接任务内合成目录后，自动接入笔记、配置和附件。真实目录接入尚未开放。</p>${!c ? btn('source-connect', '连接合成目录') : `<p role="status">${escape(stateLabels[c.status] || c.status)} · 已发现 ${c.discovered} · 已处理 ${c.processed} · 正文已解析 ${c.parsed} · 未解析或受限 ${c.unparsed} · 失败 ${c.failed} · 待处理 ${c.pending}</p><p>${c.error ? '处理中断：' + escape(sourceReason(c.error)) : !c.scanComplete || c.pending ? '正在分批处理；未完成全量接入。' : c.failed || c.unparsed ? '处理已结束，存在未解析或受限原件。' : '本轮扫描与导入完成。'}</p><div class="form-actions">${btn('source-refresh', '刷新', '', true)}${btn(c.status === 'paused' ? 'source-resume' : 'source-pause', c.status === 'paused' ? '继续' : '暂停', '', true)}${btn('source-cancel', '取消处理', '', true)}${btn('source-disconnect', '断开来源', '', true)}</div>${disconnectPending ? `<p>断开后，来源与外链退出检索，旧上下文失效；历史保留。</p>${btn('source-confirm-disconnect', '确认断开')}${btn('source-keep', '保留连接', '', true)}` : ''}<details><summary>查看原件处理状态</summary><small>此处最多显示 256 项；扫描和导入覆盖全部来源，未解析项保留状态。</small>${c.files.map((f)=>`<p>${escape(f.title)} · ${escape(stateLabels[f.status] || f.status)} · v${f.version} ${f.reason ? ' · ' + escape(sourceReason(f.reason)) : ''} ${btn('source-detail', '依据', f.sourceRef, true)}</p>`).join('')}</details><details><summary>直接引用的目标</summary>${c.links.map((l)=>`<p>${escape(l.target)} · ${escape(sourceState(l.status))}</p>${l.status === 'local_original_linked' ? '' : `<div class="form-actions">${btn('source-grant', '授权此合成目标', l.linkId, true)}${btn('source-revoke', '撤回目标授权', l.linkId, true)}</div>`}`).join('') || '<p>尚无引用目标。</p>'}</details>`}</section>`;
}
function sourceMemory() {
    return `<section class="config-card"><h2>来源与引用</h2><p>检索结果是原文依据，不代表 AI 已理解，也不是已确认长期信息。</p><label>本地检索<input id="source-query" value="${escape(sourceQuery)}" placeholder="例如：项目计划"></label>${btn('source-search', '检索来源')}<div>${sourceMatches.map((r)=>`<article class="record"><div><p>${escape(r.text)}</p><small>原始来源 · v${r.version} · ${escape(r.locator)}</small></div>${btn('source-detail', '查看原文依据', r.sourceRef, true)}</article>`).join('') || '<p>当前没有检索结果。</p>'}</div>${sourceDetail ? `<section id="source-evidence" aria-label="来源依据"><h3>${escape(sourceDetail.title)} · v${sourceDetail.version}</h3><small>${sourceDetail.observedAt ? new Date(sourceDetail.observedAt).toLocaleString() : '来源时间未提供'} · ${escape(sourceDetail.mimeType)}</small><p>${escape(stateLabels[sourceDetail.status] || sourceDetail.status)}</p>${sourceDetail.segments.map((r)=>`<small>${escape(r.locator)}</small><pre class="source-original">${escape(r.text)}</pre>`).join('')}${sourceDetail.nextCursor ? btn('source-more', '继续读取原文', '', true) : ''}</section>` : ''}</section>`;
}
function latest() {
    return snapshot?.derivations.filter((d)=>d.status !== 'stale').sort((a, b)=>b.createdAt - a.createdAt)[0];
}
function rows() {
    return validRows(snapshot).map((r)=>`<article class="record"><div><span class="eyebrow">${escape(r.sourceId)} · ${r.intent === 'remember' ? '用户确认长期信息' : r.sourceId === 'conversation' ? '原始表达' : '合成来源 · 一次导入'} · v${r.version}</span><p>${escape(r.text)}</p><small>${new Date(r.observedAt).toLocaleString()}${r.validUntil ? ' · 有效至 ' + new Date(r.validUntil).toLocaleString() : ''}</small></div>${r.sourceId === 'conversation' ? btn('edit', '纠正', r.id, true) : ''}</article>`).join('') || '<p class="muted">还没有当前有效的记录。</p>';
}
function today() {
    const output = latest();
    return `<header><div><p class="eyebrow">LifeOS · 以人为主体</p><h1>从今天的一点变化开始</h1><p class="muted">记下一句话，让已有记录与此刻的你连起来。</p></div><span class="offline-mark">合成离线 · 无网络</span></header><section class="service-card"><div><p class="eyebrow">当前重点 · 可纠正的建议</p><h2>${output ? '下一步，轻一点开始' : '先留下你的想法'}</h2><p id="suggestion">${escape(output?.body?.text || '保存后，LifeOS 会自动准备有限上下文；不会发送到云端。')}</p>${output ? `<details><summary>为什么这样建议 · ${output.inputRefs.length} 条依据</summary><ul>${output.inputRefs.map((ref)=>{
        const r = snapshot.records.find((r)=>r.id === ref.id) || snapshot.packets.flatMap((p)=>p.included || []).find((r)=>r.id === ref.id);
        return `<li>${escape(r?.text)} <small>${escape(r?.sourceId)} · v${ref.version}</small></li>`;
    }).join('')}</ul><small>${escape(output.modelId)} · AI 候选，不是用户事实</small></details><div class="form-actions">${btn('feedback-confirm', '认可', output.id, true)}${btn('feedback-reject', '不适合', output.id, true)}${btn('feedback-correct', '纠正建议', output.id, true)}</div>` : ''}</div></section>${question?.status === 'pending' ? `<section class="question-card"><p class="eyebrow">只补一个有用的问题</p><h2>${escape(question.text)}</h2><p>${escape(question.purpose)}</p><div class="form-actions">${btn('answer', '回答')}${btn('defer', '稍后再说', '', true)}${btn('ignore', '这次忽略', '', true)}${btn('refuse', '不想回答', '', true)}</div></section>` : ''}<section class="config-card"><h2>当前记录</h2>${rows()}</section>`;
}
function sources() {
    return `<header><p class="eyebrow">Contexts · 授权来源</p><h1>让已有记录参与理解</h1><p class="muted">本轮只有任务内合成样例。一次导入，不是持续同步。</p></header><div class="source-grid">${[
        [
            'obsidian-demo',
            'Obsidian Markdown',
            '两版短文，保留版本与原文'
        ],
        [
            'health-demo',
            '健康模拟来源',
            '睡眠时长，保留时间区间与单位'
        ]
    ].map(([id, title, help])=>{
        const s = snapshot.sources.find((s)=>s.id === id);
        return `<section class="config-card"><h2>${title}</h2><p>${help}</p><span class="state-dot">${s.authorized ? '合成来源可用' : '已撤权，不参与上下文'}</span><div class="form-actions">${btn('import1', '导入合成版本 1', id)}${btn('import2', '导入版本 2', id, true)}${btn('revoke', '撤权排除', id, true)}</div></section>`;
    }).join('')}</div><section class="config-card"><h2>来源与当前理解</h2>${rows()}</section>`;
}
function memories() {
    return `<header><p class="eyebrow">${page} · 本地权威</p><h1>${page === 'Memory' ? '长期记忆与变化历史' : '此刻的状态'}</h1><p class="muted">原始表达、短时状态、确认长期信息与 AI 候选各自保留身份。</p></header>${page === 'Memory' ? sourceMemory() : ''}<section class="config-card"><h2>已确认长期信息</h2>${snapshot.memories.filter((m)=>m.status === 'active').map((m)=>`<p>◇ ${escape(m.statement)} <small>用户明确确认</small></p>`).join('') || '<p class="muted">没有确认的长期信息；AI 不会自动提升。</p>'}${btn('remember', '记住一条长期偏好')}</section><section class="config-card"><h2>Current State · 有效时间明确</h2>${currentStates(snapshot).map((s)=>`<p>${escape(s.stateKey)}：${escape(s.value)} <small>有效至 ${new Date(s.validUntil).toLocaleString()}</small></p>`).join('') || '<p>暂无有效状态。</p>'}</section><section class="config-card"><h2>原始历史 · 纠正不覆盖</h2>${snapshot.records.map((r)=>`<p>${escape(r.text)} <small>v${r.version} · ${escape(r.status)}${r.supersedes ? ' · 替代 ' + escape(r.supersedes) : ''}</small></p>`).join('')}</section>`;
}
function settings() {
    return `<header><p class="eyebrow">Settings · 辅助入口</p><h1>模型设置</h1><p>主服务目录、能力、路由与凭据合同继承保留。本轮只运行两个无凭据的离线测试 Adapter。</p></header>${sourcePanel()}<section class="service-card"><div><h2>本轮离线服务</h2><span class="state-dot success">${model} · 不访问 Provider 或 Keychain</span><label>测试 Adapter<select id="model">${[
        'OfflineA',
        'OfflineB'
    ].map((m)=>`<option ${model === m ? 'selected' : ''}>${m}</option>`).join('')}</select></label><small>切换不删除个人资产、确认或反馈。真实凭据生产实现保留，本轮不可执行。</small></div></section><div class="source-grid"><section class="config-card"><h2>云端服务目录</h2>${cloud.map((p)=>`<p>${p} <small>目录保留 · 本轮不连接</small></p>`).join('')}</section><section class="config-card"><h2>本地服务目录</h2>${local.map((p)=>`<p>${p} <small>目录保留 · 不探测进程</small></p>`).join('')}<h3>凭据与连接</h3>${btn('credential-deny', '保存凭据（本轮禁止）', '', true)}${btn('network-deny', '连接测试（本轮禁止）', '', true)}</section></div><section class="config-card"><h2>路由与权限基线</h2><p>主服务 / 任务覆盖 / Fallback / 能力目录保留为继承输入；当前固定 OfflineA/B，无云端自动补齐。逐次云端披露、确认、移除与取消不被自动本地准备取代。</p><details><summary>高级边界</summary><p>未知输入失败关闭；模型不能操作文件、Repository 或权限。实际 Provider 配置、测试、启用不属于本轮。</p></details></section>`;
}
function render() {
    if (!snapshot) return;
    document.getElementById('app').innerHTML = `<div class="app-shell"><nav class="rail" aria-label="主导航"><span class="brand">✳</span>${[
        'Today',
        'Me',
        'Contexts',
        'Memory'
    ].map((n)=>`<button class="rail-button ${page === n ? 'is-current' : ''}" data-page="${n}" aria-label="${n}" title="${n}">${icons[n]}</button>`).join('')}<span class="rail-spacer"></span><button class="rail-button" data-page="Settings" aria-label="Settings">⚙</button></nav><main id="main" class="conversation-main">${page === 'Today' ? today() : page === 'Contexts' ? sources() : page === 'Settings' ? settings() : memories()}<p id="notice" class="notice" role="status">${escape(notice)}</p></main><section class="composer" aria-label="Global AI"><div class="composer-heading"><strong>✳ Global AI</strong><small>${editing ? '纠正当前记录' : intent === 'answer' ? '回答：例如“今天时间 10 分钟”' : intent === 'remember' ? '一个明确动作，保存为长期偏好' : '自然记录 · 自动本地上下文'} · ${model}</small></div><label class="sr-only" for="conversation">自然表达</label><textarea id="conversation" maxlength="200" placeholder="合成演练：例如“今天要完成项目计划，时间 10 分钟”">${escape(draft.text)}</textarea><div class="composer-footer"><span id="draft-status">${draft.text ? '草稿已在本地保留' : '保存不会发送到云端'}</span>${btn('save', editing ? '保存纠正' : intent === 'remember' ? '保存并记住这条偏好' : '保存一次')}${intent !== 'record' || editing ? btn('cancel', '取消', '', true) : ''}</div></section></div>`;
}
async function refresh() {
    snapshot = await app.snapshot();
    sourceStatus = (await app.sourceCall('get_source_status')).connectors[0] || null;
    const selection = snapshot.drafts.find((d)=>d.id === 'model-selection');
    if (selection) model = selection.modelId;
}
async function automatic(query = '') {
    packet = query ? await app.prepareSources(query) : await app.prepare();
    await app.generate(packet, model);
    question = await app.question();
    await refresh();
}
function resetDraft() {
    draft = {
        id: 'draft:' + uid(),
        turnId: uid(),
        requestId: uid(),
        observedAt: Date.now(),
        text: '',
        revision: 0
    };
    intent = 'record';
    editing = null;
}
async function act(action, id) {
    busy = true;
    notice = '';
    try {
        if (action === 'save') {
            const sourceText = draft.text;
            await queue;
            await app.draft(draft.text, draft.id, 'daily', draft.turnId, ++draft.revision, draft.requestId, draft.observedAt);
            if (editing) await app.correct(editing, draft.text, draft.observedAt, draft.id);
            else await app.save(draft.text, {
                intent,
                requestId: draft.requestId,
                conversationId: 'daily',
                turnId: draft.turnId,
                draftId: draft.id,
                now: draft.observedAt,
                questionId: intent === 'answer' ? question.id : undefined
            });
            resetDraft();
            notice = '已保存一次。';
            try {
                await automatic(sourceText);
                notice += ' 已自动准备本地上下文。';
            } catch (e) {
                notice += ' 上下文暂不可用：' + e.message;
            }
        } else if (action === 'source-connect') {
            await app.sourceCall('connect_source_directory', {
                requestId: uid()
            });
            notice = '已连接合成目录，正在自动导入。';
        } else if (action === 'source-disconnect') {
            disconnectPending = true;
        } else if (action === 'source-keep') {
            disconnectPending = false;
        } else if ([
            'source-refresh',
            'source-pause',
            'source-resume',
            'source-cancel',
            'source-confirm-disconnect'
        ].includes(action)) {
            await app.sourceCall('control_source_job', {
                requestId: uid(),
                connectorId: sourceStatus.connectorId,
                expectedGeneration: sourceStatus.grantGeneration,
                action: action === 'source-confirm-disconnect' ? 'disconnect' : action.slice(7)
            });
            disconnectPending = false;
            sourceMatches = [];
            sourceDetail = null;
            notice = '来源状态已更新。';
        } else if (action === 'source-grant' || action === 'source-revoke') {
            await app.sourceCall('authorize_source_target', {
                requestId: uid(),
                connectorId: sourceStatus.connectorId,
                expectedGeneration: sourceStatus.grantGeneration,
                linkId: id,
                decision: action === 'source-grant' ? 'grant' : 'revoke'
            });
            sourceMatches = [];
            sourceDetail = null;
            notice = '目标授权已更新；结果以实际获取状态为准。';
        } else if (action === 'source-search') {
            sourceMatches = await app.sourceSearch(sourceQuery);
            sourceDetail = null;
            notice = sourceMatches.length ? '已检索到原文来源。' : '没有相关且可用的来源。';
        } else if (action === 'source-detail' || action === 'source-more') {
            const f = sourceStatus.files.find((f)=>f.sourceRef === id) || sourceMatches.find((f)=>f.sourceRef === id);
            const p = action === 'source-more' ? {
                mode: 'detail',
                connectorId: sourceDetail.sourceIdentity.connectorId,
                sourceRef: sourceDetail.sourceIdentity.sourceRef,
                expectedVersion: sourceDetail.version,
                cursor: sourceDetail.nextCursor
            } : {
                mode: 'detail',
                connectorId: f.sourceId || sourceStatus.connectorId,
                sourceRef: id,
                expectedVersion: f.version
            };
            sourceDetail = await app.sourceCall('get_source_evidence', p);
            page = 'Memory';
        } else if (action === 'answer') {
            intent = 'answer';
            notice = '在下方输入回答，例如“今天时间 10 分钟”。';
        } else if ([
            'defer',
            'ignore',
            'refuse'
        ].includes(action)) {
            await app.decide(question, action, action === 'defer' ? Date.now() + 3600000 : undefined);
            question = null;
            notice = action === 'defer' ? '已暂缓一小时，重启仍有效。' : '已记录你的选择，不再重复追问同一缺口。';
        } else if (action === 'remember') {
            intent = 'remember';
            notice = '只填写你明确认可的长期偏好；这个保存动作表达确认。';
        } else if (action === 'cancel') {
            editing = null;
            intent = 'record';
            notice = '已取消操作；草稿保留。';
        } else if (action === 'edit') {
            editing = snapshot.records.find((r)=>r.id === id);
            draft.text = editing.text;
            notice = '保存纠正会保留旧版本，只更新受影响理解。';
        } else if (action.startsWith('feedback-')) {
            await app.feedback(id, action.slice(9));
            await automatic();
            notice = '反馈已保留，相关建议已重新考虑。';
        } else if (action === 'revoke') {
            await app.revoke(snapshot.sources.find((s)=>s.id === id));
            await automatic();
            notice = '来源已撤权；旧上下文与派生不能复活。';
        } else if (action === 'import1' || action === 'import2') {
            const version = action === 'import1' ? 1 : 2;
            const end = Math.floor(Date.now() / 86400000) * 86400000;
            const content = id === 'obsidian-demo' ? version === 1 ? '# 合成项目\n今天整理项目计划。' : '# 合成项目\n先核对项目计划，再安排下一步。' : JSON.stringify({
                sleepHours: version === 1 ? 6 : 8,
                start: end - 8 * 3600000,
                end,
                unit: 'hours'
            });
            await app.importSource({
                sourceId: id,
                externalId: 'demo',
                version,
                sourceType: id === 'obsidian-demo' ? 'synthetic_markdown' : 'synthetic_health',
                mimeType: id === 'obsidian-demo' ? 'text/markdown' : 'application/json',
                content
            });
            await automatic();
            notice = '合成来源已导入；没有读取 Vault 或 iPhone。';
        } else if (action === 'credential-deny') await app.call('save_ai_provider_credential', 'denied');
        else if (action === 'network-deny') await app.call('test_ai_provider_connection', 'denied');
    } catch (e) {
        notice = action.startsWith('source-') ? sourceReason(e.message) : e.message === 'correction_type_rejected' ? '这次纠正不能改变信息类型或移除已识别的状态。原记录未变，草稿已保留。' : '未完成：' + e.message + '。草稿已保留。';
    } finally{
        await refresh();
        busy = false;
        render();
        if ([
            'source-detail',
            'source-more'
        ].includes(action)) document.getElementById('source-evidence')?.scrollIntoView({
            block: 'start'
        });
        if ([
            'answer',
            'remember',
            'edit'
        ].includes(action)) document.getElementById('conversation')?.focus();
    }
}
document.addEventListener('click', (event)=>{
    const b = event.target.closest('button');
    if (!b || busy) return;
    if (b.dataset.page) {
        page = b.dataset.page;
        render();
    } else if (b.dataset.action) void act(b.dataset.action, b.dataset.id || '');
});
document.addEventListener('input', (event)=>{
    const t = event.target;
    if (t.id === 'source-query') {
        sourceQuery = t.value;
        return;
    }
    if (t.id !== 'conversation') return;
    draft.text = t.value;
    draft.requestId = uid();
    draft.observedAt = Date.now();
    const copy = {
        ...draft,
        revision: ++draft.revision
    };
    queue = queue.catch(()=>{}).then(()=>app.draft(copy.text, copy.id, 'daily', copy.turnId, copy.revision, copy.requestId, copy.observedAt)).then(()=>{
        const n = document.getElementById('draft-status');
        if (n) n.textContent = '草稿已在本地保留';
    }).catch((e)=>{
        notice = '草稿保存失败：' + e.message;
        const n = document.getElementById('draft-status');
        if (n) n.textContent = notice;
        throw e;
    });
});
document.addEventListener('change', async (event)=>{
    const t = event.target;
    if (t.id === 'model') {
        model = t.value;
        await app.call('save_ai_provider_settings', 'offline_settings', {
            requestId: uid(),
            modelId: model
        });
        notice = '已切换测试 Adapter，资产与反馈保持不变。';
        await refresh();
        render();
    }
});
await refresh();
const pending = snapshot.drafts.filter((d)=>d.status === 'pending').sort((a, b)=>b.revision - a.revision)[0];
if (pending) draft = {
    id: pending.draftId,
    turnId: pending.turnId,
    requestId: pending.requestId || 'save:' + pending.turnId,
    observedAt: pending.observedAt || Date.now(),
    text: pending.text,
    revision: pending.revision
};
question = await app.question();
await refresh();
render();
setInterval(async ()=>{
    if (busy || page !== 'Settings' || !sourceStatus) return;
    const previous = JSON.stringify(sourceStatus);
    try {
        sourceStatus = (await app.sourceCall('get_source_status')).connectors[0] || null;
        if (previous !== JSON.stringify(sourceStatus)) render();
    } catch  {
        notice = '来源状态暂不可用，请重试。';
    }
}, 1500);
