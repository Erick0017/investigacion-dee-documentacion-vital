"""Passive closed-cut MAIN46 witness. No owner, Native, Studio, or model calls."""
from pathlib import Path
import datetime,hashlib,importlib.util,json
ROOT=Path(__file__).resolve().parents[1]
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source(p):return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def run():
    out=ROOT/'evidencia/MAIN_REAPERTURA_35_46_R07';proof=out/'CONCILIACION_CIERRE_R07.json';ledgercopy=out/'LEDGER_AL_CIERRE.json'
    need(not proof.exists()and not ledgercopy.exists(),'ONE_FRESH_CLOSED_WITNESS')
    result=read(out/'RESULTADO.json');life=result['identity']['life'];sid=result['identity']['session']
    need(life=='ECI02_PI03_REPRO_PI04_PI05_PI07_PI10_RBX01_INTEGRAL_V3_MAIN'and sid=='R07_MAIN_adc933c82cc74fb0bb19','SAME_MAIN_AND_SESSION')
    need(result['owner_closed']is True and result['source_tick']==1000571 and result['final_tick']==1019339 and
       result['new_opportunities_completed']==12 and result['global_completed']==46 and result['new_Native_ticks']==18768,'EXACT_35_TO46_NO47')
    worldfile=out/'WORLD_CHECKPOINT.json';world=read(worldfile)
    need(sha(worldfile)==result['world_sha256']and world['native_tick']==1019339 and world['native_life_id']==life,'FULL_WORLD_SHA_AND_CUT')
    need(world['boundary']['phase']=='BOUNDARY'and world['boundary']['native_phase']=='IDLE'and
       world['boundary']['next_opportunity']==47 and world['boundary']['uncertain']is False,'ACKNOWLEDGED_WORLD_BOUNDARY_NOT_NEW_SUPPLY')
    native=ROOT/'native/MAIN';cardfile=native/'sistema/estado/vidas'/life/'VIDA.json';card=read(cardfile)
    need(card['physical']['N']==67 and card['physical']['tick']==1019339,'CLOSED_NATIVE_PHYSICAL')
    snapshot=native/'sistema'/card['snapshot'];need(sha(snapshot)==card['snapshot_sha256'],'FULL_NATIVE_SNAPSHOT_SHA')
    journalfile=native/'ENSAYOS.jsonl';journal=[json.loads(x)for x in journalfile.read_text('utf8').splitlines()if x.strip()]
    closed=next(x for x in reversed(journal)if x.get('kind')in('OWNER_STARTED','OWNER_CLOSED'))
    need(closed['kind']=='OWNER_CLOSED'and closed['pid']==3352 and closed['exit_code']==0 and
       closed['final_status']['running']is False and closed['final_status']['tick']==1019339,'OFFICIAL_OWNER3352_EXIT0')
    events=[json.loads(x)for x in(out/'EVENTS.jsonl').read_text('utf8').splitlines()if x.strip()]
    pending={};calls=[]
    for event in events:
        if event['kind']=='NATIVE_INTENT':
            ctx=event['context'];need(ctx['session_id']==sid and 35<=event['cycle']<=46 and ctx['operation_id']not in pending,'NO_REPLAY_OR_SESSION_SUBSTITUTION')
            pending[ctx['operation_id']]=event
        elif event['kind']=='NATIVE_COMPLETED':
            initial=pending.pop(event['operation_id']);need(initial['phase']==event['phase']and initial['cycle']==event['cycle'],'SAME_ORIGINAL_CALL')
            calls.append(dict(context=initial['context'],cycle=event['cycle'],phase=event['phase'],result=event['result'],wall_seconds=event['wall_seconds']))
    need(not pending and len(calls)==42,'ALL_42_CALLS_COMPLETED')
    rows=result['rows'];need([x['cycle']for x in rows]==list(range(35,47)),'ALL_TWELVE_EPISODES_INCLUDED')
    parent=read(ROOT/'evidencia/MAIN_BLOQUE_01_CONTINUACION34_R01/WORLD_CHECKPOINT.json')['S'];end=rows[-1]['state_after']
    functions=[x['tool_result']for x in rows if x['tool_result']is not None]
    derived=dict(destinations=[x['state_after']['station']for x in rows],Q1=[x['Native_Q1']['action']for x in rows],Q2=[x['Native_Q2']['action']for x in rows],
      new_resources=end['resourceCount']-parent['resourceCount'],new_deliveries=end['delivered']-parent['delivered'],
      queries=end['queries']-parent['queries'],toll_spent=end['tollSpent']-parent['tollSpent'],permission_stock_before=parent['permissionStock'],permission_stock_after=end['permissionStock'],
      B_present=end['codeBPresent'],actual_functions=functions,overall_Main_new_episodes_since_PAR28=18,overall_Main_new_ticks_since_PAR28=28152)
    ledgerfile=ROOT/'control/LEDGER_V3.json';raw=ledgerfile.read_bytes();ledger=json.loads(raw);budget=ledger['worlds'][life]
    need(ledger['consumed']==51612 and not ledger['intents']and budget['consumed']==28152 and budget['cycles']==18 and budget['reserved']==0,'EXACT_CLOSED_LEDGER_NO_RESERVED_REPLAY')
    need(ledgerfile.read_bytes()==raw,'LEDGER_CHANGED_DURING_CAPTURE')
    with ledgercopy.open('xb')as f:f.write(raw)
    spec=importlib.util.spec_from_file_location('_readonly_closed_queue',ROOT/'load/auditar_historia_cerrada_LOAD_R06.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    transport=helper.queue_closed(native,life)
    scopefile=native/'sistema/capacidades/RBX07_NATIVE_SCOPE_INTEGRAL_V3.json';scope=read(scopefile)
    need(scope['role']=='main'and scope['max_cycles']==24 and scope['q2_sensor_arm']=='local_tag'and scope['native_cutoff_utc_epoch']==1794906420,'UNCHANGED_R06_SCOPE')
    cache=native/'sistema/app/cache_fuentes_C02.py';need(sha(cache)=='e4621d4875376a910511cadd55503daccadbd0a9787be8d99516417bf2e02adf','ORIGINAL_CACHE_NOT_REPLACED')
    report=dict(schema='DEE.R07.MAIN46.closed_cut.R07',utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
      status='MAIN35_TO46_CLOSED_SAME_GENEALOGY_FULL_WORLD',life=life,session=sid,result=source(out/'RESULTADO.json'),world=source(worldfile),
      native_card=source(cardfile),snapshot=source(snapshot),physical_fingerprint_recorded_by_official_owner=card['physical'],owner_closed=closed,
      owner_journal=source(journalfile),events=source(out/'EVENTS.jsonl'),transport=transport,scope=source(scopefile),
      literal_closed_ledger=source(ledgercopy),global_consumed=ledger['consumed'],global_intents=ledger['intents'],ledger_world=budget,
      actual_native_calls=calls,derived_results=derived,Native_Studio_model_executions_by_verification=0,
      limits=['No implicit47; next_opportunity47 is a cursor, not permission or supply.',
       'Only MAIN continued; no control/LOAD experiences were fused.',
       'Inherited held-key tuple remained actual; old word recall is not reacquisition of an unencountered new public sign.',
       'Technical collision restoration/camera/persistence are host assistance, not learned self-repair or Native vision.',
       'Closed native root and complete World remain local. This witness is not an executable backup.'])
    with proof.open('x',encoding='utf8')as f:json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    return dict(proof=str(proof),sha256=sha(proof),result_sha256=sha(out/'RESULTADO.json'),world_sha256=sha(worldfile),physical=card['physical'],snapshot_sha256=card['snapshot_sha256'],ledger_sha256=sha(ledgercopy),global_consumed=ledger['consumed'],derived=derived)
if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False,indent=2))
