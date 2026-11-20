from pathlib import Path
import json,sqlite3,hashlib
W=Path(__file__).resolve().parents[5]
C=W/'DEE Cognitive 2.0'
# Resolve by documented campaign ancestor, no DEE import.
C=Path(__file__).resolve().parents[4]/'DEE Cognitive 2.0'
S=C/'sistema'
life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_REAL2_01'
db=S/'estado/servicios_persistentes'/life/'cola.sqlite3'
need=lambda ok,msg: None if ok else (_ for _ in ()).throw(ValueError(msg))
need(db.is_file(),str(db))
proof=Path(__file__).resolve().parent.parent/'control/PI10_PRODUCTO_EP13_OWNER_R01.json'
p=json.loads(proof.read_text('utf-8-sig'))
print(json.dumps({'proof':str(proof),'proof_status':p.get('status'),'closed':p.get('closed'),'keys':list(p),'db':str(db),'wal_bytes':Path(str(db)+'-wal').stat().st_size if Path(str(db)+'-wal').exists()else 0,'shm_bytes':Path(str(db)+'-shm').stat().st_size if Path(str(db)+'-shm').exists()else 0},ensure_ascii=False))
need(not Path(str(db)+'-wal').exists()or Path(str(db)+'-wal').stat().st_size==0,'Nonempty WAL: no incoherent immutable inspection')
con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
con.row_factory=sqlite3.Row
try:
 print('integrity',con.execute('PRAGMA integrity_check').fetchone()[0])
 print('owner',con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
 print('columns', [tuple(r) for r in con.execute('PRAGMA table_info(requests)')])
 for rid in ('PI10_PUBLIC_EP13_R04_EP13','PI10_PUBLIC_EP13_R04_EP13_reanudar','PI10_PUBLIC_EP13_R04_EP13_pausar'):
  r=con.execute('SELECT * FROM requests WHERE id=?',(rid,)).fetchone()
  print('REQUEST',rid,json.dumps(dict(r)if r else None,ensure_ascii=False))
 print('unresolved',json.dumps([dict(r)for r in con.execute("SELECT * FROM requests WHERE status IN('queued','processing','uncertain')")],ensure_ascii=False))
except Exception as e:print(type(e).__name__,str(e));raise
finally:con.close()

