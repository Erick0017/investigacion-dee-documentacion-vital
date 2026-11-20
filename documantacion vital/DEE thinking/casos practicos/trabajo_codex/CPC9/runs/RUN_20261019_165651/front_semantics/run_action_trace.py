"""Frozen small causal-origin pilot. All decisions use supplied current commands.
No actor target or future state is read by participant code.
"""
import argparse,hashlib,json,sys,time
from pathlib import Path
from array import array
BASE=Path(__file__).resolve().parent
sys.path.insert(0,str(BASE/'src'))
from action_trace import ActionTraceSession

def digest(s):
    r=s.world.runtime
    return {'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest(),'tick':int(r.current_tick)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--config',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    cfgpath=Path(a.config);cfg=json.loads(cfgpath.read_text(encoding='utf-8-sig'));out=Path(a.out);out.mkdir(parents=True,exist_ok=False)
    src=BASE/'src'/'action_trace.py';(out/'executed_source.py').write_bytes(src.read_bytes())
    rows=[]
    for case in cfg['cases']:
        t=time.monotonic();s=ActionTraceSession.create(**case.get('options',{}));s.curriculum(case.get('actor','A'),case.get('omit',False))
        frames=[]
        for tick in cfg['ticks']:
            s.run_until(tick);frames.append(s.capture())
            if tick in (1,11,16,32):s.save(out/(case['case_id']+'_'+str(tick)+'.snapshot.gz'))
        row={'case_id':case['case_id'],'modality':'AUX_PREPARATION','case':case,'geometry':s.geometry,
             'frames':frames,'receipts':s.receipts(),'terminal_state':digest(s),'elapsed_seconds':time.monotonic()-t,
             'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'configuration_sha256':hashlib.sha256(cfgpath.read_bytes()).hexdigest()}
        (out/(case['case_id']+'.json')).write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');rows.append(row['case_id']);print(case['case_id'],flush=True)
    (out/'BATCH.json').write_text(json.dumps({'cases':rows,'scope':cfg['scope']},ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
