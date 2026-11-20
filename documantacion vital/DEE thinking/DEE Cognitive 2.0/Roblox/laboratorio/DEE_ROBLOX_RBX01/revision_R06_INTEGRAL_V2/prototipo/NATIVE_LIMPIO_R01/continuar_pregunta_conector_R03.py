"""Finish one existing CTRL1 episode after a proven unadmitted World message.
No first Native decision is repeated; only correct JSON string transport.
Refuses a different live World, a changed Native cut, or any other Native intent.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sys,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
b=load(HERE/'ejecutar_native_limpio_R02.py','_clean_base_R03')
def run(a):
 dest=a.destination.resolve(strict=True);out=a.output.resolve()
 b.need(dest==ROOT/'native/CTRL1'and not out.exists()and out.is_relative_to(ROOT/'evidencia'),'Exact pending root and new output')
 previous=b.read(ROOT/'evidencia/NATIVE_CONECTOR_LIMPIO_R02/RESULTADO_LIVE.json')
 b.need(previous['status']=='FAILED_PRESERVED'and len(previous['native_outputs'])==1 and not previous['body_acks'],'Exact original Q1-only failure')
 first=previous['native_outputs'][0];session=previous['session_id'];qid=first['operation_id']
 b.need(first['kind']=='decision'and first['result']['nativeTick']==954007 and first['result']['action']=='ASK_STATION','Exact already-computed Q1')
 life=previous['basis']['life']
 b.need(b.read(dest/'sistema/estado/vidas'/life/'VIDA.json')['physical']['tick']==954007,'No rollback/new future')
 b.need(not b.read(a.ledger)['intents'],'Other admitted Native phase must finish before resume')
 ol=[json.loads(x)for x in(dest/'ENSAYOS.jsonl').read_text('utf8').splitlines()if x.strip()]
 closed=[x for x in ol if x.get('kind')=='OWNER_CLOSED'][-1]
 b.need(closed['exit_code']==0 and closed['final_status']['running']is False and closed['final_status']['physical']['tick']==954007,'Exact closed pending owner')
 out.mkdir();events=out/'EVENTS.jsonl'
 def record(kind,**kw):
  with events.open('a',encoding='utf8')as f:f.write(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),kind=kind,**kw),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
 client=load(ROOT/'control/mcp_persistente_R06.py','_clean_resume_sdk')
 support=load(ROOT/'native/owner_support_integral_v2.py','_clean_resume_owner')
 adapters=load(ROOT/'native/adapter_integral_v2.py','_clean_resume_adapter')
 serial=0;done=[];acks=[];failure=None;owner=None;last_tick=954007
 with client.Session(a.studio_id,'DEEConnector_NATIVE_LIMPIO_R01.rbxlx',out/'MCP_SESSION',seconds=min(3600,int(b.CUTOFF-time.time())))as sdk:
  def mcp(code,label,ro=False):
   nonlocal serial
   serial+=1;code=b.typed_result_code(code);record('MCP_INTENT',label=label,code_sha256=hashlib.sha256(code.encode()).hexdigest())
   z=sdk.run('execute_luau',dict(studio_id=a.studio_id,datamodel_type='Server',code=code),out/f'MCP_{serial:03d}_{label}.json',180,read_only=ro)
   b.need(z['status']=='REPLIED','Known/unknown failure preserved, no auto retry')
   v=client.decode_text(z['reply']['result']);record('MCP_COMPLETED',label=label,result=v);return v
  def deliver(value,operation,observation):
   wire=dict(protocol='DEE.RBX.Connector.R01',namespace=observation['namespace'],sessionId=session,seq=observation['seq'],observationId=observation['observationId'],
    actionId=operation,operationId=operation,action=dict(name=value['action'],nativeTick=value['nativeTick'],null=value['null']),sourceKind='DEE_NATIVE')
   # Main.deliverAction expects raw JSON STRING, not a decoded Lua table.
   ack=mcp(b.HEADER+'return a:deliverAction('+b.literal(wire)+')','deliver_original_or_new_'+str(len(acks)))
   b.need(ack['actionId']==operation and ack['executionStatus']=='EXECUTED','Actual correlated action ACK')
   mcp(b.HEADER+'return a:confirmActionAck('+json.dumps(operation)+','+json.dumps(operation)+')','confirm_'+str(len(acks)))
   acks.append(ack);return ack
  try:
   status=mcp(b.HEADER+'return {status=a:status(),actionCount=#a.node.Actions:GetChildren()}','known_unadmitted_world_status',True)
   state=status['status'];mo=state['observation']
   b.need(status['actionCount']==0 and state['phase']=='AWAIT_ACTION'and state['sessionId']==session and state['sequence']==1 and state['actionCursor']==0 and
    mo['observationId']=='obs_675a3915-509a-453e-a483-cb6fcd1cb56a','Original Q1 World was never admitted, exact live continuation')
   record('CONTINUED_KNOWN_UNADMITTED',previous=str(ROOT/'evidencia/NATIVE_CONECTOR_LIMPIO_R02/RESULTADO_LIVE.json'),q1_id=qid,q1_not_reexecuted=True)
   deliver(first['result'],qid,mo)
   mo=mcp(b.HEADER+'return a:observe("ROUTE_CHOICE")','observe_actual_Q2')
   observation=b.native_observation(mo)
   owner=support.configured_owner(b.PRODUCT,dest,a.ledger,tag='R06_NATIVE_CLEAN_RESUME',cutoff_epoch=b.CUTOFF,continuous=True)
   with owner:
    adapter=adapters.create_adapter({'owner':owner})
    def native(kind,payload):
     nonlocal last_tick
     op='CLEAN_RESUME_'+kind.upper()+'_'+uuid.uuid4().hex[:16]
     context=dict(session_id=session,sequence=observation['seq'],observation_id=observation['observationId'],operation_id=op,mode='LIVE_NATIVE')
     record('NATIVE_INTENT',phase=kind,payload=payload,context=context)
     v=adapter.execute(kind,payload,context);last_tick=v['nativeTick'];done.append(dict(kind=kind,operation_id=op,result=v));record('NATIVE_COMPLETED',phase=kind,operation_id=op,result=v);return v,op
    second,op=native('query_sensor',{'observation':observation});ack=deliver(second,op,mo);r=ack['result']
    fields=dict(actionId=op,seq=observation['seq'],observationId=observation['observationId'],worldTimeMs=r['worldTimeMs'],durationMs=r['durationMs'],outcome=r['outcome'],
     collision=r['collision'],resourceCollected=r['resourceCollected'],resourceDelivered=r['resourceDelivered'],permissionSpent=sum(x['result'].get('permissionSpent',0)for x in acks),
     materialConsequence=bool(r['collision']or r['invalidAction']),lastObservation=observation)
    returned,fid=native('feedback',fields)
    mcp(b.HEADER+'return a:completeFeedback(H:JSONDecode('+b.literal(dict(actionId=op,feedbackOperationId=fid,nativeTick=last_tick))+'))','commit_same_opportunity')
    owner.control('guardar')
   b.need(owner.proc.poll()==0,'Owner closed before world checkpoint')
   checkpoint=mcp(b.HEADER+'return a:capture(H:JSONDecode('+b.literal(dict(backendWriterClosed=True,bridgeQuiescent=True,sessionId=session,lifeId=life,nativeTick=last_tick,proofKind='CLOSED_OFFICIAL_OWNER_AFTER_ACTUAL_FEEDBACK'))+'))','full_module_world_checkpoint')
   (out/'WORLD_MODULE_CHECKPOINT.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf8')
  except BaseException as ex:
   failure=type(ex).__name__+': '+str(ex);record('FAILED_PRESERVED',error=failure,no_retry=True)
 result=dict(schema='DEE.NativeCleanConnector.Continuation.R03',status='ONE_ORIGINAL_EPISODE_CLOSED'if failure is None else'FAILED_PRESERVED',life=life,session_id=session,
  source_tick=954007,parent_episode_tick=953651,last_confirmed_tick=last_tick,new_ticks_this_continuation=last_tick-954007,full_episode_ticks=last_tick-953651,
  original_q1=first,new_native_outputs=done,body_acks=acks,owner_closed=owner is not None and owner.proc is not None and owner.proc.poll()==0,failure=failure,
  assistance='Prepared sensors, ±6 actuators and resource; actual Native directions unchanged. Q1 transport repaired, not recomputed.',new_episode_created=False,principal_modified=False)
 (out/'RESULTADO_CONTINUACION.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 if failure:raise RuntimeError(failure)
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true');p.add_argument('--destination',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--studio-id',required=True)
 a=p.parse_args();b.need(a.execute_root_only,'Explicit Root continuation only');print(json.dumps(run(a),ensure_ascii=False,indent=2))
