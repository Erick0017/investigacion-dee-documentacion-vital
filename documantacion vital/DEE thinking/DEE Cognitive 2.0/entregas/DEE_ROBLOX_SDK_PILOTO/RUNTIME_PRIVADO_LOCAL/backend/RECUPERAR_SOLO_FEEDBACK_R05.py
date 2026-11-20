"""ONE original feedback after proven host rejection before queue admission.

Technical reconciliation, not autonomous recovery. No BEGIN/Q1/Q2/world
actions, no payload repair, no new epoch, no lease renewal or state rollback.
Import/help/plan are stdlib only. Actual execution is explicit Root-only.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import sqlite3
import sys
import time
sys.path.insert(0,str(Path(__file__).resolve().parent))
from sdk_common import (RUNTIME, atomic, canonical, closed_native, digest,
                        instance_home, native_payload, operational_window, read, sha)

RAM_ERROR='HOST_FREE_RAM_BELOW_1GiB_BEFORE_QUEUE_ADMISSION'
ACTOR_KEY='DEE.Cognitive.Roblox.SDK.native.0.1.0'

def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m

def require(condition,message):
    if not condition:raise ValueError(message)

def plan(instance_id, operation_id=None):
    home,cfg=instance_home(instance_id)
    candidates=[]
    for p in (home/'http_operations').glob('*.json'):
        row=read(p)
        if row.get('kind')=='feedback' and (operation_id is None or row['operationId']==operation_id):candidates.append((p,row))
    require(len(candidates)==1,'EXACT_ONE_ORIGINAL_FEEDBACK_REQUIRED')
    rowpath,row=candidates[0];op=row['operationId']
    require(row['status']=='UNCERTAIN' and row.get('error',{}).get('message')==RAM_ERROR,'EXACT_HOST_PRE_QUEUE_REJECTION_ONLY')
    require(row['requestSha256']==digest({'kind':'feedback','body':row['body']}),'ORIGINAL_DURABLE_FEEDBACK_DIGEST')
    require(cfg['nativeTick']==991565 and cfg['localSequence']==2 and cfg['completedCycles']==0 and cfg['nextPhase']=='feedback','EXACT_PARTIAL_FIRST_EPISODE_CURSOR')
    payload,local,oid=native_payload('feedback',row['body']['payload'],cfg['sequenceOffset'])
    require(payload==row['nativePayload'] and local==2 and payload['seq']==58,'ORIGINAL_PAYLOAD_UNCHANGED_NOT_REPAIRED')
    context=row['nativeContext']
    require(context=={'session_id':cfg['sessionId'],'sequence':58,'observation_id':oid,'operation_id':op,'mode':'LIVE_NATIVE'},'EXACT_ORIGINAL_NATIVE_CONTEXT')
    window=operational_window(cfg)
    proof=closed_native(home,cfg);require(proof['nativeTick']==991565 and proof['dimension']==67,'CLOSED_EXISTING_NATIVE_T991565')
    system=home/'sistema';life=cfg['lifeId'];card=read(system/'estado/vidas'/life/'VIDA.json')
    require(not(system/'estado/locks'/(card['world_id']+'.lock')).exists(),'EXISTING_NATIVE_WORLD_WRITER_LOCK')
    db=system/'estado/servicios_persistentes'/life/'cola.sqlite3'
    con=sqlite3.connect(db.resolve().as_uri()+'?mode=ro&immutable=1',uri=True)
    try:require(con.execute('SELECT COUNT(*) FROM requests WHERE id=?',(op,)).fetchone()[0]==0,'ORIGINAL_FEEDBACK_ALREADY_QUEUED_NO_REPLAY')
    finally:con.close()
    require(not(home/'ensayos'/(op+'.json')).exists(),'NATIVE_FEEDBACK_RECEIPT_ALREADY_EXISTS')
    contextfile=read(home/'CONTEXTO_EJECUCION.json')
    observerpin=next(x for x in contextfile['tool_sources'] if Path(x['file']).name=='observador_pasivo.py')
    observerpath=RUNTIME/observerpin['file'];require(sha(observerpath)==observerpin['sha256'],'OFFICIAL_PASSIVE_OBSERVER_PIN')
    observer=load(observerpath,'_technical_feedback_passive_observer')
    snapshot=system/card['snapshot'];view=observer.snapshot_view(snapshot)
    m=json.loads(view['metadata'][ACTOR_KEY]);pending=m['pending']
    require(m['phase']=='AWAIT_WORLD_CONSEQUENCE' and m['uncertain'] is False and m['cycles']==0 and m['initial_tick']==991187,'EXACT_NATIVE_PENDING_ORIGINAL_EPISODE')
    require(m['session_id']==cfg['sessionId'] and pending['action_id']==payload['actionId'] and pending['route_observation']==payload['lastObservation'],'ACTUAL_Q2_OBSERVATION_ACTION_AND_SESSION')
    require(pending['start_tick']==991187 and pending['q2_action']=='EXIT_1','ONLY_OBSERVED_ORIGINAL_Q2_NO_NEW_ROUTE')
    acks=read(home/'ACTION_ACKS.json');q1=pending['context']['operation_id'];q2=payload['actionId']
    for action in(q1,q2):
        ack=acks[action]
        require(ack['actionId']==action and ack['sessionId']==cfg['sessionId'] and ack['ack']['actionId']==action and
                ack['ack']['operationId']==action and ack['ack']['executionStatus']=='EXECUTED' and ack['ack']['technicalControl'] is False,'REAL_CORRELATED_ACTION_ACK_REQUIRED')
    result=acks[q2]['ack']['result']
    require(payload['permissionSpent']==acks[q1]['ack']['result']['permissionSpent']+result['permissionSpent'],'ACTUAL_QUERY_AND_TOLL_COST_NOT_RECOMPUTED')
    require(all(payload[k]==result[k] for k in('collision','resourceCollected','resourceDelivered','materialConsequence')),'ACTUAL_BODY_CONSEQUENCE_LITERAL')
    ledgerpath=RUNTIME/'estado_demo/LEDGER_SDK.json';ledger=read(ledgerpath);world=ledger['worlds'][life]
    require(not ledger['intents'] and world['consumed']==378 and world['reserved']==3718 and world['cycles']==0,'ORIGINAL_EPISODE_RESERVATION_AND_NO_INTENT')
    journals=[json.loads(x) for x in(home/'ENSAYOS.jsonl').read_text('utf8').splitlines() if x.strip()]
    closed=[x for x in journals if x.get('kind')=='OWNER_CLOSED']
    require(closed and closed[-1]['exit_code']==0 and closed[-1]['final_status']['running'] is False,'OFFICIAL_OWNER_CLOSED_BEFORE_REOPEN')
    require(not any(x.get('kind')=='MATERIAL_REQUEST' and x.get('id')==op for x in journals),'NO_PRIOR_FEEDBACK_MATERIAL_RECORD')
    sourcepin=read(RUNTIME/'dependencias/SDK_SOURCES.json')
    require(all(sha(system/'capacidades'/name)==expected for name,expected in sourcepin['nativeSources'].items()),'UNCHANGED_NATIVE_ACTOR_READER_CODE')
    return {'schema':'DEE.Roblox.SDK.RECONCILIACION_TECNICA_FB.R05','instanceId':instance_id,'lifeId':life,'sessionId':cfg['sessionId'],
        'operationId':op,'nativePayload':payload,'nativeContext':context,'httpRowSha256':sha(rowpath),'httpRow':str(rowpath.relative_to(home)),
        'nativeBefore':proof,'ledgerBeforeSha256':sha(ledgerpath),'acksSha256':sha(home/'ACTION_ACKS.json'),
        'existingLease':cfg['operationalLease'],'sourcePins':sourcepin['nativeSources'],
        'noQ1OrQ2Allowed':True,'newEpisode':False,'originalHttpUncertainPreserved':True},home,cfg,window

def execute(instance_id, operation_id=None, *, output=None):
    value,home,cfg,window=plan(instance_id,operation_id)
    require(output is not None,'EXPLICIT_FRESH_OUTPUT')
    out=Path(output).resolve()
    require(out.is_relative_to(home) and not out.exists(),'FRESH_OUTPUT_INSIDE_THIS_INSTANCE')
    out.mkdir(parents=True);atomic(out/'PLAN.json',value,new=True)
    memory=load(Path(__file__).with_name('native_factory.py'),'_technical_feedback_memory_guard')
    require(memory.free_memory()>=3758096384,'HOST_FREE_RAM_BELOW_3_5GiB_NO_OWNER')
    owner_module=load(Path(__file__).with_name('sdk_owner.py'),'_technical_feedback_official_owner')
    adapter_module=load(Path(__file__).with_name('native_adapter.py'),'_technical_feedback_actual_adapter')
    result={'schema':value['schema'],'status':'PRESERVED_NOT_COMPLETED','originalOperationId':value['operationId'],
            'noNewEpisode':True,'Q1Q2replayed':False,'administrativeAssistance':True,'originalHttpRowPreserved':True}
    try:
        with owner_module.configured_owner(RUNTIME/'dependencias/producto',home,RUNTIME/'estado_demo/LEDGER_SDK.json',
                tag='SDK_TECH_FB_R05',cutoff_epoch=window['hardFinishUtcEpoch'],continuous=True) as owner:
            adapter=adapter_module.create_adapter({'owner':owner})
            require(memory.free_memory()>=1073741824,RAM_ERROR)
            require(sha(home/value['httpRow'])==value['httpRowSha256'] and sha(home/'ACTION_ACKS.json')==value['acksSha256'],'ORIGINAL_INPUT_CHANGED_NO_SUBMIT')
            atomic(out/'FEEDBACK_INTENT.json',{'operationId':value['operationId'],'context':value['nativeContext'],
                   'payload':value['nativePayload'],'notNewQ1':True},new=True)
            response=adapter.execute('feedback',value['nativePayload'],value['nativeContext'])
            require(response.get('accepted') is True and response['nativeTick']==992751,'ORIGINAL_FEEDBACK_NOT_CONFIRMED_PRESERVE')
            result.update(status='ORIGINAL_NATIVE_FEEDBACK_COMPLETED',nativeResult=response)
        result['nativeAfter']=closed_native(home,cfg);result['ownerClosed']=True
        require(result['nativeAfter']['nativeTick']==992751,'CLOSED_FINAL_T992751')
        result['status']='ONE_ORIGINAL_EPISODE_TECHNICALLY_COMPLETED_CLOSED'
        result['scope']='Native feedback completed from actual durable Body consequence. Agent/World remains partial unless separately completed by its original API. No normal SDK_PAIR or K4 claim.'
    except BaseException as error:
        result['error']=repr(error);result['noAutomaticRetry']=True
        atomic(out/'RESULTADO.json',result,new=True);raise
    atomic(out/'RESULTADO.json',result,new=True)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--instance',required=True);p.add_argument('--operation-id')
    p.add_argument('--output');p.add_argument('--execute-root-only',action='store_true');a=p.parse_args()
    print(canonical(execute(a.instance,a.operation_id,output=a.output) if a.execute_root_only else plan(a.instance,a.operation_id)[0]))
