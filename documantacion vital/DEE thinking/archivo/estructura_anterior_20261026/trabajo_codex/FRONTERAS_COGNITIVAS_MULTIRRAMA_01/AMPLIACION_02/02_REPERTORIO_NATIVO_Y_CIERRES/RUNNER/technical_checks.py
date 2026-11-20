"""Narrow native regression and deterministic checks; not a product-wide suite."""
import argparse,hashlib,json,sys,time,zipfile,tempfile,subprocess
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import dee_thinking as dt
from apparatus import *
from observers import *
from run_extension_02 import Context,read,utc,verify,SECTION,WHEEL_SHA

def preflight(root):
    spec={'front':'P01','id':'technical_reference','work_type':'B','role':'reference','modality':'EXPERIENCE_PROTOCOL','level':'technical'}
    ctx=Context(root,spec);timer=time.perf_counter();w=c6_pair();rt=ctx.track(w.runtime)
    assert dt.__version__=='3.0.0'
    for i,e in enumerate((7,11)):
        ctx.schedule(rt,w.qualified_channel(f'l{i}','cue'),0,5 if i==0 else 9)
        ctx.schedule(rt,w.qualified_channel(f'l{i}','teacher'),0,e)
    ctx.to(rt,6)
    old=ctx.parent_runtime('CHECKPOINTS/L01/paired/BEFORE_QUERY.deetsnap')
    assert state_equal(rt,old),'adapted reference RAW/clock differs from inherited reference'
    dense=ctx.track(rt.fork());dense.execution_options=dt.TickOptions(dt.Backend.DENSE_SEQUENTIAL,1)
    observed=ctx.track(rt.fork());plain=ctx.track(rt.fork())
    refs=(rt,dense,observed,plain)
    for f in refs:
        for j in range(2):ctx.schedule(f,w.qualified_channel(f'q{j}','query'),6,13,'probe')
    pending=ctx.cp(rt,'REFERENCE_WITH_PENDING_QUERY')
    loaded=ctx.track(dt.Runtime.load_snapshot(str(Path(root)/pending['path'])))
    before=full_hash(plain)
    mutated=ctx.edit(plain,(1,1,1),dt.pack_record(1,4,1,0,0,1),label='isolated_fork_test')
    assert full_hash(plain)==before and not state_equal(mutated,plain)
    for t in range(6,12):
        for f in (rt,dense,observed,plain,loaded):ctx.to(f,t)
        panel(observed,{'left':(10,18,8),'right':(10,18,24)})
        full_hash(observed)
    assert all(state_equal(rt,f) for f in (dense,observed,plain,loaded))
    historic=ctx.parent_runtime('CHECKPOINTS/L01/paired/FINAL.deetsnap')
    # The inherited final horizon can differ; only the explicitly shared window is compared.
    if historic.current_tick==rt.current_tick:assert state_equal(rt,historic)
    assert [site(rt,(10,18,z))['s_reg'] for z in (8,24)]==[25,33]
    result={'library_version':dt.__version__,'kernel_identity':str(dt.kernel_identity()),
            'adapted_reference_equal_RAW_clock':True,'dense_lazy_equal_RAW_clock':True,
            'passive_observation_equal_RAW_clock':True,'save_load_pending_queue_equal_future':True,
            'fork_isolation':True,'responses_at_tick11':[site(rt,(10,18,z)) for z in (8,24)],
            'elapsed_seconds':time.perf_counter()-timer,'completed_utc':utc()}
    ctx.cp(rt,'FINAL_REFERENCE');ctx.finish({'technical_checks':result,'phi':None})
    dump(Path(root)/'ANALYSIS/TECHNICAL_PREFLIGHT.json',result)
    print(json.dumps(result,indent=2))

def decisive_windows(root):
    root=Path(root);temp=Path(tempfile.mkdtemp(prefix='dee_a02_tech_'))
    windows=[('P03','context_full','T131',202),('P14','phase_transient','MAIN_FINAL',44),
             ('P14','phase_ablation','MAIN_FINAL',44),('P06','distributed_HA','T8',12)]
    reports=[]
    for front,case,label,end in windows:
        m=read(root/'BRANCHES'/front/case/'MEASUREMENTS.json');snap=next(x for x in m['checkpoints'] if x['label']==label)
        p=root/snap['path'];assert sha(p)==snap['sha256']
        seed=dt.Runtime.load_snapshot(str(p));start=seed.current_tick
        dense=seed.fork();dense.execution_options=dt.TickOptions(dt.Backend.DENSE_SEQUENTIAL,1)
        lazy=seed.fork();lazy.execution_options=dt.TickOptions(dt.Backend.LAZY,1)
        observed=seed.fork();observed.execution_options=dt.TickOptions(dt.Backend.LAZY,1)
        for f in (dense,lazy,observed):
            if front=='P14':
                target=(13,13,13)
                channel(f,'technical_phase_query',add(target,(-1,0,0),-2,f.dimension),(-1,0,0))
                events=[];schedule(f,events,'technical_phase_query',40,13,'probe')
            else:events=[]
        mid=temp/(case+'_pending.deetsnap');lazy.save_snapshot(str(mid));loaded=dt.Runtime.load_snapshot(str(mid))
        loaded.execution_options=dt.TickOptions(dt.Backend.LAZY,1)
        clone=lazy.fork();before=full_hash(lazy)
        q=(2,2,2);clone,item=edited(clone,q,dt.pack_record(1,1,0,0,1,1),None,'technical_single_site')
        assert full_hash(lazy)==before and not state_equal(lazy,clone)
        checkpoint_ticks=sorted(set([start,min(start+1,end),end]))
        equalities=[]
        for tick in checkpoint_ticks:
            for f in (dense,lazy,observed,loaded):f.run_until(tick)
            if front=='P03':relational(observed,(15,15,15))
            else:panel(observed,{'center':(15,15,15),'sample':(13,13,13)})
            full_hash(observed)
            equal=all(state_equal(lazy,f) for f in (dense,observed,loaded))
            equalities.append({'tick':tick,'Dense_Lazy_passive_save_load_equal_RAW_clock':equal})
            assert equal,(front,case,tick)
        reports.append({'case':front+'/'+case,'source_label':label,'snapshot_sha256':snap['sha256'],
            'window':[start,end],'comparisons':equalities,'fork_isolation':True,
            'pending_input_save_load':front=='P14','final_full_hashes':full_hash(lazy),
            'last_tick_backend_used':str(lazy.last_tick_info.used_backend),
            'last_tick_counters':{k:getattr(lazy.last_tick_info,k) for k in ('evaluated','overflows','genesis','used_threads')}})
    restore=[]
    for k in range(1,15):
        front=f'P{k:02}';files=sorted((root/'BRANCHES'/front).glob('*/MEASUREMENTS.json'))
        m=next(read(p) for p in files if read(p)['checkpoints'])
        snap=next((x for x in m['checkpoints'] if x['label']=='MAIN_FINAL'),m['checkpoints'][-1])
        p=root/snap['path'];assert sha(p)==snap['sha256']
        rt=dt.Runtime.load_snapshot(str(p));assert rt.current_tick==snap['tick']
        restore.append({'front':front,'case':m['case_id'],'label':snap['label'],'tick':rt.current_tick,
                        'sha256':snap['sha256'],'complete_clock_uint64_checked':True,'full_state_hashes':full_hash(rt)})
    # Use the sealed parent's wheel if the workspace-relative product layout changes.
    sealed=root.parent/'PARENT_SEALED.zip'
    with zipfile.ZipFile(sealed) as z:wheel_bytes=z.read('SHARED_TOOLS/dee_thinking-3.0.0-cp313-cp313-win_amd64.whl')
    assert hashlib.sha256(wheel_bytes).hexdigest()=='9aa3a69bf1d542308912dbeee0b7c89199dafe295ce09533a2a394c8bc83c6db'
    import io
    instrument=[];installed=Path(dt.__file__).resolve().parent.parent
    with zipfile.ZipFile(io.BytesIO(wheel_bytes)) as z:
        for name in z.namelist():
            if name.startswith('dee_thinking/') and not name.endswith('/'):
                local=installed/name;expected=hashlib.sha256(z.read(name)).hexdigest()
                assert local.is_file() and sha(local)==expected,name
                instrument.append({'wheel_member':name,'sha256':expected,'installed_byte_exact':True})
    report={'completed_utc':utc(),'decisive_windows':reports,'restored_front_checkpoints':restore,
            'library_version':dt.__version__,'kernel_identity':dt.kernel_identity(),'wheel_files':instrument,
            'native_DLL_unchanged':True,'temporary_technical_directory':str(temp),
            'scope':'Finite trajectory equalities and native instrument identity, not functional robustness outside measured domains.'}
    dump(root/'ANALYSIS/TECHNICAL_WINDOWS.json',report);print(json.dumps(report,indent=2))

def clean_extraction(root,archive):
    root=Path(root).resolve();archive=Path(archive).resolve()
    checks=verify(archive);temp=Path(tempfile.mkdtemp(prefix='dee_a02_clean_')).resolve()
    extract=temp/'PACKAGE';dependency=temp/'INSTRUMENT';extract.mkdir();dependency.mkdir()
    with zipfile.ZipFile(archive) as z:
        for name in z.namelist():
            if name.startswith(('/', '\\')) or '..' in Path(name).parts:raise ValueError('Unsafe archive member')
        z.extractall(extract)
    whl=extract/'SHARED_TOOLS/dee_thinking-3.0.0-cp313-cp313-win_amd64.whl';assert sha(whl)==WHEEL_SHA
    with zipfile.ZipFile(whl) as z:z.extractall(dependency)
    section=extract/SECTION;runner=section/'RUNNER/run_extension_02.py';replicas=[]
    cases=['P01/independent5','P09/mobile_basal_full','P14/flux_cut_replication1']
    for k,case in enumerate(cases,1):
        cmd=[sys.executable,'-I','-B',str(runner),'--root',str(section),'--package-root',str(extract),
             '--dependency-root',str(dependency),'--mode','reproduce','--case',case,'--replica-out',str(temp/f'REPLICA_{k}')]
        before=sha(section/'EXPERIMENT_CONFIG.json')
        process=subprocess.run(cmd,capture_output=True,text=True,encoding='utf-8',timeout=600)
        log={'case':case,'argv':cmd,'exit_code':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
        previous=root/'ANALYSIS'/f'CLEAN_REPRODUCTION_{k}.json'
        if previous.exists() and read(previous).get('exit_code')!=0:
            preserved=root/'ANALYSIS'/f'CLEAN_REPRODUCTION_{k}_LEGACY_METADATA_ATTEMPT.json'
            if not preserved.exists():preserved.write_bytes(previous.read_bytes())
        dump(previous,log)
        assert process.returncode==0,log
        report=json.loads(process.stdout)
        assert Path(report['runtime_module']).resolve().is_relative_to(dependency)
        assert Path(report['native_module']).resolve().is_relative_to(dependency)
        assert sha(section/'EXPERIMENT_CONFIG.json')==before,'Source cut altered by technical reproduction'
        replicas.append(report)
    # Restore the longer continuation from the clean package, without advancing a production Runtime.
    m=read(section/'BRANCHES/P06/continued_distributed_HA/MEASUREMENTS.json')
    cp=next(x for x in m['checkpoints'] if x['label']=='MAIN_FINAL');p=section/cp['path']
    assert sha(p)==cp['sha256'];rt=dt.Runtime.load_snapshot(str(p));assert rt.current_tick==700
    report={'checked_utc':utc(),'provisional_archive_sha256':sha(archive),'archive_integrity':checks,
        'clean_extraction':str(temp),'clean_WHL_sha256':sha(whl),'isolated_reproductions':replicas,
        'resumable_longer_checkpoint':{'path':cp['path'],'sha256':cp['sha256'],'tick':rt.current_tick,'full_state_hashes':full_hash(rt)},
        'exact_runner_sha256':sha(runner),'source_cut_not_mutated':True,
        'final_package_note':'This report is appended after testing a provisional archive. The final archive hash is computed outside the ZIP; no self-referential hash is claimed.'}
    dump(root/'ANALYSIS/CLEAN_EXTRACTION_CHECK.json',report)
    print(json.dumps({'clean_extraction':str(temp),'reproduced_cases':cases,'all_equal':True,
                      'provisional_archive_sha256':report['provisional_archive_sha256']},indent=2))

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True)
    p.add_argument('--mode',choices=['preflight','windows','clean'],default='preflight');p.add_argument('--archive',type=Path);a=p.parse_args()
    if a.mode=='clean':clean_extraction(a.root,a.archive)
    else:(preflight if a.mode=='preflight' else decisive_windows)(a.root)
if __name__=='__main__':main()
