import sys,unittest,io,zipfile,importlib.util
from pathlib import Path
spec=importlib.util.spec_from_file_location('parser',Path(__file__).parents[1]/'tools/parse_source.py');p=importlib.util.module_from_spec(spec);spec.loader.exec_module(p)
class Parsers(unittest.TestCase):
 def test_long_text_complete(self):
  text='合成内容\n'*100000;r=p.parse(text.encode(),'.md');self.assertEqual(''.join(x['text'] for x in r['segments']),text)
 def test_restricted_configuration(self):
  for ext in ['.json','.yaml','.toml','.ini','.conf']:
   r=p.parse(b'secret=synthetic-canary',ext);self.assertEqual(r['status'],'restricted');self.assertNotIn('canary',str(r))
 def test_encoding(self):self.assertEqual(p.parse(b'\xff','.txt')['reason'],'unsupported_encoding')
 def test_html(self):
  r=p.parse(b'<title>T</title><p>body</p><script>CANARY</script><iframe src="https://never.invalid">SECRET</iframe><a href="https://example.invalid">ref</a>','.html');self.assertEqual(r['title'],'T');self.assertNotIn('CANARY',str(r));self.assertNotIn('SECRET',str(r));self.assertEqual(len(r['links']),1)
 def test_markdown_references(self):
  r=p.parse(b'[[note]] ![[pic.png]] [web](https://example.invalid/a)','.md');self.assertEqual(r['links'],['note','pic.png','https://example.invalid/a'])
 def docx(self,entries):
  b=io.BytesIO()
  with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
   for k,v in entries:z.writestr(k,v)
  return b.getvalue()
 def test_docx(self):
  xml='<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:p><w:r><w:t>synthetic paragraph</w:t></w:r></w:p></w:document>'
  r=p.parse(self.docx([('word/document.xml',xml)]),'.docx');self.assertEqual(r['segments'][0]['text'],'synthetic paragraph');self.assertTrue(r['segments'][0]['locator'].startswith('paragraph:1'))
 def test_docx_traversal_entity_corrupt(self):
  for data in [self.docx([('../escape','x')]),self.docx([('word/document.xml','<!DOCTYPE x><x/>')]),b'bad']:
   self.assertEqual(p.parse(data,'.docx')['status'],'unparsed')
 def test_pdf_text_scan_encrypted(self):
  from reportlab.pdfgen import canvas
  from pypdf import PdfWriter,PdfReader
  b=io.BytesIO();c=canvas.Canvas(b);c.drawString(10,700,'synthetic PDF paragraph');c.showPage();c.save();r=p.parse(b.getvalue(),'.pdf');self.assertEqual(r['status'],'parsed');self.assertIn('page:1',r['segments'][0]['locator'])
  w=PdfWriter();w.add_blank_page(width=100,height=100);o=io.BytesIO();w.write(o);self.assertEqual(p.parse(o.getvalue(),'.pdf')['reason'],'ocr_required')
  w.encrypt('synthetic-password');o=io.BytesIO();w.write(o);self.assertEqual(p.parse(o.getvalue(),'.pdf')['reason'],'encrypted_document')
 def test_docx_declared_expansion_budget(self):
  import struct
  blob=bytearray(self.docx([('word/document.xml','<x/>')]))
  offset=blob.index(b'PK\x01\x02');struct.pack_into('<I',blob,offset+24,129*1024*1024)
  self.assertEqual(p.parse(bytes(blob),'.docx')['reason'],'container_budget')
 def test_attachments_original_only(self):
  for ext in ['.png','.mp3','.mp4','.exe','.zip','.unknown']:self.assertEqual(p.parse(b'opaque',ext)['reason'],'original_only')
 def test_actual_process_memory_budget_rejects_complete_payload(self):
  import subprocess,json,os
  data=b'SYNTHETIC_BUDGET_CANARY '*1000000
  result=subprocess.run([sys.executable,'-B',str(Path(__file__).parents[1]/'tools/parse_source.py'),'.txt'],input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=30,env={**os.environ,'TMPDIR':'/private/tmp/lifeos-p3-147-obsidian-source-v1/.runtime'})
  value=json.loads(result.stdout);self.assertEqual(value['reason'],'parse_memory_budget');self.assertEqual(value['segments'],[]);self.assertNotIn(b'CANARY',result.stdout+result.stderr)
if __name__=='__main__':unittest.main()
