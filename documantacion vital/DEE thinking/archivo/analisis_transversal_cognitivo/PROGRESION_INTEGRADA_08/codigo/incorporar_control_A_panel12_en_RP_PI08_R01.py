"""Root-only new A diagnostic recipe; no existing recipe/capsule is modified.

Default prepares a reviewable P8 recipe and CAS plan. --aplicar writes one NEW
RP recipe only. Existing A861426 pair/capsule/analysis are reused. No Native,
state copy, RECURSOS change, principal query, world or actor installation.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,importlib.util,json,os
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
RID='pi08_a_panel12_regulado_T861426_R01';VARIANT='panel12_sin_c2c'
STAGE=H/'RP_CONTROL_A_PANEL12_R01_PROPUESTA';PLAN=P/'control/PLAN_RP_CONTROL_A_PANEL12_PI08_R01.json'
PROOF=P/'control/RP_CONTROL_A_PANEL12_INCORPORADA_PI08_R01.json'
def require(ok,text):
 if not ok:raise ValueError(text)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def put(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def regular(path):
 for q in(path,*path.parents):require(not q.exists()or not(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked/reparse path')
def prepare():
 require(not PROOF.exists(),'Existing Root incorporation protected')
 if PLAN.exists():return read(PLAN)
 require(not STAGE.exists(),'Previous partial stage protected')
 priorfile=RP/'recetas/pi08_a_consolidada_uso_T861426_R02.json';prior=read(priorfile)
 resources=read(RP/'RECURSOS.json');pair=RP/'materiales/PI08_A_CONSOLIDADA_T861426'
 require(sha(pair/'EXPORTACION_SERVICIO.json')=='dfadc5037b804f3c6112263eb0af84f6215d53fd3cb138ae143676a56dfcc00c','Exact A complete prefix required')
 cap=resources['code_capsules'][prior['code_capsule_key']]
 require(prior['code_capsule_key']=='PI08_A_CONSOLIDADA_TRANSPORTE_R02'and cap['manifest_sha256']=='dd1d065ecbb8f9ad40224fb0446baaad89ea09eef506ed407ed4a521038a20c0','Existing preserved A313 capsule required')
 capmanifest=C/cap['product_relative']/cap['manifest'];require(sha(capmanifest)==cap['manifest_sha256'],'Preserved A code manifest changed')
 old=H/'ejecutar_conservacion_B_PI08_R02.py';spec=importlib.util.spec_from_file_location('original_frozen_panel_plan_only',old);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 steps=module.plan();require(sum('expected'in s for s in steps)==12 and sum(s['max_ticks']for s in steps)==8684,'Frozen twelve-witness bounds must total8684')
 for s in steps:
  s['feedback']='real';s['actuator']='closed';s['stop_on_unapplied_receipt']=False
  # Expected mismatches are recorded and do not stop the existing RP runner.
  # A missing upstream integer remains an error; no13 fallback is permitted.
 recipe={'schema':'DEE.reproduction.recipe.v1','id':RID,'title':'PI08 A diagnostic: fixed inherited twelve witnesses with explicit regulated FI',
  'revision':'R01_PROSPECTIVE_AFTER_B_NUMERIC_REGRESSION_BEFORE_A_CONTROL','prefix':prior['prefix'],'code_capsule_key':prior['code_capsule_key'],
  'required_life_prefix':prior['required_life_prefix'],'requires_explicit_material':True,'reproduction_enabled':True,
  'variants':{VARIANT:{'batches':[steps],'native_receipt_expectations':{'rejected':0,'pending_or_other':0},
   'fixed_API_Native_bound':8684,'bound_derivation':'7word/memory*512 +2arithmetic*600 +3regulatedFI*1300; no C2C use. The literal bodies have fixed finite calendars. Generic RP records actual ticks; Root supervisor retains the campaign budget.',
   'comparison_question':'A861426 numeric13/8 availability versus failed B875451 panel; initial absolute phases differ and all actual calendars/doses are recorded. No cause is assumed.'}},
  'analysis':copy.deepcopy(prior['analysis']),
  'verification':{'state':'PREPARADA_REPLAY_NATIVE_PENDIENTE','Native_replay_verified':False},
  'assistance':['Same fixed panel12 paths, literals, numeric decoder and actual integer binding as the closed B panel; only FI modes are explicitly regulated as already declared there.',
   'No Python chooses a correct result or substitutes13. Each expected value is an evaluator-only comparison after Native.',
   'Only fresh ARP identity/new absolute destination is allowed by the preserved importer. No C2C resource or B/R03 opportunity is consumed.'],
  'limitations':['This is a new diagnostic of complete acquired A, not a redo of B18 or a query on the selected principal.',
   'B conservation remains false regardless of this outcome. If A also returns7/2, the prepared None diagnostic is not automatically needed or authorized.',
   'Wrong numeric integer outputs continue to the subsequent fixed binding and remaining witnesses; NULL cannot be replaced with a number.',
   'Documentary recalculation points to the existing actual A selected FI/alfa evidence; it is not a recálculo of this pending new panel.'],
  'sources':{'prior_recipe':{'path':str(priorfile),'sha256':sha(priorfile)},'full_A_manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),
   'A_code_capsule_manifest_sha256':sha(capmanifest),'unchanged_original_panel_runner':{'path':str(old),'sha256':sha(old)},
   'failed_B_panel':{'path':str(P/'control/PI08_B_CONSERVACION_R02.json'),'sha256':sha(P/'control/PI08_B_CONSERVACION_R02.json')},
   'Native_executed_by_registration':False,'new_worlds_on_registration':0,'new_worlds_if_Root_runs':1,'material_C2C_calls':0}}
 put(STAGE/'receta.json',recipe)
 plan={'schema':'DEE.PI08.A.RP.prospective_numeric_panel.CAS_plan.R01','recipe_id':RID,'variant':VARIANT,'recipe_sha256':sha(STAGE/'receta.json'),
  'resource_before_sha256':sha(RP/'RECURSOS.json'),'prior_recipe_sha256':sha(priorfile),'code_manifest_sha256':sha(capmanifest),
  'source_manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'fixed_API_Native_bound':8684,'Native_executed':False,'existing_capsule_pair_untouched':True}
 put(PLAN,plan);return plan
def main(args):
 plan=prepare();require(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'CAS registry changed; review a new plan')
 require(sha(STAGE/'receta.json')==plan['recipe_sha256'],'Staged recipe changed')
 if args.aplicar:
  target=RP/'recetas'/(RID+'.json');regular(target);require(not target.exists(),'Existing recipe preserved')
  with target.open('xb')as f:f.write((STAGE/'receta.json').read_bytes());f.flush();os.fsync(f.fileno())
  require(sha(target)==plan['recipe_sha256']and sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'Recipe copy/registry changed')
  put(PROOF,{**plan,'schema':'DEE.PI08.A.RP.prospective_numeric_panel.applied.R01','applied':True,'recorded_utc':datetime.now(timezone.utc).isoformat(),'recipe_path':str(target),'RECURSOS_modified':False,'principal_source_or_capsule_modified':False})
 result=PROOF if args.aplicar else PLAN
 print(json.dumps({'mode':'APPLIED_ROOT_ONLY'if args.aplicar else'P8_PLAN_ONLY','proof':str(result),'sha256':sha(result),'recipe':RID,'variant':VARIANT,'Native_executed':False}))
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--aplicar',action='store_true');main(parser.parse_args())
