"""Verificar o copiar una selección explícita. Sólo archivos; nunca abre DEE."""
from pathlib import Path,PurePosixPath
from concurrent.futures import ThreadPoolExecutor
import argparse,datetime,hashlib,json,os,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def no_link(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('Reparse forbidden')
def member(root,name):
 r=PurePosixPath(name)
 if r.is_absolute()or ':'in name or chr(92)in name or any(x in('..','.')for x in r.parts):raise ValueError('Unsafe member')
 p=root.joinpath(*r.parts);no_link(p);return p
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('modo',choices=['listar','verificar','copiar']);p.add_argument('--perfil',choices=['sdk','privado'],required=True);p.add_argument('--destino',type=Path);p.add_argument('--registro',type=Path);a=p.parse_args()
 m=read(ROOT/('MANIFIESTO_DISTRIBUCION_SDK.json'if a.perfil=='sdk'else'MANIFIESTO_INVESTIGACION_PRIVADA.json'))
 rows=m['files'];out={'profile':a.perfil,'files':len(rows),'bytes':sum(x['bytes']for x in rows),'NativeOpened':False,'ticksAdvanced':0}
 if a.modo=='listar':print(json.dumps(out));return
 target=a.destino.absolute()if a.destino else ROOT
 if a.modo=='copiar':
  if not a.destino:raise ValueError('Explicit new destination required')
  no_link(target)
  if target.exists()or target.is_relative_to(ROOT)or ROOT.is_relative_to(target):raise ValueError('New independent destination required')
  target.mkdir(parents=True)
 def check(row):
  src=member(ROOT,row['file']);s=src.stat();assert s.st_size==row['bytes']
  if a.modo=='copiar':
   dst=member(target,row['file']);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
   assert src.stat().st_mtime_ns==s.st_mtime_ns and src.stat().st_size==s.st_size,'Source changed'
  else:dst=src
  assert dst.stat().st_size==row['bytes']and sha(dst)==row['sha256'],'Member mismatch: '+row['file']
  return {'file':row['file'],'bytes':row['bytes'],'sha256':row['sha256'],'mtime_ns':dst.stat().st_mtime_ns}
 verified=[]
 log=a.registro.open('x',encoding='utf-8')if a.registro else None
 try:
  with ThreadPoolExecutor(max_workers=12)as pool:
   for i,row in enumerate(pool.map(check,rows),1):
    verified.append(row)
    if log:log.write(json.dumps(row,ensure_ascii=False)+'\n')
    if i%4000==0:
     if log:log.flush()
     print(json.dumps({'phase':a.modo,'files':i,'total':len(rows)}),flush=True)
 finally:
  if log:log.close()
 if a.modo=='copiar':
  for name in m.get('empty_directories',[]):member(target,name).mkdir(parents=True,exist_ok=True)
  for name in('MANIFIESTO_ROBLOX.json','MANIFIESTO_DISTRIBUCION_SDK.json','MANIFIESTO_INVESTIGACION_PRIVADA.json'):
   src=ROOT/name;dst=target/name
   if a.perfil=='sdk'and name!='MANIFIESTO_DISTRIBUCION_SDK.json':continue
   shutil.copy2(src,dst);assert sha(src)==sha(dst)
  # Diagnostic copy stays a copy; no switch of active laboratory or selectors.
 out.update(integrity='VERIFIED',target=str(target),allSelectedMembersMatch=True,verifiedAt=datetime.datetime.now().astimezone().isoformat())
 print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
