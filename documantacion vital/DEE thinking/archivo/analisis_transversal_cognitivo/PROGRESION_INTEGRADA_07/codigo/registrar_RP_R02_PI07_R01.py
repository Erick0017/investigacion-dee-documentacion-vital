"""Additive registration of already qualified complete PI07 materials, no DEE import."""
from pathlib import Path
from datetime import datetime,timezone
import argparse,copy,hashlib,json,os,shutil,uuid
P=Path(__file__).resolve().parents[1];C=P.parents[2]/'DEE Cognitive 2.0';RP=C/'reproducibilidad'
STAGE=P/'codigo/RP_R02_EP04_PREPARADA';KEY='PI07_RP_R02_EP04_R01';ALIAS='PI07_PREADQUISICION_TC_T824914';NAME='pi07_r02_8_ep04'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
def regular(p):
 for q in(p,*p.parents):
  if q.exists()and(q.is_symlink()or getattr(q.lstat(),'st_file_attributes',0)&1024):raise ValueError('No linked/reparse material')
def members(root,rows):
 total=0;seen=set()
 for row in rows:
  r=Path(row['file']);p=root/r;regular(p)
  if r.is_absolute()or'..'in r.parts or str(r)in seen or not p.resolve().is_relative_to(root.resolve())or p.stat().st_size!=row['bytes']or sha(p)!=row['sha256']:raise ValueError('Qualified material differs: '+str(r))
  seen.add(str(r));total+=row['bytes']
 return {'members':len(seen),'bytes':total}
def main(a):
 report=P/'control'/('RP_R02_PI07_'+('REGISTRADA'if a.aplicar else'PLAN')+'.json')
 if report.exists():raise FileExistsError(report)
 src=STAGE/'CODIGO_SISTEMA';cm=read(src/'SISTEMA_CODIGO.json');caps=members(src,cm['files']);pair=RP/'materiales'/ALIAS;pm=read(pair/'EXPORTACION_SERVICIO.json');paircheck=members(pair,pm['members'])
 if sha(pair/'EXPORTACION_SERVICIO.json')!='5db0faf4a5cea0fb80da8822a5c122175cb3ac34a8734beb59d726768f1b8477'or pm['physical']['tick']!=824914:raise ValueError('Exact coherent unlearned P0 full pair required')
 recipe=read(STAGE/(NAME+'.json'))
 if recipe['id']!=NAME or recipe['prefix']!=ALIAS or recipe['code_capsule_key']!=KEY:raise ValueError('Exact prepared recipe binding')
 dst=RP/'codigo_preservado'/KEY;target=RP/'recetas'/(NAME+'.json');config=RP/'RECURSOS.json';old=config.read_bytes();d=copy.deepcopy(json.loads(old))
 if KEY in d.get('code_capsules',{})or ALIAS in d.get('pairs',{})or dst.exists()or target.exists():raise FileExistsError('Fresh registration only; preserve prior aliases')
 critical=[C/'sistema/estado/ACTIVO.json'];active=read(critical[0]);vf=C/'sistema/estado/vidas'/active['life_id']/'VIDA.json';critical.extend([vf,C/'sistema'/read(vf)['snapshot']]);before={str(p):sha(p)for p in critical}
 capentry={'product_relative':dst.relative_to(C).as_posix(),'manifest':'SISTEMA_CODIGO.json','manifest_sha256':sha(src/'SISTEMA_CODIGO.json')}
 pairentry={'alias':ALIAS,'product_relative':pair.relative_to(C).as_posix(),'manifest_sha256':sha(pair/'EXPORTACION_SERVICIO.json'),'life_id':pm['life_id'],'tick':824914,**paircheck,'scope':'Complete frozen preacquisition P0; not a principal or restored current life.'}
 d.setdefault('code_capsules',{})[KEY]=capentry;d.setdefault('pairs',{})[ALIAS]=pairentry
 proof={'schema':'DEE.PI07.additive_RP_registration.R01','at_utc':datetime.now(timezone.utc).isoformat(),'applied':False,'Native_ticks':0,'recipe':NAME,'recipe_sha256':sha(STAGE/(NAME+'.json')),'capsule':capentry,'code_members_verified':caps,'pair':pairentry,'resources_before_sha256':hashlib.sha256(old).hexdigest(),'protected_before':before}
 if a.aplicar:
  if(P/'PI07_ROOT_NATIVE_WRITER.lock').exists()or(RP/'EJECUCION_MATERIAL.lock').exists():raise ValueError('Register only between material owners')
  backup=STAGE/'RECURSOS_ANTES_REGISTRO_ROOT.json'
  with backup.open('xb')as f:f.write(old)
  shutil.copytree(src,dst,symlinks=False);members(dst,cm['files'])
  if sha(dst/'SISTEMA_CODIGO.json')!=capentry['manifest_sha256']:raise RuntimeError('Capsule copy mismatch')
  with target.open('xb')as f:f.write((STAGE/(NAME+'.json')).read_bytes())
  if config.read_bytes()!=old:raise RuntimeError('Concurrent resources change; preserve staged additions')
  tmp=config.with_name(config.name+'.PI07_'+uuid.uuid4().hex+'.tmp')
  with tmp.open('x',encoding='utf8')as f:json.dump(d,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
  if config.read_bytes()!=old:raise RuntimeError('Concurrent resources change; no overwrite')
  os.replace(tmp,config);proof.update(applied=True,resources_after_sha256=sha(config))
 after={str(p):sha(p)for p in critical}
 if after!=before:raise RuntimeError('Selected principal changed; no immutable-principal claim')
 proof['protected_after']=after;proof['principal_unchanged']=True
 with report.open('x',encoding='utf8')as f:json.dump(proof,f,ensure_ascii=False,indent=2);f.write('\n')
 print(json.dumps({'proof':str(report),'sha256':sha(report),'applied':proof['applied'],'Native_ticks':0}))
if __name__=='__main__':
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--aplicar',action='store_true');main(ap.parse_args())
