"""Supervised entry for finite fresh E1 and explicit question diagnostics."""
from __future__ import annotations
import argparse
from collections import Counter
import ctypes
from ctypes import wintypes
import hashlib
import json
import os
from pathlib import Path
import random
import shutil
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from shared_world import SharedSession,physical


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024**2),b''):h.update(b)
    return h.hexdigest()


def put(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+'.pending.'+str(os.getpid()))
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');os.replace(temp,path)


def peak_memory():
    try:
        class Counters(ctypes.Structure):
            _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(k,ctypes.c_size_t) for k in
                ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage')]
        c=Counters();c.cb=ctypes.sizeof(c);kernel=ctypes.WinDLL('kernel32');kernel.GetCurrentProcess.restype=wintypes.HANDLE
        query=ctypes.WinDLL('psapi').GetProcessMemoryInfo;query.argtypes=[wintypes.HANDLE,ctypes.c_void_p,wintypes.DWORD];query.restype=wintypes.BOOL
        if query(kernel.GetCurrentProcess(),ctypes.byref(c),c.cb):return int(c.PeakWorkingSetSize)
    except (OSError,AttributeError):pass
    return None


def execute(case,preparation,out,*,config_path,parent=None,diagnostic=None):
    import dee_thinking as dee
    from dee_thinking import _native
    out=Path(out);out.mkdir(parents=True,exist_ok=False);started=time.monotonic()
    if dee.__version__!='4.5.0' or not Path(dee.__file__).resolve().is_relative_to(Path(sys.prefix).resolve()):
        raise RuntimeError('Official isolated installed4.5 required')
    values=[random.Random(case['input_seed']+i*104729).choice((-1,1)) for i in range(preparation['count'])]
    snaps=[];frontiers=[]
    if parent is None:
        s=SharedSession.create(**preparation,identifier=case['id'])
        s.experience_order(case['history']);s.experience_own(case['own_values'],mode=case['own_mode'])
        s.experience_lower(values,range(32),0);s.query_lower(range(32),preparation['dimension'],9)
        s.action_resources();s.teach_name(case['name_mode']);s.query_name(payload=9)
    else:
        source=SharedSession.load(parent);parentbefore=physical(source.world)
        s=source.diagnostic_question(sham=diagnostic=='sham')
        if physical(source.world)!=parentbefore:raise AssertionError('Parent changed during diagnostic')
    identity={'version':dee.__version__,'module':dee.__file__,'native':_native.__file__,'native_sha256':sha(_native.__file__),
        'python':sys.executable,'implementation':'PUBLIC_NATIVE_REPERTOIRE_PLUS_DECLARED_RESEARCH_RECIPE'}
    m={'schema':'CPC8.integration.shared.measurements.v1','case':case,'preparation':preparation,'engine':identity,
        'configuration_sha256':sha(config_path),'code_sha256':sha(__file__),'source_sha256':sha(HERE/'shared_world.py'),
        'geometry':s.geometry,'individual':s.identifier,'preparations':int(parent is None),'diagnostic_forks':int(parent is not None),
        'parent':None if parent is None else {'snapshot_name':Path(parent).name,'snapshot_sha256':sha(parent),'mode':diagnostic},
        'input_values':values,'input_generator':'Independent per-index seeded synthetic directional events; seed/targets are never read by Session or physical decoder.',
        'snapshots':snaps,'frontiers':frontiers,'last_complete_tick':s.tick,'host_RAW_clock_writes_on_MAIN':[],'status':'RUNNING'}
    def save(tick):
        nonlocal m
        path=out/'checkpoints'/('T'+str(tick)+'.deetsnap.gz');path.parent.mkdir(parents=True,exist_ok=True)
        proof=s.save(path);snap={'tick':tick,'path':str(path.relative_to(out)),'sha256':sha(path),'bytes':path.stat().st_size,'storage':proof,'physical':physical(s.world)}
        snaps.append(snap);frontiers.append({'tick':tick,'physical':snap['physical'],'observations':s.observe()})
        m.update(last_complete_tick=s.tick,requests=s.receipts(),reads=deepcopy_reads(s),local_frames=s.state['frames'],elapsed_seconds=time.monotonic()-started,peak_memory_bytes=peak_memory())
        put(out/'MEASUREMENTS.json',m);print(json.dumps({'case':case['id'],'completed_tick':tick,'elapsed':m['elapsed_seconds']}),flush=True)
    if s.tick==0:save(0)
    if s.tick<5:
        s.run_until(5);s.actual(case['actual'])
    for tick in (20,s.geometry['ticks']['information'],s.geometry['ticks']['name_read']):
        if s.tick<tick:
            # Late new data are environmental inputs, not a lookup at query time.
            if s.tick<2*preparation['dimension']<tick:
                s.run_until(2*preparation['dimension']);s.experience_lower(values,range(32,preparation['count']),2*preparation['dimension'])
            s.run_until(tick);save(tick)
    if s.tick<=2*preparation['dimension']:
        s.run_until(2*preparation['dimension']);s.experience_lower(values,range(32,preparation['count']),2*preparation['dimension'])
    s.query_lower(range(preparation['count']),3*preparation['dimension'],9)
    s.run_until(3*preparation['dimension']+3);save(s.tick)
    if case['horizon']>=5*preparation['dimension']+3:
        s.query_lower(range(preparation['count']),5*preparation['dimension'],9)
        s.run_until(5*preparation['dimension']+3);save(s.tick)
    # Evaluator only, AFTER all native responses. This data does not return to MAIN.
    panels=[]
    for read in s.state['reads']:
        if read['kind']=='lower':
            old=[r for r in read['responses'] if int(r['name'][1:])<=32];new=[r for r in read['responses'] if int(r['name'][1:])>32]
            def counts(rows):return {'queries':len(rows),'applied':sum(r['receipt']['status']=='applied' for r in rows),
                'covered':sum(r['coverage'] for r in rows),'matches_exposed_value':sum(r['coverage'] and r['value']==values[int(r['name'][1:])-1] for r in rows)}
            panels.append({'tick':read['tick'],'old_without_reteaching':counts(old),'new':counts(new),'all':counts(read['responses'])})
    m.update(requests=s.receipts(),reads=deepcopy_reads(s),local_frames=s.state['frames'],
        calculations={'lower_panels':panels,'receipt_statuses':dict(Counter(q['receipt']['status'] for q in s.receipts()))},
        final_physical=physical(s.world),status='MEASURED',elapsed_seconds=time.monotonic()-started,peak_memory_bytes=peak_memory(),
        scope='Counts are physical correspondences and one finite own-memory/action/name integration. No65NSM accreditation, no transplanted state, no learned utility policy.')
    copy=out/'executed_source';copy.mkdir()
    for p in (Path(__file__),HERE/'shared_world.py'):shutil.copyfile(p,copy/p.name)
    put(out/'MEASUREMENTS.json',m);print(json.dumps({'case':case['id'],'status':'MEASURED','panels':panels,'elapsed':m['elapsed_seconds']}),flush=True)
    return m


def deepcopy_reads(session):
    # Public exact observations, not a response source for any later operation.
    return json.loads(json.dumps(session.state['reads']))


def main():
    p=argparse.ArgumentParser();p.add_argument('--config',type=Path,required=True);p.add_argument('--case-id',required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--parent',type=Path);p.add_argument('--diagnostic',choices=('cut','sham'))
    a=p.parse_args();cfg=json.loads(a.config.read_text(encoding='utf8'));case=next(c for c in cfg['cases'] if c['id']==a.case_id)
    if bool(a.parent)!=bool(a.diagnostic):p.error('Diagnostic requires explicit parent and mode together')
    execute(case,cfg['preparation'],a.out,config_path=a.config,parent=a.parent,diagnostic=a.diagnostic)


if __name__=='__main__':main()
