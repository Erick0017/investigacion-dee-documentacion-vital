"""Prepare the isolated R03 import-only delta; Root applies after actual close."""
from pathlib import Path
import argparse,ast,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';SOURCE=H/'FUENTES_INTERRUPCION_PI06_R02';DEST=H/'FUENTES_AMBIENTE_PI06_R03_R06'
APP={'app/mundo_genesis_apd05.py':'fb42acdae489ba50b859fe021dc15447a9c42cc0bc39cc167c8bab033eaf6b8d',
 'app/cola_local.py':'142a636ee90c95aad89ea1955ccce8e1a2f424fa61a1e7bc93205985fc2f1758'}
MODULES={'capacidades/pi06_ambiente_R03.py':'9d06316836e24f915da74116d9b70f3eafa51bd0062934d974ee2a08ca8e99c6',
 'capacidades/PROTOCOLO_PI06_AMBIENTE_R03_R06.json':'d70b1c2120569875113baab1c48da466457300c766761eb4f74ce65f5181b7d7',
 'capacidades/FIXTURE_PI06_AMBIENTE_R03_R02.json':'484b8efe0f0fbd53a815a4d33f17e0340e965370db44934aa99f35e4acbc1c7c'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source or target')
def main(a):
 proofpath=P/'control/HOOKS_AMBIENTE_PI06_R03_R06_PREPARADOS.json'
 if not a.aplicar:
  if DEST.exists()or proofpath.exists():raise FileExistsError('Preserve previous candidate version')
  changes=[]
  for name,h in APP.items():
   f=SOURCE/name;regular(f)
   if sha(f)!=h:raise ValueError('Exact reviewed R02 candidate source only')
   old=f.read_text('utf-8-sig');new=old.replace('pi06_interrupcion_R02','pi06_ambiente_R03')
   if old==new or new.replace('pi06_ambiente_R03','pi06_interrupcion_R02')!=old:raise ValueError('Only exact import-identifier changes')
   ast.parse(new);target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf8')
   changes.append({'file':name,'before_sha256':h,'after_sha256':sha(target),'import_identifiers_replaced':old.count('pi06_interrupcion_R02')})
  for name,h in MODULES.items():
   f=H/Path(name).name
   if sha(f)!=h:raise ValueError('Frozen R03 source/protocol/fixture changed')
   ast.parse(f.read_bytes())if f.suffix=='.py'else json.loads(f.read_text('utf8'))
   target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(f.read_bytes())
  proof={'schema':'DEE.PI06.R03.environment_import_delta.v1','dispatcher_files':changes,'new_files':MODULES,'applied':False,'Native_executed':False,
   'product_or_RP_modified':False,'old_R01_R02_modules_unchanged':True,'scope':'Only PI06 handler imports select R03 wrapper; all previous modes delegate unchanged. New environment is fixed external supply/host safety, not an acquired body or policy.'}
  with proofpath.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
  print(json.dumps({'proof':str(proofpath),'sha256':sha(proofpath),'files':changes},ensure_ascii=False));return
 output=P/'control/HOOKS_AMBIENTE_PI06_R03_R06_APLICADOS.json'
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
 backup=H/'ORIGINALES_AMBIENTE_PI06_R03_R06';backup.mkdir(exist_ok=False)
 for row in proof['dispatcher_files']:
  f=backup/row['file'];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((S/row['file']).read_bytes())
 for name in MODULES:
  target=S/name;regular(target)
  if not target.exists():
   with target.open('xb')as f:f.write((DEST/name).read_bytes())
 for row in proof['dispatcher_files']:
  target=S/row['file'];regular(target);tmp=target.with_name(target.name+'.PI06_R03_'+uuid.uuid4().hex+'.tmp');tmp.write_bytes((DEST/row['file']).read_bytes())
  if sha(target)!=row['before_sha256']:raise ValueError('Concurrent isolated source change')
  os.replace(tmp,target)
  if sha(target)!=row['after_sha256']:raise ValueError('Applied source differs')
 proof.update(applied=True,Native_ticks=0,original_dispatchers_preserved_in=str(backup),system=str(S))
 with output.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(output),'sha256':sha(output),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
