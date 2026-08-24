#!/usr/bin/env python3
import hashlib,json,shutil,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[6]; EV=ROOT/'lifeos/engineering/LIFEOS-P3-106/evidence/rework-1'; SRC=Path('/private/tmp/lifeos-p3-104-p3-106-app-rework1-20260823/capture.sqlite'); DST=Path('/private/tmp/lifeos-p3-104-p3-106-tamper-rework1-20260823/capture.sqlite'); SENT=DST.parent/'sentinel.txt'
before=hashlib.sha256(SENT.read_bytes()).hexdigest(); shutil.copyfile(SRC,DST)
with sqlite3.connect(DST) as c: c.execute('DROP TABLE audit'); c.commit()
after=hashlib.sha256(SENT.read_bytes()).hexdigest(); d={'source_db':str(SRC),'tamper_db':str(DST),'operation':'DROP TABLE audit on fixed non-sensitive copy','sentinel_before':before,'sentinel_after':after,'sentinel_unchanged':before==after,'status':'PASS' if before==after else 'FAIL'}; (EV/'schema_tamper_prepared.json').write_text(json.dumps(d,indent=2)+'\n'); print(json.dumps(d)); raise SystemExit(0 if d['status']=='PASS' else 1)
