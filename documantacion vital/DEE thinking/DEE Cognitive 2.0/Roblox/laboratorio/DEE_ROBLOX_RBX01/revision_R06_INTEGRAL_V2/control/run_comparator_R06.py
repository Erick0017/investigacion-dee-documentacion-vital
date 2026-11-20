"""Explicit real reference run on the same R06 world. No DEE import/owner.

Shares the World codec/action/ACK boundary implementation with the Native run.
Only the participant backend differs. A comparison of configurations, not equal
innate knowledge or an equal prior-training intelligence ranking.
"""
from pathlib import Path
import argparse,datetime,importlib.util,json,os,sys,time,uuid
sys.path.insert(0,str(Path(__file__).resolve().parent))
from run_integrated_R06 import World,ROOT,read,sha,need
sys.path.insert(0,str(ROOT/'comparadores'))
from backends_R06 import create_backend
def execute(a):
 protocol=read(ROOT/'protocolo/PROTOCOLO_INTEGRAL_V2_R01.json')
 cutoff=datetime.datetime.fromisoformat(protocol['deadline_new_episodes_utc'].replace('Z','+00:00')).timestamp()
 output=a.output.resolve();destination=a.destination.resolve()
 need(not output.exists() and output.is_relative_to(ROOT/'evidencia'),'Fresh R06 evidence output')
 need(destination.is_relative_to(ROOT/'comparadores') and (a.resume or not destination.exists()),'Fresh explicit reference history or explicit same-history resume')
 state=read(a.world);need(5<=a.stop_cycle<=28 and a.stop_cycle>=state['boundary']['next_opportunity'],'Finite R06 range')
 output.mkdir(parents=True);journal=output/'EVENTS.jsonl'
 def record(kind,**fields):
  with journal.open('a',encoding='utf8')as f:
   f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':kind,**fields},ensure_ascii=False,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
 session=a.session or 'R06_'+a.participant+'_'+uuid.uuid4().hex[:12]
 identity={'life':'R06_'+a.participant,'session':session,'participant':a.participant}
 world=World(a.studio_id,output,record)
 restored=world.initialize(state,identity,sha(a.world));record('RESTORED',result=restored,identity=identity,
  initial_environment_from_DEV4=True,Native_memory_loaded=False,associations_prepared_for_reference={'luma':-1,'nara':1})
 backend=create_backend(a.participant,destination,session_id=session,resume=a.resume)
 rows=[];record('PROTOCOL_STARTED',protocol_sha256=sha(ROOT/'protocolo/PROTOCOLO_INTEGRAL_V2_R01.json'),
  participant=a.participant,identity=identity,source_world=str(a.world),source_tick=0,Native_loaded=False)
 def invoke(kind,payload,obs,cycle):
  op='R06_'+session+'_'+str(cycle).zfill(2)+'_'+kind.upper()
  ctx={'session_id':session,'sequence':obs['seq'],'observation_id':obs['observationId'],'operation_id':op,'mode':a.participant}
  record('BACKEND_INTENT',cycle=cycle,phase=kind,payload=payload,context=ctx)
  started=time.perf_counter();out=backend.execute(kind,payload,ctx)
  record('BACKEND_COMPLETED',cycle=cycle,phase=kind,operation_id=op,result=out,wall_seconds=time.perf_counter()-started)
  return out,op
 try:
  for cycle in range(state['boundary']['next_opportunity'],a.stop_cycle+1):
   need(time.time()<cutoff,'Prospective new episode cutoff')
   base='WORLD_'+session+'_'+str(cycle).zfill(2)+'_'
   begun=world.call(base+'BEGIN','begin',{'cycle':cycle});obs=begun['observation']
   first,first_id=invoke('decision',{'observation':obs},obs,cycle)
   moved=world.call(base+'Q1','action',{'action':{'name':first['action'],'actionId':first_id,'nativeTick':0,'null':first.get('null',False)}})
   route=None;tool=None;actual=None
   if 'observation' in moved:
    obs=moved['observation'];route,op_id=invoke('query_sensor',{'observation':obs},obs,cycle)
    moved=world.call(base+'Q2','action',{'action':{'name':route['action'],'actionId':op_id,'nativeTick':0,'null':route.get('null',False)}})
   if moved.get('tool'):
    made,function_id=invoke('function',{'tool':moved['tool']},obs,cycle);tool=made['toolResult'];actual=tool.get('numeric_result')
    applied=world.call(base+'TOOL','tool',{'output':tool,'nativeTick':0,'operationId':function_id})
    moved['result']=applied['result']
   fields=world.call(base+'FEEDBACK_FIELDS','feedback_fields',{})
   returned,feedback_id=invoke('feedback',fields['feedback'],fields['observation'],cycle)
   need(returned.get('accepted') is True,'Reference feedback not acknowledged')
   final=world.call(base+'COMPLETE','complete',{'nativeTick':0,'operationId':feedback_id})
   row={'cycle':cycle,'new_opportunity':cycle-4,'Native_Q1':first,'Native_Q2':route,'tool_result':tool,
    'actual_numeric':actual,'world_result':moved['result'],'executed_route':moved.get('executed_name'),
    'Native_route':moved.get('selected_name'),'state_after':final['S'],'boundary':final['boundary'],
    'host_order_prepared':cycle<=22,'field_Native_Q_is_transport_compatibility_not_DEE':True}
   rows.append(row);record('OPPORTUNITY_COMPLETED',**row)
  saved=backend.checkpoint();record('REFERENCE_CHECKPOINT_SAVED',result=saved)
 finally:backend.close()
 final=world.checkpoint('R06_PAIR_'+session+'_C'+str(a.stop_cycle),output/'WORLD_CHECKPOINT.json')
 result={'schema':'DEE.RBX01.R06.integrated.result.R01','participant':a.participant,'identity':identity,
 'source_tick':0,'final_tick':0,'new_opportunities_completed':len(rows),'global_completed':a.stop_cycle,
 'rows':rows,'owner_closed':True,'new_Native_ticks':0,'Native_engine_loaded':False,
 'world_checkpoint':str(output/'WORLD_CHECKPOINT.json'),'world_sha256':sha(output/'WORLD_CHECKPOINT.json'),
 'principal_modified':False,'new_scenario_sha256':final['scenario_sha256']}
 (output/'RESULTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({k:v for k,v in result.items()if k!='rows'},ensure_ascii=False))
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true')
 p.add_argument('--participant',required=True,choices=('PROGRAMMED','CONVENTIONAL_AI'))
 p.add_argument('--destination',type=Path,required=True);p.add_argument('--world',type=Path,required=True)
 p.add_argument('--output',type=Path,required=True);p.add_argument('--studio-id',required=True)
 p.add_argument('--stop-cycle',type=int,required=True);p.add_argument('--session');p.add_argument('--resume',action='store_true')
 a=p.parse_args();need(a.execute_root_only,'Explicit Root material run only');execute(a)
