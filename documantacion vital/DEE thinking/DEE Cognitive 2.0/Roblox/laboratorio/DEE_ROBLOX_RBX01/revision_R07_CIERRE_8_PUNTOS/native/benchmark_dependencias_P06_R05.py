"""Root-only full BASE/PROTO/BASE checkpoint-witness benchmark, zero Native ticks.

Default --preflight reads closed clone files only. The explicit launcher uses
the official Python313 and a512MiB owned Job. It never creates QueueDB, sends
an actor request, starts a service loop, saves or advances the world.
"""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,importlib.util,json,os,sqlite3,sys,time

ROOT=Path(__file__).resolve().parent.parent
PRODUCT=ROOT.parents[2]
LIMIT=536870912
HARD_FINISH=1794884820
PROTOTYPE=ROOT/'native/prototipos/cache_fuentes_C02_R04.py'
PROTO_SHA='a94fb1a65f6578def4b39c9d5387b65b97f3ae3370b50f14e1f7bb05300c8928'
CACHE_SHA='e4621d4875376a910511cadd55503daccadbd0a9787be8d99516417bf2e02adf'
PROTOCOL=ROOT/'protocolo/PROTOCOLO_P06_DEPENDENCIAS_R05.json'
SENTINEL='DEE_P06_RESULT_JSON:'

def ensure(v,msg):
    if not v:raise ValueError(msg)
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False)
def sha(p):
    value=hashlib.sha256()
    with Path(p).open('rb')as f:
        for block in iter(lambda:f.read(1048576),b''):value.update(block)
    return value.hexdigest()
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
def no_reparse(p,stop):
    for q in(p,*p.parents):
        if q.exists():ensure(not q.is_symlink()and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked/reparse benchmark path')
        if q==stop:break
def closed_transport(dest):
    ctx=read(dest/'CONTEXTO_EJECUCION.json');life=ctx['life'];system=dest/'sistema'
    database=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
    ensure(database.is_file(),'Full operational queue must already exist')
    for suffix in('-wal','-journal'):
        extra=Path(str(database)+suffix)
        ensure(not extra.exists()or extra.stat().st_size==0,'No live/incompatible SQLite auxiliary accepted')
    connection=sqlite3.connect(database.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:
        row=connection.execute("SELECT value FROM meta WHERE key='owner'").fetchone()
        ensure(row is not None and read_json_owner(row[0]).get('running')is False,'Closed owner witness required')
        ensure(connection.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'No pending/uncertain request may be bypassed')
    finally:connection.close()
    return ctx,database
def read_json_owner(value):return json.loads(value)
def preflight(dest):
    dest=Path(dest).resolve(strict=True)
    ensure(dest in(ROOT/'native/CTRL1',ROOT/'native/PILOT'),'Only diagnostic CTRL1/PILOT; never Main')
    no_reparse(dest,ROOT)
    ctx,db=closed_transport(dest)
    # Root required the benchmark after the first Main block closes.
    closed_transport(ROOT/'native/MAIN')
    system=dest/'sistema';life=ctx['life'];card=read(system/'estado/vidas'/life/'VIDA.json')
    imported=read(dest/'IMPORTACION_DIAGNOSTICA.json')
    ensure(imported['new_native_ticks']==0 and imported['comparison']['physical_equal']and imported['comparison']['causal_prefix_equal'],'Exact coherent import0 first')
    ensure(not(system/'estado/vidas'/life/'FUTURO_INTERRUMPIDO.json').exists(),'Interrupted future preserved; no diagnostic overwrite')
    scope=read(system/'capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
    ensure(scope['life_id']==life and scope['native_cutoff_utc_epoch']==HARD_FINISH,'Prospectively renewed closed role lease required')
    ensure(sha(system/'app/cache_fuentes_C02.py')==CACHE_SHA,'Original cache source must remain exact')
    ensure(sha(PROTOTYPE)==PROTO_SHA,'Declared prototype source changed')
    protocol=read(PROTOCOL)
    ensure(protocol['criterion']['minimum_fraction_reduction']==.20 and protocol['pass_order']==['BASE_1','PROTO','BASE_2'],'Prospective P06 contract changed')
    ensure(time.time()<HARD_FINISH-1200,'Finite benchmark margin required')
    critical=[system/'estado/vidas'/life/'VIDA.json',system/card['snapshot'],db,
              system/'capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json']
    for suffix in('-wal','-shm','-journal'):
        p=Path(str(db)+suffix)
        if p.is_file():critical.append(p)
    return{'destination':str(dest),'system':str(system),'life':life,'expected_tick':card['physical']['tick'],
      'recorded_physical':card['physical'],'critical':{str(p):sha(p)for p in critical},
      'prototype_sha256':PROTO_SHA,'protocol_sha256':sha(PROTOCOL)}

def tree_hashes(root):
    values={}
    for current,dirs,files in os.walk(root,followlinks=False):
        dirs.sort();files.sort()
        for name in files:
            p=Path(current)/name;no_reparse(p,root)
            values[p.relative_to(root).as_posix()]={'bytes':p.stat().st_size,'sha256':sha(p)}
    return values
def metadata_hash(a):
    entries=[]
    for k,v in sorted(dict(a.world.runtime.snapshot_metadata_entries).items()):
        if isinstance(v,bytes):value={'type':'bytes','hex':v.hex()}
        elif isinstance(v,str):value={'type':'str','value':v}
        else:raise ValueError('Unexpected metadata encoding; no lossy coercion')
        entries.append([k,value])
    return hashlib.sha256(canonical(entries).encode()).hexdigest()

def worker(a):
    ensure(a.worker_root_only and os.name=='nt','Root Windows worker only')
    basis=preflight(a.destination)
    system=Path(basis['system']);life=basis['life']
    sys.path[:0]=[str(system),str(system/'app'),str(PRODUCT/'reproducibilidad')]
    from app import process_control as pc
    pc.protect_current(memory_limit=LIMIT)
    resources=pc.current_resources()
    ensure(resources.get('job_memory_limit')==LIMIT,'Actual512MiB owned Job is required')
    # Load the declared source-only instrument before opening the application's
    # strict operational access fence. No Native module lives in this prototype.
    prototype=load(PROTOTYPE,'_p06_source_metadata_pass')
    from app.cache_fuentes_C02 import ImmutableSourceCache
    from app.mundo_genesis_apd05 import GenesisNativeWorld
    cache=world=None;passes=[];physical=[];meta=[];failure=None
    before_files=tree_hashes(system/'estado')
    try:
        cache=ImmutableSourceCache(system).open()
        world=GenesisNativeWorld(system,life,'mente_unificada').open()
        ensure(world.tick==basis['expected_tick'],'Opening diagnostic altered Native tick')
        before=world.fingerprint()
        ensure(before==basis['recorded_physical'],'Opened RAW/clocks differ from stored closed record')
        initial_meta=metadata_hash(world.a)
        # Fail closed if any supposedly passive validator attempts a mutation.
        def forbid(*args,**kwargs):raise RuntimeError('P06_NO_MATERIAL_OR_ADVANCE_ALLOWED')
        for name in('advance','execute','before_mutation'):setattr(world,name,forbid)
        world.a.run_until=forbid
        for label in('BASE_1','PROTO','BASE_2'):
            physical.append({'stage':label+'_BEFORE','value':world.fingerprint()});meta.append(metadata_hash(world.a))
            started=time.perf_counter();cpu=time.process_time();counts=None
            if label=='PROTO':
                with prototype._checkpoint_pass_R04(cache)as counts:payload=world.operational_dependencies()
            else:payload=world.operational_dependencies()
            wall=time.perf_counter()-started;cpu=time.process_time()-cpu
            encoded=canonical(payload)
            passes.append({'label':label,'wall_seconds':wall,'cpu_seconds':cpu,
              'payload_sha256':hashlib.sha256(encoded.encode()).hexdigest(),
              'payload':payload,'source_metadata_pass':dict(counts)if counts is not None else None})
            physical.append({'stage':label+'_AFTER','value':world.fingerprint()});meta.append(metadata_hash(world.a))
            ensure(world.tick==basis['expected_tick'],'Native tick advanced during passive benchmark')
        payload_equal=len({p['payload_sha256']for p in passes})==1
        physical_equal=all(p['value']==before for p in physical)
        metadata_equal=all(m==initial_meta for m in meta)
        baseline=min(passes[0]['wall_seconds'],passes[2]['wall_seconds'])
        candidate=passes[1]['wall_seconds'];gain=(baseline-candidate)/baseline if baseline>0 else None
        cache_witness=cache.witness()
    except BaseException as error:
        failure=type(error).__name__+': '+str(error)
    finally:
        final_physical=None
        if world is not None:
            try:final_physical=world.fingerprint()
            finally:world.close()
        if cache is not None:cache.close()
    after_files=tree_hashes(system/'estado')
    critical_after={p:sha(p)for p in basis['critical']}
    unchanged=before_files==after_files
    result={'schema':'DEE.R07.P06.FullDependenciesBenchmark.R05','utc':utc(),'basis':basis,
      'failure':failure,'passes':passes,'physical_checks':physical,'metadata_hashes':meta,
      'operational_files_before':before_files,'operational_files_after':after_files,
      'operational_files_identical':unchanged,'no_operational_add_delete':set(before_files)==set(after_files),
      'critical_files_identical':basis['critical']==critical_after,
      'Native_requests_submitted':0,'Native_ticks_allowed':0,
      'Native_ticks':final_physical['tick']-basis['expected_tick']if final_physical is not None else None,
      'final_physical':final_physical,'service_loop_started':False,'queue_writer_created':False,
      'root_job':resources,'prototype_installed_in_system':False}
    if failure is None:
        result.update(payload_equal=payload_equal,physical_equal=physical_equal,metadata_equal=metadata_equal,
          baseline_faster_wall_seconds=baseline,prototype_wall_seconds=candidate,fraction_reduction=gain,
          cache_witness=cache_witness,
          criterion_met=bool(payload_equal and physical_equal and metadata_equal and unchanged and basis['critical']==critical_after and gain is not None and gain>=.20))
    print(SENTINEL+json.dumps(result,ensure_ascii=False,allow_nan=False),flush=True)
    if failure is not None or not unchanged or basis['critical']!=critical_after:return 2
    return 0

def launch(a):
    basis=preflight(a.destination)
    if not a.execute_root_only:return{'status':'PREFLIGHT_ONLY_NO_NATIVE',**basis}
    ensure(os.name=='nt','Actual Windows Root Job required')
    out=a.output.resolve();ensure(out.is_relative_to(ROOT/'evidencia')and not out.exists(),'Fresh evidence output only')
    out.mkdir(parents=True);product_pc=load(PRODUCT/'sistema/app/process_control.py','_p06_root_job')
    argv=[str(PRODUCT/'motor/python313/python.exe'),'-I','-B','-X','utf8',str(Path(__file__).resolve()),
          '--worker-root-only','--destination',str(Path(a.destination).resolve())]
    stdout_path=out/'worker.stdout.jsonl';stderr_path=out/'worker.stderr.txt'
    proc=job=None;limit=min(1800,int(HARD_FINISH-time.time()))
    ensure(limit>=1200,'Finite benchmark closing margin')
    with stdout_path.open('x',encoding='utf-8')as so,stderr_path.open('x',encoding='utf-8')as se:
        try:
            proc,job,name=product_pc.spawn_owned(argv,cwd=ROOT,stdout=so,stderr=se,memory_limit=LIMIT)
            deadline=time.monotonic()+limit
            while proc.poll()is None and time.monotonic()<deadline:time.sleep(.5)
            timed_out=proc.poll()is None
            resources=product_pc.job_resources(job)
        finally:
            if job is not None:product_pc.close_job(job)
            if proc is not None:
                try:proc.wait(timeout=20)
                except Exception:pass
    ensure(stdout_path.stat().st_size<=128*1024**2,'Finite auditor output bound')
    encoded=[line[len(SENTINEL):]for line in stdout_path.read_text('utf-8').splitlines()if line.startswith(SENTINEL)]
    ensure(not timed_out and proc.returncode in(0,2)and len(encoded)==1,'Worker incomplete; preserve files, no automatic retry')
    result=json.loads(encoded[0]);result['launcher']={'pid':proc.pid,'exit_code':proc.returncode,'actual_job_resources':resources,'memory_limit':LIMIT}
    for entry in result['passes']:
        data=entry.pop('payload');(out/('DEPENDENCIAS_'+entry['label']+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'RESULTADO_P06.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return{'output':str(out),'criterion_met':result.get('criterion_met',False),'failure':result['failure'],
      'Native_ticks':result['Native_ticks'],'payload_equal':result.get('payload_equal'),
      'physical_equal':result.get('physical_equal'),'operational_files_identical':result['operational_files_identical'],
      'fraction_reduction':result.get('fraction_reduction')}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-root-only',action='store_true');p.add_argument('--worker-root-only',action='store_true')
    p.add_argument('--destination',type=Path,required=True);p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.worker_root_only:raise SystemExit(worker(a))
    if a.execute_root_only and a.output is None:p.error('Fresh --output required')
    print(json.dumps(launch(a),ensure_ascii=False,indent=2))
