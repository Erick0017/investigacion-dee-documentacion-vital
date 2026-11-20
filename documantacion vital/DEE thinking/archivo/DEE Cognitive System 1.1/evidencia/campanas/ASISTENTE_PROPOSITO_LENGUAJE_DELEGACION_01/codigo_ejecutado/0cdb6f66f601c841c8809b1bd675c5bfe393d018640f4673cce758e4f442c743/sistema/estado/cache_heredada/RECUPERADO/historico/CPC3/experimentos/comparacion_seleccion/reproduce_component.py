"""Directed independent reproduction; never overwrites packaged evidence."""
from pathlib import Path
import argparse,json,sys,hashlib,time
from array import array


def signature(w):
    return {'tick':w.runtime.current_tick,
            'RAW':hashlib.sha256(array('Q',w.runtime.raw_copy()).tobytes()).hexdigest(),
            'clock':hashlib.sha256(array('Q',w.runtime.clock_copy()).tobytes()).hexdigest()}


def main():
    p=argparse.ArgumentParser();p.add_argument('--package-root',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    root=Path(a.package_root).resolve();out=Path(a.output).resolve()
    if out==root or root in out.parents:raise ValueError('Use an output outside the preserved package')
    out.mkdir(parents=True,exist_ok=True);sys.path.insert(0,str(root/'src'));start=time.monotonic()
    import dee_thinking as d
    from habitat.native_loop import NativeLoopSession
    from core.comparison_entity import CentralComparisonEntity
    session=NativeLoopSession.create(history='AB',consequence=-1,context=1,report=23,post_query=True)
    frames=[]
    for t in (37,47,56):session.run_until(t);frames.append(session.observe())
    session.save(out/'INFO56');restored=NativeLoopSession.load(out/'INFO56')
    restored.run_until(64);session.run_until(64);frames.append(restored.observe())
    assert signature(session.world)==signature(restored.world)
    reference=NativeLoopSession.load(root/'experimentos/comparacion_seleccion/post_information/AB/T64')
    fixture_equal=signature(restored.world)==signature(reference.world)
    entity=CentralComparisonEntity.create(initial_open=True,change_tick=80)
    entity.sense();emission=entity.predict();native_comparison=entity.compare()
    entity.save(out/'CENTRAL84.deetsnap');loaded=CentralComparisonEntity.load(out/'CENTRAL84.deetsnap')
    central_equal=entity.physical_digest()==loaded.physical_digest()
    # Observation is current physical data, not a response read from a fixture.
    live=loaded.observe()
    result={'version':d.__version__,'imported_module':d.__file__,'kernel':d.kernel_identity(),
            'elapsed_seconds':time.monotonic()-start,'frames':frames,
            'native_information_reuse_save_load_equal':True,'stored_reference_physical_equal':fixture_equal,
            'native_information_final':signature(restored.world),
            'central_emission':emission,'central_comparison':native_comparison,'central_current_after_load':live,
            'central_save_load_equal':central_equal,
            'fixture_usage':'Physical equality evaluation only; no fixture value enters an input or Native decoder',
            'operational_forks':0,'output_root':str(out)}
    (out/'REPRODUCTION.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({'native_information_reuse_save_load_equal':True,'stored_reference_physical_equal':fixture_equal,
                      'central_save_load_equal':central_equal,'output':str(out)}),flush=True)
    assert fixture_equal and central_equal


if __name__=='__main__':main()
