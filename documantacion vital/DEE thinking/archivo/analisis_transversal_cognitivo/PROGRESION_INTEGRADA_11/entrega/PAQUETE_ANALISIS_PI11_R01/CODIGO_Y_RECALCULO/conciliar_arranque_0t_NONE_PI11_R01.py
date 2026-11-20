"""Read/standard SQLite close of one proven zero-tick failed diagnostic startup.

Never purges requests or edits Native state. Retains evidence and an exact DB
backup before a standard zero-frame WAL checkpoint. Removes only this Root
campaign's exact dead-process marker after all identity/hash checks pass.
"""
from pathlib import Path
from datetime import datetime,timezone
import ctypes,hashlib,json,shutil,sqlite3
P=Path(__file__).resolve().parents[1];LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_PI11_NONE01';D=P/'estados/NONE01';S=D/'sistema';M=P/'PI11_ROOT_NATIVE_WRITER.lock'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def new(p,v):
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')
def absent(pid):
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p;k.CloseHandle.argtypes=[ctypes.c_void_p];h=k.OpenProcess(0x1000,False,pid)
 if h:k.CloseHandle(h);raise ValueError('PID exists; no marker removal or SQLite write: '+str(pid))
 error=ctypes.get_last_error();need(error==87,'Uncertain inaccessible PID: '+str(pid));return {'pid':pid,'Win32_error':error,'absent':True}
def main():
 need(M.resolve(strict=True)==P.resolve()/'PI11_ROOT_NATIVE_WRITER.lock'and not M.is_symlink()and not(getattr(M.lstat(),'st_file_attributes',0)&1024),'Exact regular scoped marker only')
 marker=read(M);need(marker['life_id']==LIFE and marker['pid']==9680 and marker['tag']=='PI11_NONE01_16_OWNER_R01','Different marker/process; do not remove')
 processes=[absent(n)for n in(9680,16672)]
 error_file=P/'control/PI11_NONE01_16_OWNER_R01.json';v=read(error_file)
 need(v['life_id']==LIFE and v['initial_tick']==v['final_tick']==947395 and v['new_Native_ticks']==0 and v['records']==[]and v['protected_before']==v['protected_after'],'Not the documented zero-admission startup')
 need(v['initial_saved_Native']==v['final_saved_Native'],'Saved Native state changed during failed startup')
 imported=read(D/'IMPORTACION_PI11.json');expected=imported['directory_transport']['critical_hashes_before']
 card=S/'estado/vidas'/LIFE/'VIDA.json';snap=S/read(card)['snapshot'];db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3'
 for f in(card,snap,db):need(sha(f)==expected[str(f)],'Imported critical bytes changed; no reconciliation: '+str(f))
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity')
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);need(owner.get('running')is False and not owner.get('pid'),'Unexpected live/cached owner')
  need(con.execute("SELECT COUNT(*)FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'Unresolved operation; never purge')
  statuses=dict(con.execute('SELECT status,COUNT(*)FROM requests GROUP BY status'))
 finally:con.close()
 for f in(S/'estado/locks').glob('*')if(S/'estado/locks').exists()else[]:need(LIFE not in f.name,'World lock remains')
 out=P/'control/RECONCILIACION_ARRANQUE_NONE_0T_PI11_R01';need(not out.exists(),'Preserved prior attempt; no retry');out.mkdir()
 shutil.copyfile(M,out/'ROOT_MARKER_ANTES.json');shutil.copyfile(db,out/'cola_ANTES.sqlite3')
 before={str(f):sha(f)for f in(card,snap,db)};aux=[]
 for suffix in('-wal','-shm'):
  f=Path(str(db)+suffix)
  if f.exists():
   aux.append({'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f)});shutil.copyfile(f,out/('cola_ANTES.sqlite3'+suffix))
 need(all(r['bytes']==0 for r in aux if r['path'].endswith('-wal')),'A nonempty WAL is not a zero-frame administrative close')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=rw',uri=True,timeout=0)
 try:
  checkpoint=list(con.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchone());need(checkpoint[0]==0,'SQLite checkpoint busy; do not remove marker')
 finally:con.close()
 need(before=={str(f):sha(f)for f in(card,snap,db)},'Critical bytes changed; preserve and stop')
 need(not any(Path(str(db)+s).exists()and Path(str(db)+s).stat().st_size for s in('-wal','-shm')),'Auxiliary remains; no marker removal')
 need(read(M)==marker,'Concurrent marker change');M.unlink()
 result={'schema':'DEE.PI11.proven_zero_tick_failed_startup_reconciliation.R01','at_utc':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,'owner_proof':{'path':str(error_file),'sha256':sha(error_file)},'actual_processes_absent':processes,'no_new_Native_proven':True,'Native_tick':947395,'Native_card_snapshot_SQLite_literal_unchanged':True,'pending_requests':0,'queue_status_counts':statuses,'auxiliary_before':aux,'standard_SQLite_zero_frame_checkpoint':checkpoint,'Root_marker_removed':str(M),'world_locks_removed':0,'requests_deleted_or_retried':0,'Native_inputs':0,'Native_ticks':0,'conservative_original_failure_proof_preserved':True,'note':'A prior mode=ro diagnostic read created WAL/SHM auxiliaries. This standard close is an administrative operation, not Native recovery or learning.'}
 new(out/'RESULTADO.json',result);print(json.dumps({'zero_Native_proven':True,'critical_unchanged':True,'marker_removed':True,'proof':str(out/'RESULTADO.json')}))
if __name__=='__main__':main()
