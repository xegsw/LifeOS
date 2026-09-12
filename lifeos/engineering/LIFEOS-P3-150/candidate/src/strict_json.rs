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

#[cfg(test)] mod tests {use super::*;#[test]fn duplicate_and_trailing_rejected(){assert!(parse(r#"{"a":1,"a":2}"#).is_err());assert!(parse("{} {}").is_err());assert!(parse(r#"{"a":[1,null]}"#).is_ok());}}
