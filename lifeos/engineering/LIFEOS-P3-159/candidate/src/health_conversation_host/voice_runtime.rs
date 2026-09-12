//! One serialized Host owner for audio, ASR, speech and playback. A-only grants.
use super::*;
use super::{voice_producer::{VoiceProducer,ProducerTransport,ProducerEvent},voice_playback::{VoicePlayback,PlaybackPort}};
use crate::{interaction_contract::{Ref,SpeechOutputRequest,InterruptionReason},voice::{audio::{WakeDetector,VadDetector},worker::Worker,gateway::{Gateway,Frame},native::{Input,NativeAudio},budget::Purpose}};
use zeroize::Zeroize;
pub(super) trait RuntimeAudio:PlaybackPort{fn input(&mut self)->Option<Input>;fn stop(&mut self);}
impl RuntimeAudio for NativeAudio{fn input(&mut self)->Option<Input>{self.events.try_recv().ok()}fn stop(&mut self){NativeAudio::stop(self)}}
pub(super) struct VoiceRuntime<W:WakeDetector,V:VadDetector,A:RuntimeAudio,N:ProducerTransport>{
 producer:VoiceProducer<W,V>,gateway:Gateway,audio:A,net:N,
 session:String,generation:u64,revision:u64,speech:Option<(SpeechOutputRequest,VoicePlayback)>,closed:bool,
}
impl<W:WakeDetector,V:VadDetector,A:RuntimeAudio,N:ProducerTransport> VoiceRuntime<W,V,A,N>{
 pub(super) fn attach(s:&Store,worker:Worker<W,V>,audio:A,net:N,session:&str,generation:u64,revision:u64)->R<Self>{Ok(Self{producer:VoiceProducer::attach(s,worker,session,generation,revision)?,gateway:Gateway::new(),audio,net,session:session.into(),generation,revision,speech:None,closed:false})}
 pub(super) fn stop_speech(&mut self,s:&Store,reason:InterruptionReason)->R<()>{
  let result=if let Some((r,mut playback))=self.speech.take(){let result=playback.stop_with_host(s,&mut self.gateway,&mut self.net,&mut self.audio,reason).map(|_|());self.net.completed(&r.request_id);result}else{self.audio.interrupt();Ok(())};
  self.producer.worker.session.interrupt(now().max(0) as u64);result
 }
 pub(super) fn shutdown(&mut self,s:&Store){let _=self.stop_speech(s,InterruptionReason::SessionClosed);self.producer.shutdown(&mut self.gateway,&mut self.net);self.audio.stop();self.closed=true;}
 pub(super) fn speak(&mut self,s:&Store,reference:&Ref,visible:bool)->R<()>{
  if self.closed||self.speech.is_some(){return Err(error("voice_runtime_busy"))}
  let local=self.producer.worker.session.generation;
  if !self.producer.worker.session.may_speak(local,self.revision,false,visible){return Err(error("speech_denied"))}
  let request=s.voice_register_speech(&self.session,self.generation,self.revision,reference,visible)?;
  let result=(||{s.voice_gateway_begin_tts(&mut self.gateway,&request,&||visible,&mut self.net)?;
   let playback=VoicePlayback::attach(s,request.clone(),&mut self.audio,visible)?;
   self.speech=Some((request.clone(),playback));
   self.producer.worker.session.speak(local,self.revision,false,visible).map_err(error)?;Ok(())})();
  if result.is_err(){
   self.audio.interrupt();
   let event=crate::interaction_contract::SpeechInterrupted{schema_version:"interaction-v1".into(),event_id:crate::conversation_store::uid("voice-start-failed"),session_id:request.session_id.clone(),session_generation:request.session_generation,speech_request_id:request.request_id.clone(),assistant_turn_ref:request.assistant_turn_ref.clone(),reason:InterruptionReason::OutputInvalidated,occurred_at:super::interaction::iso(now())?,played_milliseconds:None};
   let _=s.voice_gateway_interrupt_tts(&mut self.gateway,event,&mut self.net);self.gateway.cancel(Purpose::Tts,&mut self.net);self.net.completed(&request.request_id);self.shutdown(s)
  }result
 }
 pub(super) fn tick(&mut self,s:&Store,visible:bool)->R<Vec<Value>>{
  let result=self.tick_inner(s,visible);if result.is_err(){self.shutdown(s)}result
 }
 fn tick_inner(&mut self,s:&Store,visible:bool)->R<Vec<Value>>{
  if self.closed{return Err(error("voice_runtime_closed"))}s.voice_session(&self.session,self.generation,self.revision)?;
  if !self.audio.healthy()||!self.net.healthy(){return Err(error("voice_port_unavailable"))}
  for _ in 0..8{let Some(input)=self.audio.input()else{break};let audio=&mut self.audio;let events=self.producer.input_with_stop(s,&mut self.gateway,&mut self.net,input,now().max(0) as u64,||audio.interrupt())?;for event in events{if matches!(event,ProducerEvent::PlaybackInterruption){self.stop_speech(s,InterruptionReason::UserSpeech)?;}}}
  let (turns,other)=self.producer.drain_http(s,&mut self.gateway,&mut self.net)?;
  for (id,mut frame) in other{
   let Some((request,playback))=self.speech.as_mut()else{if let Frame::Data(v)=&mut frame{v.zeroize();}self.net.completed(&id);continue};
   if request.request_id!=id{if let Frame::Data(v)=&mut frame{v.zeroize();}self.net.completed(&id);continue;}
   let terminal=matches!(&frame,Frame::Eof|Frame::Failure);
   let outcome=s.voice_gateway_poll_tts(&mut self.gateway,&id,frame,&||visible,&mut self.net);
   let result=playback.receive(s,&id,outcome,&mut self.gateway,&mut self.net,&mut self.audio,visible);
   if terminal||result.is_err(){self.net.completed(&id)}result?;
  }
  if let Some((_,playback))=self.speech.as_mut(){if playback.poll_with_host(s,&mut self.gateway,&mut self.net,&mut self.audio,visible)?{self.speech=None;let local=self.producer.worker.session.generation;self.producer.worker.session.interrupt(now().max(0) as u64);self.producer.worker.session.assistant_finished(local,now().max(0) as u64);}}
  Ok(turns)
 }
}
impl<W:WakeDetector,V:VadDetector,A:RuntimeAudio,N:ProducerTransport> Drop for VoiceRuntime<W,V,A,N>{fn drop(&mut self){self.gateway.cancel(Purpose::Asr,&mut self.net);self.gateway.cancel(Purpose::Tts,&mut self.net);self.audio.stop();self.producer.worker.release();}}
#[cfg(test)]mod tests{
 use super::*;use crate::voice::{session::Policy,mimo::RequestBody,gateway::Transport};use std::collections::VecDeque;
 struct Wake;impl WakeDetector for Wake{fn accept(&mut self,_:&[f32])->Result<bool,&'static str>{Ok(false)}fn reset(&mut self){}}
 struct Vad;impl VadDetector for Vad{fn speech(&mut self,_:&[f32])->Result<bool,&'static str>{Ok(false)}fn reset(&mut self){}}
 impl RuntimeAudio for super::super::voice_playback::tests::Sink{fn input(&mut self)->Option<Input>{None}fn stop(&mut self){self.interrupt()}}
 #[derive(Default)]struct Net{reject:bool,frames:VecDeque<(String,Frame)>,starts:Vec<String>,done:Vec<String>,cancelled:Vec<String>}
 impl Transport for Net{fn start(&mut self,id:&str,_:&str,_:RequestBody)->Result<(),&'static str>{self.starts.push(id.into());if self.reject{Err("fake_start_failure")}else{Ok(())}}fn cancel(&mut self,id:&str){self.cancelled.push(id.into())}}
 impl ProducerTransport for Net{fn next(&mut self)->Option<(String,Frame)>{self.frames.pop_front()}fn completed(&mut self,id:&str){self.done.push(id.into())}fn healthy(&mut self)->bool{true}}
 fn fixture()->(Store,Ref,VoiceRuntime<Wake,Vad,super::super::voice_playback::tests::Sink,Net>){let(s,r)=super::super::voice_speech::tests::setup();let mut policy=get(&s.c,"sources","voice:policy").unwrap().unwrap();policy["asr"]=json!(true);policy["sessionTurn"]=json!(true);put(&s.c,"sources","voice:policy",&policy).unwrap();let mut worker=Worker::new(Wake,Vad);worker.session.policy(Policy{enabled:true,asr:true,tts:true,session_turn:true,revision:1},0);worker.session.ready(true,true,true).unwrap();worker.session.wake(0).unwrap();let rt=VoiceRuntime::attach(&s,worker,super::super::voice_playback::tests::Sink::new(),Net::default(),"speech-fixture",1,1).unwrap();(s,r,rt)}
 fn chunk(delta:Value,finish:Value)->Frame{Frame::Data(format!("data: {}\n\n",json!({"id":"runtime-fake","object":"chat.completion.chunk","model":"mimo-v2.5-tts","choices":[{"index":0,"delta":delta,"finish_reason":finish}]})).into_bytes())}
 #[test]fn voice_runtime_tts_eof_waits_for_consumption_and_closes_same_host_output(){let(s,r,mut rt)=fixture();rt.speak(&s,&r,true).unwrap();let id=rt.net.starts[0].clone();for frame in [Frame::Headers(200),chunk(json!({"audio":{"id":"a","data":"AAABAA=="}}),Value::Null),chunk(json!({}),json!("stop")),Frame::Data(b"data: [DONE]\n\n".to_vec()),Frame::Eof]{rt.net.frames.push_back((id.clone(),frame));}assert!(rt.tick(&s,true).unwrap().is_empty());assert!(rt.speech.is_some());assert_eq!(get(&s.c,"sources",&format!("voice:speech:{id}")).unwrap().unwrap()["state"],"draining");assert_eq!(rt.net.done,vec![id.clone()]);rt.audio.consume();rt.tick(&s,true).unwrap();assert!(rt.speech.is_none());assert_eq!(get(&s.c,"sources",&format!("voice:speech:{id}")).unwrap().unwrap()["state"],"complete");assert!(Store::actions(&s.c).unwrap().is_empty());}
 #[test]fn voice_runtime_idle_revocation_and_user_stop_cancel_audio_without_business_changes(){for revoke in [false,true]{let(s,r,mut rt)=fixture();rt.speak(&s,&r,true).unwrap();let id=rt.net.starts[0].clone();if revoke{let mut policy=get(&s.c,"sources","voice:policy").unwrap().unwrap();policy["enabled"]=json!(false);put(&s.c,"sources","voice:policy",&policy).unwrap();assert!(rt.tick(&s,true).is_err());assert!(rt.closed);}else{rt.stop_speech(&s,InterruptionReason::UserStop).unwrap();assert!(!rt.closed);}assert!(rt.speech.is_none());assert!(rt.net.cancelled.contains(&id));assert!(Store::actions(&s.c).unwrap().is_empty());assert_ne!(get(&s.c,"sources",&format!("voice:speech:{id}")).unwrap().unwrap()["state"],"complete");}}
 #[test]fn voice_runtime_failed_start_closes_registered_speech_without_refunding(){let(s,r,mut rt)=fixture();rt.net.reject=true;assert!(rt.speak(&s,&r,true).is_err());assert!(rt.closed);let id=&rt.net.starts[0];assert_eq!(get(&s.c,"sources",&format!("voice:speech:{id}")).unwrap().unwrap()["state"],"failed");assert_eq!(get(&s.c,"sources","voice:budget").unwrap().unwrap()["ledger"]["reservations"].as_array().unwrap().len(),1);assert!(Store::actions(&s.c).unwrap().is_empty());}

}
