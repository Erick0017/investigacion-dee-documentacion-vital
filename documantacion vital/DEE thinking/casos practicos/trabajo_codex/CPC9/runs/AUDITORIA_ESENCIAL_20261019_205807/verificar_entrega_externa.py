"""Extract and audit the exact new ZIP; optionally publish identical verified bytes.

Never imports the scientific engine or executes the historical campaign.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
import argparse, hashlib, json, os, shutil, subprocess, sys, time, zipfile

sys.stdout.reconfigure(encoding='utf8')

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def dump(path, value):
    with path.open('x',encoding='utf8') as f:
        json.dump(value,f,ensure_ascii=False,indent=2); f.write('\n')

def originals(folder):
    index=folder/'HASHES_ENTREGA.sha256'; result=[]
    for line in index.read_text(encoding='utf-8-sig').splitlines():
        if not line.strip() or line.startswith('#'):continue
        expected,name=line.split(None,1);name=name.strip().lstrip('*')
        target=(folder/name).resolve(strict=True)
        if not target.is_relative_to(folder.resolve()):raise ValueError('Unsafe old index path')
        actual=digest(target)
        if actual!=expected:raise ValueError('Original changed: '+name)
        result.append({'name':name,'sha256':actual,'bytes':target.stat().st_size})
    return {'index_sha256':digest(index),'files_checked':len(result),'entries':result}

def main():
    p=argparse.ArgumentParser();p.add_argument('--zip',type=Path,required=True);p.add_argument('--work',type=Path,required=True);p.add_argument('--original-output',type=Path,required=True);p.add_argument('--publish',action='store_true');a=p.parse_args();began=time.monotonic()
    candidate=a.zip.resolve(strict=True);work=a.work.resolve();source_output=a.original_output.resolve(strict=True)
    if work.exists():raise FileExistsError('Use a fresh independent extraction directory')
    work.mkdir(parents=True);before=originals(source_output);zip_sha=digest(candidate);expanded=0;count=0
    with zipfile.ZipFile(candidate) as z:
        if z.testzip():raise ValueError('ZIP CRC check failed')
        seen=set()
        for entry in z.infolist():
            name=PurePosixPath(entry.filename)
            if name.is_absolute() or '..'in name.parts or '\\'in entry.filename or ':'in entry.filename:raise ValueError('Unsafe ZIP path')
            if entry.filename in seen:raise ValueError('Duplicate ZIP path')
            seen.add(entry.filename)
            if entry.is_dir():continue
            target=work.joinpath(*name.parts)
            if not target.resolve().is_relative_to(work):raise ValueError('Extraction escapes work directory')
            target.parent.mkdir(parents=True,exist_ok=True)
            with z.open(entry)as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
            expanded+=entry.file_size;count+=1
    root=work/'CPC9_AUDITORIA_CIENTIFICA_ESENCIAL';tool=root/'CONFIGURACIONES_Y_REPRODUCCION/verificar_paquete.py'
    command=[sys.executable,'-I','-B',str(tool),'--root',str(root),'--out',str(work/'verificacion')]
    started=time.monotonic();run=subprocess.run(command,cwd=work,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=1500)
    (work/'verificacion.stdout.log').write_bytes(run.stdout);(work/'verificacion.stderr.log').write_bytes(run.stderr)
    if run.returncode:raise RuntimeError('Clean validation failed: '+run.stderr.decode('utf8',errors='replace')[-5000:])
    clean=json.loads((work/'verificacion/VERIFICACION_PAQUETE.json').read_bytes())
    if clean['status']!='PASS' or clean['engine_imported'] or clean['new_native_campaign_runs']!=0:raise ValueError('Invalid clean receipt')
    if digest(candidate)!=zip_sha:raise ValueError('Candidate changed during clean verification')
    after=originals(source_output)
    if before!=after:raise ValueError('Original deliverables changed')
    proof=json.loads((root/'EVIDENCIA_PRIMARIA_ESENCIAL/COMPARACION_DIRECTA_ORIGINALES.json').read_bytes())
    if proof['status']!='PASS' or proof['source_JSON_aliases_byte_and_value_verified']!=1188:raise ValueError('Missing original comparison proof')
    destination=source_output/'CPC9_AUDITORIA_CIENTIFICA_ESENCIAL.zip'
    if a.publish:
        if destination.exists():raise FileExistsError('Existing audit delivery is protected')
        temporary=source_output/'CPC9_AUDITORIA_CIENTIFICA_ESENCIAL.zip.nuevo_verificado'
        if temporary.exists():raise FileExistsError('Existing staging artifact is protected')
        with candidate.open('rb')as src,temporary.open('xb')as dst:
            shutil.copyfileobj(src,dst);dst.flush();os.fsync(dst.fileno())
        if digest(temporary)!=zip_sha:raise ValueError('Copy differs from verified bytes')
        os.replace(temporary,destination)
        with zipfile.ZipFile(destination)as z:
            if z.testzip():raise ValueError('Published ZIP CRC failure')
        if digest(destination)!=zip_sha:raise ValueError('Published identity mismatch')
    receipt={'schema':'CPC9.essential.exact_ZIP_external_validation.v1','status':'PASS','verified_utc':datetime.now(timezone.utc).isoformat(),
       'published':bool(a.publish),'zip':{'path':str(destination if a.publish else candidate),'sha256':zip_sha,'compressed_bytes':candidate.stat().st_size,'expanded_bytes':expanded,'files':count,'CRC_check':'PASS'},
       'command':command,'clean_verification_seconds':time.monotonic()-started,'clean_verification':clean,'direct_original_comparison':{'status':proof['status'],'JSON_aliases':1188,'physical_states':13,'historical_text_witnesses':91,'proof_sha256':digest(root/'EVIDENCIA_PRIMARIA_ESENCIAL/COMPARACION_DIRECTA_ORIGINALES.json')},
       'original_delivery_index_unchanged':after,'new_native_campaign_runs':0,'engine_imported':False,'independent_extraction_directory':str(work),'elapsed_seconds':time.monotonic()-began,
       'scope':'Original-value fidelity, integrity and recalculation audit. Not a new native scientific replication. No historical deliverable was modified.',
       'exclusively_in_originals':['Official engine, WHL/PYD and native C++ source','Complete operational snapshots, queues/channels and unselected intermediate states','Unselected historical corpus and code variants','Original lexical formatting/member order of normalized JSON']}
    dump(work/'VERIFICACION_ENTREGA.json',receipt)
    if a.publish:dump(source_output/'CPC9_AUDITORIA_CIENTIFICA_ESENCIAL_VERIFICACION.json',receipt)
    print(json.dumps({'status':'PASS','published':bool(a.publish),'sha256':zip_sha,'bytes':candidate.stat().st_size,'files':count,'elapsed_seconds':receipt['elapsed_seconds']},ensure_ascii=False))

if __name__=='__main__':main()
