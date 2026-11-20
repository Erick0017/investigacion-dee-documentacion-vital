"""Root-only fixed controls; no automatic retry or parallel Native writer."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,json,subprocess,time
P=Path(__file__).resolve().parents[1];H=P/'codigo';PY=P.parents[2]/'DEE Cognitive 2.0/motor/python313/python.exe';BASE=[str(PY),'-I','-B','-X','utf8']
def main(a):
 commands=[]
 def imp(slug):return BASE+[str(H/'clonar_C_PI09_R02.py'),'--slug',slug,'--vida','ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_'+slug+'_01','--importar']
 def run(slug):return BASE+[str(H/'ejecutar_plan_PI09_R01.py'),'--plan',str(H/('PLAN_'+slug+'_R03.json')),'--ejecutar']
 data=H/'DATOS_YOKE_PI09_R03.json'
 commands=[('ALWAYS_IMPORT',imp('ALWAYS'),360),('ALWAYS_NATIVE',run('ALWAYS'),1800),('YOKE_DATA',BASE+[str(H/'CREAR_PLAN_DATOS_PI09_R01.py'),'--prefijo','PI09_ALWAYS_R03','--evidencia',str(P/'control/PI09_ALWAYS_R03.json'),'--salida',str(data)],60),('YOKE_PLAN',BASE+[str(H/'preparar_planes_consulta_PI09_R03.py'),'--brazo','always_desacoplado','--plan-muestras',str(data)],60),('NEVER_IMPORT',imp('NEVER'),360),('NEVER_NATIVE',run('NEVER'),1800),('YOKE_IMPORT',imp('YOKE'),360),('YOKE_NATIVE',run('YOKE'),1800)]
 if not a.ejecutar:print(json.dumps({'plan':commands,'Native_executed':False}));return
 proof=P/'control/LOTE_CONTROLES_CONSULTA_PI09_R03.json'
 if proof.exists():raise FileExistsError(proof)
 cutoff=datetime.fromisoformat(json.loads((P/'REGISTRO_CAMPANA.json').read_text('utf8'))['budget']['new_experimental_uses_cutoff_local']).astimezone(timezone.utc);rows=[];error=None
 try:
  for label,cmd,timeout in commands:
   if datetime.now(timezone.utc)>=cutoff:raise TimeoutError('No new operation after cutoff')
   so=P/'ensayos'/(label+'.R03.supervisor.stdout.txt');se=P/'ensayos'/(label+'.R03.supervisor.stderr.txt');start=time.monotonic()
   with so.open('x',encoding='utf8')as out,se.open('x',encoding='utf8')as err:
    child=subprocess.Popen(cmd,cwd=P,stdout=out,stderr=err)
    try:code=child.wait(timeout=timeout)
    except subprocess.TimeoutExpired:raise TimeoutError('Horizon exceeded; preserve exact child PID%d. No kill/retry'%child.pid)
   rows.append({'label':label,'command':cmd,'pid':child.pid,'exit_code':code,'elapsed_seconds':time.monotonic()-start,'stdout':str(so),'stderr':str(se)})
   if code:raise RuntimeError('Stop after '+label+'; inspect exact closed/uncertain future, never repeat the batch')
 except Exception as exc:error={'type':type(exc).__name__,'message':str(exc),'automatic_retry':False}
 value={'schema':'DEE.PI09.actual.fixed_control_batch.R03','status':'CLOSED_ALL_CONTROLS'if error is None else'STOPPED_PRESERVED','error':error,'children':rows,'no_controls_can_select_MAIN':True};proof.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'status':value['status'],'error':error,'children':len(rows),'proof':str(proof)},ensure_ascii=False))
 if error:raise SystemExit(1)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--ejecutar',action='store_true');main(p.parse_args())
