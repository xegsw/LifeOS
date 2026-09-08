//! Internal bounded worker; not exposed through IPC until public contract approval.
use crate::{
    repository,
    source_file::FileGrant,
    source_store::{self, Imported, Lease},
};
use repository::Error;
use rusqlite::{params, Connection, OptionalExtension, TransactionBehavior};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
#[cfg(test)]
use std::fs;
use std::{
    fs::File,
    path::{Path, PathBuf},
    process::{Command, Stdio},
    time::{Duration, Instant},
};
type R<T> = Result<T, Error>;
use crate::runtime_root::ROOT;
fn err(s: &str) -> Error {
    Error::new(s)
}
fn stable(s: &str) -> String {
    format!("{:x}", Sha256::digest(s.as_bytes()))
}
fn root_ref(c: &Connection, l: &Lease) -> R<PathBuf> {
    source_store::check(c, l)?;
    let r: String = c.query_row(
        "SELECT root_ref FROM connectors WHERE id=?",
        [&l.connector],
        |r| r.get(0),
    )?;
    if !source_store::valid_id(&r) {
        return Err(err("grant_rejected"));
    }
    Ok(Path::new(ROOT).join("fixtures").join(r))
}
fn granted(c: &Connection, l: &Lease) -> R<FileGrant> {
    let root = root_ref(c, l)?;
    let grant = FileGrant::synthetic(&root)?;
    let identity = grant.root_identity()?;
    let expected:Option<String>=c.query_row("SELECT target_ref FROM connector_grants WHERE id=?1 AND generation=?2 AND state='active'",params![format!("root:{}",l.connector),l.generation],|r|r.get(0)).optional()?;
    if expected != Some(json!([identity.dev, identity.ino]).to_string()) {
        return Err(err("root_identity_changed"));
    }
    Ok(grant)
}
pub fn begin(c: &mut Connection, l: &Lease) -> R<()> {
    source_store::check(c, l)?;
    let root = root_ref(c, l)?;
    let identity = FileGrant::synthetic(&root)?.root_identity()?;
    let key = format!("root:{}", l.connector);
    let expected = json!([identity.dev, identity.ino]).to_string();
    let old: Option<(String, i64)> = c
        .query_row(
            "SELECT target_ref,generation FROM connector_grants WHERE id=?",
            [&key],
            |r| Ok((r.get(0)?, r.get(1)?)),
        )
        .optional()?;
    if old
        .as_ref()
        .is_some_and(|(v, g)| *g == l.generation && *v != expected)
    {
        return Err(err("root_identity_changed"));
    }
    c.execute("INSERT INTO connector_grants VALUES(?1,?2,?3,?4,'active') ON CONFLICT(id) DO UPDATE SET target_ref=excluded.target_ref,generation=excluded.generation,state='active'",params![key,l.connector,expected,l.generation])?;
    let id = format!("scan:{}:{}", l.connector, l.epoch);
    c.execute(
        "INSERT OR IGNORE INTO scan_entries VALUES(?1,?2,'',0,?3,'pending')",
        params![id, l.connector, l.epoch],
    )?;
    Ok(())
}
pub fn scan_page(c: &mut Connection, l: &Lease) -> R<bool> {
    let grant = granted(c, l)?;
    let pending:Option<(String,String,i64)>=c.query_row("SELECT id,parent_ref,cursor FROM scan_entries WHERE connector_id=?1 AND scan_epoch=?2 AND state='pending' ORDER BY id LIMIT 1",params![l.connector,l.epoch],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional()?;
    let Some((id, parent, cursor)) = pending else {
        return Ok(false);
    };
    let identity = serde_json::to_string(&grant.directory_identity(&parent)?)
        .map_err(|_| err("directory_unavailable"))?;
    let prior: Option<String> = c
        .query_row(
            "SELECT identity FROM scan_identities WHERE id=?",
            [&id],
            |r| r.get(0),
        )
        .optional()?;
    if prior.as_ref().is_some_and(|p| p != &identity) {
        return Err(err("directory_changed_refresh_required"));
    }
    let (entries, next, eof) = grant.page(&parent, cursor as u64)?;
    if serde_json::to_string(&grant.directory_identity(&parent)?).unwrap() != identity {
        return Err(err("directory_changed_refresh_required"));
    }
    let tx = c.transaction_with_behavior(TransactionBehavior::Immediate)?;
    source_store::check(&tx, l)?;
    tx.execute(
        "INSERT OR IGNORE INTO scan_identities VALUES(?1,?2)",
        params![id, identity],
    )?;
    for entry in entries {
        let mut rel = if parent.is_empty() {
            entry.name
        } else {
            format!("{parent}/{}", entry.name)
        };
        let is_directory = entry.kind == "directory"
            || (entry.kind == "link" || rel.to_lowercase().ends_with(".alias"))
                && grant.directory_identity(&rel).is_ok();
        if is_directory {
            rel = grant.resolve_ref(&rel)?;
        }
        let fid = stable(&format!("{}:{rel}", l.connector));
        if is_directory {
            tx.execute(
                "INSERT OR IGNORE INTO scan_entries VALUES(?1,?2,?3,0,?4,'pending')",
                params![
                    format!("scan:{}:{}", &fid[..32], l.epoch),
                    l.connector,
                    rel,
                    l.epoch
                ],
            )?;
        } else {
            let state = if entry.kind == "file" || entry.kind == "link" && grant.file(&rel).is_ok()
            {
                "pending"
            } else if entry.kind == "link" {
                "awaiting_target_grant"
            } else {
                "special_file_rejected"
            };
            let checkpoint = json!({"reference":rel,"kind":entry.kind,"fileId":fid});
            tx.execute("INSERT INTO import_jobs VALUES(?1,?2,?3,?4,'{}',?5) ON CONFLICT(id) DO UPDATE SET epoch=excluded.epoch,state=excluded.state,checkpoint=excluded.checkpoint",params![fid,l.connector,l.epoch,state,checkpoint.to_string()])?;
        }
    }
    tx.execute(
        "UPDATE scan_entries SET cursor=?2,state=?3 WHERE id=?1",
        params![id, next as i64, if eof { "done" } else { "pending" }],
    )?;
    tx.commit()?;
    Ok(true)
}
fn artifact_dir(c: &Connection, l: &Lease) -> R<crate::artifact_io::Dir> {
    crate::artifact_io::Dir::root()?
        .child("artifacts", false)?
        .child(
            &stable(&format!("{}:{}", c.path().unwrap_or("memory"), l.connector)),
            true,
        )
}
fn parse(file: File, ext: &str, out: &mut crate::artifact_io::OwnedFile) -> R<Value> {
    out.validate()?;
    let mut child = Command::new(
        "/Users/xxe/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3",
    )
    .args([
        "-B",
        concat!(env!("CARGO_MANIFEST_DIR"), "/tools/parse_source.py"),
        ext,
    ])
    .stdin(Stdio::from(file))
    .stdout(Stdio::from(out.descriptor()?))
    .stderr(Stdio::null())
    .env("TMPDIR", Path::new(ROOT).join(".runtime"))
    .spawn()
    .map_err(|_| err("parser_dependency_missing"))?;
    let start = Instant::now();
    loop {
        if let Some(status) = child.try_wait().map_err(|_| err("parser_failed"))? {
            if !status.success() {
                return Err(err("parser_failed"));
            }
            break;
        }
        if start.elapsed() > Duration::from_secs(30) {
            let _ = child.kill();
            let _ = child.wait();
            return Err(err("parse_timeout"));
        } // Inspect only this parser PID. No ambient process inventory or command text.
        let rss = Command::new("/bin/ps")
            .args(["-o", "rss=", "-p", &child.id().to_string()])
            .output()
            .ok()
            .and_then(|o| String::from_utf8(o.stdout).ok())
            .and_then(|s| s.trim().parse::<u64>().ok());
        let length = match out.len() {
            Ok(n) => n,
            Err(e) => {
                let _ = child.kill();
                let _ = child.wait();
                return Err(e);
            }
        };
        if rss.is_some_and(|kb| kb > 64 * 1024) || length > 64 * 1024 * 1024 {
            let _ = child.kill();
            let _ = child.wait();
            return Err(err("parse_memory_budget"));
        }
        std::thread::sleep(Duration::from_millis(10));
    }
    let bytes = out.read_limit(64 * 1024 * 1024)?;
    serde_json::from_slice(&bytes).map_err(|_| err("parser_failed"))
}
pub fn import_one(c: &mut Connection, l: &Lease) -> R<bool> {
    source_store::check(c, l)?;
    let job:Option<(String,String)>=c.query_row("SELECT id,checkpoint FROM import_jobs WHERE connector_id=?1 AND epoch=?2 AND state='pending' ORDER BY id LIMIT 1",params![l.connector,l.epoch],|r|Ok((r.get(0)?,r.get(1)?))).optional()?;
    let Some((id, raw)) = job else {
        return Ok(false);
    };
    let p: Value = serde_json::from_str(&raw).map_err(|_| err("checkpoint_corrupt"))?;
    let reference = p["reference"]
        .as_str()
        .ok_or_else(|| err("checkpoint_corrupt"))?;
    let grant = granted(c, l)?;
    let identity = match grant.identity(reference) {
        Ok(i) => i,
        Err(e) => {
            c.execute(
                "UPDATE import_jobs SET state='failed',counters=?2 WHERE id=?1",
                params![id, json!({"reason":e.code}).to_string()],
            )?;
            return Ok(true);
        }
    };
    let prior:Option<(i64,String,String)>=c.query_row("SELECT version,CASE WHEN parse_state='revoked' THEN '' ELSE identity END,fingerprint FROM source_files WHERE id=?",[&id],|r|Ok((r.get(0)?,r.get(1)?,r.get(2)?))).optional()?;
    let ident = serde_json::to_string(&identity).unwrap();
    if prior.as_ref().is_some_and(|(_, i, _)| i == &ident) {
        source_store::check(c, l)?;
        c.execute("UPDATE import_jobs SET state='done' WHERE id=?", [&id])?;
        c.execute(
            "UPDATE source_files SET seen_epoch=?2 WHERE id=?1",
            params![id, l.epoch],
        )?;
        return Ok(true);
    }
    let version = prior.map(|v| v.0 + 1).unwrap_or(1);
    let token = format!("{}-{version}-{}", id, l.epoch);
    let dir = artifact_dir(c, l)?;
    let staging_name = format!("{token}.staging");
    // Existing interrupted staging is isolated, never overwritten or treated as success.
    if dir.exists(&staging_name)? {
        c.execute("UPDATE import_jobs SET state='pending_recovery',counters='{\"reason\":\"staging_requires_recovery\"}' WHERE id=?",[&id])?;
        return Ok(true);
    }
    source_store::check(c, l)?;
    let mut staging = dir.create(&staging_name)?;
    let (fingerprint, bytes) = match grant.copy(reference, &identity, &mut staging) {
        Ok(v) => v,
        Err(e) => {
            c.execute(
                "UPDATE import_jobs SET state='failed',counters=?2 WHERE id=?1",
                params![id, json!({"reason":e.code}).to_string()],
            )?;
            return Ok(true);
        }
    };
    let resolved = grant.resolve_ref(reference)?;
    let ext = Path::new(&resolved)
        .extension()
        .and_then(|x| x.to_str())
        .map(|s| format!(".{}", s.to_lowercase()))
        .unwrap_or_default();
    let runtime = crate::artifact_io::Dir::root()?.child(".runtime", false)?;
    let parsed = if bytes > 64 * 1024 * 1024 {
        json!({"status":"pending","reason":"parse_memory_budget","segments":[]})
    } else {
        let mut output = runtime.create(&format!(
            "{}-{token}-{}.parsed",
            stable(c.path().unwrap_or("memory")),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        ))?;
        match parse(staging.descriptor()?, &ext, &mut output) {
            Ok(v) => v,
            Err(e) => json!({"status":"unparsed","reason":e.code,"segments":[]}),
        }
    };
    source_store::check(c, l)?;
    if grant.identity(reference)? != identity {
        return Err(err("source_changed"));
    }
    // Exclusive final inode populated from the held staging FD; DB exposes it only after sync.
    let published = staging.publish(&dir, &token)?;
    let segments = parsed["segments"]
        .as_array()
        .map(|a| {
            a.iter()
                .filter_map(|s| Some((s["locator"].as_str()?.into(), s["text"].as_str()?.into())))
                .collect()
        })
        .unwrap_or_default();
    let item = Imported {
        id: id.clone(),
        external_ref: reference.into(),
        version,
        identity: ident,
        fingerprint,
        artifact_ref: token,
        mime: ext,
        bytes: bytes as i64,
        observed_at: identity.modified.saturating_mul(1000),
        status: parsed["status"].as_str().unwrap_or("unparsed").into(),
        reason: parsed["reason"].as_str().map(str::to_owned),
        segments,
        links: parsed["links"]
            .as_array()
            .map(|v| {
                v.iter()
                    .filter_map(|s| s.as_str().map(str::to_owned))
                    .collect()
            })
            .unwrap_or_default(),
    };
    published.validate()?;
    source_store::commit_batch(c, l, &[item], &format!("import:{}:{}", &id[..32], l.epoch))?;
    Ok(true)
}
pub fn progress(c: &Connection, l: &Lease) -> R<Value> {
    source_store::check(c, l)?;
    let discovered: i64 = c.query_row(
        "SELECT count(*) FROM import_jobs WHERE connector_id=?",
        [&l.connector],
        |r| r.get(0),
    )?;
    let mut q =
        c.prepare("SELECT state,count(*) FROM import_jobs WHERE connector_id=? GROUP BY state")?;
    let mut states = serde_json::Map::new();
    for row in q.query_map([&l.connector], |r| {
        Ok((r.get::<_, String>(0)?, r.get::<_, i64>(1)?))
    })? {
        let (k, n) = row?;
        states.insert(k, json!(n));
    }
    let remaining:i64=c.query_row("SELECT count(*) FROM scan_entries WHERE connector_id=?1 AND scan_epoch=?2 AND state='pending'",params![l.connector,l.epoch],|r|r.get(0))?;
    Ok(json!({"discovered":discovered,"states":states,"scanComplete":remaining==0}))
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn persisted_scan_import_resume_and_revoke() {
        let suffix = std::process::id();
        let fixture = format!("worker-{suffix}");
        let root = Path::new(ROOT).join("fixtures").join(&fixture);
        fs::create_dir(&root).unwrap();
        for n in 0..125 {
            fs::write(
                root.join(format!("{n}.md")),
                format!("synthetic note {n} [reference](https://synthetic.invalid/note)"),
            )
            .unwrap();
        }
        fs::create_dir(root.join(".obsidian")).unwrap();
        fs::write(
            root.join(".obsidian/config.json"),
            b"synthetic-secret-config",
        )
        .unwrap();
        fs::write(root.join("image.png"), b"opaque synthetic image").unwrap();
        let dbname = format!("worker-store-{suffix}");
        let mut c = repository::open(&dbname).unwrap();
        source_store::init(&c).unwrap();
        let lease = source_store::connect(&mut c, "connect", "connector", &fixture).unwrap();
        begin(&mut c, &lease).unwrap();
        assert!(scan_page(&mut c, &lease).unwrap());
        drop(c);
        let mut c = repository::open(&dbname).unwrap();
        let paused = source_store::control(&mut c, &lease, "pause", "pause").unwrap();
        assert!(import_one(&mut c, &lease).is_err());
        let resumed = source_store::control(&mut c, &paused, "resume", "resume").unwrap();
        while scan_page(&mut c, &resumed).unwrap() {}
        while import_one(&mut c, &resumed).unwrap() {}
        assert_eq!(progress(&c, &resumed).unwrap()["discovered"], 127);
        assert_eq!(progress(&c, &resumed).unwrap()["states"]["done"], 127);
        let parsed: i64 = c
            .query_row(
                "SELECT count(*) FROM source_files WHERE parse_state='parsed'",
                [],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(parsed, 125);
        let secrets: i64 = c
            .query_row(
                "SELECT count(*) FROM records WHERE body LIKE '%secret-config%'",
                [],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(secrets, 0);
        let links: i64 = c
            .query_row("SELECT count(*) FROM source_links", [], |r| r.get(0))
            .unwrap();
        assert_eq!(links, 125);
        let revoked = source_store::control(&mut c, &resumed, "disconnect", "disconnect").unwrap();
        drop(c);
        let mut c = repository::open(&dbname).unwrap();
        assert!(progress(&c, &revoked).is_err());
        let reconnect = source_store::connect(&mut c, "reconnect", "connector", &fixture).unwrap();
        assert!(source_store::search(&c, &reconnect, "synthetic")
            .unwrap()
            .is_empty());
    }
}

/// Recovery only within this task's synthetic owned artifact directory. No deletion.
pub fn recover(c: &Connection, l: &Lease) -> R<usize> {
    source_store::check(c, l)?;
    let dir = artifact_dir(c, l)?;
    let quarantine = dir.child("quarantine", true)?;
    let mut count = 0;
    for name in dir.entries()? {
        if name == "quarantine" {
            continue;
        }
        // Open/type/identity check on the anchored FD, never read_dir(entry.path()).
        let file = dir.open(&name)?;
        let referenced: bool = c.query_row(
            "SELECT EXISTS(SELECT 1 FROM source_artifacts WHERE opaque_ref=?)",
            [&name],
            |r| r.get(0),
        )?;
        if referenced {
            continue;
        }
        file.validate()?;
        let destination = format!(
            "{}-{}",
            name,
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        );
        dir.quarantine(&name, &quarantine, &destination)?;
        count += 1;
    }
    c.execute(
        "UPDATE import_jobs SET state='pending' WHERE connector_id=? AND state='pending_recovery'",
        [&l.connector],
    )?;
    Ok(count)
}
#[cfg(test)]
mod recovery_tests {
    use super::*;
    #[test]
    fn publish_receipt_failure_quarantine_retry() {
        let suffix = std::process::id();
        let fixture = format!("recovery-{suffix}");
        let root = Path::new(ROOT).join("fixtures").join(&fixture);
        fs::create_dir(&root).unwrap();
        fs::write(root.join("note.md"), b"synthetic recovery body").unwrap();
        let mut c = repository::open(&format!("recovery-{suffix}")).unwrap();
        source_store::init(&c).unwrap();
        let l = source_store::connect(&mut c, "c", "connector", &fixture).unwrap();
        begin(&mut c, &l).unwrap();
        while scan_page(&mut c, &l).unwrap() {}
        c.execute_batch("CREATE TRIGGER fail_source_receipt BEFORE INSERT ON connector_requests WHEN NEW.id LIKE 'import:%' BEGIN SELECT RAISE(ABORT,'synthetic disk fault'); END;").unwrap();
        assert!(import_one(&mut c, &l).is_err());
        assert_eq!(
            c.query_row("SELECT count(*) FROM source_files", [], |r| r
                .get::<_, i64>(0))
                .unwrap(),
            0
        );
        assert!(recover(&c, &l).unwrap() >= 2); // Original/staging; parser output lives in .runtime.
        c.execute_batch("DROP TRIGGER fail_source_receipt").unwrap();
        assert!(import_one(&mut c, &l).unwrap());
        assert_eq!(source_store::search(&c, &l, "recovery").unwrap().len(), 1);
        let retained: i64 = c
            .query_row("SELECT count(*) FROM source_artifacts", [], |r| r.get(0))
            .unwrap();
        assert_eq!(retained, 1);
        recover(&c, &l).unwrap();
        assert_eq!(
            c.query_row("SELECT count(*) FROM source_artifacts", [], |r| r
                .get::<_, i64>(0))
                .unwrap(),
            1
        );
    }
}
pub fn finalize_scan(c: &mut Connection, l: &Lease) -> R<()> {
    let _grant = granted(c, l)?;
    let pending:i64=c.query_row("SELECT count(*) FROM scan_entries WHERE connector_id=?1 AND scan_epoch=?2 AND state='pending'",params![l.connector,l.epoch],|r|r.get(0))?;
    if pending != 0 {
        return Err(err("scan_incomplete"));
    }
    let mut q=c.prepare("SELECT id FROM source_files WHERE connector_id=?1 AND id NOT IN(SELECT id FROM import_jobs WHERE connector_id=?1 AND epoch=?2)")?;
    let ids = q
        .query_map(params![l.connector, l.epoch], |r| r.get::<_, String>(0))?
        .collect::<Result<Vec<_>, _>>()?;
    drop(q);
    for id in ids {
        source_store::missing(c, l, &id)?;
    }
    Ok(())
}
/// Join direct in-grant references to already imported originals; no recursive IO.
pub fn resolve_local_links(c: &Connection, l: &Lease) -> R<usize> {
    source_store::check(c, l)?;
    let mut q=c.prepare("SELECT link.id,link.target_ref,parent.external_ref FROM source_links link JOIN source_files parent ON parent.id=link.parent_file WHERE parent.connector_id=?1 AND parent.version=link.parent_version AND link.state='awaiting_target_grant'")?;
    let links = q
        .query_map([&l.connector], |r| {
            Ok((
                r.get::<_, String>(0)?,
                r.get::<_, String>(1)?,
                r.get::<_, String>(2)?,
            ))
        })?
        .collect::<Result<Vec<_>, _>>()?;
    drop(q);
    let mut linked = 0;
    for (id, target, parent) in links {
        if target.contains(':') || target.starts_with('/') || target.contains('\\') {
            continue;
        }
        let target = target.split('#').next().unwrap_or("");
        if target.is_empty() {
            continue;
        }
        let mut components = parent.split('/').map(str::to_owned).collect::<Vec<_>>();
        components.pop();
        let mut outside = false;
        for p in target.split('/') {
            match p {
                "" | "." => (),
                ".." => {
                    if components.pop().is_none() {
                        outside = true;
                        break;
                    }
                }
                _ => components.push(p.into()),
            }
        }
        if outside {
            continue;
        }
        let candidate = components.join("/");
        let matched:Option<(String,i64)>=c.query_row("SELECT id,version FROM source_files WHERE connector_id=?1 AND external_ref IN (?2,?3) AND parse_state IN('parsed','restricted','unparsed') ORDER BY external_ref LIMIT 1",params![l.connector,candidate,format!("{candidate}.md")],|r|Ok((r.get(0)?,r.get(1)?))).optional()?;
        if let Some((file, version)) = matched {
            source_store::check(c, l)?;
            c.execute("UPDATE source_links SET state='local_original_linked',final_ref=?2,target_version=?3 WHERE id=?1",params![id,file,version])?;
            linked += 1;
        }
    }
    Ok(linked)
}
#[cfg(test)]
mod lifecycle_tests {
    use super::*;
    #[test]
    fn refresh_missing_version_root_swap_and_local_link() {
        let run = std::process::id();
        let fixture = format!("lifecycle-{run}");
        let path = Path::new(ROOT).join("fixtures").join(&fixture);
        fs::create_dir(&path).unwrap();
        fs::write(path.join("parent.md"), b"synthetic parent [[child]]").unwrap();
        fs::write(path.join("child.md"), b"synthetic child v1").unwrap();
        let mut c = repository::open(&format!("life-{run}")).unwrap();
        source_store::init(&c).unwrap();
        let l = source_store::connect(&mut c, "c", "connector", &fixture).unwrap();
        begin(&mut c, &l).unwrap();
        while scan_page(&mut c, &l).unwrap() {}
        while import_one(&mut c, &l).unwrap() {}
        assert_eq!(resolve_local_links(&c, &l).unwrap(), 1);
        fs::write(path.join("child.md"), b"synthetic child version two").unwrap();
        let l = source_store::control(&mut c, &l, "refresh1", "refresh").unwrap();
        begin(&mut c, &l).unwrap();
        while scan_page(&mut c, &l).unwrap() {}
        while import_one(&mut c, &l).unwrap() {}
        finalize_scan(&mut c, &l).unwrap();
        assert_eq!(source_store::search(&c, &l, "two").unwrap().len(), 1);
        fs::remove_file(path.join("child.md")).unwrap();
        let l = source_store::control(&mut c, &l, "refresh2", "refresh").unwrap();
        begin(&mut c, &l).unwrap();
        while scan_page(&mut c, &l).unwrap() {}
        while import_one(&mut c, &l).unwrap() {}
        finalize_scan(&mut c, &l).unwrap();
        assert!(source_store::search(&c, &l, "two").unwrap().is_empty());
        // Root inode replacement remains in synthetic fixtures, but is not the granted directory.
        fs::rename(&path, path.with_file_name(format!("{fixture}-moved"))).unwrap();
        fs::create_dir(&path).unwrap();
        assert!(granted(&c, &l).is_err());
    }
}

#[cfg(test)]
mod scan_change_tests {
    use super::*;
    #[test]
    fn changed_directory_stops_before_missing_or_partial_success() {
        let fixture = format!("scan-change-{}", std::process::id());
        let root = Path::new(ROOT).join("fixtures").join(&fixture);
        fs::create_dir(&root).unwrap();
        for n in 0..300 {
            fs::write(root.join(format!("{n}.txt")), b"synthetic").unwrap();
        }
        let mut c = repository::open(&fixture).unwrap();
        source_store::init(&c).unwrap();
        let l = source_store::connect(&mut c, "connect", "connector", &fixture).unwrap();
        begin(&mut c, &l).unwrap();
        assert!(scan_page(&mut c, &l).unwrap());
        fs::remove_file(root.join("0.txt")).unwrap();
        fs::write(root.join("new.txt"), b"synthetic replacement").unwrap();
        assert_eq!(
            scan_page(&mut c, &l).unwrap_err().code,
            "directory_changed_refresh_required"
        );
        assert!(!progress(&c, &l).unwrap()["scanComplete"].as_bool().unwrap());
        let next = source_store::control(&mut c, &l, "refresh", "refresh").unwrap();
        begin(&mut c, &next).unwrap();
        while scan_page(&mut c, &next).unwrap() {}
        let count: i64 = c
            .query_row(
                "SELECT count(*) FROM import_jobs WHERE epoch=?",
                [next.epoch],
                |r| r.get(0),
            )
            .unwrap();
        assert_eq!(count, 300);
    }
    #[test]
    fn bookmark_aliases_and_directory_symlink_cycles_are_bounded() {
        let fixture = format!("alias-{}", std::process::id());
        let root = Path::new(ROOT).join("fixtures").join(&fixture);
        fs::create_dir(&root).unwrap();
        fs::create_dir(root.join("folder")).unwrap();
        fs::write(root.join("target.txt"), b"synthetic alias text").unwrap();
        fs::write(root.join("folder/note.txt"), b"synthetic directory note").unwrap();
        assert!(Command::new(Path::new(ROOT).join("create_test_alias"))
            .arg(&fixture)
            .status()
            .unwrap()
            .success());
        std::os::unix::fs::symlink("..", root.join("folder/loop")).unwrap();
        let g = FileGrant::synthetic(&root).unwrap();
        assert_eq!(g.resolve_ref("file.alias").unwrap(), "target.txt");
        assert_eq!(g.resolve_ref("dir.alias").unwrap(), "folder");
        let mut c = repository::open(&fixture).unwrap();
        source_store::init(&c).unwrap();
        let l = source_store::connect(&mut c, "connect", "connector", &fixture).unwrap();
        begin(&mut c, &l).unwrap();
        let mut pages = 0;
        while scan_page(&mut c, &l).unwrap() {
            pages += 1;
            assert!(pages <= 3)
        }
        assert_eq!(pages, 2);
        while import_one(&mut c, &l).unwrap() {}
        assert!(!source_store::search(&c, &l, "alias text")
            .unwrap()
            .is_empty());
    }
}
