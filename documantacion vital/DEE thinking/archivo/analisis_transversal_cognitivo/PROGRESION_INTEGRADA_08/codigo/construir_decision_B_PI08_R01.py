"""Root-only actual B decision builder, never an automatic approval.

Requires the completed canonical six-gate evaluation, all four real closed
arms, actual conservation clone and frozen complete source. Default approval
is false. No Native/Store/product writes; only a P8 proposal/profile is saved.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse, copy, hashlib, importlib.util, json

P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';CS=P/'estados/B_REAL_R01/sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01'
GATES=('functional_gain','conservation','causal_controls','source_reopening','new_function_at_final_cut','decisive_recipe_replay')
SELECTORS=('PROYECTO.json','CONTINUIDAD_DEE_COGNITIVE_2_0.json','sistema/estado/ACTIVO.json','sistema/estado/genesis/SELECCION_PERSONAL.json','aplicacion/GENESIS/SELECCION_CANDIDATA.json','sistema/capacidades/CATALOGO_CAPACIDADES.json')
def require(ok,text):
 if not ok:raise ValueError(text)
def read(path):return json.loads(path.read_text('utf-8-sig'))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def ref(value):
 path=Path(value['path']).resolve(strict=True)
 require(path.is_relative_to(P.resolve())and sha(path)==value['sha256'],'Actual bounded evidence reference required')
 return{'path':str(path),'sha256':value['sha256']}
def put(path,value):
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
def main(args):
 output=args.salida.resolve();require(output.is_relative_to((P/'control').resolve())and not output.exists(),'Fresh P8/control decision only')
 factsfile=args.evaluacion.resolve(strict=True);require(factsfile.is_relative_to(P.resolve()),'Canonical local B evaluation required')
 facts=read(factsfile)
 required={'schema','life_id','N','T','all_fixed_evidence_gates_met','gates','B_actual_closed_arms','B_conservation_proof','B_source_full_pair','scope','gains','losses','uncertainties','assistance','regression_coverage'}
 require(required<=set(facts)and facts['schema']=='DEE.PI08.B.combined_actual_gates.R01'and facts['life_id']==LIFE and facts['N']==67 and facts['all_fixed_evidence_gates_met']is True,'Actual closed positive canonical B evaluation required; no prepared metrics')
 process=args.process_proof.resolve(strict=True);writers=read(process)
 require(process.is_relative_to((P/'control').resolve())and writers.get('no_live_affected_writers')is True,'Actual scoped process proof required')
 gates={}
 for name in GATES:
  gate=facts['gates'][name]
  require(gate.get('result')is True and gate.get('criterion')and gate.get('evidence'),'Actual empirical gate absent/negative: '+name)
  gates[name]={'satisfied':True,'criterion':gate['criterion'],'result':True,'evidence':[ref(v)for v in gate['evidence']]}
 card=read(CS/'estado/vidas'/LIFE/'VIDA.json')
 require(card['physical']['tick']==facts['T']and card['physical']['N']==67 and sha(CS/card['snapshot'])==card['snapshot_sha256'],'Exact current closed evaluated B source required')
 deltafile=P/'control/DELTA_OPERATIVO_B_PRODUCTO_PROPUESTO_PI08_R01.json';delta=read(deltafile)
 rows=copy.deepcopy(delta['proposed_code_files_without_prepared_profile'])
 for row in rows:
  source=Path(row['source']);target=C/'sistema'/row['file']
  require(sha(source)==row['sha256'],'Reviewed code proposal changed')
  require((sha(target)if target.exists()else None)==row['before_sha256'],'Current product code differs from reviewed CAS')
 template=Path(delta['prepared_profile_template']);profile=read(template)
 require(profile['status']=='DRAFT_NOT_DEPLOYABLE_MISSING_ACTUAL_GATES','Preserve the original nondeployable template')
 profile.update(status='PREPARED_DIAGNOSTIC',all_adoption_gates_met=True,adoption_decision_sha256=None)
 profilefile=H/'PERFIL_B_OPERATIVO_APROBABLE_R01.json'
 # This file is not deployed or a COMMITTED profile. Its exact bytes are part
 # of the reviewable decision, gated again by the actual adopter.
 if profilefile.exists():require(read(profilefile)==profile,'Different existing prepared B profile protected')
 else:put(profilefile,profile)
 rows.append({'file':'contratos/PI08_B_USO_OPERATIVO_R01.json','source':str(profilefile),'sha256':sha(profilefile),
              'before_sha256':sha(C/'sistema/contratos/PI08_B_USO_OPERATIVO_R01.json')if(C/'sistema/contratos/PI08_B_USO_OPERATIVO_R01.json').exists()else None})
 decision={'schema':'DEE.PI08.B.reasoned_actual_adoption_decision.R01','built_utc':datetime.now(timezone.utc).isoformat(),
   'approved_for_adoption':bool(args.aprobar),'decision_id':'PI08_CONSOLIDACION_B_OPERATIVA_01','life_id':LIFE,
   'source_tick':facts['T'],'source_snapshot_sha256':card['snapshot_sha256'],'gates':gates,
   'approved_code_files':rows,'selectors_cas':{name:sha(C/name)for name in SELECTORS},
   'new_contract':profile,'catalog_entry':facts.get('catalog_entry',{'id':'PI08_REGULACION_FLEXIBLE_B_CONSOLIDADA_01',
      'name':'Regulación B contextual en la misma organización Native','kind':'vida_con_revision_contextual_adquirida_local',
      'status':'OPERATIVE_WITH_DECLARED_LIMITS','domain':'Contratos B finitos, accesoFIretimado, memoria nombrada y C2C32; sin agencia general',
      'not_claimed':['universal_superiority_to_WSLS','autonomous_global_planning','new_mental_architecture','branch_memory_fusion','new_B_RP_CLI_replay_if_not_executed']}),
   'scope':facts['scope'],'gains':facts['gains'],'losses':facts['losses'],'uncertainties':facts['uncertainties'],
   'assistance':facts['assistance'],'regression_coverage':facts['regression_coverage'],
   'evidence':[{'path':str(factsfile),'sha256':sha(factsfile)},{'path':str(deltafile),'sha256':sha(deltafile)},
               {'path':str(process),'sha256':sha(process)}],
   'B_actual_closed_arms':{role:ref(value)for role,value in facts['B_actual_closed_arms'].items()},
   'B_conservation_proof':ref(facts['B_conservation_proof']),'B_source_full_pair':copy.deepcopy(facts['B_source_full_pair']),
   'process_proof':str(process),'Root_explicit_approval_flag_used':bool(args.aprobar),
   'adoption_executed_by_builder':False,'Native_executed_by_builder':False}
 # Same evidence checks the administrative mover uses, without Store imports.
 spec=importlib.util.spec_from_file_location('B_actual_evidence_validation_only',H/'incorporar_B_PI08_misma_identidad_R01.py')
 mover=importlib.util.module_from_spec(spec);spec.loader.exec_module(mover);mover.validate_B_evidence(decision)
 put(output,decision)
 print(json.dumps({'decision':str(output),'sha256':sha(output),'approved_for_adoption':bool(args.aprobar),
                   'source_tick':facts['T'],'code_files':len(rows),'Native_executed':False}))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evaluacion',type=Path,required=True)
 p.add_argument('--process-proof',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
 p.add_argument('--aprobar',action='store_true');main(p.parse_args())
