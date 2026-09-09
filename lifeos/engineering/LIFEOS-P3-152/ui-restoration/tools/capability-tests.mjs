import assert from 'node:assert/strict';import {catalogCapability} from '../candidate/ui/settings_view.js';
const cases=[['openai','cloud',8],['google_gemini','cloud',8],['openrouter','cloud',6],['deepseek','cloud',5],['ollama','local',4],['lm_studio','local',4],['local_custom','local',3]];
for(const [id,mode,n] of cases)assert.equal(Array.from({length:8},(_,i)=>catalogCapability(id,mode,i)).filter(Boolean).length,n);
console.log(JSON.stringify({passed:cases.length,total:cases.length,scope:'143 capability metadata parity; no runtime support assertion'}));
