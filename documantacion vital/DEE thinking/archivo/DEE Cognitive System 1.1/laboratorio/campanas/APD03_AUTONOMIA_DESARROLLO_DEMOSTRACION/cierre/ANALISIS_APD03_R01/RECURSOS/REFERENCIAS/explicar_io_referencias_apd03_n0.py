"""Clarify already measured Windows process I/O; never rerun a task."""
import argparse,hashlib,json
from pathlib import Path


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--evidence',required=True,type=Path)
    parser.add_argument('--out',required=True,type=Path);args=parser.parse_args();rows=[]
    for name in('fijo','tabla_contextual','wsls'):
        folder=args.evidence/name;summary=json.loads((folder/'resumen.json').read_bytes())
        artifacts=[{'file':p.relative_to(folder).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
            for p in sorted((folder/'artifacts').glob('*.json'))]
        rows.append({'policy':name,'summary_sha256':sha(folder/'resumen.json'),
            'actual_worker_pid':summary['owned_job_resources']['actual_python_pid'],
            'measured_process_interval':summary['process_total'],
            'artifact_files':artifacts,'artifact_files_count':len(artifacts),
            'artifact_bytes_on_disk_sum':sum(r['bytes']for r in artifacts),
            'eventlog_bytes_on_disk':(folder/'eventos_primarios.jsonl').stat().st_size,
            'job_io_measurement':'NOT PROVIDED: no class9 IoInfo field is interpreted as measured I/O',
            'resource_scope':'Actual worker only, not the waiting venv launcher; interval excludes interpreter import and final summary write'})
    code=args.evidence/'CODIGO_EJECUTADO'
    result={'schema':'DEE.APD03.references.IO_provenance.N0','rows':rows,
        'sources':[{'file':str(code/name),'sha256':sha(code/name)}for name in
            ('comparadores_apd03.py','comparadores_apd03_r02.py','vendor/process_control.py')],
        'os_source':'kernel32.GetProcessIoCounters(GetCurrentProcess(),IO_COUNTERS)',
        'fields':{'io_read_bytes':'delta ReadTransferCount','io_write_bytes':'delta WriteTransferCount',
            'io_read_operations':'delta ReadOperationCount','io_write_operations':'delta WriteOperationCount'},
        'not_disk_physical':'Windows per-process I/O transfers include OS/cache/device accounting; they are not sector reads, disk wear, unique artifact sizes or all I/O caused systemwide.',
        'zero_rule':'A returned delta0 is only no counter increment during that sampled worker interval. Missing/unavailable measurement remains null/absent, never zero I/O.',
        'job_class9':'JOBOBJECT_EXTENDED_LIMIT_INFORMATION is queried only for configured memory limits and committed peaks. Its reserved IoInfo structure is never exported or used to infer zero I/O.',
        'artifact_rule':'Artifact byte totals are independent exact sizes of committed files present after execution, not a substitute for measured OS transfers.',
        'timing_rule':'Actual process CPU/wall interval and cumulative owned-job accounting have different start points; do not add them or compare logical schedule duration to arithmetic latency.',
        'energy':'NO MEDIDA','new_provider_calls':0,'new_native_ticks':0}
    with args.out.open('x',encoding='utf8')as stream:
        json.dump(result,stream,sort_keys=True,ensure_ascii=False,indent=2);stream.write('\n')
    print(json.dumps({'out':str(args.out),'sha256':sha(args.out),'rows':[{k:r[k]for k in
        ('policy','artifact_files_count','artifact_bytes_on_disk_sum','measured_process_interval')}for r in rows]}))


if __name__=='__main__':main()
