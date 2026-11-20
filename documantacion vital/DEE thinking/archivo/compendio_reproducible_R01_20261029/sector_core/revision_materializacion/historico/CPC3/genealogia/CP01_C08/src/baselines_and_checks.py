"""Small conventional comparisons and proportional technical/causal checks."""
import ctypes
from ctypes import wintypes
import json
from pathlib import Path
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as d
from laboratorio import *
from sesion import Session
from supervision import atomic_json


class Memory(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('faults',wintypes.DWORD),*[(n,ctypes.c_size_t) for n in ('peak','current','qpp','qp','qnp','qn','page','pagepeak')]]


def memory():
    k=ctypes.WinDLL('kernel32');p=ctypes.WinDLL('psapi');k.GetCurrentProcess.restype=wintypes.HANDLE;p.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Memory),wintypes.DWORD]
    m=Memory();m.cb=ctypes.sizeof(m)
    if not p.GetProcessMemoryInfo(k.GetCurrentProcess(),ctypes.byref(m),m.cb):return None
    return {'working_set_bytes':m.current,'process_peak_working_set_bytes':m.peak}


def main(root):
    e=CaseEvidence(root,'VALIDACION_DIRIGIDA',{'known_witnesses_not_new_scientific_replicates':True,'bounded_parameters':[34,47,127],'baseline_information':'same admitted synthetic event values; no learned result provided to native execution'})
    baselines=[]
    qlist=[0,1,3,17,31]
    for teacher in (12,16):
        start=time.perf_counter();offset=None
        # Conventional single-reference zero-origin calibration, explicit.
        offset=teacher;outputs=[q+offset for q in qlist];seconds=time.perf_counter()-start
        before=memory();start=time.perf_counter();w,rs=learned_mobile((teacher,teacher),cue=0);queries=[mobile_query(w,q,protocol='b'+str(q))[0] for q in qlist];elapsed=time.perf_counter()-start
        measured=[p['responses'][0]['s_reg'] if p['responses'][0]['active'] else None for p in queries]
        baselines.append({'task':'zero-origin calibration','reference':teacher,'queries':qlist,'conventional':outputs,'native':measured,'same_task_outputs':outputs==measured,
                          'conventional_seconds_one_tiny_run':seconds,'native_prepare_and_5_independent_queries_seconds':elapsed,'N':34,'basic_buffers_bytes':32*34**3,'process_memory_before':before,'process_memory_after':memory(),'native_response_latency_ticks':5,'conventional_state_variables':1})
    fsm=[]
    for h in ['AB','BA','ABBA','BAAB']:
        start=time.perf_counter();first=None
        for x in h:
            if first is None:first=x
        fsm.append({'history':h,'classification':first,'seconds_one_tiny_run':time.perf_counter()-start,'variables':1})
    passive=Session.create(slots=8);passive.experience(0,12,16);passive.advance_to(6);plain=passive.fork();tr=d.TraceSession();tr.sample_budget=32;tr.sites={'learned0':passive.world.view('q0').spec.ports['response']};passive.world.set_trace(tr)
    passive.signal('s0',0);plain.signal('s0',0);passive.advance_to(11);plain.advance_to(11);assert physical(passive.world)==physical(plain.world)
    before=physical(passive.world)
    for _ in range(5):passive.observe()
    assert physical(passive.world)==before
    variants=[]
    for backend in [d.Backend.LAZY,d.Backend.DENSE_SEQUENTIAL,d.Backend.DENSE_PARALLEL]:
        x=Session.create(slots=8);x.world.runtime.execution_options=d.TickOptions(backend,2 if backend==d.Backend.DENSE_PARALLEL else 1);x.experience(0,12,16);x.advance_to(6);x.signal('s0',0);x.advance_to(11);variants.append(physical(x.world))
    assert variants[0]==variants[1]==variants[2]
    # Save pending physical inputs AND external habitat/protocol state.
    pending=Session.create(slots=8,feedback=True);pending.experience(0,12,16);pending.advance_to(6);pending.signal('s0',0);pending.save(e.folder/'C08_PENDING_BEFORE_SIGNAL.deetsnap')
    restored=Session.load(e.folder/'C08_PENDING_BEFORE_SIGNAL.deetsnap');pending.advance_to(21);restored.advance_to(21)
    assert physical(pending.world)==physical(restored.world) and pending.state==restored.state
    # C06's named return point must be inspected at the actual arrival time.
    w=d.create_organization('contingent',history=d.BasalHistory.AB);site=w.view('body').spec.ports['return'];events=[];last=0;cut=None
    for rel in range(1,51):
        w.run_until(32+rel);o=w.runtime.observe(site)
        if o.raw!=last:events.append(reading(o))
        if cut is None and o.record.state>0 and o.record.semantic!=4:
            cut=w.diagnostic_fork([],True);cut=edit_fork(w,site,0,'late removal of observed actual return');cut_at=32+rel;cut_record=reading(o)
        last=o.raw
    if cut:
        cut.run_until(w.runtime.current_tick);fullq,ff=body_probe(w);cutq,cc=body_probe(cut);late_return={'cut_tick':cut_at,'events':events,'actual_record_removed':cut_record,'full_response':fullq,'cut_response':cutq,'scope':'one actual return-site cut; the test does not assert all return paths removed'}
    else:late_return={'events':events,'status':'NO_ACTIVE_RETURN_AT_DECLARED_POINT_IN_WINDOW'}
    e.json('BASELINE_COMPARISONS.json',{'calibration':baselines,'FSM':fsm,'no_industrial_performance_claim':True})
    return e.finish({'baselines':baselines,'passive_tracking_RAW_clock_equal':True,'repeated_observation_passive':True,'Dense_Lazy_Parallel_equal':True,'pending_session_save_load_same_future':True,
                     'late_native_return':late_return,'C06_loop_adaptation_not_assumed':True})


if __name__=='__main__':print(json.dumps({'status':main(sys.argv[1])['status']},indent=2))
