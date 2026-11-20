"""Root-only finite preregistered phases on one already imported PI06 clone.

No new life, selection, correction, reinjection, restart or answer-dependent
branch. All literal operations are fixed in a sealed plan before owner start.
The host controls execution/calendar/measurement; this runner proves no agency.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
MAIN='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked plan/source/world path')
def budget_ticks():
 total=0;rows=[];root=S/'estado/vidas'
 for folder in sorted(root.iterdir()):
  if not folder.is_dir():continue
  regular(folder);card=read(folder/'VIDA.json');start=card.get('parent',{}).get('source_tick')
  if type(start)is not int:raise ValueError('Each diagnostic must have an explicit imported prefix; no invented T0')
  delta=card['physical']['tick']-start
  if delta<0:raise ValueError('Diagnostic age regressed')
  total+=delta;rows.append({'life_id':card['life_id'],'import_tick':start,'saved_tick':card['physical']['tick'],'Native_delta':delta})
 record=read(P/'REGISTRO_CAMPANA.json')
 return max(total,int(record.get('Native_ticks_closed',0))),rows,record
def main(a):
 if not re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI06_[A-Za-z0-9_]{1,24}',a.vida):raise ValueError('Explicit PI06 diagnostic ID only')
 if not re.fullmatch(r'[A-Za-z0-9_]{1,60}',a.tag):raise ValueError('One fresh bounded transport tag')
 planpath=a.plan.resolve(strict=True);regular(planpath)
 if not planpath.is_relative_to(P.resolve()):raise ValueError('Only the declared existing PI06 campaign plan')
 data=planpath.read_bytes();plan=json.loads(data)
 if plan.get('schema')!='DEE.PI06.fixed_phase_plan.v1'or plan.get('status')!='SEALED':raise ValueError('Exact sealed prospective plan required')
 if set(plan)-{'schema','status','initial_tick','max_native_ticks','steps','description','source_proof','registration_utc'}:raise ValueError('No hidden policy/target/reader configuration in a runner plan')
 steps=plan['steps']
 if type(steps)is not list or not 1<=len(steps)<=256:raise ValueError('A finite1..256-step phase only')
 labels=set();declared=0
 for step in steps:
  if set(step)-{'label','literal','max_native_ticks','expected_new_ticks','feedback','actuator'}:raise ValueError('Only explicit literal and finite tick bounds per step')
  if not re.fullmatch(r'[A-Za-z0-9_]{1,40}',step['label'])or step['label']in labels:raise ValueError('Fresh unique step labels only')
  labels.add(step['label'])
  if type(step['max_native_ticks'])is not int or not 0<=step['max_native_ticks']<=20000:raise ValueError('Finite0..20000 tick bound per material request')
  declared+=step['max_native_ticks']
  if step.get('feedback','omit')not in('real','omit')or step.get('actuator','closed')not in('closed','nulled'):raise ValueError('Existing feedback/actuator contracts only')
  literal=step['literal']
  if type(literal)is not dict or not isinstance(literal.get('modo'),str)or not literal['modo'].startswith(('eci01-pi06-','eci01-pi04-c2c-','eci01-pi05-')):raise ValueError('Fixed reviewed PI06 or inherited explicit operation only')
 if type(plan['max_native_ticks'])is not int or declared>plan['max_native_ticks']:raise ValueError('Plan does not cover its full declared budget')
 if (S/'estado/ACTIVO.json').exists():raise ValueError('A diagnostic system never selects a principal')
 locks=S/'estado/locks'
 if locks.exists()and any(locks.iterdir()):raise ValueError('An isolated writer/lock is present; wait for proven close')
 if sum(1 for x in(S/'estado/vidas').iterdir()if x.is_dir())>12:raise ValueError('Frozen12-world limit exceeded')
 cardpath=S/'estado/vidas'/a.vida/'VIDA.json';regular(cardpath);card=read(cardpath)
 if card['physical']['N']!=67 or card['physical']['tick']!=plan['initial_tick']:raise ValueError('Actual current clone cut differs from the preregistration')
 if (cardpath.parent/'FUTURO_INTERRUMPIDO.json').exists():raise ValueError('Preserve an interrupted future; do not retry')
 imported=S/'estado/servicios_persistentes'/a.vida/'IMPORTACION.json'
 if not imported.is_file():raise ValueError('A complete paired clone is mandatory')
 proofpath=P/'control'/(a.tag+'.json');writer=P/'PI06_ROOT_NATIVE_WRITER.lock'
 if proofpath.exists()or writer.exists():raise FileExistsError('Fresh phase tag and one campaign writer only; no blind retry')
 total,lives,record=budget_ticks();limit=record['budget']['Native_ticks_all_branches']
 if total+declared>limit:raise ValueError('Frozen all-branch Native budget would be exceeded')
 if datetime.now(timezone.utc)>=datetime.fromisoformat(record['science_cutoff_local']).astimezone(timezone.utc):raise ValueError('Science cutoff reached; preserve and close')
 ccard=C/'sistema/estado/vidas'/MAIN/'VIDA.json';sourcecard=read(ccard)
 protected=[C/'sistema/estado/ACTIVO.json',ccard,C/'sistema'/sourcecard['snapshot']]
 protected_before={str(p):sha(p)for p in protected}
 with writer.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'life_id':a.vida,'plan':str(planpath),'plan_sha256':hashlib.sha256(data).hexdigest()},f)
 outcomes=[];owner=None;error=None
 try:
  sys.path.insert(0,str(P/'codigo'));from servicio_ensayo_PI06 import Owner
  owner=Owner(a.vida,a.tag)
  with owner:
   for step in steps:
    if datetime.now(timezone.utc)>=datetime.fromisoformat(record['science_cutoff_local']).astimezone(timezone.utc):raise ValueError('Science cutoff reached between operations')
    rid=a.tag+'_'+step['label'];outcome=owner.material(rid,step['literal'],feedback=step.get('feedback','omit'),actuator=step.get('actuator','closed'),allow_failure=True)
    outcomes.append({'label':step['label'],'id':rid,'before_tick':outcome.get('before_tick'),'after_tick':outcome.get('after_tick'),
      'primary':str(P/'ensayos'/(rid+'.json')),'primary_sha256':sha(P/'ensayos'/(rid+'.json'))})
    if 'before_tick'not in outcome or 'after_tick'not in outcome:raise RuntimeError('No completed Native result; same ID/future preserved, no automatic retry')
    delta=outcome['after_tick']-outcome['before_tick']
    if not 0<=delta<=step['max_native_ticks']:raise RuntimeError('Actual step exceeds preregistered finite Native bound')
    if 'expected_new_ticks'in step and delta!=step['expected_new_ticks']:raise RuntimeError('Unexpected schedule/age; preserve actual future without correction')
    rows=outcome.get('result',{}).get('rows',[])
    if len(rows)==1 and isinstance(rows[0],dict)and isinstance(rows[0].get('Native_inputs'),dict):
     inputs=rows[0]['Native_inputs']
     if (type(inputs.get('unique_requested'))is not int or type(inputs.get('applied'))is not int or
         inputs.get('rejected_or_other')!=0 or inputs['applied']!=inputs['unique_requested']):
      raise RuntimeError('Declared current-operation Native input admission is incomplete; preserve actual result and stop')
    if planpath.read_bytes()!=data:raise RuntimeError('Sealed phase plan changed during execution')
   owner.control('guardar')
 except Exception as e:error={'type':type(e).__name__,'message':str(e),'automatic_retry':False}
 after=read(cardpath);closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
 protected_after={str(p):sha(p)for p in protected}
 if protected_after!=protected_before:error={'type':'PROTECTED_MAIN_CHANGED','message':'Actual principal advanced/changed concurrently; no overwrite or adoption allowed','automatic_retry':False}
 result={'schema':'DEE.PI06.fixed_phase_execution.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),'life_id':a.vida,
  'status':'CLOSED'if error is None and closed else'FAILED_PRESERVED','closed':closed,'plan':str(planpath),'plan_sha256':hashlib.sha256(data).hexdigest(),
  'initial_tick':card['physical']['tick'],'final_tick':after['physical']['tick'],'new_ticks':after['physical']['tick']-card['physical']['tick'],
  'final_snapshot_sha256':after['snapshot_sha256'],'outcomes':outcomes,'error':error,'budget_before':{'Native_ticks_all_branches':total,'lives':lives},
  'protected_main_before':protected_before,'protected_main_after':protected_after,'protected_main_unchanged':protected_before==protected_after,
  'selection_modified':False,'corrective_operation_added':False,'plan_does_not_prove_agent_initiative':True}
 with proofpath.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 if closed:
  if read(writer).get('pid')!=os.getpid():raise RuntimeError('Campaign writer marker changed; preserve')
  writer.unlink()
 print(json.dumps({'proof':str(proofpath),'sha256':sha(proofpath),'status':result['status'],'closed':closed,'new_ticks':result['new_ticks'],'error':error},ensure_ascii=False))
 return 0 if result['status']=='CLOSED' else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--tag',required=True);raise SystemExit(main(ap.parse_args()))
