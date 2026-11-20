"""Root-only exact closed full-state copy, standard paired-export contract.

Default is PLAN. --exportar is stdlib only: no owner, DEE import, tick, input,
SQLite write, metadata repair or source write. Partial destination is kept.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse,hashlib,importlib.util,json,os,shutil,sqlite3

P=Path(__file__).resolve().parents[1];P9=P.with_name('PROGRESION_INTEGRADA_09');C=P.parents[2]/'DEE Cognitive 2.0';S=C/'sistema';RP=C/'reproducibilidad'
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI09_DISCOVERY_01'
PROC=P9/'codigo/comprobar_procesos_adopcion_D_PI09_R01.py';PROC_SHA='9222b2fb422bb3c19d9ed4c5bf1785d2f987dd0d5533ddf9242600a563e22107'
PARSER=RP/'observador_pasivo.py';PARSER_SHA='dbb2a5e15d70c64112d36505197f4aebf6ff7d4092972923e17cd60c10a1c873'
SERVICE='DEE.Cognitive.System.1.1.PERSISTENT_SERVICE.v1'

def need(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def ref(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def load(name,p,pin=None):
 if pin:need(sha(p)==pin,'Reviewed passive helper changed')
 spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def regular(p):
 for n in(p,*p.parents):need(not n.exists()or not(n.is_symlink()or getattr(n.lstat(),'st_file_attributes',0)&1024),'No linked full-state path')
def tree(root):
 regular(root);files=[];dirs=[]
 for base,names,leafs in os.walk(root,followlinks=False):
  base=Path(base);regular(base)
  for name in names:regular(base/name);dirs.append((base/name).relative_to(root))
  for name in leafs:
   f=base/name;regular(f);need(f.is_file(),'Only regular files in paired state');files.append((f,f.relative_to(root)))
 return sorted(files),sorted(dirs)
def write(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(v,f,ensure_ascii=False,indent=2);f.write('\n')

def export(a):
 need(not(P/'PI10_ROOT_NATIVE_WRITER.lock').exists()and not(RP/'EJECUCION_MATERIAL.lock').exists(),'Root writer/importer still declared')
 need(a.tick is not None and a.tick>=922371 and isinstance(a.snapshot_sha256,str)and len(a.snapshot_sha256)==64,'Exact actual current cut required')
 dest=(P/'pares'/('PRINCIPAL_D_T'+str(a.tick))).resolve();proof=dest.with_name(dest.name+'_PRESERVACION.json')
 need(not dest.exists()and not proof.exists(),'Fresh full-state copy only; no uncertain retry')
 activefile=S/'estado/ACTIVO.json';active=read(activefile);need(active['life_id']==LIFE,'Changed main: reconcile genealogy, never take highest tick')
 closed=load('PI10_export_closed_scope',PROC,PROC_SHA).inspect('current_selected_PI10_parent',S,LIFE)
 need(closed['no_live_affected_writer']is True,'Current process/queue/lock not proven closed')
 life=S/'estado/vidas'/LIFE;service=S/'estado/servicios_persistentes'/LIFE;worker=S/'estado/servicios_locales'/LIFE
 for folder in(life,service,worker):regular(folder);need(folder.is_dir(),'Missing complete state directory')
 cardfile=life/'VIDA.json';history=life/'HISTORIA.jsonl';card=read(cardfile);snapshot=(S/card['snapshot']).resolve(strict=True)
 need(snapshot.is_relative_to(S.resolve())and card['life_id']==card['world_id']==LIFE and card['physical']['tick']==a.tick and active['tick']==a.tick and card['snapshot_sha256']==active['snapshot_sha256']==sha(snapshot)==a.snapshot_sha256,'Current stable cut changed before preservation')
 need(json.loads(history.read_text('utf8').splitlines()[-1])['snapshot_sha256']==a.snapshot_sha256,'Current history/card mismatch')
 parser=load('PI10_export_passive_parser',PARSER,PARSER_SHA);view=parser.snapshot_view(snapshot)
 need(all(view['physical'][k]==card['physical'][k]for k in('N','tick','RAW_sha256','clocks_sha256')),'Native state/card mismatch')
 native=json.loads(view['metadata'][SERVICE]);need(native['native_tick_at_checkpoint']==a.tick and native['paused']and not native['uncertain_external_result'],'Native transport checkpoint must be paused/coherent')
 db=service/'cola.sqlite3';need(not any(Path(str(db)+s).exists()and Path(str(db)+s).stat().st_size for s in('-wal','-journal')),'Nonempty WAL/journal is not a closed copy')
 con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True);con.row_factory=sqlite3.Row
 try:
  need(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite not integral')
  statuses=dict(con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status'))
  need(not any(statuses.get(s,0)for s in('queued','processing','uncertain')),'Unresolved transport: preserve, do not purge')
  receipt=native['last_completed_receipt'];row=con.execute('SELECT * FROM requests WHERE id=?',(receipt['id'],)).fetchone();outbox=service/'resultados'/(receipt['id']+'.json')
  need(row is not None and row['status']=='completed'and row['payload_sha']==receipt['payload_sha256']and sha(outbox)==receipt['result_sha256'],'Last receipt/outbox not reconciled')
  terminal_noncompleted=[{'id':r['id'],'status':r['status'],'payload_sha':r['payload_sha']}for r in con.execute("SELECT id,status,payload_sha FROM requests WHERE status IN('failed_preserved','rejected_invalid')")]
 finally:con.close()
 sources=[(snapshot,Path('VIDA.deetsnap.gz')),(db,Path('cola.sqlite3')),(cardfile,Path('procedencia/VIDA_ORIGINAL.json')),(history,Path('procedencia/HISTORIA_ORIGINAL.jsonl'))];directories=[]
 for root,prefix in((service/'resultados',Path('resultados')),(worker,Path('artefactos_trabajador'))):
  files,dirs=tree(root);sources.extend((f,prefix/r)for f,r in files);directories.append(prefix.as_posix());directories.extend((prefix/d).as_posix()for d in dirs)
 before={str(f):ref(f)for f,_ in sources};protected={str(p):sha(p)for p in(activefile,cardfile,snapshot)}
 dest.mkdir(parents=True)
 for name in directories:(dest/name).mkdir(parents=True,exist_ok=True)
 rows=[]
 for source,name in sources:
  target=dest/name;target.parent.mkdir(parents=True,exist_ok=True)
  with source.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
  need(sha(target)==before[str(source)]['sha256']and target.stat().st_size==before[str(source)]['bytes'],'Copy mismatch; retain partial destination')
  rows.append({'file':name.as_posix(),'bytes':target.stat().st_size,'sha256':sha(target)})
 need(before=={str(f):ref(f)for f,_ in sources}and protected=={p:sha(Path(p))for p in protected},'Source changed concurrently; copy retained but not certified')
 manifest={'schema':'DEE.persistent_service.paired_export.v1','life_id':LIFE,'profile':card['profile'],'backend':'mente_unificada','native_snapshot':'VIDA.deetsnap.gz','snapshot_sha256':a.snapshot_sha256,'physical':card['physical'],'members':rows,'queue_journal_required':True,'source_record':{'life_id':LIFE,'world_id':card['world_id'],'parent':card['parent']},'empty_directories_preserved':sorted(set(directories)),'pending_Native_agenda_preserved':view['pending_native'],'no_engine_or_WHL':True,'not_a_new_cognitive_acquisition':True,'preserved_terminal_noncompleted':terminal_noncompleted,'scope':'Exact current selected D full state, closed source; no owner, Native step or metadata edit.'}
 mf=dest/'EXPORTACION_SERVICIO.json';write(mf,manifest)
 verifier=load('PI10_literal_import_pair_verifier',S/'app/importacion_emparejada.py');_,_,verified=verifier.verify_export(dest)
 record={'schema':'DEE.PI10.current_main.complete_closed_preservation.R01','at_utc':datetime.now(timezone.utc).isoformat(),'life_id':LIFE,'tick':a.tick,'destination':str(dest),'manifest_sha256':sha(mf),'snapshot_sha256':a.snapshot_sha256,'members':len(rows),'bytes':sum(r['bytes']for r in rows),'directories':len(manifest['empty_directories_preserved']),'closed_source':closed,'queue_status_counts':statuses,'terminal_noncompleted_preserved':terminal_noncompleted,'standard_contract_verified':verified,'causal_prefix_sha256':view['causal_prefix_sha256'],'source_files_unchanged':True,'Native_executed':False,'new_Native_ticks':0,'source_ACTIVO_unchanged':sha(activefile)==protected[str(activefile)]}
 write(proof,record);print(json.dumps({'preserved':True,'manifest':str(mf),'manifest_sha256':sha(mf),'proof':str(proof),'Native':0}))

if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--exportar',action='store_true');ap.add_argument('--tick',type=int);ap.add_argument('--snapshot-sha256');a=ap.parse_args()
 if a.exportar:export(a)
 else:print(json.dumps({'mode':'PLAN_ONLY_NO_SOURCE_READ','current_expected_life':LIFE,'Root_command':'--exportar --tick ACTUAL --snapshot-sha256 ACTUAL','preserves_complete_paired_contract':True,'Native':0}))
