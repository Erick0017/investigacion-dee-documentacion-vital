"""Proportional engine/observer/persistence checks, not new scientific samples."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from common import ROOT,identity,put,digest,operational,receipt,record,sha
from order_stream import prepare

def state(w):
    op=operational(w);op['metadata']={k:v for k,v in op['metadata'].items() if not k.startswith('dee_thinking.organizational.')}
    return {'physical':digest(w),'operative':json.loads(json.dumps(op))}

def build(backend='LAZY'):
    w,s=prepare({'backend':backend});ids=[]
    for port,load,t,probe in [('event.A',3,0,False),('event.B',3,1,False),('order.read',7,2,True)]+[(f'name.{b}',5,12,False) for b in ('left','right')]+[(f'query.{b}',5,t,True) for t in (22,89) for b in ('left','right')]+[(f'context.{b}.plus',3,32,False) for b in ('left','right')]:
        ids.append((w.probe if probe else w.submit)(port,load,t).id)
    return w,s,ids

def continuation(snapshot,out):
    import dee_thinking as d
    w=d.OrganizationalWorld.load_snapshot(str(snapshot));before=state(w);w.run_until(100)
    put(out,{'before':before,'after':state(w),'origin':'Technical other-process continuation without original training files'})

def suite(out):
    import dee_thinking as d
    out=Path(out);out.mkdir(parents=True,exist_ok=False);start=time.monotonic();engine=identity();runs={}
    for b in ('LAZY','DENSE_SEQUENTIAL','DENSE_PARALLEL'):
        w,s,ids=build(b);w.run_until(35);runs[b]={'state':state(w),'query':{k:record(w,q) for k,q in s['query_sites'].items()},'context':{k:record(w,q) for k,q in s['context_sites'].items()}}
        put(out/'PROGRESS.json',{'backends':runs})
    equal=all(x['state']==runs['LAZY']['state'] for x in runs.values())
    plain,s,_=build();observed,_,_=build();tr=d.TraceSession();tr.sample_budget=12;tr.sites={'A':d.Coordinate(*s['A']),'named_right':d.Coordinate(*s['query_sites']['right'])};observed.set_trace(tr)
    passive=[]
    for t in (0,2,4,15,16,24,25,34,35,92,100):
        plain.run_until(t);observed.run_until(t);before=digest(observed)
        for _ in range(3):observed.capture_trace();record(observed,s['A'])
        passive.append({'tick':t,'equal_RAW_clocks':digest(plain)==digest(observed),'observations_inert':digest(observed)==before,'trace_count':len(observed.trace().samples),'capture_stopped':observed.trace().capture_stopped})
    observed.trace().export_trace(str(out/'TRACE.json'))
    w,s,ids=build();w.run_until(16);snapshot=out/'PENDING_AT_T16.deetsnap';w.save_snapshot(str(snapshot));before=state(w)
    w.run_until(100);expected=state(w)
    argv=[sys.executable,'-I','-B',str(Path(__file__).resolve()),'continue','--snapshot',str(snapshot),'--output',str(out/'OTHER_PROCESS.json')]
    child=subprocess.run(argv,capture_output=True,text=True,timeout=180);(out/'CHILD_STDOUT.log').write_text(child.stdout,encoding='utf-8');(out/'CHILD_STDERR.log').write_text(child.stderr,encoding='utf-8');assert child.returncode==0
    loaded=json.loads((out/'OTHER_PROCESS.json').read_text(encoding='utf-8'))
    parent=state(w);fork=w.fork();initial_equal=state(fork)==parent;extra=fork.probe('query.left',9,156).id;fork.run_until(159)
    isolation=state(w)==parent
    invalid=[]
    for port,value,t in [('unknown',5,100),('query.left',-1,100),('query.left',5,99)]:
        pre=state(w)
        try:r=w.probe(port,value,t);item={'port':port,'value':value,'tick':t,'receipt':receipt(w,r.id),'raised':False}
        except Exception as e:item={'port':port,'value':value,'tick':t,'raised':True,'type':type(e).__name__}
        item['physical_unchanged']=state(w)['physical']==pre['physical'];invalid.append(item)
    result={'schema':'CPC5.extension.technical.v1','kind':'TECHNICAL_NOT_SCIENTIFIC_SAMPLE','engine':engine,
            'backend_runs':runs,'backend_full_physical_operative_equal':equal,'passive_windows':passive,
            'trace_budget_preserves_world_advance':observed.runtime.current_tick==100,
            'save_load_other_process_command':argv,'other_process_exit_code':child.returncode,
            'other_process_before_equal':before==loaded['before'],'other_process_after_equal':expected==loaded['after'],
            'deep_fork_initial_equal':initial_equal,'fork_MAIN_unchanged':isolation,'fork_new_receipt':receipt(fork,extra),
            'invalid_inputs':invalid,'snapshot_sha256':sha(snapshot),'elapsed_seconds':time.monotonic()-start,
            'normalization':'Only framework serialization envelope metadata is omitted from operative comparison; physical arrays never normalized.'}
    put(out/'TECHNICAL_CHECKS.json',result)
    assert equal and all(x['equal_RAW_clocks'] and x['observations_inert'] for x in passive)
    assert result['other_process_before_equal'] and result['other_process_after_equal'] and initial_equal and isolation
    assert all(x['physical_unchanged'] for x in invalid)
    print(json.dumps({'technical':'VERIFIED','elapsed_seconds':result['elapsed_seconds']}),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['suite','continue']);p.add_argument('--output',type=Path,required=True);p.add_argument('--snapshot',type=Path);a=p.parse_args()
    suite(a.output) if a.mode=='suite' else continuation(a.snapshot,a.output)
