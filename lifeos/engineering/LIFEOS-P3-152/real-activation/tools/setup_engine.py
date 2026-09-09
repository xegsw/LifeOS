from pathlib import Path
import json,os,stat,zipfile
R=Path('/private/tmp/lifeos-p3-152-health-conversation-v1');D=R/'real-activation-source-engine'
assert not R.is_symlink() and stat.S_IMODE(R.stat().st_mode)==0o700
m=json.loads((R/'.owner.json').read_text());assert m['task']=='P3-152' and m['owner']=='01a07f0e-dbbd-7d23-9e6d-68f2152f9484'
os.umask(0o077);D.mkdir(exist_ok=False)
(D/'.owner.json').write_text(json.dumps({'task':'P3-152','owner':m['owner'],'root':str(D),'kind':'synthetic-source-engine'}))
for d in ['fixtures','fixtures/app-source','fixtures/external','.runtime','tmp','artifacts','inputs']:(D/d).mkdir()
texts={'project.md':'# 合成项目资料\n项目星舟的目标是先核对需求，再完成验证。负责人是合成角色林舟。\n[内部笔记](notes.txt)\n[外部合成文件](../external/approved.txt)\n[合成网页](https://synthetic.invalid/article)\n','notes.txt':'合成资料：项目星舟的交付时间为下周五，先完成原型验证。\n','table.csv':'项目,状态\n星舟,待验证\n','page.html':'<html><title>合成页面</title><p>项目星舟需要保留完整来源。</p><script>excluded</script></html>','config.json':'{"project":"private configuration is excluded"}','unknown.bin':'unrecognized format'}
texts['pagination.txt']='pagination fixture '+('abcdefghijklmnop '*4000)
for n,s in texts.items():(D/'fixtures/app-source'/n).write_text(s)
(D/'fixtures/external/approved.txt').write_text('合成外部资料：项目星舟获准引用这一条说明。')
with zipfile.ZipFile(D/'fixtures/app-source/document.docx','w') as z:z.writestr('word/document.xml','<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>项目星舟合成文档，需要检查需求。</w:t></w:r></w:p></w:body></w:document>')
xml='''<?xml version="1.0" encoding="UTF-8"?><HealthData locale="en_US"><Record type="HKQuantityTypeIdentifierStepCount" sourceName="Synthetic Import Watch" unit="count" value="4321" startDate="2026-09-08 09:00:00 +0800" endDate="2026-09-08 10:00:00 +0800"/><Record type="HKCategoryTypeIdentifierSleepAnalysis" sourceName="Synthetic Import Watch" value="HKCategoryValueSleepAnalysisAsleepCore" startDate="2026-09-07 23:00:00 +0800" endDate="2026-09-08 06:00:00 +0800"/><Record type="HKQuantityTypeIdentifierAppleExerciseTime" sourceName="Synthetic Import Watch" unit="min" value="24" startDate="2026-09-08 17:00:00 +0800" endDate="2026-09-08 17:24:00 +0800"/></HealthData>'''
(D/'inputs/health-demo.xml').write_text(xml)
with zipfile.ZipFile(D/'inputs/health-demo.zip','w',zipfile.ZIP_DEFLATED) as z:z.writestr('apple_health_export/export.xml',xml)
(D/'inputs/broken.xml').write_text(xml[:-13])
print('created fixed synthetic source-engine fixtures; no real files accessed')
