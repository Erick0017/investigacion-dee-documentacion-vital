"""R04: one persistent owner,3720 enabled seconds,25 fixed literal requests.

No intermediate PAUSE, STOP, reload or export. The two final material panels
have exactly the prospectively approved payloads; their order is operator
assistance. Timing/capacity never select a useful answer or an alternative route.
"""
import argparse,gzip,hashlib,importlib.util,json,os,shutil,sqlite3,sys,time
from datetime import datetime,timezone
from pathlib import Path
def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,sort_keys=True,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def execute(system,protocol_path,out):
    p=json.loads(protocol_path.read_bytes());system=system.resolve();out.mkdir(parents=True,exist_ok=False);life=p['life_id'];prefix=p['request_prefix']
    if p['schema']!='DEE.APD01.single_owner_reserve.R04.v1'or p['status']!='FROZEN_FOR_ROOT_GO'or prefix!='apd63_'or p['seconds']!=3720 or len(p['events'])!=23 or sha(Path(__file__))!=p['harness_sha256']:raise ValueError('Exact prospective R04single-owner protocol required')
    if p['maximum_process_RAM_bytes']!=536870912 or p['maximum_closure_seconds']!=600 or p['source_sha256'].get('capacidades/asistente_proposito_01.py')!='fb93ee43d34ea88fb053f0b6a4e996d9aaf63981ec6edf76607c7271f1c4f86d':raise ValueError('Exact hard budget and the archived APD actor source are required')
    deadline=datetime.fromisoformat(p['budget_deadline_utc']);campaign_deadline_monotonic=time.monotonic()+(deadline-datetime.now(timezone.utc)).total_seconds()
    if(datetime.now(timezone.utc)-deadline).total_seconds()+p['seconds']+p['maximum_closure_seconds']+90>0:raise ValueError('Original campaign budget insufficient; no reset')
    card=system/'estado/vidas'/life/'VIDA.json';before=json.loads(card.read_bytes());cut=p['initial_cut']
    if before['snapshot_sha256']!=cut['snapshot_sha256']or before['physical']!=cut['physical']or before['life_id']!=life:raise ValueError('Actual reached R03cut differs; no favorable fallback')
    if(system/'estado/locks'/(before['world_id']+'.lock')).exists():raise ValueError('Another writer still owns the world')
    qpath=system/'estado/servicios_persistentes'/before['world_id']/'cola.sqlite3';wal=qpath.with_name(qpath.name+'-wal')
    if not qpath.is_file()or wal.exists()and wal.stat().st_size:raise ValueError('Complete settled paired journal required')
    with sqlite3.connect(qpath.as_uri()+'?mode=ro&immutable=1',uri=True)as c:
        if c.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]:raise ValueError('Actual pending rows must not be discarded for the new reserve')
        if any(r[0].startswith(prefix)for r in c.execute('SELECT id FROM requests')):raise ValueError('R04prefix already used; no replay')
    qm=module('r04_existing_queue',system/'app/cola_local.py');pc=module('r04_existing_process_owner',system/'app/process_control.py');helper_path=Path(__file__).with_name('ensayo_servicio_apd_r02.py');helper=module('r04_passive_helpers',helper_path)
    if sha(helper_path)!=p['passive_helper_sha256']:raise ValueError('Passive instrument differs')
    sources=[]
    for rel,digest in p['source_sha256'].items():
        f=system/rel
        if sha(f)!=digest:raise ValueError('Frozen source differs: '+rel)
        target=out/'codigo'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,target);sources.append({'file':rel,'sha256':digest,'bytes':f.stat().st_size})
    for event in p['events']+p['final_panels']:qm.validate_request(event['payload'])
    shutil.copyfile(protocol_path,out/'PROTOCOLO.json');shutil.copyfile(Path(__file__),out/'CODIGO_ENSAYO.py');shutil.copyfile(helper_path,out/'CODIGO_HELPER_PASIVO_R02.py')
    initial={k:before.get(k)for k in('life_id','world_id','profile','parent','snapshot','snapshot_sha256','physical')};write(out/'FUENTES_Y_CORTE_ANTES_DEL_PRIMER_TICK.json',{'utc':now(),'sources':sources,'source_record':initial,'protocol_sha256':sha(protocol_path),'harness_sha256':sha(Path(__file__)),'native_ticks_at_preparation':0})
    log=(out/'ADMISIONES_Y_EVENTOS.jsonl').open('x',encoding='utf8');owner=None;job=None;db=None;origin=None;closing_deadline=None;job_resource=None;errors=[];unexpected_pauses=[];observed_progress=[];records={};started=time.monotonic();summary={'schema':'DEE.APD01.single_owner_sixty_minute_result.R04.v1','before':initial,'sources':sources,'protocol_sha256':sha(protocol_path),'initial_VIDA_bytes':card.stat().st_size,'inherited_pending_rows_before_owner':[],'pause_intervals':[]}
    def emit(value):log.write(json.dumps({'utc':now(),**value},ensure_ascii=False,sort_keys=True)+'\n');log.flush()
    def wait(identifier,seconds=300):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            row=db.get(identifier)
            if row and row['status']in('completed','uncertain','failed_preserved','rejected_invalid'):
                if row['status']!='completed':raise RuntimeError('Same request failed/uncertain: '+identifier)
                return row
            if owner.poll()is not None:raise RuntimeError('Single owner exited; never start another within this reserve')
            time.sleep(.1)
        raise TimeoutError('Same admitted ID still unresolved: '+identifier)
    def control(identifier,operation):
        # One global closure deadline; each slow export/save does NOT receive a
        # new600second budget. Reserve60s for STOP and its own process exit.
        limit=campaign_deadline_monotonic if closing_deadline is None else closing_deadline
        reserve=0 if operation=='detener'else(60 if closing_deadline is not None else 0)
        remaining=min(p['control_wait_seconds'],limit-time.monotonic()-reserve)
        if remaining<=0:raise TimeoutError('One unchanged global closure/campaign deadline reached before '+operation)
        reply=db.put(identifier,{'operacion':operation});emit({'kind':'technical_control_admission','id':identifier,'operation':operation,'reply':reply,'remaining_global_seconds':limit-time.monotonic()});row=wait(identifier,remaining);records[identifier]=row;emit({'kind':'technical_control_result','id':identifier,'record':row});return json.loads(row['result'])
    def admit(event):
        reply=db.put(event['id'],event['payload']);emit({'kind':'admission','id':event['id'],'client':'single_fixed_calendar','desired_seconds':event.get('at_seconds'),'actual_seconds':time.monotonic()-origin,'payload':event['payload'],'reply':reply});return reply
    try:
        argv=[sys.executable,'-I','-B','-X','utf8',str(system/'gestionar.py'),'mente-unificada-iniciar','--vida',life,'--backend','mente_unificada','--pausado','--intervalo','.1','--ticks-ocio','1','--guardar-cada','60','--max-segundos',str(p['seconds']+p['maximum_closure_seconds']+90)];launch=time.time()
        owner,job,name=pc.spawn_owned(argv,cwd=system,stdout=(out/'OWNER_1_STDOUT.txt').open('x',encoding='utf8'),stderr=(out/'OWNER_1_STDERR.txt').open('x',encoding='utf8'),memory_limit=536870912);end=time.monotonic()+90
        emit({'kind':'owned_job_created','index':1,'launcher_pid':owner.pid,'job_name':name,'hard_memory_limit_bytes':536870912})
        while time.monotonic()<end:
            if owner.poll()is not None:raise RuntimeError('Owner failed before readiness')
            db=qm.QueueDB(qpath);status=db.get_meta('owner')
            if status and status.get('running')and datetime.fromisoformat(status['wall_utc']).timestamp()>=launch:summary['initial_owner']=status;break
            time.sleep(.1)
        else:raise TimeoutError('Single owner readiness')
        resumed=control(prefix+'initial_resume','reanudar');resume_finished=resumed['finished_execution_utc'];origin=time.monotonic();horizon_end=origin+p['seconds'];closing_deadline=min(horizon_end+p['maximum_closure_seconds'],campaign_deadline_monotonic);summary['initial_resume']=resumed;emit({'kind':'owner_ready','launcher_pid':owner.pid,'status':status,'effective_resume':resumed});next_event=0;last_resource=-100;post_first_attempted=False;post_second_attempted=False
        while time.monotonic()<horizon_end:
            elapsed=time.monotonic()-origin
            if owner.poll()is not None:raise RuntimeError('Single owner exited before3720s; no restart or minute aggregation')
            while next_event<len(p['events'])and p['events'][next_event]['at_seconds']<=elapsed:admit(p['events'][next_event]);next_event+=1
            if not post_first_attempted and elapsed>=3600:
                reply=admit(p['final_panels'][0]);post_first_attempted=True
                if reply.get('admission')!='queued':summary['post_first_not_admitted']=reply
            if post_first_attempted and not post_second_attempted:
                first=db.get(p['final_panels'][0]['id'])
                if first and first['status']=='completed':
                    reply=admit(p['final_panels'][1]);post_second_attempted=True
                    if reply.get('admission')!='queued':summary['post_second_not_admitted']=reply
                elif first and first['status']in('uncertain','failed_preserved','rejected_invalid'):raise RuntimeError('First postpanel did not complete; no repaired material input')
            if elapsed-last_resource>=10:
                state=db.get_meta('owner');resource=helper.process_resource(state['pid']);sizes=helper.passive_queue_size(qpath);free=shutil.disk_usage(system).free
                emit({'kind':'passive_resource_and_cached_owner','at_seconds':elapsed,'status':state,'process':resource,'VIDA_bytes':card.stat().st_size,'queue_bytes':sizes['bytes'],'queue_size_observation':sizes,'free_disk_bytes':free});last_resource=elapsed
                if state.get('wall_utc','')>resume_finished:observed_progress.append({k:state.get(k)for k in('pid','wall_utc','tick','idle_ticks','material_calls','runtime_loads_in_this_process','paused','running')})
                if state.get('paused')and state.get('wall_utc','')>resume_finished:unexpected_pauses.append(state);raise RuntimeError('Unplanned paused mode: no sixty-minute claim')
                if state.get('uncertain_external_result'):raise RuntimeError('Unknown external outcome: no automatic replay')
                if free<2147483648 or resource.get('working_set_bytes',0)>536870912:raise RuntimeError('Declared real equipment boundary reached')
            time.sleep(.2)
        summary['host_seconds_from_owner_ready_to_horizon']=time.monotonic()-origin;summary['horizon_reached_utc']=now();emit({'kind':'fixed_horizon_reached','enabled_seconds':summary['host_seconds_from_owner_ready_to_horizon'],'one_owner_required':True})
        # The second fixed panel is emitted only after the same first ID has
        # completed. A slow first panel is not duplicated under a new identity.
        if post_first_attempted and not post_second_attempted and not summary.get('post_first_not_admitted'):
            first=wait(p['final_panels'][0]['id'],max(.1,min(p['maximum_drain_seconds'],closing_deadline-time.monotonic()-60)));reply=admit(p['final_panels'][1]);post_second_attempted=True
            if reply.get('admission')!='queued':summary['post_second_not_admitted']=reply
        end=min(time.monotonic()+p['maximum_drain_seconds'],closing_deadline-60)
        while time.monotonic()<end and any(r['status']in('queued','processing')for r in db.outstanding()):
            if owner.poll()is not None:raise RuntimeError('Single owner died while draining; no replacement')
            time.sleep(.2)
        summary['remaining_before_close']=db.outstanding();summary['preclose_owner']=db.get_meta('owner');summary['final_pause']=control(prefix+'final_pause','pausar');summary['final_paired_export']=control(prefix+'final_export','exportar');control(prefix+'final_save','guardar');control(prefix+'final_stop','detener');owner.wait(timeout=max(.1,min(60,closing_deadline-time.monotonic())))
    except Exception as error:
        summary['error']={'type':type(error).__name__,'detail':str(error)};emit({'kind':'harness_or_process_error','error':summary['error']})
        if owner and owner.poll()is None and db:
            try:control(prefix+'emergency_stop','detener');owner.wait(timeout=max(.1,min(60,(closing_deadline or campaign_deadline_monotonic)-time.monotonic())))
            except Exception as stopping:summary['own_owner_stop_error']=str(stopping)
    finally:
        if job is not None:
            before_cleanup=pc.job_resources(job);summary['job_resources_after_graceful_attempt']=before_cleanup
            if owner.poll()is None or before_cleanup.get('job_active_processes',0):
                summary['forced_owned_job_termination']={'no_retry':True,'last_durable_cut_may_precede_partial_work':True,'resource_before':before_cleanup};pc.terminate_job(job,125)
                try:owner.wait(timeout=max(.1,min(60,(closing_deadline or campaign_deadline_monotonic)-time.monotonic())))
                except Exception as stop_error:summary['owned_job_wait_error']=str(stop_error)
            job_resource=pc.job_resources(job);pc.close_job(job)
        if db:
            summary['final_owner']=db.get_meta('owner');summary['pending_preserved']=db.outstanding();summary['transport_counts']=db.counters()
            with db.connect()as c:rows=[dict(r)for r in c.execute('SELECT * FROM requests ORDER BY seq')]
            with gzip.GzipFile(filename=str(out/'REGISTROS_TRANSPORTE.json.gz'),mode='wb',mtime=0)as f:f.write((json.dumps(rows,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf8'))
            summary['failed_or_uncertain_new_rows']=[{'id':r['id'],'status':r['status']}for r in rows if r['id'].startswith(prefix)and r['status']in('uncertain','failed_preserved')]
        after=json.loads(card.read_bytes());summary['final']={k:after.get(k)for k in('life_id','world_id','profile','parent','snapshot','snapshot_sha256','physical')};summary['final_VIDA_bytes']=card.stat().st_size;summary['owner_returncode']=owner.poll()if owner else None
        log.flush();os.fsync(log.fileno());log.close()
    summary['technical_errors']=errors;summary['unexpected_paused_owner_samples']=unexpected_pauses;summary['actual_owned_job_resources']=[{'owner_index':1,'reason':'final_close','resource':job_resource}];summary['host_seconds_total']=time.monotonic()-started;summary['unpaused_operational_seconds_lower_estimate']=summary.get('host_seconds_from_owner_ready_to_horizon',0);summary['conservative_pause_reload_discount_seconds']=0
    initial_pid=summary.get('initial_owner',{}).get('pid');all_pids={r['pid']for r in observed_progress}|{initial_pid,summary.get('final_owner',{}).get('pid')};summary['observed_native_progress']=observed_progress
    summary['one_native_owner_pid']=all_pids=={initial_pid}and initial_pid is not None;summary['all_cached_progress_nondecreasing']=all(b['tick']>=a['tick']and b['idle_ticks']>=a['idle_ticks']and b['material_calls']>=a['material_calls']for a,b in zip(observed_progress,observed_progress[1:]));summary['runtime_loaded_once_in_every_fresh_sample']=bool(observed_progress)and all(r['runtime_loads_in_this_process']==1 for r in observed_progress)
    summary['sixty_unpaused_minutes_reached']=summary['unpaused_operational_seconds_lower_estimate']>=3720 and summary['one_native_owner_pid']and summary['all_cached_progress_nondecreasing']and summary['runtime_loaded_once_in_every_fresh_sample']and not unexpected_pauses and not summary.get('failed_or_uncertain_new_rows')
    summary['host_closure_seconds_after_fixed_horizon']=max(0,time.monotonic()-horizon_end)if origin is not None else None;summary['global_closure_limit_seconds']=p['maximum_closure_seconds'];summary['original_campaign_deadline_utc']=p['budget_deadline_utc']
    summary['clean_closure']=not summary.get('error')and not summary.get('forced_owned_job_termination')and not summary.get('owned_job_wait_error')and job_resource is not None and job_resource.get('job_active_processes')==0 and summary.get('owner_returncode')==0 and summary.get('final_owner',{}).get('running')is False and not summary.get('pending_preserved')and summary['host_closure_seconds_after_fixed_horizon']is not None and summary['host_closure_seconds_after_fixed_horizon']<=p['maximum_closure_seconds']
    summary['sources_unchanged']=all(sha(system/r['file'])==r['sha256']for r in sources);summary['all_frozen_source_bytes_unchanged']=summary['sources_unchanged'];summary['final_source_integrity']=[{**r,'unchanged':sha(system/r['file'])==r['sha256']}for r in sources];summary['scope']='One actual3720-second enabled interval within one native PID. No pause, restart, export, branch replacement or old minutes during its horizon. Two final fixed material panels are part of this life, not a separate favorable snapshot.'
    write(out/'RESULTADO.json',summary);print(json.dumps({'result':str(out/'RESULTADO.json'),'error':summary.get('error'),'one_PID':summary['one_native_owner_pid'],'seconds':summary['unpaused_operational_seconds_lower_estimate'],'sixty_minutes':summary['sixty_unpaused_minutes_reached'],'clean_closure':summary['clean_closure']}));return bool(summary.get('error')or not summary['sixty_unpaused_minutes_reached']or not summary['clean_closure']or not summary['sources_unchanged'])
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--sistema',type=Path,required=True);p.add_argument('--protocolo',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();raise SystemExit(execute(a.sistema,a.protocolo,a.salida))
