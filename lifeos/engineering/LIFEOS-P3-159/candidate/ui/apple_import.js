const esc = (s)=>String(s ?? '').replace(/[&<>"']/g, (c)=>({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;'
        })[c]);
const time = (n)=>typeof n === 'number' ? new Date(n).toLocaleString('zh-CN', {
        hour12: false
    }) : '暂无';
export function appleImportView(state, real = false) {
    const s = state.status || {
        status: 'idle'
    }, running = s.status === 'running';
    const result = [
        'completed',
        'successful_with_skips',
        'duplicate'
    ].includes(s.status) ? `<p role="status">${s.status === 'duplicate' ? '此文件已导入，未重复写入。' : s.status === 'successful_with_skips' ? '有效记录已导入，部分记录已跳过。' : '导入完成。'} 新增观察 ${s.inserted} · 重复内容 ${s.duplicates} · 不支持 ${s.unsupported} · 跳过 ${s.skipped || 0} · 未投影观察 ${s.unprojected || 0} · 失败 ${s.failed}</p><p class="tiny">最近成功导入（本机时间）${time(s.importedAt)}${s.originalImport ? ' · 保留原导入时间' : ''}</p><p class="tiny">${s.attachments || 0} 个附件未处理；不支持数包含其他顶层对象。</p>${Object.keys(s.unsupportedTypes || {}).length ? `<details data-keep="apple-unsupported"><summary>查看不支持类型</summary>${Object.entries(s.unsupportedTypes).map(([k, v])=>`<p class="tiny">${esc(k)} · ${esc(v)}</p>`).join('')}</details>` : ''}` : s.status === 'paused' ? '<p>上次导入未完成，未自动继续。请重新选择文件手动重试。</p>' : s.status === 'failed' ? `<p role="alert">文件导入失败：${esc(s.code)}。文件失败 1，整批新增 0；无法确认的记录数量不作推测。已有数据保留。</p><button class="button secondary" data-action="apple-retry">重试此文件</button>` : running ? `<p role="status">${esc(s.phase || '正在准备导入')} · 已处理 ${Number(s.processed || 0)} 条；完成前不发布新观察。</p><progress aria-label="苹果健康文件导入进度"></progress>` : '<p>尚未导入苹果健康文件。</p>';
    return `<section class="config-card health-section" aria-label="苹果健康文件导入"><h2>苹果健康文件</h2><p>文件导入，非自动同步 · ${real ? '仅手动开始，按既有规则去重追加' : '仅本任务合成演练'}</p><button class="button primary" data-action="apple-open" ${running || state.loading ? 'disabled' : ''}>导入苹果健康文件</button>${state.loading ? '<p role="status">正在准备固定文件选项…</p>' : ''}${state.error ? `<p role="alert">${esc(state.error)}</p><button class="button secondary" data-action="apple-status-retry">重新读取健康导入状态</button>` : ''}${state.picker ? `<section class="apple-file-picker" aria-label="选择健康文件"><h3>选择 XML 或 ZIP 文件</h3><p class="tiny">${real ? '原件：/Users/xxe/Downloads/导出.zip。目标：/Users/xxe/Documents/LifeOS-Health-Import-Pilot-1/health-import.sqlite。点击下方文件开始去重追加，已有观察保留。' : '仅显示本任务专用目录，不访问个人目录。选中即导入。'}</p>${state.picker.map((file)=>`<p><button class="button secondary" data-action="apple-select" data-id="${esc(file)}">${esc(file)}</button></p>`).join('') || '<p>没有可选文件。</p>'}<button class="button ghost" data-action="apple-close">取消选择</button></section>` : ''}${s.file ? `<p class="tiny">文件：${esc(s.file)}</p>` : ''}${result}${s.statusPersistenceWarning ? '<p role="alert">导入结果已返回，但状态保存未完成；重启后请手动核对，重复导入会去重。</p>' : ''}<p class="tiny">支持睡眠区间、步数、Apple 运动时长。重复内容不是样本修订证明；同批重复有歧义时保留观察，不猜测为新样本；覆盖范围未知，不代表健康库全部导入。</p><p class="tiny">导入状态在这里保留；在“我”按需查看观察。导入不等于允许 AI 处理。</p></section>`;
}
