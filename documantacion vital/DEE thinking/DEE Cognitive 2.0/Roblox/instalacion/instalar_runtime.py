"""Instalación FS privada verificable. No crea credenciales, sesiones ni mundos."""
from pathlib import Path,PurePosixPath
import argparse,datetime,hashlib,json,os,shutil,stat,sys,zipfile
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
_checked_directories=set()
def no_link(p):
 for q in(p,*p.parents):
  if q in _checked_directories:break
  if q.exists():
   s=q.lstat()
   if q.is_symlink()or getattr(s,'st_file_attributes',0)&1024:raise ValueError('NO_REPARSE_ALLOWED')
   if stat.S_ISDIR(s.st_mode):_checked_directories.add(q)
def member(root,name):
 r=PurePosixPath(name)
 if not name or chr(92)in name or ':'in name or r.is_absolute()or any(x in('..','.')for x in r.parts):raise ValueError('UNSAFE_MEMBER')
 p=root.joinpath(*r.parts);no_link(p);return p
def manifest(package):
 m=read(package/'dependencias/MANIFIESTO_RUNTIME_R06.json')
 if m['schema']!='DEE.Roblox.PrivateRuntime.Payload.R06'or m['credentials_included']is not False:raise ValueError('EXPECTED_SECRET_FREE_PAYLOAD')
 return m
def verify_runtime(target,m):
 rows=[]
 for i,r in enumerate(m['files'],1):
  p=member(target,r['file']);ok=p.is_file()and p.stat().st_size==r['bytes']and sha(p)==r['sha256']
  if not ok:raise RuntimeError('INSTALLED_MEMBER_MISMATCH:'+r['file'])
  if i%4000==0:print(json.dumps({'phase':'verify_installed','files':i,'total':len(m['files'])}),flush=True)
 return {'files':len(m['files']),'bytes':m['expanded_bytes'],'all_hashes_match':True,'credentials_provided':(target/'configuracion/CONEXION_PRIVADA.json').is_file(),'material_session_allowed':False,'NativeOpened':False}
def install(package,target,bootstrap=False,preextracted=False):
 m=manifest(package);payload=member(package/'dependencias',m['payload']['file'])
 if payload.stat().st_size!=m['payload']['bytes']or sha(payload)!=m['payload']['sha256']:raise ValueError('PAYLOAD_HASH_MISMATCH')
 target=Path(os.path.abspath(target));no_link(target)
 if target==target.parent or target.is_relative_to(package)or package.is_relative_to(target):raise ValueError('INDEPENDENT_NEW_SHORT_TARGET_REQUIRED')
 if target.exists():
  b=target/'BOOTSTRAP_R06.json'
  tar_marker=target/'EXTRACCION_TAR_R06.sha256'
  if preextracted:
   if not tar_marker.is_file()or tar_marker.read_text('ascii').strip()!=m['payload']['sha256']:raise ValueError('FRESH_TAR_EXTRACTION_MARKER_REQUIRED')
   if(target/'INSTALACION_ROBLOX_R06.json').exists():raise FileExistsError('ALREADY_INSTALLED_NO_OVERWRITE')
  elif not bootstrap or not b.is_file()or read(b).get('payloadSha256')!=m['payload']['sha256']:raise FileExistsError('NO_EXISTING_RUNTIME_OVERWRITE')
  allowed={r['file']:r for r in m['files']if r['file'].startswith('dependencias/producto/motor/python313/')and '/'not in r['file'][len('dependencias/producto/motor/python313/'): ]}
  extracted_expected={r['file']:r for r in m['files']}
  for p in target.rglob('*'):
   no_link(p)
   if p.is_file()and p!=b and(not preextracted or p!=tar_marker):
    rel=p.relative_to(target).as_posix();r=extracted_expected.get(rel)if preextracted else allowed.get(rel)
    if not r or p.stat().st_size!=r['bytes']or(not preextracted and sha(p)!=r['sha256']):raise ValueError('BOOTSTRAP_NOT_CLEAN_NO_RESUME')
 else:target.mkdir(parents=True)
 if shutil.disk_usage(target).free<(0 if preextracted else m['expanded_bytes'])+200000000:raise RuntimeError('INSUFFICIENT_FREE_SPACE')
 marker=target/'INSTALACION_EN_CURSO_R06.json'
 if marker.exists():raise RuntimeError('PARTIAL_INSTALL_PRESERVED_NO_AUTOMATIC_RETRY')
 marker.write_text(json.dumps({'payloadSha256':m['payload']['sha256'],'startedAt':datetime.datetime.now().astimezone().isoformat(),'NativeOpened':False})+'\n',encoding='utf-8')
 expected={r['file']:r for r in m['files']}
 if len(expected)!=len(m['files'])or len({n.casefold()for n in expected})!=len(expected):raise ValueError('DUPLICATE_MEMBER')
 with zipfile.ZipFile(payload)as z:
  members=[i for i in z.infolist()if not i.is_dir()]
  if {i.filename for i in members}!=set(expected)or len(members)!=len(expected):raise ValueError('ARCHIVE_MANIFEST_SET_MISMATCH')
  for i,item in enumerate(members,1):
   if stat.S_ISLNK(item.external_attr>>16):raise ValueError('ARCHIVE_LINK_FORBIDDEN')
   r=expected[item.filename];p=member(target,item.filename);p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():
    if not(bootstrap or preextracted)or p.stat().st_size!=r['bytes']or(not preextracted and sha(p)!=r['sha256']):raise FileExistsError('Preserve existing data '+r['file'])
   else:
    h=hashlib.sha256();count=0
    with z.open(item)as src,p.open('xb')as dst:
     for b in iter(lambda:src.read(1048576),b''):dst.write(b);h.update(b);count+=len(b)
    if count!=r['bytes']or h.hexdigest()!=r['sha256']:raise RuntimeError('EXTRACTED_HASH_MISMATCH:'+r['file'])
   if i%4000==0:print(json.dumps({'phase':'install_private_payload','files':i,'total':len(members)}),flush=True)
 for name in m['empty_directories']:member(target,name).mkdir(parents=True,exist_ok=True)
 result=verify_runtime(target,m)
 # New install metadata is outside all scientific snapshots/databases/manifests.
 status={'schema':'DEE.Roblox.InstalledPrivateRuntime.R06','installedAt':datetime.datetime.now().astimezone().isoformat(),'payloadSha256':m['payload']['sha256'],'runtimeRoot':str(target),'closedNative':m['closed_native'],'CorePairCurrent':False,'authentication':'NOT_PROVISIONED','session':'PENDING_AUTHORIZED_PROSPECTIVE_PROTOCOL','NativeOpened':False,'newTicks':0}
 (target/'INSTALACION_ROBLOX_R06.json').write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 template={'schema':'DEE.Roblox.SDK.private.0.1.0','bind':'127.0.0.1','port':8896,'token':'PROPORCIONAR_POR_CANAL_AUTORIZADO'}
 (target/'configuracion/CONEXION_PRIVADA.json.template').write_text(json.dumps(template,indent=2)+'\n',encoding='utf-8')
 os.rename(marker,target/'INSTALACION_COMPLETADA_R06.json')
 result.update(runtimeRoot=str(target),installationMarker=str(target/'INSTALACION_ROBLOX_R06.json'),credentialsGenerated=False,newTicks=0)
 return result
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--paquete',type=Path,default=ROOT);p.add_argument('--destino',type=Path,required=True);p.add_argument('--continuar-bootstrap',action='store_true');p.add_argument('--finalizar-extraido',action='store_true');p.add_argument('--verificar',action='store_true');p.add_argument('--denegar',action='append',default=[]);a=p.parse_args()
 forbidden=[os.path.normcase(str(Path(x).absolute()))for x in a.denegar]
 def audit(event,args):
  if event in('open','os.scandir','os.listdir','ctypes.dlopen')and args and isinstance(args[0],(str,bytes,os.PathLike)):
   name=os.path.normcase(os.path.abspath(os.fsdecode(args[0])))
   if any(name==x or name.startswith(x+os.sep)for x in forbidden):raise PermissionError('Original installation access explicitly denied')
 if forbidden:sys.addaudithook(audit)
 package=a.paquete.resolve(strict=True)
 result=verify_runtime(a.destino.resolve(strict=True),manifest(package))if a.verificar else install(package,a.destino,a.continuar_bootstrap,a.finalizar_extraido)
 print(json.dumps(result,ensure_ascii=False));return 0
if __name__=='__main__':raise SystemExit(main())
