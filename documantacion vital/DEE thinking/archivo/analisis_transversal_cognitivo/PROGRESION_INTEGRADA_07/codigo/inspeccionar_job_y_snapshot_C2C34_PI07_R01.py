"""Read only the exact recorded failed-owner job and last saved snapshot."""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,importlib.util,json
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema';C=P.parents[2]/'DEE Cognitive 2.0';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01';RUN='PI07_CIERRE_CONJUNTO_FASE0_c1f133cf'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def job_probe(name):
 if not name.startswith('Local\\DEE_DCS11_JOB_'):raise ValueError('Exact owned job namespace only')
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenJobObjectW.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_wchar_p];k.OpenJobObjectW.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p]
 handle=k.OpenJobObjectW(4,False,name)
 if not handle:return{'job':name,'opened_for_QUERY_only':False,'winerror':ctypes.get_last_error(),'processes_stopped':False}
 class IDs(ctypes.Structure):_fields_=[('assigned',ctypes.c_uint32),('listed',ctypes.c_uint32),('ids',ctypes.c_size_t*64)]
 try:
  ids=IDs();k.QueryInformationJobObject.argtypes=[ctypes.c_void_p,ctypes.c_int,ctypes.c_void_p,ctypes.c_uint32,ctypes.c_void_p]
  ok=k.QueryInformationJobObject(handle,3,ctypes.byref(ids),ctypes.sizeof(ids),None)
  return{'job':name,'opened_for_QUERY_only':True,'query_succeeded':bool(ok),'assigned_processes':ids.assigned,'listed_processes':ids.listed,'pids':list(ids.ids[:min(ids.listed,64)]),'winerror':None if ok else ctypes.get_last_error(),'processes_stopped':False}
 finally:k.CloseHandle(handle)
def main(a):
 target=a.salida.resolve()
 if target.exists()or not target.is_relative_to((P/'control').resolve()):raise ValueError('New P7/control proof only')
 log=P/'ENSAYOS.jsonl';start=None;last=None
 for line in log.read_text('utf-8-sig').splitlines():
  row=json.loads(line)
  if row.get('run')==RUN:
   if row.get('kind')=='OWNER_STARTED':start=row
   last=row
 if not start:raise ValueError('Exact historical owner/run missing')
 card=read(S/'estado/vidas'/LIFE/'VIDA.json');snapshot=S/card['snapshot'];digest=sha(snapshot)
 parserfile=C/'reproducibilidad/observador_pasivo.py';spec=importlib.util.spec_from_file_location('PI07_failed34_saved_snapshot_only',parserfile);parser=importlib.util.module_from_spec(spec);spec.loader.exec_module(parser);state=parser.snapshot_view(snapshot)
 metadata={}
 for key in('DEE.Cognitive.PI04.C2C.coordination.R01','DEE.Cognitive.PI07.C2C.explicit_environment34.R01','DEE.Cognitive.PI05.C2C.explicit_environment30.R01','DEE.Cognitive.PI07.regulation.environment.R03'):
  literal=state['metadata'].get(key)
  if literal is None:metadata[key]={'present':False};continue
  value=json.loads(literal);metadata[key]={'present':True,'literal_sha256':hashlib.sha256(literal.encode()).hexdigest(),'fields':{k:value[k]for k in('version','life_id','ordinal','arm','protocol_sha256','ready','pending','uncertain','log_count')if k in value}}
 result={'schema':'DEE.PI07.failed34.scoped_job_and_saved_snapshot.v1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'Native_imported_or_executed':False,'owner_started':{k:start.get(k)for k in('kind','run','life','pid','job')},'last_job_event':{k:last.get(k)for k in('kind','run','pid','error','forced_stop')},'exact_named_job_probe':job_probe(start['job']),'saved_snapshot':{'path':str(snapshot),'sha256':digest,'physical':state['physical'],'causal_prefix_sha256':state['causal_prefix_sha256'],'metadata':metadata},'saved_snapshot_unchanged_during_read':sha(snapshot)==digest,'scope':'A cached runningFalse or terminal queue does not prove a coherent operational cut. No OWNER_CLOSED witness exists for the failed owner. Named-job absence and exact PID checks are process evidence only; external device34 and interrupted-future markers remain preserved. No repair, restore, resubmit, stop or lock clearing performed.'}
 with target.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(target),'sha256':sha(target),'job':result['exact_named_job_probe'],'metadata':metadata,'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path,required=True);main(ap.parse_args())
