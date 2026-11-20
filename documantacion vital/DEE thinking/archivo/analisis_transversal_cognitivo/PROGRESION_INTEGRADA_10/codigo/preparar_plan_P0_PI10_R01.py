"""Write a finite P0-only plan from closed configuration. No Native imports."""
from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 system=P/'estados/P0/sistema';life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_P0_01';source=P/'pares/PRINCIPAL_D_T922371/EXPORTACION_SERVICIO.json';out=H/'PLAN_PI10_P0_OWNER_R01.json'
 if not system.is_dir()or sha(source)!='cd56d93b1a76a27198b4bacf8922f9ed16228337f162e72c5967806785958d65':raise ValueError('Exact current-D pair and prepared P0 system required')
 value={'schema':'DEE.PI10.prospective.finite_owner_plan.R01','tag':'PI10_P0_OWNER_R01','system':str(system),'life_id':life,'initial_tick':922371,'max_host_seconds':900,'source_complete_pair':{'file':str(source),'sha256':sha(source)},'scope':'One additive legal unlearned TC installation, inherited device reused. Invalid literal is rejected before queue admission. No evaluation or learned gain claimed.','steps':[{'label':'INVALID_LITERAL_REJECTED_BEFORE_ADMISSION','literal':{'modo':'eci01-pi10-preparar','respuesta':1},'max_ticks':0,'expect_prequeue_rejection':True,'feedback':'omit','actuator':'closed'},{'label':'LEGAL_P0_PREPARATION','literal':{'modo':'eci01-pi10-preparar'},'max_ticks':3,'feedback':'omit','actuator':'closed'},{'label':'STATE_AFTER_P0','literal':{'modo':'eci01-pi10-estado'},'max_ticks':0,'feedback':'omit','actuator':'closed'}],'pins':{str(H/'pi10_consulta_adaptativa_R01.py'):sha(H/'pi10_consulta_adaptativa_R01.py'),str(H/'pi10_transporte_ancestral_R01.py'):sha(H/'pi10_transporte_ancestral_R01.py')}}
 if out.exists():
  if json.loads(out.read_text('utf-8-sig'))!=value:raise ValueError('Prior plan differs; preserve before writing a declared new revision')
 else:
  with out.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'plan':str(out),'sha256':sha(out),'finite_bound':3,'Native':0}))
if __name__=='__main__':main()
