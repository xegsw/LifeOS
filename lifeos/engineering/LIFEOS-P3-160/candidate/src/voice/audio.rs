use std::collections::VecDeque;
use zeroize::Zeroize;
pub const INPUT_RATE: usize = 16000;
pub const OUTPUT_RATE: usize = 24000;
pub const FRAME: usize = 320; // 20 ms at the ASR input rate
pub trait WakeDetector {
    fn accept(&mut self, pcm: &[f32]) -> Result<bool, &'static str>;
    fn reset(&mut self);
}
pub trait VadDetector {
    fn speech(&mut self, pcm: &[f32]) -> Result<bool, &'static str>;
    fn reset(&mut self);
}
/// All audio owners erase samples on release. Debug deliberately omits samples.
pub struct Audio(pub Vec<i16>);
impl Drop for Audio {
    fn drop(&mut self) {
        self.0.zeroize();
    }
}
impl Audio {
    pub fn wav(&self) -> Result<Vec<u8>, &'static str> {
        if self.0.is_empty() || self.0.len() > INPUT_RATE * 60 {
            return Err("audio_bounds");
        }
        let n = (self.0.len() * 2) as u32;
        let mut b = Vec::with_capacity(n as usize + 44);
        b.extend(b"RIFF");
        b.extend((n + 36).to_le_bytes());
        b.extend(b"WAVEfmt ");
        b.extend(16u32.to_le_bytes());
        b.extend(1u16.to_le_bytes());
        b.extend(1u16.to_le_bytes());
        b.extend((INPUT_RATE as u32).to_le_bytes());
        b.extend((INPUT_RATE as u32 * 2).to_le_bytes());
        b.extend(2u16.to_le_bytes());
        b.extend(16u16.to_le_bytes());
        b.extend(b"data");
        b.extend(n.to_le_bytes());
        for s in &self.0 {
            b.extend(s.to_le_bytes());
        }
        Ok(b)
    }
}
/// Wake history stays local; take/serialize is intentionally absent.
pub struct WakeRing {
    samples: VecDeque<i16>,
    capacity: usize,
}
impl WakeRing {
    pub fn new() -> Self {
        Self {
            samples: VecDeque::with_capacity(INPUT_RATE * 2),
            capacity: INPUT_RATE * 2,
        }
    }
    pub fn push(&mut self, input: &[i16]) {
        for &s in input {
            if self.samples.len() == self.capacity {
                if let Some(v) = self.samples.front_mut() {
                    *v = 0;
                }
                self.samples.pop_front();
            }
            self.samples.push_back(s);
        }
    }
    pub fn clear(&mut self) {
        for v in self.samples.iter_mut() {
            *v = 0;
        }
        self.samples.clear();
    }
    pub fn len(&self) -> usize {
        self.samples.len()
    }
}
impl Drop for WakeRing {
    fn drop(&mut self) {
        self.clear();
    }
}
/// Segmentation consumes a real detector's classifications; it is not a KWS/VAD model.
pub struct Segmenter {
    pcm: Audio,
    silence: usize,
    voiced: usize,
    end_frames: usize,
}
impl Segmenter {
    pub fn new(silence_ms: usize) -> Result<Self, &'static str> {
        if !(500..=1200).contains(&silence_ms) {
            return Err("vad_bounds");
        }
        Ok(Self {
            pcm: Audio(Vec::new()),
            silence: 0,
            voiced: 0,
            end_frames: silence_ms / 20,
        })
    }
    pub fn reset(&mut self) {
        self.pcm = Audio(Vec::new());
        self.silence = 0;
        self.voiced = 0;
    }
    pub fn accept(&mut self, frame: &[i16], speech: bool) -> Result<Option<Audio>, &'static str> {
        if frame.len() != FRAME {
            self.reset();
            return Err("frame_format");
        }
        // Keep initial post-wake/onset frames, including low-energy beginnings.
        self.pcm.0.extend_from_slice(frame);
        if speech {
            self.voiced += 1;
            self.silence = 0;
        } else {
            self.silence += 1;
        }
        if self.silence >= self.end_frames || self.pcm.0.len() >= INPUT_RATE * 60 {
            let valid = self.voiced >= 5;
            let out = std::mem::replace(&mut self.pcm, Audio(Vec::new()));
            self.silence = 0;
            self.voiced = 0;
            return Ok(if valid { Some(out) } else { None });
        }
        Ok(None)
    }
    pub fn buffered(&self) -> usize {
        self.pcm.0.len()
    }
}
/// PCM16LE mono; at most 2 seconds queued. A stale generation cannot enqueue.
pub struct Playback {
    pub generation: u64,
    queue: VecDeque<i16>,
    total: usize,
    active: bool,
}
impl Playback {
    pub fn new() -> Self {
        Self {
            generation: 0,
            queue: VecDeque::new(),
            total: 0,
            active: false,
        }
    }
    pub fn begin(&mut self) -> u64 {
        self.stop();
        self.active = true;
        self.total = 0;
        self.generation
    }
    pub fn push(&mut self, g: u64, bytes: &[u8]) -> Result<(), &'static str> {
        if !self.active || g != self.generation {
            return Err("stale_audio");
        }
        if bytes.len() % 2 != 0 {
            return Err("pcm_alignment");
        }
        if self.total + bytes.len() > 8 * 1024 * 1024 {
            return Err("decoded_audio_limit");
        }
        if self.queue.len() + bytes.len() / 2 > OUTPUT_RATE * 2 {
            return Err("backpressure");
        }
        self.total += bytes.len();
        for b in bytes.chunks_exact(2) {
            self.queue.push_back(i16::from_le_bytes([b[0], b[1]]));
        }
        Ok(())
    }
    pub fn drain(&mut self, max: usize) -> Audio {
        Audio(
            (0..max.min(self.queue.len()))
                .filter_map(|_| self.queue.pop_front())
                .collect(),
        )
    }
    pub fn stop(&mut self) {
        self.generation = self
            .generation
            .checked_add(1)
            .expect("generation exhausted");
        self.active = false;
        for v in &mut self.queue {
            *v = 0;
        }
        self.queue.clear();
    }
    pub fn queued(&self) -> usize {
        self.queue.len()
    }
}
impl Drop for Playback {
    fn drop(&mut self) {
        self.stop();
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn bounded_wake_history() {
        let mut r = WakeRing::new();
        r.push(&vec![1; 100000]);
        assert_eq!(r.len(), 32000);
        r.clear();
        assert_eq!(r.len(), 0);
    }
    #[test]
    fn silence_and_noise_do_not_form_intent() {
        let mut s = Segmenter::new(800).unwrap();
        for _ in 0..10000 {
            assert!(s.accept(&[0; FRAME], false).unwrap().is_none());
            assert!(s.buffered() <= 12800);
        }
    }
    #[test]
    fn preserves_onset_and_sixty_second_boundary() {
        let mut s = Segmenter::new(800).unwrap();
        let mut out = None;
        for i in 0..3000 {
            out = s.accept(&[i as i16; FRAME], true).unwrap();
        }
        let a = out.unwrap();
        assert_eq!(a.0.len(), 960000);
        assert_eq!(a.0[0], 0);
        assert_eq!(a.wav().unwrap().len(), 1920044);
        assert_eq!(s.buffered(), 0);
    }
    #[test]
    fn vad_tail_and_release() {
        let mut s = Segmenter::new(800).unwrap();
        for _ in 0..5 {
            s.accept(&[1; FRAME], true).unwrap();
        }
        for _ in 0..39 {
            assert!(s.accept(&[0; FRAME], false).unwrap().is_none());
        }
        assert!(s.accept(&[0; FRAME], false).unwrap().is_some());
        assert_eq!(s.buffered(), 0);
    }
    #[test]
    fn interruption_and_backpressure() {
        let mut p = Playback::new();
        let g = p.begin();
        p.push(g, &vec![0; 96000]).unwrap();
        assert_eq!(p.push(g, &[0, 0]), Err("backpressure"));
        assert_eq!(p.drain(480).0.len(), 480);
        p.stop();
        assert_eq!(p.queued(), 0);
        assert_eq!(p.push(g, &[0, 0]), Err("stale_audio"));
        let n = p.begin();
        assert!(n > g);
        assert_eq!(p.push(g, &[0, 0]), Err("stale_audio"));
        assert_eq!(p.push(n, &[0]), Err("pcm_alignment"));
    }
}
