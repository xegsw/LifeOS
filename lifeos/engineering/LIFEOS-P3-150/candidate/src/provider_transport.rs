//! Fixed DeepSeek adapter. Engineering profile cannot execute this transport.
use crate::{conversation_contract::*, repository::Error};
use serde_json::Value;
use std::{
    io::{Read, Write},
    process::{Command, Stdio},
    time::{Duration, Instant},
};
use zeroize::Zeroizing;
pub const AUTHORITY: &str = "https://api.deepseek.com";
fn escape(s: &str) -> String {
    s.replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
}
fn call(path: &str, body: Option<&str>, key: &[u8]) -> R<Zeroizing<Vec<u8>>> {
    call_received(path, body, key, &mut || {})
}
fn call_received(
    path: &str,
    body: Option<&str>,
    key: &[u8],
    received: &mut dyn FnMut(),
) -> R<Zeroizing<Vec<u8>>> {
    if !crate::runtime_root::is_real() {
        return fail("real_capability_denied");
    }
    if !matches!(
        (path, body.is_some()),
        ("/models", false) | ("/chat/completions", true)
    ) {
        return fail("real_capability_denied");
    }
    if body.is_some_and(|b| b.len() > 24576) {
        return fail("context_budget_rejected");
    }
    let key = std::str::from_utf8(key).map_err(|_| Error::new("credential_invalid"))?;
    if key.len() < 8
        || key.len() > 512
        || !key
            .bytes()
            .all(|b| b.is_ascii_graphic() && b != b'"' && b != b'\\')
    {
        return fail("credential_invalid");
    }
    let mut config = Zeroizing::new(format!(
        "header = \"Authorization: Bearer {}\"\nheader = \"Content-Type: application/json\"\n",
        escape(key)
    ));
    if let Some(body) = body {
        config.push_str(&format!("data = \"{}\"\n", escape(body)));
    }
    // Bounded transport receipt: validated exact body/key now owned in config.
    // Release caller coordination before spawning or waiting on network I/O.
    received();
    let mut child = Command::new("/usr/bin/curl")
        .env_clear()
        .args([
            "-q",
            "--silent",
            "--request",
            if body.is_some() { "POST" } else { "GET" },
            "--url",
            &format!("{AUTHORITY}{path}"),
            "--proto",
            "=https",
            "--proto-redir",
            "=https",
            "--max-redirs",
            "0",
            "--noproxy",
            "*",
            "--proxy",
            "",
            "--connect-timeout",
            "15",
            "--max-time",
            "60",
            "--config",
            "-",
            "--write-out",
            "\n%{http_code}",
        ])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|_| Error::new("provider_unavailable"))?;
    let started = Instant::now();
    let write = child
        .stdin
        .take()
        .ok_or_else(|| Error::new("provider_unavailable"))
        .and_then(|mut s| {
            use std::os::fd::AsRawFd;
            let flags = unsafe { libc::fcntl(s.as_raw_fd(), libc::F_GETFL) };
            if flags < 0
                || unsafe { libc::fcntl(s.as_raw_fd(), libc::F_SETFL, flags | libc::O_NONBLOCK) }
                    < 0
            {
                return fail("provider_unavailable");
            }
            let mut offset = 0;
            while offset < config.len() {
                if started.elapsed() > Duration::from_secs(61) {
                    return fail("dispatch_outcome_unknown");
                }
                match s.write(&config.as_bytes()[offset..]) {
                    Ok(0) => return fail("dispatch_outcome_unknown"),
                    Ok(n) => offset += n,
                    Err(e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                        std::thread::sleep(Duration::from_millis(10))
                    }
                    Err(_) => return fail("dispatch_outcome_unknown"),
                }
            }
            Ok(())
        });
    if write.is_err() {
        let _ = child.kill();
        let _ = child.wait();
        return write.map(|_| Zeroizing::new(Vec::new()));
    }
    drop(config);
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| Error::new("provider_unavailable"))?;
    let (sender, receiver) = std::sync::mpsc::sync_channel(1);
    let reader = std::thread::spawn(move || {
        let mut b = Zeroizing::new(Vec::new());
        let result = stdout.take(262150).read_to_end(&mut b);
        let _ = sender.send((result, b));
    });
    let mut bytes = None;
    let mut status = None;
    loop {
        if let Ok((read, b)) = receiver.try_recv() {
            if read.is_err() || b.len() > 262149 {
                let _ = child.kill();
                let _ = child.wait();
                let _ = reader.join();
                return fail("response_too_large");
            }
            bytes = Some(b);
        }
        match child.try_wait() {
            Ok(Some(s)) => status = Some(s),
            Ok(None) => (),
            Err(_) => {
                let _ = child.kill();
                let _ = child.wait();
                let _ = reader.join();
                return fail("dispatch_outcome_unknown");
            }
        }
        if bytes.is_some() && status.is_some() {
            break;
        }
        if started.elapsed() > Duration::from_secs(61) {
            let _ = child.kill();
            let _ = child.wait();
            let _ = reader.join();
            return fail("dispatch_outcome_unknown");
        }
        std::thread::sleep(Duration::from_millis(10));
    }
    let _ = reader.join();
    let b = bytes.unwrap();
    let status = status.unwrap();
    if !status.success() {
        // Once curl has started, a nonzero exit cannot establish that the
        // server did not receive the request (including connection loss).
        return fail("dispatch_outcome_unknown");
    }
    decode_wire(&b)
}
fn decode_wire(b: &[u8]) -> R<Zeroizing<Vec<u8>>> {
    let split = b
        .iter()
        .rposition(|b| *b == b'\n')
        .ok_or_else(|| Error::new("provider_protocol"))?;
    if split > 262144 {
        return fail("response_too_large");
    }
    let code = std::str::from_utf8(&b[split + 1..])
        .ok()
        .and_then(|s| s.parse::<u16>().ok())
        .ok_or_else(|| Error::new("provider_protocol"))?;
    if !(200..300).contains(&code) {
        return fail(match code {
            401 | 403 => "provider_authentication",
            404 | 422 => "provider_model",
            408 | 504 => "dispatch_outcome_unknown",
            500..=599 => "provider_unavailable",
            _ => "provider_protocol",
        });
    }
    Ok(Zeroizing::new(b[..split].to_vec()))
}
pub fn models(key: &[u8]) -> R<Vec<String>> {
    let b = call("/models", None, key)?;
    decode_models(&b)
}
fn decode_models(b: &[u8]) -> R<Vec<String>> {
    let v: Value = serde_json::from_slice(b).map_err(|_| Error::new("provider_protocol"))?;
    let rows = v["data"]
        .as_array()
        .ok_or_else(|| Error::new("provider_protocol"))?;
    if rows.is_empty() || rows.len() > 256 {
        return fail("provider_protocol");
    }
    rows.iter()
        .map(|r| {
            let s = r["id"]
                .as_str()
                .ok_or_else(|| Error::new("provider_protocol"))?;
            if s.is_empty()
                || s.len() > 128
                || !s
                    .bytes()
                    .all(|b| b.is_ascii_alphanumeric() || b"_.:-".contains(&b))
            {
                return fail("provider_protocol");
            }
            Ok(s.into())
        })
        .collect()
}
pub struct DeepSeekModel;
impl crate::model_port::ModelPort for DeepSeekModel {
    fn generate(&mut self, body: &str, key: &[u8]) -> R<crate::model_port::ModelResponse> {
        self.generate_with_receipt(body, key, &mut || {})
    }
    fn generate_with_receipt(
        &mut self,
        body: &str,
        key: &[u8],
        received: &mut dyn FnMut(),
    ) -> R<crate::model_port::ModelResponse> {
        let bytes = call_received("/chat/completions", Some(body), key, received)?;
        let v: Value =
            serde_json::from_slice(&bytes).map_err(|_| Error::new("provider_protocol"))?;
        let text = v["choices"][0]["message"]["content"]
            .as_str()
            .ok_or_else(|| Error::new("provider_protocol"))?;
        if text.is_empty() || text.len() > 65536 || text.chars().count() > 16000 {
            return fail("response_too_large");
        }
        let mut usage = serde_json::json!({});
        for (remote, local) in [
            ("prompt_tokens", "inputTokens"),
            ("completion_tokens", "outputTokens"),
        ] {
            if let Some(n) = v["usage"][remote]
                .as_u64()
                .filter(|n| *n <= 9007199254740991)
            {
                usage[local] = serde_json::json!(n);
            }
        }
        Ok(crate::model_port::ModelResponse {
            text: text.into(),
            usage: if usage.as_object().unwrap().is_empty() {
                None
            } else {
                Some(usage)
            },
        })
    }
}

#[cfg(test)]
mod p149_transport_checks {
    use super::*;
    #[test]
    fn p149_runtime_env_cannot_enable_transport() {
        assert!(!crate::runtime_root::is_real());
        let previous = std::env::var_os("LIFEOS_P3_149_BUILD_PROFILE");
        std::env::set_var("LIFEOS_P3_149_BUILD_PROFILE", "source-pilot-1");
        let result = models(b"synthetic-only-secret");
        match previous {
            Some(v) => std::env::set_var("LIFEOS_P3_149_BUILD_PROFILE", v),
            None => std::env::remove_var("LIFEOS_P3_149_BUILD_PROFILE"),
        };
        assert_eq!(result.unwrap_err().code, "real_capability_denied");
    }
    #[test]
    fn p149_http_response_envelopes_are_bounded_and_fixed_errors() {
        assert_eq!(&*decode_wire(b"fictional\n200").unwrap(), b"fictional");
        for (code, expected) in [
            (401, "provider_authentication"),
            (422, "provider_model"),
            (504, "dispatch_outcome_unknown"),
            (500, "provider_unavailable"),
        ] {
            assert_eq!(
                decode_wire(format!("do not return fictional response body\n{code}").as_bytes())
                    .unwrap_err()
                    .code,
                expected
            );
        }
        assert!(decode_wire(format!("{}\n200", "x".repeat(262145)).as_bytes()).is_err());
        assert_eq!(
            decode_models(br#"{"data":[{"id":"fiction-model"}]}"#).unwrap(),
            vec!["fiction-model"]
        );
        for input in [
            br#"{"data":[]}"#.as_slice(),
            br#"{"data":[{"id":"invalid model"}]}"#,
            br#"{"wrong":[]}"#,
        ] {
            assert!(decode_models(input).is_err());
        }
    }
}
