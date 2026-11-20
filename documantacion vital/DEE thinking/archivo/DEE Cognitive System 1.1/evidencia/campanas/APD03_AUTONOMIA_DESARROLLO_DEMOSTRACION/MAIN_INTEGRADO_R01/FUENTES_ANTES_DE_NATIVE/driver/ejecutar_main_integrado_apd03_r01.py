"""APD03 MAIN driver: literal curriculum through the existing single-entry UI.

No engine/actor import, Runtime construction, answer, route or repair decision.
Only the existing Supervisor/OriginalBackend own evolution and transport.
"""
import argparse
import ctypes
from datetime import datetime,timezone
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys
import time


def read(path):return json.loads(Path(path).read_bytes())
def sha(path):
    digest=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):digest.update(block)
    return digest.hexdigest()
def now():return datetime.now(timezone.utc).isoformat()
def emit(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    data=(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8')
    with path.open('xb') as stream:stream.write(gzip.compress(data,mtime=0) if path.suffix=='.gz' else data)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def unwrap(value):return value.get('request') or value
def decoded(value):
    result=unwrap(value).get('result')
    return json.loads(result) if isinstance(result,str) else result


def job_measure(pc,handle):
    if not pc or not handle:return None
    result=pc.job_resources(handle);extended=pc.Extended()
    if pc.K.QueryInformationJobObject(handle,9,ctypes.byref(extended),ctypes.sizeof(extended),None):
        result['job_io']={name:int(getattr(extended.IoInfo,name)) for name,_ in pc.IO._fields_}
    result['instrument_scope']='Actual owned Native Job tree, CPU cumulative seconds and I/O counters. Not host/DEE energy.'
    return result


def stopped_pair(root,ui,life,target,*,allow_queued,scope):
    """N0 adaptation of the APD02 exact-postSTOP sealer, no owner reload."""
    system=root/'sistema';record=read(system/'estado/vidas'/life/'VIDA.json')
    if (system/'estado/locks'/(record['world_id']+'.lock')).exists():raise ValueError('World still locked; no live journal copying')
    side=system/'estado'/record['persistent_service']['sidecar_directory']
    worker=system/'estado'/record['persistent_service']['worker_directory']
    journal=side/'cola.sqlite3';wal=journal.with_name(journal.name+'-wal')
    if wal.exists() and wal.stat().st_size:raise ValueError('Nonempty WAL must not be omitted or silently checkpointed')
    before=sha(journal)
    with sqlite3.connect(journal.as_uri()+'?mode=ro&immutable=1',uri=True) as con:
        if con.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Stopped journal integrity failure')
        owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        con.row_factory=sqlite3.Row
        outstanding=[dict(row) for row in con.execute("SELECT * FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq")]
    if owner.get('running') is not False:raise ValueError('No confirmed STOP; never label a live cut as stopped')
    if any(row['status']!='queued' for row in outstanding) or (outstanding and not allow_queued):
        raise ValueError('Unresolved processing/uncertain transport is preserved, not sealed as a clean usable cut')
    observer=ui.load_module('apd03_offline_snapshot_only',system/'capacidades/observador_causal_retrospectivo_01.py')
    native=system/record['snapshot'];snapshot=observer.Snapshot(native)
    protocol=json.loads(snapshot.metadata.get('DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1','{}'))
    actual={'N':snapshot.N,'tick':snapshot.tick,'RAW_sha256':observer.sha(observer.pbytes(snapshot.raw)),
        'clocks_sha256':observer.sha(observer.pbytes(snapshot.clocks))}
    if snapshot.encoded_sha256!=record['snapshot_sha256'] or any(actual[key]!=record['physical'][key] for key in actual):
        raise ValueError('PostSTOP current snapshot/pointer differs')
    if snapshot.pending or protocol.get('native_tick_at_checkpoint')!=snapshot.tick or protocol.get('closed_epoch'):
        raise ValueError('Do not omit a native agenda or change the open protocol epoch')
    target.mkdir(parents=True,exist_ok=False);files=[(native,'VIDA.deetsnap.gz'),(journal,'cola.sqlite3')]
    for base,prefix in((side/'resultados','resultados'),(worker,'artefactos_trabajador')):
        for path in sorted(base.rglob('*')):
            if path.is_file():
                if path.is_symlink() or not path.resolve().is_relative_to(base.resolve()):raise ValueError('No operational external link followed')
                files.append((path,prefix+'/'+path.relative_to(base).as_posix()))
    members=[]
    for source,name in files:
        digest=sha(source);destination=target/name;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,destination)
        if sha(source)!=digest or sha(destination)!=digest:raise ValueError('Stopped operational source changed during copy')
        members.append({'file':name,'source_system_relative':source.relative_to(system).as_posix(),'bytes':source.stat().st_size,'sha256':digest})
    manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':life,'world_id':record['world_id'],
        'profile':record['profile'],'backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz',
        'snapshot_sha256':record['snapshot_sha256'],'physical':record['physical'],'members':members,
        'queue_journal_required':True,'source_record':{'life_id':life,'world_id':record['world_id'],'parent':record.get('parent')},
        'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,'scope':scope}
    emit(target/'EXPORTACION_SERVICIO.json',manifest)
    validator=ui.load_module('apd03_existing_pair_validator',system/'app/importacion_emparejada.py')
    _,_,proof=validator.verify_export(target)
    if sha(journal)!=before:raise ValueError('N0 sealer altered original transport')
    return {'directory':str(target),'manifest_sha256':sha(target/'EXPORTACION_SERVICIO.json'),
        'record':record,'snapshot_summary':snapshot.summary(),'protocol':protocol,'owner':owner,
        'outstanding':outstanding,'verification':proof,'new_native_ticks_in_sealing':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    parser.add_argument('--root-go',required=True,choices=['APD03_MAIN_R01_REVIEWED_ONLY'])
    args=parser.parse_args();root=args.root.resolve();system=root/'sistema';out=args.out.resolve()
    if out.exists():raise FileExistsError('New evidence directory only; do not overwrite a life trajectory')
    plan_path=Path(__file__).with_name('PROGRAMA_MAIN_INTEGRADO_R01.json');plan=read(plan_path)
    deadline=datetime.fromisoformat(plan['deadline_utc'].replace('Z','+00:00')).timestamp()
    if time.time()+plan['evolving_window_minimum_seconds']+900>=deadline:raise ValueError('Insufficient authorized wall budget; no new owner started')
    out.mkdir(parents=True)
    ui_path=system/'app/usar_dee.py';ui=load('apd03_exact_existing_ui',ui_path)
    if any(name.startswith('dee_thinking') for name in sys.modules):raise RuntimeError('Driver unexpectedly imported engine')
    config_path=ui.selected_config_path(root);config=read(config_path);life=plan['life']
    if config['memory_limit_bytes']!=536870912 or config['owner_max_seconds']<4500:raise ValueError('Predeclared owner resources do not cover this window')
    backend=ui.OriginalBackend(root,config);session=ui.Supervisor(root,life,backend,config)
    initial=backend.record(life)
    if initial['snapshot_sha256']!=plan['initial_imported_snapshot_sha256'] or initial['physical']['tick']!=plan['initial_tick'] or initial['parent'].get('encoded_sha256')!=plan['parent_snapshot_sha256']:
        raise ValueError('The designated current paired import changed; do not substitute another past')
    if not session.state_path.is_file() or session.state.get('world_id')!=initial['world_id'] or session.state.get('source_snapshot_sha256')!=plan['parent_snapshot_sha256']:
        raise ValueError('Root must register the existing paired life with UI; never import another copy silently')
    paths=[Path(__file__),plan_path,ui_path,config_path,system/'gestionar.py',
        system/'capacidades/observador_causal_retrospectivo_01.py',system/'app/importacion_emparejada.py']
    paths+=sorted((system/'app').rglob('*.py'));paths+=sorted((system/'capacidades').rglob('*.py'))
    paths=list(dict.fromkeys(path.resolve() for path in paths));sources=[]
    for index,path in enumerate(paths):
        relative=path.relative_to(system) if path.is_relative_to(system) else Path('driver')/path.name
        destination=out/'FUENTES_ANTES_DE_NATIVE'/relative;destination.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(path,destination)
        sources.append({'source':str(path),'file':destination.relative_to(out).as_posix(),'bytes':path.stat().st_size,'sha256':sha(path)})
    protected_paths=[system/'estado/ACTIVO.json',system/'estado/vidas/APD02_MAIN/VIDA.json',system/read(system/'estado/vidas/APD02_MAIN/VIDA.json')['snapshot']]
    protected=[{'path':str(path),'sha256':sha(path)} for path in protected_paths]
    emit(out/'ANTES_DEL_PRIMER_TICK.json',{'plan':plan,'root_go':args.root_go,'config':config,
        'sources':sources,'initial_record':initial,'ui_protocol':session.state,'protected':protected,
        'native_not_started':True,'energy':'NO MEDIDA','parent_driver_pid':__import__('os').getpid()})
    events=[];heartbeats=[];blocks=[];counter=0;window_start=None;window_end=None
    error=None;first_cut=None;final_cut=None;main_job_query=None;job_pc=None;startup=None;stop_result=None
    child_ui=None;child_streams=[];child_job_query=None;child_pc=None;continuation=None;forced_child_cleanup=None
    ui_journal=session.folder/'SESIONES.jsonl';ui_offset=ui_journal.stat().st_size if ui_journal.exists() else 0
    began=time.monotonic();driver_cpu_start=time.process_time_ns();last_heartbeat=0

    def sources_unchanged():return all(sha(row['source'])==row['sha256'] for row in sources)
    def metrics():return job_measure(job_pc,main_job_query)
    def append_event(kind,body):
        index=len(events);record={'index':index,'kind':kind,'wall_utc':now(),
            'driver_elapsed_seconds':time.monotonic()-began,**body}
        events.append(record);emit(out/'EVENTOS'/(str(index).zfill(3)+'_'+kind+'.json.gz'),record);return record
    def control(operation):
        before=metrics();t=time.monotonic_ns();cpu=time.process_time_ns()
        value=session.control(operation)
        append_event('control',{'operation':operation,'result':value,'elapsed_ns':time.monotonic_ns()-t,
            'driver_cpu_ns':time.process_time_ns()-cpu,'job_before':before,'job_after':metrics()})
        return value
    def material(tag,situations,feedback='real'):
        nonlocal counter
        counter+=1;request_id='apd03main_r01_'+str(counter).zfill(3)+'_'+tag
        before=metrics();t=time.monotonic_ns();cpu=time.process_time_ns()
        value=session.material(situations,feedback=feedback,actuator='closed',request_id=request_id)
        terminal=unwrap(value);polls=[];limit=time.monotonic()+plan['transport_result_limit_seconds']
        while terminal.get('status') not in ui.TERMINAL:
            if str(value.get('admission','')).startswith('rejected'):raise RuntimeError('Literal request was rejected; preserve, no retry: '+request_id)
            if time.monotonic()>limit or time.time()>=deadline-90:raise TimeoutError('Pending same ID preserved without re-put: '+request_id)
            time.sleep(.25);value=session.result(request_id);terminal=unwrap(value)
            polls.append({'wall_utc':now(),'status':terminal.get('status'),'id':request_id})
        record=append_event('material',{'tag':tag,'id':request_id,'literal_situations':situations,'feedback':feedback,
            'transport_result':value,'decoded_result':decoded(value),'read_only_same_ID_polls':polls,
            'elapsed_ns':time.monotonic_ns()-t,'driver_cpu_ns':time.process_time_ns()-cpu,
            'job_before':before,'job_after':metrics()})
        if terminal['status']!='completed':raise RuntimeError('Adverse/uncertain transport result preserved: '+request_id+' '+terminal['status'])
        return record
    def checkpoint(tag):
        control('guardar');card=backend.record(life);target=out/'CHECKPOINTS'/tag;target.mkdir(parents=True)
        shutil.copyfile(system/card['snapshot'],target/'VIDA.deetsnap.gz');emit(target/'VIDA.json',card)
        append_event('checkpoint',{'tag':tag,'record':card,'copied_snapshot_sha256':sha(target/'VIDA.deetsnap.gz'),
            'scope':'Complete native checkpoint; live transport remains with the owning service, not an independent paired export'})
        return card
    def heartbeat(force=False):
        nonlocal last_heartbeat
        if force or time.monotonic()-last_heartbeat>=plan['heartbeat_maximum_seconds']:
            t=time.monotonic_ns();value=session.status();row={'wall_utc':now(),
                'enabled_elapsed_seconds':None if window_start is None else time.monotonic()-window_start,
                'cached_status':value,'job':metrics(),'instrumentation_elapsed_ns':time.monotonic_ns()-t}
            heartbeats.append(row);emit(out/'HEARTBEATS'/(str(len(heartbeats)).zfill(4)+'.json.gz'),row)
            print(json.dumps({'heartbeat':len(heartbeats),'enabled_seconds':row['enabled_elapsed_seconds'],
                'cached_tick':ui.observation(value['ESTADO_PUBLICADO']).get('tick')}),flush=True);last_heartbeat=time.monotonic()
    def wait_until(target):
        while time.monotonic()<target:
            if time.time()>=deadline-900:raise TimeoutError('Campaign closing reserve reached; no automatic extension')
            heartbeat();time.sleep(min(5,max(0,target-time.monotonic())))

    try:
        with ui.SessionLock(backend.protocol_home/life/'SUPERVISOR.lock'):
            session.open(new=False);t=time.monotonic_ns();startup=session.start();job_pc=backend.pc
            main_job_query=job_pc.K.OpenJobObjectW(0x0004,False,startup['job_name'])
            if not main_job_query:raise RuntimeError('Cannot observe own existing Job resources')
            append_event('start_paused',{'start':startup,'elapsed_ns':time.monotonic_ns()-t,'job':metrics()})
            control('reanudar')
            for event in plan['prelude']:material(event['id'],event['situations'],event['feedback'])
            control('pausar');checkpoint('ADMITTED_BEFORE_RESERVED_WINDOW')
            if not sources_unchanged():raise RuntimeError('Source freeze breached before reserved window')
            control('reanudar');window_start=time.monotonic();emit(out/'INICIO_VENTANA_CONGELADA.json',{
                'wall_utc':now(),'monotonic':window_start,'minimum_seconds':plan['evolving_window_minimum_seconds'],
                'owner':startup,'source_hashes':sources,'no_more_engineering_during_window':True})
            for block in plan['blocks']:
                wait_until(window_start+block['at_seconds'])
                if not sources_unchanged():raise RuntimeError('Frozen actor/source changed during reserved use')
                block_before=metrics();block_started=time.monotonic();first_event=len(events)
                for event in block['events']:
                    if event['kind']=='goal':
                        material(event['id']+'_init',[{'modo':'apd03-tarea-iniciar','texto':event['text'],
                            'operandos':event['operands'],'segundo_visible':event['visible'],'contexto_ambiente':event['context']}],event['feedback'])
                        material(event['id']+'_offered',[{'modo':'apd03-paso','oportunidades':event['opportunities']}],event['feedback'])
                    else:material(event['id'],event['situations'],event['feedback'])
                checkpoint(block['id']);heartbeat(force=True)
                blocks.append({'id':block['id'],'scheduled_seconds':block['at_seconds'],
                    'actual_start_enabled_seconds':block_started-window_start,'actual_end_enabled_seconds':time.monotonic()-window_start,
                    'events':[first_event,len(events)],'job_before':block_before,'job_after':metrics()})
                emit(out/'BLOQUES'/(block['id']+'.json'),blocks[-1])
            wait_until(window_start+plan['evolving_window_minimum_seconds']);window_end=time.monotonic()
            emit(out/'FIN_VENTANA_CONGELADA.json',{'wall_utc':now(),'monotonic':window_end,
                'actual_enabled_seconds':window_end-window_start,'job':metrics(),'owner':startup,
                'sources_unchanged':sources_unchanged(),'not_a_global_cognitive_verdict':True})
            # Pending goal and transport are prepared only AFTER the full
            # evolving window; a new UI process must consume this exact ID.
            after=plan['after_window'];goal=after['goal']
            material('pending_goal_init',[{'modo':'apd03-tarea-iniciar','texto':goal['text'],
                'operandos':goal['operands'],'segundo_visible':goal['visible'],'contexto_ambiente':goal['context']}])
            material('pending_goal_first_op',[{'modo':'apd03-paso','oportunidades':after['first_opportunity_budget']}])
            control('pausar');checkpoint('PENDING_GOAL_BEFORE_STOP')
            previous_wait=session.config['material_wait_seconds'];session.config['material_wait_seconds']=plan['queueing_wait_seconds']
            try:queued=session.material(after['queued_situations'],request_id=after['queued_request_id'])
            finally:session.config['material_wait_seconds']=previous_wait
            exact_pending=session.result(after['queued_request_id'])
            if unwrap(exact_pending).get('status')!='queued':raise ValueError('Expected exact queued material while paused; preserve actual state')
            append_event('intentional_pending_transport',{'admission':queued,'actual_same_ID_row':exact_pending,
                'queued_ID':after['queued_request_id'],'supervisor_protocol':session.state,
                'predeclared_wait_seconds':plan['queueing_wait_seconds'],'no_re_put':True})
            checkpoint('EXACT_QUEUED_ID_BEFORE_STOP');control('detener')
            append_event('first_owner_closed',{'job_final':metrics(),'state':session.state})
            if metrics()['job_active_processes']!=0:raise RuntimeError('Own first job still active')
            first_cut=stopped_pair(root,ui,life,out/'PAR_POSTSTOP_PENDIENTE',allow_queued=True,
                scope='Exact reached APD03 state after >=60min with one queued goal step preserved; no native reload in sealing')
            if len(first_cut['outstanding'])!=1 or first_cut['outstanding'][0]['id']!=after['queued_request_id']:
                raise ValueError('Pending cut does not contain exactly the intended same ID')
            emit(out/'CORTE_PENDIENTE_POSTSTOP.json',first_cut)
        # A genuinely new ordinary UI process (and its own Native child) opens
        # --vida. Only readiness and the already queued ID are polled here.
        panel_file=out/'PANEL_CONTINUACION_LITERAL.json';emit(panel_file,after['continuation_material'])
        child_streams=[(out/'UI_CONTINUACION_STDOUT.txt').open('x',encoding='utf8'),(out/'UI_CONTINUACION_STDERR.txt').open('x',encoding='utf8')]
        command=[str(backend.python),'-I','-B','-X','utf8',str(ui_path),'--raiz',str(root),'--vida',life]
        child_offset=ui_journal.stat().st_size if ui_journal.exists() else 0
        child_ui=subprocess.Popen(command,cwd=backend.python.parent,stdin=subprocess.PIPE,stdout=child_streams[0],stderr=child_streams[1],text=True,encoding='utf8',creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        opened_at=time.time();readiness=[];ready=None;limit=time.monotonic()+config['start_wait_seconds']+30
        while time.monotonic()<limit:
            if child_ui.poll() is not None:raise RuntimeError('Second ordinary UI exited before readiness')
            value=ui.observation(backend.manager(['mente-unificada-estado','--vida',life]));readiness.append(value)
            if value.get('running') and value.get('paused') and value.get('wall_utc') and datetime.fromisoformat(value['wall_utc']).timestamp()>=opened_at:
                ready=value;break
            time.sleep(.25)
        if ready is None:raise TimeoutError('Second UI owner readiness missing; no replacement')
        # A read-only query handle preserves whole-Job CPU/I/O accounting even
        # after the genuine UI closes its own owner handle. No new Job/world.
        child_pc=ui.load_module('apd03_child_job_query_only',system/'app/process_control.py')
        start_event=None;log_limit=time.monotonic()+5
        while start_event is None and time.monotonic()<log_limit:
            with ui_journal.open('rb') as stream:stream.seek(child_offset);new_lines=stream.read().decode('utf8').splitlines()
            starts=[json.loads(line) for line in new_lines if line and json.loads(line).get('event')=='owned_start_paused']
            if starts:start_event=starts[-1]
            else:time.sleep(.1)
        if start_event is None:raise RuntimeError('Second UI owned Job identity was not logged')
        # QUERY | TERMINATE applies only to the Job named by this exact child
        # UI's owned_start_paused receipt. TERMINATE is reserved for the final
        # bounded technical guard, never a decision or arbitrary Job lookup.
        child_job_query=child_pc.K.OpenJobObjectW(0x000C,False,start_event['job_name'])
        if not child_job_query:raise RuntimeError('Cannot observe the actual second Native Job')
        child_job_before=job_measure(child_pc,child_job_query)
        for key in('tick','RAW_sha256','clocks_sha256'):
            actual=ready['tick'] if key=='tick' else ready['physical'][key]
            if actual!=first_cut['record']['physical'][key]:raise ValueError('Second owner changed physical state before resume: '+key)
        commands=['reanudar'];child_ui.stdin.write('reanudar\n');child_ui.stdin.flush()
        pending_id=after['queued_request_id'];polls=[];limit=time.monotonic()+plan['transport_result_limit_seconds'];value=None
        while time.monotonic()<limit:
            if child_ui.poll() is not None:raise RuntimeError('Second UI exited while same ID was pending')
            value=backend.manager(['mente-unificada-resultado','--vida',life,'--id',pending_id]);row=unwrap(value)
            polls.append({'wall_utc':now(),'status':row.get('status'),'id':row.get('id'),'payload_sha':row.get('payload_sha')})
            if row.get('status') in ui.TERMINAL:break
            time.sleep(.5)
        if not value or unwrap(value).get('status')!='completed':raise RuntimeError('Same queued ID was not completed; never re-put')
        old=first_cut['outstanding'][0];new=unwrap(value)
        if any(new[key]!=old[key] for key in('id','payload','payload_sha','arrived_utc','seq')):raise ValueError('Queued identity/payload/arrival changed across processes')
        tail=['resultado '+pending_id,'evento "'+panel_file.as_posix()+'"','guardar','detener','salir']
        commands+=tail;child_ui.stdin.write('\n'.join(tail)+'\n');child_ui.stdin.flush();child_ui.stdin.close()
        limit=time.monotonic()+600
        while child_ui.poll() is None and time.monotonic()<limit:
            if time.time()>=deadline-90:raise TimeoutError('Campaign deadline during ordinary continuation')
            time.sleep(.5)
        if child_ui.poll() is None:raise TimeoutError('Second UI did not close within fixed continuation guard')
        for stream in child_streams:stream.close()
        if child_ui.returncode:raise RuntimeError('Second UI exited with adverse status; preserve stdout/stderr and state')
        continuation={'command':command,'UI_pid':child_ui.pid,'returncode':child_ui.returncode,'literal_stdin':commands,
            'readiness_samples':readiness,'ready_before_new_input':ready,'same_queued_ID_result':value,
            'read_only_polls':polls,'same_original_queue_row_fields_preserved':True,
            'source_Main_not_reimported':True,'new_native_owner_PID':ready['pid'],
            'native_job_before':child_job_before,'native_job_after':job_measure(child_pc,child_job_query)}
        if continuation['native_job_after']['job_active_processes']!=0:raise RuntimeError('Second UI left a Native process in its owned Job')
        emit(out/'CONTINUACION_OTRO_PROCESO.json.gz',continuation)
        final_cut=stopped_pair(root,ui,life,out/'PAR_POSTSTOP_FINAL',allow_queued=False,
            scope='Actual final reached APD03 state after ordinary UI continuation, same queued request consumed once, no restore or teaching reset')
        emit(out/'CORTE_FINAL_POSTSTOP.json',final_cut)
    except Exception as caught:
        error={'type':type(caught).__name__,'detail':str(caught),'wall_utc':now(),
            'no_retry_no_rewind':True,'same_supervisor_pending':session.state.get('pending_material')}
        emit(out/'ERROR_PRESERVADO.json',error)
    finally:
        try:
            if session.owned:stop_result=session.close()
        except Exception as caught:
            error=error or {'type':'StopNotConfirmed','detail':str(caught),'no_other_owner_terminated':True}
        if child_ui is not None and child_ui.poll() is None:
            # Only our identified UI/Native descendant receives this technical
            # STOP. No retry of material work or another owner's termination.
            cleanup_started=time.monotonic()
            try:
                if child_ui.stdin is not None and not child_ui.stdin.closed:
                    child_ui.stdin.write('detener\nsalir\n');child_ui.stdin.flush();child_ui.stdin.close()
                else:
                    backend.manager(['mente-unificada-detener','--vida',life,'--id','apd03_main_error_stop_only_01',
                        '--esperar','0.25'],timeout=5)
                close_limit=cleanup_started+60
                while child_ui.poll() is None and time.monotonic()<close_limit:time.sleep(.25)
                if child_ui.poll() is None:
                    # This is the exact Popen child created above, never an
                    # enumerated process or a protected/original owner.
                    forced_child_cleanup={'reason':'Own second UI failed technical STOP within60s',
                        'UI_pid':child_ui.pid,'native_job_before':job_measure(child_pc,child_job_query),
                        'host_process_cut_not_a_cognitive_failure':True,
                        'uncommitted_future_may_be_lost_keep_interruption_markers':True}
                    child_ui.terminate()
                    child_ui.wait(timeout=5)
                    # The read-only query handle can keep a KILL_ON_JOB_CLOSE
                    # Job alive after the UI dies, so explicitly end ONLY this
                    # already identified owned Native Job if it still runs.
                    if child_pc and child_job_query and job_measure(child_pc,child_job_query).get('job_active_processes'):
                        child_pc.terminate_job(child_job_query,124)
                        grace=time.monotonic()+5
                        while job_measure(child_pc,child_job_query).get('job_active_processes') and time.monotonic()<grace:time.sleep(.05)
                        forced_child_cleanup['native_job_after']=job_measure(child_pc,child_job_query)
                    error=error or {'type':'OwnChildForcedHostStop','detail':forced_child_cleanup['reason'],'no_material_retry':True}
            except Exception as caught:
                error=error or {'type':'SecondUIStopNotConfirmed','detail':str(caught),'no_material_retry':True}
            for stream in child_streams:
                if not stream.closed:stream.close()
        if main_job_query and job_pc:
            final_job=job_measure(job_pc,main_job_query);job_pc.close_job(main_job_query);main_job_query=None
        else:final_job=None
        child_job_final=job_measure(child_pc,child_job_query)
        if child_job_query and child_pc:child_pc.close_job(child_job_query);child_job_query=None
        if ui_journal.exists():
            with ui_journal.open('rb') as stream:stream.seek(ui_offset);journal_bytes=stream.read()
            with (out/'SESIONES_UI_NUEVAS.jsonl.gz').open('xb') as stream:stream.write(gzip.compress(journal_bytes,mtime=0))
        final_source_receipts=[{**row,'actual_sha256':sha(row['source']),'unchanged':sha(row['source'])==row['sha256']} for row in sources]
        protected_end=[{**row,'actual_sha256':sha(row['path']),'unchanged':sha(row['path'])==row['sha256']} for row in protected]
        result={'schema':'APD03.main_continuous_execution.R01','life':life,'plan':plan,
            'initial_record':initial,'startup':startup,'window_start_monotonic':window_start,'window_end_monotonic':window_end,
            'enabled_seconds':None if window_start is None or window_end is None else window_end-window_start,
            'events':events,'blocks':blocks,'heartbeats_count':len(heartbeats),'request_count':counter,
            'first_stopped_pending_cut':first_cut,'continuation':continuation,'final_stopped_cut':final_cut,
            'job_first_owner_final':final_job,'stop_on_error_result':stop_result,'error':error,
            'job_second_owner_final':child_job_final,
            'forced_child_cleanup':forced_child_cleanup,
            'sources':final_source_receipts,'sources_unchanged':all(row['unchanged'] for row in final_source_receipts),
            'protected_originals':protected_end,'protected_originals_unchanged':all(row['unchanged'] for row in protected_end),
            'driver_wall_seconds':time.monotonic()-began,'driver_cpu_ns':time.process_time_ns()-driver_cpu_start,
            'energy':'NO MEDIDA','native_engine_imported_in_driver':any(name.startswith('dee_thinking') for name in sys.modules),
            'scope':'One real MAIN history; literal opportunities are offered by the operator. Supervisors/queues/resources are external instrumentation, not a learned cognitive policy.'}
        emit(out/'REGISTROS_VENTANA.json.gz',result)
        print(json.dumps({'life':life,'enabled_seconds':result['enabled_seconds'],'error':error,
            'final_tick':None if final_cut is None else final_cut['record']['physical']['tick'],
            'requests':counter,'sources_unchanged':result['sources_unchanged'],
            'protected_unchanged':result['protected_originals_unchanged'],'wall_seconds':result['driver_wall_seconds']}),flush=True)
    return 1 if error else 0


if __name__=='__main__':raise SystemExit(main())
