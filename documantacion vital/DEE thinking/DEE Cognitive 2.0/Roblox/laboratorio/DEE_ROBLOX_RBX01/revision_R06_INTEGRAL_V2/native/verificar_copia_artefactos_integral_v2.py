"""Read-only source/copy SHA verification after preparation has finished.

No DEE, owner, SQLite connection, snapshot load or physics execution. The
optional NEW report is the sole write. Never repeats preparation/import.
"""
from pathlib import Path
import argparse,datetime,hashlib,json,os,stat
HERE=Path(__file__).resolve().parent
SOURCE_LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_DEV'

def regular(p):
 p=Path(p).absolute()
 for x in(p,*p.parents):
  m=x.lstat()
  if stat.S_ISLNK(m.st_mode)or getattr(m,'st_file_attributes',0)&1024:raise ValueError('No links/reparse points')
 return p

def sha(p):
 before=p.stat();h=hashlib.sha256()
 with p.open('rb')as f:
  for block in iter(lambda:f.read(1048576),b''):h.update(block)
 after=p.stat()
 if(before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError('Source changed during a read')
 return h.hexdigest()

def walk(root):
 root=regular(root);files={};empty=[]
 for folder,dirs,names in os.walk(root,followlinks=False):
  folder=regular(folder);dirs.sort();names.sort()
  for d in dirs:regular(folder/d)
  if not dirs and not names:empty.append(folder.relative_to(root).as_posix())
  for name in names:
   p=regular(folder/name)
   if not p.is_file():raise ValueError('Regular files only')
   files[p.relative_to(root).as_posix()]=p
 return files,empty

def verify(destination,imported=False):
 dest=regular(Path(destination).resolve(strict=True))
 if dest.parent!=HERE:raise ValueError('Only this revision native/direct destination')
 context=json.loads((dest/'CONTEXTO_EJECUCION.json').read_text('utf8'))
 if context['source_life_id']!=SOURCE_LIFE or context['source_tick']!=953651:raise ValueError('Exact DEV4 parent required')
 source=HERE.parents[1]/'revision_R05_C02/native/DEV/sistema';prefix=regular(dest/'PREFIJO_DEV4_COMPLETO')
 issues=[];rows=[];before={};total=0
 groups=[(source/'estado/servicios_locales'/SOURCE_LIFE,prefix/'artefactos_trabajador','worker'),
         (source/'estado/servicios_persistentes'/SOURCE_LIFE/'resultados',prefix/'resultados','results')]
 for origin,copied,group in groups:
  originals,empty=walk(origin);targets,_=walk(copied)
  if set(originals)!=set(targets):issues.append({'group':group,'issue':'Member-set difference','source_only':sorted(set(originals)-set(targets)),'copy_only':sorted(set(targets)-set(originals))})
  for rel,p in originals.items():
   digest=sha(p);before[str(p)]=digest;size=p.stat().st_size;total+=size;t=targets.get(rel)
   equal=t is not None and t.stat().st_size==size and sha(t)==digest
   rows.append({'group':group,'file':rel,'bytes':size,'source_sha256':digest,'copy_sha256':sha(t)if t else None,'equal':equal})
   if not equal:issues.append({'group':group,'file':rel,'issue':'Missing/changed copy'})
   if imported:
    target=dest/'sistema/estado'/('servicios_locales'if group=='worker'else'servicios_persistentes')/context['life']
    if group=='results':target=target/'resultados'
    target=target/rel
    if not target.is_file()or sha(regular(target))!=digest:issues.append({'group':group,'file':rel,'issue':'Imported inherited member differs'})
  for rel in empty:
   target=copied if rel=='.'else copied/rel
   if not target.is_dir():issues.append({'group':group,'file':rel,'issue':'Missing exact empty source directory'})
 card_path=source/'estado/vidas'/SOURCE_LIFE/'VIDA.json';card=json.loads(card_path.read_text('utf8'))
 originals=[(source/card['snapshot'],prefix/'VIDA.deetsnap.gz','snapshot'),
 (source/'estado/servicios_persistentes'/SOURCE_LIFE/'cola.sqlite3',prefix/'cola.sqlite3','queue')]
 for p,t,kind in originals:
  h=sha(regular(p));before[str(p)]=h;equal=sha(regular(t))==h
  rows.append({'group':kind,'file':p.name,'bytes':p.stat().st_size,'source_sha256':h,'copy_sha256':sha(t),'equal':equal})
  if not equal:issues.append({'group':kind,'issue':'Parent copy changed'})
 changed=[p for p,h in before.items()if sha(Path(p))!=h]
 if changed:issues.append({'issue':'Original changed between verifier start/end','files':changed})
 return {'schema':'DEE.RBX01.INTEGRAL.V2.parent_artifact_copy_verification.R01',
  'inspected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'destination':str(dest),
  'parent_life_id':SOURCE_LIFE,'parent_tick':953651,'files_verified':len(rows),'worker_result_bytes':total,
  'imported_inherited_members_checked':imported,'source_hashes_before_after_equal':not changed,
  'all_copies_equal':not issues,'issues':issues,'members':rows,
  'Native_imported':False,'Native_ticks':0,'SQLite_opened':False,'originals_written':False,
  'scope':'Independent passive evidence added after the preparation source-version race; no clone/import is repeated.'}

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--destination',type=Path,required=True);p.add_argument('--imported',action='store_true');p.add_argument('--output',type=Path)
 a=p.parse_args();r=verify(a.destination,a.imported)
 if a.output:
  if a.output.exists()or not a.output.parent.is_dir():raise FileExistsError('New absent report in existing parent required')
  with a.output.open('x',encoding='utf8')as f:json.dump(r,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({k:v for k,v in r.items()if k!='members'},ensure_ascii=False,indent=2))
