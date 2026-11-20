"""Correct the un-applied plan's stale informational pin list; no source changes.
The R02 actual staged manifest already pins current A1 code correctly.
"""
from pathlib import Path
import hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';oldplan=P/'control/PI08_A1_HOOKS_PREPARADOS_R02.json';plan=P/'control/PI08_A1_HOOKS_PREPARADOS_R03.json';stage=H/'PI08_A1_INSTALACION_R02';applier=H/'instalar_hooks_A1_PI08_R03.py'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def put(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
if plan.exists()or applier.exists():raise FileExistsError('Corrected prepared revision preserved')
d=read(oldplan);manifest=read(stage/'capacidades/PROTOCOLO_PI08_C2C_INTEGRACION_R01.json');d['unchanged_scientific_sources']={name:digest for name,digest in manifest['files_sha256'].items()if name not in('pi08_integracion_c2c_R01.py','PROTOCOLO_PI08_C2C_32_R01.json','PROTOCOLO_PI08_RECHAZO34_R01.json')};d['plan_preparation_revision']={'prior_literal':str(oldplan),'prior_sha256':sha(oldplan),'reason':'Informational unchanged_scientific_sources accidentally came from oldpreteststage and included a changingnewA1module. Actual R02installedstage manifest/filesentry alreadyagreed; no Source/Nativecontract criteria changed.'}
for row in d['files']:
 if sha(Path(row['source']))!=row['sha256']:raise ValueError('Staged source changed')
put(plan,d)
s=(H/'instalar_hooks_A1_PI08_R02.py').read_text('utf8').replace('PI08_A1_HOOKS_PREPARADOS_R02.json','PI08_A1_HOOKS_PREPARADOS_R03.json').replace('PI08_A1_HOOKS_APLICADOS_R02.json','PI08_A1_HOOKS_APLICADOS_R03.json').replace('ORIGINALES_HOOKS_A1_PI08_R02','ORIGINALES_HOOKS_A1_PI08_R03');compile(s,str(applier),'exec');applier.write_text(s,encoding='utf8')
modulefile=stage/'capacidades/pi08_integracion_c2c_R01.py';spec=importlib.util.spec_from_file_location('PI08_A1_final_installed_configuration_only',modulefile);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);cfg,p,digest=m._configuration('32');error=None
try:m._configuration('34')
except ValueError as exc:error=str(exc)
if sha(modulefile)!=cfg['files_sha256']['pi08_integracion_c2c_R01.py']or error!='One bounded2..32-opportunity schedule required':raise ValueError('Actual final configuration failed')
proof=P/'control/PI08_A1_CONFIGURACION_FINAL_REAL_SIN_NATIVE_R03.json';put(proof,{'schema':'DEE.PI08.A1.final_staged_configuration_actual.v1','plan':{'path':str(plan),'sha256':sha(plan)},'applier':{'path':str(applier),'sha256':sha(applier)},'module_sha256':sha(modulefile),'actual_manifest_self_pin_equal':True,'effective32_actual_full_validator_passed':True,'protocol32_sha256':digest,'original30schedule_literal_preserved':len(p['schedule'])==32,'invalid34_actual_consumer_rejection':error,'Native_imported_or_executed':False,'operational_transaction_test_pending':True})
print(json.dumps({'plan':str(plan),'plan_sha256':sha(plan),'Root_applier':str(applier),'applier_sha256':sha(applier),'actual_final_configuration_proof':str(proof),'proof_sha256':sha(proof)}))
