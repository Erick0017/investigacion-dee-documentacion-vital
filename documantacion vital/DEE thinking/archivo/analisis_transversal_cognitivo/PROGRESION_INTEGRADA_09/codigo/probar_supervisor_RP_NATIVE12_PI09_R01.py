"""Pure actual CLI/recipe/bound contracts, no invocation of material stages."""
from pathlib import Path
import ast,hashlib,importlib.util,json,subprocess,sys
P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0';OUT=H/'PRUEBA_SUPERVISOR_RP_NATIVE12_PI09_R01'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n,p):
 sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def main():
 if OUT.exists():raise FileExistsError('Prueba anterior preservada')
 OUT.mkdir();s=load('RP_cold12_supervisor_contract',H/'supervisar_RP_NATIVE12_PI09_R01.py');g=load('RP_cold12_guard_contract',H/'guardia_frontdoor_RP_NATIVE12_PI09_R01.py');tests=[]
 def check(n,v):
  if v is not True:raise AssertionError(n)
  tests.append({'name':n,'pass':True})
 recipe=json.loads((C/'reproducibilidad/recetas'/(s.RID+'.json')).read_text('utf-8-sig'));steps=recipe['variants'][s.VARIANT]['batches'][0]
 check('actual_registered_recipe_pin',sha(C/'reproducibilidad/recetas'/(s.RID+'.json'))==g.RECIPE_SHA==s.RECIPE_SHA)
 check('actual_14fixed_calls_bound27360',len(steps)==14 and sum(g.allowance(x)for x in steps)==s.BOUND==27360)
 check('all_EP_literals_frozen_no_expected_input',[x['literal']for x in steps if x['label'].startswith('EP_')]==[{'modo':'eci01-pi09-episodio'}]*12)
 check('fixed_public_frontdoor_arguments',g.command_arguments()==['reproducir',s.RID,'--variante','native12','--vida',s.LIFE,'--destino',str(s.DEST),'--material'])
 check('registered_fixed_limits',s.LIMIT==536870912 and sha(s.LEDGER)==g.LEDGER_SHA==s.LEDGER_SHA)
 for file in(H/'supervisar_RP_NATIVE12_PI09_R01.py',H/'guardia_frontdoor_RP_NATIVE12_PI09_R01.py',H/'registrar_RP_NATIVE12_PI09_R01.py'):ast.parse(file.read_bytes())
 check('three_actual_prepared_sources_AST',True)
 completed=subprocess.run([sys.executable,'-I','-B','-X','utf8',str(H/'supervisar_RP_NATIVE12_PI09_R01.py')],capture_output=True,text=True,encoding='utf8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 check('default_plan_no_material_stage',completed.returncode==0 and json.loads(completed.stdout)['mode']=='PLAN_ONLY_NO_STATE_READ');(OUT/'PLAN_STDOUT.json').write_text(completed.stdout,'utf8')
 check('no_DEE_app_import',not any(n=='app'or n.startswith(('app.','dee_thinking'))for n in sys.modules))
 result={'schema':'DEE.PI09.RP.cold12.actual_contract_pure_tests.R01','passed':len(tests),'tests':tests,'Native_executed':False,'DEE_imports':0,'source_state_read':False,'actual_material_supervision_still_Root_only':True,'supervisor_sha256':sha(H/'supervisar_RP_NATIVE12_PI09_R01.py'),'guard_sha256':sha(H/'guardia_frontdoor_RP_NATIVE12_PI09_R01.py')}
 file=OUT/'RESULTADO.json';file.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'passed':len(tests),'proof':str(file),'sha256':sha(file),'Native_executed':False}))
if __name__=='__main__':main()
