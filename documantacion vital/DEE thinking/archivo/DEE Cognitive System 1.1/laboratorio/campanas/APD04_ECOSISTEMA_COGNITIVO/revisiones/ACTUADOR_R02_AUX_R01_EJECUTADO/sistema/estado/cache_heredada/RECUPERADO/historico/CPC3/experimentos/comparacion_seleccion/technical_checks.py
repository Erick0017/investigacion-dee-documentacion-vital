"""Only technical booleans: observer, backend, snapshot and information cut."""
from pathlib import Path
import argparse,sys,json,hashlib,time
from array import array


def signature(w):
    return {'tick':w.runtime.current_tick,
            'RAW':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),
            'clock':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',required=True);a=p.parse_args()
    root=Path(a.root).resolve();sys.path.insert(0,str(root/'src'))
    import dee_thinking as d
    from habitat.native_loop import prepare_native_loop,decode_current_state
    out=root/'experimentos/comparacion_seleccion/technical';out.mkdir(parents=True,exist_ok=True)
    start=time.monotonic();spec=dict(history='AB',consequence=-1,context=1)
    def drive(w,m,stop):
        while w.runtime.current_tick<stop:
            t=w.runtime.current_tick
            if t in (32,33):w.submit('sensor.'+('A' if t==32 else 'B'),0,t)
            if t==34:w.probe('read.offaxis',7,t)
            if t==m['arrival_tick']-4:
                for tag in ('negative','positive'):w.submit('observed_consequence.'+tag,17,t)
            w.advance()
        return w
    w,m=prepare_native_loop(**spec);drive(w,m,47);pre=signature(w)
    reads=[decode_current_state(w,m) for _ in range(10)]
    observation_passive=signature(w)==pre
    w.save_snapshot(str(out/'MID47.deetsnap'));restored=d.OrganizationalWorld.load_snapshot(str(out/'MID47.deetsnap'))
    drive(w,m,63);drive(restored,m,63);continuation=signature(w)==signature(restored)
    reference=d.OrganizationalWorld.load_snapshot(str(root/'experimentos/comparacion_seleccion/native_discovery/AB_changed/FINAL.deetsnap'))
    trace_on_off=signature(w)==signature(reference)
    equalities={}
    for backend in (d.Backend.DENSE_SEQUENTIAL,d.Backend.DENSE_PARALLEL):
        b,bm=prepare_native_loop(**spec);b.runtime.execution_options=d.TickOptions(backend,1);drive(b,bm,63)
        equalities[str(backend)]=signature(b)==signature(w)
    # Future consequence fields in inert interface declarations do not enter
    # physical history before a real report is submitted. Context and all
    # source inventory are held fixed for this contrast.
    a0,am=prepare_native_loop(history='AB',consequence=1,context=1)
    a1,bm=prepare_native_loop(history='AB',consequence=-1,context=1)
    drive(a0,am,37);drive(a1,bm,37);future_cut=signature(a0)==signature(a1)
    result={'version':d.__version__,'kernel':d.kernel_identity(),'native_module':d.build_info(),
            'passive_observer_repeated':observation_passive,'trace_on_off_same_future':trace_on_off,
            'direct_save_load_same_future':continuation,'backend_equalities':equalities,
            'future_consequence_inert_before_submission':future_cut,
            'readouts_at47':reads[:1],'physical_final':signature(w),
            'elapsed_seconds':time.monotonic()-start,
            'scope':'Technical equivalence; no scientific global success/failure judgement'}
    (out/'TECHNICAL_CHECKS.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result),flush=True)
    assert observation_passive and trace_on_off and continuation and future_cut and all(equalities.values())


if __name__=='__main__':main()
