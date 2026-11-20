"""Explicit operator-requested Native functions in a separate SDK event domain.

Import/registry inspection is stdlib only. No prepare, pulse, answer, replay or
new world is generated at import. Existing helper bodies and fixed readers are
retained; this file adds identity, event durability and bounded owner routing.
"""
from pathlib import Path
import hashlib
import json
import os
import re
import time

VERSION='DEE.Roblox.SDK.assisted_capabilities.R06'
MODE='eci01-pi10-sdk-capability-r06'
MODES={MODE}
KEY='DEE.Cognitive.Roblox.SDK.assisted_capabilities.R06'
CODE_KEY=KEY+'.CODE_SCOPE'
SCOPE=Path(__file__).with_name('SDK_CAPABILITIES_SCOPE_R06.json')
CORE_KEY='DEE.Cognitive.Roblox.SDK.native.0.1.0'
SYSTEM_KEY='DEE.Cognitive.System.1.1.life.v1'
FOLDER='DEE_SDK_ASSISTED_CAPABILITIES_R06'
KINDS={'RECALL','LESSON','NUMERIC','SOLVE','COMPOSE','COMPARE'}

def need(value,message):
    if not value:raise ValueError(message)
def canonical(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def scope():
    c=json.loads(SCOPE.read_text('utf-8-sig'))
    need(c.get('schema')=='DEE.Roblox.SDK.capabilities.scope.R06' and c.get('sealed') is True,'Exact sealed capabilities scope')
    life=c.get('lifeId')
    need(isinstance(life,str) and re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_SDK_DEMO_[0-9A-F]{16}',life)
         and c.get('allowedLifeIds')==[life],'One absolute SDK diagnostic life allowlist')
    need(c.get('instanceId')==life.removeprefix('ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_'),'Exact instance/life relation')
    need(c.get('max_ticks_per_cycle')==4096 and c.get('max_total_ticks')==40000 and
         c.get('max_raw_support')==10000 and c.get('monitor_tick_block')==16 and
         c.get('ownerMemoryBytes')==536870912 and c.get('threads')==1 and
         type(c.get('maxEvents')) is int and 1<=c['maxEvents']<=12,'Fixed capabilities safeguards')
    need(type(c.get('lastNewUtcEpoch')) is int and type(c.get('native_cutoff_utc_epoch')) is int and
         c['startUtcEpoch']<c['lastNewUtcEpoch']<c['native_cutoff_utc_epoch'],'Finite prospective capabilities window')
    for name,expected in c['sourceHashes'].items():
        need(Path(name).name==name and sha(SCOPE.with_name(name))==expected,'Changed capability source:'+name)
    return c
def identity(a,expected_life_id=None):
    c=scope();root=Path(__file__).resolve().parents[1]
    need(not os.path.lexists(root/'estado/ACTIVO.json'),'Capabilities refuse every selected product')
    from capacidades import rbx07_native_v3 as core
    actual=core.identity(a);entries=dict(a.world.runtime.snapshot_metadata_entries)
    need(actual['life_id']==c['lifeId'] and int(a.world.runtime.dimension)==67 and
         actual.get('profile')=='fisica_directa','Exact unselected N67 SDK owner')
    if expected_life_id is not None:need(expected_life_id==c['lifeId'],'Caller cannot substitute a life')
    m=core.get(a)
    need(m is not None and m['session_id']==c['sessionId'] and m['phase']=='IDLE' and
         m['pending'] is None and m['uncertain'] is False and m['cycles']>=2,'Normal K4 core must be complete and idle')
    need(c.get('participantIdentityRevision')=='R03_SCOPE_NATIVE_ONLY' and
         c.get('hostProfile')=={'runtimeVersion':'0.1.1','validationRevision':'R06'},
         'Pinned host-admitted SDK R06 profile required; no transport-file read')
    return actual
def _integer(value,maximum):return type(value) is int and 0<=value<=maximum
def validate_request(request):
    need(isinstance(request,dict) and request.get('kind') in KINDS,'One advertised assisted capability')
    kind=request['kind'];fields={'kind'}
    if kind=='RECALL':fields|={'form'}
    elif kind=='LESSON':fields|={'form','observedSign','revision','teacherMode'}
    elif kind=='NUMERIC':fields|={'operation','left','right'}
    elif kind=='SOLVE':fields|={'form','left','right'}
    elif kind=='COMPOSE':fields|={'forms','data'}
    else:fields|={'left','right'}
    need(set(request)==fields,'Exact assisted request; no target/expected answer field')
    if 'form' in request:need(request['form'] in ('luma','nara'),'Literal existing cue')
    if kind=='LESSON':
        need(type(request['observedSign']) is int and request['observedSign'] in(-1,1) and
             type(request['revision']) is bool and request['teacherMode'] in('paired','omitted','desync'),'Explicit observed lesson mode')
    if kind in('NUMERIC','SOLVE','COMPARE'):
        maximum=20 if kind=='COMPARE' else 32
        need(_integer(request['left'],maximum) and _integer(request['right'],maximum),'Independent exact operand domain')
    if kind=='NUMERIC':need(request['operation'] in('suma','diferencia'),'Existing operation literal only')
    if kind=='COMPOSE':
        need(isinstance(request['forms'],list) and len(request['forms'])==2 and all(x in('luma','nara') for x in request['forms']) and
             isinstance(request['data'],list) and len(request['data'])==3 and all(_integer(x,32) for x in request['data']),
             'Two explicit forms and three independent raw operands')
    return request
def validate_literal(row):
    need(isinstance(row,dict) and set(row)=={'modo','request','context'} and row['modo']==MODE,'Exact capability-event literal')
    validate_request(row['request']);context=row['context']
    need(isinstance(context,dict) and set(context)=={'operation_id','session_id','capability_sequence'} and
         isinstance(context['operation_id'],str) and re.fullmatch(r'[A-Za-z0-9_-]{1,90}',context['operation_id']) and
         isinstance(context['session_id'],str) and type(context['capability_sequence']) is int and context['capability_sequence']>=1,
         'Exact durable assisted event context')
def get(a):
    entries=dict(a.world.runtime.snapshot_metadata_entries)
    if KEY not in entries:return None
    m=json.loads(entries[KEY]);c=scope()
    need(m['version']==VERSION and m['scope']==c and entries.get(CODE_KEY)==canonical(c),'Capabilities metadata/source witness changed')
    return m
def validate(a,row):
    validate_literal(row);identity(a);c=scope();m=get(a)
    need(row['context']['session_id']==c['sessionId'],'Same actual SDK session')
    need(time.time()<c['lastNewUtcEpoch'],'Capabilities admission cutoff reached')
    need(m is None or m['uncertain'] is False and m['pending'] is None,'Prior event remains uncertain; no replay')
    count=0 if m is None else m['events']
    need(count<c['maxEvents'] and row['context']['capability_sequence']==count+1,'Finite exact capability cursor')
def save(a,m):
    text=canonical(m);need(len(text.encode('utf8'))<=65536,'Own metadata bound')
    a.world.runtime.set_snapshot_metadata(KEY,text)
def home(directory,a):
    p=Path(directory).resolve(strict=True);need(p.name==identity(a)['life_id'],'Owned exact artifact home')
    for q in (p,*p.parents):need(not q.is_symlink() and not(getattr(q.lstat(),'st_file_attributes',0)&1024),'No linked artifacts')
    out=p/FOLDER;out.mkdir(exist_ok=True);return out
def record(a,directory,m,event):
    row={'index':m['log_count'],'tick':int(a.tick),**event};data=(canonical(row)+'\n').encode('utf8')
    with (home(directory,a)/'events.jsonl').open('ab') as f:f.write(data);f.flush();os.fsync(f.fileno())
    m['log_count']+=1;m['log_chain_sha256']=hashlib.sha256(bytes.fromhex(m['log_chain_sha256'])+data).hexdigest();save(a,m)
def install(a):
    """Cold Python registration only; no Native metadata or physical input."""
    identity(a)
    from capacidades import rbx07_identity_v3 as original
    from capacidades import pi10_permiso_operativo_R02 as permission
    current=original.validate_external
    if getattr(current,'__sdk_capabilities_r06__',False):return
    def extended(owner,row,*,payload):
        if isinstance(row,dict) and row.get('modo')==MODE:
            need(payload.get('operacion')=='sesion' and payload.get('retorno')=='omit' and
                 payload.get('actuador')=='closed' and payload.get('situaciones')==[row],
                 'One explicit closed-actuator capability event')
            validate(owner,row);return
        return current(owner,row,payload=payload)
    extended.__sdk_capabilities_r06__=True
    original.validate_external=extended;permission.validate_external=extended
def dispatch(a,row,*,actuator='closed',directory=None):
    validate(a,row);need(actuator=='closed' and directory is not None,'Closed actual owner required')
    from capacidades import sdk_native_functions_R06 as tools
    from capacidades import pi10_consulta_adaptativa_R02 as b
    from capacidades import rbx07_native_v3 as core
    start=int(a.tick);c=scope();m=get(a)
    if m is None:
        a.world.runtime.set_snapshot_metadata(CODE_KEY,canonical(c))
        m={'version':VERSION,'scope':c,'initial_tick':start,'events':0,'pending':None,
           'uncertain':False,'log_count':0,'log_chain_sha256':'00'*32}
    old_core=dict(a.world.runtime.snapshot_metadata_entries)[CORE_KEY]
    timer=BoundedTime(a,m['initial_tick'],start);owned=TimedAdapter(a,timer)
    op=row['context']['operation_id'];request=row['request'];kind=request['kind'];deadline=start+4096
    primary=home(directory,a)/(op+'.json');need(not primary.exists(),'No primary overwrite or material replay')
    m.update(uncertain=True,pending={'context':row['context'],'request':request,'start_tick':start})
    record(a,directory,m,{'kind':'CAPABILITY_INTENT','context':row['context'],'request':request})
    try:
        life=c['lifeId'];options={'expected_life_id':life,'deadline_tick':deadline}
        if kind=='RECALL':value=tools.recall(owned,request['form'],**options)
        elif kind=='LESSON':value=tools.lesson(owned,request['form'],request['observedSign'],revision=request['revision'],teacher_mode=request['teacherMode'],**options)
        elif kind=='NUMERIC':value=tools.numeric(owned,request['operation'],request['left'],request['right'],**options)
        elif kind=='SOLVE':value=tools.solve(owned,request['form'],request['left'],request['right'],**options)
        elif kind=='COMPOSE':value=tools.compose(owned,request['forms'],request['data'],**options)
        else:
            from capacidades import acceso_eci01
            value=acceso_eci01.balance(owned,request['left'],request['right'])
        requested=normalized_requests(value);receipts=b.receipts(a,requested);counts=b.summary(receipts)
        need(requested,'Actual capability produced no identifiable Native requests')
        need(dict(a.world.runtime.snapshot_metadata_entries)[CORE_KEY]==old_core,'Core episode metadata changed')
        data={'schema':'DEE.Roblox.SDK.assisted_capability_primary.R06','lifeId':life,
              'sessionId':c['sessionId'],'context':row['context'],'request':request,
              'before_tick':start,'after_tick':int(a.tick),'nativeValue':value,
              'requests_normalized':receipts,'Native_inputs':counts,
              'inputAdmissionComplete':all(x['receipt']['status']=='applied' for x in receipts),
              'assistance':'Operator chose the request/order/cue/raw operands; existing Native mechanisms produced content.',
              'hostComputedAnswer':False,'monitor_samples':timer.samples,'coreEpisodeMetadataLiteral':True}
        raw=(canonical(data)+'\n').encode('utf8')
        with primary.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        out={'version':VERSION,'nativeTick':int(a.tick),'nativeTicks':int(a.tick)-start,
             'capabilitySequence':row['context']['capability_sequence'],'nativeValue':value,
             'Native_inputs':counts,'inputAdmissionComplete':data['inputAdmissionComplete'],
             'primary':{'path':str(primary.relative_to(Path(directory).resolve())),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()},
             'technicalControl':False,'assisted':True,'coreEpisodeCompleted':False}
        m.update(events=m['events']+1,pending=None,uncertain=False)
        record(a,directory,m,{'kind':'CAPABILITY_COMPLETED','context':row['context'],'result':out})
        return out
    except BaseException as error:
        m['uncertain']=True;m['failure']={'type':type(error).__name__,'tick':int(a.tick),'automaticRetry':False};save(a,m);raise
def operational_dependencies(a,directory):
    install(a);m=get(a)
    return {'version':VERSION,'present':m is not None,'events':0 if m is None else m['events'],
            'uncertain':False if m is None else m['uncertain'],'scopeSha256':sha(SCOPE),'new_ticks':0,
            'tickCountScope':'new_ticks=0 describes this passive inspection, not accumulated event doses',
            'assistedInterfaceNotAutonomousPlanner':True}
def uncertain(a):
    identity(a);m=get(a);return m is not None and bool(m['uncertain'])
def code_files():return (Path(__file__),Path(__file__).with_name('sdk_native_functions_R06.py'),SCOPE)

# BoundedTime, TimedAdapter and normalized_requests are copied mechanically from
# the actual SDK actor by the FS generator. They are not reimplemented here.

class HostSafetyStop(RuntimeError):
    pass

class BoundedTime:
    """Owner/agenda advances in <=16ticks, RAW-support checked each block."""
    def __init__(self, a, initial, cycle_start):
        self.a, self.initial, self.cycle_start, self.samples = a, initial, cycle_start, []

    def run_until(self, end):
        c = scope()
        need(int(end) >= int(self.a.tick), 'No rewind')
        need(int(end) - self.initial <= c['max_total_ticks'], 'Total Native budget')
        need(int(end) - self.cycle_start <= c['max_ticks_per_cycle'], 'Prospective whole-cycle Native budget')
        need(time.time() < c['native_cutoff_utc_epoch'], 'Finite Native wall cutoff')
        while int(self.a.tick) < int(end):
            need(time.time() < c['native_cutoff_utc_epoch'], 'Finite Native wall cutoff')
            self.a.run_until(min(int(end), int(self.a.tick) + 16))
            support = sum(int(x) != 0 for x in self.a.world.runtime.raw_copy())
            self.samples.append({'tick': int(self.a.tick), 'RAW_nonzero_support': support})
            if support > c['max_raw_support']:
                raise HostSafetyStop('HOST_SAFETY_STOP RAWsupport>10000; preserve')

class TimedAdapter:
    """Forward the existing owner; route every helper advance through safety."""
    def __init__(self, adapter, timer):
        self._adapter, self._timer = adapter, timer

    def __getattr__(self, name):
        return getattr(self._adapter, name)

    def run_until(self, tick):
        return self._timer.run_until(tick)

def normalized_requests(value):
    """Normalize legacy receipts without treating missing fields as zero.

    The full source tree remains byte-for-byte represented in the primary.
    Aliases are deduplicated by actual owner receipt ID, never counted twice.
    """
    found = {}
    def visit(v):
        if isinstance(v, list):
            for item in v:
                visit(item)
        elif isinstance(v, dict):
            if 'id' in v and ('channel' in v or 'port' in v):
                channel = v.get('channel', v.get('port'))
                payload = v['payload'] if 'payload' in v else v.get('value')
                tick = v['requested_tick'] if 'requested_tick' in v else v.get('tick')
                need(type(v['id']) is int and isinstance(channel, str)
                     and type(payload) is int and type(tick) is int,
                     'Exact receipt ID/channel/payload/tick required; no zero fill')
                row = {'id': v['id'], 'channel': channel, 'payload': payload,
                       'requested_tick': tick}
                need(v['id'] not in found or found[v['id']] == row,
                     'Conflicting aliases of one Native request')
                found[v['id']] = row
            for item in v.values():
                visit(item)
    visit(value)
    return [found[key] for key in sorted(found)]
