"""Proportionate worker timeouts, same frozen neutral cases and recorder.

The original4.0 suite log remains intact. N127 complete-array instrumentation
has a600second limit here after measured180second initial technical bounds.
"""
from pathlib import Path
import argparse,json,subprocess,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from neutral_differential import put,sha


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,default=Path(__file__).with_name('neutral_config.json'))
    p.add_argument('--out',type=Path,required=True);p.add_argument('--expected-version',required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf-8'));a.out.mkdir(parents=True,exist_ok=True);rows=[]
    for case in cfg['cases']:
        for backend in cfg['backend_names']:
            folder=a.out/(case['id']+'_'+backend);target=folder/'RESULT.json'
            if target.exists():r=json.loads(target.read_text(encoding='utf-8'))
            else:
                argv=[sys.executable,'-I','-B',str(Path(__file__).with_name('neutral_differential.py')),'case',
                    '--config',str(a.config.resolve()),'--case-id',case['id'],'--backend',backend,
                    '--out',str(folder.resolve()),'--expected-version',a.expected_version]
                timeout=600 if case.get('recipe')=='cascade2' else 90;start=time.monotonic()
                try:
                    q=subprocess.run(argv,capture_output=True,text=True,timeout=timeout)
                    r={'status':'PASS' if q.returncode==0 and target.exists() else 'FAIL','exit_code':q.returncode,
                       'stdout':q.stdout,'stderr':q.stderr,'timeout_seconds':timeout,'elapsed_seconds':time.monotonic()-start}
                except subprocess.TimeoutExpired as e:r={'status':'TIMEOUT','error':str(e),'timeout_seconds':timeout,'elapsed_seconds':time.monotonic()-start}
                put(a.out/(folder.name+'.PROCESS.json'),r)
            rows.append({'case_id':case['id'],'backend':backend,'status':r['status'],'result':folder.name+'/RESULT.json'})
            put(a.out/'INDEX.json',{'schema':'DEE45.neutral_differential.index.v1','library':a.expected_version,'config_sha256':sha(a.config),'cases':rows})
    if any(x['status']!='PASS' for x in rows):raise SystemExit(1)

if __name__=='__main__':main()
