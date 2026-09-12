import {test} from 'node:test';import assert from 'node:assert/strict';import {readFileSync} from 'node:fs';import vm from 'node:vm';
// Execute the actual compiled pure chat renderer with a supplied snapshot, without a network/DOM adapter.
const ui=readFileSync(new URL('../candidate/ui/health_ui.js',import.meta.url),'utf8');
const code=ui.slice(ui.indexOf('function clarificationActions('),ui.indexOf('function errorText('));
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('"','&quot;');
function render(snapshot){return vm.runInNewContext(code+';chat();',{flow:{snapshot},esc,date:String,button:(action,label,id)=>`<button data-action="${action}" data-id="${esc(id)}">${label}</button>`});}
const question=status=>({id:'q-health',status,field:'available_time',domain:'health'});
const state=status=>({turns:[{turnId:'ask',clarificationId:'q-health',text:'健康活动怎么安排',answer:'需要多少分钟？',refs:[]}],questions:[question(status)]});
test('pending exposes three separate decisions without adding a save confirmation',()=>{const html=render(state('pending'));for(const label of ['稍后再说','忽略这个问题','不要再问'])assert(html.includes(label));assert(!html.includes('重新讨论'));assert.equal((html.match(/<button/g)||[]).length,3)});
test('rejected exposes only explicit reopen',()=>{const html=render(state('rejected'));assert(html.includes('已停止主动询问'));assert(html.includes('重新讨论'));assert(!html.includes('不要再问'));assert.equal((html.match(/<button/g)||[]).length,1)});
test('answered and ignored do not present pending actions; deferred states retry condition',()=>{for(const status of ['answered','ignored','deferred'])assert(!render(state(status)).includes('<button'));assert(render(state('ignored')).includes('本次'));assert(render(state('deferred')).includes('30 分钟'))});
test('reopen remains reachable when original turn left the bounded history response',()=>{const html=render({turns:[],questions:[question('rejected')],hasMore:true});assert(html.includes('健康活动的可用时间'));assert.equal((html.match(/重新讨论/g)||[]).length,1);assert(!html.includes('不要再问'))});
test('invalidated original state response labels history without changing its text',()=>{const s=state('answered');s.turns[0].status='stale';s.turns[0].answer='按15分钟安排';const html=render(s);assert(html.includes('旧依据已失效，保留历史'));assert(html.includes('按15分钟安排'))});
