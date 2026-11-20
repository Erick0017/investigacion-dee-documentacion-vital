"""Freeze evaluator-only expectations from the actual CLOSED canonical12.

Never passes observations/expected values into actor literals. Does not read
live state, import DEE, register RP or execute its material route.
"""
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;P=H.parent;SOURCE=H/'RP_CAPSULA_PI09_R03_PROPUESTA';OUT=H/'RECETA_RP_PI09_NATIVE12_R01_FIJADA'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def get(v,path):
 for key in path:v=v[key]
 return v
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n')
def main():
 require(not OUT.exists(),'Expectativas anteriores preservadas')
 proof_file=P/'control/PI09_NATIVE_R03.json';proof=read(proof_file)
 require(proof['closed']is True and proof['error']is None and proof['life_id']==LIFE and proof['initial_tick']==884835 and proof['final_tick']==903603 and proof['new_Native_ticks']==18768,'Sólo el cierre Native12 real fijado')
 records=[r for r in proof['records']if r['label'].startswith('EP')];require(len(records)==12,'Doce primarios reales completos requeridos')
 recipe=read(SOURCE/'recipe_PREPARADA.json');steps=recipe['variants']['native12']['batches'][0];episodes=[s for s in steps if s['label'].startswith('EP_')]
 checks=[];frozen=[];all_receipts={}
 paths=[['first_stage','reader'],['first_stage','native_motor'],['first_stage','actual_query_motor'],['first_stage','sample_register'],['second_stage','reader'],['second_stage','native_motor'],['second_stage','actual_motor'],['second_stage','FI','early_physical_choice'],['second_stage','pulse_applied'],['second_stage','message'],['actual_failed'],['returned_failed'],['extra_bit_entered_second_TC'],['Native_inputs'],['whole_new_native_ticks']]
 for index,(record,step)in enumerate(zip(records,episodes)):
  file=Path(record['primary']).resolve(strict=True);require(file.parent==(P/'ensayos').resolve()and sha(file)==record['sha256'],'Cambió el primario de origen')
  row=record['rows'][0];require(row['ordinal']==index and row['old_metadata_literal_unchanged']is True and row['Native_inputs']['all_terminal']is True,'Fase o recibos de origen incompletos')
  require(record['ticks']==1564 and row['whole_new_native_ticks']==1564 and row['before_prepared_wait']==record['before_tick']and row['after_tick']==record['after_tick'],'Calendario real inesperado')
  step['expected']=row['first_stage']['reader']['choice'];step['stop_on_NULL']=True
  for path in paths:
   expected=get(row,path);checks.append({'label':step['label']+'_'+'.'.join(path),'operation':'value','values':[{'step':step['label'],'path':['result','rows',0,*path]}],'expected':expected})
  for request in row['requests']:
   rid=request['id'];require(rid==request['receipt']['id'],'Alias Native incoherente')
   if rid in all_receipts:require(all_receipts[rid]==request['receipt'],'Recibo Native contradictorio')
   all_receipts[rid]=request['receipt']
  frozen.append({'ordinal':index,'primary':{'path':str(file),'sha256':sha(file)},'before_tick':record['before_tick'],'after_tick':record['after_tick'],'first_choice':row['first_stage']['reader']['choice'],'second_choice':row['second_stage']['reader']['choice'],'question_applied':row['first_stage']['sample_register']['question_applied'],'actual_failed':row['actual_failed'],'Native_inputs':row['Native_inputs']})
 statuses=[r['status']for r in all_receipts.values()];dose={'unique_requested':len(all_receipts),'applied':statuses.count('applied'),'rejected':sum(x.startswith('rejected')for x in statuses),'pending_or_other':sum(x!='applied'and not x.startswith('rejected')for x in statuses)}
 variant=recipe['variants']['native12'];variant['final_checks']=checks;variant['native_receipt_expectations']=dose
 require(sum(r['question_applied']for r in frozen)==8 and not any(r['actual_failed']for r in frozen)and all(r['first_choice']is not None for r in frozen),'El cierre actual no coincide con los denominadores declarados')
 recipe.update(revision='R03_ACTUAL_NATIVE12_EXPECTATIONS_FROZEN',reproduction_enabled=True)
 recipe['verification'].update(state='PREPARADA_REPLAY_NATIVE_PENDIENTE',expected_observables_frozen=True,Native_replay_verified=False,canonical_actual_closed=True)
 recipe['sources']['actual_canonical12']={'path':str(proof_file),'sha256':sha(proof_file),'tick':903603,'new_Native_ticks':18768,'snapshot_sha256':'be148b940159a48fecc94526656574e0e698860d283f91d7fb424bc1b128d982','post12_manifest_sha256':'0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553'}
 recipe['variants']['native12']['interpretation']='Replay fixed Native-real12 from complete C. Auditor-only expectations are actual canonical observations. Equality is distinct from cognitive generalization. No environment expected value is passed to actor.'
 write(OUT/'receta.json',recipe)
 write(OUT/'EXPECTATIVAS.json',{'schema':'DEE.PI09.actual_canonical12.evaluator_expectations.R01','source':recipe['sources']['actual_canonical12'],'episodes':frozen,'whole_receipts':dose,'all_reads_from_closed_immutable_evidence':True,'expected_values_never_actor_inputs':True,'Native_executed':False})
 write(OUT/'PLAN.json',{'schema':'DEE.PI09.RP.recipe_expectations_frozen.R01','recipe':recipe['id'],'recipe_sha256':sha(OUT/'receta.json'),'expectations_sha256':sha(OUT/'EXPECTATIVAS.json'),'capsule_manifest_sha256':sha(SOURCE/'capsule/SISTEMA_CODIGO.json'),'new_RP_frontdoor_Native_replay_executed':False,'requires_Root_registration_review':True,'Native_executed':False})
 print(json.dumps({'prepared':str(OUT),'recipe':recipe['id'],'recipe_sha256':sha(OUT/'receta.json'),'checks':len(checks),'dose':dose,'Native_executed':False}))
if __name__=='__main__':main()
