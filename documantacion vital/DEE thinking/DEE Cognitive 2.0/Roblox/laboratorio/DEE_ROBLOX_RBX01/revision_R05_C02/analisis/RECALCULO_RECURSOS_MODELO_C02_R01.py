"""Passive model/resource accounting from frozen own-policy/lifecycle JSONL only.

No model, Native, SDK, HTTP, process or private identity access. Duration fields
from the local server API are nanoseconds; host Job CPU seconds are sampled
cumulative counters, not energy, pure thought time or per-response CPU.
"""
from pathlib import Path
import argparse, csv, datetime, hashlib, json, math, statistics


def canon(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(",",":"),allow_nan=False)
def number(x):return type(x)in(int,float)and math.isfinite(x)
def timestamp(x):
    if not isinstance(x,str):return None
    try:
        d=datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
        return d.timestamp()if d.tzinfo is not None else None
    except ValueError:return None

def load(path,sources):
    path=Path(path);before=path.stat();raw=path.read_bytes();after=path.stat()
    if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):
        raise ValueError('Source changed during passive read; freeze/copy it first')
    rows=[]
    for line_no,line in enumerate(raw.decode('utf-8-sig').splitlines(),1):
        if not line.strip():continue
        value=json.loads(line)
        if not isinstance(value,dict):raise ValueError('Object JSONL required')
        rows.append((value,str(path),line_no))
    sources.append({'path':str(path),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
       'modified_utc':datetime.datetime.fromtimestamp(after.st_mtime,datetime.timezone.utc).isoformat(),
       'rows':len(rows)})
    return rows

def stats(values):
    values=[x for x in values if number(x)]
    return {'n':len(values),'sum':sum(values)if values else None,'min':min(values)if values else None,
       'median':statistics.median(values)if values else None,'max':max(values)if values else None}

def recalculate(policy_paths,server_paths,output):
    output=Path(output)
    if output.exists():raise FileExistsError('New absent output directory required')
    sources=[];issues=[];responses={};completed={};policy_bounds={};aliases=0
    for path in policy_paths:
        for row,source,line in load(path,sources):
            run=row.get('run_id');kind=row.get('kind');instant=timestamp(row.get('utc'))
            if isinstance(run,str)and instant is not None:
                bounds=policy_bounds.setdefault(run,{'start':instant,'end':instant})
                bounds['start']=min(bounds['start'],instant);bounds['end']=max(bounds['end'],instant)
            if kind=='COMPLETED':
                result=row.get('result',{});evidence=result.get('evidence',{})if isinstance(result,dict)else{}
                call=evidence.get('model_call')if isinstance(evidence,dict)else None
                if type(call)is int:completed.setdefault((run,call),[]).append(row)
            if kind not in('MODEL_RESPONSE','RESPONSE'):continue
            call=row.get('call')
            if not isinstance(run,str)or type(call)is not int:
                issues.append({'source':source,'line':line,'issue':'Missing run/call identity'});continue
            key=(run,call);prior=responses.get(key)
            material={k:row.get(k)for k in('kind_requested','choice','wall_seconds','metrics','context_near_limit','monetary_cost_usd')}
            if prior:
                if canon(prior['material'])!=canon(material):issues.append({'run':run,'call':call,'issue':'Conflicting response alias'})
                aliases+=1;continue
            responses[key]={'row':row,'material':material,'source':source,'line':line}
    calls=[]
    duration_keys=('total_duration','load_duration','prompt_eval_duration','eval_duration')
    for (run,call),item in sorted(responses.items()):
        row=item['row'];metric=row.get('metrics',{});metric=metric if isinstance(metric,dict)else{}
        choice=row.get('choice');action=choice.get('action')if isinstance(choice,dict)else None
        value={'run_id':run,'call':call,'requested_kind':row.get('kind_requested'),'utc':row.get('utc'),
           'action':action,'choice_valid':choice is not None,'voluntary_safe_wait':action=='SAFE_WAIT',
           'wall_seconds':row.get('wall_seconds'),'model':metric.get('model'),'done':metric.get('done'),
           'done_reason':metric.get('done_reason'),'prompt_tokens_reported':metric.get('prompt_eval_count'),
           'generated_tokens_reported':metric.get('eval_count'),'context_near_limit':row.get('context_near_limit'),
           'linked_completed_operation_count':len({r.get('operation_id')for r in completed.get((run,call),[])if r.get('operation_id')}),
           'source':item['source'],'line':item['line']}
        for k in duration_keys:value[k+'_seconds']=metric[k]/1e9 if number(metric.get(k))else None
        calls.append(value)
    resources=[];lifecycles=[]
    for path in server_paths:
        rows=load(path,sources);samples=[]
        for row,source,line in rows:
            if row.get('kind')=='HOST_RESOURCES':
                sample={'utc':row.get('utc'),'timestamp':timestamp(row.get('utc')),'source':source,'line':line,
                   **{k:row.get(k)for k in('cpu_user_seconds','cpu_kernel_seconds','peak_job_committed_bytes',
                       'peak_process_committed_bytes','job_memory_limit','job_active_processes','job_total_processes')}}
                samples.append(sample);resources.append(sample)
        samples.sort(key=lambda x:x['timestamp']if x['timestamp']is not None else float('-inf'))
        cpu=[s for s in samples if number(s.get('cpu_user_seconds'))and number(s.get('cpu_kernel_seconds'))]
        cpu_delta=None
        if len(cpu)>=2:
            first,last=cpu[0],cpu[-1]
            cpu_delta=(last['cpu_user_seconds']+last['cpu_kernel_seconds'])-(first['cpu_user_seconds']+first['cpu_kernel_seconds'])
            if cpu_delta<0:issues.append({'source':str(path),'issue':'Cumulative CPU counter decreased'});cpu_delta=None
        lifecycles.append({'source':str(path),'host_sample_count':len(samples),
          'started_records':[r for r,_,_ in rows if r.get('kind')=='STARTED'],
          'closed_records':[r for r,_,_ in rows if r.get('kind')=='CLOSED'],
          'observed_cumulative_job_cpu_delta_seconds':cpu_delta,
          'cpu_sample_first_utc':cpu[0]['utc']if cpu else None,'cpu_sample_last_utc':cpu[-1]['utc']if cpu else None,
          'max_reported_peak_job_committed_bytes':max((s['peak_job_committed_bytes']for s in samples if number(s.get('peak_job_committed_bytes'))),default=None),
          'scope':'Entire owned server Job interval; includes all its runs, setup and idle; not allocated to individual calls.'})
    run_stats={}
    for run in sorted({r['run_id']for r in calls}):
        rows=[r for r in calls if r['run_id']==run]
        d={k:stats([r[k]for r in rows])for k in('wall_seconds','prompt_tokens_reported','generated_tokens_reported',
              'total_duration_seconds','load_duration_seconds','prompt_eval_duration_seconds','eval_duration_seconds')}
        generated=d['generated_tokens_reported']['sum'];seconds=d['eval_duration_seconds']['sum']
        run_stats[run]={'recorded_responses':len(rows),'valid_choices':sum(r['choice_valid']for r in rows),
           'voluntary_safe_wait_responses':sum(r['voluntary_safe_wait']for r in rows),
           'responses_linked_to_completed_operations':sum(r['linked_completed_operation_count']>0 for r in rows),
           'response_kind_counts':{str(k):sum(r['requested_kind']==k for r in rows)for k in sorted({r['requested_kind']for r in rows},key=str)},
           'metrics':d,'aggregate_generated_tokens_per_eval_second':generated/seconds if number(generated)and number(seconds)and seconds>0 else None,
           'own_policy_event_window_epoch':policy_bounds.get(run)}
    result={'schema':'DEE.C02.passive_model_resources.R01','Native_executed':False,'model_HTTP_MCP_calls':0,
       'response_aliases_deduplicated':aliases,'runs':run_stats,'server_lifecycles':lifecycles,'sources':sources,'issues':issues,
       'limits':['Tokens are sums reported by the server: repeated prompt history is counted repeatedly, not unique information or concepts.',
       'No arithmetic opportunity is not an arithmetic error; actual tool opportunity/results are measured by the separate world comparison.',
       'Intentional SAFE_WAIT is distinct from an invalid/null output forced to the neutral action.',
       'CPU is sampled cumulative host Job CPU, not cognitive memory, energy or task-specific inference CPU; shared server runs are not separated.',
       'Absent metrics are NULL, not zero. Recorded response count does not include reserved calls that failed before a response.',
       'API durations are nanoseconds converted to seconds. Wall response latency includes local request/dispatch; interval gaps and GUI pauses are not thinking time.',
       'This is recalculation of supplied frozen logs, not a new model invocation or Native reproduction.']}
    output.mkdir()
    (output/'RECURSOS_MODELO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for name,rows in(('RESPUESTAS_MODELO.csv',calls),('MUESTRAS_HOST_JOB.csv',resources)):
        keys=list(dict.fromkeys(k for r in rows for k in r))
        with (output/name).open('w',encoding='utf-8-sig',newline='')as f:
            w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(rows)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--policy-log',type=Path,nargs='+',required=True)
    p.add_argument('--server-log',type=Path,nargs='*',default=[])
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=recalculate(a.policy_log,a.server_log,a.output)
    print(json.dumps({'output':str(a.output),'runs':{k:v['recorded_responses']for k,v in r['runs'].items()},'issues':r['issues']},ensure_ascii=False))
if __name__=='__main__':main()
