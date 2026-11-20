"""Prospective busy/idle local-service trial; prepare now, execute only at freeze.

The caller explicitly selects one existing life/backend. No target, expected sign,
answer-driven curriculum or external policy chooses a native action.
"""
import argparse,ctypes,gzip,hashlib,json,os,queue,random,shutil,subprocess,sys,threading,time
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(path,life,contexts,seed,count=480,seconds=3605):
    if seconds<3600:raise ValueError('The final protocol cannot label a short window as sixty minutes.')
    rng=random.Random(seed);events=[];sizes=(count//4,count//2,count-count//4-count//2)
    for regime,(begin,end,n)in enumerate(zip((5,1100,2300),(1090,2290,3490),sizes),1):
        for i in range(n):
            t=begin+(end-begin)*(i+.1+.7*rng.random())/max(1,n)
            if 1788<t<1812:t+=24
            index=len(events)
            if index%13==0:row={'modo':'memoria','contexto':contexts[(index//13)%len(contexts)]}
            elif index%7==0:row={'modo':'usar'}
            else:row={'modo':'trabajo','valores':[rng.randint(2,31),rng.randint(2,31)],'dominio':'trabajadores'}
            events.append({'at_seconds':round(t,6),'regime':regime,'client':index%2,'id':'fi60_'+str(index).zfill(5),'payload':{'operacion':'sesion','situaciones':[row]}})
    events.sort(key=lambda x:x['at_seconds'])
    protocol={'schema':'DEE.unified.persistent_sixty_minute_prospective.v1','life_id':life,'backend':'mente_unificada','seconds':seconds,
        'private_auditor_seed':seed,'events':events,'nominal_events':len(events),'regimes':[{'id':i+1,'scheduled_events':sizes[i]}for i in range(3)],
        'contexts_explicit_P0':contexts,'idle_interval_seconds':.1,'idle_quantum_ticks':1,'save_seconds':60,
        'technical_pause_windows':[600,1800,3000],'pause_seconds_after_actual_safe_boundary':3,
        'burst_at_first_pause':14,'burst_material_capacity':8,'paired_export_at_second_pause_with_one_literal_pending_input':True,
        'invalid_tests_at_seconds':300,'end_arrivals_before_seconds':3520,'maximum_drain_seconds':120,
        'maximum_process_RAM_bytes':2147483648,'minimum_free_disk_bytes':2147483648,
        'assistance':'Calendar, codec, user-request initiation and old-memory context addresses are prepared. Public work values are fixed independently of native answers. Only literal payload reaches DEE; private seed/regime/times/IDs are transport or audit, never targets.',
        'worker_interruption':'Separate explicitly identified diagnostic copy, not an interruption or retry of this main trajectory.',
        'scope':'Operational continuous world trial, not a blanket cognitive or 24/7 certification. Cumulative queries and clones are not independent learners.'}
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8')as f:json.dump(protocol,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    return {'protocol':str(path),'sha256':sha(path),'events':len(events),'seconds':seconds,'native_ticks':0}


def process_resource(pid):
    if os.name!='nt':return {'pid':pid,'scope':'Process memory unavailable on this host'}
    from ctypes import wintypes
    class PMC(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD),('PeakWorkingSetSize',ctypes.c_size_t),('WorkingSetSize',ctypes.c_size_t),('QuotaPeakPagedPoolUsage',ctypes.c_size_t),('QuotaPagedPoolUsage',ctypes.c_size_t),('QuotaPeakNonPagedPoolUsage',ctypes.c_size_t),('QuotaNonPagedPoolUsage',ctypes.c_size_t),('PagefileUsage',ctypes.c_size_t),('PeakPagefileUsage',ctypes.c_size_t)]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE;kernel.CloseHandle.argtypes=[wintypes.HANDLE]
    handle=kernel.OpenProcess(0x0400|0x0010,False,pid)
    if not handle:return {'pid':pid,'error':'OpenProcess failed','winerror':ctypes.get_last_error()}
    try:
        value=PMC();value.cb=ctypes.sizeof(value);api=ctypes.WinDLL('psapi');api.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(PMC),wintypes.DWORD];api.GetProcessMemoryInfo.restype=wintypes.BOOL;ok=api.GetProcessMemoryInfo(handle,ctypes.byref(value),value.cb)
        return {'pid':pid,'working_set_bytes':int(value.WorkingSetSize),'peak_working_set_bytes':int(value.PeakWorkingSetSize)}if ok else{'pid':pid,'error':'Memory observation unavailable'}
    finally:kernel.CloseHandle(handle)


def execute(system,protocol_path,out):
    system=system.resolve();p=json.loads(protocol_path.read_bytes());life=p['life_id'];out=out.resolve();out.mkdir(parents=True,exist_ok=False)
    if p.get('schema')!='DEE.unified.persistent_sixty_minute_prospective.v1'or p['seconds']<3600:raise ValueError('Final frozen sixty-minute protocol required')
    if(system/'estado/locks'/(life+'.lock')).exists():raise ValueError('Life has another writer; do not interrupt it')
    shutil.copyfile(protocol_path,out/'PROTOCOLO.json');shutil.copyfile(Path(__file__),out/'CODIGO_ENSAYO.py')
    record=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes());before={k:record.get(k)for k in('life_id','world_id','profile','parent','snapshot','snapshot_sha256','physical')};del record
    sources=[]
    for rel in('gestionar.py','app/lives.py','app/cola_local.py','app/servicio_persistente.py','app/cliente_mente_unificada.py','app/finalizar_protocolo.py','capacidades/mente_unificada_01.py','capacidades/mente_acumulativa_r02.py','capacidades/selector_acrecion_nativo.py','capacidades/eo02_trabajador_local.py'):
        f=system/rel;target=out/'codigo'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);sources.append({'file':rel,'bytes':f.stat().st_size,'sha256':sha(f)})
    log=(out/'ADMISIONES_Y_EVENTOS.jsonl').open('x',encoding='utf8');mutex=threading.Lock();errors=[];stop_clients=threading.Event();clients=[queue.Queue(),queue.Queue()];owner=None;db=None;origin=None
    def emit(value):
        with mutex:log.write(json.dumps({'utc':now(),**value},sort_keys=True,ensure_ascii=False)+'\n');log.flush()
    def admission(event):
        try:reply=db.put(event['id'],event['payload']);emit({'kind':'admission','desired_seconds':event.get('at_seconds'),'actual_seconds':time.monotonic()-origin,'client':event.get('client'),'id':event['id'],'payload':event['payload'],'reply':reply})
        except Exception as error:emit({'kind':'transport_validation_rejection','id':event['id'],'payload':event['payload'],'type':type(error).__name__,'detail':str(error),'no_native_input':True})
    def client_loop(index):
        while not stop_clients.is_set()or not clients[index].empty():
            try:event=clients[index].get(timeout=.2)
            except queue.Empty:continue
            admission(event);clients[index].task_done()
    def control(identifier,op,timeout=30):
        reply=db.put(identifier,{'operacion':op});emit({'kind':'technical_control_admission','id':identifier,'operation':op,'reply':reply});deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            row=db.get(identifier)
            if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):
                emit({'kind':'technical_control_result','id':identifier,'record':row})
                if row['status']!='completed':raise RuntimeError('Control not completed: '+str(row))
                return json.loads(row['result'])
            time.sleep(.1)
        raise TimeoutError('Technical control '+identifier)
    def technical_windows():
        try:
            for index,at in enumerate(p['technical_pause_windows']):
                while not stop_clients.is_set()and time.monotonic()-origin<at:time.sleep(.2)
                if stop_clients.is_set():break
                paused=control('fi60_pause_'+str(index),'pausar');started_pause=time.monotonic()
                if index==0:
                    for i in range(p['burst_at_first_pause']):clients[i%2].put({'id':'fi60_burst_'+str(i),'client':i%2,'payload':{'operacion':'sesion','situaciones':[{'modo':'usar'}]}})
                if index==1:
                    admission({'id':'fi60_pending_export','client':'technical','payload':{'operacion':'sesion','situaciones':[{'modo':'usar'}]}})
                    exported=control('fi60_export_pending','exportar');emit({'kind':'paired_pending_export','value':exported})
                saved=control('fi60_pause_witness_'+str(index),'guardar')
                emit({'kind':'pause_exact_boundary_comparison','pause_tick':paused['after_tick'],'saved_tick':saved['after_tick'],'equal':paused['after_tick']==saved['after_tick']})
                while time.monotonic()-started_pause<p['pause_seconds_after_actual_safe_boundary']:time.sleep(.1)
                control('fi60_resume_'+str(index),'reanudar')
        except Exception as error:errors.append({'phase':'technical_windows','type':type(error).__name__,'detail':str(error)});emit({'kind':'technical_window_error','error':errors[-1]})
    started=time.monotonic();summary={'schema':'DEE.unified.persistent_sixty_minute_result.v1','before':before,'protocol_sha256':sha(protocol_path),'sources':sources};threads=[]
    try:
        argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend',p['backend'],'--intervalo',str(p['idle_interval_seconds']),'--ticks-ocio',str(p['idle_quantum_ticks']),'--guardar-cada',str(p['save_seconds']),'--max-segundos',str(p['seconds']+p['maximum_drain_seconds']+60)]
        launch_wall=time.time();owner=subprocess.Popen(argv,stdout=(out/'OWNER_STDOUT.txt').open('x',encoding='utf8'),stderr=(out/'OWNER_STDERR.txt').open('x',encoding='utf8'),text=True,encoding='utf8');deadline=time.monotonic()+30;path=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
        while time.monotonic()<deadline:
            if owner.poll()is not None:raise RuntimeError('Explicit owner failed before readiness')
            if path.is_file():
                db=QueueDB(path);status=db.get_meta('owner')
                if status and status.get('running')and status.get('wall_utc')and datetime.fromisoformat(status['wall_utc']).timestamp()>=launch_wall:break
            time.sleep(.1)
        else:raise TimeoutError('Native owner startup')
        origin=time.monotonic();summary['initial_owner']=status;emit({'kind':'owner_ready','launcher_pid':owner.pid,'status':status})
        for index in range(2):thread=threading.Thread(target=client_loop,args=(index,),daemon=True);thread.start();threads.append(thread)
        controls=threading.Thread(target=technical_windows,daemon=True);controls.start();next_event=0;last_resource=-100;invalid_done=False
        while time.monotonic()-origin<p['seconds']:
            elapsed=time.monotonic()-origin
            if owner.poll()is not None:raise RuntimeError('Owner exited before frozen horizon; no automatic restart or old-state fallback')
            while next_event<len(p['events'])and p['events'][next_event]['at_seconds']<=elapsed:
                event=p['events'][next_event];clients[event['client']].put(event);next_event+=1
            if not invalid_done and elapsed>=p['invalid_tests_at_seconds']:
                for i,payload in enumerate(({'operacion':'sesion','situaciones':[]},{'operacion':'sesion','situaciones':[{'modo':'usar','target':1}]},{'operacion':'guardar','shell':'do_not_execute'},{'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'fuera_dominio'}]})):
                    admission({'id':'fi60_invalid_'+str(i),'client':'technical','payload':payload})
                invalid_done=True
            if elapsed-last_resource>=10:
                status=db.get_meta('owner');resource=process_resource(status['pid']);free=shutil.disk_usage(system).free
                emit({'kind':'passive_resource_and_cached_owner','at_seconds':elapsed,'process':resource,'free_disk_bytes':free,'status':status});last_resource=elapsed
                if free<p['minimum_free_disk_bytes']or resource.get('working_set_bytes',0)>p['maximum_process_RAM_bytes']:raise RuntimeError('Declared equipment resource boundary reached; not a cognitive failure')
            time.sleep(.1)
        summary['host_seconds_from_owner_ready_to_horizon']=time.monotonic()-origin;stop_clients.set();[t.join(10)for t in threads];controls.join(10)
        deadline=time.monotonic()+p['maximum_drain_seconds']
        while time.monotonic()<deadline and any(r['status']in('queued','processing')for r in db.outstanding()):
            if owner.poll()is not None:break
            time.sleep(.2)
        summary['preclose_owner']=db.get_meta('owner');summary['remaining_before_close']=db.outstanding();control('fi60_final_pause','pausar')
        summary['final_paired_export']=control('fi60_final_export','exportar');control('fi60_final_save','guardar');control('fi60_final_stop','detener');owner.wait(timeout=30)
        summary['owner_returncode']=owner.returncode;summary['final_owner']=db.get_meta('owner');summary['transport_counts']=db.counters()
        with db.connect()as con:rows=[dict(r)for r in con.execute('SELECT * FROM requests ORDER BY seq')]
        with gzip.GzipFile(filename=str(out/'REGISTROS_TRANSPORTE.json.gz'),mode='wb',mtime=0)as f:f.write((json.dumps(rows,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
        after=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes());summary['final']={k:after.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical','operation_count_offset')}
    except Exception as error:
        summary['error']={'type':type(error).__name__,'detail':str(error)};emit({'kind':'harness_or_process_error','error':summary['error']})
        stop_clients.set()
        if owner and owner.poll()is None and db:
            try:control('fi60_emergency_stop','detener',timeout=60);owner.wait(timeout=30)
            except Exception as stop_error:summary['own_owner_stop_error']=str(stop_error)
        if db:summary['final_observed_owner']=db.get_meta('owner');summary['pending_preserved']=db.outstanding()
    finally:
        stop_clients.set();log.flush();os.fsync(log.fileno());log.close()
    summary['technical_errors']=errors;summary['host_seconds_total']=time.monotonic()-started
    summary['scope']='Actual executed times/counts only. Queue rejection is not native rejection; silence is not replaced by an intelligent action. All repeated queries belong to one life, not independent learners. Native reproducibility and causal learning require their separate controls.'
    (out/'RESULTADO.json').write_text(json.dumps(summary,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'result':str(out/'RESULTADO.json'),'error':summary.get('error'),'host_seconds':summary['host_seconds_total'],'counts':summary.get('transport_counts')}));return bool(summary.get('error'))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('preparar');q.add_argument('--salida',type=Path,required=True);q.add_argument('--vida',required=True);q.add_argument('--contextos',default='alfa,beta,gamma,delta,epsilon,zeta');q.add_argument('--semilla',type=int,default=2602511);q.add_argument('--cantidad',type=int,default=480);q.add_argument('--segundos',type=int,default=3605)
    q=sub.add_parser('ejecutar');q.add_argument('--sistema',type=Path,required=True);q.add_argument('--protocolo',type=Path,required=True);q.add_argument('--salida',type=Path,required=True)
    a=p.parse_args()
    if a.command=='preparar':print(json.dumps(prepare(a.salida,a.vida,a.contextos.split(','),a.semilla,a.cantidad,a.segundos)));return 0
    return execute(a.sistema,a.protocolo,a.salida)


if __name__=='__main__':raise SystemExit(main())
