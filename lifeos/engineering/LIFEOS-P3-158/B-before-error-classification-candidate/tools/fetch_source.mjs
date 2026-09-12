import {WebSourceAdapter} from '../ui/web_source.js';
// No HTTP client, DNS, socket, cookies or credentials. Exact injection fixture only.
const pages=new Map([['https://synthetic.invalid/article','合成外链目标正文：项目计划需要先核对资料，再确认下一步。']]);
const transport={resolve:async()=>[{ip:'93.184.216.34'}],get:async(url)=>{if(!pages.has(url))throw Error('synthetic_target_unavailable');const body=new TextEncoder().encode(pages.get(url));return {status:200,peer:'93.184.216.34',contentType:'text/plain',body,decodedBytes:body.byteLength,elapsedMs:1}}};
let url='';for await(const chunk of process.stdin){url+=chunk.toString();if(url.length>8192)process.exit(2)}const grant={active:true,generation:1,targets:new Set([url])};
try{const r=await new WebSourceAdapter(transport).read(url,grant,()=>grant);process.stdout.write(JSON.stringify({...r,body:new TextDecoder().decode(r.body)}))}catch{process.stdout.write(JSON.stringify({status:'unavailable'}));process.exitCode=1}
