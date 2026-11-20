"""Prepare additive R02 environment sources and import-only isolated hooks.

Root alone uses --aplicar after all affected owners close. R01 module,
protocol and physical preparation remain byte-identical; no product writes.
"""
from pathlib import Path
import argparse,ast,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';DEST=H/'FUENTES_ENTORNO_PI07_R02'
R1={'capacidades/pi07_regulacion_R01.py':'8e6ccfc2d9463c46d2312cc81108ba7e481c5cb31026f05c6d349409f8a09499','capacidades/PROTOCOLO_PI07_R01.json':'1db513e8f38607ed9e41929fc49afada1be584875d6744e718ccdd9b628cb949'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for x in(p,*p.parents):
  if x.exists()and(x.is_symlink()or getattr(x.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source or target')
def read(p):return json.loads(p.read_text('utf-8-sig'))
def save(p,x):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x',encoding='utf8')as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
def main(a):
 proofpath=P/'control/HOOKS_ENTORNO_PI07_R02_PREPARADOS.json'
 for name,h in R1.items():
  if sha(S/name)!=h:raise ValueError('Current R01 body/history differs')
 if not a.aplicar:
  if DEST.exists()or proofpath.exists():raise FileExistsError('Preserve prior qualified candidate')
  rows=[]
  for name in('app/mundo_genesis_apd05.py','app/cola_local.py'):
   source=S/name;regular(source);old=source.read_text('utf-8-sig');new=old.replace('pi07_regulacion_R01','pi07_regulacion_R02')
   if new==old or new.replace('pi07_regulacion_R02','pi07_regulacion_R01')!=old:raise ValueError('Only exact PI07 import-name changes')
   ast.parse(new);target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf8');rows.append({'file':name,'before_sha256':sha(source),'after_sha256':sha(target),'identifiers_replaced':old.count('pi07_regulacion_R01')})
  newfiles=[]
  for name in('capacidades/pi07_regulacion_R02.py','capacidades/PROTOCOLO_PI07_R02.json'):
   source=H/Path(name).name;regular(source)
   if source.suffix=='.py':ast.parse(source.read_bytes())
   else:
    p=read(source)
    if p.get('schema')!='DEE.PI07.regulation.protocol.R02'or p.get('status')!='SEALED_FOR_EVALUATION':raise ValueError('Actual separately sealed R02 evaluation protocol required')
   target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes());newfiles.append({'file':name,'bytes':source.stat().st_size,'sha256':sha(source)})
  proof={'schema':'DEE.PI07.R02.isolated_environment_import_delta.v1','dispatcher_files':rows,'new_files':newfiles,'preserved_R1':R1,'Native_executed':False,'product_modified':False,'applied':False,
   'scope':'New external environment progress/control/observation with fixed R01 Native actor functions/anatomy; no bank/state transfer or R01 protocol rewrite.'}
  save(proofpath,proof);print(json.dumps({'proof':str(proofpath),'sha256':sha(proofpath),'Native_executed':False}));return
 output=P/'control/HOOKS_ENTORNO_PI07_R02_APLICADOS.json'
 if output.exists():raise FileExistsError('No blind reapplication')
 if (S/'estado/ACTIVO.json').exists()or(P/'PI07_ROOT_NATIVE_WRITER.lock').exists():raise ValueError('Only closed unselected isolated S7')
 locks=S/'estado/locks'
 if locks.exists()and any(locks.iterdir()):raise ValueError('An S7 owner lock remains')
 proof=read(proofpath)
 for row in proof['dispatcher_files']:
  if sha(S/row['file'])!=row['before_sha256']or sha(DEST/row['file'])!=row['after_sha256']:raise ValueError('Import-only dispatcher CAS failed')
 for row in proof['new_files']:
  if(S/row['file']).exists()or sha(DEST/row['file'])!=row['sha256']:raise ValueError('Only fresh immutable R02 source names')
 backup=H/'ORIGINALES_HOOKS_ENTORNO_PI07_R02';backup.mkdir(exist_ok=False)
 for row in proof['dispatcher_files']:
  file=backup/row['file'];file.parent.mkdir(parents=True,exist_ok=True);file.write_bytes((S/row['file']).read_bytes())
 for row in proof['new_files']:
  with(S/row['file']).open('xb')as f:f.write((DEST/row['file']).read_bytes())
 for row in proof['dispatcher_files']:
  target=S/row['file'];regular(target);tmp=target.with_name(target.name+'.PI07_ENV_R02_'+uuid.uuid4().hex+'.tmp');tmp.write_bytes((DEST/row['file']).read_bytes())
  if sha(target)!=row['before_sha256']:raise ValueError('Concurrent isolated dispatcher change')
  os.replace(tmp,target)
 for name,h in R1.items():
  if sha(S/name)!=h:raise RuntimeError('R01 source history changed')
 proof.update(applied=True,new_Native_ticks=0,original_dispatchers_preserved_in=str(backup));save(output,proof)
 print(json.dumps({'proof':str(output),'sha256':sha(output),'Native_executed':False}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
