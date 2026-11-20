"""Prospectively freeze the common twelve actual consultation opportunities."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json
P=Path(__file__).resolve().parents[1];H=P/'codigo'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(a):
 seal=read(H/'SELLO_PI09_CONSULTA_R01.json');arm=a.brazo;slug={'native_real':'NATIVE','always_real':'ALWAYS','never':'NEVER','always_desacoplado':'YOKE'}[arm]
 dest=H/('PLAN_'+slug+'_R01.json')
 if dest.exists():raise FileExistsError('Preserve prospective plan')
 admission={'modo':'eci01-pi09-preparar','brazo':arm}
 if arm=='always_desacoplado':
  if a.plan_muestras is None:raise ValueError('Actual complete fixed-permutation source samples required')
  value=read(a.plan_muestras);admission['plan']=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
 steps=[{'label':'STATE_BEFORE','literal':{'modo':'eci01-pi09-estado'},'max_ticks':0},{'label':'ADMISSION','literal':admission,'max_ticks':0}]
 steps.extend({'label':'EP%02d'%i,'literal':{'modo':'eci01-pi09-episodio'},'max_ticks':2110,'stage':'development'if i<6 else'reserved'}for i in range(12))
 steps.append({'label':'STATE_AFTER','literal':{'modo':'eci01-pi09-estado'},'max_ticks':0})
 v={'schema':'DEE.PI09.prospective.finite_plan.R01','created_utc':datetime.now(timezone.utc).isoformat(),'system':str(P/'estados'/slug/'sistema'),'life_id':seal['arms'][arm],'tag':'PI09_'+slug+'_R01','initial_tick':884835,'steps':steps,'pins':{str(H/n):sha(H/n)for n in('SELLO_PI09_CONSULTA_R01.json','PROTOCOLO_PI09_CONSULTA_R01.json','pi09_consulta_selectiva_R01.py','CRITERIOS_PI09_R01.json')},'evaluation_only':'No expected choice, target or outcome is passed to the candidate. The arm and yoke are declared controls, not a hidden host policy.'}
 dest.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'plan':str(dest),'sha256':sha(dest),'ticks_bound':25320,'new_Native':False}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--brazo',choices=('native_real','always_real','never','always_desacoplado'),required=True);p.add_argument('--plan-muestras',type=Path);main(p.parse_args())
