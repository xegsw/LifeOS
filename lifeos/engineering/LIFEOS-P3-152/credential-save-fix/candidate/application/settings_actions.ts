// Only fixed codes reach presentation; backend payloads may contain sensitive details.
const messages:Record<string,string>={
 runtime_target_rejected:'本地存储目录未通过检查，保存已停止。',
 database_path_rejected:'本地凭据存储未通过检查，保存已停止。',
 database_unavailable:'本地存储暂不可用。',
 store_contract_mismatch:'本地存储结构未通过检查。',
 credential_invalid:'API Key 格式不正确，请检查输入。',
 credential_missing:'尚未保存 API Key。',
 credential_unavailable:'系统钥匙串暂不可用，请检查系统授权后重试。',
 credential_revision_conflict:'凭据状态已变化，请核对后再次保存。',
 credential_authentication_failed:'本地凭据无法解密，请重新保存。',
 credential_reference_rejected:'本地凭据引用未通过检查。',
 credential_cleanup_pending:'凭据清理尚未完成。',
 catalog_rejected:'请填写有效的模型名称和配置。',
 catalog_revision_conflict:'配置已变化，请核对后再次保存。',
 model_rejected:'模型名称格式不正确。',
 model_limit_reached:'已保存的模型数量达到上限。',
 settings_save_failed:'保存未完成，请重试。'
};
export function settingsError(e:any){const code=Object.hasOwn(messages,e?.code)?e.code:'settings_save_failed';return `${messages[code]}（${code}）`;}
export class SettingsActions {
 busy=false;notice='';
 constructor(private flow:any,private changed:()=>void){}
 async save(kind:'catalog'|'credential'|'delete',input:{value:string}|null,settings:any){
  if(this.busy)return;
  this.busy=true;this.notice='正在保存…';
  let credentialSaved=false,catalogSaved=false;
  const key=input?.value||'';
  const clear=()=>{credentialSaved=true;if(input&&input.value===key)input.value='';};
  this.changed();
  try{
   if(kind==='delete'){await this.flow.deleteCredential();this.notice='凭据已移除。';return;}
   if(kind==='catalog'){
    await this.flow.saveCatalog(settings,()=>{catalogSaved=true;});
    if(key&&settings.primary.mode==='cloud'&&settings.primary.providerId==='deepseek')await this.flow.saveCredential(key,clear);
   }else await this.flow.saveCredential(key,clear);
   this.notice=credentialSaved?(catalogSaved?'配置和 API Key 已保存。':'API Key 已保存。'):'配置已保存。';
  }catch(e){
   this.notice=(credentialSaved?'API Key 已保存，后续配置未完成。':catalogSaved?'配置已保存，后续保存未完成。':'')+settingsError(e);
  }finally{this.busy=false;this.changed();}
 }
}
