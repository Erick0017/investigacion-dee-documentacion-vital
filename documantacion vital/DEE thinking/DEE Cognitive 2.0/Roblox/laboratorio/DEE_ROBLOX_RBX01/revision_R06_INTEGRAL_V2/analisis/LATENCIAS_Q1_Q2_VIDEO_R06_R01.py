"""Passive Q1/Q2 latency median from unique actual completed R06 phase events."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,statistics
ARMS=('LIVE_NATIVE','PROGRAMMED','CONVENTIONAL_AI')
PHASES=('decision','query_sensor')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def main(entries,output):
    output=Path(output)
    if output.exists()or not output.parent.is_dir():raise ValueError('FRESH_OUTPUT_REQUIRED')
    records={};sources=[];aliases=0
    for entry in entries:
        arm,name=entry.split('=',1)
        if arm not in ARMS:raise ValueError('PARTICIPANT_REQUIRED')
        path=Path(name).resolve(strict=True)
        for item in(path,*path.parents):
            if item.is_symlink()or getattr(item.lstat(),'st_file_attributes',0)&1024:raise ValueError('LINK_REFUSED')
        before=path.stat()
        if before.st_size>10_000_000:raise ValueError('FINITE_INPUT_BOUND')
        raw=path.read_bytes();after=path.stat()
        if(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('INPUT_CHANGED')
        if raw and not raw.endswith(b'\n'):raise ValueError('UNFINISHED_JSONL')
        source={'path':str(path),'bytes':len(raw),'sha256':sha(raw),'participant':arm};sources.append(source)
        for line_no,line in enumerate(raw.decode('utf-8-sig').splitlines(),1):
            if not line.strip():continue
            row=json.loads(line)
            if row.get('kind')not in('NATIVE_COMPLETED','BACKEND_COMPLETED')or row.get('phase')not in PHASES:continue
            identifier=row.get('operation_id');value=row.get('wall_seconds');cycle=row.get('cycle')
            if not isinstance(identifier,str)or not identifier.startswith('R06_'):raise ValueError('ACTUAL_R06_OPERATION_ID_REQUIRED')
            if type(cycle)is not int or not 5<=cycle<=28:raise ValueError('R06_NEW_OPPORTUNITY_RANGE_REQUIRED')
            if type(value)not in(int,float)or not math.isfinite(value)or value<0:raise ValueError('ACTUAL_NONNEGATIVE_WALL_SECONDS_REQUIRED')
            expected='NATIVE_COMPLETED'if arm=='LIVE_NATIVE'else'BACKEND_COMPLETED'
            if row['kind']!=expected:raise ValueError('EXECUTION_SOURCE_PARTICIPANT_MISMATCH')
            key=(arm,identifier)
            if key in records:
                if canonical(records[key]['row'])!=canonical(row):raise ValueError('CONFLICTING_PHASE_ALIAS')
                aliases+=1;continue
            records[key]={'participant':arm,'source_index':len(sources),'source_line':line_no,'row':row}
    summary={}
    for arm in ARMS:
        summary[arm]={}
        for phase in('Q1_Q2_combined',*PHASES):
            rows=[x['row']for(a,_),x in records.items()if a==arm and(phase=='Q1_Q2_combined'or x['row']['phase']==phase)]
            values=[x['wall_seconds']for x in rows]
            summary[arm][phase]={'n':len(values),'p50_seconds':statistics.median(values)if values else None,
                'minimum_seconds':min(values)if values else None,'maximum_seconds':max(values)if values else None,
                'cycles_observed':sorted({x['cycle']for x in rows})}
    report={'schema':'DEE.INTEGRAL.V2.Q1Q2_actual_latency.R01','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'summary':summary,'identical_aliases_deduplicated':aliases,'sources':sources,'unique_completed_responses':len(records),
        'definition':'Median of actual per-call wall_seconds on unique completed decision/query_sensor operations; Q1 and Q2 pooled for the video row, also split below.',
        'scope':'Backend/Native response latency, not CPU, owner lifetime, full opportunity latency, render FPS, energy or inherited S.latency. Failed/uncompleted calls are not synthesized; denominators are shown.',
        'Native_model_MCP_SQLite_calls':0}
    output.mkdir()
    primary=''.join(canonical(v)+'\n'for v in sorted(records.values(),key=lambda x:(x['participant'],x['row']['cycle'],x['row']['phase'])))
    (output/'PRIMARIOS_Q1_Q2.jsonl').write_text(primary,encoding='utf-8')
    report['selected_primaries']={'file':'PRIMARIOS_Q1_Q2.jsonl','bytes':len(primary.encode('utf-8')),'sha256':sha(primary.encode('utf-8'))}
    (output/'LATENCIAS_Q1_Q2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--events',action='append',required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=main(a.events,a.output);print(json.dumps(r['summary'],ensure_ascii=False,indent=2))
