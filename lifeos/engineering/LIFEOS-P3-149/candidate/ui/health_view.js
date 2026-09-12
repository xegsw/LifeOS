const esc = (s)=>String(s ?? '').replace(/[&<>"']/g, (c)=>({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[c]);
const metric = {
    sleep: '睡眠区间',
    steps: '步数',
    exercise: '运动时长'
};
const time = (n, offset)=>typeof n === 'number' ? offset === undefined ? new Date(n).toLocaleString('zh-CN', {
        hour12: false
    }) : new Date(n + offset * 60000).toISOString().slice(0, 19).replace('T', ' ') : '未记录';
const amount = (s, v)=>typeof v === 'number' ? `${Number(v.toFixed(1))} ${s.unit === 'count' ? '步' : '分钟'}` : '暂无法可靠合并';
export function healthStates(snapshot) {
    return (snapshot?.states || []).filter((s)=>s.kind === 'health_current_state').sort((a, b)=>b.dayIndex - a.dayIndex || a.metric.localeCompare(b.metric) || a.offsetMinutes - b.offsetMinutes);
}
export function healthView(snapshot, details = false) {
    const states = healthStates(snapshot);
    const latest = states[0]?.dayIndex;
    const shown = details ? states : states.filter((s)=>s.dayIndex === latest);
    return `<section class="config-card health-section"><p class="eyebrow">健康 · 合成来源</p><h2>${details ? '健康来源与观察记录' : '健康近况'}</h2><p class="quiet">${details ? '保留样本及修订来源，未确认为长期事实。' : '按来源观察，不代表健康 App 的权威总量。'}</p>${shown.length ? shown.map((s)=>{
        const date = new Date(s.dayIndex * 86400000).toISOString().slice(0, 10);
        const old = typeof s.observedAt === 'number' && Date.now() - s.observedAt > 86400000;
        return `<article class="record"><div><h3>${metric[s.metric] || esc(s.metric)} · ${date}</h3><p>${s.method === 'no_current_sample' ? '更正后本日已无有效样本' : amount(s, s.value)}${s.estimated ? ' · 跨日按时长分摊估算' : ''}</p><small>UTC${s.offsetMinutes >= 0 ? '+' : ''}${s.offsetMinutes / 60} · ${old ? '观察已超过24小时' : '最近观察'} ${time(s.observedAt, s.offsetMinutes)}</small><p class="tiny">收到（本机时间）${time(s.receivedAt)}</p>${s.sources.map((o)=>`<p>${esc(o.name)} · ${amount(s, o.value)}${o.estimated ? '（估算）' : ''}</p>`).join('')}${s.metric === 'sleep' ? '<p class="tiny">明确睡眠区间并集，重叠不重复累计。</p>' : ''}<details data-keep="health:${esc(s.id)}"><summary>查看来源与版本</summary>${s.refs.map((r)=>{
            const raw = (snapshot.records || []).find((v)=>v.id === r.id)?.observation;
            return `<p>${esc(r.sourceId)} / ${esc(r.sampleId)} · v${r.version}</p>${raw ? `<p class="tiny">原始观察 ${time(raw.sample.startMs, raw.offset)} — ${time(raw.sample.endMs, raw.offset)} · ${raw.sample.value} ${esc(raw.sample.unit)}</p>` : ''}`;
        }).join('') || '<p>旧版本保留在来源记录中。</p>'}</details></div></article>`;
    }).join('') : '<p>还没有收到健康观察；缺失不记为零。</p>'}<p class="tiny">仅合成演练 · 不推断疲劳或疼痛 · 未授权 AI 读取</p>${details ? `<details data-keep="health-history"><summary>样本修订历史</summary>${(snapshot?.records || []).filter((r)=>r.kind === 'health_sample').map((r)=>`<p>${esc(r.observation.source.name)} / ${esc(r.externalId)} · v${r.version} · ${metric[r.observation.sample.metric]} ${r.observation.sample.value} ${esc(r.observation.sample.unit)}</p>`).join('')}</details>` : ''}</section>`;
}
export function healthSettings(snapshot) {
    const sources = (snapshot?.sources || []).filter((s)=>s.kind === 'health_source' && s.externalSourceId);
    const receiver = (snapshot?.sources || []).find((s)=>s.id === 'health-inbox');
    const errors = (receiver?.files || []).filter((f)=>f.error);
    return `<section class="config-card health-section"><h2>健康来源</h2><p>合成收件箱 · 本 App 打开时自动接收</p><p>${sources.length ? '已接收 ' + sources.length + ' 个合成来源' : '等待首个合成健康文件'}</p>${sources.map((s)=>`<p>${esc(s.name)} · 最近收到（本机时间）${time(s.receivedAt)}</p>`).join('')}${receiver?.error ? `<p role="status">接收暂停（${esc(receiver.error)}），已有数据保留。</p>` : ''}${errors.length ? `<p role="status">${errors.length} 个文件未接收，已有数据保留。</p><details data-keep="health-errors"><summary>查看未接收文件</summary>${errors.map((f)=>`<p>${esc(f.file)} · ${esc(f.error)}</p>`).join('')}</details>` : ''}<p>观察结果在“我”，样本与版本在 Memory。健康接收不授权 AI 读取。</p><p class="tiny">尚未连接 iPhone 或 iCloud；关闭 App 后停止接收。</p></section>`;
}
