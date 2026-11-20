"""Explicit R07 reference execution using the same World transport. No DEE import.

The caller is the root executor. Import alone opens no Studio/model connection.
PROGRAMMED/AI retain their own durable histories and source pins across reopen.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import sys
import time
import uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'control'))
sys.path.insert(0,str(ROOT/'comparadores'))
from world_comprimido_v3 import CompressedWorld
from backends_v3 import create_backend

CUTOFF=1794859200  #2026-11-16 20:00 UTC; no new episode after this instant.
HARD_CLOSE=1794863220

def need(condition,message):
    if not condition:raise ValueError(message)
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()

def execute(a):
    need(a.execute_root_only,'Explicit Root execution required')
    source=a.world.resolve();destination=a.destination.resolve();output=a.output.resolve()
    need(source.is_file() and not source.is_symlink(),'Existing explicit source World')
    need(not output.exists() and output.is_relative_to(ROOT/'evidencia'),'Fresh R07 evidence output')
    need(destination.is_relative_to(ROOT/'comparadores') and not destination.is_symlink(),'Isolated R07 reference history')
    need(a.resume or not destination.exists() or not any(destination.iterdir()),'Do not reuse a policy ID/history')
    state=read(source)
    need(state['world_id'] in ('RBX01_INTEGRAL_V2_R06','RBX01_CIERRE8_R07'),'Explicit parent or R07 continuation')
    need(29<=a.stop_cycle<=52 and a.stop_cycle>=state['boundary']['next_opportunity'],'Finite R07 cursor')
    if not a.resume:
        need(state['S']['completedCycles']==28 and state['native_tick']==991187,'First comparison starts at exact PAR28 environment')
    else:
        need(state['world_id']=='RBX01_CIERRE8_R07','Resume requires this revision checkpoint')
        need(bool(a.session),'Resume requires original explicit session')
    need(time.time()<CUTOFF,'Prospective new-episode cutoff reached before opening reference')
    output.mkdir(parents=True)
    journal=output/'EVENTS.jsonl'
    def record(kind,**fields):
        with journal.open('a',encoding='utf-8')as f:
            f.write(json.dumps({'utc':utc(),'kind':kind,**fields},ensure_ascii=False,allow_nan=False)+'\n')
            f.flush();os.fsync(f.fileno())
    session=a.session or 'R07_'+a.participant+'_'+uuid.uuid4().hex[:12]
    identity={'life':'R07_'+a.participant,'session':session,'participant':a.participant,'diagnostic':False}
    world=CompressedWorld(a.studio_id,output,record,expected_place=a.expected_place)
    backend=None;rows=[];failure=None
    try:
        restored=world.initialize(state,identity,sha(source))
        record('RESTORED',result=restored,identity=identity,source_world_sha256=sha(source),
               initial_environment_from_PAR28=True,Native_memory_loaded=False,
               prepared_public_prior={'luma':1,'nara':-1,'A':11,'B':None},
               prior_knowledge_equivalent_to_Native=False)
        backend=create_backend(a.participant,destination,session_id=session,resume=a.resume)
        record('PROTOCOL_STARTED',participant=a.participant,identity=identity,
               source_world=str(source),source_environment_native_tick=state['native_tick'],
               Native_loaded=False,port_overrides=False,host_pathfinding_geometry_only=True,
               prospective_cutoff_epoch=CUTOFF,source_code_sha256=sha(__file__))
        def invoke(kind,payload,obs,cycle):
            op='R07_'+session+'_'+str(cycle).zfill(2)+'_'+kind.upper()
            context={'session_id':session,'sequence':obs['seq'],'observation_id':obs['observationId'],
                     'operation_id':op,'mode':a.participant}
            record('BACKEND_INTENT',cycle=cycle,phase=kind,payload=payload,context=context)
            started=time.perf_counter()
            result=backend.execute(kind,payload,context)
            record('BACKEND_COMPLETED',cycle=cycle,phase=kind,operation_id=op,
                   result=result,wall_seconds=time.perf_counter()-started)
            return result,op
        for cycle in range(state['boundary']['next_opportunity'],a.stop_cycle+1):
            need(time.time()<CUTOFF,'Prospective new-episode cutoff; preserve completed prefix')
            base='WORLD_'+session+'_'+str(cycle).zfill(2)+'_'
            begun=world.call(base+'BEGIN','begin',{'cycle':cycle});obs=begun['observation']
            first,op=invoke('decision',{'observation':obs},obs,cycle)
            moved=world.call(base+'Q1','action',{'action':{'name':first['action'],'actionId':op,
                   'nativeTick':0,'null':first.get('null',False)}})
            route=None;tool=None;actual=None
            if 'observation'in moved:
                obs=moved['observation'];route,op=invoke('query_sensor',{'observation':obs},obs,cycle)
                moved=world.call(base+'Q2','action',{'action':{'name':route['action'],'actionId':op,
                       'nativeTick':0,'null':route.get('null',False)}})
            if moved.get('tool'):
                made,function_id=invoke('function',{'tool':moved['tool']},obs,cycle)
                tool=made['toolResult'];actual=tool.get('numeric_result')
                applied=world.call(base+'TOOL','tool',{'output':tool,'nativeTick':0,'operationId':function_id})
                moved['result']=applied['result']
            fields=world.call(base+'FEEDBACK_FIELDS','feedback_fields',{})
            feedback,feedback_id=invoke('feedback',fields['feedback'],fields['observation'],cycle)
            need(feedback.get('accepted')is True,'Reference feedback not acknowledged')
            final=world.call(base+'COMPLETE','complete',{'nativeTick':0,'operationId':feedback_id})
            row={'cycle':cycle,'new_opportunity':cycle-28,'Native_Q1':first,'Native_Q2':route,
                 'tool_result':tool,'actual_numeric':actual,'world_result':moved['result'],
                 'executed_route':moved.get('executed_name'),'Native_route':moved.get('selected_name'),
                 'state_after':final['S'],'boundary':final['boundary'],'host_order_prepared':False,
                 'field_Native_Q_is_transport_compatibility_not_DEE':True}
            rows.append(row);record('OPPORTUNITY_COMPLETED',**row)
        saved=backend.checkpoint();record('REFERENCE_CHECKPOINT_SAVED',result=saved)
        final=world.checkpoint('R07_PAIR_'+session+'_C'+str(a.stop_cycle),output/'WORLD_CHECKPOINT.json')
        result={'schema':'DEE.RBX01.R07.reference.result.v1','participant':a.participant,'identity':identity,
                'source_environment_tick':state['native_tick'],'source_tick':0,'final_tick':0,
                'new_opportunities_completed':len(rows),'global_completed':final['S']['completedCycles'],
                'rows':rows,'owner_closed':False,'new_Native_ticks':0,'Native_engine_loaded':False,
                'world_checkpoint':str(output/'WORLD_CHECKPOINT.json'),
                'world_sha256':sha(output/'WORLD_CHECKPOINT.json'),'principal_modified':False,
                'new_scenario_sha256':final['scenario_sha256'],'source_world_sha256':sha(source)}
    except BaseException as error:
        failure=error
        record('FAILED_PRESERVED',exception=type(error).__name__,detail=str(error),completed_new=len(rows),
               no_automatic_retry=True,no_synthetic_completion=True)
        partial={'schema':'DEE.RBX01.R07.reference.partial.v1','identity':identity,'rows':rows,
                 'completed_new':len(rows),'exception':type(error).__name__,'detail':str(error),
                 'world_state_may_be_nonboundary':True,'Native_executed':False}
        (output/'RESULTADO_PARCIAL.json').write_text(json.dumps(partial,indent=2,ensure_ascii=False),encoding='utf-8')
        raise
    finally:
        if backend is not None:backend.close()
        world.close()
        record('REFERENCE_OWNER_CLOSED',uncertain=failure is not None,Native_executed=False)
    result['owner_closed']=True
    (output/'RESULTADO.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items()if k!='rows'},ensure_ascii=False))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--execute-root-only',action='store_true')
    p.add_argument('--participant',required=True,choices=('PROGRAMMED','CONVENTIONAL_AI'))
    p.add_argument('--destination',type=Path,required=True);p.add_argument('--world',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--studio-id',required=True)
    p.add_argument('--expected-place',default='DEE_RBX01_R07_NATIVE.rbxlx')
    p.add_argument('--stop-cycle',type=int,required=True);p.add_argument('--session');p.add_argument('--resume',action='store_true')
    execute(p.parse_args())
