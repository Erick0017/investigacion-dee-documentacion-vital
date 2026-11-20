"""Portable APD real-time and transport-mode accounting, no native replay."""
import argparse,gzip,hashlib,json
from datetime import datetime
from pathlib import Path

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stamp(value):return datetime.fromisoformat(value)

def calculate(root):
    result=json.loads((root/'RESULTADO.json').read_bytes());protocol=json.loads((root/'PROTOCOLO.json').read_bytes());events=[json.loads(x)for x in(root/'ADMISIONES_Y_EVENTOS.jsonl').read_text(encoding='utf8').splitlines()if x.strip()]
    rows=json.loads(gzip.decompress((root/'REGISTROS_APD.json.gz').read_bytes()))
    prefix=protocol['request_prefix'];inherited_ids={r['id']for r in protocol.get('inherited_pending_rows',[])};controls={e['id']:json.loads(e['record']['result'])for e in events if e['kind']=='technical_control_result'};intervals=[];issues=[]
    checks={}
    def check(label,ok):
        checks[label]=bool(ok)
        if not ok:issues.append(label)
    for i in range(3):
        pause=controls.get(prefix+'pause_'+str(i));resume=controls.get(prefix+'resume_'+str(i))
        if not pause or not resume:
            issues.append('missing_complete_pause_resume_interval_'+str(i));continue
        start=stamp(pause['started_utc']);end=stamp(resume['finished_execution_utc']);duration=(end-start).total_seconds()
        intervals.append({'pause':pause['id'],'resume':resume['id'],'discount_start_utc':start.isoformat(),'discount_end_utc':end.isoformat(),'discount_seconds':duration,'pause_tick':pause['after_tick'],'resume_tick':resume['before_tick']})
        check('nonnegative_pause_'+str(i),duration>=0);check('no_native_ticks_inside_pause_'+str(i),pause['after_tick']==resume['before_tick'])
    selected=[r for r in rows if r['id'].startswith(prefix)or r['id']in inherited_ids]
    autopausing=[{'id':r['id'],'status':r['status']}for r in selected if r['status']in('failed_preserved','uncertain')]
    initial_resume=controls.get(prefix+'initial_resume');initial_resume_utc=stamp(initial_resume['finished_execution_utc'])if initial_resume else None
    unplanned=[];cached_before_initial_resume=[]
    for e in events:
        if e['kind']!='passive_resource_and_cached_owner':continue
        status=e['status']
        if not status.get('paused'):continue
        t=stamp(status['wall_utc'])
        if initial_resume_utc is not None and t<=initial_resume_utc:
            cached_before_initial_resume.append({'observed_at_seconds':e['at_seconds'],'cached_wall_utc':status['wall_utc'],'scope':'Cached paused status predates the completed explicit initial resume; not an extra physical pause.'});continue
        if not any(stamp(i['discount_start_utc'])<=t<=stamp(i['discount_end_utc'])for i in intervals):
            unplanned.append({'observed_at_seconds':e['at_seconds'],'cached_wall_utc':status['wall_utc'],'native_tick':status.get('tick'),'uncertain':status.get('uncertain_external_result')})
    elapsed=result.get('host_seconds_from_owner_ready_to_horizon',0);discount=sum(i['discount_seconds']for i in intervals)
    active=elapsed-discount if len(intervals)==3 else None
    check('fixed_frozen_horizon_reached',protocol['seconds']==4500 and elapsed>=protocol['seconds'])
    check('fresh_exclusive_APD_prefix',prefix=='apd62_'and all(e['id'].startswith(prefix)for e in protocol['events']))
    check('120_frozen_opportunities',protocol['nominal_events']==len(protocol['events'])==120)
    check('protocol_exact_SHA',sha(root/'PROTOCOLO.json')==result['protocol_sha256'])
    check('no_technical_or_harness_error',not result.get('error')and not result.get('technical_errors'))
    check('no_unplanned_or_auto_pausing_failure',not unplanned and not autopausing)
    check('at_least_sixty_unpaused_operational_minutes',active is not None and active>=3600 and not unplanned and not autopausing)
    if result.get('final'):
        check('same_actual_life_world_and_parent',all(result['before'][k]==result['final'][k]for k in('life_id','world_id','parent')))
        check('actual_native_world_advanced',result['final']['physical']['tick']>result['before']['physical']['tick'])
    else:check('completed_final_saved_cut_present',False)
    check('no_unresolved_queue_or_uncertainty',not result.get('remaining_before_close')and not result.get('final_owner',{}).get('uncertain_external_result',True))
    check('owner_gracefully_stopped',result.get('owner_returncode')==0 and result.get('final_owner',{}).get('running')is False)
    jobs=result.get('actual_owned_job_resources',[])
    job_trees_clean=len(jobs)==2 and all(r['resource'].get('job_active_processes')==0 for r in jobs)
    checks['two_owned_jobs_recorded_after_processes_exited']=job_trees_clean
    operational_issues=[]if job_trees_clean else[{'criterion':'two_owned_jobs_recorded_after_processes_exited','recorded':jobs,'scope':'Original criterion remains false. Both Jobs recorded one active process immediately after launcher.wait before close_job. Late exit versus KILL_ON_JOB_CLOSE is unresolved; never relabelled clean. Durable postSTOP integrity is checked separately.'}]
    check('hard_memory_budget512MiB_for_both_jobs',len(jobs)==2 and all(r['resource'].get('job_memory_limit')==protocol['maximum_process_RAM_bytes']for r in jobs))
    check('no_forced_job_termination_or_wait_failure',not result.get('forced_owned_job_termination')and not result.get('owned_job_wait_error'))
    for source in result['sources']:
        check('archived_source_'+source['file'],sha(root/'codigo'/source['file'])==source['sha256'])
    check('frozen_sources_unchanged_after_reserve',all(s['unchanged']for s in result.get('final_source_integrity',[])))
    reloads=[e for e in events if e['kind']=='same_life_full_state_process_reload']
    check('one_process_reload',len(reloads)==1)
    if reloads:
        r=reloads[0];before=r['before'];after=r['after']
        check('reload_exact_physical_fields',before['physical']==after['physical'])
        check('reload_exact_environment_and_external_protocol',before['operational_dependencies']==after['operational_dependencies'])
        check('reload_actual_complete_FIFO_rows',r.get('pending_transport_rows_before')==r.get('pending_transport_rows_after'))
        check('no_cascade_invented_or_required',protocol['pending_contract']=='REAL_FIFO_AND_OPERATIONAL_STATE_WITHOUT_REQUIRED_CASCADE'and r['required_cascade']is False)
    samples=[e for e in events if e['kind']=='passive_resource_and_cached_owner']
    ram=[e['process']['working_set_bytes']for e in samples if 'working_set_bytes'in e['process']];peaks=[e['process']['peak_working_set_bytes']for e in samples if 'peak_working_set_bytes'in e['process']]
    size=[e['VIDA_bytes']for e in samples if 'VIDA_bytes'in e]
    return {'schema':'DEE.APD01.real_operational_time_accounting.v1','sources':[{'file':name,'sha256':sha(root/name)}for name in('RESULTADO.json','PROTOCOLO.json','ADMISIONES_Y_EVENTOS.jsonl','REGISTROS_APD.json.gz')],
        'issues':issues,'operational_issues':operational_issues,'clean_closure':job_trees_clean and not result.get('forced_owned_job_termination')and not result.get('owned_job_wait_error'),'checks':checks,'fixed_horizon_seconds':elapsed,'conservative_pause_reload_discount_seconds':discount,'unpaused_operational_seconds':active,
        'pause_intervals':intervals,'unplanned_paused_samples':unplanned,'auto_pausing_failed_or_uncertain_rows':autopausing,
        'cached_paused_samples_before_initial_resume':cached_before_initial_resume,
        'sampled_memory':{'samples':len(ram),'maximum_working_set_bytes':max(ram)if ram else None,'maximum_recorded_peak_bytes':max(peaks)if peaks else None,'budget_bytes':protocol['maximum_process_RAM_bytes'],'CPU_integral_measured_for_owned_process_jobs':bool(jobs)and all(all(isinstance(row['resource'].get(k),(int,float))and not isinstance(row['resource'].get(k),bool)for k in('cpu_user_seconds','cpu_kernel_seconds'))for row in jobs)},
        'actual_owned_job_resources':result.get('actual_owned_job_resources',[]),
        'VIDA_sizes':{'minimum_sampled_bytes':min(size)if size else None,'maximum_sampled_bytes':max(size)if size else None,'initial_bytes':result.get('initial_VIDA_bytes'),'final_bytes':result.get('final_VIDA_bytes')},
        'idle_ticks_added':result.get('final_owner',{}).get('idle_ticks',0)-result.get('initial_owner',{}).get('idle_ticks',0),
        'scope':'Real host time in enabled native-evolution mode, not nonstop CPU time, simulated DEE time or 24/7 stability. Entire technical pause/export/reload spans are discounted. Unknown extra pauses invalidate the sixty-minute claim rather than being credited. No engine, new ticks, policy or repaired result.'}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();r=calculate(a.evidencia);a.salida.parent.mkdir(parents=True,exist_ok=True)
    with a.salida.open('x',encoding='utf8')as f:json.dump(r,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'issues':r['issues'],'unpaused_seconds':r['unpaused_operational_seconds'],'RAM':r['sampled_memory']}));return bool(r['issues'])
if __name__=='__main__':raise SystemExit(main())
