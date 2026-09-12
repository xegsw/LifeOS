//! Pure backend protocol adapter. Host injects HTTP/CredentialPort after grants.
//! There is deliberately no URL override, HTTP client, key storage, or retry here.
use serde_json::{json, Value};
use zeroize::Zeroize;
pub const ENDPOINT: &str = "https://api.xiaomimimo.com/v1/chat/completions";
pub const CONNECT_TIMEOUT_MS: u64 = 15000;
pub const ASR_TIMEOUT_MS: u64 = 60000;
pub const TTS_FIRST_IDLE_MS: u64 = 15000;
pub const TTS_TOTAL_MS: u64 = 120000;
pub struct RequestBody(pub Vec<u8>);
impl Drop for RequestBody {
    fn drop(&mut self) {
        self.0.zeroize();
    }
}
const B64: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
fn encode(b: &[u8]) -> String {
    let mut out = String::new();
    for c in b.chunks(3) {
        let n = ((c[0] as u32) << 16)
            | ((c.get(1).copied().unwrap_or(0) as u32) << 8)
            | c.get(2).copied().unwrap_or(0) as u32;
        out.push(B64[((n >> 18) & 63) as usize] as char);
        out.push(B64[((n >> 12) & 63) as usize] as char);
        out.push(if c.len() > 1 {
            B64[((n >> 6) & 63) as usize] as char
        } else {
            '='
        });
        out.push(if c.len() > 2 {
            B64[(n & 63) as usize] as char
        } else {
            '='
        });
    }
    out
}
fn decode(s: &str) -> Result<Vec<u8>, &'static str> {
    if s.len() % 4 != 0 || s.len() > 12 * 1024 * 1024 {
        return Err("base64_invalid");
    }
    let mut out = Vec::new();
    for (i, c) in s.as_bytes().chunks_exact(4).enumerate() {
        let last = (i + 1) * 4 == s.len();
        let pad = if c[2] == b'=' {
            2
        } else if c[3] == b'=' {
            1
        } else {
            0
        };
        if pad > 0 && !last || pad == 2 && c[3] != b'=' {
            return Err("base64_invalid");
        }
        let mut n = 0u32;
        for (j, x) in c.iter().enumerate() {
            let v = if j >= 4 - pad {
                0
            } else {
                B64.iter().position(|a| a == x).ok_or("base64_invalid")? as u32
            };
            n = (n << 6) | v;
        }
        if (pad == 2 && n & 0xffff != 0) || (pad == 1 && n & 0xff != 0) {
            return Err("base64_invalid");
        }
        out.push((n >> 16) as u8);
        if pad < 2 {
            out.push((n >> 8) as u8);
        }
        if pad == 0 {
            out.push(n as u8);
        }
    }
    Ok(out)
}
pub fn asr_request(audio: &super::audio::Audio) -> Result<RequestBody, &'static str> {
    let mut wav = audio.wav()?;
    let mut data = encode(&wav);
    wav.zeroize();
    let mut body = json!({"model":"mimo-v2.5-asr","messages":[{"role":"user","content":[{"type":"input_audio","input_audio":{"data":data,"format":"wav"}}]}],"asr_options":{"language":"zh"},"stream":true});
    data.zeroize();
    let bytes = serde_json::to_vec(&body).map_err(|_| "encode_failed")?;
    if let Some(Value::String(v)) = body.pointer_mut("/messages/0/content/0/input_audio/data") {
        v.zeroize();
    }
    if bytes.len() > 4 * 1024 * 1024 {
        return Err("request_limit");
    }
    Ok(RequestBody(bytes))
}
pub fn tts_request(host_projection: &str) -> Result<RequestBody, &'static str> {
    if host_projection.trim().is_empty() || host_projection.chars().count() > 4000 {
        return Err("projection_limit");
    }
    Ok(RequestBody(serde_json::to_vec(&json!({"model":"mimo-v2.5-tts","messages":[{"role":"assistant","content":host_projection}],"audio":{"format":"pcm16","voice":"mimo_default","optimize_text_preview":false},"stream":true})).map_err(|_|"encode_failed")?))
}
#[derive(Clone, Copy, PartialEq, Eq)]
pub enum Mode {
    Asr,
    Tts,
}
pub enum Part {
    Text(String),
    Pcm(Vec<u8>),
}
/// Streaming UTF-8 framing: partial bytes never parse as a final turn.
pub struct Sse {
    mode: Mode,
    buffer: Vec<u8>,
    received: usize,
    decoded: usize,
    id: Option<String>,
    audio_id: Option<String>,
    text: String,
    stopped: bool,
    done: bool,
    failed: bool,
}
impl Drop for Sse {
    fn drop(&mut self) {
        self.buffer.zeroize();
        self.text.zeroize();
    }
}
impl Sse {
    pub fn new(mode: Mode) -> Self {
        Self {
            mode,
            buffer: Vec::new(),
            received: 0,
            decoded: 0,
            id: None,
            audio_id: None,
            text: String::new(),
            stopped: false,
            done: false,
            failed: false,
        }
    }
    pub fn push(&mut self, b: &[u8]) -> Result<Vec<Part>, &'static str> {
        let result = self.feed(b);
        if result.is_err() {
            self.failed = true;
            self.buffer.zeroize();
            self.buffer.clear();
            self.text.zeroize();
        }
        result
    }
    fn feed(&mut self, b: &[u8]) -> Result<Vec<Part>, &'static str> {
        if self.failed {
            return Err("stream_failed");
        }
        self.received += b.len();
        let limit = if self.mode == Mode::Asr {
            256 * 1024
        } else {
            12 * 1024 * 1024
        };
        if self.received > limit {
            return Err("response_limit");
        }
        self.buffer.extend_from_slice(b);
        let mut out = Vec::new();
        loop {
            let split = self
                .buffer
                .windows(2)
                .position(|w| w == b"\n\n")
                .map(|p| (p, 2))
                .or_else(|| {
                    self.buffer
                        .windows(4)
                        .position(|w| w == b"\r\n\r\n")
                        .map(|p| (p, 4))
                });
            let Some((end, sep)) = split else { break };
            let event = self.buffer.drain(..end + sep).collect::<Vec<_>>();
            let raw = std::str::from_utf8(&event).map_err(|_| "utf8_invalid")?;
            let mut data = Vec::new();
            for line in raw.lines() {
                if let Some(d) = line.strip_prefix("data:") {
                    data.push(d.strip_prefix(' ').unwrap_or(d));
                } else if !line.is_empty() && !line.starts_with(':') && !line.starts_with("event:")
                {
                    return Err("sse_field");
                }
            }
            if data.is_empty() {
                continue;
            }
            let payload = data.join("\n");
            if self.done {
                return Err("after_done");
            }
            if payload == "[DONE]" {
                if !self.stopped {
                    return Err("missing_stop");
                }
                self.done = true;
                continue;
            }
            let v: Value = super::strict::parse(&payload)?;
            if v.get("error").is_some() {
                return Err("provider_error");
            }
            let model = if self.mode == Mode::Asr {
                "mimo-v2.5-asr"
            } else {
                "mimo-v2.5-tts"
            };
            if v["model"] != model || v["object"] != "chat.completion.chunk" {
                return Err("response_identity");
            }
            let id = v["id"]
                .as_str()
                .filter(|s| !s.is_empty())
                .ok_or("response_identity")?;
            if self.id.as_deref().is_some_and(|old| old != id) {
                return Err("response_identity");
            }
            self.id = Some(id.to_owned());
            let choices = v["choices"].as_array().ok_or("choices_invalid")?;
            if choices.is_empty() {
                if v.get("usage").is_none() {
                    return Err("choices_invalid");
                }
                continue;
            }
            if choices.len() != 1 || choices[0]["index"] != 0 || self.stopped {
                return Err("choices_invalid");
            }
            let c = &choices[0];
            let d = &c["delta"];
            if !d.is_object() {
                return Err("delta_invalid");
            }
            for key in [
                "tool_calls",
                "function_call",
                "reasoning_content",
                "final_text_preview",
            ] {
                if d.get(key).is_some_and(|v| !v.is_null()) {
                    return Err("unexpected_modality");
                }
            }
            if let Some(role) = d.get("role") {
                if role != "assistant" {
                    return Err("role_invalid");
                }
            }
            if self.mode == Mode::Asr {
                if d.get("audio").is_some_and(|v| !v.is_null()) {
                    return Err("unexpected_modality");
                }
                if let Some(t) = d.get("content").filter(|v| !v.is_null()) {
                    let t = t.as_str().ok_or("text_invalid")?;
                    self.text.push_str(t);
                    out.push(Part::Text(t.to_owned()));
                }
            } else {
                if d.get("content")
                    .and_then(Value::as_str)
                    .is_some_and(|s| !s.is_empty())
                {
                    return Err("unexpected_text");
                }
                if let Some(a) = d.get("audio").filter(|v| !v.is_null()) {
                    if let Some(id) = a.get("id") {
                        let id = id.as_str().ok_or("audio_identity")?;
                        if self.audio_id.as_deref().is_some_and(|old| old != id) {
                            return Err("audio_identity");
                        }
                        self.audio_id = Some(id.to_owned());
                    }
                    if let Some(s) = a.get("data") {
                        let bytes = decode(s.as_str().ok_or("audio_invalid")?)?;
                        if bytes.len() % 2 != 0 {
                            return Err("pcm_alignment");
                        }
                        self.decoded += bytes.len();
                        if self.decoded > 8 * 1024 * 1024 {
                            return Err("decoded_audio_limit");
                        }
                        out.push(Part::Pcm(bytes));
                    }
                }
            }
            if let Some(reason) = c.get("finish_reason").filter(|v| !v.is_null()) {
                if reason != "stop" {
                    return Err("incomplete_output");
                }
                self.stopped = true;
            }
        }
        Ok(out)
    }
    pub fn finish(&self) -> Result<Option<&str>, &'static str> {
        if self.failed
            || !self.done
            || !self.stopped
            || self.buffer.iter().any(|b| !b.is_ascii_whitespace())
        {
            return Err("truncated_stream");
        }
        if self.mode == Mode::Asr {
            if self.text.trim().is_empty() {
                return Err("empty_transcript");
            }
            Ok(Some(&self.text))
        } else if self.decoded == 0 {
            Err("empty_audio")
        } else {
            Ok(None)
        }
    }
}
pub fn error_code(status: u16) -> &'static str {
    match status {
        401 | 403 => "voice_credentials_required",
        429 => "provider_rate_limited",
        300..=399 => "redirect_rejected",
        _ => "voice_network_failed",
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    fn event(mode: Mode, delta: Value, finish: Value) -> Vec<u8> {
        format!("data: {}\n\n",json!({"id":"r1","object":"chat.completion.chunk","model":if mode==Mode::Asr{"mimo-v2.5-asr"}else{"mimo-v2.5-tts"},"choices":[{"index":0,"delta":delta,"finish_reason":finish}]})).into_bytes()
    }
    #[test]
    fn asr_every_byte_split_and_real_final_only() {
        let mut b = event(Mode::Asr, json!({"content":"合成测试"}), Value::Null);
        b.extend(event(Mode::Asr, json!({}), json!("stop")));
        b.extend(b"data: [DONE]\n\n");
        for width in 1..b.len() {
            let mut s = Sse::new(Mode::Asr);
            for chunk in b.chunks(width) {
                s.push(chunk).unwrap();
            }
            assert_eq!(s.finish().unwrap(), Some("合成测试"));
        }
    }
    #[test]
    fn broken_partial_and_length_never_final() {
        let mut s = Sse::new(Mode::Asr);
        s.push(&event(Mode::Asr, json!({"content":"partial"}), Value::Null))
            .unwrap();
        assert!(s.finish().is_err());
        assert!(s
            .push(&event(Mode::Asr, json!({}), json!("length")))
            .is_err());
        assert!(s.finish().is_err());
    }
    #[test]
    fn tts_emits_before_completion() {
        let mut s = Sse::new(Mode::Tts);
        let out = s
            .push(&event(
                Mode::Tts,
                json!({"audio":{"id":"a1","data":"AAABAA=="}}),
                Value::Null,
            ))
            .unwrap();
        assert!(matches!(&out[0],Part::Pcm(b) if b==&[0,0,1,0]));
        assert!(s.finish().is_err());
        s.push(&event(Mode::Tts, json!({}), json!("stop"))).unwrap();
        s.push(b"data: [DONE]\n\n").unwrap();
        assert!(s.finish().is_ok());
    }
    #[test]
    fn mismatch_and_tools_rejected() {
        let mut s = Sse::new(Mode::Asr);
        assert!(s.push(&event(Mode::Tts, json!({}), Value::Null)).is_err());
        let mut s = Sse::new(Mode::Asr);
        assert!(s
            .push(&event(Mode::Asr, json!({"tool_calls":[]}), Value::Null))
            .is_err());
    }
    #[test]
    fn base64_canonical_and_request_minimization() {
        for n in 0..100 {
            let b: Vec<u8> = (0..n).collect();
            assert_eq!(decode(&encode(&b)).unwrap(), b);
        }
        assert!(decode("AB==").is_err());
        assert!(decode("====").is_err());
        let r = asr_request(&super::super::audio::Audio(vec![0; 1600])).unwrap();
        let v: Value = serde_json::from_slice(&r.0).unwrap();
        assert_eq!(v["messages"].as_array().unwrap().len(), 1);
        assert_eq!(v["messages"][0]["content"].as_array().unwrap().len(), 1);
        let v: Value = serde_json::from_slice(&tts_request("合成回复").unwrap().0).unwrap();
        assert_eq!(v["messages"][0]["role"], "assistant");
        assert_eq!(v["audio"]["optimize_text_preview"], false);
        assert!(tts_request(&"字".repeat(4001)).is_err());
    }
    #[test]
    fn duplicate_json_and_missing_done_fail_closed() {
        let mut s = Sse::new(Mode::Asr);
        let raw = String::from_utf8(event(
            Mode::Asr,
            json!({"content":"synthetic"}),
            json!("stop"),
        ))
        .unwrap();
        let duplicate = raw.replace("\"index\":0", "\"index\":1,\"index\":0");
        assert!(s.push(duplicate.as_bytes()).is_err());
        let mut s = Sse::new(Mode::Asr);
        s.push(raw.as_bytes()).unwrap();
        assert!(s.finish().is_err());
        s.push(b"data: [DONE]\n\n").unwrap();
        assert_eq!(s.finish().unwrap(), Some("synthetic"));
    }
}
