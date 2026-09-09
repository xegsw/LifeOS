# coding: utf-8
import importlib.util,io,json,struct,unittest,zipfile,stat
from pathlib import Path
from make_fixtures import doc,record,zipped,make
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('parser',ROOT/'candidate/tools/apple_health_source.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class ParserTests(unittest.TestCase):
 def parse(self,data,**limits):
  out=[];p.run(io.BytesIO(data),{**p.DEFAULTS,**limits},out.append);return out
 def rejects(self,data,**limits):
  with self.assertRaises((p.Rejected,zipfile.BadZipFile)):self.parse(data,**limits)
 def test_normal_inline_dtd_and_zip(self):
  d=doc([record()]);a=self.parse(d);b=self.parse(zipped(d,{'apple_health_export/route.gpx':b'ignored'}));self.assertEqual(a[1],b[1]);self.assertEqual(b[-1]['attachments'],1)
 def test_over_legacy_limits(self):
  d=(ROOT/'fixtures/07-large.xml').read_bytes();self.assertGreater(len(d),128*1024);self.assertEqual(self.parse(d)[-1]['supported'],1000)
 def test_entity_denied(self):self.rejects(b'<!DOCTYPE HealthData [<!ENTITY x SYSTEM "file:///synthetic-not-opened">]><HealthData>&x;</HealthData>')
 def test_internal_entity_denied(self):self.rejects(b'<!DOCTYPE HealthData [<!ENTITY x "abc">]><HealthData>&x;</HealthData>')
 def test_external_dtd_denied(self):self.rejects(b'<!DOCTYPE HealthData SYSTEM "https://synthetic.invalid/never"><HealthData/>')
 def test_escaping(self):self.assertEqual(self.parse(doc([record(source='A &amp; B')]))[1]['source'],'A & B')
 def test_truncated(self):self.rejects(doc([record()])[:-3])
 def test_bad_root(self):self.rejects(b'<Other/>')
 def test_unknown_type(self):self.assertEqual(self.parse(doc([record(typ='OtherType')]))[-1]['unsupported'],1)
 def test_chinese_not_asleep(self):self.assertEqual(self.parse(doc([record('HKCategoryTypeIdentifierSleepAnalysis','睡眠时间')]))[-1]['unsupported'],1)
 def test_sleep_identifiers(self):
  for value in sorted(p.ASLEEP|p.NON_SLEEP):
   r=self.parse(doc([record('HKCategoryTypeIdentifierSleepAnalysis',value)]))[1];self.assertEqual(r['asleep'],value in p.ASLEEP)
 def test_units(self):
  self.assertEqual(self.parse(doc([record('HKQuantityTypeIdentifierAppleExerciseTime','120','s')]))[1]['value'],2)
  self.rejects(doc([record(unit='km')]))
 def test_bad_values_dates(self):
  for v in ['NaN','inf','-1','0.5']:self.rejects(doc([record(value=v)]))
  self.rejects(doc([record(start='2026-02-30 00:00:00 +0800')]))
 def test_offset_and_crossday(self):
  r=self.parse(doc([record(start='2026-09-07 23:00:00 -0500',end='2026-09-08 01:00:00 -0500')]))[1];self.assertEqual(r['offset'],-300);self.assertEqual(r['endMs']-r['startMs'],7200000)
 def test_limits(self):
  d=doc([record(),record()])
  for limit in [{'fileBytes':10},{'xmlBytes':20},{'records':1},{'tokenBytes':50},{'depth':1}]:self.rejects(d,**limit)
 def test_zip_paths(self):
  for name in ['../bad','/bad','C:/bad','a\\bad','a//bad','a/./bad']:self.rejects(zipped(doc([]),{name:b'x'}))
 def test_zip_duplicates(self):self.rejects(zipped(doc([]),{'EXPORT.XML':b'x'},name='export.xml'))
 def test_zip_ambiguous(self):self.rejects(zipped(doc([]),{'export.xml':doc([])}))
 def test_zip_symlink(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w') as z:
   z.writestr('export.xml',doc([]));i=zipfile.ZipInfo('link');i.create_system=3;i.external_attr=(stat.S_IFLNK|0o777)<<16;z.writestr(i,'not-opened')
  self.rejects(b.getvalue())
 def test_zip_bomb_and_entries(self):
  self.rejects(zipped(doc([]),{'bomb':b'A'*50000}),ratio=2)
  self.rejects(zipped(doc([]),{'a':b'x'}),entries=1)
 def test_zip_crc(self):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w',compression=zipfile.ZIP_STORED) as z:z.writestr('export.xml',doc([]))
  raw=bytearray(b.getvalue());at=raw.find(b'HealthData');raw[at]=ord('X');self.rejects(bytes(raw))
 def test_zip_encrypted(self):
  raw=bytearray(zipped(doc([])));at=raw.find(b'PK\x01\x02');flags=struct.unpack_from('<H',raw,at+8)[0];struct.pack_into('<H',raw,at+8,flags|1);self.rejects(bytes(raw))
 def test_attachments_never_parse(self):self.assertEqual(self.parse(zipped(doc([]),{'routes/ref.xml':b'<!ENTITY xx SYSTEM "file:///not-opened">'}))[-1]['attachments'],1)
 def test_zip_central_allocation_bound(self):
  raw=bytearray(zipped(doc([])));at=raw.rfind(b'PK\x05\x06');struct.pack_into('<I',raw,at+12,9*1024*1024);self.rejects(bytes(raw))
 def test_zip_multidisk_and_zip64(self):
  for offset,value in [(4,1),(10,65535)]:
   raw=bytearray(zipped(doc([])));at=raw.rfind(b'PK\x05\x06');struct.pack_into('<H',raw,at+offset,value);self.rejects(bytes(raw))
 def test_cross_offset_record_rejected(self):self.rejects(doc([record(start='2026-09-08 01:00:00 +0800',end='2026-09-08 02:00:00 +0700')]))
if __name__=='__main__':unittest.main(verbosity=2)
