//! Preserve duplicate-key rejection at raw JSON entrypoints (stdio fixture runner).
use serde::{
    de::{Error as _, MapAccess, SeqAccess, Visitor},
    Deserialize, Deserializer,
};
use serde_json::{Map, Number, Value};
struct Unique(Value);
impl<'de> Deserialize<'de> for Unique {
    fn deserialize<D: Deserializer<'de>>(d: D) -> Result<Self, D::Error> {
        d.deserialize_any(UniqueVisitor)
    }
}
struct UniqueVisitor;
impl<'de> Visitor<'de> for UniqueVisitor {
    type Value = Unique;
    fn expecting(&self, f: &mut std::fmt::Formatter) -> std::fmt::Result {
        f.write_str("JSON without duplicate keys")
    }
    fn visit_bool<E: serde::de::Error>(self, v: bool) -> Result<Unique, E> {
        Ok(Unique(Value::Bool(v)))
    }
    fn visit_i64<E: serde::de::Error>(self, v: i64) -> Result<Unique, E> {
        Ok(Unique(Value::Number(v.into())))
    }
    fn visit_u64<E: serde::de::Error>(self, v: u64) -> Result<Unique, E> {
        Ok(Unique(Value::Number(v.into())))
    }
    fn visit_f64<E: serde::de::Error>(self, v: f64) -> Result<Unique, E> {
        Ok(Unique(Value::Number(
            Number::from_f64(v).ok_or_else(|| E::custom("dto_rejected"))?,
        )))
    }
    fn visit_str<E: serde::de::Error>(self, v: &str) -> Result<Unique, E> {
        Ok(Unique(Value::String(v.into())))
    }
    fn visit_string<E: serde::de::Error>(self, v: String) -> Result<Unique, E> {
        Ok(Unique(Value::String(v)))
    }
    fn visit_unit<E: serde::de::Error>(self) -> Result<Unique, E> {
        Ok(Unique(Value::Null))
    }
    fn visit_seq<A: SeqAccess<'de>>(self, mut a: A) -> Result<Unique, A::Error> {
        let mut v = Vec::new();
        while let Some(x) = a.next_element::<Unique>()? {
            v.push(x.0)
        }
        Ok(Unique(Value::Array(v)))
    }
    fn visit_map<A: MapAccess<'de>>(self, mut a: A) -> Result<Unique, A::Error> {
        let mut map = Map::new();
        while let Some(k) = a.next_key::<String>()? {
            if map.contains_key(&k) {
                return Err(A::Error::custom("duplicate_field"));
            }
            map.insert(k, a.next_value::<Unique>()?.0);
        }
        Ok(Unique(Value::Object(map)))
    }
}
pub fn parse(s: &str) -> Result<Value, crate::repository::Error> {
    let mut d = serde_json::Deserializer::from_str(s);
    let value = Unique::deserialize(&mut d).and_then(|v| {
        d.end()?;
        Ok(v.0)
    });
    value.map_err(|e| {
        crate::repository::Error::new(if e.to_string().starts_with("duplicate_field") {
            "duplicate_field"
        } else {
            "dto_rejected"
        })
    })
}

#[cfg(test)]
mod boundary_tests {
    use super::*;

    // Source-bound reproduction of tauri 2.11.5 protocol.rs:527 and
    // command.rs:97. This is NOT a live WebView/IPC invocation or a T08 PASS.
    #[test]
    fn p149_tauri_value_boundary_loses_duplicate_keys_before_request() {
        let cases = [
            r#"{"request":{"version":3,"version":3,"operation":"read_settings","payload":{}}}"#,
            r#"{"request":{"version":3,"operation":"read_settings","operation":"read_settings","payload":{}}}"#,
            r#"{"request":{"version":3,"operation":"read_conversation","payload":{"conversationId":"first","conversationId":"last"}}}"#,
            r#"{"request":{"version":3,"operation":"read_settings","payload":{}},"request":{"version":3,"operation":"read_settings","payload":{}}}"#,
        ];
        for raw in cases {
            assert_eq!(parse(raw).unwrap_err().code, "duplicate_field");
            let body: tauri::ipc::InvokeBody = serde_json::from_slice::<Value>(raw.as_bytes())
                .unwrap()
                .into();
            let tauri::ipc::InvokeBody::Json(value) = body else {
                panic!("JSON expected")
            };
            let request: crate::repository::Request =
                serde_json::from_value(value.get("request").unwrap().clone()).unwrap();
            assert_eq!(request.version, 3);
            if request.operation == "read_conversation" {
                assert_eq!(request.payload["conversationId"], "last");
            }
            // Re-serializing the Value cannot recover lost duplicate information.
            assert!(parse(&serde_json::to_string(&value).unwrap()).is_ok());
        }
    }
}
