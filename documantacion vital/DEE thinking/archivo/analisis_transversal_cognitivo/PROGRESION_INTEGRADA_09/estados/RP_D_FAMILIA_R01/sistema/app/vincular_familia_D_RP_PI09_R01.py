"""Bind only a new RP D diagnostic copy before any Store.import_state."""
from pathlib import Path
import hashlib,json,re
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DRF_';RID='pi09_d6_familia_desde_DISCOVERY_T907543_R01';CAP='PI09_D_FAMILIA_R01';PAIR_SHA='8500dafda573afb48ca631b1a7cd3f2cdb1131769485f49811f4f1cfac5fe067'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked D family binding')
def bind(store,pair,manifest,life):
 regular(Path(store.root).absolute());root=Path(store.root).resolve(strict=True);need(re.fullmatch(re.escape(PREFIX)+r'[A-Z0-9]{1,10}',life)is not None,'Bounded fresh DRF diagnostic ID required')
 need(not(root/'estado/ACTIVO.json').exists()and all(not(root/'estado'/name/life).exists()for name in('vidas','servicios_locales','servicios_persistentes')),'Never bind selected, used or partially imported life')
 context=read(root.parent/'CONTEXTO_EJECUCION.json');need(context.get('life')==life and Path(context['system']).resolve()==root and context.get('recipe')==RID and context.get('variant')=='real6'and context.get('source_code_capsule_key')==CAP and context.get('prefix_manifest_sha256')==PAIR_SHA,'Only the fixed actual RP D family context')
 product=Path(context['product']).resolve(strict=True);need(root!=product/'sistema'and root!=Path(pair).resolve()and not product.is_relative_to(root),'No operational/source product identity binding')
 need(sha(Path(pair)/'EXPORTACION_SERVICIO.json')==PAIR_SHA and manifest['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'and manifest['physical']['tick']==907543,'Exact complete pre-D907543 source required')
 cap=root/'capacidades';files=[cap/name for name in('PI09_REPRODUCCION_D_FAMILIA_R01.json','PI09_TRANSPORTE_HEREDADO_R02.json','PI09_TRANSPORTE_D_R02.json')];values=[read(p)for p in files];proof=root.parent/'VINCULO_FAMILIA_D_DIAGNOSTICA_PI09_R01.json'
 need(not proof.exists()and values[0].get('schema')=='DEE.PI09.D.explicit_diagnostic_family.v1'and values[0].get('bound_life_id')is None and values[1].get('life_id')==values[2].get('life_id')=='UNBOUND_PI09_DRF_DIAGNOSTIC','Fresh unbound D capsule copy required; partial binding is never retried')
 binding={'recipe':RID,'exact_life_id':life,'full_pre_D_manifest_sha256':PAIR_SHA,'capsule_manifest_sha256':context['source_code_manifest_sha256'],'Native_inputs_changed':False,'Native_state_created_yet':False,'not_learning_or_new_principal':True};before={str(p):sha(p)for p in files}
 values[0]['bound_life_id']=life;values[0]['administrative_binding']=binding
 for value in values[1:]:value['life_id']=life;value['diagnostic_family_binding']=binding
 for p,value in zip(files,values):
  temp=p.with_name(p.name+'.BINDING');need(not temp.exists(),'Partial administrative binding preserved')
  with temp.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
  temp.replace(p)
 result={'schema':'DEE.PI09.D.diagnostic_family.bound_before_native.v1',**binding,'files_before':before,'files_after':{str(p):sha(p)for p in files},'new_native_ticks':0,'new_native_inputs':0}
 with proof.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 return result
