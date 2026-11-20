"""Stdlib-only tests. No DEE, process Owner, state write or Native import."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,types
H=Path(__file__).resolve().parent;P=H.parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def run():
 driver=load('PI10_pure_driver_R03',H/'ejecutar_plan_PI10_R03.py');permission=load('PI10_pure_permission_R02',H/'pi10_permiso_operativo_R02.py');panel=json.loads((H/'PANEL_HEREDADO_12_PI10_R03_PASOS.json').read_text('utf8'));rows=[]
 def check(name,ok):
  assert ok,name;rows.append({'test':name,'pass':True})
 numeric=panel['steps'][10]
 for actual in(13,7,0,-1):
  literal,evidence=driver.bind_actual_integer(numeric,{'number13':{'id':'ACTUAL_PRIOR_RECEIPT','actual':actual,'expected':13}})
  check('Transport actual integer '+str(actual),literal['izquierda']==actual and literal['derecha']==5 and evidence['actual']==actual and evidence['expected_used']is False)
 for actual in(None,True,'13',13.0,{},[]):
  literal,evidence=driver.bind_actual_integer(numeric,{'number13':{'id':'ACTUAL_PRIOR_RECEIPT','actual':actual,'expected':13}})
  check('Abstain noninteger '+repr(actual),literal is None and evidence['no_Native_request']is True and evidence['expected_used']is False)
 check('No binding in Native literal','actual_integer_binding'not in numeric['literal']and numeric['literal']=={'modo':'eci01-aritmetica-directa','operacion':'diferencia','derecha':5})
 old={'life_id':permission.PARENT,'protocol_sha256':permission.C2C_PROTOCOL,'arm':'real','ready':True,'admitted':True,'ordinal':3,'rows':[{'case':i}for i in range(3)],'pending':None,'uncertain':False,'halted_reason':None,'custom_history':{'retain':['all',0,-1]}}
 new,leaf=permission.propose_C2C_identity(old);expected=copy.deepcopy(old);expected['life_id']=permission.LIFE
 check('C2C proposal exactly one administrative leaf',new==expected and old['life_id']==permission.PARENT and leaf['changed_paths']==['/life_id']and leaf['new_ticks']==0)
 saved={k:v for k,v in sys.modules.items()if k=='capacidades'or k.startswith('capacidades.')}
 try:
  for k in list(saved):sys.modules.pop(k,None)
  pkg=types.ModuleType('capacidades');pkg.__path__=[];generic=types.ModuleType('capacidades.pi09_permiso_operativo_D_R01');private=types.ModuleType('PI04_private_actual_permission');dispatcher=types.ModuleType('capacidades.pi04_dispatcher')
  generic.configure_C2C=lambda c,a:('old_generic',c);private.configure_C2C=lambda c,a:('old_private',c);dispatcher._load=lambda name:private if name=='pi09_permiso_operativo_D_R01'else None
  pkg.pi09_permiso_operativo_D_R01=generic;pkg.pi04_dispatcher=dispatcher;sys.modules['capacidades']=pkg;sys.modules['capacidades.pi09_permiso_operativo_D_R01']=generic;sys.modules['capacidades.pi04_dispatcher']=dispatcher
  permission.applies=lambda a:a=='exact';permission.configure_C2C=lambda c,a:('PI10_bound',c);permission.install('exact')
  check('Both actual consumer namespaces wrapped',generic.configure_C2C(1,'exact')==('PI10_bound',1)and private.configure_C2C(2,'exact')==('PI10_bound',2))
  check('Other-life generic fallback preserved',generic.configure_C2C(3,'other')==('old_generic',3)and private.configure_C2C(4,'other')==('old_private',4))
 finally:
  for k in list(sys.modules):
   if k=='capacidades'or k.startswith('capacidades.'):sys.modules.pop(k,None)
  sys.modules.update(saved)
 staged=H/'PERMISO_PI10_R02_PREPARADO/app/mundo_genesis_apd05.py';tree=ast.parse(staged.read_text('utf8'));methods={n.name:n for n in ast.walk(tree)if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))};text=staged.read_text('utf8')
 check('Staged owner installs permission and public routing exactly',text.count('pi10_permission.install(self.a)')==1 and text.count('pi10_permission.routes_public(self.a,row)')==2 and text.count('pi10_permission.validate_external(self.a,row,payload=payload)')==2)
 check('No target supplied to operation literals',all(not({'expected','correct','target','respuesta'}&set(s['literal']))for s in panel['steps']))
 return {'schema':'DEE.PI10.pure_panel_and_permission_tests.R03','Native_imports':0,'Native_ticks':0,'product_modified':False,'tests':rows,'passed':len(rows),'files':{str(p):sha(p)for p in(H/'ejecutar_plan_PI10_R03.py',H/'pi10_permiso_operativo_R02.py',H/'PANEL_HEREDADO_12_PI10_R03_PASOS.json',staged)}}
if __name__=='__main__':
 result=run();out=P/'control/PRUEBAS_PURAS_PANEL_PERMISO_PI10_R03.json';data=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
 if out.exists():assert out.read_text('utf8')==data
 else:
  with out.open('x',encoding='utf8')as f:f.write(data)
 print(json.dumps({'proof':str(out),'sha256':sha(out),'tests':result['passed'],'Native':0}))
