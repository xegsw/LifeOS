//! P3-148 closed request contracts. No filesystem, provider or credential effects.
use crate::repository::{Error, Request};
use serde_json::Value;
pub type R<T> = Result<T, Error>;
pub fn fail<T>(code: &str) -> R<T> {
    Err(Error::new(code))
}
pub fn fields(v: &Value, required: &[&str], optional: &[&str]) -> R<()> {
    let o = v.as_object().ok_or_else(|| Error::new("dto_rejected"))?;
    if o.keys()
        .any(|k| !required.contains(&k.as_str()) && !optional.contains(&k.as_str()))
    {
        return fail("unknown_field");
    }
    if required.iter().any(|k| !o.contains_key(*k)) || o.values().any(Value::is_null) {
        return fail("dto_rejected");
    }
    Ok(())
}
pub fn id(v: &Value, k: &str) -> R<String> {
    let s = v[k]
        .as_str()
        .ok_or_else(|| Error::new("identity_rejected"))?;
    if s.is_empty()
        || s.len() > 120
        || !s
            .bytes()
            .all(|b| b.is_ascii_alphanumeric() || b"_:-".contains(&b))
    {
        return fail("identity_rejected");
    }
    Ok(s.into())
}
pub fn num(v: &Value, k: &str, min: u64) -> R<u64> {
    v[k].as_u64()
        .filter(|n| *n >= min && *n <= 9007199254740991)
        .ok_or_else(|| Error::new("integer_rejected"))
}
pub fn text(v: &Value, k: &str, empty: bool) -> R<String> {
    let s = v[k].as_str().ok_or_else(|| Error::new("text_rejected"))?;
    if (!empty && s.trim().is_empty()) || s.chars().count() > 2000 || s.len() > 8192 {
        return fail("text_rejected");
    }
    Ok(s.into())
}
pub fn ids(v: &Value, k: &str, max: usize) -> R<Vec<String>> {
    let a = v[k].as_array().ok_or_else(|| Error::new("dto_rejected"))?;
    if a.len() > max {
        return fail("dto_rejected");
    }
    let mut out = Vec::new();
    for s in a {
        let x = id(&serde_json::json!({"id":s}), "id")?;
        if out.contains(&x) {
            return fail("dto_rejected");
        }
        out.push(x)
    }
    Ok(out)
}
