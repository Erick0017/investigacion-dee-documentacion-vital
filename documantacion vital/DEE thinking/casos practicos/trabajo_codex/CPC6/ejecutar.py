"""Single supervised entry; resume completed cases instead of duplicating them."""
import argparse,json,sys,subprocess,time,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'src'))
from common import ROOT
from supervisor import run,remaining,OwnedJob

def future_reproduction(name,command,timeout):
    """Explicit later authorized reproduction; never changes campaign BUDGET."""
    timeout=min(max(int(timeout),1),900);target=ROOT/'jobs'/name;target.mkdir(parents=True,exist_ok=False)
    started=time.monotonic()
    with (target/'stdout.log').open('w',encoding='utf-8') as out,(target/'stderr.log').open('w',encoding='utf-8') as err:
        p=subprocess.Popen([str(x) for x in command],cwd=ROOT,stdout=out,stderr=err,creationflags=subprocess.CREATE_NO_WINDOW)
        try:job=OwnedJob(p)
        except Exception:p.kill();p.wait();raise
        try:p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:job.terminate();p.wait(timeout=30)
        finally:job.close()
    result={'name':name,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-started,
            'mode':'EXPLICIT_LATER_REPRODUCTION_NOT_ORIGINAL_CAMPAIGN','original_budget_unchanged':True,'timeout_seconds':timeout}
    (target/'COMMAND.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result));return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path);p.add_argument('--salida',type=Path)
    p.add_argument('--demo',action='store_true');p.add_argument('--seed',type=int,default=1)
    p.add_argument('--timeout',type=int,default=600)
    p.add_argument('--reproduccion',action='store_true',help='Explicit later replay with local timeout; never resets the original campaign budget')
    a=p.parse_args()
    stem='demo' if a.demo else (a.config.stem if a.config else 'D06_BILATERAL')
    config=a.config or ROOT/'configuraciones/D06_BILATERAL.json'
    out=a.salida or ROOT/'resultados'/('REPRO_'+stem)
    name='entry_'+stem;number=1
    while (ROOT/'jobs'/name).exists():number+=1;name='entry_'+stem+'_'+str(number)
    if a.demo:
        command=[sys.executable,ROOT/'app.py','--demo','--seed',a.seed,'--salida',out/'DIALOGOS.jsonl','--snapshot',out/'SESSION.deetsnap']
    else:command=[sys.executable,ROOT/'src/life.py','--config',config,'--out',out]
    result=future_reproduction(name,command,a.timeout) if a.reproduccion and remaining()<=0 else run(name,command,timeout=a.timeout)
    raise SystemExit(result['exit_code'])
if __name__=='__main__':main()
