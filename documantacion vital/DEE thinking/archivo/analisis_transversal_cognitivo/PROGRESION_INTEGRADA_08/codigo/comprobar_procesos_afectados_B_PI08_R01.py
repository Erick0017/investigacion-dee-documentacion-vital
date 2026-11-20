"""Pure stdlib scoped process/closed-queue proof. Never stops a process,
clears a lock, changes SQLite or imports DEE. Run freshly for each admin phase.
"""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,json,os,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';SOURCE=P/'estados/B_REAL_R01/sistema';TARGET=C/'sistema';LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01';PARENT='ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for node in(p,*p.parents):
  if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&0x400):raise ValueError('No linked scoped process evidence path')
def pid_proof(owner):
 pid=owner.get('pid');stamp=owner.get('wall_utc')
 if type(pid)is not int or pid<=0:return {'no_live_affected_writer':False,'reason':'No actual cached owner PID'}
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p];handle=k.OpenProcess(0x1000,False,pid)
 if not handle:
  error=ctypes.get_last_error();return {'pid':pid,'present':False if error==87 else None,'winerror':error,'no_live_affected_writer':error==87,'process_stopped':False}
 class FT(ctypes.Structure):_fields_=[('low',ctypes.c_uint32),('high',ctypes.c_uint32)]
 try:
  code=ctypes.c_uint32();k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];ok=k.GetExitCodeProcess(handle,ctypes.byref(code))
  if not ok:return {'pid':pid,'present':True,'no_live_affected_writer':False,'reason':'GetExitCodeProcess uncertain','process_stopped':False}
  if code.value!=259:return {'pid':pid,'present':True,'exit_code':code.value,'no_live_affected_writer':True,'process_stopped':False}
  buffer=ctypes.create_unicode_buffer(32768);length=ctypes.c_uint32(32768);k.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint32)];image=buffer.value if k.QueryFullProcessImageNameW(handle,0,buffer,ctypes.byref(length))else None
  if image is not None:image=buffer.value
  values=[FT()for _ in range(4)];k.GetProcessTimes.argtypes=[ctypes.c_void_p,*([ctypes.POINTER(FT)]*4)];times=k.GetProcessTimes(handle,*[ctypes.byref(value)for value in values]);created=None
  if times:created=datetime.datetime.fromtimestamp((((values[0].high<<32)|values[0].low)-116444736000000000)/10000000,datetime.timezone.utc)
  wall=datetime.datetime.fromisoformat(stamp.replace('Z','+00:00')).astimezone(datetime.timezone.utc)if isinstance(stamp,str)else None
  reused=bool(image and Path(image).name.lower()not in('python.exe','pythonw.exe')and created and wall and created>wall and owner.get('running')is False)
  return {'pid':pid,'present':True,'running':True,'current_image':image,'creation_utc':None if created is None else created.isoformat(),'cached_owner_wall_utc':stamp,'PID_reused_later_other_nonPython_image':reused,'no_live_affected_writer':reused,'reason':'Different later process instance; original Native owner cannot be this current PID instance.'if reused else'Active/uncertain Python or undemonstrated identity; stop and inspect, never kill.','process_stopped':False}
 finally:k.CloseHandle(handle)
def inspect(role,system,life):
 cardpath=system/'estado/vidas'/life/'VIDA.json'
 if not cardpath.exists():return {'role':role,'system':str(system),'life_id':life,'present':False,'no_live_affected_writer':True,'scope':'Target not yet created, no world opened.'}
 regular(cardpath);card=read(cardpath);world=card['world_id'];db=system/'estado/servicios_persistentes'/world/'cola.sqlite3';regular(db);wal=db.with_name(db.name+'-wal');shm=db.with_name(db.name+'-shm')
 if wal.exists()and wal.stat().st_size:raise ValueError('Nonempty scoped WAL; preserve before attempting a process claim')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  integrity=con.execute('PRAGMA integrity_check').fetchone()[0];row=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(row[0])if row else{};pending=[dict(zip(('id','status'),r))for r in con.execute("SELECT id,status FROM requests WHERE status IN('queued','processing','uncertain')")]
 finally:con.close()
 markers=[path for path in(system/'estado/locks'/(world+'.lock'),cardpath.parent/'FUTURO_INTERRUMPIDO.json',db.parent/'IMPORTACION_EN_CURSO.json')if path.exists()];locks=system/'estado/locks'
 if locks.exists():markers+=list(p for p in locks.glob('*')if p.is_file()and(world in p.name or life in p.name)and p not in markers)
 process=pid_proof(owner);valid=integrity=='ok'and owner.get('running')is False and not pending and not markers and process['no_live_affected_writer']
 return {'role':role,'system':str(system),'life_id':life,'present':True,'world_id':world,'physical':card['physical'],'card':{'path':str(cardpath),'sha256':sha(cardpath)},'snapshot':{'path':str(system/card['snapshot']),'sha256':sha(system/card['snapshot'])},'SQLite':{'path':str(db),'integrity_check':integrity,'owner_cached':{k:owner.get(k)for k in('pid','running','wall_utc','tick','last_saved_tick')},'unresolved':pending,'WAL_bytes':wal.stat().st_size if wal.exists()else 0,'SHM_bytes':shm.stat().st_size if shm.exists()else 0},'preserved_marker_paths':[str(p)for p in markers],'Win32_process':process,'no_live_affected_writer':valid}
def main(a):
 output=a.salida.resolve()
 if output.exists()or not output.is_relative_to((P/'control').resolve()):raise ValueError('New P8/control proof path required')
 scope=[('protected_parent',TARGET,PARENT),('source_successor',SOURCE,LIFE),('product_successor',TARGET,LIFE)];evidence=[]
 for role,system,life in scope:
  try:evidence.append(inspect(role,system,life))
  except Exception as exc:evidence.append({'role':role,'system':str(system),'life_id':life,'no_live_affected_writer':False,'error':type(exc).__name__+': '+str(exc),'preservation_no_intervention':True})
 result={'schema':'DEE.PI08.affected_writer_scope.v1','recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'no_live_affected_writers':all(row['no_live_affected_writer']for row in evidence),'scope':[{'role':role,'system':str(system),'life_id':life}for role,system,life in scope],'affected_life_ids':[PARENT,LIFE],'evidence':evidence,'Native_imported_or_executed':False,'processes_stopped':False,'queues_locks_or_states_modified':False,'reuse_limit_seconds':600}
 with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(output),'sha256':sha(output),'no_live_affected_writers':result['no_live_affected_writers'],'roles':[{'role':r['role'],'safe':r['no_live_affected_writer'],'error':r.get('error')}for r in evidence]}));return 0 if result['no_live_affected_writers']else 2
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path,required=True);raise SystemExit(main(ap.parse_args()))
