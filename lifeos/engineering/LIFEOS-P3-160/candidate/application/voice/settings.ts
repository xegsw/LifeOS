import type {VoiceStatus} from './consumer.ts';
const labels={disabled:'语音已关闭',wake_listening:'正在本地等待唤醒',capturing:'正在聆听',transcribing:'正在转写',awaiting_assistant:'正在思考',speaking:'正在朗读',recovering:'语音暂不可用，可继续打字'};
const esc=(s:string)=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]!));
export interface VoiceSettings {enabled:boolean;asr:boolean;tts:boolean;sessionTurn:boolean;wakeWord:string;keyConfigured:boolean;usageLabel:string;available:boolean;}
/** Mounted by the existing settings owner; contains no secret field or persistence. */
export function voiceSettings(v:VoiceSettings,s:VoiceStatus):string{
 const disabled=v.available?'':' disabled';
 const check=(name:string,text:string,on:boolean)=>`<label><input type="checkbox" data-voice-purpose="${name}"${on?' checked':''}${disabled}>${text}</label>`;
 return `<details class="voice-settings"><summary>语音</summary><p role="status" aria-live="polite">${labels[s.state]}</p>${check('enabled','启用语音',v.enabled)}<p>启用后，App 运行且未锁屏时使用麦克风在本地等待“${esc(v.wakeWord)}”。唤醒前音频仅留在内存，不上传。</p>${check('voice_asr.v1','允许向 MiMo 发送唤醒后的音频以转写',v.asr)}<p>录音可能包含环境声；请勿说出不愿上传的内容。</p>${check('voice_tts.v1','允许 MiMo 合成当前获准回答',v.tts)}${check('voice_session_turn.v1','允许已唤醒会话内自动发送转写',v.sessionTurn)}<p>${v.keyConfigured?'MiMo 已配置':'请通过现有模型设置配置 MiMo'} · ${esc(v.usageLabel)}</p><p>服务端保存与使用规则以适用条款为准，本地释放音频不代表服务端删除。</p><a href="https://mimo.mi.com/docs/quick-start/terms/user-agreement">服务条款</a><a href="https://mimo.mi.com/docs/quick-start/terms/privacy-policy">隐私政策</a>${v.available?'':'<p>离线工程验证阶段，真实语音尚未启用。</p>'}</details>`;
}
export function voiceStatus(s:VoiceStatus):string{return `<span role="status" aria-live="polite">${labels[s.state]}</span>${s.state==='speaking'?'<button type="button" data-voice-control="stop_playback">停止朗读</button>':''}`;}
