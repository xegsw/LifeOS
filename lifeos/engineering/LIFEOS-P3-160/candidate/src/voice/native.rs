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
    fn lifeos_voice_audio_create(
        ctx: *mut c_void,
        samples: extern "C" fn(*mut c_void, *const f32, i32),
        event: extern "C" fn(*mut c_void, i32),
    ) -> *mut c_void;
    fn lifeos_voice_audio_start(p: *mut c_void) -> i32;
    fn lifeos_voice_audio_stop(p: *mut c_void);
    fn lifeos_voice_audio_interrupt(p: *mut c_void) -> u64;
    fn lifeos_voice_audio_push(p: *mut c_void, b: *const u8, n: i32, g: u64) -> i32;
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
struct AudioContext {
    sender: SyncSender<Input>,
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
pub struct NativeAudio {
    handle: NonNull<c_void>,
    _context: Box<AudioContext>,
    pub events: Receiver<Input>,
    overflow: Arc<AtomicBool>,
    play_generation: u64,
}
impl NativeAudio {
    pub fn new() -> Result<Self, &'static str> {
        let (sender, events) = sync_channel(8);
        let overflow = Arc::new(AtomicBool::new(false));
        let mut context = Box::new(AudioContext {
            sender,
            overflow: overflow.clone(),
        });
        let p = unsafe {
            lifeos_voice_audio_create(
                (&mut *context as *mut AudioContext).cast(),
                samples,
                device_event,
            )
        };
        Ok(Self {
            handle: NonNull::new(p).ok_or("native_audio_unavailable")?,
            _context: context,
            events,
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
        while let Ok(v) = self.events.try_recv() {
            if let Input::Samples(mut p) = v {
                use zeroize::Zeroize;
                p.zeroize();
            }
        }
    }
    pub fn interrupt(&mut self) {
        self.play_generation = unsafe { lifeos_voice_audio_interrupt(self.handle.as_ptr()) };
    }
    pub fn enqueue(&mut self, pcm: &[u8]) -> Result<(), &'static str> {
        if pcm.len() > 96000 {
            return Err("playback_backpressure");
        }
        if unsafe {
            lifeos_voice_audio_push(
                self.handle.as_ptr(),
                pcm.as_ptr(),
                pcm.len() as i32,
                self.play_generation,
            )
        } == 0
        {
            Ok(())
        } else {
            Err("native_playback_rejected")
        }
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
}
