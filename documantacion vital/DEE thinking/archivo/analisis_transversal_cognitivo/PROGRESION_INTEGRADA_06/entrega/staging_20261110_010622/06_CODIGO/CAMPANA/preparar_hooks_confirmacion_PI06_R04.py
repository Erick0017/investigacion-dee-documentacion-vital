"""Prepare the isolated R04 import-only delta; Root applies after actual close."""
from pathlib import Path
import argparse,ast,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';SOURCE=H/'FUENTES_AMBIENTE_PI06_R03_R06';DEST=H/'FUENTES_CONFIRMACION_PI06_R04'
APP={'app/mundo_genesis_apd05.py':'ad6600b4748f27c4c52f0b70e1e8790c999cbaef6e7f6516a172cf39bb14f1cc',
 'app/cola_local.py':'6b3be37d27547cc7d5289ebe5270abbeafb98470a3645dbfeb5a0333b2f42686'}
MODULES={'capacidades/pi06_ambiente_fino_R04.py':'69feb30ebbe621091ce9297f755021476ef2218df2cc177e8bb9b3baf8b1f280',
 'capacidades/PROTOCOLO_PI06_CONFIRMACION_R04.json':'30bc006be8f73859654fe47231f5ce19b5ac6128ea4e9bd40832fd30346baba8'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source or target')
def main(a):
 proofpath=P/'control/HOOKS_AMBIENTE_PI06_R04_PREPARADOS.json'
 if not a.aplicar:
  if DEST.exists()or proofpath.exists():raise FileExistsError('Preserve previous candidate version')
  changes=[]
  for name,h in APP.items():
   f=SOURCE/name;regular(f)
   if sha(f)!=h:raise ValueError('Exact reviewed R03 candidate source only')
   old=f.read_text('utf-8-sig');new=old.replace('pi06_ambiente_R03','pi06_ambiente_fino_R04')
   if old==new or new.replace('pi06_ambiente_fino_R04','pi06_ambiente_R03')!=old:raise ValueError('Only exact import-identifier changes')
   ast.parse(new);target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf8')
   changes.append({'file':name,'before_sha256':h,'after_sha256':sha(target),'import_identifiers_replaced':old.count('pi06_ambiente_R03')})
  for name,h in MODULES.items():
   f=H/Path(name).name
   if sha(f)!=h:raise ValueError('Frozen R04 source/protocol/fixture changed')
   ast.parse(f.read_bytes())if f.suffix=='.py'else json.loads(f.read_text('utf8'))
   target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes())
  proof={'schema':'DEE.PI06.R04.fine_confirmation_import_delta.v1','dispatcher_files':changes,'new_files':MODULES,'applied':False,'Native_executed':False,
   'product_or_RP_modified':False,'old_R01_R02_R03_modules_unchanged':True,'scope':'Only PI06 handler imports select R04 wrapper; all previous modes delegate unchanged. Fine confirmation is the same fixed external supply with every-tick host safety, not an acquired body or policy.'}
  with proofpath.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
  print(json.dumps({'proof':str(proofpath),'sha256':sha(proofpath),'files':changes},ensure_ascii=False));return
 output=P/'control/HOOKS_AMBIENTE_PI06_R04_APLICADOS.json'
 if output.exists():raise FileExistsError('No blind second application')
 regular(S)
 if (S/'estado/ACTIVO.json').exists()or(P/'PI06_ROOT_NATIVE_WRITER.lock').exists():raise ValueError('Only closed unselected S6')
 locks=S/'estado/locks'
 if locks.exists()and any(locks.iterdir()):raise ValueError('An S6 owner lock blocks code application')
 proof=json.loads(proofpath.read_text('utf8'))
 for row in proof['dispatcher_files']:
  if sha(S/row['file'])!=row['before_sha256']or sha(DEST/row['file'])!=row['after_sha256']:raise ValueError('Dispatcher CAS failed before writes')
 for name,h in MODULES.items():
  if sha(DEST/name)!=h or((S/name).exists()and sha(S/name)!=h):raise ValueError('New diagnostic source conflicts with an existing revision')
 backup=H/'ORIGINALES_CONFIRMACION_PI06_R04';backup.mkdir(exist_ok=False)
 for row in proof['dispatcher_files']:
  f=backup/row['file'];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((S/row['file']).read_bytes())
 for name in MODULES:
  target=S/name;regular(target)
  if not target.exists():
   with target.open('xb')as f:f.write((DEST/name).read_bytes())
 for row in proof['dispatcher_files']:
  target=S/row['file'];regular(target);tmp=target.with_name(target.name+'.PI06_R04_'+uuid.uuid4().hex+'.tmp');tmp.write_bytes((DEST/row['file']).read_bytes())
  if sha(target)!=row['before_sha256']:raise ValueError('Concurrent isolated source change')
  os.replace(tmp,target)
  if sha(target)!=row['after_sha256']:raise ValueError('Applied source differs')
 proof.update(applied=True,Native_ticks=0,original_dispatchers_preserved_in=str(backup),system=str(S))
 with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(output),'sha256':sha(output),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
