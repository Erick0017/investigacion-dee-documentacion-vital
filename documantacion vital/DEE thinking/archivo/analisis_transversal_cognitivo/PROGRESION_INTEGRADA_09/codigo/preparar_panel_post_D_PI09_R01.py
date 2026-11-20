"""Prepare fixed old12 panel in the same D descendant, no Native execution."""
from pathlib import Path
import argparse,ast,copy,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(a):
 driver=H/'ejecutar_plan_PI09_R03.py';base=H/'ejecutar_plan_PI09_R02.py';source=base.read_text('utf8');old=source[source.index('def ledger():'):source.index('def main(args):')]
 new="def ledger():\n file=P/'codigo/ledger_PI09_misma_identidad_R01.py'\n require(sha(file)=='bb1f326aa981ba00b9a6e3417700cca31d92a0d28a6e8a5ad601042bf2a26260','Exact same-ID ledger')\n sp=importlib.util.spec_from_file_location('PI09_panel_final_ledger',file);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);v=m.ledger()\n return v['ticks'],v['worlds']\n\n"
 text=source.replace(old,new).replace('DEE.PI09.actual.finite_owner_plan.R02','DEE.PI09.actual.finite_owner_plan.R03');ast.parse(text)
 if driver.exists():assert driver.read_text('utf8')==text
 else:driver.write_text(text,'utf8')
 out=H/'PLAN_PI09_PANEL_POST_D12_R03.json';assert not out.exists();p=read(H/'PLAN_DISCOVERY_P0_R01.json');steps=copy.deepcopy(p['steps'][:13]);assert len(steps)==13 and sum(s['label'].startswith('FI')for s in steps)==3
 for s in steps:
  if s['label'].startswith('FI'):s['literal']['modo']='eci01-pi09-fi-lote-consultar';s['stage']='retention_previous_relation_new_explicit_environmental_FI_lot8'
 assert [s['label']for s in steps][1:]==['luma','nara','clasifica','suma','alfa','FIplus','FIminus','FIzero','number13','number8','alfa_after','luma_after']
 p.update(tag='PI09_PANEL_POST_D12_R03',initial_tick=a.tick,steps=steps,protocol='Previous twelve witnesses, same retained-domain old numeric reader; FI only uses explicitly admitted new lot8. No reteaching or P0 timing guard.')
 p['pins']={str(driver):sha(driver),str(H/'ledger_PI09_misma_identidad_R01.py'):sha(H/'ledger_PI09_misma_identidad_R01.py'),str(H/'SELLO_PI09_D_R02.json'):sha(H/'SELLO_PI09_D_R02.json')}
 p['post_D_scope']={'same_continuous_life':True,'first_D_evaluation_closed6_required':True,'reader_frozen_before_panel':True,'not_on_selected_principal_yet':True,'old_FI7of8_untouched':True,'new_FI_lot8_expected_before':0,'new_FI_expected_after':3,'no_new_acquisition_from_taught_answer':True,'Native_executed_by_preparation':False}
 out.write_text(json.dumps(p,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'plan':str(out),'sha256':sha(out),'driver_sha256':sha(driver),'bound':sum(s['max_ticks']for s in steps),'Native_executed':False}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--tick',type=int,required=True);main(p.parse_args())
