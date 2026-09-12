import {test} from 'node:test';
import assert from 'node:assert/strict';
import {ConversationFlow} from '../candidate/ui/conversation_flow.js';
const old={requestId:'old',draftId:'old-draft',conversationId:'source-chat',turnId:'old-turn',revision:4,text:'old persisted draft'};
function setup(failures){let attempts=0;const writes=[];const flow=new ConversationFlow({open:async()=>{if(attempts++<failures)throw {code:'database_unavailable'};return {pendingDraft:{...old}}},call:async(c,o,p)=>writes.push({...p})},()=>{},async()=>{});return {flow,writes}}
test('IR-D2-001 failed open, user edit, successful retry with OLD pendingDraft',async()=>{const {flow,writes}=setup(1);try{await flow.start();flow.edit('new local draft');const expected={...flow.draft};await flow.start();await Promise.resolve();assert.deepEqual(flow.draft,expected);assert(writes.some(d=>d.text==='new local draft'));}finally{flow.dispose()}});
test('multiple failures and edits keep last user input including intentional empty draft',async()=>{const {flow}=setup(3);try{await flow.start();flow.edit('first');await flow.start();flow.edit('second');await flow.start();flow.edit('');const expected={...flow.draft};await flow.start();assert.deepEqual(flow.draft,expected);}finally{flow.dispose()}});
test('successful first recovery without edits restores stored draft',async()=>{const {flow}=setup(0);try{await flow.start();assert.deepEqual(flow.draft,old);}finally{flow.dispose()}});
test('failed retries without edits still recover stored draft',async()=>{const {flow}=setup(2);try{await flow.start();await flow.start();await flow.start();assert.deepEqual(flow.draft,old);}finally{flow.dispose()}});
test('input before initial start takes priority over persisted draft',async()=>{const {flow}=setup(0);try{flow.edit('typed before open');await flow.start();assert.equal(flow.draft.text,'typed before open');}finally{flow.dispose()}});
