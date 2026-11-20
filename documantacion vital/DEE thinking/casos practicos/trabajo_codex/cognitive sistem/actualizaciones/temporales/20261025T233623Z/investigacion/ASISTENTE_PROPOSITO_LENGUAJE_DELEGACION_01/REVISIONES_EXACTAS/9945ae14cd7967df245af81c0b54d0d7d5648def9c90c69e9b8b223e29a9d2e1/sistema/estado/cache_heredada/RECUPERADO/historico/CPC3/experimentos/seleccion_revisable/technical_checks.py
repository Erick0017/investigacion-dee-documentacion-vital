"""Finite selection engineering checks and exact-state R14 reference port."""
import hashlib,json,sys
from array import array
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
import dee_thinking as d
from core.revisable_selection import A,B,SENSOR,NORMALIZER,PENALTY0,ACTION0,ACTION1,prepare
from core.comparison import plus,coordinate,observed,make_placement
def digest(w):return {'tick':w.runtime.current_tick,'raw':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),'clock':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}
def exact_r14():
    rows=[]
    for bit in (0,1):
        n=23;q=(10,10,10);ps=[make_placement(q,7,A,state=1,clock=11)]
        def put(target,t,dr,state,load):ps.append(make_placement(plus(target,dr,-t,n),load,dr,state=state,clock=0))
        t1=plus(q,A,1,n);put(t1,1,SENSOR,1001,47);t2=plus(t1,ACTION0,1,n);put(t2,2,NORMALIZER,1002,53)
        if bit:put(t2,2,PENALTY0,1003,59)
        ta=plus(t2,A,1,n);tb=plus(t2,B,1,n);put(ta,3,SENSOR,1004,101);put(tb,3,SENSOR,1005,103)
        r=d.OrganizationRecipe.research(n,ps,0);r.execution=d.TickOptions(d.Backend.LAZY,1);w=d.OrganizationalWorld.create(r);w.advance();a=observed(w.runtime.observe(coordinate(t1)));w.advance();p=observed(w.runtime.observe(coordinate(t2)));w.advance();pa=observed(w.runtime.observe(coordinate(ta)));pb=observed(w.runtime.observe(coordinate(tb)));rows.append({'bit':bit,'action':a,'policy':p,'probeP':pa,'probeQ':pb,'checks':{'first_action_direction':tuple(a['direction'])==ACTION0,'policy_direction':tuple(p['direction'])==(B if bit else A),'later_action_direction':tuple((pb if bit else pa)['direction'])==(ACTION1 if bit else ACTION0)},'source_exact_fields':'state1001...1005, sourceclocks0, policyclock11, original vectors/loads; only product Runtime/backend differ'})
    return rows
def main(root):
    folder=root/'experimentos/seleccion_revisable';tmp=folder/'technical';tmp.mkdir(parents=True,exist_ok=True);checks={};reference=exact_r14();checks['recovered_R14_exact_fields_directions']=all(all(x['checks'].values()) for x in reference)
    # Prepared-source context must not choose the first action from the host.
    a,ma=prepare(roles='P_INFORMATIVE',truth=1);b,mb=prepare(roles='Q_INFORMATIVE',truth=1);a.advance();b.advance();qa=a.view('selection').spec.ports['first_action'];qb=b.view('selection').spec.ports['first_action'];checks['same_first_native_action_before_evidence']=observed(a.runtime.observe(qa))==observed(b.runtime.observe(qb))
    before=digest(b)
    for _ in range(15):[b.runtime.observe(q) for q in b.view('selection').spec.ports.values()]
    checks['passive_observation_no_raw_clock_effect']=digest(b)==before
    f=b.fork();f.advance();checks['audit_fork_independent']=digest(b)==before
    # Persist a real, still-pending environmental input at absolute2.
    for tag in ('negative','positive'):b.submit('actual.'+tag+'.1',1,2)
    b.save_snapshot(str(tmp/'PENDING_ACTUAL_T1.deetsnap'));loaded=d.OrganizationalWorld.load_snapshot(str(tmp/'PENDING_ACTUAL_T1.deetsnap'));checks['save_load_physical_t1']=digest(loaded)==digest(b)
    b.run_until(15);loaded.run_until(15);checks['pending_receipts_and_future_survive_load']=digest(loaded)==digest(b)
    port=b.view('selection').spec.ports['negative_-1_Q_information'];final=observed(b.runtime.observe(port));loaded_final=observed(loaded.runtime.observe(loaded.view('selection').spec.ports['negative_-1_Q_information']));checks['restored_world_really_runs_through_information']=final==loaded_final and b.runtime.current_tick==15
    backend={}
    for name in ('DENSE_SEQUENTIAL','DENSE_PARALLEL','LAZY'):
        x=d.OrganizationalWorld.load_snapshot(str(tmp/'PENDING_ACTUAL_T1.deetsnap'));x.runtime.execution_options=d.TickOptions(getattr(d.Backend,name),1);x.run_until(15);backend[name]=digest(x)
    checks['Dense_Parallel_Lazy_same_future']=len({json.dumps(v,sort_keys=True) for v in backend.values()})==1
    result={'schema':1,'checks':checks,'all_technical_assertions':all(checks.values()),'exact_recovered_R14_reference':reference,'backend':backend,'initial_reference_deviation':'Earlier R14_REVALIDATION.json preserved the exact trajectory/direction recipe but normalized positive source states to1; this exact-fields check restores source states1001...1005 and confirms the reference without rerunning new scientific cases.','new_science_not_reexecuted':True};(folder/'TECHNICAL_CHECKS.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps({'checks':checks},ensure_ascii=True));assert all(checks.values())
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
