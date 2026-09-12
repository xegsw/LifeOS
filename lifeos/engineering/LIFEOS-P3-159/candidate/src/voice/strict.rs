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
pub fn parse(s: &str) -> Result<Value, &'static str> {
    let mut d = serde_json::Deserializer::from_str(s);
    let value = Unique::deserialize(&mut d).map_err(|_| "json_invalid_or_duplicate")?;
    d.end().map_err(|_| "json_trailing")?;
    Ok(value.0)
}
