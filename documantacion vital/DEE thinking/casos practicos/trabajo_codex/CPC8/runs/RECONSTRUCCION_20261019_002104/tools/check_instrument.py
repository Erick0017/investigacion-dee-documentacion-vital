"""Small real import, empty-Runtime, optional-session and persistence check."""
from array import array
import hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def digest(w):
    r=w.runtime
    return {'tick':int(r.current_tick),'RAW_sha256':hashlib.sha256(array('Q',r.raw_copy()).tobytes()).hexdigest(),
        'clocks_sha256':hashlib.sha256(array('Q',r.clock_copy()).tobytes()).hexdigest()}

def main():
    import dee_thinking as d
    from dee_thinking.persistence import save_world_snapshot,load_world_snapshot
    assert d.__version__=='4.5.0' and Path(d.__file__).is_relative_to(Path(sys.prefix))
    native_hash=hashlib.sha256(Path(d._native.__file__).read_bytes()).hexdigest()
    assert native_hash=='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
    empty=d.Runtime(11)
    assert not any(empty.raw_copy()) and not any(empty.clock_copy()) and empty.current_tick==0
    s=d.RepertoireSession.create(count=2)
    s.acquire('L01',-1,0);s.acquire('L02',1,0);s.run_until(3)
    first=s.query(['L01','L02'],67)
    path=ROOT/'checkpoints/instrument/pending.deetsnap.gz'
    proof=save_world_snapshot(s.world,path)
    restored,storage=load_world_snapshot(path,expected_sha256=proof['decoded_sha256'])
    before={'main':digest(s.world),'restored':digest(restored)}
    assert before['main']==before['restored']
    s.world.run_until(70);restored.run_until(70)
    after={'main':digest(s.world),'restored':digest(restored)}
    assert after['main']==after['restored']
    result={'schema':'CPC8.instrument-check.v1','status':'PASS','module':d.__file__,'native':d._native.__file__,
        'native_sha256':native_hash,'version':d.__version__,'build_info':d.build_info(),
        'direct_empty_Runtime_no_cognitive_inventory':True,'new_interfaces':[x for x in ('Runtime','OrganizationalWorld','RepertoireSession','IntegratedSession') if hasattr(d,x)],
        'snapshot':proof,'restored_storage':storage,'before':before,'after':after,
        'readout_at67':str(first),'scope':'Smoke/reference, not scientific replica or new CPC8 cognitive claim'}
    out=ROOT/'runtime/INSTALL_IDENTITY.json';out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'status':'PASS','version':d.__version__,'module':d.__file__,'snapshot_continued_to':70}))

if __name__=='__main__':main()
