"""Root-only finite PI10 owned Native driver. Default PLAN never imports DEE.

The plan fixes operations, never selects Native answers. Uses the preserved
diagnostic Owner/queue with one outer512MiB Job and current PI10 budget. No
automatic resend, restart, principal adoption, policy or state repair.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,copy,hashlib,importlib.util,json,os,re,sys,time,types
P=Path(__file__).resolve().parents[1];H=P/'codigo';P9=P.with_name('PROGRESION_INTEGRADA_09');C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';PY=C/'motor/python313/python.exe'
DRIVER=RP/'propietario_diagnostico.py';DRIVER_SHA='e7053088b6492d9d10abe1c861da560de1fb1f4a9d00468661df53782523e52b';PROC=P9/'codigo/comprobar_procesos_adopcion_D_PI09_R01.py';PROC_SHA='9222b2fb422bb3c19d9ed4c5bf1785d2f987dd0d5533ddf9242600a563e22107'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def load(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def require_regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked/reparse execution paths')
def validate_plan(path):
 plan=read(path);system=Path(plan['system']).resolve(strict=True);life=plan['life_id'];steps=plan['steps'];tag=plan['tag']
 need(re.fullmatch(r'PI10_[A-Z0-9_]{1,55}_OWNER_R[0-9]+',tag),'Unique exact PI10 owner phase tag')
 need(system.name=='sistema'and system.parent.parent==(P/'estados').resolve()and not(system/'estado/ACTIVO.json').exists(),'Only explicit unselected PI10 diagnostic system')
 require_regular(system);need(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_[A-Z0-9_]{1,25}',life),'Exact PI10 diagnostic identity')
 need(isinstance(steps,list)and 0<len(steps)<=64,'Finite nonempty operation plan')
 for step in steps:
  need(type(step.get('max_ticks'))is int and 0<=step['max_ticks']<=5000 and isinstance(step.get('literal'),dict),'Bounded literal each step')
  need(set(step)<={'label','literal','max_ticks','feedback','actuator','expect_prequeue_rejection','expected','read_path'},'No hidden selector/target binding in driver')
  need(step.get('feedback','omit')in('real','omit')and step.get('actuator','closed')=='closed','Closed fixed actuator only')
  need(not step.get('expect_prequeue_rejection')or step['max_ticks']==0,'A rejection test has zero Native allowance')
 return plan,system,life,tag,sum(s['max_ticks']for s in steps)
def ledger():
 file=H/'ledger_PI10_R01.py';need(sha(file)=='55ec5b9b131f251a7b452b19adc2df38a07eaf54ab049804f2205359631a3ff3','Reviewed PI10 ledger changed')
 return load('PI10_exact_aggregate_ledger',file).ledger()
def passive_snapshot(system,card):
 parser=load('PI10_exact_frozen_saved_snapshot',RP/'observador_pasivo.py');v=parser.snapshot_view(system/card['snapshot'])
 need(v['encoded_sha256']==card['snapshot_sha256']and all(v['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Saved physical/card mismatch')
 return {k:v[k]for k in('physical','encoded_sha256','causal_prefix_sha256','interfaces','pending_native','native_receipts','phase','scope')}
def main(a):
 planpath=a.plan.resolve(strict=True);need(planpath.parent==H.resolve(),'Explicit local frozen finite plan only');plan,system,life,tag,bound=validate_plan(planpath)
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY_NO_DEE_IMPORT','life_id':life,'steps':len(plan['steps']),'finite_bound':bound,'plan_sha256':sha(planpath)}));return
 need(Path(sys.executable).resolve()==PY.resolve(),'Root official Python only')
 need(a.plan_sha256==sha(planpath),'Actual externally supplied frozen plan SHA required')
 budget=read(P/'REGISTRO_CAMPANA.json')['budget'];cutoff=datetime.fromisoformat(budget['new_experimental_uses_cutoff_utc']).astimezone(timezone.utc);hard=datetime.fromisoformat(budget['hard_finish_utc']).astimezone(timezone.utc)
 need(datetime.now(timezone.utc)<cutoff,'No new Native phase after prospective cutoff')
 prior=ledger();need(prior['charged_ticks']+bound<=budget['Native_ticks_all_new_branches']and prior['world_count']<=budget['new_worlds_all'],'Aggregate Native/world budget insufficient')
 need(sum(f.stat().st_size for f in P.rglob('*')if f.is_file())+budget['closing_storage_reserve_bytes']<budget['new_logical_storage_bytes'],'Preserve closing storage reserve')
 context=read(system.parent/'CONTEXTO_EJECUCION.json');code=system.parent/'SISTEMA_CODIGO_PI10.json';need(context.get('PI10_actor_ready')and context['source_code_manifest_sha256']==sha(code),'Exact actor/code closure not ready')
 for row in read(code)['files']:need(sha(system/row['file'])==row['sha256'],'Prepared source changed: '+row['file'])
 need(sha(DRIVER)==DRIVER_SHA and sha(PROC)==PROC_SHA,'Reviewed diagnostic/process helpers changed')
 cardfile=system/'estado/vidas'/life/'VIDA.json';card=read(cardfile);initial=card['physical']['tick'];need(initial==plan['initial_tick']and sha(system/card['snapshot'])==card['snapshot_sha256'],'Stale source/corrupt checkpoint; never reset')
 need(not(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists(),'Preserve interrupted future before any new writer');initial_native=passive_snapshot(system,card)
 process=load('PI10_finite_process_guard',PROC).inspect('PI10_diagnostic_before',system,life);need(process['no_live_affected_writer'],'Affected process/queue not proven closed')
 marker=P/'PI10_ROOT_NATIVE_WRITER.lock';proof=P/'control'/(tag+'.json');intent=proof.with_suffix('.INTENT.json')
 need(not marker.exists()and not(RP/'EJECUCION_MATERIAL.lock').exists()and not proof.exists()and not intent.exists(),'Never overlap or retry an uncertain writer/phase')
 active=C/'sistema/estado/ACTIVO.json';selected=read(active)['life_id'];acard=C/'sistema/estado/vidas'/selected/'VIDA.json';protected=[active,acard,C/'sistema'/read(acard)['snapshot']];before={str(p):sha(p)for p in protected}
 pins={str(Path(k).resolve(strict=True)):v for k,v in plan.get('pins',{}).items()};pins[str(planpath)]=sha(planpath);pins[str(code)]=sha(code);need(all(sha(Path(k))==v for k,v in pins.items()),'Frozen plan/code pins changed')
 write(intent,{'schema':'DEE.PI10.prospective.owner_intent.R01','life_id':life,'initial_tick':initial,'finite_bound':bound,'proof':str(proof),'plan_sha256':sha(planpath),'started_utc':datetime.now(timezone.utc).isoformat()});write(marker,{'pid':os.getpid(),'life_id':life,'tag':tag,'finite_bound':bound,'phase':'OWNED_NATIVE_DRIVER'})
 max_seconds=min(int(plan.get('max_host_seconds',1800)),int((hard-datetime.now(timezone.utc)).total_seconds())-90);need(60<=max_seconds<=7200,'A finite safe owner interval must fit the hard stop')
 source=DRIVER.read_text('utf-8-sig');anchor="'--max-segundos','7200'";need(source.count(anchor)==1,'Literal owner finite-runtime command changed');source=source.replace(anchor,"'--max-segundos',str(ROOT_MAX_SECONDS)");ast.parse(source)
 d=types.ModuleType('PI10_literal_owned_driver_finite_runtime_only');d.__file__=str(DRIVER);d.ROOT_MAX_SECONDS=max_seconds;exec(compile(source,str(DRIVER)+':PI10_finite_host_runtime_only','exec'),d.__dict__);d.configure(P,system,PY);owner=None;error=None;records=[];cursor=initial
 try:
  owner=d.Owner(life,tag)
  with owner:
   for index,step in enumerate(plan['steps']):
    need(datetime.now(timezone.utc)<cutoff,'Cutoff reached before next use');need(all(sha(Path(k))==v for k,v in pins.items()),'Frozen source changed')
    identifier=tag+'_%02d'%index;literal=copy.deepcopy(step['literal']);payload={'operacion':'sesion','situaciones':[literal],'retorno':step.get('feedback','omit'),'actuador':'closed'}
    if step.get('expect_prequeue_rejection'):
     before_snapshot=sha(system/read(cardfile)['snapshot']);rejected=None
     try:owner.q.put(identifier,payload)
     except ValueError as exc:rejected={'type':type(exc).__name__,'message':str(exc)}
     need(rejected is not None and owner.q.get(identifier)is None and sha(system/read(cardfile)['snapshot'])==before_snapshot,'Malformed literal was admitted or changed saved world; preserve')
     records.append({'index':index,'id':identifier,'label':step.get('label',str(index)),'literal':literal,'before_tick':cursor,'after_tick':cursor,'ticks':0,'prequeue_rejection':rejected,'no_Native_request':True});continue
    result=owner.material(identifier,literal,feedback=step.get('feedback','omit'),actuator='closed',allow_failure=True)
    need('before_tick'in result and'after_tick'in result,'Missing complete receipt; SAME id retained')
    delta=result['after_tick']-result['before_tick'];need(result['before_tick']==cursor and 0<=delta<=step['max_ticks'],'Unexpected advance/phase horizon; preserve actual future');cursor=result['after_tick']
    primary=P/'ensayos'/(identifier+'.json');rec={'index':index,'id':identifier,'label':step.get('label',str(index)),'literal':literal,'before_tick':result['before_tick'],'after_tick':cursor,'ticks':delta,'primary':str(primary),'sha256':sha(primary),'rows':result.get('result',{}).get('rows',[])}
    if step.get('read_path'):
     actual=result
     for key in step['read_path']:actual=actual[key]
     rec.update(actual=actual,expected=step.get('expected'),correct=actual==step['expected']if'expected'in step else None)
    records.append(rec);need(result.get('status','completed')not in('failed_preserved','uncertain','rejected_invalid'),'Failed future preserved, no resend')
   owner.control('guardar')
 except BaseException as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
 # Do not drop a live KILL_ON_CLOSE Job handle after a readiness/close error.
 # Its own manager has a finite runtime. Keep the only writer visible; Root
 # can inspect the exact PID. No second owner or unlogged terminate follows.
 if owner is not None and owner.proc is not None and owner.proc.poll()is None:
  live=P/'control'/(tag+'.OWNER_VIVO.json')
  if not live.exists():write(live,{'schema':'DEE.PI10.owned_handle_retained_after_error.R01','pid':owner.proc.pid,'life_id':life,'automatic_retry':False,'forced_kill':False,'error':error})
  while owner.proc.poll()is None:
   try:owner.sample();time.sleep(.1)
   except KeyboardInterrupt:pass
  if owner.job is not None:d.pc.close_job(owner.job);owner.job=None
 closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'));after={str(p):sha(p)for p in protected}
 if before!=after:error={'type':'PRINCIPAL_CHANGED','automatic_retry':False}
 final=read(cardfile);closed_guard=None;final_native=passive_snapshot(system,final)
 if closed:
  closed_guard=load('PI10_finite_process_guard_after',PROC).inspect('PI10_diagnostic_after',system,life)
  if not closed_guard['no_live_affected_writer']:error={'type':'CLOSED_PROCESS_OR_QUEUE_NOT_PROVEN','automatic_retry':False}
 output={'schema':'DEE.PI10.actual.finite_owner_plan.R01','status':'CLOSED_FINITE_PHASE'if closed and error is None else'STOPPED_PRESERVED','life_id':life,'tag':tag,'plan':str(planpath),'plan_sha256':sha(planpath),'initial_tick':initial,'final_tick':final['physical']['tick'],'new_Native_ticks':final['physical']['tick']-initial,'finite_bound':bound,'closed':closed,'error':error,'records':records,'protected_before':before,'protected_after':after,'ledger_before':prior,'closed_process_queue':closed_guard,'initial_saved_Native':initial_native,'final_saved_Native':final_native,'no_adoption':True,'outer_job_memory_limit_bytes':536870912,'owner_finite_host_max_seconds':max_seconds,'literal_driver_adaptation':'Only max-segundos argument, chosen before opening from fixed plan/hard deadline; no Native selector or feedback changes','hard_finish_utc':hard.isoformat()};write(proof,output)
 if closed and marker.exists():marker.unlink()
 print(json.dumps({'proof':str(proof),'status':output['status'],'error':error,'new_Native_ticks':output['new_Native_ticks'],'final_tick':output['final_tick'],'operations':len(records)},ensure_ascii=False))
 if error:raise SystemExit(1)
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--plan-sha256');ap.add_argument('--ejecutar',action='store_true');main(ap.parse_args())
