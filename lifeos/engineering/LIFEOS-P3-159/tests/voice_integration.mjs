import test from 'node:test';import assert from 'node:assert/strict';
import {OfflineVoiceApplication} from '../candidate/ui/voice_application.js';
import {InteractionApplication} from '../candidate/ui/interaction_application.js';
import {readFileSync} from 'node:fs';import {createHash} from 'node:crypto';
test('fixed native v4 delta preserves prior voice lineage and exact current sources',()=>{
 const load=p=>JSON.parse(readFileSync(new URL(p,import.meta.url)));
 const previous=load('../contracts/voice-A2-v2/delta_manifest_v2.json');previous.files['src/voice/worker.rs']='544a6f3f1ec0d58d46e7862df27d683c422ce08391f697c50dd29cd4cd7c28db';
 const bytes=readFileSync(new URL('../contracts/voice-native-a38a90cf/delta_manifest_v4.json',import.meta.url));assert.equal(createHash('sha256').update(bytes).digest('hex'),'c71fa2b9a92c64eef99223fe9d99c45f116e7df41e1d37f585a323bb7e4af8eb');
 const current=JSON.parse(bytes),delta=load('../contracts/voice-native-a38a90cf/delta_since_93c98bb0.json');assert.equal(Object.keys(delta.added).length,1);assert.equal(Object.keys(delta.modified).length,2);assert.deepEqual(delta.removed,[]);
 for(const[p,v]of Object.entries(delta.modified)){assert.equal(previous.files[p],v.before_sha256);previous.files[p]=v.after_sha256;}Object.assign(previous.files,delta.added);assert.deepEqual(previous.files,current.files);
 for(const[p,h]of Object.entries(current.files))assert.equal(createHash('sha256').update(readFileSync(new URL('../candidate/'+p,import.meta.url))).digest('hex'),h,p);
});
test('actual offline settings adapter denies all final/speech and never submits a business turn',async()=>{let submits=0;const calls=[];const interaction=new InteractionApplication(async()=>{submits++;throw Error('no business call expected')});const voice=new OfflineVoiceApplication(async(c,r)=>{calls.push([c,r]);return {version:1,status:{state:'disabled',sessionId:null,generation:0,policyRevision:0},settings:{available:false,enabled:false,asr:false,tts:false,sessionTurn:false,wakeWord:'LifeOS',keyConfigured:false,usageLabel:'A offline'}}},interaction);await voice.refresh();assert.equal(voice.canSubmit({}),false);assert.equal((voice.html().match(/ disabled/g)||[]).length,4);await assert.rejects(voice.speak({}));voice.dispose();assert.equal(submits,0);assert.deepEqual(calls,[['voice_status',{version:1,payload:{}}]]);});
