# coding: utf-8
import importlib.util,io,json,struct,unittest,zipfile,stat
from pathlib import Path
from make_fixtures import doc,record,zipped,make
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('parser',ROOT/'candidate/tools/apple_health_source.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
def legacy_name_flags(data):
 b=bytearray(data)
 with zipfile.ZipFile(io.BytesIO(data)) as z:
  for i in z.infolist():struct.pack_into('<H',b,i.header_offset+6,i.flag_bits & ~0x800)
 end=b.rfind(b'PK\x05\x06');off=struct.unpack_from('<I',b,end+16)[0]
 while b[off:off+4]==b'PK\x01\x02':
  flag=struct.unpack_from('<H',b,off+8)[0];struct.pack_into('<H',b,off+8,flag & ~0x800)
  n,e,c=struct.unpack_from('<HHH',b,off+28);off+=46+n+e+c
 return bytes(b)
class ParserTests(unittest.TestCase):
 def test_closure3_points_are_metric_specific(self):
  at='2026-09-08 01:00:00 +0800'
  rows=[record(start=at,end=at),record('HKQuantityTypeIdentifierAppleExerciseTime','5','min',start=at,end=at),record('HKCategoryTypeIdentifierSleepAnalysis','HKCategoryValueSleepAnalysisAsleep','',start=at,end=at)]
  e=self.parse(doc(rows));self.assertEqual(e[-1]['supported'],2);self.assertEqual(e[-1]['skipped'],1);self.assertEqual(e[-1]['unprojected'],2)
 def test_closure3_mixed_conservation_and_skip_reason(self):
  e=self.parse(doc([record(),record(value='NaN'),record(typ='Other'),record(start='2026-09-09 00:00:00 +0800',end='2026-09-08 00:00:00 +0800')]))[-1]
  self.assertEqual((e['supported'],e['skipped'],e['unsupported']),(1,2,1));self.assertEqual(sum(e['skipReasons'].values()),2)
 def test_closure3_long_observation_not_arbitrary_seven_day_rejection(self):
  e=self.parse(doc([record(start='2026-01-01 00:00:00 +0800',end='2026-03-01 00:00:00 +0800')]))
  self.assertEqual(e[-1]['supported'],1);self.assertFalse(e[1]['projectionEligible']);self.assertEqual(e[-1]['compatibility']['long_interval'],1)
 def test_closure3_skips_still_count_towards_hard_record_limit(self):
  self.rejects(doc([record(value='NaN'),record(value='NaN')]),records=1)
 def test_closure3_structural_corruption_still_fails_whole_stream(self):
  self.rejects(doc([record(),record(value='NaN')])[:-6])

 def test_closure2_missing_utf8_flag_fixed_allowlist(self):
  data=legacy_name_flags(zipped(doc([record()]),name='apple_health_export/导出.xml'))
  self.assertEqual(self.parse(data)[-1]['supported'],1)
 def test_closure2_encoding_alias_ambiguity_rejected(self):
  data=legacy_name_flags(zipped(doc([]),{'apple_health_export/导出.xml':doc([])}))
  self.rejects(data)
 def test_closure2_encoding_does_not_admit_unknown_or_traversal(self):
  self.rejects(legacy_name_flags(zipped(doc([]),name='其他/导出.xml')))
  self.rejects(legacy_name_flags(zipped(doc([]),name='../导出.xml')))

 def test_closure_fixed_english_chinese_names(self):
  for name in ['export.xml','apple_health_export/export.xml','导出.xml','apple_health_export/导出.xml']:
   self.assertEqual(self.parse(zipped(doc([record()]),name=name))[-1]['supported'],1)
 def test_closure_multiple_whitelist_members_rejected(self):
  self.rejects(zipped(doc([]),{'apple_health_export/导出.xml':doc([])}))
 def test_closure_nonallowlisted_and_spoofed_root_rejected(self):
  self.rejects(zipped(doc([]),name='arbitrary/export.xml'))
  self.rejects(zipped(b'<OtherData/>',name='导出.xml'))
  self.rejects(zipped(doc([]),name='../导出.xml'))

 def test_closure_xml_budget_excludes_unopened_attachment_total(self):
  from unittest.mock import patch
  d=doc([record()]);data=zipped(d,{'attachment.bin':bytes(range(256))*8});opened=[];original=zipfile.ZipFile.open
  def track(z,name,*a,**kw):
   opened.append(name.filename if isinstance(name,zipfile.ZipInfo) else name);return original(z,name,*a,**kw)
  with patch.object(zipfile.ZipFile,'open',track):events=self.parse(data,xmlBytes=len(d))
  self.assertEqual(events[-1]['supported'],1);self.assertEqual(events[-1]['attachments'],1)
  self.assertEqual(opened,['apple_health_export/export.xml'])
 def test_closure_selected_xml_exact_boundary_and_over_limit(self):
  d=doc([record()]);data=zipped(d)
  self.assertEqual(self.parse(data,xmlBytes=len(d))[-1]['supported'],1)
  self.rejects(data,xmlBytes=len(d)-1)
 def test_closure_attachment_bomb_guard_and_count_remain(self):
  self.rejects(zipped(doc([]),{'unopened.bin':b'A'*50000}),ratio=2)
  self.rejects(zipped(doc([]),{'unopened.bin':b'x'}),entries=1)

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
  self.assertEqual(self.parse(doc([record(unit='km')]))[-1]['skipped'],1)
 def test_bad_values_dates(self):
  for v in ['NaN','inf','-1','0.5']:self.assertEqual(self.parse(doc([record(value=v)]))[-1]['skipped'],1)
  self.assertEqual(self.parse(doc([record(start='2026-02-30 00:00:00 +0800')]))[-1]['skipped'],1)
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
 def test_cross_offset_record_observed_without_daily_guess(self):
  e=self.parse(doc([record(start='2026-09-08 01:00:00 +0800',end='2026-09-08 02:00:00 +0700')]))
  self.assertEqual(e[-1]['supported'],1);self.assertFalse(e[1]['projectionEligible']);self.assertEqual(e[1]['endMs']-e[1]['startMs'],7200000)
if __name__=='__main__':unittest.main(verbosity=2)
