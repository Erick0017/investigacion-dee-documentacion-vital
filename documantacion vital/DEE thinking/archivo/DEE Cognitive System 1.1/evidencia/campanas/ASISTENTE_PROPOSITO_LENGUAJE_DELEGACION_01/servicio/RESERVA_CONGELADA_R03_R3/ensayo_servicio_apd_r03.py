"""R03 prospective APD service: one existing world, bounded literal workload.

The calendar is fixed before execution. This is transport/time instrumentation,
not a policy: no numeric answer, useful route or response repair is computed.
Prior R01/R02 negative records are neither replaced nor credited as minutes.
"""
import argparse,gzip,hashlib,importlib.util,json,os,shutil,sqlite3,subprocess,sys,time
from datetime import datetime,timezone
from pathlib import Path

def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def load_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def execute(system,protocol_path,out):
    system=system.resolve();p=json.loads(protocol_path.read_bytes());life=p['life_id'];prefix=p['request_prefix'];out=out.resolve();out.mkdir(parents=True,exist_ok=False)
    if p['schema']!='DEE.APD01.prospective_service_curriculum.v2' or p['status']!='FROZEN_FOR_ONE_SELECTED_CANDIDATE' or prefix!='apd62_' or p['seconds']!=4500 or len(p['events'])!=120:raise ValueError('Exact R03 prospective fixed protocol required')
    if sha(Path(__file__))!=p['harness_sha256']:raise ValueError('Executed harness differs from its frozen source; no silent instrumentation revision')
    if p['pending_contract']!='REAL_FIFO_AND_OPERATIONAL_STATE_WITHOUT_REQUIRED_CASCADE':raise ValueError('No invented or mandatory cascade in this time reserve')
    budget_deadline=datetime.fromisoformat(p['budget_deadline_utc'])
    if (budget_deadline-datetime.now(timezone.utc)).total_seconds()<p['seconds']+p['maximum_closure_seconds']+p['owner_startup_allowance_seconds']:raise ValueError('Insufficient original budget; no reset')
    if not 1<=p['maximum_process_RAM_bytes']<=536870912:raise ValueError('Original memory bound')
    qm=load_module('apd_r03_queue',system/'app/cola_local.py');QueueDB=qm.QueueDB
    helper_path=Path(__file__).with_name('ensayo_servicio_apd_r02.py');helper=load_module('apd_r03_passive_helpers',helper_path)
    if sha(helper_path)!=p['passive_helper_sha256']:raise ValueError('Passive helper bytes differ')
    for e in p['events']:qm.validate_request(e['payload'])
    for value in (p['burst_payload'],p['pending_transport_payload'],p['inherited_finish']['payload']):qm.validate_request(value)
    if (system/'estado/locks'/(life+'.lock')).exists():raise ValueError('Another writer owns this life')
    record_path=system/'estado/vidas'/life/'VIDA.json';record=json.loads(record_path.read_bytes());before={k:record.get(k)for k in('life_id','world_id','profile','parent','snapshot','snapshot_sha256','physical')};del record
    cut=p['initial_cut']
    if before['life_id']!=cut['life_id']or before['physical']['tick']!=cut['tick']or before['physical']['N']!=cut['N']or before['snapshot_sha256']!=cut['snapshot_sha256']:raise ValueError('Wrong reached complete cut; no favorable substitution')
    queue_path=system/'estado/servicios_persistentes'/before['world_id']/'cola.sqlite3'
    if not queue_path.is_file():raise ValueError('Existing paired queue required')
    wal=queue_path.with_name(queue_path.name+'-wal')
    if wal.exists()and wal.stat().st_size:raise ValueError('Unresolved WAL; preserve, do not discard')
    with sqlite3.connect(queue_path.as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        c.row_factory=sqlite3.Row
        if any(r[0].startswith(prefix)for r in c.execute('SELECT id FROM requests')):raise ValueError('R03 prefix already used')
        inherited=[dict(r)for r in c.execute("SELECT * FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq")]
    if inherited!=p['inherited_pending_rows']or len(inherited)!=8 or any(r['status']!='queued'for r in inherited):raise ValueError('Eight original queued rows differ; no reissue or clearing')
    sources=[]
    for rel,digest in p['source_sha256'].items():
        src=(system/rel).resolve(strict=True)
        if not src.is_relative_to(system)or sha(src)!=digest:raise ValueError('Frozen source changed: '+rel)
        dst=out/'codigo'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst);sources.append({'file':rel,'sha256':digest,'bytes':src.stat().st_size})
    shutil.copyfile(protocol_path,out/'PROTOCOLO.json');shutil.copyfile(Path(__file__),out/'CODIGO_ENSAYO.py');shutil.copyfile(helper_path,out/'CODIGO_HELPER_PASIVO_R02.py')
    dump(out/'FUENTES_Y_CORTE_ANTES_DEL_PRIMER_TICK.json',{'utc':now(),'protocol_sha256':sha(protocol_path),'harness_sha256':sha(Path(__file__)),'sources':sources,'source_record':before,'native_ticks_at_preparation':0})
    log=(out/'ADMISIONES_Y_EVENTOS.jsonl').open('x',encoding='utf8');owner=None;db=None;origin=None;owner_index=0;pause_intervals=[];errors=[];unexpected_pauses=[];planned_pause=False;last_resume_utc=None
    service_deadline=time.monotonic()+p['owner_startup_allowance_seconds']+p['seconds']+p['maximum_closure_seconds']
    summary={'schema':'DEE.APD01.persistent_sixty_minute_result.v2','before':before,'protocol_sha256':sha(protocol_path),'sources':sources,'initial_VIDA_bytes':record_path.stat().st_size,'inherited_pending_rows_before_owner':inherited,'continuation_scope':p['continuation_scope']}
    def emit(value):log.write(json.dumps({'utc':now(),**value},sort_keys=True,ensure_ascii=False)+'\n');log.flush()
    def rows():
        with db.connect()as c:return [dict(r)for r in c.execute('SELECT * FROM requests ORDER BY seq')]
    def admission(event):
        try:
            reply=db.put(event['id'],event['payload']);emit({'kind':'admission','desired_seconds':event.get('at_seconds'),'actual_seconds':None if origin is None else time.monotonic()-origin,'client':event.get('client'),'id':event['id'],'payload':event['payload'],'reply':reply});return reply
        except Exception as error:emit({'kind':'transport_validation_rejection','id':event['id'],'payload':event['payload'],'type':type(error).__name__,'detail':str(error),'no_native_input':True});return None
    def wait_existing(identifier,timeout):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            row=db.get(identifier)
            if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):return row
            if owner.poll()is not None:raise RuntimeError('Owner exited while waiting for SAME admitted ID')
            time.sleep(.2)
        raise TimeoutError('Existing request did not reach terminal status: '+identifier)
    def control(identifier,operation):
        reply=db.put(identifier,{'operacion':operation});emit({'kind':'technical_control_admission','id':identifier,'operation':operation,'reply':reply})
        row=wait_existing(identifier,p['technical_control_wait_seconds']);emit({'kind':'technical_control_result','id':identifier,'record':row})
        if row['status']!='completed':raise RuntimeError('Technical control not completed; preserve actual result')
        return json.loads(row['result'])
    def launch_owner(paused):
        nonlocal owner,owner_index,db
        for item in sources:
            if sha(system/item['file'])!=item['sha256']:raise ValueError('Frozen S source changed; no runtime interface substitution')
        remaining=min(service_deadline-time.monotonic(),(budget_deadline-datetime.now(timezone.utc)).total_seconds())
        if remaining<=0:raise TimeoutError('Original shared deadline exhausted')
        owner_index+=1;launch_wall=time.time();env=dict(os.environ);env['OMP_NUM_THREADS']='1'
        argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--intervalo',str(p['idle_interval_seconds']),'--ticks-ocio',str(p['idle_quantum_ticks']),'--guardar-cada',str(p['save_seconds']),'--max-segundos',str(remaining)]
        if paused:argv+=['--pausado']
        owner=subprocess.Popen(argv,stdout=(out/f'OWNER_{owner_index}_STDOUT.txt').open('x',encoding='utf8'),stderr=(out/f'OWNER_{owner_index}_STDERR.txt').open('x',encoding='utf8'),env=env,text=True,encoding='utf8')
        end=time.monotonic()+p['owner_startup_allowance_seconds']
        while time.monotonic()<end:
            if owner.poll()is not None:raise RuntimeError('Owner failed before readiness')
            db=QueueDB(queue_path);status=db.get_meta('owner')
            if status and status.get('running')and datetime.fromisoformat(status['wall_utc']).timestamp()>=launch_wall:
                emit({'kind':'owner_process_ready','index':owner_index,'launcher_pid':owner.pid,'status':status})
                if status.get('uncertain_external_result'):raise ValueError('Uncertain actual side effect; no automatic retry')
                return status
            time.sleep(.2)
        raise TimeoutError('Owner startup')
    def pause_window(index):
        nonlocal planned_pause,last_resume_utc
        planned_pause=True;paused=None;resumed=None;window_error=None
        try:
            paused=control(prefix+'pause_'+str(index),'pausar')
            if index==0:
                for i in range(p['burst_at_first_pause']):admission({'id':prefix+'burst_'+str(i),'client':i%2,'payload':p['burst_payload']})
            if index==1:
                reply=admission({'id':prefix+'pending_export','client':'technical','payload':p['pending_transport_payload']})
                emit({'kind':'optional_pending_token_admission','reply':reply,'scope':'If capacity rejects it, preserve that negative; actual FIFO remains the boundary.'})
                exported=control(prefix+'export_pending','exportar');emit({'kind':'paired_pending_export','value':exported})
            saved=control(prefix+'pause_witness_'+str(index),'guardar');emit({'kind':'pause_exact_boundary_comparison','pause_tick':paused['after_tick'],'saved_tick':saved['after_tick'],'equal':paused['after_tick']==saved['after_tick']})
            if paused['after_tick']!=saved['after_tick']:raise ValueError('Pause native fields advanced')
            if index==1:
                fifo_before=[r for r in rows()if not r['is_control']and r['status']in('queued','processing','uncertain')]
                stopped=control(prefix+'midpoint_stop','detener');old_pid=owner.pid;owner.wait(timeout=60)
                before_restart=saved['committed_snapshot'];launch_owner(True);after_restart=control(prefix+'midpoint_reloaded_witness','guardar')['committed_snapshot']
                fifo_after=[r for r in rows()if not r['is_control']and r['status']in('queued','processing','uncertain')]
                if before_restart['physical']!=after_restart['physical']or before_restart['operational_dependencies']!=after_restart['operational_dependencies']or fifo_before!=fifo_after:raise ValueError('Paused physical, actual operational or FIFO state differs across process')
                emit({'kind':'same_life_full_state_process_reload','old_launcher_pid':old_pid,'new_launcher_pid':owner.pid,'before':before_restart,'after':after_restart,'physical_equal':True,'pending_protocol_equal':True,'pending_transport_rows_before':fifo_before,'pending_transport_rows_after':fifo_after,'no_material_action_retried':True,'required_cascade':False})
        except Exception as error:window_error={'phase':'technical_windows','type':type(error).__name__,'detail':str(error)};errors.append(window_error);emit({'kind':'technical_window_error','error':window_error})
        finally:
            # Never leave a live owner silently paused. Resume the SAME state or
            # abort the whole experiment; no inputs/answers are retried here.
            if paused and owner and owner.poll()is None:
                try:
                    resumed=control(prefix+'resume_'+str(index),'reanudar');last_resume_utc=resumed['finished_execution_utc']
                    span=(datetime.fromisoformat(last_resume_utc)-datetime.fromisoformat(paused['started_utc'])).total_seconds()
                    pause_intervals.append({'pause_id':paused['id'],'resume_id':resumed['id'],'discount_start_utc':paused['started_utc'],'discount_end_utc':last_resume_utc,'discount_seconds':span,'tick_preserved':paused['after_tick']==resumed['before_tick']})
                    if span<0 or not pause_intervals[-1]['tick_preserved']:raise ValueError('Invalid pause span')
                except Exception as error:
                    failure={'phase':'technical_resume','type':type(error).__name__,'detail':str(error)};errors.append(failure);emit({'kind':'technical_resume_error','error':failure});window_error=window_error or failure
            planned_pause=False
        if window_error:raise RuntimeError('Technical window failed; explicitly abort rather than remain paused')
    started=time.monotonic();next_event=0;next_pause=0;last_resource=-100;invalid_done=False;inherited_complete=False;finish_sent=False
    try:
        status=launch_owner(True);summary['initial_owner']=status
        resumed=control(prefix+'initial_resume','reanudar');last_resume_utc=resumed['finished_execution_utc'];origin=time.monotonic();summary['initial_resume']=resumed;emit({'kind':'owner_ready','launcher_pid':owner.pid,'status':status,'effective_resume':resumed})
        while time.monotonic()-origin<p['seconds']:
            elapsed=time.monotonic()-origin
            if owner.poll()is not None:raise RuntimeError('Owner exited before horizon; no auto restart')
            if not inherited_complete:
                prior=[db.get(r['id'])for r in inherited]
                if any(r['status']in('uncertain','failed_preserved')for r in prior):raise RuntimeError('Inherited execution failed/uncertain; no retry')
                inherited_complete=all(r['status']in('completed','rejected_invalid')for r in prior)
                if inherited_complete:
                    summary['inherited_pending_terminal_rows']=prior;emit({'kind':'inherited_pending_completed_once','rows':prior})
                    begin=next(r for r in prior if r['id']==p['inherited_finish']['begin_id']);result=json.loads(begin['result'])if begin.get('result')else{}
                    found=[]
                    def find(value):
                        if isinstance(value,dict):
                            if value.get('kind')=='assisted_chain_begin':found.append(value)
                            for child in value.values():find(child)
                        elif isinstance(value,list):
                            for child in value:find(child)
                    find(result)
                    finish_exists=[r for r in rows()if r['id']in p['inherited_finish']['prior_finish_ids']]
                    if finish_exists:raise ValueError('Unexpected already-admitted FINISH; preserve and diagnose before new action')
                    if len(found)==1 and found[0].get('next_stage_available'):
                        reply=admission(p['inherited_finish']);finish_sent=True
                        if not reply or reply.get('admission')!='queued':raise RuntimeError('Declared inherited FINISH not admitted; preserve without retry')
                        terminal=wait_existing(p['inherited_finish']['id'],p['inherited_finish']['wait_seconds']);summary['inherited_finish_result']=terminal;emit({'kind':'inherited_finish_result','record':terminal})
                        if terminal['status']!='completed':raise RuntimeError('Inherited FINISH failed/uncertain; no replay')
                    else:summary['inherited_finish_not_emitted']={'reason':'Existing BEGIN did not form one actual prepared chain','begin_status':begin['status'],'formed_chains':len(found)};emit({'kind':'inherited_finish_not_emitted',**summary['inherited_finish_not_emitted']})
                elif elapsed>p['inherited_completion_deadline_seconds']:raise TimeoutError('Original eight FIFO requests not completed before fixed boundary; preserve, do not discard')
            # Drain the eight already-admitted rows and any one genuine
            # inherited FINISH first. The public due time remains recorded;
            # no environment request is retried or selected from a response.
            while inherited_complete and next_event<len(p['events'])and p['events'][next_event]['at_seconds']<=elapsed:
                event=p['events'][next_event];admission(event);next_event+=1
            if next_pause<len(p['technical_pause_windows'])and elapsed>=p['technical_pause_windows'][next_pause]:pause_window(next_pause);next_pause+=1
            if not invalid_done and elapsed>=p['invalid_tests_at_seconds']:
                for i,payload in enumerate(p['invalid_payloads']):admission({'id':prefix+'invalid_'+str(i),'client':'technical','payload':payload})
                invalid_done=True
            if elapsed-last_resource>=10:
                status=db.get_meta('owner');resource=helper.process_resource(status['pid']);free=shutil.disk_usage(system).free;sizes=helper.passive_queue_size(queue_path)
                emit({'kind':'passive_resource_and_cached_owner','at_seconds':elapsed,'process':resource,'free_disk_bytes':free,'VIDA_bytes':record_path.stat().st_size,'queue_bytes':sizes['bytes'],'queue_size_observation':sizes,'status':status});last_resource=elapsed
                fresh=last_resume_utc is None or status.get('wall_utc','')>last_resume_utc
                if status.get('paused')and fresh and not planned_pause:
                    unexpected_pauses.append({'at_seconds':elapsed,'cached_status':status});emit({'kind':'unplanned_paused_owner_sample',**unexpected_pauses[-1]});raise RuntimeError('Unexpected paused owner: abort, never credit as evolving')
                if free<p['minimum_free_disk_bytes']or resource.get('working_set_bytes',0)>p['maximum_process_RAM_bytes']:raise RuntimeError('Real equipment resource boundary, not cognitive failure')
            time.sleep(.2)
        summary['host_seconds_from_owner_ready_to_horizon']=time.monotonic()-origin
        end=time.monotonic()+p['maximum_drain_seconds']
        while time.monotonic()<end and any(r['status']in('queued','processing')for r in db.outstanding()):time.sleep(.2)
        summary['preclose_owner']=db.get_meta('owner');summary['remaining_before_close']=db.outstanding();control(prefix+'final_pause','pausar');summary['final_paired_export']=control(prefix+'final_export','exportar');control(prefix+'final_save','guardar');control(prefix+'final_stop','detener');owner.wait(timeout=60)
    except Exception as error:
        summary['error']={'type':type(error).__name__,'detail':str(error)};emit({'kind':'harness_or_process_error','error':summary['error']})
        if owner and owner.poll()is None and db:
            try:control(prefix+'emergency_stop','detener');owner.wait(timeout=60)
            except Exception as stop_error:summary['own_owner_stop_error']=str(stop_error)
    finally:
        if db:
            summary['final_owner']=db.get_meta('owner');summary['pending_preserved']=db.outstanding();summary['transport_counts']=db.counters();allrows=rows()
            with gzip.GzipFile(filename=str(out/'REGISTROS_TRANSPORTE.json.gz'),mode='wb',mtime=0)as f:f.write((json.dumps(allrows,sort_keys=True,ensure_ascii=False,indent=2)+'\n').encode('utf8'))
            summary['auto_pausing_failed_or_uncertain_rows']=[{'id':r['id'],'status':r['status'],'error':r['error']}for r in allrows if r['id'].startswith(prefix)and r['status']in('failed_preserved','uncertain')]
        if owner:summary['owner_returncode']=owner.poll()
        after=json.loads(record_path.read_bytes());summary['final']={k:after.get(k)for k in('life_id','world_id','parent','snapshot','snapshot_sha256','physical','operation_count_offset')};summary['final_VIDA_bytes']=record_path.stat().st_size
        log.flush();os.fsync(log.fileno());log.close()
    summary['technical_errors']=errors;summary['host_seconds_total']=time.monotonic()-started;summary['pause_intervals']=pause_intervals;summary['conservative_pause_reload_discount_seconds']=sum(i['discount_seconds']for i in pause_intervals)
    summary['unpaused_operational_seconds_lower_estimate']=max(0,summary.get('host_seconds_from_owner_ready_to_horizon',0)-summary['conservative_pause_reload_discount_seconds']);summary['unexpected_paused_owner_samples']=unexpected_pauses
    summary['unplanned_pause_excluded_or_indeterminate']=bool(unexpected_pauses or summary.get('auto_pausing_failed_or_uncertain_rows'))
    summary['sixty_unpaused_minutes_reached']=summary['unpaused_operational_seconds_lower_estimate']>=3600 and len(pause_intervals)==3 and not errors and not summary.get('error')and not summary['unplanned_pause_excluded_or_indeterminate']
    summary['final_source_integrity']=[{**item,'unchanged':sha(system/item['file'])==item['sha256']}for item in sources];summary['all_frozen_source_bytes_unchanged']=all(i['unchanged']for i in summary['final_source_integrity'])
    summary['scope']='120 scheduled literal opportunities, finite public cost/teaching changes; actual admissions and physical outputs determine results. Inherited FIFO and its one declared FINISH are separate. R01/R02 minutes never count toward this reserve. No policy or favorable response is computed by this instrument.'
    dump(out/'RESULTADO.json',summary);print(json.dumps({'result':str(out/'RESULTADO.json'),'error':summary.get('error'),'unpaused_seconds':summary['unpaused_operational_seconds_lower_estimate'],'completed_criterion':summary['sixty_unpaused_minutes_reached']}));return bool(summary.get('error')or errors or not summary['sixty_unpaused_minutes_reached']or not summary['all_frozen_source_bytes_unchanged'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--sistema',type=Path,required=True);parser.add_argument('--protocolo',type=Path,required=True);parser.add_argument('--salida',type=Path,required=True);args=parser.parse_args();raise SystemExit(execute(args.sistema,args.protocolo,args.salida))
