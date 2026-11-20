"""Solid lossless research-data packaging, not another simulation.

Original JSON bytes are preserved. gzip trace containers are replaced by
their byte-exact decompressed JSONL payloads with both hashes indexed. Native
operational snapshots and the engine are intentionally outside this analysis.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,sys,json,hashlib,io,gzip,tarfile,lzma,time
p=argparse.ArgumentParser();p.add_argument('--system',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--case',required=True);a=p.parse_args();sys.path.insert(0,str(a.system))
from app.process_control import protect_current
protect_current(output=a.out/'RECURSOS.json');a.out.mkdir(parents=True,exist_ok=False);root=a.out.parent.parent;start=time.perf_counter();items=[];seen=set()
def add(path,name,transform='EXACT_ORIGINAL_BYTES'):
    if path in seen:return
    seen.add(path);items.append((path,name,transform))
for path in sorted(root.glob('*/*/PRIMARIOS.json')):add(path,'primarios/'+path.relative_to(root).as_posix())
primary_count=len(items)
for path in sorted(root.rglob('*.jsonl.gz')):
    if a.out in path.parents:continue
    add(path,'campos/'+path.relative_to(root).as_posix()[:-3],'EXACT_GZIP_DECOMPRESSED_PAYLOAD_ORIGINAL_CONTAINER_RETAINED_LOCALLY')
for pattern in('*/EJECUCION.json','*/FUENTES_EJECUTADAS.json','*/PREFLIGHT_SINTAXIS.json','*/*.stdout.log','*/*.stderr.log','*/*/CLI_*.stdout.json','*/*/CLI_*.stderr.log','*/*/RECURSOS.json','ARRANQUE_01/*.json'):
    for path in sorted(root.glob(pattern)):
        if a.out in path.parents:continue
        add(path,'ejecuciones/'+path.relative_to(root).as_posix())
archive=a.out/'REGISTROS_COMPLETOS.tar.xz';index=[]
with lzma.open(archive,'wb',preset=8,check=lzma.CHECK_CRC64)as compressed:
    with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.PAX_FORMAT)as tf:
        for path,name,transform in items:
            original=path.read_bytes();payload=gzip.decompress(original)if transform!='EXACT_ORIGINAL_BYTES'else original;h=hashlib.sha256(payload).hexdigest();info=tarfile.TarInfo(name);info.size=len(payload);info.mtime=0;info.uid=0;info.gid=0;info.mode=0o644;tf.addfile(info,io.BytesIO(payload));index.append({'member':name,'payload_bytes':len(payload),'payload_sha256':h,'source_path':str(path),'source_relative':path.relative_to(root).as_posix(),'source_bytes':len(original),'source_sha256':hashlib.sha256(original).hexdigest(),'source_mtime_ns':path.stat().st_mtime_ns,'transform':transform})
lookup={r['member']:r for r in index};verified=[]
with tarfile.open(archive,'r|xz')as tf:
    for member in tf:
        if not member.isfile()or member.name not in lookup:raise AssertionError('Unexpected archive member')
        b=tf.extractfile(member).read();r=lookup[member.name]
        if len(b)!=r['payload_bytes']or hashlib.sha256(b).hexdigest()!=r['payload_sha256']:raise AssertionError('Lossless archive reconstruction mismatch')
        verified.append(member.name)
if len(verified)!=len(index):raise AssertionError('Missing scientific member')
record={'schema':'PC01.lossless.data_archive.v1','created_utc':datetime.now(timezone.utc).isoformat(),'archive':archive.name,'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'primary_cases':primary_count,'members':index,'verified_all_members':True,'verified_members':len(verified),'payload_expanded_bytes':sum(r['payload_bytes']for r in index),'source_stored_bytes':sum(r['source_bytes']for r in index),'seconds':time.perf_counter()-start,'no_engine_or_operational_backup':True,'gzip_container_metadata_not_carried_as_original_bytes':True,'all_selected_scientific_payload_bytes_preserved':True,'budget_not_restarted':True};(a.out/'INDICE_REGISTROS.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:record[k]for k in('archive_bytes','primary_cases','verified_members','payload_expanded_bytes','seconds')}))
