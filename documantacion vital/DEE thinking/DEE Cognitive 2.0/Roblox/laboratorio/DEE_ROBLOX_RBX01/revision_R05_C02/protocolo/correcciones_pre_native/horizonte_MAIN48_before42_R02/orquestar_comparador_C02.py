"""Root-only real-Studio comparator lifecycle; NO Native owner or DEE imports.

Uses the same Body/controller/bridge ABI and fixed exogenous calendar. The
participant is PROGRAMMED or CONVENTIONAL_AI. A complete comparator checkpoint
is own policy state + closed bridge + world; it is never a Native backup.
Importing this file creates no processes, calls no model and contacts no MCP.
"""
from pathlib import Path
import argparse, copy, datetime, hashlib, http.client, importlib.util, json
import os, re, shutil, sqlite3, subprocess, sys, time, uuid

ROOT=Path(__file__).resolve().parents[1]
HARD_FINISH=1794744900
WORLD_ID='RBX01_R05_C02_V1'
FILES={'PROGRAMMED':'DEE_RBX01_C02_PROGRAMMED.rbxlx',
       'CONVENTIONAL_AI':'DEE_RBX01_C02_CONVENTIONAL_AI.rbxlx'}

def load(relative,name):
    spec=importlib.util.spec_from_file_location(name,ROOT/relative)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

# This sibling contains stdlib functions only at import. Its run() is NEVER
# called. Native-specific preflight/owner code is not imported or reached.
u=load('control/orquestar_C02.py','_C02_safe_orchestrator_utilities')
need,read,write,sha,safe=u.need,u.read,u.write,u.sha,u.safe

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def verify_world(world,participant,run_id):
    need(world.get('schema')=='DEE.RBX01.C02.world_checkpoint.v1','Full common world checkpoint required')
    life='COMPARATOR_'+participant+'_'+run_id
    need(world.get('native_life_id')==life and world.get('native_tick')==0,'Comparator wire identity must not claim Native life/ticks')
    state=world.get('S',{});b=world.get('boundary',{});bridge=world.get('bridge',{})
    need(state.get('nativeTick')==0 and state.get('lifeId')==life,'Comparator S identity/tick mismatch')
    n=b.get('completed_opportunities')
    need(type(n)is int and n>=0 and state.get('completedCycles')==state.get('cycle')==n and b.get('next_opportunity')==n+1,'Exact continuing opportunity cursor required')
    need(b.get('phase')=='BOUNDARY'and b.get('native_phase')=='IDLE'and b.get('uncertain')is False
         and b.get('pending_action')is None and b.get('pending_operation')is None,'Settled common protocol boundary required')
    need(bridge.get('pending_count')==bridge.get('uncertain_count')==0 and bridge.get('phase')=='READY_QUERY','Bridge must be quiescent')
    need(isinstance(bridge.get('session_id'),str)and isinstance(bridge.get('server_id'),str),'Preserved transport identities required')
    need(isinstance(world.get('executed_actions'),dict)and all(v in('EXECUTED','ACKNOWLEDGED')for v in world['executed_actions'].values()),'Uncertain action cannot be restored')
    if n:
        need(b.get('last_action_id')==b.get('acknowledged_action_id') and
             world['executed_actions'].get(b.get('last_action_id'))in('EXECUTED','ACKNOWLEDGED')and
             isinstance(b.get('last_feedback_operation_id'),str),'Exact action ACK/feedback boundary required')
    need(isinstance(world.get('events'),list)and isinstance(world.get('pose_trace'),list)and
         isinstance(world.get('physical',{}).get('parts'),list),'Complete events/poses/geometry required')
    need(len(world.get('body_pose',[]))==12 and world.get('rng',{}).get('algorithm')=='PREDECLARED_EVENT_TABLE_V1','Pose and exogenous calendar required')
    return {'participant':participant,'run_id':run_id,'native_ticks':0,'completed_cycles':n,'next_opportunity':n+1}

def compare_world(before,after,participant,run_id):
    verify_world(before,participant,run_id);verify_world(after,participant,run_id)
    a,b=copy.deepcopy(before),copy.deepcopy(after)
    for value in(a,b):
        value.pop('observer',None);value.pop('close_requested',None)
        for k in('mode','reason','latency'):value.get('S',{}).pop(k,None)
    tolerance=1e-5
    def same(x,y,path=''):
        if type(x)in(int,float)and type(y)in(int,float)and(path.startswith('/physical/')or path.startswith('/body_pose/')):return abs(x-y)<=tolerance
        if type(x)is not type(y):return False
        if isinstance(x,dict):return x.keys()==y.keys()and all(same(x[k],y[k],path+'/'+k)for k in x)
        if isinstance(x,list):return len(x)==len(y)and all(same(v,w,path+'/'+str(i))for i,(v,w)in enumerate(zip(x,y)))
        return x==y
    need(same(a,b),'Restored comparator world changed semantically; no host/policy opened')
    return {'equal':True,'geometry_tolerance':tolerance,'ignored':['observer segment','close_requested','S.mode','S.reason','S.latency'],
            'scope':'ACTUAL_WORLD_SAVE_RESTORE_NO_NATIVE_EXECUTION'}

def comparator_closure(log,returncode,participant,run_id):
    if returncode!=0 or not log.exists():return None
    text=log.read_text('utf8',errors='replace')[-2000000:];decoder=json.JSONDecoder();found=None
    for i,char in enumerate(text):
        if char!='{':continue
        try:value,_=decoder.raw_decode(text[i:])
        except ValueError:continue
        if isinstance(value,dict)and value.get('schema')=='DEE.RBX01.C02.comparator_closure.v1'and value.get('status')=='CLOSED'and value.get('participant')==participant and value.get('run_id')==run_id:
            if(value.get('writerDrained')is True and value.get('policyWriterClosed')is True and value.get('nativeOwnerOpened')is False and value.get('nativeTicks')==0 and value.get('coherence_error')is None and(value.get('coherence')or{}).get('coherent')is True):found=value
    return found

def seal_comparator(directory,config,world_path,closure,output,runner):
    """Called only after proved closed policy/bridge. No Native root is copied."""
    directory=safe(directory);world=read(world_path);participant=closure['participant'];run_id=closure['run_id']
    verify_world(world,participant,run_id)
    db=Path(config['databaseFile']);policy=directory/'POLICY_STATE_C02.json'
    need(not(directory/'policy_writer.lock').exists()and not policy.with_name(policy.name+'.WRITING').exists(),'Policy writer/uncertain transaction preserved')
    for suffix in('-wal','-shm','-journal'):
        extra=Path(str(db)+suffix);need(not extra.exists()or extra.stat().st_size==0,'Closed comparator bridge has nonempty SQLite auxiliary')
    state=runner.db_read(db);coherence=runner.compare_states(state,read(policy))
    need(coherence['status']=='SUSPENDED_BOUNDARY'and state['binding']is None,'Only first clean suspended boundary may be bound')
    need(world['bridge']['session_id']==state['session']['id']and world['bridge']['server_id']==state['session']['server_id'],'World/bridge logical identities mismatch')
    need(closure['policy_checkpoint']['sha256']==sha(policy),'Closed policy checkpoint bytes changed')
    pack=output/'PAIR_COMPARATOR_C02';need(not pack.exists(),'Fresh pair destination required');pack.mkdir()
    anchor={'schema':'DEE.RBX01.C02.comparator_pair_anchor.R01','checkpoint_id':world['checkpoint_id'],
            'participant':participant,'run_id':run_id,'session_id':state['session']['id'],'server_id':state['session']['server_id'],
            'world_sha256':sha(world_path),'policy_sha256':sha(policy),'identity_sha256':sha(directory/'RUNNER_IDENTITY_C02.json'),
            'native_owner_opened':False,'native_ticks':0,'next_opportunity':world['boundary']['next_opportunity']}
    write(pack/'ANCHOR_COMPARATOR_C02.json',anchor);anchor_sha=sha(pack/'ANCHOR_COMPARATOR_C02.json')
    bridge=runner.load('puente/rbx02_bridge_C02.py','_C02_comparator_offline_binder')
    binding=bridge.bind_checkpoint(db,world['checkpoint_id'],anchor_sha)
    write(output/'BINDING_COMPARATOR_C02.json',binding)
    for source,name in((world_path,'WORLD_CHECKPOINT.json'),(policy,'POLICY_STATE_C02.json'),
                       (directory/'RUNNER_IDENTITY_C02.json','RUNNER_IDENTITY_C02.json'),(db,'BRIDGE.sqlite3')):
        shutil.copyfile(source,pack/name);need(sha(source)==sha(pack/name),'Closed comparator pair copy mismatch')
    write(pack/'CIERRE_COMPARADOR.json',closure)
    members={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)}for p in pack.iterdir()if p.is_file()}
    manifest={'schema':'DEE.RBX01.C02.comparator_pair.R01','participant':participant,'run_id':run_id,
              'policy_directory_live':str(directory),'bridge_database_live':str(db),'anchor_sha256':anchor_sha,
              'members':members,'Native_backup':False,'new_Native_ticks':0,'source_files_sha256':runner.source_pins(),
              'resume_requires':'same own policy directory and bound closed DB; fresh matching physical world apply; then --resume'}
    write(pack/'PAIR_COMPARATOR_C02.json',manifest)
    for name,row in members.items():need(sha(pack/name)==row['sha256'],'Sealed pair member changed')
    return {'directory':str(pack),'manifest_sha256':sha(pack/'PAIR_COMPARATOR_C02.json'),
            'bound_checkpoint_sha256':anchor_sha,'world_file':str(pack/'WORLD_CHECKPOINT.json'),
            'world_checkpoint_sha256':sha(pack/'WORLD_CHECKPOINT.json'),'Native_backup':False}

def run(args):
    need(args.root_run,'Root-only execution')
    need(args.participant in FILES and args.expected_place==FILES[args.participant],'Exact comparator Studio file required')
    need(args.world_id==WORLD_ID and args.max_cycles==48 and args.suspend_after==16,'Same48/16 world for comparator')
    need(re.fullmatch('[0-9a-f]{64}',args.scenario_sha256),'Frozen scenario fingerprint required')
    need(time.time()<args.cutoff_utc_epoch<=HARD_FINISH,'Prospective finite comparator horizon required')
    config_path,policy_dir,output=map(safe,(args.config,args.policy_directory,args.output))
    need(output.is_relative_to(ROOT/'evidencia')and not output.exists(),'Fresh comparator evidence output')
    config=read(config_path);need(config.get('port')==8895 and config.get('worldId')==WORLD_ID and config.get('allowControl')is True,'Fixed comparator private config')
    database=safe(ROOT/'configuracion_privada'/config['databaseFile']);output.mkdir(parents=True)
    runner=load('puente/run_comparador_C02.py','_C02_comparator_runner_preflight')
    runner_args=argparse.Namespace(config=config_path,participant=args.participant,policy_directory=policy_dir,
                                   run_id=args.run_id,resume=bool(args.world_checkpoint),cutoff_utc_epoch=args.cutoff_utc_epoch)
    _,_,normalized,_,_,_=runner.preflight(runner_args)
    operator=load('control/mcp_operator_C02.py','_C02_comparator_operator')
    def note(kind,**fields):
        with(output/'supervisor.jsonl').open('a',encoding='utf8')as stream:
            stream.write(json.dumps({'utc':utc(),'kind':kind,**fields},ensure_ascii=False,allow_nan=False)+'\n');stream.flush()
    def mcp(tool,arguments,label,seconds=90):
        fields=dict(arguments)
        if tool!='list_roblox_studios':fields['studio_id']=args.studio_id
        extra={'wait_file':args.expected_place}if tool=='list_roblox_studios'else{}
        return u.decode_tool(operator.run(tool,fields,output/(label+'.json'),seconds,**extra))
    def capture_world(context,label,filename):
        # TransportR02 preserves the same actual world, own-policy attribution
        # and verifier. R01 single-value source is preserved separately.
        transport=load('control/transporte_checkpoint_C02_R02.py','_C02_comparator_transport_R02')
        world,path,_=transport.capture_world(mcp,context,label,output/filename,
            lambda value:verify_world(value,args.participant,args.run_id))
        return world,path

    def health():
        con=http.client.HTTPConnection('127.0.0.1',8895,timeout=2)
        try:
            con.request('GET','/health');r=con.getresponse();raw=r.read(65537)
            return json.loads(raw)if r.status==200 and len(raw)<=65536 else None
        finally:con.close()
    policy_process=relay=None;streams=[];play=False;close_sent=False
    host_log=output/'comparator_utf8.log';relay_log=output/'relay_utf8.log';relay_events=output/'relay.jsonl';relay_stop=output/'relay.stop'
    env=dict(os.environ,PYTHONUTF8='1',PYTHONUNBUFFERED='1',PYTHONDONTWRITEBYTECODE='1')
    summary={'schema':'DEE.RBX01.C02.comparator_orchestrator.R01','participant':args.participant,'run_id':args.run_id,
             'started_utc':utc(),'Native_imported':False,'Native_owner_opened':False,'Native_ticks':0,'policy_retries':0,
             'native_orchestrator_utilities_sha256':sha(ROOT/'control/orquestar_C02.py')}
    def close_once(reason):
        nonlocal close_sent
        if close_sent or not play:return
        close_sent=True;note('SAVE_CLOSE_BOUNDARY_ONCE',reason=reason)
        try:mcp('execute_luau',{'datamodel_type':'Client','code':u.client_control('SAVE_CLOSE_BOUNDARY')},'boundary_close_once',120)
        except BaseException as error:note('CLOSE_UNKNOWN_PRESERVED',error_type=type(error).__name__)
    def monitor():
        while policy_process.poll()is None:
            try:
                state=u.bridge_read(database);note('COMPARATOR_PROGRESS',bridge=state,world=u.relay_observation(relay_events),pid=policy_process.pid)
                if state and state['uncertain']:close_once('UNCERTAIN_TRANSPORT_NO_REPLAY')
                if relay and relay.poll()is not None:close_once('RELAY_ENDED_NO_REPLAY')
            except(OSError,ValueError,sqlite3.Error)as error:note('PASSIVE_PROGRESS_UNAVAILABLE',error_type=type(error).__name__)
            if time.time()>=args.cutoff_utc_epoch-240:close_once('PROSPECTIVE_MODEL_AND_DRAIN_MARGIN')
            if time.time()>=HARD_FINISH-30:note('HARD_FINISH_WRITER_PRESERVED',pid=policy_process.pid);return
            time.sleep(5)
    try:
        listing=mcp('list_roblox_studios',{},'00_inventory');target=next((r for r in listing.get('studios',[])if r.get('id')==args.studio_id),None)
        need(target and target.get('file')==args.expected_place,'Exact comparator scene required')
        guard=mcp('execute_luau',{'datamodel_type':'Server','code':u.prepared_guard(48,16,args.participant,WORLD_ID)},'01_fresh_server_guard')
        need(guard.get('verified')is True and guard.get('scenarioFingerprint')==args.scenario_sha256,'Common prepared scenario mismatch');play=True
        relay_module=load('control/studio_mailbox_relay_C02.py','_C02_comparator_relay_profile')
        relay_module.configure_profile(WORLD_ID,expected_place=args.expected_place,max_cycles=48)
        account=mcp('execute_luau',{'datamodel_type':'Server','code':relay_module.ACCOUNT_CODE},'01B_account')
        need(account.get('studioUserId')==11981994305 and account.get('verified')is True,'Authenticated Studio account guard')
        probe=mcp('execute_luau',{'datamodel_type':'Server','code':relay_module.PULL_CODE},'01C_mailbox_absent')
        need(probe.get('ready')is False and probe.get('reason')=='MAILBOX_NOT_CREATED','No preexisting mailbox/start allowed')
        if args.world_checkpoint:
            path=safe(args.world_checkpoint);world=read(path);verify_world(world,args.participant,args.run_id)
            need(sha(path)==args.world_checkpoint_sha256,'Saved world bytes mismatch')
            dbstate=runner.db_read(database)
            need(dbstate['binding']and dbstate['binding']['checkpoint_id']==world['checkpoint_id']and dbstate['binding']['checkpoint_sha256']==args.bound_checkpoint_sha256,'Bound comparator checkpoint mismatch')
            need(dbstate['session']['id']==world['bridge']['session_id']and dbstate['session']['server_id']==world['bridge']['server_id'],'Saved logical IDs mismatch')
            expected={k:world[k]for k in('world_id','scenario_sha256','native_life_id','native_tick','checkpoint_id')}
            expected.update(checkpoint_sha256=args.bound_checkpoint_sha256,owner_closed=True,bridge_quiescent=True)
            raw=json.dumps(world,ensure_ascii=False,separators=(',',':'),allow_nan=False);count=(len(raw)+23999)//24000
            mcp('execute_luau',{'datamodel_type':'Server','code':'local s=game:GetService("ServerStorage");assert(not s:FindFirstChild("C02ComparatorRestore"),"RESTORE_ALREADY_ATTEMPTED");local f=Instance.new("Folder");f.Name="C02ComparatorRestore";f.Parent=s;return {prepared=true}'},'02_restore_transport_once')
            for i in range(count):
                code='local f=game:GetService("ServerStorage").C02ComparatorRestore;assert(not f:FindFirstChild("c'+str(i)+'"),"CHUNK_ALREADY_WRITTEN");local v=Instance.new("StringValue");v.Name="c'+str(i)+'";v.Value='+u.long_string(raw[i*24000:(i+1)*24000])+';v.Parent=f;return {written=true}'
                mcp('execute_luau',{'datamodel_type':'Server','code':code},'02_restore_chunk_%04d'%i)
            code='local s=game:GetService("ServerStorage");local h=game:GetService("HttpService");local t={};for i=0,'+str(count-1)+' do table.insert(t,s.C02ComparatorRestore["c"..i].Value)end;return s.RBX01Restore_C02:Invoke(h:JSONDecode(table.concat(t)),h:JSONDecode('+u.long_string(json.dumps(expected,separators=(',',':')))+'))'
            restored=mcp('execute_luau',{'datamodel_type':'Server','code':code},'02_restore_apply_once',120);need(restored.get('restored')is True,'Unknown restore; preserve without replay')
            recaptured,_=capture_world({'checkpoint_id':world['checkpoint_id'],'native_life_id':world['native_life_id'],'native_tick':0,'bridge':world['bridge']},'02_restored','WORLD_RESTORED_BEFORE_POLICY.json')
            write(output/'WORLD_RESTORE_COMPARISON.json',compare_world(world,recaptured,args.participant,args.run_id))
        try:existing=health()
        except(OSError,http.client.HTTPException,ValueError):existing=None
        need(existing is None,'Existing loopback listener must be reconciled first')
        stream=host_log.open('xb');streams.append(stream)
        command=[sys.executable,'-I','-B','-X','utf8','-u',str(ROOT/'puente/run_comparador_C02.py'),'--serve','--participant',args.participant,'--policy-directory',str(policy_dir),'--run-id',args.run_id,'--config',str(config_path),'--cutoff-utc-epoch',str(args.cutoff_utc_epoch)]
        if args.world_checkpoint:command.append('--resume')
        policy_process=subprocess.Popen(command,cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));note('ONE_COMPARATOR_HOST_STARTED',pid=policy_process.pid,command=command)
        deadline=time.monotonic()+600
        while True:
            need(policy_process.poll()is None,'Comparator host ended before health')
            try:ready=health()
            except(OSError,http.client.HTTPException,ValueError):ready=None
            if ready:break
            need(time.monotonic()<deadline,'600s comparator health timeout');time.sleep(.5)
        stream=relay_log.open('xb');streams.append(stream)
        relay=subprocess.Popen([sys.executable,'-I','-B','-X','utf8','-u',str(ROOT/'control/studio_mailbox_relay_C02.py'),'--config',str(config_path),'--studio-id',args.studio_id,'--seconds',str(min(32400,max(5,int(args.cutoff_utc_epoch-time.time())-10))),'--evidence',str(relay_events),'--stop-file',str(relay_stop),'--world-id',WORLD_ID,'--expected-place',args.expected_place],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
        deadline=time.monotonic()+600
        while not u.relay_observation(relay_events).get('connected'):
            need(policy_process.poll()is None and relay.poll()is None,'Comparator/relay ended before start')
            need(time.monotonic()<deadline,'600s relay connect timeout');time.sleep(.5)
        write(output/'START_INTENT.json',{'utc':utc(),'command':'START_NATIVE','wire_command_legacy_name':True,'Native_opened':False,'single_attempt':True,'replay_allowed':False})
        try:summary['start_reply']=mcp('execute_luau',{'datamodel_type':'Client','code':u.client_control('START_NATIVE')},'03_start_once',120)
        except BaseException as error:summary['start_unknown_preserved']=type(error).__name__;note('START_UNKNOWN_NO_REPLAY')
        monitor();summary['status']='COMPARATOR_EXITED_AWAITING_PROOF'
    except BaseException as error:
        summary.update(status='FAILED_PRESERVED',error_type=type(error).__name__,error=str(error));close_once('ORCHESTRATOR_EXCEPTION')
        if policy_process is not None and policy_process.poll()is None:monitor()
    finally:
        closure=comparator_closure(host_log,policy_process.poll()if policy_process else None,args.participant,args.run_id)
        summary.update(policy_closed=closure is not None,closure=closure,process_returncode=policy_process.poll()if policy_process else None)
        if closure:
            write(output/'COMPARATOR_CLOSED.json',closure)
            try:
                state=u.bridge_read(database);need(state and state['pending']==state['uncertain']==state['unacknowledged_actions']==state['unacknowledged_tools']==0,'Bridge not quiescent')
                session=state['session'];deadline=time.monotonic()+45
                while True:
                    view=u.relay_observation(relay_events);event=view.get('suspended')if session['status']=='SUSPENDED_BOUNDARY'else view.get('closed')
                    if event:break
                    need(relay is not None and relay.poll()is None and time.monotonic()<deadline,'Actual world boundary not observed; Play preserved');time.sleep(.5)
                context={'checkpoint_id':'C02CMP_'+uuid.uuid4().hex,'native_life_id':'COMPARATOR_'+args.participant+'_'+args.run_id,'native_tick':0,
                         'bridge':{'session_id':session['id'],'server_id':session['server_id'],'phase':session['phase'],'pending_count':0,'uncertain_count':0,'native_ticks_in_session':0}}
                world,path=capture_world(context,'04_world','WORLD_CHECKPOINT.json')
                if session['status']=='SUSPENDED_BOUNDARY':
                    pair=seal_comparator(policy_dir,normalized,path,closure,output,runner)
                    write(output/'CHECKPOINT_LOCATOR.json',pair);summary.update(status='COMPARATOR_SUSPENDED_CLOSED',pair=pair,next_opportunity=world['boundary']['next_opportunity'])
                else:
                    summary.update(status='COMPARATOR_HORIZON_CLOSED'if world['boundary']['completed_opportunities']==48 and session['status']=='STOPPED'else'COMPARATOR_PARTIAL_CLOSED',world_final=str(path),world_sha256=sha(path))
            except BaseException as error:summary.update(status='COMPARATOR_CLOSED_EXPORT_INCOMPLETE_PRESERVED',export_error_type=type(error).__name__,export_error=str(error))
        else:summary.update(reconciliation_required=policy_process is not None,Play_preserved=play,no_other_writer_may_start=policy_process is not None)
        if relay is not None and closure and relay.poll()is None:
            with relay_stop.open('x',encoding='ascii')as stream:stream.write('ROOT_RELAY_ONLY_STOP\n')
            try:relay.wait(timeout=45)
            except subprocess.TimeoutExpired:summary['relay_still_open_no_force_kill']=True
        if closure and play and(relay is None or relay.poll()is not None)and summary.get('status')in('COMPARATOR_SUSPENDED_CLOSED','COMPARATOR_HORIZON_CLOSED'):
            try:mcp('start_stop_play',{'is_start':False},'05_play_stopped');summary['Play_stopped_after_export']=True
            except BaseException as error:summary['play_stop_unknown_preserved']=type(error).__name__
        summary['ended_utc']=utc()
        for stream in streams:stream.close()
        write(output/'RESULTADO.json',summary)
    return summary

def parser():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--root-run',action='store_true',required=True)
    p.add_argument('--participant',choices=tuple(FILES),required=True);p.add_argument('--studio-id',required=True);p.add_argument('--run-id',required=True)
    for name in('config','policy-directory','output'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--world-id',default=WORLD_ID,choices=(WORLD_ID,));p.add_argument('--expected-place',choices=tuple(FILES.values()),required=True)
    p.add_argument('--scenario-sha256',required=True);p.add_argument('--max-cycles',type=int,default=48);p.add_argument('--suspend-after',type=int,default=16)
    p.add_argument('--cutoff-utc-epoch',type=float,default=HARD_FINISH)
    p.add_argument('--world-checkpoint',type=Path);p.add_argument('--world-checkpoint-sha256');p.add_argument('--bound-checkpoint-sha256')
    return p
if __name__=='__main__':print(json.dumps(run(parser().parse_args()),ensure_ascii=False,indent=2))
