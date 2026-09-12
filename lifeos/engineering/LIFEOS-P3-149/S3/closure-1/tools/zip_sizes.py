"""Read only EOCD/central-directory metadata; never open a ZIP member."""
import os,stat,struct,zipfile,json
from pathlib import Path

def summarize(f):
 size=os.fstat(f.fileno()).st_size
 f.seek(max(0,size-65557));tail=f.read(65557);pos=tail.rfind(b'PK\x05\x06')
 if pos<0 or len(tail)-pos<22:raise ValueError("eocd")
 _,disk,cdisk,n1,n,central,offset,comment=struct.unpack_from('<4s4H2IH',tail,pos)
 if disk or cdisk or n1!=n or n>4096 or central>8*1024*1024 or offset+central!=max(0,size-65557)+pos or pos+22+comment!=len(tail):raise ValueError("central_bounds")
 f.seek(0)
 with zipfile.ZipFile(f) as z:
  infos=z.infolist();selected=[i for i in infos if i.filename in ['export.xml','apple_health_export/export.xml','导出.xml','apple_health_export/导出.xml']]
  xml=selected[0] if len(selected)==1 else None;total=sum(i.file_size for i in infos);ratio=max((i.file_size/max(1,i.compress_size) for i in infos),default=0)
  return {'status':'metadata_only','expected_xml_selection_unique':len(selected)==1,'archive_bytes':size,'entries':len(infos),'total_declared_uncompressed_bytes':total,'selected_xml_bytes':xml.file_size if xml else None,'selected_xml_compressed_bytes':xml.compress_size if xml else None,'max_member_ratio':round(ratio,2),'selected_xml_ratio':round(xml.file_size/max(1,xml.compress_size),2) if xml else None,'total_exceeds_512MiB':total>512*1024*1024,'selected_xml_exceeds_512MiB':xml.file_size>512*1024*1024 if xml else None,'any_member_ratio_exceeds_200':ratio>200,'member_body_read':False}
def main():
 handles=[];stage="open_source"
 try:
  d=os.open('/',os.O_RDONLY|os.O_DIRECTORY);handles.append(d);chain=[]
  for name in ['Users','xxe','Downloads']:
   child=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=d);chain.append((d,name,child));handles.append(child);d=child
  fd=os.open('导出.zip',os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=d);handles.append(fd);before=os.fstat(fd)
  if not stat.S_ISREG(before.st_mode) or before.st_uid!=os.getuid() or before.st_nlink!=1:raise ValueError()
  stage="central_directory"
  with os.fdopen(os.dup(fd),'rb') as f:v=summarize(f)
  stage="identity_check"
  for parent,name,child in chain:
   a=os.stat(name,dir_fd=parent,follow_symlinks=False);b=os.fstat(child)
   if not stat.S_ISDIR(a.st_mode) or (a.st_dev,a.st_ino)!=(b.st_dev,b.st_ino):raise ValueError()
  after=os.stat('导出.zip',dir_fd=d,follow_symlinks=False)
  identity=lambda x:(x.st_dev,x.st_ino,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
  if identity(before)!=identity(after):raise ValueError()
 except Exception as e:v={'status':'metadata_failed','stage':stage,'error_class':type(e).__name__,'reason':str(e) if str(e) in ['xml_selection','eocd','central_bounds'] else 'withheld','member_body_read':False}
 finally:
  for fd in reversed(handles):os.close(fd)
 p=Path(__file__).resolve().parents[1]/'evidence/zip-size-summary-whitelist.json'
 with p.open('x') as f:json.dump(v,f,indent=2)
 print(json.dumps(v))
if __name__=='__main__':main()
