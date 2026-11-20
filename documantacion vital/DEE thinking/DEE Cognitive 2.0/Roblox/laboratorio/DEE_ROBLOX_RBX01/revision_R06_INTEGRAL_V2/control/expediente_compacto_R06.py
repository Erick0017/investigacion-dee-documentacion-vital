"""Explicit-file R06 evidence packager. Stdlib only; no DEE imports or execution.

freeze records selected immutable bytes; build requires finalized:true and verifies
the eleven protected originals again. verify extracts to a NEW directory and
checks exact archive names, CRC, SHA, UTF-8/JSON/CSV and Python syntax. No globbing
of Native states, no database access, no automatic scientific approval.
"""
from __future__ import annotations
import argparse, ast, csv, datetime as dt, hashlib, io, json, os, re, stat, struct, zipfile, zlib
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parents[1]
MAX_ZIP = 15_000_000
DEFAULT_MEMBER = 2_000_000
MAX_MEMBER = 8_000_000
MAX_TOTAL = 40_000_000
MAX_FILES = 750
MANIFEST = 'CONTROL/MANIFIESTO_SHA256.json'
PROTECTION = 'CONTROL/PROTECCION_CRITICOS.json'
SUFFIXES = {'.txt','.md','.json','.jsonl','.csv','.py','.luau','.rbxmx','.rbxlx','.jpg','.png'}
DENIED_PARTS = {'configuracion_privada','configuración_privada','secrets','.ssh',
                '.git','__pycache__','site-packages','python313','motor'}
SECRET_KEYS = {'password','passwd','auth_token','access_token','refresh_token',
               'api_key','apikey','authorization','cookie','credential','credentials'}

def dump(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False)+'\n').encode('utf-8')

def load_bytes(raw):
    return json.loads(raw.decode('utf-8-sig'), parse_constant=lambda x: (_ for _ in ()).throw(ValueError('NONFINITE_JSON')))

def sha(raw): return hashlib.sha256(raw).hexdigest()
def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()

def no_links(path):
    """Check each ancestor once per call; selected file count is bounded."""
    path = Path(os.path.abspath(path))
    for item in (path, *path.parents):
        st = item.lstat()
        if stat.S_ISLNK(st.st_mode) or getattr(st, 'st_file_attributes', 0) & 0x400:
            raise ValueError('LINK_OR_REPARSE_POINT: '+str(item))
    return path

def within(path, roots):
    return any(path == root or root in path.parents for root in roots)

def archive_name(value):
    if not isinstance(value,str) or '\\' in value or ':' in value or '\x00' in value:
        raise ValueError('UNSAFE_ARCHIVE_NAME')
    p = PurePosixPath(value)
    if p.is_absolute() or not p.parts or any(x in ('','.','..') for x in p.parts) or str(p)!=value:
        raise ValueError('NONCANONICAL_ARCHIVE_NAME: '+value)
    if p.suffix.lower() not in SUFFIXES or any(x.lower() in DENIED_PARTS for x in p.parts):
        raise ValueError('EXCLUDED_MEMBER: '+value)
    return value

def secret_values(value, trail=''):
    if isinstance(value,dict):
        for key,item in value.items():
            if str(key).lower() in SECRET_KEYS and item not in (None,False,'','REDACTED','<redacted>'):
                # Names of fields in source code are allowed; actual JSON credentials are not.
                raise ValueError('CREDENTIAL_FIELD_REQUIRES_REDACTION: '+trail+'/'+str(key))
            secret_values(item, trail+'/'+str(key))
    elif isinstance(value,list):
        for item in value: secret_values(item,trail+'[]')

def validate_png(raw):
    """CRC/chunks plus bounded zlib scanline structure; no image library/codecs."""
    if raw[:8]!=b'\x89PNG\r\n\x1a\n':raise ValueError('PNG_MAGIC')
    pos=8;header=None;palette=False;compressed=[];idat_ended=False;ended=False
    while pos<len(raw):
        if len(raw)-pos<12:raise ValueError('PNG_TRUNCATED_CHUNK')
        length=struct.unpack_from('>I',raw,pos)[0];kind=raw[pos+4:pos+8]
        if not re.fullmatch(b'[A-Za-z]{4}',kind)or kind[2]&32:raise ValueError('PNG_CHUNK_TYPE')
        finish=pos+12+length
        if finish>len(raw)or length>MAX_MEMBER:raise ValueError('PNG_CHUNK_BOUND')
        data=raw[pos+8:pos+8+length];crc=struct.unpack_from('>I',raw,pos+8+length)[0]
        if zlib.crc32(kind+data)&0xffffffff!=crc:raise ValueError('PNG_CRC')
        if header is None and kind!=b'IHDR':raise ValueError('PNG_IHDR_FIRST')
        if kind==b'IHDR':
            if header is not None or length!=13:raise ValueError('PNG_IHDR')
            width,height,bits,color,compression,filtering,interlace=struct.unpack('>IIBBBBB',data)
            valid={0:(1,2,4,8,16),2:(8,16),3:(1,2,4,8),4:(8,16),6:(8,16)}
            if not 1<=width<=8192 or not 1<=height<=8192 or color not in valid or bits not in valid[color]or compression or filtering or interlace not in(0,1):
                raise ValueError('PNG_DIMENSION_OR_FORMAT')
            header=(width,height,bits,color,interlace)
        elif kind==b'PLTE':
            if palette or compressed or not 3<=length<=768 or length%3:raise ValueError('PNG_PALETTE')
            palette=True
        elif kind==b'IDAT':
            if idat_ended or header[3]==3 and not palette:raise ValueError('PNG_IDAT_ORDER')
            compressed.append(data)
        elif kind==b'IEND':
            if length or not compressed or finish!=len(raw):raise ValueError('PNG_IEND')
            ended=True;pos=finish;break
        elif not(kind[0]&32):raise ValueError('PNG_UNKNOWN_CRITICAL_CHUNK')
        if compressed and kind!=b'IDAT':idat_ended=True
        pos=finish
    if not ended:raise ValueError('PNG_IEND_MISSING')
    width,height,bits,color,interlace=header;channels={0:1,2:3,3:1,4:2,6:4}[color]
    passes=[(0,0,1,1)]if not interlace else[(0,0,8,8),(4,0,8,8),(0,4,4,8),(2,0,4,4),(0,2,2,4),(1,0,2,2),(0,1,1,2)]
    layout=[]
    for x,y,dx,dy in passes:
        w=max(0,(width-x+dx-1)//dx);h=max(0,(height-y+dy-1)//dy)
        if w and h:layout.append(((w*bits*channels+7)//8,h))
    expected=sum((row+1)*h for row,h in layout)
    if expected>64_000_000:raise ValueError('PNG_DECOMPRESSED_BOUND')
    decoder=zlib.decompressobj()
    try:pixels=decoder.decompress(b''.join(compressed),expected+1)
    except zlib.error as error:raise ValueError('PNG_DEFLATE')from error
    if len(pixels)!=expected or not decoder.eof or decoder.unused_data or decoder.unconsumed_tail:raise ValueError('PNG_SCANLINE_PAYLOAD')
    cursor=0
    for row,h in layout:
        for _ in range(h):
            if pixels[cursor]>4:raise ValueError('PNG_FILTER_BYTE')
            cursor+=row+1

def validate_jpg(raw):
    """Finite marker/frame/table/scan parser; entropy pixels are not decoded here."""
    if raw[:2]!=b'\xff\xd8' or raw[-2:]!=b'\xff\xd9':raise ValueError('JPG_MAGIC_OR_EOI')
    pos=2;frame=None;quant=False;huffman=False;scans=0
    while pos<len(raw):
        if raw[pos]!=255:raise ValueError('JPG_MARKER_REQUIRED')
        while pos<len(raw)and raw[pos]==255:pos+=1
        if pos>=len(raw):raise ValueError('JPG_TRUNCATED_MARKER')
        marker=raw[pos];pos+=1
        if marker==0xd9:
            if pos!=len(raw)or frame is None or not quant or not huffman or not scans:raise ValueError('JPG_INCOMPLETE_STRUCTURE')
            return
        if marker in(0,0xd8,1)or 0xd0<=marker<=0xd7:raise ValueError('JPG_UNEXPECTED_STANDALONE_MARKER')
        if pos+2>len(raw):raise ValueError('JPG_TRUNCATED_SEGMENT')
        length=struct.unpack_from('>H',raw,pos)[0]
        if length<2 or pos+length>len(raw):raise ValueError('JPG_SEGMENT_BOUND')
        payload=raw[pos+2:pos+length];pos+=length
        if marker in(0xc0,0xc1,0xc2):
            if frame is not None or len(payload)<6:raise ValueError('JPG_SOF')
            precision=payload[0];height,width=struct.unpack_from('>HH',payload,1);components=payload[5]
            if precision not in(8,12)or not 1<=width<=8192 or not 1<=height<=8192 or components not in(1,3,4)or len(payload)!=6+3*components or width*height*components*2>64_000_000:
                raise ValueError('JPG_DIMENSION_OR_FORMAT')
            component_ids=[]
            for offset in range(6,len(payload),3):
                component_ids.append(payload[offset]);sampling=payload[offset+1]
                if not 1<=sampling>>4<=4 or not 1<=sampling&15<=4 or payload[offset+2]>3:raise ValueError('JPG_COMPONENT')
            if len(set(component_ids))!=components:raise ValueError('JPG_COMPONENT_IDS')
            frame=(width,height,components,set(component_ids))
        elif marker in(0xc3,0xc5,0xc6,0xc7,0xc9,0xca,0xcb,0xcd,0xce,0xcf):raise ValueError('JPG_UNSUPPORTED_CODING')
        elif marker==0xdb:
            q=0
            while q<len(payload):
                info=payload[q];q+=1
                if info>>4 not in(0,1)or info&15>3:raise ValueError('JPG_DQT')
                q+=64*(1+(info>>4))
                if q>len(payload):raise ValueError('JPG_DQT_LENGTH')
            if not payload:raise ValueError('JPG_EMPTY_DQT')
            quant=True
        elif marker==0xc4:
            q=0
            while q<len(payload):
                if q+17>len(payload):raise ValueError('JPG_DHT_LENGTH')
                info=payload[q];count=sum(payload[q+1:q+17]);q+=17
                if info>>4 not in(0,1)or info&15>3 or not 1<=count<=256 or q+count>len(payload):raise ValueError('JPG_DHT')
                q+=count
            if not payload:raise ValueError('JPG_EMPTY_DHT')
            huffman=True
        elif marker==0xda:
            if frame is None or len(payload)<4:raise ValueError('JPG_SOS_BEFORE_FRAME')
            n=payload[0]
            if not 1<=n<=frame[2]or len(payload)!=4+2*n or any(payload[1+2*i]not in frame[3]for i in range(n)):
                raise ValueError('JPG_SOS_COMPONENTS')
            start=pos;entropy=0
            while pos<len(raw):
                if raw[pos]!=255:entropy+=1;pos+=1;continue
                begin=pos
                while pos<len(raw)and raw[pos]==255:pos+=1
                if pos>=len(raw):raise ValueError('JPG_TRUNCATED_SCAN')
                following=raw[pos]
                if following==0 or 0xd0<=following<=0xd7:entropy+=1;pos+=1;continue
                pos=begin;break
            if not entropy or pos<=start:raise ValueError('JPG_EMPTY_SCAN')
            scans+=1
    raise ValueError('JPG_EOI_MISSING')

def validate_content(name, raw):
    suffix=PurePosixPath(name).suffix.lower()
    if suffix=='.png':validate_png(raw);return
    if suffix=='.jpg':validate_jpg(raw);return
    text=raw.decode('utf-8-sig')
    if '\x00' in text: raise ValueError('NUL_IN_TEXT: '+name)
    if suffix=='.json': secret_values(load_bytes(raw))
    elif suffix=='.jsonl':
        for line in text.splitlines():
            if line.strip(): secret_values(load_bytes(line.encode('utf-8')))
    elif suffix=='.csv':
        list(csv.reader(io.StringIO(text)))
    elif suffix=='.py': ast.parse(text,filename=name)
    # Avoid dumping matches: credentials, if accidentally selected, never appear in diagnostics.
    if re.search(r'(?i)(?:password|auth_token|access_token|refresh_token|api_key)\s*[:=]\s*[\"\'](?![\"\']|<|REDACTED)[A-Za-z0-9_+/.=-]{10,}[\"\']',text):
        raise ValueError('POSSIBLE_LITERAL_SECRET: '+name)

def stable_read(path, limit=DEFAULT_MEMBER):
    path=no_links(path)
    before=path.stat()
    if not stat.S_ISREG(before.st_mode) or before.st_size>limit:
        raise ValueError('REGULAR_BOUNDED_FILE_REQUIRED: '+str(path))
    raw=path.read_bytes(); after=path.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns) or len(raw)!=before.st_size:
        raise ValueError('SOURCE_CHANGED_DURING_READ: '+str(path))
    return raw

def read_plan(path, require_final=False):
    path=no_links(path); plan=load_bytes(stable_read(path,MAX_TOTAL))
    if plan.get('schema')!='DEE.INTEGRAL.V2.explicit_export_plan.R01': raise ValueError('PLAN_SCHEMA')
    if require_final and plan.get('finalized') is not True: raise ValueError('PLAN_NOT_FINALIZED')
    roots=[no_links(HERE)]
    # Only a named sibling C02 revision may supply historical small primaries.
    for extra in plan.get('source_roots',[]):
        root=no_links(HERE/extra)
        if root!=HERE.parent/'revision_R05_C02': raise ValueError('UNAPPROVED_SOURCE_ROOT')
        roots.append(root)
    entries=plan.get('files')
    if not isinstance(entries,list) or not 1<=len(entries)<=MAX_FILES: raise ValueError('FINITE_FILE_LIST_REQUIRED')
    seen=set(); total=0; large_primaries=0
    for row in entries:
        name=archive_name(row['archive'])
        if name.casefold() in seen or name in (MANIFEST,PROTECTION): raise ValueError('ARCHIVE_COLLISION: '+name)
        seen.add(name.casefold())
        src=Path(row['source']); src=src if src.is_absolute() else HERE/src
        src=no_links(src)
        if not within(src,roots): raise ValueError('SOURCE_OUTSIDE_DECLARED_ROOTS: '+str(src))
        if src.suffix.lower() not in SUFFIXES or any(x.lower() in DENIED_PARTS for x in src.parts):
            raise ValueError('EXCLUDED_SOURCE: '+str(src))
        if not isinstance(row.get('role'),str) or not row['role']: raise ValueError('MEMBER_ROLE_REQUIRED')
        limit=row.get('max_bytes',DEFAULT_MEMBER)
        if type(limit)is not int or not 1<=limit<=MAX_MEMBER:raise ValueError('FINITE_MEMBER_LIMIT_REQUIRED')
        if limit>DEFAULT_MEMBER:
            if row['role']not in ('native_primary','native_control_primary'):raise ValueError('LARGE_EXCEPTION_ONLY_FOR_DECISIVE_NATIVE_PRIMARY')
            large_primaries+=1
        if large_primaries>4:raise ValueError('AT_MOST_FOUR_DECLARED_LARGE_NATIVE_PRIMARIES')
        row['_limit']=limit
        row['_path']=src
        total+=src.stat().st_size
    if total>MAX_TOTAL: raise ValueError('SELECTED_TOTAL_OVER_40MB')
    return plan

def protected_report():
    source=HERE/'control/CRITICOS_ANTES_R06.json'
    raw=stable_read(source); ref=load_bytes(raw); files=ref.get('files',[])
    if len(files)!=11: raise ValueError('EXPECTED_ELEVEN_CRITICAL_REFERENCES')
    rows=[]
    for row in files:
        value=stable_read(row['path'],20_000_000)
        rows.append({'role':row['role'],'path':row['path'],'expected_bytes':row['bytes'],
                     'expected_sha256':row['sha256'],'current_bytes':len(value),
                     'current_sha256':sha(value),'matches_before':len(value)==row['bytes'] and sha(value)==row['sha256']})
    report={'schema':'DEE.INTEGRAL.V2.protected_files_verification.R01','utc':utc(),
            'source_reference':str(source),'source_reference_sha256':sha(raw),
            'coverage':'Eleven explicit critical files only; no claim of whole-project immutability.',
            'all_eleven_unchanged':all(row['matches_before'] for row in rows),'files':rows}
    if not report['all_eleven_unchanged']: raise ValueError('PROTECTED_CRITICAL_CHANGED')
    return report

def freeze(plan_path, output):
    plan=read_plan(plan_path)
    for row in plan['files']:
        raw=stable_read(row.pop('_path'),row.pop('_limit')); validate_content(row['archive'],raw)
        row.update(bytes=len(raw),sha256=sha(raw))
    plan['frozen_utc']=utc()
    plan['finalized']=False
    plan['freeze_scope']='Selected files only. Root must review and set finalized:true after all runtime/scientific sources close.'
    output=Path(output)
    if output.exists(): raise ValueError('FRESH_OUTPUT_REQUIRED')
    output.write_bytes(dump(plan))
    return {'files':len(plan['files']),'raw_bytes':sum(x['bytes']for x in plan['files']),'frozen_plan':str(output),'finalized':False}

def build(plan_path, output):
    plan=read_plan(plan_path,True)
    output=Path(output)
    if output.exists() or not output.parent.is_dir(): raise ValueError('FRESH_ZIP_AND_EXISTING_PARENT_REQUIRED')
    no_links(output.parent)
    if output.suffix.lower()!='.zip': raise ValueError('ZIP_SUFFIX_REQUIRED')
    protection=dump(protected_report()); records=[]; content=[]
    for row in plan['files']:
        raw=stable_read(row['_path'],row['_limit']); validate_content(row['archive'],raw)
        if len(raw)!=row.get('bytes') or sha(raw)!=row.get('sha256'): raise ValueError('SOURCE_DIFFERS_FROM_FROZEN_PLAN: '+row['archive'])
        record={key:row[key] for key in ('archive','source','role','bytes','sha256')}
        if row['_limit']>DEFAULT_MEMBER:record['max_bytes']=row['_limit']
        records.append(record)
        content.append((row['archive'],raw))
    records.append({'archive':PROTECTION,'role':'verification','source':None,'bytes':len(protection),'sha256':sha(protection)})
    content.append((PROTECTION,protection))
    manifest={'schema':'DEE.INTEGRAL.V2.content_manifest.R01','created_utc':utc(),'plan_sha256':sha(stable_read(plan_path,MAX_TOTAL)),
              'ZIP_is_executable_backup':False,'hash_scope':'Content members; excludes this manifest and external ZIP hash.',
              'recalculations':plan.get('recalculations',[]),'files':records}
    content.append((MANIFEST,dump(manifest)))
    # ZIP names come from the explicit plan, never from Windows case-insensitive staging paths.
    with zipfile.ZipFile(output,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,raw in content:
            info=zipfile.ZipInfo(name); info.compress_type=zipfile.ZIP_DEFLATED; info.external_attr=0o100644<<16
            z.writestr(info,raw,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    if output.stat().st_size>MAX_ZIP: raise ValueError('ZIP_OVERSIZE_PRESERVED_NOT_DELIVERABLE: '+str(output.stat().st_size))
    # Recheck the protected originals at the very end; generated proof is not a lifetime guarantee.
    protected_report()
    return verify(output)

def verify(zip_path, extraction=None):
    zip_path=no_links(zip_path)
    raw=stable_read(zip_path,MAX_ZIP)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members=z.infolist(); names=[x.filename for x in members]
        if len(names)>MAX_FILES+2 or len(names)!=len(set(x.casefold()for x in names)): raise ValueError('DUPLICATE_ZIP_MEMBERS')
        for info in members:
            archive_name(info.filename)
            if info.flag_bits&1 or info.compress_type!=zipfile.ZIP_DEFLATED or info.is_dir() or ((info.external_attr>>16)&0o170000)==0o120000:
                raise ValueError('NONSTANDARD_OR_UNSAFE_ZIP_MEMBER')
            if info.file_size>MAX_MEMBER or info.file_size<0: raise ValueError('MEMBER_SIZE_BOUND')
        if sum(x.file_size for x in members)>MAX_TOTAL: raise ValueError('UNCOMPRESSED_SIZE_BOUND')
        if z.testzip() is not None: raise ValueError('ZIP_CRC_ERROR')
        manifest=load_bytes(z.read(MANIFEST))
        if manifest.get('schema')!='DEE.INTEGRAL.V2.content_manifest.R01': raise ValueError('MANIFEST_SCHEMA')
        records=manifest.get('files',[])
        expected={x['archive']for x in records}|{MANIFEST}
        if set(names)!=expected or len(records)+1!=len(names): raise ValueError('EXACT_MEMBER_SET_MISMATCH')
        large=0
        for row in records:
            limit=row.get('max_bytes',DEFAULT_MEMBER)
            if type(limit)is not int or not 1<=limit<=MAX_MEMBER:raise ValueError('MANIFEST_MEMBER_LIMIT')
            if limit>DEFAULT_MEMBER:
                large+=1
                if row['role']not in ('native_primary','native_control_primary')or large>4:raise ValueError('MANIFEST_LARGE_PRIMARY_EXCEPTION')
            if row['bytes']>limit:raise ValueError('MANIFEST_MEMBER_SIZE_BOUND')
            value=z.read(row['archive']); validate_content(row['archive'],value)
            if len(value)!=row['bytes'] or sha(value)!=row['sha256']: raise ValueError('MEMBER_HASH_MISMATCH: '+row['archive'])
        protection=load_bytes(z.read(PROTECTION))
        if protection.get('all_eleven_unchanged') is not True or len(protection.get('files',[]))!=11:
            raise ValueError('CRITICAL_PROTECTION_PROOF_MISSING')
        if extraction is not None:
            extraction=Path(extraction)
            if extraction.exists() or not extraction.parent.is_dir(): raise ValueError('NEW_CLEAN_EXTRACTION_REQUIRED')
            no_links(extraction.parent); extraction.mkdir()
            for name in names:
                dst=extraction.joinpath(*PurePosixPath(name).parts)
                dst.parent.mkdir(parents=True,exist_ok=True)
                with dst.open('xb') as f:f.write(z.read(name))
            # Case-exact names are checked in ZIP, bytes again on disk. No original paths opened here.
            for row in records:
                dst=extraction.joinpath(*PurePosixPath(row['archive']).parts)
                if sha(stable_read(dst,row.get('max_bytes',DEFAULT_MEMBER)))!=row['sha256']: raise ValueError('EXTRACTED_HASH_MISMATCH')
    return {'schema':'DEE.INTEGRAL.V2.ZIP_verification.R01','utc':utc(),'zip':str(zip_path),
            'bytes':len(raw),'sha256':sha(raw),'limit_bytes':MAX_ZIP,'members':len(names),
            'all_member_CRC_SHA_UTF8_checks':True,'Native_MCP_model_calls':0,
            'extraction':str(extraction)if extraction else None,
            'scope':'Integrity and selected-content legibility; not scientific approval or an executable Native backup.'}

def cli():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest='mode',required=True)
    f=sub.add_parser('freeze');f.add_argument('--plan',type=Path,required=True);f.add_argument('--output',type=Path,required=True)
    b=sub.add_parser('build');b.add_argument('--plan',type=Path,required=True);b.add_argument('--output',type=Path,required=True)
    v=sub.add_parser('verify');v.add_argument('--zip',type=Path,required=True);v.add_argument('--extract',type=Path)
    a=p.parse_args()
    result=freeze(a.plan,a.output)if a.mode=='freeze' else build(a.plan,a.output)if a.mode=='build'else verify(a.zip,a.extract)
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':cli()
