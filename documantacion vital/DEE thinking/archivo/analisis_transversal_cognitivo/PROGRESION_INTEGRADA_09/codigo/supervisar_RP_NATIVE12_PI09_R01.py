"""Root-only real gestionar/RP cold12, global writer, one world,512MiB.

Default prints a plan. Published RP tools remain literal. Coherent closure is
separate from fixed local criteria. No uncertain retry or unlogged process kill.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,importlib.util,json,os,sqlite3,sys,time
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01';A='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';RID='pi09_consulta_native12_desde_C_T884835_R03';VARIANT='native12';DEST=P/'estados/RP_REPRO_R01'
GUARD=P/'codigo/guardia_frontdoor_RP_NATIVE12_PI09_R01.py';LEDGER=P/'codigo/ledger_PI09_misma_identidad_R01.py';LEDGER_SHA='bb1f326aa981ba00b9a6e3417700cca31d92a0d28a6e8a5ad601042bf2a26260'
OUTPUT=P/'control/SUPERVISION_RP_NATIVE12_PI09_R01.json';MARKER=P/'PI09_ROOT_NATIVE_WRITER.lock';LIMIT=512*1024*1024;BOUND=12*2280;INITIAL=884835
RECIPE_SHA='d41ed2b642c93fee45d61fe933f429822352f96557d1fb590c82346ad06bfac0';CAPSULE_SHA='67be03d36afc2890cb2d61425fe842509a671f09dcffb6b03ba19ad54afddda5'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load_ledger():
 need(sha(LEDGER)==LEDGER_SHA,'Changed exact saved-cut ledger');sp=importlib.util.spec_from_file_location('PI09_cold12_supervisor_ledger',LEDGER);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def record(v):
 tmp=OUTPUT.with_name(OUTPUT.name+'.WRITING')
 with tmp.open('w',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,OUTPUT)
def coherent():
 resultfile=DEST/'RESULTADO_REPRODUCCION.json';cardfile=DEST/'sistema/estado/vidas'/LIFE/'VIDA.json'
 if not resultfile.is_file()or not cardfile.is_file():return None
 r=read(resultfile);card=read(cardfile)
 if r.get('status')!='COMPLETED'or r.get('owner_closed_coherently')is not True or r.get('life')!=LIFE:return None
 system=DEST/'sistema';db=system/'estado/servicios_persistentes'/card['world_id']/'cola.sqlite3'
 if any(Path(str(db)+suffix).exists()and Path(str(db)+suffix).stat().st_size for suffix in('-wal','-journal'))or(system/'estado/locks'/(card['world_id']+'.lock')).exists()or(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists():return None
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':return None
  row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(row[0])if row else{}
  if owner.get('running')is not False or con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]:return None
 finally:con.close()
 guardfile=P/'control/GUARDIA_DRIVER_RP_NATIVE12_PI09_R01.json'
 if not guardfile.is_file():return None
 g=read(guardfile)
 if g.get('status')!='COMPLETED_DRIVER'or g.get('completed_material_requests')!=14 or g.get('final_tick')!=card['physical']['tick']:return None
 return {'summary':str(resultfile),'summary_sha256':sha(resultfile),'criteria_met':r.get('criteria_met'),'denominators':r.get('denominators'),'Native_receipts':r.get('native_receipts'),'card':str(cardfile),'card_sha256':sha(cardfile),'snapshot_sha256':card['snapshot_sha256'],'final_tick':card['physical']['tick'],'actual_new_Native_ticks':card['physical']['tick']-INITIAL,'Native_bound_met':0<=card['physical']['tick']-INITIAL<=BOUND,'driver_guard':{'path':str(guardfile),'sha256':sha(guardfile)},'scientific_result_distinct_from_coherent_closure':True}
def main(a):
 command=[str(PY),'-I','-B','-X','utf8',str(GUARD),'--stage','manager'];actualcli=['reproducibilidad','reproducir',RID,'--variante',VARIANT,'--vida',LIFE,'--destino',str(DEST),'--material']
 if not a.ejecutar:
  print(json.dumps({'mode':'PLAN_ONLY_NO_STATE_READ','command':command,'actual_manager':str(S/'gestionar.py'),'actual_CLI':actualcli,'memory_limit_bytes':LIMIT,'new_worlds':1,'conservative_Native_bound':BOUND,'registered_canonical_ticks':18768,'published_RP_tools_changed':False,'expected_criteria_from_literal_recipe':{'step_expected':14,'final_checks':180,'receipt_expectations':4},'deadline':'actual REGISTRO_CAMPANA new_experimental_uses_cutoff_local','automatic_retry':False},ensure_ascii=False));return
 need(Path(sys.executable).resolve()==PY.resolve(),'Root official existing Python required')
 need(not DEST.exists()and not OUTPUT.exists()and not MARKER.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Fresh destination and one Root/RP writer required; never clear stale guards')
 need(not(RP/'EJECUCIONES'/(LIFE+'.json')).exists(),'Exact reproduction identity was already used')
 for root in(S/'estado/vidas'/LIFE,S/'estado/servicios_locales'/LIFE,S/'estado/servicios_persistentes'/LIFE):need(not root.exists(),'Reproduction ID exists in product')
 need(sha(RP/'recetas'/(RID+'.json'))==RECIPE_SHA,'Registered actual recipe changed')
 integration=read(P/'control/RP_CONSULTA_INCORPORADA_PI09_R01.json');need(integration.get('applied')is True and integration['recipe_sha256']==RECIPE_SHA and integration['capsule_manifest_sha256']==CAPSULE_SHA,'Actual additive RP integration required')
 budget=read(P/'REGISTRO_CAMPANA.json')['budget'];need(budget['owned_Native_job_memory_bytes']==LIMIT and budget['Native_threads']==1 and budget['diagnostic_worlds_all_new']==12 and budget['Native_ticks_all_branches']==220000,'Fixed registered campaign limits must remain literal')
 deadline=datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc);need(datetime.now(timezone.utc)<deadline,'No new research after cutoff')
 ledger=load_ledger();before=ledger.ledger();need(before['ticks']+BOUND<=budget['Native_ticks_all_branches']and before['world_count']+1<=budget['diagnostic_worlds_all_new'],'Actual all-branch budget plus one cold world does not fit')
 cardfile=S/'estado/vidas'/A/'VIDA.json';card=read(cardfile);need(read(S/'estado/ACTIVO.json')['life_id']==A and card['physical']['tick']==861426,'Protected A current principal changed before cold12')
 protected={str(p):sha(p)for p in(S/'estado/ACTIVO.json',cardfile,S/card['snapshot'])}
 need(sha(P/'pares/NATIVE_POST12_T903603/EXPORTACION_SERVICIO.json')=='0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553','Canonical post12 prefix changed')
 with MARKER.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'life_id':LIFE,'created_utc':datetime.now(timezone.utc).isoformat(),'scope':'Real fixed RP cold12, diagnostic clone only','Native_bound':BOUND,'new_worlds':1,'memory_limit_bytes':LIMIT,'no_automatic_stale_lock_removal':True},f)
 sys.path.insert(0,str(S));from app import process_control as pc
 stdout=OUTPUT.with_suffix('.stdout.txt');stderr=OUTPUT.with_suffix('.stderr.txt');started=time.monotonic();samples=[];warnings=[];cleanup=None
 base={'schema':'DEE.PI09.RP.cold12.owned_supervision.R01','started_utc':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,'destination':str(DEST),'command':command,'actual_public_manager_CLI':actualcli,'supervisor_sha256':sha(Path(__file__)),'driver_guard_sha256':sha(GUARD),'ledger_sha256':LEDGER_SHA,'recipe_sha256':RECIPE_SHA,'memory_limit_bytes':LIMIT,'Native_bound':BOUND,'new_worlds':1,'deadline_utc':deadline.isoformat(),'budget_before':before,'global_mutex':str(MARKER),'RP_material_lock_managed_only_by_existing_RP':str(RP/'EJECUCION_MATERIAL.lock'),'automatic_retry':False,'unlogged_kill':False}
 with stdout.open('x',encoding='utf8')as out,stderr.open('x',encoding='utf8')as err:
  proc,job,name=pc.spawn_owned(command,cwd=str(P),stdout=out,stderr=err,memory_limit=LIMIT);base.update(pid=proc.pid,owned_job=name);record({**base,'status':'RUNNING'})
  while True:
   try:
    sample={'at_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-started,'exit_code':proc.poll(),**pc.job_resources(job)};samples.append(sample)
    if proc.poll()is not None and sample.get('job_active_processes')==0:break
    if proc.poll()==0 and sample.get('job_active_processes')==1:
     saved=coherent()
     if saved:
      cleanup={'kind':'EXPLICIT_COHERENT_DIAGNOSTIC_IDLE_JOB_CLOSE','saved_state':saved,'remaining_owned_processes':1,'mechanism':'Logged KILL_ON_JOB_CLOSE for own idle bridge only after rootexit0, all material requests closed/pending0; no uncertain termination.'};record({**base,'status':'CLOSING_COHERENT_IDLE_BRIDGE','cleanup':cleanup,'samples':samples});pc.close_job(job);job=None;break
    if(datetime.now(timezone.utc)>=deadline or time.monotonic()-started>a.horizonte_segundos)and not warnings:
     warnings.append({'kind':'TIME_LIMIT_REACHED','at_utc':datetime.now(timezone.utc).isoformat(),'automatic_kill':False,'next':'Guard refuses subsequent inputs; supervisor retains owned handle while current bounded work closes. Root must inspect an uncertain live job.'});record({**base,'status':'TIME_LIMIT_LIVE_JOB_PRESERVED','samples':samples,'warnings':warnings});print(json.dumps(warnings[-1]),flush=True)
    time.sleep(.5)
   except KeyboardInterrupt:warnings.append({'kind':'ROOT_INTERRUPT_LIVE_HANDLE_RETAINED','automatic_kill':False});record({**base,'status':'INTERRUPTION_PRESERVED','samples':samples,'warnings':warnings})
  exitcode=proc.wait(timeout=1)
  if job is not None:need(pc.job_resources(job).get('job_active_processes')==0,'Uncertain live job retained');pc.close_job(job)
 saved=coherent();unchanged=protected=={path:sha(Path(path))for path in protected};closed=bool(exitcode==0 and saved and saved['Native_bound_met']and unchanged and not(RP/'EJECUCION_MATERIAL.lock').exists())
 final={**base,'status':'COMPLETED_DIAGNOSTIC'if closed else'STOPPED_FUTURE_PRESERVED','finished_utc':datetime.now(timezone.utc).isoformat(),'exit_code':exitcode,'closed':closed,'actual':saved,'original_A_unchanged':unchanged,'budget_after_saved':ledger.ledger(),'elapsed_seconds':time.monotonic()-started,'peak_job_committed_bytes':max(s.get('peak_job_committed_bytes',0)for s in samples),'samples':samples,'warnings':warnings,'explicit_idle_bridge_cleanup':cleanup,'stdout':{'path':str(stdout),'bytes':stdout.stat().st_size,'sha256':sha(stdout)},'stderr':{'path':str(stderr),'bytes':stderr.stat().st_size,'sha256':sha(stderr)},'functional_criteria_not_conflated_with_closure':True};record(final)
 if closed:need(read(MARKER)['pid']==os.getpid(),'Only own Root mutex can be released');MARKER.unlink()
 print(json.dumps({'proof':str(OUTPUT),'sha256':sha(OUTPUT),'status':final['status'],'closed':closed,'actual':saved,'original_A_unchanged':unchanged}));return 0 if closed else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--ejecutar',action='store_true');ap.add_argument('--horizonte-segundos',type=int,default=3600);raise SystemExit(main(ap.parse_args()))
