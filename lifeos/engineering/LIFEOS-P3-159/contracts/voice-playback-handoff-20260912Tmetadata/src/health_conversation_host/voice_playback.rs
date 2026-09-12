//! Serialized Host playback owner. Port callbacks never become business authorization.
use super::*;
use crate::{interaction_contract::SpeechOutputRequest,voice::{audio::Playback,native::{NativeAudio,PlaybackStatus,PlaybackFeedback}}};
pub(super) trait PlaybackPort{
 fn healthy(&mut self)->bool;
 fn interrupt(&mut self);
 fn generation(&self)->u64;
 fn enqueue(&mut self,g:u64,pcm:&[u8])->Result<u64,&'static str>;
 fn status(&self,g:u64)->Result<PlaybackStatus,&'static str>;
 fn seal(&mut self,g:u64)->Result<(),&'static str>;
 fn feedback(&mut self)->Option<PlaybackFeedback>;
}
impl PlaybackPort for NativeAudio{
 fn healthy(&mut self)->bool{NativeAudio::healthy(self)}
 fn interrupt(&mut self){NativeAudio::interrupt(self)}
 fn generation(&self)->u64{self.playback_generation()}
 fn enqueue(&mut self,g:u64,pcm:&[u8])->Result<u64,&'static str>{self.enqueue_for(g,pcm)}
 fn status(&self,g:u64)->Result<PlaybackStatus,&'static str>{self.playback_status(g)}
 fn seal(&mut self,g:u64)->Result<(),&'static str>{self.finish_stream(g)}
 fn feedback(&mut self)->Option<PlaybackFeedback>{self.poll_playback()}
}
pub(super) struct VoicePlayback{
 request:SpeechOutputRequest,
 local:Playback,
 local_epoch:u64,
 native_epoch:u64,
 accepted:u64,
 consumed:u64,
 tokens:std::collections::HashSet<u64>,
 eof:bool,
 sealed:bool,
 closed:bool,
}
impl VoicePlayback{
 // Attach only after existing Host Gateway begin; never opens the device or starts a second POST.
 pub(super) fn attach(s:&Store,request:SpeechOutputRequest,port:&mut dyn PlaybackPort,visible:bool)->R<Self>{
  s.voice_validate_playback(&request,visible)?;if !port.healthy(){return Err(error("voice_device_unavailable"))}
  port.interrupt();let native_epoch=port.generation();let mut local=Playback::new();let local_epoch=local.begin();
  Ok(Self{request,local,local_epoch,native_epoch,accepted:0,consumed:0,tokens:std::collections::HashSet::new(),eof:false,sealed:false,closed:false})
 }
 fn check(&self,s:&Store,port:&mut dyn PlaybackPort,visible:bool)->R<()>{
  if self.closed||!port.healthy()||port.generation()!=self.native_epoch{return Err(error("voice_playback_stale"))}s.voice_validate_playback(&self.request,visible)
 }
 fn abort(&mut self,port:&mut dyn PlaybackPort){self.local.stop();port.interrupt();self.tokens.clear();self.closed=true;}
 pub(super) fn cancel(&mut self,port:&mut dyn PlaybackPort){self.abort(port)}
 pub(super) fn stop_with_host(&mut self,s:&Store,g:&mut crate::voice::gateway::Gateway,net:&mut dyn crate::voice::gateway::Transport,port:&mut dyn PlaybackPort,reason:crate::interaction_contract::InterruptionReason)->R<Value>{
  self.abort(port);
  let event=crate::interaction_contract::SpeechInterrupted{schema_version:"interaction-v1".into(),event_id:crate::conversation_store::uid("voice-stop"),session_id:self.request.session_id.clone(),session_generation:self.request.session_generation,speech_request_id:self.request.request_id.clone(),assistant_turn_ref:self.request.assistant_turn_ref.clone(),reason,occurred_at:super::interaction::iso(now())?,played_milliseconds:None};
  s.voice_gateway_interrupt_tts(g,event,net)
 }
 // Serialized owner passes the outcome from exactly one Host Gateway poll.
 pub(super) fn receive(&mut self,s:&Store,id:&str,outcome:R<crate::voice::gateway::Outcome>,g:&mut crate::voice::gateway::Gateway,net:&mut dyn crate::voice::gateway::Transport,port:&mut dyn PlaybackPort,visible:bool)->R<()>{
  if id!=self.request.request_id{return Err(error("stale_response"))}
  let result=(||{match outcome?{crate::voice::gateway::Outcome::Parts(parts)=>{for part in parts{if let crate::voice::mimo::Part::Pcm(bytes)=part{let bytes=zeroize::Zeroizing::new(bytes);self.accept_pcm(s,id,&bytes,port,visible)?;}}Ok(())},crate::voice::gateway::Outcome::Complete=>self.http_complete(s,id,port,visible),crate::voice::gateway::Outcome::Pending=>Ok(()),_=>Err(error("voice_output_invalidated"))}})();
  if result.is_err(){let _=self.stop_with_host(s,g,net,port,crate::interaction_contract::InterruptionReason::OutputInvalidated);}result
 }
 pub(super) fn poll_with_host(&mut self,s:&Store,g:&mut crate::voice::gateway::Gateway,net:&mut dyn crate::voice::gateway::Transport,port:&mut dyn PlaybackPort,visible:bool)->R<bool>{
  let result=self.poll(s,port,visible);if result.is_err(){let _=self.stop_with_host(s,g,net,port,crate::interaction_contract::InterruptionReason::OutputInvalidated);}result
 }

 pub(super) fn accept_pcm(&mut self,s:&Store,request_id:&str,pcm:&[u8],port:&mut dyn PlaybackPort,visible:bool)->R<()>{
  if request_id!=self.request.request_id{return Err(error("stale_response"))}
  let result=(||{self.check(s,port,visible)?;if self.eof{return Err(error("voice_stream_closed"))}self.local.push(self.local_epoch,pcm).map_err(error)?;self.pump_inner(s,port,visible)})();if result.is_err(){self.abort(port)}result
 }
 fn pump_inner(&mut self,s:&Store,port:&mut dyn PlaybackPort,visible:bool)->R<()>{
  self.check(s,port,visible)?;
  let status=port.status(self.native_epoch).map_err(error)?;
  if status.generation!=self.native_epoch||status.queued_samples>48000||status.available_samples!=48000-status.queued_samples||status.consumed_samples>self.accepted{return Err(error("voice_playback_status_invalid"))}
  let amount=(status.available_samples as usize).min(self.local.queued());
  if amount>0{
   self.check(s,port,visible)?;let samples=self.local.drain(amount);
   let pcm=zeroize::Zeroizing::new(samples.0.iter().flat_map(|x|x.to_le_bytes()).collect::<Vec<u8>>());
   let token=port.enqueue(self.native_epoch,&pcm).map_err(error)?;
   if token==0||!self.tokens.insert(token){return Err(error("voice_playback_token_invalid"))}self.accepted+=amount as u64;
  }
  if self.eof&&self.local.queued()==0&&!self.sealed{self.check(s,port,visible)?;port.seal(self.native_epoch).map_err(error)?;self.sealed=true;}
  Ok(())
 }
 pub(super) fn http_complete(&mut self,s:&Store,request_id:&str,port:&mut dyn PlaybackPort,visible:bool)->R<()>{
  if request_id!=self.request.request_id{return Err(error("stale_response"))}
  let result=(||{self.check(s,port,visible)?;if self.eof{return Err(error("voice_stream_closed"))}self.eof=true;self.pump_inner(s,port,visible)})();if result.is_err(){self.abort(port)}result
 }
 // Called by serialized owner for timer/feedback even when no new HTTP frames arrive.
 pub(super) fn poll(&mut self,s:&Store,port:&mut dyn PlaybackPort,visible:bool)->R<bool>{
  if self.closed{return Ok(false)}
  let result=(||{
   self.check(s,port,visible)?;
   while let Some(f)=port.feedback(){
    if f.generation!=self.native_epoch{continue}
    self.check(s,port,visible)?;
    if f.consumed_samples<self.consumed||f.consumed_samples>self.accepted||f.queued_samples>48000{return Err(error("voice_playback_feedback_invalid"))}
    if f.drained{
     let status=port.status(self.native_epoch).map_err(error)?;
     if f.buffer_token!=0||!self.tokens.is_empty()||status.generation!=self.native_epoch||!self.eof||!self.sealed||self.local.queued()!=0||f.queued_samples!=0||!status.sealed||!status.drained||status.queued_samples!=0||status.available_samples!=48000||status.consumed_samples!=self.accepted||f.consumed_samples!=status.consumed_samples||self.accepted==0{return Err(error("voice_playback_completion_invalid"))}
     self.check(s,port,visible)?;s.voice_playback_completed(&self.request,visible)?;self.closed=true;self.local.stop();self.tokens.clear();return Ok(true)
    }
    if f.buffer_token==0||!self.tokens.remove(&f.buffer_token){return Err(error("voice_playback_token_invalid"))}self.consumed=f.consumed_samples;
   }
   self.pump_inner(s,port,visible)?;Ok(false)
  })();if result.is_err(){self.abort(port)}result
 }
}

impl Drop for VoicePlayback{fn drop(&mut self){self.local.stop();self.tokens.clear();}}
#[cfg(test)]mod tests{
 use super::*;use crate::voice::{gateway::{Gateway,Transport,Frame,Outcome},mimo::RequestBody};use std::collections::VecDeque;
 #[derive(Default)]struct Net{starts:usize,cancels:usize}
 impl Transport for Net{fn start(&mut self,_:&str,_:&str,_:RequestBody)->Result<(),&'static str>{self.starts+=1;Ok(())}fn cancel(&mut self,_:&str){self.cancels+=1;}}
 struct Sink{g:u64,next:u64,queued:u32,consumed:u64,sealed:bool,ok:bool,buffers:VecDeque<(u64,u32)>,events:VecDeque<PlaybackFeedback>}
 impl Sink{fn new()->Self{Self{g:7,next:1,queued:0,consumed:0,sealed:false,ok:true,buffers:VecDeque::new(),events:VecDeque::new()}}fn consume(&mut self){let(token,n)=self.buffers.pop_front().unwrap();self.queued-=n;self.consumed+=n as u64;self.events.push_back(PlaybackFeedback{generation:self.g,buffer_token:token,queued_samples:self.queued,consumed_samples:self.consumed,drained:false});if self.queued==0&&self.sealed{self.drained();}}fn drained(&mut self){self.events.push_back(PlaybackFeedback{generation:self.g,buffer_token:0,queued_samples:0,consumed_samples:self.consumed,drained:true});}}
 impl PlaybackPort for Sink{
  fn healthy(&mut self)->bool{self.ok}fn interrupt(&mut self){self.g+=1;self.queued=0;self.consumed=0;self.sealed=false;self.buffers.clear();self.events.clear();}fn generation(&self)->u64{self.g}
  fn enqueue(&mut self,g:u64,pcm:&[u8])->Result<u64,&'static str>{if g!=self.g||self.sealed||pcm.len()/2>48000-self.queued as usize{return Err("fake_sink_rejected")}let token=self.next;self.next+=1;let n=pcm.len() as u32/2;self.queued+=n;self.buffers.push_back((token,n));Ok(token)}
  fn status(&self,g:u64)->Result<PlaybackStatus,&'static str>{if g!=self.g{return Err("stale_audio")}Ok(PlaybackStatus{generation:g,queued_samples:self.queued,available_samples:48000-self.queued,consumed_samples:self.consumed,sealed:self.sealed,drained:self.sealed&&self.queued==0})}
  fn seal(&mut self,g:u64)->Result<(),&'static str>{if g!=self.g||self.sealed{return Err("fake_seal_rejected")}self.sealed=true;if self.queued==0{self.drained();}Ok(())}
  fn feedback(&mut self)->Option<PlaybackFeedback>{self.events.pop_front()}
 }
 fn fixture()->(Store,SpeechOutputRequest,Gateway,Net,Sink,VoicePlayback){let(s,reference)=super::super::voice_speech::tests::setup();let r=s.voice_register_speech("speech-fixture",1,1,&reference,true).unwrap();let mut g=Gateway::new();let mut n=Net::default();s.voice_gateway_begin_tts(&mut g,&r,&||true,&mut n).unwrap();let mut port=Sink::new();let player=VoicePlayback::attach(&s,r.clone(),&mut port,true).unwrap();assert_ne!(player.local_epoch,player.native_epoch);(s,r,g,n,port,player)}
 fn event(delta:Value,finish:Value)->Frame{Frame::Data(format!("data: {}\n\n",json!({"id":"playback-joint","object":"chat.completion.chunk","model":"mimo-v2.5-tts","choices":[{"index":0,"delta":delta,"finish_reason":finish}]})).into_bytes())}
 fn eof(s:&Store,r:&SpeechOutputRequest,g:&mut Gateway,n:&mut Net){s.voice_gateway_poll_tts(g,&r.request_id,event(json!({}),json!("stop")),&||true,n).unwrap();s.voice_gateway_poll_tts(g,&r.request_id,Frame::Data(b"data: [DONE]\n\n".to_vec()),&||true,n).unwrap();assert!(matches!(s.voice_gateway_poll_tts(g,&r.request_id,Frame::Eof,&||true,n).unwrap(),Outcome::Complete));}
 #[test]fn voice_playback_joint_requires_native_drained_after_gateway_eof(){let(s,r,mut g,mut n,mut port,mut player)=fixture();s.voice_gateway_poll_tts(&mut g,&r.request_id,Frame::Headers(200),&||true,&mut n).unwrap();let Outcome::Parts(parts)=s.voice_gateway_poll_tts(&mut g,&r.request_id,event(json!({"audio":{"id":"p","data":"AAABAA=="}}),Value::Null),&||true,&mut n).unwrap() else{panic!()};player.receive(&s,&r.request_id,Ok(Outcome::Parts(parts)),&mut g,&mut n,&mut port,true).unwrap();assert_eq!(port.queued,2);eof(&s,&r,&mut g,&mut n);player.receive(&s,&r.request_id,Ok(Outcome::Complete),&mut g,&mut n,&mut port,true).unwrap();assert!(!player.poll(&s,&mut port,true).unwrap());assert_eq!(get(&s.c,"sources",&format!("voice:speech:{}",r.request_id)).unwrap().unwrap()["state"],"draining");port.consume();assert!(player.poll_with_host(&s,&mut g,&mut n,&mut port,true).unwrap());assert!(!player.poll_with_host(&s,&mut g,&mut n,&mut port,true).unwrap());assert_eq!(get(&s.c,"sources",&format!("voice:speech:{}",r.request_id)).unwrap().unwrap()["state"],"complete");assert_eq!(n.starts,1);assert!(Store::actions(&s.c).unwrap().is_empty());}
 #[test]fn voice_playback_backpressure_delays_seal_until_all_local_pcm_is_accepted(){let(s,r,mut g,mut n,mut port,mut player)=fixture();s.voice_gateway_poll_tts(&mut g,&r.request_id,Frame::Headers(200),&||true,&mut n).unwrap();s.voice_gateway_poll_tts(&mut g,&r.request_id,event(json!({"audio":{"id":"p","data":"AAABAA=="}}),Value::Null),&||true,&mut n).unwrap();player.accept_pcm(&s,&r.request_id,&vec![0;96000],&mut port,true).unwrap();player.accept_pcm(&s,&r.request_id,&[0;8],&mut port,true).unwrap();assert_eq!(player.local.queued(),4);eof(&s,&r,&mut g,&mut n);player.http_complete(&s,&r.request_id,&mut port,true).unwrap();assert!(!port.sealed);port.consume();assert!(!player.poll(&s,&mut port,true).unwrap());assert!(port.sealed);assert_eq!(port.queued,4);port.consume();assert!(player.poll(&s,&mut port,true).unwrap());}
 #[test]fn voice_playback_old_feedback_revocation_and_overflow_cannot_complete_current(){for mode in ["old","revoked","overflow","premature"]{let(s,r,_g,_n,mut port,mut player)=fixture();player.accept_pcm(&s,&r.request_id,&[0;4],&mut port,true).unwrap();if mode=="old"{port.events.push_back(PlaybackFeedback{generation:port.g-1,buffer_token:0,consumed_samples:2,queued_samples:0,drained:true});assert!(!player.poll(&s,&mut port,true).unwrap());assert_eq!(port.queued,2);}else{if mode=="revoked"{let mut policy=get(&s.c,"sources","voice:policy").unwrap().unwrap();policy["tts"]=json!(false);put(&s.c,"sources","voice:policy",&policy).unwrap();}else if mode=="overflow"{port.ok=false;}else{port.events.push_back(PlaybackFeedback{generation:port.g,buffer_token:0,consumed_samples:2,queued_samples:0,drained:true});}assert!(player.poll(&s,&mut port,true).is_err());assert_eq!(port.queued,0);assert!(player.closed);}assert_ne!(get(&s.c,"sources",&format!("voice:speech:{}",r.request_id)).unwrap().unwrap()["state"],"complete");}}
 #[test]fn voice_playback_failure_wrapper_stops_only_its_host_output(){let(s,r,mut g,mut n,mut port,mut player)=fixture();player.accept_pcm(&s,&r.request_id,&[0;4],&mut port,true).unwrap();assert!(player.receive(&s,"late-other-request",Err(error("provider_timeout")),&mut g,&mut n,&mut port,true).is_err());assert_eq!(n.cancels,0);port.ok=false;assert!(player.poll_with_host(&s,&mut g,&mut n,&mut port,true).is_err());assert_eq!(n.cancels,1);assert_eq!(port.queued,0);assert_eq!(get(&s.c,"sources",&format!("voice:speech:{}",r.request_id)).unwrap().unwrap()["state"],"interrupted");assert!(Store::actions(&s.c).unwrap().is_empty());}

}
