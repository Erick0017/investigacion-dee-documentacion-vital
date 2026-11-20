"""Root-only FS reconciliation of the exact pre-Store long-path import error.

This does not copy the runtime, load a Native package, import a life or remove
source evidence. After a separately completed copy, only the two copied import
markers move to a fresh archive in the SHORT copy. Official import0 is later,
explicit and uses the unchanged CORE R06 importer.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import sys
import time

SOURCE=Path(__file__).resolve().parents[2]
ID=re.compile(r'SDK_DEMO_[0-9A-F]{16}')
FILES=('INSTANCE.json','CONTEXTO_EJECUCION.json','PREPARACION_PAR28_SDK.json',
       'WORLD_PADRE_PAR28.json','VIDA_PADRE_PAR28.json',
       'IMPORT0_EN_CURSO.json','IMPORT0_INCOMPLETO.json')

def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):
    with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def unlinked(p):
    s=p.lstat()
    if p.is_symlink() or getattr(s,'st_file_attributes',0)&1024:raise ValueError('No linked or reparse paths')
def safe(root,relative):
    root=Path(root).resolve(strict=True);p=root/relative
    if p.is_absolute() and not p.is_relative_to(root):raise ValueError('Contained path required')
    if '..' in Path(relative).parts:raise ValueError('No parent paths')
    cursor=root;unlinked(cursor)
    for part in p.relative_to(root).parts:
        cursor/=part
        if cursor.exists() or cursor.is_symlink():unlinked(cursor)
    if not p.resolve(strict=False).is_relative_to(root):raise ValueError('Escaped runtime')
    return p
def need(value,message):
    if not value:raise ValueError(message)
def no_store(home,cfg):
    s=home/'sistema';life=cfg['lifeId']
    paths=['SDK_SERVICE.lock','SDK_PAIR.json','SDK_READY.json','IMPORTACION_DIAGNOSTICA.json']
    paths+=['sistema/estado/ACTIVO.json','sistema/estado/vidas/'+life,
            'sistema/estado/servicios_persistentes/'+life,
            'sistema/estado/servicios_locales/'+life,'sistema/estado/locks/'+life+'.lock']
    for name in paths:need(not safe(home,name).exists(),'TARGET_STATE_OR_OWNER_EXISTS:'+name)
    roots=('estado/vidas','estado/servicios_persistentes','estado/servicios_locales','estado/checkpoints')
    for name in roots:
        d=safe(s,name)
        need(not d.exists() or d.is_dir() and not any(d.iterdir()),'IMPORT_CREATED_STATE:'+name)
    return {'targetLifeExists':False,'queueExists':False,'snapshotExists':False,
            'SDK_READY':False,'ACTIVO':False,'ownerLock':False,'inspection':'Known target state roots only; no live SQL/Native imports'}

def plan(runtime,instance):
    need(ID.fullmatch(instance) is not None,'Exact diagnostic instance')
    source=SOURCE.resolve(strict=True);target=Path(runtime).resolve(strict=True)
    need(target!=source,'Separate short deployment required')
    need(len(str(target))<len(str(source)),'New operational path must be shorter')
    rel='estado_demo/instancias/'+instance;src=safe(source,rel);dst=safe(target,rel)
    cfg=read(src/'INSTANCE.json')
    need(cfg==read(dst/'INSTANCE.json'),'Literal instance identity/cursor changed during deployment')
    need(cfg['instanceId']==instance and cfg['lifeId']=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'+instance
         and cfg['runtimeVersion']=='0.1.1' and cfg['validationRevision']=='R06'
         and cfg['nativeTick']==991187 and cfg['localSequence']==cfg['completedCycles']==0
         and cfg['nextPhase']=='decision' and cfg['sequenceOffset']==56,'Unused prepared PAR28 only')
    pins={}
    for name in FILES:
        a=safe(src,name);b=safe(dst,name);need(a.is_file() and b.is_file(),'Complete copied pre-Store evidence required')
        left=sha(a);need(left==sha(b),'Copied pre-Store evidence differs:'+name)
        pins[name]={'sha256':left,'bytes':a.stat().st_size}
    failure=read(src/'IMPORT0_INCOMPLETO.json');intent=read(src/'IMPORT0_EN_CURSO.json')
    need(failure.get('error')=="ImportError('DLL load failed while importing _native: El nombre del archivo o la extensión es demasiado largo.')",
         'Only the known DLL path-length pre-Store failure may be reconciled')
    need(failure.get('lifeId')==cfg['lifeId'] and intent.get('lifeId')==cfg['lifeId'] and
         intent.get('phase')=='BEFORE_OFFICIAL_IMPORT' and intent.get('new_native_ticks')==0,
         'Exact failed-before-official-import marker required')
    states={'source':no_store(src,cfg),'target':no_store(dst,cfg)}
    freeze='configuracion/FUENTES_CORE_RUNTIME_R06_0_1_1.json'
    need(sha(safe(source,freeze))==sha(safe(target,freeze)),'Core freeze changed during deployment')
    for row in read(target/freeze)['files']:
        p=safe(target,row['file']);need(p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],'R06 source mismatch:'+row['file'])
    for name in ('configuracion/VENTANA_R06.json','dependencias/SDK_SOURCES.json',
                 'dependencias/PLANTILLA_SISTEMA.json','estado_demo/LEDGER_SDK_R06.json',
                 'estado_demo/prefijos/PAR28_COMPLETO/EXPORTACION_SERVICIO.json'):
        need(sha(safe(source,name))==sha(safe(target,name)),'Copied operational anchor changed:'+name)
    ledger=read(target/'estado_demo/LEDGER_SDK_R06.json')
    need(ledger['intents']=={} and cfg['lifeId'] not in ledger['worlds'],'Never reserve/admit an unimported child')
    return {'schema':'DEE.Roblox.SDK.pre_store_relocation.R06','instanceId':instance,
        'lifeId':cfg['lifeId'],'sessionId':cfg['sessionId'],'sourceRuntime':str(source),'targetRuntime':str(target),
        'home':rel,'pins':pins,'coreFreezeSha256':sha(target/freeze),'noStore':states,
        'NativeImported':False,'newNativeTicks':0,'sourceEvidenceRemoved':False,
        'status':'VERIFIED_PRE_STORE_DLL_FAILURE_NEW_SHORT_ATTEMPT_PREPARED'}

def apply(runtime,instance,*,confirm_closed=False):
    need(confirm_closed,'Root must confirm the original importer process exited; this helper does not guess PIDs')
    p=plan(runtime,instance);root=Path(runtime).resolve(strict=True);home=root/p['home']
    archive=safe(home,'despliegue/IMPORT0_DLL_PRE_STORE_R06')
    need(not archive.exists(),'Fresh archive only; never repeat an uncertain FS transaction')
    archive.mkdir(parents=True)
    (archive/'PLAN.json').write_text(json.dumps(p,sort_keys=True,indent=2)+'\n',encoding='utf8')
    for name in ('IMPORT0_EN_CURSO.json','IMPORT0_INCOMPLETO.json'):
        path=safe(home,name);need(sha(path)==p['pins'][name]['sha256'],'Marker changed before archive')
        path.rename(archive/name)
    # Source evidence remains byte-identical. Only copied technical markers moved.
    for name,row in p['pins'].items():need(sha(Path(p['sourceRuntime'])/p['home']/name)==row['sha256'],'Source changed during reconciliation')
    no_store(home,read(home/'INSTANCE.json'))
    value={**p,'status':'READY_NEW_OFFICIAL_IMPORT0_ATTEMPT_IN_SHORT_DEPLOYMENT',
           'rootConfirmedOriginalImporterClosed':True,'archivedTechnicalMarkers':str(archive.relative_to(root)),
           'newImportIdRequired':True,'samePreparedInstanceAndSession':True,
           'originalFailedAttemptPreserved':True,'createdUtcEpoch':time.time()}
    output=archive/'RESULTADO.json';output.write_text(json.dumps(value,sort_keys=True,indent=2)+'\n',encoding='utf8')
    return {'status':value['status'],'proof':str(output),'sha256':sha(output),'NativeOpened':False,
            'instanceId':instance,'contextSha256':p['pins']['CONTEXTO_EJECUCION.json']['sha256']}

if __name__=='__main__':
    q=argparse.ArgumentParser(description=__doc__);q.add_argument('--runtime',type=Path,required=True)
    q.add_argument('--instance',required=True);q.add_argument('--execute-fs-only',action='store_true')
    q.add_argument('--confirm-source-importer-closed',action='store_true');a=q.parse_args()
    value=apply(a.runtime,a.instance,confirm_closed=a.confirm_source_importer_closed) if a.execute_fs_only else plan(a.runtime,a.instance)
    print(json.dumps(value,ensure_ascii=False,sort_keys=True))
