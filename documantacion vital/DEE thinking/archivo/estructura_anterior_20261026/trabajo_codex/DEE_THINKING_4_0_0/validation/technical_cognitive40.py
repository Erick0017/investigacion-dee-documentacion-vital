"""Bounded public-API technical checks; no new scientific apparatus/fitting."""
import argparse
from array import array
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
import time
import zlib

def put(p,x):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);q=p.with_suffix(p.suffix+'.tmp');q.write_text(json.dumps(x,indent=2,default=str),encoding='utf-8');os.replace(q,p)

def physical(w):
    r=w.runtime;raw=array('Q',r.raw_copy()).tobytes();clock=array('Q',r.clock_copy()).tobytes()
    return struct.pack('<QQ',r.current_tick,r.dimension)+raw+clock

def worker(a):
    import dee_thinking as d
    import dee_thinking._native as native
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    evidence={};checks={};started=time.monotonic()
    if a.worker=='backend':
        execution=d.TickOptions();execution.backend=getattr(d.Backend,a.backend);execution.threads=2 if a.backend=='DENSE_PARALLEL' else 1
        def create(profile):
            p=d.CognitiveParameters();p.seed_path=d.reference_seed_path();p.profile=profile;p.execution=execution
            return d.CognitiveSession.create(p)
        e=create('continuity');before=physical(e.world)
        for _ in range(20):e.observe()
        checks['passive_prestate_equal']=physical(e.world)==before
        e.sense();e.predict();evidence['continuity37']=physical(e.world)
        c=create('comparison');traced=c.fork()
        tr=d.TraceSession();spec=traced.world.view('body').spec
        tr.sites={'a':spec.a,'b':spec.b,'reader':spec.comparator};tr.sample_budget=12
        traced.world.set_trace(tr);traced.world.capture_trace()
        for s in (c,traced):s.sense();s.predict();s.compare()
        checks['trace_on_off_equal']=physical(c.world)==physical(traced.world)
        checks['trace_budget_exact']=len(traced.world.trace().samples)==12
        checks['trace_budget_did_not_stop_runtime']=traced.tick==84 and traced.world.trace().capture_stopped
        before=physical(c.world)
        for _ in range(20):c.observe()
        checks['passive_poststate_equal']=physical(c.world)==before
        evidence['comparison84']=physical(c.world)
        ap=d.NativeAssociationParameters();ap.execution=execution
        assoc=d.NativeAssociationSession.create(ap);assoc.train([7,11]);assoc.query_panel(13)
        evidence['association11']=physical(assoc.world)
    else:
        # This child must use the already installed native4 package. The C++
        # executable is supervised independently by the parent below.
        e=d.CognitiveSession.load_snapshot(a.input)
        if a.worker=='bridge_python':
            checks['cpp_pending_tick37']=e.tick==37
            checks['cpp_metadata_present']=e.get_interface_metadata('cross_language')=='cpp_pending'
            e.advance(1) # Real native evolution in Python before C++ resumes.
            e.set_interface_metadata('cross_language_python','pending_native_tick38')
            e.save_snapshot(a.destination)
            checks['python_pending_tick38']=e.tick==38
            e.compare();evidence['python_direct84']=physical(e.world)
            expected=e.observe()['comparison_live']['presentation']
            checks['python_direct_comparison_measured']=expected=='discrepancia_direccional'
        else:
            checks['cpp_resumed_to84']=e.tick==84
            checks['python_metadata_survived_cpp']=e.get_interface_metadata('cross_language_python')=='pending_native_tick38'
            checks['comparison_not_reused_as_forecast']=e.predict()['status']=='OUTSIDE_FORECAST_DOMAIN'
            evidence['cpp_resumed84']=physical(e.world)
            e.advance(1);checks['after_cross_language_native_continue85']=e.tick==85
    states={}
    for k,b in evidence.items():
        p=out/(k+'.state.zlib');p.write_bytes(zlib.compress(b,9));states[k]={'file':p.name,'sha256':hashlib.sha256(b).hexdigest()}
    result={'worker':a.worker,'backend':a.backend,'checks':checks,'states':states,
            'python':sys.executable,'native_module':native.__file__,
            'native_binary_sha256':hashlib.sha256(Path(native.__file__).read_bytes()).hexdigest(),
            'elapsed_seconds':time.monotonic()-started}
    put(out/'RESULTS.json',result)
    if not all(checks.values()):raise AssertionError(result)

def run(a):
    root=Path(a.root).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
    spec=importlib.util.spec_from_file_location('supervise40',root/'supervise40.py');sup=importlib.util.module_from_spec(spec);spec.loader.exec_module(sup)
    script=str(Path(__file__).resolve());jobs=[]
    def job(name,argv):
        j=sup.run(root,name+'_'+str(int(time.time())),argv,timeout=240,cwd=str(out));jobs.append(j)
        if j['exit_code']!=0:raise RuntimeError(j)
    for backend in ('DENSE_SEQUENTIAL','DENSE_PARALLEL','LAZY'):
        dest=out/backend
        if not (dest/'RESULTS.json').exists():job('cognitive_technical_'+backend,[a.python_new,'-I','-B',script,'--root',str(root),'--output',str(dest),'--worker','backend','--backend',backend])
    results={b:json.loads((out/b/'RESULTS.json').read_text()) for b in ('DENSE_SEQUENTIAL','DENSE_PARALLEL','LAZY')}
    equal={}
    for case in ('continuity37','comparison84','association11'):
        states=[zlib.decompress((out/b/results[b]['states'][case]['file']).read_bytes()) for b in results]
        equal[case]=states[0]==states[1]==states[2]
    with tempfile.TemporaryDirectory(prefix='dt40-cognitive-bridge-') as scratch:
        scratch=Path(scratch);cpp=scratch/'cpp_pending.deetsnap';python=scratch/'python_pending.deetsnap';finished=scratch/'cpp_finished.deetsnap'
        import dee_thinking as d
        job('cognitive_bridge_cpp_write',[a.cpp_executable,'--write-pending',d.reference_seed_path(),str(cpp)])
        job('cognitive_bridge_python',[a.python_new,'-I','-B',script,'--root',str(root),'--output',str(out/'bridge_python'),'--worker','bridge_python','--input',str(cpp),'--destination',str(python)])
        job('cognitive_bridge_cpp_continue',[a.cpp_executable,'--continue',str(python),str(finished)])
        job('cognitive_bridge_check',[a.python_new,'-I','-B',script,'--root',str(root),'--output',str(out/'bridge_check'),'--worker','bridge_check','--input',str(finished)])
        for p in (cpp,python,finished):(out/p.name).write_bytes(p.read_bytes())
    direct=zlib.decompress((out/'bridge_python'/'python_direct84.state.zlib').read_bytes())
    crossed=zlib.decompress((out/'bridge_check'/'cpp_resumed84.state.zlib').read_bytes())
    checks={'dense_parallel_lazy_full_state_equal':all(equal.values()),'cpp_python_cpp_full_state_equal':direct==crossed}
    result={'technical_checks':checks,'backend_equality':equal,'backends':results,'jobs':jobs,
            'scope':'public native4 sessions only; technical replicas, not new scientific cases'}
    put(out/'TECHNICAL_CHECKS.json',result)
    if not all(checks.values()):raise AssertionError(result)
    print(json.dumps(result))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);p.add_argument('--output',required=True)
    p.add_argument('--python-new');p.add_argument('--cpp-executable');p.add_argument('--worker',choices=['backend','bridge_python','bridge_check'])
    p.add_argument('--backend',default='LAZY');p.add_argument('--input');p.add_argument('--destination');a=p.parse_args()
    worker(a) if a.worker else run(a)
