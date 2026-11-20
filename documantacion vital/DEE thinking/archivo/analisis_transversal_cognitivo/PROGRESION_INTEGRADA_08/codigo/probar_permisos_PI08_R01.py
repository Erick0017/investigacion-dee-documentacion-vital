"""Pure exact-life/contract/routing tests. No Native import or execution."""
from pathlib import Path
import copy,hashlib,importlib.util,json,types,sys
P=Path(__file__).resolve().parents[1];STAGE=P/'codigo/PI08_A1_INSTALACION_R02';OUT=P/'control/PRUEBAS_PERMISOS_PI08_R01'
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def put(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v),encoding='utf8')
def main():
 if OUT.exists():raise FileExistsError('Pure evidence preserved')
 OUT.mkdir();m=load('PI08_PERMISSION_PURE',STAGE/'capacidades/pi08_permisos_operativos_R01.py');fake=OUT/'FAKE_SYSTEM';fake.mkdir();m._root=lambda:fake
 contract=json.loads((STAGE/'contratos/PI08_USO_OPERATIVO_R01.json').read_text('utf8'));contractpath=fake/'contratos'/m.CONTRACT
 def adapter(life):return types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=((m.SYSTEM_KEY,json.dumps({'life_id':life,'profile':'fisica_directa'})),))))
 a=adapter(m.LIFE);original=adapter('ECI02_PI03_REPRO_PI04_PI05_MAIN_01');active=fake/'estado/ACTIVO.json';checks={}
 put(contractpath,contract);checks['prepared_unselected_exact_profile_accepted']=m.profile(a)['status']=='PREPARED_DIAGNOSTIC'
 checks['original_main_does_not_receive_PI08_permission']=m.profile(original)is None
 put(active,{'life_id':m.LIFE})
 try:m.profile(a);checks['selected_prepared_is_rejected']=False
 except ValueError:checks['selected_prepared_is_rejected']=True
 committed={**contract,'status':'COMMITTED','adoption_decision_sha256':'c'*64};put(contractpath,committed);checks['selected_committed_exact_hash_accepted']=m.profile(a)['status']=='COMMITTED'
 broken={**committed,'adoption_decision_sha256':'not_a_hash'};put(contractpath,broken)
 try:m.profile(a);checks['selected_bad_adoption_hash_rejected']=False
 except ValueError:checks['selected_bad_adoption_hash_rejected']=True
 put(contractpath,committed);m._ORIGINAL_FI_ROUTE=lambda aa,row:False
 checks['all_outer_FI_signs_use_same_route']=all(m._outer_FI_route(a,{'modo':'eci01-balance','izquierda':left,'derecha':right})for left,right in((14,3),(2,11),(6,6),(0,20)))
 checks['non_FI_never_redirected']=not m._outer_FI_route(a,{'modo':'otra-consulta','izquierda':14,'derecha':3})
 checks['other_life_legacy_route_unchanged']=not m._outer_FI_route(original,{'modo':'eci01-balance','izquierda':14,'derecha':3})
 source={'life_id':m.SOURCE_C2C_LIFE,'pending':None,'uncertain':False,'rows':[{'actual':23}],'ordinal':30,'products':['original'],'protocol_sha256':'d'*64};updated,proof=m.administrative_C2C_identity_proposal(source)
 checks['identity_changes_exactly_one_leaf']=updated['life_id']==m.LIFE and {k:v for k,v in source.items()if k!='life_id'}=={k:v for k,v in updated.items()if k!='life_id'}and proof['changed_paths']==['/life_id']
 body=load('PI08_PERMISSION_REAL_C2C',STAGE/'capacidades/pi04_coordinacion_central_C2C.py');body.PROTOCOL=STAGE/'capacidades/PROTOCOLO_PI08_C2C_32_R01.json';configured=m.configure_C2C(body,a);checks['C2C_only_exact_selected_constant_adapted']=configured.OPERATIONAL_LIFE_ID==m.LIFE
 try:configured._require_adopted_C2C_use(a,{'life_id':m.LIFE},configured.protocol()[0],configured.protocol()[1],configured.PREPARE,None);checks['selected_C2C_preparation_still_forbidden']=False
 except ValueError:checks['selected_C2C_preparation_still_forbidden']=True
 checks['no_DEE_or_app_import']=not any(name=='dee_thinking'or name.startswith(('dee_thinking.','app.'))for name in sys.modules)
 if not all(checks.values()):raise AssertionError(checks)
 proof={'schema':'DEE.PI08.operational_permission.pure.v1','checks':checks,'FAKE_runtime_and_contract_root':True,'Native_executed':False,'scope':'Guard/routing contract tests only. Actual public FI through Cognitive and selected close/reopen remain Root gates.'};target=OUT/'RESULTADO_PURO.json';put(target,proof);print(json.dumps({'proof':str(target),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'checks':checks}))
if __name__=='__main__':main()
