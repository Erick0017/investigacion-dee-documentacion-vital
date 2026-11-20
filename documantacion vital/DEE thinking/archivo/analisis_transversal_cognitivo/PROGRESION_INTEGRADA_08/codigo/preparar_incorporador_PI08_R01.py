"""Prepare a conditional same-ID PI08 successor installer from the reviewed
PI07 base. No application, Store import, Native or product write occurs here.
"""
from pathlib import Path
import ast,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo';P7=P.parent/'PROGRESION_INTEGRADA_07';oldlife='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01';newlife='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 target=H/'incorporar_PI08_misma_identidad_R01.py';adapter=H/'pi08_identidad_c2c_R01.py'
 if target.exists()or adapter.exists():raise FileExistsError('Prepared revision preserved')
 source=P7/'codigo/incorporar_PI07_misma_identidad_R02.py';s=source.read_text('utf-8-sig').replace("CS=P/'estados/candidato/sistema'","CS=P/'estados/RP_A01/sistema'").replace(oldlife,newlife)
 for old,new in [('PRODUCTO_PI07','PRODUCTO_PI08'),('INCORPORACION_PI07','INCORPORACION_PI08'),('PI07_WRITING','PI08_WRITING'),('PI07_DEPLOY','PI08_DEPLOY'),('DEE.PI07.same_identity','DEE.PI08.same_identity'),('PI07_relocation_passive','PI08_relocation_passive'),('prior_selection_PI07','prior_selection_PI08'),('PI07_prior_selected_seed','PI08_prior_selected_seed'),('prior_cut_PI07','prior_cut_PI08'),('PI07_same_identity_relocation_map','PI08_same_identity_relocation_map'),('PI07_prior_current_principal','PI08_prior_current_principal'),('PI07_ADOPCION_OPERATIVA_01','PI08_ADOPCION_OPERATIVA_01'),('app/pi07_identidad_c2c_R02.py','app/pi08_identidad_c2c_R01.py'),('app.pi07_identidad_c2c_R02','app.pi08_identidad_c2c_R01'),('PI07_REGULACION_USO_PRINCIPAL_01.json','PI08_USO_OPERATIVO_R01.json')]:s=s.replace(old,new)
 # Prepared source permission contracts are not code payloads. They become
 # COMMITTED only after actual Store.promote, before the selected owner opens.
 old=" required=('app/pi08_identidad_c2c_R01.py','app/usar_dee.py','capacidades/pi07_regulacion_R01.py','capacidades/PROTOCOLO_PI07_R01.json','capacidades/pi07_regulacion_R02.py','capacidades/PROTOCOLO_PI07_R02.json','capacidades/pi07_regulacion_R03.py','capacidades/PROTOCOLO_PI07_R03.json')"
 new=" required=('app/pi08_identidad_c2c_R01.py','app/usar_dee.py','capacidades/pi07_regulacion_R01.py','capacidades/PROTOCOLO_PI07_R01.json','capacidades/pi07_regulacion_R02.py','capacidades/PROTOCOLO_PI07_R02.json','capacidades/pi07_regulacion_R03.py','capacidades/PROTOCOLO_PI07_R03.json','capacidades/pi07_acceso_FI_regulado_R01.py','capacidades/PROTOCOLO_PI07_ACCESO_FI_R01.json','capacidades/pi08_integracion_c2c_R01.py','capacidades/PROTOCOLO_PI08_C2C_32_R01.json','capacidades/PROTOCOLO_PI08_C2C_INTEGRACION_R01.json','capacidades/pi08_permisos_operativos_R01.py')"
 if old not in s:raise ValueError('Exact required-source baseline differs')
 s=s.replace(old,new)
 old=" if set(d['selectors_cas'])!=set(SELECTORS):raise ValueError('All six existing product references need CAS')\n return d"
 new=""" if set(d['selectors_cas'])!=set(SELECTORS):raise ValueError('All six existing product references need CAS')
 contract=d['new_contract']
 if (contract.get('schema')!='DEE.PI08.exact_operational_profile.v1'or contract.get('life_id')!=LIFE or contract.get('R03_protocol_sha256')!='f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269'or contract.get('FI_protocol_sha256')!='4f15e2c892ab067c46338a7d89c0c6714b68f1436f936568e723a6bc1a7ccbc6'or contract.get('all_outer_FI_requests')is not True or contract.get('internal_C2C_FI_redirected')is not False or contract.get('public_FI_domain')!=[0,20]):raise ValueError('Exact all-outer public FI migration/identity profile required')
 for witness in('PI08_A1_PRECONTROL_REAL_R01.json','PI08_A1_POSTCONTROL_REAL_R02.json'):
  proof=read(CONTROL/witness)
  if proof.get('life_id')!=LIFE or proof.get('closed')is not True or proof.get('criteria_met')is not True or proof.get('new_Native_ticks')!=0 or not all(proof.get('full_Native_field_equalities',{}).values()):raise ValueError('Actual full-route A1 prepare/commit/idempotence/reopen witnesses required: '+witness)
 return d"""
 if old not in s:raise ValueError('Exact decision validation baseline differs')
 s=s.replace(old,new)
 # Public selected profile is absent during prepare, or an exact prepared
 # diagnostic profile must be preserved before the final committed update.
 old=" if path.exists()and read(path)!=contract:raise FileExistsError('Another permission contract preserved')\n if not path.exists():write(path,contract)"
 new=""" if path.exists()and read(path)!=contract:
  prior=read(path)
  if prior.get('schema')!='DEE.PI08.exact_operational_profile.v1'or prior.get('life_id')!=LIFE or prior.get('status')!='PREPARED_DIAGNOSTIC':raise FileExistsError('Another permission contract preserved')
  write(CONTROL/'PERFIL_PREPARADO_ANTES_COMMITTED_PI08.json',prior)
  write(path,contract,True)
 elif not path.exists():write(path,contract)"""
 if old not in s:raise ValueError('Exact contract publication baseline differs')
 s=s.replace(old,new);ast.parse(s);target.write_text(s,encoding='utf8')
 identity_source=P7/'codigo/pi07_identidad_c2c_R02.py';i=identity_source.read_text('utf-8-sig').replace(oldlife,newlife).replace('PI07 main','PI08 main').replace('DEE.PI07.C2C.same_identity','DEE.PI08.C2C.same_identity').replace('AFTER_SAME_ID_MOVE_PI07','AFTER_SAME_ID_MOVE_PI08');ast.parse(i);adapter.write_text(i,encoding='utf8')
 launcher_source=P7/'codigo/PI07_LAUNCHER_EXISTENTE_PREPARADO/app/usar_dee.py';launcher=H/'usar_dee_existente_PI08_R01.py'
 if launcher.exists():raise FileExistsError('Prepared launcher preserved')
 launcher.write_bytes(launcher_source.read_bytes())
 proof=P/'control/INCORPORADOR_PI08_PREPARADO_R01.json'
 with proof.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI08.conditional_whole_successor.preparation.v1','source_base':{'path':str(source),'sha256':sha(source)},'new_installer':{'path':str(target),'sha256':sha(target)},'identity_adapter':{'path':str(adapter),'sha256':sha(adapter)},'existing_only_launcher':{'path':str(launcher),'sha256':sha(launcher)},'source_system':str(P/'estados/RP_A01/sistema'),'target_life_id':newlife,'moves':'Same life/world_id; all3complete directories, allsame-life checkpoint/history closure, no engine or main displacement until actualgates.','actual_adoption_executed':False,'Native_executed':False,'status':'CONDITIONAL_PREPARED_NOT_EXECUTED','required_real_tests':'A1PRE/POST; actual current SourceA2gates; freshprocess/noWAL; unselectedproduct0reopen; selectedproduct0reopen/publicuse. None predeclared positive.'},f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'installer':str(target),'sha256':sha(target),'identity_adapter_sha256':sha(adapter),'launcher_sha256':sha(launcher),'proof':str(proof),'proof_sha256':sha(proof)}))
if __name__=='__main__':main()
