"""Installed4.5 finite profile vs frozen4.0; references read AFTER trajectory."""
from array import array
import argparse
import hashlib
import json
from pathlib import Path
import sys


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def digest(s):
    r=s.world.runtime
    return {'tick':int(r.current_tick),'raw_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
            'clock_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True)
    p.add_argument('--baseline',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=False)
    import dee_thinking as d
    from dee_thinking.experimental_absence import AbsenceSession
    assert d.__version__=='4.5.0' and Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    config=json.loads(a.config.read_text(encoding='utf8'));result={'schema':'DEE4.5.absence-port.differential.v1',
        'version':d.__version__,'module':d.__file__,'profile_module':sys.modules[AbsenceSession.__module__].__file__,
        'native_sha256':sha(d._native.__file__),'config_sha256':sha(a.config),'cases':[]}
    for case in config['cases']:
        s=AbsenceSession.create();s.experience_order(case['history'])
        s.acquire_source(case['source_value'],mode=case['source_mode']);s.prepare_use();frames=[]
        for tick in (0,5,15,19,24,29,35):
            s.run_until(tick)
            if tick==5 and case['actual'] is not None:s.actual(case['actual'])
            frames.append(digest(s))
        requests=sorted([{'port':q['port'],'payload':q['payload'],'tick':q['tick'],'kind':q['kind'],
            'status':q['receipt']['status'],'effective_tick':q['receipt']['effective_tick'],'reason':q['receipt']['reason']}
            for q in s.receipts()],key=lambda q:(q['tick'],q['port'],q['kind']))
        # No reference, target or table is accessible to the participant above.
        baseline=json.loads((a.baseline/'RESULT.json').read_text(encoding='utf8'))
        reference=next(q for q in baseline['cases'] if q['case']['id']==case['id'])
        checks=[{'tick':x['tick'],'RAW_clocks_tick_equal':x==y} for x,y in zip(frames,reference['frames'])]
        item={'case':case,'frames':frames,'exact_local_readings':s.readings,'requests':requests,'physical_comparisons':checks,
            'request_payload_tick_status_equal':requests==reference['requests']}
        item['status']='PASS' if all(x['RAW_clocks_tick_equal'] for x in checks) and item['request_payload_tick_status_equal'] else'FAIL'
        result['cases'].append(item);(a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    result['historical_imports']=[x for x in sys.modules if x in('order_memory','common','comparison_need','comparison_need_v2','run_need')]
    result['status']='PASS' if all(x['status']=='PASS' for x in result['cases']) and not result['historical_imports'] else'FAIL'
    (a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({'status':result['status'],'cases':len(result['cases'])}))
    if result['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
