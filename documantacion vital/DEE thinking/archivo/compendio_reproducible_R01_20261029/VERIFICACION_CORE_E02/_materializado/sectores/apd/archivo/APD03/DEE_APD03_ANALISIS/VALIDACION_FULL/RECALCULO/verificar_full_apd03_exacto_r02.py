"""Exact archive extraction and APD03 UI proof; private and explicitly gated.

No upload, original installation, original life, updater or Source-S import.
Every executed helper/interpreter is inside the exact extracted archive.
"""
import argparse
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path,PurePosixPath
import shutil
import stat
import subprocess
import sys
import time
import zipfile

WHL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def write(p,v):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    with Path(p).open('x',encoding='utf8',newline='\n')as f:json.dump(v,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def archive_inventory(z):
    seen=set();files=[]
    for item in z.infolist():
        p=PurePosixPath(item.filename)
        raw_name=getattr(item,'orig_filename',item.filename)
        if raw_name!=item.filename or p.is_absolute()or'..'in p.parts or'\\'in raw_name or':'in item.filename or not p.parts or p.parts[0]!='cognitive sistem':raise ValueError('Unsafe/noncanonical archive member')
        if stat.S_ISLNK(item.external_attr>>16):raise ValueError('Archive symbolic link forbidden')
        key=item.filename.rstrip('/').casefold()
        if key in seen:raise ValueError('Repeated case-insensitive archive member')
        seen.add(key)
        if not item.is_dir():files.append(item.filename)
    return files
def validate_manifest(root):
    manifest=read(root/'actualizaciones/ARCHIVOS_GESTIONADOS.json');verified=[]
    for name,row in manifest['members'].items():
        p=PurePosixPath(name)
        if p.is_absolute()or'..'in p.parts or'\\'in name or':'in name:raise ValueError('Unsafe managed member')
        path=(root/Path(*p.parts)).resolve(strict=True)
        if not path.is_relative_to(root)or path.is_symlink()or not path.is_file():raise ValueError('Managed member outside exact extraction')
        if path.stat().st_size!=row['bytes']or sha(path)!=row['sha256']:raise ValueError('Managed bytes/hash mismatch:'+name)
        verified.append(name)
    return {'members_verified':len(verified),'manifest_sha256':sha(root/'actualizaciones/ARCHIVOS_GESTIONADOS.json'),'release':manifest.get('release'),'source_campaign':manifest.get('source_campaign')}
def inner_argv(root,protocol_copy,folder):
    root=Path(root).resolve()
    return [str(root/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(root/'actualizaciones/probar_full_apd03_entrada.py'),'--raiz',str(root),'--protocolo',str(Path(protocol_copy).resolve()),'--salida',str(Path(folder).resolve()),'--ejecutar-native']
def runtime_probe_argv(root):
    code="import sys,struct,json,importlib.metadata,dee_thinking,dee_thinking._native as d; print(json.dumps({'python':sys.version,'pointer_bytes':struct.calcsize('P'),'version':importlib.metadata.version('dee-thinking'),'module':dee_thinking.__file__,'pyd':d.__file__,'loaded_files':sorted({str(m.__file__)for m in list(sys.modules.values())if isinstance(getattr(m,'__file__',None),str)and not m.__file__.startswith('<')}),'runtime_created':False}))"
    return [str(Path(root).resolve()/'motor/python313/python.exe'),'-I','-B','-X','utf8','-c',code]
def bootstrap_argv():
    return ['cmd.exe','/d','/c','INICIAR.bat','usar','--help']
def bootstrap(root):
    """Use the shipped first-start path, not another installation or policy."""
    personal=root/'trabajo_personal'
    def personal_files():
        return [{'file':p.relative_to(personal).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(personal.rglob('*'))if p.is_file()]
    before=personal_files()
    if any(r['file'].endswith('VIDA.json')or r['file'].startswith(('estado/checkpoints/','entrada_sencilla/vidas/'))for r in before):raise ValueError('First-start extraction already contains a personal life or Native operational cut')
    marker=root/'motor/python313/site-packages/INSTALACION_DEE.json'
    marker_before=marker.exists();command=bootstrap_argv();started=time.monotonic()
    operation=subprocess.run(command,cwd=root,text=True,encoding='utf8',capture_output=True,timeout=60)
    after=personal_files()
    evidence={'argv':command,'cwd':str(root),'exit_code':operation.returncode,'stdout':operation.stdout,'stderr':operation.stderr,'wall_seconds':time.monotonic()-started,'personal_files_before':before,'personal_files_after':after,'no_VIDA_or_native_cut_before':True,'no_personal_files_created_or_changed':before==after,'marker_before':marker_before,'new_native_execution':False,'scope':'N0 first-start installation through the shipped bat/launcher help. No UI owner or Native Runtime requested; unchanged personal files and no life/cut attest this boundary. Importing the official extension afterwards is not evolving a world.'}
    if marker.is_file():evidence['marker']={'file':marker.relative_to(root).as_posix(),'bytes':marker.stat().st_size,'sha256':sha(marker),'content':read(marker)}
    if operation.returncode or '--nueva'not in operation.stdout or '--vida'not in operation.stdout or before!=after or not marker.is_file()or read(marker).get('wheel_sha256')!=WHL_SHA:raise RuntimeError('Shipped first-start help failed its no-life/import-preparation boundary: '+json.dumps(evidence,ensure_ascii=False))
    return evidence
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--zip',type=Path,required=True);p.add_argument('--zip-sha256',required=True);p.add_argument('--destino',type=Path,required=True);p.add_argument('--protocolo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);p.add_argument('--ejecutar-native',action='store_true');a=p.parse_args()
    if not a.ejecutar_native:raise SystemExit('Root GO required; no archive execution by default')
    total_started=time.monotonic()
    source=a.zip.resolve(strict=True);dest=a.destino.resolve();proto_path=a.protocolo.resolve(strict=True);protocol=read(proto_path)
    if protocol.get('status')!='CLOSED_FOR_EXACT_FULL_PROOF':raise ValueError('Prospective protocol not Root-closed')
    if sha(source)!=a.zip_sha256:raise ValueError('Not the exact Root-approved archive')
    if dest.exists():raise FileExistsError('Existing extraction/personal results preserved; no automatic reuse')
    if len(str(dest))>120:raise ValueError('Choose a short, new, workspace-owned extraction directory')
    report={'schema':'APD03.exact_full.external_verification.R02','zip':str(source),'zip_sha256':a.zip_sha256,'zip_bytes':source.stat().st_size,'protocol_sha256':sha(proto_path),'same_computer_not_independent_hardware':True,'original_archive_not_modified':True,'new_native_execution_not_archived_recalculation':True,'native_execution_started':False,'intent_scope':'The Native flag authorizes an intended proof; native_execution_started remains false until the supervised proof helper is actually spawned. A first-start/import failure does not constitute a Native experiment.'}
    dest.mkdir(parents=True,exist_ok=False)
    try:
        with zipfile.ZipFile(source)as z:
            files=archive_inventory(z);bad=z.testzip()
            if bad:raise ValueError('ZIP CRC failure:'+bad)
            z.extractall(dest);report['zip_members']=len(files);report['CRC']='all_members_checked'
        root=(dest/'cognitive sistem').resolve(strict=True);report['extracted_root']=str(root);report['managed_manifest']=validate_manifest(root)
        python=root/'motor/python313/python.exe';entry=root/'sistema/app/usar_dee.py';helper=root/'actualizaciones/probar_full_apd03_entrada.py';wheel=root/'motor/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
        if not all(p.is_file()for p in(python,entry,helper,wheel))or sha(wheel)!=WHL_SHA:raise ValueError('Required exact operational files/motor absent')
        if any(not p.resolve().is_relative_to(root)for p in(python,entry,helper)):raise ValueError('Executable escapes exact extraction')
        report['durations_monotonic']={'preflight_zip_hash_crc_extract_manifest_seconds':time.monotonic()-total_started}
        report['first_start_N0']=bootstrap(root)
        report['durations_monotonic']['first_start_N0_seconds']=report['first_start_N0']['wall_seconds']
        import_started=time.monotonic()
        probe_argv=runtime_probe_argv(root);probe=subprocess.run(probe_argv,cwd=python.parent,text=True,encoding='utf8',capture_output=True,timeout=60)
        report['durations_monotonic']['included_import_probe_seconds']=time.monotonic()-import_started
        if probe.returncode:raise RuntimeError('Included runtime import failed: '+probe.stderr)
        identity=json.loads(probe.stdout)
        if identity['pointer_bytes']!=8 or identity['version']!='4.5.0'or not identity['python'].startswith('3.13.')or not Path(identity['module']).resolve().is_relative_to(root/'motor')or not Path(identity['pyd']).resolve().is_relative_to(root/'motor')or sha(identity['pyd'])!=PYD_SHA:raise ValueError('Included engine/platform identity differs')
        if any(not Path(path).resolve().is_relative_to(root)for path in identity['loaded_files']):raise ValueError('Probe imported a Python source/library outside the exact extraction')
        report['included_runtime_import']={'argv':probe_argv,'identity':identity,'pyd_sha256':sha(identity['pyd']),'new_native_ticks':0,'Runtime_created':False}
        folder=root/'trabajo_personal/resultados'/protocol['personal_life'];protocol_copy=root/'trabajo_personal'/('PROTOCOLO_FULL_'+protocol['personal_life']+'.json')
        if protocol_copy.exists():raise FileExistsError('Existing protocol is never overwritten')
        shutil.copyfile(proto_path,protocol_copy)
        command=inner_argv(root,protocol_copy,folder)
        pc=load('exact_archive_owned_job',root/'sistema/app/process_control.py');start=time.monotonic()
        with(dest/'PROOF_STDOUT.txt').open('xb')as stdout,(dest/'PROOF_STDERR.txt').open('xb')as stderr:
            proc,job,name=pc.spawn_owned(command,cwd=python.parent,stdout=stdout,stderr=stderr,memory_limit=protocol['proof_tree_memory_limit_bytes'])
            report['native_execution_started']=True
            try:
                proc.wait(timeout=3*protocol['session_wall_limit_seconds']+120);resources=pc.job_resources(job);deadline=time.monotonic()+5
                while resources.get('job_active_processes')and time.monotonic()<deadline:time.sleep(.02);resources=pc.job_resources(job)
                if resources.get('job_active_processes'):raise RuntimeError('Own proof job not closed')
            finally:pc.close_job(job)
        report['execution']={'argv':command,'pid':proc.pid,'exit_code':proc.returncode,'wall_seconds':time.monotonic()-start,'resources':resources,'resource_scope':'Outer proof helper, UI, managers and Native descendants in one1GiB total tree; nested512MiB Native-worker scope is not added to the outer total. Actual job peaks are measured.','included_helper_sha256':sha(helper),'included_entry_sha256':sha(entry),'included_python':str(python)}
        if(folder/'RESULTADOS_FULL_APD03.json').is_file():report['native_proof']=read(folder/'RESULTADOS_FULL_APD03.json')
        report['managed_manifest_after']=validate_manifest(root)
        if report['managed_manifest_after']!=report['managed_manifest']:raise ValueError('Managed package sources changed during personal execution')
        if sha(source)!=a.zip_sha256:raise ValueError('The approved archive changed during proof')
        report['zip_still_exact']=True;report['finished_utc']=datetime.now(timezone.utc).isoformat()
        if proc.returncode:raise RuntimeError('Exact Full proof failed, preserved without repeat')
        if report['native_proof']['issues']:raise RuntimeError('Functional limits recorded in the proof')
    except BaseException as error:
        report['error']={'type':type(error).__name__,'detail':str(error),'no_retry_no_new_life':True};raise
    finally:
        report.setdefault('durations_monotonic',{})['total_external_proof_seconds']=time.monotonic()-total_started
        report['durations_monotonic']['scope']='Preflight/hash/extraction and first-start are host distribution costs, not cognitive latency. execution.wall_seconds separately covers the supervised helper and three sequential owner sessions.'
        write(a.salida,report)
    print(json.dumps({'zip_sha256':report['zip_sha256'],'zip_bytes':report['zip_bytes'],'same_computer':True,'extracted':str(dest),'exit_code':report['execution']['exit_code']}))
if __name__=='__main__':main()
