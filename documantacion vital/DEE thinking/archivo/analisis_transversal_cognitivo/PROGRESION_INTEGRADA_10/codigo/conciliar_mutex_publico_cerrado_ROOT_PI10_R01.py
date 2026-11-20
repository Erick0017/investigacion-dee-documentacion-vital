"""Reconcile only the exact closed, zero-admission public R04 attempt."""
from pathlib import Path
import hashlib, importlib.util, json, shutil
from datetime import datetime, timezone

H = Path(__file__).resolve().parent
P = H.parent
def read(p): return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok, why):
    if not ok: raise ValueError(why)
def load(name, p):
    sp=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m

u=load('PI10_exact_existing_public_guard',H/'pi10_publico_acotado_comun_R04.py')
failure=P/'control/PI10_PRODUCTO_EP13_OWNER_R01.json'
v=read(failure)
need(v['closed'] is True and v['status']=='STOPPED_PRESERVED' and v['new_Native_ticks']==0 and v['records']==[], 'Exact zero-Native failed R04 attempt only')
need(u.LOCK.name=='PI10_ROOT_NATIVE_WRITER.lock' and u.LOCK.resolve().parent==P.resolve() and not u.LOCK.is_symlink(), 'Exact campaign mutex only')
lock=read(u.LOCK)
need(lock['life_id']==u.LIFE and lock['phase']=='PUBLIC_SELECTED_PI10_EP13' and lock['finite_bound']==2016, 'Exact failed public mutex')
guard=u.guard()
old=P.with_name('PROGRESION_INTEGRADA_09')/'codigo/comprobar_procesos_adopcion_D_PI09_R01.py'
need(sha(old)=='9222b2fb422bb3c19d9ed4c5bf1785d2f987dd0d5533ddf9242600a563e22107', 'Pinned PID checker')
m=load('PI10_exact_prior_supervisor_PID_check',old)
process=m.pid_proof({'pid':lock['pid'],'running':False,'wall_utc':v['started_utc']})
need(process['no_live_affected_writer'], 'Actual supervisor process is not proven gone')
card, native=u.snapshot(u.parser())
need(card['physical']['tick']==945831 and native['physical']==v['initial_saved_Native']['physical'] and native['causal_prefix_sha256']==v['initial_saved_Native']['causal_prefix_sha256'], 'No physical advance permitted')
out=P/'control/RECONCILIACION_MUTEX_PUBLICO_R04_ROOT_R01.json'
backup=P/'control/MUTEX_PUBLICO_R04_CERRADO_LITERAL.json'
need(not out.exists() and not backup.exists(), 'Never repeat reconciliation')
shutil.copyfile(u.LOCK,backup)
need(sha(backup)==sha(u.LOCK), 'Literal mutex backup')
proof={'schema':'DEE.PI10.exact_closed_public_mutex_reconciliation.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'failed_proof_sha256':sha(failure),'supervisor_process':process,'actual_closed_owner_and_queue':guard,'mutex_before':lock,'literal_mutex_backup':str(backup),'literal_mutex_sha256':sha(backup),'Native_ticks':0,'requests_resent':0,'only_deleted_file':str(u.LOCK.resolve()),'original_principal_state_unchanged':True}
out.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
need(sha(backup)==sha(u.LOCK), 'Concurrent mutex change')
u.LOCK.unlink()
need(not u.LOCK.exists(), 'Mutex removal failed')
print(json.dumps({'proof':str(out),'sha256':sha(out),'Native':0,'only_exact_closed_mutex_removed':True}))
