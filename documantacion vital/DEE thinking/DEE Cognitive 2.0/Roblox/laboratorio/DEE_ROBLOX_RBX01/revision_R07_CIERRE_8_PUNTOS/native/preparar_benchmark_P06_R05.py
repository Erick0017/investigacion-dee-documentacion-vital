"""Finish the unexecuted P06 draft with final lease guards; no Native calls."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parent.parent
old=ROOT/'native/benchmark_dependencias_P06_R04.py'
out=ROOT/'native/benchmark_dependencias_P06_R05.py'
source=old.read_text('utf-8').replace('HARD_FINISH=1794874020','HARD_FINISH=1794884820')
source=source.replace('PROTOCOLO_P06_DEPENDENCIAS_R04.json','PROTOCOLO_P06_DEPENDENCIAS_R05.json')
# Report an observed tick delta, never assume zero if the passive guard failed.
source=source.replace("    finally:\n        if world is not None:world.close()\n        if cache is not None:cache.close()",
 "    finally:\n        final_physical=None\n        if world is not None:\n            try:final_physical=world.fingerprint()\n            finally:world.close()\n        if cache is not None:cache.close()")
source=source.replace("'Native_requests':0,'Native_ticks':0,'service_loop_started':False,'queue_writer_created':False,",
 "'Native_requests_submitted':0,'Native_ticks_allowed':0,\n      'Native_ticks':final_physical['tick']-basis['expected_tick']if final_physical is not None else None,\n      'final_physical':final_physical,'service_loop_started':False,'queue_writer_created':False,")
source=source.replace('benchmark.R04','benchmark.R05').replace('Benchmark.R04','Benchmark.R05')
if out.exists():raise ValueError('Preserve prepared benchmark source')
compile(source,str(out),'exec');out.write_text(source,encoding='utf-8',newline='\n')
pold=ROOT/'protocolo/PROTOCOLO_P06_DEPENDENCIAS_R04.json';pnew=ROOT/'protocolo/PROTOCOLO_P06_DEPENDENCIAS_R05.json'
protocol=json.loads(pold.read_text('utf-8'));protocol['schema']='DEE.R07.P06.FullDependenciesProspective.R05'
protocol['campaign_hard_close_utc']='2026-11-17T03:07:00Z'
protocol['administrative_note']='Only align the draft guard with the final12h R05 lease. The P06 criterion/pass order/zero-tick scope were fixed before execution and are unchanged.'
if pnew.exists():raise ValueError('Preserve prospective P06 protocol')
pnew.write_text(json.dumps(protocol,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
proof={'schema':'DEE.R07.P06.prepared_driver.R05','source':str(out),
 'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'parent_draft_sha256':hashlib.sha256(old.read_bytes()).hexdigest(),
 'protocol':str(pnew),'protocol_sha256':hashlib.sha256(pnew.read_bytes()).hexdigest(),
 'status':'ROOT_ONLY_PREPARED_NOT_NATIVE_EXECUTED','criterion_and_scope_unchanged':True,
 'observed_ticks_reporting':'Nullable actual final_tick minus recorded_tick; no unconditional zero on error'}
(ROOT/'native/prototipos/BENCHMARK_P06_PREPARADO_R05.json').write_text(json.dumps(proof,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps(proof,indent=2,ensure_ascii=False))
