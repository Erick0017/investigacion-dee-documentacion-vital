"""PI09 explicit-plan packager. Default read-only. No Native, DOCX authoring or cleanup.

The final plan must name actual published files and frozen evidence. This helper
does not manufacture adoption, owner closure, experimental results or visual QA.
"""
from pathlib import Path, PurePosixPath
import argparse
import ast
import csv
import datetime
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
import zlib

HERE = Path(__file__).resolve().parent
P9 = HERE.parent
R = P9.parents[2]
W = P9.parents[4]
C = R/'DEE Cognitive 2.0'
LIMIT = 15_000_000
MANIFEST = '05_CONTROL/MANIFIESTO_SHA256.json'
sys.path.insert(0, str(HERE))
from auditoria_documental_PI09 import digest, pointer, safe_name


FENCE = r'''from pathlib import Path
import builtins, importlib.abc, json, os, runpy, sys, sysconfig, traceback
x=Path(sys.argv[1]).resolve(strict=True);out=Path(sys.argv[2]).resolve(strict=True)
jobs=json.loads(Path(sys.argv[3]).read_text('utf-8'));audit_file=Path(sys.argv[4]).resolve()
base=Path(sys.base_prefix).resolve();denied=[];imports=[];counts={};results=[]
def inside(p,r):
 try:p.relative_to(r);return True
 except ValueError:return False
def std(p):return inside(p,base)and 'site-packages'not in p.parts
def check(value,write=False):
 if isinstance(value,int):return
 p=Path(value).resolve()
 area='extraction'if inside(p,x)else'destination'if inside(p,out)else'stdlib'if std(p)else None
 if area is None or(write and area!='destination'):
  denied.append({'path':str(p),'write':write});raise PermissionError('Extraction fence denied '+str(p))
 counts[area]=counts.get(area,0)+1
class ImportFence(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  root=fullname.split('.')[0]
  if root in('dee_thinking','dee_universe_v27','app','capacidades','_native')or root.startswith('dee_kernel'):
   imports.append(fullname);raise ImportError('DEE/application import denied')
def hook(event,args):
 if event=='open':
  mode=args[1]if len(args)>1 else'r';flags=args[2]if len(args)>2 else 0
  writing=(isinstance(mode,str)and any(c in mode for c in'wa+x'))or(isinstance(flags,int)and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
  check(args[0],writing)
 elif event in('os.listdir','os.scandir')and args and args[0]is not None:check(args[0])
 elif event in('os.remove','os.rmdir','os.mkdir','os.rename','os.replace'):
  for value in args[:2]if event in('os.rename','os.replace')else args[:1]:check(value,True)
 elif event.startswith(('socket.','subprocess.','ctypes.dlopen','os.system','os.exec','os.spawn')):
  denied.append({'event':event});raise PermissionError('Process/network/native loading denied')
sys.meta_path.insert(0,ImportFence());sys.addaudithook(hook)
error=None
try:
 for job in jobs:
  script=x.joinpath(*Path(job['script']).parts);check(script)
  argv=[v.replace('{EXTRACTION}',str(x)).replace('{OUTPUT}',str(out))for v in job['argv']]
  sys.argv=[str(script),*argv]
  try:runpy.run_path(str(script),run_name='__main__')
  except SystemExit as e:
   if e.code not in(None,0):raise
  results.append({'script':job['script'],'successful_CLI_exit':True})
except BaseException as e:
 error={'type':type(e).__name__,'message':str(e),'traceback':traceback.format_exc()}
finally:
 value={'schema':'DEE.PI09.extraction_access_fence.v1','denied':denied,'DEE_or_app_imports':imports,'open_counts':counts,'jobs':results,'error':error,'new_Native_ticks':0,'no_original_source_access':not denied and not imports}
 audit_file.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if error is not None:raise SystemExit(2)
'''


def need(value, message):
    if not value:
        raise ValueError(message)


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(1024*1024), b''):
            h.update(part)
    return h.hexdigest()


def source(entry):
    raw = Path(entry['source'])
    p = raw if raw.is_absolute() else P9/raw
    p = p.absolute()
    need(p.is_relative_to(R), 'Source outside declared DEE root')
    for node in (p, *p.parents):
        st = node.lstat()
        need(not node.is_symlink() and not getattr(st, 'st_file_attributes', 0)&1024,
             'Reparse/link source rejected')
        if node == R:
            break
    p = p.resolve(strict=True)
    need(p.is_file() and p.stat().st_size == entry['bytes'] and sha(p) == entry['sha256'],
         'Exact source bytes/hash changed: '+str(p))
    return p


def validate(name, data):
    suffix = PurePosixPath(name).suffix.lower()
    if suffix == '.json':
        json.loads(data.decode('utf-8-sig'))
    elif suffix == '.jsonl':
        for line in data.decode('utf-8-sig').splitlines():
            if line.strip():
                json.loads(line)
    elif suffix == '.csv':
        list(csv.reader(io.StringIO(data.decode('utf-8-sig'))))
    elif suffix in ('.md', '.txt', '.py', '.ps1', '.cpp', '.hpp'):
        text = data.decode('utf-8-sig')
        if suffix == '.py':
            ast.parse(text)
    elif suffix == '.docx':
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            need(z.testzip() is None, 'DOCX CRC failure')
            need('word/document.xml' in z.namelist(), 'Incomplete DOCX')
            for n in z.namelist():
                if n.endswith('.xml'):
                    ET.fromstring(z.read(n))


def secret_guard(name, data):
    """Fail visibly on obvious credentials; never silently redact evidence."""
    if PurePosixPath(name).suffix.lower() not in ('.json','.jsonl','.txt','.md','.py','.ps1','.bat','.csv'):
        return
    text=data.decode('utf-8-sig')
    patterns=(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
              r'\bAKIA[0-9A-Z]{16}\b',r'\bghp_[A-Za-z0-9]{30,}\b')
    need(not any(re.search(p,text)for p in patterns),'Credential-shaped content requires Root review before packaging: '+name)


def plan_report(plan):
    total=compressed=0;missing=[];unbound=[]
    for entry in [*plan.get('members',[]),*plan.get('complete_documents',{}).values()]:
        raw=Path(entry['source']);p=raw if raw.is_absolute()else P9/raw
        if not p.is_file():missing.append(str(p));continue
        if not entry.get('sha256')or type(entry.get('bytes'))is not int:unbound.append(entry.get('file',str(p)));continue
        p=source(entry);blob=p.read_bytes();total+=len(blob);compressed+=len(zlib.compress(blob,9))+len(entry['file'].encode('utf8'))+100
    return {'mode':'READ_ONLY_PLAN_NO_ZIP_NO_NATIVE','plan_status':plan.get('status'),
            'strict_limit_bytes':LIMIT,'estimated_deflate_bytes_plus_headers':compressed,
            'uncompressed_bound_members_bytes':total,'estimate_is_not_final_ZIP_size':True,
            'missing_sources':missing,'unbound_source_hashes':unbound,
            'actual_members_listed':len(plan.get('members',[])),
            'complete_documents_listed':list(plan.get('complete_documents',{})),
            'portable_jobs':[j.get('id')for j in plan.get('portable_verifications',[])],
            'no_staging_payload':True,'clean_extraction_and_access_fence_required':True,
            'files_written':0,'new_Native_ticks':0}


def validate_plan(plan):
    need(plan.get('schema') == 'DEE.PI09.final_package_plan.v1', 'Exact package plan schema required')
    need(plan.get('status') == 'CLOSED_ACTUAL_FILES_READY_TO_PACKAGE', 'A template/proposal cannot be sealed')
    need(plan.get('new_Native_ticks_by_packager') == 0, 'No material execution in packaging')
    need(plan.get('privacy_review')=='ROOT_APPROVED_LOCAL_ANALYSIS_SELECTION', 'Root must approve explicit local analysis selection; no automatic privacy claim')
    gates = plan.get('gates', [])
    need({'scientific_closure','operational_writer_scope','literal_document_publication','D_execution_status'} <= {g['name'] for g in gates},
         'Actual scientific, writer-scope and publication gates required')
    for gate in gates:
        p = source(gate['evidence'])
        obj = json.loads(p.read_text('utf-8-sig'))
        actual=pointer(obj,gate['pointer'])
        need(type(actual) is type(gate['expected']) and actual==gate['expected'], 'Actual source gate failed: '+gate['name'])
    docs = plan.get('complete_documents', {})
    need(set(docs) == {'Manual','Compendium'}, 'Both complete current documents must travel literally')
    need(docs['Manual']['source'].endswith('DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'),
         'Compatible complete current Cognitive Manual required')
    need(Path(docs['Manual']['source']).resolve() == (C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx').resolve(),
         'A staged/old Manual cannot replace the current original')
    need(plan.get('visual_QA_status') in ('VALIDATED_WITH_REAL_RENDER_WITNESS','NOT_VALIDATED_WITH_ACTUAL_LIMITATION'),
         'Visual status must be explicit, never inferred from OOXML')
    need(plan.get('portable_verifications'), 'Implemented documentary verifiers required')
    need(plan.get('D_executed') in (True,False), 'Actual D execution status must be explicit')
    need(any(g['name']=='D_execution_status' and type(g['expected']) is bool and g['expected'] is plan['D_executed'] for g in gates),
         'Actual closure witness must bind whether D was executed, including false')
    need(plan.get('edition') and any(g['name']=='literal_document_publication' and g['expected']==plan['edition'] for g in gates), 'Actual publication gate must confirm edition')
    for protected in plan.get('protected_files', []):
        source(protected)


def create(a, plan):
    validate_plan(plan)
    items = {}
    names = set()
    for entry in [*plan['members'], *plan['complete_documents'].values()]:
        name = str(safe_name(entry['file']))
        need(name != MANIFEST and name.casefold() not in names, 'Duplicate or reserved member')
        need(PurePosixPath(name).suffix.lower() not in ('.zip','.sqlite','.sqlite3','.db','.pyd','.whl','.deetsnap','.gz','.exe','.dll','.pkl'),
             'Worlds, engines, nested archives and executable binaries stay local')
        need(Path(entry['source']).name not in ('VIDA.json','HISTORIA.jsonl','ESTADO_DISPOSITIVO.json','EXPORTACION_SERVICIO.json'),
             'Operational worlds and full state inventories stay local; include exact locators instead')
        p = source(entry);data = p.read_bytes();validate(name,data);secret_guard(name,data)
        items[name] = {'source':str(p),'data':data,'role':entry.get('role','explicit evidence')}
        names.add(name.casefold())
    selection_name='05_CONTROL/SELECCION_FUENTES_PI09.json'
    need(selection_name.casefold() not in names,'Selection declaration is included once automatically')
    selected=a.plan.resolve(strict=True)
    need(json.loads(selected.read_text('utf-8-sig'))==plan,'Selection changed during loading')
    items[selection_name]={'source':str(selected),'data':selected.read_bytes(),'role':'Literal Root-closed explicit source declaration'}
    need('00_LEER_PRIMERO.txt' in items and sum('INFORME_CIENTIFICO' in n for n in items)==1,
         'Readable entry and single scientific report required')
    need({'C1','AR'} <= {j.get('id') for j in plan['portable_verifications']}, 'Actual C1 and AR documentary recalculations required')
    if plan.get('D_executed') is True:
        need('D' in {j.get('id') for j in plan['portable_verifications']}, 'Executed D requires its actual documentary recalculation; prepared is not executed')
    for job in plan['portable_verifications']:
        name = str(safe_name(job['script']))
        need(name in items and name.endswith('.py'), 'Portable script not included')
        safe_name(job['result_file'])
        need(isinstance(job.get('argv'),list) and all(isinstance(v,str) for v in job['argv']), 'Explicit portable CLI required')
    manifest = {'schema':'DEE.PI09.content_manifest.v1','created_at':datetime.datetime.now().astimezone().isoformat(),
        'content':[{'file':n,'bytes':len(v['data']),'sha256':digest(v['data']),
                    'source_reference_for_provenance_only':v['source'],'role':v['role']}for n,v in sorted(items.items())],
        'ZIP_hash_and_manifest_self_hash_excluded':True,'analysis_is_not_executable_full_backup':True}
    mb = (json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    home=P9/'entrega';home.mkdir(exist_ok=True)
    name = str(safe_name(a.nombre))
    need(PurePosixPath(name).name == name and name.endswith('.zip'), 'One simple ZIP filename required')
    final=home/name;part=home/(name+'.writing')
    proof=P9/'control'/a.comprobante
    need(proof.name==a.comprobante and proof.suffix=='.json','Simple new proof filename required')
    need(not any(p.exists()for p in(final,part,proof)), 'Prior attempt/delivery exists; preserve it')
    with zipfile.ZipFile(part,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,v in sorted(items.items()):
            z.writestr(n,v['data'])
        z.writestr(MANIFEST,mb)
    need(part.stat().st_size<=LIMIT,'ZIP exceeds15,000,000bytes; candidate preserved, nothing truncated')
    stamp=datetime.datetime.now().strftime('%H%M%S');clean=W/('p9v'+stamp)
    need(not clean.exists(),'Fresh short extraction destination required')
    extraction=clean/'x';output=clean/'r';extraction.mkdir(parents=True);output.mkdir()
    with zipfile.ZipFile(part)as z:
        need(sum(i.file_size for i in z.infolist())<=plan.get('max_uncompressed_bytes',500000000),'Uncompressed analysis budget exceeded')
        need(z.testzip()is None,'ZIP CRC failure')
        need(set(z.namelist())==set(items)|{MANIFEST},'ZIP content set mismatch')
        for n in z.namelist():
            need(((z.getinfo(n).external_attr>>16)&0o170000)!=0o120000,'ZIP symlink rejected')
            rel=safe_name(n);target=extraction.joinpath(*rel.parts)
            need(target.resolve().is_relative_to(extraction.resolve()),'Extraction escape')
            data=z.read(n);target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb')as f:f.write(data)
            need(target.read_bytes()==data,'Extracted byte mismatch')
            validate(n,data)
    decoded_manifest=json.loads((extraction/MANIFEST).read_text('utf8'))
    for row in decoded_manifest['content']:
        pp=extraction.joinpath(*safe_name(row['file']).parts)
        need(pp.stat().st_size==row['bytes'] and sha(pp)==row['sha256'],'Clean member manifest mismatch')
    fence=clean/'FENCE.py';jobs=clean/'JOBS.json';audit=output/'AUDIT.json'
    fence.write_text(FENCE,encoding='utf-8');jobs.write_text(json.dumps(plan['portable_verifications']),encoding='utf-8')
    command=[sys.executable,'-I','-B','-X','utf8',str(fence),str(extraction),str(output),str(jobs),str(audit)]
    run=subprocess.run(command,cwd=extraction,capture_output=True,text=True,encoding='utf-8',errors='strict',timeout=600,
                       creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (clean/'stdout.txt').write_text(run.stdout,encoding='utf-8');(clean/'stderr.txt').write_text(run.stderr,encoding='utf-8')
    need(audit.is_file(),'Actual FENCE audit absent')
    av=json.loads(audit.read_text('utf-8'))
    need(run.returncode==0 and not av['denied']and not av['DEE_or_app_imports']and av['error']is None,
         'Clean-extraction documentary verification failed; preserve evidence')
    results=[]
    for job in plan['portable_verifications']:
        p=output.joinpath(*safe_name(job['result_file']).parts);need(p.is_file(),'Portable result not produced')
        obj=json.loads(p.read_text('utf-8-sig'))
        need(obj.get('schema')==job['result_schema'],'Actual portable result schema differs')
        for path,wanted in job['expect'].items():
            actual=pointer(obj,path)
            need(type(actual) is type(wanted) and actual==wanted,'Actual portable criterion failed:'+path)
        if job.get('expected_result_file'):
            original_result=extraction.joinpath(*safe_name(job['expected_result_file']).parts)
            baseline=json.loads(original_result.read_text('utf-8-sig'))
            need(json.dumps(obj,sort_keys=True,separators=(',',':'))==json.dumps(baseline,sort_keys=True,separators=(',',':')),
                 'Fresh extraction recalculation differs from the included closed documentary result')
        results.append({'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'schema':obj['schema']})
    for n,v in items.items():
        need(sha(v['source'])==digest(v['data']),'Original selected source changed while sealing')
    validate_plan(plan)
    need(not final.exists(),'Concurrent final delivery appeared');part.rename(final)
    result={'schema':'DEE.PI09.final_package_verification.v1','status':'SEALED_AND_CLEAN_EXTRACTION_VERIFIED',
        'zip':{'path':str(final),'bytes':final.stat().st_size,'sha256':sha(final)},'strict_limit_bytes':LIMIT,
        'content_members':len(items),'ZIP_members':len(items)+1,'manifest_sha256':digest(mb),
        'clean_extraction':str(extraction),'portable_outputs':results,'access_fence':av,
        'literal_complete_documents':{k:{'bytes':v['bytes'],'sha256':v['sha256'],'source':v['source']}for k,v in plan['complete_documents'].items()},
        'visual_QA_status':plan['visual_QA_status'],'new_Native_ticks':0,'DEE_imports':0,
        'staging_payload_materialized':False,'originals_modified':False,'cleanup_performed':False,
        'D_executed':plan['D_executed'],'Native_reproduction_scope':'Only existing separately cited local Native witnesses; ZIP jobs are documentary recalculation.',
        'scope':'Literal explicit evidence, full CRC/manifest/clean-byte validation and documentary recalculation under a source/import fence. '
                'No Native replay, automatic adoption or inferred visual approval.'}
    with proof.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(proof),'zip':result['zip'],'new_Native_ticks':0},ensure_ascii=False))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan',type=Path,default=P9/'codigo/PLAN_ENTREGA_PI09_PLANTILLA.json')
    ap.add_argument('--crear-y-verificar',action='store_true')
    ap.add_argument('--nombre',default='DEE_PROGRESION_INTEGRADA_08_'+datetime.datetime.now().strftime('%Y_%m_%d')+'_ANALISIS.zip')
    ap.add_argument('--comprobante',default='VERIFICACION_ZIP_FINAL_PI09_R01.json')
    a=ap.parse_args();plan=json.loads(a.plan.read_text('utf-8-sig'))
    if not a.crear_y_verificar:
        print(json.dumps(plan_report(plan),ensure_ascii=False));return
    create(a,plan)


if __name__=='__main__':
    main()
