"""Root-only finite focal load worker. Default --preflight never opens Native.

Uses the exact R06 configured_owner/adapter and shared global ledger. Three
processes can own three distinct lives; no SQLite bridge or Roblox action.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1]
PRODUCT=ROOT.parents[2]
LAST_NEW=1794859200
CUTOFF=1794863220
PINS={'native/owner_support_v3.py': 'f97d147aa1df805248e69bb312997f7291f2c26b3e0da6ede4fb1ebad8324ffc', 'native/adapter_v3.py': '378301b65f117a03ddfc834b18a2eb32d3d0164dea912292d0b1f84cb47dd137'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def need(x,message):
    if not x:raise ValueError(message)
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def write_new(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def atomic(p,value):
    temp=p.with_name(p.name+'.new_'+uuid.uuid4().hex)
    write_new(temp,value);os.replace(temp,p)
def append(p,value):
    with p.open('a',encoding='utf8')as f:f.write(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
def load(relative,name):
    p=ROOT/relative;need(sha(p)==PINS[relative],'Frozen load support source changed')
    spec=importlib.util.spec_from_file_location(name,p);module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module);return module
def wire_action(result,operation_id):
    """Actor returns a name, not the HTTP bridge's action object. No choice here."""
    name=result.get('action')
    need(name in('ASK_STATION','SKIP_STATION','SAFE_WAIT','EXIT_0','EXIT_1'),'Actual Native action name required; no fallback')
    need(type(result.get('null'))is bool,'Actual Native NULL flag required')
    return dict(name=name,null=result['null'],actionId=operation_id,nativeTick=result['nativeTick'])
def preflight(a):
    protocol=read(ROOT/'load/PROTOCOLO_CARGA_V3_R02.json');profile=protocol['lifes'][a.profile]
    destination=a.destination.resolve(strict=True);need(destination==ROOT/'native'/a.profile,'Only exact native/LOAD1..3 roots admitted by the frozen preparer')
    context=read(destination/'CONTEXTO_EJECUCION.json');scope=read(destination/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
    imported=read(destination/'IMPORTACION_DIAGNOSTICA.json')
    need(context['life']==profile['id']==scope['life_id'],'Exact independent load life')
    need(scope['role']=='load'and scope['source_tick']==991187 and scope['parent_completed_opportunities']==28,'Declared complete DEV4 prefix')
    need(imported['new_native_ticks']==0 and imported['comparison']['physical_equal']and imported['comparison']['causal_prefix_equal'],'Coherent full import0 required before any owner')
    need(scope['max_cycles']==3 and scope['native_cutoff_utc_epoch']==CUTOFF,'Fixed R06 scope')
    for path,want in PINS.items():need(sha(ROOT/path)==want,'Pinned support changed')
    progress=ROOT/'load'/('PROGRESO_'+a.profile+'.json')
    if progress.exists():
        state=read(progress);need(state['life']==profile['id']and state['last_stage']==a.stage-1,'No stage replay or skipped cumulative history')
        need(state['closed']is True and state['phase']=='IDLE','Prior load writer must have closed without pending future')
    else:
        need(a.stage==1,'One new three-owner batch; do not repeat a ladder')
        journal=destination/'sistema/estado/servicios_locales'/profile['id']/'RBX07_NATIVE_INTEGRAL_V3/events.jsonl'
        need(not journal.exists()or journal.stat().st_size==0,'Existing unaccounted R06 Native history; no counter reconstruction')
        state=dict(life=profile['id'],session_id='FOCAL_'+a.profile+'_'+uuid.uuid4().hex[:10],sequence=56,
                   completed_new=0,last_action_id=None,native_tick=991187,world_time_ms=100000,phase='IDLE',closed=True,last_stage=a.stage-1)
    return protocol,profile,destination,context,state,progress
def run(a):
    protocol,profile,destination,context,state,progress=preflight(a)
    if not a.execute_root_only:return dict(status='PREFLIGHT_ONLY_NO_NATIVE',life=profile['id'],stage=a.stage,state=state)
    need(time.time()<LAST_NEW,'No new load episode after20:00UTC')
    output=a.output.resolve();need(output.is_relative_to(ROOT/'load')and not output.exists(),'Fresh load output only')
    output.mkdir(parents=True);write_new(output/'FUENTES.json',dict(source_pins=PINS,protocol_sha256=sha(ROOT/'load/PROTOCOLO_CARGA_V3_R02.json'),scope_sha256=sha(destination/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')))
    barrier=a.barrier.resolve();need(barrier.is_relative_to(ROOT/'load')and barrier.is_dir(),'Root stage barrier required')
    support=load('native/owner_support_v3.py','_load_owner_support');adapter_module=load('native/adapter_v3.py','_load_native_adapter')
    owner=support.configured_owner(PRODUCT,destination,a.ledger,tag='R07_'+a.profile+'_S'+str(a.stage),cutoff_epoch=CUTOFF,continuous=True)
    started=time.time();results=[];failure=None;closed=False;owner_pid=None;entered=None;left=None;last_tick=state['native_tick'];actual_a=None
    def phase(adapter,kind,payload,observation_id,sequence):
        identifier=a.profile+'_S'+str(a.stage)+'_'+kind+'_'+uuid.uuid4().hex[:16]
        ctx=dict(session_id=state['session_id'],sequence=sequence,observation_id=observation_id,operation_id=identifier,mode='LIVE_NATIVE')
        atomic(output/'PENDIENTE.json',dict(status='INTENT_NO_RETRY',id=identifier,kind=kind,context=ctx,payload=payload,utc=stamp()))
        append(output/'FASES.jsonl',dict(event='INTENT',context=ctx,kind=kind,payload=payload,utc=stamp()))
        t=time.monotonic();value=adapter.execute(kind,payload,ctx)
        append(output/'FASES.jsonl',dict(event='COMPLETED',context=ctx,kind=kind,result=value,elapsed_seconds=time.monotonic()-t,utc=stamp()))
        atomic(output/'PENDIENTE.json',dict(status='COMPLETED',id=identifier,kind=kind,utc=stamp()))
        return value,identifier
    def observe(phase_name):
        state['sequence']+=1;state['world_time_ms']+=1
        return dict(observationId='obs_'+uuid.uuid4().hex,seq=state['sequence'],phase=phase_name,
            worldTimeMs=state['world_time_ms'],sampleTimeMs=state['world_time_ms'],previousActionId=state['last_action_id'],
            sensors=dict(station=2,stage=2,contact=2,inventoryKey=False,inventoryResource=False,queryAvailable=True,
                stationSignal=(1 if phase_name=='ROUTE_CHOICE' and state.get('query_applied')else-1),permissionStock=164,publicContactCode=2,lastFailure=False,
                numberAPresent=True,codeBPresent=False,numberAVersion=1,codeBCurrent=False,goalDelivery=True))
    try:
        with owner:
            entered=time.time();owner_pid=owner.proc.pid;adapter=adapter_module.create_adapter({'owner':owner})
            write_new(output/'READY.json',dict(utc=stamp(),epoch=entered,owner_pid=owner_pid,worker_pid=os.getpid(),life=profile['id'],state_before=state))
            wait_until=time.monotonic()+600
            while not(barrier/'GO.json').exists():
                if(barrier/'ABORT.json').exists():raise RuntimeError('Root barrier aborted before Native admission')
                need(time.monotonic()<wait_until and time.time()<LAST_NEW,'Finite load barrier expired')
                owner.sample();time.sleep(.1)
            go=read(barrier/'GO.json');need(a.profile in go['profiles']and go['stage']==a.stage,'Root barrier identity')
            for index in range(3):
                if time.time()>=LAST_NEW or(barrier/'ABORT.json').exists():break
                q1obs=observe('QUERY_CHOICE');q1,q1id=phase(adapter,'decision',{'observation':q1obs},q1obs['observationId'],q1obs['seq'])
                q1action=wire_action(q1,q1id);last=q1obs;action=q1action;function=None;tool=None
                motor_missing=bool(q1action.get('null'))
                if not motor_missing:
                    state['query_applied']=q1action['name']=='ASK_STATION';q2obs=observe('ROUTE_CHOICE');q2,q2id=phase(adapter,'query_sensor',{'observation':q2obs},q2obs['observationId'],q2obs['seq'])
                    action=wire_action(q2,q2id);last=q2obs;motor_missing=bool(action.get('null'))
                    if index==0:tool={'kind':'LESSON','items':profile['lesson']}
                    elif index==1:tool={'kind':'CALCULATE','slot':'A','form':'luma','left':6,'right':2}
                    else:tool={'kind':'CALCULATE','slot':'B','form':'nara','left':actual_a,'right':1}
                    if tool['kind']=='CALCULATE'and(type(tool['left'])is not int or not 0<=tool['left']<=32):
                        append(output/'FASES.jsonl',dict(event='TOOL_NOT_INVOKED',reason='ACTUAL_NUMERIC_INPUT_UNAVAILABLE',tool=tool,utc=stamp()))
                        public={'kind':'CALCULATE','numeric_result':None,'reason':'ACTUAL_NUMERIC_INPUT_UNAVAILABLE'}
                        function={'toolResult':public}
                    else:
                        function,function_id=phase(adapter,'function',{'tool':tool},last['observationId'],last['seq'])
                        public=function['toolResult']
                    if index==1:
                        v=public.get('numeric_result');actual_a=v if type(v)is int and 0<=v<=32 else None
                public=None if function is None else function['toolResult']
                failed=motor_missing or(public is not None and(public.get('reason')=='NATIVE_PARTIAL_ADMISSION'or tool['kind']=='CALCULATE'and type(public.get('numeric_result'))is not int))
                fields=dict(actionId=action['actionId'],seq=last['seq'],observationId=last['observationId'],worldTimeMs=last['worldTimeMs'],durationMs=0,
                    outcome='FOCAL_NO_ROBLOX_ACTUATION',collision=False,resourceCollected=False,resourceDelivered=False,permissionSpent=0,
                    materialConsequence=bool(failed),lastObservation=last)
                feedback,feedback_id=phase(adapter,'feedback',fields,last['observationId'],last['seq'])
                need(feedback.get('accepted')is True,'Native feedback not confirmed; preserve state and do not commit a cursor')
                last_tick=feedback['nativeTick'];state.update(native_tick=last_tick,completed_new=state['completed_new']+1,last_action_id=action['actionId'],phase='IDLE',closed=False)
                results.append(dict(index=index+1,q1=q1action,actual_final_action=action,tool=tool,public_tool_result=public,feedback_operation_id=feedback_id,native_tick=last_tick,
                    Native_routes_observed_not_executed=True,resource_counted_as_new=0))
                atomic(output/'PROGRESO_DURANTE.json',state)
                # A known Native NULL is a measured completed episode after its
                # real return, not an uncertain call or permission to invent an action.
        left=time.time();closed=owner.proc.poll()==0
    except BaseException as error:
        failure=type(error).__name__+': '+str(error);left=time.time()
        closed=owner.proc is not None and owner.proc.poll()==0
    state.update(last_stage=a.stage,closed=closed and failure is None)
    if state['closed']:atomic(progress,state)
    ledger=read(a.ledger);intent=ledger.get('intents',{}).get(profile['id'])
    report=dict(schema='DEE.RBX.IntegralV3.LoadWorker.R01',profile=a.profile,life=profile['id'],stage=a.stage,
        owner_pid=owner_pid,worker_pid=os.getpid(),owner_open_epoch=entered,owner_closed_epoch=left,
        elapsed_seconds=time.time()-started,closed=closed,writer_progress_committed=state['closed'],failure=failure,
        pending_global_intent=intent,native_tick=last_tick,state=state,results=results,
        scope='Focal Native load only; no Roblox movement, no new resource, shared prefix not an independent organism.',
        owner_job_limit_bytes=536870912,source_pins=PINS,owner_resource_journal=str(destination/'ENSAYOS.jsonl'),
        complete_native_root=str(destination),no_material_retry=True)
    write_new(output/'RESULTADO.json',report)
    if failure or intent is not None:raise RuntimeError('Load life preserved; inspect RESULTADO/PENDIENTE, no retry: '+str(failure))
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true')
    p.add_argument('--profile',choices=('LOAD1','LOAD2','LOAD3'),required=True);p.add_argument('--stage',type=int,choices=(1,),required=True)
    p.add_argument('--destination',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
    p.add_argument('--output',type=Path);p.add_argument('--barrier',type=Path)
    a=p.parse_args()
    if a.execute_root_only and(a.output is None or a.barrier is None):p.error('Explicit fresh output/barrier required')
    print(json.dumps(run(a),ensure_ascii=False,indent=2))
