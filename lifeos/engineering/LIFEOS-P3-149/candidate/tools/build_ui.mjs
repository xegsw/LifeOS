import {stripTypeScriptTypes} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
for(const name of ['core','ui','web_source','source_conversation','conversation_flow','source_icons','health_view','source_ui']) {
 const input=await readFile(new URL('../application/'+name+'.ts',import.meta.url),'utf8');
 const output=stripTypeScriptTypes(input,{mode:'transform'}).replaceAll('./core.ts','./core.js').replaceAll('./source_conversation.ts','./source_conversation.js').replaceAll('./conversation_flow.ts','./conversation_flow.js').replaceAll('./source_icons.ts','./source_icons.js').replaceAll('./health_view.ts','./health_view.js');
 await writeFile(new URL('../ui/'+name+'.js',import.meta.url),output);
}
