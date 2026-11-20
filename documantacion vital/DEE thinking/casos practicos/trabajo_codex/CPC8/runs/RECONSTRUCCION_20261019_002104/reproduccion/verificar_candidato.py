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
 paths=list((ROOT/'src').rglob('*.py'))+list((ROOT/'app').rglob('*.py'))+list((ROOT/'reproduccion').glob('*.py'))+list((ROOT/'base_validada').glob('*.py'))+list((ROOT/'configuraciones').glob('demo*.jsonl'))+[ROOT/'ejecutar.py',ROOT/'iniciar_cpc8.ps1',ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl',ROOT/'genealogia/product45/kernel_v27.cpp']
 return{str(x.relative_to(ROOT)):sha(x)for x in paths}
def main():
 if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
 p=argparse.ArgumentParser();p.add_argument('--python',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--artifact',type=Path);p.add_argument('--installation-command',type=Path,help='Optional completed supervised offline-install COMMAND.json, embedded and checked in the external proof');a=p.parse_args();out=a.out.resolve();python=a.python.resolve();artifact=a.artifact.resolve()if a.artifact else None
 if out==ROOT or out.is_relative_to(ROOT)or ROOT.is_relative_to(out):raise ValueError('Output must be a new directory OUTSIDE candidate and not its ancestor')
 if not python.is_file():raise FileNotFoundError('Explicit CPython executable absent')
 if artifact and not artifact.is_file():raise FileNotFoundError('Explicit closed artifact absent')
 out.mkdir(parents=True,exist_ok=False);started=time.monotonic();report={'schema':'CPC8R.clean.candidate.v1','status':'RUNNING','mode':'FINAL_EXACT_ARTIFACT'if artifact else'DEVELOPMENT','candidate_root':str(ROOT),'output':str(out),'artifact':str(artifact)if artifact else None,'artifact_sha256':sha(artifact)if artifact else None,'commands':[],'elapsed_seconds':0,'engine_expected':'Official installed4.5/CPython313x64; no engine imported from candidate source','candidate_writes_authorized':False};report_path=out/'VALIDACION_LIMPIA.json';before=critical_hashes();report['critical_sources_before']=before
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
  if a.installation_command:
   install_path=a.installation_command.resolve();installation=json.loads(install_path.read_text(encoding='utf-8-sig'));argv=installation['argv'];wheel=ROOT/'runtime/dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
   if installation.get('status')!='COMPLETED'or installation.get('exit_code')!=0 or not installation.get('owned_worker_waited')or not installation.get('owned_job_closed'):raise ValueError('Offline installation worker did not complete and close')
   if Path(argv[0]).resolve()!=python or not all(token in argv for token in('pip','install','--no-index','--no-deps'))or not any(Path(token).resolve()==wheel for token in argv if str(token).endswith('.whl')):raise ValueError('Installation command must identify THIS isolated Python and extracted local wheel without index/dependency resolution')
   if sha(wheel)!=report['identity']['wheel_sha256']:raise ValueError('Installed instrument identity differs from the extracted wheel')
   report['installation_command']={'path':str(install_path),'sha256':sha(install_path),'completed_record':installation,'installed_wheel_path':str(wheel),'wheel_sha256':sha(wheel),'verified':True};save()
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
  run('07_demo_basica_regression',[python,'-I','-B',ROOT/'ejecutar.py','demo','--eventos',ROOT/'configuraciones/demo_e1.jsonl','--salida',out/'demo_basica'],300)
  run('08_legacy_profiles_audit',[python,'-I','-B',ROOT/'tools/auditar_app_v2.py','--basica',out/'demo_basica','--integrada',out/'demo_integrada','--out',out/'PERFILES_PREVIOS.json'],180);report['legacy_profiles']=json.loads((out/'PERFILES_PREVIOS.json').read_text(encoding='utf8'))
  contact_apps=out/'app_contacto';contact_cases=(('P11','demo_contacto_social.jsonl','DEMO_CONTACTO_SOCIAL_P11'),('P12','demo_contacto_social_libre.jsonl','DEMO_CONTACTO_SOCIAL_P12'),('R31','demo_contacto_social_reserva.jsonl','DEMO_CONTACTO_SOCIAL_R31'),('C11','demo_contacto_social_control.jsonl','DEMO_CONTACTO_SOCIAL_C11'),('C15','demo_contacto_social_contraflujo_fuera_ruta.jsonl','DEMO_CONTACTO_SOCIAL_C15'))
  for tag,events,directory in contact_cases:run('09_contacto_'+tag,[python,'-I','-B',ROOT/'ejecutar.py','demo','--eventos',ROOT/'configuraciones'/events,'--salida',contact_apps/directory],300)
  run('10_contacto_separate_restore',[python,'-I','-B',worker,'restaurar','--profile','contacto_social','--snapshot',contact_apps/'DEMO_CONTACTO_SOCIAL_P11/E1_CONTACTO_T549.deetsnap.gz','--out',out/'restore_contacto_process'],180)
  run('11_contacto_posttrajectory_audit',[python,'-I','-B',ROOT/'reproduccion/auditar_contacto_social.py','--apps',contact_apps,'--restore',out/'restore_contacto_process','--report',out/'COMPARACIONES_CONTACTO_SOCIAL.json'],180);report['contacto_social_comparisons']=json.loads((out/'COMPARACIONES_CONTACTO_SOCIAL.json').read_text(encoding='utf8'))
  magnitude_apps=out/'app_magnitud';magnitude_cases=(('P31','demo_magnitud_social.jsonl','DEMO_MAGNITUD_SOCIAL_P31'),('H11','demo_magnitud_social_historia11.jsonl','DEMO_MAGNITUD_SOCIAL_H11'),('R17','demo_magnitud_social_reserva17.jsonl','DEMO_MAGNITUD_SOCIAL_R17'),('C01','demo_magnitud_social_control.jsonl','DEMO_MAGNITUD_SOCIAL_C01'))
  for tag,events,directory in magnitude_cases:run('12_magnitud_'+tag,[python,'-I','-B',ROOT/'ejecutar.py','demo','--eventos',ROOT/'configuraciones'/events,'--salida',magnitude_apps/directory],300)
  run('13_magnitud_separate_restore',[python,'-I','-B',worker,'restaurar','--profile','magnitud_social','--snapshot',magnitude_apps/'DEMO_MAGNITUD_SOCIAL_P31/E1_MAGNITUD_T73.deetsnap.gz','--out',out/'restore_magnitud_process'],180)
  run('14_magnitud_posttrajectory_audit',[python,'-I','-B',ROOT/'reproduccion/auditar_magnitud_social.py','--apps',magnitude_apps,'--restore',out/'restore_magnitud_process','--report',out/'COMPARACIONES_MAGNITUD_SOCIAL.json'],180);report['magnitud_social_comparisons']=json.loads((out/'COMPARACIONES_MAGNITUD_SOCIAL.json').read_text(encoding='utf8'))
  k65=[]
  for case,primary in(('K65_PAIRED','K65_PAIRED_RECOVER658'),('K65_REVISION_CADENCE','K65_REVISION_CADENCE')):
   destination=out/'referencia_K65'/case;run('15_repertorio_'+case,[python,'-I','-B',ROOT/'base_validada/reproducir_repertorio65.py','--case',case,'--out',destination],900)
   # Only this post-trajectory auditor reads frozen primary outcomes. The
   # native reference script did not open them or copy an old trained state.
   actual=json.loads((destination/'MEASUREMENTS.json').read_text(encoding='utf8'));reference_path=ROOT/'resultados/repertorio65_referencia'/primary/'MEASUREMENTS.json';reference=json.loads(reference_path.read_text(encoding='utf8'));readings_equal=[x['captured']['responses']for x in actual['all65queries']]==[x['captured']['responses']for x in reference['all65queries']]
   row={'case':case,'primary':str(reference_path.relative_to(ROOT)),'primary_sha256':sha(reference_path),'correct_counts':[x['auditor_correct']for x in actual['all65queries']],'denominator_each':65,'exact_native_readouts_equal':readings_equal,'final_full_physical_equal':actual['final']==reference['final'],'scope':'Published finite K65 physical-form reference on N131. Not65NSMmeanings, not K65incorporated into N67E1, and not a free arbitrary overwrite.'}
   if case=='K65_REVISION_CADENCE':row['revision']={'status':actual['revision']['status'],'revised_L01':actual['revision'].get('auditor_revised_correct'),'other_retained':actual['revision'].get('auditor_other_correct'),'other_denominator':64,'exact_native_readouts_equal':actual['revision'].get('captured',{}).get('responses')==reference['revision'].get('captured',{}).get('responses')}
   row['passed']=row['correct_counts']==[65,65,65]and readings_equal and row['final_full_physical_equal']and(case!='K65_REVISION_CADENCE'or row['revision']['status']=='EXECUTED'and row['revision']['revised_L01']and row['revision']['other_retained']==64 and row['revision']['exact_native_readouts_equal']);k65.append(row)
  report['reference_K65']=k65
  count_reference=ROOT/'resultados/semantica/count_sign_final_fixed/CNS_G13_ONE_B/MEASUREMENTS.json';count_worker=ROOT/'reproduccion/repetir_count_sign.py';count_positive=out/'count_aux_positive'
  run('15b_count_aux_positive',[python,'-I','-B',count_worker,'--out',count_positive,'--case','CNS_G13_ONE_B','--config',ROOT/'configuraciones/semantica/COUNT_SIGN_FINAL_READER_FROZEN.json','--reference',count_reference],180)
  run('15c_count_aux_control',[python,'-I','-B',count_worker,'--out',out/'count_aux_control','--case','CNS_G51_B_NO_FORM','--config',ROOT/'configuraciones/semantica/COUNT_SIGN_BONLY_CONFIRMATION_FROZEN.json','--reference',ROOT/'resultados/semantica/count_sign_Bonly_confirm/CNS_G51_B_NO_FORM/MEASUREMENTS.json'],180)
  run('15d_count_aux_restore',[python,'-I','-B',count_worker,'--out',out/'count_aux_restore','--case','CNS_G13_ONE_B','--restore',count_positive/'T94.deetsnap.gz','--reference',count_reference],180)
  report['count_auxiliary']=[json.loads((out/name/'CHECK.json').read_text(encoding='utf8'))for name in('count_aux_positive','count_aux_control','count_aux_restore')]
  coupled=[]
  for condition,case in(('plus','RCAM_D02_CONTINUED_FROM4'),('minus','RCAM_H01_MINUS_HIGH')):
   destination=out/('regulation_coupled_'+condition)
   run('15e_regulation_coupled_'+condition,[python,'-I','-B',ROOT/'tools/reproducir_regulacion_acoplada.py','--condition',condition,'--reference',ROOT/'resultados/regulacion_acoplada'/case/'MEASUREMENTS.json','--out',destination],300)
   coupled.append(json.loads((destination/'RESULT.json').read_text(encoding='utf8')))
  report['regulation_coupled_auxiliary']=coupled
  functional=[]
  for medium,case in((1,'RCAM_R201_FUNCTION_PLUS'),(-1,'RCAM_R202_FUNCTION_MINUS')):
   destination=out/('regulation_function_'+str(medium))
   run('15f_regulation_function_'+str(medium),[python,'-I','-B',ROOT/'src/regulacion_acoplada/run_mcts.py','--case','CLEAN_'+case,'--medium',str(medium),'--reference','31','--objects','16','37','--out',destination],300)
   # Newly selected object37 is an actual material experience, not an answer
   # bit. Expected native observations enter this auditor only afterwards.
   actual=json.loads((destination/'MEASUREMENTS.json').read_text(encoding='utf8'));frozen=ROOT/'resultados/regulacion_acoplada'/case/'MEASUREMENTS.json';expected=json.loads(frozen.read_text(encoding='utf8'))
   frames_equal=actual['frames']==expected['frames'];receipts_equal=[r['receipt']for r in actual['requests']]==[r['receipt']for r in expected['requests']]
   row={'case':case,'primary_sha256':sha(frozen),'all_native_frames_equal':frames_equal,'exact_native_receipts':receipts_equal,'full_final_physical_equal':actual['final_physical']==expected['final_physical'],'readings':actual['regulation_readings'],'scope':'Post-first-factorial frozen discriminating design: R.quantity original36/object42 versus corrupted43/object42. Separate new life, not MAIN35 and not a pre-existing confirmatory reserve.'}
   row['passed']=frames_equal and receipts_equal and row['full_final_physical_equal'];functional.append(row)
  report['regulation_discriminating_function']=functional
  run('16_all_snapshot_storage',[python,'-I','-B',ROOT/'tools/verificar_snapshots_locales.py','--out',out/'SNAPSHOTS_INTEGRIDAD.json'],300)
  report['snapshot_storage']=json.loads((out/'SNAPSHOTS_INTEGRIDAD.json').read_text(encoding='utf8'))
  run('17_revision_data_only',[python,'-I','-B',ROOT/'reproduccion/recalcular_revision.py','--out',out/'revision_data_only'],300);report['revision_data_only']=json.loads((out/'revision_data_only/RECALCULO_REVISION.json').read_text(encoding='utf8'))
  report['all_functional_gates_passed']=bool(report['identity']['passed']and report['reference_summary']['status']=='PASS'and report['comparisons']['passed']and report['contacto_social_comparisons']['passed']and report['magnitud_social_comparisons']['passed']and report['revision_data_only']['passed']and all(x['passed']for x in functional)and all(x['status']=='PASS'for x in coupled)and all(x['passed']for x in report['count_auxiliary'])and all(x['passed']for x in k65)and all(x['exact_RAW_clocks_tick']and x['exact_native_receipts']for x in report['legacy_profiles']['comparisons']));report['wheel_sha256']=report['identity']['wheel_sha256'];report['import_path']=report['identity']['module']
  report['manifest_after']=manifest_check(artifact);after=critical_hashes();report['critical_sources_after']=after;report['critical_sources_unchanged']=before==after;report['critical_sources_changed']=[{'path':name,'before_sha256':before.get(name),'after_sha256':after.get(name)}for name in sorted(set(before)|set(after))if before.get(name)!=after.get(name)];report['artifact_unchanged']=not artifact or report['artifact_sha256']==sha(artifact)
  if not report['critical_sources_unchanged']or not report['artifact_unchanged']:raise RuntimeError('Candidate/artifact changed during validation')
  if not report['all_functional_gates_passed']:raise AssertionError('At least one functional gate failed')
  report['status']='PASS'if artifact else'DEVELOPMENT';report['publication_valid']=bool(artifact);report['note']='PASS is allowed only with this exact closed artifact SHA and matching extracted manifest. DEVELOPMENT never authorizes publication.'
 except BaseException as e:report.update(status='FAIL',publication_valid=False,error_type=type(e).__name__,error=str(e),traceback=traceback.format_exc());save();raise
 finally:save()
 print(json.dumps({'status':report['status'],'artifact_sha256':report['artifact_sha256'],'seconds':report['elapsed_seconds'],'report':str(report_path)}),flush=True)
if __name__=='__main__':main()
