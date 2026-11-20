"""Prepare RP code/draft recipe from immutable canonical code only.

Safe while Native is running: never reads its card, SQLite or checkpoint.
Writes codigo only. No product mutation or claim of material reproduction.
"""
from pathlib import Path
import argparse,hashlib,json,shutil
P=Path(__file__).resolve().parents[1];D=P/'estados/NATIVE';S=D/'sistema';OUT=P/'codigo/RP_CAPSULA_PI09_R02_PROPUESTA'
CAP='PI09_CONSULTA_SELECTIVA_R02';RECIPE='pi09_consulta_native12_desde_C_T884835_R02';REPRO='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 require(not OUT.exists(),'Cápsula propuesta ya existe')
 mf=D/'SISTEMA_CODIGO_PI09.json';m=read(mf);seal=read(S/'capacidades/SELLO_PI09_CONSULTA_R02.json')
 require(REPRO in seal['native_reproduction_ids'],'REPRO exacta debe estar preautorizada')
 require(sha(S/'capacidades/pi09_consulta_selectiva_R02.py')=='3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf','Cuerpo científico distinto')
 cap=OUT/'capsule';cap.mkdir(parents=True)
 for row in m['files']:
  name=row['file'];require(not name.startswith(('estado/','runtime/'))and '..'not in Path(name).parts,'Sólo código/dependencias')
  source=S/name;require(source.is_file()and sha(source)==row['sha256'],'Fuente de código cambió: '+name)
  target=cap/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 scopefile=cap/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json';scope=read(scopefile);scope['life_id']=REPRO
 scope['reproduction_identity_scope']={'exact_sealed_id':REPRO,'source_code_manifest_sha256':sha(mf),'Native_metadata_life_ids_not_rewritten':True}
 scopefile.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n','utf8')
 rows=[{'file':p.relative_to(cap).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(cap.rglob('*'))if p.is_file()]
 write(cap/'SISTEMA_CODIGO.json',{'schema':'DEE.PI09.preserved_reproduction_code.v1','files':rows,'source_canonical_code_manifest_sha256':sha(mf),'administrative_scope_rebound_only':True,'scientific_source_and_protocol_bytes_preserved':True,'Native_reproduction_executed':False})
 prefix='PI09_C_HEREDADA_T884835';base=['result','rows',0]
 steps=[{'label':'PREPARAR_NATIVE','literal':{'modo':'eci01-pi09-preparar','brazo':'native_real'},'require_zero_ticks':True,'read_path':base+['ready'],'expected':True,'feedback':'real','actuator':'closed'}]
 for index in range(12):steps.append({'label':'EP_%02d'%index,'literal':{'modo':'eci01-pi09-episodio'},'feedback':'real','actuator':'closed','read_path':base+['actual_failed'],'receipt_paths':[base+['requests']],'stop_on_NULL':True,'stop_on_unapplied_receipt':False,'max_ticks':2280})
 steps.append({'label':'STATE_FINAL','literal':{'modo':'eci01-pi09-estado'},'require_zero_ticks':True,'read_path':base+['progress','ordinal'],'expected':12,'feedback':'real','actuator':'closed'})
 recipe={'schema':'DEE.reproduction.recipe.v1','id':RECIPE,'title':'PI09 canonical Native-real acquisition12 from preserved complete C','revision':'R02_PREPARED_EXPECTATIONS_NOT_FINAL','prefix':prefix,'code_capsule_key':CAP,'required_life_id':REPRO,'required_life_prefix':'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_','requires_explicit_material':True,'reproduction_enabled':False,
  'variants':{'native12':{'batches':[steps],'interpretation':'Fixed protocol and Native selection. Expected episode observables must be frozen from actual canonical12 primaries before execution is enabled. Conflicts can be material results; never convert0 intoNULL or hide adverse outcomes.'}},
  'verification':{'state':'PREPARADA_NATIVE_REPLAY_PENDIENTE','Native_replay_verified':False,'expected_observables_frozen':False},
  'assistance':['Prepared inherited Native TC/sensor/device and fixed two-stage schedule','Actual technical sample register; only second trace has established consequence credit','Administrative18-offer lot, old C/B histories preserved','Fixed native_real control; expected values auditor-only after outputs'],
  'limitations':['No controlled new Native first-trace credit or general curiosity claim','Cannot infer12successes or causal information benefit before actual controls','New RP frontdoor Native reproduction not executed'],
  'sources':{'full_C_manifest_sha256':'08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f','protocol_sha256':sha(S/'capacidades/PROTOCOLO_PI09_CONSULTA_R01.json'),'prospective_seal_sha256':sha(S/'capacidades/SELLO_PI09_CONSULTA_R02.json'),'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json')}}
 write(OUT/'recipe_PREPARADA.json',recipe)
 write(OUT/'PLAN.json',{'schema':'DEE.PI09.RP_capsule_recipe.prepared.R02','applied':False,'Native_executed':False,'source_state_read':False,'code_capsule_key':CAP,'capsule_files':len(rows),'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'recipe':RECIPE,'required_life_id':REPRO,
   'remaining':['Root verify stable RP prefix alias copy','Root optional required_life_id microguard before world creation after current imports close','Freeze evaluator-only exact observables/doses/physical prefix from actual canonical12 closed','Root CAS register capsule/recipe/analysis then actual CLI cold12 in fresh diagnostic destination','Record actual Native closed verification; prepared is not executed']})
 print(json.dumps({'prepared':str(OUT),'files':len(rows),'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'Native_executed':False,'source_state_read':False}))
if __name__=='__main__':main()
