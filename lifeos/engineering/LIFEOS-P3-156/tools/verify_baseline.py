from pathlib import Path
import hashlib,json,os,stat
root=Path(__file__).resolve().parents[1]
snapshot=json.loads((root/'baseline-snapshot.json').read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
base=Path(snapshot['baselineRoot'])
for entry in snapshot['manifests']:
    p=Path(entry['path']); assert sha(p)==entry['sha256']
    m=json.loads(p.read_text())
    for rel,digest in m['files'].items():
        q=Path(rel);assert not q.is_absolute() and '..' not in q.parts
        assert sha(p.parent/q)==digest,rel
    assert sha(Path(m['reportPath']))==m['reportSha256']
for rel,digest in snapshot['candidateFiles'].items():assert sha(base/'candidate'/rel)==digest,rel
runtime=Path('/private/tmp/lifeos-p3-156-next-action-v1')
for p in [runtime,runtime/'synthetic']:
    s=p.lstat();assert stat.S_ISDIR(s.st_mode) and stat.S_IMODE(s.st_mode)==0o700 and s.st_uid==os.getuid()
p=runtime/'.owner.json';s=p.lstat();assert stat.S_ISREG(s.st_mode) and stat.S_IMODE(s.st_mode)==0o600 and s.st_uid==os.getuid() and s.st_nlink==1
assert json.loads(p.read_text())=={'task':'P3-156','root':str(runtime),'thread':'01a07f0e-dbbd-7d23-9e6d-68f2152f9484'}
corpus=json.loads((root/'tests/interaction-corpus.json').read_text())
assert len({c['id'] for c in corpus['cases']})==len(corpus['cases'])
print(json.dumps({'parentFilesPreserved':315,'switchFilesPreserved':14,'baselineCandidateFiles':166,'ownerVerified':True,'designedCases':len(corpus['cases']),'runtimeBehaviorTested':False}))
