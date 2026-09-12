//! Model capability owns no repository, authorization, source or tool access.
use crate::conversation_contract::*;
use crate::repository::Error;
use serde_json::{json, Value};
pub struct ModelResponse {
    pub text: String,
    pub usage: Option<Value>,
}
/// D0673 metadata only: never provider text, reasoning, headers or errors.
#[derive(Default,Clone,Debug,serde::Serialize)]
pub struct ModelDiagnostics {
 pub finish_reason: Option<FinishReason>,
 pub prompt_tokens: Option<u64>,
 pub completion_tokens: Option<u64>,
 pub total_tokens: Option<u64>,
}
#[derive(Clone,Debug,serde::Serialize)]
#[serde(rename_all="snake_case")]
pub enum FinishReason {Stop,Length,ToolCalls,ContentFilter,InsufficientSystemResource,Unknown}
pub trait ModelPort {
    fn generate_proactive(&mut self,body:&str,key:&[u8],received:&mut dyn FnMut())->R<ModelResponse>{
        if crate::runtime_root::network_enabled(){return fail("real_capability_denied")}
        self.generate_with_receipt(body,key,received)
    }
    fn generate(&mut self, exact_body: &str, key: &[u8]) -> R<ModelResponse>;
    /// Receipt means this adapter has accepted the immutable request. The caller's
    /// coordinator is held on entry and released by received(), before response work.
    /// Network adapters override this at their bounded transport acceptance point.
    /// v8 passes its remaining active wall-time budget, excluding human waits.
    /// A network port must override this to enforce the transport deadline.
    fn generate_bounded_with_receipt(&mut self, body: &str, key: &[u8], budget_ms: u64, received: &mut dyn FnMut()) -> R<ModelResponse> {
        if budget_ms==0 || budget_ms>60000 { return fail("activity_budget_exceeded"); }
        if crate::runtime_root::network_enabled() { return fail("real_capability_denied"); }
        self.generate_with_receipt(body,key,received)
    }
    fn generate_diagnosed_with_receipt(&mut self,body:&str,key:&[u8],budget_ms:u64,received:&mut dyn FnMut(),_diagnostics:&mut dyn FnMut(ModelDiagnostics))->R<ModelResponse>{
        self.generate_bounded_with_receipt(body,key,budget_ms,received)
    }
    fn generate_with_receipt(
        &mut self,
        body: &str,
        key: &[u8],
        received: &mut dyn FnMut(),
    ) -> R<ModelResponse> {
        received();
        self.generate(body, key)
    }
}
pub struct SyntheticModel;
impl ModelPort for SyntheticModel {
    fn generate(&mut self, body: &str, _key: &[u8]) -> R<ModelResponse> {
        if crate::runtime_root::network_enabled() {
            return fail("real_capability_denied");
        }
        let b: Value = serde_json::from_str(body).map_err(|_| Error::new("provider_protocol"))?;
        let content = b["messages"][1]["content"]
            .as_str()
            .ok_or_else(|| Error::new("provider_protocol"))?;
        let quoted = content
            .split("[C1] source\n")
            .nth(1)
            .and_then(|s| s.split("\n\n").next())
            .ok_or_else(|| Error::new("provider_protocol"))?;
        Ok(ModelResponse{text:format!("合成离线演练：本次提交的来源片段为「{quoted}」[C1]。此回答用于验证发送、引用和反馈流程，不代表真实模型理解。"),usage:None})
    }
}
pub fn citations(text: &str, items: &[Value]) -> (Vec<Value>, usize) {
    let mut valid = Vec::new();
    let mut invalid = 0;
    for chunk in text.split('[').skip(1) {
        let Some(end) = chunk.find(']') else { continue };
        let id = &chunk[..end];
        if !id.starts_with('C') {
            continue;
        }
        if let Some(item) = items
            .iter()
            .find(|i| i["kind"] == "source" && i["citationId"] == id)
        {
            if !valid.iter().any(|c: &Value| c["citationId"] == id) {
                valid.push(
                    json!({"citationId":id,"source":item["source"],"availability":"available"}),
                );
            }
        } else {
            invalid += 1
        }
    }
    (valid, invalid)
}
