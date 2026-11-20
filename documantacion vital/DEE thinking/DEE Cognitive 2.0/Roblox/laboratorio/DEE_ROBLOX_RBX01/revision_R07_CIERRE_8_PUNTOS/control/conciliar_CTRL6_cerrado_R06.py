"""Closed CTRL1 witness only: no Native, owner, Studio, or model execution."""
from pathlib import Path
import datetime,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]

def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def record(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))

def run():
    folder=ROOT/'evidencia/CTRL1_SEIS_R06';proof=folder/'CONCILIACION_CIERRE_R06.json'
    ledger_copy=folder/'LEDGER_AL_CIERRE.json'
    need(not proof.exists()and not ledger_copy.exists(),'FRESH_CLOSED_WITNESS_ONLY')
    result_path=folder/'RESULTADO.json';result=read(result_path);world_path=folder/'WORLD_CHECKPOINT.json';world=read(world_path)
    native=ROOT/'native/CTRL1';life=read(native/'CONTEXTO_EJECUCION.json')['life'];sid=result['identity']['session']
    need(result['identity']['life']==life and life.endswith('_V3_CTRL1')and result['owner_closed']is True,'EXACT_CLOSED_CONTROL')
    need(result['source_tick']==991187 and result['final_tick']==1000571 and result['new_Native_ticks']==9384 and
         result['new_opportunities_completed']==6 and result['global_completed']==34,'EXACT_SIX_NO_SEVENTH')
    need(world['native_life_id']==life and world['native_tick']==1000571 and sha(world_path)==result['world_sha256'],'CURRENT_WHOLE_WORLD_MATCH')
    need(world['boundary']['next_opportunity']==35 and world['boundary']['phase']=='BOUNDARY'and
         world['boundary']['native_phase']=='IDLE'and world['boundary']['uncertain']is False,'FULL_ACKNOWLEDGED_BOUNDARY')
    rows=result['rows'];need([x['cycle']for x in rows]==list(range(29,35)),'ALL_SIX_EPISODES_INCLUDED')
    phases=[json.loads(x)for x in(folder/'EVENTS.jsonl').read_text('utf8').splitlines()if x.strip()]
    pending={};calls=[]
    for event in phases:
        if event['kind']=='NATIVE_INTENT':
            ctx=event['context'];need(ctx['session_id']==sid and ctx['operation_id']not in pending,'EXACT_SINGLE_SESSION_UNIQUE_INTENT')
            pending[ctx['operation_id']]=event
        elif event['kind']=='NATIVE_COMPLETED':
            initial=pending.pop(event['operation_id']);need(initial['phase']==event['phase']and initial['cycle']==event['cycle'],'SAME_PHASE_ID')
            calls.append(dict(context=initial['context'],phase=event['phase'],cycle=event['cycle'],
              intent_utc=initial['utc'],completed_utc=event['utc'],wall_seconds=event['wall_seconds'],result=event['result']))
    need(not pending and len(calls)==21,'ALL_21_NATIVE_CALLS_COMPLETED_NO_PENDING_OR_REPLAY')
    need([x['Native_Q1']['action']for x in rows]==['ASK_STATION']*6 and
         [x['Native_Q2']['action']for x in rows]==['EXIT_1']*6,'REPORTED_ACTUAL_CHOICES')
    card_path=native/'sistema/estado/vidas'/life/'VIDA.json';card=read(card_path);snapshot=native/'sistema'/card['snapshot']
    need(card['physical']['N']==67 and card['physical']['tick']==1000571 and sha(snapshot)==card['snapshot_sha256'],'FINAL_FULL_SNAPSHOT_INTEGRITY')
    journal_path=native/'ENSAYOS.jsonl';journal=[json.loads(x)for x in journal_path.read_text('utf8').splitlines()if x.strip()]
    closed=next(x for x in reversed(journal)if x.get('kind')in('OWNER_STARTED','OWNER_CLOSED'))
    need(closed['kind']=='OWNER_CLOSED'and closed['pid']==12028 and closed['exit_code']==0 and
         closed['final_status']['running']is False and closed['final_status']['tick']==1000571,'OFFICIAL_OWNER_EXIT_ZERO')
    spec=importlib.util.spec_from_file_location('_closed_queue_only',ROOT/'load/auditar_historia_cerrada_LOAD_R06.py')
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    transport=helper.queue_closed(native,life) # stdlib immutable SQLite only; no Native import.
    scope_path=native/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json';scope=read(scope_path)
    need(scope['role']=='control'and scope['max_cycles']==6 and scope['q2_sensor_arm']=='constant_tag2'and
         scope['native_cutoff_utc_epoch']==1794906420,'FROZEN_R06_CONTROL_SCOPE')
    cache=native/'sistema/app/cache_fuentes_C02.py'
    need(sha(cache)=='e4621d4875376a910511cadd55503daccadbd0a9787be8d99516417bf2e02adf','ORIGINAL_CACHE_UNCHANGED')
    ledger_path=ROOT/'control/LEDGER_V3.json';ledger_bytes=ledger_path.read_bytes();ledger=json.loads(ledger_bytes)
    budget=ledger['worlds'][life]
    need(ledger['consumed']==32844 and not ledger['intents']and budget['consumed']==9384 and budget['cycles']==6 and budget['reserved']==0,'EXACT_CLOSED_GLOBAL_BUDGET')
    need(ledger_path.read_bytes()==ledger_bytes,'GLOBAL_LEDGER_CHANGED_DURING_READ')
    with ledger_copy.open('xb')as out:out.write(ledger_bytes)
    parent=read(native/'WORLD_PADRE_PAR28.json')['S'];end=rows[-1]['state_after'];destinations=[x['state_after']['station']for x in rows]
    derived=dict(destinations=destinations,last_three_outside_cycle=sum(x not in(2,3)for x in destinations[-3:]),
       sustained_exit_criterion_at_least_two=False,new_resources=end['resourceCount']-parent['resourceCount'],
       new_deliveries=end['delivered']-parent['delivered'],new_queries=end['queries']-parent['queries'],
       new_toll_spent=end['tollSpent']-parent['tollSpent'],permission_stock_initial=parent['permissionStock'],permission_stock_final=end['permissionStock'],
       B_present=end['codeBPresent'],actual_functions=[x['tool_result']for x in rows if x['tool_result']is not None])
    need(derived['last_three_outside_cycle']==0 and derived['new_resources']==0 and derived['new_deliveries']==0,'ACTUAL_REPORTED_NEGATIVE_RESULTS')
    report=dict(schema='DEE.R07.CTRL6.closed_witness.R06',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
       status='SIX_REAL_EPISODES_OWNER_WORLD_AND_LEDGER_CLOSED',life=life,session=sid,owner_closed=closed,
       result=record(result_path),world=record(world_path),events=record(folder/'EVENTS.jsonl'),journal=record(journal_path),
       card=record(card_path),snapshot=record(snapshot),physical_fingerprint_recorded_by_official_owner=card['physical'],
       transport=transport,scope=record(scope_path),original_cache_sha256=sha(cache),
       literal_closed_ledger=record(ledger_copy),global_consumed=ledger['consumed'],global_intents=ledger['intents'],ledger_world=budget,
       derived_results=derived,actual_native_calls=calls,
       limits=['Paired descendant from PAR28, not an independent individual. No experiences merged into MAIN.',
       'Camera follower and passive screen recorder are external host instrumentation; Native receives scalar inputs, not camera pixels.',
       'No sustained exit, B, new resource or new delivery was obtained in these six opportunities.',
       'Three inherited luma/actual arithmetic uses are retained capability, not newly acquired planning.',
       'Snapshot bytes were hashed; RAW/clocks fingerprints are the closed official owner record, not an independent Native rerun.'],
       verification_Native_MCP_model_calls=0)
    with proof.open('x',encoding='utf8')as out:json.dump(report,out,ensure_ascii=False,indent=2);out.write('\n')
    return dict(proof=str(proof),sha256=sha(proof),world_sha256=sha(world_path),result_sha256=sha(result_path),
                physical=card['physical'],ledger_sha256=sha(ledger_copy),global_consumed=ledger['consumed'],derived=derived)

if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
