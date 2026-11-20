"""Select, losslessly encode, seal, verify and publish CPC7 only.

Snapshots are representations of measured states, not response caches. Originals
are never removed or changed. Publication needs the exact candidate's clean proof.
All paths in payload manifests are relative to the single CPC7/ archive root.
"""
from __future__ import annotations
import argparse
from collections import Counter
from datetime import datetime,timezone
import gzip
import hashlib
import io
import json
import os
from pathlib import Path,PurePosixPath
import shutil
import stat
import sys
import tempfile
import time
import zipfile

ROOT=Path(__file__).resolve().parents[2]
NAME='CPC7_MENTE_DEE_ACCESO_SELECTIVO_Y_APRENDIZAJE_CONTINUO_RESULTADOS.zip'
WHL='dee_thinking-4.0.0-cp313-cp313-win_amd64.whl'
WHL_SHA='17c07745b9687d8686d132f055c39c149da1dde807e7246a67d457fe69df5623'
PYD_SHA='20d7c764dbc22d1f110ba255f92073b4f64c744c91f6980335a4e08dd61fe066'
KERNEL_SHA='fbd8190381ed76085f404e6578ff15fe185ab66cd48c67300d2abad61ddc7e31'
BLOCK=4*1024*1024
ALLOWED_DIRS={'app','base_validada','src','configuraciones','resultados','checkpoints','genealogia','revision','referencias','runtime','jobs','tests','pruebas','tools'}
FORBIDDEN_DIRS={'.venv','venv','__pycache__','.git','.pytest_cache','node_modules','_delivery','_distribution','_distribution_tests','build','dist','documantacion vital'}
EXTENSIONS={'.py','.pyi','.ps1','.md','.txt','.json','.jsonl','.eventos','.csv','.tsv','.toml','.yaml','.yml','.ini','.cfg','.log','.deetsnap','.bin','.npy','.npz','.gz','.whl','.cpp','.hpp','.h','.c','.cmake','.png','.svg','.pdf'}
VIRTUAL_NAMES={'MANIFEST.json','HASHES.sha256','LOGICAL_STATES_CPC7.json','SOURCE_CUT.json','PACKAGING_SELECTION.json'}
PROTECTED={
 'CPC3_ENTE_COGNITIVO_CAUSAL_DEE_3_5_0_RESULTADOS.zip':'1c10b8501ff0bb9756d6b1ebe5876a63ae7300ec4722d651e94dfe9e8f45a0f6',
 'CPC4_COMUNICACION_NATIVA_Y_META_ROSETTA_RESULTADOS.zip':'4a14a81f913a434a8e54e47c0c700d7ee54418bb16913aedded8bf49a3294723',
 'CPC5_ARQUITECTURAS_COMPUESTAS_Y_APRENDIZAJE_ACUMULATIVO_RESULTADOS.zip':'d31972a47f12bb574a71a14d7ddca3b7a011f320eaba37dcb2ac97abe1f4ce05',
 'CPC6_MENTE_DEE_INTEGRADA_APRENDIZAJE_Y_COMUNICACION_RESULTADOS.zip':'9d8c72a2536a7d8a782e0f3885d6d9ceba48b5f3d9111f618386def13fff708b'}
PRODUCT_SHA='c78609a7d0d501324324408ed955f60f127965c77efbcbe3b3d04fc14dbb16cf'

def stream_sha(stream):
    h=hashlib.sha256()
    for block in iter(lambda:stream.read(BLOCK),b''):h.update(block)
    return h.hexdigest()

def sha(path):
    with Path(path).open('rb') as stream:return stream_sha(stream)

def put(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.pending.'+str(os.getpid()))
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    os.replace(temporary,path)

def safe_name(name):
    p=PurePosixPath(name)
    assert name and not p.is_absolute() and '\\' not in name and '\x00' not in name
    assert p.as_posix()==name,'Noncanonical archive path'
    assert all(x not in {'','.','..'} and ':' not in x for x in p.parts)
    assert '\n' not in name and '\r' not in name
    return p

def protected(root):
    cases=root.resolve().parents[1];rows=[]
    targets=[(cases/name,value) for name,value in PROTECTED.items()]
    product=cases.parent/'4.0'
    targets.extend([(product/'DEE_thinking_4_0_0_ENTREGA_FINAL_RESULTADOS.zip',PRODUCT_SHA),(product/WHL,WHL_SHA)])
    for path,expected in targets:
        actual=sha(path);assert actual==expected,'Protected original differs: '+str(path)
        rows.append({'name':path.name,'bytes':path.stat().st_size,'sha256':actual,'unchanged':True})
    # Capture small external reviews/transport as well; never overwrite them.
    sidecars=[]
    for path in sorted(cases.iterdir()):
        if path.is_file() and not path.name.startswith('CPC7') and path.suffix.lower() in {'.json','.py','.ps1','.txt','.md'}:
            sidecars.append({'name':path.name,'bytes':path.stat().st_size,'sha256':sha(path)})
    return {'official_artifacts':rows,'existing_sidecars':sidecars}

def select(root):
    root=root.resolve();selected=[];excluded=[]
    for directory,dirs,files in os.walk(root,followlinks=False):
        parent=Path(directory);relparent=parent.relative_to(root)
        kept=[]
        for name in sorted(dirs):
            path=parent/name;rel=path.relative_to(root)
            if path.is_symlink() or path.is_junction():raise ValueError('No symlink/junction: '+str(path))
            if name in FORBIDDEN_DIRS or (len(rel.parts)==1 and name not in ALLOWED_DIRS):
                excluded.append({'path':rel.as_posix()+'/','reason':'DIRECTORY_NOT_IN_POSITIVE_SELECTION'});continue
            if len(rel.parts)>2 and rel.parts[0]=='resultados' and rel.parts[1].startswith(('clean_','minimal_app_')) and name in {'extracted','isolated_env','minimal_payload','generated','minimal_stage'}:
                excluded.append({'path':rel.as_posix()+'/','reason':'DUPLICATE_TECHNICAL_EXTRACTION'});continue
            kept.append(name)
        dirs[:]=kept
        for name in sorted(files):
            path=parent/name;rel=path.relative_to(root);key=rel.as_posix();safe_name(key)
            if path.is_symlink() or not path.resolve().is_relative_to(root):raise ValueError('Escaping source: '+str(path))
            if len(rel.parts)==1 and name in VIRTUAL_NAMES:continue
            if '.pending.' in name or name.endswith(('.pyc','.pyo','.tmp')):
                excluded.append({'path':key,'reason':'TEMPORARY_OR_CACHE'});continue
            if '.zip' in name.lower() and path.suffix.lower()!='.whl':
                raise ValueError('No nested delivery ZIP/segment: '+str(path))
            if path.suffix.lower() not in EXTENSIONS and name not in {'LICENSE','COPYING','NOTICE','CMakeLists.txt'}:
                if rel.parts[0] in {'resultados','checkpoints','genealogia','revision','referencias'}:
                    raise ValueError('Unclassified evidence extension needs explicit review: '+str(path))
                excluded.append({'path':key,'reason':'EXTENSION_NOT_IN_POSITIVE_SELECTION'});continue
            if path.suffix.lower() in {'.ttf','.otf','.woff','.woff2','.exe','.dll','.pyd'}:
                raise ValueError('Toolchain/font/unwrapped binary not permitted: '+str(path))
            selected.append((path,key))
    assert selected and len(selected)==len({rel for _,rel in selected})
    return selected,excluded

def engine(root):
    assert sha(root/'runtime'/WHL)==WHL_SHA
    with zipfile.ZipFile(root/'runtime'/WHL) as z:
        assert z.testzip() is None
        pyd=[name for name in z.namelist() if name.endswith('.pyd')]
        assert len(pyd)==1 and hashlib.sha256(z.read(pyd[0])).hexdigest()==PYD_SHA
    assert sha(root/'genealogia/kernel_v27.cpp')==KERNEL_SHA
    return {'wheel_sha256':WHL_SHA,'native_sha256':PYD_SHA,'kernel_source_sha256':KERNEL_SHA}

def encode_snapshot(source,target,logical):
    target.parent.mkdir(parents=True,exist_ok=True)
    before=sha(source);size=source.stat().st_size
    reused=False
    if target.exists():
        with gzip.open(target,'rb') as decoded:reused=stream_sha(decoded)==before
        if not reused:raise ValueError('Existing encoded snapshot differs: '+str(target))
    else:
        temporary=target.with_name(target.name+'.pending.'+str(os.getpid()))
        with source.open('rb') as original,temporary.open('xb') as stored:
            with gzip.GzipFile(filename='',mode='wb',fileobj=stored,compresslevel=9,mtime=0) as encoded:
                shutil.copyfileobj(original,encoded,BLOCK)
        os.rename(temporary,target)
    count=0
    with source.open('rb') as original,gzip.open(target,'rb') as decoded:
        while True:
            block=original.read(BLOCK);other=decoded.read(BLOCK)
            assert block==other,'Encoded snapshot is not byte-exact: '+str(source)
            if not block:break
            count+=len(block)
    assert count==size and source.stat().st_size==size and sha(source)==before
    return {'logical_path':logical,'logical_bytes':size,'logical_sha256':before,
            'encoded_path':logical+'.gz','encoded_bytes':target.stat().st_size,'encoded_sha256':sha(target),
            'proof':{'byte_for_byte_original_comparison':True,'gzip_CRC_verified':True,'deterministic_mtime':0,'reused_verified_encoding':reused}}

def stage(root,directory):
    root=root.resolve();directory=directory.resolve()
    assert directory.is_relative_to(root/'_delivery'),'Storage writes are confined to CPC7/_delivery'
    files,excluded=select(root);states=[];encoded={}
    previous=directory/'LOGICAL_STATES_CPC7.json'
    if previous.exists():
        old=json.loads(previous.read_text(encoding='utf-8'))
        current={rel for _,rel in files}
        assert all(row['logical_path'] in current for row in old['states']),'Previously staged state disappeared from the scientific cut'
    for source,rel in files:
        if rel.startswith(('resultados/','checkpoints/')) and rel.endswith('.deetsnap'):
            target=directory/'encoded'/Path(rel+'.gz')
            row=encode_snapshot(source,target,rel);states.append(row);encoded[rel]=(target,rel+'.gz')
    report={'schema':'CPC7.logical-state-storage.v1','created_utc':datetime.now(timezone.utc).isoformat(),
            'states':states,'logical_bytes':sum(x['logical_bytes'] for x in states),
            'encoded_bytes':sum(x['encoded_bytes'] for x in states),
            'workspace_originals_untouched':True,'selection_exclusions':excluded}
    put(directory/'LOGICAL_STATES_CPC7.json',report)
    return report

def json_bytes(data):return (json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode('utf-8')

def build(root,candidate,storage,required,check_protected=True):
    started=time.monotonic();root=root.resolve();candidate=candidate.resolve();storage=storage.resolve()
    assert root.name=='CPC7' and candidate.name.endswith('.candidate.zip')
    if candidate.exists():raise FileExistsError(candidate)
    identities=engine(root);originals=protected(root) if check_protected else None
    files,exclusions=select(root)
    logical=stage(root,storage);state_map={x['logical_path']:x for x in logical['states']}
    mapped=[];cut=[]
    for source,rel in files:
        identity=sha(source);size=source.stat().st_size
        cut.append({'path':rel,'bytes':size,'sha256':identity})
        if rel in state_map:
            row=state_map[rel];assert identity==row['logical_sha256'] and size==row['logical_bytes']
            mapped.append((storage/'encoded'/Path(row['encoded_path']),row['encoded_path']))
        else:mapped.append((source,rel))
    payload={rel:{'source':source,'bytes':source.stat().st_size,'sha256':sha(source)} for source,rel in mapped}
    delivery_proofs=[]
    proofs=root/'_delivery/proofs'
    if proofs.exists():
        for path in sorted(proofs.rglob('*')):
            if not path.is_file():continue
            assert not path.is_symlink() and path.resolve().is_relative_to(proofs.resolve())
            assert path.suffix.lower() in {'.json','.jsonl','.log','.txt','.md'} and path.stat().st_size<=25*1024*1024
            rel='validation/packaging/'+path.relative_to(proofs).as_posix();safe_name(rel)
            assert rel not in payload
            payload[rel]={'source':path,'bytes':path.stat().st_size,'sha256':sha(path)}
            delivery_proofs.append({'source':path.relative_to(root).as_posix(),'payload_path':rel,'bytes':path.stat().st_size,'sha256':sha(path)})
    virtual={
      'LOGICAL_STATES_CPC7.json':json_bytes(logical),
      'SOURCE_CUT.json':json_bytes({'schema':'CPC7.source-cut.v1','files':cut,'delivery_proofs':delivery_proofs,'scope':'Exact unencoded workspace file identities before ZIP emission; no files are changed to obtain this cut.'}),
      'PACKAGING_SELECTION.json':json_bytes({'schema':'CPC7.selection.v1','allowed_directories':sorted(ALLOWED_DIRS),'forbidden_directories':sorted(FORBIDDEN_DIRS),'excluded':exclusions,'selected_logical_files':len(cut),'required_files':required})}
    for rel,data in virtual.items():
        assert rel not in payload;payload[rel]={'data':data,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    assert all(name in payload for name in required),'Missing required public runner/review file'
    rows=[{'path':key,'bytes':row['bytes'],'sha256':row['sha256']} for key,row in sorted(payload.items())]
    manifest=json_bytes({'schema':'CPC7.payload-manifest.v1','created_utc':datetime.now(timezone.utc).isoformat(),
      'root_in_zip':'CPC7/','paths_relative_to':'CPC7 package root','files':rows,'payload_bytes':sum(x['bytes'] for x in rows),
      'engine':identities,'protected_originals':originals,'required_files':required,
      'self_exclusions':['MANIFEST.json','HASHES.sha256'],'zip_sha256_intentionally_external':True})
    hashes=''.join(row['sha256']+'  '+row['path']+'\n' for row in rows)+hashlib.sha256(manifest).hexdigest()+'  MANIFEST.json\n'
    candidate.parent.mkdir(parents=True,exist_ok=True)
    temporary=candidate.with_name(candidate.name+'.pending.'+str(os.getpid()))
    with zipfile.ZipFile(temporary,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as z:
        for rel,row in sorted(payload.items()):
            if 'source' in row:
                source=row['source'];assert source.stat().st_size==row['bytes'] and sha(source)==row['sha256'],'Source changed during seal: '+rel
                z.write(source,'CPC7/'+rel)
                assert sha(source)==row['sha256'],'Source changed while being read: '+rel
            else:z.writestr('CPC7/'+rel,row['data'])
        z.writestr('CPC7/MANIFEST.json',manifest);z.writestr('CPC7/HASHES.sha256',hashes)
    os.rename(temporary,candidate)
    report=verify(candidate);report['build_seconds']=time.monotonic()-started
    put(storage/'BUILD_MANIFEST.json',json.loads(manifest));return report

def verify(candidate):
    started=time.monotonic()
    with zipfile.ZipFile(candidate) as z:
        names=z.namelist();assert len(names)==len(set(names))
        for name in names:
            safe_name(name);assert name.startswith('CPC7/')
            assert not any(x in FORBIDDEN_DIRS for x in PurePosixPath(name).parts)
            assert stat.S_IFMT(z.getinfo(name).external_attr>>16)!=stat.S_IFLNK
        assert z.testzip() is None,'ZIP CRC failure'
        manifest=json.loads(z.read('CPC7/MANIFEST.json'));assert manifest['schema']=='CPC7.payload-manifest.v1'
        assert manifest['root_in_zip']=='CPC7/' and manifest['paths_relative_to']=='CPC7 package root'
        rows=manifest['files'];assert len(rows)==len({row['path'] for row in rows})
        payload={row['path']:row for row in rows};hashes={}
        for line in z.read('CPC7/HASHES.sha256').decode('utf-8').splitlines():
            value,rel=line.split('  ',1);safe_name(rel);assert rel not in hashes and len(value)==64;hashes[rel]=value
        assert set(hashes)==set(payload)|{'MANIFEST.json'}
        assert set(names)=={'CPC7/'+rel for rel in hashes}|{'CPC7/HASHES.sha256'}
        expanded=Counter();compressed=Counter()
        for name in names:
            info=z.getinfo(name);rel=name.removeprefix('CPC7/');category=rel.split('/')[0]
            expanded[category]+=info.file_size;compressed[category]+=info.compress_size
            if rel in hashes:
                with z.open(name) as stream:assert stream_sha(stream)==hashes[rel],'Member SHA failure: '+name
                if rel in payload:assert payload[rel]['sha256']==hashes[rel] and payload[rel]['bytes']==info.file_size
        assert hashlib.sha256(z.read('CPC7/runtime/'+WHL)).hexdigest()==WHL_SHA
        with zipfile.ZipFile(io.BytesIO(z.read('CPC7/runtime/'+WHL))) as wheel:
            assert wheel.testzip() is None
            pyd=[name for name in wheel.namelist() if name.endswith('.pyd')]
            assert len(pyd)==1 and hashlib.sha256(wheel.read(pyd[0])).hexdigest()==PYD_SHA
        assert hashlib.sha256(z.read('CPC7/genealogia/kernel_v27.cpp')).hexdigest()==KERNEL_SHA
        assert all('CPC7/'+name in names for name in manifest['required_files'])
        logical=json.loads(z.read('CPC7/LOGICAL_STATES_CPC7.json'));assert logical['schema']=='CPC7.logical-state-storage.v1'
        states=logical['states'];assert len(states)==len({row['logical_path'] for row in states})
        encoded={name.removeprefix('CPC7/') for name in names if name.endswith('.deetsnap.gz')}
        assert encoded=={row['encoded_path'] for row in states},'Unmapped encoded states'
        for row in states:
            safe_name(row['logical_path']);safe_name(row['encoded_path'])
            assert row['logical_path'].startswith(('resultados/','checkpoints/')) and row['logical_path'].endswith('.deetsnap')
            assert row['encoded_path']==row['logical_path']+'.gz' and 'CPC7/'+row['logical_path'] not in names
            assert hashes[row['encoded_path']]==row['encoded_sha256'] and payload[row['encoded_path']]['bytes']==row['encoded_bytes']
            h=hashlib.sha256();size=0
            with z.open('CPC7/'+row['encoded_path']) as stream,gzip.GzipFile(fileobj=stream,mode='rb') as decoded:
                for block in iter(lambda:decoded.read(BLOCK),b''):h.update(block);size+=len(block)
            assert size==row['logical_bytes'] and h.hexdigest()==row['logical_sha256']
            assert row['proof']['byte_for_byte_original_comparison'] and row['proof']['gzip_CRC_verified']
        plain=[name for name in names if name.endswith('.deetsnap')]
        plain_bytes=sum(z.getinfo(name).file_size for name in plain)
        assert plain or states,'Missing physical/operative states'
    return {'schema':'CPC7.container-verification.v1','status':'VERIFIED','path':str(Path(candidate).resolve()),
       'sha256':sha(candidate),'bytes':Path(candidate).stat().st_size,'members':len(names),
       'manifest_hashes_verified':len(hashes),'crc_verified':True,'expanded_bytes':sum(expanded.values()),
       'expanded_bytes_by_category':dict(expanded),'compressed_bytes_by_category':dict(compressed),
       'encoded_snapshots':len(states),'plain_snapshots':len(plain),'logical_snapshot_bytes':logical['logical_bytes']+plain_bytes,
       'encoded_snapshot_bytes':logical['encoded_bytes'],'all_gzip_CRC_and_logical_SHA_verified':True,
       'engine':manifest['engine'],'verification_seconds':time.monotonic()-started}

def split(path,destination):
    size=path.stat().st_size
    if size<=20*1024*1024:return {'split_required':False,'threshold_compressed_bytes':20*1024*1024}
    metadata=destination/'transporte_CPC7'
    if metadata.exists():raise FileExistsError(metadata)
    for i in (1,2):
        if (destination/(NAME+f'.{i:03d}')).exists():raise FileExistsError(destination/(NAME+f'.{i:03d}'))
    metadata.mkdir();rows=[]
    with path.open('rb') as stream:
        for i,size_part in ((1,(size+1)//2),(2,size//2)):
            target=destination/(NAME+f'.{i:03d}');temporary=target.with_name(target.name+'.pending.'+str(os.getpid()))
            h=hashlib.sha256();left=size_part
            with temporary.open('xb') as out:
                while left:
                    block=stream.read(min(BLOCK,left));assert block;out.write(block);h.update(block);left-=len(block)
            os.rename(temporary,target);rows.append({'order':i,'name':target.name,'bytes':size_part,'sha256':h.hexdigest()})
        assert not stream.read(1)
    with tempfile.TemporaryFile(dir=metadata) as joined:
        for row in rows:
            with (destination/row['name']).open('rb') as stream:shutil.copyfileobj(stream,joined,BLOCK)
        assert joined.tell()==size;joined.seek(0);reconstructed=stream_sha(joined)
    assert reconstructed==sha(path)
    report={'schema':'CPC7.binary-parts.v1','zip_name':NAME,'zip_bytes':size,'zip_sha256':reconstructed,
            'parts_directory':'..','parts':rows,'reconstruction_tested':True,'reconstruction_sha256':reconstructed}
    put(metadata/'PARTES.json',report)
    shutil.copyfile(Path(__file__).with_name('reunir.py'),metadata/'REUNIR_CPC7.py')
    (metadata/'INSTRUCCIONES_PARTES.txt').write_text(
      'Las partes son segmentos binarios, no ZIP independientes. Conserve ambas junto al ZIP canónico.\n'
      'En esta carpeta transporte_CPC7 ejecute: py -3.13 REUNIR_CPC7.py\n'
      'El reunificador verifica cada parte y el resultado; no sobrescribe archivos existentes.\n'
      'El nombre predeterminado del resultado termina en _RECONSTRUIDO.zip.\n',encoding='utf-8')
    return report

def publish(root,candidate,destination,clean_report):
    report=verify(candidate);proof=json.loads(clean_report.read_text(encoding='utf-8'))
    assert proof['status']=='VERIFIED' and proof['candidate_sha256']==report['sha256']
    assert proof.get('posttrajectory_assertions') and all(row['status']=='COMPLETED' and row['exit_code']==0 for row in proof['commands'])
    with zipfile.ZipFile(candidate) as z:assert hashlib.sha256(z.read('CPC7/'+proof['plan_member'])).hexdigest()==proof['plan_sha256']
    originals=protected(root);target=destination/NAME
    if target.exists():raise FileExistsError('Never overwrite an existing CPC7 delivery: '+str(target))
    small={}
    with zipfile.ZipFile(candidate) as z:
        for member,label in [('revision/LEER_PRIMERO.md','CPC7_LEER_PRIMERO.md'),('revision/LECTURA_PROVISIONAL.md','CPC7_LECTURA_PROVISIONAL.md')]:
            if 'CPC7/'+member in z.namelist():
                path=destination/label
                if path.exists():raise FileExistsError(path)
                small[path]=z.read('CPC7/'+member)
    transport=split(candidate,destination)
    for path,data in small.items():
        with path.open('xb') as stream:stream.write(data)
    os.rename(candidate,target);assert sha(target)==report['sha256']
    assert protected(root)==originals
    return {'schema':'CPC7.publication.v1','canonical':str(target.resolve()),'published_utc':datetime.now(timezone.utc).isoformat(),
            **{key:value for key,value in report.items() if key!='path'},'transport':transport,
            'protected_originals':originals,'exact_candidate_clean_proof':proof}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=('inventory','stage','build','verify','publish','protected'))
    p.add_argument('--root',type=Path,default=ROOT);p.add_argument('--stage',type=Path)
    p.add_argument('--candidate',type=Path);p.add_argument('--destination',type=Path);p.add_argument('--clean-report',type=Path)
    p.add_argument('--required',nargs='*',default=['iniciar_cpc7.ps1','app/console.py','LEEME.md','revision/LEER_PRIMERO.md','revision/LECTURA_PROVISIONAL.md'])
    p.add_argument('--report',type=Path,required=True);a=p.parse_args();root=a.root.resolve()
    if a.action=='inventory':
        files,excluded=select(root);result={'schema':'CPC7.selection-inventory.v1','files':[{'path':rel,'bytes':path.stat().st_size} for path,rel in files],'excluded':excluded}
    elif a.action=='stage':result=stage(root,a.stage)
    elif a.action=='build':result=build(root,a.candidate,a.stage,a.required)
    elif a.action=='verify':result=verify(a.candidate)
    elif a.action=='protected':result=protected(root)
    else:result=publish(root,a.candidate,a.destination,a.clean_report)
    put(a.report,result);print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
