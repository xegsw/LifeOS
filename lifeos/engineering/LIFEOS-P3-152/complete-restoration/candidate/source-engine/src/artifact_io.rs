//! Writes and publication stay on owned directory/file descriptors, never reopened paths.
use crate::{repository::Error, runtime_root};
use std::{
    ffi::{CStr, CString},
    fs::{File, OpenOptions},
    io::{Read, Seek, SeekFrom, Write},
    os::{
        fd::{AsRawFd, FromRawFd},
        unix::fs::{MetadataExt, OpenOptionsExt},
    },
    sync::Arc,
};
type R<T> = Result<T, Error>;
fn err() -> Error {
    Error::new("artifact_boundary_rejected")
}
fn name(s: &str) -> R<CString> {
    if s.is_empty() || s == "." || s == ".." || s.contains('/') || s.contains('\\') {
        return Err(err());
    }
    CString::new(s).map_err(|_| err())
}
fn regular(f: &File) -> R<()> {
    let m = f.metadata().map_err(|_| err())?;
    if !m.is_file() || m.uid() != unsafe { libc::getuid() } || m.mode() & 0o777 != 0o600 {
        return Err(err());
    }
    Ok(())
}
#[derive(Clone)]
struct Node {
    fd: Arc<File>,
    name: String,
    strict: bool,
}
#[derive(Clone)]
pub struct Dir {
    chain: Vec<Node>,
}
impl Dir {
    // Absolute component walk for the fixed source and user-click-owned output bootstrap.
    // No canonicalization through links and no chmod of pre-existing objects.
    pub fn absolute(path: &std::path::Path, create_leaf: bool, strict_leaf: bool) -> R<Self> {
        let fd = OpenOptions::new()
            .read(true)
            .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open("/")
            .map_err(|_| err())?;
        let mut d = Self {
            chain: vec![Node {
                fd: Arc::new(fd),
                name: String::new(),
                strict: false,
            }],
        };
        let parts: Vec<_> = path.components().collect();
        if parts.first() != Some(&std::path::Component::RootDir) {
            return Err(err());
        }
        for (i, part) in parts.iter().enumerate().skip(1) {
            let std::path::Component::Normal(n) = part else {
                return Err(err());
            };
            d = d.open_child(
                n.to_str().ok_or_else(err)?,
                create_leaf && i + 1 == parts.len(),
                strict_leaf && i + 1 == parts.len(),
            )?;
        }
        Ok(d)
    }
    fn fd(&self) -> &File {
        &self.chain.last().unwrap().fd
    }
    pub fn root() -> R<Self> {
        runtime_root::verify()?;
        let fd = OpenOptions::new()
            .read(true)
            .custom_flags(libc::O_DIRECTORY | libc::O_NOFOLLOW | libc::O_CLOEXEC)
            .open("/")
            .map_err(|_| err())?;
        let mut d = Self {
            chain: vec![Node {
                fd: Arc::new(fd),
                name: String::new(),
                strict: false,
            }],
        };
        let parts: Vec<_> = runtime_root::ROOT
            .trim_start_matches('/')
            .split('/')
            .collect();
        for (i, p) in parts.iter().enumerate() {
            d = d.open_child(p, false, i + 1 == parts.len())?;
        }
        let mut marker = d.open(".owner.json")?;
        let bytes = marker.read_limit(4096)?;
        if serde_json::from_slice::<serde_json::Value>(&bytes).map_err(|_| err())?
            != runtime_root::expected_marker()?
        {
            return Err(err());
        }
        d.validate()?;
        Ok(d)
    }
    pub fn validate(&self) -> R<()> {
        for (i, n) in self.chain.iter().enumerate() {
            let m = n.fd.metadata().map_err(|_| err())?;
            if !m.is_dir()
                || (n.strict && (m.uid() != unsafe { libc::getuid() } || m.mode() & 0o777 != 0o700))
            {
                return Err(err());
            }
            if i > 0 {
                let mut st: libc::stat = unsafe { std::mem::zeroed() };
                let n = name(&n.name)?;
                if unsafe {
                    libc::fstatat(
                        self.chain[i - 1].fd.as_raw_fd(),
                        n.as_ptr(),
                        &mut st,
                        libc::AT_SYMLINK_NOFOLLOW,
                    )
                } != 0
                    || st.st_dev as u64 != m.dev()
                    || st.st_ino != m.ino()
                    || st.st_mode as u32 & libc::S_IFMT as u32 != libc::S_IFDIR as u32
                {
                    return Err(err());
                }
            }
        }
        Ok(())
    }
    fn open_child(&self, s: &str, create: bool, strict: bool) -> R<Self> {
        self.validate()?;
        let n = name(s)?;
        if create
            && unsafe { libc::mkdirat(self.fd().as_raw_fd(), n.as_ptr(), 0o700) } != 0
            && std::io::Error::last_os_error().kind() != std::io::ErrorKind::AlreadyExists
        {
            return Err(err());
        }
        let fd = unsafe {
            libc::openat(
                self.fd().as_raw_fd(),
                n.as_ptr(),
                libc::O_RDONLY
                    | libc::O_DIRECTORY
                    | libc::O_NOFOLLOW
                    | libc::O_CLOEXEC
                    | libc::O_NONBLOCK,
            )
        };
        if fd < 0 {
            return Err(err());
        }
        let mut d = self.clone();
        d.chain.push(Node {
            fd: Arc::new(unsafe { File::from_raw_fd(fd) }),
            name: s.into(),
            strict,
        });
        d.validate()?;
        Ok(d)
    }
    pub fn child(&self, s: &str, create: bool) -> R<Self> {
        self.open_child(s, create, true)
    }
    pub fn new_child(&self, s: &str) -> R<Self> {
        self.validate()?;
        let n = name(s)?;
        if unsafe { libc::mkdirat(self.fd().as_raw_fd(), n.as_ptr(), 0o700) } != 0 {
            return Err(err());
        }
        self.open_child(s, false, true)
    }
    pub fn create(&self, s: &str) -> R<OwnedFile> {
        self.create_after_check(s, || {})
    }
    fn create_after_check(&self, s: &str, hook: impl FnOnce()) -> R<OwnedFile> {
        self.validate()?;
        let n = name(s)?;
        hook();
        let fd = unsafe {
            libc::openat(
                self.fd().as_raw_fd(),
                n.as_ptr(),
                libc::O_RDWR
                    | libc::O_CREAT
                    | libc::O_EXCL
                    | libc::O_NOFOLLOW
                    | libc::O_CLOEXEC
                    | libc::O_NONBLOCK,
                0o600,
            )
        };
        if fd < 0 {
            return Err(err());
        }
        let f = OwnedFile {
            dir: self.clone(),
            name: s.into(),
            fd: unsafe { File::from_raw_fd(fd) },
        };
        f.validate()?;
        Ok(f)
    }
    pub fn open(&self, s: &str) -> R<OwnedFile> {
        self.validate()?;
        let n = name(s)?;
        let fd = unsafe {
            libc::openat(
                self.fd().as_raw_fd(),
                n.as_ptr(),
                libc::O_RDONLY | libc::O_NOFOLLOW | libc::O_CLOEXEC | libc::O_NONBLOCK,
            )
        };
        if fd < 0 {
            return Err(err());
        }
        let f = OwnedFile {
            dir: self.clone(),
            name: s.into(),
            fd: unsafe { File::from_raw_fd(fd) },
        };
        f.validate()?;
        Ok(f)
    }
    pub fn exists(&self, s: &str) -> R<bool> {
        self.validate()?;
        let n = name(s)?;
        let mut st = unsafe { std::mem::zeroed() };
        if unsafe {
            libc::fstatat(
                self.fd().as_raw_fd(),
                n.as_ptr(),
                &mut st,
                libc::AT_SYMLINK_NOFOLLOW,
            )
        } == 0
        {
            return Ok(true);
        }
        if std::io::Error::last_os_error().kind() == std::io::ErrorKind::NotFound {
            Ok(false)
        } else {
            Err(err())
        }
    }
    pub fn entries(&self) -> R<Vec<String>> {
        self.validate()?;
        let dot = CString::new(".").unwrap();
        let fd = unsafe {
            libc::openat(
                self.fd().as_raw_fd(),
                dot.as_ptr(),
                libc::O_RDONLY | libc::O_DIRECTORY | libc::O_CLOEXEC,
            )
        };
        if fd < 0 {
            return Err(err());
        }
        let dir = unsafe { libc::fdopendir(fd) };
        if dir.is_null() {
            unsafe { libc::close(fd) };
            return Err(err());
        }
        let mut names = vec![];
        loop {
            let entry = unsafe { libc::readdir(dir) };
            if entry.is_null() {
                break;
            }
            let s = unsafe { CStr::from_ptr((*entry).d_name.as_ptr()) }
                .to_str()
                .map(str::to_owned);
            match s {
                Ok(s) if s != "." && s != ".." => names.push(s),
                Ok(_) => (),
                Err(_) => {
                    unsafe { libc::closedir(dir) };
                    return Err(err());
                }
            }
        }
        unsafe { libc::closedir(dir) };
        self.validate()?;
        Ok(names)
    }
    pub fn quarantine(&self, s: &str, dest: &Dir, new_name: &str) -> R<()> {
        let original = self.open(s)?;
        dest.validate()?;
        let src = name(s)?;
        let dst = name(new_name)?;
        // Atomic no-overwrite rename relative to the two held FDs. Never follows a source link.
        if unsafe {
            libc::renameatx_np(
                self.fd().as_raw_fd(),
                src.as_ptr(),
                dest.fd().as_raw_fd(),
                dst.as_ptr(),
                4,
            )
        } != 0
        {
            return Err(err());
        }
        let moved = dest.open(new_name)?;
        let a = original.fd.metadata().map_err(|_| err())?;
        let b = moved.fd.metadata().map_err(|_| err())?;
        if (a.dev(), a.ino()) != (b.dev(), b.ino()) {
            return Err(err());
        }
        self.validate()?;
        dest.sync()?;
        self.sync()
    }
    pub fn descriptor(&self) -> R<File> {
        self.validate()?;
        self.fd().try_clone().map_err(|_| err())
    }
    pub fn sync(&self) -> R<()> {
        self.validate()?;
        self.fd().sync_all().map_err(|_| err())?;
        self.validate()
    }
}
pub struct OwnedFile {
    dir: Dir,
    name: String,
    fd: File,
}
impl OwnedFile {
    pub fn validate(&self) -> R<()> {
        self.dir.validate()?;
        regular(&self.fd)?;
        let n = name(&self.name)?;
        let mut st: libc::stat = unsafe { std::mem::zeroed() };
        let m = self.fd.metadata().map_err(|_| err())?;
        if unsafe {
            libc::fstatat(
                self.dir.fd().as_raw_fd(),
                n.as_ptr(),
                &mut st,
                libc::AT_SYMLINK_NOFOLLOW,
            )
        } != 0
            || st.st_dev as u64 != m.dev()
            || st.st_ino != m.ino()
            || st.st_mode as u32 & libc::S_IFMT as u32 != libc::S_IFREG as u32
        {
            return Err(err());
        }
        Ok(())
    }
    pub fn write_all(&mut self, bytes: &[u8]) -> R<()> {
        self.write_after_check(bytes, || {})
    }
    fn write_after_check(&mut self, bytes: &[u8], hook: impl FnOnce()) -> R<()> {
        self.validate()?;
        hook();
        self.fd.write_all(bytes).map_err(|_| err())?;
        self.validate()
    }
    pub fn sync(&self) -> R<()> {
        self.validate()?;
        self.fd.sync_all().map_err(|_| err())?;
        self.validate()
    }
    pub fn len(&self) -> R<u64> {
        self.validate()?;
        Ok(self.fd.metadata().map_err(|_| err())?.len())
    }
    pub fn descriptor(&mut self) -> R<File> {
        self.validate()?;
        self.fd.seek(SeekFrom::Start(0)).map_err(|_| err())?;
        self.fd.try_clone().map_err(|_| err())
    }
    pub fn read_limit(&mut self, limit: u64) -> R<Vec<u8>> {
        self.validate()?;
        self.fd.seek(SeekFrom::Start(0)).map_err(|_| err())?;
        let mut bytes = vec![];
        std::io::Read::by_ref(&mut self.fd)
            .take(limit + 1)
            .read_to_end(&mut bytes)
            .map_err(|_| err())?;
        self.validate()?;
        if bytes.len() as u64 > limit {
            return Err(Error::new("parse_memory_budget"));
        }
        Ok(bytes)
    }
    pub fn publish(&mut self, dest: &Dir, token: &str) -> R<OwnedFile> {
        self.validate()?;
        let mut out = dest.create(token)?;
        self.fd.seek(SeekFrom::Start(0)).map_err(|_| err())?;
        let mut buf = [0u8; 65536];
        loop {
            self.validate()?;
            let n = self.fd.read(&mut buf).map_err(|_| err())?;
            if n == 0 {
                break;
            }
            out.write_all(&buf[..n])?;
        }
        self.validate()?;
        out.sync()?;
        dest.sync()?;
        Ok(out)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::{
        fs,
        os::unix::fs::{symlink, PermissionsExt},
        path::PathBuf,
    };
    fn setup(label: &str) -> (PathBuf, Dir, PathBuf) {
        let n = format!(
            "artifact-{}-{}-{}",
            label,
            std::process::id(),
            std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .unwrap()
                .as_nanos()
        );
        let d = Dir::root()
            .unwrap()
            .child("fixtures", false)
            .unwrap()
            .child(&n, true)
            .unwrap();
        let p = PathBuf::from(runtime_root::ROOT).join("fixtures").join(n);
        let sentinel = p.join("sentinel");
        fs::create_dir(&sentinel).unwrap();
        fs::write(sentinel.join("canary"), b"synthetic-untouched").unwrap();
        fs::set_permissions(&sentinel, fs::Permissions::from_mode(0o750)).unwrap();
        fs::set_permissions(sentinel.join("canary"), fs::Permissions::from_mode(0o640)).unwrap();
        (p, d, sentinel)
    }
    fn unchanged(p: &std::path::Path) {
        assert_eq!(fs::metadata(p).unwrap().mode() & 0o777, 0o750);
        assert_eq!(
            fs::metadata(p.join("canary")).unwrap().mode() & 0o777,
            0o640
        );
        assert_eq!(fs::read(p.join("canary")).unwrap(), b"synthetic-untouched");
        assert_eq!(fs::read_dir(p).unwrap().count(), 1);
    }
    #[test]
    fn normal_fd_copy_publication_and_quarantine() {
        let (_, d, s) = setup("control");
        let a = d.child("artifacts", true).unwrap();
        let mut f = a.create("stage").unwrap();
        f.write_all(b"full synthetic body").unwrap();
        let mut published = f.publish(&a, "final").unwrap();
        assert_eq!(published.read_limit(100).unwrap(), b"full synthetic body");
        assert!(f.publish(&a, "final").is_err());
        let q = a.child("quarantine", true).unwrap();
        a.quarantine("stage", &q, "old-stage").unwrap();
        assert!(!a.exists("stage").unwrap());
        assert_eq!(
            q.open("old-stage").unwrap().read_limit(100).unwrap(),
            b"full synthetic body"
        );
        unchanged(&s);
    }
    #[test]
    fn directory_and_file_symlinks_reject_without_chmod() {
        let (p, d, s) = setup("links");
        symlink(&s, p.join("artifacts")).unwrap();
        assert!(d.child("artifacts", true).is_err());
        symlink(s.join("canary"), p.join("output")).unwrap();
        assert!(d.create("output").is_err());
        assert!(d.open("output").is_err());
        unchanged(&s);
    }
    #[test]
    fn ancestor_replaced_after_check_create_uses_old_fd_and_rejects() {
        let (p, d, s) = setup("create-race");
        let a = d.child("artifacts", true).unwrap();
        let result = a.create_after_check("output", || {
            fs::rename(p.join("artifacts"), p.join("detached")).unwrap();
            symlink(&s, p.join("artifacts")).unwrap();
        });
        assert!(result.is_err());
        unchanged(&s);
        assert!(!s.join("output").exists());
    }
    #[test]
    fn file_replaced_after_check_write_never_follows_replacement() {
        let (p, d, s) = setup("write-race");
        let mut f = d.create("output").unwrap();
        let result = f.write_after_check(b"owned bytes", || {
            fs::rename(p.join("output"), p.join("detached")).unwrap();
            symlink(s.join("canary"), p.join("output")).unwrap();
        });
        assert!(result.is_err());
        unchanged(&s);
        assert_eq!(fs::read(p.join("detached")).unwrap(), b"owned bytes");
    }
    #[test]
    fn staging_replacement_cannot_publish_or_reopen() {
        let (p, d, s) = setup("stage-race");
        let mut f = d.create("stage").unwrap();
        f.write_all(b"original stage").unwrap();
        fs::rename(p.join("stage"), p.join("detached")).unwrap();
        symlink(s.join("canary"), p.join("stage")).unwrap();
        assert!(f.publish(&d, "final").is_err());
        assert!(!d.exists("final").unwrap());
        assert!(f.read_limit(100).is_err());
        unchanged(&s);
    }
    #[test]
    fn parser_fd_output_and_reopen_reject_after_name_replacement() {
        let (p, d, s) = setup("parser-race");
        let mut out = d.create("parsed").unwrap();
        let mut child_fd = out.descriptor().unwrap();
        fs::rename(p.join("parsed"), p.join("detached")).unwrap();
        symlink(s.join("canary"), p.join("parsed")).unwrap();
        child_fd.write_all(b"synthetic parser result").unwrap();
        assert!(out.len().is_err());
        assert!(out.read_limit(100).is_err());
        unchanged(&s);
    }
    #[test]
    fn quarantine_directory_swap_never_moves_into_sentinel() {
        let (p, d, s) = setup("quarantine-race");
        let mut f = d.create("orphan").unwrap();
        f.write_all(b"orphan").unwrap();
        let q = d.child("quarantine", true).unwrap();
        fs::rename(p.join("quarantine"), p.join("detached")).unwrap();
        symlink(&s, p.join("quarantine")).unwrap();
        assert!(d.quarantine("orphan", &q, "moved").is_err());
        assert!(d.exists("orphan").unwrap());
        unchanged(&s);
    }
}

/// Read-only external input. Unlike owned output, never requires/chmods source permissions.
pub struct ReadInput { dir: Dir, name: String, fd: File }
impl Dir {
    pub fn read_input(&self, s: &str) -> R<ReadInput> {
        self.validate()?;
        let n=name(s)?;
        let fd=unsafe { libc::openat(self.fd().as_raw_fd(),n.as_ptr(),libc::O_RDONLY|libc::O_NOFOLLOW|libc::O_CLOEXEC|libc::O_NONBLOCK) };
        if fd<0 {return Err(err());}
        let f=ReadInput{dir:self.clone(),name:s.into(),fd:unsafe{File::from_raw_fd(fd)}};
        crate::apple_health::Input::validate(&f)?; Ok(f)
    }
}
impl crate::apple_health::Input for ReadInput {
    fn validate(&self) -> R<()> {
        self.dir.validate()?;
        let m=self.fd.metadata().map_err(|_|err())?;
        if !m.is_file() || m.uid()!=unsafe{libc::getuid()} || m.nlink()!=1 {return Err(err());}
        let n=name(&self.name)?; let mut st:libc::stat=unsafe{std::mem::zeroed()};
        if unsafe{libc::fstatat(self.dir.fd().as_raw_fd(),n.as_ptr(),&mut st,libc::AT_SYMLINK_NOFOLLOW)}!=0 || st.st_dev as u64!=m.dev() || st.st_ino!=m.ino() || st.st_mode as u32 & libc::S_IFMT as u32!=libc::S_IFREG as u32 {return Err(err());}
        Ok(())
    }
    fn descriptor(&mut self) -> R<File> {
        self.validate()?;self.fd.seek(SeekFrom::Start(0)).map_err(|_|err())?;self.fd.try_clone().map_err(|_|err())
    }
}
impl OwnedFile {
    pub fn validate_unique(&self)->R<()> {
        self.validate()?;
        if self.fd.metadata().map_err(|_|err())?.nlink()!=1{return Err(err());}
        Ok(())
    }
}
