import argparse,hashlib,json,sys,time
from pathlib import Path
BASE=Path(__file__).resolve().parent;sys.path.insert(0,str(BASE));sys.path.insert(0,str(BASE/'src'))
from content_reflection import ContentReflectionSession
from run_action_trace import digest

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    configpath=Path(a.config);cfg=json.loads(configpath.read_text(encoding='utf-8-sig'));out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    source=BASE/'src/content_reflection.py';(out/'executed_source.py').write_bytes(source.read_bytes())
    ids=[]
    for case in cfg['cases']:
        started=time.monotonic();s=ContentReflectionSession.create(**case.get('options',{}))
        s.curriculum(case['reference'],case['object'],omit=case.get('omit'),unpaired=case.get('unpaired',False))
        frames=[]
        for tick in cfg['ticks']:
            s.run_until(tick);frames.append(s.capture())
            if tick in (5,72,75,207):s.save(out/(case['case_id']+'_'+str(tick)+'.snapshot.gz'))
        m={'case_id':case['case_id'],'modality':'AUX_PREPARATION','case':case,'geometry':s.geometry,'frames':frames,
           'receipts':s.receipts(),'terminal_state':digest(s),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
           'configuration_sha256':hashlib.sha256(configpath.read_bytes()).hexdigest(),'elapsed_seconds':time.monotonic()-started}
        (out/(case['case_id']+'.json')).write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf-8');ids.append(case['case_id']);print(case['case_id'],flush=True)
    (out/'BATCH.json').write_text(json.dumps({'cases':ids,'criteria':cfg['criteria']},ensure_ascii=False,indent=2),encoding='utf-8')
if __name__=='__main__':main()
