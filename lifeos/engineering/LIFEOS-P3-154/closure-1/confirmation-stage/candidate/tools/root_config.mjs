// Helpers follow the same immutable build profile. No root argument accepted.
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const helper=fileURLToPath(new URL('task_root.py',import.meta.url));
const run=action=>{const r=spawnSync('/usr/bin/python3',['-B',helper,action],{encoding:'utf8'});if(r.status!==0)throw Error('root_rejected');return r.stdout;};
const config=JSON.parse(run('describe'));
run('verify');
export const root=config.root;
export const profile=config.profile;
