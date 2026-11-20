"""Versioned RP-only directory transport; preserve R02 proposal and bodies."""
from pathlib import Path
import ast,hashlib,json,shutil
H=Path(__file__).resolve().parent;OLD=H/'RP_CAPSULA_PI09_R02_PROPUESTA';OUT=H/'RP_CAPSULA_PI09_R03_PROPUESTA'
CAP='PI09_CONSULTA_SELECTIVA_R02_TRANSPORTE_R03';RECIPE='pi09_consulta_native12_desde_C_T884835_R03'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def require(ok,msg):
 if not ok:raise ValueError(msg)
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def main():
 require(not OUT.exists(),'Propuesta R03 existente preservada')
 oldmanifest=OLD/'capsule/SISTEMA_CODIGO.json';m=read(oldmanifest);cap=OUT/'capsule';cap.mkdir(parents=True)
 for row in m['files']:
  source=OLD/'capsule'/row['file'];require(sha(source)==row['sha256'],'Cambió el código propuesto anterior')
  target=cap/row['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
 file=cap/'app/importacion_emparejada.py';before=sha(file);text=file.read_text('utf-8-sig')
 anchor="        mapping['external_directory_scaffold']=restore_known_device_directories(store.state/'servicios_locales'/life)"
 require(text.count(anchor)==1,'Cambió el ancla exacta del importador transportado')
 text=text.replace(anchor,anchor+"\n        from app.directorios_RP_PI09_R01 import restore_declared\n        mapping['manifest_declared_directories']=restore_declared(store,source,m,life)")
 ast.parse(text);file.write_text(text,'utf8');target=cap/'app/directorios_RP_PI09_R01.py';shutil.copyfile(H/'directorios_RP_PI09_R01.py',target);ast.parse(target.read_bytes())
 rows=[{'file':p.relative_to(cap).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(cap.rglob('*'))if p.is_file()]
 write(cap/'SISTEMA_CODIGO.json',{'schema':'DEE.PI09.preserved_reproduction_code.v1','files':rows,'source_canonical_code_manifest_sha256':m['source_canonical_code_manifest_sha256'],'source_R02_proposal_manifest_sha256':sha(oldmanifest),'scientific_source_and_protocol_bytes_preserved':True,'Native_reproduction_executed':False,'transport_only_delta':{'file':'app/importacion_emparejada.py','before_sha256':before,'after_sha256':sha(file),'supplement':'app/directorios_RP_PI09_R01.py','purpose':'Restore exact manifest empty directories before first Owner; shared RP importer remains literal'}})
 recipe=read(OLD/'recipe_PREPARADA.json');recipe.update(id=RECIPE,code_capsule_key=CAP,revision='R03_PREPARED_TRANSPORT_FIXED_EXPECTATIONS_NOT_FINAL')
 for step in recipe['variants']['native12']['batches'][0]:
  if step['label'].startswith('EP_'):
   step.pop('max_ticks',None)
   step['read_path']=['result','rows',0,'first_stage','reader','choice'];step['stop_on_NULL']=False
   step['NULL_handling']='Preserve actual first Native NULL as invalid selection/declared NoQuery, never0. Do not add a replay-only stop absent from the frozen actor.'
 recipe['variants']['native12']['documented_actor_bound']={'max_ticks_per_C_opportunity':2110,'separate_wait_max':11,'whole_max':2121,'enforced_by':'Frozen C two-stage calendar check plus PI09 protocol wait validator; outer512MiB supervised job still mandatory','recipe_field_max_ticks_not_enforced_by_shared_RP_driver':True}
 recipe['variants']['native12']['observables_to_freeze']=['first_stage.reader.choice','first_stage.native_motor','first_stage.actual_query_motor','first_stage.sample_register','second_stage.reader.choice','second_stage.FI.early_physical_choice','actual_failed','returned_failed','Native_inputs','whole_new_native_ticks','physical_after/actual whole Native prefix via separate passive comparator']
 recipe['sources']['capsule_manifest_sha256']=sha(cap/'SISTEMA_CODIGO.json')
 recipe['limitations'].extend(['Recipe equality includes original first Native NULL explicitly; this is reproduction equality, not functional success','No per-step max_ticks enforcement added to shared RP driver; original actor bounds and Root owned supervisor remain required'])
 write(OUT/'recipe_PREPARADA.json',recipe)
 write(OUT/'PLAN.json',{'schema':'DEE.PI09.RP_capsule_recipe.prepared.R03','applied':False,'Native_executed':False,'source_state_read':False,'code_capsule_key':CAP,'capsule_files':len(rows),'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'recipe':RECIPE,'required_life_id':recipe['required_life_id'],'original_R02_proposal_preserved':str(OLD),'directory_import_delta':read(cap/'SISTEMA_CODIGO.json')['transport_only_delta'],'scientific_sources_preserved':True,'recipe_enabled':False,'remaining':['Actual canonical12 observables/portable analysis','Root code review and scoped RP required_life_id guard','Root CAS preservation/registration then actual owned cold12 CLI','Passive whole Native comparison and actual additive verification']})
 print(json.dumps({'prepared':str(OUT),'files':len(rows),'manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'Native_executed':False}))
if __name__=='__main__':main()
