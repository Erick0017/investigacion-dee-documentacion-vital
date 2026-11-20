"""Prepared same-life LOAD continuation: existing Q1 -> corrected Q2, then2/3.

No Q1 replay, import0, reset, Roblox action, expected numeric value or model.
Requires a separately reviewed completed zero-tick technical recovery first.
"""
from pathlib import Path
import argparse,copy,datetime,hashlib,importlib.util,json,os,sys,time,uuid
ROOT=Path(__file__).resolve().parents[1];PRODUCT=ROOT.parents[2]
LAST_NEW=1794902400;CUTOFF=1794906420
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def write_new(p,value):
    with p.open('x',encoding='utf8')as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def atomic(p,value):
    tmp=p.with_name(p.name+'.new_'+uuid.uuid4().hex);write_new(tmp,value);os.replace(tmp,p)
def append(p,value):
    with p.open('a',encoding='utf8')as f:f.write(json.dumps(value,ensure_ascii=False,separators=(',',':'))+'\n');f.flush();os.fsync(f.fileno())
def actual_action(result,identifier):
    need(result.get('action')in('ASK_STATION','SKIP_STATION','SAFE_WAIT','EXIT_0','EXIT_1')and type(result.get('null'))is bool,'ACTUAL_NATIVE_ACTION_ONLY')
    return dict(name=result['action'],null=result['null'],actionId=identifier,nativeTick=result['nativeTick'])
def consumed_stock(stock,action):
    need(type(stock)is int and stock>=0,'ACTUAL_FOCAL_PERMISSION_STOCK')
    used=int(action['name']=='ASK_STATION'and not action['null'])
    need(stock>=used,'NO_INVENTED_SUPPLY');return stock-used,used
def basis(a):
    root=a.destination.resolve(strict=True);need(root==ROOT/'native'/a.profile,'EXACT_EXISTING_LOAD_ROOT')
    tx=a.recovery_transaction.resolve(strict=True);result=read(tx/'RESULTADO.json')
    need(result['status']=='THREE_KNOWN_ZERO_ADMISSION_GUARDS_RECOVERED'and result['new_native_ticks']==0 and not result['remaining_intents'],'REVIEWED_TECHNICAL_RECOVERY_MUST_BE_COMPLETE')
    env=read(tx/a.profile/'ENVIRONMENT_VALIDATED.json');life=env['life'];need(env['profile']==a.profile and env['no_Q1_replay']is True,'EXACT_ORIGINAL_EPISODE')
    marker=read(root/'TECHNICAL_RECOVERY_APPLIED_R06.json');card=read(root/'sistema/estado/vidas'/life/'VIDA.json')
    need(marker['transaction']==str(tx)and marker['snapshot_after_sha256']==card['snapshot_sha256']and card['physical']['tick']==991543,'NO_MATERIAL_SINCE_RECOVERY')
    scope=read(root/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')
    need(scope['role']=='load'and scope['max_cycles']==3 and scope['native_cutoff_utc_epoch']==CUTOFF and scope['last_new_cycle_utc_epoch']==LAST_NEW,'FINITE_UNRESET_LOAD_SCOPE')
    budget=read(a.ledger);world=budget['worlds'][life]
    need(not budget['intents']and world['reserved']==3740 and world['consumed']==356 and world['cycles']==0,'CONTINUE_RESERVED_ORIGINAL_CYCLE_NOT_NEW_Q1')
    protocol=read(ROOT/'load/PROTOCOLO_CARGA_V3_R06.json')
    return root,life,env,protocol['lifes'][a.profile],scope
def run(a):
    root,life,env,profile,scope=basis(a)
    if not a.execute_root_only:return {'status':'PREFLIGHT_ONLY_NO_NATIVE','life':life,'first_phase':'query_sensor','source_tick':991543,'Q1_replay':False}
    output=a.output.resolve();need(output.is_relative_to(ROOT/'load')and not output.exists(),'FRESH_CONTINUATION_OUTPUT')
    need(time.time()<CUTOFF,'HARD_DRAIN_WINDOW');output.mkdir(parents=True)
    barrier=a.barrier.resolve(strict=True);need(barrier.is_relative_to(ROOT/'load'),'EXPLICIT_BATCH_BARRIER')
    freeze=read(ROOT/'control/CONGELADO_NATIVE_R07_LEASE_R06.json')
    for name in('native/owner_support_v3_R06.py','native/ledger_v3_R06.py'):
        pin=next(x['sha256']for x in freeze['files']if x['file']==name);need(sha(ROOT/name)==pin,'PINNED_R06_SUPPORT')
    need(sha(ROOT/'native/adapter_v3.py')=='378301b65f117a03ddfc834b18a2eb32d3d0164dea912292d0b1f84cb47dd137','UNCHANGED_NATIVE_ADAPTER')
    support=load(ROOT/'native/owner_support_v3_R06.py','_continued_load_owner_R06');adapters=load(ROOT/'native/adapter_v3.py','_continued_load_adapter_R06')
    owner=support.configured_owner(PRODUCT,root,a.ledger,tag='R07_'+a.profile+'_CONT_R06',cutoff_epoch=CUTOFF,continuous=True)
    state={'life':life,'session_id':env['session_id'],'sequence':58,'permission_stock':163,'completed_new':0,'last_action_id':None,'native_tick':991543,'world_time_ms':env['corrected_Q2_observation']['worldTimeMs'],'phase':'AWAIT_ROUTE_SENSOR'}
    results=[];failure=None;entered=left=None;pid=None;last_tick=991543;actual_a=None
    def phase(adapter,kind,payload,observation,index,identifier=None):
        identifier=identifier or a.profile+'_R06_E'+str(index+1)+'_'+kind.upper()
        ctx={'session_id':state['session_id'],'sequence':observation['seq'],'observation_id':observation['observationId'],'operation_id':identifier,'mode':'LIVE_NATIVE'}
        value={'event':'INTENT','context':ctx,'kind':kind,'payload':payload,'utc':stamp()};append(output/'FASES.jsonl',value);atomic(output/'PENDIENTE.json',value)
        start=time.monotonic();result=adapter.execute(kind,payload,ctx)
        append(output/'FASES.jsonl',{'event':'COMPLETED','context':ctx,'kind':kind,'result':result,'elapsed_seconds':time.monotonic()-start,'utc':stamp()})
        atomic(output/'PENDIENTE.json',{'status':'COMPLETED','id':identifier,'kind':kind,'utc':stamp()});return result,identifier
    def observe(phase_name,query_applied=False):
        state['sequence']+=1;state['world_time_ms']+=1
        return {'observationId':'obs_'+uuid.uuid4().hex,'seq':state['sequence'],'phase':phase_name,'worldTimeMs':state['world_time_ms'],
          'sampleTimeMs':state['world_time_ms'],'previousActionId':state['last_action_id'],
          'sensors':dict(station=2,stage=2,contact=2,inventoryKey=False,inventoryResource=False,queryAvailable=True,
            stationSignal=1 if phase_name=='ROUTE_CHOICE'and query_applied else-1,permissionStock=state['permission_stock'],publicContactCode=2,
            lastFailure=False,numberAPresent=True,codeBPresent=False,numberAVersion=1,codeBCurrent=False,goalDelivery=True)}
    try:
        with owner:
            entered=time.time();pid=owner.proc.pid;adapter=adapters.create_adapter({'owner':owner})
            write_new(output/'READY.json',{'utc':stamp(),'epoch':entered,'owner_pid':pid,'worker_pid':os.getpid(),'life':life,'resumes_original_Q1':True})
            deadline=time.monotonic()+600
            while not(barrier/'GO.json').exists():
                need(not(barrier/'ABORT.json').exists(),'BATCH_ABORT_BEFORE_NEXT_NATIVE_PHASE');need(time.monotonic()<deadline and time.time()<CUTOFF,'FINITE_BARRIER')
                owner.sample();time.sleep(.1)
            for index in range(3):
                if index>0 and(time.time()>=LAST_NEW or(barrier/'ABORT.json').exists()):break
                if index==0:
                    q1=env['original_Q1']['result'];q1id=env['original_Q1']['context']['operation_id'];first=actual_action(q1,q1id)
                    append(output/'FASES.jsonl',{'event':'ORIGINAL_Q1_REUSED_NO_REQUEST','original_id':q1id,'native_tick':991543,'utc':stamp()})
                    q2obs=copy.deepcopy(env['corrected_Q2_observation']);spent=1
                    route,routeid=phase(adapter,'query_sensor',{'observation':q2obs},q2obs,index,env['corrected_Q2_id']);action=actual_action(route,routeid);last=q2obs
                else:
                    q1obs=observe('QUERY_CHOICE');q1,q1id=phase(adapter,'decision',{'observation':q1obs},q1obs,index);first=actual_action(q1,q1id)
                    state['permission_stock'],spent=consumed_stock(state['permission_stock'],first);last=q1obs;action=first
                    if not first['null']:
                        q2obs=observe('ROUTE_CHOICE',first['name']=='ASK_STATION');route,routeid=phase(adapter,'query_sensor',{'observation':q2obs},q2obs,index)
                        action=actual_action(route,routeid);last=q2obs
                function=None;tool=None
                if not first['null']:
                    tool={'kind':'LESSON','items':profile['lesson']}if index==0 else {'kind':'CALCULATE','slot':'A'if index==1 else'B','form':'luma'if index==1 else'nara','left':6 if index==1 else actual_a,'right':2 if index==1 else 1}
                    if tool['kind']=='CALCULATE'and(type(tool['left'])is not int or not 0<=tool['left']<=32):
                        append(output/'FASES.jsonl',{'event':'TOOL_NOT_INVOKED','reason':'ACTUAL_NUMERIC_INPUT_UNAVAILABLE','tool':tool,'utc':stamp()})
                        function={'toolResult':{'kind':'CALCULATE','numeric_result':None,'reason':'ACTUAL_NUMERIC_INPUT_UNAVAILABLE'}}
                    else:function,_=phase(adapter,'function',{'tool':tool},last,index)
                    if index==1:
                        number=function['toolResult'].get('numeric_result');actual_a=number if type(number)is int and 0<=number<=32 else None
                public=None if function is None else function['toolResult']
                failed=bool(action['null'])or(public is not None and(public.get('reason')=='NATIVE_PARTIAL_ADMISSION'or tool['kind']=='CALCULATE'and type(public.get('numeric_result'))is not int))
                fields=dict(actionId=action['actionId'],seq=last['seq'],observationId=last['observationId'],worldTimeMs=last['worldTimeMs'],durationMs=0,
                  outcome='FOCAL_NO_ROBLOX_ACTUATION',collision=False,resourceCollected=False,resourceDelivered=False,permissionSpent=spent,materialConsequence=failed,lastObservation=last)
                returned,returnid=phase(adapter,'feedback',fields,last,index);need(returned.get('accepted')is True,'REAL_RETURN_CONFIRMED')
                last_tick=returned['nativeTick'];state.update(native_tick=last_tick,completed_new=index+1,last_action_id=action['actionId'],phase='IDLE')
                results.append({'index':index+1,'q1':first,'original_Q1_reused':index==0,'actual_final_action':action,'tool':tool,'public_tool_result':public,
                  'feedback_operation_id':returnid,'native_tick':last_tick,'Native_routes_observed_not_executed':True,'resource_counted_as_new':0,'permission_stock':state['permission_stock']})
                atomic(output/'PROGRESO_DURANTE.json',state)
        left=time.time();closed=owner.proc.poll()==0
    except BaseException as error:
        failure=type(error).__name__+': '+str(error);left=time.time();closed=owner.proc is not None and owner.proc.poll()==0
    budget=read(a.ledger);intent=budget.get('intents',{}).get(life)
    report={'schema':'DEE.RBX.IntegralV3.LoadWorker.ContinuationR06','profile':a.profile,'life':life,'owner_pid':pid,'worker_pid':os.getpid(),
      'owner_open_epoch':entered,'owner_closed_epoch':left,'closed':closed,'failure':failure,'pending_global_intent':intent,'native_tick':last_tick,'results':results,'state':state,
      'original_Q1_not_replayed':True,'continuation_new_ticks':last_tick-991543,'whole_new_ticks_since_PAR28':last_tick-991187,
      'scope':'Same three existing Native lives; host-assisted focal lesson/A/B sequence, no Roblox motion/resource, no merged memories or autonomous repair.'}
    write_new(output/'RESULTADO.json',report)
    if failure or intent is not None:raise RuntimeError('CONTINUATION_PRESERVED_NO_RETRY: '+str(failure))
    return {k:v for k,v in report.items()if k not in('results','state')}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true');p.add_argument('--profile',choices=('LOAD1','LOAD2','LOAD3'),required=True)
    p.add_argument('--destination',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--recovery-transaction',type=Path,required=True)
    p.add_argument('--output',type=Path);p.add_argument('--barrier',type=Path);a=p.parse_args()
    if a.execute_root_only:need(a.output and a.barrier,'EXPLICIT_FRESH_OUTPUT_AND_BARRIER')
    print(json.dumps(run(a),ensure_ascii=False,indent=2))
