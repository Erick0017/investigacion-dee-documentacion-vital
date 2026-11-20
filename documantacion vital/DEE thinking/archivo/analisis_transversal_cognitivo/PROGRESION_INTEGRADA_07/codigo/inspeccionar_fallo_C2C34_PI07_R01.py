"""Read-only, bounded inspection of the preserved PI07 external34 failure.
No DEE/app imports, checkpoint, queue mutation, lock removal or process stop.
"""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,json,os,sqlite3
P=Path(__file__).resolve().parents[1];S=P/'estados/candidato/sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_CAND_01'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def file(p):return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def process(pid):
 result={'pid':int(pid),'operation':'OpenProcess_QUERY_LIMITED_INFORMATION_only','stopped':False}
 if os.name!='nt':return dict(result,determined=False,reason='Windows required')
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p]
 handle=k.OpenProcess(0x1000,False,int(pid))
 if not handle:
  error=ctypes.get_last_error();return dict(result,present=False if error==87 else None,winerror=error,determined=error==87)
 try:
  size=ctypes.c_uint32(32768);buffer=ctypes.create_unicode_buffer(size.value);k.QueryFullProcessImageNameW.argtypes=[ctypes.c_void_p,ctypes.c_uint32,ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint32)]
  image=buffer.value if k.QueryFullProcessImageNameW(handle,0,buffer,ctypes.byref(size)) else None
  if image is not None:image=buffer.value
  code=ctypes.c_uint32();k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];ok=k.GetExitCodeProcess(handle,ctypes.byref(code))
  return dict(result,present=True,image=image,exit_code=code.value if ok else None,running=code.value==259 if ok else None,determined=bool(ok))
 finally:k.CloseHandle(handle)
def main(a):
 target=a.salida.resolve()
 if target.exists()or not target.is_relative_to((P/'control').resolve()):raise ValueError('Fresh P7/control proof only')
 cardpath=S/'estado/vidas'/LIFE/'VIDA.json';card=read(cardpath);snapshot=S/card['snapshot'];db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3'
 before={str(p):sha(p)for p in(cardpath,snapshot,db)};con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro',uri=True);con.row_factory=sqlite3.Row
 try:
  rows=[]
  for row in con.execute('SELECT seq,id,payload,status,is_control,started_utc,finished_utc,error,LENGTH(result) AS result_bytes FROM requests WHERE seq>=3133 ORDER BY seq'):
   value=dict(row)
   for key in('payload','error'):
    if value[key] is not None:
     try:value[key]=json.loads(value[key])
     except ValueError:pass
   rows.append(value)
  meta={r['key']:json.loads(r['value'])for r in con.execute('SELECT key,value FROM meta')}
  counts=dict(con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status'))
  unresolved=[dict(r)for r in con.execute("SELECT seq,id,status FROM requests WHERE status IN('queued','processing','uncertain') ORDER BY seq")]
 finally:con.close()
 events=[]
 with(P/'ENSAYOS.jsonl').open(encoding='utf-8-sig')as f:
  for line in f:
   if 'CIERRE_CONJUNTO_FASE0' in line and any(k in line for k in('OWNER','pid','PID')):
    events.append(json.loads(line))
 events=events[-12:];pids={19956,19224}
 def collect(v):
  if isinstance(v,dict):
   for key,value in v.items():
    if key.lower()in('pid','worker_pid','owner_pid','child_pid','launcher_pid')and type(value)is int:pids.add(value)
    else:collect(value)
  elif isinstance(v,list):
   for value in v:collect(value)
 collect(meta);collect(events)
 local=S/'estado/servicios_locales'/LIFE;home=local/'PI04_C2C_COORDINACION_R01/dispositivo';devicepath=home/'ESTADO_DISPOSITIVO.json';device=read(devicepath)
 ext=local/'PI07_C2C_OFERTAS_R01/eventos.jsonl';extension_events=[json.loads(line)for line in ext.read_text('utf8').splitlines()]if ext.exists()else[]
 resources=[]
 for ordinal in range(30,34):
  resource=home/'reservoir'/('%04d.resource'%ordinal)
  resources.append(file(resource)if resource.exists()else{'path':str(resource),'missing':True})
 locks=[]
 for parent in(S/'estado/vidas'/LIFE,S/'estado/locks'):
  if parent.is_dir():
   locks.extend({'path':str(p),'bytes':p.stat().st_size}for p in parent.glob('*')if p.is_file()and('lock'in p.name.lower()or'owner'in p.name.lower()))
 after={str(p):sha(p)for p in(cardpath,snapshot,db)}
 result={'schema':'DEE.PI07.failure34.readonly_inspection.v1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'life_id':LIFE,'Native_executed':False,'world_or_queue_modified':False,'source_files_unchanged_during_inspection':before==after,'source_hashes':before,'current_saved_card':{'physical':card.get('physical'),'snapshot':card['snapshot'],'snapshot_sha256':sha(snapshot),'keys':list(card)},'SQLite':{'path':str(db),'counts':counts,'unresolved':unresolved,'scoped_requests':rows,'meta':meta,'WAL_exists':db.with_name(db.name+'-wal').exists(),'SHM_exists':db.with_name(db.name+'-shm').exists()},'scoped_OWNER_events':events,'scoped_process_handles':[process(pid)for pid in sorted(pids)],'locks_preserved':locks,'external_device':{'file':file(devicepath),'ordinal':device.get('ordinal'),'resources':len(device.get('resources',[])),'products':len(device.get('products',[])),'rejections':len(device.get('rejections',[])),'pending':device.get('pending'),'uncertain':device.get('uncertain'),'explicit_supply_history':device.get('explicit_supply_history')},'external34_events':extension_events,'four_new_resource_files':resources,'causal_diagnosis':{'cause':'New external34 protocol violates unchanged C2C protocol() finite bound2..32, checked only after external transaction had committed resource/device/protocol/journal changes.','validator_file':'capacidades/pi04_coordinacion_central_C2C.py','validator_line':142,'Native_physics_or_kernel_failure':False,'implementation_preflight_gap':'Pure transaction Fakes replaced operational_dependencies; they did not invoke the actual C2C validator before writes.','checkpoint_refusal':'Current34 effective component re-enters the same validator; failure can prevent checkpoint and stop checkpoint.','preservation_rule':'Do not resend, clear locks/queues, restart from the older saved card or silently rewrite resources/metadata. Snapshot, external state and RAM must be treated as separate preserved evidence until reconciled by an explicit reviewed recovery.'}}
 with target.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(target),'sha256':sha(target),'snapshot':result['current_saved_card'],'requests':[{k:r[k]for k in('seq','id','status')}for r in rows],'device':result['external_device'],'pids':result['scoped_process_handles'],'unchanged':before==after}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--salida',type=Path,required=True);main(ap.parse_args())
