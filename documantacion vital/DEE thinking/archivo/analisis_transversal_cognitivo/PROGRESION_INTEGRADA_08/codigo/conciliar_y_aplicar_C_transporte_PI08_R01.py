"""Root-only stdlib/Win32 reconciliation and exact two-file C CAS, Native0.
Never kills processes, edits a queue/snapshot or removes a world-owner lock.
Only the exact dead Root's administrative mutex can be reconciled.
"""
from pathlib import Path
from ctypes import wintypes as W
import argparse, ctypes, datetime, hashlib, importlib.util, json, os, shutil, sqlite3

P=Path(__file__).resolve().parents[1];H=P/'codigo';C=P.parents[2]/'DEE Cognitive 2.0'
S=P/'estados/C_R03/sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_C_01'
RUN='PI08_C_PREPARAR_R03_8ec32a9a';KEY='DEE.Cognitive.PI08.conditional_sensor_register_access.C.R02'
PLAN=H.parent/'control/PLAN_FIX_C_IDENTIDAD_TRANSPORTE_PI08_R01.json'

def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def load(name,p):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def process_tree():
 k=ctypes.WinDLL('kernel32',use_last_error=True)
 class PE(ctypes.Structure):
  _fields_=[('dwSize',W.DWORD),('cntUsage',W.DWORD),('th32ProcessID',W.DWORD),('th32DefaultHeapID',ctypes.c_size_t),('th32ModuleID',W.DWORD),('cntThreads',W.DWORD),('th32ParentProcessID',W.DWORD),('pcPriClassBase',W.LONG),('dwFlags',W.DWORD),('szExeFile',W.WCHAR*260)]
 k.CreateToolhelp32Snapshot.argtypes=[W.DWORD,W.DWORD];k.CreateToolhelp32Snapshot.restype=W.HANDLE
 k.Process32FirstW.argtypes=[W.HANDLE,ctypes.POINTER(PE)];k.Process32NextW.argtypes=k.Process32FirstW.argtypes
 k.CloseHandle.argtypes=[W.HANDLE]
 handle=k.CreateToolhelp32Snapshot(2,0);require(handle not in(None,ctypes.c_void_p(-1).value),'Cannot enumerate actual current descendants')
 rows=[]
 try:
  entry=PE();entry.dwSize=ctypes.sizeof(entry);ok=k.Process32FirstW(handle,ctypes.byref(entry))
  while ok:
   rows.append({'pid':int(entry.th32ProcessID),'parent_pid':int(entry.th32ParentProcessID),'image':entry.szExeFile});ok=k.Process32NextW(handle,ctypes.byref(entry))
 finally:k.CloseHandle(handle)
 return rows

def main(args):
 failpath=P/'control/PI08_C_PREPARAR_R03.json';fail=read(failpath)
 require(fail['life_id']==LIFE and fail['phase']=='preparar'and fail['new_Native_ticks']==0 and fail['initial_tick']==fail['final_tick']==875451,'Only the actual zero-Native C startup failure')
 require(not fail['records']and not fail['intervals']and fail['opportunities_completed']==0,'Material C operation exists; never retry an ambiguous ID')
 marker=P/'PI08_ROOT_NATIVE_WRITER.lock';require(marker.is_file(),'Exact failed Root mutex required')
 helper=load('PI08_C_closed_scope_RO',H/'comprobar_procesos_afectados_PI08_R01.py');helper.regular(marker)
 mark=read(marker);require(mark.get('pid')==22192 and mark.get('life_id')==LIFE and mark.get('phase')=='preparar','Another Root mutex must not be touched')
 scope=helper.inspect('failed_C_pre_ready',S,LIFE)
 require(scope['SQLite']['integrity_check']=='ok'and not scope['SQLite']['unresolved']and not scope['SQLite']['WAL_bytes']and not scope['preserved_marker_paths'],'Queue/WAL/world lock/interrupted future unresolved')
 require(scope['SQLite']['owner_cached']['running']is False,'Cached owner is running; actual processes must also be checked')
 samples=[json.loads(line)for line in(P/'ENSAYOS.jsonl').read_text('utf8').splitlines()if RUN in line]
 owned={r['pid']for r in samples if r.get('kind')=='OWNED_PROCESS_RESOURCES'}
 require(owned=={17316} and all(r.get('job_memory_limit')==536870912 for r in samples if r.get('kind')=='OWNED_PROCESS_RESOURCES'),'Actual failed owned PID/job evidence differs')
 processes=[helper.pid_proof({'pid':pid})for pid in sorted({22192,28563}|owned)]
 require(all(row['no_live_affected_writer']for row in processes),'Failed Root/outer/owner process remains live or uncertain')
 tree=process_tree();roots={22192,28563}|owned;descendants=set()
 while True:
  found={r['pid']for r in tree if r['parent_pid']in roots|descendants}-roots
  if found<=descendants:break
  descendants|=found
 require(not descendants,'Live descendant of the failed supervised process remains; never force-stop or hide it')
 cardpath=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardpath)
 parser=load('PI08_C_passive_snapshot',C/'reproducibilidad/observador_pasivo.py')
 pair=P/'pares/PI08_B_REAL_POST18_T875451';manifest=read(pair/'EXPORTACION_SERVICIO.json')
 require(sha(pair/'EXPORTACION_SERVICIO.json')=='15179db03e175bae1f3e830f3ef5b691c69e2061c1703832ad47a25b105f2f7d','Original B source manifest changed')
 source=parser.snapshot_view(pair/manifest['native_snapshot']);actual=parser.snapshot_view(S/card['snapshot'])
 comparison=parser.compare_native(source,actual,allow_service=True)
 require(actual['physical']['N']==67 and actual['physical']['tick']==875451 and KEY not in actual['metadata'],'C material history or changed source exists')
 db=Path(scope['SQLite']['path']);con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:requests=con.execute("SELECT id,status FROM requests WHERE id LIKE 'PI08_C_%'").fetchall()
 finally:con.close()
 require(not requests,'Actual C transport request exists; preserve and inspect rather than repeat')
 require(fail['protected_before']==fail['protected_after']and all(sha(Path(p))==d for p,d in fail['protected_after'].items()),'Protected actual A changed')
 plan=read(PLAN);require(sha(PLAN)=='bb7ba3224e6d1186f41248cc6a600f03f8cdd3e99943015d7d8f14978df1a08c'and plan['applied']is False,'Exact immutable transport proposal required')
 for row in plan['scientific_files_literal']:require(sha(row['file'])==row['sha256'],'Scientific C/B source/protocol changed')
 for row in plan['files']:
  target=S/row['relative'];helper.regular(target)
  require((not target.exists())if row['before_sha256']is None else sha(target)==row['before_sha256'],'Transport CAS source changed')
  require(sha(row['proposal'])==row['after_sha256'],'Prepared transport code changed')
 frozen={str(p):sha(p)for p in(cardpath,S/card['snapshot'],db,marker)}
 proof={'schema':'DEE.PI08.C.zero_Native_startup_transport_reconciliation.R01','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
  'failed_proof':{'path':str(failpath),'sha256':sha(failpath)},'life_id':LIFE,'N':67,'T':875451,'Native_executed':False,
  'Win32_actual_failed_process_checks':processes,'Win32_no_live_descendants_of_actual_failed_ancestors':True,
  'historical_Native_backend_child_PID_identified':False,'job_scope':'Original Root and owned process dead; no live descendants seen. Original Job used KILL_ON_JOB_CLOSE; its noninheritable supervision handle cannot survive Root exit. No historical Job handle is reopened or falsely queried.',
  'closed_queue_scope':scope,'Native_complete_comparison':comparison,'no_C_KEY_or_C_requests':True,'root_mutex_original':mark,'root_mutex_sha256':sha(marker),
  'plan':{'path':str(PLAN),'sha256':sha(PLAN)},'applied':False,'root_mutex_reconciled':False,'world_locks_or_queues_or_snapshots_modified':False,'processes_stopped':False}
 if args.aplicar:
  out=P/'control/FIX_C_IDENTIDAD_TRANSPORTE_APLICADO_PI08_R01.json';require(not out.exists(),'Prior application proof preserved')
  for row in plan['files']:
   target=S/row['relative']
   if row['before_sha256']is None:
    with target.open('xb')as stream:stream.write(Path(row['proposal']).read_bytes())
   else:
    temporary=target.with_name(target.name+'.PI08_C_TRANSPORTE.tmp');require(not temporary.exists(),'Unexpected pending code swap')
    shutil.copyfile(row['proposal'],temporary);os.replace(temporary,target)
   require(sha(target)==row['after_sha256'],'Code CAS failed')
  require(all(sha(Path(path))==digest for path,digest in frozen.items()),'State/DB/mutex changed during code-only CAS')
  proof['applied']=True;proof['root_mutex_reconciled']=True;proof['actual_files']=plan['files']
  with out.open('x',encoding='utf8')as stream:json.dump(proof,stream,ensure_ascii=False,indent=2);stream.write('\n')
  require(read(marker)==mark and sha(marker)==frozen[str(marker)],'Root mutex changed; do not remove')
  marker.unlink()
  print(json.dumps({'proof':str(out),'sha256':sha(out),'applied':True,'Native_ticks':0,'only_dead_Root_mutex_removed':True}))
 else:print(json.dumps(proof,ensure_ascii=False,indent=2))

if __name__=='__main__':
 cli=argparse.ArgumentParser(description=__doc__);cli.add_argument('--aplicar',action='store_true');main(cli.parse_args())
