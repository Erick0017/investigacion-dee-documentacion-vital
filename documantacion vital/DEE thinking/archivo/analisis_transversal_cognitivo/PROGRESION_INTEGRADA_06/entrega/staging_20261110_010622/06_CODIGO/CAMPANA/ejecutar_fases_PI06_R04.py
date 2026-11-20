"""Root-only R04 finite environment plan, separate from all already used runners.

No new life, selection, correction, reinjection, restart or answer-dependent
branch. All literal operations are fixed in a sealed plan before owner start.
The host controls execution/calendar/measurement; this runner proves no agency.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,re,sys
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';S=P/'estados/candidato/sistema'
MAIN='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
R04_PLANS={'PLAN_CONFIRMACION_FINA_PI06_R04.json':('64fef6625e73e6890720850fee153268695f9455443608fac0ef5a69fad44a23','ECI02_PI03_REPRO_PI04_PI05_PI06_R03_FINE_01','eci01-pi06-ambiente-fino'),
 'PLAN_CONFIRMACION_CONTROL67_PI06_R04.json':('3ad0f1ec8a1961aad6a039a0e93ec5ee44c689b1d85ecd8a2afd2d7c0561c59b','ECI02_PI03_REPRO_PI04_PI05_PI06_DISC_01','eci01-pi06-control67')}
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked plan/source/world path')
def r04_plan_enabled(life,planpath,data,steps,initial_tick):
 expected=R04_PLANS.get(planpath.name)
 return bool(expected and expected[0]==hashlib.sha256(data).hexdigest()and life==expected[1]and initial_tick==826449 and
  steps and steps[0]['literal']['modo']==expected[2])

def r04_fi_terminal_admission(row,outcome,literal,enabled):
 if not enabled or literal.get('modo')!='eci01-pi06-fiplus'or literal.get('condicion')!='intacto':return False
 inputs=row.get('Native_inputs',{});included={}
 for request in row.get('requests',[]):
  receipt=request['receipt'];rid=request['id']
  if rid!=receipt['id']or not outcome['before_tick']<=receipt['requested_tick']<=outcome['after_tick']or(rid in included and included[rid]!=receipt):raise RuntimeError('Invalid current FI receipt identity/window')
  included[rid]=receipt
 return (len(included)==inputs.get('unique_requested')==176 and
  all(v['status']in('applied','rejected_occupied')for v in included.values())and
  sum(v['status']=='applied'for v in included.values())==inputs.get('applied')and
  sum(v['status']=='rejected_occupied'for v in included.values())==inputs.get('rejected_or_other'))
def budget_ticks():
 total=0;rows=[];stores={S.resolve()};seen=set()
 for child in(P/'estados').iterdir():
  candidate=child/'sistema'
  if child.is_dir()and(candidate/'estado/vidas').is_dir():stores.add(candidate.resolve())
 registry=RP/'EJECUCIONES'
 if registry.is_dir():
  for file in registry.glob('*PI06_*.json'):
   record=read(file);dest=Path(record['destination']).resolve(strict=True)
   if not(dest.is_relative_to((P/'estados').resolve())or dest.is_relative_to((RP/'diagnosticos').resolve())):raise ValueError('A registered PI06 Native replay lies outside the bounded campaign/reproducibility stores')
   if not(dest/'sistema/estado/vidas').is_dir():raise ValueError('Do not drop a registered Native history whose local state is missing')
   stores.add(dest/'sistema')
 for system in sorted(stores):
  root=system/'estado/vidas'
  for folder in sorted(root.iterdir()):
   if not folder.is_dir():continue
   regular(folder);card=read(folder/'VIDA.json');start=card.get('parent',{}).get('source_tick')
   if card['life_id']in seen:raise ValueError('Diagnostic identity duplicated across stores; reconcile instead of double counting')
   seen.add(card['life_id'])
   if type(start)is not int:raise ValueError('Each diagnostic must have an explicit imported prefix; no invented T0')
   delta=card['physical']['tick']-start
   if delta<0:raise ValueError('Diagnostic age regressed')
   total+=delta;rows.append({'system':str(system),'life_id':card['life_id'],'import_tick':start,'saved_tick':card['physical']['tick'],'Native_delta':delta})
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
 if (RP/'EJECUCION_MATERIAL.lock').exists():raise ValueError('An RP material owner is active or uncertain; one campaign Native writer only')
 if sum(1 for x in(S/'estado/vidas').iterdir()if x.is_dir())>12:raise ValueError('Frozen12-world limit exceeded')
 cardpath=S/'estado/vidas'/a.vida/'VIDA.json';regular(cardpath);card=read(cardpath)
 if card['physical']['N']!=67 or card['physical']['tick']!=plan['initial_tick']:raise ValueError('Actual current clone cut differs from the preregistration')
 if (cardpath.parent/'FUTURO_INTERRUMPIDO.json').exists():raise ValueError('Preserve an interrupted future; do not retry')
 imported=S/'estado/servicios_persistentes'/a.vida/'IMPORTACION.json'
 if not imported.is_file():raise ValueError('A complete paired clone is mandatory')
 proofpath=P/'control'/(a.tag+'.json');writer=P/'PI06_ROOT_NATIVE_WRITER.lock'
 if proofpath.exists()or writer.exists():raise FileExistsError('Fresh phase tag and one campaign writer only; no blind retry')
 total,lives,record=budget_ticks();limit=record['budget']['Native_ticks_all_branches']
 if len(lives)>record['budget']['diagnostic_worlds_max']:raise ValueError('All-store diagnostic-world limit exceeded; no reset by moving a life')
 if total+declared>limit:raise ValueError('Frozen all-branch Native budget would be exceeded')
 if datetime.now(timezone.utc)>=datetime.fromisoformat(record['science_cutoff_local']).astimezone(timezone.utc):raise ValueError('Science cutoff reached; preserve and close')
 ccard=C/'sistema/estado/vidas'/MAIN/'VIDA.json';sourcecard=read(ccard)
 protected=[C/'sistema/estado/ACTIVO.json',ccard,C/'sistema'/sourcecard['snapshot']]
 protected_before={str(p):sha(p)for p in protected}
 r04_policy=r04_plan_enabled(a.vida,planpath,data,steps,plan['initial_tick'])
 if not r04_policy:raise ValueError('Only the two exact R04 fine/control67 plans with their respective fixed life IDs')
 with writer.open('x',encoding='utf8')as f:json.dump({'pid':os.getpid(),'life_id':a.vida,'plan':str(planpath),'plan_sha256':hashlib.sha256(data).hexdigest()},f)
 outcomes=[];owner=None;error=None;preserved_stop=None;partial_fi_admission=False
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
    rows=outcome.get('result',{}).get('rows',[])
    row=rows[0]if len(rows)==1 and isinstance(rows[0],dict)else{}
    if r04_policy and row.get('host_safety_stop')is True:
     preserved_stop={'kind':'HOST_SAFETY','label':step['label'],'reason':row.get('host_safety_reason'),'not_Native_autoregulation':True};break
    if r04_policy and row.get('admission_stop')is True:
     preserved_stop={'kind':'UNRESOLVED_OR_UNEXPECTED_ADMISSION','label':step['label'],'birth_inputs':row.get('birth_inputs'),'automatic_retry':False};break
    if 'expected_new_ticks'in step and delta!=step['expected_new_ticks']:raise RuntimeError('Unexpected schedule/age; preserve actual future without correction')
    if len(rows)==1 and isinstance(rows[0],dict)and isinstance(rows[0].get('Native_inputs'),dict):
     inputs=rows[0]['Native_inputs']
     relaxed=r04_fi_terminal_admission(row,outcome,step['literal'],r04_policy)
     if relaxed:
      if relaxed and inputs.get('rejected_or_other',0)>0:partial_fi_admission=True
     if not relaxed and(type(inputs.get('unique_requested'))is not int or type(inputs.get('applied'))is not int or
         inputs.get('rejected_or_other')!=0 or inputs['applied']!=inputs['unique_requested']):
      raise RuntimeError('Declared current-operation Native input admission is incomplete; preserve actual result and stop')
    if r04_policy and step['literal']['modo']in('eci01-pi06-ambiente-fino','eci01-pi06-control67'):
     birth=row.get('birth_inputs',{});expected=61 if step['literal']['modo']=='eci01-pi06-ambiente-fino'else 0
     if birth.get('unique_requested')!=expected or birth.get('terminal_all_known')is not True:raise RuntimeError('The fixed environment has unknown/missing admission receipts')
    if planpath.read_bytes()!=data:raise RuntimeError('Sealed phase plan changed during execution')
   owner.control('guardar')
 except Exception as e:error={'type':type(e).__name__,'message':str(e),'automatic_retry':False}
 after=read(cardpath);closed=bool(owner is not None and owner.proc is not None and owner.proc.poll()==0 and not(owner.q.get_meta('owner')or{}).get('running'))
 protected_after={str(p):sha(p)for p in protected}
 if protected_after!=protected_before:error={'type':'PROTECTED_MAIN_CHANGED','message':'Actual principal advanced/changed concurrently; no overwrite or adoption allowed','automatic_retry':False}
 status='FAILED_PRESERVED'if error is not None or not closed else('CLOSED'if preserved_stop is None else preserved_stop['kind']+'_STOP_CLOSED')
 result={'schema':'DEE.PI06.fixed_phase_execution.R04_host_safety_and_terminal_admission','recorded_utc':datetime.now(timezone.utc).isoformat(),'life_id':a.vida,
  'status':status,'closed':closed,'plan':str(planpath),'plan_sha256':hashlib.sha256(data).hexdigest(),
  'initial_tick':card['physical']['tick'],'final_tick':after['physical']['tick'],'new_ticks':after['physical']['tick']-card['physical']['tick'],
  'final_snapshot_sha256':after['snapshot_sha256'],'outcomes':outcomes,'error':error,'budget_before':{'Native_ticks_all_branches':total,'lives':lives},
  'protected_main_before':protected_before,'protected_main_after':protected_after,'protected_main_unchanged':protected_before==protected_after,
  'selection_modified':False,'corrective_operation_added':False,'plan_does_not_prove_agent_initiative':True,
  'R04_terminal_occupied_policy_enabled':r04_policy,'preserved_stop':preserved_stop,'full_plan_completed':len(outcomes)==len(steps)and preserved_stop is None,
  'historical_full176_FI_preservation_not_claimed':partial_fi_admission,
  'admission_scope':'Only two preregistered fine/control67 plans and their exact life IDs permit terminal rejected_occupied in fixed FI or material supply. Counts, zeros and NULL remain unchanged; no quality/preservation success is inferred.'}
 with proofpath.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 if closed:
  if read(writer).get('pid')!=os.getpid():raise RuntimeError('Campaign writer marker changed; preserve')
  writer.unlink()
 print(json.dumps({'proof':str(proofpath),'sha256':sha(proofpath),'status':result['status'],'closed':closed,'new_ticks':result['new_ticks'],'error':error},ensure_ascii=False))
 return 0 if result['status']in('CLOSED','HOST_SAFETY_STOP_CLOSED') else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True);ap.add_argument('--plan',type=Path,required=True);ap.add_argument('--tag',required=True);raise SystemExit(main(ap.parse_args()))
