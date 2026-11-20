"""PI08 explicit-plan packager. Default read-only. No Native, DOCX authoring or cleanup.

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
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

HERE = Path(__file__).resolve().parent
P8 = HERE.parent
R = P8.parents[2]
W = P8.parents[4]
C = R/'DEE Cognitive 2.0'
LIMIT = 15_000_000
MANIFEST = '05_CONTROL/MANIFIESTO_SHA256.json'
sys.path.insert(0, str(HERE))
from auditoria_documental_PI08 import digest, pointer, safe_name


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
 value={'schema':'DEE.PI08.extraction_access_fence.v1','denied':denied,'DEE_or_app_imports':imports,'open_counts':counts,'jobs':results,'error':error,'new_Native_ticks':0,'no_original_source_access':not denied and not imports}
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
    p = raw if raw.is_absolute() else P8/raw
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


def validate_plan(plan):
    need(plan.get('schema') == 'DEE.PI08.final_package_plan.v1', 'Exact package plan schema required')
    need(plan.get('status') == 'CLOSED_ACTUAL_FILES_READY_TO_PACKAGE', 'A template/proposal cannot be sealed')
    need(plan.get('new_Native_ticks_by_packager') == 0, 'No material execution in packaging')
    gates = plan.get('gates', [])
    need({'scientific_closure','operational_writer_scope','literal_document_publication'} <= {g['name'] for g in gates},
         'Actual scientific, writer-scope and publication gates required')
    for gate in gates:
        p = source(gate['evidence'])
        obj = json.loads(p.read_text('utf-8-sig'))
        need(pointer(obj, gate['pointer']) == gate['expected'], 'Actual source gate failed: '+gate['name'])
    docs = plan.get('complete_documents', {})
    need(set(docs) == {'Manual','Compendium'}, 'Both complete current documents must travel literally')
    need(docs['Manual']['source'].endswith('DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx'),
         'Compatible complete current Cognitive Manual required')
    need(Path(docs['Manual']['source']).resolve() == (C/'DEE_Cognitive_2_0_Manual_Maestro_DCS11_MM_001_Edicion_1_21.docx').resolve(),
         'A staged/old Manual cannot replace the current original')
    need(plan.get('visual_QA_status') in ('VALIDATED_WITH_REAL_RENDER_WITNESS','NOT_VALIDATED_WITH_ACTUAL_LIMITATION'),
         'Visual status must be explicit, never inferred from OOXML')
    need(plan.get('portable_verifications'), 'At least the implemented primary documentary verifier is required')
    for protected in plan.get('protected_files', []):
        source(protected)


def create(a, plan):
    validate_plan(plan)
    items = {}
    names = set()
    f1_names={'04_EVIDENCIAS/F1_Q8/Q8_PARENT_BEFORE.deetsnap.gz','04_EVIDENCIAS/F1_Q8/Q8_IDENTITY_NO_FUTURE.deetsnap.gz','04_EVIDENCIAS/F1_Q8/Q8_BRANCH_AFTER.deetsnap.gz'}
    allow={v['file']:v for v in plan.get('small_F1_snapshots',[])}
    need(not allow or(len(allow)in(2,3)and set(allow)<=f1_names and {'04_EVIDENCIAS/F1_Q8/Q8_PARENT_BEFORE.deetsnap.gz','04_EVIDENCIAS/F1_Q8/Q8_BRANCH_AFTER.deetsnap.gz'}<=set(allow)), 'Only two/three explicitly indexed fixedq8F1 diagnostic snapshots')
    need(sum(v['bytes']for v in allow.values())<=9_000_000 and all(v['bytes']<=3_000_000 for v in allow.values()), 'F1small-snapshot evidence allowance exceeded; retain larger states locally')
    for entry in [*plan['members'], *plan['complete_documents'].values()]:
        name = str(safe_name(entry['file']))
        need(name != MANIFEST and name.casefold() not in names, 'Duplicate or reserved member')
        permitted_f1=name in allow
        need(PurePosixPath(name).suffix.lower() not in ('.zip','.sqlite','.sqlite3','.db','.pyd','.whl','.deetsnap','.gz') or permitted_f1,
             'Large state/runtime or nested archive must remain local with a locator; only explicit boundedq8F1exception')
        if permitted_f1:
            need(entry['bytes']==allow[name]['bytes'] and entry['sha256']==allow[name]['sha256'], 'F1 snapshot exception differs from exact content manifest')
            need(Path(entry['source']).resolve().is_relative_to((P8/'estados/F1_CUT_R03').resolve()), 'F1 snapshot exception cannot include principal or anotherstate')
        p = source(entry);data = p.read_bytes();validate(name,data)
        items[name] = {'source':str(p),'data':data,'role':entry.get('role','explicit evidence')}
        names.add(name.casefold())
    need('00_LEER_PRIMERO.txt' in items and any('INFORME_CIENTIFICO' in n for n in items),
         'Readable entry and single scientific report required')
    need('04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI08.json' in items, 'Portable exact primary index absent')
    if allow:
        need('04_EVIDENCIAS/F1_Q8/INDICE_F1_Q8_PI08_R03.json'in items and '05_RECALCULO/RECALCULAR_SNAPSHOTS_F1_PI08_R03.py'in items,
             'Explicit F1snapshot allowance requires its portable index and pure fullstate comparator')
        need(any(j['script']=='05_RECALCULO/RECALCULAR_SNAPSHOTS_F1_PI08_R03.py'for j in plan['portable_verifications']),
             'F1snapshot fullstate recalc must actually run under the final extraction fence')
    for job in plan['portable_verifications']:
        name = str(safe_name(job['script']))
        need(name in items and name.endswith('.py'), 'Portable script not included')
        safe_name(job['result_file'])
        need(isinstance(job.get('argv'),list) and all(isinstance(v,str) for v in job['argv']), 'Explicit portable CLI required')
    manifest = {'schema':'DEE.PI08.content_manifest.v1','created_at':datetime.datetime.now().astimezone().isoformat(),
        'content':[{'file':n,'bytes':len(v['data']),'sha256':digest(v['data']),
                    'source_reference_for_provenance_only':v['source'],'role':v['role']}for n,v in sorted(items.items())],
        'ZIP_hash_and_manifest_self_hash_excluded':True,'analysis_is_not_executable_full_backup':True}
    mb = (json.dumps(manifest,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    home=P8/'entrega';home.mkdir(exist_ok=True)
    name = str(safe_name(a.nombre))
    need(PurePosixPath(name).name == name and name.endswith('.zip'), 'One simple ZIP filename required')
    final=home/name;part=home/(name+'.writing')
    proof=P8/'control'/a.comprobante
    need(proof.name==a.comprobante and proof.suffix=='.json','Simple new proof filename required')
    need(not any(p.exists()for p in(final,part,proof)), 'Prior attempt/delivery exists; preserve it')
    with zipfile.ZipFile(part,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,v in sorted(items.items()):
            z.writestr(n,v['data'])
        z.writestr(MANIFEST,mb)
    need(part.stat().st_size<=LIMIT,'ZIP exceeds15,000,000bytes; candidate preserved, nothing truncated')
    stamp=datetime.datetime.now().strftime('%H%M%S');clean=W/('p8v'+stamp)
    need(not clean.exists(),'Fresh short extraction destination required')
    extraction=clean/'x';output=clean/'r';extraction.mkdir(parents=True);output.mkdir()
    with zipfile.ZipFile(part)as z:
        need(z.testzip()is None,'ZIP CRC failure')
        need(set(z.namelist())==set(items)|{MANIFEST},'ZIP content set mismatch')
        for n in z.namelist():
            rel=safe_name(n);target=extraction.joinpath(*rel.parts)
            need(target.resolve().is_relative_to(extraction.resolve()),'Extraction escape')
            data=z.read(n);target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb')as f:f.write(data)
            need(target.read_bytes()==data,'Extracted byte mismatch')
            validate(n,data)
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
            need(pointer(obj,path)==wanted,'Actual portable criterion failed:'+path)
        results.append({'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'schema':obj['schema']})
    for n,v in items.items():
        need(sha(v['source'])==digest(v['data']),'Original selected source changed while sealing')
    validate_plan(plan)
    need(not final.exists(),'Concurrent final delivery appeared');part.rename(final)
    result={'schema':'DEE.PI08.final_package_verification.v1','status':'SEALED_AND_CLEAN_EXTRACTION_VERIFIED',
        'zip':{'path':str(final),'bytes':final.stat().st_size,'sha256':sha(final)},'strict_limit_bytes':LIMIT,
        'content_members':len(items),'ZIP_members':len(items)+1,'manifest_sha256':digest(mb),
        'clean_extraction':str(extraction),'portable_outputs':results,'access_fence':av,
        'literal_complete_documents':{k:{'bytes':v['bytes'],'sha256':v['sha256'],'source':v['source']}for k,v in plan['complete_documents'].items()},
        'visual_QA_status':plan['visual_QA_status'],'new_Native_ticks':0,'DEE_imports':0,
        'staging_payload_materialized':False,'originals_modified':False,'cleanup_performed':False,
        'scope':'Literal explicit evidence, full CRC/manifest/clean-byte validation and documentary recalculation under a source/import fence. '
                'No Native replay, automatic adoption or inferred visual approval.'}
    with proof.open('x',encoding='utf-8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'proof':str(proof),'zip':result['zip'],'new_Native_ticks':0},ensure_ascii=False))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--plan',type=Path,default=P8/'fuentes/PLAN_ENTREGA_PI08_PLANTILLA.json')
    ap.add_argument('--crear-y-verificar',action='store_true')
    ap.add_argument('--nombre',default='DEE_PROGRESION_INTEGRADA_08_'+datetime.datetime.now().strftime('%Y_%m_%d')+'_ANALISIS.zip')
    ap.add_argument('--comprobante',default='VERIFICACION_ZIP_FINAL_PI08_R01.json')
    a=ap.parse_args();plan=json.loads(a.plan.read_text('utf-8-sig'))
    if not a.crear_y_verificar:
        print(json.dumps({'mode':'READ_ONLY_PLAN_NO_ZIP_NO_NATIVE','plan_status':plan.get('status'),
            'required_final_state':'CLOSED_ACTUAL_FILES_READY_TO_PACKAGE','strict_limit_bytes':LIMIT,
            'actual_members_listed':len(plan.get('members',[])),'complete_documents_listed':list(plan.get('complete_documents',{})),
            'no_staging_payload':True,'clean_extraction_and_access_fence_required':True,
            'files_written':0,'new_Native_ticks':0},ensure_ascii=False));return
    create(a,plan)


if __name__=='__main__':
    main()
