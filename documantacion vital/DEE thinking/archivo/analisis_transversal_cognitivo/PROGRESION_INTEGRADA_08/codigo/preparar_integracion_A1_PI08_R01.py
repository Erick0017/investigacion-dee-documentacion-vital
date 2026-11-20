"""Prepare a versioned PI08 A1 source delta; Root alone may --aplicar it.
No Native/app imports, process control or source-world/state modifications.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,importlib.util,json,os,shutil,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad';BASE=RP/'codigo_preservado/PI07_R03_LOCAL_FI_PRE34_R03';STAGE=H/'PI08_A1_STAGE';PLAN=P/'control/PI08_A1_DELTA_PREPARADO_R01.json'
BODY='pi04_coordinacion_central_C2C.py';BODY_SHA='31778467ef0917f74fe422d538b9ed97a8144e05aaff1717dae4124b1ade87dd';P30='PROTOCOLO_PI05_C2C_30_R01.json';P30_SHA='5dda50c36fa72ea3932eded545e0bb673b40202d0d553cfa97a50ab31c67d1bc'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def build():
 if PLAN.exists()or STAGE.exists():raise FileExistsError('Prepared source revision preserved')
 old=read(BASE/'capacidades'/P30)
 if sha(BASE/'capacidades'/BODY)!=BODY_SHA or sha(BASE/'capacidades'/P30)!=P30_SHA:raise ValueError('Exact immutable real consumer and effective30 protocol required')
 STAGE.mkdir();cap=STAGE/'capacidades';cap.mkdir();(STAGE/'app').mkdir()
 new=read(BASE/'capacidades'/P30);offers=[{'stage':'retention','context':3,'left':27,'right':4},{'stage':'retention','context':7,'left':8,'right':7}];new['schedule']+=offers;new['attribution']+=' PI08 A1 explicit external30to32 preparation/commit: original30 offers literal; exactly2 public future offers, no Native policy or counter reset.'
 write(cap/'PROTOCOLO_PI08_C2C_32_R01.json',new)
 original34=P.parent/'PROGRESION_INTEGRADA_07/codigo/PROTOCOLO_PI07_C2C_34_R01.json';shutil.copyfile(original34,cap/'PROTOCOLO_PI08_RECHAZO34_R01.json')
 shutil.copyfile(H/'pi08_integracion_c2c_R01.py',cap/'pi08_integracion_c2c_R01.py')
 pins={BODY:BODY_SHA,P30:P30_SHA,**old['dependencies_sha256']}
 for name in('pi05_c2c_ofertas_R01.py','PROTOCOLO_PI05_C2C_EXTENSION_R01.json','PROTOCOLO_PI04_C2C_R01.json','pi05_permiso_principal_R01.py'):
  pins[name]=sha(BASE/'capacidades'/name)
 for name,digest in pins.items():
  source=BASE/'capacidades'/name
  if sha(source)!=digest:raise ValueError('Changed actual inherited consumer dependency: '+name)
  shutil.copyfile(source,cap/name)
 files={name:sha(cap/name)for name in sorted(set(pins)|{'pi08_integracion_c2c_R01.py','PROTOCOLO_PI08_C2C_32_R01.json','PROTOCOLO_PI08_RECHAZO34_R01.json'})}
 write(cap/'PROTOCOLO_PI08_C2C_INTEGRACION_R01.json',{'schema':'DEE.PI08.C2C.integration32.protocol.v1','status':'SEALED_BEFORE_WRITES','original_protocol_file':P30,'original_protocol_sha256':P30_SHA,'effective_protocol_file':'PROTOCOLO_PI08_C2C_32_R01.json','invalid34_control_file':'PROTOCOLO_PI08_RECHAZO34_R01.json','additional_public_offers':offers,'files_sha256':files,'Native_body_unchanged':BODY_SHA,'scope':'Prepared P0 environment extension/location migration, not learning. Current real30history is required; no oldfailed34 repair.'})
 # Three insertion points in the existing owner; retain all historical routes.
 before={};changed=[]
 for name in('app/mundo_genesis_apd05.py','app/cola_local.py'):
  source=BASE/name;text=source.read_text('utf-8-sig');before[name]=sha(source)
  if name.endswith('mundo_genesis_apd05.py'):
   marker="        if mode.startswith('eci01-pi07-'):"
   # Actual historical code uses row['modo'] in the validator and dispatch.
   print('World hook anchors require exact review; source prepared separately')if False else None
  target=STAGE/name;target.write_text(text,encoding='utf8')
 # Prepare only capability/config here. Actual app/dispatcher hook delta is
 # derived by the bounded hook builder from the exact isolated target source.
 write(PLAN,{'schema':'DEE.PI08.A1.prepared_capability.v1','prepared_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_capsule':str(BASE),'source_capsule_manifest_sha256':sha(BASE/'SISTEMA_CODIGO.json'),'stage':str(STAGE),'new_files':[{'file':p.relative_to(STAGE).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(cap.iterdir())if p.name in {'pi08_integracion_c2c_R01.py','PROTOCOLO_PI08_C2C_32_R01.json','PROTOCOLO_PI08_RECHAZO34_R01.json','PROTOCOLO_PI08_C2C_INTEGRACION_R01.json'}],'unchanged_consumer_pins':pins,'Native_executed':False,'implementation_status':'PREPARED_FOR_ROOT_OPERATIONAL_TESTS_NOT_VERIFIED','requires':'Actual closed complete prefix, realC2Cordinal30, Sourceownerclosed before hooks, actual prepare/reject/interruption/repeat/reopen tests before adoption.'})
 # Invoke the actual unchanged finite consumer validator, no mocks/DEE.
 spec=importlib.util.spec_from_file_location('PI08_actual_finite_consumer_pure',cap/BODY);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);module.PROTOCOL=cap/'PROTOCOLO_PI08_C2C_32_R01.json';p,digest=module.protocol(material=True,evaluation=True)
 if len(p['schedule'])!=32:raise ValueError('Effective32 real validator failed')
 module.PROTOCOL=cap/'PROTOCOLO_PI08_RECHAZO34_R01.json';error=None
 try:module.protocol(material=True,evaluation=True)
 except ValueError as exc:error=str(exc)
 if error!='One bounded2..32-opportunity schedule required':raise ValueError('Actual34invalid contract must reject unchanged')
 proof=P/'control/PI08_A1_VALIDADOR_REAL_SIN_NATIVE_R01.json';write(proof,{'schema':'DEE.PI08.A1.actual_consumer_pure_validation.v1','protocol32_accepted':True,'protocol32_sha256':digest,'protocol34_rejected':error,'body_sha256':BODY_SHA,'old30protocol_literal_sha256':P30_SHA,'original30schedule_literal_unchanged':p['schedule'][:30]==old['schedule'],'Native_imported_or_executed':False,'scope':'Real protocol(material=True,evaluation=True), including every declared dependency hash. Operational world/transaction tests remain pending; not a mock-only closure or an already executed adoption.'})
 return {'plan':str(PLAN),'sha256':sha(PLAN),'pure_real_validator_proof':str(proof),'proof_sha256':sha(proof),'Native_executed':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.parse_args();print(json.dumps(build()))
