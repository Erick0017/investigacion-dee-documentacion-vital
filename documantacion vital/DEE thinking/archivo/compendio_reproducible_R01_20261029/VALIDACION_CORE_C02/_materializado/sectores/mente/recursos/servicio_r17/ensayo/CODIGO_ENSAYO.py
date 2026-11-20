"""R04 R3P0 prospective busy/idle service trial, exclusive fi60r3_ IDs.

Derived from the archived R11 harness, not a repeated R11 run or a new T0.
3720s fixed horizon; fresh raw3/64/126, explicit beta-plus to minus teaching.

The caller explicitly selects one existing life/backend. No target, expected sign,
answer-driven curriculum or external policy chooses a native action.
"""
import argparse,importlib.util,sqlite3,ctypes,gzip,hashlib,json,os,queue,random,shutil,subprocess,sys,threading,time
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cola_local import QueueDB


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(path,life,contexts,seed,count=480,seconds=3720):
    if seconds<3600:raise ValueError('The final protocol cannot label a short window as sixty minutes.')
    if count!=480 or contexts!=['alfa','beta','gamma','delta','epsilon','zeta']:raise ValueError('R04 freezes480 opportunities and six admitted literal P0 contexts.')
    rng=random.Random(seed);events=[];sizes=(160,160,160)
    chain_cases=[('gamma',[23,4]),('epsilon',[5,24]),('zeta',[18,3])]
    for regime,(begin,end,n)in enumerate(zip((5,1100,2300),(1090,2290,3490),sizes),1):
        for i in range(n):
            t=begin+(end-begin)*(i+.1+.7*rng.random())/max(1,n)
            if 1730<t<1890:t=1730+(t-1730)*.01 if t<1800 else 1890+(t-1800)*.01
            index=len(events)
            position=i%24;context,values=chain_cases[(regime-1+(i//24))%3]
            if position==9 and i+3<n-6:row={'modo':'cadena-iniciar','contexto':context,'valores':values}
            elif position==12:row={'modo':'cadena-finalizar'}
            elif position in(1,5,15,21):row={'modo':'dato','valor':(13,32,11,29)[(1,5,15,21).index(position)]}
            elif position%3==0:row={'modo':'memoria','contexto':contexts[(regime+i//3)%len(contexts)]}
            elif position%7==0:row={'modo':'usar'}
            else:row={'modo':'trabajo','valores':([3,11]if index%2 else[23,4]),'dominio':'trabajadores'}
            if i<6 or i>=n-6:row={'modo':'memoria','contexto':contexts[i%6]}
            if i in(30,66,102,138):
                components=[0]*128;components[0]=19;extra=(None,3,64,126)[(30,66,102,138).index(i)]
                if extra is not None:components[extra]=2
                row={'modo':'crudos','componentes':components}
            events.append({'at_seconds':round(t,6),'regime':regime,'client':index%2,'id':'fi60r3_'+str(index).zfill(5),'payload':{'operacion':'sesion','situaciones':[row]}})
    events.sort(key=lambda x:x['at_seconds'])
    for when,row,label in[(1750,{'modo':'cadena-iniciar','contexto':'gamma','valores':[23,4]},'pending_chain_begin'),(1870,{'modo':'cadena-finalizar'},'pending_chain_finish'),(1910,{'modo':'memoria','contexto':'beta','operacion_memoria':'revisar','senal':-1},'declared_beta_revision')]:
        candidates=[e for e in events if e.get('fixed_purpose')is None and e['payload']['situaciones'][0]['modo']not in('cadena-iniciar','cadena-finalizar')]
        e=min(candidates,key=lambda e:abs(e['at_seconds']-when));e.update(at_seconds=when,fixed_purpose=label,payload={'operacion':'sesion','situaciones':[row]})
    events.sort(key=lambda x:x['at_seconds'])
    for e in events:e['payload']['retorno']='omit'
    opened=False
    for event in events:
        mode=event['payload']['situaciones'][0]['modo']
        if mode=='cadena-iniciar':
            if opened:raise ValueError('Protocol contains overlapping operator chain stages; fix before any native tick.')
            opened=True
        elif mode=='cadena-finalizar':
            if not opened:raise ValueError('Protocol contains an unpaired operator chain finish; fix before any native tick.')
            opened=False
    if opened:raise ValueError('Protocol ends with an unintentionally unmatched operator chain.')
    protocol={'schema':'DEE.unified.persistent_sixty_minute_prospective.v2','life_id':life,'backend':'mente_unificada','seconds':seconds,
        'private_auditor_seed':seed,'events':events,'nominal_events':len(events),'request_prefix':'fi60r3_','initial_memory_signs':{'alfa':-1,'beta':1,'gamma':1,'delta':-1,'epsilon':-1,'zeta':1},'requires_prepared_phase_protection':'MUFI01.sensor_calendar.R3P0','regimes':[{'id':i+1,'scheduled_events':sizes[i]}for i in range(3)],
        'contexts_explicit_P0':contexts,'idle_interval_seconds':.1,'idle_quantum_ticks':1,'save_seconds':60,
        'technical_pause_windows':[600,1800,3000],'pause_seconds_after_actual_safe_boundary':3,
        'burst_at_first_pause':14,'burst_material_capacity':8,'paired_export_at_second_pause_with_one_literal_pending_input':True,'same_life_owner_process_restart_at_second_pause':True,
        'reserved_public_chain_cases':[{'contexto':c,'valores':v}for c,v in chain_cases],
        'datum_values':[13,32,11,29],'declared_single_beta_revision':{'at_seconds':1910,'senal':-1,'scope':'Explicit new teaching, not retained old beta knowledge or learned initiative.'},
        'raw128_frames_per_regime':4,'raw128_layouts':{'baseline':{'component0':19,'others':0},'variants':{'component0':19,'additional_value':2,'additional_indices':[3,64,126]},'new_layouts':'Prospective3/64/126 in the R3 continuation; shared R11 ancestry, not independent new lives.'},
        'chain_stage_calendar':'Fixed two explicit user requests even if preparation fails; no success-based skip, retry, favorable-reader switch or hidden repair.',
        'return_scope':'Local work return omitted explicitly to isolate operational retention. Actual prepared artifact bytes are still sensed by chain-finalizar. The one beta revision is an explicit teaching event, not learned control policy.',
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
    if p.get('schema')!='DEE.unified.persistent_sixty_minute_prospective.v2'or p['seconds']<3600:raise ValueError('Final frozen sixty-minute R04 R3P0 protocol required')
    if p.get('request_prefix')!='fi60r3_'or life!='MU_MAIN_FASE_R3'or any(not e['id'].startswith('fi60r3_')for e in p['events']):raise ValueError('R04 requires its explicit new identity and IDs; never deduplicate against inherited R11')
    if(system/'estado/locks'/(life+'.lock')).exists():raise ValueError('Life has another writer; do not interrupt it')
    shutil.copyfile(protocol_path,out/'PROTOCOLO.json');shutil.copyfile(Path(__file__),out/'CODIGO_ENSAYO.py')
    record=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes());before={k:record.get(k)for k in('life_id','world_id','profile','parent','snapshot','snapshot_sha256','physical')};del record
    spec=importlib.util.spec_from_file_location('read_only_R3_preflight',system/'capacidades/observador_causal_retrospectivo_01.py');obs=importlib.util.module_from_spec(spec);spec.loader.exec_module(obs);snapshot=obs.Snapshot(system/before['snapshot']);prepared=json.loads(snapshot.metadata['DEE.Cognitive.System.1.1.MENTE_UNIFICADA_01.v1']).get('phase_protection',{})
    if not prepared.get('enabled')or prepared.get('version')!=p['requires_prepared_phase_protection']:raise ValueError('Declared R3P0 preparation absent; never install it silently or change protocol during evaluation')
    with sqlite3.connect((system/'estado/servicios_persistentes'/life/'cola.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        if any(r[0].startswith(p['request_prefix'])for r in c.execute('SELECT id FROM requests')):raise ValueError('R04 transport prefix already used; preserve prior future, do not replay it')
    del snapshot
    sources=[]
    for rel in('gestionar.py','app/lives.py','app/cola_local.py','app/servicio_persistente.py','app/cliente_mente_unificada.py','app/finalizar_protocolo.py','app/importacion_emparejada.py','capacidades/mente_unificada_01.py','capacidades/mente_acumulativa_r02.py','capacidades/percepcion_cruda_fi01.py','capacidades/selector_acrecion_nativo.py','capacidades/eo02_trabajador_local.py'):
        f=system/rel;target=out/'codigo'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);sources.append({'file':rel,'bytes':f.stat().st_size,'sha256':sha(f)})
    (out/'FUENTES_Y_CORTE_ANTES_DEL_PRIMER_TICK.json').write_text(json.dumps({'utc':now(),'protocol_sha256':sha(protocol_path),'harness_sha256':sha(Path(__file__)),'source_record':before,'sources':sources,'native_ticks_at_preparation':0},sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    log=(out/'ADMISIONES_Y_EVENTOS.jsonl').open('x',encoding='utf8');mutex=threading.Lock();errors=[];stop_clients=threading.Event();planned_restart=threading.Event();clients=[queue.Queue(),queue.Queue()];owner=None;db=None;origin=None;owner_index=0
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
    def launch_owner(*,paused=False,remaining=None):
        nonlocal owner,owner_index,db
        for identity in sources:
            if sha(system/identity['file'])!=identity['sha256']:raise ValueError('Frozen source changed; no silent interface/reader substitution during an executed reserve.')
        owner_index+=1
        argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend',p['backend'],'--intervalo',str(p['idle_interval_seconds']),'--ticks-ocio',str(p['idle_quantum_ticks']),'--guardar-cada',str(p['save_seconds']),'--max-segundos',str(remaining or p['seconds']+p['maximum_drain_seconds']+180)]
        if paused:argv+=['--pausado']
        launch_wall=time.time()
        owner=subprocess.Popen(argv,stdout=(out/('OWNER_'+str(owner_index)+'_STDOUT.txt')).open('x',encoding='utf8'),stderr=(out/('OWNER_'+str(owner_index)+'_STDERR.txt')).open('x',encoding='utf8'),text=True,encoding='utf8')
        deadline=time.monotonic()+60;path=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
        while time.monotonic()<deadline:
            if owner.poll()is not None:raise RuntimeError('Explicit owner failed before readiness')
            if path.is_file():
                db=QueueDB(path);status=db.get_meta('owner')
                if status and status.get('running')and status.get('wall_utc')and datetime.fromisoformat(status['wall_utc']).timestamp()>=launch_wall:
                    emit({'kind':'owner_process_ready','index':owner_index,'launcher_pid':owner.pid,'status':status,'planned_restart':planned_restart.is_set()});return status
            time.sleep(.1)
        raise TimeoutError('Native owner startup')
    def technical_windows():
        try:
            for index,at in enumerate(p['technical_pause_windows']):
                while not stop_clients.is_set()and time.monotonic()-origin<at:time.sleep(.2)
                if stop_clients.is_set():break
                paused=control('fi60r3_pause_'+str(index),'pausar');started_pause=time.monotonic()
                if index==0:
                    for i in range(p['burst_at_first_pause']):clients[i%2].put({'id':'fi60r3_burst_'+str(i),'client':i%2,'payload':{'operacion':'sesion','situaciones':[{'modo':'usar'}]}})
                if index==1:
                    admission({'id':'fi60r3_pending_export','client':'technical','payload':{'operacion':'sesion','situaciones':[{'modo':'usar'}]}})
                    exported=control('fi60r3_export_pending','exportar');emit({'kind':'paired_pending_export','value':exported})
                saved=control('fi60r3_pause_witness_'+str(index),'guardar')
                emit({'kind':'pause_exact_boundary_comparison','pause_tick':paused['after_tick'],'saved_tick':saved['after_tick'],'equal':paused['after_tick']==saved['after_tick']})
                if index==1:
                    planned_restart.set();stopped=control('fi60r3_midpoint_stop','detener');old_pid=owner.pid;owner.wait(timeout=60)
                    before_restart=saved['committed_snapshot'];launch_owner(paused=True,remaining=p['seconds']-(time.monotonic()-origin)+p['maximum_drain_seconds']+180)
                    after_restart=control('fi60r3_midpoint_reloaded_witness','guardar')['committed_snapshot']
                    emit({'kind':'same_life_full_state_process_reload','old_launcher_pid':old_pid,'new_launcher_pid':owner.pid,'before':before_restart,'after':after_restart,
                        'physical_equal':before_restart['physical']==after_restart['physical'],
                        'pending_protocol_equal':before_restart.get('operational_dependencies')==after_restart.get('operational_dependencies'),
                        'pending_transport_row':db.get('fi60r3_pending_export'),'no_material_action_retried':True})
                    planned_restart.clear()
                while time.monotonic()-started_pause<p['pause_seconds_after_actual_safe_boundary']:time.sleep(.1)
                control('fi60r3_resume_'+str(index),'reanudar')
        except Exception as error:errors.append({'phase':'technical_windows','type':type(error).__name__,'detail':str(error)});emit({'kind':'technical_window_error','error':errors[-1]})
        finally:planned_restart.clear()
    started=time.monotonic();summary={'schema':'DEE.unified.persistent_sixty_minute_result.v1','before':before,'protocol_sha256':sha(protocol_path),'sources':sources};threads=[]
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
                for i,payload in enumerate(({'operacion':'sesion','situaciones':[]},{'operacion':'sesion','situaciones':[{'modo':'usar','target':1}]},{'operacion':'guardar','shell':'do_not_execute'},{'operacion':'sesion','situaciones':[{'modo':'memoria','contexto':'fuera_dominio'}]})):
                    admission({'id':'fi60r3_invalid_'+str(i),'client':'technical','payload':payload})
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
        summary['preclose_owner']=db.get_meta('owner');summary['remaining_before_close']=db.outstanding();control('fi60r3_final_pause','pausar')
        summary['final_paired_export']=control('fi60r3_final_export','exportar');control('fi60r3_final_save','guardar');control('fi60r3_final_stop','detener');owner.wait(timeout=30)
        summary['owner_returncode']=owner.returncode;summary['final_owner']=db.get_meta('owner');summary['transport_counts']=db.counters()
        with db.connect()as con:rows=[dict(r)for r in con.execute('SELECT * FROM requests ORDER BY seq')]
        with gzip.GzipFile(filename=str(out/'REGISTROS_TRANSPORTE.json.gz'),mode='wb',mtime=0)as f:f.write((json.dumps(rows,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
        after=json.loads((system/'estado/vidas'/life/'VIDA.json').read_bytes());summary['final']={k:after.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical','operation_count_offset')}
    except Exception as error:
        summary['error']={'type':type(error).__name__,'detail':str(error)};emit({'kind':'harness_or_process_error','error':summary['error']})
        stop_clients.set()
        if owner and owner.poll()is None and db:
            try:control('fi60r3_emergency_stop','detener',timeout=60);owner.wait(timeout=30)
            except Exception as stop_error:summary['own_owner_stop_error']=str(stop_error)
        if db:summary['final_observed_owner']=db.get_meta('owner');summary['pending_preserved']=db.outstanding()
    finally:
        stop_clients.set();log.flush();os.fsync(log.fileno());log.close()
    summary['technical_errors']=errors;summary['host_seconds_total']=time.monotonic()-started
    summary['final_source_integrity']=[{**identity,'unchanged':sha(system/identity['file'])==identity['sha256']}for identity in sources]
    summary['scope']='Actual executed times/counts only. Queue rejection is not native rejection; silence is not replaced by an intelligent action. All repeated queries belong to one life, not independent learners. Native reproducibility and causal learning require their separate controls.'
    (out/'RESULTADO.json').write_text(json.dumps(summary,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({'result':str(out/'RESULTADO.json'),'error':summary.get('error'),'host_seconds':summary['host_seconds_total'],'counts':summary.get('transport_counts')}));return bool(summary.get('error'))


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('preparar');q.add_argument('--salida',type=Path,required=True);q.add_argument('--vida',required=True);q.add_argument('--contextos',default='alfa,beta,gamma,delta,epsilon,zeta');q.add_argument('--semilla',type=int,default=2602511);q.add_argument('--cantidad',type=int,default=480);q.add_argument('--segundos',type=int,default=3720)
    q=sub.add_parser('ejecutar');q.add_argument('--sistema',type=Path,required=True);q.add_argument('--protocolo',type=Path,required=True);q.add_argument('--salida',type=Path,required=True)
    a=p.parse_args()
    if a.command=='preparar':print(json.dumps(prepare(a.salida,a.vida,a.contextos.split(','),a.semilla,a.cantidad,a.segundos)));return 0
    return execute(a.sistema,a.protocolo,a.salida)


if __name__=='__main__':raise SystemExit(main())
