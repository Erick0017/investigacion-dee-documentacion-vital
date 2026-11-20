"""Closed-only focal evidence export and portable descriptive recalculation.

No Native/DEE/SQLite/Studio imports. Source paths are provenance only in the
export; recalculate() opens exclusively manifest archive paths in extraction.
Native snapshots, databases and credentials are never selected for copying.
"""
from pathlib import Path,PurePosixPath
import argparse
import hashlib
import json
import os
import re
import sys

SCHEMA='DEE.Roblox.SDK.closed_focal_evidence.R06'
SOURCE_TICK=991187
LIMIT=8*1024*1024
ID=re.compile(r'SDK_DEMO_[0-9A-F]{16}')
OP=re.compile(r'[A-Za-z0-9_-]{1,90}')
BAD_STATES={'PENDING','PENDING_RESOURCE','RUNNING','UNCERTAIN'}

def need(value,message):
    if not value:raise ValueError(message)
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(data):return hashlib.sha256(data).hexdigest()
def no_link(p):
    s=p.lstat()
    need(not p.is_symlink() and not(getattr(s,'st_file_attributes',0)&1024),'NO_LINK_OR_REPARSE:'+str(p))
def root_path(path):
    p=Path(path).absolute()
    for q in reversed((p,*p.parents)):
        if os.path.lexists(q):no_link(q)
    return p.resolve(strict=True)
def contained(root,name,exists=True):
    need(isinstance(name,str) and name and '\\' not in name and ':' not in name,'SAFE_ARCHIVE_PATH')
    rel=PurePosixPath(name);need(not rel.is_absolute() and all(x not in('','.','..') for x in name.split('/')),'SAFE_ARCHIVE_PATH')
    root=root_path(root);p=root.joinpath(*rel.parts);cursor=root;no_link(cursor)
    for part in rel.parts:
        cursor/=part
        if os.path.lexists(cursor):no_link(cursor)
    need(p.resolve(strict=exists).is_relative_to(root),'PATH_ESCAPED')
    return p
def primary_source(worker, name):
    """Resolve one relative Unix/Windows locator within the current worker.

    Absolute, drive-relative, drive and UNC locators are deliberately refused.
    No linked/reparse path, traversal or alternate source fallback is allowed.
    """
    need(isinstance(name, str) and name and chr(0) not in name,
         'PRIMARY_RELATIVE_PATH_REQUIRED')
    need(':' not in name and not name.startswith(('/', '\\')),
         'PRIMARY_RELATIVE_PATH_ONLY_NO_DRIVE_OR_UNC')
    parts = re.split(r'[\\/]', name)
    need(all(part not in ('', '.', '..') for part in parts),
         'SAFE_PRIMARY_PATH_COMPONENTS')
    return contained(worker, '/'.join(parts))

def raw(p):
    p=Path(p);no_link(p);a=p.stat();need(p.is_file() and a.st_size<=LIMIT,'BOUNDED_REGULAR_FILE')
    data=p.read_bytes();b=p.stat()
    need((a.st_size,a.st_mtime_ns,a.st_ino)==(b.st_size,b.st_mtime_ns,b.st_ino),'SOURCE_CHANGED_DURING_READ')
    return data
def read(p):return json.loads(raw(p).decode('utf-8-sig'))
def lines(p):return [json.loads(x) for x in raw(p).decode('utf-8-sig').splitlines() if x.strip()]
def pin(p):
    data=raw(p);return {'source':str(Path(p).resolve()),'bytes':len(data),'sha256':digest(data)}
def destination(path,forbidden=()):
    p=Path(path).absolute();need(p.parent.is_dir(),'EXISTING_OUTPUT_PARENT_REQUIRED')
    for q in (p.parent,*p.parent.parents):no_link(q)
    p=p.resolve(strict=False);need(not os.path.lexists(p),'FRESH_OUTPUT_REQUIRED')
    for root in forbidden:
        q=Path(root).resolve(strict=True)
        need(not p.is_relative_to(q) and not q.is_relative_to(p),'OUTPUT_OVERLAPS_SOURCE')
    return p

def safe_payload(data,secrets=(),jsonl=False):
    text=data.decode('utf-8-sig')
    need(not any(s and s in text for s in secrets),'PRIVATE_TOKEN_IN_SELECTED_SOURCE')
    values=[json.loads(x) for x in text.splitlines() if x.strip()] if jsonl else [json.loads(text)]
    def visit(v):
        if isinstance(v,dict):
            for k,x in v.items():
                field=re.sub('[^a-z0-9]','',k.lower())
                need(field not in {'authorization','password','apikey','accesstoken','bearertoken','privatetoken','secret',
                                   'snapshotmetadataentries','rawcopy','clockscopy'},'PRIVATE_OR_NATIVE_BUFFER_FIELD')
                if field=='token' and isinstance(x,str):need(len(x)<24,'PRIVATE_TOKEN_FIELD')
                visit(x)
        elif isinstance(v,list):
            for x in v:visit(x)
    for v in values:visit(v)

def mapping(v):
    if isinstance(v,dict):return v
    need(v==[],'JSON_MAP_OR_EMPTY_LUA_TABLE_REQUIRED');return {}

def unique_receipts(requests):
    values={}
    for request in requests:
        need(type(request.get('id')) is int and isinstance(request.get('receipt'),dict),'EXACT_NATIVE_REQUEST_RECEIPT')
        i=request['id'];receipt=request['receipt']
        need(receipt.get('id')==i and isinstance(receipt.get('status'),str),'MATCHING_TERMINAL_RECEIPT_ID')
        status=receipt['status'];need(status=='applied' or status.startswith('rejected'),'PENDING_NATIVE_INPUT')
        if i in values:need(values[i]==request,'RECEIPT_ID_CONFLICT')
        values[i]=request
    return values

def request_applied(request,receipts):
    if not isinstance(request,dict):return False
    r=receipts.get(request.get('id'))
    return r is not None and r['receipt']['status']=='applied'

def facts(index,local):
    cfg=index['configuration'];pair=local('PRIMARIOS/SDK_PAIR.json');acks=mapping(local('PRIMARIOS/ACTION_ACKS.json'))
    snap=pair['snapshot'];state=snap['state'];world=snap['world'];ws=world['state'];law=world['availability']
    need(digest(canonical(snap).encode())==pair['snapshotSha256'],'SDK_WORLD_SNAPSHOT_DIGEST_MISMATCH')
    need(world['schema']=='DEE.Focal.World.R02' and law['schema']=='DEE.Focal.LocalAvailability.R02','EXACT_FOCAL_WORLD_LAW')
    arm={'OSCILANTE':'CONSUME_RECHARGE','CONTROL':'NONCONSUMING_CONTROL'}[cfg['focalCondition']]
    need(law['arm']==arm and len(law['ports'])==12,'FOCAL_ARM_OR_PORTS_MISMATCH')
    need({(x['station'],x['port']) for x in law['ports']}=={(s,p) for s in range(6) for p in range(2)},'EXACT_TWELVE_LOCAL_PORTS')
    operations={}
    for archive in index['operations']:
        op=local(archive);need(op['operationId'] not in operations,'DUPLICATE_OPERATION_ID');operations[op['operationId']]=op
        need(op['status'] in('COMPLETED','FAILED_KNOWN'),'UNRESOLVED_HTTP_OPERATION')
        if op['status']=='FAILED_KNOWN':need(op.get('nativeAdmissionStarted') is False,'FAILED_NOT_PROVEN_PRE_NATIVE')
    events=ws['environmentEvents'];action_events={};panels={};passages=[];replenished=[]
    for event in events:
        kind=event['kind'];data=event['data']
        if kind=='ACTION_EXECUTED':
            identifier=data['actionId'];need(identifier not in action_events,'DUPLICATE_WORLD_ACTION');action_events[identifier]=data
        elif kind=='PAID_LOCAL_PANEL':
            identifier=data['actionId'];need(identifier not in panels,'DUPLICATE_PAID_PANEL');panels[identifier]=data
        elif kind=='FOCAL_PASSAGE':passages.append(data)
        elif kind=='FOCAL_PASS_REPLENISHED':replenished.append(data)
    journal=local('PRIMARIOS/NATIVE/events.jsonl',True);pending=None;cycle=None;cycles=[];tick=SOURCE_TICK;all_receipts={};used_actions=set()
    for row in journal:
        if row.get('kind')=='PHASE_INTENT':
            need(pending is None and row['tick']==tick,'OVERLAP_OR_NATIVE_TICK_CHAIN')
            need(row['context']['session_id']==cfg['sessionId'],'NATIVE_JOURNAL_SESSION_MISMATCH');pending=row
            if row['mode']=='eci01-rbx01-decision':
                need(cycle is None,'SECOND_DECISION_BEFORE_FEEDBACK')
                cycle={'cycle':len(cycles)+1,'partition':'development' if len(cycles)<4 else 'reserve','beforeTick':tick,'phases':[],'actions':[]}
            need(cycle is not None,'PHASE_WITHOUT_DECISION')
        elif row.get('kind')=='PHASE_COMPLETED':
            need(pending is not None and pending['mode']==row['mode'],'UNMATCHED_NATIVE_COMPLETION')
            v=row['result'];opid=pending['context']['operation_id'];op=operations[opid];kind=op['kind']
            need(op['status']=='COMPLETED' and op['value']==v,'DURABLE_HTTP_NATIVE_RESULT_MISMATCH')
            need(row['tick']>=tick and v['nativeTick']==row['tick'] and v['nativeTicks']==row['tick']-tick,'NATIVE_PHASE_DOSE_MISMATCH')
            need(op['nativeContext']==pending['context'] and op['nativePayload']==pending['payload'],'EXACT_NATIVE_ADMITTED_PAYLOAD')
            phase={'kind':kind,'operationId':opid,'beforeTick':tick,'afterTick':row['tick'],'nativeTicks':v['nativeTicks'],
                   'localSequence':op['localSequence'],'nativeSequence':pending['context']['sequence']}
            need(phase['nativeSequence']==cfg['sequenceOffset']+phase['localSequence'],'LOCAL_NATIVE_OFFSET_MISMATCH')
            cycle['phases'].append(phase);tick=row['tick'];e=v.get('evidence',{})
            if kind in('decision','query_sensor'):
                ack=acks[opid]['ack'];committed=mapping(snap['actions'])[opid]
                need(ack==committed['ack'] and committed['status'] in('ACKNOWLEDGED','COMMITTED') and ack['executionStatus']=='EXECUTED' and
                     ack['technicalControl'] is False and ack['actionId']==opid==ack['operationId'] and ack['seq']==op['localSequence'],
                     'LITERAL_EXECUTED_ACTION_ACK_REQUIRED')
                result=ack['result'];event=action_events[opid]
                need(all(result[k]==event['result'][k] for k in('permissionSpent','querySpent','tollSpent')),'WORLD_ACK_COST_MISMATCH')
                need(result['permissionSpent']==result['querySpent']+result['tollSpent'],'PER_ACTION_COST_ACCOUNTING')
                action={'operationId':opid,'kind':kind,'nativeAction':v.get('action'),'nativeNull':v.get('null'),
                        'costs':{k:result[k] for k in('permissionSpent','querySpent','tollSpent')},'bodyResult':result,
                        'observation':pending['payload']['observation'],'nativeEvidence':e}
                cycle['actions'].append(action);used_actions.add(opid)
            elif kind=='feedback':
                need(v.get('accepted') is True,'FEEDBACK_NOT_ACCEPTED')
                need(mapping(snap['actions'])[pending['payload']['actionId']]['status']=='COMMITTED','LAST_ACTION_RETURN_NOT_COMMITTED')
                receipts=unique_receipts(e['requests'])
                for identifier,request in receipts.items():
                    if identifier in all_receipts:need(all_receipts[identifier]==request,'CROSS_CYCLE_RECEIPT_ID_CONFLICT')
                    all_receipts[identifier]=request
                q1=next(x for x in cycle['actions'] if x['kind']=='decision');q2=next((x for x in cycle['actions'] if x['kind']=='query_sensor'),None)
                qe=q1['nativeEvidence'];question=qe.get('question_receipt');qo=qe.get('question_observation')
                released=(request_applied(question,receipts) and isinstance(qo,dict) and
                          int(qo.get('state',0))>0 and qo.get('semantic')==1 and qo.get('direction')==[1,0,0])
                panel=panels.get(q1['operationId']);costs={k:sum(x['costs'][k] for x in cycle['actions']) for k in('permissionSpent','querySpent','tollSpent')}
                need(pending['payload']['permissionSpent']==costs['permissionSpent'],'FEEDBACK_REAL_COST_MISMATCH')
                need((panel is not None)==(q1['costs']['querySpent']>0),'PAID_PANEL_WORLD_COST_MISMATCH')
                q2e={} if q2 is None else q2['nativeEvidence'];datum=q2e.get('datum_request')
                exposure=(q2 is not None and q2e.get('datum_omitted') is False and request_applied(datum,receipts))
                counts={'requested':len(receipts),'applied':sum(x['receipt']['status']=='applied' for x in receipts.values()),
                        'rejected':sum(x['receipt']['status'].startswith('rejected') for x in receipts.values())}
                cycle.update(afterTick=tick,nativeTicks=tick-cycle['beforeTick'],costs=costs,
                    nativeQuestionReleased=released,paidASKApplied=panel is not None,paidPanel=panel,
                    NativeQ2DatumApplied=exposure,datumOmitted=None if q2 is None else q2e.get('datum_omitted'),
                    nativeRawPrice=None if q2 is None else q2e.get('raw_price'),actualTag=None if q2 is None else q2e.get('actual_tag'),
                    submittedTag=None if q2 is None else q2e.get('submitted_tag'),NativeInputs=counts,
                    feedbackOperationId=opid,feedbackPayload=pending['payload'],actualConsequence=e.get('actual_consequence'),
                    actualPhysicalFailed=e.get('actual_physical_failed'),appliedGenericFailed=e.get('applied_generic_failed'),
                    genericReturnPulses=e.get('generic_return_pulses'))
                cycles.append(cycle);cycle=None
            else:need(False,'UNEXPECTED_MATERIAL_KIND')
            pending=None
    need(pending is None and cycle is None,'INFLIGHT_NATIVE_PHASE_OR_EPISODE')
    n=len(cycles);closure=index['closure'];costs={k:sum(c['costs'][k] for c in cycles) for k in('permissionSpent','querySpent','tollSpent')}
    need(n==cfg['completedCycles']==state['completedOpportunities']==closure['ledgerWorld']['cycles'] and 0<=n<=6,'CLOSED_CYCLE_COUNT_MISMATCH')
    need(state['phase']=='BOUNDARY' and (state['lifeId'],state['sessionId'],state['nativeTick'],state['sequence'])==
         (cfg['lifeId'],cfg['sessionId'],tick,cfg['localSequence']),'COUPLED_AGENT_NATIVE_CURSOR_MISMATCH')
    need(tick==closure['nativeTick']==cfg['nativeTick'] and tick-SOURCE_TICK==closure['ledgerWorld']['consumed'] and closure['ledgerWorld']['reserved']==0,'FINAL_NATIVE_LEDGER_DOSE_MISMATCH')
    need(used_actions==set(acks)==set(action_events),'UNMATCHED_NATIVE_ACK_OR_WORLD_ACTION')
    initial=cfg['initialPublicState']['permissionStock'];need(initial-costs['permissionSpent']==ws['stock'],'ACTUAL_STOCK_ACCOUNTING_MISMATCH')
    need(costs['tollSpent']==ws['tollSpent'] and len(panels)==sum(c['paidASKApplied'] for c in cycles),'WORLD_COST_OR_PANEL_COUNT_MISMATCH')
    return {'schema':SCHEMA+'.facts','instanceId':cfg['instanceId'],'lifeId':cfg['lifeId'],'sessionId':cfg['sessionId'],
        'condition':cfg['focalCondition'],'sourceTick':SOURCE_TICK,'finalNativeTick':tick,'newNativeTicks':tick-SOURCE_TICK,
        'actualCompletedCycles':n,'configuredMaximum':6,'fullSixClosed':n==6,'cycles':cycles,'costs':costs,
        'stock':{'initial':initial,'final':ws['stock']},'paidASKApplied':sum(c['paidASKApplied'] for c in cycles),
        'paidPanelsWithAnyDepletedPort':sum(c['paidPanel'] is not None and
            (c['paidPanel']['sample']['price0']==2 or c['paidPanel']['sample']['price1']==2) for c in cycles),
        'nativeQuestionReleased':sum(c['nativeQuestionReleased'] for c in cycles),'NativeQ2DatumApplied':sum(c['NativeQ2DatumApplied'] for c in cycles),
        'datumOmitted':sum(c['datumOmitted'] is True for c in cycles),'noQ2':sum(c['datumOmitted'] is None for c in cycles),
        'NativeInputs':{'requested':len(all_receipts),'applied':sum(x['receipt']['status']=='applied' for x in all_receipts.values()),
                        'rejected':sum(x['receipt']['status'].startswith('rejected') for x in all_receipts.values())},
        'environment':{'finalAvailability':law,'passages':passages,'replenished':replenished,'queries':ws['queries'],
                       'skips':ws['skips'],'moves':ws['moves'],'waits':ws['waits'],'freePassesUsed':ws['freePassesUsed']},
        'issues':[],'inference':'Descriptive paired descendants n=1 per arm. No policy learning or external validation inferred.',
        'NativeExecuted':False,'SQLiteOpened':False}

def export(runtime,instance,condition,protocol,output):
    runtime=root_path(runtime);need(ID.fullmatch(instance) is not None and condition in('OSCILANTE','CONTROL'),'EXACT_FOCAL_ID_ARM')
    home=contained(runtime,'estado_demo/instancias/'+instance);cfg=read(contained(home,'INSTANCE.json'))
    life='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'+instance
    need((cfg['instanceId'],cfg['lifeId'],cfg['profile'],cfg['validationRevision'],cfg['focalCondition'])==
         (instance,life,'FOCAL','FOCAL_R06',condition),'EXACT_FOCAL_PROFILE')
    need(cfg['maxCycles']==6 and cfg['maxLocalSequence']==12 and cfg['sequenceOffset']==56,'PRESERVED_FOCAL_LIMITS_OFFSET')
    locks=('SDK_SERVICE.lock','SDK_CAPABILITIES_SERVICE.lock','sistema/estado/locks/'+life+'.lock',
           'sistema/estado/vidas/'+life+'/FUTURO_INTERRUMPIDO.json','sistema/estado/ACTIVO.json')
    for p in locks:need(not os.path.lexists(home/p),'OWNER_OR_UNCOMMITTED_FUTURE_PRESENT')
    ledger=read(contained(runtime,'estado_demo/LEDGER_SDK_R06.json'));need(ledger['intents']=={} and ledger['worlds'][life]['reserved']==0,'GLOBAL_LEDGER_NOT_QUIESCENT')
    pairfile=contained(home,'SDK_PAIR.json');pair=read(pairfile);native=pair['native'];proof=read(contained(home,'BACKEND_CLOSED.json'))
    need(native['writerClosed'] is True and native['pending']==0 and native['lifeId']==life and native['dimension']==67,'CLOSED_NATIVE_PAIR_REQUIRED')
    need(proof['backendWriterClosed'] is True and proof['bridgeQuiescent'] is True and
         all(proof[k]==native[k] for k in('nativeTick','snapshotSha256','databaseSha256','cardSha256')),'CLOSED_PAIR_PROOF_MISMATCH')
    cardfile=contained(home,'sistema/estado/vidas/'+life+'/VIDA.json');card=read(cardfile)
    need(pin(cardfile)['sha256']==native['cardSha256'] and card['snapshot_sha256']==native['snapshotSha256'] and
         card['physical']['N']==67 and card['physical']['tick']==native['nativeTick'] and card['life_id']==life,'ACTUAL_CLOSED_NATIVE_CARD_MISMATCH')
    ownerfile=contained(home,'ENSAYOS.jsonl');owner=lines(ownerfile)
    need(owner and owner[-1]['kind']=='OWNER_CLOSED' and owner[-1]['exit_code']==0 and owner[-1]['final_status']['running'] is False,'LATEST_NATIVE_OWNER_NOT_CLOSED')
    protocol=root_path(protocol);selected=[];secrets=[]
    connection=contained(runtime,'configuracion/CONEXION_PRIVADA.json')
    secret=read(connection).get('token')
    if isinstance(secret,str):secrets.append(secret)
    def add(path,archive,jsonl=False):
        data=raw(path);safe_payload(data,secrets,jsonl)
        selected.append({'archive':archive,**pin(path),'jsonl':jsonl,'literal':True,'data':data})
    for name in('SDK_PAIR.json','BACKEND_CLOSED.json','ACTION_ACKS.json'):add(contained(home,name),'PRIMARIOS/'+name)
    add(protocol,'PROTOCOLO/PROTOCOLO_PROSPECTIVO.json')
    add(contained(runtime,'configuracion/VENTANA_FOCAL_R06.json'),'PROTOCOLO/VENTANA_FOCAL_R06.json')
    add(contained(runtime,'backend/focal_r06/FUENTES_FOCAL_R06.json'),'PROTOCOLO/FUENTES_FOCAL_R06.json')
    worker=contained(home,'sistema/estado/servicios_locales/'+life)
    add(contained(worker,'DEE_SDK_FOCAL_NATIVE_0_1_0/events.jsonl'),'PRIMARIOS/NATIVE/events.jsonl',True)
    archives=[]
    for p in sorted(contained(home,'http_operations').glob('*.json')):
        archive='PRIMARIOS/HTTP/'+p.name;add(p,archive);archives.append(archive)
    keys=('instanceId','lifeId','sessionId','focalCondition','sequenceOffset','completedCycles','localSequence','nativeTick','initialPublicState')
    index={'schema':SCHEMA,'configuration':{k:cfg[k] for k in keys},'operations':archives,
           'closure':{'nativeTick':native['nativeTick'],'native':native,'ledgerWorld':ledger['worlds'][life],
                      'ownerClosed':owner[-1],'sourcePins':{'card':pin(cardfile),'ownerJournal':pin(ownerfile),
                          'instance':pin(home/'INSTANCE.json'),'ledgerCaptured':pin(runtime/'estado_demo/LEDGER_SDK_R06.json')}}}
    members={x['archive']:x['data'] for x in selected}
    def local(name,jsonl=False):
        b=members[name].decode('utf-8-sig');return [json.loads(x) for x in b.splitlines() if x.strip()] if jsonl else json.loads(b)
    result=facts(index,local);safe_payload((canonical(index)+'\n').encode(),secrets)
    out=destination(output,(runtime,home));out.mkdir();manifest=[]
    for item in selected:
        target=contained(out,item['archive'],False);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(item['data'])
        manifest.append({k:v for k,v in item.items() if k!='data'})
    for name,value in(('INDICE_CERRADO.json',index),('HECHOS_RECALCULADOS.json',result)):
        b=(canonical(value)+'\n').encode();(out/name).write_bytes(b);manifest.append({'archive':name,'bytes':len(b),'sha256':digest(b),'literal':False})
    code=raw(Path(__file__));(out/'RECALCULAR_FOCAL_R06.py').write_bytes(code)
    manifest.append({'archive':'RECALCULAR_FOCAL_R06.py','bytes':len(code),'sha256':digest(code),'literal':True})
    for item in selected:need(pin(item['source'])['sha256']==item['sha256'],'CLOSED_SOURCE_CHANGED_DURING_EXPORT')
    need(pin(cardfile)['sha256']==index['closure']['sourcePins']['card']['sha256'] and
         pin(ownerfile)['sha256']==index['closure']['sourcePins']['ownerJournal']['sha256'] and
         pin(home/'INSTANCE.json')['sha256']==index['closure']['sourcePins']['instance']['sha256'],'CLOSED_NATIVE_ANCHOR_CHANGED')
    for p in locks:need(not os.path.lexists(home/p),'OWNER_OPENED_DURING_EXPORT')
    latest=read(runtime/'estado_demo/LEDGER_SDK_R06.json')
    need(latest['intents']=={} and latest['worlds'][life]==index['closure']['ledgerWorld'],'CLOSED_WORLD_LEDGER_CHANGED')
    value={'schema':SCHEMA+'.manifest','files':manifest,'NativeExecuted':False,'NativeSnapshotsOrDBIncluded':False}
    (out/'MANIFIESTO.json').write_text(canonical(value)+'\n',encoding='utf8')
    return {'status':'EXPORTED_CLOSED','condition':condition,'completedCycles':result['actualCompletedCycles'],
            'files':len(manifest),'output':str(out),'manifestSha256':pin(out/'MANIFIESTO.json')['sha256'],'NativeExecuted':False}

def recalculate(package,output=None):
    package=root_path(package);manifest=read(contained(package,'MANIFIESTO.json'));need(manifest['schema']==SCHEMA+'.manifest','EXACT_FOCAL_MANIFEST')
    members={}
    for item in manifest['files']:
        name=item['archive'];need(name not in members,'DUPLICATE_ARCHIVE');b=raw(contained(package,name))
        need(len(b)==item['bytes'] and digest(b)==item['sha256'],'EXTRACTED_MEMBER_HASH_MISMATCH');members[name]=item
    def local(name,jsonl=False):
        need(name in members,'UNDECLARED_PORTABLE_MEMBER');p=contained(package,name);return lines(p) if jsonl else read(p)
    result=facts(local('INDICE_CERRADO.json'),local)
    if output is not None:
        out=destination(output);out.mkdir();(out/'HECHOS_RECALCULADOS.json').write_text(canonical(result)+'\n',encoding='utf8')
    return result

def compare_packages(osc,control,output):
    a=recalculate(osc);b=recalculate(control)
    need(a['condition']=='OSCILANTE' and b['condition']=='CONTROL' and a['lifeId']!=b['lifeId'] and
         a['sourceTick']==b['sourceTick']==SOURCE_TICK,'PAIRED_DISTINCT_DESCENDANTS_REQUIRED')
    pairs=[]
    for left,right in zip(a['cycles'],b['cycles']):
        la=[x['nativeAction'] for x in left['actions']];ra=[x['nativeAction'] for x in right['actions']]
        pairs.append({'cycle':left['cycle'],'partition':left['partition'],'OSCILANTE':{'actions':la,'costs':left['costs'],
            'paidASK':left['paidASKApplied'],'NativeQ2DatumApplied':left['NativeQ2DatumApplied'],'rawPrice':left['nativeRawPrice']},
            'CONTROL':{'actions':ra,'costs':right['costs'],'paidASK':right['paidASKApplied'],
                       'NativeQ2DatumApplied':right['NativeQ2DatumApplied'],'rawPrice':right['nativeRawPrice']},'observedActionSequenceDiffers':la!=ra})
    value={'schema':SCHEMA+'.paired_description','actualCycles':{'OSCILANTE':len(a['cycles']),'CONTROL':len(b['cycles'])},
           'commonClosedCycles':len(pairs),'paired':pairs,'policyLearningInferred':False,
           'limit':'One paired descendant per condition, fixed prepared law. Exposure/cost differences do not prove policy learning.',
           'NativeExecuted':False,'SQLiteOpened':False}
    out=destination(output);out.mkdir();(out/'COMPARACION_DESCRIPTIVA.json').write_text(canonical(value)+'\n',encoding='utf8');return value

if __name__=='__main__':
    q=argparse.ArgumentParser(description=__doc__);sub=q.add_subparsers(dest='command',required=True)
    p=sub.add_parser('export');p.add_argument('--runtime',type=Path,required=True);p.add_argument('--instance',required=True)
    p.add_argument('--condition',choices=('OSCILANTE','CONTROL'),required=True);p.add_argument('--protocol',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('recalculate');p.add_argument('--package-root',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('compare');p.add_argument('--osc',type=Path,required=True);p.add_argument('--control',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args=q.parse_args()
    if args.command=='export':result=export(args.runtime,args.instance,args.condition,args.protocol,args.output)
    elif args.command=='recalculate':result=recalculate(args.package_root,args.output)
    else:result=compare_packages(args.osc,args.control,args.output)
    print(canonical(result))
