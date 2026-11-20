"""Prepare D6 reusable RP capsule from frozen Discovery code; no state read."""
from pathlib import Path
import argparse,ast,hashlib,json,shutil
H=Path(__file__).resolve().parent;P=H.parent;SOURCE=P/'estados/DISCOVERY/sistema';KEY='PI09_D_FAMILIA_R01';RID='pi09_d6_familia_desde_DISCOVERY_T907543_R01';PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DRF_'
PAIR_SHA='8500dafda573afb48ca631b1a7cd3f2cdb1131769485f49811f4f1cfac5fe067'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def once(t,a,b):need(t.count(a)==1,'Exact D transport anchor changed '+a[:70]);return t.replace(a,b)
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--destino',type=Path,default=H/'RP_D_FAMILIA_R01_PREPARADA');a=ap.parse_args();out=a.destino.resolve();need(out.is_relative_to(H.resolve())and not out.exists(),'Fresh P9 codigo proposal only');mf=SOURCE.parent/'SISTEMA_CODIGO_PI09.json';m=read(mf)
 need(m.get('D_permissions_resolved')is True,'Wait for Root D overlay; never use a partial source code closure')
 for row in m['files']:need(not row['file'].startswith(('estado/','runtime/'))and sha(SOURCE/row['file'])==row['sha256'],'Frozen code closure changed '+row['file'])
 cap=out/'capsule';cap.mkdir(parents=True)
 for row in m['files']:
  target=cap/row['file'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(SOURCE/row['file'],target)
 body='c9938b50fbdf68d94954eaf341abae025faa307e4c8d24d23862c7b78bf085f8';need(sha(cap/'capacidades/pi09_entorno_persistente_D_R02.py')==body,'Literal D body required')
 for name,relative in(('pi09_reproduccion_D_familia_R01.py','capacidades/'),('vincular_familia_D_RP_PI09_R01.py','app/')):shutil.copyfile(H/name,cap/relative/name)
 put(cap/'capacidades/PI09_REPRODUCCION_D_FAMILIA_R01.json',{'schema':'DEE.PI09.D.explicit_diagnostic_family.v1','prefix':PREFIX,'suffix_pattern':'[A-Z0-9]{1,10}','bound_life_id':None,'scientific_source_sha256':body,'only_real':True,'pre_D_manifest_sha256':PAIR_SHA,'selected_or_control_policy_forbidden':True,'partial_binding_never_retried':True})
 for name in('PI09_TRANSPORTE_HEREDADO_R02.json','PI09_TRANSPORTE_D_R02.json'):
  file=cap/'capacidades'/name;value=read(file);value['life_id']='UNBOUND_PI09_DRF_DIAGNOSTIC'
  if name=='PI09_TRANSPORTE_D_R02.json':value['role']='reproduction'
  put(file,value)
 file=cap/'capacidades/PI09_PLUGINS_D_R02.json';registry=read(file);need(registry['plugins'].count('pi09_entorno_persistente_D_R02')==1,'Canonical D real plugin required')
 registry['plugins']=['pi09_reproduccion_D_familia_R01'if name=='pi09_entorno_persistente_D_R02'else name for name in registry['plugins']]
 for name in('PI09_TRANSPORTE_HEREDADO_R02.json','PI09_TRANSPORTE_D_R02.json'):registry['files_sha256'].pop(name,None)
 registry['files_sha256']['pi09_reproduccion_D_familia_R01.py']=sha(cap/'capacidades/pi09_reproduccion_D_familia_R01.py');registry['diagnostic_family_bound_configs']='Exactly3 JSON bindings checked before import and by passive replay comparator; scientific seal remains literal';put(file,registry)
 world=cap/'app/mundo_genesis_apd05.py';text=world.read_text('utf-8-sig');anchor='        result=super()._open_locked()';text=once(text,anchor,anchor+'\n        from capacidades import pi09_reproduccion_D_familia_R01 as reproduction_family\n        reproduction_family.install_transport()  # New isolated RP identity only; no Native input.')
 ast.parse(text);world.write_text(text,'utf8')
 importer=cap/'app/importacion_emparejada.py';text=importer.read_text('utf-8-sig');anchor='    source,m,verification=verify_export(directory)';text=once(text,anchor,anchor+'\n    from app.vincular_familia_D_RP_PI09_R01 import bind\n    family_binding=bind(store,source,m,life)')
 text=once(text,'\n    atomic_json(marker,mapping)',"\n    mapping['diagnostic_family_binding']=family_binding\n    atomic_json(marker,mapping)")
 anchor="        mapping['external_directory_scaffold']=restore_known_device_directories(store.state/'servicios_locales'/life)";text=once(text,anchor,anchor+'\n        from app.directorios_D_RP_PI09_R01 import restore_declared\n        mapping[\'manifest_declared_directories\']=restore_declared(store,source,m,life)');ast.parse(text);importer.write_text(text,'utf8')
 directory=(H/'RP_FAMILIA_R04_PREPARADA_R02/capsule/app/directorios_RP_PI09_R02.py').read_text('utf-8-sig').replace('PI09_RPF_','PI09_DRF_').replace("manifest.get('life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'and manifest.get('physical',{}).get('tick')==884835","manifest.get('life_id')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'and manifest.get('physical',{}).get('tick')==907543")
 ast.parse(directory);(cap/'app/directorios_D_RP_PI09_R01.py').write_text(directory,'utf8')
 rows=[{'file':p.relative_to(cap).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}for p in sorted(cap.rglob('*'))if p.is_file()]
 put(cap/'SISTEMA_CODIGO.json',{'schema':'DEE.PI09.D.preserved_family_reproduction_code.R01','files':rows,'canonical_D_source_manifest_sha256':sha(mf),'scientific_D_R02_C_B_body_and_seals_literal':True,'only_reproduction_identity_and_full_directory_transport_changed':True,'Native_replay_executed':False})
 for name,digest in read(cap/'capacidades/SELLO_PI09_D_R02.json')['files_sha256'].items():need(sha(cap/'capacidades'/name)==digest,'Scientific D seal source changed '+name)
 plan={'schema':'DEE.PI09.D.family_capsule.prepared.R01','applied':False,'Native_executed':False,'code_capsule_key':KEY,'recipe':RID,'variant':'real6','family':PREFIX+'[A-Z0-9]{1,10}','first_validation_life':PREFIX+'20261111A','capsule_files':len(rows),'capsule_manifest_sha256':sha(cap/'SISTEMA_CODIGO.json'),'source_manifest_sha256':sha(mf),'complete_pre_D_pair_sha256':PAIR_SHA,'remaining':['Actual Real6 closed proof/primaries to freeze evaluator expectations','Root stable pair/capsule/recipe CAS registration','Root owned512MiB CLI replay6 then strict passive comparator/additive registrar'],'shared_RP_tools_changed':False}
 put(out/'PLAN.json',plan);print(json.dumps({'prepared':str(out),'files':len(rows),'manifest_sha256':plan['capsule_manifest_sha256'],'Native_executed':False}))
if __name__=='__main__':main()
