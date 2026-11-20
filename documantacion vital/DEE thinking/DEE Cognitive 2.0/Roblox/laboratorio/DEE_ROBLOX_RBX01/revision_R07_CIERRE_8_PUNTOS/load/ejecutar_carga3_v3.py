"""Root-only1->2->3 focal process load. No clone/import, shell, model or MCP.

Default is a plan/preflight. Only --execute-root-only opens worker processes;
each worker uses its own official Native owner and the SAME100k R06 ledger.
"""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
LAST_NEW=1794859200
CUTOFF=1794863220
def need(ok,msg):
    if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write_new(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def memory():
    class Memory(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('totalPhysical',ctypes.c_ulonglong),('availablePhysical',ctypes.c_ulonglong),
                  ('totalPage',ctypes.c_ulonglong),('availablePage',ctypes.c_ulonglong),('totalVirtual',ctypes.c_ulonglong),('availableVirtual',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
    need(os.name=='nt','Installed Windows host memory guard required; no invented Linux/RAM measurement')
    m=Memory();m.length=ctypes.sizeof(m)
    need(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)),'Cannot measure actual free host RAM')
    return dict(utc=utc(),epoch=time.time(),total_bytes=m.totalPhysical,available_bytes=m.availablePhysical,load_percent=m.load)
def closed_baseline(path):
    proof=read(path)
    need(proof.get('schema')=='DEE.RBX01.R07.integrated.result.R01'and proof.get('owner_closed')is True,'Closed R06 Main block proof required')
    need(proof.get('identity',{}).get('life')=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN','Declared R06 candidate')
    world=Path(proof['world_checkpoint'])
    need(world.is_file()and sha(world)==proof['world_sha256'],'Whole matching Main World remains preserved')
    return dict(path=str(path),sha256=sha(path),final_tick=proof['final_tick'],world=str(world),world_sha256=proof['world_sha256'])
def preflight(a):
    protocol=read(ROOT/'load/PROTOCOLO_CARGA_V3_R01.json')
    profiles=protocol['stages'][a.stage-1]['simultaneous_lives']
    load_root=a.load_root.resolve(strict=True);need(load_root==ROOT/'native','Exact native/LOAD1..3 roots; never a link or another system')
    ledger=a.ledger.resolve(strict=True);need(ledger.is_relative_to(ROOT),'The one R07 global ledger')
    value=read(ledger)
    need(value.get('limit')==160000 and value.get('max_worlds')==6 and isinstance(value.get('intents'),dict),'Concurrent global R06 budget schema')
    need(not value['intents'],'Resolve prior Native intents before a load stage; never purge/replay')
    need(value['consumed']+sum(x.get('reserved',0)for x in value['worlds'].values())+4096*len(profiles)<=160000,'Not enough actual global reservation for one simultaneous opportunity')
    specs=[]
    for profile in profiles:
        destination=load_root/profile;need(destination.is_dir(),'Root must prepare/import full load root first: '+str(destination))
        context=read(destination/'CONTEXTO_EJECUCION.json');need(context['life']==protocol['lifes'][profile]['id'],'Unique expected load identity')
        need((destination/'IMPORTACION_DIAGNOSTICA.json').is_file(),'Root import0 before any owner')
        specs.append(dict(profile=profile,destination=str(destination),life=context['life']))
    baseline=closed_baseline(a.baseline_close_proof.resolve(strict=True))
    if a.stage>1:
        previous=read(a.previous_stage.resolve(strict=True))
        need(previous['stage']==a.stage-1 and previous['status']=='ALL_DECLARED_LIVES_CLOSED_AND_COMPLETE','Previous actual stage closed/complete before increasing load')
    return protocol,specs,ledger,baseline
def run(a):
    protocol,specs,ledger,baseline=preflight(a)
    plan=dict(stage=a.stage,profiles=specs,ledger=str(ledger),baseline=baseline,protocol_sha256=sha(ROOT/'load/PROTOCOLO_CARGA_V3_R01.json'),
              new_Native_requested_by_preflight=0,worker=str(ROOT/'load/worker_carga_v3.py'),worker_sha256=sha(ROOT/'load/worker_carga_v3.py'))
    if not a.execute_root_only:return dict(status='PREFLIGHT_ONLY_NO_OWNER',**plan)
    need(time.time()<protocol['latest_batch_start_epoch'],'Do not launch three owners too late; stage start before18:00UTC')
    output=a.output.resolve();need(output.is_relative_to(ROOT/'load')and not output.exists(),'Fresh load stage evidence only')
    minimum=2*1024**3+len(specs)*536870912
    measured=memory();need(measured['available_bytes']>=minimum,'Insufficient measured RAM; stop ladder without lifting installed guards')
    output.mkdir(parents=True);barrier=output/'BARRERA';barrier.mkdir()
    write_new(output/'PLAN_EJECUTADO.json',dict(**plan,host_before=measured,minimum_free_before_bytes=minimum,owner_memory_limit_bytes=536870912))
    workers=[];samples=[measured];abort_reason=None;go_sent=False
    for spec in specs:
        child=output/spec['profile'];stdout=(output/(spec['profile']+'.stdout.txt')).open('x',encoding='utf8');stderr=(output/(spec['profile']+'.stderr.txt')).open('x',encoding='utf8')
        command=[sys.executable,'-I','-B',str(ROOT/'load/worker_carga_v3.py'),'--execute-root-only','--profile',spec['profile'],'--stage',str(a.stage),
                 '--destination',spec['destination'],'--ledger',str(ledger),'--output',str(child),'--barrier',str(barrier)]
        process=subprocess.Popen(command,cwd=ROOT,stdout=stdout,stderr=stderr,shell=False,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        workers.append(dict(spec=spec,process=process,output=child,stdout=stdout,stderr=stderr,command=command))
    ready_deadline=time.monotonic()+660;last_sample=0
    def abort(reason):
        nonlocal abort_reason
        if abort_reason is None:
            abort_reason=reason;write_new(barrier/'ABORT.json',dict(reason=reason,utc=utc(),applies='BEFORE_NEXT_OPPORTUNITY_FINISH_ADMITTED_CYCLE_NO_KILL'))
    while any(w['process'].poll()is None for w in workers):
        now=time.time()
        if time.monotonic()-last_sample>=3:
            sample=memory();samples.append(sample);last_sample=time.monotonic()
            if sample['available_bytes']<1024**3:abort('HOST_FREE_RAM_BELOW_1GiB')
        if now>=LAST_NEW:abort('LAST_NEW_EPISODE_CUTOFF')
        if not go_sent:
            if now>=protocol['latest_GO_epoch']:abort('LATEST_GO_MARGIN_EXPIRED')
            ready=all((w['output']/'READY.json').is_file()for w in workers)
            if any(w['process'].poll()is not None and not(w['output']/'READY.json').is_file()for w in workers):abort('WORKER_EXIT_BEFORE_READY')
            if time.monotonic()>ready_deadline:abort('BOUNDED_READINESS_EXPIRED')
            if ready and abort_reason is None and now<protocol['latest_GO_epoch']:
                rows=[read(w['output']/'READY.json')for w in workers]
                need(len({r['owner_pid']for r in rows})==len(rows)and len({r['life']for r in rows})==len(rows),'Independent Native owner PID/life identities')
                write_new(barrier/'GO.json',dict(stage=a.stage,profiles=[x['profile']for x in specs],utc=utc(),epoch=now,owners=rows));go_sent=True
        if any(w['process'].poll()not in(None,0)for w in workers):abort('WORKER_FAILURE_PRESERVE_OTHER_ADMITTED_CYCLES')
        if now>=CUTOFF:
            abort('HARD_CUTOFF_DRAIN_PROOF_MISSING_ACTIVE_PRESERVED');break
        time.sleep(.2)
    reports=[]
    for w in workers:
        w['stdout'].close();w['stderr'].close()
        path=w['output']/'RESULTADO.json'
        reports.append(dict(profile=w['spec']['profile'],worker_pid=w['process'].pid,exit_code=w['process'].poll(),result_path=str(path),
            result=read(path)if path.is_file()else None,active_preserved=w['process'].poll()is None))
    all_closed=all(r['exit_code']==0 and r['result']and r['result']['closed']and r['result']['pending_global_intent']is None and len(r['result']['results'])==3 for r in reports)
    intervals=[r['result']for r in reports if r['result']and r['result']['owner_open_epoch']is not None and r['result']['owner_closed_epoch']is not None]
    overlap=max(0,min(x['owner_closed_epoch']for x in intervals)-max(x['owner_open_epoch']for x in intervals))if len(intervals)==len(specs)else None
    final_ledger=read(ledger)
    result=dict(schema='DEE.RBX.IntegralV3.LoadStage.R01',stage=a.stage,
        status='ALL_DECLARED_LIVES_CLOSED_AND_COMPLETE'if all_closed else'PARTIAL_OR_BLOCKED_PRESERVED',abort_reason=abort_reason,
        owners=reports,owner_lifetime_common_overlap_seconds=overlap,host_samples=samples,
        ledger_after=final_ledger,global_limit=160000,one_native_writer_per_life=True,
        source=plan,scope='Concurrent separate owner processes; transport-free focal Native test, no Roblox action/model/MCP, not kernel-instruction simultaneity or a theoretical capacity ceiling.')
    target=output/'RESULTADO_ETAPA.json';write_new(target,result)
    return dict(result=str(target),sha256=sha(target),stage=a.stage,status=result['status'],overlap_seconds=overlap)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true')
    p.add_argument('--stage',type=int,choices=(1,),required=True);p.add_argument('--load-root',type=Path,required=True)
    p.add_argument('--ledger',type=Path,required=True);p.add_argument('--baseline-close-proof',type=Path,required=True)
    p.add_argument('--previous-stage',type=Path);p.add_argument('--output',type=Path)
    a=p.parse_args()
    if a.stage>1 and a.previous_stage is None:p.error('Actual previous stage result required')
    if a.execute_root_only and a.output is None:p.error('Fresh explicit evidence output required')
    print(json.dumps(run(a),ensure_ascii=False,indent=2))
