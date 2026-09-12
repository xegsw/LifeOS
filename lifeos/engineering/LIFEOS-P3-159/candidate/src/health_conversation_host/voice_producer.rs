//! Host serialized ASR producer adapter. No device startup, policy grant or IPC entry.
use super::*;
use crate::voice::{audio::{WakeDetector,VadDetector},worker::{Worker,AudioEvent},native::Input,gateway::{Gateway,Transport,Binding,Frame},budget::Purpose};
use zeroize::Zeroize;
pub(super) enum ProducerEvent{Woke,PlaybackInterruption,AsrStarted}
pub(super) struct VoiceProducer<W:WakeDetector,V:VadDetector>{
 pub(super) worker:Worker<W,V>,session:String,generation:u64,revision:u64,
 asr:Option<(Binding,u64)>,closed:bool,
}
impl<W:WakeDetector,V:VadDetector> VoiceProducer<W,V>{
 pub(super) fn attach(s:&Store,worker:Worker<W,V>,session:&str,generation:u64,revision:u64)->R<Self>{
  s.voice_session(session,generation,revision)?;
  Ok(Self{worker,session:session.into(),generation,revision,asr:None,closed:false})
 }
 pub(super) fn shutdown(&mut self,g:&mut Gateway,net:&mut dyn Transport){
  g.cancel(Purpose::Asr,net);self.asr=None;self.worker.release();self.closed=true;
 }
 fn check(&self,s:&Store)->R<()>{if self.closed{return Err(error("voice_producer_closed"))}s.voice_session(&self.session,self.generation,self.revision).map(|_|())}
 pub(super) fn input(&mut self,s:&Store,g:&mut Gateway,net:&mut dyn Transport,input:Input,at:u64)->R<Vec<ProducerEvent>>{
  self.input_with_stop(s,g,net,input,at,||{})
 }
 pub(super) fn input_with_stop(&mut self,s:&Store,g:&mut Gateway,net:&mut dyn Transport,input:Input,at:u64,mut stop_native:impl FnMut())->R<Vec<ProducerEvent>>{
  let result=(||{
   let events=match input{Input::Samples(mut pcm)=>{let valid=self.check(s);if let Err(e)=valid{pcm.zeroize();return Err(e)}let events=self.worker.accept(&pcm,at);pcm.zeroize();events},Input::DeviceStopped(_)=>return Err(error("voice_device_unavailable"))};
   let mut out=vec![];
   for event in events{self.check(s)?;match event{
    AudioEvent::Woke{generation}=>{if generation!=self.worker.session.generation{return Err(error("voice_producer_stale"))}out.push(ProducerEvent::Woke)},
    AudioEvent::Interrupted=>{stop_native();out.push(ProducerEvent::PlaybackInterruption)},
    AudioEvent::Error(_)=>return Err(error("voice_audio_rejected")),
    AudioEvent::Utterance{generation,audio}=>{
     if self.asr.is_some()||generation!=self.worker.session.generation{return Err(error("voice_producer_stale"))}
     let local=self.worker.session.begin_asr().map_err(error)?;
     let binding=s.voice_gateway_begin_asr(g,&self.session,self.generation,self.revision,audio,net)?;
     self.asr=Some((binding,local));out.push(ProducerEvent::AsrStarted);
    }
   }}Ok(out)
  })();if result.is_err(){self.shutdown(g,net)}result
 }
 /// Caller retains other-purpose frames for the speech owner. A terminal frame
 /// must also call NativeTransport.completed after this method (even on error).
 pub(super) fn accepts(&self,id:&str)->bool{self.asr.as_ref().is_some_and(|(b,_)|b.request_id==id)}
 pub(super) fn http(&mut self,s:&Store,g:&mut Gateway,net:&mut dyn Transport,id:&str,mut frame:Frame)->R<Option<Value>>{
  if !self.accepts(id){if let Frame::Data(v)=&mut frame{v.zeroize();}return Err(error("stale_response"))}
  let result=(||{self.check(s)?;let local=self.asr.as_ref().unwrap().1;if local!=self.worker.session.generation{return Err(error("voice_producer_stale"))}
   let turn=s.voice_gateway_poll_asr(g,id,frame,net)?;
   if let Some(turn)=turn{
    self.worker.session.asr_final(local,true).map_err(error)?;self.asr=None;
    // The original interaction transaction owns the turn/preview. Audio never writes Actions.
    let result=s.interaction_dispatch("capture_record",json!({"version":"interaction-v1","operation":"submit_user_turn","payload":turn}))?;
    Ok(Some(result))
   }else{Ok(None)}
  })();if result.is_err(){self.shutdown(g,net)}result
 }
}

pub(super) trait ProducerTransport:Transport{
 fn next(&mut self)->Option<(String,Frame)>;
 fn completed(&mut self,id:&str);
 fn healthy(&mut self)->bool;
}
impl<C:crate::voice::native::CredentialAccess> ProducerTransport for crate::voice::native::NativeTransport<C>{
 fn next(&mut self)->Option<(String,Frame)>{self.events.try_recv().ok()}
 fn completed(&mut self,id:&str){crate::voice::native::NativeTransport::completed(self,id)}
 fn healthy(&mut self)->bool{crate::voice::native::NativeTransport::healthy(self)}
}
impl<W:WakeDetector,V:VadDetector> VoiceProducer<W,V>{
 pub(super) fn drain_audio(&mut self,s:&Store,g:&mut Gateway,net:&mut dyn Transport,audio:&mut crate::voice::native::NativeAudio,at:u64)->R<Vec<ProducerEvent>>{
  if !audio.healthy(){self.shutdown(g,net);audio.stop();return Err(error("voice_device_unavailable"))}
  let mut events=vec![];for _ in 0..8{let Ok(input)=audio.events.try_recv()else{break};match self.input_with_stop(s,g,net,input,at,||audio.interrupt()){Ok(v)=>{let interrupted=v.iter().any(|e|matches!(e,ProducerEvent::PlaybackInterruption));events.extend(v);if interrupted{audio.interrupt();break;}},Err(e)=>{audio.stop();return Err(e)}}}Ok(events)
 }
 /// Bounded serialized transport drain. Other-purpose frames retain their exact
 /// request IDs and are returned to the existing Host speech/playback owner.
 pub(super) fn drain_http<N:ProducerTransport>(&mut self,s:&Store,g:&mut Gateway,net:&mut N)->R<(Vec<Value>,Vec<(String,Frame)>)>{
  if !net.healthy(){self.shutdown(g,net);return Err(error("voice_transport_unavailable"))}
  let mut turns=vec![];let mut other=vec![];
  for _ in 0..16{let Some((id,frame))=net.next()else{break};if !self.accepts(&id){other.push((id,frame));continue;}
   let terminal=matches!(&frame,Frame::Eof|Frame::Failure);let result=self.http(s,g,net,&id,frame);
   if terminal||result.is_err(){net.completed(&id)}
   if let Some(v)=result?{turns.push(v)}
  }Ok((turns,other))
 }
}
#[cfg(test)]mod tests{
 use super::*;use crate::voice::{audio::FRAME,session::Policy,budget::Ledger,mimo::RequestBody};use std::{rc::Rc,cell::Cell,collections::VecDeque};
 struct Wake(bool);impl WakeDetector for Wake{fn accept(&mut self,_:&[f32])->Result<bool,&'static str>{Ok(std::mem::replace(&mut self.0,false))}fn reset(&mut self){}}
 struct Vad(Rc<Cell<bool>>);impl VadDetector for Vad{fn speech(&mut self,_:&[f32])->Result<bool,&'static str>{Ok(self.0.get())}fn reset(&mut self){}}
 #[derive(Default)]struct Net{starts:Vec<String>,cancelled:Vec<String>,done:Vec<String>,frames:VecDeque<(String,Frame)>}
 impl Transport for Net{fn start(&mut self,id:&str,_:&str,_:RequestBody)->Result<(),&'static str>{self.starts.push(id.into());Ok(())}fn cancel(&mut self,id:&str){self.cancelled.push(id.into());}}
 impl ProducerTransport for Net{fn next(&mut self)->Option<(String,Frame)>{self.frames.pop_front()}fn completed(&mut self,id:&str){self.done.push(id.into())}fn healthy(&mut self)->bool{true}}
 fn setup()->(Store,VoiceProducer<Wake,Vad>,Rc<Cell<bool>>){let s=super::super::controlled_tests::store();put(&s.c,"sources","voice:policy",&json!({"scope":"A_contract_fake","enabled":true,"asr":true,"tts":true,"sessionTurn":true,"revision":1})).unwrap();put(&s.c,"sources","voice:session:producer",&json!({"state":"active","generation":1,"policyRevision":1})).unwrap();put(&s.c,"sources","voice:budget",&json!({"kind":"voice_budget","ledger":Ledger::default()})).unwrap();let speech=Rc::new(Cell::new(true));let mut worker=Worker::new(Wake(true),Vad(speech.clone()));worker.session.policy(Policy{enabled:true,asr:true,tts:true,session_turn:true,revision:1},0);worker.session.ready(true,true,true).unwrap();let p=VoiceProducer::attach(&s,worker,"producer",1,1).unwrap();(s,p,speech)}
 fn utterance(s:&Store,p:&mut VoiceProducer<Wake,Vad>,speech:&Cell<bool>,g:&mut Gateway,n:&mut Net){p.input(s,g,n,Input::Samples(vec![0.9;FRAME]),0).unwrap();for _ in 0..5{p.input(s,g,n,Input::Samples(vec![0.2;FRAME]),20).unwrap();}speech.set(false);for _ in 0..40{p.input(s,g,n,Input::Samples(vec![0.;FRAME]),40).unwrap();}assert_eq!(n.starts.len(),1);assert_ne!(p.asr.as_ref().unwrap().0.generation,p.asr.as_ref().unwrap().1);}
 #[test]fn voice_producer_full_audio_to_existing_preview_releases_terminal_transport_once(){let(s,mut p,speech)=setup();let mut g=Gateway::new();let mut n=Net::default();utterance(&s,&mut p,&speech,&mut g,&mut n);let id=n.starts[0].clone();let chunk=|delta:Value,finish:Value|format!("data: {}\n\n",json!({"id":"producer-fake","object":"chat.completion.chunk","model":"mimo-v2.5-asr","choices":[{"index":0,"delta":delta,"finish_reason":finish}]})).into_bytes();n.frames.push_back((id.clone(),Frame::Headers(200)));n.frames.push_back((id.clone(),Frame::Data(chunk(json!({"content":"讨论合成报告"}),Value::Null))));let(a,b)=p.drain_http(&s,&mut g,&mut n).unwrap();assert!(a.is_empty()&&b.is_empty());assert!(list(&s.c,"drafts",32).unwrap().is_empty());let mut done=chunk(json!({}),json!("stop"));done.extend(b"data: [DONE]\n\n");n.frames.push_back((id.clone(),Frame::Data(done)));n.frames.push_back((id.clone(),Frame::Eof));n.frames.push_back(("existing-tts-request".into(),Frame::Connecting));let(a,b)=p.drain_http(&s,&mut g,&mut n).unwrap();assert_eq!(a.len(),1);assert_eq!(a[0]["result"]["receipt"]["status"],"pending_authorization");assert_eq!(b.len(),1);assert_eq!(b[0].0,"existing-tts-request");assert_eq!(n.done,vec![id.clone()]);assert!(!p.accepts(&id));assert_eq!(list(&s.c,"drafts",32).unwrap().len(),1);assert!(Store::actions(&s.c).unwrap().is_empty());}
 #[test]fn voice_producer_revocation_device_loss_and_stale_ids_never_submit(){for device in [false,true]{let(s,mut p,speech)=setup();let mut g=Gateway::new();let mut n=Net::default();utterance(&s,&mut p,&speech,&mut g,&mut n);assert!(p.http(&s,&mut g,&mut n,"foreign",Frame::Eof).is_err());assert!(n.cancelled.is_empty());if !device{put(&s.c,"sources","voice:session:producer",&json!({"state":"closed","generation":2,"policyRevision":1})).unwrap();}let input=if device{Input::DeviceStopped(-1)}else{Input::Samples(vec![0.;FRAME])};assert!(p.input(&s,&mut g,&mut n,input,60).is_err());assert_eq!(n.cancelled.len(),1);assert!(p.closed);assert!(list(&s.c,"drafts",32).unwrap().is_empty());assert_eq!(get(&s.c,"sources","voice:budget").unwrap().unwrap()["ledger"]["reservations"].as_array().unwrap().len(),1);}}
}
