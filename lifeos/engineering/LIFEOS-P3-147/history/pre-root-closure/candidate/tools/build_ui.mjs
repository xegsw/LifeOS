import {stripTypeScriptTypes} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
for(const name of ['core','ui','web_source']) {
 const input=await readFile(new URL('../application/'+name+'.ts',import.meta.url),'utf8');
 const output=stripTypeScriptTypes(input,{mode:'transform'}).replaceAll('./core.ts','./core.js');
 await writeFile(new URL('../ui/'+name+'.js',import.meta.url),output);
}
