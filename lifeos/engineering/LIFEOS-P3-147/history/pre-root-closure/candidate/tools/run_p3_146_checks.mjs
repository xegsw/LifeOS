import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,lstatSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
const root='/private/tmp/lifeos-p3-147-obsidian-source-v1';
const base=fileURLToPath(new URL('..',import.meta.url));
const marker=JSON.parse(readFileSync(root+'/.lifeos-p3-147-owner.json','utf8'));
if(marker.task!=='LIFEOS-P3-147'||marker.root!==root||lstatSync(root).isSymbolicLink())throw Error('root_rejected');
const env={...process.env,CARGO_TARGET_DIR:root+'/initial-build-cache',TMPDIR:root+'/tmp',LIFEOS_P3_147_PROFILE:'synthetic'};
const steps=[['ui',process.execPath,['tools/build_ui.mjs']],['format','/Users/xxe/.cargo/bin/cargo',['fmt','--all','--','--check']],['build','/Users/xxe/.cargo/bin/cargo',['build','--locked','--offline']],['integration',process.execPath,['--test','--test-concurrency=1','--test-timeout=15000','tests/integration.mjs']]];
const result=[];const run=Date.now().toString();
for(const [name,exe,args] of steps){const r=spawnSync(exe,args,{cwd:base,env,encoding:'utf8',timeout:180000});writeFileSync(root+'/'+run+'-'+name+'.log',(r.stdout||'')+(r.stderr||''));result.push({name,command:[exe,...args],exit:r.status,error:r.error?.message});if(r.status!==0)break;}
writeFileSync(new URL('../../evidence/checks-'+run+'.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify(result));if(result.length!==steps.length||result.some(s=>s.exit!==0))process.exitCode=1;
