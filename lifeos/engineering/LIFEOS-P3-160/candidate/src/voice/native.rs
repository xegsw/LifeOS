//! macOS C ABI bindings. Link the voice libraries into the SAME existing Tauri host.
//! All handles remain on one audio worker; no raw context crosses IPC.
use super::{
    audio::{VadDetector, WakeDetector},
    gateway::{Frame, Transport},
    mimo::RequestBody,
};
use std::{
    collections::HashMap,
    ffi::{c_void, CString},
    ptr::NonNull,
    sync::{
        atomic::{AtomicBool, Ordering},
        mpsc::{sync_channel, Receiver, SyncSender},
        Arc,
    },
};
unsafe extern "C" {
    fn lifeos_voice_http_available() -> i32;
    fn lifeos_voice_audio_create_v2(
        ctx: *mut c_void,
        samples: extern "C" fn(*mut c_void, *const f32, i32),
        event: extern "C" fn(*mut c_void, i32),
        playback: extern "C" fn(*mut c_void, u64, u64, u64, i32, i32),
    ) -> *mut c_void;
    fn lifeos_voice_audio_start(p: *mut c_void) -> i32;
    fn lifeos_voice_audio_stop(p: *mut c_void);
    fn lifeos_voice_audio_interrupt(p: *mut c_void) -> u64;
    fn lifeos_voice_audio_push_v2(p: *mut c_void, b: *const u8, n: i32, g: u64, token: *mut u64) -> i32;
    fn lifeos_voice_audio_finish_stream(p: *mut c_void, g: u64) -> i32;
    fn lifeos_voice_audio_generation(p: *mut c_void) -> u64;
    fn lifeos_voice_audio_playback_status(p: *mut c_void, g: u64, queued: *mut i32, consumed: *mut u64, state: *mut i32) -> i32;
    fn lifeos_voice_audio_destroy(p: *mut c_void);
    fn lifeos_voice_http_create(
        ctx: *mut c_void,
        cb: extern "C" fn(*mut c_void, i32, *const u8, i32) -> i32,
        asr: i32,
    ) -> *mut c_void;
    fn lifeos_voice_http_start(
        p: *mut c_void,
        b: *const u8,
        n: i32,
        key: *const u8,
        kn: i32,
        asr: i32,
    ) -> i32;
    fn lifeos_voice_http_cancel(p: *mut c_void);
    fn lifeos_voice_http_destroy(p: *mut c_void);
    fn lifeos_detector_create(
        e: *const i8,
        d: *const i8,
        j: *const i8,
        t: *const i8,
        k: *const i8,
        v: *const i8,
    ) -> *mut c_void;
    fn lifeos_detector_accept(p: *mut c_void, pcm: *const f32, n: i32, wake: i32) -> i32;
    fn lifeos_detector_reset(p: *mut c_void);
    fn lifeos_detector_destroy(p: *mut c_void);
}
pub enum Input {
    Samples(Vec<f32>),
    DeviceStopped(i32),
}
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlaybackFeedback {
    pub generation: u64,
    pub buffer_token: u64,
    pub consumed_samples: u64,
    pub queued_samples: u32,
    pub drained: bool,
}
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct PlaybackStatus {
    pub generation: u64,
    pub consumed_samples: u64,
    pub queued_samples: u32,
    pub available_samples: u32,
    pub sealed: bool,
    pub drained: bool,
}
struct AudioContext {
    sender: SyncSender<Input>,
    playback_sender: SyncSender<PlaybackFeedback>,
    overflow: Arc<AtomicBool>,
}
extern "C" fn samples(ctx: *mut c_void, pcm: *const f32, n: i32) {
    if ctx.is_null() || pcm.is_null() || n <= 0 || n > 8192 {
        return;
    }
    let c = unsafe { &*(ctx as *const AudioContext) };
    let data = unsafe { std::slice::from_raw_parts(pcm, n as usize) }.to_vec();
    if c.sender.try_send(Input::Samples(data)).is_err() {
        c.overflow.store(true, Ordering::Release);
    }
}
extern "C" fn device_event(ctx: *mut c_void, code: i32) {
    if ctx.is_null() {
        return;
    }
    let c = unsafe { &*(ctx as *const AudioContext) };
    if c.sender.try_send(Input::DeviceStopped(code)).is_err() {
        c.overflow.store(true, Ordering::Release);
    }
}
extern "C" fn playback_event(ctx: *mut c_void, generation: u64, token: u64, consumed: u64, queued: i32, kind: i32) {
    if ctx.is_null() { return; }
    let c = unsafe { &*(ctx as *const AudioContext) };
    if !(0..=48000).contains(&queued) || !matches!(kind, 1 | 2)
        || (kind == 1 && token == 0) || (kind == 2 && (token != 0 || queued != 0)) {
        c.overflow.store(true, Ordering::Release); return;
    }
    let f = PlaybackFeedback { generation, buffer_token: token, consumed_samples: consumed,
        queued_samples: queued as u32, drained: kind == 2 };
    if c.playback_sender.try_send(f).is_err() { c.overflow.store(true, Ordering::Release); }
}
pub struct NativeAudio {
    handle: NonNull<c_void>,
    _context: Box<AudioContext>,
    pub events: Receiver<Input>,
    playback_events: Receiver<PlaybackFeedback>,
    overflow: Arc<AtomicBool>,
    play_generation: u64,
}
impl NativeAudio {
    pub fn new() -> Result<Self, &'static str> {
        let (sender, events) = sync_channel(8);
        let (playback_sender, playback_events) = sync_channel(8);
        let overflow = Arc::new(AtomicBool::new(false));
        let mut context = Box::new(AudioContext {
            sender,
            playback_sender,
            overflow: overflow.clone(),
        });
        let p = unsafe {
            lifeos_voice_audio_create_v2(
                (&mut *context as *mut AudioContext).cast(),
                samples,
                device_event,
                playback_event,
            )
        };
        Ok(Self {
            handle: NonNull::new(p).ok_or("native_audio_unavailable")?,
            _context: context,
            events,
            playback_events,
            overflow,
            play_generation: 0,
        })
    }
    pub fn start(&mut self) -> Result<(), &'static str> {
        if unsafe { lifeos_voice_audio_start(self.handle.as_ptr()) } == 0 {
            Ok(())
        } else {
            Err("microphone_not_started")
        }
    }
    pub fn stop(&mut self) {
        unsafe { lifeos_voice_audio_stop(self.handle.as_ptr()) };
        self.play_generation = unsafe { lifeos_voice_audio_generation(self.handle.as_ptr()) };
        while self.playback_events.try_recv().is_ok() {}
        while let Ok(v) = self.events.try_recv() {
            if let Input::Samples(mut p) = v {
                use zeroize::Zeroize;
                p.zeroize();
            }
        }
    }
    pub fn interrupt(&mut self) {
        self.play_generation = unsafe { lifeos_voice_audio_interrupt(self.handle.as_ptr()) };
        while self.playback_events.try_recv().is_ok() {}
    }
    /// Compatibility helper. New host routing must use enqueue_for with its saved epoch.
    pub fn enqueue(&mut self, pcm: &[u8]) -> Result<(), &'static str> {
        self.enqueue_for(self.play_generation, pcm).map(|_| ())
    }
    pub fn playback_generation(&self) -> u64 { self.play_generation }
    pub fn enqueue_for(&mut self, generation: u64, pcm: &[u8]) -> Result<u64, &'static str> {
        if generation != self.play_generation { return Err("stale_audio"); }
        if pcm.is_empty() || pcm.len() % 2 != 0 || pcm.len() > 96000 { return Err("playback_backpressure"); }
        let mut token = 0;
        if unsafe { lifeos_voice_audio_push_v2(self.handle.as_ptr(), pcm.as_ptr(), pcm.len() as i32, generation, &mut token) } == 0 {
            Ok(token)
        } else { Err("native_playback_rejected") }
    }
    /// Mark HTTP-complete only after all verified PCM has been enqueued; not playback completion.
    pub fn finish_stream(&mut self, generation: u64) -> Result<(), &'static str> {
        if generation != self.play_generation { return Err("stale_audio"); }
        if unsafe { lifeos_voice_audio_finish_stream(self.handle.as_ptr(), generation) } == 0 { Ok(()) }
        else { Err("native_playback_rejected") }
    }
    pub fn playback_status(&self, generation: u64) -> Result<PlaybackStatus, &'static str> {
        if generation != self.play_generation { return Err("stale_audio"); }
        let (mut queued, mut consumed, mut state) = (0, 0, 0);
        if unsafe { lifeos_voice_audio_playback_status(self.handle.as_ptr(), generation, &mut queued, &mut consumed, &mut state) } != 0
            || !(0..=48000).contains(&queued) || !(0..=2).contains(&state) { return Err("native_playback_rejected"); }
        Ok(PlaybackStatus { generation, consumed_samples: consumed, queued_samples: queued as u32,
            available_samples: 48000 - queued as u32, sealed: state > 0, drained: state == 2 })
    }
    /// Old generations already queued before cancellation are filtered as well.
    pub fn poll_playback(&mut self) -> Option<PlaybackFeedback> {
        while let Ok(f) = self.playback_events.try_recv() {
            if f.generation == self.play_generation { return Some(f); }
        }
        None
    }
    pub fn healthy(&mut self) -> bool {
        if self.overflow.swap(false, Ordering::AcqRel) {
            self.stop();
            false
        } else {
            true
        }
    }
}
impl Drop for NativeAudio {
    fn drop(&mut self) {
        self.stop();
        unsafe { lifeos_voice_audio_destroy(self.handle.as_ptr()) };
    }
}
/// Internal assets must already be licensed/hash-verified by package resolution.
/// This type is NOT Deserialize and never an IPC payload.
pub struct DetectorAssets {
    pub encoder: CString,
    pub decoder: CString,
    pub joiner: CString,
    pub tokens: CString,
    pub keywords: CString,
    pub vad: CString,
}
struct Detector {
    handle: NonNull<c_void>,
}
impl Drop for Detector {
    fn drop(&mut self) {
        unsafe { lifeos_detector_destroy(self.handle.as_ptr()) };
    }
}
pub struct NativeWake(std::rc::Rc<Detector>);
pub struct NativeVad(std::rc::Rc<Detector>);
pub fn detectors(a: &DetectorAssets) -> Result<(NativeWake, NativeVad), &'static str> {
    let p = unsafe {
        lifeos_detector_create(
            a.encoder.as_ptr(),
            a.decoder.as_ptr(),
            a.joiner.as_ptr(),
            a.tokens.as_ptr(),
            a.keywords.as_ptr(),
            a.vad.as_ptr(),
        )
    };
    let d = std::rc::Rc::new(Detector {
        handle: NonNull::new(p).ok_or("model_unavailable")?,
    });
    Ok((NativeWake(d.clone()), NativeVad(d)))
}
impl WakeDetector for NativeWake {
    fn accept(&mut self, pcm: &[f32]) -> Result<bool, &'static str> {
        let r = unsafe {
            lifeos_detector_accept(self.0.handle.as_ptr(), pcm.as_ptr(), pcm.len() as i32, 1)
        };
        if r < 0 {
            Err("kws_failed")
        } else {
            Ok(r & 1 != 0)
        }
    }
    fn reset(&mut self) {
        unsafe { lifeos_detector_reset(self.0.handle.as_ptr()) };
    }
}
impl VadDetector for NativeVad {
    fn speech(&mut self, pcm: &[f32]) -> Result<bool, &'static str> {
        let r = unsafe {
            lifeos_detector_accept(self.0.handle.as_ptr(), pcm.as_ptr(), pcm.len() as i32, 0)
        };
        if r < 0 {
            Err("vad_failed")
        } else {
            Ok(r & 2 != 0)
        }
    }
    fn reset(&mut self) {
        unsafe { lifeos_detector_reset(self.0.handle.as_ptr()) };
    }
}
/// Key supplied transiently from original CredentialPort. The callback may NOT log it.
pub trait CredentialAccess {
    fn with_key(
        &mut self,
        purpose: super::budget::Purpose,
        send: &mut dyn FnMut(&[u8]) -> Result<(), &'static str>,
    ) -> Result<(), &'static str>;
}
struct HttpContext {
    id: String,
    sender: SyncSender<(String, Frame)>,
    overflow: Arc<AtomicBool>,
}
extern "C" fn http_event(ctx: *mut c_void, code: i32, data: *const u8, n: i32) -> i32 {
    if ctx.is_null() {
        return -1;
    }
    let c = unsafe { &*(ctx as *const HttpContext) };
    let f = match code {
        0 => {
            if data.is_null() || n <= 0 || n > 262144 {
                return -1;
            }
            Frame::Data(unsafe { std::slice::from_raw_parts(data, n as usize) }.to_vec())
        }
        -1 => Frame::Eof,
        -2 | -3 => Frame::Failure,
        200..=599 => Frame::Headers(code as u16),
        _ => return -1,
    };
    if c.sender.try_send((c.id.clone(), f)).is_err() {
        c.overflow.store(true, Ordering::Release);
        -1
    } else {
        0
    }
}
struct Request {
    handle: NonNull<c_void>,
    _context: Box<HttpContext>,
}
impl Drop for Request {
    fn drop(&mut self) {
        unsafe {
            lifeos_voice_http_cancel(self.handle.as_ptr());
            lifeos_voice_http_destroy(self.handle.as_ptr())
        };
    }
}
pub struct NativeTransport<C: CredentialAccess> {
    credential: C,
    requests: HashMap<String, Request>,
    sender: SyncSender<(String, Frame)>,
    pub events: Receiver<(String, Frame)>,
    overflow: Arc<AtomicBool>,
}
impl<C: CredentialAccess> NativeTransport<C> {
    pub fn new(credential: C) -> Self {
        let (sender, events) = sync_channel(16);
        Self {
            credential,
            requests: HashMap::new(),
            sender,
            events,
            overflow: Arc::new(AtomicBool::new(false)),
        }
    }
    pub fn healthy(&mut self) -> bool {
        if self.overflow.swap(false, Ordering::AcqRel) {
            self.requests.clear();
            false
        } else {
            true
        }
    }
    pub fn completed(&mut self, id: &str) {
        self.requests.remove(id);
    }
}
impl<C: CredentialAccess> Transport for NativeTransport<C> {
    fn start(&mut self, id: &str, endpoint: &str, body: RequestBody) -> Result<(), &'static str> {
        if unsafe { lifeos_voice_http_available() } != 1 {
            return Err("voice_transport_not_started");
        }
        if endpoint != super::mimo::ENDPOINT
            || self.requests.contains_key(id)
            || self.requests.len() >= 2
        {
            return Err("transport_denied");
        }
        let v: serde_json::Value =
            serde_json::from_slice(&body.0).map_err(|_| "voice_request_invalid")?;
        let asr = match v["model"].as_str() {
            Some("mimo-v2.5-asr") => true,
            Some("mimo-v2.5-tts") => false,
            _ => return Err("voice_model_denied"),
        };
        let mut context = Box::new(HttpContext {
            id: id.into(),
            sender: self.sender.clone(),
            overflow: self.overflow.clone(),
        });
        let handle = NonNull::new(unsafe {
            lifeos_voice_http_create(
                (&mut *context as *mut HttpContext).cast(),
                http_event,
                asr as i32,
            )
        })
        .ok_or("transport_unavailable")?;
        let request = Request {
            handle,
            _context: context,
        };
        let purpose = if asr {
            super::budget::Purpose::Asr
        } else {
            super::budget::Purpose::Tts
        };
        self.credential.with_key(purpose, &mut |key| {
            let status = unsafe {
                lifeos_voice_http_start(
                    handle.as_ptr(),
                    body.0.as_ptr(),
                    body.0.len() as i32,
                    key.as_ptr(),
                    key.len() as i32,
                    asr as i32,
                )
            };
            if status == 0 {
                Ok(())
            } else {
                Err("voice_transport_not_started")
            }
        })?;
        self.requests.insert(id.into(), request);
        Ok(())
    }
    fn cancel(&mut self, id: &str) {
        self.requests.remove(id);
    }
}

#[cfg(all(test, feature = "voice-native-tests"))]
mod tests {
    use super::*;
    struct ContractCredentialFake;
    impl CredentialAccess for ContractCredentialFake {
        fn with_key(
            &mut self,
            _: super::super::budget::Purpose,
            send: &mut dyn FnMut(&[u8]) -> Result<(), &'static str>,
        ) -> Result<(), &'static str> {
            {let _=send;panic!("A must deny before CredentialPort")}
        }
    }
    #[test]
    fn native_audio_A_is_hard_disabled_through_rust_ffi() {
        let mut a = NativeAudio::new().unwrap();
        assert_eq!(a.start(), Err("microphone_not_started"));
        a.interrupt();
        assert!(a.enqueue(&[0, 0]).is_err());
        a.stop();
        assert!(a.events.try_recv().is_err());
    }
    #[test]
    fn native_http_A_is_hard_disabled_through_rust_ffi() {
        let mut n = NativeTransport::new(ContractCredentialFake);
        let body = super::super::mimo::tts_request("合成文字").unwrap();
        assert_eq!(
            n.start("native-test", super::super::mimo::ENDPOINT, body),
            Err("voice_transport_not_started")
        );
        assert!(n.requests.is_empty());
        assert!(n.events.try_recv().is_err());
    }
    #[test]
    fn native_playback_feedback_epochs_and_overflow_without_devices() {
        let mut n = NativeAudio::new().unwrap();
        let old = n.playback_generation();
        assert_eq!(n.playback_status(old).unwrap().available_samples, 48000);
        assert!(n.enqueue_for(old, &[0, 0]).is_err());
        assert!(n.finish_stream(old).is_err());
        let ctx = (&mut *n._context as *mut AudioContext).cast();
        // Fake callbacks only. No enqueue succeeds, no start, no hardware audio.
        playback_event(ctx, old, 1, 12, 0, 1);
        n.interrupt();
        let fresh = n.playback_generation();
        assert!(fresh > old && n.poll_playback().is_none());
        playback_event(ctx, old, 2, 24, 0, 1);
        assert!(n.poll_playback().is_none());
        assert!(n.playback_status(old).is_err());
        assert!(n.enqueue_for(old, &[0, 0]).is_err());
        playback_event(ctx, fresh, 3, 32, 0, 1);
        let f = n.poll_playback().unwrap();
        assert_eq!((f.generation, f.buffer_token, f.consumed_samples), (fresh, 3, 32));
        for token in 10..20 { playback_event(ctx, fresh, token, 32, 0, 1); }
        assert!(!n.healthy());
        assert!(n.poll_playback().is_none());
        assert_eq!(n.playback_status(n.playback_generation()).unwrap().queued_samples, 0);
    }

}
