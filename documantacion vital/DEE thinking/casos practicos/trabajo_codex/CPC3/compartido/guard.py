"""Independent CPC3 guard; only registered exact child PIDs may be terminated."""
import json,os,subprocess,sys,time
from pathlib import Path
from datetime import datetime,timezone
sys.path.insert(0,str(Path(__file__).resolve().parent))
from supervise import Budget,atomic_json,stop_registered,stop_child

def main(root):
    root=Path(root).resolve();b=Budget(root);active=root/'compartido/ACTIVE';active.mkdir(exist_ok=True)
    atomic_json(root/'compartido/GUARD_STATUS.json',{'pid':os.getpid(),'status':'ACTIVE','campaign':'CPC3','deadline':b.data['deadline_utc']})
    while b.remaining()>0:
        if (root/'compartido/CLOSED.json').exists():
            atomic_json(root/'compartido/GUARD_STATUS.json',{'pid':os.getpid(),'status':'CLOSED'});return
        for path in active.glob('*.json'):
            item=json.loads(path.read_text(encoding='utf-8'))
            if item.get('status')!='RUNNING':continue
            age=(datetime.now(timezone.utc)-datetime.fromisoformat(item['started_utc'])).total_seconds()
            if age>item['timeout_seconds']+5:
                stopped=stop_registered(item);atomic_json(root/'compartido'/('TIMEOUT_'+path.stem+'.json'),{'task':item,'own_process_stopped':stopped})
        if b.elapsed()>=13200:
            for path in active.glob('*.json'):
                item=json.loads(path.read_text(encoding='utf-8'))
                if item.get('status')=='RUNNING':stop_registered(item)
            atomic_json(root/'compartido/CLOSED.json',{'partial':True,'reason':'original CPC3 closure cutoff','elapsed_seconds':b.elapsed()})
            finalizer=root/'compartido/package_cpc3.py'
            if finalizer.exists():
                with (root/'compartido/AUTO_PACKAGE.log').open('w',encoding='utf-8') as log:
                    p=subprocess.Popen([sys.executable,'-I','-B',str(finalizer),'--root',str(root),'--partial','--publish'],stdout=log,stderr=log,creationflags=subprocess.CREATE_NO_WINDOW)
                    try:p.wait(timeout=min(900,max(1,b.remaining()-15)))
                    except subprocess.TimeoutExpired:stop_child(p)
            atomic_json(root/'compartido/GUARD_STATUS.json',{'pid':os.getpid(),'status':'AUTO_CLOSED'});return
        time.sleep(1)

if __name__=='__main__':main(sys.argv[1])
