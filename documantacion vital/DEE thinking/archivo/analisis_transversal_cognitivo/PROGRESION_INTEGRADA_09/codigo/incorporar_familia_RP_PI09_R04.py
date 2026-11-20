"""Root-only additive reusable RP family. Default prepares code, never Native.

R03 recipe/capsule/verification are preserved literally. R04 changes only the
fresh diagnostic identity binder/admission and declared-directory transport.
The literal R02 scientific body, C/B ancestry, inputs and actual12 expectations
are unchanged. Root must validate a new actual material replay separately.
"""
from pathlib import Path
import argparse,ast,datetime,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
OLDKEY='PI09_CONSULTA_SELECTIVA_R02_TRANSPORTE_R03';OLDID='pi09_consulta_native12_desde_C_T884835_R03'
KEY='PI09_CONSULTA_R02_FAMILIA_R04';RID='pi09_consulta_native12_familia_desde_C_R04';PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_'
STAGE=H/'RP_FAMILIA_R04_PREPARADA_R02';PROOF=P/'control/RP_FAMILIA_INCORPORADA_PI09_R04.json'
OLDMF='67be03d36afc2890cb2d61425fe842509a671f09dcffb6b03ba19ad54afddda5';OLDRSHA='d41ed2b642c93fee45d61fe933f429822352f96557d1fb590c82346ad06bfac0'
BODY='3b81573f4dc0d9401db2210f3b23694e1f1f4a4d820d7654bcbd1e1b42b2dfbf';PAIR='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked RP paths')
def put(p,v):
 regular(p);p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
def cp(src,dst):
 regular(src);regular(dst);dst.parent.mkdir(parents=True,exist_ok=True);before=sha(src)
 with src.open('rb')as i,dst.open('xb')as o:shutil.copyfileobj(i,o)
 need(sha(src)==before==sha(dst),'Source/copy changed')
def verify(root,mf='SISTEMA_CODIGO.json'):
 m=read(root/mf)
 for row in m['files']:
  file=root/row['file'];regular(file);need(file.is_file()and file.stat().st_size==row['bytes']and sha(file)==row['sha256'],'Changed capsule member '+row['file'])
 return m
def protected():
 s=C/'sistema';active=s/'estado/ACTIVO.json';card=s/'estado/vidas'/read(active)['life_id']/'VIDA.json';r=read(card)
 return {str(p):sha(p)for p in(active,card,s/r['snapshot'])}
def prepare():
 if (STAGE/'PLAN.json').is_file():return read(STAGE/'PLAN.json')
 need(not STAGE.exists(),'Prior partial proposal preserved; use an explicit new revision')
 old=RP/'codigo_preservado'/OLDKEY;oldrecipe=RP/'recetas'/(OLDID+'.json');need(sha(old/'SISTEMA_CODIGO.json')==OLDMF and sha(oldrecipe)==OLDRSHA,'Actual verified R03 capsule/recipe changed')
 m=verify(old);cap=STAGE/'capsule';cap.mkdir(parents=True)
 for row in m['files']:cp(old/row['file'],cap/row['file'])
 importer=cap/'app/importacion_emparejada.py';text=importer.read_text('utf-8-sig');before=sha(importer)
 anchor='    source,m,verification=verify_export(directory)';need(text.count(anchor)==1,'Exact importer pre-Native anchor changed')
 text=text.replace(anchor,anchor+'\n    from app.vincular_familia_RP_PI09_R01 import bind\n    family_binding=bind(store,source,m,life)')
 anchor='\n    atomic_json(marker,mapping)';need(text.count(anchor)==1,'Exact first import marker anchor changed')
 text=text.replace(anchor,"\n    mapping['diagnostic_family_binding']=family_binding"+anchor)
 need(text.count('from app.directorios_RP_PI09_R01 import restore_declared')==1,'Exact R03 directory supplement anchor changed')
 text=text.replace('from app.directorios_RP_PI09_R01 import restore_declared','from app.directorios_RP_PI09_R02 import restore_declared');ast.parse(text);importer.write_text(text,'utf8')
 cp(H/'vincular_familia_RP_PI09_R01.py',cap/'app/vincular_familia_RP_PI09_R01.py');cp(H/'pi09_reproduccion_familia_R01.py',cap/'capacidades/pi09_reproduccion_familia_R01.py')
 directory=(H/'directorios_RP_PI09_R01.py').read_text('utf-8-sig');oldguard="require(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01','Este suplemento RP sólo admite la identidad REPRO PI09 predeclarada')";need(directory.count(oldguard)==1,'Directory identity anchor changed')
 directory=directory.replace('import hashlib','import hashlib,re').replace(oldguard,"require(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_[A-Z0-9]{1,10}',life)is not None,'Sólo la familia diagnóstica RP explícita')");ast.parse(directory);(cap/'app/directorios_RP_PI09_R02.py').write_text(directory,'utf8')
 config={'schema':'DEE.PI09.explicit_diagnostic_reproduction_family.v1','prefix':PREFIX,'suffix_pattern':'[A-Z0-9]{1,10}','bound_life_id':None,'scientific_source_sha256':BODY,'only_native_real':True,'binding_before_Store_import_state':True,'source_C_manifest_sha256':PAIR,'selected_and_preexisting_destinations_forbidden':True,'partial_binding_never_automatically_retried':True}
 put(cap/'capacidades/PI09_REPRODUCCION_FAMILIA_R01.json',config)
 scopefile=cap/'capacidades/PI09_TRANSPORTE_HEREDADO_R02.json';scope=read(scopefile);scope['life_id']='UNBOUND_PI09_RPF_DIAGNOSTIC';scope['reproduction_identity_scope']={'diagnostic_family':PREFIX+'[A-Z0-9]{1,10}','binding_before_Native_import':True,'original_R03_exact_id_capsule_preserved':OLDKEY,'Native_metadata_life_ids_not_rewritten':True};scopefile.write_text(json.dumps(scope,ensure_ascii=False,indent=2)+'\n','utf8')
 regfile=cap/'capacidades/PI09_PLUGINS_R02.json';reg=read(regfile);need(reg['plugins'].count('pi09_consulta_selectiva_R02')==1,'Exact R02 plugin registry required');reg['plugins']=['pi09_reproduccion_familia_R01'if name=='pi09_consulta_selectiva_R02'else name for name in reg['plugins']];reg['files_sha256']['pi09_reproduccion_familia_R01.py']=sha(cap/'capacidades/pi09_reproduccion_familia_R01.py');regfile.write_text(json.dumps(reg,ensure_ascii=False,indent=2)+'\n','utf8')
 need(sha(cap/'capacidades/pi09_consulta_selectiva_R02.py')==BODY,'Scientific body changed')
 rows=[{'file':f.relative_to(cap).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)}for f in sorted(cap.rglob('*'))if f.is_file()]
 put(cap/'SISTEMA_CODIGO.json',{'schema':'DEE.PI09.preserved_reproduction_code.v1','files':rows,'source_R03_capsule_manifest_sha256':OLDMF,'source_canonical_code_manifest_sha256':m['source_canonical_code_manifest_sha256'],'scientific_source_and_protocol_bytes_preserved':True,'Native_reproduction_executed':False,'transport_only_delta':{'importer_before_sha256':before,'importer_after_sha256':sha(importer),'family_config_initially_unbound':True,'clone_binding_proof_required':True,'single_validate_line_changes_only_reproduction_identity_admission':True}})
 recipe=read(oldrecipe);recipe.update(id=RID,code_capsule_key=KEY,revision='R04_FRESH_DIAGNOSTIC_FAMILY_TRANSPORT_MATERIAL_VALIDATION_PENDING');recipe.pop('required_life_id',None);recipe['required_life_prefix']=PREFIX
 recipe['identity_contract']={'schema':'DEE.PI09.reproduction.family_identity.v1','prefix':PREFIX,'suffix_pattern':'[A-Z0-9]{1,10}','enforced_before_Native_by':'Capsule app.vincular_familia_RP_PI09_R01.bind; actual RP context+new destination+unused registry ID','selected_lives_forbidden':True,'control_arms_forbidden':True}
 recipe['sources']['capsule_manifest_sha256']=sha(cap/'SISTEMA_CODIGO.json');recipe['sources']['literal_R03_recipe_sha256']=OLDRSHA;recipe['sources']['literal_R03_capsule_manifest_sha256']=OLDMF
 recipe['verification']={'state':'PREPARADA_REPLAY_NATIVE_R04_PENDIENTE','Native_replay_verified':False,'historical_literal_R03_replay_verified_separately':True,'no_material_R04_execution_by_preparation':True}
 recipe['limitations'].append('R04 changes only diagnostic identity transport/admission. First new actual family CLI validation remains pending; old R03 actual verification stays literal. Future IDs do not require code/catalog changes; every execution remains a fresh new bounded diagnostic world.')
 put(STAGE/'receta.json',recipe)
 resources=read(RP/'RECURSOS.json');need(KEY not in resources['code_capsules']and not(RP/'recetas'/(RID+'.json')).exists(),'New capsule and recipe IDs only');need(resources['pairs']['PI09_C_HEREDADA_T884835']['manifest_sha256']==PAIR,'Actual stable complete C alias differs')
 analysis=recipe['analysis'];afile=C/analysis['product_relative']/analysis['manifest'];need(sha(afile)==analysis['manifest_sha256'],'Stable actual Native12 analysis changed')
 resources['code_capsules'][KEY]={'product_relative':'reproducibilidad/codigo_preservado/'+KEY,'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(cap/'SISTEMA_CODIGO.json')};put(STAGE/'RECURSOS_PROPUESTOS.json',resources)
 changes=[{'file':row['file'],'before_sha256':next((r['sha256']for r in m['files']if r['file']==row['file']),None),'after_sha256':row['sha256']}for row in rows if not any(r['file']==row['file']and r['sha256']==row['sha256']for r in m['files'])]
 plan={'schema':'DEE.PI09.RP.reusable_family.CAS_plan.R04','applied':False,'Native_executed':False,'resource_before_sha256':sha(RP/'RECURSOS.json'),'resource_after_sha256':sha(STAGE/'RECURSOS_PROPUESTOS.json'),'recipe':RID,'recipe_sha256':sha(STAGE/'receta.json'),'capsule_key':KEY,'capsule_files':len(rows),'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'preserved_R03_recipe_sha256':OLDRSHA,'preserved_R03_capsule_manifest_sha256':OLDMF,'reused_C_pair_manifest_sha256':PAIR,'reused_analysis_manifest_sha256':analysis['manifest_sha256'],'shared_RP_tools_changed':False,'new_large_state_copies':0,'transport_delta_files':changes,'first_material_validation_life':PREFIX+'20261111A','first_material_validation_pending':True}
 put(STAGE/'PLAN.json',plan);return plan
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');a=ap.parse_args();plan=prepare();need(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'RP registry CAS changed; preserve prepared proposal')
 verify(STAGE/'capsule');need(sha(STAGE/'receta.json')==plan['recipe_sha256']and sha(STAGE/'RECURSOS_PROPUESTOS.json')==plan['resource_after_sha256'],'Prepared metadata changed')
 need(sha(RP/'recetas'/(OLDID+'.json'))==OLDRSHA and sha(RP/'codigo_preservado'/OLDKEY/'SISTEMA_CODIGO.json')==OLDMF,'Historical verified R03 changed')
 if a.aplicar:
  need(not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Only closed writer scope may install RP metadata')
  cap=RP/'codigo_preservado'/KEY;recipe=RP/'recetas'/(RID+'.json');need(not cap.exists()and not recipe.exists()and not PROOF.exists(),'Prior registration or partial destinations preserved')
  prior=protected();cp(RP/'RECURSOS.json',P/'control/RECURSOS_ANTES_FAMILIA_PI09_R04.json')
  for file in sorted((STAGE/'capsule').rglob('*')):
   if file.is_file():cp(file,cap/file.relative_to(STAGE/'capsule'))
  cp(STAGE/'receta.json',recipe);need(sha(RP/'RECURSOS.json')==plan['resource_before_sha256'],'Registry changed during additive copy')
  temp=RP/'RECURSOS.json.PI09_FAMILIA_WRITING';cp(STAGE/'RECURSOS_PROPUESTOS.json',temp);os.replace(temp,RP/'RECURSOS.json');need(protected()==prior,'Current principal changed during RP-only registration')
  put(PROOF,{**plan,'schema':'DEE.PI09.RP.reusable_family.applied.R04','applied':True,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'recipe_path':str(recipe),'code_capsule':str(cap),'capsule_manifest':str(cap/'SISTEMA_CODIGO.json'),'principal_unchanged':True,'protected_principal':prior,'new_frontdoor_R04_material_replay_executed':False})
 file=PROOF if a.aplicar else STAGE/'PLAN.json';print(json.dumps({'mode':'APPLIED_ROOT_ONLY'if a.aplicar else'PREPARED_NO_RP_WRITES','proof':str(file),'sha256':sha(file),'recipe':RID,'Native_executed':False}))
if __name__=='__main__':main()
