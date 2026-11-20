"""Root-only fixed RP A diagnostic, one writer, one world,512MiB owned job.

Default is a plan. No ambiguous automatic retry or termination. Original RP
manager/scripts stay literal; the separately hashed guard checks each request.
Wrong numeric results are saved and do not stop the fixed panel.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,sqlite3,sys,time
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
A='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_ARP_PANEL12_01'
DEST=P/'estados/RP_A_PANEL12_R01';RID='pi08_a_panel12_regulado_T861426_R01'
GUARD=P/'codigo/guardia_frontdoor_RP_A_panel12_PI08_R01.py'
OUTPUT=P/'control/SUPERVISION_RP_A_PANEL12_PI08_R01.json';MARKER=P/'PI08_ROOT_NATIVE_WRITER.lock';LIMIT=512*1024*1024;BOUND=8684
ALLOCATION=P/'control/REASIGNACION_MUNDO_F1_A_CONTROL_PI08_R01.json';ALLOCATION_SHA='7c522c9759039c4e2942f9c87bc3443f6134f165dd2978429dd5f243b0ffc20a'
def need(ok,message):
 if not ok:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(value):
 temp=OUTPUT.with_name(OUTPUT.name+'.WRITING')
 with temp.open('w',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(temp,OUTPUT)
def ledger(allocation):
 cards=list((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json'))+list((S/'estado/vidas').glob('*PI08_*/VIDA.json'));seen={}
 for path in cards:
  card=read(path);life=card['life_id'];initial=card.get('parent',{}).get('source_tick');current=card['physical']['tick']
  need(type(initial)is int and current>=initial,'Known complete imported parent required')
  value=(initial,current,card['snapshot_sha256']);need(life not in seen or seen[life]==value,'Divergent identity aliases')
  seen[life]=value
 # This conservative reserve covers BOTH bounded F1 source/identity traces,
 # even if their actual saved source-card ticks have already been counted.
 return {'cards':len(seen),'card_ticks':sum(c-i for i,c,_ in seen.values()),'additional_conservative_F1_Native_allowance':5200,
         'worlds_with_actual_identity_fork_and_new_A_control':len(seen)+allocation['F1_identity_forks_created']+1}
def coherent():
 summary=DEST/'RESULTADO_REPRODUCCION.json';cardfile=DEST/'sistema/estado/vidas'/LIFE/'VIDA.json'
 if not summary.is_file()or not cardfile.is_file():return None
 result=read(summary);card=read(cardfile)
 if result.get('owner_closed_coherently')is not True or result.get('status')!='COMPLETED'or result.get('life')!=LIFE:return None
 system=DEST/'sistema';world=card['world_id'];db=system/'estado/servicios_persistentes'/world/'cola.sqlite3';wal=Path(str(db)+'-wal')
 if(wal.exists()and wal.stat().st_size)or(system/'estado/locks'/(world+'.lock')).exists()or(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists():return None
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','Final queue integrity')
  row=con.execute("select value from meta where key='owner'").fetchone();owner=read_json(row[0])if row else{}
  if owner.get('running')is not False or con.execute("select count(*)from requests where status in('queued','processing','uncertain')").fetchone()[0]:return None
 finally:con.close()
 return {'summary':str(summary),'summary_sha256':sha(summary),'criteria_met':result['criteria_met'],'denominators':result['denominators'],'Native_receipts':result['native_receipts'],
         'card':str(cardfile),'card_sha256':sha(cardfile),'final_tick':card['physical']['tick'],'actual_new_Native_ticks':card['physical']['tick']-861426,'Native_bound_met':0<=card['physical']['tick']-861426<=BOUND,
         'driver_guard':str(P/'control/GUARDIA_DRIVER_RP_A_PANEL12_PI08_R01.json')}
def read_json(value):return json.loads(value)
def main(args):
 command=[str(PY),'-I','-B','-X','utf8',str(GUARD),'--stage','manager']
 if not args.ejecutar:
  print(json.dumps({'mode':'PLAN_ONLY','actual_manager':str(S/'gestionar.py'),'command':command,'actual_CLI':['reproducibilidad','reproducir',RID,'--variante','panel12_sin_c2c','--vida',LIFE,'--destino',str(DEST),'--material'],
    'Native_memory_limit':LIMIT,'Native_threads':1,'new_worlds':1,'Native_bound':BOUND,'published_RP_tools_changed':False,'guard_scope':'External per-request admission deadline/fixed-payload/budget checks only; old manager/RP/driver run literally.'}));return
 need(Path(sys.executable).resolve()==PY.resolve(),'Root official existing Python required')
 need(not DEST.exists()and not OUTPUT.exists()and not MARKER.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Fresh destination/ID and one Root writer; no automatic retry')
 need(not(RP/'EJECUCIONES'/(LIFE+'.json')).exists(),'This identity has never been registered')
 need(sha(ALLOCATION)==ALLOCATION_SHA,'Actual prospective world reassignment proof required');allocation=read(ALLOCATION)
 budget=read(P/'REGISTRO_CAMPANA.json')['budget'];before=ledger(allocation)
 need(before['card_ticks']+5200+BOUND<=budget['Native_ticks_all_branches']and before['worlds_with_actual_identity_fork_and_new_A_control']<=budget['diagnostic_worlds_all_new'],'Fixed all-branch budget exhausted')
 deadline=datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
 need(datetime.now(timezone.utc)<datetime.fromisoformat('2026-11-10T18:15:00-06:00').astimezone(timezone.utc),'Start before18:15 to retain deadline margin')
 incorporation=read(P/'control/RP_CONTROL_A_PANEL12_INCORPORADA_PI08_R01.json')
 need(incorporation['applied']is True and sha(RP/'recetas'/(RID+'.json'))==incorporation['recipe_sha256']=='54fd4318d8ac25d999c632876715ecd0799b23e7e291ea4c32b7e2b6b8782700','Actual incorporated fixed recipe required')
 cardfile=S/'estado/vidas'/A/'VIDA.json';card=read(cardfile);need(read(S/'estado/ACTIVO.json')['life_id']==A and card['physical']['tick']==861426,'Protected A current principal changed')
 protected={str(p):sha(p)for p in(S/'estado/ACTIVO.json',cardfile,S/card['snapshot'])}
 with MARKER.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'life_id':LIFE,'scope':'Fixed diagnostic RPpanel, not selected Main','Native_bound':BOUND,'new_worlds':1,'allocation_proof_sha256':ALLOCATION_SHA},f)
 sys.path.insert(0,str(S));from app import process_control as pc
 stdout=OUTPUT.with_suffix('.stdout.txt');stderr=OUTPUT.with_suffix('.stderr.txt');started=time.monotonic();samples=[];warnings=[];cleanup=None
 base={'schema':'DEE.PI08.A.RP.panel_owned_supervision.R01','started_utc':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,'destination':str(DEST),'command':command,
  'supervisor_sha256':sha(Path(__file__)),'driver_guard_sha256':sha(GUARD),'memory_limit_bytes':LIMIT,'Native_bound':BOUND,'new_worlds':1,'deadline_utc':deadline.isoformat(),'budget_before':before,'global_mutex':str(MARKER),'automatic_retry':False,'unlogged_kill':False}
 with stdout.open('x',encoding='utf8')as out,stderr.open('x',encoding='utf8')as err:
  proc,job,name=pc.spawn_owned(command,cwd=str(P),stdout=out,stderr=err,memory_limit=LIMIT);base.update(pid=proc.pid,owned_job=name);record({**base,'status':'RUNNING'})
  while True:
   try:
    sample={'at_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-started,'exit_code':proc.poll(),**pc.job_resources(job)};samples.append(sample)
    if proc.poll()is not None and sample.get('job_active_processes')==0:break
    if proc.poll()==0 and sample.get('job_active_processes')==1:
     saved=coherent()
     if saved:
      cleanup={'kind':'EXPLICIT_COHERENT_DIAGNOSTIC_IDLE_JOB_CLOSE','saved_state':saved,'remaining_owned_processes':1,'mechanism':'Logged KILL_ON_JOB_CLOSE for owned idle bridge only; all material requests closed and pending0.'}
      record({**base,'status':'CLOSING_COHERENT_IDLE_BRIDGE','cleanup':cleanup,'samples':samples});pc.close_job(job);job=None;break
    if(datetime.now(timezone.utc)>=deadline or time.monotonic()-started>1200)and not warnings:
     warnings.append({'kind':'TIME_LIMIT_REACHED','at_utc':datetime.now(timezone.utc).isoformat(),'automatic_kill':False,'next':'Per-request guard refuses subsequent Native material input. Supervisor retains job handle; Root must inspect if a bounded current request does not close.'});record({**base,'status':'TIME_LIMIT_LIVE_JOB_PRESERVED','samples':samples,'warnings':warnings});print(json.dumps(warnings[-1]),flush=True)
    time.sleep(.5)
   except KeyboardInterrupt:
    warnings.append({'kind':'ROOT_INTERRUPT_JOB_HANDLE_RETAINED','automatic_kill':False});record({**base,'status':'INTERRUPTION_PRESERVED','samples':samples,'warnings':warnings})
  exitcode=proc.wait(timeout=1)
  if job is not None:
   need(pc.job_resources(job).get('job_active_processes')==0,'Uncertain live job retained');pc.close_job(job)
 saved=coherent();unchanged=protected=={s:sha(Path(s))for s in protected}
 closed=bool(exitcode==0 and saved and saved['Native_bound_met']and unchanged)
 result={**base,'status':'COMPLETED_DIAGNOSTIC'if closed else'STOPPED_FUTURE_PRESERVED','finished_utc':datetime.now(timezone.utc).isoformat(),'exit_code':exitcode,'closed':closed,'actual':saved,'original_A_unchanged':unchanged,
  'elapsed_seconds':time.monotonic()-started,'peak_job_committed_bytes':max(s.get('peak_job_committed_bytes',0)for s in samples),'samples':samples,'warnings':warnings,'explicit_idle_bridge_cleanup':cleanup,
  'stdout':{'path':str(stdout),'sha256':sha(stdout),'bytes':stdout.stat().st_size},'stderr':{'path':str(stderr),'sha256':sha(stderr),'bytes':stderr.stat().st_size},'B_conservation_gate_remains_false':True}
 record(result)
 if closed:
  need(read(MARKER)['pid']==os.getpid(),'Only own Root mutex may be released');MARKER.unlink()
 print(json.dumps({'proof':str(OUTPUT),'sha256':sha(OUTPUT),'status':result['status'],'closed':closed,'actual':saved,'original_A_unchanged':unchanged}));return 0 if closed else 2
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--ejecutar',action='store_true');raise SystemExit(main(parser.parse_args()))
