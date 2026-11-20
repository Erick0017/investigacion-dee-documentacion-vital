"""Reconcile only the actual pre-material B REAL startup failure. Zero Native.
No request is replayed, queue row removed, snapshot restored or process stopped.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/B_REAL_R01/sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_REAL_01';TAG='PI08_B_REAL_R01';RUN=TAG+'_fa14ac85'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,p):
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main(a):
 failfile=P/'control/PI08_B_REAL_R01.json';fail=read(failfile);marker=P/'PI08_ROOT_NATIVE_WRITER.lock'
 if fail['status']!='STOPPED_PRESERVED'or fail['new_Native_ticks']!=0 or fail['opportunities_completed']!=0 or fail['intents']:raise ValueError('Only this proven pre-material startup failure')
 if not marker.is_file()or marker.is_symlink()or getattr(marker.lstat(),'st_file_attributes',0)&1024:raise ValueError('Exact plain marker required')
 mark=read(marker)
 if mark['life_id']!=LIFE or mark['role']!='real':raise ValueError('Another writer marker exists')
 helper=load('PI08_scoped_RO_process_helper',P/'codigo/comprobar_procesos_afectados_PI08_R01.py')
 scope=helper.inspect('failed_B_startup',S,LIFE)
 imported=read(P/'control/IMPORTACION_B_REAL_PI08_R01.json')
 # A newly imported transport deliberately has no PID. In this one case use
 # the ACTUAL failed owned PID and Root PID below, not a fictional cached PID.
 fresh_no_pid=(scope['SQLite']['owner_cached']['pid']is None and scope['SQLite']['owner_cached']['running']is False
  and scope['SQLite']['integrity_check']=='ok'and not scope['SQLite']['unresolved']and not scope['SQLite']['WAL_bytes']
  and not scope['preserved_marker_paths']and imported['closed']and imported['new_Native_ticks']==0
  and imported['no_owner_started']and imported['status']=='IMPORTED_CLOSED_NO_NATIVE_TICKS')
 if not scope['no_live_affected_writer']and not fresh_no_pid:raise ValueError('World owner/queue/locks remain unresolved')
 samples=[json.loads(line)for line in(P/'ENSAYOS.jsonl').read_text(encoding='utf8').splitlines()if RUN in line]
 pids={mark['pid']}|{r['pid']for r in samples if r.get('kind')=='OWNED_PROCESS_RESOURCES'}
 if len(pids)<2:raise ValueError('Failed Root and exact owned process identities required')
 processes=[helper.pid_proof({'pid':pid})for pid in sorted(pids)]
 if not all(r['no_live_affected_writer']for r in processes):raise ValueError('A failed owned process is still present/uncertain')
 card=read(S/'estado/vidas'/LIFE/'VIDA.json');seal=read(P/'codigo/SELLO_PI08_B_R01.json')
 parser=load('PI08_frozen_snapshot_reader',C/'reproducibilidad/observador_pasivo.py');v=parser.snapshot_view(S/card['snapshot'])
 if any(v['physical'][k]!=val for k,val in seal['source_prefix']['physical'].items())or 'DEE.Cognitive.PI08.successive_contextual_regulation.B.R01'in v['metadata']:raise ValueError('Material B future exists or source changed; no retry')
 db=S/'estado/servicios_persistentes'/LIFE/'cola.sqlite3';con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:attempts=con.execute('SELECT id,status FROM requests WHERE id LIKE ?', (TAG+'_%',)).fetchall()
 finally:con.close()
 if attempts:raise ValueError('There were actual transport requests; inspect rather than repeat')
 if fail['protected_before']!=fail['protected_after']or any(sha(Path(p))!=d for p,d in fail['protected_after'].items()):raise ValueError('Protected A changed')
 out=P/'control/CONCILIACION_ARRANQUE_B_REAL_PI08_R01.json'
 if out.exists():raise FileExistsError('Prior reconciliation preserved')
 proof={'schema':'DEE.PI08.B.pre_material_startup_reconciled.v1','at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'failed_proof':{'path':str(failfile),'sha256':sha(failfile)},'life_id':LIFE,'N':67,'T':card['physical']['tick'],'no_B_KEY_or_requests':True,'actual_process_checks':processes,'fresh_import_has_no_cached_PID_as_expected':fresh_no_pid,'actual_failed_process_checks_replace_absent_cache':True,'closed_world':scope,'marker_original':mark,'marker_sha256':sha(marker),'Native_inputs_or_ticks':0,'processes_stopped':False,'queues_or_snapshots_edited':False,'scope':'Root runner and exact owned Python exited before readiness. No material request existed; its non-inheritable KILL_ON_JOB_CLOSE supervision handles do not survive Root exit. This reconciles the administrative marker only, not the incomplete directory transport. A new technical tag may be used after that transport correction.'}
 with out.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2)
 if a.conciliar:
  if marker.resolve().parent!=P.resolve()or read(marker)!=mark:raise ValueError('Marker identity changed')
  marker.unlink()
 print(json.dumps({'proof':str(out),'sha256':sha(out),'marker_reconciled':a.conciliar,'no_material_retry':True}))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--conciliar',action='store_true');main(ap.parse_args())
