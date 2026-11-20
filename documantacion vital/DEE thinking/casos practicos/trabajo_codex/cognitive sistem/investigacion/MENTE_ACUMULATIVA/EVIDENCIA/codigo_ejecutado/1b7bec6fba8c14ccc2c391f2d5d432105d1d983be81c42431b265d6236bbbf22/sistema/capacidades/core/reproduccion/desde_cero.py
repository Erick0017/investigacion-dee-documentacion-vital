"""Install and recover from THIS closed artifact, never from historical ZIPs.

Default panel: available CPython3.13 x64 Windows plus OS runtime libraries.
Two optional direct-array contracts additionally require explicit NumPy2.2.6.
All recovery outputs/environment are outside the artifact.
No arbitrary deserialization, downloads, historical launchers or cleanup.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[1]
BASE_FAMILIES=('cpc1','cpc2','sem01','cpc4','cpc5','cpc6','cpc7','mcts','repertoire','rca','count','product','product_extra')
EXTENSIONS=('ordered','stream','network','architectures','bridge','capacity','longitudinal','policy','native_loop','central','qfm','l15','need','missing')
RETENTION=('retain_early','retain_word','retain_late')
FAMILIES=BASE_FAMILIES+EXTENSIONS+RETENTION+('social','initial_cpc8')
LEGACY_ARRAY_FAMILIES=('core06','core07')
AVAILABLE_FAMILIES=FAMILIES+('product_persistence',)+LEGACY_ARRAY_FAMILIES
PREFIXES=('historico/CPC3/genealogia/CP01_C08/','historico/CPC3/genealogia/CP02_B/','historico/CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/src/','historico/CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/resultados/confirmacion/','historico/CPC4/ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD/src/','historico/CPC4/ampliaciones/02_APRENDIZAJE_CONTINUO_RED_ABCD/resultados/red/fixed_counterflow01/','historico/CPC5/src/','historico/CPC5/configuraciones/compound','historico/CPC5/resultados/compound_reuse','historico/CPC6/src/','historico/CPC6/configuraciones/R03_WORD_BUS_V2','historico/CPC6/resultados/R03_WORD_BUS_V2/','cpc8/src/','cpc8/configuraciones/','cpc8/base_validada/','cpc8/genealogia/CPC7/','cpc8/resultados/transferencia_magnitud/','cpc8/resultados/repertorio65_referencia/','cpc8/resultados/regulacion_acoplada/RCAM_R201_FUNCTION_PLUS/','cpc8/resultados/regulacion_acoplada/RCAM_R202_FUNCTION_MINUS/','cpc8/reproduccion/repetir_count_sign.py','cpc8/resultados/semantica/count_sign_final_fixed/','cpc8/resultados/semantica/count_sign_Bonly_confirm/')
PREFIXES+=('historico/CPC3/src/','historico/CPC3/experimentos/comparacion_seleccion/','historico/CPC3/experimentos/seleccion_revisable/','historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/src/','historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/ordered_','historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/order_stream','historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/network_dialogue','historico/CPC5/ampliaciones/01_SEMANTICA_RELACIONAL_Y_DIALOGO/resultados/capacity_','historico/CPC6/configuraciones/','historico/CPC6/resultados/ARCHITECTURE_','historico/CPC6/resultados/CONSOLIDATION_CONTROLS_01/','historico/CPC6/resultados/WORD_BUS_CONTROLS_01/','historico/CPC6/resultados/LATE_ACCESS_01/','historico/CPC6/resultados/D04_OPEN_LANDING/','historico/CPC6/resultados/B01_WORD_BUS/','historico/CPC6/resultados/D06_BILATERAL/','cpc8/genealogia/product45/kernel_v27.cpp','cpc8/tools/ejecutar_cantidad_forma_movil.py','cpc8/resultados/cantidad/QFM_','cpc8/resultados/diagnostico_L15_r1/passive_original_PRE_JOIN_T78.deetsnap.gz','cpc8/resultados/diagnostico_L15_causal/')
PREFIXES+=('historico/CPC7/src/','historico/CPC7/configuraciones/endogenous/','historico/CPC7/resultados/endogenous/comparison_','historico/CPC7/resultados/endogenous/missing_actual_fallback/')
PREFIXES+=('cpc8/resultados/semantica/CTS_',)
PREFIXES+=('cpc8_inicial/resultados/semantica/SOC_I','cores/',)
PREFIXES+=('cpc8_inicial/resultados/integracion/LIF_','cpc8_inicial/resultados/integracion/USE_','cpc8_inicial/configuraciones/integracion/LONGITUDINAL_690_FROZEN.json','cpc8_inicial/configuraciones/integracion/RIGHT_ACCESS_1182_FROZEN.json')
PREFIXES+=('cpc8/genealogia/fuentes/6f3babac1f303f340b0e.py','cpc8/genealogia/fuentes/3867d6fa86a3b2c90b42.json','cpc8/genealogia/fuentes/f4390ffab1cc3101ae02.py','historico/CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/fuentes/CORE06/RUNNERS/native_core.py','historico/CPC3/experimentos/SEM01_SIGNIFICADO_ADQUIRIDO/fuentes/CORE07/RUNNERS/core07_common.py')
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1024**2),b''):h.update(b)
 return h.hexdigest()
def put(p,v):Path(p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def verify(artifact):
 manifest=json.loads((ROOT/'MANIFIESTO.json').read_text(encoding='utf8'));expected={r['path']for r in manifest['files']}|{'MANIFIESTO.json','HASHES.sha256'}
 actual={p.relative_to(ROOT).as_posix()for p in ROOT.rglob('*')if p.is_file()}
 if actual!=expected:raise ValueError('Extracted inventory differs from manifest')
 for row in manifest['files']:
  p=PurePosixPath(row['path'])
  if p.is_absolute()or'..'in p.parts or':'in str(p):raise ValueError('Unsafe manifest path')
  f=ROOT/p
  if f.stat().st_size!=row['bytes']or sha(f)!=row['sha256']:raise ValueError('Manifest hash mismatch: '+str(p))
 if artifact:
  with zipfile.ZipFile(artifact)as z:
   names=z.namelist()
   if len(names)!=len(set(n.casefold()for n in names))or set(names)!={'DEE_COGNITIVE_CORE/'+n for n in expected}:raise ValueError('Archive inventory mismatch')
   if z.testzip():raise ValueError('CRC failure')
   for name in expected:
    if hashlib.sha256(z.read('DEE_COGNITIVE_CORE/'+name)).hexdigest()!=sha(ROOT/name):raise ValueError('Exact archive/extraction bytes differ: '+name)
 return{'passed':True,'files':len(expected),'manifest_sha256':sha(ROOT/'MANIFIESTO.json')}
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--artifact',type=Path);p.add_argument('--python',type=Path,default=Path(sys.executable));p.add_argument('--families',default=','.join(FAMILIES));p.add_argument('--numpy-root',type=Path,help='Explicit site-packages containing optional tested NumPy2.2.6 for core06/core07 only');p.add_argument('--include-legacy-cores',action='store_true',help='Add the two original direct-array CORE06/CORE07 contracts; requires --numpy-root');p.add_argument('--total-seconds',type=int,default=3600);a=p.parse_args()
 out=a.out.resolve();artifact=a.artifact.resolve()if a.artifact else None
 if out==ROOT or out.is_relative_to(ROOT)or ROOT.is_relative_to(out):raise ValueError('Use new external recovery output')
 out.mkdir(parents=True,exist_ok=False);start=time.monotonic();path=out/'PRUEBA_RECUPERACION_DESDE_CERO.json'
 report={'schema':'DEE_CORE.clean_recovery.v1','status':'RUNNING','started_utc':datetime.now(timezone.utc).isoformat(),'artifact':str(artifact)if artifact else None,'artifact_sha256':sha(artifact)if artifact else None,'artifact_root':str(ROOT),'external_dependencies':['Available CPython3.13 x64 Windows installation and OS C++runtime, no pipindex'],'historical_archives_opened':False,'commands':[],'family_results':{},'total_limit_seconds':a.total_seconds}
 def save():report['elapsed_seconds']=time.monotonic()-start;put(path,report)
 def run(name,argv,timeout=900):
  remaining=a.total_seconds-(time.monotonic()-start)
  if remaining<=0:raise TimeoutError('Recovery total time limit reached')
  row={'name':name,'argv':list(map(str,argv)),'cwd':str(out),'timeout':min(timeout,remaining),'status':'RUNNING'};report['commands'].append(row);save();t=time.monotonic()
  with(out/(name+'.stdout.log')).open('w',encoding='utf8')as stdout,(out/(name+'.stderr.log')).open('w',encoding='utf8')as stderr:
   process=subprocess.Popen(list(map(str,argv)),cwd=out,stdout=stdout,stderr=stderr,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));row['owned_pid']=process.pid
   try:code=process.wait(timeout=min(timeout,remaining))
   except subprocess.TimeoutExpired:process.kill();process.wait();row.update(status='TIMEOUT',owned_worker_waited=True);save();return False
  row.update(status='PASS'if code==0 else'FAIL',exit_code=code,elapsed_seconds=time.monotonic()-t,owned_worker_waited=True);save();return code==0
 try:
  report['integrity_before']=verify(artifact);save()
  if not run('01_create_environment',[a.python,'-I','-B','-m','venv',out/'environment'],180):raise RuntimeError('Environment creation failed')
  python=out/'environment/Scripts/python.exe';wheel=next((ROOT/'runtime').glob('*.whl'))
  if not run('02_absent_before_install',[python,'-I','-B','-c','import importlib.util,sys,struct; assert sys.version_info[:2]==(3,13) and struct.calcsize("P")==8; assert importlib.util.find_spec("dee_thinking") is None; print(sys.executable)'],60):raise RuntimeError('Fresh interpreter identity failed')
  if not run('03_install_local_official_wheel',[python,'-I','-B','-m','pip','--disable-pip-version-check','install','--no-index','--no-deps','--no-cache-dir',wheel],180):raise RuntimeError('Offline installation failed')
  if not run('03b_example',[python,'-I','-B',ROOT/'ejemplos_funcionales/crear_consultar_continuar.py','--out',out/'example'],180):raise RuntimeError('Fresh small example failed')
  command=[python,'-I','-B',ROOT/'scripts/materializar.py','--out',out/'RECUPERADO']
  for prefix in PREFIXES:command+=['--prefix',prefix]
  if not run('04_materialize_exact_sources',command,300):raise RuntimeError('Materialization/hash validation failed')
  if not run('04b_recalculate_historical_observers',[python,'-I','-B',ROOT/'reproduccion/recalcular_observadores.py','--materialized',out/'RECUPERADO','--out',out/'CORE15_17_RECALCULADO.json'],60):raise RuntimeError('Historical observer calculation failed')
  families=a.families.split(',')
  if a.include_legacy_cores:families+=list(f for f in LEGACY_ARRAY_FAMILIES if f not in families)
  if set(families)&set(LEGACY_ARRAY_FAMILIES):report['external_dependencies'].append('Optional NumPy2.2.6 at explicitly supplied --numpy-root; no historical scientific data supplied by that dependency')
  if not set(families)<=set(AVAILABLE_FAMILIES):raise ValueError('Unknown family requested')
  for family in families:
   if family in LEGACY_ARRAY_FAMILIES:
    if a.numpy_root is None:raise ValueError('core06/core07 require explicit --numpy-root for the declared optional NumPy2.2.6 dependency')
    report['optional_numpy_root']=str(a.numpy_root.resolve());target=out/('native_'+family);okay=run('05_'+family,[python,'-I','-B',ROOT/'reproduccion/worker_legacy_core.py','--family',family,'--numpy-root',a.numpy_root.resolve(),'--materialized',out/'RECUPERADO','--out',target],2400)
    proof=target/'RECOVERY.json';value=json.loads(proof.read_text(encoding='utf8'))if proof.exists()else{'status':'PROCESS_FAILED_WITHOUT_RESULT','command_completed':okay}
    # Auditor-only reference access AFTER the native worker has exited. The
    # historical primaries lack full-world hashes; this separate comparison
    # verifies complete states of the newly published official4.5 port.
    development=ROOT/'verificaciones'/(family.upper()+'_PRIMARY_TRANSITIONS.json');observed=target/'PRIMARY_TRANSITIONS.json'
    if development.is_file()and observed.is_file():
     expected=json.loads(development.read_text(encoding='utf8'));actual=json.loads(observed.read_text(encoding='utf8'));keys=('family','worlds','transitions','physical_imports');checks={k:actual[k]==expected[k]for k in keys};value['technical_published_port_full_state_comparison']={'checks':checks,'development_reference_sha256':sha(development),'scope':'Exact initial states/external writes/terminal RAW-clock hashes of official4.5 port. Does NOT invent unavailable historical full-state hashes.'}
     if not all(checks.values()):value['status']='FAIL_PORT_REPRODUCTION'
    else:value['status']='MISSING_PUBLISHED_PORT_STATE_REFERENCE'
    report['family_results'][family]=value;save();continue
   script='worker_initial_cpc8.py'if family=='initial_cpc8'else'worker_social.py'if family=='social'else'worker_extension.py'if family in EXTENSIONS else'worker_retention.py'if family in RETENTION else'worker_core.py';argument=family.removeprefix('retain_')if family in RETENTION else family
   target=out/('native_'+family);okay=run('05_'+family,[python,'-I','-B',ROOT/'reproduccion'/script,argument,'--materialized',out/'RECUPERADO','--out',target])
   proof=target/'RECOVERY.json';report['family_results'][family]=json.loads(proof.read_text(encoding='utf8'))if proof.exists()else{'status':'PROCESS_FAILED_WITHOUT_RESULT','command_completed':okay};save()
  report['integrity_after']=verify(artifact);report['no_artifact_changes']=report['integrity_after']==report['integrity_before']
  report['all_requested_families_passed']=all(v['status']=='PASS'for v in report['family_results'].values())
  report['blocked_external_reads']=sum(len(v.get('undeclared_read_attempts',[]))+len(v.get('historical_reads_denied',[]))for v in report['family_results'].values())
  report['status']='PASS'if artifact and report['all_requested_families_passed']and report['no_artifact_changes']and report['blocked_external_reads']==0 else'PARTIAL_OR_DEVELOPMENT'
 except BaseException as e:
  import traceback;report.update(status='ERROR',error=repr(e),traceback=traceback.format_exc())
 report['finished_utc']=datetime.now(timezone.utc).isoformat();save()
 lines=['# Recuperación desde cero','',f"Estado: {report['status']}",f"ZIP exacto: {report.get('artifact_sha256')}",'','La instalación y las ejecuciones usan únicamente este paquete y las dependencias externas explícitas de DEPENDENCIAS.json: CPython3.13x64 y runtime del sistema; NumPy2.2.6 sólo para los dos contratos directos opcionales CORE06/07. No se abren ZIP históricos. El control de acceso es un audit-hook de archivos Python más revisión de rutas y fuentes; no es una caja de seguridad del sistema operativo.','']
 for family,value in report['family_results'].items():lines.append(f"- {family}: {value['status']} ({value.get('elapsed_seconds',0):.3f}s). {value.get('scope','')}")
 lines+=['','PASS califica recuperación de los contratos ejecutados, no atribución de todas las capacidades a un E1 ni nuevos significados NSM. Las capacidades documentales no ejecutadas permanecen fuera de esta afirmación.']
 (out/'PRUEBA_RECUPERACION_DESDE_CERO.md').write_text('\n'.join(lines)+'\n',encoding='utf8');print(json.dumps({'status':report['status'],'artifact_sha256':report.get('artifact_sha256'),'seconds':report['elapsed_seconds']}))
 if report['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
