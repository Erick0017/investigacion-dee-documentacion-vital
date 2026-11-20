"""Pure tests against real inherited files/metadata; no DEE import or owner."""
from pathlib import Path
import ast,hashlib,importlib.util,json,sys,types
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/AR0/sistema'
def load(name,path):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=P/'codigo/PRUEBAS_TRANSPORTE_PI09_R01'
 if out.exists():raise FileExistsError(out)
 out.mkdir();checks=[]
 def check(label,ok):
  checks.append({'check':label,'passed':bool(ok)})
  if not ok:raise ValueError(label)
 parser=load('PI09_TEST_PASSIVE_REAL',C/'reproducibilidad/observador_pasivo.py')
 view=parser.snapshot_view(P/'pares/C_HEREDADA_T884835/VIDA.deetsnap.gz');actual_A=read(C/'sistema/estado/ACTIVO.json');acard=read(C/'sistema/estado/vidas'/actual_A['life_id']/'VIDA.json');av=parser.snapshot_view(C/'sistema'/acard['snapshot'])
 sys.path.insert(0,str(S));from capacidades import pi09_transporte_heredado_R01 as t
 from capacidades import pi09_dispatcher_R01 as dispatcher
 original_C=load('PI09_TEST_ORIGINAL_C',S/'capacidades/pi08_consulta_condicional_C_R03.py')
 original_B=load('PI09_TEST_ORIGINAL_B',S/'capacidades/pi08_revision_flexible_B_R01.py')
 class Runtime:
  dimension=67
  def __init__(self,entries):self.snapshot_metadata_entries=tuple(entries.items())
 def fake(entries,life):
  entries=dict(entries);identity=json.loads(entries[t.SYSTEM_KEY]);identity['life_id']=life
  entries[t.SYSTEM_KEY]=json.dumps(identity,ensure_ascii=False,sort_keys=True,separators=(',',':'))
  return types.SimpleNamespace(world=types.SimpleNamespace(runtime=Runtime(entries)))
 new_life=read(S/'capacidades/PI09_TRANSPORTE_HEREDADO_R01.json')['life_id'];a=fake(view['metadata'],new_life)
 check('real_source_pair_and_metadata_used',view['physical']['tick']==884835 and view['encoded_sha256']==t.SOURCE_SNAPSHOT)
 check('exact_clone_identity_applies',t.applies(a)and t.current(a)['life_id']==new_life)
 private=t.component_C(a,original_C)
 check('C_private_home_uses_new_transport_ID',private.LIFE==new_life and original_C.LIFE=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01')
 _,protocol_hash=private.protocol(True)
 check('actual_frozen_C_protocol_and_seal_still_validate',protocol_hash=='06a7c5f3384ab16ba12ccf9750df8d2282ce899d3c9f95bae05e74c9c335bbcd')
 for component in(private,t.component_B(a,original_B)):
  try:component.validate(a,{'modo':component.EPISODE});denied=False
  except ValueError:denied=True
  check('old_material_denied_'+component.VERSION,denied)
 # Use the exact original _home function without importing its Native module.
 root_source=S/'capacidades/pi07_regulacion_R01.py';node=next(n for n in ast.parse(root_source.read_text('utf8')).body if isinstance(n,ast.FunctionDef)and n.name=='_home')
 ns={'Path':Path,'FOLDER':'PURE_NOT_NATIVE'};exec(compile(ast.Module(body=[node],type_ignores=[]),str(root_source),'exec'),ns)
 home=out/'homes'/new_life;home.mkdir(parents=True)
 check('actual_home_validator_accepts_private_C_ID',ns['_home'](home,private.LIFE)==home/'PURE_NOT_NATIVE')
 try:ns['_home'](home,original_C.LIFE);denied=False
 except ValueError:denied=True
 check('actual_home_validator_rejects_stale_C_ID',denied)
 original_a=fake(av['metadata'],actual_A['life_id'])
 check('actual_protected_A_not_in_PI09_scope',not t.applies(original_a))
 check('A_old_components_remain_original',t.component_B(original_a,original_B)is original_B and t.component_C(original_a,original_C)is original_C)
 check('actual_A_metadata_PI09_dependencies_absent',dispatcher.operational_dependencies(original_a,Path('.'))['present']is False)
 check('actual_A_metadata_PI09_uncertainty_false',dispatcher.uncertain(original_a)is False)
 outsider=fake(view['metadata'],'ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_OTHER_01')
 try:t.current(outsider);denied=False
 except ValueError:denied=True
 check('unsealed_other_ID_rejected',denied)
 hooks=P/'codigo/HOOKS_PI09_R03_PREPARADOS/app/mundo_genesis_apd05.py';text=hooks.read_text('utf8');ast.parse(text)
 check('all_five_C_and_B_call_sites_private',text.count('component_C(self.a,pi08c)')==5 and text.count('component_B(self.a,pi08b)')==5)
 check('source_mente_unificada_not_modified',sha(S/'capacidades/mente_unificada_01.py')=='184c418b02c80a5d804fcfe9477d51787282d215aa9e0b482fc25d00022878e6')
 check('no_DEE_imported',not any(k=='dee_thinking'or k.startswith('dee_thinking.')for k in sys.modules))
 proof={'schema':'DEE.PI09.inherited_transport.pure_checks.R01','all_passed':True,'Native_executed':False,'DEE_imports':0,'checks':checks,
        'scope':'Real prepared AR0 sources, real passive C/A metadata and actual frozen protocol/home functions; identity holder is a pure fixture. Actual import/reopen remains Root evidence.'}
 (out/'RESULTADO.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf8')
 print(json.dumps({'passed':len(checks),'result':str(out/'RESULTADO.json'),'Native_executed':False}))
if __name__=='__main__':main()
