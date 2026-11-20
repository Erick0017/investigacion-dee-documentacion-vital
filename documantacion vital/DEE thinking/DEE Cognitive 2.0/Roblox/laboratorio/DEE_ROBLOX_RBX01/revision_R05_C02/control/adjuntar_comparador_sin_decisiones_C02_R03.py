"""Root-only ONE first start on an existing zero-decision comparator host.

No owner/model/policy process is started, reopened or terminated. A separate
relay supplies the existing original observer path; the original supervisor
gets first opportunity to export/seal. This helper waits its RESULTADO before
any fallback capture. Never retries an unknown START or policy request.
"""
from pathlib import Path
import argparse,datetime,importlib.util,json,os,subprocess,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def run(a):
 v=load('control/orquestar_comparador_C02_R03.py','_attach_comparator_util');u=v.u
 identity=load('control/adjuntar_propietario_sin_material_C02_R06.py','_attach_process_identity')
 u.need(a.root_run,'Root-only explicit action')
 original,directory,config,out=map(u.safe,(a.original_output,a.policy_directory,a.config,a.output))
 u.need(not out.exists()and out.is_relative_to(ROOT/'evidencia'),'Fresh evidence output only')
 u.need(time.time()<a.cutoff_utc_epoch-240 and a.cutoff_utc_epoch<=v.HARD_FINISH,'Prospective finite comparator drain margin required')
 u.need(a.participant in v.FILES and not(original/'START_INTENT.json').exists(),'No prior START may have been attempted')
 rows=[json.loads(x)for x in(original/'supervisor.jsonl').read_text('utf8').splitlines()if x.strip()]
 hosts=[x for x in rows if x.get('kind')=='ONE_COMPARATOR_HOST_STARTED']
 u.need(len(hosts)==1 and hosts[0]['pid']==a.host_pid and identity.alive(a.host_pid),'Exact existing comparator host required')
 command=hosts[0]['command']
 for key,value in[('--participant',a.participant),('--run-id',a.run_id),('--policy-directory',str(directory)),('--config',str(config))]:
  u.need(command[command.index(key)+1]==value,'Original host argument identity mismatch')
 u.need(not(original/'RESULTADO.json').exists(),'Original supervisor already ended; reconcile it')
 c=u.read(config);u.need(c.get('worldId')==v.WORLD_ID and c.get('port')==8895 and c.get('allowControl')is True,'Fixed comparator bridge only')
 database=u.safe(ROOT/'configuracion_privada'/c['databaseFile'])
 def zero():
  state=u.bridge_read(database)
  u.need(state and state['session']is None and state['boundary']is None and not state['operation_counts'],'Bridge already has a session, decision or operation')
  u.need(state['pending']==state['uncertain']==state['unacknowledged_actions']==state['unacknowledged_tools']==state['feedback_operations_completed']==0,'Pending/uncertain comparator work')
  u.need(identity.alive(a.host_pid),'Existing sole host exited')
  return state
 before=zero();out.mkdir();u.write(out/'ANTES_ADJUNTAR.json',dict(host_pid=a.host_pid,participant=a.participant,run_id=a.run_id,bridge=before,Native_calls=0,policy_calls=0,hosts_started=0))
 operator=load('control/mcp_operator_C02.py','_attach_comparator_operator')
 def mcp(tool,args,label,seconds=120):return u.decode_tool(operator.run(tool,dict(args,studio_id=a.studio_id),out/(label+'.json'),seconds))
 guard=mcp('execute_luau',dict(datamodel_type='Server',code=u.prepared_guard(18,6,a.participant,v.WORLD_ID)),'00_fresh_world_guard')
 u.need(guard.get('verified')is True and guard.get('scenarioFingerprint')==a.scenario_sha256,'Fresh exact comparator scene required')
 relaymod=load('control/studio_mailbox_relay_C02_R03.py','_attach_comparator_relay')
 relaymod.configure_profile(v.WORLD_ID,expected_place=v.FILES[a.participant],max_cycles=18)
 probe=mcp('execute_luau',dict(datamodel_type='Server',code=relaymod.PULL_CODE),'01_mailbox_absent')
 u.need(probe.get('ready')is False and probe.get('reason')=='MAILBOX_NOT_CREATED','A START/mailbox already exists')
 relay_events=original/'relay.jsonl';u.need(not relay_events.exists(),'Old failed relay must never have written observer events')
 log=(out/'relay_utf8.log').open('xb');stop=out/'relay.stop'
 relay=subprocess.Popen([sys.executable,'-I','-B','-u',str(ROOT/'control/studio_mailbox_relay_C02_R03.py'),
  '--config',str(config),'--studio-id',a.studio_id,'--expected-place',v.FILES[a.participant],
  '--seconds',str(max(5,int(a.cutoff_utc_epoch-time.time())-10)),'--evidence',str(relay_events),'--stop-file',str(stop)],
  cwd=ROOT,env=dict(os.environ,PYTHONUTF8='1',PYTHONUNBUFFERED='1',PYTHONDONTWRITEBYTECODE='1'),
  stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 result=dict(schema='DEE.RBX01.C02.attach_comparator_first_start.R03',participant=a.participant,run_id=a.run_id,
             original_output=str(original),host_pid=a.host_pid,relay_pid=relay.pid,Native_calls=0,policy_hosts_started=0,
             first_start_attempts=0,retries=0,started_utc=u.utc())
 started=close_sent=world_saved=False
 def close_once(reason):
  nonlocal close_sent
  if close_sent:return
  close_sent=True
  try:mcp('execute_luau',dict(datamodel_type='Client',code=u.client_control('SAVE_CLOSE_BOUNDARY')),'03_close_once')
  except BaseException:pass
 try:
  deadline=time.monotonic()+180
  while not u.relay_observation(relay_events).get('connected'):
   u.need(identity.alive(a.host_pid)and relay.poll()is None and time.monotonic()<deadline,'Existing host/relay unavailable before first start');time.sleep(.5)
  zero();u.need(time.time()<a.cutoff_utc_epoch-240,'First-start horizon expired')
  intent=dict(utc=u.utc(),command='START_NATIVE',wire_command_legacy_name=True,Native_opened=False,single_attempt=True,replay_allowed=False,attached_by=str(out),host_pid=a.host_pid)
  u.write(original/'START_INTENT.json',intent);u.write(out/'START_INTENT.json',intent)
  started=True;result['first_start_attempts']=1
  try:result['start_reply']=mcp('execute_luau',dict(datamodel_type='Client',code=u.client_control('START_NATIVE')),'02_first_start_once')
  except BaseException as error:result['start_unknown_preserved']=type(error).__name__
  while identity.alive(a.host_pid):
   try:state=u.bridge_read(database)
   except Exception:state=None
   if(time.time()>=a.cutoff_utc_epoch-240 or relay.poll()is not None or(state and state['uncertain'])):close_once('FINITE_OR_UNCERTAIN')
   u.need(time.time()<v.HARD_FINISH-60,'Hard end; preserve owner/world, no termination');time.sleep(2)
  deadline=time.monotonic()+120
  while not(original/'RESULTADO.json').exists():u.need(time.monotonic()<deadline,'Original supervisor did not finalize');time.sleep(.5)
  old=u.read(original/'RESULTADO.json');u.write(out/'SUPERVISOR_ORIGINAL_FINAL.json',old)
  closure=u.read(original/'COMPARATOR_CLOSED.json')
  u.need(closure.get('participant')==a.participant and closure.get('run_id')==a.run_id and closure.get('status')=='CLOSED'
         and closure.get('policyWriterClosed')is True and closure.get('writerDrained')is True and closure.get('nativeOwnerOpened')is False and closure.get('nativeTicks')==0,'Exact drained comparator proof required')
  u.write(out/'COMPARATOR_CLOSED.json',closure)
  if old.get('status')in('COMPARATOR_SUSPENDED_CLOSED','COMPARATOR_HORIZON_CLOSED'):
   result.update(status='ORIGINAL_COMPARATOR_EXPORT_REUSED',original_result=str(original/'RESULTADO.json'));world_saved=True
  else:
   state=u.bridge_read(database);s=state['session'];b=state['boundary']
   u.need(state['pending']==state['uncertain']==state['unacknowledged_actions']==state['unacknowledged_tools']==0,'Transport not settled')
   u.need(s['status']=='SUSPENDED_BOUNDARY'and b and b['completed_cycles']==state['feedback_operations_completed']and b['next_opportunity']==b['completed_cycles']+1,'Exact actual partial/full suspension required')
   deadline=time.monotonic()+45
   while not u.relay_observation(relay_events).get('suspended'):
    u.need(relay.poll()is None and time.monotonic()<deadline,'Actual world suspension not observed');time.sleep(.5)
   context=dict(checkpoint_id='C02CMP_'+uuid.uuid4().hex,native_life_id='COMPARATOR_'+a.participant+'_'+a.run_id,native_tick=0,
    bridge=dict(session_id=s['id'],server_id=s['server_id'],phase=s['phase'],pending_count=0,uncertain_count=0,native_ticks_in_session=0))
   transport=load('control/transporte_checkpoint_C02_R02.py','_attach_comparator_transport')
   world,path,_=transport.capture_world(mcp,context,'CMP_ATTACH_R03_checkpoint',out/'WORLD_CHECKPOINT.json',lambda x:v.verify_world(x,a.participant,a.run_id))
   world_saved=True;result.update(status='COMPARATOR_WORLD_SAVED_PAIR_PENDING',world_checkpoint=str(path),world_sha256=u.sha(path),completed_cycles=b['completed_cycles'],next_opportunity=b['next_opportunity'])
   try:
    runner=load('puente/run_comparador_C02_R02.py','_attach_comparator_closed_runner')
    normalized=dict(c,databaseFile=str(database))
    pair=v.seal_comparator(directory,normalized,path,closure,out,runner)
    u.write(out/'CHECKPOINT_LOCATOR.json',pair);result.update(status='COMPARATOR_SUSPENDED_CLOSED',pair=pair)
   except BaseException as error:result['pair_pending_reason']=dict(type=type(error).__name__,message=str(error))
  if relay.poll()is None:stop.write_text('ROOT_ATTACH_COMPARATOR_RELAY_STOP\n',encoding='ascii');relay.wait(timeout=45)
  if world_saved and old.get('Play_stopped_after_export')is not True:result['play_stop_reply']=mcp('start_stop_play',dict(is_start=False),'05_play_stopped')
 except BaseException as error:
  result.update(status='COMPARATOR_ATTACH_FAILED_PRESERVED',error_type=type(error).__name__,error=str(error),Play_preserved=True,world_saved=world_saved,first_start_was_attempted=started)
  if started and identity.alive(a.host_pid):close_once('ATTACH_FAILURE_NO_REPLAY')
  elif not started and relay.poll()is None:stop.write_text('ROOT_ATTACH_PRESTART_RELAY_STOP\n',encoding='ascii')
 finally:log.close();result['ended_utc']=u.utc();u.write(out/'RESULTADO.json',result)
 return result
def parser():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
 for n in('original-output','policy-directory','config','output'):p.add_argument('--'+n,type=Path,required=True)
 p.add_argument('--participant',choices=('PROGRAMMED','CONVENTIONAL_AI'),required=True);p.add_argument('--run-id',required=True)
 p.add_argument('--host-pid',type=int,required=True);p.add_argument('--studio-id',required=True);p.add_argument('--scenario-sha256',required=True)
 p.add_argument('--cutoff-utc-epoch',type=float,default=1794744900);return p
if __name__=='__main__':print(json.dumps(run(parser().parse_args()),ensure_ascii=False,indent=2))
