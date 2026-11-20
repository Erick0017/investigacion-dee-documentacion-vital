"""Root-only additive stable RP copy of the already closed C prefix.

Default plan; --aplicar copies exact sealed bytes/directories without Native,
registry changes, source removal or rewriting the original campaign prefix.
"""
from pathlib import Path,PurePosixPath
import argparse,datetime,hashlib,json,os,shutil,sqlite3
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';SRC=P/'pares/C_HEREDADA_T884835';DST=C/'reproducibilidad/materiales/PI09_C_HEREDADA_T884835'
PIN='08a8e65deb2071b7653bc0ab95f3d55b8038191a4f585c6803f6d81c16e8182f'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def require(ok,msg):
 if not ok:raise ValueError(msg)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def safe(root,name):
 r=PurePosixPath(name);require(isinstance(name,str)and name and '\\'not in name and ':'not in name and not r.is_absolute()and all(x not in('.','..')for x in r.parts),'Miembro portátil inseguro')
 p=root.joinpath(*r.parts)
 for x in(p,*p.parents):
  require(not x.exists()or not(x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024),'No se admiten enlaces')
  if x==root:break
 return p
def validate(root):
 manifest=root/'EXPORTACION_SERVICIO.json';require(sha(manifest)==PIN,'Prefijo C distinto del fijado');m=read(manifest)
 require(m['schema']=='DEE.persistent_service.paired_export.v1'and m['physical']['tick']==884835 and m['queue_journal_required']is True,'Conjunto completo C requerido')
 rows=m['members'];names=[x['file']for x in rows];require(len(names)==len(set(names)),'Miembro repetido')
 for row in rows:
  f=safe(root,row['file']);require(f.is_file()and f.stat().st_size==row['bytes']and sha(f)==row['sha256'],'Miembro C no íntegro: '+row['file'])
 require({p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()and p!=manifest}==set(names),'Archivos no indexados/ausentes')
 for name in m['empty_directories_preserved']:require(safe(root,name).is_dir(),'Directorio C ausente')
 con=sqlite3.connect((root/'cola.sqlite3').as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  require(con.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite no íntegra')
  require(con.execute("SELECT COUNT(*) FROM requests WHERE status IN('queued','processing','uncertain')").fetchone()[0]==0,'Transporte sin cierre')
 finally:con.close()
 return m
def main():
 p=argparse.ArgumentParser();p.add_argument('--aplicar',action='store_true');a=p.parse_args()
 if not a.aplicar:
  print(json.dumps({'mode':'PLAN_ONLY_NO_NATIVE','source':str(SRC),'destination':str(DST),'manifest_sha256':PIN,'registry_modified':False,'source_retired':False,'Root_budget_check_required':True},ensure_ascii=False,indent=2));return
 proof_path=P/'control/PREFIJO_C_ESTABLE_RP_PI09_R01.json';require(not DST.exists()and not proof_path.exists(),'Destino/comprobante ya existe; no se sobrescribe')
 m=validate(SRC);active=C/'sistema/estado/ACTIVO.json';active_before=sha(active)
 DST.mkdir(parents=True)
 for name in m['empty_directories_preserved']:safe(DST,name).mkdir(parents=True,exist_ok=True)
 for row in m['members']:
  source=safe(SRC,row['file']);target=safe(DST,row['file']);target.parent.mkdir(parents=True,exist_ok=True)
  with source.open('rb')as src,target.open('xb')as dst:shutil.copyfileobj(src,dst)
  require(sha(target)==row['sha256'],'Copia parcial no íntegra; conservar destino')
 with(SRC/'EXPORTACION_SERVICIO.json').open('rb')as src,(DST/'EXPORTACION_SERVICIO.json').open('xb')as dst:shutil.copyfileobj(src,dst)
 validate(DST);validate(SRC);require(sha(active)==active_before,'Cambió la selección de la principal')
 proof={'schema':'DEE.PI09.stable_RP_prefix_preserved.R01','applied':True,'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source':str(SRC),'destination':str(DST),'manifest_sha256':PIN,'members':len(m['members']),'bytes':sum(x['bytes']for x in m['members']),'directories':len(m['empty_directories_preserved']),'source_and_destination_verified':True,'source_removed':False,'Native_executed':False,'new_native_ticks':0,'registry_modified':False,'principal_selection_unchanged':True}
 proof_path.parent.mkdir(parents=True,exist_ok=True)
 with proof_path.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'applied':True,'proof':str(proof_path),'sha256':sha(proof_path),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':main()
