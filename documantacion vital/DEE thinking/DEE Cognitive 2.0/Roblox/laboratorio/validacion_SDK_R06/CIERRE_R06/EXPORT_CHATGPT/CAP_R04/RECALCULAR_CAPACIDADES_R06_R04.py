"""Closed-only stdlib SDK evidence export and portable capabilities recalculation.

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

SCHEMA='DEE.Roblox.SDK.closed_capability_evidence.R06.R04'
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
def safe_content(data,secrets=(),jsonl=False):
    text=data.decode('utf-8-sig')
    need(not any(secret and secret in text for secret in secrets),'PRIVATE_CREDENTIAL_IN_SELECTED_SOURCE')
    values=[json.loads(x) for x in text.splitlines() if x.strip()] if jsonl else [json.loads(text)]
    def visit(value):
        if isinstance(value,dict):
            for key,item in value.items():
                field=re.sub('[^a-z0-9]','',str(key).lower())
                need(field not in {'authorization','bearertoken','password','apikey','accesstoken','privatetoken','secret'},'SECRET_FIELD:'+str(key))
                if field=='token' and isinstance(item,str):need(len(item)<24,'LONG_TOKEN_FIELD')
                need(not(field in {'snapshot','committedsnapshot','snapshotmetadataentries','rawcopy','clockscopy'} and isinstance(item,(dict,list))),'SNAPSHOT_OR_BUFFER_PAYLOAD')
                visit(item)
        elif isinstance(value,list):
            for item in value:visit(item)
    for value in values:visit(value)

def select_capability_state(home):
    """Select current R03 exclusively; old FAILED is literal provenance only."""
    home=Path(home);oldpath=home/'CAPABILITIES_STATE_R06.json'
    current=home/'CAPABILITIES_STATE_R06_R03.json';history=[]
    if current.exists():
        state=read(current);old=read(oldpath);link=state.get('previousFailedBoot',{})
        need(state.get('status')=='CLOSED' and state.get('lastError') is None,'R03_CAPABILITIES_NOT_CLOSED_NO_FALLBACK')
        need(old.get('status')=='FAILED_PRESERVED' and old.get('capabilitySequence')==0 and old.get('lastError') is not None,
             'R03_REQUIRES_LITERAL_ZERO_EVENT_OLD_FAILURE')
        need((old['instanceId'],old['sessionId'])==(state['instanceId'],state['sessionId']) and
             old['nativeTick']<=state['nativeTick'],'HISTORICAL_FAILURE_IDENTITY_OR_TICK')
        need(link.get('file')==oldpath.name and link.get('sha256')==pin(oldpath)['sha256'] and
             link.get('errorPreserved')==old['lastError'],'R03_FAILURE_LINK_MISMATCH')
        history.append({'path':oldpath,'archive':'PRIMARIOS/ESTADO_HOST/HISTORICO_CAPABILITIES_STATE_R06.json',
                        'role':'historical_failed_boot'})
        receipt=home/'CAPABILITIES_REPAIR_ACCESS_R03/RESULTADO.json'
        if receipt.exists():
            r=read(receipt)
            need(r.get('status')=='REPAIRED_ZERO_EVENT_FS_ONLY' and r.get('newNativeTicks')==0 and
                 r.get('nativeBefore')==r.get('nativeAfter') and r.get('ledgerUnchanged') is True and
                 r.get('oldFailurePreserved') is True and r.get('accessGuardUnchanged') is True,
                 'R03_TECHNICAL_REPAIR_RECEIPT_MISMATCH')
            history.append({'path':receipt,'archive':'PRIMARIOS/ESTADO_HOST/REPARACION_R03_RESULTADO.json',
                            'role':'technical_repair_receipt'})
        return current,state,history
    return oldpath,read(oldpath) if oldpath.exists() else None,history

def receipt_summary(receipts):
    unique={}
    for item in receipts:
        need(isinstance(item,dict) and type(item.get('id')) is int,'LITERAL_RECEIPT_ID')
        identifier=item['id'];r=item.get('receipt')
        need(isinstance(r,dict) and r.get('id')==identifier and isinstance(r.get('status'),str),'LITERAL_TERMINAL_RECEIPT')
        need(type(item.get('payload')) is int and type(item.get('requested_tick')) is int and isinstance(item.get('channel'),str),'LITERAL_REQUEST_FIELDS')
        if identifier in unique:need(unique[identifier]==item,'CONFLICTING_RECEIPT_ALIAS')
        unique[identifier]=item
    statuses={}
    for item in unique.values():statuses[item['receipt']['status']]=statuses.get(item['receipt']['status'],0)+1
    applied=statuses.get('applied',0);rejected=sum(n for key,n in statuses.items() if key.startswith('rejected'))
    return {'unique_requested':len(unique),'applied':applied,'rejected':rejected,
            'pending_or_other':len(unique)-applied-rejected,'status_counts':statuses},unique

def facts(index,read_archive):
    """Derive counts/content from literal selected files; never solve operands."""
    issues=[];core=[];pending=None;previous=SOURCE_TICK
    for row in read_archive(index['coreJournal'],jsonl=True):
        if row.get('kind')=='PHASE_INTENT':
            need(pending is None,'OVERLAPPED_CORE_INTENT');pending=row
            need(row['tick']==previous and row['context']['session_id']==index['sessionId'],'CORE_TICK_OR_SESSION_CHAIN')
        elif row.get('kind')=='PHASE_COMPLETED':
            need(pending is not None and row['mode']==pending['mode'],'UNMATCHED_CORE_COMPLETION')
            result=row['result'];ticks=row['tick']-pending['tick']
            need(ticks>=0 and result['nativeTicks']==ticks and result['nativeTick']==row['tick'],'CORE_TICK_RECEIPT_MISMATCH')
            core.append({'operationId':pending['context']['operation_id'],'mode':row['mode'],
                'beforeTick':pending['tick'],'afterTick':row['tick'],'nativeTicks':ticks,
                'action':result.get('action'),'accepted':result.get('accepted'),
                'Native_inputs_cumulative':result.get('evidence',{}).get('Native_inputs')});pending=None;previous=row['tick']
    need(pending is None,'UNFINISHED_CORE_PHASE')
    events=[];all_receipts={};last_tick=core[-1]['afterTick'] if core else SOURCE_TICK
    for selected in index['capabilityPrimaries']:
        primary=read_archive(selected['archive']);operation=read_archive(selected['operationArchive'])
        identifier=selected['operationId'];context=primary['context']
        need(primary['lifeId']==index['lifeId'] and primary['sessionId']==index['sessionId'],'PRIMARY_IDENTITY_MISMATCH')
        need(context['operation_id']==identifier and operation['operationId']==identifier and operation['status']=='COMPLETED','PRIMARY_OPERATION_MISMATCH')
        need(context['capability_sequence']==len(events)+1==operation['value']['capabilitySequence'],'CAPABILITY_CURSOR_MISMATCH')
        need(primary['before_tick']==last_tick and primary['after_tick']>=last_tick,'CAPABILITY_TICK_CHAIN_MISMATCH')
        ticks=primary['after_tick']-primary['before_tick'];need(operation['value']['nativeTicks']==ticks and operation['value']['nativeTick']==primary['after_tick'],'CAPABILITY_RESULT_TICKS_MISMATCH')
        counts,receipts=receipt_summary(primary['requests_normalized'])
        need(counts['pending_or_other']==0,'UNFINISHED_NATIVE_INPUT_RECEIPT')
        for key in('unique_requested','applied','rejected','pending_or_other'):
            if key in primary['Native_inputs']:need(primary['Native_inputs'][key]==counts[key],'NATIVE_INPUT_DENOMINATOR_MISMATCH')
        for key,item in receipts.items():
            if key in all_receipts:need(all_receipts[key]==item,'CROSS_EVENT_RECEIPT_CONFLICT')
            all_receipts[key]=item
        value=primary['nativeValue'];kind=primary['request']['kind']
        actual={}
        if kind=='RECALL':actual={'native_sign':value.get('native_sign'),'status':value.get('status')}
        elif kind=='LESSON':actual={'observed_sign':value.get('observed_sign'),'revision':value.get('revision'),'teacher_mode':value.get('teacher_mode'),'learningSuccessNotInferred':True}
        elif kind=='COMPARE':actual={key:value.get(key) for key in('early_physical_choice','old_q6_choice','early_tick','query_tick','early_observation')}
        else:actual={key:value.get(key) for key in('numeric_result','status','operation','transported_actual_intermediate')}
        events.append({'operationId':identifier,'capabilitySequence':len(events)+1,'kind':kind,
            'request':primary['request'],'beforeTick':primary['before_tick'],'afterTick':primary['after_tick'],
            'nativeTicks':ticks,'Native_inputs':counts,'actualNativeContent':actual})
        last_tick=primary['after_tick']
    provenance=index.get('capturedHostStates',{'current':None,'historical':[]})
    if provenance['current'] is not None:
        host=read_archive(provenance['current']['archive'])
        need(host['status']=='CLOSED' and host.get('lastError') is None,'COPIED_CURRENT_HOST_NOT_CLOSED')
        need(host['nativeTick']==index['closure']['nativeTick'] and host['capabilitySequence']==len(events),
             'COPIED_HOST_FINAL_CURSOR_MISMATCH')
        if provenance['current']['archive'].endswith('/CAPABILITIES_STATE_R06_R03.json'):
            prior=[x for x in provenance['historical'] if x['role']=='historical_failed_boot']
            need(len(prior)==1,'ONE_COPIED_HISTORICAL_FAILURE_REQUIRED')
            old=read_archive(prior[0]['archive']);link=host['previousFailedBoot']
            need(old['status']=='FAILED_PRESERVED' and old['capabilitySequence']==0 and
                 old['lastError']==link['errorPreserved'] and link['sha256']==prior[0]['sha256'] and
                 link['file']=='CAPABILITIES_STATE_R06.json','COPIED_R03_FAILURE_LINK_MISMATCH')
    closure=index['closure'];total=sum(x['nativeTicks'] for x in core)+sum(x['nativeTicks'] for x in events)
    need(last_tick==closure['nativeTick'] and SOURCE_TICK+total==last_tick,'FINAL_NATIVE_TICK_DOSE_MISMATCH')
    need(closure['ledgerWorld']['consumed']==total and closure['ledgerWorld']['reserved']==0,'LEDGER_DOSE_OR_RESERVATION_MISMATCH')
    complete=sum(x['mode']=='eci01-rbx01-feedback' and x['accepted'] is True for x in core)
    need(complete==closure['ledgerWorld']['cycles']==closure['coreCompletedCycles'],'SDK_CYCLE_COUNTER_MISMATCH')
    need(len(events)==closure['capabilitySequence']==closure['ledgerWorld'].get('capability_events',0),'CAPABILITY_FINAL_COUNTER_MISMATCH')
    aggregate,_=receipt_summary(list(all_receipts.values()))
    return {'schema':SCHEMA+'.recalculation','instanceId':index['instanceId'],'lifeId':index['lifeId'],'sessionId':index['sessionId'],
        'sourceTick':SOURCE_TICK,'finalNativeTick':last_tick,'newNativeTicks':total,
        'coreCompletedCycles':complete,'corePhases':core,'capabilityEvents':events,
        'capabilityNativeInputSummary':aggregate,'issues':issues,'capturedHostStates':provenance,
        'scope':['Only actual copied primaries/receipts were recalculated. No expected arithmetic answer was computed.',
                 'NULL remains distinct from integer0. Teaching receipt admission does not prove learning.',
                 'K4 World equality is captured source evidence, not independently recalculated without its World checkpoint.',
                 'No Native snapshot/database is in this package; it is not an executable backup.']}

def export(home,output,runtime,strict_closed=True):
    need(strict_closed is True,'CLOSED_ONLY_EXPORT_NO_BYPASS')
    runtime=root_path(runtime);home=root_path(home)
    need(home.parent==runtime/'estado_demo/instancias' and ID.fullmatch(home.name),'EXACT_DIAGNOSTIC_HOME')
    cfg=read(home/'INSTANCE.json');life=cfg['lifeId'];sid=cfg['sessionId']
    need(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'+home.name,'EXACT_DIAGNOSTIC_LIFE')
    lock_names=('SDK_SERVICE.lock','SDK_CAPABILITIES_SERVICE.lock','sistema/estado/locks/'+life+'.lock',
                'sistema/estado/vidas/'+life+'/FUTURO_INTERRUMPIDO.json')
    for name in lock_names:need(not os.path.lexists(home/name),'OWNER_OR_UNCOMMITTED_FUTURE_EXISTS')
    need(not os.path.lexists(home/'sistema/estado/ACTIVO.json'),'SELECTED_PRODUCT_REFUSED')
    ledger_path=runtime/'estado_demo/LEDGER_SDK_R06.json';ledger=read(ledger_path)
    need(ledger['intents']=={} and life in ledger['worlds'],'NATIVE_INTENT_OR_MISSING_LEDGER_LIFE')
    world=ledger['worlds'][life];need(world['reserved']==0,'RESERVATION_NOT_CLOSED')
    pair_path=home/'SDK_PAIR.json';pair=read(pair_path)
    state_path,capstate,historical_states=select_capability_state(home)
    if capstate is not None:need((capstate['instanceId'],capstate['sessionId'])==(home.name,sid),'CURRENT_HOST_IDENTITY_MISMATCH')
    descriptor=capstate['closedNativeDescriptor'] if capstate is not None else pair['native']
    if capstate is not None:need(capstate['status']=='CLOSED' and capstate.get('lastError') is None,'CAPABILITIES_NOT_CLOSED')
    need(descriptor['writerClosed'] is True and descriptor['pending']==0,'NATIVE_WRITER_OR_QUEUE_NOT_CLOSED')
    need(descriptor['lifeId']==life and descriptor['dimension']==67,'CLOSED_NATIVE_IDENTITY')
    card_path=home/'sistema/estado/vidas'/life/'VIDA.json';card=read(card_path)
    need(card['life_id']==life and card['physical']['N']==67 and card['physical']['tick']==descriptor['nativeTick'],'CURRENT_NATIVE_CARD_MISMATCH')
    need(pin(card_path)['sha256']==descriptor['cardSha256'] and card['snapshot_sha256']==descriptor['snapshotSha256'],'CURRENT_CLOSED_ANCHOR_MISMATCH')
    owner_path=home/'ENSAYOS.jsonl';journal=lines(owner_path);closed=[r for r in journal if r.get('kind')=='OWNER_CLOSED']
    need(closed and journal[-1].get('kind')=='OWNER_CLOSED','LATEST_OWNER_JOURNAL_NOT_CLOSED')
    last=closed[-1];need(last['exit_code']==0 and last['final_status']['running'] is False,'OWNER_EXIT_NOT_CLOSED')
    for key in('tick','nativeTick','native_tick'):
        if key in last['final_status']:need(last['final_status'][key]==descriptor['nativeTick'],'OWNER_FINAL_TICK_MISMATCH')
    secrets=[];connection=runtime/'configuracion/CONEXION_PRIVADA.json'
    if connection.exists():
        secret=read(connection).get('token')
        if isinstance(secret,str):secrets.append(secret)
    selected=[]
    def literal(path,archive,jsonl=False,expected=None):
        data=raw(path);safe_content(data,secrets,jsonl)
        if expected is not None:need(len(data)==expected['bytes'] and digest(data)==expected['sha256'],'PRIMARY_LOCATOR_HASH_MISMATCH')
        selected.append({'archive':archive,**pin(path),'literal':True,'jsonl':jsonl,'data':data})
    captured_states={'current':None,'historical':[]}
    if capstate is not None:
        current_archive='PRIMARIOS/ESTADO_HOST/'+state_path.name
        literal(state_path,current_archive)
        captured_states['current']={'archive':current_archive,'role':'current_closed_host_state',**pin(state_path)}
    for historical in historical_states:
        literal(historical['path'],historical['archive'])
        captured_states['historical'].append({'archive':historical['archive'],'role':historical['role'],**pin(historical['path'])})
    worker=home/'sistema/estado/servicios_locales'/life
    core_journal=worker/'DEE_SDK_NATIVE_0_1_0/events.jsonl'
    literal(core_journal,'PRIMARIOS/CORE/events.jsonl',True)
    caps=[];operations=home/'capability_operations'
    if operations.exists():
        for p in sorted(operations.glob('*.json')):
            op=read(p);need(op['status'] not in BAD_STATES,'OPERATION_PENDING_OR_UNCERTAIN')
            need(op['status'] in('COMPLETED','FAILED_KNOWN'),'UNRESOLVED_OPERATION_STATE')
            if op['status']=='FAILED_KNOWN':need(op.get('nativeAdmissionStarted') is False,'FAILED_KNOWN_NOT_PROVEN_PRE_NATIVE')
            literal(p,'PRIMARIOS/OPERACIONES/'+p.name)
            if op['status']=='COMPLETED' and op['kind']!='CLOSE':
                identifier=op['operationId'];need(OP.fullmatch(identifier),'EXACT_OPERATION_ID')
                locator=op['value']['primary'];primary=primary_source(worker,locator['path'])
                archive='PRIMARIOS/CAPABILITIES/'+identifier+'.json';literal(primary,archive,expected=locator)
                caps.append({'operationId':identifier,'archive':archive,
                             'operationArchive':'PRIMARIOS/OPERACIONES/'+p.name,'sequence':op['value']['capabilitySequence']})
    caps.sort(key=lambda x:x['sequence'])
    # Copy the event journal as literal corroboration if it exists.
    cap_journal=worker/'DEE_SDK_ASSISTED_CAPABILITIES_R06/events.jsonl'
    if cap_journal.exists():literal(cap_journal,'PRIMARIOS/CAPABILITIES/events.jsonl',True)
    k4=[];proof_dir=home/'restoration_proofs'
    if proof_dir.exists():
        for p in sorted(proof_dir.glob('*.json')):
            proof=read(p)
            k4.append({'source':pin(p),'status':proof['status'],'serverComparison':proof.get('serverComparison'),
                       'serverCursorMatched':proof.get('serverCursorMatched'),'pairSha256':proof.get('pairSha256'),
                       'checkpointSha256':proof.get('checkpointSha256'),
                       'actualState':proof.get('body',{}).get('proof',{}).get('actual',{}).get('state')})
    closure={'nativeTick':descriptor['nativeTick'],'nativeClosedDescriptor':descriptor,
        'physical':card['physical'],'coreCompletedCycles':cfg['completedCycles'],
        'capabilitySequence':0 if capstate is None else capstate['capabilitySequence'],'ledgerWorld':world,
        'ownerClosed':{'exit_code':last['exit_code'],'final_status':{'running':False},
                       'runid':last.get('runid'),'utc':last.get('utc')},
        'sourcePins':{'card':pin(card_path),'ownerJournal':pin(owner_path),'ledger':pin(ledger_path),'SDK_PAIR':pin(pair_path)},
        'K4RecordedComparisons':k4,'snapshotPayloadsExported':False,'WorldPairCurrentAfterCapabilities':capstate is None}
    index={'schema':SCHEMA,'instanceId':home.name,'lifeId':life,'sessionId':sid,
           'coreJournal':'PRIMARIOS/CORE/events.jsonl','capabilityPrimaries':caps,'closure':closure,'capturedHostStates':captured_states}
    by_archive={x['archive']:x['data'] for x in selected}
    def from_source(archive,jsonl=False):
        text=by_archive[archive].decode('utf-8-sig');return [json.loads(x) for x in text.splitlines() if x.strip()] if jsonl else json.loads(text)
    report=facts(index,from_source)
    safe_content((canonical(index)+'\n').encode(),secrets)
    # All source verification precedes creating a new output directory.
    out=destination(output,(runtime,home));out.mkdir()
    manifests=[]
    for row in selected:
        target=contained(out,row['archive'],False);target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(row['data'])
        manifests.append({k:v for k,v in row.items() if k!='data'})
    for name,value in(('INDICE_CERRADO.json',index),('RECALCULO.json',report)):
        data=(canonical(value)+'\n').encode();(out/name).write_bytes(data)
        manifests.append({'archive':name,'bytes':len(data),'sha256':digest(data),'literal':False,'role':'captured_projection' if name.startswith('INDICE') else 'recalculation'})
    script=raw(Path(__file__));(out/'RECALCULAR_CAPACIDADES_R06_R04.py').write_bytes(script)
    manifests.append({'archive':'RECALCULAR_CAPACIDADES_R06_R04.py','bytes':len(script),'sha256':digest(script),'literal':True,'role':'code'})
    guide=('Evidencia cerrada SDK/CAP R06 revision R04. Estado actual y fallo anterior separados. No contiene Native snapshots, bases SQLite ni credenciales.\n'
        'No es un respaldo ejecutable del cerebro ni sustituye el NativeRoot privado completo.\n'
        'Desde esta carpeta extraída, con Python estándar y un destino NUEVO:\n'
        'python -I -S -B RECALCULAR_CAPACIDADES_R06_R04.py recalculate --package-root . --output RECALCULO_NUEVO\n'
        'El recálculo sólo abre miembros archive del manifiesto y verifica SHA/tamaño.\n'
        'Las rutas source son procedencia histórica, nunca fallback operativo.\n'
        'Recuenta pulsos/estados/ticks y reproduce contenido Native; no calcula respuestas aritméticas esperadas.\n'
        'NULL no se convierte en0. Admisión de una lección no prueba aprendizaje.\n'
        'Las comparaciones K4 exportadas son proyecciones de pruebas ya registradas; sin World checkpoint no se repite esa comparación completa.\n').encode('utf8')
    (out/'LEER_RECALCULO.txt').write_bytes(guide)
    manifests.append({'archive':'LEER_RECALCULO.txt','bytes':len(guide),'sha256':digest(guide),'literal':False,'role':'guide'})
    manifest={'schema':SCHEMA+'.manifest','files':manifests,'NativeExecuted':False,'NativeSnapshotsOrDBIncluded':False}
    # The original closed inputs must still match after copying.
    for row in selected:need(pin(row['source'])['sha256']==row['sha256'],'SOURCE_CHANGED_DURING_EXPORT')
    need(pin(card_path)['sha256']==closure['sourcePins']['card']['sha256'] and
         pin(ledger_path)['sha256']==closure['sourcePins']['ledger']['sha256'],'CLOSED_ANCHOR_CHANGED_DURING_EXPORT')
    need(pin(owner_path)['sha256']==closure['sourcePins']['ownerJournal']['sha256'] and
         pin(pair_path)['sha256']==closure['sourcePins']['SDK_PAIR']['sha256'],'OWNER_OR_PAIR_CHANGED_DURING_EXPORT')
    for name in lock_names:need(not os.path.lexists(home/name),'OWNER_OPENED_DURING_EXPORT')
    (out/'MANIFIESTO.json').write_text(canonical(manifest)+'\n',encoding='utf8')
    return {'status':'EXPORTED_CLOSED','output':str(out),'manifestSha256':pin(out/'MANIFIESTO.json')['sha256'],
            'files':len(manifests),'facts':report,'NativeExecuted':False}

def recalculate(package,output):
    package=root_path(package);manifest=read(package/'MANIFIESTO.json')
    need(manifest['schema']==SCHEMA+'.manifest','EXACT_PORTABLE_MANIFEST')
    members={}
    for row in manifest['files']:
        need(row['archive'] not in members,'DUPLICATE_ARCHIVE')
        p=contained(package,row['archive']);data=raw(p)
        need(len(data)==row['bytes'] and digest(data)==row['sha256'],'EXTRACTED_MEMBER_HASH_MISMATCH')
        members[row['archive']]=row
    def local(archive,jsonl=False):
        need(archive in members,'UNDECLARED_ARCHIVE_READ')
        return lines(contained(package,archive)) if jsonl else read(contained(package,archive))
    index=local('INDICE_CERRADO.json')
    states=index.get('capturedHostStates',{'current':None,'historical':[]})
    for state in ([states['current']] if states['current'] is not None else [])+states['historical']:
        member=members.get(state['archive'],{})
        need((member.get('sha256'),member.get('bytes'))==(state['sha256'],state['bytes']),
             'CAPTURED_HOST_STATE_MANIFEST_BINDING_MISMATCH')
    value=facts(index,local)
    out=destination(output);out.mkdir();(out/'RECALCULO.json').write_text(canonical(value)+'\n',encoding='utf8')
    return value

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    a=sub.add_parser('export');a.add_argument('--home',type=Path,required=True);a.add_argument('--runtime',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    a=sub.add_parser('recalculate');a.add_argument('--package-root',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    args=p.parse_args();value=export(args.home,args.output,args.runtime) if args.command=='export' else recalculate(args.package_root,args.output)
    print(canonical(value))
