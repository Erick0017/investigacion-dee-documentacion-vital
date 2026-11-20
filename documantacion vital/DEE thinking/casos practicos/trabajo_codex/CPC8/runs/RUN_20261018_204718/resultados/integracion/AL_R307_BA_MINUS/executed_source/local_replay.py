"""Deterministic T0 continuation with additional passive Moore-27 telemetry.

Original MEASUREMENTS are read only after evolution. The added observer never
selects inputs or writes cells; all scientific source files remain unchanged.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import random
import sys
import time
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from shared_world import SharedSession,move,physical
from run_shared import put,sha
from dee_thinking import _native as native
from dee_thinking.consolidated import exact_observation


def windows(s,tick):
    g=s.geometry;t=g['ticks'];targets={}
    if tick in(4,5):targets['body.emission']=g['body']['emission']
    if tick in(14,15):targets.update({'comparison.'+k:q for k,q in g['comparison_hubs'].items()})
    if tick in(18,19):targets.update({'question.'+k:p['site'] for k,p in g['questions'].items()})
    if tick in(t['information']-1,t['information']):targets.update({'own.'+k:p['hub'] for k,p in g['own_banks'].items()})
    if tick in(t['action']-1,t['action']):targets.update({'action.'+k:p['site'] for k,p in g['actions'].items()})
    if tick in(t['association']-1,t['association'],t['name_read']-1,t['name_read']):targets.update({'name.'+k:p['site'] for k,p in g['names'].items()})
    n=g['N']
    if tick in(n+2,n+3,3*n+2,3*n+3,5*n+2,5*n+3):
        targets.update({'sampled.lower.'+g['lower_forms'][i]['name']:g['lower_forms'][i]['hub'] for i in(0,16,31,32,64) if i<g['K']})
    return [{'tick':tick,'target':name,'center':q,'Moore27':[exact_observation(s.world.runtime.observe(native.Coordinate(*move(q,(dx,dy,dz),1,n))))
        for dx in(-1,0,1) for dy in(-1,0,1) for dz in(-1,0,1)],
        'scope':'Exact passive local pre/post window; not unique particle ancestry and not the whole causal history.'} for name,q in targets.items()]


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True)
    p.add_argument('--initial',type=Path,required=True);p.add_argument('--reference',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(q for q in cfg['cases'] if q['id']==a.case_id)
    s=SharedSession.load(a.initial)
    if s.tick!=0:raise ValueError('This directed replay requires the stored T0 operational state')
    n=s.geometry['N'];values=[random.Random(case['input_seed']+i*104729).choice((-1,1)) for i in range(s.geometry['K'])]
    frames=[physical(s.world)];local=[]
    for tick in range(1,case['horizon']+1):
        s.run_until(tick)
        if tick==5:s.actual(case['actual'])
        if tick==2*n:s.experience_lower(values,range(32,s.geometry['K']),2*n)
        local.extend(windows(s,tick))
        if tick in(20,s.geometry['ticks']['information'],s.geometry['ticks']['name_read'],3*n+3,5*n+3):frames.append(physical(s.world))
        if tick==s.geometry['ticks']['name_read']:s.query_lower(range(s.geometry['K']),3*n,9)
        if tick==3*n+3 and case['horizon']>=5*n+3:s.query_lower(range(s.geometry['K']),5*n,9)
    # Reference inspection is an audit after the new native trajectory ends.
    ref=json.loads(a.reference.read_text(encoding='utf8'));bytick={q['physical']['tick']:q['physical'] for q in ref['frontiers']}
    comparisons=[{'tick':q['tick'],'full_RAW_clocks_tick_equal':q==bytick[q['tick']]} for q in frames]
    actual=[{k:v for k,v in q.items() if k!='origin'} for q in s.receipts()]
    old=[{k:v for k,v in q.items() if k!='origin'} for q in ref['requests']]
    result={'schema':'CPC8.integration.passive_local_replay.v1','case_id':case['id'],
        'continuations':1,'independent_preparations':0,'scientific_replicates_added':0,
        'initial_snapshot_sha256':sha(a.initial),'reference_sha256':sha(a.reference),
        'observer_sha256':sha(__file__),'participant_source_sha256':sha(HERE/'shared_world.py'),
        'config_sha256':sha(a.config),'comparisons':comparisons,'full_receipts_and_call_ticks_equal':actual==old,
        'Moore27_windows':local,'readings':s.state['reads'],'final_physical':physical(s.world),
        'observer_writes_to_MAIN':[],'elapsed_seconds':time.monotonic()-started,
        'coverage_gaps':'Unlisted sites/ticks are not traced locally. Full states at original frontiers plus exact code/inputs permit directed re-evolution; no missing encounters are invented.'}
    result['technical_status']='PASS' if all(q['full_RAW_clocks_tick_equal'] for q in comparisons) and actual==old else'FAIL'
    put(a.out/'MEASUREMENTS.json',result);print(json.dumps({'status':result['technical_status'],'windows':len(local),'comparisons':comparisons}))
    if result['technical_status']!='PASS':raise SystemExit(1)


if __name__=='__main__':main()
