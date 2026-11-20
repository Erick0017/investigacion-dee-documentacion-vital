"""Root-only six-opportunity lexical contingency control, no Roblox claims.

Stdlib on import. The default CLI shows the frozen protocol only. Explicit
--execute-root-only opens the existing official bounded owner on a fresh,
complete MEMPAIR/MEMCTRL clone. No Runtime creation, Native field edit, new
decoder, expected-result input, action retry or principal selection exists.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import json
import os
import re
import time
import uuid

BASE = Path(__file__).resolve().parents[1]
PRODUCT = BASE.parents[2]
PROTOCOL = BASE/'protocolo/CONTROL_MEMORIA_RESERVA_C02.json'
CUTOFF = 1794738600
SOURCE_TICK = 947395
LIFE_PREFIX = 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_'


def need(ok, text):
    if not ok: raise ValueError(text)


def canonical(value):
    return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value)
    return value


def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))


def check_no_links(path):
    for part in (path,*path.parents):
        need(not part.is_symlink() and not (part.exists() and getattr(part.lstat(),'st_file_attributes',0)&1024),
             'No symlink/reparse path')


def protocol(expected_sha256=None):
    raw=PROTOCOL.read_bytes(); sha=hashlib.sha256(raw).hexdigest()
    need(expected_sha256 is None or expected_sha256==sha,'Protocol changed; no execution')
    value=json.loads(raw)
    need(value['schema']=='DEE.RBX01.C02.reserved_memory_contingency.R01'
         and value['opportunities']==6 and value['frozen']is True,'Exact frozen6 protocol')
    return value,sha


def step_tool(index, actual_intermediate):
    """Prepared opportunities; transport only a previously produced integer."""
    need(type(index)is int and 1<=index<=6,'One of six frozen opportunities')
    if index==3:
        return {'kind':'LESSON','items':[{'form':'luma','observedSign':-1},
                                         {'form':'nara','observedSign':1}]}
    if index in(2,5):
        if type(actual_intermediate)is not int or not 0<=actual_intermediate<=32:
            return None
        return {'kind':'CALCULATE','slot':'B','form':'nara','left':actual_intermediate,'right':1}
    left,right=(7,3)if index==6 else(6,2)
    return {'kind':'CALCULATE','slot':'A','form':'luma','left':left,'right':right}


def expected_for_audit(index, actual_intermediate):
    """Evaluator only, called AFTER response, never placed in Native input."""
    if index==3:return None
    if index in(2,5):
        if type(actual_intermediate)is not int or not 0<=actual_intermediate<=32:return None
        return actual_intermediate-1 if index==2 else actual_intermediate+1
    if index==1:return 8
    return 4


def observation(sequence, phase, previous_action, last_failure):
    # Focal operator-opened device, not navigation or an autonomously discovered
    # interface. Query availability is false in BOTH arms, preventing paid input.
    return {'observationId':'FOCAL_OBS_'+str(sequence).zfill(4),'seq':sequence,
            'phase':phase,'worldTimeMs':sequence*1000,'sampleTimeMs':sequence*1000,
            'previousActionId':previous_action,
            'sensors':{'station':0,'stage':0,'contact':0,'inventoryKey':False,
                       'inventoryResource':False,'queryAvailable':False,
                       'stationSignal':-1,'permissionStock':200,'publicContactCode':0,
                       'lastFailure':last_failure}}


def run_sequence(adapter, session_id, record):
    """Exactly existing public C02 phases; adapter supplied by one owned clone."""
    previous=None;last_failure=False;actual_a=None;rows=[];sequence=0
    for index in range(1,7):
        sequence+=1;obs=observation(sequence,'QUERY_CHOICE',previous,last_failure)
        def invoke(kind,payload,obs):
            operation='C02_FOCAL_'+session_id+'_'+str(index).zfill(2)+'_'+kind.upper()
            context={'session_id':session_id,'sequence':obs['seq'],
                     'observation_id':obs['observationId'],'operation_id':operation,'mode':'LIVE_NATIVE'}
            record('INTENT',index=index,kind=kind,payload=payload,context=context)
            value=adapter.execute(kind,payload,context)
            record('COMPLETED',index=index,kind=kind,operation_id=operation,result=value)
            return value,operation
        first,first_id=invoke('decision',{'observation':obs},obs)
        actual=None;tool=None;tool_result=None;abort=False
        if first.get('null')is True:
            action_id=first_id;abort=True
        else:
            need(first['action']=='SKIP_STATION','Unavailable query must not release ASK')
            sequence+=1;obs=observation(sequence,'ROUTE_CHOICE',first_id,last_failure)
            second,action_id=invoke('query_sensor',{'observation':obs},obs)
            tool=step_tool(index,actual_a)
            if tool is not None:
                made,_=invoke('function',{'tool':tool},obs)
                tool_result=made['toolResult']
                actual=tool_result.get('numeric_result')
        # No correctness/desired sign is converted into a teaching instruction.
        # Same generic failure law: absence of an actual numeric result, or a
        # missing actual prior operand. A formed wrong number is NOT suppressed.
        last_failure=abort or (index!=3 and actual is None)
        feedback={'actionId':action_id,'seq':obs['seq'],'observationId':obs['observationId'],
                  'worldTimeMs':sequence*1000+250,'durationMs':250,
                  'outcome':'TOOL_NO_RESULT'if last_failure else'MOVED',
                  'collision':False,'resourceCollected':False,'resourceDelivered':False,
                  'permissionSpent':0,'materialConsequence':bool(last_failure),'lastObservation':obs}
        returned,_=invoke('feedback',feedback,obs)
        expected=expected_for_audit(index,actual_a)
        row={'index':index,'tool':tool,'tool_result':tool_result,'actual_numeric':actual,
             'evaluator_only_expected':expected,'correct_if_numeric_opportunity':
             (None if index==3 or expected is None else type(actual)is int and actual==expected),
             'formed':type(actual)is int,'actual_intermediate_used':actual_a if index in(2,5) else None,
             'generic_material_failure':bool(last_failure),'after_tick':returned.get('nativeTick'),
             'Native_Q1_NULL':abort,'route_selected_by_Native':not abort,
             'function_opportunity_and_order_prepared':True}
        rows.append(row);record('OPPORTUNITY_CLOSED',**row)
        if index in(1,4):actual_a=actual
        previous=action_id
        if abort:break
    return {'opportunities_requested':6,'opportunities_completed':len(rows),'rows':rows,
            'pipeline':'prepared opportunities; Native lexical sign selects opcode; Native integer carried unchanged',
            'Roblox_executed':False,'autonomous_plan_demonstrated':False}


def preflight(destination, ledger, output, expected_protocol_sha256):
    destination=Path(destination).resolve(strict=True);ledger=Path(ledger).resolve(strict=True)
    output=Path(output).resolve();check_no_links(destination);check_no_links(output)
    need(destination.parent==(BASE/'native').resolve(),'Only explicit C02 native clone')
    context=read(destination/'CONTEXTO_EJECUCION.json');life=context['life']
    need(life in(LIFE_PREFIX+'MEMPAIR',LIFE_PREFIX+'MEMCTRL'),'Only fresh memory-control IDs; no MAIN/DEV/principal')
    need(not(output.exists()) and output.parent.is_dir() and output.is_relative_to(BASE/'evidencia'),
         'New absent evidence directory below existing C02 evidencia parent')
    need(ledger.is_relative_to(BASE) and read(ledger).get('intent')is None,'Existing shared ledger, no pending intent')
    scope=read(destination/'sistema/capacidades/RBX02_NATIVE_SCOPE_C02.json')
    mode='paired'if life.endswith('MEMPAIR')else'desync'
    need(scope['role']=='control'and scope['max_cycles']==6 and scope['teacher_mode']==mode
         and scope['feedback_arm']=='real'and scope['native_cutoff_utc_epoch']==CUTOFF,
         'Frozen matched control scope; never edit modes at execution')
    card=read(destination/'sistema/estado/vidas'/life/'VIDA.json')
    need(card['physical']['tick']==SOURCE_TICK,'Fresh coherent source only, not a restarted learned control')
    imported=read(destination/'IMPORTACION_DIAGNOSTICA.json')
    need(imported['new_native_ticks']==0 and imported['comparison']['physical_equal']
         and imported['comparison']['causal_prefix_equal'],'Verified complete import0 required')
    closure=load(BASE/'native/rbx02_import0_C02.py','_C02_focal_closed_preflight')
    need(closure.closed(destination),'Clone owner, queue, WAL and locks must be coherently closed')
    _,ph=protocol(expected_protocol_sha256)
    need(time.time()<scope['last_new_cycle_utc_epoch'],'Prospective new-Q1 cutoff; do not begin control')
    return destination,ledger,output,life,mode,ph


def execute_root_only(destination,ledger,output,expected_protocol_sha256):
    destination,ledger,output,life,mode,ph=preflight(destination,ledger,output,expected_protocol_sha256)
    output.mkdir();journal=output/'Fases.jsonl';session='FOCAL_'+life.rsplit('_',1)[-1]+'_'+uuid.uuid4().hex[:12]
    def record(event,**data):
        row={'event':event,'utc_epoch':time.time(),'life':life,**data}
        with journal.open('a',encoding='utf8')as f:
            f.write(canonical(row)+'\n');f.flush();os.fsync(f.fileno())
    record('PROTOCOL_STARTED',protocol_sha256=ph,teacher_mode=mode,session=session,
           code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    support=load(BASE/'fuentes/rbx02_owner_support_C02.py','_C02_focal_support')
    adapters=load(BASE/'native/rbx02_adapter_C02.py','_C02_focal_adapter')
    # The sole Native process is the preserved official owner, opened explicitly
    # HERE, not on import or when showing the protocol. Root alone invokes it.
    with support.configured_owner(PRODUCT,destination,ledger,tag='C02_FOCAL_'+mode,
                                  cutoff_epoch=CUTOFF,continuous=True)as owner:
        result=run_sequence(adapters.create_adapter({'owner':owner}),session,record)
        saved=owner.control('guardar')
        record('OFFICIAL_SAVE_COMPLETED',request_id=saved.get('id'))
    result.update(schema='DEE.RBX01.C02.reserved_memory_control.result.R01',life_id=life,
                  teacher_mode=mode,protocol_sha256=ph,owner_closed=True,
                  source_tick=SOURCE_TICK,session=session,adopted=False)
    with(output/'RESULTADO.json').open('x',encoding='utf8')as f:f.write(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--execute-root-only',action='store_true')
    parser.add_argument('--destination',type=Path)
    parser.add_argument('--ledger',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--protocol-sha256')
    args=parser.parse_args()
    if not args.execute_root_only:
        value,sha=protocol();print(json.dumps({'protocol_sha256':sha,'protocol':value},ensure_ascii=False,indent=2))
    else:
        need(all((args.destination,args.ledger,args.output,args.protocol_sha256)),
             'Explicit diagnostic paths and prospectively pinned protocol SHA256 required')
        print(json.dumps(execute_root_only(args.destination,args.ledger,args.output,args.protocol_sha256),ensure_ascii=False,indent=2))
