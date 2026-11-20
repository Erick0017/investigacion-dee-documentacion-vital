"""Prueba real stdlib del bloque de publicación, aislada de Store y Native."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text('utf8'))
def write(p,v,replace=False):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
 if p.exists()and not replace:raise FileExistsError(str(p))
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
sp=importlib.util.spec_from_file_location('D_R03_commit_profile_test_only',H/'incorporar_D_PI09_misma_identidad_R03.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);b=m.base();old='DEE.PI09.exact_native_consultation_permission.v1';new='DEE.PI09.D.exact_operational_permission.v2';raw=b.D_original_adopt_with_D_schema_R03
assert old not in raw.__code__.co_consts and new in raw.__code__.co_consts;checks=['actual_private_adopt_constant_is_D_v2_not_C1']
# Extrae exclusivamente las cuatro instrucciones reales de publicar perfil.
# No se ejecuta Store.promote, movimiento, carga de mundo ni selección alguna.
tree=ast.parse((H/'incorporar_PI09_misma_identidad_R03.py').read_bytes());fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='adopt');index=next(i for i,n in enumerate(fn.body)if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='contract'for t in n.targets));nodes=fn.body[index:index+4];assert isinstance(nodes[-1],ast.If)
class Administrative(ast.NodeTransformer):
 def visit_Constant(self,node):
  if type(node.value)is str:
   replacements={old:new,'contratos/PI09_CONSULTA_OPERATIVA_R01.json':'contratos/PI09_D_USO_OPERATIVO_R02.json','PERFIL_PREPARADO_ANTES_COMMITTED_PI09.json':'PERFIL_D_PREPARADO_ANTES_COMMITTED_PI09.json'}
   if node.value in replacements:return ast.copy_location(ast.Constant(replacements[node.value]),node)
  return node
block=ast.fix_missing_locations(Administrative().visit(ast.Module(body=nodes,type_ignores=[])));code=compile(block,'actual_C1_publication_block:D_admin_strings_only','exec')
root=H/'PRUEBA_PUBLICACION_PERFIL_D_R03';root.mkdir(exist_ok=False);template=read(H/'DELTA_D_OPERATIVO_R01_PROPUESTO/codigo/contratos/PI09_D_USO_OPERATIVO_R02.json');template['all_adoption_gates_met']=True;life=template['life_id'];promotion=root/'promotion.json';write(promotion,{'decision':'TEST_ADMIN_ONLY_NO_NATIVE'})
for scenario in('absent','prepared','already_committed','wrong_schema'):
 folder=root/scenario;system=folder/'sistema';control=folder/'control';profile=system/'contratos/PI09_D_USO_OPERATIVO_R02.json';contract={**template,'status':'COMMITTED','life_id':life,'adoption_decision_sha256':sha(promotion),'actual_native_commit_witness':{'TEST':'NO_NATIVE'}}
 if scenario=='prepared':write(profile,template)
 if scenario=='already_committed':write(profile,contract)
 if scenario=='wrong_schema':write(profile,{**template,'schema':old})
 env={'d':{'new_contract':template},'LIFE':life,'sha':sha,'promotion':promotion,'witness':{'TEST':'NO_NATIVE'},'S':system,'CONTROL':control,'read':read,'write':write}
 try:exec(code,env)
 except FileExistsError:
  assert scenario=='wrong_schema'and read(profile)['schema']==old;checks.append('wrong_schema_rejected_and_original_bytes_preserved')
 else:
  assert scenario!='wrong_schema'and read(profile)==contract
  if scenario=='prepared':assert read(control/'PERFIL_D_PREPARADO_ANTES_COMMITTED_PI09.json')==template
  checks.append('actual_profile_block_'+scenario+'_PASS')
# El suplemento rechaza schema equivocado ANTES de entrar al método Store.
b.S=root/'wrong_schema/sistema'
try:b.adopt({'new_contract':template},None,None,None)
except ValueError:checks.append('wrong_prior_profile_stopped_before_Store_adopt')
else:raise AssertionError('Pre-Store gate absent')
assert 'app.lives'not in sys.modules;checks.append('no_Store_or_DEE_imports')
for name,needle in(('construir_decision_D_PI09_R02.py','incorporar_D_PI09_misma_identidad_R03.py'),('ejecutar_administracion_D_con_tope_PI09_R03.py','incorporar_D_PI09_misma_identidad_R03.py')):assert needle in(H/name).read_text('utf8');checks.append('real_callsite_'+name)
out=P/'control/PRUEBA_PERFIL_COMMITTED_D_PI09_R03.json';assert not out.exists();result={'schema':'DEE.PI09.D.separate_COMMITTED_profile.stdlib_actual_block_checks.R03','passed':True,'checks':checks,'Native_executed':False,'DEE_imports':False,'product_writes':False,'only_test_JSON_directory':str(root),'files_sha256':{n:sha(H/n)for n in('incorporar_D_PI09_misma_identidad_R03.py','construir_decision_D_PI09_R02.py','ejecutar_administracion_D_con_tope_PI09_R03.py')}};write(out,result);print(json.dumps({'proof':str(out),'sha256':sha(out),'passed':True,'checks':len(checks)}))
