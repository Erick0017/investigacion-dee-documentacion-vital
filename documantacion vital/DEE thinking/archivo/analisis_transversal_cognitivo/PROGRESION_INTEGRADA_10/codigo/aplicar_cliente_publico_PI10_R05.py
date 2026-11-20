from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,json,sqlite3
H=Path(__file__).resolve().parent;P=H.parent;D=H/'CLIENTE_PUBLICO_PI10_R05_PREPARADO'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(ok,msg):
 if not ok:raise ValueError(msg)
def main():
 ap=argparse.ArgumentParser(description='Root-only one-line client import fix, no Native/queue writes. Default PLAN.');ap.add_argument('--aplicar',action='store_true');a=ap.parse_args()
 d=json.loads((D/'DELTA.json').read_text('utf-8'));target=Path(d['target']);staged=Path(d['staged_file'])
 need(sha(target)==d['before_sha256'] and sha(staged)==d['after_sha256'],'Exact before/after CAS required')
 ast.parse(staged.read_text('utf-8-sig'))
 print(json.dumps({'mode':'APPLY'if a.aplicar else'PLAN','delta':d,'Native_calls':0},ensure_ascii=False))
 if not a.aplicar:return 0
 life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01';S=target.parents[1];db=S/'estado/servicios_persistentes'/life/'cola.sqlite3'
 need(not Path(str(db)+'-wal').exists()or Path(str(db)+'-wal').stat().st_size==0,'Nonempty WAL; preserve and stop')
 con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity required')
  owner=json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0]);need(owner.get('running')is False and owner.get('uncertain_external_result')is False,'Closed reconciled owner required')
  ids=['PI10_PUBLIC_EP13_R04_EP13','PI10_PUBLIC_EP13_R04_EP13_reanudar','PI10_PUBLIC_EP13_R04_EP13_pausar']
  need(all(con.execute('SELECT id FROM requests WHERE id=?',(x,)).fetchone()is None for x in ids),'R04 IDs must be absent; never retry or purge')
  need(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'No unresolved transport')
 finally:con.close()
 out=P/'control/REPARACION_CLIENTE_PUBLICO_PI10_R05';need(not out.exists(),'No overwrite repair transaction');out.mkdir()
 backup=out/'cliente_mente_unificada.original.py';backup.write_bytes(target.read_bytes());need(sha(backup)==d['before_sha256'],'Backup mismatch')
 need(sha(target)==d['before_sha256'],'Final CAS mismatch');target.write_bytes(staged.read_bytes());need(sha(target)==d['after_sha256'],'After hash mismatch')
 proof={**d,'schema':'DEE.PI10.applied_one_line_client_repair.R05','applied_utc':datetime.now(timezone.utc).isoformat(),'backup':str(backup),'backup_sha256':sha(backup),'queues_read_only':True,'no_Native_execution':True,'R04_ID_absent':True,'R04_not_resent':True,'new_material_ID_not_submitted':True}
 f=out/'APLICACION.json';f.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
 print(json.dumps({'proof':str(f),'sha256':sha(f),'new_client_sha256':sha(target)}));return 0
if __name__=='__main__':raise SystemExit(main())

