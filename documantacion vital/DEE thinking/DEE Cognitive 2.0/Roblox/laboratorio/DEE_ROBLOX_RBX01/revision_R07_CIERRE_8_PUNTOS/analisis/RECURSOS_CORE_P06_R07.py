"""Passive supplement: closed MAIN resource report plus separate closed P06 jobs.

No Native, database, Studio, model, OS measurement or subprocess. Portable CLI
uses explicit delivered JSON paths, never follows historical paths inside them.
"""
from pathlib import Path
import argparse
import csv
import hashlib
import json
import math

def finite(v):return type(v)in(int,float)and math.isfinite(v)and v>=0
def maximum(rows,key):
    values=[r[key]for r in rows if finite(r.get(key))]
    return max(values)if values else None
def read(path,sources):
    path=Path(path).resolve(strict=True);before=path.stat();raw=path.read_bytes();after=path.stat()
    if(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('Frozen input changed')
    sources.append({'path':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
    return json.loads(raw.decode('utf-8-sig'))

def p06_job(label,value):
    launch=value.get('launcher')or{};worker=value.get('root_job')or{};last=launch.get('actual_job_resources')or{}
    pid=launch.get('pid')
    if type(pid)is not int or worker.get('actual_python_pid')!=pid:raise ValueError('P06 exact owned worker PID required')
    if type(launch.get('exit_code'))is not int or last.get('job_active_processes')!=0:raise ValueError('P06 closed Job proof required')
    snapshots=[worker,last]
    user=maximum(snapshots,'cpu_user_seconds');kernel=maximum(snapshots,'cpu_kernel_seconds')
    cpu=user+kernel if finite(user)and finite(kernel)else None
    return {'label':label,'launcher_pid':pid,'exit_code':launch['exit_code'],
        'closed_job_active_processes':0,'failure_preserved':value.get('failure'),
        'status':'CLOSED_KNOWN_FAILURE'if launch['exit_code']!=0 or value.get('failure')else'CLOSED_COMPLETED',
        'cpu_user_Job_seconds_max':user,'cpu_kernel_Job_seconds_max':kernel,'cpu_Job_seconds':cpu,
        'cpu_scope':'Max cumulative Job counters once for this owned job; never sum worker and final snapshots or add pass CPU again',
        'peak_job_committed_bytes':maximum(snapshots,'peak_job_committed_bytes'),
        'peak_process_committed_bytes':maximum(snapshots,'peak_process_committed_bytes'),
        'wrapper_pid_peak_working_set_bytes':worker.get('actual_worker_peak_working_set_bytes'),
        'wrapper_pid_working_set_bytes':worker.get('actual_worker_working_set_bytes'),
        'wrapper_pid_private_bytes':worker.get('actual_worker_private_bytes'),
        'memory_scope':'Job commitment and wrapper PID physical WorkingSet are distinct; wrapper RSS is not all children or Native landscape memory',
        'job_memory_limit_bytes':last.get('job_memory_limit',launch.get('memory_limit')),
        'new_Native_ticks_recorded':value.get('Native_ticks'),
        'Native_requests_submitted':value.get('Native_requests_submitted'),
        'passes':value.get('passes',[]),'fraction_reduction':value.get('fraction_reduction'),
        'criterion_met':value.get('criterion_met'),'prototype_installed':value.get('prototype_installed_in_system'),
        'payload_equal':value.get('payload_equal'),'physical_equal':value.get('physical_equal'),
        'metadata_equal':value.get('metadata_equal')}

def execute(core_report,science,p06,output):
    output=Path(output)
    if output.exists()or not output.parent.is_dir():raise ValueError('Fresh output with existing parent required')
    sources=[];core=read(core_report,sources);facts=read(science,sources)
    if core['status']!='CLOSED_INPUTS_RECALCULATED'or core['unclosed_inputs']:raise ValueError('Closed core resources required')
    main=[a for a in facts['arms']if a['participant']=='LIVE_NATIVE'and a['sensor_arm']=='local_tag']
    if len(main)!=1:raise ValueError('One actual MAIN scientific denominator required')
    main=main[0];jobs=[p06_job(label,read(path,sources))for label,path in p06]
    if len({j['launcher_pid']for j in jobs})!=len(jobs):raise ValueError('P06 owned Job duplicate PID; do not add twice')
    p06cpu=sum(j['cpu_Job_seconds']for j in jobs)if jobs and all(finite(j['cpu_Job_seconds'])for j in jobs)else None
    cpu=core['closed_owner_aggregate']['cpu_job_seconds_sum_of_run_maxima']
    new_deliveries=main['delta']['delivered']
    report={'schema':'DEE.R07.ClosedCoreAndSeparateP06Resources.R01',
        'status':'PASSIVE_CLOSED_INPUTS_RECALCULATED','main_core_report':sources[0],
        'main_scientific_facts':sources[1],'main_owner_runs':core['owner_runs'],
        'main_owner_aggregate':core['closed_owner_aggregate'],'main_phase_times':core['phase_times'],
        'main_phase_aliases_deduplicated':core['phase_aliases_deduplicated'],
        'main_actual_denominators':{'completed_new_opportunities':main['completed_new'],
            'unique_completed_operations':main['deduplicated_completed_operations'],
            'new_native_ticks':main['native_ticks_from_unique_phases'],
            'new_resources':main['delta']['resourceCount'],'new_deliveries':new_deliveries},
        'main_CPU_seconds_per_new_delivery':cpu/new_deliveries if finite(cpu)and finite(new_deliveries)and new_deliveries>0 else None,
        'delivery_cost_status':'DEFINED'if finite(new_deliveries)and new_deliveries>0 else'UNDEFINED_ZERO_NEW_DELIVERIES',
        'P06_separate_host_verification_jobs':jobs,'P06_CPU_Job_seconds_separate_total':p06cpu,
        'P06_included_in_MAIN_CPU_or_tick_totals':False,
        'source_files':sources,'main_issues':core['issues'],
        'limits':['Only these closed files were read; no LOAD, current owner, queue, database or OS was queried.',
            'Owner lifetimes, phase wall latency, per-pass process CPU and Job cumulative CPU are distinct and are not added together.',
            'S.latency is inherited and was not read as a new latency measurement.',
            'PeakJobMemoryUsed/peak_job_committed_bytes is commitment, not RSS or physical free RAM.',
            'Source current/peak process WorkingSet is kept under its exact scope; no Job-wide physical RSS is fabricated.',
            'P06 R01 negative is retained; P06 R02 below20percent did not authorize deployment.',
            'No new delivery means cost per successful new delivery is undefined, not zero or infinity.',
            'This is passive accounting, not a Native reproduction, new benchmark, energy measurement or fair efficiency ranking.'],
        'Native_SQLite_MCP_Studio_model_OS_measurement_calls':0}
    output.mkdir()
    target=output/'RECURSOS_MAIN6_Y_P06.json'
    target.write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n','utf-8')
    fields=[k for k in jobs[0]if k!='passes']if jobs else[]
    with(output/'P06_JOBS_SEPARADOS.csv').open('w',encoding='utf-8',newline='')as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for j in jobs:writer.writerow({k:json.dumps(j[k],ensure_ascii=False)if isinstance(j[k],(dict,list))else j[k]for k in fields})
    recipe={'script':'analisis/RECURSOS_CORE_P06_R07.py',
        'local_inputs':{'core_report':str(Path(core_report).resolve()),'science_facts':str(Path(science).resolve()),
            'p06':[{'label':label,'path':str(Path(path).resolve())}for label,path in p06]},
        'portable_rule':'Supply exact delivered archive paths for these JSONs; paths stored inside JSON provenance are never opened',
        'sources':sources}
    (output/'RECETA_Y_FUENTES_RECURSOS_R01.json').write_text(json.dumps(recipe,ensure_ascii=False,indent=2)+'\n','utf-8')
    print(json.dumps({'output':str(output),'report_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
        'MAIN_CPU_Job_seconds':cpu,'P06_CPU_Job_seconds_separate':p06cpu,
        'main_new_deliveries':new_deliveries,'delivery_cost':report['delivery_cost_status'],
        'Native_SQLite_MCP_Studio_model_OS_measurement_calls':0},ensure_ascii=False))
    return report

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--core-report',type=Path,required=True);p.add_argument('--science',type=Path,required=True)
    p.add_argument('--p06',action='append',default=[],help='LABEL=exact closed RESULTADO_P06.json')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    values=[x.split('=',1)for x in a.p06]
    execute(a.core_report,a.science,values,a.output)
