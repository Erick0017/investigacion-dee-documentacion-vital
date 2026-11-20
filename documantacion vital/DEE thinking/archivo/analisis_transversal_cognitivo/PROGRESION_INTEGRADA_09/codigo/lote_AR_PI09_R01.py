"""Root-only three fixed arithmetic controls, sequential, never retry."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,subprocess,time
P=Path(__file__).resolve().parents[1];H=P/'codigo';PY=P.parents[2]/'DEE Cognitive 2.0/motor/python313/python.exe'
def main(a):
 cases=('AR36','AR64','AR0NOD');commands=[]
 for case in cases:
  common=[str(PY),'-I','-B','-X','utf8',str(H/'clonar_C_PI09_R01.py'),'--slug',case,'--vida','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'+case+'_01']
  commands.extend([(case+'_PREP',common+['--preparar'],360),(case+'_IMPORT',common+['--importar'],360),(case+'_NATIVE',[str(PY),'-I','-B','-X','utf8',str(H/'ejecutar_plan_PI09_R01.py'),'--plan',str(H/('PLAN_'+case+'_R02.json')),'--ejecutar'],1200)])
 if not a.ejecutar:print(json.dumps({'plan':commands,'Native_executed':False}));return
 out=P/'control/LOTE_AR_PI09_R01.json'
 if out.exists():raise FileExistsError(out)
 cutoff=datetime.fromisoformat(json.loads((P/'REGISTRO_CAMPANA.json').read_text('utf8'))['budget']['new_experimental_uses_cutoff_local']).astimezone(timezone.utc);rows=[]
 try:
  for label,cmd,bound in commands:
   if datetime.now(timezone.utc)>=cutoff:raise TimeoutError('No new child after scientific cutoff')
   stdout=P/'ensayos'/(label+'.supervisor.stdout.txt');stderr=P/'ensayos'/(label+'.supervisor.stderr.txt')
   with stdout.open('x',encoding='utf8')as so,stderr.open('x',encoding='utf8')as se:
    begin=time.monotonic();process=subprocess.Popen(cmd,cwd=P,stdout=so,stderr=se)
    try:code=process.wait(timeout=bound)
    except subprocess.TimeoutExpired:raise TimeoutError('Child horizon exceeded; preserve exact PID%d and state, no kill/retry'%process.pid)
   rows.append({'label':label,'command':cmd,'pid':process.pid,'exit_code':code,'elapsed_seconds':time.monotonic()-begin,'stdout':str(stdout),'stderr':str(stderr)})
   if code:raise RuntimeError('Stopped after '+label+'; inspect preserved child output, do not repeat the batch')
  status='CLOSED_THREE_FIXED_CONTROLS';error=None
 except Exception as e:status='STOPPED_PRESERVED';error={'type':type(e).__name__,'message':str(e),'automatic_retry':False}
 out.write_text(json.dumps({'schema':'DEE.PI09.fixed_AR_sequential_batch.R01','status':status,'error':error,'children':rows},ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'status':status,'error':error,'completed_children':len(rows),'proof':str(out)},ensure_ascii=False))
 if error:raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ejecutar',action='store_true');main(p.parse_args())
