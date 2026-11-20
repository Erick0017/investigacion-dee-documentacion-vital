"""Archived one-owner duration audit; no Runtime, live queue or extra observation."""
import argparse,datetime as dt,gzip,hashlib,json
from pathlib import Path

def read(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def seconds(a,b):return(dt.datetime.fromisoformat(b)-dt.datetime.fromisoformat(a)).total_seconds()
def calculate(x,protocol,logs):
    horizon=protocol['enabled_seconds'];timeline=x.get('owner_samples',[]);owners=[r['owner']for r in timeline if r.get('owner')];initial=x.get('owner_initial',{});final=x.get('owner_final',{});resume=x.get('resume');pause=x.get('pause');pids={r.get('pid')for r in owners}
    records={k:v for k,v in x.get('records',{}).items()if not k.endswith('_parsed')};controls=[{'id':l['id'],'operation':l['payload']['operacion'],'enabled_seconds':l.get('enabled_seconds')}for l in logs if l['payload']['operacion']!='sesion']
    sampled_ticks=[r['tick']for r in owners];sampled_idle=[r['idle_ticks']for r in owners];sampled_seconds=[r['seconds']for r in timeline if r.get('owner')];elapsed=x.get('enabled_seconds')
    control_order=[r['operation']for r in controls];epoch_set={r.get('epoch')for r in owners};record_epochs={json.loads(r['result']).get('owner_epoch')for r in records.values()if r.get('result')}
    checks={
      'protocol_requires_one_owner':protocol.get('one_owner_required')is True,
      'protocol_horizon_at_least3600':type(horizon)is int and horizon>=3600,
      'actual_monotonic_enabled_horizon_reached':type(elapsed)in(int,float)and elapsed>=horizon,
      'no_instrument_error':not x.get('error'),
      'nonvacuous_owner_samples':len(owners)>=2,
      'single_same_owner_PID':len(pids)==1 and None not in pids and initial.get('pid')in pids and final.get('pid')in pids,
      'one_runtime_load_in_process':all(r.get('runtime_loads_in_this_process')==1 for r in owners+[initial,final]),
      'one_transport_epoch':len(epoch_set)==1 and None not in epoch_set and initial.get('epoch')in epoch_set and final.get('epoch')in epoch_set and record_epochs<=epoch_set,
      'all_sampled_owners_running':bool(owners)and all(r.get('running')is True for r in owners),
      'all_sampled_owners_unpaused':bool(owners)and all(r.get('paused')is False for r in owners),
      'sample_times_ordered_within_window':all(0<=v<=elapsed for v in sampled_seconds)if type(elapsed)in(int,float)else False,
      'sample_times_monotonic':all(a<b for a,b in zip(sampled_seconds,sampled_seconds[1:])),
      'sample_ticks_monotonic':all(a<=b for a,b in zip(sampled_ticks,sampled_ticks[1:])),
      'physical_tick_progress_inside_window':len(sampled_ticks)>=2 and sampled_ticks[-1]>sampled_ticks[0],
      'idle_progress_inside_window':len(sampled_idle)>=2 and sampled_idle[-1]>sampled_idle[0],
      'idle_quantum_fixed1':protocol.get('idle_quantum_ticks')==1,
      'one_resume_only_no_intermediate_pause_stop_or_reload':control_order==['reanudar','pausar','exportar','detener'],
      'pause_only_after_whole_enabled_horizon':len(controls)>=2 and type(controls[1]['enabled_seconds'])in(int,float)and controls[1]['enabled_seconds']>=horizon,
      'one_original_world_and_life':x.get('initial',{}).get('life_id')==x.get('final',{}).get('life_id')==protocol['life']and x.get('initial',{}).get('world_id')==x.get('final',{}).get('world_id'),
      'exact_full_parent_cut':x.get('initial',{}).get('snapshot_sha256')==protocol['snapshot_sha256']and x.get('new_ticks_before_start')==0,
      'frozen_executed_sources_unchanged':x.get('sources_unchanged')is True
    }
    wall_enabled=seconds(resume['finished_execution_utc'],pause['started_utc'])if resume and pause else None
    if wall_enabled is not None:checks['wall_resume_completion_to_pause_at_least_horizon']=wall_enabled>=horizon
    clean={'owner_stopped':final.get('running')is False,'owned_process_exit_zero':x.get('owner_returncode')==0,'owned_job_active_zero':x.get('job_before_cleanup',{}).get('job_active_processes')==0,'no_forced_owned_job_cleanup':not x.get('forced_own_job_close',False),'no_pending_transport':x.get('pending')==[],'no_uncertain_effect':final.get('uncertain_external_result')is False}
    resources=x.get('job_before_cleanup',{});cpu_present=all(type(resources.get(k))in(int,float)for k in('cpu_user_seconds','cpu_kernel_seconds'));cache=[]
    if resume:
        start=dt.datetime.fromisoformat(resume['finished_execution_utc'])
        for row in timeline:
            owner=row.get('owner')
            if owner:cache.append({'seconds':row['seconds'],'owner_wall_utc':owner['wall_utc'],'approx_cache_age_seconds':(start+dt.timedelta(seconds=row['seconds'])-dt.datetime.fromisoformat(owner['wall_utc'])).total_seconds(),'tick':owner['tick'],'idle_ticks':owner['idle_ticks'],'pid':owner['pid'],'running':owner['running'],'paused':owner['paused']})
    return{'schema':'DEE.APD02.single_owner_duration_archived.R01','hour_criterion_supported':all(checks.values()),'issues':[k for k,v in checks.items()if not v],'checks':checks,'clean_closure_separate':{'supported':all(clean.values()),'checks':clean},'duration':{'planned_enabled_seconds':horizon,'recorded_monotonic_enabled_seconds':elapsed,'wall_resume_completion_to_pause_seconds':wall_enabled,'host_total_including_load_and_export_seconds':x.get('host_seconds'),'samples':len(owners),'first_sample_seconds':sampled_seconds[0]if sampled_seconds else None,'last_sample_seconds':sampled_seconds[-1]if sampled_seconds else None,'tick_delta_inside_sample_window':sampled_ticks[-1]-sampled_ticks[0]if sampled_ticks else None,'idle_delta_inside_sample_window':sampled_idle[-1]-sampled_idle[0]if sampled_idle else None,'idle_total_owner_delta_including_closure':final.get('idle_ticks',0)-initial.get('idle_ticks',0),'no_owner_duration_summing':True},'owner_identity':{'pids':sorted(pids,key=str),'epochs':sorted(epoch_set,key=str),'initial':initial,'final':final},'controls':controls,'samples':cache,'resources':{'cpu_integral_measured_from_owned_job':cpu_present,'job_aggregate_user_seconds':resources.get('cpu_user_seconds'),'job_aggregate_kernel_seconds':resources.get('cpu_kernel_seconds'),'peak_job_committed_bytes':resources.get('peak_job_committed_bytes'),'memory_limit_bytes':resources.get('job_memory_limit'),'scope':'Owned Job aggregate may include launcher/children. This is not DEE energy, cost feedback or a per-native-operation CPU attribution.'},'scope':'Only archived protocol, native transport receipts and cached owner samples are read. No live SQLite, Runtime, native query or new tick. Heartbeats are sampled cached witnesses, not continuous instantaneous tracing; their ages are reported. Whole-window continuity also relies on the exact executed single-owner source and absence of intermediate pause/stop/reload controls. Functional correctness, file quality, clean closure and the duration criterion are separate, not a global cognitive PASS.'}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--evidencia',type=Path,required=True);p.add_argument('--salida',type=Path,required=True);a=p.parse_args();root=a.evidencia;x=read(root/'REGISTROS_VENTANA.json.gz');protocol=read(root/'PROTOCOLO.json');logs=[json.loads(v)for v in(root/'ADMISIONES.jsonl').read_text(encoding='utf8').splitlines()if v];result=calculate(x,protocol,logs);result['primary_sha256']=sha(root/'REGISTROS_VENTANA.json.gz')
    with a.salida.open('x',encoding='utf8')as f:json.dump(result,f,sort_keys=True,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'hour_criterion_supported':result['hour_criterion_supported'],'issues':result['issues'],'clean_closure':result['clean_closure_separate']['supported'],'new_native_ticks':0}));return 0
if __name__=='__main__':raise SystemExit(main())
