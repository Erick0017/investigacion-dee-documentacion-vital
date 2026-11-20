"""Finite fresh native order/contact trials, exact data before interpretation."""
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
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from integracion.relational_pair import PairSession,physical,move
from dee_thinking import _native as d
from dee_thinking.consolidated import exact_observation,exact_receipt


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def put(path,value):
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()));temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)


def main():
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf8')
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases']if c['id']==a.case_id);a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    paths=(Path(__file__),ROOT/'src/integracion/relational_pair.py');source=a.out/'executed_source';source.mkdir()
    for path in paths:shutil.copyfile(path,source/path.name)
    import dee_thinking as dee
    if dee.__version__!='4.5.0'or not Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Isolated official4.5 required')
    s=PairSession.create(identifier=case['id'],actor_mode=case['actor_mode'],include_order=case['include_order'],include_contact=case['include_contact'],
        event_state_offset=case.get('event_state_offset',0),medium_load=case.get('medium_load',1),actor_state=case.get('actor_state',1))
    m={'schema':'CPC8R.relational_pair.measurements.v1','case':case,'configuration_sha256':sha(a.config),'source':{p.name:sha(p)for p in paths},
        'engine':{'version':dee.__version__,'module':dee.__file__,'native_sha256':sha(d.__file__),'python':sys.executable},'geometry':s.geometry,
        'preparations':1,'continuations':0,'diagnostic_forks':0,'host_RAW_clock_writes_on_MAIN':[],'frames':[],'windows':[],'snapshots':[],'status':'RUNNING'}
    def save(tick):
        path=a.out/('T'+str(tick)+'.deetsnap.gz');proof=s.save(path);m['snapshots'].append({'path':path.name,'tick':tick,'sha256':sha(path),'bytes':path.stat().st_size,'physical':physical(s.world),'storage':proof})
    def checkpoint():m.update(last_complete_tick=s.tick,elapsed_seconds=time.monotonic()-started,requests=s.receipts());put(a.out/'MEASUREMENTS.json',m)
    try:
        s.curriculum(order=case['order'],order_name=case['order_name'],contact_name=case['contact_name'],joint_name=case['joint_name'],
            include_order=case['include_order'],include_contact=case['include_contact'],extra_value=case['extra_value']);save(0);checkpoint()
        windows={5:[s.geometry['body']['emission'],s.geometry['contact_base']],9:[p['hub']for p in s.geometry['contact'].values()],11:[p['hub']for p in s.geometry['order'].values()],
            31:[p['query_site']for p in s.geometry['order'].values()],76:[p['query_site']for p in s.geometry['contact'].values()],82:[p['effect_site']for p in s.geometry['contact'].values()],
            143:[p['renewed_site']for p in s.geometry['contact'].values()],149:[p['renewed_effect']for p in s.geometry['contact'].values()],165:[p['query_site']for p in s.geometry['order'].values()],
            170:[s.geometry['auxiliary_hub']],206:[s.geometry['common_join']],210:[p['use_site']for p in s.geometry['joint_names'].values()],214:[p['delivery_site']for p in s.geometry['joint_names'].values()],281:[p['delivery_site']for p in s.geometry['joint_names'].values()]}
        boundaries={99,100}
        for tick in windows:boundaries.update((tick-1,tick))
        for tick in sorted(boundaries):
            s.run_until(tick);m['frames'].append(s.view())
            for target,centers in windows.items():
                if tick in(target-1,target):
                    for center in centers:m['windows'].append({'tick':tick,'nominal_stage':target,'center':center,'Moore27':[s.observe(move(center,(dx,dy,dz)))for dx in(-1,0,1)for dy in(-1,0,1)for dz in(-1,0,1)]})
            if tick in(11,82,170,206,214,281):save(tick)
            checkpoint()
        m.update(status='MEASURED',final_physical=physical(s.world),receipt_statuses=dict(Counter(x['receipt']['status']for x in s.receipts())),
            scope='Fresh exploratory component/coupling trial. Arrays/receipts before interpretation; no automatically assigned semantic mastery. Uncovered trajectory segments have no invented genealogy.')
    except BaseException as error:m.update(status='TECHNICAL_ERROR',error_type=type(error).__name__,error=str(error),traceback=traceback.format_exc());raise
    finally:checkpoint()
    def small(record):return{'raw':record['raw'],'load':record['s_reg'],'direction':record['direction'],'active':record['active']}
    frames={f['tick']:f for f in m['frames']}
    print(json.dumps({'id':case['id'],'status':m['status'],'order31':{k:small(v['query_site'])for k,v in frames[31]['order'].items()},
        'join206':small(frames[206]['common_join']),'names281':{k:small(v['delivery_site'])for k,v in frames[281]['joint'].items()},'receipts':m['receipt_statuses'],'seconds':m['elapsed_seconds']}),flush=True)


if __name__=='__main__':main()
