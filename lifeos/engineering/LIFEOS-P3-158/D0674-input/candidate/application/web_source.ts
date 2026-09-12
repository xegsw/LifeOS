/** No network implementation exists. All resolution/requests use an injected test Transport. */
export type Address={ip:string};
export type Response={status:number,peer:string,location?:string,contentType:string,body:Uint8Array,decodedBytes:number,elapsedMs:number};
export interface Transport {resolve(host:string):Promise<Address[]>;get(url:string,pinned:string[],limits:{connectMs:number,totalMs:number,maxDecodedBytes:number}):Promise<Response>}
export type WebGrant={generation:number,active:boolean,targets:ReadonlySet<string>};
const MAX=20*1024*1024;
export function publicAddress(ip:string):boolean {
 // Accept canonical IPv4 global unicast only. Unimplemented address families fail closed.
 const p=ip.split('.');if(p.length!==4||p.some(v=>! /^(0|[1-9]\d{0,2})$/.test(v)||Number(v)>255))return false;
 const [a,b,c]=p.map(Number);
 return !(a===0||a===10||a===127||a>=224||a===169&&b===254||a===172&&b>=16&&b<=31||a===192&&(b===168||b===0||b===2)||a===100&&b>=64&&b<=127||a===198&&(b===18||b===19||b===51&&c===100)||a===203&&b===0&&c===113);
}
export function checkedTarget(raw:string,grant:WebGrant):URL {
 let u:URL;try{u=new URL(raw)}catch{throw new Error('url_rejected')}
 if(!grant.active||!Number.isSafeInteger(grant.generation)||grant.generation<1||!grant.targets.has(u.href))throw new Error('target_not_authorized');
 if(!['https:','http:'].includes(u.protocol)||u.username||u.password||u.hash||u.port&&!['80','443'].includes(u.port))throw new Error('url_rejected');
 // Query strings are not assumed secret-free, so none are transmitted in this profile.
 if(u.search||/%[0-9a-f]{2}/i.test(u.hostname)||u.hostname==='localhost'||u.hostname.endsWith('.local'))throw new Error('sensitive_url_rejected');
 return u;
}
export class WebSourceAdapter {
 private running=0;
 constructor(private transport:Transport){}
 async read(raw:string,grant:WebGrant,current:()=>WebGrant){
  if(this.running>=2)throw new Error('web_concurrency_limit');this.running++;const start=Date.now(),generation=grant.generation;let url=raw;const visited=new Set<string>();
  const check=()=>{const g=current();if(!g.active||g.generation!==generation)throw new Error('grant_stale');return g};
  try{
   for(let hop=0;hop<=5;hop++){
    const u=checkedTarget(url,check());if(visited.has(u.href))throw new Error('redirect_cycle');visited.add(u.href);
    let dnsTimer:ReturnType<typeof setTimeout>|undefined;
    const resolved=await Promise.race([this.transport.resolve(u.hostname),new Promise<never>((_,reject)=>{dnsTimer=setTimeout(()=>reject(new Error('web_timeout')),Math.min(10000,Math.max(1,30000-(Date.now()-start))))})]).finally(()=>clearTimeout(dnsTimer));
    const ips=resolved.map(v=>v.ip);check();if(!ips.length||ips.some(v=>!publicAddress(v)))throw new Error('address_rejected');
    const remaining=30000-(Date.now()-start);if(remaining<=0)throw new Error('web_timeout');
    let timer:ReturnType<typeof setTimeout>|undefined;
    const response=await Promise.race([this.transport.get(u.href,ips,{connectMs:10000,totalMs:remaining,maxDecodedBytes:MAX}),new Promise<never>((_,reject)=>{timer=setTimeout(()=>reject(new Error('web_timeout')),remaining)})]).finally(()=>clearTimeout(timer));
    check();if(!ips.includes(response.peer)||!publicAddress(response.peer))throw new Error('peer_rebinding_rejected');
    if(response.elapsedMs>remaining||Date.now()-start>30000)throw new Error('web_timeout');
    if(response.decodedBytes!==response.body.byteLength||response.decodedBytes>MAX)throw new Error('response_budget_exceeded');
    if([301,302,303,307,308].includes(response.status)){if(hop===5||!response.location)throw new Error('redirect_limit');url=new URL(response.location,u).href;checkedTarget(url,check());continue;}
    if(response.status!==200)throw new Error(response.status===401||response.status===403?'authentication_required':'http_unavailable');
    if(!['text/html','text/plain'].includes(response.contentType.split(';')[0]))throw new Error('mime_unsupported');
    check();return {originalUrl:raw,finalUrl:u.href,generation,fetchedAt:Date.now(),body:response.body,status:'fetched',recursive:false};
   }throw new Error('redirect_limit');
  }finally{this.running--;}
 }
}
