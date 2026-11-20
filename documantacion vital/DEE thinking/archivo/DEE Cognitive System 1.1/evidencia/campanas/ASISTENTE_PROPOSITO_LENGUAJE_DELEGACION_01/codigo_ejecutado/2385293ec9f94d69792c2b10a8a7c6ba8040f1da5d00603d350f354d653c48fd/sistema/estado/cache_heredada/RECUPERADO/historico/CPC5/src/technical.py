"""Finite technical comparisons; no scientific repetitions counted here."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))

from common import identity, put, digest, operational, receipt
from network import geometry, interfaces_for, protocol, NetworkWorld, observe

ROOT = Path(__file__).resolve().parents[1]


def state(world):
    value = operational(world)
    # save_snapshot adds its own serialization envelope, not physical inputs.
    value['metadata'] = {k:v for k,v in value['metadata'].items()
                         if not k.startswith('dee_thinking.organizational.')}
    return {'physical': digest(world), 'operative': value}


def build(backend):
    import dee_thinking as d
    case={'id':'TECHNICAL_NATIVE_CHAIN4','N':67,'chains':[4], 'query':13}
    spec=geometry(case)
    recipe=d.OrganizationRecipe.research(67, [], 0)
    recipe.interfaces=interfaces_for(spec)
    recipe.execution=d.TickOptions(backend, 1 if backend != d.Backend.DENSE_PARALLEL else 2)
    world=d.OrganizationalWorld.create(recipe)
    ids=[]
    for item in protocol(case,spec):
        ids.append(world.submit(item['channel'],item['load'],item['tick']).id)
    return world,spec,ids


def continue_worker(snapshot, output):
    import dee_thinking as d
    identity()
    world=d.OrganizationalWorld.load_snapshot(str(snapshot))
    before=state(world)
    world.run_until(31)
    result={'before':before, 'after':state(world),
            'readout':observe(world,(35,38,8)),
            'provenance':'Separate process; restored real physical world and pending inputs'}
    put(output,result)
    return result


def suite(output):
    import dee_thinking as d
    if output.exists(): raise FileExistsError('Protected completed or partial technical run')
    output.mkdir(parents=True)
    started=time.monotonic()
    engine=identity()
    runs={}; world=None; spec=None
    for label,backend in [('Lazy',d.Backend.LAZY),('DenseSequential',d.Backend.DENSE_SEQUENTIAL),('DenseParallel2',d.Backend.DENSE_PARALLEL)]:
        t=time.monotonic(); candidate,geometry_,ids=build(backend)
        candidate.run_until(31)
        runs[label]={'state':state(candidate),'elapsed_seconds':time.monotonic()-t,
                     'readouts': [observe(candidate,s['first_meeting']) for s in geometry_['stages']],
                     'receipts':[receipt(candidate,i) for i in ids]}
        put(output/'INCREMENTAL.json',{'engine':engine,'backend_runs':runs})
        if label=='Lazy': world,spec=candidate,geometry_
    backend_equal=all(row['state']['physical']==runs['Lazy']['state']['physical'] for row in runs.values())
    backend_operative_equal=all(row['state']['operative']==runs['Lazy']['state']['operative'] for row in runs.values())
    plain, spec, ids=build(d.Backend.LAZY)
    traced,_,_=build(d.Backend.LAZY)
    trace=d.TraceSession(); trace.sample_budget=8
    trace.sites={'hub':d.Coordinate(*spec['stages'][0]['hub']),
                 'first_encounter':d.Coordinate(*spec['stages'][0]['first_meeting'])}
    traced.set_trace(trace)
    windows=[]
    for tick in (0,1,2,3,6,8,10,11,16,21,26,31):
        plain.run_until(tick); traced.run_until(tick)
        before=digest(traced)
        traced.capture_trace()
        passive=digest(traced)==before
        windows.append({'tick':tick,'physical_equal':digest(plain)==digest(traced),
                        'capture_no_mutation':passive,'sample_count':len(traced.trace().samples),
                        'capture_stopped':traced.trace().capture_stopped})
    traced.trace().export_trace(str(output/'TRACE_BUDGET.json'))
    main_before=state(world)
    fork=world.fork(); fork_initial_equal=state(fork)==main_before
    extra=fork.submit('stage0.cue',7,35)
    fork.run_until(39)
    fork_isolated=state(world)==main_before and fork.runtime.current_tick==39
    fork_receipt=receipt(fork,extra.id)
    pending,_,pendingids=build(d.Backend.LAZY)
    pending.run_until(3)
    snapshot=output/'PENDING_QUERY_T3.deetsnap'
    pending.save_snapshot(str(snapshot))
    pending_state=state(pending)
    # The query requested for t6 is still in Runtime's real queue at t3.
    pending_receipts=[receipt(pending,i) for i in pendingids]
    pending.run_until(31)
    expected=state(pending)
    command=[sys.executable,'-B',str(Path(__file__).resolve()),'continue',
             '--snapshot',str(snapshot),'--output',str(output/'OTHER_PROCESS.json')]
    completed=subprocess.run(command,timeout=180,capture_output=True,text=True)
    (output/'OTHER_PROCESS_STDOUT.txt').write_text(completed.stdout,encoding='utf-8')
    (output/'OTHER_PROCESS_STDERR.txt').write_text(completed.stderr,encoding='utf-8')
    if completed.returncode: raise RuntimeError('Separate continuation exited '+str(completed.returncode))
    child=json.loads((output/'OTHER_PROCESS.json').read_text(encoding='utf-8'))
    result={'kind':'TECHNICAL_VALIDATION_NOT_SCIENTIFIC_SAMPLE','engine':engine,
        'configuration':{'N':67,'chains':[4],'initial_tick':0,'horizon':31,'passive_trace_budget':8},
        'backend_runs':runs,'backend_RAW_clock_tick_equal':backend_equal,
        'backend_receipts_channels_equal':backend_operative_equal,
        'passive_windows':windows,'trace_budget_does_not_stop_world':traced.runtime.current_tick==31,
        'fork_initial_operational_physical_equal':fork_initial_equal,'fork_parent_unchanged':fork_isolated,
        'fork_only_new_input_receipt':fork_receipt,
        'pending_queue_before_snapshot':pending_receipts,
        'other_process_command':command,'other_process_exit_code':completed.returncode,
        'other_process_snapshot_equal':pending_state==child['before'],
        'other_process_future_physical_equal':expected['physical']==child['after']['physical'],
        'other_process_future_operative_equal':expected['operative']==child['after']['operative'],
        'elapsed_seconds':time.monotonic()-started,
        'scope':'Exact comparison of RAW, clocks, tick and external operative state. Serializer internal envelope is reported separately from user metadata.'}
    put(output/'TECHNICAL_CHECKS.json',result)
    assert backend_equal and backend_operative_equal and all(x['physical_equal'] and x['capture_no_mutation'] for x in windows)
    assert fork_initial_equal and fork_isolated and result['other_process_snapshot_equal']
    assert result['other_process_future_physical_equal'] and result['other_process_future_operative_equal']
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['suite','continue'])
    p.add_argument('--output',type=Path,required=True);p.add_argument('--snapshot',type=Path)
    a=p.parse_args()
    result=suite(a.output) if a.mode=='suite' else continue_worker(a.snapshot,a.output)
    print(json.dumps({'mode':a.mode,'completed':True,'result':str(a.output)}))

if __name__=='__main__':main()
