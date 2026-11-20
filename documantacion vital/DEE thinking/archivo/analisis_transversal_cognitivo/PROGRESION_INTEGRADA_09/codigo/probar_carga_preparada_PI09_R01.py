"""Pure administrative permissions; no DEE import, state or Native execution."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,tempfile,types
H=Path(__file__).resolve().parent;OUT=H/'PRUEBA_CARGA_PREPARADA_PI09_R01';P=H.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists():raise FileExistsError('Preserve previous proof')
 OUT.mkdir();sp=importlib.util.spec_from_file_location('prepared_load_pure',H/'pi09_carga_preparada_R01.py');m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 parent=types.ModuleType('capacidades');permission=types.ModuleType('capacidades.pi09_permiso_operativo_R01');parent.pi09_permiso_operativo_R01=permission;sys.modules['capacidades']=parent;sys.modules[permission.__name__]=permission
 identity={'life_id':m.LIFE,'profile':'fisica_directa'};profile={'status':'PREPARED_DIAGNOSTIC','all_adoption_gates_met':True,'adoption_decision_sha256':None};selection=m.PREDECESSOR
 permission.profile=lambda a:profile;permission._selected=lambda:selection;permission._identity=lambda a:identity
 metadata={'ordinal':12,'rows':[{}]*12,'sample_register':None,'ready':True,'pending':None,'uncertain':None,'control':{'arm':'native_real','query_policy':'native','information_policy':'real'}}
 def adapter():return types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=((m.SYSTEM,json.dumps(identity)),(m.KEY,json.dumps(metadata))))))
 rows=[]
 def check(name,call,accept):
  try:call();actual=True
  except(ValueError,KeyError):actual=False
  if actual!=accept:raise AssertionError(name)
  rows.append({'name':name,'passed':True,'accepted':actual})
 check('exact_prepared_load',lambda:m.prepared(adapter(),identity),True)
 for mode in sorted(m.STATES):check('state_'+mode,lambda mode=mode:m.guard_external(adapter(),{'modo':mode}),True)
 for literal in({'modo':'eci01-pi09-episodio'},{'modo':'eci01-pi09-preparar','brazo':'native_real'},{'modo':'eci01-balance','izquierda':17,'derecha':6},{'modo':'eci01-pi09-estado','extra':0}):check('reject_'+str(literal),lambda literal=literal:m.guard_external(adapter(),literal),False)
 for key,value in(('ordinal',11),('sample_register',{'not':'empty'}),('pending',{'phase':'pending'}),('uncertain',True),('ready',False)):
  previous=metadata[key];metadata[key]=value;check('reject_meta_'+key,lambda:m.prepared(adapter(),identity),False);metadata[key]=previous
 previous=selection;selection='OTHER';check('other_selected_life_rejected',lambda:m.prepared(adapter(),identity),False);selection=previous
 profile['status']='COMMITTED';check('unselected_committed_not_prepared',lambda:m.prepared(adapter(),identity),False);profile['status']='PREPARED_DIAGNOSTIC'
 source=H/'CARGA_PREPARADA_PI09_R01_PROPUESTA/pi09_permiso_operativo_R01.py';ast.parse(source.read_bytes())
 transport=H/'RP_FAMILIA_R04_PREPARADA_R02/capsule/capacidades/pi09_transporte_heredado_R02.py';text=transport.read_text('utf-8-sig');node=next(n for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)and n.name=='current');body=ast.get_source_segment(text,node);assert body.count('if active.exists():')==1
 code=body.replace('if active.exists():','if active.exists() and _prepared_load_gate(a,identity,active):');ast.parse(code);rows.append({'name':'only_current_active_branch_administrative_source_local_change','passed':True})
 result={'schema':'DEE.PI09.prepared_load.pure_tests.R01','passed':len(rows),'checks':rows,'Native_executed':False,'DEE_imports':0,'source_bodies_modified':False,'sources':{p.name:sha(p)for p in(H/'pi09_carga_preparada_R01.py',source)}}
 (OUT/'RESULTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':len(rows),'proof':str(OUT/'RESULTADO.json'),'sha256':sha(OUT/'RESULTADO.json'),'Native_executed':False}))
if __name__=='__main__':main()
