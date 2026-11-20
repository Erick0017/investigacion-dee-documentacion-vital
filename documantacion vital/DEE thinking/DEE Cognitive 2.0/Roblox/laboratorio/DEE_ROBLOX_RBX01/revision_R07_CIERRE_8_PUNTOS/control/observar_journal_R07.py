"""Read only a fixed prefix of declared journal files; no DB/runtime imports."""
from pathlib import Path
import argparse,datetime,hashlib,json
MAX=20_000_000
def rows(path):
    path=Path(path);before=path.stat()
    if before.st_size>MAX:raise ValueError('Explicit journal exceeds bounded20MB; do not imply latest coverage')
    with path.open('rb')as f:raw=f.read(before.st_size)
    after=path.stat();tail=not raw.endswith(b'\n')and bool(raw)
    if tail:raw=raw[:raw.rfind(b'\n')+1]if b'\n'in raw else b''
    parsed=[json.loads(x)for x in raw.decode('utf-8-sig').splitlines()if x.strip()]
    return parsed,{'path':str(path),'bytes_read':len(raw),'sha256_read_prefix':hashlib.sha256(raw).hexdigest(),
      'source_bytes_before':before.st_size,'source_bytes_after':after.st_size,'unfinished_tail_excluded':tail,
      'changed_while_reading':(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns)}
def observe(events,owner=None):
    data,source=rows(events);intents={};completed={};cycles=[];numeric=[];latest_native=None
    for row in data:
        kind=row.get('kind')
        if kind=='NATIVE_INTENT':intents[row['context']['operation_id']]=row
        elif kind=='NATIVE_COMPLETED':
            key=row['operation_id'];completed[key]=row
            value=row.get('result',{});latest_native={'utc':row.get('utc'),'cycle':row.get('cycle'),'phase':row.get('phase'),
              'operation_id':key,'native_tick':value.get('nativeTick'),'action':value.get('action'),'null':value.get('null'),
              'accepted':value.get('accepted'),'wall_seconds':row.get('wall_seconds')}
            if row.get('phase')=='function':numeric.append({'cycle':row.get('cycle'),'operation_id':key,'toolResult':value.get('toolResult')})
        elif kind=='OPPORTUNITY_COMPLETED':
            s=row.get('state_after',{});cycles.append({'cycle':row.get('cycle'),'native_tick':s.get('nativeTick'),
              'station':s.get('station'),'resource_count':s.get('resourceCount'),'delivered':s.get('delivered'),
              'numberA_present':s.get('numberAPresent'),'numberA_actual':s.get('numberA'),'codeB_present':s.get('codeBPresent'),
              'codeB_actual':s.get('finalCode'),'Native_route':row.get('Native_route'),'executed_route':row.get('executed_route')})
    result={'schema':'DEE.R07.passive_journal_observation.R01','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'source':source,'complete_lines':len(data),'completed_opportunities':cycles,'latest_native_completed':latest_native,'functions':numeric,
      'unresolved_journal_intents':[{'operation_id':key,'phase':r.get('phase'),'cycle':r.get('cycle'),'intent_utc':r.get('utc')}for key,r in intents.items()if key not in completed],
      'scope':'File evidence only, not an instantaneous world/queue/process observation. An unmatched intent does not prove admission or pending status. No request is retried.',
      'Native_calls':0,'MCP_calls':0,'SQLite_reads':0}
    if owner:
        journal,meta=rows(owner);eligible=[r for r in journal if str(r.get('run','')).startswith('R07_')]
        result['owner_source']=meta
        for kind in('OWNER_STARTED','OWNED_PROCESS_RESOURCES','OWNER_CLOSED'):
            result['last_'+kind.lower()]=next((r for r in reversed(eligible)if r.get('kind')==kind),None)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--events',type=Path,required=True);p.add_argument('--owner-journal',type=Path);p.add_argument('--output',type=Path);p.add_argument('--compact',action='store_true');a=p.parse_args()
    value=observe(a.events,a.owner_journal)
    if a.output:
        with a.output.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2)
    if a.compact:
        for key in('last_owner_started','last_owner_closed'):
            r=value.get(key)
            if r:
                keep={k:r.get(k)for k in('kind','run','life','pid','job','exit_code','utc')}
                cache=r.get('initial_status',r.get('final_status',{}))
                keep['cached_status']={k:cache.get(k)for k in('wall_utc','tick','running','paused','uncertain_external_result')}
                value[key]=keep
    print(json.dumps(value,ensure_ascii=False,indent=2))
