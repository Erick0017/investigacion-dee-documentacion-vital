"""Installed4.5 remote preparation vs official4.0 frozen CPC6 trajectories.

Comparison records are read only AFTER their corresponding new trajectory.
Participant inputs use the fixed selected historical configuration only.
"""
from array import array
import argparse
import hashlib
import json
from pathlib import Path
import sys
import traceback


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def digest(s):
    r=s.world.runtime
    return {'tick':int(r.current_tick),
        'raw_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
        'clock_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}


def requests(s):
    return sorted([{'port':q['port'],'payload':q['payload'],'tick':q['tick'],'kind':q.get('kind','submit'),
                    'status':q['receipt']['status'],'effective_tick':q['receipt']['effective_tick'],
                    'reason':q['receipt']['reason']} for q in s.receipts()],key=lambda q:(q['tick'],q['port'],q['kind']))


def baseline_requests(result):
    return sorted([{'port':q['port'],'payload':q['payload'],'tick':q['tick'],'kind':q.get('kind','submit'),
                    'status':q['receipt']['status'],'effective_tick':q['receipt']['effective_tick'],
                    'reason':q['receipt']['reason']} for q in result['requests']],key=lambda q:(q['tick'],q['port'],q['kind']))


def execute(case):
    from dee_thinking.remote_reader import RemoteReaderSession
    s=RemoteReaderSession.create();frames=[]
    s.experience_order(case['history'],event_payload=case['event_load'])
    s.acquire_sources(case['source_values']['P'],case['source_values']['Q'])
    s.late_use(payload=case['late_payload'])
    # Keep the original request calendar for this differential instrument.
    # The public facade only transports the explicitly declared ports.
    s.stimulate([{'port':s.geometry['renewed_interfaces']['original']['port'],'payload':11,'tick':69,'kind':'probe'}])
    frames.append({'label':'INITIAL_T0','physical':digest(s)})
    checkpoints=set(case['checkpoints'])
    for tick in range(case['horizon']+1):
        s.run_until(tick)
        if tick==5:s.consequence(case['actual'])
        if tick==34:
            s.teach_first_form(mode=case['language_mode'])
            s.query_first_form(tick=50,payload=case['language_query_load'])
            for delay in case.get('language_repeat_delays',[]):
                s.query_first_form(tick=50+delay,payload=case['language_query_load'])
        if tick==71:
            g=s.geometry['order_language'];entries=[]
            for x in g['items'].values():entries.append({'port':x['teach_port'],'payload':5,'tick':77})
            for x in g['items'].values():entries.append({'port':x['query_port'],'payload':7,'tick':87,'kind':'probe'})
            s.stimulate(entries)
            # Recorder only: no physical write or information returned to MAIN.
            s._read_boundary('second_form',90)
        if tick in checkpoints:frames.append({'label':'T'+str(tick),'physical':digest(s)})
    return s,frames


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--baseline',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False)
    import dee_thinking as d
    assert d.__version__=='4.5.0' and Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    config=json.loads(a.config.read_text(encoding='utf-8'));selected=[config['cases'][i] for i in(0,1,4)]
    result={'schema':'DEE4.5.remote-reader.differential.v1','version':d.__version__,'module':d.__file__,
            'python':sys.executable,'native_sha256':sha(d._native.__file__),'instrument_sha256':sha(__file__),
            'config_sha256':sha(a.config),'cases':[],'historical_imports':[]}
    try:
        for case in selected:
            item={'case_id':case['id']};result['cases'].append(item)
            try:
                s,frames=execute(case)
                item['frames']=frames;item['requests']=requests(s);item['readings']=s.readings
                reference_path=a.baseline/case['id']/'MEASUREMENTS.json'
                reference=json.loads(reference_path.read_text(encoding='utf-8'))
                item['baseline_measurements_sha256']=sha(reference_path)
                ref_frames={Path(x['path']).stem:x['physical'] for x in reference['snapshots']}
                item['frame_comparisons']=[{'label':f['label'],'exact_RAW_clocks_tick':f['physical']==ref_frames[f['label']]} for f in frames]
                item['physical_all_boundaries_equal']=all(x['exact_RAW_clocks_tick'] for x in item['frame_comparisons'])
                item['receipt_payload_tick_status_equal']=item['requests']==baseline_requests(reference)
                item['baseline_decoded']=[{'tick':r['tick'],'first':r.get('decoded_language'),
                    'second':r.get('decoded_order_language'),'remote':r.get('decoded_word_bus')}
                    for r in reference['rows'] if r['tick'] in(53,90,162)]
                item['status']='PASS' if item['physical_all_boundaries_equal'] and item['receipt_payload_tick_status_equal'] else 'FAIL'
            except BaseException as error:
                item.update(status='FAIL',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc())
            (a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        result['historical_imports']=[x for x in sys.modules if x in('life','common','integrated','consolidation','curriculum','word_bus','language')]
        result['scope']='Full physical fields at all listed frozen boundaries and physical input/status multiset. Version/session envelope and operation-ID chronology may differ; no binary ABI claim.'
        result['status']='PASS' if all(x['status']=='PASS' for x in result['cases']) and not result['historical_imports'] else 'FAIL'
    finally:
        (a.out/'RESULT.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    if result['status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
