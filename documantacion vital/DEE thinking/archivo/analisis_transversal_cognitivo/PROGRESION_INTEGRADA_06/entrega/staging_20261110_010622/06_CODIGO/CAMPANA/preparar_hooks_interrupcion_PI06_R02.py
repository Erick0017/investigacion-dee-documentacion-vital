"""Prepare/apply only the isolated R02 wrapper and import-name dispatcher delta.

Default writes candidates under campaign code. Root --aplicar requires all S6
owners closed; current Cognitive, old R01 modules and RP capsule stay intact.
"""
from pathlib import Path
import argparse,ast,hashlib,json,os,uuid
P=Path(__file__).resolve().parents[1];H=P/'codigo';S=P/'estados/candidato/sistema';DEST=H/'FUENTES_INTERRUPCION_PI06_R02'
APP={'app/mundo_genesis_apd05.py':'10a4f3168c23f386e8babe0d5ff2eb304963747c4cebfa18223ddbd05db2ec8c',
 'app/cola_local.py':'b3e7080ba521964bbb879adab6839ffcf3c0acdc905f4ece5410f11b0f245420'}
MODULES={'capacidades/pi06_interrupcion_R02.py':'80643a9d81ee92225350d3bc81a94d7e65c685e4c1b1f27b932cd9956454ef72',
 'capacidades/PROTOCOLO_PI06_INTERRUPCION_R02.json':'08c4531eb6722e2a229636d36e3724cbb370093eb81f47497f6465b76754be3c'}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked source or target')
def main(a):
 proofpath=P/'control/HOOKS_INTERRUPCION_PI06_R02_PREPARADOS.json'
 if not a.aplicar:
  if DEST.exists()or proofpath.exists():raise FileExistsError('Preserve candidate revision')
  changes=[]
  for name,h in APP.items():
   source=S/name;regular(source)
   if sha(source)!=h:raise ValueError('Qualified isolated R01 dispatcher changed')
   old=source.read_text('utf-8-sig');new=old.replace('pi06_organizacion_R01','pi06_interrupcion_R02')
   if old==new or new.replace('pi06_interrupcion_R02','pi06_organizacion_R01')!=old:raise ValueError('Not an exact import-name-only delta')
   ast.parse(new);target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_text(new,encoding='utf8')
   changes.append({'file':name,'before_sha256':h,'after_sha256':sha(target),'replaced_import_identifiers':old.count('pi06_organizacion_R01')})
  for name,h in MODULES.items():
   source=H/Path(name).name
   if sha(source)!=h:raise ValueError('Candidate instrument source changed')
   if source.suffix=='.py':ast.parse(source.read_bytes())
   else:json.loads(source.read_text('utf8'))
   target=DEST/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(source.read_bytes())
  proof={'schema':'DEE.PI06.R02.import_only_wrapper_preparation.v1','dispatcher_files':changes,'new_files':MODULES,
   'Native_executed':False,'applied':False,'R01_scientific_source_modified':False,'product_or_RP_modified':False,
   'scope':'Only PI06 handler imports now select wrapper. All old PI06 calls delegate to exact R01; new fixed counterflow mode remains an external causal diagnostic.'}
  with proofpath.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
  print(json.dumps({'proof':str(proofpath),'sha256':sha(proofpath),'changes':changes},ensure_ascii=False));return
 result=P/'control/HOOKS_INTERRUPCION_PI06_R02_APLICADOS.json'
 if result.exists():raise FileExistsError('No blind second apply')
 if (S/'estado/ACTIVO.json').exists()or(P/'PI06_ROOT_NATIVE_WRITER.lock').exists():raise ValueError('Only closed unselected S6')
 locks=S/'estado/locks'
 if locks.exists()and any(locks.iterdir()):raise ValueError('Any S6 writer lock blocks code changes')
 proof=json.loads(proofpath.read_text('utf8'))
 for row in proof['dispatcher_files']:
  if sha(S/row['file'])!=row['before_sha256']or sha(DEST/row['file'])!=row['after_sha256']:raise ValueError('Dispatcher CAS failed before writes')
 for name,h in MODULES.items():
  if sha(DEST/name)!=h:raise ValueError('Frozen wrapper/protocol differs')
  if (S/name).exists()and sha(S/name)!=h:raise ValueError('An existing diagnostic instrument is protected')
 backup=H/'ORIGINALES_INTERRUPCION_PI06_R02';backup.mkdir(exist_ok=False)
 for row in proof['dispatcher_files']:
  f=backup/row['file'];f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes((S/row['file']).read_bytes())
 for name,h in MODULES.items():
  target=S/name;regular(target)
  if not target.exists():
   with target.open('xb')as f:f.write((DEST/name).read_bytes())
 for row in proof['dispatcher_files']:
  target=S/row['file'];regular(target);tmp=target.with_name(target.name+'.PI06_R02_'+uuid.uuid4().hex+'.tmp');tmp.write_bytes((DEST/row['file']).read_bytes())
  if sha(target)!=row['before_sha256']:raise ValueError('Concurrent dispatcher change')
  os.replace(tmp,target)
  if sha(target)!=row['after_sha256']:raise ValueError('Applied dispatcher hash mismatch')
 proof.update(applied=True,original_dispatchers_preserved_in=str(backup),system=str(S),Native_ticks=0)
 with result.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(result),'sha256':sha(result),'Native_executed':False},ensure_ascii=False))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
