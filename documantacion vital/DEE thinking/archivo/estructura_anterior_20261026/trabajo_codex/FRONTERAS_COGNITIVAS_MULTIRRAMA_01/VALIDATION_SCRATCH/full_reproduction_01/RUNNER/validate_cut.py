"""Exact technical equalities on measured interfaces; no cognitive scoring."""
import json,hashlib,shutil,sys,time,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as dt
from apparatus import schedule
from observations import *
from run_multibranch import technical,utc,WHEEL_SHA,PRODUCT_SHA,KERNEL_SHA

def operational(rt):
    return {'tick':rt.current_tick,'receipts':[receipt(x) for x in rt.receipts],
            'channels':list(rt.channel_names),'paused':rt.paused,'phase':rt.protocol_phase,
            'metadata':dict(rt.snapshot_metadata_entries)}

def equal(a,b):return state_equal(a,b) and operational(a)==operational(b)

def main(root):
    root=Path(root).resolve();begun=time.perf_counter();technical(root)
    windows=[];total_ticks=5*2+7*2+10*2+9*2*2
    for branch,name,filename,target in (('L02','paired_1','BEFORE_ACTION',19),
                                        ('L05','full','BEFORE_QUERY',20),('L08','full','BEFORE_QUERY',22)):
        path=root/f'CHECKPOINTS/{branch}/{name}/{filename}.deetsnap'
        a=dt.Runtime.load_snapshot(str(path));b=a.fork()
        b.execution_options=dt.TickOptions(dt.Backend.DENSE_SEQUENTIAL,1)
        if branch!='L02':
            for r in (a,b):schedule(r,[],'query',6,13,'probe')
        per_tick=[]
        while a.current_tick<target:
            a.advance();b.advance();total_ticks+=2
            same=equal(a,b);per_tick.append({'tick':a.current_tick,'raw_clock_operational_equal':same});assert same
        windows.append({'branch':branch,'checkpoint':str(path.relative_to(root)),'sha256':sha(path),
                        'ticks':per_tick,'last_hashes':full_hash(a),'queued_inputs_preserved_by_future':True,
                        'lazy_vs_dense':True})
    path=root/'CHECKPOINTS/L02/paired_1/BEFORE_ACTION.deetsnap'
    initial=dt.Runtime.load_snapshot(str(path));continuous=initial.fork()
    snap=root/'CHECKPOINTS/TECHNICAL/PENDING_INPUT_ROUNDTRIP.deetsnap';initial.save_snapshot(str(snap))
    restored=dt.Runtime.load_snapshot(str(snap));assert equal(continuous,restored)
    queued_roundtrip=[]
    for _ in range(13):
        continuous.advance();restored.advance();total_ticks+=2
        same=equal(continuous,restored);assert same
        queued_roundtrip.append({'tick':continuous.current_tick,'exact_raw_clock_channels_receipts_metadata':same})
    # Real bounded local accessibility check; both worlds evolve normally, no labels/input.
    hidden=[]
    origin=(15,15,15)
    local=[(origin[0]+dx,origin[1]+dy,origin[2]+dz) for dx in range(-2,3) for dy in range(-2,3) for dz in range(-2,3)]
    for hist in ('AB','BA','H0'):
        a=dt.Runtime.load_snapshot(str(root/f'CHECKPOINTS/L09/{hist}_hidden0/HIDDEN_WORLD_T0.deetsnap'))
        b=dt.Runtime.load_snapshot(str(root/f'CHECKPOINTS/L09/{hist}_hidden2/HIDDEN_WORLD_T0.deetsnap'))
        frames=[]
        for rel in range(9):
            ar=[record(a.observe(c(q))) for q in local];br=[record(b.observe(c(q))) for q in local]
            frames.append({'relative_tick':rel,'equal_local_raw_and_uint64_clock':ar==br})
            if rel<8:a.advance();b.advance();total_ticks+=2
        hidden.append({'history':hist,'region':'origin + [-2,2]^3, inclusive; 125 sites',
                       'frames':frames,'coverage':'Only this local interface and 0..8; not global indistinguishability.'})
    snapshots=[];indexed=0
    for directory in (root/'BRANCHES',root/'COMBINATIONS'):
        for p in directory.rglob('MEASUREMENTS.json'):
            m=json.loads(p.read_text(encoding='utf-8'))
            for item in m['checkpoints']:
                q=root/item['path'];assert sha(q)==item['sha256']
                loaded=dt.Runtime.load_snapshot(str(q));assert loaded.current_tick==item['tick']
                indexed+=1
                if item['label'] in ('FINAL','CALIBRATION_FINAL'):
                    snapshots.append({'path':item['path'],'tick':loaded.current_tick,'sha256':sha(q),
                                      'dimension':loaded.dimension,'snapshot_loaded':True,
                                      'channels':list(loaded.channel_names),'receipt_count':len(loaded.receipts)})
    wheel=next((root/'SHARED_TOOLS').glob('*.whl'));assert sha(wheel)==WHEEL_SHA
    package=Path(dt.__file__).resolve().parent
    wheel_files=[]
    with zipfile.ZipFile(wheel) as z:
        for name in z.namelist():
            if name.startswith('dee_thinking/') and not name.endswith('/'):
                rel=Path(name).relative_to('dee_thinking');installed=package/rel
                if installed.is_file():
                    expected=hashlib.sha256(z.read(name)).hexdigest();actual=sha(installed)
                    assert expected==actual,name
                    wheel_files.append({'member':name,'installed_path':str(installed),'sha256':actual,'byte_exact':True})
    assert any(x['member'].endswith('.pyd') for x in wheel_files)
    dee=root.parents[1]
    originals={'wheel':dee/'3.0'/wheel.name,'product':dee/'archivo/DEE_thinking_3_0_0_ENTREGA_FINAL_RESULTADOS.zip'}
    assert sha(originals['wheel'])==WHEEL_SHA and sha(originals['product'])==PRODUCT_SHA
    assert sha(root/'SHARED_TOOLS/product_reference/source/src/kernel_v27.cpp')==KERNEL_SHA
    size=sum(p.stat().st_size for p in root.rglob('*') if p.is_file())
    disk=shutil.disk_usage(root)
    report={'verified_utc':utc(),'baseline_file':'SHARED_TOOLS/TECHNICAL_CHECKS.json',
            'backend_windows':windows,'queued_save_load_future':queued_roundtrip,
            'hidden_local_prefix':hidden,'all_indexed_snapshots_verified':indexed,
            'final_snapshots':snapshots,'installed_product_files_exact':wheel_files,
            'original_assets_unchanged':True,'validation_ticks_executed':total_ticks,
            'technical_elapsed_seconds':time.perf_counter()-begun,
            'resource_measurements':{'world_dimensions':[31,34,47],'basic_buffers_bytes_by_N':{str(n):32*n**3 for n in (31,34,47)},
                'working_files_total_bytes':size,'disk_free_bytes':disk.free,'used_native_threads':1,'max_simultaneous_processes_used':1},
            'scope':'Exact technical checks only. Local-prefix observations do not demonstrate selection of informative action.'}
    dump(root/'SHARED_TOOLS/CUT_VALIDATION.json',report)
    print(json.dumps({'indexed_snapshots_verified':indexed,'backend_windows':len(windows),'technical_ticks':total_ticks,
                      'elapsed_seconds':report['technical_elapsed_seconds'],'installed_native_exact':True},indent=2))

if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
