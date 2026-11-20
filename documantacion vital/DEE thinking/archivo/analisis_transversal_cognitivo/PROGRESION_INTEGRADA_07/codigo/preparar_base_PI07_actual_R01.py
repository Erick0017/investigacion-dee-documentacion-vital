"""Root-only isolated code copy from current Cognitive, never an old capsule.

Default plans without writes. --apply copies only source/contract directories,
shares the exact official wheel by hard link, and records all source hashes.
No source state, selected pointer, engine installation or DEE import is made.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,ast,hashlib,json,os,shutil
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';SOURCE=C/'sistema';DEST=P/'estados/candidato/sistema'
LIFE='ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
WHEEL='dee_thinking-4.5.0-cp313-cp313-win_amd64.whl'
WHEEL_SHA='09e191d259fd15d321ea11b587f8cc02c12c7adfe81b7b96ca2dbebb1fb12d0c'
PYD_SHA='17f827341530f66816ec146af085b00a5f7b3d34d645bcd407f1279e8ac6c50d'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for node in(p,*p.parents):
  if node.exists()and(node.is_symlink()or getattr(node.lstat(),'st_file_attributes',0)&1024):raise ValueError('No reparse source/destination: '+str(node))
def main(a):
 regular(SOURCE);regular(DEST)
 if DEST.exists():raise FileExistsError('Never replace an experimental system')
 output=P/'control/SISTEMA_BASE_PI07_R01.json'
 if output.exists():raise FileExistsError('Never overwrite the baseline witness')
 active=SOURCE/'estado/ACTIVO.json';cardfile=SOURCE/'estado/vidas'/LIFE/'VIDA.json'
 selected=json.loads(active.read_text('utf-8-sig'));card=json.loads(cardfile.read_text('utf-8-sig'))
 if selected['life_id']!=LIFE or card['physical']['N']!=67 or card['physical']['tick']!=824911:raise ValueError('Reconfirm any newer actual principal instead of using an old PI07 baseline')
 source_pointers={str(p):sha(p)for p in(active,cardfile,SOURCE/card['snapshot'])}
 files=[SOURCE/'gestionar.py',SOURCE/'iniciar_sistema.ps1']
 for name in('app','capacidades','contratos','organizaciones'):
  root=SOURCE/name
  for base,dirs,names in os.walk(root,followlinks=False):
   base=Path(base);regular(base);dirs[:]=[n for n in dirs if n!='__pycache__']
   for n in dirs:regular(base/n)
   for n in sorted(names):
    f=base/n;regular(f)
    if f.suffix not in('.pyc','.pyo'):
     if not f.is_file():raise ValueError('Only regular bounded source files')
     files.append(f)
 rows=[]
 for f in files:
  regular(f)
  if f.suffix=='.py':ast.parse(f.read_bytes())
  rows.append({'file':f.relative_to(SOURCE).as_posix(),'bytes':f.stat().st_size,'sha256':sha(f)})
 wheel=SOURCE/'runtime'/WHEEL;pyd=C/'motor/python313/site-packages/dee_thinking/_native.cp313-win_amd64.pyd'
 if sha(wheel)!=WHEEL_SHA or sha(pyd)!=PYD_SHA:raise ValueError('Official frozen engine identity changed')
 proof={'schema':'DEE.PI07.current_product_isolated_code_base.v1','recorded_utc':datetime.now(timezone.utc).isoformat(),
  'source':str(SOURCE),'destination':str(DEST),'files':rows,'source_root':'ACTUAL_PRODUCT_NOT_PI04_CAPSULE',
  'logical_source_bytes':sum(v['bytes']for v in rows),'shared_engine':{'wheel':str(wheel),'wheel_sha256':WHEEL_SHA,'pyd':str(pyd),'pyd_sha256':PYD_SHA},
  'source_main':{'life_id':LIFE,'tick':824911,'snapshot_sha256':card['snapshot_sha256']},
  'source_pointers_before':source_pointers,'Native_executed':False,'new_ticks':0,'source_states_copied':False,'selected_pointer_created':False}
 if not a.apply:
  print(json.dumps({k:v for k,v in proof.items()if k!='files'},ensure_ascii=False,indent=2));return
 DEST.mkdir(parents=True,exist_ok=False)
 for row in rows:
  f=SOURCE/row['file'];dest=DEST/row['file'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,dest)
  if sha(dest)!=row['sha256']or dest.stat().st_size!=row['bytes']:raise ValueError('Copied source mismatch; preserve partial destination')
 (DEST/'runtime').mkdir(exist_ok=True);os.link(wheel,DEST/'runtime'/WHEEL)
 (DEST/'estado/checkpoints').mkdir(parents=True,exist_ok=True)
 if any(sha(SOURCE/row['file'])!=row['sha256']for row in rows):raise ValueError('Source code changed during copy; preserve partial destination')
 after={str(Path(p)):sha(Path(p))for p in source_pointers}
 if after!=source_pointers:raise ValueError('Source selection or state changed during source copy')
 proof.update(source_pointers_after=after,source_code_unchanged=True,all_copied_hashes_verified=True,shared_wheel_hardlink=True)
 with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'system':str(DEST),'files':len(rows),'proof':str(output),'proof_sha256':sha(output),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--apply',action='store_true');main(ap.parse_args())
