"""One fixed exploratory explicit reader for the newly acquired RIGHT state.

Three controlled continuations, no recipe, state edit, timing search, response
lookup, autonomous-question claim or replacement of the earlier failed life.
"""
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import time
import traceback
ROOT=Path(__file__).resolve().parents[2]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):h.update(block)
    return h.hexdigest()


def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    config=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in config['cases']if c['id']==a.case_id);parent=ROOT/case['parent']
    if sha(parent)!=case['parent_sha256']:raise AssertionError('Parent identity mismatch')
    a.out.mkdir(parents=True,exist_ok=False);start=time.monotonic();source=a.out/'executed_source'
    shutil.copytree(ROOT/config['source_bundle'],source/'src');shutil.copyfile(__file__,source/'longitudinal_right_read.py')
    sys.path.insert(0,str(source/'src'))
    import dee_thinking as dee
    from dee_thinking import _native as native
    from dee_thinking.consolidated import exact_observation,exact_receipt
    from comunicacion.social_channel import SocialSession
    from integracion.shared_world import physical,move
    if dee.__version__!='4.5.0'or not Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise AssertionError('Official isolated4.5 required')
    s=SocialSession.load(parent)
    if s.tick!=case['entry_tick']or s.geometry['own_banks']['right']['hub']!=config['query']['fixed_target']:raise AssertionError('Stored physical access differs from frozen contract')
    old_count=len(s.receipts());m={'schema':'CPC8.integration.right1182.measurements.v1','case':case,'query_contract':config['query'],
        'parent':{'path':case['parent'],'sha256':sha(parent),'individual':s.identifier,'physical':physical(s.world)},
        'preparations':0,'continuations':1,'diagnostic_forks':0,'new_interfaces':[],'host_RAW_clock_writes_on_MAIN':[],
        'configuration_sha256':sha(a.config),'executed_source':{p.relative_to(source).as_posix():sha(p)for p in source.rglob('*.py')},
        'engine':{'version':dee.__version__,'module':dee.__file__,'native_sha256':sha(native.__file__),'python':sys.executable},
        'geometry':s.geometry,'frames':[],'snapshots':[],'status':'RUNNING'}
    def save(tick):
        path=a.out/('T'+str(tick)+'.deetsnap.gz');proof=s.save(path);m['snapshots'].append({'tick':tick,'path':path.name,'sha256':sha(path),'physical':physical(s.world),'storage':proof})
    def checkpoint():m.update(last_complete_tick=s.tick,elapsed_seconds=time.monotonic()-start);put(a.out/'MEASUREMENTS.json',m)
    save(s.tick);checkpoint()
    try:
        if s.tick==690:
            entries=[{'port':'event.A','payload':3,'tick':786,'origin':'NEW_CURRENT_ORDER_EVENT'},
                {'port':'event.B','payload':3,'tick':787,'origin':'NEW_CURRENT_ORDER_EVENT'},
                {'port':'order.read','payload':7,'tick':788,'kind':'probe','origin':'EXPLICIT_EXTERNAL_ORDER_QUERY'},
                {'port':'U.right.signal','payload':5,'tick':787,'origin':'SAME_DOSE_RIGHT_CUE_ONE_TICK_DISPLACED'},
                {'port':'U.right.event.minus','payload':11,'tick':786,'origin':'SAME_CURRENT_RIGHT_DIRECTIONAL_EVENT'}]
            entries.extend({'port':'need.actual.'+lane+'.-1','payload':17,'tick':797,'origin':'CURRENT_SENSOR_REPORT_FIXED_CODEC'}for lane in('left','right'))
            s.stimulate(entries);s.query_lower(range(65),1048,9);m['new_experience_inputs']=entries
            for tick in(785,786,787,788,789,919,920,921,922,925,926,1051):
                s.run_until(tick);m['frames'].append({'tick':tick,'observation':s.observe()})
            save(1051);checkpoint()
        q=config['query'];entries=[{'port':q['port'],'payload':q['payload'],'tick':q['input_tick'],'kind':'probe','origin':'EXPLICIT_USER_INSTRUMENTAL_EXPLORATORY_RIGHT_QUERY'}]
        receipt=s.stimulate(entries)[0];m['explicit_query_receipt_id']=receipt['id'];m['explicit_query_input']=entries[0]
        hub=q['fixed_target'];channel=next(p.channel for p in s.world.interfaces if p.name==q['port']);entry=[channel.injection_site.x,channel.injection_site.y,channel.injection_site.z]
        def at(site):return exact_observation(s.world.runtime.observe(native.Coordinate(*site)))
        for tick in(1178,1179,1180,1181,1182):
            s.run_until(tick);frame={'tick':tick,'hub':at(hub),'entry':at(entry),
                'Moore27':[at(move(hub,(dx,dy,dz),1,131))for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)]}
            m['frames'].append(frame)
            if tick==1182:
                r=native.read_directional_response(s.world,native.Coordinate(*hub),receipt['id'],q['payload'],tick)
                m['native_readout']={'physical':exact_observation(r.physical),'receipt':exact_receipt(r.receipt),'coverage':bool(r.covered),
                    'value':r.value,'status':r.status,'provenance':'INSTRUMENTO_READS_NATIVE_PHYSICAL_RESPONSE','modality':q['modality']}
            checkpoint()
        save(1182)
        # Audit of old knowledge after all trajectories, never response input.
        late=[p for p in s.state['reads']if p['kind']=='lower'and p['tick']==1051]
        baseline_path=ROOT/'resultados/semantica/SOC_I21_SOCIAL_THEN_L01_REVISION/MEASUREMENTS.json';baseline=json.loads(baseline_path.read_text(encoding='utf8'))
        old={r['name']:r for p in baseline['native_readouts']if p['kind']=='lower'and p['tick']==658 for r in p['responses']}
        rows=[r for p in late for r in p['responses']];m['retention1051']={'read_after_final1182':True,'source':str(baseline_path.relative_to(ROOT)),
            'source_sha256':sha(baseline_path),'queries':len(rows),'covered':sum(r['coverage']for r in rows),
            'prior_covered':sum(r['coverage']for r in old.values()),'both_covered':sum(r['coverage']and old[r['name']]['coverage']for r in rows),
            'same_when_both_covered':sum(r['coverage']and old[r['name']]['coverage']and r['value']==old[r['name']]['value']for r in rows),'exact_readouts':late}
        m.update(status='MEASURED',new_requests=s.receipts()[old_count:],requests=s.receipts(),final_physical=physical(s.world),
            new_receipt_statuses=dict(Counter(r['receipt']['status']for r in s.receipts()[old_count:])),parent_file_preserved=sha(parent)==case['parent_sha256'])
    except BaseException as error:m.update(status='TECHNICAL_ERROR',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc());raise
    finally:checkpoint()
    print(json.dumps({'id':case['id'],'status':m['status'],'readout':m['native_readout'],'retention1051':{k:v for k,v in m['retention1051'].items()if k!='exact_readouts'},'elapsed_seconds':m['elapsed_seconds']}),flush=True)


if __name__=='__main__':main()
