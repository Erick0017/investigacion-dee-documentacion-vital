"""Root-only additive frozen PI06 code/pairs; no Native or source modification.

Default prints a plan. --aplicar copies verified bytes into existing RP stores.
No selector, recipe, engine, state field, counter or original is overwritten.
"""
from pathlib import Path,PurePosixPath
from datetime import datetime,timezone
import argparse,hashlib,json,os,shutil,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';S=P/'estados/candidato/sistema';RP=C/'reproducibilidad';CAP='PI06_ORGANIZACION_DIAGNOSTICO_R01'
PAIRS={'base':('BASE_MAIN_T824911','PI06_PRE_BASE_T824911',824911,'adb71add120a24629ac836da00009011e670b2f890edd93ef80bb4483acc3524'),
 'postbase':('POST_BASE_T825849','PI06_POST_BASE_T825849',825849,'1dc5636081eb828ffe5219dbab3a08ec2c163f62708935b293c0eeb281cf5cd2')}
PINNED={'app/mundo_genesis_apd05.py':'10a4f3168c23f386e8babe0d5ff2eb304963747c4cebfa18223ddbd05db2ec8c',
 'app/cola_local.py':'b3e7080ba521964bbb879adab6839ffcf3c0acdc905f4ece5410f11b0f245420',
 'capacidades/pi06_organizacion_R01.py':'c2cec3a42ea9c033869a2c689564ea51faac079f929b51cc271463b396477285',
 'capacidades/PROTOCOLO_PI06_ORGANIZACION_R01.json':'2a1743f16c9969c770f1fbc8bdad26ee411ac1b395664eb6a2c679a46e7c2570'}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source/target')
def rel(name):
 r=PurePosixPath(name)
 if not isinstance(name,str)or '\\'in name or ':'in name or r.is_absolute()or r.as_posix()!=name or any(x in('..','.')for x in r.parts):raise ValueError('Unsafe member path')
 return Path(*r.parts)
def verify(root,rows):
 seen=set()
 for v in rows:
  f=root/rel(v['file']);regular(f)
  if v['file']in seen or not f.resolve().is_relative_to(root.resolve())or not f.is_file()or f.stat().st_size!=v['bytes']or sha(f)!=v['sha256']:raise ValueError('Material differs: '+v['file'])
  seen.add(v['file'])
 return {'files':len(rows),'bytes':sum(v['bytes']for v in rows)}
def code_rows():
 rows=[];omit={'estado','runtime','__pycache__','.git','.venv','site-packages','node_modules','documentacion'}
 for base,dirs,names in os.walk(S,followlinks=False):
  base=Path(base);regular(base);dirs[:]=[n for n in dirs if n not in omit]
  for n in dirs:regular(base/n)
  for n in sorted(names):
   f=base/n;regular(f)
   if f.suffix not in('.pyc','.pyo'):rows.append({'file':f.relative_to(S).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
 rows.sort(key=lambda v:v['file']);d={v['file']:v['sha256']for v in rows}
 if any(d.get(n)!=h for n,h in PINNED.items()):raise ValueError('Qualified R01 changed; preserve a new revision')
 return rows
def capsule(apply):
 rows=code_rows();dest=RP/'codigo_preservado'/CAP;regular(dest);mf=dest/'SISTEMA_CODIGO.json'
 if dest.exists():
  if not mf.is_file()or read(mf)['files']!=rows:raise ValueError('Existing/partial capsule is protected')
  verify(dest,rows);action='REUSED_VERIFIED'
 elif apply:
  dest.mkdir(parents=True,exist_ok=False)
  for v in rows:
   f=dest/v['file'];f.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(S/v['file'],f)
  verify(dest,rows)
  m={'schema':'DEE.Cognitive.frozen_source_capsule.v1','id':CAP,'source_root':str(S),'files':rows,'created_utc':datetime.now(timezone.utc).isoformat(),
   'engine_shared_once':True,'Native_executed_by_preservation':False,'scope':'Exact diagnostic PI06 plus inherited current Cognitive code. No state/WHL/PYD; no new capability certification.'}
  with mf.open('x',encoding='utf8')as f:json.dump(m,f,ensure_ascii=False,indent=2);f.write('\n')
  action='COPIED_VERIFIED'
 else:action='PLAN_ONLY'
 if code_rows()!=rows:raise ValueError('Source code changed concurrently')
 return {'key':CAP,'action':action,'destination':str(dest),'product_relative':dest.relative_to(C).as_posix(),'manifest':'SISTEMA_CODIGO.json',
  'manifest_sha256':sha(mf)if mf.exists()else None,'files':len(rows),'bytes':sum(v['bytes']for v in rows)}
def pair(key,apply):
 source_name,alias,tick,h=PAIRS[key];source=P/'pares'/source_name;regular(source);index=source/'EXPORTACION_SERVICIO.json'
 if sha(index)!=h:raise ValueError('Exact frozen pair manifest changed')
 m=read(index)
 if m.get('schema')!='DEE.persistent_service.paired_export.v1'or m.get('queue_journal_required')is not True or m['physical']['N']!=67 or m['physical']['tick']!=tick:raise ValueError('Complete exact N67 pair required')
 checked=verify(source,m['members']);db=source/'cola.sqlite3'
 if any(Path(str(db)+x).exists()for x in('-wal','-shm','-journal')):raise ValueError('Standalone frozen SQLite required')
 q=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  if q.execute('pragma integrity_check').fetchone()[0]!='ok':raise ValueError('Queue integrity failure')
 finally:q.close()
 dest=RP/'materiales'/alias;regular(dest)
 if dest.exists():
  if not(dest/'EXPORTACION_SERVICIO.json').is_file()or sha(dest/'EXPORTACION_SERVICIO.json')!=h:raise ValueError('Existing/partial stable pair is protected')
  verify(dest,m['members']);action='REUSED_VERIFIED'
 elif apply:
  dest.mkdir(parents=True,exist_ok=False)
  for name in m.get('empty_directories_preserved',[]):
   target=dest/rel(name);regular(target);target.mkdir(parents=True,exist_ok=True)
  for v in m['members']:
   target=dest/rel(v['file']);target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source/v['file'],target)
  shutil.copyfile(index,dest/'EXPORTACION_SERVICIO.json');verify(dest,m['members']);verify(source,m['members'])
  if sha(dest/'EXPORTACION_SERVICIO.json')!=h:raise ValueError('Copied manifest differs')
  action='COPIED_VERIFIED'
 else:action='PLAN_ONLY'
 return {'alias':alias,'source':str(source),'destination':str(dest),'product_relative':dest.relative_to(C).as_posix(),'manifest_sha256':h,
  'life_id':m['life_id'],'tick':tick,**checked,'declared_directories':len(m.get('empty_directories_preserved',[])),'action':action,'not_a_second_principal':True}
def main(a):
 output=P/'control'/('MATERIALES_RP_PI06_R01_'+a.tag+'.json')
 if output.exists():raise FileExistsError('Fresh preservation tag required')
 selected=C/'sistema/estado/ACTIVO.json';act=read(selected);cardfile=C/'sistema/estado/vidas'/act['life_id']/'VIDA.json';card=read(cardfile)
 critical=[selected,cardfile,C/'sistema'/card['snapshot']];before={str(p):sha(p)for p in critical}
 names=[]if a.pares=='ninguno'else(list(PAIRS)if a.pares=='ambos'else[a.pares]);cap=capsule(a.aplicar);pairs=[pair(n,a.aplicar)for n in names]
 after={str(p):sha(p)for p in critical}
 if after!=before:raise ValueError('Actual principal changed concurrently; preserve and reconcile')
 result={'schema':'DEE.PI06.stable_RP_materials.R01','recorded_utc':datetime.now(timezone.utc).isoformat(),'applied':a.aplicar,'code_capsule':cap,'pairs':pairs,
  'protected_main_before':before,'protected_main_after':after,'Native_executed':False,'new_ticks':0,'selectors_or_recipes_registered':False,'original_states_or_code_modified':False}
 if a.aplicar:
  with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');ap.add_argument('--pares',choices=('base','postbase','ambos','ninguno'),default='ambos');ap.add_argument('--tag',default='PRESERVACION');a=ap.parse_args()
 if not a.tag.isascii()or not a.tag.replace('_','').isalnum():raise ValueError('Fresh bounded preservation tag only')
 main(a)
