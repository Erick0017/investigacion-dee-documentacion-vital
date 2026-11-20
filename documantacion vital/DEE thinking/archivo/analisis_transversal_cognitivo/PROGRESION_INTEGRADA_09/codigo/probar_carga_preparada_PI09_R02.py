"""Full real transport-payload matrix, pure stdlib, no Native/DEE."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,types
H=Path(__file__).resolve().parent;OUT=H/'PRUEBA_CARGA_PREPARADA_PI09_R02';STAGE=H/'CARGA_PREPARADA_PI09_R02_PROPUESTA'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 if OUT.exists():raise FileExistsError('Prior proof preserved')
 OUT.mkdir();file=STAGE/'pi09_carga_preparada_R02.py';sp=importlib.util.spec_from_file_location('full_payload_gate',file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 parent=types.ModuleType('capacidades');permission=types.ModuleType('capacidades.pi09_permiso_operativo_R01');parent.pi09_permiso_operativo_R01=permission;sys.modules['capacidades']=parent;sys.modules[permission.__name__]=permission
 identity={'life_id':m.LIFE,'profile':'fisica_directa'};permission.profile=lambda a:{'status':'PREPARED_DIAGNOSTIC','all_adoption_gates_met':True,'adoption_decision_sha256':None};permission._selected=lambda:m.PREDECESSOR;permission._identity=lambda a:identity
 metadata={'ordinal':12,'rows':[{}]*12,'sample_register':None,'ready':True,'pending':None,'uncertain':None,'control':{'arm':'native_real','query_policy':'native','information_policy':'real'}};a=types.SimpleNamespace(world=types.SimpleNamespace(runtime=types.SimpleNamespace(dimension=67,snapshot_metadata_entries=((m.KEY,json.dumps(metadata)),))))
 rows=[]
 def check(name,payload,row,expected):
  try:m.guard_external(a,row,payload=payload);actual=True
  except(ValueError,KeyError):actual=False
  if actual!=expected:raise AssertionError(name)
  rows.append({'name':name,'accepted':actual,'passed':True})
 for mode in('reanudar','pausar','guardar','detener'):check('control_'+mode,{'operacion':mode},None,True)
 for mode in sorted(m.STATES):
  row={'modo':mode};check('state_'+mode,{'operacion':'sesion','situaciones':[row],'retorno':'omit','actuador':'closed'},row,True)
  check('state_no_default_real_feedback_'+mode,{'operacion':'sesion','situaciones':[row]},row,False)
 for payload,row in(({'operacion':'avanzar','ticks':1},None),({'operacion':'exportar'},None),({'operacion':'detener','ticks':0},None),({'operacion':'guardar','situaciones':[]},None),({'operacion':'sesion','situaciones':[{'modo':'eci01-pi09-episodio'}],'retorno':'omit','actuador':'closed'},{'modo':'eci01-pi09-episodio'}),({'operacion':'sesion','situaciones':[{'modo':'eci01-balance','izquierda':17,'derecha':6}],'retorno':'omit','actuador':'closed'},{'modo':'eci01-balance','izquierda':17,'derecha':6}),({'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'alfa'}],'retorno':'omit','actuador':'closed'},None),({'operacion':'sesion','situaciones':[{'modo':'eci01-pi09-estado'},{'modo':'eci01-pi09-estado'}],'retorno':'omit','actuador':'closed'},{'modo':'eci01-pi09-estado'}),(None,None)):
  check('reject_'+str(payload),payload,row,False)
 # Extract the real public _eci01_row method; exercise actual control None
 # and session row translation, rather than a fake situation-only caller.
 world=(STAGE/'mundo_genesis_apd05.py').read_text('utf-8-sig');tree=ast.parse(world);cls=next(n for n in tree.body if isinstance(n,ast.ClassDef));node=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='_eci01_row');code=ast.get_source_segment(world,node);namespace={};exec(compile('class ActualParser:\n'+''.join(' '+line+'\n'for line in code.splitlines()),'<actual _eci01_row>','exec'),namespace);parser=namespace['ActualParser']()
 for mode in('reanudar','pausar','guardar','detener'):
  payload={'operacion':mode};assert parser._eci01_row(payload)is None;check('actual_parser_control_'+mode,payload,parser._eci01_row(payload),True)
 assert world.count('pi09_permission.validate_selected_external(self.a,row,payload=payload)')==2;rows.append({'name':'both_actual_validate_and_execute_forward_complete_payload','passed':True})
 result={'schema':'DEE.PI09.prepared_load.full_payload_pure_tests.R02','passed':len(rows),'checks':rows,'Native_executed':False,'DEE_imports':0,'actual_public_payload_parser_AST_used':True,'sources':{p.name:sha(p)for p in STAGE.glob('*.py')}}
 (OUT/'RESULTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':len(rows),'proof':str(OUT/'RESULTADO.json'),'sha256':sha(OUT/'RESULTADO.json'),'Native_executed':False}))
if __name__=='__main__':main()
