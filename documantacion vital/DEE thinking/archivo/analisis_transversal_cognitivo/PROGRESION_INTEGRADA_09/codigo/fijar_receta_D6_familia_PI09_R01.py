"""Freeze auditor-only D6 expectations from actual closed Real6 evidence."""
from pathlib import Path
import argparse,hashlib,json,shutil
H=Path(__file__).resolve().parent;P=H.parent;CAPSULE=H/'RP_D_FAMILIA_R01_PREPARADA/capsule';RID='pi09_d6_familia_desde_DISCOVERY_T907543_R01';CAP='PI09_D_FAMILIA_R01';ALIAS='PI09_DISCOVERY_PRE_D_T907543';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def get(v,path):
 for k in path:v=v[k]
 return v
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n','utf8')
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--closed-proof',type=Path,required=True);ap.add_argument('--destino',type=Path,default=H/'RP_D6_EXPECTATIVAS_R01');a=ap.parse_args();proof=a.closed_proof.resolve(strict=True);out=a.destino.resolve();need(proof.is_relative_to((P/'control').resolve())and out.is_relative_to(H.resolve())and not out.exists(),'Actual immutable closed proof and fresh codigo proposal only');p=read(proof)
 need(p.get('schema')=='DEE.PI09.D.actual.finite_owner_phase.R03'and p.get('life_id')==LIFE and p.get('arm')=='real'and p.get('closed')is True and p.get('error')is None and p.get('protected_before')==p.get('protected_after'),'Only actual protected Real D phase closure')
 eps=[r for r in p['records']if r.get('literal',{}).get('modo')=='eci01-pi09-d-episodio'];need(len(eps)==6 and [r['rows'][0]['ordinal']for r in eps]==list(range(6)),'Exactly first six D evaluations; no future or partial source')
 seal=read(H/'SELLO_PI09_D_R02.json');need(p['initial_tick']in(907543,907546)and seal['source_prefix']['tick']==907543,'Actual fixed pre-D source and preparation boundary required')
 prepar=[r for r in p['records']if r.get('literal',{}).get('modo')=='eci01-pi09-d-preparar'];allrefs=[]
 if prepar:
  need(len(prepar)==1 and prepar[0]['rows'][0].get('ready')is True and prepar[0]['ticks']==3,'Actual legal single support installation required');allrefs=prepar[0]['rows'][0]['requests']
 else:
  # Preparation may have closed in its own actual phase; require its explicit
  # matched proof through the Real6 BEFORE-state P0_guard receipt evidence.
  states=[r for r in p['records']if r.get('label')=='STATE_BEFORE'];need(len(states)==1 and states[0]['rows'][0]['progress']['ordinal']==0,'Separate preparation must appear in the actual initial state')
  guard=states[0]['rows'][0]['progress']['P0_guard'];need(guard['Native_inputs']['applied']==1 and guard['Native_inputs']['all_terminal']is True,'Actual admitted single P0 receipt required');allrefs=guard['requests']
 steps=[{'label':'D_PREPARAR_REAL','literal':{'modo':'eci01-pi09-d-preparar','brazo':'real'},'feedback':'real','actuator':'closed','require_zero_ticks':False,'read_path':['result','rows',0,'ready'],'expected':True,'receipt_paths':[['result','rows',0,'requests']],'stop_on_unapplied_receipt':False}];checks=[];receipts={};frozen=[]
 paths=[['first_stage','reader'],['first_stage','native_motor'],['first_stage','actual_query_motor'],['first_stage','sample_register'],['second_stage','reader'],['second_stage','native_motor'],['second_stage','actual_motor'],['second_stage','FI','early_physical_choice'],['second_stage','pulse_applied'],['second_stage','message'],['actual_failed'],['returned_failed'],['extra_bit_entered_second_TC'],['Native_inputs'],['whole_new_native_ticks'],['prepared_wait_ticks']]
 for index,record in enumerate(eps):
  file=Path(record['primary']).resolve(strict=True);need(file.parent==(P/'ensayos').resolve()and sha(file)==record['sha256']and read(file)['status']=='completed','Actual complete primary hash differs');row=record['rows'][0]
  need(row.get('D_feedback_arm')=='real'and row.get('old_metadata_literal_unchanged')is True and row['Native_inputs']['all_terminal']is True and row['prepared_wait_ticks']==(400 if index==3 else 0),'Exact actual D control/schedule/receipt scope required')
  label='D_EP_%02d'%index;steps.append({'label':label,'literal':{'modo':'eci01-pi09-d-episodio'},'feedback':'real','actuator':'closed','read_path':['result','rows',0,'first_stage','reader','choice'],'expected':row['first_stage']['reader']['choice'],'stop_on_NULL':False,'stop_on_unapplied_receipt':False,'receipt_paths':[['result','rows',0,'requests']],'NULL_handling':'Preserve first Native NULL distinctly; fixed source may continue declared NoQuery. Equality is not all-success.'})
  for path in paths:checks.append({'label':label+'_'+'.'.join(path),'operation':'value','values':[{'step':label,'path':['result','rows',0,*path]}],'expected':get(row,path)})
  allrefs.extend(row['requests']);frozen.append({'ordinal':index,'primary':{'path':str(file),'sha256':sha(file)},'first_choice':row['first_stage']['reader']['choice'],'second_choice':row['second_stage']['reader']['choice'],'actual_failed':row['actual_failed'],'returned_failed':row['returned_failed'],'before_tick':record['before_tick'],'after_tick':record['after_tick']})
 for req in allrefs:
  need(req['id']==req['receipt']['id'],'Native receipt alias mismatch')
  if req['id']in receipts:need(receipts[req['id']]==req['receipt'],'Contradictory same Native ID')
  receipts[req['id']]=req['receipt']
 statuses=[r['status']for r in receipts.values()];dose={'unique_requested':len(receipts),'applied':statuses.count('applied'),'rejected':sum(v.startswith('rejected')for v in statuses),'pending_or_other':sum(v!='applied'and not v.startswith('rejected')for v in statuses)};need(dose['pending_or_other']==0,'No uncertain Native dose permitted')
 steps.append({'label':'D_ESTADO_FINAL','literal':{'modo':'eci01-pi09-d-estado'},'feedback':'real','actuator':'closed','require_zero_ticks':True,'read_path':['result','rows',0,'progress','ordinal'],'expected':6})
 recipe={'schema':'DEE.reproduction.recipe.v1','id':RID,'title':'PI09 D real6 from complete post-panel/pre-learning907543; fresh diagnostic family','revision':'R01_ACTUAL_REAL6_EXPECTATIONS_FROZEN','prefix':ALIAS,'code_capsule_key':CAP,'required_life_prefix':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DRF_','requires_explicit_material':True,'reproduction_enabled':True,'variants':{'real6':{'batches':[steps],'final_checks':checks,'native_receipt_expectations':dose,'documented_and_external_guarded_Native_bound':13063}},'verification':{'state':'PREPARADA_REPLAY_NATIVE_D_FAMILIA_PENDIENTE','Native_replay_verified':False,'actual_source6_frozen':True},'sources':{'actual_real6':{'path':str(proof),'sha256':sha(proof),'final_tick':p['final_tick']},'pre_D_manifest_sha256':seal['source_prefix']['manifest_sha256'],'protocol_sha256':sha(H/'PROTOCOLO_PI09_D_R02.json'),'scientific_source_sha256':sha(H/'pi09_entorno_persistente_D_R02.py'),'source_seal_sha256':sha(H/'SELLO_PI09_D_R02.json'),'capsule_manifest_sha256':sha(CAPSULE/'SISTEMA_CODIGO.json')},'assistance':['Fixed external P0 support48, inherited C/R02 body and two traces','Explicit twelve D opportunities, six evaluated and six available','Only second generic return/shared physical banks; no first-query specific credit'],'limitations':['Actual Real6 observations, including errors/NULL/known terminal conflicts, are auditor-only expectations','No all-six-success or new family Native replay claim before actual cold closure','No selected/control policy in this reproduction family','Outer owned512MiB/shared budget guard required; metadata max_ticks alone is not enforced by old RP driver']}
 out.mkdir();put(out/'receta.json',recipe);put(out/'EXPECTATIVAS.json',{'schema':'DEE.PI09.D.actual6.evaluator_expectations.R01','source':recipe['sources']['actual_real6'],'episodes':frozen,'receipts':dose,'expected_values_never_actor_inputs':True,'Native_executed':False});put(out/'PLAN.json',{'schema':'DEE.PI09.D.family_recipe.prepared.R01','recipe':RID,'recipe_sha256':sha(out/'receta.json'),'checks':len(checks),'actual_source_ticks_with_preparation':p['final_tick']-907543,'dose':dose,'Native_executed':False,'material_replay_pending':True});print(json.dumps({'prepared':str(out),'recipe_sha256':sha(out/'receta.json'),'checks':len(checks),'dose':dose,'Native_executed':False}))
if __name__=='__main__':main()
