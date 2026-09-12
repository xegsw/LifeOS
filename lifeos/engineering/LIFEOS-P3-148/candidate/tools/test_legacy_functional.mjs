// New P3-148 ordinary positive compatibility smoke. No old security tests or real paths.
import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {createInterface} from 'node:readline';
import {Application} from '../ui/core.js';
const root='/private/tmp/lifeos-p3-148-source-ai-v1';
assert.equal(process.env.LIFEOS_P3_148_BUILD_PROFILE,'engineering');
const bin=root+'/target/debug/lifeos-p3-148',fixture='legacy-'+crypto.randomUUID();
assert.equal(spawnSync(bin,['--init-synthetic-fixture',fixture],{encoding:'utf8'}).status,0);
const child=spawn(bin,['--repository-stdio',fixture],{stdio:['pipe','pipe','pipe']});const queue=[];const calls=new Set();
createInterface({input:child.stdout}).on('line',line=>{const v=JSON.parse(line),q=queue.shift();v.error?q.reject(new Error(v.error.code)):q.resolve(v.ok)});
const repo={invoke(ipc,request){calls.add(ipc+':'+request.operation);return new Promise((resolve,reject)=>{queue.push({resolve,reject});child.stdin.write(JSON.stringify({ipc,request})+'\n')})}};
const a=new Application(repo);
try {
 await repo.invoke('get_context_recovery',{version:3,operation:'open_conversation',payload:{requestId:'open',conversationId:'source-chat'}});
 await a.draft('fictional record','legacy-draft','daily','legacy-turn',1);
 await a.save('fictional record',{requestId:'legacy-save',conversationId:'daily',turnId:'legacy-turn',draftId:'legacy-draft'});
 const q=await a.question();if(q)await a.decide(q,'ignore');
 await a.save('喜欢清晨整理图纸',{intent:'remember'});
 let s=await a.snapshot();await a.correct(s.records.find(r=>r.intent==='remember'),'喜欢傍晚整理图纸');
 await a.save('今天时间 10 分钟');s=await a.snapshot();await a.correct(s.records.find(r=>r.text==='今天时间 10 分钟'),'今天时间 20 分钟');
 await a.call('save_ai_provider_settings','offline_settings',{requestId:'offline-settings',modelId:'OfflineA'});
 const packet=await a.prepare();const output=await a.generate(packet);await a.feedback(output.id,'ignore');
 await a.importSource({sourceId:'obsidian-demo',externalId:'fiction-note',sourceType:'synthetic_markdown',mimeType:'text/markdown',version:1,content:'纯虚构项目来源'});
 s=await a.snapshot();await a.revoke(s.sources.find(r=>r.id==='obsidian-demo'));
 assert(s.records.some(r=>r.text==='今天时间 20 分钟'));
 console.log(JSON.stringify({status:'pass',scope:'ordinary positive v2 functional compatibility',operations:[...calls].sort()},null,2));
} finally {child.stdin.end();await new Promise(resolve=>child.on('exit',resolve));}
