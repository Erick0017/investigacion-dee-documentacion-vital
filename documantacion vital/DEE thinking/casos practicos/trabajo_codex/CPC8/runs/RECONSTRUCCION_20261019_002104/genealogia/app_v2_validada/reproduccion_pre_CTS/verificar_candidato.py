"""Read-only candidate validation; all logs/states/reports are external.

Example: python -I -B reproduccion/verificar_candidato.py --python PY313
--out NEW_EXTERNAL_DIRECTORY --artifact THE_EXACT_CLOSED_CANDIDATE.zip
Without --artifact the result can only be DEVELOPMENT, never publicationPASS.
No environment installation or ZIP construction is performed here.
"""
import argparse,hashlib,json,os,subprocess,sys,time,traceback,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def put(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def manifest_check(artifact):
 p=ROOT/'MANIFEST.json'
 if not p.is_file():
  if artifact:raise ValueError('A final artifact requires the extracted MANIFEST.json')
  return{'status':'NOT_SEALED_DEVELOPMENT','passed':True,'publication_valid':False}
 m=json.loads(p.read_text(encoding='utf8'));rows=m['files'];expected={r['path']for r in rows}|{'MANIFEST.json','HASHES.sha256'};actual={x.relative_to(ROOT).as_posix()for x in ROOT.rglob('*')if x.is_file()}
 if expected!=actual:raise ValueError('Candidate extracted inventory differs from its manifest')
 for row in rows:
  rel=PurePosixPath(row['path'])
  if rel.is_absolute()or '..'in rel.parts or '\\'in row['path']or ':'in row['path']:raise ValueError('Unsafe manifest path')
  f=ROOT/row['path']
  if f.stat().st_size!=row['bytes']or sha(f)!=row['sha256']:raise ValueError('Manifest mismatch: '+row['path'])
 hashes={}
 for line in(ROOT/'HASHES.sha256').read_text(encoding='utf8').splitlines():
  digest,name=line.split('  ',1)
  if name in hashes:raise ValueError('Duplicate HASHES entry')
  hashes[name]=digest
 if set(hashes)!=expected-{'HASHES.sha256'}:raise ValueError('HASHES scope differs')
 if any(sha(ROOT/name)!=digest for name,digest in hashes.items()):raise ValueError('HASHES mismatch')
 result={'status':'EXTRACTED_MANIFEST_PASS','passed':True,'manifest_sha256':sha(p),'payload_files':len(rows),'expanded_bytes':sum(r['bytes']for r in rows)}
 if artifact:
  with zipfile.ZipFile(artifact)as z:
   names=z.namelist()
   if len(names)!=len(set(names))or len(names)!=len(set(x.casefold()for x in names)):raise ValueError('Duplicate ZIP members')
   if set(names)!={'CPC8/'+x for x in expected}:raise ValueError('Artifact/extracted inventory differs')
   if z.testzip()is not None:raise ValueError('Artifact CRC failure')
   if hashlib.sha256(z.read('CPC8/MANIFEST.json')).hexdigest()!=result['manifest_sha256']:raise ValueError('Artifact/extracted manifest differs')
   for name,digest in hashes.items():
    h=hashlib.sha256()
    with z.open('CPC8/'+name)as f:
     for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    if h.hexdigest()!=digest:raise ValueError('Artifact member hash differs: '+name)
  result['closed_artifact_crc_and_hashes']=True
 return result
def critical_hashes():
 paths=list((ROOT/'src').rglob('*.py'))+list((ROOT/'app').rglob('*.py'))+list((ROOT/'reproduccion').glob('*.py'))+[ROOT/'ejecutar.py',ROOT/'base_validada/reproducir_cpc7.py',ROOT/'configuraciones/demo_integrada.jsonl',ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',ROOT/'genealogia/product45/kernel_v27.cpp']
 return{str(x.relative_to(ROOT)):sha(x)for x in paths}
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--python',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--artifact',type=Path);a=p.parse_args();out=a.out.resolve();python=a.python.resolve();artifact=a.artifact.resolve()if a.artifact else None
 if out==ROOT or out.is_relative_to(ROOT)or ROOT.is_relative_to(out):raise ValueError('Output must be a new directory OUTSIDE candidate and not its ancestor')
 if not python.is_file():raise FileNotFoundError('Explicit CPython executable absent')
 if artifact and not artifact.is_file():raise FileNotFoundError('Explicit closed artifact absent')
 out.mkdir(parents=True,exist_ok=False);started=time.monotonic();report={'schema':'CPC8R.clean.candidate.v1','status':'RUNNING','mode':'FINAL_EXACT_ARTIFACT'if artifact else'DEVELOPMENT','candidate_root':str(ROOT),'output':str(out),'artifact':str(artifact)if artifact else None,'artifact_sha256':sha(artifact)if artifact else None,'commands':[],'elapsed_seconds':0,'engine_expected':'Official installed4.5/CPython313x64; no engine imported from candidate source','candidate_writes_authorized':False};report_path=out/'VALIDACION_LIMPIA.json';before=critical_hashes()
 def save():report['elapsed_seconds']=time.monotonic()-started;put(report_path,report)
 def run(name,argv,timeout):
  remaining=1800-(time.monotonic()-started)
  if remaining<=0:raise TimeoutError('Clean validation total1800s exhausted')
  row={'name':name,'argv':[str(x)for x in argv],'cwd':str(out),'timeout_seconds':min(timeout,remaining),'status':'RUNNING'};report['commands'].append(row);save();t=time.monotonic()
  with(out/(name+'.stdout.log')).open('w',encoding='utf8')as stdout,(out/(name+'.stderr.log')).open('w',encoding='utf8')as stderr:
   process=subprocess.Popen([str(x)for x in argv],cwd=out,stdout=stdout,stderr=stderr,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));row['owned_pid']=process.pid
   try:code=process.wait(timeout=min(timeout,remaining))
   except subprocess.TimeoutExpired:
    process.kill();process.wait();row.update(status='TIMEOUT_OWN_CHILD_TERMINATED',elapsed_seconds=time.monotonic()-t);save();raise
  row.update(status='COMPLETED'if code==0 else'FAILED',exit_code=code,elapsed_seconds=time.monotonic()-t);save()
  if code:raise RuntimeError('Clean child failed: '+name)
 try:
  report['manifest_before']=manifest_check(artifact);save()
  worker=ROOT/'reproduccion/worker_limpio.py';run('01_identidad',[python,'-I','-B',worker,'identidad','--report',out/'IDENTIDAD.json'],120);report['identity']=json.loads((out/'IDENTIDAD.json').read_text(encoding='utf8'))
  run('02_cpc7_reference',[python,'-I','-B',ROOT/'base_validada/reproducir_cpc7.py','--out',out/'cpc7_reference'],900);report['reference_summary']=json.loads((out/'cpc7_reference/SUMMARY.json').read_text(encoding='utf8'))
  run('03_demo_integrada',[python,'-I','-B',ROOT/'ejecutar.py','demo','--eventos',ROOT/'configuraciones/demo_integrada.jsonl','--salida',out/'demo_integrada'],300)
  events=[]
  for line in(ROOT/'configuraciones/demo_integrada.jsonl').read_text(encoding='utf8').splitlines():
   if not line.strip()or line.lstrip().startswith('#'):continue
   e=json.loads(line)
   if e['op']=='crear':e['id']='E1_CONTROL_QUANTITY_NEGATIVE'
   if e['op']=='curriculo':e['parametros']['quantity_reference']=11
   events.append(e)
   if e['op']=='guardar'and e.get('archivo')=='E1_T549.deetsnap.gz':break
  control=out/'control_integrada.jsonl';control.write_text('\n'.join(json.dumps(e,ensure_ascii=False)for e in events)+'\n',encoding='utf8');report['control_protocol']={'events_sha256':sha(control),'only_difference':'Current actual reference quantity11 instead31, same other experiences/ports; stops after549. Not a precomputed action.'}
  run('04_demo_control',[python,'-I','-B',ROOT/'ejecutar.py','demo','--eventos',control,'--salida',out/'demo_control'],300)
  run('05_separate_restore',[python,'-I','-B',worker,'restaurar','--snapshot',out/'demo_integrada/E1_T86.deetsnap.gz','--out',out/'restore_process'],300)
  run('06_posttrajectory_audit',[python,'-I','-B',worker,'auditar','--out',out,'--report',out/'COMPARACIONES.json'],180);report['comparisons']=json.loads((out/'COMPARACIONES.json').read_text(encoding='utf8'))
  report['manifest_after']=manifest_check(artifact);report['critical_sources_unchanged']=before==critical_hashes();report['artifact_unchanged']=not artifact or report['artifact_sha256']==sha(artifact)
  if not report['critical_sources_unchanged']or not report['artifact_unchanged']:raise RuntimeError('Candidate/artifact changed during validation')
  report['all_functional_gates_passed']=bool(report['identity']['passed']and report['reference_summary']['status']=='PASS'and report['comparisons']['passed']);report['wheel_sha256']=report['identity']['wheel_sha256'];report['import_path']=report['identity']['module']
  if not report['all_functional_gates_passed']:raise AssertionError('At least one functional gate failed')
  report['status']='PASS'if artifact else'DEVELOPMENT';report['publication_valid']=bool(artifact);report['note']='PASS is allowed only with this exact closed artifact SHA and matching extracted manifest. DEVELOPMENT never authorizes publication.'
 except BaseException as e:report.update(status='FAIL',publication_valid=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());save();raise
 finally:save()
 print(json.dumps({'status':report['status'],'artifact_sha256':report['artifact_sha256'],'seconds':report['elapsed_seconds'],'report':str(report_path)}),flush=True)
if __name__=='__main__':main()
