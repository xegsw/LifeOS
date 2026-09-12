import {readFile,writeFile} from 'node:fs/promises';
import {stripTypeScriptTypes} from 'node:module';
const root=new URL('../candidate/',import.meta.url);
for(const name of ['core','source_icons','health_context','health_conversation','health_ui','controlled_conversation','settings_view']){
 const source=await readFile(new URL(`application/${name}.ts`,root),'utf8');
 const js=stripTypeScriptTypes(source,{mode:'transform'}).replace(/from (['"])(\.\/[^'"]+)\.ts\1/g,'from $1$2.js$1');
 await writeFile(new URL(`ui/${name}.js`,root),js);
}

await writeFile(new URL('ui/health_aux.js',root),await readFile(new URL('application/health_aux.js',root)));
