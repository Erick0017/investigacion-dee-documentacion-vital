"""Bind the actual post12 pair and freeze two plans. Stdlib, Native0."""
from pathlib import Path
from datetime import datetime,timezone
import copy,hashlib,json,os
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0'
PAIR=P/'pares/NATIVE_POST12_T903603';PAIR_SHA='0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553'
HELPER=P/'codigo/pi09_aritmetica_temporal_P0_R01.py';HELPER_SHA='ebff5dbe0d3b85000a33b7f789a72688e7c24c0151076558a01e32a803824656'
PROTO=P/'codigo/PROTOCOLO_PI09_ARITMETICA_TEMPORAL_P0_R02.json';PRE_SHA='3f1066123158d674386c8e701a6b9b7f177dc2629ad47ee9ad972730b36eac72'
RECIPE=C/'reproducibilidad/recetas/pi08_a_panel12_regulado_T861426_R01.json'
RUNNER=P/'codigo/ejecutar_plan_PI09_R02.py'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def encoded(value):return(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf8')
def info(p):return {'file':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def require(ok,message):
 if not ok:raise ValueError(message)
def new(p,data):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('xb')as f:f.write(data)

def registry_proposal(original,protocol_sha):
 r=copy.deepcopy(original);name=HELPER.stem
 require(name not in r['plugins']and HELPER.name not in r['files_sha256'],'P0 already registered; no reuse')
 r['plugins'].append(name);r['files_sha256'][HELPER.name]=HELPER_SHA;r['files_sha256'][PROTO.name]=protocol_sha
 return r

def main():
 require(sha(PAIR/'EXPORTACION_SERVICIO.json')==PAIR_SHA and sha(HELPER)==HELPER_SHA and sha(PROTO)==PRE_SHA,'Pinned source/protocol/helper changed')
 mf=read(PAIR/'EXPORTACION_SERVICIO.json');require(mf['physical']['N']==67 and mf['physical']['tick']==903603 and mf['PI09_actual_progress']['ordinal']==12 and mf['PI09_actual_progress']['role']=='native_real','Actual complete canonical12 required')
 before=PROTO.read_bytes();proto=read(PROTO);proto.update(source_full_pair=info(PAIR/'EXPORTACION_SERVICIO.json'),execution_enabled=True,phase='SEALED_BEFORE_POST12_P0_NATIVE',sealed_utc=datetime.now(timezone.utc).isoformat())
 proto.pop('unmet_requirement',None);proto['source_physical']=mf['physical'];proto['source_snapshot_sha256']=mf['snapshot_sha256'];proto['source_life_id']=mf['life_id'];proto['prior_prepared_protocol_sha256']=PRE_SHA
 proto['retention_panel']={'recipe':info(RECIPE),'witnesses':12,'admin_pause_zero_ticks':True,'FI_access':'unchanged regulated API, max1300each','two_numeric_witnesses':'Legacy direct arithmetic; actual previous integer transported. No P0 protection for these two retained-domain witnesses.'}
 proto['phase_challenge_binding']='Before each fresh operation, Root runner computes smallest legal prewait from actual previous after_tick using the frozen clock helper only. Both arms same formula; no expected value/outcome selects it.'
 data=encoded(proto);protocol_sha=hashlib.sha256(data).hexdigest()
 original_registry=read(P/'estados/NATIVE/sistema/capacidades/PI09_PLUGINS_R02.json');registry=registry_proposal(original_registry,protocol_sha);registry_sha=hashlib.sha256(encoded(registry)).hexdigest()
 oldsteps=read(RECIPE)['variants']['panel12_sin_c2c']['batches'][0]
 require(len(oldsteps)==13 and sum(s['label']!='habitat_off'for s in oldsteps)==12,'Exact published twelve-witness panel plus pause')
 plans=[]
 for slug,guard in (('PANEL',False),('DISCOVERY',True)):
  system=P/'estados'/slug/'sistema';steps=copy.deepcopy(oldsteps)
  for s in steps:
   s['stage']='retention_published_domain';s['expected_auditor_only_not_actor']=True
  for i,(left,right,expected)in enumerate(((2,8,10),(9,7,16),(5,11,16),(3,4,7))):
   steps.append({'label':'CHALLENGE_%d_SUM'%i,'stage':'new_reserved_clock_challenge','literal':{'modo':'eci01-pi09-aritmetica-temporal','operacion':'suma','izquierda':left,'derecha':right,'espera_previa':0,'guardia_temporal':guard},'clock_alignment':True,'read_path':['result','rows',0,'numeric_result'],'expected':expected,'max_ticks':364,'feedback':'real','actuator':'closed'})
  steps.append({'label':'CHALLENGE_4_DIF_ACTUAL_MINUS2','stage':'new_reserved_clock_challenge','literal':{'modo':'eci01-pi09-aritmetica-temporal','operacion':'diferencia','izquierda':0,'derecha':2,'espera_previa':0,'guardia_temporal':guard},'clock_alignment':True,'actual_integer_binding':{'from_step':'CHALLENGE_3_SUM','field':'izquierda'},'read_path':['result','rows',0,'numeric_result'],'expected':5,'max_ticks':364,'feedback':'real','actuator':'closed','expected_scope':'Normative end-to-end5; independent difference correctness must also use actual previous integer, never infer two independent failures.'})
  pins={str(HELPER):HELPER_SHA,str(PROTO):protocol_sha,str(RUNNER):sha(RUNNER),str(RECIPE):sha(RECIPE),str(system/'capacidades'/HELPER.name):HELPER_SHA,str(system/'capacidades'/PROTO.name):protocol_sha,str(system/'capacidades/PI09_PLUGINS_R02.json'):registry_sha}
  plan={'schema':'DEE.PI09.P0.post12.retention_and_fresh_arithmetic_plan.R01','tag':'PI09_'+slug+'_P0_R01','system':str(system),'life_id':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'+slug+'_01','initial_tick':903603,'source_full_pair':info(PAIR/'EXPORTACION_SERVICIO.json'),'steps':steps,'pins':pins,'runner':info(RUNNER),'new_Native_executed':False,'guard_enabled_only_for_fresh_challenges':guard,'no_PI09_episode_preparation_reset':True,'no_automatic_adoption':True,'shared_prefix_paired_controls_not_independent_lives':True,'protocol_sha256':protocol_sha,'finite_bound':sum(s['max_ticks']for s in steps),'actual_result_transport_required':True,'results_not_yet_observed':True}
  path=P/'codigo'/('PLAN_'+slug+'_P0_R01.json');new(path,encoded(plan));plans.append(info(path))
 backup=P/'codigo/revisiones/PROTOCOLO_PI09_ARITMETICA_TEMPORAL_P0_R02_PRE_POST12.json';new(backup,before)
 require(sha(PROTO)==PRE_SHA,'Concurrent protocol change; plans remain unapplied')
 temp=PROTO.with_name(PROTO.name+'.SEALED_TMP');new(temp,data);os.replace(temp,PROTO)
 seal={'schema':'DEE.PI09.P0.actual_post12_pair_and_new_reserve_seal.R01','sealed_utc':datetime.now(timezone.utc).isoformat(),'Native_executed':False,'source':info(PAIR/'EXPORTACION_SERVICIO.json'),'protocol':info(PROTO),'helper':info(HELPER),'plans':plans,'prior_prepared_protocol':info(backup),'expected_installed_registry_sha256':registry_sha,'states_or_selectors_modified':False}
 target=P/'control/SELLO_PANEL_DISCOVERY_P0_PI09_R01.json';new(target,encoded(seal));print(json.dumps({'seal':str(target),'sha256':sha(target),'protocol_sha256':protocol_sha,'plans':plans,'Native':0},ensure_ascii=False))

if __name__=='__main__':main()
