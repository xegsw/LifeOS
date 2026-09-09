"""Offline stdin parser. Never opens a source path or resolves a URL.
Caller owns the input FD, memory/resource deadline, and artifact lifecycle.
"""
import sys,json,io,zipfile,posixpath,re
from html.parser import HTMLParser
from xml.etree import ElementTree as ET
MAX=64*1024*1024
EXPANDED=128*1024*1024
class StaticHTML(HTMLParser):
 def __init__(self):
  super().__init__(convert_charrefs=True);self.hidden=0;self.title_mode=False;self.title=[];self.parts=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  if tag in ('script','style','iframe','form','object','template','noscript'):self.hidden+=1
  if tag=='title':self.title_mode=True
  if not self.hidden:
   for k,v in attrs:
    if k=='href' and tag=='a' and v:self.links.append(v)
   if tag in ('p','div','br','h1','h2','li','section'):self.parts.append('\n')
 def handle_endtag(self,tag):
  if tag in ('script','style','iframe','form','object','template','noscript'):self.hidden=max(0,self.hidden-1)
  if tag=='title':self.title_mode=False
 def handle_data(self,s):
  if self.title_mode:self.title.append(s)
  elif not self.hidden:self.parts.append(s)
def parts(text,locator):
 # Preserve every character in source-order; no silent total or segment truncation.
 return [{'text':text[i:i+1024],'locator':locator+':char:'+str(i)} for i in range(0,len(text),1024)]
def parse(data,ext):
 if len(data)>MAX:return {'status':'pending','reason':'parse_memory_budget','segments':[],'links':[]}
 if ext in ['.md','.markdown','.txt','.json','.yaml','.yml','.toml','.ini','.cfg','.conf','.html','.htm','.csv','.log']:
  try:text=data.decode('utf-8',errors='strict')
  except UnicodeError:return {'status':'unparsed','reason':'unsupported_encoding','segments':[],'links':[]}
  if '\x00' in text:return {'status':'unparsed','reason':'unsupported_encoding','segments':[],'links':[]}
  if ext in ['.json','.yaml','.yml','.toml','.ini','.cfg','.conf']:
   return {'status':'restricted','reason':'configuration_excluded','segments':[],'links':[]}
  if ext in ['.html','.htm']:
   h=StaticHTML();h.feed(text);return {'status':'parsed','title':''.join(h.title),'segments':parts(''.join(h.parts),'html'),'links':list(dict.fromkeys(h.links))}
  links=[]
  if ext in ['.md','.markdown']:
   links=re.findall(r'!?\[\[([^\]|]+)(?:\|[^\]]*)?\]\]',text)+re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+[^)]*)?\)',text)
  return {'status':'parsed','segments':parts(text,'text'),'links':list(dict.fromkeys(links))}
 if ext=='.docx':
  try:
   z=zipfile.ZipFile(io.BytesIO(data));infos=z.infolist()
   if len(infos)>10000 or sum(i.file_size for i in infos)>EXPANDED:raise ValueError('container_budget')
   names=set()
   for i in infos:
    n=i.filename
    if n.startswith('/') or '\\' in n or '..' in n.split('/') or n in names or (i.external_attr>>16)&0o170000==0o120000:raise ValueError('container_path_rejected')
    names.add(n)
    if i.flag_bits&1:raise ValueError('encrypted_document')
   info=z.getinfo('word/document.xml')
   if info.file_size>MAX:raise ValueError('parse_memory_budget')
   xml=z.read(info)
   if b'<!DOCTYPE' in xml or b'<!ENTITY' in xml:raise ValueError('xml_entity_rejected')
   root=ET.fromstring(xml);segments=[];ns='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
   for n,p in enumerate(root.iter(ns+'p')):
    text=''.join(t.text or '' for t in p.iter(ns+'t'));segments.extend(parts(text,'paragraph:'+str(n+1)))
   return {'status':'parsed','segments':segments,'links':[]}
  except (ValueError,KeyError,zipfile.BadZipFile,ET.ParseError,RuntimeError) as e:
   code=str(e) if str(e) in ['container_budget','container_path_rejected','encrypted_document','parse_memory_budget','xml_entity_rejected'] else 'damaged_document'
   return {'status':'unparsed','reason':code,'segments':[],'links':[]}
 if ext=='.pdf':
  try:
   from pypdf import PdfReader
   import pypdf.filters
   pypdf.filters.ZLIB_MAX_OUTPUT_LENGTH=8*1024*1024
   reader=PdfReader(io.BytesIO(data),strict=True)
   if reader.is_encrypted:return {'status':'unparsed','reason':'encrypted_document','segments':[],'links':[]}
   segments=[]
   for n,page in enumerate(reader.pages):segments.extend(parts(page.extract_text() or '', 'page:'+str(n+1)))
   return {'status':'parsed' if segments else 'unparsed','reason':None if segments else 'ocr_required','segments':segments,'links':[]}
  except ImportError:return {'status':'unparsed','reason':'parser_dependency_missing','segments':[],'links':[]}
  except Exception:return {'status':'unparsed','reason':'damaged_document','segments':[],'links':[]}
 return {'status':'unparsed','reason':'original_only','segments':[],'links':[]}
if __name__=='__main__':
 try:
  data=sys.stdin.buffer.read(MAX+1);out=parse(data,sys.argv[1].lower())
  import resource
  peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
  if sys.platform!='darwin':peak*=1024
  if peak>MAX:out={'status':'pending','reason':'parse_memory_budget','segments':[],'links':[]}
  print(json.dumps(out,ensure_ascii=False))
 except Exception:print(json.dumps({'status':'unparsed','reason':'parser_failed','segments':[],'links':[]}))
