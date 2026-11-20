"""PREPARED R03 fresh-episode driver; NOT materially reproduced end-to-end.

R06 proved its own original episode; this R07 adaptation is PREPARED until actually executed.
This fresh driver only corrects the raw-JSON-string deliverAction ABI, retains
R02 LF-normalized Source checks and all finite new R07 safety/cutoff guards.
Do not run on any advanced PILOT after991187 or imply a fresh scope/date/counter reset.

ONE fresh Native PILOT episode -> unchanged exported connector -> real body.

Root-only. Default preflight reads metadata and never opens SDK/Native. No model,
teacher, forced route, calculator or replay. Native seq=module seq+ancestral56.
"""
from pathlib import Path
import argparse,ctypes,datetime,hashlib,importlib.util,json,os,sys,time,uuid
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1];PRODUCT=ROOT.parents[2]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_PILOT'
CUTOFF=1794863220;LAST_NEW=1794859200
HEADER='local p=game:GetService("ServerScriptService").DEEConnector_R07;local API=require(p.Main);local a=API.lookupRuntime("R07_NATIVE_PILOT","map_b"):get("PILOT");local H=game:GetService("HttpService");'
def need(x,msg):
    if not x:raise ValueError(msg)
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def literal(v):return json.dumps(json.dumps(v,ensure_ascii=True,separators=(',',':')))
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def host_memory():
    class Memory(ctypes.Structure):
        _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong),('total',ctypes.c_ulonglong),('available',ctypes.c_ulonglong),
                  ('pageTotal',ctypes.c_ulonglong),('pageAvailable',ctypes.c_ulonglong),('virtualTotal',ctypes.c_ulonglong),('virtualAvailable',ctypes.c_ulonglong),('extended',ctypes.c_ulonglong)]
    need(os.name=='nt','The actual Windows host guard is required')
    value=Memory();value.length=ctypes.sizeof(value)
    need(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)),'Measured host memory unavailable')
    return dict(total_bytes=value.total,available_bytes=value.available,load_percent=value.load)
def native_observation(observation):
    need(observation['protocol']=='DEE.RBX.Connector.R01'and observation['namespace']=='R07_NATIVE_PILOT/map_b/PILOT','Exact module context')
    return dict(observationId=observation['observationId'],seq=observation['seq']+56,phase=observation['phase'],
        worldTimeMs=observation['worldTimeMs'],sampleTimeMs=observation['sampleTimeMs'],previousActionId=observation.get('previousActionId'),sensors=observation['sensors'])
def typed_result_code(code):
    # The SDK's structured-Luau conversion can turn arrays into numeric-keyed
    # objects. Encode the COMPLETE result inside Roblox; never guess list types.
    return 'local function r06TypedValue()\n'+code+'\nend\nreturn game:GetService("HttpService"):JSONEncode(r06TypedValue())'
def preflight(a):
    manifest=read(HERE/'MANIFIESTO_PILOTO_R07.json')
    need(sha(HERE/'DEEConnector_PILOTO_OTRO_MAPA_R07.rbxlx')==manifest['scene']['sha256'],'Prepared clean XML changed')
    need(a.destination.resolve(strict=True)==ROOT/'native/PILOT','Exact dedicated PILOT root only')
    scope=read(a.destination/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json');context=read(a.destination/'CONTEXTO_EJECUCION.json')
    need(context['life']==scope['life_id']==LIFE and scope['teacher_mode']=='paired'and scope['source_tick']==991187,'Declared PILOT/PAR28/teacher scope paired; no new teaching performed')
    need(scope['parent_native_cycles']==24 and scope['parent_last_sequence']==56,'Preserved PAR28 ancestry counters')
    imported=read(a.destination/'IMPORTACION_DIAGNOSTICA.json')
    need(imported['new_native_ticks']==0 and imported['comparison']['physical_equal']and imported['comparison']['causal_prefix_equal'],'Root full import0 first')
    card=read(a.destination/'sistema/estado/vidas'/LIFE/'VIDA.json');need(card['physical']['tick']==991187,'At most one fresh episode: advanced PILOT cannot be retried as new')
    journal=a.destination/'sistema/estado/servicios_locales'/LIFE/'RBX07_NATIVE_INTEGRAL_V3/events.jsonl'
    need(not journal.exists()or journal.stat().st_size==0,'Existing Native episode preserved; no new replay/ID')
    ledger=read(a.ledger);need(ledger['limit']==160000 and ledger['max_worlds']==6 and not ledger['intents'],'Single actual global ledger, no pending Native intents')
    need(ledger['consumed']+sum(x.get('reserved',0)for x in ledger['worlds'].values())+4096<=160000,'Global Native headroom')
    return dict(life=LIFE,source_tick=991187,scope_sha256=sha(a.destination/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json'),source_manifest=sha(HERE/'MANIFIESTO_PILOTO_R07.json'))
def execute(a):
    basis=preflight(a)
    if not a.execute_root_only:return dict(status='PREFLIGHT_ONLY_NO_NATIVE_OR_SDK',**basis)
    need(time.time()<LAST_NEW,'No new Native pilot episode after20:00UTC')
    memory=host_memory();need(memory['available_bytes']>=1536*1024**2,'Need1.5GiB actual free host RAM before this512MiB owner; no cap raised')
    output=a.output.resolve();need(output.is_relative_to(ROOT/'evidencia')and not output.exists(),'Fresh evidence output only');output.mkdir(parents=True)
    def record(kind,**fields):
        with(output/'EVENTS.jsonl').open('a',encoding='utf8')as f:f.write(json.dumps(dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),kind=kind,**fields),ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    client=load(ROOT/'control/mcp_persistente_v3.py','_native_clean_sdk');support=load(ROOT/'native/owner_support_v3.py','_native_clean_owner');adapters=load(ROOT/'native/adapter_v3.py','_native_clean_adapter')
    session_id=a.session or'R07_NATIVE_PILOT_'+uuid.uuid4().hex[:20]
    serial=0;native_outputs=[];acks=[];failure=None;owner=None;final_tick=991187;checkpoint=None
    with client.Session(a.studio_id,a.expected_place,output/'MCP_SESSION',seconds=min(7200,int(CUTOFF-time.time())))as sdk:
        def mcp(code,label,read_only=False):
            nonlocal serial
            code=typed_result_code(code)
            serial+=1;record('MCP_INTENT',label=label,code_sha256=hashlib.sha256(code.encode()).hexdigest())
            report=sdk.run('execute_luau',dict(studio_id=a.studio_id,datamodel_type='Server',code=code),output/f'MCP_{serial:03d}_{label}.json',180,read_only=read_only)
            need(report['status']=='REPLIED','SDK call not confirmed; preserve and never retry')
            value=client.decode_text(report['reply']['result']);need(isinstance(value,dict),'Structured module result')
            record('MCP_COMPLETED',label=label,result=value);return value
        try:
            hashes=mcp('local p=game:GetService("ServerScriptService").DEEConnector_R07;local e=game:GetService("EncodingService");local out={};for _,n in ipairs({"Main","BackendBinding","LiveAdapters_R07","MotorPathfinding_R07"})do local h=e:ComputeStringHash((p[n].Source:gsub(string.char(13)..string.char(10),string.char(10))),Enum.HashAlgorithm.Sha256);if #h==32 then h=(h:gsub(".",function(c)return string.format("%02x",string.byte(c))end))end;out[n]=h:lower()end;return out','verify_actual_module_sources',read_only=True)
            expected=read(HERE/'MANIFIESTO_PILOTO_R07.json')['modules_sha256']
            need(all(hashes.get(n)==expected[n]for n in('Main','BackendBinding','LiveAdapters_R07','MotorPathfinding_R07')),'Actual opened Studio module Sources differ; no Native owner opened')
            # Actual opened XML already contains unchanged Main/Bindings and the
            # injected adapter. No Source rewrite occurs in this live controller.
            mcp((HERE/'INSTALAR_PILOTO_R07.luau').read_text(encoding='utf8'),'install_scene_once')
            module_obs=mcp(HEADER+'a:bindSession(H:JSONDecode('+literal(dict(sessionId=session_id,lifeId=LIFE,nativeTick=991187))+'));return a:observe("QUERY_CHOICE")','bind_and_observe_Q1_once')
            owner=support.configured_owner(PRODUCT,a.destination,a.ledger,tag='R07_NATIVE_PILOT',cutoff_epoch=CUTOFF,continuous=True)
            with owner:
                adapter=adapters.create_adapter({'owner':owner})
                def native(kind,payload,observation):
                    nonlocal final_tick
                    operation='CLEAN_'+kind.upper()+'_'+uuid.uuid4().hex[:18]
                    context=dict(session_id=session_id,sequence=observation['seq'],observation_id=observation['observationId'],operation_id=operation,mode='LIVE_NATIVE')
                    record('NATIVE_INTENT',phase=kind,payload=payload,context=context)
                    value=adapter.execute(kind,payload,context);record('NATIVE_COMPLETED',phase=kind,operation_id=operation,result=value)
                    final_tick=value['nativeTick']
                    native_outputs.append(dict(kind=kind,operation_id=operation,result=value));return value,operation
                def deliver(value,operation,observation):
                    need(value.get('action')in('ASK_STATION','SKIP_STATION','SAFE_WAIT','EXIT_0','EXIT_1')and type(value.get('null'))is bool,'Actual Native name/NULL, no fallback')
                    wire=dict(protocol='DEE.RBX.Connector.R01',namespace=observation['namespace'],sessionId=session_id,seq=observation['seq'],observationId=observation['observationId'],
                        actionId=operation,operationId=operation,action=dict(name=value['action'],nativeTick=value['nativeTick'],null=value['null']),sourceKind='DEE_NATIVE')
                    ack=mcp(HEADER+'return a:deliverAction('+literal(wire)+')','deliver_'+str(len(acks))+'_once')
                    need(ack['actionId']==operation and ack['operationId']==operation and ack['executionStatus']=='EXECUTED','Exact real body ACK')
                    mcp(HEADER+'return a:confirmActionAck('+json.dumps(operation)+','+json.dumps(operation)+')','confirm_'+str(len(acks))+'_once')
                    acks.append(ack);return ack
                last=native_observation(module_obs);first,operation=native('decision',{'observation':last},last);ack=deliver(first,operation,module_obs)
                if first['action']in('ASK_STATION','SKIP_STATION'):
                    module_obs=mcp(HEADER+'return a:observe("ROUTE_CHOICE")','observe_Q2_once');last=native_observation(module_obs)
                    second,operation=native('query_sensor',{'observation':last},last);ack=deliver(second,operation,module_obs)
                result=ack['result']
                fields=dict(actionId=operation,seq=last['seq'],observationId=last['observationId'],worldTimeMs=result['worldTimeMs'],durationMs=result['durationMs'],outcome=result['outcome'],
                    collision=result['collision'],resourceCollected=result['resourceCollected'],resourceDelivered=result['resourceDelivered'],
                    permissionSpent=sum(x['result'].get('permissionSpent',0)for x in acks),materialConsequence=bool(result['collision']or result['invalidAction']),lastObservation=last)
                returned,feedback_id=native('feedback',fields,last);need(returned.get('accepted')is True,'Native feedback must complete')
                final_tick=returned['nativeTick']
                mcp(HEADER+'return a:completeFeedback(H:JSONDecode('+literal(dict(actionId=operation,feedbackOperationId=feedback_id,nativeTick=final_tick))+'))','complete_opportunity_once')
                owner.control('guardar')
            need(owner.proc.poll()==0,'Owner must close cleanly before world capture')
            checkpoint=mcp(HEADER+'return a:capture(H:JSONDecode('+literal(dict(backendWriterClosed=True,bridgeQuiescent=True,sessionId=session_id,lifeId=LIFE,nativeTick=final_tick,proofKind='CLOSED_OFFICIAL_OWNER_AFTER_ACTUAL_FEEDBACK'))+'))','closed_world_checkpoint')
            with(output/'WORLD_MODULE_CHECKPOINT.json').open('x',encoding='utf8')as f:json.dump(checkpoint,f,ensure_ascii=False,indent=2);f.write('\n')
        except BaseException as error:
            failure=type(error).__name__+': '+str(error);record('FAILED_PRESERVED',error=failure,no_retry=True)
    report=dict(schema='DEE.NativeCleanConnector.LiveResult.R01',status='ONE_LIVE_EPISODE_CLOSED'if failure is None else'FAILED_PRESERVED',
        basis=basis,session_id=session_id,native_outputs=native_outputs,body_acks=acks,
        final_tick=final_tick if failure is None else None,new_native_ticks=final_tick-991187 if failure is None else None,
        last_confirmed_phase_tick=final_tick,confirmed_phase_tick_delta=final_tick-991187,
        owner_closed=owner is not None and owner.proc is not None and owner.proc.poll()==0,failure=failure,
        module_checkpoint='WORLD_MODULE_CHECKPOINT.json'if checkpoint is not None else None,
        scope='ONE actual Native selector episode on PILOT drives unchanged exported connector and injected Humanoid body on another map; not replay, no new teacher, no new arithmetic, no host route override.',
        assistance='Prepared absolute ports on a different map, public panel1/bothfree with fixed local tags, transduction, opportunities and goal flag; no expected route/number given to Native.',
        source_sequence_mapping='Native seq=module seq+56; exact same observationId/session/actionId and actual previousActionId preserved.',
        host_memory_before=memory,owner_job_limit_bytes=536870912,principal_modified=False)
    with(output/'RESULTADO_LIVE.json').open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    if failure:raise RuntimeError('One live attempt preserved; no automatic retry: '+failure)
    return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true');p.add_argument('--destination',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True)
    p.add_argument('--studio-id');p.add_argument('--expected-place',default='DEEConnector_PILOTO_OTRO_MAPA_R07.rbxlx');p.add_argument('--output',type=Path);p.add_argument('--session')
    a=p.parse_args()
    if a.execute_root_only and(not a.studio_id or a.output is None):p.error('Actual Studio and fresh output required')
    print(json.dumps(execute(a),ensure_ascii=False,indent=2))
