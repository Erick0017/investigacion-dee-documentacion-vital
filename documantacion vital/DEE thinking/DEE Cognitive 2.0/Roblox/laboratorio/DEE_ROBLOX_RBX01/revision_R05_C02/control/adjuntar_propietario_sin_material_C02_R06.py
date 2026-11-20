"""Root-only first START attach to the same already-running zero-material owner.

Does not start/stop/reopen a Native owner, replay any request, or change Native
sources. The original supervisor remains alive. This helper owns its separate
relay, deadline control, and boundary export after the old supervisor finalizes.
Import/--help have no Native, HTTP or MCP side effects.
"""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,http.client,importlib.util,json,os,sqlite3,subprocess,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
def load(path,name):
 s=importlib.util.spec_from_file_location(name,ROOT/path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def alive(pid):
 k=ctypes.WinDLL('kernel32',use_last_error=True);k.OpenProcess.restype=ctypes.c_void_p
 h=k.OpenProcess(0x1000,False,pid)
 if not h:return False
 try:
  code=ctypes.c_ulong();return bool(k.GetExitCodeProcess(ctypes.c_void_p(h),ctypes.byref(code)))and code.value==259
 finally:k.CloseHandle(ctypes.c_void_p(h))
def run(a):
 o=load('control/orquestar_C02_R02.py','_C02_R05_attach_orq')
 o.need(a.root_run,'Root-only explicit operation')
 original,dest,config,ledger,out=map(o.safe,(a.original_output,a.destination,a.config,a.ledger,a.output))
 o.need(not out.exists() and out.is_relative_to(ROOT/'evidencia'),'New evidence output only')
 o.need(time.time()<o.CUTOFF-1800,'No first admission beyond new-Q1 margin')
 o.need(original.is_dir() and not(original/'START_NATIVE_INTENT.json').exists(),'Original START must never have been attempted')
 oldlog=original/'supervisor.jsonl'
 events=[json.loads(x)for x in oldlog.read_text('utf8').splitlines()if x.strip()]
 owned=[x for x in events if x.get('kind')=='ONE_OWNER_STARTED']
 o.need(len(owned)==1 and owned[0]['pid']==a.owner_pid and alive(a.owner_pid),'Exact sole existing launcher required')
 o.need(not(original/'RESULTADO.json').exists(),'Old supervisor already ended; reconcile separately')
 c=o.read(config);db=o.safe(ROOT/'configuracion_privada'/c['databaseFile'])
 o.need(c.get('worldId')==o.WORLD_ID and c.get('port')==8895 and c.get('resumeAllowed')is not True,'Fresh R02 bridge configuration only')
 life=o.read(dest/'CONTEXTO_EJECUCION.json')['life']
 o.need(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_C02_MAIN_R02','Exact experimental R02 life')
 card=o.read(dest/'sistema/estado/vidas'/life/'VIDA.json');before=o.read(original/'BEFORE.json')
 o.need(card['physical']==before['card']['physical'] and card['physical']['tick']==947395,'Exact initial physical state, not another future')
 def no_material():
  state=o.bridge_read(db);l=o.read(ledger);m=o.owner_meta(dest,life)
  o.need(state is not None and state['session']is None and state['boundary']is None,'Bridge session must remain absent')
  o.need(state['pending']==state['uncertain']==state['unacknowledged_actions']==state['unacknowledged_tools']==state['feedback_operations_completed']==0,'No bridge material or pending work')
  o.need(l.get('intent')is None and life not in l.get('worlds',{}),'No R02 ledger admission or unresolved intent')
  o.need(m.get('pid')==a.native_pid and alive(a.native_pid) and m.get('uncertain_external_result')is False,'Exact known live Native child')
  o.need(all(m['physical'].get(k)==card['physical'].get(k)for k in('N','tick','RAW_sha256','clocks_sha256')),'Native physical cache changed')
  q=dest/'sistema/estado/servicios_persistentes'/life/'cola.sqlite3'
  con=sqlite3.connect(q.as_uri()+'?mode=ro',uri=True,timeout=3)
  try:
   con.execute('BEGIN')
   # Queue table names are verified from the installed stdlib schema below.
   tables={x[0]for x in con.execute("SELECT name FROM sqlite_master WHERE type='table'")}
   table='requests' if 'requests'in tables else 'request'
   pending=con.execute('SELECT COUNT(*) FROM '+table+" WHERE status IN ('queued','running','processing','uncertain')").fetchone()[0]
   o.need(pending==0,'Native queued/material request exists');con.rollback()
  finally:con.close()
  return dict(bridge=state,ledger=l,owner_cache=m)
 initial=no_material();out.mkdir()
 def note(kind,**fields):
  with(out/'attach.jsonl').open('a',encoding='utf8')as f:f.write(json.dumps(dict(utc=o.utc(),kind=kind,**fields),ensure_ascii=False)+'\n')
 o.write(out/'ANTES_ADJUNTAR.json',dict(original_output=str(original),owner_pid=a.owner_pid,native_pid=a.native_pid,physical=card['physical'],state=initial,Native_owners_started=0,Native_controls_sent=0))
 cache=load('control/preparar_recuperacion_cache_C02_R05.py','_C02_noidle_fresh_R05')
 obs=cache.observe(lambda:o.owner_meta(dest,life),lambda:alive(a.owner_pid),card['physical'],5,maximum_seconds=75)
 o.write(out/'NO_IDLE_FRESH_BASELINE_R05.json',obs);o.need(obs['passed'],'Fresh running baseline observation failed')
 operator=load('control/mcp_operator_C02.py','_C02_attach_operator')
 def mcp(tool,args,label,seconds=120):
  fields=dict(args,studio_id=a.studio_id)
  return o.decode_tool(operator.run(tool,fields,out/(label+'.json'),seconds))
 guard=mcp('execute_luau',dict(datamodel_type='Server',code=o.prepared_guard(18,6)),'00_fresh_world_guard')
 o.need(guard.get('verified')is True and guard.get('scenarioFingerprint')==a.scenario_sha256,'Fresh exact prepared world required')
 relaymod=load('control/studio_mailbox_relay_C02_R02.py','_C02_attach_relay')
 relaymod.configure_profile(o.WORLD_ID,expected_place=o.EXPECTED_PLACE,max_cycles=48)
 probe=mcp('execute_luau',dict(datamodel_type='Server',code=relaymod.PULL_CODE),'01_mailbox_absent')
 o.need(probe.get('ready')is False and probe.get('reason')=='MAILBOX_NOT_CREATED','Existing mailbox/start is not repeatable')
 no_material()
 relay_path=out/'relay.jsonl';stop=out/'relay.stop';log=(out/'relay_utf8.log').open('xb')
 env=dict(os.environ,PYTHONUTF8='1',PYTHONUNBUFFERED='1',PYTHONDONTWRITEBYTECODE='1')
 relay=subprocess.Popen([sys.executable,'-I','-B','-u',str(ROOT/'control/studio_mailbox_relay_C02_R02.py'),'--config',str(config),'--studio-id',a.studio_id,'--expected-place',o.EXPECTED_PLACE,'--seconds',str(max(5,int(o.HARD_FINISH-time.time())-10)),'--evidence',str(relay_path),'--stop-file',str(stop)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 result=dict(schema='DEE.RBX01.C02.attach_first_start.R06',lifeId=life,owner_pid=a.owner_pid,native_pid=a.native_pid,relay_pid=relay.pid,Native_owners_started=0,Native_controls_sent=0,material_retries=0,old_supervisor_preserved=True,started_utc=o.utc())
 close_sent=False;started=False
 try:
  deadline=time.monotonic()+600
  while not o.relay_observation(relay_path).get('connected'):
   o.need(alive(a.owner_pid)and relay.poll()is None and time.monotonic()<deadline,'Existing owner/relay unavailable before FIRST_START');time.sleep(.5)
  no_material()
  o.need(not(original/'START_NATIVE_INTENT.json').exists(),'Original START appeared concurrently')
  o.need(time.time()<o.CUTOFF-1800,'First admission deadline rechecked after relay connection')
  intent=dict(utc=o.utc(),command='START_NATIVE',first_attempt=True,replay_allowed=False,same_existing_owner=a.owner_pid,attached_by=str(out),recovery_revision='R06')
  # Shared exclusive-create marker prevents another attach after ambiguous START.
  # The original supervisor has already left its START block and only monitors.
  o.write(original/'START_NATIVE_INTENT.json',intent)
  o.write(out/'START_NATIVE_INTENT.json',intent)
  started=True
  try:result['start_reply']=mcp('execute_luau',dict(datamodel_type='Client',code=o.client_control('START_NATIVE')),'02_first_start_once')
  except BaseException as error:note('START_UNKNOWN_NO_REPLAY',error_type=type(error).__name__)
  while alive(a.owner_pid):
   try:state=o.bridge_read(db);note('PROGRESS',bridge=state,ledger=o.read(ledger),relay_returncode=relay.poll())
   except(OSError,sqlite3.Error,ValueError)as error:
    state=None;note('READONLY_PROGRESS_UNAVAILABLE',error_type=type(error).__name__)
   if not close_sent and ((state and state['uncertain'])or relay.poll()is not None or time.time()>=o.CUTOFF-1890):
    close_sent=True;note('SAVE_CLOSE_ONCE',reason='UNCERTAIN_RELAY_EXIT_OR_PROSPECTIVE_MARGIN')
    try:mcp('execute_luau',dict(datamodel_type='Client',code=o.client_control('SAVE_CLOSE_BOUNDARY')),'03_save_close_once')
    except BaseException as error:note('SAVE_CLOSE_UNKNOWN_NO_RETRY',error_type=type(error).__name__)
   if time.time()>=o.HARD_FINISH-60:raise RuntimeError('Bounded end; preserve live owner/world, no force kill')
   time.sleep(5)
  deadline=time.monotonic()+120
  while not(original/'RESULTADO.json').exists():
   o.need(time.monotonic()<deadline,'Old supervisor completion not observed; preserve Play');time.sleep(.5)
  old=o.read(original/'RESULTADO.json');o.write(out/'SUPERVISOR_ORIGINAL_FINAL.json',old)
  proof=o.read(original/'SOURCE_OWNER_CLOSED.json')
  o.need(proof.get('ownerClosed')is True and proof.get('writerDrained')is True and proof.get('lifeId')==life and proof.get('exit_code')==0 and proof.get('source_journal_event',{}).get('final_status',{}).get('running')is False,'Official matching old supervisor closure missing')
  o.write(out/'SOURCE_OWNER_CLOSED.json',proof)
  state=o.bridge_read(db);session=state['session'];boundary=state['boundary']
  o.need(state['pending']==state['uncertain']==state['unacknowledged_actions']==state['unacknowledged_tools']==0 and o.read(ledger).get('intent')is None,'Unsettled transport/ledger; preserve')
  if old.get('status')in('SUSPENDED_CLOSED','HORIZON_CLOSED'):
   result.update(status='OLD_SUPERVISOR_EXPORTED_REUSED',old_result=str(original/'RESULTADO.json'))
  else:
   deadline=time.monotonic()+45
   while True:
    observed=o.relay_observation(relay_path)
    if observed.get('suspended')or observed.get('closed'):break
    o.need(relay.poll()is None and time.monotonic()<deadline,'No actual World boundary; preserve');time.sleep(.5)
   o.need(session['status']=='SUSPENDED_BOUNDARY'and boundary['completed_cycles']==6 and boundary['next_opportunity']==7 and state['feedback_operations_completed']==6,'Exact six-cycle boundary required')
   card=o.read(dest/'sistema/estado/vidas'/life/'VIDA.json')
   context=dict(checkpoint_id='C02_'+uuid.uuid4().hex,native_life_id=life,native_tick=card['physical']['tick'],bridge=dict(session_id=session['id'],server_id=session['server_id'],phase=session['phase'],pending_count=0,uncertain_count=0,native_ticks_in_session=session['ticks']))
   transport=load('control/transporte_checkpoint_C02_R02.py','_C02_attach_transport');persistence=load('control/persistencia_C02.py','_C02_attach_persistence')
   world,path,nbytes=transport.capture_world(mcp,context,'R06_checkpoint',out/'WORLD_CHECKPOINT.json',persistence.validate_world)
   o.write(out/'CHECKPOINT_LOCATOR.json',dict(checkpoint_id=context['checkpoint_id'],world_file=str(path),world_sha256=o.sha(path),bytes=nbytes,native_snapshot_sha256=card['snapshot_sha256'],native_root=str(dest),bridge_database=str(db),native_tick=card['physical']['tick'],complete_pair_not_yet_sealed=True))
   result.update(status='SUSPENDED_CLOSED',world_checkpoint=str(path),world_checkpoint_sha256=o.sha(path),next_opportunity=7)
  if relay.poll()is None:
   stop.write_text('ROOT_ATTACH_RELAY_STOP\n',encoding='ascii');relay.wait(timeout=45)
  if result['status']=='SUSPENDED_CLOSED':
   result['play_stop_reply']=mcp('start_stop_play',dict(is_start=False),'05_play_stopped')
 except BaseException as error:
  result.update(status='ATTACH_FAILED_PRESERVED',error_type=type(error).__name__,error=str(error),first_start_was_attempted=started,Play_preserved=True,no_replay=True)
  if not started and relay.poll()is None:
   stop.write_text('ROOT_ATTACH_PRESTART_RELAY_STOP\n',encoding='ascii')
 finally:
  log.close();result['ended_utc']=o.utc();o.write(out/'RESULTADO.json',result)
 return result
def parser():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
 for name in('original-output','destination','config','ledger','output'):p.add_argument('--'+name,type=Path,required=True)
 for name in('owner-pid','native-pid'):p.add_argument('--'+name,type=int,required=True)
 p.add_argument('--studio-id',required=True);p.add_argument('--scenario-sha256',required=True);return p
if __name__=='__main__':print(json.dumps(run(parser().parse_args()),ensure_ascii=False,indent=2))
