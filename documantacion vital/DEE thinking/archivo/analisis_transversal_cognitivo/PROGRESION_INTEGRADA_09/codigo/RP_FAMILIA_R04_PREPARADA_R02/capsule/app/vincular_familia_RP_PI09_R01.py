"""Stdlib binding of a fresh RP clone identity before Store.import_state.

No Native import or source/product writes. The capsule is immutable; only its
new diagnostic copy receives exact current transport life/config binding.
"""
from pathlib import Path
import hashlib,json,re
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_';PATTERN=re.compile(re.escape(PREFIX)+r'[A-Z0-9]{1,10}\Z')
RID='pi09_consulta_native12_familia_desde_C_R04';CAP='PI09_CONSULTA_R02_FAMILIA_R04';PAIR_SHA='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f'
def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked family binding')
def bind(store,pair,manifest,life):
 regular(Path(store.root).absolute());root=Path(store.root).resolve(strict=True);regular(root);need(PATTERN.fullmatch(life)is not None,'Explicit bounded RPF diagnostic ID required')
 need(not(root/'estado/ACTIVO.json').exists()and not(root/'estado/vidas'/life).exists()and not(root/'estado/servicios_persistentes'/life).exists()and not(root/'estado/servicios_locales'/life).exists(),'Never bind a selected, existing or partial future')
 contextfile=root.parent/'CONTEXTO_EJECUCION.json';context=read(contextfile)
 need(context.get('life')==life and Path(context['system']).resolve()==root and context.get('recipe')==RID and context.get('variant')=='native12'and context.get('source_code_capsule_key')==CAP and context.get('prefix_manifest_sha256')==PAIR_SHA,'Only the actual new fixed RP family context')
 product=Path(context['product']).resolve(strict=True);need(root!=product/'sistema'and root!=Path(pair).resolve()and not product.is_relative_to(root),'Never bind operational/source product')
 need(sha(Path(pair)/'EXPORTACION_SERVICIO.json')==PAIR_SHA and manifest['life_id']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'and manifest['physical']['tick']==884835,'Only immutable complete C884835 prefix')
 cap=root/'capacidades';configfile=cap/'PI09_REPRODUCCION_FAMILIA_R01.json';scopefile=cap/'PI09_TRANSPORTE_HEREDADO_R02.json';proof=root.parent/'VINCULO_FAMILIA_DIAGNOSTICA_PI09_R01.json';need(not proof.exists(),'A prior family binding is preserved; never automatically repeat partial import')
 config=read(configfile);scope=read(scopefile);need(config.get('schema')=='DEE.PI09.explicit_diagnostic_reproduction_family.v1'and config.get('prefix')==PREFIX and config.get('bound_life_id')is None and scope.get('life_id')=='UNBOUND_PI09_RPF_DIAGNOSTIC','Fresh unbound capsule copy required')
 old={str(p):sha(p)for p in(configfile,scopefile)};config['bound_life_id']=life;scope['life_id']=life
 binding={'recipe':RID,'exact_life_id':life,'full_C_manifest_sha256':PAIR_SHA,'capsule_manifest_sha256':context['source_code_manifest_sha256'],'Native_inputs_changed':False,'Native_state_created_yet':False,'not_learning_or_new_principal':True}
 config['administrative_binding']=binding;scope['diagnostic_family_binding']=binding
 for file,value in((configfile,config),(scopefile,scope)):
  temp=file.with_name(file.name+'.BINDING');need(not temp.exists(),'Partial binding preserved')
  with temp.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
  temp.replace(file)
 evidence={'schema':'DEE.PI09.explicit_diagnostic_family.bound_before_native.v1',**binding,'files_before':old,'files_after':{str(p):sha(p)for p in(configfile,scopefile)},'new_native_ticks':0,'new_native_inputs':0}
 with proof.open('x',encoding='utf8')as f:json.dump(evidence,f,ensure_ascii=False,indent=2);f.write('\n')
 return evidence
