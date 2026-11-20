"""Root-only FOCAL_R06 FS preparation; import0 is separate and explicit."""
from pathlib import Path
import argparse,importlib.util,sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sdk_common import RUNTIME,atomic,budget,canonical,read,sha,verify_focal_sources,instance_home
from serial_guard import REGISTRY,other_services_closed
HERE=Path(__file__).resolve().parent

def load(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def profile():
    frozen=read(HERE/'PERFIL_FOCAL_CONGELADO.json')
    for name,pin in frozen['nativeSources'].items():
        if sha(HERE/name)!=pin:raise RuntimeError('FOCAL_NATIVE_SOURCE_CHANGED')
    return frozen

def check_overlay(home):
    cfg=read(home/'INSTANCE.json');ctx=read(home/'CONTEXTO_EJECUCION.json')
    if (cfg.get('profile')!='FOCAL' or cfg.get('validationRevision')!='FOCAL_R06'
            or cfg.get('focalCondition') not in ('OSCILANTE','CONTROL')):
        raise ValueError('EXACT_FOCAL_R06_PROFILE')
    if any((home/n).exists() for n in ('FOCAL_OVERLAY_IN_PROGRESS.json','FOCAL_OVERLAY_INCOMPLETE.json')):
        raise RuntimeError('PARTIAL_OVERLAY_PRESERVED_NO_RETRY')
    window=budget()
    pin=ctx['focalOverlay']
    if (pin['focalWindowSha256']!=sha(RUNTIME/'configuracion/VENTANA_FOCAL_R06.json')
            or pin['sourceManifestSha256']!=sha(HERE/'PERFIL_FOCAL_CONGELADO.json')
            or pin['hostFreezeSha256']!=verify_focal_sources()):
        raise RuntimeError('FROZEN_FOCAL_CONTEXT_CHANGED')
    for name,expected in pin['nativeSources'].items():
        if sha(home/'sistema/capacidades'/name)!=expected:raise RuntimeError('FOCAL_INSTANCE_SOURCE_CHANGED')
    return cfg,window

def crear(instance_id,session_id,condition,*,execute=False):
    if condition not in ('OSCILANTE','CONTROL'):raise ValueError('CLOSED_FOCAL_CONDITION')
    window=budget();frozen=profile();other_services_closed()
    fs=load(HERE/'preparacion/preparar_instancia_par28_sdk.py','_focal_r06_base_fs')
    planned=fs.plan(RUNTIME,instance_id,session_id)
    if not execute:return {'executed':False,'profile':'FOCAL','condition':condition,'maxCycles':6,'basePlan':planned,'newNativeTicks':0}
    regpath=RUNTIME/REGISTRY
    registry=read(regpath) if regpath.exists() else {'schema':'DEE.SDK.FocalParticipants.R06','participants':[],
        'focalWindowSha256':sha(RUNTIME/'configuracion/VENTANA_FOCAL_R06.json'),'hostFreezeSha256':verify_focal_sources()}
    if registry['focalWindowSha256']!=sha(RUNTIME/'configuracion/VENTANA_FOCAL_R06.json'):
        raise RuntimeError('PARTICIPANT_WINDOW_CHANGED')
    expected=['OSCILANTE','CONTROL']
    rows=registry['participants']
    if len(rows)>=2 or condition!=expected[len(rows)] or any(r['instanceId']==instance_id for r in rows):
        raise RuntimeError('TWO_FRESH_IDS_FIXED_ORDER_NO_REUSE')
    entry={'instanceId':instance_id,'condition':condition,'status':'FS_PREPARATION_INTENT'}
    rows.append(entry);atomic(regpath,registry,new=not regpath.exists())
    try:
        prepared=fs.prepare(planned,RUNTIME,execute_root_only=True)
        home=RUNTIME/prepared['home'];cfgpath=home/'INSTANCE.json';ctxpath=home/'CONTEXTO_EJECUCION.json'
        marker=home/'FOCAL_OVERLAY_IN_PROGRESS.json';atomic(marker,{'condition':condition,'newNativeTicks':0},new=True)
        cfg=read(cfgpath);ctx=read(ctxpath);archive=home/'FOCAL_BASE_PREPARATION';archive.mkdir()
        for name in ('INSTANCE.json','CONTEXTO_EJECUCION.json','PREPARACION_PAR28_SDK.json'):
            (archive/name).write_bytes((home/name).read_bytes())
        for name,pin in frozen['nativeSources'].items():
            target=home/'sistema/capacidades'/name;(archive/name).write_bytes(target.read_bytes())
            target.write_bytes((HERE/name).read_bytes())
            if sha(target)!=pin:raise RuntimeError('FOCAL_NATIVE_COPY_CHANGED')
        scopepath=home/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json';scope=read(scopepath)
        lease=scope['operational_lease'];lease.update(startUtcEpoch=window['startUtcEpoch'],
            lastNewUtcEpoch=window['lastNewUtcEpoch'],hardFinishUtcEpoch=window['hardFinishUtcEpoch'],
            additionalCycles=6,cumulativeCycleCap=6,validationCampaignSha256=sha(RUNTIME/'configuracion/VENTANA_FOCAL_R06.json'))
        scope.update(role='focal',max_cycles=6,max_total_ticks=24576,sources_sha256=frozen['nativeSources'],
            code_scope_manifest_sha256=sha(HERE/'PERFIL_FOCAL_CONGELADO.json'),
            native_cutoff_utc_epoch=window['hardFinishUtcEpoch'],last_new_cycle_utc_epoch=window['lastNewUtcEpoch'],
            operational_lease=lease)
        atomic(scopepath,scope)
        hostpath=home/'sistema/app/HOST_INTEGRAL_V3.json';host=read(hostpath)
        host['native_cutoff_utc_epoch']=window['hardFinishUtcEpoch'];atomic(hostpath,host)
        cfg.update(profile='FOCAL',validationRevision='FOCAL_R06',focalCondition=condition,maxCycles=6,maxLocalSequence=12)
        ctx['profile']='FOCAL';ctx['focalOverlay']={'condition':condition,'nativeSources':frozen['nativeSources'],
            'sourceManifestSha256':sha(HERE/'PERFIL_FOCAL_CONGELADO.json'),
            'focalWindowSha256':sha(RUNTIME/'configuracion/VENTANA_FOCAL_R06.json'),
            'hostFreezeSha256':verify_focal_sources(),'baseContextSha256':sha(archive/'CONTEXTO_EJECUCION.json')}
        atomic(cfgpath,cfg);atomic(ctxpath,ctx)
        proof={'profile':'FOCAL','validationRevision':'FOCAL_R06','condition':condition,'instanceId':cfg['instanceId'],
            'lifeId':cfg['lifeId'],'sessionId':cfg['sessionId'],'home':str(home.relative_to(RUNTIME)),
            'contextSha256':sha(ctxpath),'NativeImported':False,'newNativeTicks':0,'maxCycles':6,'maxLocalSequence':12}
        atomic(home/'PREPARACION_FOCAL.json',proof,new=True);marker.unlink()
        entry.update(status='PREPARED_NOT_IMPORTED',contextSha256=proof['contextSha256']);atomic(regpath,registry)
        return proof
    except BaseException as error:
        entry.update(status='INCOMPLETE_PRESERVED',error=repr(error));atomic(regpath,registry)
        raise

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    c=sub.add_parser('crear');c.add_argument('--instance',required=True);c.add_argument('--session')
    c.add_argument('--condition',choices=('OSCILANTE','CONTROL'),required=True);c.add_argument('--execute-fs-only',action='store_true')
    i=sub.add_parser('importar');i.add_argument('--instance',required=True);i.add_argument('--context-sha256',required=True)
    i.add_argument('--deadline-utc-epoch',type=float,required=True);i.add_argument('--execute-root-only',action='store_true')
    a=p.parse_args()
    if a.command=='crear':result=crear(a.instance,a.session,a.condition,execute=a.execute_fs_only)
    else:
        home,_=instance_home(a.instance);cfg,w=check_overlay(home)
        importer=load(HERE/'preparacion/importar_instancia_sdk.py','_focal_r06_import0')
        result=importer.import0(home,RUNTIME,execute_root_only=a.execute_root_only,context_sha256=a.context_sha256,
            deadline_utc_epoch=min(a.deadline_utc_epoch,w['hardFinishUtcEpoch']),validation_campaign=True)
    print(canonical(result))
if __name__=='__main__':main()
