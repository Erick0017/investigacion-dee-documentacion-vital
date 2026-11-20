"""Root finite R03 operation list; parameters select protocol arms, never answers."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,re
P=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(a):
 if not re.fullmatch(r'[A-Za-z0-9_]{1,45}',a.name):raise ValueError('Fresh scoped plan name')
 steps=[];mode='eci01-pi07-r03-'
 if a.kind=='prepare':
  if not a.prefix_sha or len(a.prefix_sha)!=64:raise ValueError('Actual closed post28 source manifest SHA')
  steps=[{'label':'PREPARAR','literal':{'modo':mode+'preparar','prefijo_sha256':a.prefix_sha},'max_native_ticks':3,'expected_new_ticks':3}]
 elif a.kind=='calibrate':
  if a.force not in('pulso','nada'):raise ValueError('Fixed diagnostic force')
  steps=[{'label':'INICIAR','literal':{'modo':mode+'iniciar','clase':'viability','brazo':'real','registro_global':True},'max_native_ticks':0}]
  steps += [{'label':f'CAL{i:02d}','literal':{'modo':mode+'calibrar','forzar':a.force},'max_native_ticks':1300}for i in range(2)]
 else:
  if not 0<=a.ordinal<18 or not 1<=a.count<=18-a.ordinal:raise ValueError('Finite frozen R03 range')
  if a.arm:
   if a.ordinal!=0 or not a.authorization:raise ValueError('Only initial exact closed-calibration admission')
   text=a.authorization.read_text('utf8');auth=json.loads(text)
   if auth.get('evaluation_authorized')is not True:raise ValueError('No failed calibration authorization')
   literal={'modo':mode+'iniciar','clase':'evaluation','brazo':a.arm,'registro_global':a.global_record,'autorizacion':text,'autorizacion_sha256':hashlib.sha256(text.encode('utf8')).hexdigest()}
   if a.arm=='yoked':
    if not a.source:raise ValueError('Actual real first12 consequence evidence required')
    d=json.loads(a.source.read_text('utf8'));values=d['actual_failed']
    if len(values)!=12 or any(type(x)is not bool for x in values):raise ValueError('Twelve actual booleans')
    plan=json.dumps({'schema':'DEE.PI07.yoked_return.roll5.v1','roll':5,'roll_direction':'source_plus_5','source_failed':values,'values':[values[(i+5)%12]for i in range(12)],'source_evidence_sha256':sha(a.source)},ensure_ascii=False,separators=(',',':'))
    literal.update(plan=plan,plan_sha256=hashlib.sha256(plan.encode('utf8')).hexdigest())
   steps.append({'label':'INICIAR','literal':literal,'max_native_ticks':0})
  for i in range(a.ordinal,a.ordinal+a.count):
   literal={'modo':mode+'episodio'}
   if a.sensor_ablation:literal['sensor_ablation']=True
   if a.actuator_ablation:literal['actuator_ablation']=True
   steps.append({'label':f'EP{i:02d}','literal':literal,'max_native_ticks':1300})
 protocol=P/'codigo/PROTOCOLO_PI07_R03.json'
 if sha(protocol)!='f69e8558799558a1ccceb70e0684a061a971b9521ad8985205d1662aea55d269':raise ValueError('Frozen R03 differs')
 d={'schema':'DEE.PI07.fixed_phase_plan.v1','status':'SEALED','initial_tick':a.tick,'max_native_ticks':sum(x['max_native_ticks']for x in steps),'steps':steps,'description':a.description,'registration_utc':datetime.now(timezone.utc).isoformat(),'source_proof':{'protocol':str(protocol),'sha256':sha(protocol)}}
 out=P/'control'/('PLAN_'+a.name+'.json')
 with out.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'plan':str(out),'sha256':sha(out)}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--kind',choices=['prepare','calibrate','evaluate'],required=True);ap.add_argument('--name',required=True);ap.add_argument('--tick',type=int,required=True);ap.add_argument('--description',required=True)
 ap.add_argument('--prefix-sha');ap.add_argument('--force',choices=['pulso','nada']);ap.add_argument('--ordinal',type=int,default=0);ap.add_argument('--count',type=int,default=1);ap.add_argument('--arm',choices=['real','none','yoked']);ap.add_argument('--global-record',action='store_true');ap.add_argument('--authorization',type=Path);ap.add_argument('--source',type=Path);ap.add_argument('--sensor-ablation',action='store_true');ap.add_argument('--actuator-ablation',action='store_true');main(ap.parse_args())
