"""Harden only the Root source applier; scientific Stage stays literal."""
from pathlib import Path
import hashlib
H=Path(__file__).resolve().parent;source=H/'instalar_hooks_A1_PI08_R03.py';target=H/'instalar_hooks_A1_PI08_R04.py'
if target.exists():raise FileExistsError('Prepared applier revision preserved')
s=source.read_text('utf8').replace('PI08_A1_HOOKS_APLICADOS_R03.json','PI08_A1_HOOKS_APLICADOS_R04.json').replace('ORIGINALES_HOOKS_A1_PI08_R03','ORIGINALES_HOOKS_A1_PI08_R04')
s=s.replace('import argparse,ast,datetime,hashlib,json,os,shutil','import argparse,ast,datetime,hashlib,json,os,shutil,ctypes')
anchor='def main(a):'
guards='''def regular(path):
 path=Path(path)
 for node in(path,*path.parents):
  if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&0x400):raise ValueError('No linked/reparse source deployment path')
 return path
def owner_process_proof(owner):
 pid=owner.get('pid')
 if type(pid)is not int or pid<=0:raise ValueError('An actual cached ownerPID is required; do not infer absence')
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p]
 handle=k.OpenProcess(0x1000,False,pid)
 if not handle:
  error=ctypes.get_last_error()
  if error!=87:raise ValueError('Owner process identity/absence uncertain: '+str(error))
  return {'pid':pid,'present':False,'Win32_error':87,'queried_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'process_stopped':False}
 try:
  code=ctypes.c_uint32();k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)]
  if not k.GetExitCodeProcess(handle,ctypes.byref(code))or code.value==259:raise ValueError('Cached ownedPID is still active or uncertain; Root must reconcile exact identity before source deployment')
  return {'pid':pid,'present':True,'exit_code':code.value,'queried_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'process_stopped':False}
 finally:k.CloseHandle(handle)

'''
if s.count(anchor)!=1:raise ValueError('Exact applier anchor required')
s=s.replace(anchor,guards+anchor)
s=s.replace("if owner.get('running')or pending or db.with_name(db.name+'-wal').exists():raise ValueError('Closed/reconciled/noWAL owner required before source CAS')", "wal=db.with_name(db.name+'-wal')\n if owner.get('running')or pending or(wal.exists()and wal.stat().st_size):raise ValueError('Closed/reconciled/no nonemptyWAL owner required before source CAS')\n processproof=owner_process_proof(owner)\n world_id=card.get('world_id',LIFE);lockroot=target/'estado/locks'\n locks=[path for path in lockroot.glob('*')if path.is_file()and(world_id in path.name or LIFE in path.name)]if lockroot.exists()else[]\n if locks:raise ValueError('An affected writer lock remains; never clear it in the source applier')\n if(target/'estado/vidas'/LIFE/'FUTURO_INTERRUMPIDO.json').exists():raise ValueError('Interrupted scientific future preserved; no source transition until explicit reconciliation')\n critical={str(path):sha(path)for path in(target/'estado/vidas'/LIFE/'VIDA.json',target/card['snapshot'],db)}")
s=s.replace("source=Path(row['source']);destination=target/row['file']", "source=regular(Path(row['source']));destination=regular(target/row['file'])")
s=s.replace("'source_backups':str(backup),'Native_executed':False", "'source_backups':str(backup),'scoped_owner_process_proof':processproof,'affected_writer_locks':[],'allowed_zero_byte_WAL':wal.exists()and wal.stat().st_size==0,'state_files_unchanged':all(sha(Path(path))==digest for path,digest in critical.items()),'state_before_hashes':critical,'Native_executed':False")
compile(s,str(target),'exec');target.write_text(s,encoding='utf8');print(str(target));print(hashlib.sha256(target.read_bytes()).hexdigest())
