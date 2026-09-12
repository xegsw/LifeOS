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
    call_received_with_budget(path,body,key,60000,received)
}
fn call_received_with_budget(path:&str,body:Option<&str>,key:&[u8],budget_ms:u64,received:&mut dyn FnMut())->R<Zeroizing<Vec<u8>>>{
    call_received_limited(path,body,key,budget_ms,65536,received)
}
fn call_received_limited(path:&str,body:Option<&str>,key:&[u8],budget_ms:u64,response_limit:usize,received:&mut dyn FnMut())->R<Zeroizing<Vec<u8>>>{
    if budget_ms==0 || budget_ms>60000 { return fail("activity_budget_exceeded"); }
    let deadline=Instant::now()+Duration::from_millis(budget_ms);
    if !crate::runtime_root::network_enabled() {
        return fail("real_capability_denied");
    }
    if !matches!(
        (path, body.is_some()),
        ("/chat/completions", true) | ("/models", false)
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
            &format!("{:.3}",budget_ms.min(15000) as f64/1000.0),
            "--max-time",
            &format!("{:.3}",budget_ms as f64/1000.0),
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
                if Instant::now() >= deadline {
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
        let result = stdout.take((response_limit+6) as u64).read_to_end(&mut b);
        let _ = sender.send((result, b));
    });
    let mut bytes = None;
    let mut status = None;
    loop {
        if let Ok((read, b)) = receiver.try_recv() {
            if read.is_err() || b.len() > response_limit+5 {
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
        if Instant::now() >= deadline {
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
    decode_wire_limited(&b,response_limit)
}
fn exit_failure(code:Option<i32>)->&'static str{match code{Some(28)=>"provider_timeout",Some(5|6|7|35|60)=>"provider_network",_=>"dispatch_outcome_unknown"}}
fn decode_wire(b: &[u8]) -> R<Zeroizing<Vec<u8>>> {decode_wire_limited(b,65536)}
fn decode_wire_limited(b:&[u8],response_limit:usize)->R<Zeroizing<Vec<u8>>>{
    let split = b
        .iter()
        .rposition(|b| *b == b'\n')
        .ok_or_else(|| Error::new("provider_protocol"))?;
    if split > response_limit {
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
            429 => "provider_rate_limited",
            500..=599 => "provider_unavailable",
            _ => "provider_protocol",
        });
    }
    Ok(Zeroizing::new(b[..split].to_vec()))
}
pub fn models(key:&[u8])->R<Vec<String>>{let body=call("/models",None,key)?;decode_models(&body,key)}
fn decode_models(body:&[u8],key:&[u8])->R<Vec<String>>{
 if !key.is_empty()&&body.windows(key.len()).any(|v|v==key){return fail("provider_protocol");}
 let v:Value=serde_json::from_slice(body).map_err(|_|Error::new("provider_protocol"))?;
 let rows=v["data"].as_array().ok_or_else(||Error::new("provider_protocol"))?;
 if rows.is_empty()||rows.len()>256{return fail("provider_protocol");}
 let mut out=Vec::new();
 for row in rows {let id=row["id"].as_str().ok_or_else(||Error::new("provider_protocol"))?;
  if std::str::from_utf8(key).ok().is_some_and(|k|!k.is_empty()&&id.contains(k))||id.is_empty()||id.len()>128||!id.bytes().all(|b|b.is_ascii_alphanumeric()||b"_.:-".contains(&b))||out.iter().any(|s|s==id){return fail("provider_protocol");}out.push(id.to_owned());
 }if serde_json::to_vec(&out).map_err(|_|Error::new("provider_protocol"))?.len()>8192{return fail("response_too_large");}Ok(out)
}
pub struct DeepSeekModel;
impl crate::model_port::ModelPort for DeepSeekModel {
    fn generate_proactive(&mut self,body:&str,key:&[u8],received:&mut dyn FnMut())->R<crate::model_port::ModelResponse>{
        let bytes=call_received_limited("/chat/completions",Some(body),key,60000,1_048_576,received)?;decode_chat_limited(&bytes,1_048_576,1_048_576)
    }
    fn generate_diagnosed_with_receipt(&mut self,body:&str,key:&[u8],budget_ms:u64,received:&mut dyn FnMut(),diagnostics:&mut dyn FnMut(crate::model_port::ModelDiagnostics))->R<crate::model_port::ModelResponse>{
        let bytes=call_received_with_budget("/chat/completions",Some(body),key,budget_ms,received)?;
        diagnostics(chat_diagnostics(&bytes));
        decode_chat_response(&bytes)
    }
    fn generate_bounded_with_receipt(&mut self,body:&str,key:&[u8],budget_ms:u64,received:&mut dyn FnMut())->R<crate::model_port::ModelResponse>{
        let bytes=call_received_with_budget("/chat/completions",Some(body),key,budget_ms,received)?;
        decode_chat_response(&bytes)
    }
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
        decode_chat_response(&bytes)
    }
}

fn chat_diagnostics(bytes:&[u8])->crate::model_port::ModelDiagnostics {
 use crate::model_port::{ModelDiagnostics,FinishReason};
 let Ok(v)=serde_json::from_slice::<Value>(bytes) else{return ModelDiagnostics::default()};
 let finish_reason=v["choices"][0]["finish_reason"].as_str().map(|r|match r {"stop"=>FinishReason::Stop,"length"=>FinishReason::Length,"tool_calls"=>FinishReason::ToolCalls,"content_filter"=>FinishReason::ContentFilter,"insufficient_system_resource"=>FinishReason::InsufficientSystemResource,_=>FinishReason::Unknown});
 let n=|k:&str|v["usage"][k].as_u64().filter(|n|*n<=9007199254740991);
 ModelDiagnostics{finish_reason,prompt_tokens:n("prompt_tokens"),completion_tokens:n("completion_tokens"),total_tokens:n("total_tokens")}
}
pub(crate) fn decode_chat_response(bytes:&[u8])->R<crate::model_port::ModelResponse>{decode_chat_limited(bytes,65536,16000)}
fn decode_chat_limited(bytes:&[u8],byte_limit:usize,scalar_limit:usize)->R<crate::model_port::ModelResponse>{
        let v: Value =
            serde_json::from_slice(&bytes).map_err(|_| Error::new("provider_protocol"))?;
        if v["choices"][0]["finish_reason"]=="length"{return fail("provider_response_truncated");}
        if v["choices"][0].get("finish_reason").is_some_and(|r|r!="stop"){return fail("provider_protocol");}
        let text = v["choices"][0]["message"]["content"]
            .as_str()
            .ok_or_else(|| Error::new("provider_protocol"))?;
        if text.is_empty(){return fail("provider_response_empty");}
        if text.len() > byte_limit || text.chars().count() > scalar_limit {
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

#[cfg(test)]mod p152_tests {
 use super::*;use crate::model_port::ModelPort;
 #[test]fn synthetic_cannot_execute_real_transport(){let result=DeepSeekModel.generate("{}",b"p152-secret-canary");assert_eq!(result.err().unwrap().code,"real_capability_denied");}
 #[test]fn wire_errors_are_fixed_and_do_not_return_body(){for(code,want)in[(401,"provider_authentication"),(422,"provider_model"),(504,"provider_timeout"),(500,"provider_unavailable")]{let e=decode_wire(format!("p152-secret-and-private-body\n{code}").as_bytes()).unwrap_err();assert_eq!(e.code,want);}assert_eq!(exit_failure(Some(28)),"provider_timeout");assert_eq!(exit_failure(Some(7)),"provider_network");assert_eq!(exit_failure(None),"dispatch_outcome_unknown");}
}

#[cfg(test)]mod models_tests{use super::*;#[test]fn model_directory_is_bounded_distinct_and_never_echoes_key(){assert_eq!(decode_models(br#"{"data":[{"id":"model-a"},{"id":"model-b"}]}"#,b"fictional-key").unwrap().len(),2);for b in [br#"{"data":[]}"#.as_slice(),br#"{"data":[{"id":"same"},{"id":"same"}]}"#,br#"{"data":[{"id":"bad id"}]}"#,br#"{"data":[{"id":"fictional-key"}]}"#]{assert!(decode_models(b,b"fictional-key").is_err());}}#[test]fn synthetic_transport_cannot_access_models_network(){assert_eq!(models(b"fictional-key").unwrap_err().code,"real_capability_denied");}}

#[cfg(test)] mod d0673_tests {use super::*;
 #[test]fn diagnostics_drop_all_content_and_preserve_only_bounded_metadata(){let raw=serde_json::json!({"choices":[{"finish_reason":"secret-canary","message":{"content":"secret-canary","reasoning_content":"secret-canary"}}],"usage":{"prompt_tokens":42,"completion_tokens":-1,"total_tokens":9007199254740992u64,"private":"secret-canary"}}).to_string();let d=serde_json::to_value(chat_diagnostics(raw.as_bytes())).unwrap();assert_eq!(d["finish_reason"],"unknown");assert_eq!(d["prompt_tokens"],42);assert!(d["completion_tokens"].is_null()&&d["total_tokens"].is_null());assert!(!d.to_string().contains("secret-canary"));}
 #[test]fn truncated_metadata_remains_available_without_accepting_response(){let raw=br#"{"choices":[{"finish_reason":"length","message":{"content":"{}"}}],"usage":{"completion_tokens":1024}}"#;assert_eq!(chat_diagnostics(raw).completion_tokens,Some(1024));assert_eq!(decode_chat_response(raw).err().unwrap().code,"provider_response_truncated");assert!(chat_diagnostics(b"{").finish_reason.is_none());}
}

#[cfg(test)] mod proactive_limits_tests {
    use super::*;
    #[test] fn proactive_response_limit_does_not_expand_ordinary_chat() {
        let mut wire = vec![b'x'; 65_537];
        wire.extend_from_slice(b"\n200");
        assert_eq!(decode_wire(&wire).unwrap_err().code, "response_too_large");
        assert_eq!(decode_wire_limited(&wire, 1_048_576).unwrap().len(), 65_537);
        let mut exact = vec![b'x'; 1_048_576];
        exact.extend_from_slice(b"\n200");
        assert_eq!(decode_wire_limited(&exact, 1_048_576).unwrap().len(), 1_048_576);
        exact.insert(0, b'x');
        assert_eq!(decode_wire_limited(&exact, 1_048_576).unwrap_err().code, "response_too_large");
    }
}
