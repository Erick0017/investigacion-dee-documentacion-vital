"""Generate separate reviewed R04 supervisors from literal used R03 tools."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent
OLDID='pi09_consulta_native12_desde_C_T884835_R03';RID='pi09_consulta_native12_familia_desde_C_R04'
OLDLIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_REPRO_01';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_20261111A'
NAMES={'supervisar_RP_NATIVE12_PI09_R01.py':'supervisar_RP_FAMILIA_PI09_R04.py','guardia_frontdoor_RP_NATIVE12_PI09_R01.py':'guardia_frontdoor_RP_FAMILIA_PI09_R04.py','contrastar_RP_NATIVE12_PI09_R01.py':'contrastar_RP_FAMILIA_PI09_R04.py','registrar_RP_NATIVE12_PI09_R01.py':'registrar_RP_FAMILIA_PI09_R04.py'}
def need(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def replace_one(text,before,after):
 need(text.count(before)==1,'Exact tool anchor changed: '+before[:100]);return text.replace(before,after)
def main():
 plan=json.loads((H/'RP_FAMILIA_R04_PREPARADA_R02/PLAN.json').read_text('utf-8-sig'));rows=[]
 for oldname,newname in NAMES.items():
  old=H/oldname;out=H/newname;need(not out.exists(),'New tool already exists; preserve it')
  text=old.read_text('utf-8-sig').replace(OLDID,RID).replace(OLDLIFE,LIFE).replace('RP_REPRO_R01','RP_FAMILIA_R04_R01')
  text=text.replace('d41ed2b642c93fee45d61fe933f429822352f96557d1fb590c82346ad06bfac0',plan['recipe_sha256']).replace('67be03d36afc2890cb2d61425fe842509a671f09dcffb6b03ba19ad54afddda5',plan['capsule_manifest_sha256'])
  for before,after in NAMES.items():text=text.replace(before,after)
  text=text.replace('SUPERVISION_RP_NATIVE12_PI09_R01','SUPERVISION_RP_FAMILIA_PI09_R04').replace('GUARDIA_DRIVER_RP_NATIVE12_PI09_R01','GUARDIA_DRIVER_RP_FAMILIA_PI09_R04').replace('RP_NATIVE12_REGISTRADA_PI09_R01','RP_FAMILIA_REGISTRADA_PI09_R04').replace('RP_NATIVE12_REGISTRO_PI09_R01','RP_FAMILIA_REGISTRO_PI09_R04')
  text=text.replace('original_A_unchanged','protected_principal_unchanged').replace('DEE.PI09.RP.cold12.owned_supervision.R01','DEE.PI09.RP.family_cold12.owned_supervision.R04').replace('DEE.PI09.RP.external_per_request_guard.R01','DEE.PI09.RP.family_external_per_request_guard.R04').replace('DEE.PI09.RP.canonical12.full_passive_comparison.R01','DEE.PI09.RP.family_canonical12.full_passive_comparison.R04').replace('DEE.PI09.RP.actual_cold12.additive_registration.R01','DEE.PI09.RP.family_actual_cold12.additive_registration.R04')
  if oldname.startswith('supervisar'):
   text=text.replace('RP_CONSULTA_INCORPORADA_PI09_R01.json','RP_FAMILIA_INCORPORADA_PI09_R04.json')
   text=text.replace("budget['diagnostic_worlds_all_new']==12","type(budget['diagnostic_worlds_all_new'])is int and 12<=budget['diagnostic_worlds_all_new']<=16")
   before="cardfile=S/'estado/vidas'/A/'VIDA.json';card=read(cardfile);need(read(S/'estado/ACTIVO.json')['life_id']==A and card['physical']['tick']==861426,'Protected A current principal changed before cold12')"
   after="selected=read(S/'estado/ACTIVO.json')['life_id'];need(selected in(A,'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'),'Only protected A or committed quiet Native903603 principal');cardfile=S/'estado/vidas'/selected/'VIDA.json';card=read(cardfile);need(card['physical']['tick']==(861426 if selected==A else 903603),'Protected actual principal cut differs')"
   text=replace_one(text,before,after)
  if oldname.startswith('contrastar'):
   before="system=dest/'sistema';require(not(system/'estado/ACTIVO.json').exists(),'No se contrasta un principal seleccionado')"
   after="""system=dest/'sistema';require(not(system/'estado/ACTIVO.json').exists(),'No se contrasta un principal seleccionado')
 capsule=C/'reproducibilidad/codigo_preservado/PI09_CONSULTA_R02_FAMILIA_R04';cm=read(capsule/'SISTEMA_CODIGO.json')
 require(sha(capsule/'SISTEMA_CODIGO.json')==context['source_code_manifest_sha256'] and context['source_code_capsule_key']=='PI09_CONSULTA_R02_FAMILIA_R04','Cápsula familiar distinta')
 bindingfile=dest/'VINCULO_FAMILIA_DIAGNOSTICA_PI09_R01.json';binding=read(bindingfile)
 expectedbinding={'recipe':context['recipe'],'exact_life_id':REPRO,'full_C_manifest_sha256':context['prefix_manifest_sha256'],'capsule_manifest_sha256':context['source_code_manifest_sha256'],'Native_inputs_changed':False,'Native_state_created_yet':False,'not_learning_or_new_principal':True}
 require(binding['schema']=='DEE.PI09.explicit_diagnostic_family.bound_before_native.v1'and all(binding.get(k)==v for k,v in expectedbinding.items())and binding.get('new_native_ticks')==binding.get('new_native_inputs')==0,'Vínculo administrativo anterior a Native inválido')
 changed={'capacidades/PI09_REPRODUCCION_FAMILIA_R01.json','capacidades/PI09_TRANSPORTE_HEREDADO_R02.json'}
 for item in cm['files']:
  current=system/item['file'];original=capsule/item['file']
  require(sha(original)==item['sha256'],'Cambió la cápsula estable')
  if item['file']not in changed:require(sha(current)==item['sha256'],'Otro código de clon cambió: '+item['file']);continue
  expected=read(original)
  if item['file'].endswith('PI09_REPRODUCCION_FAMILIA_R01.json'):expected['bound_life_id']=REPRO;expected['administrative_binding']=expectedbinding
  else:expected['life_id']=REPRO;expected['diagnostic_family_binding']=expectedbinding
  require(read(current)==expected and binding['files_before'].get(str(current))==item['sha256']and binding['files_after'].get(str(current))==sha(current),'Cambió algo distinto de la identidad administrativa declarada')"""
   text=replace_one(text,before,after)
   text=replace_one(text,"'source_pair_manifest_sha256':PAIR_SHA,","'source_pair_manifest_sha256':PAIR_SHA,'family_binding':{'path':str(bindingfile),'sha256':sha(bindingfile),'only_two_administrative_code_bindings_verified':True},")
  ast.parse(text);out.write_text(text,'utf8');rows.append({'source':oldname,'source_sha256':sha(old),'new':newname,'sha256':sha(out)})
 proof={'schema':'DEE.PI09.RP.family.tools_prepared.R04','Native_executed':False,'shared_RP_tools_changed':False,'life_id':LIFE,'recipe':RID,'files':rows,'notes':['Root material replay required before R04 validation claim','Fixed initial validation ID; generic published recipe later accepts another fresh family ID without code/catalog changes','Actual REG world limit read at execution; no budget expansion performed']}
 (H/'HERRAMIENTAS_RP_FAMILIA_PI09_R04.json').write_text(json.dumps(proof,indent=2)+'\n','utf8');print(json.dumps(proof))
if __name__=='__main__':main()
