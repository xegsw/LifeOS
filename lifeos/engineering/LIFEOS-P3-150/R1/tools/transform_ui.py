# coding: utf-8
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'candidate/ui/readonly.js'
s=p.read_text()
s=s.replace("this.seq=0;","this.seq=0;this.overview=null;this.detailsOpen=false;this.trendOpen=false;")
s=s.replace(' async load(patch={})', ''' async initialize(){this.loading=true;this.error='';this.changed();try{const overview=[];for(const metric of ['steps','sleep','exercise']){const d=await this.call({version:2,operation:'health_view',payload:{metric,days:7,groupPage:0}});if(metric==='steps')this.data=d;overview.push({metric,latestDay:d.latestDay,importedAt:d.importedAt});}this.overview=overview;}catch{this.overview=null;this.error='暂时无法读取导入状态。请稍后重新打开此窗口。';}finally{this.loading=false;this.changed();}}
 async load(patch={})''')
a=s.index('return `<header',s.index('export function content(c)'));b=s.index('<section class="panel health-reader">',a)
s=s[:a]+'''return `<section class="panel health-reader"><label class="metric-select">查看内容<select id="metric" ${c.loading?'disabled':''}>${Object.keys(labels).map(m=>`<option value="${m}" ${q.metric===m?'selected':''}>${labels[m]}</option>`).join('')}</select></label>'''+s[b+len('<section class="panel health-reader">'):]
s=s.replace('export function content(c)','export function detailContent(c)')
s=s.replace('${chart(d)}', '''<button id="history-toggle" class="button secondary" data-action="trend" aria-expanded="${!!c.trendOpen}">${c.trendOpen?'收起趋势':'查看历史趋势'}</button>${c.trendOpen?chart(d):''}''')
s=s.replace("const call=r=>", "const call=r=>")
pos=s.index("if(typeof document!=='undefined')")
s=s[:pos]+'''export function content(c){
 const list=c.overview||[],times=list.map(v=>v.importedAt).filter(v=>typeof v==='number'),latest=times.length?Math.max(...times):null;
 return `<header class="page-head source-head"><div><h1>健康来源</h1><p class="subhead">核对已导入的资料，需要时再查看细节。</p></div><span class="synthetic-mark">${globalThis.__HEALTH_REAL_READONLY__?'本地只读':'合成只读验证'}</span></header><section class="source-summary"><p>这是来源检查辅助窗口，只提供资料查看，不提供对话或 AI 解读。</p>${!c.overview?(c.loading?'<p role="status">正在读取导入状态…</p>':`<p role="alert">${esc(c.error)}</p><button class="button secondary" data-action="overview-retry">重试</button>`):`<p class="import-state">${latest!==null?'已找到成功导入记录':'尚无成功导入记录'}</p><p class="tiny">最近导入：${latest!==null?new Date(latest).toLocaleString('zh-CN',{hour12:false})+'（本机时间）':'暂无'}</p><p class="freshness">各指标最近记录：${list.map(v=>`${labels[v.metric]} ${date(v.latestDay)}`).join('；')}。</p><p class="tiny">各来源日期可能不同；以上日期不代表连续或完整覆盖。</p><button id="data-toggle" class="button secondary" data-action="details" aria-expanded="${!!c.detailsOpen}">${c.detailsOpen?'收起已导入数据':'查看已导入数据'}</button>`}</section>${c.detailsOpen?detailContent(c):''}`;
}
'''+s[pos:]
s=s.replace("switch(b.dataset.action){", "switch(b.dataset.action){case'overview-retry':c.initialize();break;case'details':c.detailsOpen=!c.detailsOpen;if(!c.detailsOpen)c.trendOpen=false;render();break;case'trend':c.trendOpen=!c.trendOpen;render();break;")
s=s.replace("if(e.target.id==='days')", "if(e.target.id==='metric')c.load({metric:e.target.value,source:undefined,offset:undefined,endDay:undefined,groupPage:0});if(e.target.id==='days')")
s=s.replace('render();c.load();','render();c.initialize();')
p.write_text(s)
