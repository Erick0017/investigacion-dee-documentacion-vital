"""Prospective finite opportunity list; no actor policy or response targets.

Root uses a fresh plan for an already identified diagnostic continuation.
The R02 protocol supplies every environmental row; this only bounds execution.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
P=Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main(a):
 if not re.fullmatch(r'[A-Za-z0-9_]{1,45}',a.name):raise ValueError('Fresh scoped plan name')
 if not 0<=a.ordinal<28 or not 1<=a.count<=28-a.ordinal:raise ValueError('Frozen28-opportunity range only')
 steps=[]
 if a.arm:
  if a.ordinal!=0:raise ValueError('Initial admission only at actual P0')
  literal={'modo':'eci01-pi07-iniciar','brazo':a.arm,'registro_global':False}
  if a.arm=='yoked':
   if not a.source:raise ValueError('Actual closed twelve-return evidence required')
   source=a.source.resolve(strict=True);d=json.loads(source.read_text('utf-8-sig'))
   values=d['actual_failed']
   if len(values)!=12 or any(type(x)is not bool for x in values):raise ValueError('Exactly twelve actual boolean consequences')
   text=json.dumps({'schema':'DEE.PI07.yoked_return.roll5.v1','roll':5,'roll_direction':'source_plus_5','source_failed':values,'values':[values[(i+5)%12]for i in range(12)],'source_evidence_sha256':sha(source)},ensure_ascii=False,separators=(',',':'))
   literal.update(plan=text,plan_sha256=hashlib.sha256(text.encode('utf8')).hexdigest())
  steps.append({'label':'INICIAR','literal':literal,'max_native_ticks':0})
 if a.reverse:
  if a.ordinal!=12:raise ValueError('Only declared post12 nonfailure control')
  steps.append({'label':'CONTROL','literal':{'modo':'eci01-pi07-configurar-control','brazo':'none','registro_global':False},'max_native_ticks':0})
 for i in range(a.ordinal,a.ordinal+a.count):
  literal={'modo':'eci01-pi07-episodio'}
  if a.sensor_ablation:literal['sensor_ablation']=True
  if a.actuator_ablation:literal['actuator_ablation']=True
  steps.append({'label':f'EP{i:02d}','literal':literal,'max_native_ticks':1300})
 protocol=P/'codigo/PROTOCOLO_PI07_R02.json'
 d={'schema':'DEE.PI07.fixed_phase_plan.v1','status':'SEALED','initial_tick':a.tick,'max_native_ticks':a.count*1300,'steps':steps,'description':a.description,'registration_utc':datetime.now(timezone.utc).isoformat(),'source_proof':{'protocol':str(protocol),'sha256':sha(protocol),'ordinal_range':[a.ordinal,a.ordinal+a.count-1]}}
 out=P/'control'/('PLAN_'+a.name+'.json')
 with out.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'plan':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument('--name',required=True);ap.add_argument('--tick',required=True,type=int);ap.add_argument('--ordinal',required=True,type=int);ap.add_argument('--count',required=True,type=int)
 ap.add_argument('--arm',choices=['real','none','yoked']);ap.add_argument('--source',type=Path);ap.add_argument('--reverse',action='store_true');ap.add_argument('--sensor-ablation',action='store_true');ap.add_argument('--actuator-ablation',action='store_true');ap.add_argument('--description',required=True)
 main(ap.parse_args())
