"""Root-only FS repair of the proven zero-event CAP access-guard boot failure.

No Native imports, no access_guard changes, no snapshot/queue/state rollback.
Original code/scope/registry/failed host state remain in an exact archive. The
new host state is a separate file linked to that failed attempt.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import os
import sys

HERE=Path(__file__).resolve().parent
FILES=('sdk_capabilities_R06.py','sdk_native_functions_R06.py')

def need(value,message):
    if not value:raise ValueError(message)
def common(runtime):
    path=runtime/'backend/r06/sdk_common.py'
    s=importlib.util.spec_from_file_location('_cap_r03_closed_fs',path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def plan(runtime,instance,failure_stderr):
    runtime=Path(runtime).resolve(strict=True);c=common(runtime);home,cfg=c.instance_home(instance,runtime)
    need(cfg['runtimeVersion']=='0.1.1' and cfg['validationRevision']=='R06','Host-only actual SDK profile guard')
    need(not(home/'SDK_SERVICE.lock').exists() and not(home/'SDK_CAPABILITIES_SERVICE.lock').exists(),'Both HTTP/Native services must have exited')
    statepath=home/'CAPABILITIES_STATE_R06.json';oldstate=c.read(statepath)
    need(oldstate['capabilitySequence']==0 and oldstate['status']=='FAILED_PRESERVED' and oldstate.get('lastError') is not None,
         'Exact failed boot before the first event required')
    need(not(home/'CAPABILITIES_STATE_R06_R03.json').exists(),'New R03 host state only; no repeated repair')
    system=home/'sistema';scopepath=system/'capacidades/SDK_CAPABILITIES_SCOPE_R06.json';scope=c.read(scopepath)
    need(scope['lifeId']==cfg['lifeId'] and scope['allowedLifeIds']==[cfg['lifeId']] and
         scope['instanceId']==instance and scope['sessionId']==cfg['sessionId'],'Exact same existing identity/session')
    need(scope.get('participantIdentityRevision') is None,'Only original prepared R02 scope may be repaired')
    need(oldstate['nativeTick']==scope['preCapNative']['nativeTick'] and cfg['nativeTick']==oldstate['nativeTick'],
         'No post-K4 physical event may have occurred')
    ledgerpath=runtime/'estado_demo/LEDGER_SDK_R06.json';ledger=c.read(ledgerpath);world=ledger['worlds'][cfg['lifeId']]
    need(ledger['intents']=={} and world['reserved']==0 and world.get('capability_events',0)==0,
         'No capability event/reservation/intent may be cleared')
    ops=home/'capability_operations'
    if ops.exists():
        for p in ops.glob('*.json'):
            row=c.read(p)
            need(row['kind']=='CLOSE' and row['status']=='COMPLETED' and row.get('nativeAdmissionStarted') is False,
                 'Only known zero-material administrative close records may exist')
    nativefolder=system/'estado/servicios_locales'/cfg['lifeId']/'DEE_SDK_ASSISTED_CAPABILITIES_R06'
    need(not nativefolder.exists() or not any(nativefolder.iterdir()),'No Native capability artifact/event allowed')
    before=c.closed_native(home,cfg)
    need(before==scope['preCapNative'],'Exact pre-CAP Native proof required; never repair after a pulse')
    registry=system/'capacidades/PI10_PLUGINS_R01.json';reg=c.read(registry)
    need(reg['plugins'].count('sdk_capabilities_R06')==1,'Exactly one installed capabilities plugin')
    for name,expected in reg['files_sha256'].items():
        need(Path(name).name==name and c.sha(system/'capacidades'/name)==expected,'Existing declared source changed:'+name)
    for name,expected in scope['sourceHashes'].items():need(c.sha(system/'capacidades'/name)==expected,'Installed R02 participant changed')
    failure=c.safe(home,failure_stderr,exists=True);data=failure.read_text('utf-8-sig')
    need('INSTANCE.json' in data and ('access_guard' in data or 'AccessGuard' in data or 'ACCESS_GUARD' in data),
         'Exact declared-file access failure evidence required')
    paths={'scope':scopepath,'registry':registry,'failedState':statepath,'failureStderr':failure,
           **{name:system/'capacidades'/name for name in FILES}}
    pins={key:{'path':str(p.relative_to(runtime)).replace('\\','/'),'bytes':p.stat().st_size,'sha256':c.sha(p)} for key,p in paths.items()}
    revised=dict(scope)
    revised.update(sourceHashes={name:c.sha(HERE/name) for name in FILES},
                   participantIdentityRevision='R03_SCOPE_NATIVE_ONLY',
                   hostProfile={'runtimeVersion':'0.1.1','validationRevision':'R06'})
    return {'schema':'DEE.Roblox.SDK.capability_boot_repair.R03','home':str(home.relative_to(runtime)),
        'instanceId':instance,'sessionId':cfg['sessionId'],'nativeBefore':before,'ledgerSha256':c.sha(ledgerpath),
        'pins':pins,'oldScope':scope,'newScope':revised,'oldRegistry':reg,'failedState':oldstate,
        'participantContentReadsAfterRepair':'Only declared sibling Scope/source files plus Native metadata; no INSTANCE content/stat',
        'accessGuardModified':False,'newNativeTicks':0,'NativeOpened':False}

def apply(runtime,instance,failure_stderr):
    runtime=Path(runtime).resolve(strict=True);c=common(runtime);p=plan(runtime,instance,failure_stderr)
    home=runtime/p['home'];out=home/'CAPABILITIES_REPAIR_ACCESS_R03'
    need(not out.exists(),'Fresh repair only; partial transactions are preserved')
    out.mkdir();c.atomic(out/'PLAN.json',p,new=True)
    try:
        for key,row in p['pins'].items():
            source=c.safe(runtime,row['path'],exists=True)
            need(c.sha(source)==row['sha256'],'Source changed before repair')
            (out/(key+'.before')).write_bytes(source.read_bytes())
        need(c.closed_native(home,c.instance_home(instance,runtime)[1])==p['nativeBefore'],'Native changed before FS repair')
        system=home/'sistema'
        for name in FILES:
            target=system/'capacidades'/name;data=(HERE/name).read_bytes()
            need(c.sha(HERE/name)==p['newScope']['sourceHashes'][name],'New source changed')
            # Prepared bytes + same bounded atomic rename, not any Native call.
            temporary=target.with_name(target.name+'.R03_WRITING')
            with temporary.open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
            os.replace(temporary,target)
        scopepath=system/'capacidades/SDK_CAPABILITIES_SCOPE_R06.json';c.atomic(scopepath,p['newScope'])
        reg=dict(p['oldRegistry']);reg['files_sha256']=dict(reg['files_sha256'])
        reg['files_sha256'].update(p['newScope']['sourceHashes'])
        reg['files_sha256'][scopepath.name]=c.sha(scopepath)
        c.atomic(system/'capacidades/PI10_PLUGINS_R01.json',reg)
        old=p['failedState']
        fresh={key:old[key] for key in('instanceId','sessionId','nativeTick','capabilitySequence','preCapDescriptor')}
        fresh.update(status='REPAIRED_CLOSED_ZERO_EVENTS_R03',closedNativeDescriptor=p['nativeBefore'],
                     previousFailedBoot={'file':'CAPABILITIES_STATE_R06.json','sha256':p['pins']['failedState']['sha256'],
                                         'errorPreserved':old['lastError']})
        c.atomic(home/'CAPABILITIES_STATE_R06_R03.json',fresh,new=True)
        after=c.closed_native(home,c.instance_home(instance,runtime)[1])
        need(after==p['nativeBefore'],'FS repair changed Native state')
        need(c.sha(runtime/'estado_demo/LEDGER_SDK_R06.json')==p['ledgerSha256'],'Repair changed ledger or intents')
        need(c.sha(home/'CAPABILITIES_STATE_R06.json')==p['pins']['failedState']['sha256'],'Old failure flags changed')
        result={'status':'REPAIRED_ZERO_EVENT_FS_ONLY','newNativeTicks':0,'nativeBefore':p['nativeBefore'],
                'nativeAfter':after,'ledgerUnchanged':True,'oldFailurePreserved':True,'accessGuardUnchanged':True,
                'registrySha256':c.sha(system/'capacidades/PI10_PLUGINS_R01.json'),'scopeSha256':c.sha(scopepath),
                'newHostState':'CAPABILITIES_STATE_R06_R03.json','NativeOpened':False}
        c.atomic(out/'RESULTADO.json',result,new=True);return result
    except BaseException as error:
        c.atomic(out/'INCOMPLETE_PRESERVED.json',{'error':repr(error),'automaticRetry':False,'NativeRollback':False},new=True)
        raise

if __name__=='__main__':
    q=argparse.ArgumentParser(description=__doc__);q.add_argument('--runtime',type=Path,required=True)
    q.add_argument('--instance',required=True);q.add_argument('--failure-stderr',required=True)
    q.add_argument('--execute-fs-only',action='store_true');a=q.parse_args()
    value=apply(a.runtime,a.instance,a.failure_stderr) if a.execute_fs_only else plan(a.runtime,a.instance,a.failure_stderr)
    print(json.dumps(value,ensure_ascii=False,sort_keys=True))
