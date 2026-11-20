"""APD01 prospective busy/idle service harness over the existing native owner.

The separately frozen literal curriculum supplies all messages, teachings and
environmental changes before data. This harness records transport and time; it
does not parse meanings, calculate results, choose routes or repair a failure.
Derived from the preserved MUFI R04 infrastructure, not a repeated science run.
"""
import argparse,importlib.util,sqlite3,ctypes,gzip,hashlib,json,os,queue,random,shutil,subprocess,sys,threading,time
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


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
    if p.get('schema')!='DEE.APD01.prospective_service_curriculum.v1'or p.get('status')!='FROZEN_FOR_ONE_SELECTED_CANDIDATE'or p['seconds']<3720:raise ValueError('An actual frozen APD candidate and prospective sixty-minute protocol are required')
    prefix=p.get('request_prefix')
    if prefix!='apd60_'or len(p['events'])!=480 or any(not e['id'].startswith(prefix)for e in p['events']):raise ValueError('APD requires its fresh480-event transport prefix; inherited IDs are not replayed')
    if p.get('backend')!='mente_unificada':raise ValueError('Explicit existing unified backend required; no automatic substitution')
    budget_deadline=datetime.fromisoformat(p['budget_deadline_utc'])
    if (budget_deadline-datetime.now(timezone.utc)).total_seconds()<p['seconds']+p['maximum_closure_seconds']+p['owner_startup_allowance_seconds']:raise ValueError('Insufficient time in the original campaign budget; do not reset the deadline or start an unfinishable trial')
    if not 1<=p['maximum_process_RAM_bytes']<=536870912:raise ValueError('Frozen worker memory limit exceeds the original APD budget')
    spec=importlib.util.spec_from_file_location('apd_frozen_queue',system/'app/cola_local.py');queue_module=importlib.util.module_from_spec(spec);spec.loader.exec_module(queue_module);QueueDB=queue_module.QueueDB
    for event in p['events']:queue_module.validate_request(event['payload'])
    if(system/'estado/locks'/(life+'.lock')).exists():raise ValueError('Life has another writer; do not interrupt it')
    shutil.copyfile(protocol_path,out/'PROTOCOLO.json');shutil.copyfile(Path(__file__),out/'CODIGO_ENSAYO.py')
    record=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes());before={k:record.get(k)for k in('life_id','world_id','profile','parent','snapshot','snapshot_sha256','physical')};del record
    if before['life_id']!=p['initial_cut']['life_id']or before['physical']['tick']!=p['initial_cut']['tick']or before['physical']['N']!=p['initial_cut']['N']or before['snapshot_sha256']!=p['initial_cut']['snapshot_sha256']:raise ValueError('Selected complete cut differs from the protocol; no current/favorable state substituted')
    queue_path=system/'estado/servicios_persistentes'/before['world_id']/'cola.sqlite3'
    if not p.get('requires_existing_paired_queue')or not queue_path.is_file():raise ValueError('This selected APD candidate requires its existing complete paired journal, even for a closed epoch; no empty journal or bare-fork fallback')
    wal=queue_path.with_name(queue_path.name+'-wal')
    if wal.is_file()and wal.stat().st_size:raise ValueError('Unsettled WAL before the selected closed handoff; no immutable partial-journal interpretation or deletion')
    with sqlite3.connect(queue_path.as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        if any(r[0].startswith(prefix)for r in c.execute('SELECT id FROM requests')):raise ValueError('APD transport prefix already used; preserve prior future, do not replay it')
    sources=[]
    for rel,expected in p['source_sha256'].items():
        f=(system/rel).resolve(strict=True)
        if not f.is_relative_to(system)or sha(f)!=expected:raise ValueError('Frozen exact source differs before first tick: '+rel)
        target=out/'codigo'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);sources.append({'file':rel,'bytes':f.stat().st_size,'sha256':sha(f)})
    (out/'FUENTES_Y_CORTE_ANTES_DEL_PRIMER_TICK.json').write_text(json.dumps({'utc':now(),'protocol_sha256':sha(protocol_path),'harness_sha256':sha(Path(__file__)),'source_record':before,'sources':sources,'native_ticks_at_preparation':0},sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    log=(out/'ADMISIONES_Y_EVENTOS.jsonl').open('x',encoding='utf8');mutex=threading.Lock();errors=[];stop_clients=threading.Event();planned_restart=threading.Event();planned_pause=threading.Event();clients=[queue.Queue(),queue.Queue()];owner=None;db=None;origin=None;owner_index=0;controls_record={};pause_intervals=[];unexpected_pauses=[];last_resume_utc=None
    service_deadline=time.monotonic()+p['owner_startup_allowance_seconds']+p['seconds']+p['maximum_closure_seconds']
    def emit(value):
        with mutex:log.write(json.dumps({'utc':now(),**value},sort_keys=True,ensure_ascii=False)+'\n');log.flush()
    def admission(event):
        try:
            reply=db.put(event['id'],event['payload']);emit({'kind':'admission','desired_seconds':event.get('at_seconds'),'actual_seconds':time.monotonic()-origin,'client':event.get('client'),'id':event['id'],'payload':event['payload'],'reply':reply});return reply
        except Exception as error:emit({'kind':'transport_validation_rejection','id':event['id'],'payload':event['payload'],'type':type(error).__name__,'detail':str(error),'no_native_input':True});return None
    def client_loop(index):
        while not stop_clients.is_set()or not clients[index].empty():
            try:event=clients[index].get(timeout=.2)
            except queue.Empty:continue
            admission(event);clients[index].task_done()
    def control(identifier,op,timeout=None):
        if timeout is None:timeout=p['export_client_wait_seconds']if op=='exportar'else 45
        reply=db.put(identifier,{'operacion':op});emit({'kind':'technical_control_admission','id':identifier,'operation':op,'reply':reply});deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            row=db.get(identifier)
            if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):
                emit({'kind':'technical_control_result','id':identifier,'record':row})
                if row['status']!='completed':raise RuntimeError('Control not completed: '+str(row))
                value=json.loads(row['result']);controls_record[identifier]=value;return value
            time.sleep(.1)
        raise TimeoutError('Technical control '+identifier)
    def launch_owner(*,paused=False,remaining=None):
        nonlocal owner,owner_index,db
        for identity in sources:
            if sha(system/identity['file'])!=identity['sha256']:raise ValueError('Frozen source changed; no silent interface/reader substitution during an executed reserve.')
        owner_index+=1
        remaining_global=min(service_deadline-time.monotonic(),(budget_deadline-datetime.now(timezone.utc)).total_seconds())
        if remaining_global<=0:raise TimeoutError('The one original owner/campaign deadline is exhausted; no restart extends it')
        argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend',p['backend'],'--intervalo',str(p['idle_interval_seconds']),'--ticks-ocio',str(p['idle_quantum_ticks']),'--guardar-cada',str(p['save_seconds']),'--max-segundos',str(remaining_global)]
        if paused:argv+=['--pausado']
        launch_wall=time.time()
        env=dict(os.environ);env['OMP_NUM_THREADS']='1'
        owner=subprocess.Popen(argv,stdout=(out/('OWNER_'+str(owner_index)+'_STDOUT.txt')).open('x',encoding='utf8'),stderr=(out/('OWNER_'+str(owner_index)+'_STDERR.txt')).open('x',encoding='utf8'),text=True,encoding='utf8',env=env)
        deadline=time.monotonic()+60;path=queue_path
        while time.monotonic()<deadline:
            if owner.poll()is not None:raise RuntimeError('Explicit owner failed before readiness')
            if path.is_file():
                db=QueueDB(path);status=db.get_meta('owner')
                if status and status.get('running')and status.get('wall_utc')and datetime.fromisoformat(status['wall_utc']).timestamp()>=launch_wall:
                    emit({'kind':'owner_process_ready','index':owner_index,'launcher_pid':owner.pid,'status':status,'planned_restart':planned_restart.is_set()})
                    if not paused and(status.get('paused')or status.get('uncertain_external_result')):raise ValueError('Selected current transport starts paused/uncertain outside the fixed protocol; do not silently resume or retry it')
                    return status
            time.sleep(.1)
        raise TimeoutError('Native owner startup')
    def technical_windows():
        nonlocal last_resume_utc
        try:
            for index,at in enumerate(p['technical_pause_windows']):
                while not stop_clients.is_set()and time.monotonic()-origin<at:time.sleep(.2)
                if stop_clients.is_set():break
                planned_pause.set();paused=control(prefix+'pause_'+str(index),'pausar');started_pause=time.monotonic()
                if index==0:
                    for i in range(p['burst_at_first_pause']):clients[i%2].put({'id':prefix+'burst_'+str(i),'client':i%2,'payload':p['burst_payload']})
                if index==1:
                    reply=admission({'id':prefix+'pending_export','client':'technical','payload':p['pending_transport_payload']})
                    if not reply or reply.get('admission')!='queued':raise ValueError('The reserved literal pending request was not queued; absence is not a successful pending-state test')
                    pending_before=db.get(prefix+'pending_export')
                    if not pending_before or pending_before['status']!='queued'or pending_before['payload_sha']!=queue_module.digest(p['pending_transport_payload']):raise ValueError('Reserved pending FIFO payload/status differs before save')
                    exported=control(prefix+'export_pending','exportar');emit({'kind':'paired_pending_export','value':exported})
                saved=control(prefix+'pause_witness_'+str(index),'guardar')
                emit({'kind':'pause_exact_boundary_comparison','pause_tick':paused['after_tick'],'saved_tick':saved['after_tick'],'equal':paused['after_tick']==saved['after_tick']})
                if index==1:
                    dependencies=saved['committed_snapshot']['operational_dependencies']
                    if p['pending_contract']=='APD_SYNCHRONOUS_WITH_REAL_MUFI_CHAIN_PENDING'and not(dependencies.get('external_pending_present')and dependencies.get('cascade_pending_present')):raise ValueError('No genuine native MUFI pending artifact/cascade at the reserved boundary; do not invent a pending APD calculator')
                    planned_restart.set();stopped=control(prefix+'midpoint_stop','detener');old_pid=owner.pid;owner.wait(timeout=60)
                    before_restart=saved['committed_snapshot'];launch_owner(paused=True,remaining=p['seconds']-(time.monotonic()-origin)+p['maximum_drain_seconds']+180)
                    after_restart=control(prefix+'midpoint_reloaded_witness','guardar')['committed_snapshot']
                    pending_after=db.get(prefix+'pending_export')
                    if pending_before!=pending_after:raise ValueError('Reserved queued request changed across owner processes; no silent replacement or replay')
                    if before_restart['physical']!=after_restart['physical']or before_restart.get('operational_dependencies')!=after_restart.get('operational_dependencies'):raise ValueError('Actual native fields or external/APD environment witness changed across paused reload')
                    emit({'kind':'same_life_full_state_process_reload','old_launcher_pid':old_pid,'new_launcher_pid':owner.pid,'before':before_restart,'after':after_restart,
                        'physical_equal':before_restart['physical']==after_restart['physical'],
                        'pending_protocol_equal':before_restart.get('operational_dependencies')==after_restart.get('operational_dependencies'),
                        'pending_transport_row_before':pending_before,'pending_transport_row_after':pending_after,'no_material_action_retried':True})
                    planned_restart.clear()
                while time.monotonic()-started_pause<p['pause_seconds_after_actual_safe_boundary']:time.sleep(.1)
                resumed=control(prefix+'resume_'+str(index),'reanudar')
                last_resume_utc=resumed['finished_execution_utc'];planned_pause.clear()
                duration=(datetime.fromisoformat(resumed['finished_execution_utc'])-datetime.fromisoformat(paused['started_utc'])).total_seconds()
                pause_intervals.append({'pause_id':paused['id'],'resume_id':resumed['id'],'discount_start_utc':paused['started_utc'],'discount_end_utc':resumed['finished_execution_utc'],'discount_seconds':duration,'tick_preserved':paused['after_tick']==resumed['before_tick']})
                if duration<0 or not pause_intervals[-1]['tick_preserved']:raise ValueError('Invalid full pause/reload time span or native pause advanced')
        except Exception as error:errors.append({'phase':'technical_windows','type':type(error).__name__,'detail':str(error)});emit({'kind':'technical_window_error','error':errors[-1]})
        finally:planned_restart.clear();planned_pause.clear()
    started=time.monotonic();summary={'schema':'DEE.APD01.persistent_sixty_minute_result.v1','before':before,'initial_VIDA_bytes':(system/'estado/vidas'/life/'VIDA.json').stat().st_size,'protocol_sha256':sha(protocol_path),'sources':sources};threads=[]
    try:
        status=launch_owner()
        origin=time.monotonic();summary['initial_owner']=status;emit({'kind':'owner_ready','launcher_pid':owner.pid,'status':status})
        for index in range(2):thread=threading.Thread(target=client_loop,args=(index,),daemon=True);thread.start();threads.append(thread)
        controls=threading.Thread(target=technical_windows,daemon=True);controls.start();next_event=0;last_resource=-100;invalid_done=False
        while time.monotonic()-origin<p['seconds']:
            elapsed=time.monotonic()-origin
            if owner.poll()is not None and not planned_restart.is_set():raise RuntimeError('Owner exited before frozen horizon; no automatic restart or old-state fallback')
            while next_event<len(p['events'])and p['events'][next_event]['at_seconds']<=elapsed:
                event=p['events'][next_event];clients[event['client']].put(event);next_event+=1
            if not invalid_done and elapsed>=p['invalid_tests_at_seconds']:
                for i,payload in enumerate(p['invalid_payloads']):
                    admission({'id':prefix+'invalid_'+str(i),'client':'technical','payload':payload})
                invalid_done=True
            if elapsed-last_resource>=10:
                status=db.get_meta('owner');resource=process_resource(status['pid']);free=shutil.disk_usage(system).free
                emit({'kind':'passive_resource_and_cached_owner','at_seconds':elapsed,'process':resource,'free_disk_bytes':free,'VIDA_bytes':(system/'estado/vidas'/life/'VIDA.json').stat().st_size,'queue_bytes':sum(f.stat().st_size for f in queue_path.parent.glob(queue_path.name+'*')if f.is_file()),'status':status});last_resource=elapsed
                fresh_after_resume=last_resume_utc is None or status.get('wall_utc','')>last_resume_utc
                if status.get('paused')and not planned_pause.is_set()and fresh_after_resume:
                    unexpected={'at_seconds':elapsed,'cached_status':status,'classification':'Unplanned paused mode; real-time criterion becomes indeterminate, not silently credited as evolving.'};unexpected_pauses.append(unexpected);emit({'kind':'unplanned_paused_owner_sample',**unexpected})
                if free<p['minimum_free_disk_bytes']or resource.get('working_set_bytes',0)>p['maximum_process_RAM_bytes']:raise RuntimeError('Declared equipment resource boundary reached; not a cognitive failure')
            time.sleep(.1)
        summary['host_seconds_from_owner_ready_to_horizon']=time.monotonic()-origin;stop_clients.set();[t.join(10)for t in threads];controls.join(10)
        deadline=time.monotonic()+p['maximum_drain_seconds']
        while time.monotonic()<deadline and any(r['status']in('queued','processing')for r in db.outstanding()):
            if owner.poll()is not None:break
            time.sleep(.2)
        summary['preclose_owner']=db.get_meta('owner');summary['remaining_before_close']=db.outstanding();control(prefix+'final_pause','pausar')
        summary['final_paired_export']=control(prefix+'final_export','exportar');control(prefix+'final_save','guardar');control(prefix+'final_stop','detener');owner.wait(timeout=30)
        summary['owner_returncode']=owner.returncode;summary['final_owner']=db.get_meta('owner');summary['transport_counts']=db.counters()
        with db.connect()as con:rows=[dict(r)for r in con.execute('SELECT * FROM requests ORDER BY seq')]
        summary['auto_pausing_failed_or_uncertain_rows']=[{'id':r['id'],'status':r['status'],'error':r['error']}for r in rows if r['id'].startswith(prefix)and r['status']in('failed_preserved','uncertain')]
        with gzip.GzipFile(filename=str(out/'REGISTROS_TRANSPORTE.json.gz'),mode='wb',mtime=0)as f:f.write((json.dumps(rows,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
        after=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes());summary['final']={k:after.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical','operation_count_offset')};summary['final_VIDA_bytes']=(system/'estado/vidas'/life/'VIDA.json').stat().st_size
    except Exception as error:
        summary['error']={'type':type(error).__name__,'detail':str(error)};emit({'kind':'harness_or_process_error','error':summary['error']})
        stop_clients.set()
        if owner and owner.poll()is None and db:
            try:control(prefix+'emergency_stop','detener',timeout=60);owner.wait(timeout=30)
            except Exception as stop_error:summary['own_owner_stop_error']=str(stop_error)
        if db:summary['final_observed_owner']=db.get_meta('owner');summary['pending_preserved']=db.outstanding()
    finally:
        stop_clients.set();log.flush();os.fsync(log.fileno());log.close()
    summary['technical_errors']=errors;summary['host_seconds_total']=time.monotonic()-started;summary['pause_intervals']=pause_intervals
    summary['conservative_pause_reload_discount_seconds']=sum(i['discount_seconds']for i in pause_intervals)
    summary['unpaused_operational_seconds_lower_estimate']=summary.get('host_seconds_from_owner_ready_to_horizon',0)-summary['conservative_pause_reload_discount_seconds']
    summary['unexpected_paused_owner_samples']=unexpected_pauses
    summary['unplanned_pause_excluded_or_indeterminate']=bool(unexpected_pauses or summary.get('auto_pausing_failed_or_uncertain_rows'))
    summary['sixty_unpaused_minutes_reached']=summary['unpaused_operational_seconds_lower_estimate']>=3600 and len(pause_intervals)==3 and not errors and not summary.get('error')and not summary['unplanned_pause_excluded_or_indeterminate']and not summary.get('remaining_before_close')
    summary['final_source_integrity']=[{**identity,'unchanged':sha(system/identity['file'])==identity['sha256']}for identity in sources]
    summary['all_frozen_source_bytes_unchanged']=all(i['unchanged']for i in summary['final_source_integrity'])
    summary['scope']='Actual executed times/counts only. Queue rejection is not native rejection; silence is not replaced by an intelligent action. All repeated queries belong to one life, not independent learners. Native reproducibility and causal learning require their separate controls.'
    (out/'RESULTADO.json').write_text(json.dumps(summary,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'result':str(out/'RESULTADO.json'),'error':summary.get('error'),'technical_errors':errors,'host_seconds':summary['host_seconds_total'],'unpaused_seconds':summary['unpaused_operational_seconds_lower_estimate'],'counts':summary.get('transport_counts')}));return bool(summary.get('error')or errors or not summary['sixty_unpaused_minutes_reached']or not summary['all_frozen_source_bytes_unchanged'])


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--protocolo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True)
    a=p.parse_args()
    return execute(a.sistema,a.protocolo,a.salida)


if __name__=='__main__':raise SystemExit(main())
