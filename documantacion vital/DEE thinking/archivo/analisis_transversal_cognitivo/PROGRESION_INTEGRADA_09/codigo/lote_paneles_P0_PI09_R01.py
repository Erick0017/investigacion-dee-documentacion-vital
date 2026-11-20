"""Root-only paired conservation/challenge continuations; fixed before Native."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,subprocess,time
P=Path(__file__).resolve().parents[1];H=P/'codigo';PY=P.parents[2]/'DEE Cognitive 2.0/motor/python313/python.exe';BASE=[str(PY),'-I','-B','-X','utf8']
def main(a):
 commands=[]
 for slug in('PANEL','DISCOVERY'):
  commands.extend([(slug+'_IMPORT',BASE+[str(H/'clonar_post12_PI09_R03.py'),'--slug',slug,'--prefijo',str(P/'pares/NATIVE_POST12_T903603'),'--manifest-sha256','0cce6bcfe366551b52b0ca25c5959bd6e07ed4493221ec26b76af962c13b6553','--importar'],360),(slug+'_P0_CODE',BASE+[str(H/'instalar_P0_post12_PI09_R01.py'),'--slug',slug,'--aplicar'],120),(slug+'_NATIVE',BASE+[str(H/'ejecutar_plan_PI09_R02.py'),'--plan',str(H/('PLAN_'+slug+'_P0_R01.json')),'--ejecutar'],1800)])
 if not a.ejecutar:print(json.dumps({'mode':'PLAN_ONLY','commands':commands,'Native_executed':False}));return
 proof=P/'control/LOTE_PANELES_P0_PI09_R01.json'
 if proof.exists():raise FileExistsError(proof)
 cutoff=datetime.fromisoformat(json.loads((P/'REGISTRO_CAMPANA.json').read_text('utf8'))['budget']['new_experimental_uses_cutoff_local']).astimezone(timezone.utc);rows=[];error=None
 try:
  for label,cmd,bound in commands:
   if datetime.now(timezone.utc)>=cutoff:raise TimeoutError('No next child after cutoff')
   so=P/'ensayos'/(label+'.P0.supervisor.stdout.txt');se=P/'ensayos'/(label+'.P0.supervisor.stderr.txt');start=time.monotonic()
   with so.open('x',encoding='utf8')as out,se.open('x',encoding='utf8')as err:
    child=subprocess.Popen(cmd,cwd=P,stdout=out,stderr=err)
    try:code=child.wait(timeout=bound)
    except subprocess.TimeoutExpired:raise TimeoutError('Child horizon exceeded; preserve exactPID%d and state. No automatic kill/retry'%child.pid)
   rows.append({'label':label,'command':cmd,'pid':child.pid,'exit_code':code,'elapsed_seconds':time.monotonic()-start,'stdout':str(so),'stderr':str(se)})
   if code:raise RuntimeError('Stop after '+label+'; inspect preserved result, do not repeat batch')
 except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
 value={'schema':'DEE.PI09.actual_paired_P0_conservation_batch.R01','status':'CLOSED_BOTH_PANELS'if error is None else'STOPPED_PRESERVED','error':error,'children':rows,'never_promotes':True};proof.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'status':value['status'],'error':error,'children':len(rows),'proof':str(proof)}))
 if error:raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ejecutar',action='store_true');main(p.parse_args())
