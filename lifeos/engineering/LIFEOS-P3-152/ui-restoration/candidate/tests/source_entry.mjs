// Ordinary synthetic product flow only. No independent review or security attack runner.
import {root} from '../tools/root_config.mjs';
import {spawn} from 'node:child_process';
import {createInterface} from 'node:readline';
import assert from 'node:assert/strict';
const fixture='entry-'+process.pid;
let child,pending=[],calls=[],results=[];
function start(){
  child=spawn(root+'/initial-build-cache/debug/lifeos-p3-147',['--repository-stdio',fixture],{stdio:['pipe','pipe','inherit']});
  createInterface({input:child.stdout}).on('line',line=>{const r=JSON.parse(line),p=pending.shift();r.error?p.reject(r.error):p.resolve(r.ok)});
}
async function stop(){child.stdin.end();await new Promise(resolve=>child.once('exit',resolve))}
function invoke(ipc,{request}){calls.push(ipc);return new Promise((resolve,reject)=>{pending.push({resolve,reject});child.stdin.write(JSON.stringify({ipc,request})+'\n')})}
const source=(ipc,payload={})=>invoke(ipc,{request:{version:1,payload}});
const host={innerHTML:'',scrollIntoView(){}};const listeners={};
globalThis.window={__TAURI__:{core:{invoke}}};
globalThis.document={getElementById:()=>host,addEventListener:(name,fn)=>listeners[name]=fn};
globalThis.setInterval=()=>0;
function click(dataset){listeners.click({target:{closest:()=>({dataset})}})}
const wait=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function until(fn){for(let i=0;i<400;i++){if(await fn())return;await wait(100)}throw Error('ordinary flow timed out')}
start();
try{
  await import('../ui/ui.js');click({page:'Settings'});
  const before=calls.length;click({action:'source-plan'});
  assert.match(host.innerHTML,/source-connection-plan/);
  assert.match(host.innerHTML,/<button[^>]*disabled[^>]*>连接此目录（未激活）/);
  assert.match(host.innerHTML,/未加密/);assert.equal(calls.length,before);
  results.push('preparation visible; activation disabled; opening causes zero IPC');
  click({action:'source-plan-close'});assert.equal(calls.length,before);
  click({action:'source-connect'});
  await until(()=>host.innerHTML.includes('已连接合成目录，正在自动导入。'));
  let status;await until(async()=>{status=(await source('get_source_status')).connectors[0];return status.scanComplete&&!status.pending});
  assert.equal(status.discovered,6);assert.equal(status.parsed,3);assert.equal(status.unparsed,3);
  results.push('UI connect and automatic six-file import with honest format counts');
  const control=action=>source('control_source_job',{requestId:action+'-'+Date.now(),connectorId:'directory',expectedGeneration:status.grantGeneration,action});
  await control('pause');assert.equal((await source('get_source_status')).connectors[0].status,'paused');
  await stop();start();assert.equal((await source('get_source_status')).connectors[0].status,'paused');
  await control('resume');assert.equal((await source('get_source_status')).connectors[0].status,'active');
  results.push('pause survives process restart and resumes');
  const matches=await source('get_source_evidence',{mode:'search',connectorId:'directory',expectedGeneration:status.grantGeneration,query:'项目计划'});
  assert(matches.results.length>0);results.push('local source search returns evidence');
  await control('refresh');await until(async()=>{status=(await source('get_source_status')).connectors[0];return status.scanComplete&&!status.pending});
  assert.equal(status.discovered,6);results.push('manual refresh completes');
  await control('disconnect');assert.deepEqual((await source('get_source_status')).connectors,[]);
  await stop();start();assert.deepEqual((await source('get_source_status')).connectors,[]);
  results.push('disconnect remains disconnected after restart');
  assert(!calls.includes('authorize_source_target'));
  console.log(JSON.stringify({scope:'ordinary synthetic entry flow; No Independent Pass',count:results.length,results,external_target_calls:0}));
}finally{await stop()}
