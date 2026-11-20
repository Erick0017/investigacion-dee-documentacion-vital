"""Pure/static registration tests only; never --aplicar, DEE or Native."""
from pathlib import Path
import hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';src=H/'incorporar_reproducibilidad_instrumental_PI06_R01.py'
spec=importlib.util.spec_from_file_location('PI06_RP_registration_static',src);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
tests=[]
def test(name,ok):
 if not ok:raise AssertionError(name)
 tests.append({'name':name,'passed':True})
plan=m.read(m.STAGE/'PLAN.json');manifest=m.read(m.STAGE/'SISTEMA_CODIGO_PROPUESTO.json')
test('plan_native0_no_pair_copy',plan['Native_executed']is False and plan['new_ticks']==0 and plan['no_large_pair_copy'])
test('new_capsule_304files',plan['code_files']==len(manifest['files'])==304)
for name,h in plan['staged_files'].items():test('reviewed_stage_hash_'+name,m.sha(m.STAGE/m.rel(name))==h)
cfg=m.read(m.STAGE/'RECURSOS_PROPUESTO.json')
test('capsule_manifest_pinned',cfg['code_capsules'][m.CAP]['manifest_sha256']==m.sha(m.STAGE/'SISTEMA_CODIGO_PROPUESTO.json'))
test('frozen_pair_reused',cfg['pairs'][m.ALIAS]['manifest_sha256']==m.PAIR_SHA)
recipes=m.make_recipes()
for name,r in recipes.items():test('staged_recipe_matches_observed_primaries_'+name,m.read(m.STAGE/'recetas'/(name+'.json'))==r)
r=recipes['pi06_interrupcion_causal_y_sham_R02'];cloud=recipes['pi06_nube_fija_y_parada_host_R03']
test('R02_enabled_but_not_replayed',r['reproduction_enabled']and not r['verification']['Native_replay_verified'])
test('R02_fixed201_177_each',all(v['native_receipt_expectations']=={'unique_requested':177,'applied':177,'rejected':0,'pending_or_other':0}and v['final_checks'][1]['expected']==201 for v in r['variants'].values()))
test('evaluator_expected_not_actor_payload',all('expected'not in step['literal']and 'target'not in step['literal']for v in r['variants'].values()for b in v['batches']for step in b))
test('R03_disabled_preserves_host_stop',cloud['reproduction_enabled']is False and cloud['variants']['nube_historica_bloqueada']['batches'][0][0]['expected']is True)
test('R03_all61_58applied3occupied_preserved',cloud['variants']['nube_historica_bloqueada']['native_receipt_expectations']=={'unique_requested':61,'applied':58,'rejected':3,'pending_or_other':0})
test('R04_not_an_executable_freshID_recipe',all('R04'not in name for name in recipes)and len(cloud['historical_R04_evidence'])==2)
oldcat=m.read(m.STAGE/'CATALOGO_ANTES.json');newcat=m.read(m.STAGE/'CATALOGO_PROPUESTO.json')
test('catalog_old_entries_literal_values_preserved',newcat['entries'][:-2]==oldcat['entries'])
test('catalog_all_other_fields_preserved',{k:v for k,v in oldcat.items()if k!='entries'}=={k:v for k,v in newcat.items()if k!='entries'})
test('both_new_entries_no_main_acquisition',all(x['principal_acquisition']is False for x in newcat['entries'][-2:]))
test('protected_main_and_oldRP_literal_unchanged',m.protected()==plan['protected'])
for value in('../outside','/absolute','C:/elsewhere','a\\b','a/./b',''):
 try:m.rel(value)
 except ValueError:test('unsafe_path_rejected_'+repr(value),True)
 else:raise AssertionError('Unsafe path accepted: '+value)
test('no_engine_or_app_import',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
output=P/'control/INCORPORACION_RP_PI06_PRUEBAS_PURAS_R01.json'
m.save(output,{'schema':'DEE.PI06.instrumental_RP_addition.static_tests.v1','tests':tests,'passed':len(tests),'Native_executed':False,'product_or_RP_modified':False,
 'helper_sha256':m.sha(src),'plan_sha256':m.sha(m.STAGE/'PLAN.json'),'scope':'Static safeguards, exact observed recipe values and preserved critical files only. No Native replay, new mental capacity or application performed.'})
print(json.dumps({'proof':str(output),'sha256':m.sha(output),'passed':len(tests),'Native_executed':False}))
