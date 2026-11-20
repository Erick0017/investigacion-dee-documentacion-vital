"""Pure permission/transport contract tests; no DEE import or Native state."""
from pathlib import Path
from types import SimpleNamespace
import ast,copy,hashlib,importlib.util,json,shutil
H=Path(__file__).resolve().parent;OUT=H/'PRUEBA_PERMISO_OPERATIVO_PI09_R01'

def load(name,p):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def main():
 if OUT.exists():raise FileExistsError('Prueba anterior preservada')
 OUT.mkdir();m=load('permission_pure',H/'pi09_permiso_operativo_R01.py');root=OUT/'sistema';cap=root/'capacidades';cap.mkdir(parents=True)
 source=H/'PERMISO_OPERATIVO_PI09_R01_PROPUESTO';plan=json.loads((source/'PLAN.json').read_text('utf8'));tests=[]
 def check(name,value):
  if value is not True:raise AssertionError(name)
  tests.append({'name':name,'pass':True})
 def rejects(name,fn):
  try:fn()
  except ValueError:check(name,True);return
  raise AssertionError(name)
 for name,digest in m.PINS.items():
  src=Path(plan['unchanged_scientific_sources'][name]['source']);check('actual_frozen_'+name,sha(src)==digest);shutil.copyfile(src,cap/name)
 shutil.copyfile(H/'pi09_aritmetica_temporal_P0_R01.py',cap/'pi09_aritmetica_temporal_P0_R01.py')
 m.__file__=str(cap/'pi09_permiso_operativo_R01.py');m._root=lambda:root
 identity={'life_id':m.LIFE,'profile':'fisica_directa'};control={'control':{'arm':'native_real','query_policy':'native','information_policy':'real'}}
 entries={m.SYSTEM_KEY:json.dumps(identity),m.QUERY_KEY:json.dumps(control)}
 a=SimpleNamespace(world=SimpleNamespace(runtime=SimpleNamespace(dimension=67,snapshot_metadata_entries=entries.items())))
 profile=json.loads((source/'contratos'/m.CONTRACT).read_text('utf8'));contract=root/'contratos'/m.CONTRACT;write(contract,profile)
 check('prepared_profile_no_selected_permission',m.profile(a)['status']=='PREPARED_DIAGNOSTIC'and not m.routes_public(a,{'modo':'eci01-balance'}))
 write(root/'estado/ACTIVO.json',{'life_id':m.LIFE})
 rejects('selected_prepared_profile_denied',lambda:m.profile(a))
 profile.update(status='COMMITTED',all_adoption_gates_met=True,adoption_decision_sha256='ab'*32);write(contract,profile)
 check('selected_committed_all_outer_FI',all(m.routes_public(a,{'modo':'eci01-balance','izquierda':l,'derecha':r})for l,r in((14,3),(2,11),(6,6))))
 check('arithmetic_legacy_not_silently_changed',not m.routes_public(a,{'modo':'eci01-aritmetica-directa'}))
 rejects('old_material_calendar_denied',lambda:m.validate_selected_external(a,{'modo':'eci01-pi07-r03-episodio'}))
 m.validate_selected_external(a,{'modo':'eci01-pi07-r03-estado'});check('historical_state_retained',True)
 profile['public_arithmetic_policy']='P0_phase19_fixed';write(contract,profile)
 rejects('P0_without_actual_pair_and_reserve_denied',lambda:m.profile(a))
 profile.update(arithmetic_guard_actual_gate_met=True,arithmetic_guard_actual_evidence=[{'path':'PAIR_ACTUAL.json','sha256':'cd'*32},{'path':'RESERVE_ACTUAL.json','sha256':'ef'*32}]);write(contract,profile)
 check('P0_only_after_explicit_gate',m.routes_public(a,{'modo':'eci01-aritmetica-directa'}))
 control['control']['arm']='always_real';entries[m.QUERY_KEY]=json.dumps(control)
 rejects('reference_policy_selected_denied',lambda:m.profile(a));control['control']['arm']='native_real';entries[m.QUERY_KEY]=json.dumps(control)
 old={'life_id':m.PREDECESSOR,'ordinal':31,'rows':[{'literal':'unchanged'}],'pending':None,'uncertain':False,'resources':32}
 new,proof=m.administrative_C2C_identity_proposal(old)
 check('one_C2C_administrative_leaf_only',new['life_id']==m.LIFE and{key:value for key,value in old.items()if key!='life_id'}=={key:value for key,value in new.items()if key!='life_id'}and proof['new_native_ticks']==0)
 entries[m.SYSTEM_KEY]=json.dumps({'life_id':m.PREDECESSOR,'profile':'fisica_directa'})
 check('protected_A_bypass_even_with_native_ACTIVO',m.profile(a)is None and not m.routes_public(a,{'modo':'eci01-balance'}))
 for row in plan['code_files']:
  path=Path(row['source']);check('CAS_source_'+row['file'],sha(path)==row['sha256'])
  if path.suffix=='.py':ast.parse(path.read_bytes())
 world=(source/'app/mundo_genesis_apd05.py').read_text('utf8')
 check('public_boundary_before_legacy_dispatch',world.index('pi09_permission.routes_public(self.a,row)')<world.index("str(row.get('modo','')).startswith('eci01-pi09-')"))
 check('frozen_FI_and_R03_body_not_rewritten',all((Path(plan['unchanged_scientific_sources'][n]['source']).read_bytes()==(cap/n).read_bytes())for n in m.PINS))
 result={'schema':'DEE.PI09.exact_public_permission.pure_tests.R01','passed':len(tests),'tests':tests,'Native_executed':False,'DEE_imports':0,'source_state_read':False,'actual_source_hashes_checked':True,'not_a_material_or_selected_operation_test':True}
 write(OUT/'RESULTADO.json',result);print(json.dumps({'passed':len(tests),'proof':str(OUT/'RESULTADO.json'),'sha256':sha(OUT/'RESULTADO.json'),'Native_executed':False}))
if __name__=='__main__':main()
