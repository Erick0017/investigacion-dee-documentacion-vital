"""Root-only declared-directory restoration on a closed imported S7 clone.

Default is read-only. --aplicar may only mkdir directories declared by its
verified imported pair; existing files, snapshot/card/SQLite are never written.
This is external schema preservation, not Native repair or learned recovery.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,ctypes,hashlib,json,os,re,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema'
PREFIX='ECI02_PI03_REPRO_PI04_PI05_PI07_'
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def regular(p):
 for node in(p,*p.parents):
  if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source or target: '+str(node))
def closed_pid(pid):
 if os.name!='nt':raise ValueError('Windows scoped process proof is required')
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.argtypes=[ctypes.c_uint32,ctypes.c_int,ctypes.c_uint32];k.OpenProcess.restype=ctypes.c_void_p
 k.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint32)];k.GetExitCodeProcess.restype=ctypes.c_int
 k.CloseHandle.argtypes=[ctypes.c_void_p];k.CloseHandle.restype=ctypes.c_int
 h=k.OpenProcess(0x1000,False,pid)
 if not h:
  error=ctypes.get_last_error()
  if error!=87:raise OSError(error,'Cannot establish affected cached PID absence')
  return {'pid':pid,'observation':'PID_ABSENT','windows_error':error,'confirmed_not_alive':True}
 try:
  code=ctypes.c_uint32()
  if not k.GetExitCodeProcess(h,ctypes.byref(code)):raise ctypes.WinError(ctypes.get_last_error())
  if code.value==259:raise ValueError('Cached owner PID exists/alive or reused; preserve and obtain exact ownership proof')
  return {'pid':pid,'exit_code':code.value,'confirmed_not_alive':True}
 finally:k.CloseHandle(h)
def directory_map(names,service,worker):
 """Pure bounded mapping; no mkdir, state read or implicit source expansion."""
 result=[];seen=set()
 for name in names:
  if not isinstance(name,str)or '\\'in name or ':'in name:raise ValueError('Invalid declared directory member')
  rel=PurePosixPath(name)
  if rel.is_absolute()or not rel.parts or rel.as_posix()!=name or any(x in('..','.')for x in rel.parts)or name in seen:raise ValueError('Unsafe/duplicate declared directory')
  seen.add(name)
  if rel.parts[0]=='resultados':base=service;target=service/Path(*rel.parts)
  elif rel.parts[0]=='artefactos_trabajador':base=worker;target=worker/Path(*rel.parts[1:])
  else:raise ValueError('Only resultados and artefactos_trabajador mappings are allowed')
  if not target.resolve(strict=False).is_relative_to(base.resolve(strict=False)):raise ValueError('Directory mapping escaped exact clone')
  result.append({'member':name,'target':target,'base':base})
 return sorted(result,key=lambda row:(len(row['target'].parts),str(row['target'])))
def materialize(life,pair,*,apply=False,output=None):
 if not re.fullmatch(re.escape(PREFIX)+r'[A-Za-z0-9_]{1,24}',life):raise ValueError('Explicit isolated PI07 diagnostic only')
 regular(S);pair=Path(pair).resolve(strict=True);regular(pair)
 if not(pair.is_relative_to((P/'pares').resolve())or pair.is_relative_to((C/'reproducibilidad/materiales').resolve())):raise ValueError('Only preserved complete pair stores')
 if (S/'estado/ACTIVO.json').exists():raise ValueError('Never selected/global principal')
 locks=S/'estado/locks'
 if locks.exists()and any(locks.iterdir()):raise ValueError('Any S7 writer lock blocks this external schema operation')
 if (P/'PI07_ROOT_NATIVE_WRITER.lock').exists():raise ValueError('Campaign Native owner is active or uncertain; wait for proven closure')
 service=S/'estado/servicios_persistentes'/life;worker=S/'estado/servicios_locales'/life;cardfile=S/'estado/vidas'/life/'VIDA.json'
 for f in(service,worker,cardfile):regular(f)
 if (service/'IMPORTACION_EN_CURSO.json').exists()or(cardfile.parent/'FUTURO_INTERRUMPIDO.json').exists():raise ValueError('Unresolved import/future is protected')
 imported=read(service/'IMPORTACION.json');manifestfile=pair/'EXPORTACION_SERVICIO.json';manifest=read(manifestfile)
 if (imported.get('new_life_id')!=life or imported.get('source_life_id')!=manifest.get('life_id')or
     imported.get('source_snapshot_sha256')!=manifest.get('snapshot_sha256')or
     imported.get('verification',{}).get('manifest_sha256')!=sha(manifestfile)):
  raise ValueError('Pair manifest is not the exact complete import source of this clone')
 card=read(cardfile);snap=S/card['snapshot'];db=service/'cola.sqlite3'
 for f in(snap,db,manifestfile):regular(f)
 if sha(snap)!=card['snapshot_sha256']:raise ValueError('Current clone snapshot pointer mismatch')
 if any(Path(str(db)+x).exists()for x in('-wal','-shm','-journal')):raise ValueError('Closed standalone SQLite is required')
 q=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  if q.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('SQLite integrity failure')
  row=q.execute("select value from meta where key='owner'").fetchone();owner=None if row is None else json.loads(row[0])
  unresolved=q.execute("select id,status from requests where status in('queued','processing','uncertain','failed_preserved')").fetchall()
 finally:q.close()
 if owner is None or owner.get('running')is not False or owner.get('uncertain_external_result')or unresolved:raise ValueError('Closed coherent owner/transport proof required')
 if type(owner.get('pid'))is int:process=closed_pid(owner['pid'])
 elif owner.get('imported_not_yet_started')is True:
  process={'observation':'EXPLICIT_IMPORTED_NEVER_STARTED','cached_running':False,'actual_PID_not_claimed':True,'import_mapping_sha256':sha(service/'IMPORTACION.json')}
 else:raise ValueError('Closed cache has neither a scoped PID nor an explicit never-started import')
 rows=directory_map(manifest.get('empty_directories_preserved',[]),service,worker)
 if not rows:raise ValueError('No explicit directory manifest; do not infer one')
 for row in rows:
  regular(row['target'])
  if row['target'].exists()and not row['target'].is_dir():raise ValueError('A file already occupies a declared directory')
 critical=[cardfile,snap,db,service/'IMPORTACION.json',manifestfile]
 history=cardfile.parent/'HISTORIA.jsonl'
 if history.exists():critical.append(history)
 before={str(f):sha(f)for f in critical};missing=[row for row in rows if not row['target'].exists()]
 proof={'schema':'DEE.PI07.declared_empty_directory_preservation.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),
  'life_id':life,'source_pair':str(pair),'manifest_sha256':sha(manifestfile),'Native_executed':False,'new_ticks':0,
  'mode':'APPLY_DIRECTORIES_ONLY'if apply else'READ_ONLY_DRY_RUN','process_proof':process,
  'declared_directories':len(rows),'already_present':len(rows)-len(missing),'planned_missing':len(missing),
  'mapping':[{'member':row['member'],'target':str(row['target'])}for row in rows],
  'critical_before_sha256':before,'created':[],'existing_files_opened_for_writing':0,
  'scope':'Only declared external directory schema. No file content, Native fields, clocks, metadata, journal rows, resources, outputs or counters changed.'}
 if not apply:return proof
 if output is None:raise ValueError('Explicit fresh control proof path is required when applying')
 output=Path(output).resolve(strict=False);regular(output)
 if not output.is_relative_to((P/'control').resolve())or output.exists():raise ValueError('Fresh PI07/control proof only')
 try:
  for row in missing:
   target=row['target'];regular(target)
   # Parent directories belong to the same explicit bounded schema; never
   # follow a junction and never replace an existing directory/file.
   chain=[];current=target
   while not current.exists():chain.append(current);current=current.parent
   for node in reversed(chain):regular(node);node.mkdir();proof['created'].append(str(node))
  after={str(f):sha(f)for f in critical};proof['critical_after_sha256']=after
  if before!=after:raise ValueError('Native card/snapshot/SQLite/import/provenance changed concurrently')
  proof.update(status='VERIFIED',all_declared_directories_present=all(row['target'].is_dir()for row in rows),critical_files_unchanged=True)
 except Exception as e:
  proof.update(status='PARTIAL_PRESERVED_INSPECT_BEFORE_RETRY',error={'type':type(e).__name__,'message':str(e)})
  with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
  raise
 with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 return proof
def main(a):
 proof=materialize(a.vida,a.par,apply=a.aplicar,output=a.salida)
 summary={k:v for k,v in proof.items()if k not in('mapping','created','critical_before_sha256','critical_after_sha256')}
 if a.salida is not None and a.aplicar:summary.update(proof=str(a.salida),proof_sha256=sha(a.salida))
 print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--vida',required=True);ap.add_argument('--par',type=Path,required=True);ap.add_argument('--aplicar',action='store_true');ap.add_argument('--salida',type=Path);main(ap.parse_args())
