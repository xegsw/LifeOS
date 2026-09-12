import {readFileSync} from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';
const source=readFileSync(new URL('../../candidate/application/health_ui.ts',import.meta.url),'utf8');
const line=source.split('\n').find(l=>l.startsWith('function errorText'));
const errorText=vm.runInNewContext('('+line.replace('(e:any)','(e)').replace('messages:any','messages')+')');
const results=['readonly_sidecar_required','database_unavailable','clarification_rejected','provider_protocol','response_too_large','adapter_rejected'].map(code=>{const text=errorText({code});assert.equal(text,'操作未完成，草稿已保留。');return {code,rendered:text,indistinguishable:true}});
console.log(JSON.stringify({reproduced:true,scope:'fixed error mapping only; actual user cause unknown',results},null,2));
