"""Closed complete SDK K4 freeze; FS copy/hash only, no Native import."""
from pathlib import Path
import hashlib, json, os, shutil, sys, time
RUNTIME=Path("D:\\GENESIS AI\\GENESIS 5.0\\simulador de universo ab-initio\\dee_libreria\\VERSION_27\\tests\\_sdk_r06_valid_20261118\\RUNTIME_PRIVADO_LOCAL")
sys.path.insert(0,str(RUNTIME/'backend/r06'))
from sdk_common import closed_native,instance_home,read,sha
home,cfg=instance_home('SDK_DEMO_3666B1B0A4134233',RUNTIME)
target=RUNTIME/'estado_demo/prefijos/SDK_R06_K4_COMPLETO'
if target.exists():raise FileExistsError('Existing frozen point; reconcile instead of repeating')
for lock in ('SDK_SERVICE.lock','SDK_CAPABILITIES_SERVICE.lock'):
    if (home/lock).exists():raise RuntimeError('Owner still active')
before=closed_native(home,cfg)
if before['nativeTick']!=994315 or before['pending']!=0 or cfg['completedCycles']!=2:
    raise RuntimeError('Exact closed K4 cut required')
if read(RUNTIME/'estado_demo/LEDGER_SDK_R06.json')['intents']:raise RuntimeError('Pending Native intent')
closed=read(home/'BACKEND_CLOSED.json')
if not closed['backendWriterClosed'] or closed['nativeTick']!=994315:raise RuntimeError('Closed proof required')
files=[]
for base,dirs,names in os.walk(home,followlinks=False):
    for entry in [Path(base),*[Path(base)/n for n in dirs+names]]:
        st=entry.lstat()
        if entry.is_symlink() or getattr(st,'st_file_attributes',0)&1024:raise RuntimeError('No reparse path')
    for name in names:files.append((Path(base)/name).relative_to(home))
target.mkdir()
(target/'COPIA_EN_CURSO.json').write_text(json.dumps({'source':str(home),'tick':994315,'newNativeTicks':0}),encoding='utf8')
for base,dirs,_ in os.walk(home,followlinks=False):
    for name in dirs:(target/(Path(base)/name).relative_to(home)).mkdir(parents=True,exist_ok=True)
rows=[]
for rel in sorted(files,key=str):
    src=home/rel;dst=target/rel
    if not dst.parent.exists():dst.parent.mkdir(parents=True)
    shutil.copy2(src,dst)
    a=sha(src);b=sha(dst)
    if a!=b or src.stat().st_size!=dst.stat().st_size:raise RuntimeError('Copy mismatch:'+str(rel))
    rows.append({'file':rel.as_posix(),'bytes':src.stat().st_size,'sha256':a})
after=closed_native(home,cfg)
if before!=after:raise RuntimeError('Source changed during closed copy')
manifest={'schema':'DEE.SDK.complete_closed_K4_copy.R06','source':str(home),'target':str(target),
'lifeId':cfg['lifeId'],'sessionId':cfg['sessionId'],'native':before,'newNativeTicks':0,
'files':rows,'members':len(rows),'bytes':sum(x['bytes']for x in rows),'completedUtcEpoch':time.time(),
'sharedRuntime':str(RUNTIME),'sharedMotorAndBackendCopiedAgain':False,
'scope':'Complete closed diagnostic HOME copy with unchanged Native/SQLite/interfaces/queues/artifacts and World/Agent pair; shared official dependencies remain at sharedRuntime. Frozen recovery point, not another selected principal.'}
out=target/'MANIFIESTO_COPIA_K4.json'
out.write_text(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf8')
(target/'COPIA_EN_CURSO.json').rename(target/'COPIA_COMPLETADA_DESDE_INTENTO.json')
print(json.dumps({'status':'COMPLETE_CLOSED_K4_COPY_VERIFIED','members':len(rows),'bytes':manifest['bytes'],
'manifest':str(out),'sha256':sha(out),'NativeOpened':False},ensure_ascii=False),flush=True)
