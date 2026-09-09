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
        ("/chat/completions", true)
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
                    return fail("provider_timeout");
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
        return fail(exit_failure(status.code()));
    }
    decode_wire(&b)
}
fn exit_failure(code:Option<i32>)->&'static str{match code{Some(28)=>"provider_timeout",Some(5|6|7|35|60)=>"provider_network",_=>"dispatch_outcome_unknown"}}
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
            408 | 504 => "provider_timeout",
            500..=599 => "provider_unavailable",
            _ => "provider_protocol",
        });
    }
    Ok(Zeroizing::new(b[..split].to_vec()))
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

#[cfg(test)]mod p152_tests {
 use super::*;use crate::model_port::ModelPort;
 #[test]fn synthetic_cannot_execute_real_transport(){let result=DeepSeekModel.generate("{}",b"p152-secret-canary");assert_eq!(result.err().unwrap().code,"real_capability_denied");}
 #[test]fn wire_errors_are_fixed_and_do_not_return_body(){for(code,want)in[(401,"provider_authentication"),(422,"provider_model"),(504,"provider_timeout"),(500,"provider_unavailable")]{let e=decode_wire(format!("p152-secret-and-private-body\n{code}").as_bytes()).unwrap_err();assert_eq!(e.code,want);}assert_eq!(exit_failure(Some(28)),"provider_timeout");assert_eq!(exit_failure(Some(7)),"provider_network");assert_eq!(exit_failure(None),"dispatch_outcome_unknown");}
}
