"""Pure exact-life permission/one-leaf proposal tests, no Native or product."""
from pathlib import Path
from types import SimpleNamespace
import copy,hashlib,importlib.util,json,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';OUT=P/'control/PERMISOS_CONDICIONALES_FAKE';OUT.mkdir(exist_ok=False)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
perm=load('PI07_permission_FAKE',H/'pi07_permiso_principal_R01.py');ident=load('PI07_identity_FAKE',H/'pi07_identidad_c2c.py');tests=[]
def check(n,v):
 if not v:raise AssertionError(n)
 tests.append({'name':n,'passed':True})
base={'life_id':perm.OLD_PI05,'pending':None,'uncertain':False,'halted_reason':None,'ordinal':28,'rows':[{'life_id':perm.OLD_PI05,'actual':13}],'protocol_sha256':perm.C2C_PROTOCOL_SHA,'protocol_history':[{'unchanged':'historical'}],'plan':[False,True]};literal=copy.deepcopy(base)
mapped,leaf=ident.propose_identity(base,perm.LIFE,perm.LIFE)
check('only_current_leaf_changes',base==literal and mapped['life_id']==perm.LIFE and {k:v for k,v in mapped.items()if k!='life_id'}=={k:v for k,v in base.items()if k!='life_id'})
check('historical_life_id_literal_retained',mapped['rows'][0]['life_id']==perm.OLD_PI05)
for i,(data,source,target)in enumerate(((base,'WRONG',perm.LIFE),(base,perm.LIFE,perm.OLD_PI05),({**base,'uncertain':True},perm.LIFE,perm.LIFE),({**base,'life_id':'ANOTHER_WORLD'},perm.LIFE,perm.LIFE))):
 try:ident.propose_identity(data,source,target)
 except ValueError:check('reject_unsafe_identity_'+str(i),True)
 else:raise AssertionError('Unsafe identity proposal accepted')
root=OUT/'sistema';(root/'capacidades').mkdir(parents=True);(root/'contratos').mkdir();(root/'estado').mkdir()
component=SimpleNamespace(__file__=str(root/'capacidades/FAKE_C2C.py'),OPPORTUNITY='eci01-pi04-c2c-oportunidad',STATE='eci01-pi04-c2c-estado',OPERATIONAL_LIFE_ID=perm.OLD_PI04,_get=lambda a:mapped)
entries={perm.SYSTEM:json.dumps({'life_id':perm.LIFE}),perm.EXTENSION:json.dumps({'ready':True,'pending':None,'uncertain':False})}
a=SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(snapshot_metadata_entries=list(entries.items()))))
check('no_contract_is_dormant',perm.configure(component,a)is component and component.OPERATIONAL_LIFE_ID==perm.OLD_PI04)
template=json.loads((H/'PI07_ADOPCION_PERMISOS_PREPARADA/PI07_REGULACION_USO_PRINCIPAL_01.PLANTILLA_NO_ACTIVA.json').read_text('utf8'));contract=root/'contratos'/perm.CONTRACT;contract.write_text(json.dumps(template),encoding='utf8')
try:perm.configure(component,a)
except ValueError:check('draft_contract_cannot_activate',True)
else:raise AssertionError('Draft permission activated')
template.update(status='COMMITTED',adoption_decision_sha256='f'*64);contract.write_text(json.dumps(template),encoding='utf8');active=root/'estado/ACTIVO.json';active.write_text(json.dumps({'life_id':perm.OLD_PI05}),encoding='utf8')
try:perm.configure(component,a)
except ValueError:check('wrong_selected_life_blocks_permission',True)
else:raise AssertionError('Other selected principal changed')
active.write_text(json.dumps({'life_id':perm.LIFE}),encoding='utf8');before=copy.deepcopy(entries)
check('only_exact_fake_committed_life_configures_constant',perm.configure(component,a)is component and component.OPERATIONAL_LIFE_ID==perm.LIFE)
check('no_metadata_or_acquired_data_written',entries==before and mapped['rows']==base['rows'])
component.OPERATIONAL_LIFE_ID='ANOTHER_PERMISSION'
try:perm.configure(component,a)
except ValueError:check('other_permission_revision_protected',True)
else:raise AssertionError('Unrelated permission overwritten')
check('no_DEE_or_app_import',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
out=P/'control/PI07_PERMISOS_CONDICIONALES_PRUEBAS_PURAS_R01.json'
with out.open('x',encoding='utf8')as f:json.dump({'schema':'DEE.PI07.conditional_permission.pure_tests.v1','tests':tests,'passed':len(tests),'permission_module_sha256':hashlib.sha256((H/'pi07_permiso_principal_R01.py').read_bytes()).hexdigest(),'identity_adapter_sha256':hashlib.sha256((H/'pi07_identidad_c2c.py').read_bytes()).hexdigest(),'Native_executed':False,'product_or_S7_modified':False,'actual_permission_activated':False,'scope':'Fake files only, one-leaf pure proposal and strict permission constants. No real import, identity mutation, promotion or selected Owner proof.'},f,ensure_ascii=False,indent=2);f.write('\n')
print(json.dumps({'proof':str(out),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'passed':len(tests),'Native_executed':False}))
