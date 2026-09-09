# coding: utf-8
from pathlib import Path
import json,zipfile,io,os
ROOT=Path(__file__).resolve().parents[1]
DTD='''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE HealthData [<!ELEMENT HealthData (ExportDate,Me,Record*)><!ATTLIST HealthData locale CDATA #REQUIRED><!ELEMENT Record EMPTY><!ATTLIST Record type CDATA #REQUIRED sourceName CDATA #REQUIRED value CDATA #IMPLIED>]>
'''
def record(typ='HKQuantityTypeIdentifierStepCount',value='120',unit='count',start='2026-09-07 23:00:00 +0800',end='2026-09-08 01:00:00 +0800',source='Synthetic Watch'):
 return f'<Record type="{typ}" sourceName="{source}" unit="{unit}" value="{value}" startDate="{start}" endDate="{end}"/>'
def doc(rows):return (DTD+'<HealthData locale="zh_CN"><ExportDate value="2026-09-09 00:00:00 +0800"/><Me/>'+''.join(rows)+'</HealthData>').encode()
def zipped(data,extras=None,name='apple_health_export/export.xml'):
 b=io.BytesIO()
 with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_DEFLATED) as z:
  z.writestr(zipfile.ZipInfo(name,(2000,1,1,0,0,0)),data,compress_type=zipfile.ZIP_DEFLATED)
  for k,v in (extras or {}).items():z.writestr(zipfile.ZipInfo(k,(2000,1,1,0,0,0)),v,compress_type=zipfile.ZIP_DEFLATED)
 return b.getvalue()
def make():
 rows=[record(),record('HKCategoryTypeIdentifierSleepAnalysis','HKCategoryValueSleepAnalysisAsleepCore','',start='2026-09-07 23:00:00 +0800',end='2026-09-08 07:00:00 +0800'),record('HKQuantityTypeIdentifierAppleExerciseTime','600','s',start='2026-09-08 08:00:00 +0800',end='2026-09-08 08:10:00 +0800'),record('HKQuantityTypeIdentifierHeartRate','70','count/min')]
 files={'01-synthetic-export.xml':doc(rows),'02-synthetic-export.zip':zipped(doc(rows),{'apple_health_export/workout-routes/synthetic.gpx':b'not opened'}),'03-overlap.xml':doc([rows[0],record(value='30',start='2026-09-08 09:00:00 +0800',end='2026-09-08 09:10:00 +0800')]),'04-broken.xml':doc(rows)[:-8], '05-conflict.xml':doc([record(value='999')]), '06-empty.xml':doc([]), '07-large.xml':doc([record(value=str(i+1),source='Synthetic Bulk',start='2026-09-08 10:00:00 +0800',end='2026-09-08 10:10:00 +0800') for i in range(1000)])}
 for name,data in files.items():
  p=ROOT/'fixtures'/name
  if p.exists():assert p.read_bytes()==data
  else:
   with p.open('xb') as f:f.write(data)
 return files
if __name__=='__main__':
 files=make();print(json.dumps({n:len(b) for n,b in files.items()}))
