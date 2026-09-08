//! File capability: anchored directory descriptors, never UI paths.
use crate::repository::Error;
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use std::{
    ffi::{CStr, CString},
    fs::{File, OpenOptions},
    io::{Read, Write},
    os::{
        fd::{AsRawFd, FromRawFd},
        unix::fs::{MetadataExt, OpenOptionsExt},
    },
    path::Path,
    time::{Duration, Instant},
};
type R<T> = Result<T, Error>;
fn err(s: &str) -> Error {
    Error::new(s)
}
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq)]
pub struct Identity {
    pub dev: u64,
    pub ino: u64,
    pub size: u64,
    pub modified: i64,
    pub nanos: i64,
    pub changed: i64,
    pub changed_nanos: i64,
}
fn identity(f: &File) -> R<Identity> {
    let m = f.metadata().map_err(|_| err("file_unavailable"))?;
    Ok(Identity {
        dev: m.dev(),
        ino: m.ino(),
        size: m.len(),
        modified: m.mtime(),
        nanos: m.mtime_nsec(),
        changed: m.ctime(),
        changed_nanos: m.ctime_nsec(),
    })
}
pub struct FileGrant {
    root: File,
    root_path: std::path::PathBuf,
}
#[derive(Debug, Serialize, Deserialize)]
pub struct Entry {
    pub name: String,
    pub kind: String,
    pub identity: Option<Identity>,
}
impl FileGrant {
    pub fn synthetic(root: &Path) -> R<Self> {
        let verified = crate::runtime_root::verify()?;
        let allowed_path = verified.join("fixtures");
        let allowed = allowed_path.as_path();
        if !root.starts_with(allowed)
            || root
                .components()
                .any(|c| matches!(c, std::path::Component::ParentDir))
        {
            return Err(err("grant_rejected"));
        }
        let mut f = OpenOptions::new()
            .read(true)
            .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open(allowed)
            .map_err(|_| err("grant_unavailable"))?;
        for c in root.strip_prefix(allowed).unwrap().components() {
            f = openat(
                &f,
                c.as_os_str()
                    .to_str()
                    .ok_or_else(|| err("encoding_rejected"))?,
                true,
            )?;
        }
        Ok(Self {
            root: f,
            root_path: root.to_path_buf(),
        })
    }
    pub fn root_identity(&self) -> R<Identity> {
        identity(&self.root)
    }
    pub fn resolve_ref(&self, reference: &str) -> R<String> {
        let mut components = normalize(reference)?;
        let mut seen = std::collections::HashSet::new();
        for _ in 0..40 {
            if !seen.insert(components.join("/")) {
                return Err(err("link_cycle"));
            }
            let mut current = self.root.try_clone().map_err(|_| err("file_unavailable"))?;
            let mut restart = false;
            for i in 0..components.len() {
                match openat(&current, &components[i], i + 1 != components.len()) {
                    Ok(f) => current = f,
                    Err(original) => {
                        let n = CString::new(components[i].as_bytes())
                            .map_err(|_| err("reference_rejected"))?;
                        let mut bytes = [0u8; 4096];
                        let count = unsafe {
                            libc::readlinkat(
                                current.as_raw_fd(),
                                n.as_ptr(),
                                bytes.as_mut_ptr() as *mut libc::c_char,
                                bytes.len(),
                            )
                        };
                        if count < 0 {
                            return Err(original);
                        }
                        if count as usize >= bytes.len() {
                            return Err(err("link_target_too_long"));
                        }
                        let target = std::str::from_utf8(&bytes[..count as usize])
                            .map_err(|_| err("encoding_rejected"))?;
                        if target.starts_with('/') || target.contains('\\') {
                            return Err(err("outside_target_grant_required"));
                        }
                        let mut next = components[..i].to_vec();
                        for part in target.split('/') {
                            match part {
                                "" | "." => (),
                                ".." => {
                                    if next.pop().is_none() {
                                        return Err(err("outside_target_grant_required"));
                                    }
                                }
                                _ => next.push(part.into()),
                            }
                        }
                        next.extend_from_slice(&components[i + 1..]);
                        components = next;
                        restart = true;
                        break;
                    }
                }
            }
            if !restart
                && components
                    .last()
                    .is_some_and(|s| s.to_lowercase().ends_with(".alias"))
            {
                if current
                    .metadata()
                    .map_err(|_| err("alias_unavailable"))?
                    .len()
                    > 1024 * 1024
                {
                    return Err(err("alias_metadata_budget"));
                }
                let output = std::process::Command::new(
                    crate::runtime_root::verify()?.join("alias_metadata"),
                )
                .stdin(std::process::Stdio::from(current))
                .stderr(std::process::Stdio::null())
                .output()
                .map_err(|_| err("alias_parser_unavailable"))?;
                if !output.status.success() {
                    return Err(err("alias_metadata_unavailable"));
                }
                let raw = std::str::from_utf8(&output.stdout)
                    .map_err(|_| err("alias_metadata_unavailable"))?;
                let relative = Path::new(raw)
                    .strip_prefix(&self.root_path)
                    .map_err(|_| err("outside_target_grant_required"))?;
                components = normalize(
                    relative
                        .to_str()
                        .ok_or_else(|| err("alias_metadata_unavailable"))?,
                )?;
                restart = true;
            }
            if !restart {
                return Ok(components.join("/"));
            }
        }
        Err(err("link_cycle"))
    }
    pub fn file(&self, reference: &str) -> R<File> {
        let resolved = self.resolve_ref(reference)?;
        let components = normalize(&resolved)?;
        if components.is_empty() {
            return Err(err("reference_rejected"));
        }
        let mut current = self.root.try_clone().map_err(|_| err("file_unavailable"))?;
        for (i, c) in components.iter().enumerate() {
            current = openat(&current, c, i + 1 != components.len())?;
        }
        if !current
            .metadata()
            .map_err(|_| err("file_unavailable"))?
            .is_file()
        {
            return Err(err("special_file_rejected"));
        }
        Ok(current)
    }
    pub fn directory_identity(&self, reference: &str) -> R<Identity> {
        let resolved = self.resolve_ref(reference)?;
        let mut dir = self
            .root
            .try_clone()
            .map_err(|_| err("directory_unavailable"))?;
        for part in normalize(&resolved)? {
            dir = openat(&dir, &part, true)?;
        }
        identity(&dir)
    }
    pub fn page(&self, reference: &str, offset: u64) -> R<(Vec<Entry>, u64, bool)> {
        let mut dir = self
            .root
            .try_clone()
            .map_err(|_| err("directory_unavailable"))?;
        for c in normalize(reference)? {
            dir = openat(&dir, &c, true)?;
        }
        // Open a separate file description so enumeration never advances the grant handle.
        let fresh = openat(&dir, ".", true)?;
        let fd = unsafe { libc::dup(fresh.as_raw_fd()) };
        if fd < 0 {
            return Err(err("directory_unavailable"));
        }
        let stream = unsafe { libc::fdopendir(fd) };
        if stream.is_null() {
            unsafe { libc::close(fd) };
            return Err(err("directory_unavailable"));
        }
        let mut out = Vec::new();
        let mut seen = 0;
        let mut eof = false;
        loop {
            let p = unsafe { libc::readdir(stream) };
            if p.is_null() {
                eof = true;
                break;
            }
            let name = unsafe { CStr::from_ptr((*p).d_name.as_ptr()) }
                .to_string_lossy()
                .to_string();
            if name == "." || name == ".." {
                continue;
            }
            if seen < offset {
                seen += 1;
                continue;
            }
            if out.len() == 256 {
                break;
            }
            seen += 1;
            let c = CString::new(name.as_bytes()).map_err(|_| err("reference_rejected"))?;
            let mut st: libc::stat = unsafe { std::mem::zeroed() };
            let rc = unsafe {
                libc::fstatat(
                    dir.as_raw_fd(),
                    c.as_ptr(),
                    &mut st,
                    libc::AT_SYMLINK_NOFOLLOW,
                )
            };
            let kind = if rc != 0 {
                "unavailable"
            } else {
                match st.st_mode as u32 & libc::S_IFMT as u32 {
                    x if x == libc::S_IFREG as u32 => "file",
                    x if x == libc::S_IFDIR as u32 => "directory",
                    x if x == libc::S_IFLNK as u32 => "link",
                    _ => "special",
                }
            };
            out.push(Entry {
                name,
                kind: kind.into(),
                identity: None,
            });
        }
        unsafe { libc::closedir(stream) };
        Ok((out, seen, eof))
    }
    pub fn identity(&self, reference: &str) -> R<Identity> {
        identity(&self.file(reference)?)
    }
    pub fn copy(
        &self,
        reference: &str,
        expected: &Identity,
        destination: &Path,
    ) -> R<(String, u64)> {
        let mut f = self.file(reference)?;
        if identity(&f)? != *expected {
            return Err(err("source_changed"));
        }
        let mut out = OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o600)
            .custom_flags(libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open(destination)
            .map_err(|_| err("artifact_unavailable"))?;
        let start = Instant::now();
        let mut digest = Sha256::new();
        let mut bytes = 0;
        let mut buf = [0u8; 65536];
        loop {
            let n = f.read(&mut buf).map_err(|_| err("source_read_failed"))?;
            if n == 0 {
                break;
            }
            out.write_all(&buf[..n])
                .map_err(|_| err("artifact_write_failed"))?;
            digest.update(&buf[..n]);
            bytes += n as u64;
            if start.elapsed() > Duration::from_secs(30) {
                return Err(err("read_timeout"));
            }
        }
        if identity(&f)? != *expected || self.identity(reference)? != *expected {
            return Err(err("source_changed"));
        }
        out.sync_all().map_err(|_| err("artifact_sync_failed"))?;
        Ok((format!("{:x}", digest.finalize()), bytes))
    }
}
fn openat(dir: &File, name: &str, directory: bool) -> R<File> {
    let n = CString::new(name).map_err(|_| err("reference_rejected"))?;
    let mut metadata: libc::stat = unsafe { std::mem::zeroed() };
    if unsafe {
        libc::fstatat(
            dir.as_raw_fd(),
            n.as_ptr(),
            &mut metadata,
            libc::AT_SYMLINK_NOFOLLOW,
        )
    } != 0
    {
        return Err(err("source_unavailable_or_link_requires_grant"));
    }
    let kind = metadata.st_mode as u32 & libc::S_IFMT as u32;
    if ![
        libc::S_IFREG as u32,
        libc::S_IFDIR as u32,
        libc::S_IFLNK as u32,
    ]
    .contains(&kind)
    {
        return Err(err("special_file_rejected"));
    }
    let flags = libc::O_RDONLY
        | libc::O_NOFOLLOW
        | libc::O_CLOEXEC
        | libc::O_NONBLOCK
        | if directory { libc::O_DIRECTORY } else { 0 };
    let fd = unsafe { libc::openat(dir.as_raw_fd(), n.as_ptr(), flags) };
    if fd < 0 {
        return Err(err("source_unavailable_or_link_requires_grant"));
    }
    Ok(unsafe { File::from_raw_fd(fd) })
}
fn normalize(s: &str) -> R<Vec<String>> {
    if s.starts_with('/') || s.contains('\0') || s.contains('\\') {
        return Err(err("reference_rejected"));
    }
    let mut out = vec![];
    for c in s.split('/') {
        match c {
            "" | "." => (),
            ".." => return Err(err("outside_grant")),
            _ => out.push(c.into()),
        }
    }
    Ok(out)
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn anchored_read_pages_special_links_and_changed() {
        let base = Path::new(crate::runtime_root::ROOT).join("fixtures");
        let p = base.join(format!("fd-test-{}", std::process::id()));
        std::fs::create_dir(&p).unwrap();
        for n in 0..530 {
            std::fs::write(p.join(format!("note-{n}.txt")), b"synthetic").unwrap();
        }
        let grant = FileGrant::synthetic(&p).unwrap();
        let (a, c, e) = grant.page("", 0).unwrap();
        assert_eq!(a.len(), 256);
        assert!(!e);
        let (b, c, e) = grant.page("", c).unwrap();
        assert_eq!(b.len(), 256);
        assert!(!e);
        let (d, _, e) = grant.page("", c).unwrap();
        assert_eq!(d.len(), 18);
        assert!(e);
        assert!(grant.file("../outside").is_err());
        assert!(grant.file("/absolute").is_err());
        std::os::unix::fs::symlink("note-0.txt", p.join("link")).unwrap();
        assert_eq!(grant.resolve_ref("link").unwrap(), "note-0.txt");
        assert!(grant.file("link").is_ok());
        std::os::unix::fs::symlink("../not-authorized", p.join("escape-link")).unwrap();
        assert!(grant.file("escape-link").is_err());
        std::os::unix::fs::symlink("loop", p.join("loop")).unwrap();
        assert!(grant.file("loop").is_err());
        let fifo = CString::new(p.join("fifo").to_str().unwrap()).unwrap();
        assert_eq!(unsafe { libc::mkfifo(fifo.as_ptr(), 0o600) }, 0);
        assert!(grant.file("fifo").is_err());
        let old = grant.identity("note-0.txt").unwrap();
        std::fs::write(p.join("note-0.txt"), b"changed synthetic").unwrap();
        assert!(grant
            .copy("note-0.txt", &old, &p.join("copy-rejected"))
            .is_err());
        assert!(!p.join("copy-rejected").exists());
        let now = grant.identity("note-0.txt").unwrap();
        let copy = p.join("copy");
        assert_eq!(grant.copy("note-0.txt", &now, &copy).unwrap().1, 17);
        assert_eq!(std::fs::read(&copy).unwrap(), b"changed synthetic");
        assert!(grant.copy("note-0.txt", &now, &copy).is_err());
    }
}
#[cfg(test)]
mod scale_tests {
    use super::*;
    #[test]
    fn beyond_old_count_depth_and_size_limits() {
        let root = Path::new(crate::runtime_root::ROOT)
            .join("fixtures")
            .join(format!("scale-{}", std::process::id()));
        std::fs::create_dir(&root).unwrap();
        for n in 0..5201 {
            std::fs::write(root.join(format!("n{n}")), b"s").unwrap()
        }
        let grant = FileGrant::synthetic(&root).unwrap();
        let mut offset = 0;
        let mut total = 0;
        loop {
            let (v, next, eof) = grant.page("", offset).unwrap();
            assert!(v.len() <= 256);
            total += v.len();
            offset = next;
            if eof {
                break;
            }
        }
        assert_eq!(total, 5201);
        let mut current = root.clone();
        let mut reference = vec![];
        for _ in 0..24 {
            current = current.join("deep");
            reference.push("deep");
            std::fs::create_dir(&current).unwrap();
        }
        let content = vec![b'a'; 300 * 1024];
        std::fs::write(current.join("large.txt"), &content).unwrap();
        reference.push("large.txt");
        let r = reference.join("/");
        let expected = grant.identity(&r).unwrap();
        assert_eq!(
            grant
                .copy(&r, &expected, &root.join("large-copy"))
                .unwrap()
                .1,
            300 * 1024
        );
        assert_eq!(std::fs::read(root.join("large-copy")).unwrap(), content);
    }
}
