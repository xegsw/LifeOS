"""Prepare only the contract-owned P3-157 synthetic source root; never use legacy roots."""
from pathlib import Path
import os,json,stat,datetime,zipfile
ROOT=Path('/private/tmp/lifeos-p3-157-real-actions-v1/closure-1')
os.umask(0o077)
def verify(p):
 m=p.lstat();assert stat.S_ISDIR(m.st_mode) and stat.S_IMODE(m.st_mode)==0o700 and m.st_uid==os.getuid()
verify(ROOT)
with (ROOT/'.owner.json').open() as f: owner=json.load(f)
assert owner['task']=='P3-157' and owner['root']==str(ROOT)
r=ROOT/'source-engine';verify(r)
for n in ['fixtures','fixtures/app-source','fixtures/external','inputs','artifacts','tmp','.runtime']:
 p=r/n;p.mkdir(mode=0o700,exist_ok=True);verify(p)
def write(p,body):
 if p.exists():
  assert p.is_file() and not p.is_symlink() and p.read_bytes()==body, 'fixture conflict'
  return
 with p.open('xb') as f:f.write(body)
(r/'fixtures/app-source/.obsidian').mkdir(mode=0o700,exist_ok=True)
write(r/'fixtures/app-source/.obsidian/settings.json',b'{"synthetic_secret":"CONFIG_CANARY_DO_NOT_DISCLOSE"}')
write(r/'fixtures/app-source/项目计划.md','# 合成项目计划\n先核对项目计划，再安排下一步。\n[[参考]]\n[目录外合成依据](../external/approved.txt)\n[合成网页](https://synthetic.invalid/article)\n'.encode())
write(r/'fixtures/app-source/参考.md','合成参考：项目计划需要保留原始依据。'.encode())
write(r/'fixtures/app-source/长文.txt',('合成长文的完整依据。\n'*6000+'全文终点。').encode())
write(r/'fixtures/app-source/附件.bin',b'\x00SYNTHETIC_ATTACHMENT\xff')
write(r/'fixtures/app-source/坏编码.txt',b'\xff\xfeINVALID_SYNTHETIC')
write(r/'fixtures/external/approved.txt','合成目录外目标：项目计划需要先核对外部资料。'.encode())
write(r/'fixtures/app-source/star.txt','项目星舟：合成工作资料。先确认项目依据，再推进工作报告。'.encode())
write(r/'fixtures/app-source/pagination.txt',('pagination fixture '+'abcdefghijklmnop '*4000).encode())
# Fixed synthetic day: imported values are fixture observations, unrelated to user data.
day='2026-09-08';start=f'{day} 08:00:00 +0800';end=f'{day} 08:30:00 +0800'
xml=('<?xml version="1.0" encoding="UTF-8"?><HealthData>'+''.join(f'<Record type="{kind}" sourceName="Synthetic Watch" unit="{unit}" value="{value}" creationDate="{end}" startDate="{start}" endDate="{end}"/>' for kind,unit,value in [('HKQuantityTypeIdentifierStepCount','count','4321'),('HKQuantityTypeIdentifierAppleExerciseTime','min','18'),('HKCategoryTypeIdentifierSleepAnalysis','','HKCategoryValueSleepAnalysisAsleep')])+'</HealthData>').encode()
write(r/'inputs/health-demo.xml',xml);write(r/'inputs/broken.xml',b'<HealthData><Record broken')
p=r/'inputs/health-demo.zip'
if not p.exists():
 with zipfile.ZipFile(p,'x') as z:z.writestr('apple_health_export/export.xml',xml)
else:
 with zipfile.ZipFile(p) as z:assert z.read('apple_health_export/export.xml')==xml
print('P3-157 fixtures ready')
