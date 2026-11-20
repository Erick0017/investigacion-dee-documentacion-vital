"""Root-only closed post-K4 FS installation; no Native import or pulse.

Adds a pinned PI10 plugin and a separately named host entrypoint. CORE26,
the three SDK Native source files and all Native state bytes stay unchanged.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'r06'))
from sdk_common import RUNTIME,atomic,budget,canonical,closed_native,digest,instance_home,read,safe,sha,validate_pair

HERE=Path(__file__).resolve().parent
FILES=('sdk_capabilities_R06.py','sdk_native_functions_R06.py')
SCOPE_NAME='SDK_CAPABILITIES_SCOPE_R06.json'

def need(value,message):
    if not value:raise ValueError(message)
def plan(instance_id,*,minutes=180,max_events=12):
    need(type(minutes) is int and 45<=minutes<=360 and type(max_events) is int and 1<=max_events<=12,'Finite capabilities session')
    home,cfg=instance_home(instance_id);system=home/'sistema';window=budget()
    need(not(home/'SDK_SERVICE.lock').exists() and not(home/'SDK_CAPABILITIES_SERVICE.lock').exists(),'All SDK services must be closed')
    need(not(system/'capacidades'/SCOPE_NAME).exists(),'First installation only; never reset event history')
    need(cfg['completedCycles']>=2 and cfg['nextPhase']=='decision','Ordinary two-cycle K4 core precedes capabilities')
    proof=closed_native(home,cfg);pair=validate_pair(home,cfg,proof)
    ledger=read(RUNTIME/'estado_demo/LEDGER_SDK_R06.json');world=ledger['worlds'][cfg['lifeId']]
    need(not ledger['intents'] and world['reserved']==0 and world['cycles']==cfg['completedCycles'],'No pending episode or Native intent')
    candidates=[]
    folder=home/'restoration_proofs'
    if folder.exists():
        for p in folder.glob('*.json'):
            row=read(p)
            if (row.get('status')=='RECORDED' and row.get('serverCursorMatched') is True and
                    row['serverComparison']['passed'] is True and row['body']['sessionId']==cfg['sessionId']):
                state=row['body']['proof']['actual']['state']
                if state['completedOpportunities']>=1 and state['nativeTick']<proof['nativeTick']:
                    candidates.append({'file':p.relative_to(home).as_posix(),'sha256':sha(p)})
    need(candidates,'Persisted actual K4 restoration proof and later actual usage required')
    native_scope=read(system/'capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
    need(native_scope['life_id']==cfg['lifeId'] and native_scope['max_cycles']==3 and native_scope['max_raw_support']==10000,'Core scope remains unchanged')
    for name,expected in native_scope['sources_sha256'].items():need(sha(system/'capacidades'/name)==expected,'Core Native source changed')
    now=int(time.time());hard=min(now+minutes*60,window['hardFinishUtcEpoch']);last=min(hard-1800,window['lastNewUtcEpoch'])
    need(last>now+300,'Finite prospective capability admission and closing margin')
    registry=system/'capacidades/PI10_PLUGINS_R01.json';old=read(registry)
    need(old['schema']=='DEE.PI10.fixed_plugins.v1' and 'sdk_capabilities_R06' not in old['plugins'],'New explicit plugin only')
    for name,expected in old['files_sha256'].items():need(sha(system/'capacidades'/name)==expected,'Existing PI10 source changed')
    corefreeze=RUNTIME/'configuracion/FUENTES_CORE_RUNTIME_R06_0_1_1.json'
    for row in read(corefreeze)['files']:need(sha(RUNTIME/row['file'])==row['sha256'],'Frozen core host changed')
    scope={'schema':'DEE.Roblox.SDK.capabilities.scope.R06','sealed':True,
        'instanceId':cfg['instanceId'],'lifeId':cfg['lifeId'],'allowedLifeIds':[cfg['lifeId']],'sessionId':cfg['sessionId'],
        'startUtcEpoch':now,'lastNewUtcEpoch':last,'native_cutoff_utc_epoch':hard,
        'maxEvents':max_events,'max_ticks_per_cycle':4096,'max_total_ticks':40000,'max_raw_support':10000,
        'monitor_tick_block':16,'ownerMemoryBytes':536870912,'threads':1,
        'sourceHashes':{name:sha(HERE/name) for name in FILES},
        'coreFreezeSha256':sha(corefreeze),'preCapPairSha256':sha(home/'SDK_PAIR.json'),
        'preCapSnapshotSha256':pair['snapshotSha256'],'preCapNative':proof,'k4Proofs':candidates,
        'oldRegistrySha256':sha(registry),'originalNativeSources':native_scope['sources_sha256'],
        'assistedOperatorRequest':True,'worldBinding':'PRE_CAP_SDK_PAIR_NOT_CURRENT_AFTER_NATIVE_ADVANCE'}
    return {'home':str(home),'cfg':cfg,'scope':scope,'registry':old,'registrySha256':sha(registry),'nativeBefore':proof,
            'ledgerBeforeSha256':sha(RUNTIME/'estado_demo/LEDGER_SDK_R06.json'),
            'scopeCanonicalSha256':digest(scope),'NativeOpened':False}

def install(instance_id,*,minutes=180,max_events=12,execute_fs_only=False):
    need(execute_fs_only,'Explicit Root-only FS installation')
    value=plan(instance_id,minutes=minutes,max_events=max_events);home=Path(value['home']);system=home/'sistema'
    out=home/'CAPABILITIES_INSTALL_R06';need(not out.exists(),'Fresh installation transaction only')
    out.mkdir();atomic(out/'PLAN.json',value,new=True)
    scope=value['scope'];paths={}
    for name in FILES:
        p=safe(system,'capacidades/'+name)
        need(not p.exists(),'No capability source overwrite');p.write_bytes((HERE/name).read_bytes());paths[name]=sha(p)
    scopepath=system/'capacidades'/SCOPE_NAME;atomic(scopepath,scope,new=True)
    entry=system/'app/servicio_capabilities_R06.py';need(not entry.exists(),'No host entry overwrite')
    entry.write_bytes((HERE/'servicio_capabilities_R06.py').read_bytes())
    host=read(system/'app/HOST_INTEGRAL_V3.json')
    host['native_cutoff_utc_epoch']=scope['native_cutoff_utc_epoch']
    host['host_sources_sha256']={'servicio_capabilities_R06.py':sha(entry),
                               'cache_fuentes_C02.py':sha(system/'app/cache_fuentes_C02.py')}
    atomic(system/'app/HOST_SDK_CAPABILITIES_R06.json',host,new=True)
    registry=system/'capacidades/PI10_PLUGINS_R01.json'
    need(sha(registry)==value['registrySha256'],'Registry changed before publication')
    (out/'PI10_PLUGINS_ANTES.json').write_bytes(registry.read_bytes())
    extended=dict(value['registry']);extended['plugins']=list(extended['plugins'])+['sdk_capabilities_R06']
    extended['files_sha256']=dict(extended['files_sha256'],**paths,**{SCOPE_NAME:sha(scopepath)})
    atomic(registry,extended)
    after=closed_native(home,value['cfg']);need(after==value['nativeBefore'],'FS installation changed Native state')
    need(sha(RUNTIME/'estado_demo/LEDGER_SDK_R06.json')==value['ledgerBeforeSha256'],'FS installation changed Native ledger')
    descriptor={'schema':'DEE.Roblox.SDK.PRE_CAP_DESCRIPTOR.R06','pairSha256':scope['preCapPairSha256'],
        'checkpointSha256':scope['preCapSnapshotSha256'],'nativeTick':after['nativeTick'],
        'scope':'Historical normal SDK_PAIR before capability inputs; not a current World pair after Native advances.'}
    atomic(home/'SDK_PAIR_PRE_CAP_R06.json',read(home/'SDK_PAIR.json'),new=True)
    atomic(home/'CAPABILITIES_STATE_R06.json',{'instanceId':instance_id,'sessionId':scope['sessionId'],
        'nativeTick':after['nativeTick'],'capabilitySequence':0,'status':'INSTALLED_CLOSED_NO_NATIVE',
        'preCapDescriptor':descriptor},new=True)
    result={'status':'INSTALLED_CLOSED_NO_NATIVE','NativeOpened':False,'newNativeTicks':0,
        'nativeBefore':value['nativeBefore'],'nativeAfter':after,'coreNativeSourcesUnchanged':True,
        'scopeSha256':sha(scopepath),'registryAfterSha256':sha(registry),'preCapDescriptor':descriptor}
    atomic(out/'RESULTADO.json',result,new=True);return result

if __name__=='__main__':
    q=argparse.ArgumentParser(description=__doc__);q.add_argument('--instance',required=True)
    q.add_argument('--minutes',type=int,default=180);q.add_argument('--max-events',type=int,default=12)
    q.add_argument('--execute-fs-only',action='store_true');a=q.parse_args()
    result=install(a.instance,minutes=a.minutes,max_events=a.max_events,execute_fs_only=True) if a.execute_fs_only else plan(a.instance,minutes=a.minutes,max_events=a.max_events)
    print(canonical(result))
