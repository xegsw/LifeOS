import os,stat,json
from pathlib import Path
r=Path('/private/tmp/lifeos-p3-151-health-conversation-v1')
for p,mode in [(r,0o700),(r/'.owner.json',0o600),(r/'synthetic',0o700),(r/'tmp',0o700)]:
 st=p.lstat();assert not stat.S_ISLNK(st.st_mode) and st.st_uid==os.getuid() and stat.S_IMODE(st.st_mode)==mode
m=json.loads((r/'.owner.json').read_text());assert m['task']=='P3-151' and m['root']==str(r) and m['owner']=='01a07f0e-dbbd-7d23-9e6d-68f2152f9484'
