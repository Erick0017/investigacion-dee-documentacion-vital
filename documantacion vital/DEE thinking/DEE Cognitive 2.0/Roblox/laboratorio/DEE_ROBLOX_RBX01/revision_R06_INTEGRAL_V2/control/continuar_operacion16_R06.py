"""Root-only continuation of ONE proved-not-admitted function, then17..28.

Never replays Q1/Q2 or movement16, never restores a past checkpoint and never
changes the actor/reader. Requires reconciliation proof and the original live
World in phaseTOOL16. The function keeps its original operation identifier.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sys,time
ROOT=Path(__file__).resolve().parents[1]
def load(p,name):
 s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
base=load(ROOT/'control/run_integrated_R06.py','_r06_resume_base')
transport=load(ROOT/'control/world_comprimido_R06.py','_r06_resume_world')
def execute(a):
 dest=a.destination.resolve(strict=True);out=a.output.resolve();old=a.interrupted.resolve(strict=True)
 base.need(dest==ROOT/'native/MAIN'and not out.exists()and out.parent==ROOT/'evidencia','Exact live candidate and fresh output')
 proof=base.read(a.reconciliation)
 # The separate proof must already have archived, not guessed, the absent ID.
 ledger=base.read(a.ledger);life=base.read(dest/'CONTEXTO_EJECUCION.json')['life']
 base.need(life not in ledger['intents'],'Known before-queue refusal must be reconciled explicitly first')
 prior=[json.loads(x)for x in(old/'EVENTS.jsonl').read_text('utf8').splitlines()if x.strip()]
 intent=next(x for x in reversed(prior)if x['kind']=='NATIVE_INTENT'and x.get('cycle')==16 and x.get('phase')=='function')
 ctx=intent['context'];opid=ctx['operation_id'];session=ctx['session_id']
 base.need(any(x.get('id')==opid for x in ledger.get('rejected_before_queue',[])),'Exact archived not-admitted ID required')
 actual=base.read(a.cached_tool)
 base.need(isinstance(actual.get('tool',{}).get('items'),list),'Authoritative cached Lua JSON array required')
 old_items=intent['payload']['tool']['items']
 base.need(isinstance(old_items,dict)and set(old_items)=={'1','2'}and actual['tool']['items']==[old_items['1'],old_items['2']],
  'Transport repair may change shape only, never experience content/order')
 card=base.read(dest/'sistema/estado/vidas'/life/'VIDA.json')
 base.need(card['physical']['tick']==971233,'No rollback or different future may be attached')
 out.mkdir();journal=out/'EVENTS.jsonl'
 def record(kind,**fields):
  with journal.open('a',encoding='utf8')as f:
   f.write(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'kind':kind,**fields},ensure_ascii=False,allow_nan=False)+'\n');f.flush();os.fsync(f.fileno())
 world=transport.CompressedWorld(a.studio_id,out,record)
 try:
  status=world.mcp("return require(game:GetService('ServerScriptService').RBX01Server.WorldAPI_R06).status()",'live_pending_status')
  base.need(status['phase']=='TOOL'and status['S']['cycle']==16 and status['S']['completedCycles']==15 and
   status['S']['nativeTick']==971233 and status['S']['sessionId']==session and status['S']['lifeId']==life,'Same original live half-op only')
  record('LIVE_PENDING_ATTACHED',status=status,proof_path=str(a.reconciliation),proof_sha256=base.sha(a.reconciliation),
   no_world_restore=True,no_Q1_Q2_or_movement_repeated=True,original_function_operation_id=opid)
  support=load(ROOT/'native/owner_support_integral_v2.py','_r06_resume_support')
  adapters=load(ROOT/'native/adapter_integral_v2.py','_r06_resume_adapter')
  rows=[]
  with support.configured_owner(base.PRODUCT,dest,a.ledger,tag='R06_CONTINUAR_C16',cutoff_epoch=1794802380,continuous=True)as owner:
   adapter=adapters.create_adapter({'owner':owner})
   def native(kind,payload,obs,cycle,context=None):
    identifier='R06_'+session+'_'+str(cycle).zfill(2)+'_'+kind.upper()
    c=context or{'session_id':session,'sequence':obs['seq'],'observation_id':obs['observationId'],'operation_id':identifier,'mode':'LIVE_NATIVE'}
    record('NATIVE_INTENT',cycle=cycle,phase=kind,payload=payload,context=c)
    start=time.perf_counter();v=adapter.execute(kind,payload,c)
    record('NATIVE_COMPLETED',cycle=cycle,phase=kind,operation_id=c['operation_id'],result=v,wall_seconds=time.perf_counter()-start)
    return v,c['operation_id']
   # Complete the already physically executed original16, without another action.
   made,function_id=native('function',{'tool':actual['tool']},None,16,ctx)
   prefix='WORLD_'+session+'_16_'
   applied=world.call(prefix+'TOOL','tool',{'output':made['toolResult'],'nativeTick':made['nativeTick'],'operationId':function_id})
   fields=world.call(prefix+'FEEDBACK_FIELDS','feedback_fields',{})
   returned,fid=native('feedback',fields['feedback'],fields['observation'],16)
   final=world.call(prefix+'COMPLETE','complete',{'nativeTick':returned['nativeTick'],'operationId':fid})
   q1=next(x['result']for x in reversed(prior)if x['kind']=='NATIVE_COMPLETED'and x.get('cycle')==16 and x.get('phase')=='decision')
   q2=next(x['result']for x in reversed(prior)if x['kind']=='NATIVE_COMPLETED'and x.get('cycle')==16 and x.get('phase')=='query_sensor')
   row={'cycle':16,'new_opportunity':12,'Native_Q1':q1,'Native_Q2':q2,'tool_result':made['toolResult'],
    'actual_numeric':None,'world_result':applied['result'],'executed_route':actual['executed_name'],'Native_route':actual['selected_name'],
    'state_after':final['S'],'boundary':final['boundary'],'host_order_prepared':True,
    'Q1_Q2_and_motion_from_interrupted_prefix':True,'original_function_ID_reused_after_proved_nonadmission':True}
   rows.append(row);record('OPPORTUNITY_COMPLETED',**row)
   for cycle in range(17,29):
    base.need(time.time()<1794798600,'Same prospective new episode cutoff')
    prefix='WORLD_'+session+'_'+str(cycle).zfill(2)+'_'
    begun=world.call(prefix+'BEGIN','begin',{'cycle':cycle});obs=begun['observation']
    first,first_id=native('decision',{'observation':obs},obs,cycle)
    moved=world.call(prefix+'Q1','action',{'action':{'name':first['action'],'actionId':first_id,'nativeTick':first['nativeTick'],'null':first.get('null',False)}})
    route=None;tool=None;number=None
    if 'observation'in moved:
     obs=moved['observation'];route,rid=native('query_sensor',{'observation':obs},obs,cycle)
     moved=world.call(prefix+'Q2','action',{'action':{'name':route['action'],'actionId':rid,'nativeTick':route['nativeTick'],'null':route.get('null',False)}})
    if moved.get('tool'):
     made,mid=native('function',{'tool':moved['tool']},obs,cycle);tool=made['toolResult'];number=tool.get('numeric_result')
     applied=world.call(prefix+'TOOL','tool',{'output':tool,'nativeTick':made['nativeTick'],'operationId':mid})
     moved['result']=applied['result']
    fields=world.call(prefix+'FEEDBACK_FIELDS','feedback_fields',{})
    returned,fid=native('feedback',fields['feedback'],fields['observation'],cycle)
    final=world.call(prefix+'COMPLETE','complete',{'nativeTick':returned['nativeTick'],'operationId':fid})
    row={'cycle':cycle,'new_opportunity':cycle-4,'Native_Q1':first,'Native_Q2':route,'tool_result':tool,
     'actual_numeric':number,'world_result':moved['result'],'executed_route':moved.get('executed_name'),
     'Native_route':moved.get('selected_name'),'state_after':final['S'],'boundary':final['boundary'],'host_order_prepared':cycle<=22}
    rows.append(row);record('OPPORTUNITY_COMPLETED',**row)
   saved=owner.control('guardar');record('OFFICIAL_SAVE_COMPLETED',request_id=saved.get('id'))
  record('OWNER_CLOSED',life=life,expected_tick=rows[-1]['state_after']['nativeTick'])
  final=world.checkpoint('R06_PAIR_'+session+'_C28',out/'WORLD_CHECKPOINT.json')
  result={'schema':'DEE.RBX01.R06.integrated.result.R01','identity':{'life':life,'session':session,'participant':'LIVE_NATIVE'},
   'source_tick':971233,'final_tick':final['native_tick'],'new_opportunities_completed':len(rows),'global_completed':28,
   'rows':rows,'owner_closed':True,'new_Native_ticks':final['native_tick']-971233,
   'continued_partial_original_opportunity':16,'earlier_partial_ticks_in_interrupted_dataset':378,
   'world_checkpoint':str(out/'WORLD_CHECKPOINT.json'),'world_sha256':base.sha(out/'WORLD_CHECKPOINT.json'),
   'principal_modified':False,'new_scenario_sha256':final['scenario_sha256']}
  (out/'RESULTADO.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
  print(json.dumps({k:v for k,v in result.items()if k!='rows'},ensure_ascii=False))
 finally:world.close()
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true')
 for n in('destination','output','interrupted','ledger','reconciliation','cached-tool'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--studio-id',required=True);a=p.parse_args();base.need(a.execute_root_only,'Root-only explicit phase continuation');execute(a)
