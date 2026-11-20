"""Passive reconciliation of the one preserved LOAD batch. No Native/SQL/MCP."""
from pathlib import Path
import argparse,datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
ACTOR_SHA='89fe4343694b546d480b6d80d73af6d6d6813fec1b67b9f5a067d96846c03b4e'
def need(v,m):
    if not v:raise ValueError(m)
def read(p):return json.loads(Path(p).read_text('utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb')as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def rows(p):return[json.loads(x)for x in Path(p).read_text('utf8').splitlines()if x.strip()]
def stamp(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00')).timestamp()
def intersect(a,b):return[(max(x,z),min(y,w))for x,y in a for z,w in b if max(x,z)<min(y,w)]
def run(a):
    stage=a.stage_root.resolve(strict=True);need(stage==ROOT/'load/evidencia/CARGA3_R01','ONE_ORIGINAL_STAGE_ONLY')
    output=a.output.resolve();need(not output.exists()and output.parent==stage,'FRESH_PASSIVE_RESULT')
    summary=read(stage/'RESULTADO_ETAPA.json');need(summary['status']=='PARTIAL_OR_BLOCKED_PRESERVED','PRESERVE_REAL_PARTIAL_STAGE')
    ledger_path=ROOT/'control/LEDGER_V3.json';ledger=read(ledger_path);reports=[];common=None
    process_proof=read(a.process_proof);expected_pids={240,19092,9968,11812,16284,6540}
    need({x['pid']for x in process_proof['processes']}==expected_pids and all(x['present']is False for x in process_proof['processes']),'EXACT_RECORDED_OWNED_PIDS_ABSENT')
    actor=ROOT/'native/lease_R05_bundle/rbx07_native_v3.py';need(sha(actor)==ACTOR_SHA,'UNCHANGED_ACTOR_SOURCE')
    source=actor.read_text('utf8');guard=source.index("'Real station query consumes exactly one environmental permit'")
    pulse=source.index('requests.extend(h.submit_query',guard);need(guard<pulse,'STOCK_GUARD_DOMINATES_Q2_PULSES')
    for declared in summary['owners']:
        profile=declared['profile'];folder=stage/profile;r=read(folder/'RESULTADO.json');life=r['life'];native=ROOT/'native'/profile
        need(declared['exit_code']==1 and r['closed']is True and not declared['active_preserved'],'FAILED_WORKER_AND_CLOSED_NATIVE_OWNER')
        phases=rows(folder/'FASES.jsonl');pending={};completed=[];intervals=[]
        for event in phases:
            if event.get('event')=='INTENT':
                identifier=event['context']['operation_id'];need(identifier not in pending,'UNIQUE_INTENT');pending[identifier]=event
            elif event.get('event')=='COMPLETED':
                identifier=event['context']['operation_id'];first=pending.pop(identifier);need(first['context']==event['context'],'SAME_CALL_CONTEXT')
                completed.append(event);intervals.append((stamp(first['utc']),stamp(event['utc'])))
        need(len(completed)==1 and completed[0]['kind']=='decision'and completed[0]['result']['action']=='ASK_STATION'and completed[0]['result']['nativeTick']==991543,'ONE_ACTUAL_Q1_NO_REPLAY')
        need(len(pending)==1,'ONE_PRESERVED_FAILED_Q2');failed_id,failed_intent=next(iter(pending.items()));need(failed_intent['kind']=='query_sensor','Q2_ONLY')
        official_path=native/'ensayos'/(failed_id+'.json');official=read(official_path)
        need(official['status']=='failed_preserved','EXACT_FAILED_PRESERVED_QUEUE_RECEIPT')
        error=official['error'];error=json.loads(error)if isinstance(error,str)else error
        need(error['external_execution_may_be_uncertain']is False and error['detail']=='Real station query consumes exactly one environmental permit','KNOWN_HOST_CONTRACT_REJECTION')
        future=error['failed_native_future_preserved'];m=future['operational_dependencies']['RBX01']['progress']
        need(error['native_tick_after_attempt']==991543 and future['physical']['tick']==991543,'ZERO_Q2_TICKS_AFTER_ACTUAL_Q1')
        need(m['phase']=='AWAIT_ROUTE_SENSOR'and m['uncertain']is True and m['cycles']==0 and m['last_sequence']==56,'EXACT_PRESERVED_NATIVE_PHASE_AND_GUARD')
        need('q2_reader'not in m['pending']and m['pending']['question_released']is True,'NO_Q2_READER_OR_PULSE_RESULT_CREATED')
        need(m['pending']['context']==completed[0]['context'],'SAME_ORIGINAL_Q1_CONTEXT')
        need(failed_intent['payload']['observation']['sensors']['permissionStock']==164 and m['pending']['initial_observation']['sensors']['permissionStock']==164,'ORIGINAL_HOST_SUPPLY_BUG_NOT_HIDDEN')
        card_path=native/'sistema/estado/vidas'/life/'VIDA.json';card=read(card_path)
        need(card['physical']==future['physical'],'CURRENT_CLOSED_PHYSICAL_EQUALS_FAILED_FUTURE')
        snapshot=native/'sistema'/card['snapshot'];need(sha(snapshot)==card['snapshot_sha256'],'CURRENT_CLOSED_SNAPSHOT_INTEGRITY')
        journal_path=native/'ENSAYOS.jsonl';journal=rows(journal_path)
        last=next(x for x in reversed(journal)if x.get('kind')in('OWNER_STARTED','OWNER_CLOSED'))
        need(last['kind']=='OWNER_CLOSED'and last['exit_code']==0 and last['pid']==r['owner_pid']and last['final_status']['running']is False and last['final_status']['tick']==991543,'EXACT_LATEST_OWNER_CLOSED_NO_NATIVE_ADVANCE')
        resources=next(x for x in reversed(journal)if x.get('kind')=='OWNED_PROCESS_RESOURCES'and x['run']==last['run'])
        # Cached resource samples can precede process exit. They are retained,
        # not rewritten as a fresh zero. Direct OWNER_CLOSED.exit0 and the exact
        # six-PID OS absence proof above establish closure independently.
        budget=ledger['worlds'][life];need(budget['consumed']==356 and budget['cycles']==0 and budget['reserved']==3740 and ledger['intents'][life]['id']==failed_id,'EXACT_PRESERVED_BUDGET_NOT_CLEARED')
        common=intervals if common is None else intersect(common,intervals)
        reports.append({'profile':profile,'life':life,'owner_pid':r['owner_pid'],'worker_pid':declared['worker_pid'],'owner_closed':True,
          'actual_native_tick':991543,'new_actual_ticks':356,'complete_episodes':0,'stale_worker_tick_not_physical':r['native_tick'],
          'q1':completed[0],'failed_q2_intent':failed_intent,'failed_q2_id':failed_id,
          'failed_official_receipt':str(official_path),'failed_official_sha256':sha(official_path),
          'known_no_Q2_native_admission':{'external_uncertainty':False,'tick_delta':0,'guard_precedes_first_submit_query':True,'q2_reader_absent':True,'q1_request_list_preserved':m['pending']['requests']},
          'environment_transaction_needed':{'old_permission_stock':164,'actual_prior_ASK':True,'corrected_permission_stock':163,'Native_memory_must_not_be_rewritten_for_stock':True},
          'own_metadata_preserved_from_failed_snapshot':m,'physical':card['physical'],'card':str(card_path),'card_sha256':sha(card_path),
          'snapshot':str(snapshot),'snapshot_sha256':card['snapshot_sha256'],'owner_closed_run':last['run'],'owner_journal':str(journal_path),'owner_journal_sha256':sha(journal_path),
          'result_path':str(folder/'RESULTADO.json'),'result_sha256':sha(folder/'RESULTADO.json'),'phases_path':str(folder/'FASES.jsonl'),'phases_sha256':sha(folder/'FASES.jsonl'),
          'ledger_reserved':3740,'material_call_intervals':intervals,'last_resource_sample_may_precede_exit':resources})
    need(len(reports)==3 and ledger['consumed']==10452,'THREE_CLOSED_PARTIAL_LIVES_AND_GLOBAL_DOSE')
    result={'schema':'DEE.R07.LOAD3.failed_host_contract_reconciliation.R06','observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'stage_result':str(stage/'RESULTADO_ETAPA.json'),'stage_result_sha256':sha(stage/'RESULTADO_ETAPA.json'),'status':'THREE_Q1_REAL_ZERO_COMPLETE_EPISODES_KNOWN_Q2_HOST_REJECTION',
      'lives':reports,'material_call_common_overlap_seconds':sum(b-a for a,b in common),'material_call_common_intervals':common,
      'owner_lifetime_overlap_seconds_distinct':summary['owner_lifetime_common_overlap_seconds'],
      'global_ledger':str(ledger_path),'global_ledger_sha256':sha(ledger_path),'consumed':ledger['consumed'],'preserved_intents':ledger['intents'],
      'exact_owned_process_absence_proof':str(a.process_proof),'process_proof_sha256':sha(a.process_proof),
      'Native_or_SQL_MCP_calls_by_recalculation':0,'scope':'Completed adapter.execute Q1 wall intervals overlap. This includes host/checkpoint time; not simultaneous CPU-instruction proof. No lesson/arithmetic episode completed. No intent, phase, memory or cursor was repaired.'}
    with output.open('x',encoding='utf8')as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    return{'result':str(output),'sha256':sha(output),'status':result['status'],'actual_ticks':1068,'complete_episodes':0,'common_material_call_overlap_seconds':result['material_call_common_overlap_seconds']}
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--stage-root',type=Path,required=True);p.add_argument('--process-proof',type=Path,required=True);p.add_argument('--output',type=Path,required=True);print(json.dumps(run(p.parse_args()),indent=2))
