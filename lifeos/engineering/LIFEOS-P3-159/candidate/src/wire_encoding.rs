//! Canonical base64 for credential envelopes; no permissive decoder fallbacks.
use crate::conversation_contract::*;
const ALPHABET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
pub fn encode(bytes: &[u8]) -> String {
    let mut out = String::new();
    for c in bytes.chunks(3) {
        let a = c[0] as u32;
        let b = *c.get(1).unwrap_or(&0) as u32;
        let d = *c.get(2).unwrap_or(&0) as u32;
        let n = (a << 16) | (b << 8) | d;
        out.push(ALPHABET[((n >> 18) & 63) as usize] as char);
        out.push(ALPHABET[((n >> 12) & 63) as usize] as char);
        out.push(if c.len() > 1 {
            ALPHABET[((n >> 6) & 63) as usize] as char
        } else {
            '='
        });
        out.push(if c.len() > 2 {
            ALPHABET[(n & 63) as usize] as char
        } else {
            '='
        });
    }
    out
}
pub fn decode(s: &str) -> R<Vec<u8>> {
    if s.len() > 4096 || !s.len().is_multiple_of(4) {
        return fail("credential_authentication_failed");
    }
    let mut out = Vec::new();
    for c in s.as_bytes().chunks(4) {
        let mut n = 0u32;
        for b in c {
            let v = if *b == b'=' {
                0
            } else {
                match ALPHABET.iter().position(|x| x == b) {
                    Some(i) => i as u32,
                    None => return fail("credential_authentication_failed"),
                }
            };
            n = (n << 6) | v;
        }
        out.push((n >> 16) as u8);
        if c[2] != b'=' {
            out.push((n >> 8) as u8)
        }
        if c[3] != b'=' {
            out.push(n as u8)
        }
    }
    if encode(&out) != s {
        return fail("credential_authentication_failed");
    }
    Ok(out)
}
