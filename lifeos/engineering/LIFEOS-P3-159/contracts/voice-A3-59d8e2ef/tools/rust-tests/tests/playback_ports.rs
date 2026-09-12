//! Contract fakes only: exercises existing voice ports, not production host/GUI.
use lifeos_voice_offline_tests::{audio::{Audio,Playback},budget::{BudgetStore,Ledger,Phase,Purpose},gateway::{Authority,Binding,Frame,Gateway,Outcome,Transport},mimo::{Part,RequestBody}};
use std::cell::Cell;
struct HostFake { revision: Cell<u64>, generation:u64 }
impl Authority for HostFake {
 fn check(&self,b:&Binding,_:Purpose)->Result<(), &'static str>{
  if b.session_id=="synthetic-session" && b.generation==self.generation && b.policy_revision==self.revision.get(){Ok(())}else{Err("revoked")}
 }
 fn projection(&self,b:&Binding)->Result<String,&'static str>{self.check(b,Purpose::Tts)?;Ok("合成的最终回复".into())}
 fn now(&self)->(u64,u64){(100,1)}
}
#[derive(Default)] struct StoreFake(Ledger);
impl BudgetStore for StoreFake {
 fn load(&self)->Result<Ledger,&'static str>{Ok(self.0.clone())}
 fn compare_save(&mut self,old:u64,new:Ledger)->Result<(),&'static str>{assert_eq!(old,self.0.revision);self.0=new;Ok(())}
}
#[derive(Default)] struct HttpFake { starts:Vec<String>, cancels:Vec<String> }
impl Transport for HttpFake {
 fn start(&mut self,id:&str,_:&str,body:RequestBody)->Result<(),&'static str>{assert!(!body.0.is_empty());self.starts.push(id.into());Ok(())}
 fn cancel(&mut self,id:&str){self.cancels.push(id.into())}
}
fn binding(id:&str)->Binding{Binding{request_id:id.into(),session_id:"synthetic-session".into(),generation:7,policy_revision:1}}
fn pcm()->Frame{Frame::Data(b"data: {\"id\":\"provider1\",\"object\":\"chat.completion.chunk\",\"model\":\"mimo-v2.5-tts\",\"choices\":[{\"index\":0,\"delta\":{\"audio\":{\"id\":\"audio1\",\"data\":\"AAABAA==\"}},\"finish_reason\":null}]}\n\n".to_vec())}
fn chunk(g:&mut Gateway,a:&HostFake,n:&mut HttpFake,id:&str)->Vec<u8>{
 g.poll(Purpose::Tts,id,Frame::Headers(200),a,n).unwrap();
 let Outcome::Parts(parts)=g.poll(Purpose::Tts,id,pcm(),a,n).unwrap() else{panic!()};
 parts.into_iter().find_map(|p|if let Part::Pcm(v)=p{Some(v)}else{None}).unwrap()
}
#[test]
fn streaming_output_interrupt_does_not_cancel_asr_or_accept_late_pcm(){
 let a=HostFake{revision:Cell::new(1),generation:7};let mut s=StoreFake::default();let mut n=HttpFake::default();let mut g=Gateway::new();let mut p=Playback::new();
 g.begin_asr(binding("asr"),Audio(vec![0;1600]),Phase::BDevelopment,&a,&mut s,&mut n).unwrap();
 g.begin_tts(binding("tts-old"),Phase::BDevelopment,&a,&mut s,&mut n).unwrap();
 let old=p.begin();let bytes=chunk(&mut g,&a,&mut n,"tts-old");p.push(old,&bytes).unwrap();assert_eq!(p.queued(),2);
 // Serialized host sequence: stop output first, cancel only TTS, retain input/business work.
 p.stop();g.cancel(Purpose::Tts,&mut n);assert_eq!(p.queued(),0);
 assert!(g.poll(Purpose::Tts,"tts-old",pcm(),&a,&mut n).is_err());
 assert!(g.poll(Purpose::Asr,"asr",Frame::Headers(200),&a,&mut n).is_ok());
 g.begin_tts(binding("tts-new"),Phase::BDevelopment,&a,&mut s,&mut n).unwrap();let current=p.begin();
 assert!(p.push(old,&bytes).is_err());
 assert!(g.poll(Purpose::Tts,"tts-old",pcm(),&a,&mut n).is_err());
 let fresh=chunk(&mut g,&a,&mut n,"tts-new");p.push(current,&fresh).unwrap();assert_eq!(p.queued(),2);
 assert_eq!(n.starts,vec!["asr","tts-old","tts-new"]);assert_eq!(n.cancels,vec!["tts-old"]);assert_eq!(s.0.reservations.len(),3);
}
#[test]
fn revoke_after_parser_before_sink_requires_authority_recheck(){
 let a=HostFake{revision:Cell::new(1),generation:7};let mut s=StoreFake::default();let mut n=HttpFake::default();let mut g=Gateway::new();let mut p=Playback::new();let b=binding("tts");
 g.begin_tts(b.clone(),Phase::BDevelopment,&a,&mut s,&mut n).unwrap();let pg=p.begin();let bytes=chunk(&mut g,&a,&mut n,"tts");
 a.revision.set(2);
 // Gateway checking alone cannot authorize already-returned PCM: sink owner checks again.
 if a.check(&b,Purpose::Tts).is_ok(){p.push(pg,&bytes).unwrap()}else{p.stop();g.cancel(Purpose::Tts,&mut n)}
 assert_eq!(p.queued(),0);assert!(p.push(pg,&bytes).is_err());assert!(g.poll(Purpose::Tts,"tts",Frame::Eof,&a,&mut n).is_err());
 assert_eq!(n.starts.len(),1);assert_eq!(n.cancels,vec!["tts"]);assert_eq!(s.0.reservations.len(),1);
}
#[test]
fn revoked_inflight_chunk_cancels_transport_without_returning_audio(){
 let a=HostFake{revision:Cell::new(1),generation:7};let mut s=StoreFake::default();let mut n=HttpFake::default();let mut g=Gateway::new();
 g.begin_tts(binding("tts"),Phase::BDevelopment,&a,&mut s,&mut n).unwrap();g.poll(Purpose::Tts,"tts",Frame::Headers(200),&a,&mut n).unwrap();a.revision.set(2);
 assert!(matches!(g.poll(Purpose::Tts,"tts",pcm(),&a,&mut n),Err("revoked")));assert_eq!(n.cancels,vec!["tts"]);assert_eq!(n.starts.len(),1);
}

#[test]
fn fake_native_frames_produce_one_utterance_then_gateway_final_only(){
 use lifeos_voice_offline_tests::{audio::{WakeDetector,VadDetector,FRAME},worker::{Worker,AudioEvent},session::Policy};
 use std::rc::Rc;
 struct Wake(bool);impl WakeDetector for Wake{fn accept(&mut self,_:&[f32])->Result<bool,&'static str>{Ok(std::mem::replace(&mut self.0,false))}fn reset(&mut self){}}
 struct Vad(Rc<Cell<bool>>);impl VadDetector for Vad{fn speech(&mut self,_:&[f32])->Result<bool,&'static str>{Ok(self.0.get())}fn reset(&mut self){}}
 let speech=Rc::new(Cell::new(true));let mut worker=Worker::new(Wake(true),Vad(speech.clone()));
 worker.session.policy(Policy{enabled:true,asr:true,tts:false,session_turn:true,revision:1},0);worker.session.ready(true,true,true).unwrap();
 // Synthetic callback chunks; no NativeAudio constructed and no permission requested.
 assert!(matches!(worker.accept(&[0.9;FRAME],0).first(),Some(AudioEvent::Woke{..})));
 let generation=worker.session.generation;let mut events=vec![];
 for _ in 0..5{events.extend(worker.accept(&[0.2;FRAME],20));}speech.set(false);
 for _ in 0..40{events.extend(worker.accept(&[0.0;FRAME],40));}
 assert_eq!(events.len(),1);let AudioEvent::Utterance{generation:utterance_generation,audio}=events.pop().unwrap() else{panic!()};assert_eq!(utterance_generation,generation);assert_eq!(audio.0[0],6553);assert!(audio.0.iter().all(|s|*s<7000));
 let a=HostFake{revision:Cell::new(1),generation};let mut s=StoreFake::default();let mut n=HttpFake::default();let mut g=Gateway::new();
 // Fake binding stands in for Store::voice_gateway_begin_asr's returned binding.
 // This test does NOT allocate a canonical UserTurn or prove production Host integration.
 let mut b=binding("host-fake-asr");b.generation=generation;assert_eq!(worker.session.begin_asr().unwrap(),generation);
 g.begin_asr(b.clone(),audio,Phase::BDevelopment,&a,&mut s,&mut n).unwrap();
 g.poll(Purpose::Asr,&b.request_id,Frame::Headers(200),&a,&mut n).unwrap();
 let event=|delta:serde_json::Value,finish:serde_json::Value|format!("data: {}\n\n",serde_json::json!({"id":"fake-asr","object":"chat.completion.chunk","model":"mimo-v2.5-asr","choices":[{"index":0,"delta":delta,"finish_reason":finish}]})).into_bytes();
 assert!(matches!(g.poll(Purpose::Asr,&b.request_id,Frame::Data(event(serde_json::json!({"content":"合成输入"}),serde_json::Value::Null)),&a,&mut n).unwrap(),Outcome::Parts(_)));
 let mut end=event(serde_json::json!({}),serde_json::json!("stop"));end.extend(b"data: [DONE]\n\n");assert!(matches!(g.poll(Purpose::Asr,&b.request_id,Frame::Data(end),&a,&mut n).unwrap(),Outcome::Parts(_)));
 let Outcome::Final(text)=g.poll(Purpose::Asr,&b.request_id,Frame::Eof,&a,&mut n).unwrap() else{panic!()};assert_eq!(text,"合成输入");worker.session.asr_final(generation,true).unwrap();
 assert!(g.poll(Purpose::Asr,&b.request_id,Frame::Eof,&a,&mut n).is_err());assert_eq!(n.starts.len(),1);
}
