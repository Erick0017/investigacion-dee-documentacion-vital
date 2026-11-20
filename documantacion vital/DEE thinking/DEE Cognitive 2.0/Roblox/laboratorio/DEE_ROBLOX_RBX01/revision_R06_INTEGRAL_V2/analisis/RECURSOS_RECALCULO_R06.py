"""Portable passive accounting of explicit R06 resource JSON/JSONL files.

No Native, SQLite, Studio, model, socket or subprocess. CPU is cumulative Job CPU:
take maxima per unique owner/run, NEVER sum resource samples. Owner lifetime,
phase latency, import0, model service and host RAM are different measurements.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,csv,datetime as dt,hashlib,json,math,statistics

PREFIX='R06_'
ARMS=('LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI')
CPU=('cpu_user_seconds','cpu_kernel_seconds')
MEM=('peak_job_committed_bytes','peak_process_committed_bytes','working_set_bytes',
     'peak_working_set_bytes','private_bytes')
OWNER_KINDS={'OWNED_PROCESS_RESOURCES','OWNER_STARTED','OWNER_CLOSED','OWN_CLOSE_PROBLEM'}
LIMIT=30_000_000

def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def encode(v):return (json.dumps(v,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8')
def sha(v):return hashlib.sha256(v).hexdigest()
def number(v):return type(v)in(int,float)and math.isfinite(v)and v>=0
def peak(rows,key):
    values=[r[key]for r in rows if number(r.get(key))]
    return max(values)if values else None
def total_known(values):
    values=list(values)
    return sum(values)if values and all(number(x)for x in values)else None
def timestamp(v):
    if not isinstance(v,str):return None
    try:return dt.datetime.fromisoformat(v.replace('Z','+00:00')).timestamp()
    except ValueError:return None

class Inputs:
    def __init__(self,allow_partial):self.partial=allow_partial;self.sources=[];self.primaries=[]
    def read(self,path,category,label):
        path=Path(path).resolve(strict=True)
        for part in(path,*path.parents):
            st=part.lstat()
            if part.is_symlink()or getattr(st,'st_file_attributes',0)&1024:raise ValueError('LINK_INPUT_REFUSED')
        before=path.stat()
        if before.st_size>LIMIT:raise ValueError('FINITE30MB_INPUT_REQUIRED')
        with path.open('rb')as f:raw=f.read(before.st_size)
        after=path.stat();changed=(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns)
        if changed and not self.partial:raise ValueError('SOURCE_CHANGED; freeze it or explicitly --allow-partial')
        truncated=False
        if path.suffix.lower()=='.jsonl':
            if raw and not raw.endswith(b'\n'):
                if not self.partial:raise ValueError('INCOMPLETE_JSONL_LINE')
                raw=raw[:raw.rfind(b'\n')+1]if b'\n'in raw else b'';truncated=True
            value=[json.loads(line)for line in raw.decode('utf-8-sig').splitlines()if line.strip()]
        else:value=json.loads(raw.decode('utf-8-sig'))
        source={'index':len(self.sources)+1,'category':category,'label':label,'path':str(path),
                'bytes_read':len(raw),'sha256_read_prefix':sha(raw),'source_bytes_before':before.st_size,
                'source_bytes_after':after.st_size,'changed_while_reading':changed,'unfinished_tail_excluded':truncated,
                'scope':'Fixed prefix read; active append is not a final result'if changed or truncated else'Bytes stable during this read, not a claim that every writer is closed'}
        self.sources.append(source);return value,source
    def keep(self,category,label,value,source,derived=False):
        filename=f'PRIMARIOS/{len(self.primaries)+1:02d}_{category}.jsonl'if isinstance(value,list)else f'PRIMARIOS/{len(self.primaries)+1:02d}_{category}.json'
        raw=(''.join(canonical(x)+'\n'for x in value).encode('utf-8')if isinstance(value,list)else encode(value))
        self.primaries.append({'archive_relative':filename,'category':category,'label':label,'bytes':len(raw),'sha256':sha(raw),
            'source_index':source['index'],'selection':'DERIVED projection of exact measurement fields'if derived else'Complete relevant event rows; unrelated journal kinds/prefixes omitted',
            '_raw':raw})

def owner_runs(journals,inputs,issues):
    grouped=defaultdict(list);excluded=Counter();aliases=0;seen=set()
    for label,path in journals:
        rows,source=inputs.read(path,'owner_journal',label)
        if not isinstance(rows,list):raise ValueError('OWNER_JSONL_REQUIRED')
        selected=[]
        for row in rows:
            if not isinstance(row,dict):raise ValueError('JSON_OBJECT_EVENT_REQUIRED')
            run=row.get('run')
            if not isinstance(run,str)or not run.startswith(PREFIX):excluded['non_R06_prefix']+=1;continue
            if row.get('kind')not in OWNER_KINDS:excluded['other_R06_kind']+=1;continue
            key=canonical(row)
            if key in seen:aliases+=1;continue
            seen.add(key);selected.append(row);grouped[(row.get('life'),run)].append(row)
        inputs.keep('owner',label,selected,source)
    summaries=[]
    for(life,run),rows in sorted(grouped.items(),key=lambda x:str(x[0])):
        samples=[r for r in rows if r['kind']=='OWNED_PROCESS_RESOURCES']
        starts=[r for r in rows if r['kind']=='OWNER_STARTED'];closes=[r for r in rows if r['kind']=='OWNER_CLOSED']
        pids=sorted({r['pid']for r in rows if type(r.get('pid'))is int})
        jobs=sorted({r['job']for r in starts if isinstance(r.get('job'),str)})
        if len(pids)!=1:issues.append({'issue':'OWNER_RUN_PID_CONFLICT','run':run,'pids':pids})
        if len(jobs)!=1:issues.append({'issue':'OWNER_RUN_JOB_IDENTITY_MISSING_OR_CONFLICTING','run':run,'jobs':jobs})
        if len(closes)>1:issues.append({'issue':'MULTIPLE_DIFFERENT_CLOSE_ROWS','run':run})
        close=closes[-1]if len(closes)==1 else None
        closed=bool(close and close.get('exit_code')==0 and(close.get('final_status')or{}).get('running')is False and len(pids)==1 and len(jobs)==1)
        values={key:peak(samples,key)for key in(*CPU,*MEM,'elapsed_seconds')}
        regressions=[]
        for key in CPU:
            prior=None
            for row in samples:
                value=row.get(key)
                if number(value):
                    if prior is not None and value<prior:regressions.append({'field':key,'prior':prior,'next':value})
                    prior=value
        if regressions:issues.append({'issue':'CUMULATIVE_JOB_CPU_DECREASE','run':run,'count':len(regressions)})
        estimates=[timestamp(s.get('utc'))-s['elapsed_seconds']for s in samples if timestamp(s.get('utc'))is not None and number(s.get('elapsed_seconds'))]
        estimated_start=statistics.median(estimates)if estimates else None
        lifetime=close.get('elapsed_seconds')if close and number(close.get('elapsed_seconds'))else None
        final_sample=next((s for s in reversed(samples)if s.get('exit_code')==0),None)
        summaries.append({'life':life,'run':run,'pid':pids[0]if len(pids)==1 else None,'job':jobs[0]if len(jobs)==1 else None,
            'owner_started_record_present':bool(starts),
            'closed_clean':closed,'owner_close_record_present':close is not None,'resource_samples':len(samples),
            'cpu_user_job_seconds_max':values['cpu_user_seconds'],'cpu_kernel_job_seconds_max':values['cpu_kernel_seconds'],
            'cpu_job_seconds_total_maxima':total_known(values[k]for k in CPU),
            'cpu_samples_are_not_summed':True,'final_post_exit_resource_sample_present':final_sample is not None,
            'owner_lifetime_seconds_from_OWNER_CLOSED':lifetime,'last_sample_elapsed_seconds':values['elapsed_seconds'],
            'memory_peaks_bytes':{key:values[key]for key in MEM},
            'job_memory_limits_observed':sorted({s['job_memory_limit']for s in samples if number(s.get('job_memory_limit'))}),
            'estimated_start_utc_from_sample_utc_minus_elapsed':dt.datetime.fromtimestamp(estimated_start,dt.timezone.utc).isoformat()if estimated_start is not None else None,
            'estimated_end_utc':dt.datetime.fromtimestamp(estimated_start+lifetime,dt.timezone.utc).isoformat()if estimated_start is not None and lifetime is not None else None,
            'UTC_interval_scope':'Estimate from wall UTC and monotonic elapsed; not an independently logged exact timestamp.',
            'CPU_scope':'Whole owned Job including its child processes; not kernel-only CPU or host-global CPU.',
            'counter_regressions':regressions})
    return summaries,{'excluded_rows':dict(excluded),'identical_event_aliases':aliases}

def phase_times(paths,inputs,issues):
    found={};aliases=0
    for arm,path in paths:
        if arm not in ARMS:raise ValueError('EXPLICIT_PARTICIPANT_REQUIRED')
        rows,source=inputs.read(path,'phase_events',arm);selected=[]
        for row in rows:
            if row.get('kind')not in('NATIVE_COMPLETED','BACKEND_COMPLETED'):continue
            identifier=row.get('operation_id')
            if not isinstance(identifier,str):issues.append({'issue':'PHASE_WITHOUT_OPERATION_ID','source_index':source['index']});continue
            key=(arm,identifier)
            projected={k:row[k]for k in('kind','phase','operation_id','wall_seconds','utc','cycle')if k in row}
            if key in found:
                if projected!=found[key]:issues.append({'issue':'CONFLICTING_PHASE_ALIAS','participant':arm,'operation_id':identifier})
                else:aliases+=1
                continue
            found[key]=projected;selected.append(projected)
        inputs.keep('phases',arm,selected,source,True)
    summaries=[]
    for arm in ARMS:
        rows=[r for(a,_),r in found.items()if a==arm]
        values=[r['wall_seconds']for r in rows if number(r.get('wall_seconds'))]
        summaries.append({'participant':arm,'completed_phase_count':len(rows),'phase_latency_samples':len(values),
            'phase_wall_seconds_sum':sum(values)if values else None,'phase_wall_seconds_max':max(values)if values else None,
            'CPU_seconds':None,'CPU_status':'Not instrumented by phase events; elapsed latency is not CPU.',
            'scope':'Completed backend/Native call latency only; not owner lifetime, total experiment wall, energy or rendering FPS.'})
    return summaries,aliases

def import_cost(paths,inputs,issues):
    output=[];seen=set()
    for label,path in paths:
        value,source=inputs.read(path,'import0_job',label)
        key=value.get('job')or value.get('pid')or source['sha256_read_prefix']
        if key in seen:issues.append({'issue':'DUPLICATE_IMPORT_JOB_NOT_ADDED','label':label});continue
        seen.add(key);samples=value.get('samples',[])
        selected={k:value[k]for k in('schema','status','job','pid','exit_code','elapsed_seconds','new_native_ticks','owner_opened','life_id')if k in value}
        selected['samples']=samples;inputs.keep('import0',label,selected,source,True)
        output.append({'label':label,'job':value.get('job'),'closed':value.get('status')=='COMPLETED'and value.get('exit_code')==0,
            'new_Native_ticks_reported':value.get('new_native_ticks'),'wall_seconds':value.get('elapsed_seconds'),
            'cpu_user_job_seconds_max':peak(samples,'cpu_user_seconds'),'cpu_kernel_job_seconds_max':peak(samples,'cpu_kernel_seconds'),
            'memory_peaks_bytes':{key:peak(samples,key)for key in MEM},
            'scope':'Import/verification host work; separate from new Native experience and from every owner run.'})
    return output

def load_memory(paths,inputs):
    result=[]
    for label,path in paths:
        value,source=inputs.read(path,'load_stage',label);samples=value.get('host_samples',[])
        projection={k:value[k]for k in('schema','stage','status','owner_lifetime_common_overlap_seconds','abort_reason')if k in value}
        projection['host_samples']=samples;inputs.keep('host_memory',label,projection,source,True)
        available=[r['available_bytes']for r in samples if number(r.get('available_bytes'))]
        result.append({'label':label,'stage':value.get('stage'),'stage_status':value.get('status'),'host_samples':len(samples),
            'host_available_bytes_min':min(available)if available else None,'host_available_bytes_max':max(available)if available else None,
            'host_load_percent_max':peak(samples,'load_percent'),
            'owner_lifetime_common_overlap_seconds':value.get('owner_lifetime_common_overlap_seconds'),
            'scope':'Whole-host physical available RAM sampled by supervisor; not cognitive memory or a per-Native allocation.'})
    return result

def model_cost(paths,services,inputs,issues):
    calls={};aliases=0
    for label,path in paths:
        rows,source=inputs.read(path,'model_policy',label);selected=[]
        for row in rows:
            if row.get('kind')not in('RESPONSE','FAILED_PRESERVED'):continue
            key=(row.get('run_id',label),row.get('call'))
            if type(key[1])is not int:issues.append({'issue':'MODEL_CALL_ID_MISSING','label':label});continue
            projected={k:row[k]for k in('kind','utc','run_id','call','wall_seconds','elapsed_seconds','metrics','rejection','exception')if k in row}
            if key in calls:
                if calls[key]!=projected:issues.append({'issue':'MODEL_CALL_CONFLICT','run':key[0],'call':key[1]})
                else:aliases+=1
                continue
            calls[key]=projected;selected.append(projected)
        inputs.keep('model_calls',label,selected,source,True)
    complete=[x for x in calls.values()if x['kind']=='RESPONSE'];metrics=[x.get('metrics')or{}for x in complete]
    keys=('prompt_eval_count','eval_count','total_duration','load_duration','prompt_eval_duration','eval_duration')
    metric_coverage={key:sum(number(m.get(key))for m in metrics)for key in keys}
    tokens={key:sum(m[key]for m in metrics if number(m.get(key)))if metric_coverage[key]else None for key in keys[:2]}
    durations={key:sum(m[key]for m in metrics if number(m.get(key)))/1e9 if metric_coverage[key]else None for key in keys[2:]}
    service_rows=[]
    for label,path in services:
        rows,source=inputs.read(path,'model_service',label)
        selected=[x for x in rows if x.get('kind')in('STARTED','HOST_RESOURCES','CLOSED','SERVER_EXITED','FINITE_STOP')]
        inputs.keep('model_service',label,selected,source)
        resources=[x for x in selected if x['kind']=='HOST_RESOURCES'];starts=[x for x in selected if x['kind']=='STARTED'];closes=[x for x in selected if x['kind']=='CLOSED']
        service_rows.append({'label':label,'pid':starts[0].get('pid')if len(starts)==1 else None,
            'closed_record_present':len(closes)==1,'resources_samples':len(resources),
            'cpu_user_job_seconds_max':peak(resources,'cpu_user_seconds'),'cpu_kernel_job_seconds_max':peak(resources,'cpu_kernel_seconds'),
            'memory_peaks_bytes':{key:peak(resources,key)for key in MEM},
            'scope':'Entire model-server Job, including idle/warmup and all clients; cannot attribute its CPU to one decision or compare directly to Native phase wall.'})
    return {'recorded_response_calls':len(complete),'failed_calls':sum(x['kind']=='FAILED_PRESERVED'for x in calls.values()),
        'identical_aliases':aliases,'client_wall_seconds_sum':sum(x['wall_seconds']for x in complete if number(x.get('wall_seconds')))if any(number(x.get('wall_seconds'))for x in complete)else None,
        'token_counts_reported':tokens,'server_durations_reported_seconds':durations,'metric_coverage_response_count':metric_coverage,
        'service_jobs':service_rows,'scope':'API-reported durations/tokens are not CPU, cost, FPS, weight learning or equal preparation to DEE.'}

def pairs(values):
    output=[]
    for value in values:
        label,path=value.split('=',1)
        if not label or not path:raise ValueError('LABEL=EXPLICIT_PATH_REQUIRED')
        output.append((label,Path(path)))
    return output

def csv_out(path,rows):
    fields=list(dict.fromkeys(k for r in rows for k in r))
    with path.open('w',encoding='utf-8-sig',newline='')as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        w.writerows({k:canonical(v)if isinstance(v,(dict,list))else v for k,v in r.items()}for r in rows)

def calculate(a):
    output=Path(a.output)
    if output.exists()or not output.parent.is_dir():raise ValueError('NEW_OUTPUT_EXISTING_PARENT_REQUIRED')
    inputs=Inputs(a.allow_partial);issues=[]
    owners,coverage=owner_runs(pairs(a.owner_journal),inputs,issues)
    phases,aliases=phase_times(pairs(a.phase_events),inputs,issues)
    imports=import_cost(pairs(a.import_job),inputs,issues)
    loads=load_memory(pairs(a.load_stage),inputs)
    model=model_cost(pairs(a.model_log),pairs(a.model_service),inputs,issues)
    unclosed=[x['run']for x in owners if not x['closed_clean']]
    unclosed.extend('IMPORT0:'+x['label']for x in imports if not x['closed'])
    unclosed.extend('MODEL_SERVICE:'+x['label']for x in model['service_jobs']if not x['closed_record_present'])
    if unclosed and not a.allow_partial:raise ValueError('CLOSED_PROOF_REQUIRED_BEFORE_FINAL_TOTALS: '+','.join(unclosed))
    closed=[x for x in owners if x['closed_clean']]
    report={'schema':'DEE.INTEGRAL.V2.passive_resources.R01','created_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
        'status':'PARTIAL_NOT_FINAL'if unclosed or any(s['changed_while_reading']or s['unfinished_tail_excluded']for s in inputs.sources)else'CLOSED_INPUTS_RECALCULATED',
        'Native_SQLite_Studio_model_executions':0,'all_owner_runs_closed_clean':not unclosed,'unclosed_inputs':unclosed,
        'owner_runs':owners,'owner_journal_coverage':coverage,'phase_times':phases,'phase_aliases_deduplicated':aliases,
        'closed_owner_aggregate':{'runs':len(closed),'cpu_job_seconds_sum_of_run_maxima':total_known(x['cpu_job_seconds_total_maxima']for x in closed),
            'sum_owner_lifetimes_seconds_not_elapsed_campaign':total_known(x['owner_lifetime_seconds_from_OWNER_CLOSED']for x in closed),
            'maximum_single_owner_peak_job_committed_bytes':max((x['memory_peaks_bytes']['peak_job_committed_bytes']for x in closed if number(x['memory_peaks_bytes']['peak_job_committed_bytes'])),default=None)},
        'import0_separate':imports,'load_host_memory':loads,'model_separate':model,'issues':issues,
        'limits':['Only explicit inputs; no owner/queue/snapshot is queried.',
            'R06_ run prefix is mandatory; inherited C02 samples are excluded, even if present in the same journal.',
            'CPU cumulative maxima per unique Job/run are added once; samples are never added. Post-exit sample coverage is exposed.',
            'Owner lifetime includes startup, waits and closing. Phase latency excludes some of those and must not be added to it.',
            'Concurrent owner lifetimes overlap; their sum is not elapsed campaign time. Sum of RAM peaks is not measured simultaneous RAM.',
            'LOAD3/CTRL1 import0 reportedly overlapped Native around00:41–00:50UTC16Nov; treat host-load/paging as a confound, not a Native mechanism. Exact overlap is not inferred without timestamped import evidence.',
            'Import0 costs are separate0-new-tick host preparation. Their CPU is not added to Native owner or new experience.',
            'References without Job CPU instrumentation retain CPU=null; phase/model latency is not a substitute.',
            'Frames/render FPS, model tokens, API nanoseconds, wall latency, Job CPU and cognitive memory are different quantities.',
            'No power meter, energy, monetary estimate, kernel-only CPU, theoretical capacity ceiling or scientific approval is inferred.'],
        'sources':inputs.sources,'portable_primary_selection':[{k:v for k,v in r.items()if k!='_raw'}for r in inputs.primaries]}
    output.mkdir();(output/'PRIMARIOS').mkdir()
    for row in inputs.primaries:(output/row['archive_relative']).write_bytes(row['_raw'])
    (output/'RECURSOS_RECALCULADOS.json').write_bytes(encode(report))
    csv_out(output/'OWNERS_POR_RUN.csv',owners);csv_out(output/'IMPORT0_SEPARADO.csv',imports);csv_out(output/'FASES_POR_PARTICIPANTE.csv',phases)
    recipe=[]
    flags={'owner':'--owner-journal','phases':'--phase-events','import0':'--import-job','host_memory':'--load-stage','model_calls':'--model-log','model_service':'--model-service'}
    for row in inputs.primaries:recipe.extend((flags[row['category']],row['label']+'={resource_primary_root}/'+row['archive_relative']))
    if a.allow_partial:recipe.append('--allow-partial')
    recipe.extend(('--output','{new_output}'))
    (output/'REPETIR_PORTABLE.json').write_bytes(encode({'script':'analisis/RECURSOS_RECALCULO_R06.py','args':recipe,
        'root_placeholder':'resource_primary_root is this delivered result directory, not any original source path',
        'scope':'Recalculates the selected exact resource events/measurement projections; omitted unrelated science rows are outside this resource calculation.'}))
    return report

def cli():
    p=argparse.ArgumentParser(description=__doc__)
    for flag in('owner-journal','phase-events','import-job','load-stage','model-log','model-service'):p.add_argument('--'+flag,action='append',default=[],help='LABEL=explicit JSON/JSONL path; repeatable')
    p.add_argument('--allow-partial',action='store_true');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    if not any(getattr(a,k)for k in('owner_journal','phase_events','import_job','load_stage','model_log','model_service')):p.error('At least one explicit input required')
    r=calculate(a);print(json.dumps({'status':r['status'],'owner_runs':len(r['owner_runs']),'closed_CPU_job_seconds':r['closed_owner_aggregate']['cpu_job_seconds_sum_of_run_maxima'],'output':str(a.output),'issues':r['issues'],'Native_executed':False},ensure_ascii=False,indent=2))
if __name__=='__main__':cli()
