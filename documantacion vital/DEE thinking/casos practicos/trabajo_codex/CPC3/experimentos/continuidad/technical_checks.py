"""Directed tests only: observation, segmentation, snapshots and backend windows."""
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from core.entity import Entity,atomic_json
import dee_thinking as d

def history():
    e=Entity.create();e.sense();e.predict();return e
def progress(e,segmented=False,end=600):
    for t in (163,292,554):
        if t>end:break
        if segmented:
            while e.tick<t:e._advance_to(min(t,e.tick+7))
        else:e._advance_to(t)
        p=e.habitat.sample();e._input('A' if p['arrived'] else 'B',t,{'kind':'ACTUAL_OBSERVED_PACKET','past':p})
    e._advance_to(end)
    return e.physical_digest()
def main(root):
    out=root/'experimentos/continuidad/TECHNICAL_CHECKS.json';tmp=root/'checkpoints/continuidad/technical';tmp.mkdir(parents=True,exist_ok=True);rows={};e=history()
    before=e.physical_digest()
    for _ in range(25):e.observe()
    rows['passive_observer_raw_clock_unchanged']=e.physical_digest()==before
    f=e.world.fork();f.advance(8);rows['diagnostic_fork_independence']=e.physical_digest()==before
    e.save(tmp/'MID_T37.deetsnap');l=Entity.load(tmp/'MID_T37.deetsnap');rows['save_load_initial_physical']=l.physical_digest()==before
    rows['save_load_protocol_state']=l.reader_primed and l.past_pair_presented and l.slot_index==e.slot_index and l.habitat.export()==e.habitat.export()
    d1=progress(e,False);d2=progress(l,True);rows['segmentation_and_save_load_same_future']=d1==d2
    e.save(tmp/'MID_T600.deetsnap');l=Entity.load(tmp/'MID_T600.deetsnap');l.event_sink=root/'experimentos/continuidad/TECHNICAL_PREDICTIONS.jsonl'
    em=l.predict(30);rows['restored_new_query_uses_current_MAIN']=em['emission_tick']==600 and em['target_tick']==630 and em['physical_output']==l.observe()['physical_output'] and em['modality']=='PASSIVE_OBSERVATION_OF_RENEWED_MAIN_OUTPUT'
    ev=l.advance(30);rows['restored_future_really_advanced']=l.tick==630 and any(x['target_tick']==630 for x in ev['evaluations'])
    backend={}
    for name in ('DENSE_SEQUENTIAL','LAZY','DENSE_PARALLEL'):
        x=Entity.load(tmp/'MID_T37.deetsnap');opts=d.TickOptions();opts.backend=getattr(d.Backend,name);opts.threads=1;x.world.runtime.execution_options=opts;x._advance_to(65);backend[name]=x.physical_digest()
    rows['Dense_Lazy_Parallel_window_equal']=len({json.dumps(x,sort_keys=True) for x in backend.values()})==1
    # Metadata persistence performs no RAW/clock mutation, but the calls are logged.
    x=history();h=x.physical_digest();x.save(tmp/'AUDITED_METADATA.deetsnap');rows['metadata_not_physical_write']=x.physical_digest()==h
    rows['metadata_calls_actually_recorded']=any(c['operation']=='set_snapshot_metadata' for c in x.operation_calls) and any(c['operation']=='save_snapshot' for c in x.operation_calls)
    result={'checks':rows,'all_technical_assertions':all(rows.values()),'backend_windows':backend,'restored_emission':em,'restored_evaluations':ev['evaluations'],'operational_write_audit':x.operation_calls,'source_variants':{'confirmation':'src/core/entity_before_metadata_audit.py','current':'src/core/entity.py','difference':'adds explicit non-RAW metadata/save operation records only; physical evolution unchanged'},'time_axes':'absolute Runtime tick, local centre clock=t_abs+228, wall-clock separate'}
    atomic_json(out,result);print(json.dumps({'checks':rows,'all':all(rows.values())},ensure_ascii=True));assert all(rows.values())
if __name__=='__main__':main(Path(sys.argv[1]) if len(sys.argv)>1 else ROOT)
