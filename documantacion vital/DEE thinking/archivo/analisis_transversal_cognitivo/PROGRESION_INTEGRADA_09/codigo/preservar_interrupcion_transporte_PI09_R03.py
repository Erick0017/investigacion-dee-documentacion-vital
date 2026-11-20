"""Preserve exact dead-owner SQLite/WAL/SHM and inspect only a copied database."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,importlib.util,json,shutil,sqlite3
P=Path(__file__).resolve().parents[1];S=P.parents[2]/'DEE Cognitive 2.0/sistema';L='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_NATIVE_01';O=P/'control/INTERRUPCION_TRANSPORTE_PRODUCTO_R03';J=P/'control/PRESERVACION_INTERRUPCION_TRANSPORTE_PI09_R03.json'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 assert not O.exists()and not J.exists()and not(P/'PI09_ROOT_NATIVE_WRITER.lock').exists()
 probe=P/'codigo/comprobar_procesos_afectados_PI09_R01.py';sp=importlib.util.spec_from_file_location('PI09_exact_dead_pid_probe',probe);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m)
 lock=S/'estado/locks'/(L+'.lock');lease=read(lock);assert lease['pid']==9308
 pid=m.pid_proof({'pid':9308,'running':True,'wall_utc':'2026-11-11T10:17:18.819684+00:00'});assert pid['no_live_affected_writer']is True
 card=S/'estado/vidas'/L/'VIDA.json';c=read(card);db=S/'estado/servicios_persistentes'/L/'cola.sqlite3'
 files=[db,*[Path(str(db)+suffix)for suffix in ('-wal','-shm')if Path(str(db)+suffix).exists()],lock,card,S/c['snapshot']]
 for p in files:m.regular(p)
 before={str(p):sha(p)for p in files};O.mkdir();raw=O/'raw';raw.mkdir();audit=O/'audit';audit.mkdir();rows=[]
 for p in files:
  target=raw/p.name;assert not target.exists();shutil.copyfile(p,target);assert sha(target)==before[str(p)];rows.append({'source':str(p),'copy':str(target),'bytes':p.stat().st_size,'sha256':sha(target)})
 after={str(p):sha(p)for p in files};assert before==after
 for name in ('cola.sqlite3','cola.sqlite3-wal','cola.sqlite3-shm'):
  if(raw/name).exists():shutil.copyfile(raw/name,audit/name)
 con=sqlite3.connect(audit/'cola.sqlite3');con.row_factory=sqlite3.Row
 try:
  integrity=con.execute('PRAGMA integrity_check').fetchone()[0]
  pending=[dict(r)for r in con.execute("SELECT id,status,payload,is_control FROM requests WHERE status IN('queued','processing','uncertain')")]
  exact=[dict(r)for r in con.execute("SELECT seq,id,status,payload,error FROM requests WHERE id IN (?,?,?)",('PI09_PRODUCT0_UNSELECTED_R03_PI09','PI09_PRODUCT0_UNSELECTED_R03_PI09_reanudar','PI09_PRODUCT0_UNSELECTED_R03_d85495c9_detener_745066e4'))]
  r=con.execute("SELECT value FROM meta WHERE key='owner'").fetchone();owner=json.loads(r[0])if r else None
 finally:con.close()
 assert integrity=='ok'and pending and all(p['id']=='PI09_PRODUCT0_UNSELECTED_R03_PI09'and p['status']=='queued'and json.loads(p['payload'])['situaciones']==[{'modo':'eci01-pi09-estado'}]for p in pending)
 value={'schema':'DEE.PI09.dead_owner.interrupted_transport_preservation.R03','recorded_utc':datetime.now(timezone.utc).isoformat(),'life_id':L,'Win32_process':pid,'source_raw_trio_and_markers_unchanged_during_copy':before==after,'files':rows,'logical_SQLite_integrity_of_COPY':integrity,'cached_owner_from_COPY':owner,'pending_in_COPY':pending,'exact_attempts_in_COPY':exact,'saved_physical':c['physical'],'source_snapshot_sha256':c['snapshot_sha256'],'Native_imported_or_executed':False,'original_SQLite_opened':False,'processes_stopped':False,'source_states_queues_locks_modified':False,'scope':'Coherent raw dead-writer copy, source hashes stable before/after. WAL is applied ONLY in audit copy. Not a complete backup of the participant. Original queued STATE must be completed or reconciled by its existing ID; never re-admitted, purged, or called an uncertain physical experience.'}
 assert before=={str(p):sha(p)for p in files}
 J.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps({'proof':str(J),'sha256':sha(J),'PID_absent':pid['no_live_affected_writer'],'pending_ids':[v['id']for v in pending],'source_unchanged':True,'Native_executed':False}))
if __name__=='__main__':main()
