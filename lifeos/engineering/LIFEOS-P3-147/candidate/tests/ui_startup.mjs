import {root} from '../tools/root_config.mjs';
// Diagnostic render against this task's synthetic app DB; no GUI or network substitution.
import {spawn} from 'node:child_process';import {createInterface} from 'node:readline';
const child=spawn(root+'/initial-build-cache/debug/lifeos-p3-147',['--repository-stdio','app'],{stdio:['pipe','pipe','pipe']});
const pending=[];createInterface({input:child.stdout}).on('line',s=>{const v=JSON.parse(s),p=pending.shift();v.error?p.reject(v.error):p.resolve(v.ok)});
globalThis.window={__TAURI__:{core:{invoke:(ipc,{request})=>new Promise((resolve,reject)=>{pending.push({resolve,reject});child.stdin.write(JSON.stringify({ipc,request})+'\n')})}}};
const host={innerHTML:''};globalThis.document={getElementById:()=>host,addEventListener:()=>{}};globalThis.setInterval=()=>0;
try{await import('../ui/ui.js');console.log(JSON.stringify({rendered:host.innerHTML.length>0,htmlBytes:host.innerHTML.length}));}catch(e){console.error(e);process.exitCode=1}finally{child.stdin.end();}
