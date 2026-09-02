use serde_json::{json, Value};
use std::io::Write;
use std::process::{Command, Stdio};
use zeroize::Zeroize;

pub const AUTHORITY: &str = "https://api.deepseek.com";
pub const FIXED_CANARY: &str = "LifeOS secure activation canary. Reply with exactly: OK";

#[derive(Clone, Debug)]
pub struct NetworkReceipt {
    pub authority: &'static str,
    pub method_class: &'static str,
    pub status_class: String,
    pub timestamp_ms: i64,
    pub request_bucket: &'static str,
    pub response_bucket: &'static str,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub enum AdapterFailure {
    Authorization,
    Authentication,
    Timeout,
    Network,
    Model,
    Capability,
    Protocol,
}

#[derive(Clone, Debug)]
pub struct ModelList {
    pub models: Vec<String>,
    pub receipt: NetworkReceipt,
}

#[derive(Clone, Debug)]
pub struct CanaryResponse {
    pub transient_response: String,
    pub receipt: NetworkReceipt,
}

fn is_safe_model_id(value: &str) -> bool {
    !value.is_empty()
        && value.len() <= 128
        && value
            .bytes()
            .all(|byte| byte.is_ascii_alphanumeric() || matches!(byte, b'-' | b'_' | b'.' | b':'))
}

fn request_bucket(length: usize) -> &'static str {
    if length == 0 {
        "0B"
    } else if length <= 1024 {
        "1KiB_or_less"
    } else {
        "over_1KiB"
    }
}

fn response_bucket(length: usize) -> &'static str {
    if length == 0 {
        "0B"
    } else if length <= 1024 {
        "1KiB_or_less"
    } else if length <= 8192 {
        "8KiB_or_less"
    } else {
        "over_8KiB"
    }
}

fn classify(status: u16, had_process_error: bool) -> AdapterFailure {
    if had_process_error || status == 0 {
        return AdapterFailure::Network;
    }
    match status {
        401 | 403 => AdapterFailure::Authentication,
        408 | 504 => AdapterFailure::Timeout,
        404 | 422 => AdapterFailure::Model,
        400..=499 => AdapterFailure::Protocol,
        500..=599 => AdapterFailure::Capability,
        _ => AdapterFailure::Protocol,
    }
}

fn curl_escape(value: &str) -> String {
    value
        .replace('\\', "\\\\")
        .replace('"', "\\\"")
        .replace('\n', "\\n")
        .replace('\r', "\\r")
}

fn call(
    method: &'static str,
    path: &'static str,
    api_key: &str,
    body: Option<Value>,
    timestamp_ms: i64,
) -> Result<(Vec<u8>, NetworkReceipt), AdapterFailure> {
    if !matches!(path, "/models" | "/chat/completions") || api_key.is_empty() {
        return Err(AdapterFailure::Authorization);
    }
    let url = format!("{AUTHORITY}{path}");
    let mut config = format!(
        "header = \"Authorization: Bearer {}\"\nheader = \"Content-Type: application/json\"\n",
        curl_escape(api_key)
    );
    if let Some(value) = body {
        let raw = serde_json::to_string(&value).map_err(|_| AdapterFailure::Protocol)?;
        config.push_str(&format!("data = \"{}\"\n", curl_escape(&raw)));
    }
    let request_size = config.len();
    let mut child = Command::new("/usr/bin/curl")
        .env_clear()
        .arg("-q")
        .arg("--silent")
        .arg("--show-error")
        .arg("--request")
        .arg(method)
        .arg("--url")
        .arg(&url)
        .arg("--proto")
        .arg("=https")
        .arg("--proto-redir")
        .arg("=https")
        .arg("--max-redirs")
        .arg("0")
        .arg("--noproxy")
        .arg("*")
        .arg("--proxy")
        .arg("")
        .arg("--connect-timeout")
        .arg("15")
        .arg("--max-time")
        .arg("30")
        .arg("--config")
        .arg("-")
        .arg("--write-out")
        .arg("\n%{http_code}")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|_| AdapterFailure::Network)?;
    if let Some(mut stdin) = child.stdin.take() {
        stdin
            .write_all(config.as_bytes())
            .map_err(|_| AdapterFailure::Network)?;
    } else {
        return Err(AdapterFailure::Network);
    }
    config.zeroize();
    let output = child
        .wait_with_output()
        .map_err(|_| AdapterFailure::Network)?;
    let split = output.stdout.iter().rposition(|byte| *byte == b'\n');
    let (mut response, status) = match split {
        Some(index) => {
            let status = std::str::from_utf8(&output.stdout[index + 1..])
                .ok()
                .and_then(|value| value.trim().parse::<u16>().ok())
                .unwrap_or(0);
            (output.stdout[..index].to_vec(), status)
        }
        None => (Vec::new(), 0),
    };
    let receipt = NetworkReceipt {
        authority: AUTHORITY,
        method_class: method,
        status_class: if (200..300).contains(&status) {
            "2xx".into()
        } else if status == 0 {
            "no_http_status".into()
        } else {
            format!("{}xx", status / 100)
        },
        timestamp_ms,
        request_bucket: request_bucket(request_size),
        response_bucket: response_bucket(response.len()),
    };
    if !output.status.success() || !(200..300).contains(&status) {
        response.zeroize();
        return Err(classify(status, !output.status.success()));
    }
    Ok((response, receipt))
}

pub fn synthetic_models(timestamp_ms: i64) -> ModelList {
    ModelList {
        models: vec!["deepseek-synthetic-v1".into()],
        receipt: NetworkReceipt {
            authority: AUTHORITY,
            method_class: "NONE",
            status_class: "synthetic_no_network".into(),
            timestamp_ms,
            request_bucket: "0B",
            response_bucket: "0B",
        },
    }
}

pub fn real_models(api_key: &str, timestamp_ms: i64) -> Result<ModelList, AdapterFailure> {
    let (mut bytes, receipt) = call("GET", "/models", api_key, None, timestamp_ms)?;
    let parsed: Value = match serde_json::from_slice(&bytes) {
        Ok(value) => value,
        Err(_) => {
            bytes.zeroize();
            return Err(AdapterFailure::Protocol);
        }
    };
    bytes.zeroize();
    let models = parsed
        .get("data")
        .and_then(Value::as_array)
        .ok_or(AdapterFailure::Protocol)?
        .iter()
        .filter_map(|item| item.get("id").and_then(Value::as_str))
        .filter(|id| is_safe_model_id(id))
        .map(str::to_owned)
        .collect::<Vec<_>>();
    if models.is_empty() {
        return Err(AdapterFailure::Capability);
    }
    Ok(ModelList { models, receipt })
}

pub fn synthetic_canary(timestamp_ms: i64) -> CanaryResponse {
    CanaryResponse {
        transient_response: "合成 canary 已完成；没有网络请求。".into(),
        receipt: NetworkReceipt {
            authority: AUTHORITY,
            method_class: "NONE",
            status_class: "synthetic_no_network".into(),
            timestamp_ms,
            request_bucket: "0B",
            response_bucket: "0B",
        },
    }
}

pub fn real_canary(
    api_key: &str,
    model: &str,
    timestamp_ms: i64,
) -> Result<CanaryResponse, AdapterFailure> {
    if !is_safe_model_id(model) {
        return Err(AdapterFailure::Model);
    }
    let request = json!({"model": model, "messages": [{"role": "user", "content": FIXED_CANARY}], "stream": false, "temperature": 0});
    let (mut bytes, receipt) = call(
        "POST",
        "/chat/completions",
        api_key,
        Some(request),
        timestamp_ms,
    )?;
    let parsed: Value = match serde_json::from_slice(&bytes) {
        Ok(value) => value,
        Err(_) => {
            bytes.zeroize();
            return Err(AdapterFailure::Protocol);
        }
    };
    bytes.zeroize();
    let response = parsed
        .get("choices")
        .and_then(Value::as_array)
        .and_then(|items| items.first())
        .and_then(|item| item.get("message"))
        .and_then(|item| item.get("content"))
        .and_then(Value::as_str)
        .filter(|value| !value.is_empty())
        .ok_or(AdapterFailure::Protocol)?;
    Ok(CanaryResponse {
        transient_response: response.to_owned(),
        receipt,
    })
}
