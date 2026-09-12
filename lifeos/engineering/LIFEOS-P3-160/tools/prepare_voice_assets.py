#!/usr/bin/env python3
"""Explicit public dependency fetch, or fully offline verification. No personal assets."""
import argparse,hashlib,json,pathlib,urllib.request
p=argparse.ArgumentParser();p.add_argument('--download-public',action='store_true');a=p.parse_args()
r=pathlib.Path(__file__).resolve().parents[1];root=pathlib.Path('/private/tmp/lifeos-p3-160-voice-v1/models');root.mkdir(parents=True,exist_ok=True)
lock=json.loads((r/'candidate/src/voice/assets.lock.json').read_text());results=[]
for e in lock['assets']:
 rel=pathlib.PurePosixPath(e['path']);assert not rel.is_absolute() and '..' not in rel.parts
 target=root/rel;assert not target.is_symlink()
 if not target.exists():
  if not a.download_public:raise SystemExit('model_asset_missing: '+e['path'])
  assert e['url'].startswith(('https://www.modelscope.cn/api/v1/models/pkufool/','https://raw.githubusercontent.com/snakers4/silero-vad/'))
  data=urllib.request.urlopen(e['url'],timeout=45).read(16000000);assert hashlib.sha256(data).hexdigest()==e['sha256'];target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
 assert hashlib.sha256(target.read_bytes()).hexdigest()==e['sha256'];results.append(e['path'])
print(json.dumps({'verified_assets':results,'download_requested':a.download_public,'real_data_access':False}))
