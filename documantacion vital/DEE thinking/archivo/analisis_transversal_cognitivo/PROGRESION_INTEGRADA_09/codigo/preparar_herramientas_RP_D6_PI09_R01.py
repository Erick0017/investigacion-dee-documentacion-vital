"""Prepare new D6 owned frontdoor/guard/registrar from literal R04 tools."""
from pathlib import Path
import ast,hashlib,json
H=Path(__file__).resolve().parent;STAGE=H/'RP_D6_INCORPORACION_R01_PREPARADA'
RID='pi09_d6_familia_desde_DISCOVERY_T907543_R01';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DRF_20261111A';DEST='RP_D_FAMILIA_R01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(t,a,b):
 if t.count(a)!=1:raise ValueError('Exact used R04 source anchor changed '+a[:90])
 return t.replace(a,b)
def main():
 plan=json.loads((STAGE/'PLAN.json').read_text('utf-8-sig'));recipe=json.loads((STAGE/'receta.json').read_text('utf-8-sig'));finaltick=recipe['sources']['actual_real6']['final_tick'];oldplan=json.loads((H/'RP_FAMILIA_R04_PREPARADA_R02/PLAN.json').read_text('utf-8-sig'))
 names={'supervisar_RP_FAMILIA_PI09_R04.py':'supervisar_RP_D6_FAMILIA_PI09_R01.py','guardia_frontdoor_RP_FAMILIA_PI09_R04.py':'guardia_frontdoor_RP_D6_FAMILIA_PI09_R01.py','registrar_RP_FAMILIA_PI09_R04.py':'registrar_RP_D6_FAMILIA_PI09_R01.py'};rows=[]
 for source_name,target_name in names.items():
  source=H/source_name;out=H/target_name
  if out.exists():raise FileExistsError('New D6 tool already present; preserve used source')
  t=source.read_text('utf-8-sig').replace('pi09_consulta_native12_familia_desde_C_R04',RID).replace('ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_RPF_20261111A',LIFE).replace('RP_FAMILIA_R04_R01',DEST).replace("VARIANT='native12'","VARIANT='real6'").replace("=='native12'","=='real6'")
  for old,new in names.items():t=t.replace(old,new)
  t=t.replace(oldplan['recipe_sha256'],plan['recipe_sha256']).replace(oldplan['capsule_manifest_sha256'],plan['capsule_manifest_sha256'])
  t=t.replace('SUPERVISION_RP_FAMILIA_PI09_R04','SUPERVISION_RP_D6_FAMILIA_PI09_R01').replace('GUARDIA_DRIVER_RP_FAMILIA_PI09_R04','GUARDIA_DRIVER_RP_D6_FAMILIA_PI09_R01').replace('RP_FAMILIA_REGISTRADA_PI09_R04','RP_D6_FAMILIA_REGISTRADA_PI09_R01').replace('RP_FAMILIA_REGISTRO_PI09_R04','RP_D6_FAMILIA_REGISTRO_PI09_R01').replace('RP_FAMILIA_INCORPORADA_PI09_R04.json','RP_D6_FAMILIA_INCORPORADA_PI09_R01.json')
  t=t.replace("INITIAL=884835","INITIAL=907543").replace('BOUND=12*2280','BOUND=13063').replace('BOUND=12*STEP_BOUND','BOUND=13063').replace('STEP_BOUND=2280','STEP_BOUND=2110').replace('903603 and sha(system/card','%d and sha(system/card'%finaltick).replace("result.get('last_tick')==903603","result.get('last_tick')==%d"%finaltick)
  t=t.replace('08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f','8500dafda573afb48ca631b1a7cd3f2cdb1131769485f49811f4f1cfac5fe067')
  t=t.replace('completed_material_requests\')!=14',"completed_material_requests')!=8").replace('len(steps)==14','len(steps)==8').replace("'step_expected':14,'final_checks':180","'step_expected':8,'final_checks':96").replace("'registered_canonical_ticks':18768","'registered_canonical_ticks':%d"%(finaltick-907543))
  t=t.replace('DEE.PI09.RP.family_cold12.owned_supervision.R04','DEE.PI09.D.RP.family6.owned_supervision.R01').replace('DEE.PI09.RP.family_external_per_request_guard.R04','DEE.PI09.D.RP.family6.external_guard.R01').replace('DEE.PI09.RP.family_actual_cold12.additive_registration.R04','DEE.PI09.D.RP.family6.additive_registration.R01')
  if source_name.startswith('guardia'):
   t=once(t,"def allowance(step):return STEP_BOUND if step['literal']['modo']=='eci01-pi09-episodio'else 0","def allowance(step):\n if step['literal']['modo']=='eci01-pi09-d-preparar':return 3\n if step['literal']['modo']=='eci01-pi09-d-episodio':return STEP_BOUND+(400 if step['label']=='D_EP_03'else 0)\n return 0")
  if source_name.startswith('supervisar'):
   # The supervisor protects current Native903603. It never advances it.
   t=t.replace("selected in(A,'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01')","selected=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01'")
  if source_name.startswith('registrar'):
   old="need(result['native_receipts']=={'unique_requested':2280,'applied':2280,'rejected':0,'pending_or_other':0,'scope':'Only explicit receipt_paths frozen in recipe; aliases deduplicated by Native ID.'},'Actual2280/2280 direct receipts required')"
   dose=recipe['variants']['real6']['native_receipt_expectations'];expected={**dose,'scope':'Only explicit receipt_paths frozen in recipe; aliases deduplicated by Native ID.'};t=once(t,old,'need(result[\'native_receipts\']=='+repr(expected)+",'Actual frozen D6 guard+whole two-stage receipt dose required')")
   start=t.index(" note='PI09 cold12");end=t.index('\n stdout=',start);t=t[:start]+" note='PI09 D6 actual generic-family gestionar/RP frontdoor. Full source6 Native comparison '+sha(comparison_file)+'. Frozen actual errors, NULL and terminal conflicts are preserved; equality is separate from all-six usefulness. No first-query credit or learned guard claim.'"+t[end:]
   t=t.replace("'actual_prior_native_replay_ticks':18768","'actual_prior_native_replay_ticks':%d"%(finaltick-907543))
  ast.parse(t);out.write_text(t,'utf8');rows.append({'source':source_name,'source_sha256':sha(source),'file':target_name,'sha256':sha(out)})
 proof={'schema':'DEE.PI09.D.RP.generic_family6.tools_prepared.R01','Native_executed':False,'files':rows,'life_id':LIFE,'recipe':RID,'source_actual6_tick':finaltick,'expected_ticks':finaltick-907543,'conservative_whole_bound':13063,'shared_RP_tools_changed':False}
 (H/'HERRAMIENTAS_RP_D6_FAMILIA_PI09_R01.json').write_text(json.dumps(proof,indent=2)+'\n','utf8');print(json.dumps(proof))
if __name__=='__main__':main()
