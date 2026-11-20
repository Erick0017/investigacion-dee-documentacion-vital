"""A bounded continuation of the exact SOC_I21 MAIN, never a fresh body.

All new inputs are frozen current events or explicit external read requests.
The hypothesis is that unused native opportunities may return after6N.
No state inspection selects stimuli, timing, route, decoder, or rescues.
"""
import argparse
from collections import Counter
from copy import deepcopy
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
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);temp=path.with_name(path.name+'.pending.'+str(os.getpid()))
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)


def execute(case,out,config_path):
    config=json.loads(config_path.read_text(encoding='utf8'));parent=ROOT/config['parent_snapshot']
    if sha(parent)!=config['parent_sha256']:raise AssertionError('Parent identity mismatch; no continuation launched')
    out.mkdir(parents=True,exist_ok=False);started=time.monotonic();source=out/'executed_source'
    shutil.copytree(ROOT/config['parent_source'],source/'src');shutil.copyfile(__file__,source/'longitudinal_native.py')
    source_hashes={p.relative_to(source).as_posix():sha(p) for p in source.rglob('*.py')}
    sys.path.insert(0,str(source/'src'))
    import dee_thinking as dee
    from dee_thinking import _native as native
    from dee_thinking.consolidated import exact_observation
    from comunicacion.social_channel import SocialSession
    from integracion.shared_world import physical,move
    if dee.__version__!='4.5.0' or not Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise AssertionError('Isolated official4.5 required')
    s=SocialSession.load(parent);entry_physical=physical(s.world);entry_requests=s.receipts();request_start=len(entry_requests)
    if s.tick!=690:raise AssertionError('Exact690 frontier required')
    result={'schema':'CPC8.integration.longitudinal690.measurements.v1','case':case,'hypothesis':config['hypothesis'],
        'parent':{'path':config['parent_snapshot'],'sha256':sha(parent),'individual':s.identifier,'physical':entry_physical},
        'configuration_sha256':sha(config_path),'executed_source':source_hashes,'preparations':0,'continuations':1,'diagnostic_forks':0,
        'trajectory_role':'PILOT_MAIN_CONTINUATION' if case['role'].startswith('PILOT')else'CONTROLLED_CONTINUATION_FROM_SAME_PARENT',
        'engine':{'version':dee.__version__,'module':dee.__file__,'native_sha256':sha(native.__file__),'python':sys.executable},
        'geometry':s.geometry,'resources_actual':{'N':int(s.world.runtime.dimension),'interfaces':len(s.world.interfaces),'initial_material_sites':len(s.world.recipe.placements)},
        'initial_request_count':request_start,'initial_requests':entry_requests,'initial_protocols':deepcopy(s.state['queries']),
        'initial_social_protocols':deepcopy(s.state.get('social_queries',[])),
        'host_RAW_clock_writes_on_MAIN':[],'new_interfaces':[],'new_material_placements':[],'new_inputs':[],
        'frames':[],'snapshots':[],'status':'RUNNING','last_complete_tick':690}
    def save(tick):
        target=out/('T'+str(tick)+'.deetsnap.gz');proof=s.save(target)
        result['snapshots'].append({'tick':tick,'path':target.name,'sha256':sha(target),'bytes':target.stat().st_size,'physical':physical(s.world),'storage':proof})
    def checkpoint():
        result.update(last_complete_tick=s.tick,requests=s.receipts(),elapsed_seconds=time.monotonic()-started)
        put(out/'MEASUREMENTS.json',result)
    save(690);checkpoint()
    try:
        entries=[]
        if case['new_order']is not None:
            entries.extend({'port':'event.'+event,'payload':3,'tick':786+i,'origin':'NEW_CURRENT_ORDER_EVENT'}for i,event in enumerate(case['new_order']))
        entries.append({'port':'order.read','payload':7,'tick':788,'kind':'probe','origin':'EXPLICIT_EXTERNAL_ORDER_QUERY'})
        if case['right_cue']:entries.append({'port':'U.right.signal','payload':5,'tick':786,'origin':'NEW_OPAQUE_RIGHT_CUE'})
        entries.append({'port':'U.right.event.minus','payload':11,'tick':786,'origin':'NEW_CURRENT_RIGHT_DIRECTIONAL_EVENT'})
        entries.extend({'port':'need.actual.'+lane+'.-1','payload':17,'tick':797,'origin':'CURRENT_SENSOR_REPORT_FIXED_CODEC'}for lane in('left','right'))
        result['new_inputs']=entries;s.stimulate(entries)
        # This panel occurs after every hypothesis window; no re-teaching.
        s.query_lower(range(65),1048,9)
        centers={'emission':[s.geometry['body']['emission']],
            'comparison':list(s.geometry['comparison_hubs'].values()),
            'question':[p['site']for p in s.geometry['questions'].values()],
            'own_information':[p['hub']for p in s.geometry['own_banks'].values()],
            'action':[p['site']for p in s.geometry['actions'].values()],
            'social_acquisition':[p['hub']for p in s.geometry['social']['parts'].values()],
            'B_query':[p['query_site']for p in s.geometry['social']['parts'].values()],
            'B_use':[p['effect_site']for p in s.geometry['social']['parts'].values()],
            'delivery':[q for p in s.geometry['social']['parts'].values()for q in p['delivery_sites'].values()]}
        windows=config['hypothesis']['predicted_windows'];boundaries={786,787,788,797,1048,1050,1051}
        for target in windows.values():boundaries.update((target-1,target))
        def at(q):return exact_observation(s.world.runtime.observe(native.Coordinate(*q)))
        for tick in sorted(boundaries):
            s.run_until(tick);frame={'tick':tick,'observation':s.observe(),'expected_window':None,'local_windows':[]}
            for label,target in windows.items():
                if tick in(target-1,target):
                    frame['expected_window']=label
                    for center in centers[label]:
                        frame['local_windows'].append({'center':center,'Moore27':[at(move(center,(dx,dy,dz),1,131))for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)]})
            result['frames'].append(frame)
            if tick in(805,926,952,1051):save(tick)
            checkpoint()
        # The participant has finished before this evaluator reads the parent measurements.
        baseline=json.loads((ROOT/config['parent_measurements']).read_text(encoding='utf8'))
        old={x['name']:x for q in baseline['native_readouts']if q['kind']=='lower'and q['tick']==658 for x in q['responses']}
        reads=[q for q in s.state['reads']if q['kind']=='lower'and q['tick']==1051]
        retention=[]
        for panel in reads:
            for response in panel['responses']:
                previous=old.get(response['name']);retention.append({'name':response['name'],
                    'previous658_covered':None if previous is None else previous['coverage'],'previous658_value':None if previous is None else previous['value'],
                    'read1051':response,'same_when_both_covered':None if previous is None or not previous['coverage']or not response['coverage']else previous['value']==response['value']})
        result.update(status='MEASURED',final_physical=physical(s.world),requests=s.receipts(),new_requests=s.receipts()[request_start:],
            new_reads=reads,retention_reference={'path':config['parent_measurements'],'sha256':sha(ROOT/config['parent_measurements']),'read_after_final_tick':s.tick},
            retention=retention,calculations={'new_receipt_statuses':dict(Counter(x['receipt']['status']for x in s.receipts()[request_start:])),
                'covered1051':sum(x['read1051']['coverage']for x in retention),'previous658_covered':sum(bool(x['previous658_covered'])for x in retention),
                'both_covered':sum(x['same_when_both_covered']is not None for x in retention),'both_covered_same_value':sum(x['same_when_both_covered']is True for x in retention)},
            parent_file_preserved=sha(parent)==config['parent_sha256'],coverage='Pre/post Moore27 at frozen sites and stages; other intervals are not assigned unique lineage.')
    except BaseException as error:
        result.update(status='TECHNICAL_ERROR',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc())
        raise
    finally:checkpoint()
    print(json.dumps({'case':case['id'],'status':result['status'],'calculations':result['calculations'],'elapsed_seconds':result['elapsed_seconds']}),flush=True)


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    config=json.loads(a.config.read_text(encoding='utf8'));execute(next(c for c in config['cases']if c['id']==a.case_id),a.out,a.config)


if __name__=='__main__':main()
