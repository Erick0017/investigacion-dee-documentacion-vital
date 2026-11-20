"""Trajectory-level resource/latency summary from the four archived references."""
import argparse,hashlib,json
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def distribution(values):
    values=sorted(values)
    if not values:return {'samples':0,'minimum':None,'median':None,'maximum':None,'sum':None}
    n=len(values);numerator=values[n//2]if n%2 else values[n//2-1]+values[n//2]
    return {'samples':n,'minimum':values[0],'median_exact':{'numerator':numerator,'denominator':1 if n%2 else 2},
        'maximum':values[-1],'sum':sum(values)}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--three',required=True,type=Path)
    parser.add_argument('--standard',required=True,type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args();rows=[]
    for name,root in[(name,args.three)for name in('fijo','tabla_contextual','wsls')]+[('wsls_estandar',args.standard)]:
        folder=root/name;summary=json.loads((folder/'resumen.json').read_bytes())
        events=[json.loads(line)for line in(folder/'eventos_primarios.jsonl').read_bytes().splitlines()]
        opportunities=[r for r in events if r['kind']=='opportunity'];artifact_files=list((folder/'artifacts').glob('*.json'))
        rows.append({'policy':name,'summary_sha256':sha(folder/'resumen.json'),'primary_sha256':sha(folder/'eventos_primarios.jsonl'),
            'program_sha256':summary['program_sha256'],'source_sha256':summary['source_sha256'],
            'native_only_files_correct_total':[summary['native_only_completed'],summary['native_only_total']],
            'quality_files_correct_total':[summary['quality_completed'],summary['quality_total']],
            'files_correct_tasks_total':[summary['tasks_completed'],summary['task_count']],
            'opportunities_requested':summary['opportunities_requested'],'admitted_conventional':summary['admitted_conventional'],
            'queries':summary['queries'],'ACT_incorrect_unusable':summary['wrong_or_unusable_acts'],
            'no_output':summary['no_output'],'uncertain_effects':summary['uncertain_effects'],
            'CPU_process_interval_ns':summary['process_total']['cpu_ns'],'wall_process_interval_ns':summary['process_total']['wall_ns'],
            'peak_worker_working_set_bytes':summary['owned_job_resources']['actual_worker_peak_working_set_bytes'],
            'process_IO_delta':{k:summary['process_total'][k]for k in('io_read_bytes','io_write_bytes','io_read_operations','io_write_operations')},
            'decision_wall_ns_distribution':distribution([r['decision_resources']['wall_ns']for r in opportunities]),
            'decision_CPU_ns_distribution':distribution([r['decision_resources']['cpu_ns']for r in opportunities]),
            'effect_wall_ns_distribution':distribution([r['effect_resources']['wall_ns']for r in opportunities]),
            'artifact_files_count':len(artifact_files),'artifact_files_bytes':sum(p.stat().st_size for p in artifact_files),
            'energy':'NO MEDIDA','sample_unit':'one policy trajectory; opportunities are not independent learners'})
    result={'schema':'DEE.APD03.reference_measurements.N0.R01','rows':rows,'new_native_ticks':0,'new_provider_calls':0,
        'scope':'Only the11 shared task subset; not MAIN physical evolution, MA/lexical acquisition or v27 arithmetic cost.',
        'IO':'Actual GetProcessIoCounters worker deltas; not reserved class9 IoInfo, physical sectors or unique file bytes. Missing remains null, not zero.',
        'timing':'Instrumented run interval excludes interpreter imports/final summary write. Job cumulative values are not added. Logical schedule is not a timed one-hour comparison.',
        'interpretation':'Descriptive within-trajectory distributions only; no confidence interval or speed ranking from these four different policies.'}
    with args.out.open('x',encoding='utf8')as stream:
        json.dump(result,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'out':str(args.out),'sha256':sha(args.out),'policies':len(rows)}))


if __name__=='__main__':main()
