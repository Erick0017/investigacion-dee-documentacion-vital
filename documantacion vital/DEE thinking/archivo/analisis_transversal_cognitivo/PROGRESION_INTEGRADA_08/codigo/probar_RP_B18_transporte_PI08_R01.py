"""Pure administrative/routing checks against the18 actual preserved primaries."""
from pathlib import Path
from types import SimpleNamespace
from collections import Counter
import hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';R=P.parents[2]
RP=R/'DEE Cognitive 2.0/reproducibilidad';STAGE=H/'RP_B_ADQUISICION18_R01_PROPUESTA'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def check(ok,why):
 if not ok:raise ValueError(why)
checks=[]
def passed(label,ok):check(ok,label);checks.append(label)
def rejects(label,call):
 try:call()
 except ValueError:checks.append(label);return
 raise ValueError('Did not reject: '+label)
runner=load('pure_existing_RP_paths',RP/'ejecutar_diagnostico.py')
spec=read(STAGE/'receta.json');variant=spec['variants']['real18_sin_global'];results={};all_receipts={};fails=[];choices=[]
for index,step in enumerate(variant['batches'][0][1:-1]):
 primary=read(P/'control/B_PORTABLE_REAL18_R01/PRIMARIOS'/('PI08_B_REAL_R02_EP%02d.json'%index))
 result=primary['result'];result=json.loads(result)if isinstance(result,str)else result
 results[step['label']]=result
 observed=runner.path_value(result,step['read_path'])
 passed('actual_ep%02d_expected_failure_including_adverse'%index,type(observed)is bool and observed==step['expected'])
 fails.append(observed);choices.append(runner.path_value(result,['result','rows',0,'reader','choice']))
 ledger=runner.receipts(result,step['receipt_paths']);all_receipts.update(ledger)
for c in variant['final_checks']:
 passed(c['label'],runner.path_value(results[c['values'][0]['step']],c['values'][0]['path'])==c['expected'])
passed('all_four_actual_failures_kept',sum(fails)==4)
passed('numeric_zero_preserved_distinct_from_NULL',0 in choices and None not in choices)
status=Counter(x['status']for x in all_receipts.values())
passed('all_current_direct_receipts_no_history',len(all_receipts)==3306 and status=={'applied':3302,'rejected_conflict':4})
passed('known_conflicts_do_not_stop_new_recipe',all(s.get('stop_on_unapplied_receipt')is False for s in variant['batches'][0][1:-1]))
cap=STAGE/'capsule';manifest=read(cap/'SISTEMA_CODIGO.json')
passed('315_exact_staged_code_files',len(manifest['files'])==315 and all(sha(cap/r['file'])==r['sha256']for r in manifest['files']))
scientific_before={n:sha(cap/'capacidades'/n)for n in manifest['scientific_sources_literal']}
research=load('literal_B_for_RP_transport_test',cap/'capacidades/pi08_revision_flexible_B_R01.py')
transport=load('bounded_RP_B_identity_test',cap/'capacidades/pi08_permiso_B_reproduccion_R02.py')
identity={'life_id':transport.PREFIX+'PURE01','profile':'fisica_directa'}
entries={transport.SYSTEM_KEY:json.dumps(identity),'DEE.Cognitive.PI07.regulation.environment.R03':json.dumps({'ordinal':12,'rows':[{}]*12,'ready':True,'pending':None,'uncertain':False})}
runtime=SimpleNamespace(snapshot_metadata_entries=list(entries.items()),dimension=67)
fake=SimpleNamespace(world=SimpleNamespace(runtime=runtime),tick=861426)
private=transport.component(fake,research);seal=read(cap/'capacidades/SELLO_PI08_B_R01.json')
stub=SimpleNamespace(_native=lambda:(None,None,None,json.loads,None),_physical=lambda a:seal['source_prefix']['physical'])
private._component=lambda:stub
start=variant['batches'][0][0]['literal'];private.validate(fake,start)
passed('actual_identity_restored_after_original_validation',private._identity(fake)==identity)
passed('actual_SYSTEM_literal_not_rebound',runtime.snapshot_metadata_entries==list(entries.items()))
rejects('no_none_control_admission',lambda:private.validate(fake,{**start,'brazo':'none'}))
rejects('no_changed_source_prefix',lambda:private.validate(fake,{**start,'prefijo_sha256':'0'*64}))
rejects('no_recorder_override',lambda:private.validate(fake,{**start,'registro_global':True}))
m={'version':research.VERSION,'control':{'arm':'real','max_ordinal':32},'ordinal':12,'protocol_sha256':sha(cap/'capacidades/PROTOCOLO_PI08_B_R01.json'),'ready':True,'admitted':True,'pending':None,'uncertain':False}
entries[transport.B_KEY]=json.dumps(m);runtime.snapshot_metadata_entries=list(entries.items())
private.validate(fake,{'modo':'eci01-pi08-b-episodio'})
passed('real_continuation_original_validator_runs',private._identity(fake)==identity)
rejects('existing_KEY_cannot_readmit',lambda:private.validate(fake,start))
entries[transport.B_KEY]=json.dumps({**m,'reference_policy':{}});runtime.snapshot_metadata_entries=list(entries.items())
rejects('reference_policy_never_candidate',lambda:private.validate(fake,{'modo':'eci01-pi08-b-estado'}))
passed('all_B_scientific_sources_literal_after_private_fake',scientific_before=={n:sha(cap/'capacidades'/n)for n in scientific_before})
out=P/'control/PRUEBA_RP_B_REAL18_TRANSPORTE_R01.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI08.B.RP.pure_transport_checks.R01','checks_passed':len(checks),'checks':checks,'Native_executed':False,'DEE_imported':False,'source_or_product_modified':False,'recipe_sha256':sha(STAGE/'receta.json'),'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'material_replay_verified':False},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'passed':True,'checks':len(checks),'proof':str(out),'sha256':sha(out),'Native_executed':False}))
