"""Longitudinal lower learning, native L17 use, then selective L01 revision."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import sys
import time
SRC=Path(__file__).resolve().parents[1];sys.path.insert(0,str(SRC))
from integracion.revision_lower import RevisableRelocatedSession
from integracion.shared_world import physical,move
from integracion.local_replay import windows
from dee_thinking import _native as native
from dee_thinking.consolidated import exact_observation


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()


def put(path,value):
    path=Path(path);tmp=path.with_name(path.name+'.pending.'+str(os.getpid()))
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(tmp,path)


def neighborhood(world,q):
    return [exact_observation(world.runtime.observe(native.Coordinate(*move(q,(dx,dy,dz),1,131)))) for dx in(-1,0,1) for dy in(-1,0,1) for dz in(-1,0,1)]


def execute(case,out,config,reference=None):
    import dee_thinking as d
    if d.__version__!='4.5.0' or not Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Isolated official4.5 required')
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    values=[random.Random(case['input_seed']+i*104729).choice((-1,1)) for i in range(65)]
    values[0]=case['old_L01'];values[16]=case['alias_value']
    s=RevisableRelocatedSession.create(identifier=case['id']);s.experience_order(case['history'])
    s.expose_extra_right(case['extra_right']);s.expose_lower_first(values,alias_mode=case['alias_mode'])
    s.query_lower([i for i in range(32) if i!=16],131,9)
    s.action_resources();s.teach_name('paired');s.query_name(payload=9)
    snapshots=[];frontiers=[];local=[]
    source_paths=[Path(__file__),SRC/'integracion/revision_lower.py',SRC/'integracion/relocated_lower.py',SRC/'integracion/alias_lower.py',SRC/'integracion/shared_world.py',SRC/'integracion/local_replay.py']
    m={'schema':'CPC8.integration.revision_L01.measurements.v1','case':case,'individual':s.identifier,'preparations':1,'diagnostic_forks':0,'controlled_continuations':0,
        'engine':{'version':d.__version__,'module':d.__file__,'native_sha256':sha(native.__file__),'python':sys.executable},
        'configuration_sha256':sha(config),'executed_source':{p.name:sha(p) for p in source_paths},'geometry':s.geometry,'input_values':values,
        'future_current_consequence':'The current_L01 event is a predeclared external exposure, never derived by reading or correcting the old response.',
        'snapshots':snapshots,'frontiers':frontiers,'local_windows':local,'last_complete_tick':0,'status':'RUNNING','host_RAW_clock_writes_on_MAIN':[]}
    def save(tick):
        path=out/'checkpoints'/('T'+str(tick)+'.deetsnap.gz');path.parent.mkdir(parents=True,exist_ok=True);storage=s.save(path);f=physical(s.world)
        snapshots.append({'tick':tick,'path':str(path.relative_to(out)),'sha256':sha(path),'bytes':path.stat().st_size,'storage':storage,'physical':f})
        frontiers.append({'tick':tick,'physical':f,'observation':s.observe()});m.update(last_complete_tick=tick,requests=s.receipts(),reads=s.state['reads'],local_frames=s.state['frames'],elapsed_seconds=time.monotonic()-started)
        put(out/'MEASUREMENTS.json',m);print(json.dumps({'case':case['id'],'completed_tick':tick,'elapsed':m['elapsed_seconds']}),flush=True)
    save(0)
    targets=(4,5,14,15,18,19,20,133,134,135,136,138,139,262,269,270,395,396,400,401,523,524,525,526,527,528,657,658,662,663)
    for tick in targets:
        s.run_until(tick)
        if tick==5:s.actual(case['actual'])
        if tick==262:s.experience_lower(values,range(32,65),262)
        if tick==524:s.revise_l01(case['current_L01'],mode=case['revision_mode'])
        local.extend(windows(s,tick))
        if tick in(523,524,525,526,527,528,657,658):
            hub=s.geometry['lower_forms'][0]['hub'];local.append({'tick':tick,'target':'revision.L01','center':hub,'Moore27':neighborhood(s.world,hub),
                'scope':'Exact declared revised target neighborhood; no ancestry beyond covered window is assumed.'})
        if tick in(400,401,662,663):
            for key,p in s.geometry['names'].items():local.append({'tick':tick,'target':'repeat.name.'+key,'center':p['site'],'Moore27':neighborhood(s.world,p['site'])})
        if tick in(20,134,270,396,401,523,527,658,663):save(tick)
        if tick==270:s.query_lower(range(65),393,9)
        if tick==396:s.query_name(at_tick=398,payload=9);s.query_lower(range(65),655,9)
        if tick==658:s.query_name(at_tick=660,payload=9)
    panels=[]
    for read in s.state['reads']:
        if read['kind']=='lower':
            expected=list(values)
            if read['tick']>=658 and case['revision_mode']=='treatment':expected[0]=case['current_L01']
            def counts(rows):return {'queries':len(rows),'applied':sum(r['receipt']['status']=='applied' for r in rows),'covered':sum(r['coverage'] for r in rows),
                'matches_declared_current_or_retained_consequence':sum(r['coverage'] and r['value']==expected[int(r['name'][1:])-1] for r in rows)}
            panels.append({'tick':read['tick'],'all':counts(read['responses']),'L01':[r for r in read['responses'] if r['name']=='L01'],
                'other64':counts([r for r in read['responses'] if r['name']!='L01'])})
    comparisons=[]
    if reference:
        # Audit only, after all native experiences and outputs have finished.
        baseline=json.loads(Path(reference).read_text(encoding='utf8'));old={p['tick']:p['physical'] for p in baseline['frontiers']}
        comparisons=[{'tick':p['tick'],'full_RAW_clocks_tick_equal':p['physical']==old[p['tick']]} for p in frontiers if p['tick']<=401 and p['tick'] in old]
        m['baseline_before_revision']={'path_name':Path(reference).name,'sha256':sha(reference),'comparisons':comparisons,
            'scope':'Inert extra interfaces/metadata may differ; initial and evolving physical states are compared exactly.'}
    m.update(status='MEASURED',requests=s.receipts(),reads=s.state['reads'],local_frames=s.state['frames'],final_physical=physical(s.world),elapsed_seconds=time.monotonic()-started,
        calculations={'panels':panels,'receipt_statuses':dict(Counter(q['receipt']['status'] for q in s.receipts()))},
        scope='One fixed4.5M1 experience protocol within the same Research MAIN, after new learning and native use. No learned update policy,65NSM claim or forced valid response.')
    copies=out/'executed_source';copies.mkdir()
    for p in source_paths:shutil.copyfile(p,copies/p.name)
    put(out/'MEASUREMENTS.json',m);print(json.dumps({'case':case['id'],'status':'MEASURED','L01_final':[r for p in panels if p['tick']==658 for r in p['L01']],'elapsed':m['elapsed_seconds']}),flush=True)
    return m


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--reference',type=Path)
    a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));execute(next(c for c in cfg['cases'] if c['id']==a.case_id),a.out,a.config,a.reference)


if __name__=='__main__':main()
