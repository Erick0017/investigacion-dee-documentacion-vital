"""Fresh alias-L17 trajectories; all comparisons occur after native evolution."""
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
from integracion.alias_lower import AliasSession
from integracion.shared_world import physical,move
from integracion.local_replay import windows
from dee_thinking import _native as native
from dee_thinking.consolidated import exact_observation


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()


def put(path,v):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+'.pending.'+str(os.getpid()))
    tmp.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf8');os.replace(tmp,path)


def execute(case,out,config,*,parent=None,diagnostic=None):
    import dee_thinking as d
    if d.__version__!='4.5.0' or not Path(d.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):raise RuntimeError('Isolated official4.5 required')
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic();snaps=[];frontiers=[];local=[];edits=[]
    values=[random.Random(case['input_seed']+i*104729).choice((-1,1)) for i in range(65)]
    values[16]=case['alias_value']  # A declared current teaching event, never a readout or old-state compensation.
    if parent is None:
        s=AliasSession.create(identifier=case['id']);s.experience_order(case['history'])
        s.expose_extra_right(case['extra_right']);s.expose_lower_first(values,alias_mode=case['alias_mode'])
        s.query_lower([i for i in range(32) if i!=16],131,9)
        s.action_resources();s.teach_name('paired');s.query_name(payload=9)
    else:
        original=AliasSession.load(parent);before=physical(original.world)
        candidates=[]
        for p in original.geometry['questions'].values():
            if p['dx']:
                q=move(p['site'],(p['dx'],0,0),1,131)
                candidates.append({'site':q,'before':exact_observation(original.world.runtime.observe(native.Coordinate(*q)))})
        s=original.diagnostic_question(sham=diagnostic=='sham')
        for q in candidates:q['after']=exact_observation(s.world.runtime.observe(native.Coordinate(*q['site'])))
        edits={'modality':'DIAGNOSTIC_FORK','tick':20,'fields':'RAW0 cut or identical RAW sham; clocks unchanged',
            'sites':candidates,'parent_physical':before,'parent_unchanged':physical(original.world)==before}
        if not edits['parent_unchanged']:raise AssertionError('Parent changed')
    m={'schema':'CPC8.integration.alias_L17.measurements.v1','case':case,'individual':s.identifier,
        'preparations':int(parent is None),'diagnostic_forks':int(parent is not None),'controlled_continuations':0,
        'engine':{'version':d.__version__,'module':d.__file__,'native_sha256':sha(native.__file__),'python':sys.executable},
        'configuration_sha256':sha(config),'executed_source':{p.name:sha(p) for p in (Path(__file__),SRC/'integracion/alias_lower.py',SRC/'integracion/shared_world.py',SRC/'integracion/local_replay.py')},
        'geometry':s.geometry,'input_values':values,'input_generator':'Preassigned synthetic current directional exposures; no target/seed is passed into Session or the physical decoder.',
        'diagnostic_edits':edits,'snapshots':snaps,'frontiers':frontiers,'local_windows':local,'status':'RUNNING',
        'host_RAW_clock_writes_on_MAIN':[],'last_complete_tick':s.tick}
    def save(tick):
        path=out/'checkpoints'/('T'+str(tick)+'.deetsnap.gz');path.parent.mkdir(parents=True,exist_ok=True)
        proof=s.save(path);f=physical(s.world)
        snaps.append({'tick':tick,'path':str(path.relative_to(out)),'sha256':sha(path),'bytes':path.stat().st_size,'storage':proof,'physical':f})
        frontiers.append({'tick':tick,'physical':f,'observation':s.observe()})
        m.update(last_complete_tick=tick,requests=s.receipts(),reads=s.state['reads'],local_frames=s.state['frames'],elapsed_seconds=time.monotonic()-started)
        put(out/'MEASUREMENTS.json',m);print(json.dumps({'case':case['id'],'completed_tick':tick,'elapsed':m['elapsed_seconds']}),flush=True)
    if s.tick==0:save(0)
    targets=(4,5,14,15,18,19,20,133,134,135,136,138,139,262,269,270,395,396,400,401,657,658,662,663)
    for tick in targets:
        if tick<=s.tick or tick>case['horizon']:continue
        s.run_until(tick)
        if tick==5:s.actual(case['actual'])
        if tick==262:s.experience_lower(values,range(32,65),262)
        local.extend(windows(s,tick))
        if tick in(400,401,662,663):
            for key,p in s.geometry['names'].items():
                local.append({'tick':tick,'target':'repeat.name.'+key,'center':p['site'],
                    'Moore27':[exact_observation(s.world.runtime.observe(native.Coordinate(*move(p['site'],(dx,dy,dz),1,131)))) for dx in(-1,0,1) for dy in(-1,0,1) for dz in(-1,0,1)],
                    'scope':'Repeated-sign local pre/post window; not unique ancestry.'})
        if tick in(20,134,270,396,401,658,663):save(tick)
        if tick==270:s.query_lower(range(65),393,9)
        if tick==396:
            s.query_name(at_tick=398,payload=9)
            if case['horizon']>=658:s.query_lower(range(65),655,9)
        if tick==658:s.query_name(at_tick=660,payload=9)
    panels=[]
    for read in s.state['reads']:
        if read['kind']=='lower':
            def count(rows):return {'queries':len(rows),'applied':sum(r['receipt']['status']=='applied' for r in rows),
                'covered':sum(r['coverage'] for r in rows),'matches_current_exposed_value':sum(r['coverage'] and r['value']==values[int(r['name'][1:])-1] for r in rows)}
            others=[r for r in read['responses'] if r['name']!='L17'];alias=[r for r in read['responses'] if r['name']=='L17']
            panels.append({'tick':read['tick'],'all':count(read['responses']),'other64_or_initial31':count(others),'alias_L17':alias})
    m.update(requests=s.receipts(),reads=s.state['reads'],local_frames=s.state['frames'],status='MEASURED',
        final_physical=physical(s.world),elapsed_seconds=time.monotonic()-started,
        calculations={'lower_panels':panels,'receipt_statuses':dict(Counter(q['receipt']['status'] for q in s.receipts()))},
        scope='Actual L17 is used by the native LEFT question. Its initial acquisition, subsequent uses, original-port access and later sign access are separate observations; no automatic sum as65integrated meanings.')
    copies=out/'executed_source';copies.mkdir()
    for p in (Path(__file__),SRC/'integracion/alias_lower.py',SRC/'integracion/shared_world.py',SRC/'integracion/local_replay.py'):shutil.copyfile(p,copies/p.name)
    put(out/'MEASUREMENTS.json',m);print(json.dumps({'case':case['id'],'status':'MEASURED','lower_panels':[{'tick':p['tick'],'all':p['all']} for p in panels]}),flush=True)
    return m


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--parent',type=Path);p.add_argument('--diagnostic',choices=('cut','sham'));a=p.parse_args()
    if bool(a.parent)!=bool(a.diagnostic):p.error('Explicit parent and diagnostic mode together required')
    c=json.loads(a.config.read_text(encoding='utf8'));case=next(q for q in c['cases'] if q['id']==a.case_id)
    execute(case,a.out,a.config,parent=a.parent,diagnostic=a.diagnostic)


if __name__=='__main__':main()
