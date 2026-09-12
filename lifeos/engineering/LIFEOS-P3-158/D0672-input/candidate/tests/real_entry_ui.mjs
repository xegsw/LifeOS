// Ordinary UI click sequencing with a synthetic IPC stub; no filesystem adapters.
import assert from 'node:assert/strict';
const calls=[],listeners={};const host={innerHTML:'',scrollIntoView(){}};
const snapshot={records:[],sources:[],memories:[],states:[],drafts:[],derivations:[],packets:[],questions:[],feedback:[]};
globalThis.window={__LIFEOS_REAL_SOURCE__:true,__TAURI__:{core:{invoke:async(ipc)=>{
  calls.push(ipc);
  if(ipc==='connect_source_directory')return {connectorId:'directory',grantGeneration:1,status:'active'};
  if(ipc==='get_today')return snapshot;
  if(ipc==='get_source_status')return {connectors:[{connectorId:'directory',grantGeneration:1,status:'active',discovered:6,processed:6,parsed:3,unparsed:3,failed:0,pending:0,scanComplete:true,files:[],links:[]}]};
  throw Error('unexpected ordinary UI call');
}}}};
globalThis.document={getElementById:()=>host,addEventListener:(name,fn)=>listeners[name]=fn};globalThis.setInterval=()=>0;
function click(action){listeners.click({target:{closest:()=>({dataset:{action}})}})}
await import('../ui/ui.js');
assert.equal(calls.length,0);assert.match(host.innerHTML,/连接此目录/);assert.match(host.innerHTML,/本地保存已获授权/);
click('source-plan-close');click('source-plan');assert.equal(calls.length,0);
click('source-connect');for(let i=0;i<100&&!host.innerHTML.includes('已打开本地来源');i++)await new Promise(r=>setTimeout(r,10));
assert.equal(calls[0],'connect_source_directory');assert.match(host.innerHTML,/已打开本地来源/);
assert(!calls.includes('authorize_source_target'));
console.log(JSON.stringify({scope:'ordinary real-entry UI with synthetic stub',count:3,results:['startup zero IPC','explanation zero IPC','user click precedes all repository reads'],real_path_contact:false}));
