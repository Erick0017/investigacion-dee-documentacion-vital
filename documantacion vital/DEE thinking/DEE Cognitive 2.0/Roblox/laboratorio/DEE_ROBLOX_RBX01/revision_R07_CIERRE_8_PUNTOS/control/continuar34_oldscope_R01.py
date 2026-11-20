"""Root-only continuation of the ONE already admitted episode34 after knownQ1.

Never BEGIN, never NativeQ1, never reset/restore World. Read Root's frozen completed
Q1 cache receipt, then submit only unoffered original planned IDs
Q2/function/feedback. Old21:07 hard lease stays in force until episode closes.
"""
from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,sys,time
ROOT=Path(__file__).resolve().parents[1];PRODUCT=ROOT.parents[2]
LIFE='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN'
SESSION='R07_MAIN_adc933c82cc74fb0bb19';CYCLE=34;Q1_ID='R07_'+SESSION+'_34_DECISION'
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p,name):
    s=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
def rows(p):return[json.loads(x)for x in Path(p).read_text('utf8').splitlines()if x.strip()]
def reconciled_receipt(source):
    path=source/'RECONCILIACION34_ROOT_R01.json';proof=read(path)
    need(proof.get('no_Native_request_submitted')is True and proof.get('no_BEGIN_no_Q1_material_replay')is True,'ROOT_RECONCILIATION_NO_REPLAY')
    raw=proof['raw_tool_responses']['R07_RECONCILE34_Q1_CACHED_RECEIPT'];need(raw.get('isError')is False,'CACHED_RECEIPT_SUCCESS')
    value=json.loads(raw['content'][0]['text']);need(value['before']==value['after'],'ROOT_LOOKUP_ZERO_WORLD_CHANGE')
    need(value['reconciliation']=='EXACT_ALREADY_APPLIED_Q1_CACHED_RESULT','EXACT_ROOT_RECONCILIATION_KIND')
    obs=value['result']['observation']
    need(obs['phase']=='ROUTE_CHOICE'and obs['seq']==68 and obs['previousActionId']==Q1_ID,'ROOT_ORIGINAL_Q2_OBSERVATION')
    need(value['after']['phase']=='Q2'and value['after']['S']['sessionId']==SESSION and value['after']['S']['lifeId']==LIFE and value['after']['S']['nativeTick']==999363,'ROOT_EXACT_PARTIAL_STATE')
    return path,value
def preflight(a):
    source=a.source_output.resolve(strict=True);destination=a.destination.resolve(strict=True)
    need(destination==ROOT/'native/MAIN'and source==ROOT/'evidencia/MAIN_BLOQUE_01_R03','EXACT_ORIGINAL_PARTIAL')
    events=rows(source/'EVENTS.jsonl');actor=rows(destination/'sistema/estado/servicios_locales'/LIFE/'RBX07_NATIVE_INTEGRAL_V3/events.jsonl')
    q1=[r for r in events if r.get('kind')=='NATIVE_COMPLETED'and r.get('operation_id')==Q1_ID]
    need(len(q1)==1 and q1[0]['result']['nativeTick']==999363 and q1[0]['result']['action']=='ASK_STATION'and q1[0]['result']['null']is False,'KNOWN_ACTUAL_Q1_ONLY')
    later={'R07_'+SESSION+'_34_'+k for k in('QUERY_SENSOR','FUNCTION','FEEDBACK')}
    need(not any(r.get('kind')=='NATIVE_INTENT'and r.get('context',{}).get('operation_id')in later for r in events),'NO_EXISTING_LATER_INTENT_MAY_REPLAY')
    need(not any(r.get('kind')=='PHASE_INTENT'and r.get('context',{}).get('operation_id')in later for r in actor),'NO_LATER_NATIVE_PHASE_ALREADY_ADMITTED')
    completed=[r for r in actor if r.get('kind')=='PHASE_COMPLETED'];need(completed[-1]['mode']=='eci01-rbx01-decision'and completed[-1]['tick']==999363,'LATEST_NATIVE_PHASE_Q1_COMPLETE')
    journal=rows(destination/'ENSAYOS.jsonl');closed=next(r for r in reversed(journal)if r.get('kind')in('OWNER_STARTED','OWNER_CLOSED'))
    need(closed['kind']=='OWNER_CLOSED'and closed['exit_code']==0 and closed['final_status']['running']is False and closed['final_status']['tick']==999363 and not closed['final_status'].get('uncertain_external_result',False),'OLD_OWNER_CLOSED_KNOWN_FUTURE')
    card=read(destination/'sistema/estado/vidas'/LIFE/'VIDA.json');need(card['physical']['tick']==999363,'EXACT_SAVED_Q1_TICK')
    ledger=read(a.ledger);w=ledger['worlds'][LIFE]
    need(not ledger['intents']and w['cycles']==5 and w['reserved']==3740 and w['last_completed']['id']==Q1_ID and ledger['consumed']==8176,'EXACT_PARTIAL_BUDGET_NO_RESET')
    need(read(destination/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json')['native_cutoff_utc_epoch']==1794863220 and not(destination/'LEASE_APPLIED_R05.json').exists(),'OLD_SCOPE_NOT_MIGRATED_WHILE_PARTIAL')
    path,receipt=reconciled_receipt(source)
    return events,q1[0]['result'],card,path,receipt
def run(a):
    original,first,card,receipt_path,receipt=preflight(a)
    if not a.execute_root_only:return{'status':'READ_ONLY_PREFLIGHT','tick':999363,'NativeQ1WillBeExecuted':False,'Native_calls':0}
    need(time.time()<1794863220-900,'ENOUGH_OLD_HARD_LEASE_FOR_EXISTING_EPISODE_DRAIN')
    output=a.output.resolve();need(output.is_relative_to(ROOT/'evidencia')and not output.exists(),'FRESH_CONTINUATION_OUTPUT')
    output.mkdir(parents=True);journal=output/'EVENTS.jsonl'
    def record(kind,**fields):
        with journal.open('a',encoding='utf8')as f:f.write(json.dumps({'kind':kind,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),**fields},ensure_ascii=False)+'\n');f.flush();os.fsync(f.fileno())
    transport=load(ROOT/'control/world_comprimido_v3_R03.py','_r07_original_scope_world_attach');world=transport.CompressedWorld(a.studio_id,output,record,expected_place='DEE_RBX01_R07_NATIVE.rbxlx')
    try:
        # Existing initialized World only. NO API.call for Q1: Root already
        # reconciled that completed cache, preserving the exact public packet.
        guard="local api=require(game:GetService('ServerScriptService').RBX01Server.WorldAPI_R07);local s=api.status();assert(s.phase=='Q2' and s.S.seq==68 and s.S.nativeTick==999363 and s.S.previousActionId=="+json.dumps(Q1_ID)+",'EXACT_EXISTING_WORLD_Q1_APPLIED');"
        before=world.mcp(guard+'return s','world_existing_q2_ro')
        need(before==receipt['after'],'WORLD_UNCHANGED_SINCE_ROOT_CACHED_RECEIPT')
        cached=receipt['result'];record('ORIGINAL_Q1_RECEIPT_USED',path=str(receipt_path),sha256=sha(receipt_path),Native_request_repeated=False,World_action_repeated=False)
        obs=cached['observation'];need(obs['phase']=='ROUTE_CHOICE'and obs['seq']==68 and obs['previousActionId']==Q1_ID,'ORIGINAL_PUBLIC_Q2_OBSERVATION')
        marker=a.source_output/'CONTINUACION34_INTENT.json'
        with marker.open('x',encoding='utf8')as f:json.dump({'output':str(output),'original_Q1_id':Q1_ID,'first_new_phase':'query_sensor','automatic_retry':False},f)
        support=load(ROOT/'native/owner_support_v3.py','_r07_original_scope_support_resume34');adapters=load(ROOT/'native/adapter_v3.py','_r07_original_adapter_resume34')
        def native(adapter,kind,payload,observation):
            identifier='R07_'+SESSION+'_34_'+kind.upper();ctx={'session_id':SESSION,'sequence':observation['seq'],'observation_id':observation['observationId'],'operation_id':identifier,'mode':'LIVE_NATIVE'}
            record('NATIVE_INTENT',cycle=34,phase=kind,payload=payload,context=ctx);started=time.monotonic();value=adapter.execute(kind,payload,ctx)
            record('NATIVE_COMPLETED',cycle=34,phase=kind,operation_id=identifier,result=value,wall_seconds=time.monotonic()-started);return value,identifier
        with support.configured_owner(PRODUCT,a.destination,a.ledger,tag='R07_RESUME_EXISTING34',cutoff_epoch=1794863220,continuous=True)as owner:
            adapter=adapters.create_adapter({'owner':owner});route,op=native(adapter,'query_sensor',{'observation':obs},obs)
            moved=world.call('WORLD_'+SESSION+'_34_Q2','action',{'action':{'name':route['action'],'actionId':op,'nativeTick':route['nativeTick'],'null':route['null']}})
            tool=None
            if moved.get('tool'):
                made,function_id=native(adapter,'function',{'tool':moved['tool']},obs);tool=made['toolResult']
                world.call('WORLD_'+SESSION+'_34_TOOL','tool',{'output':tool,'nativeTick':made['nativeTick'],'operationId':function_id})
            fields=world.call('WORLD_'+SESSION+'_34_FEEDBACK_FIELDS','feedback_fields',{})
            returned,feedback_id=native(adapter,'feedback',fields['feedback'],fields['observation'])
            final=world.call('WORLD_'+SESSION+'_34_COMPLETE','complete',{'nativeTick':returned['nativeTick'],'operationId':feedback_id})
            row={'cycle':34,'new_opportunity':6,'Native_Q1':first,'Native_Q2':route,'tool_result':tool,'actual_numeric':None if tool is None else tool.get('numeric_result'),
              'world_result':moved['result'],'executed_route':moved.get('executed_name'),'Native_route':moved.get('selected_name'),'state_after':final['S'],'boundary':final['boundary'],'host_order_prepared':False,'Q1_reused_from_original_completed':True}
            record('OPPORTUNITY_COMPLETED',**row);saved=owner.control('guardar');record('OFFICIAL_SAVE_COMPLETED',request_id=saved.get('id'))
        record('OWNER_CLOSED',life=LIFE,expected_tick=returned['nativeTick'])
        state=world.checkpoint('R07_PAIR_'+SESSION+'_C34_RECOVERED_ORIGINAL',output/'WORLD_CHECKPOINT.json')
        allrows=[r for r in original if r.get('kind')=='OPPORTUNITY_COMPLETED']+[row]
        need([r['cycle']for r in allrows]==list(range(29,35)),'SIX_ACTUAL_EPISODES_NO_DUPLICATE')
        result={'schema':'DEE.RBX01.R07.integrated.result.R01','identity':{'life':LIFE,'session':SESSION,'participant':'LIVE_NATIVE'},'source_tick':991187,
          'final_tick':state['native_tick'],'new_opportunities_completed':6,'global_completed':34,'rows':allrows,'owner_closed':True,
          'new_Native_ticks':state['native_tick']-991187,'resume_new_Native_ticks':state['native_tick']-999363,'original_Q1_executed_again':False,
          'world_checkpoint':str(output/'WORLD_CHECKPOINT.json'),'world_sha256':sha(output/'WORLD_CHECKPOINT.json'),'principal_modified':False,
          'source_original_attempt':str(a.source_output),'source_original_events_sha256':sha(a.source_output/'EVENTS.jsonl'),'new_scenario_sha256':state['scenario_sha256']}
        with(output/'RESULTADO.json').open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2)
        return {k:v for k,v in result.items()if k!='rows'}
    finally:world.close()
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--execute-root-only',action='store_true');p.add_argument('--source-output',type=Path,required=True);p.add_argument('--destination',type=Path,required=True);p.add_argument('--ledger',type=Path,required=True);p.add_argument('--output',type=Path);p.add_argument('--studio-id');a=p.parse_args()
    if a.execute_root_only:need(a.output is not None and a.studio_id,'EXPLICIT_ROOT_CONTINUATION_FIELDS')
    print(json.dumps(run(a),ensure_ascii=False,indent=2))
