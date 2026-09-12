#!/usr/bin/python3
# coding: utf-8
"""Read one already-open synthetic SourcePort descriptor; never resolve XML/ZIP references."""
import datetime as dt
import hashlib
import json
import math
import os
import re
import stat
import struct
import sys
import time
import zipfile
from xml.parsers import expat

DEFAULTS = dict(fileBytes=256*1024*1024, xmlBytes=512*1024*1024,
                entries=4096, ratio=200, records=2_000_000, tokenBytes=65536, depth=32)
TYPES = {'HKQuantityTypeIdentifierStepCount':'steps',
         'HKQuantityTypeIdentifierAppleExerciseTime':'exercise',
         'HKCategoryTypeIdentifierSleepAnalysis':'sleep'}
ASLEEP = {'HKCategoryValueSleepAnalysis'+x for x in ('Asleep','AsleepUnspecified','AsleepCore','AsleepDeep','AsleepREM')}
NON_SLEEP = {'HKCategoryValueSleepAnalysisInBed','HKCategoryValueSleepAnalysisAwake'}
class Rejected(Exception): pass
def reject(code): raise Rejected(code)
def emit(v): print(json.dumps(v, ensure_ascii=False, separators=(',',':')),flush=True)
def timestamp(s):
    if not re.fullmatch(r'\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d(?:\.\d{1,6})?\s?[+-]\d\d:?\d\d',s or ''):
        reject('health_date_rejected')
    try:
        s=re.sub(r'\s?([+-]\d{2}):?(\d{2})$',r'\1:\2',s)
        v=dt.datetime.fromisoformat(s)
        offset=int(v.utcoffset().total_seconds()/60)
        ms=int(v.timestamp()*1000)
    except (ValueError,OverflowError): reject('health_date_rejected')
    if not -840<=offset<=840 or not 0<=ms<=4102444800000: reject('health_date_rejected')
    return ms,offset

def run(f, limits, output=emit):
    started=time.monotonic()
    def tick():
        if time.monotonic()-started>110: reject('health_time_limit')
    digest=hashlib.sha256(); size=0
    while True:
        block=f.read(65536)
        if not block: break
        size+=len(block)
        if size>limits['fileBytes']: reject('health_file_limit')
        digest.update(block);tick()
    f.seek(0)
    output({'event':'begin','digest':digest.hexdigest(),'bytes':size})
    magic=f.read(4);f.seek(0);archive=None;attachments=0
    if magic.startswith(b'PK'):
        # Bound central-directory allocation before ZipFile materializes ZipInfo objects.
        f.seek(max(0,size-65557));tail=f.read(65557);pos=tail.rfind(b'PK\x05\x06')
        if pos<0 or len(tail)-pos<22:reject('health_zip_corrupt')
        _,disk,central_disk,on_disk,entries,central_bytes,central_offset,comment=struct.unpack_from('<4s4H2IH',tail,pos)
        if pos+22+comment!=len(tail) or disk or central_disk or on_disk!=entries:reject('health_zip_corrupt')
        if entries==65535 or central_bytes==0xffffffff or central_offset==0xffffffff:reject('health_zip64_unsupported')
        if entries>limits['entries'] or central_bytes>8*1024*1024:reject('health_zip_entries_limit')
        if central_offset+central_bytes!=max(0,size-65557)+pos:reject('health_zip_corrupt')
        f.seek(0)
        try: archive=zipfile.ZipFile(f)
        except (zipfile.BadZipFile,ValueError): reject('health_zip_corrupt')
        infos=archive.infolist()
        if len(infos)>limits['entries']:reject('health_zip_entries_limit')
        names=set();selected=[];total=0
        for info in infos:
            name=info.filename;parts=name.rstrip('/').split('/')
            if (not name or '\\' in name or name.startswith('/') or ':' in name or '\x00' in info.orig_filename
                or any(x in ('','.','..') for x in parts) or name.casefold().rstrip('/') in names):reject('health_zip_path_rejected')
            names.add(name.casefold().rstrip('/'))
            mode=info.external_attr>>16;kind=stat.S_IFMT(mode)
            if kind not in (0,stat.S_IFREG,stat.S_IFDIR):reject('health_zip_special_rejected')
            if info.flag_bits&1:reject('health_zip_encrypted')
            if info.compress_type not in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED):reject('health_zip_compression_rejected')
            total+=info.file_size
            if total>limits['xmlBytes'] or info.file_size>max(1,info.compress_size)*limits['ratio']:reject('health_zip_expansion_limit')
            if name in ('export.xml','apple_health_export/export.xml'):selected.append(info)
            elif not info.is_dir():attachments+=1
        if len(selected)!=1:reject('health_zip_xml_ambiguous')
        source=archive.open(selected[0])
    else:source=f
    counts={'supported':0,'unsupported':0,'attachments':attachments,'types':{}}
    parser=expat.ParserCreate('UTF-8');depth=0;root_seen=False;closed=False;read=0;lex=0;quote=None;in_tag=False
    def unsupported(name):
        counts['unsupported']+=1
        if len(counts['types'])>=128 and name not in counts['types']:name='other-types'
        counts['types'][name]=counts['types'].get(name,0)+1
    def start(name,a):
        nonlocal depth,root_seen
        depth+=1
        if depth>limits['depth'] or sum(len(k)+len(v) for k,v in a.items())>limits['tokenBytes']:reject('health_xml_structure_limit')
        if depth==1:
            if root_seen or name!='HealthData':reject('health_xml_root_rejected')
            root_seen=True;return
        if depth!=2:return
        if name=='Record':
            typ=a.get('type','');metric=TYPES.get(typ)
            if metric is None:unsupported(typ[:160] or 'Record-without-type');return
            category=a.get('value','') if metric=='sleep' else None
            if metric=='sleep' and category not in ASLEEP|NON_SLEEP:unsupported('sleep-category:'+category[:100]);return
            start_ms,offset=timestamp(a.get('startDate'));end_ms,end_offset=timestamp(a.get('endDate'))
            if end_ms<=start_ms or end_ms-start_ms>7*86400000 or offset!=end_offset:reject('health_interval_rejected')
            source_name=a.get('sourceName','')
            if not source_name or len(source_name)>160 or any(ord(c)<32 for c in source_name):reject('health_source_rejected')
            if metric=='sleep':value=None;unit='minutes'
            else:
                try:value=float(a.get('value',''))
                except ValueError:reject('health_value_rejected')
                if not math.isfinite(value) or value<0 or value>100_000_000:reject('health_value_rejected')
                raw_unit=a.get('unit')
                if metric=='steps':
                    if raw_unit!='count' or value!=int(value):reject('health_unit_rejected')
                    unit='count'
                else:
                    if raw_unit not in ('min','s'):reject('health_unit_rejected')
                    if raw_unit=='s':value/=60
                    unit='minutes'
            counts['supported']+=1
            output({'event':'row','source':source_name,'metric':metric,'startMs':start_ms,'endMs':end_ms,
                    'offset':offset,'value':value,'unit':unit,'category':category,'asleep':category in ASLEEP if category else False})
        elif name not in ('ExportDate','Me'):
            unsupported(name[:160])
        if counts['supported']+counts['unsupported']>limits['records']:reject('health_records_limit')
    def end(name):
        nonlocal depth,closed
        depth-=1
        if depth==0:closed=True
    def entity(*args):reject('health_xml_entity_rejected')
    parser.StartElementHandler=start;parser.EndElementHandler=end
    parser.EntityDeclHandler=entity;parser.ExternalEntityRefHandler=entity
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    def doctype(name,system,public,internal):
        if name!='HealthData' or system or public:reject('health_xml_external_dtd_rejected')
    parser.StartDoctypeDeclHandler=doctype
    try:
        while True:
            block=source.read(32768)
            if not block:break
            tick();read+=len(block)
            if read>limits['xmlBytes']:reject('health_xml_limit')
            # Bound unfinished tags/comments/text before Expat can buffer them.
            for ch in block:
                lex+=1
                if lex>limits['tokenBytes']:reject('health_xml_token_limit')
                if quote:
                    if ch==quote:quote=None
                elif in_tag and ch in (34,39):quote=ch
                elif ch==60:in_tag=True
                elif ch==62:in_tag=False;lex=0
            parser.Parse(block,False)
            if counts['supported']+counts['unsupported']>limits['records']:reject('health_records_limit')
        parser.Parse(b'',True)
        if not root_seen or not closed:reject('health_xml_incomplete')
        if archive:
            source.close()
            # Read/check only the selected XML; unrelated attachments never opened.
            archive.close()
    except (expat.ExpatError,zipfile.BadZipFile,EOFError,RuntimeError,NotImplementedError):reject('health_document_corrupt')
    output({'event':'end','digest':digest.hexdigest(),**counts})

def main():
    try:
        limits=dict(DEFAULTS)
        if len(sys.argv)>1:
            overrides=json.loads(sys.argv[1])
            for k,v in overrides.items():
                if k not in limits or type(v)!=int or not 1<=v<=limits[k]:reject('health_limits_rejected')
                limits[k]=v
        # stdin is a seekable regular descriptor granted by Rust, never an arbitrary filename.
        run(sys.stdin.buffer,limits)
    except (Rejected,OSError,ValueError) as e:
        emit({'event':'error','code':str(e) if isinstance(e,Rejected) else 'health_source_io_failed'})
        return 2
    return 0
if __name__=='__main__':sys.exit(main())
