"""Passive audit of the three closed, continued LOAD histories. No Native imports.

Checks closed transport using immutable SQLite reads, hashes frozen evidence,
and separates offered lexical labels from individually admitted input receipts.
It never changes a world, queue, ledger, receipt, or source record.
"""
from pathlib import Path
import argparse, collections, datetime, hashlib, json, sqlite3

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ('LOAD1', 'LOAD2', 'LOAD3')


def need(value, message):
    if not value:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as source:
        for block in iter(lambda: source.read(1048576), b''):
            digest.update(block)
    return digest.hexdigest()


def canonical(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                     separators=(',', ':')).encode('utf8')).hexdigest()


def source(path):
    return {'path': str(path), 'bytes': path.stat().st_size, 'sha256': sha(path)}


def events(path):
    return [json.loads(line) for line in path.read_text('utf8').splitlines() if line.strip()]


def queue_closed(native, life):
    database = native / 'sistema/estado/servicios_persistentes' / life / 'cola.sqlite3'
    need(not (native / 'sistema/estado/locks' / (life + '.lock')).exists(), 'NO_OWNER_LOCK')
    for suffix in ('-wal', '-journal'):
        auxiliary = Path(str(database) + suffix)
        need(not auxiliary.exists() or auxiliary.stat().st_size == 0, 'CLOSED_ZERO_WAL_OR_JOURNAL')
    before = sha(database)
    con = sqlite3.connect(database.resolve().as_uri() + '?mode=ro&immutable=1', uri=True)
    try:
        con.execute('BEGIN')
        owner = json.loads(con.execute("SELECT value FROM meta WHERE key='owner'").fetchone()[0])
        counts = dict(con.execute('SELECT status,COUNT(*) FROM requests GROUP BY status').fetchall())
        need(owner.get('running') is False, 'OFFICIAL_TRANSPORT_OWNER_CLOSED')
        need(not any(counts.get(status, 0) for status in ('queued', 'processing', 'uncertain')),
             'NO_PENDING_OR_UNCERTAIN_QUEUE')
        quick = con.execute('PRAGMA quick_check').fetchall()
        need(quick == [('ok',)], 'CLOSED_DATABASE_QUICK_CHECK')
        con.rollback()
    finally:
        con.close()
    need(before == sha(database), 'IMMUTABLE_QUEUE_READ_CHANGED_NO_BYTES')
    return dict(database=source(database), owner=owner, status_counts=counts,
                immutable_read=True, no_pending_or_uncertain=True)


def function_primary(native, life, event):
    identifier = event['context']['operation_id']
    path = (native / 'sistema/estado/servicios_locales' / life /
            'RBX07_NATIVE_INTEGRAL_V3/functions' / (identifier + '.json'))
    record = read(path)
    need(record['life_id'] == life and record['context'] == event['context'], 'EXACT_FUNCTION_LIFE_AND_CONTEXT')
    offered = record['visible_tool']
    normalized = record['requests_normalized']
    actual_signature = [{'channel': item['channel'], 'payload': item['payload'],
                         'offset': item['requested_tick'] - record['before_tick'],
                         'status': item['receipt']['status']}
                        for item in normalized]
    result = dict(primary=source(path), visible_tool=offered,
                  public_tool_result=record['public_tool_result'],
                  before_tick=record['before_tick'], after_tick=record['after_tick'],
                  actual_tick_dose=record['after_tick'] - record['before_tick'],
                  admission=record['Native_inputs'],
                  input_admission_complete=record['input_admission_complete'],
                  actual_input_signature_sha256=canonical(actual_signature))
    if offered['kind'] == 'LESSON':
        lessons = []
        for item in record['native_function']:
            lesson = item['native_lesson']
            requests = []
            for request in lesson['requests']:
                requests.append({key: request[key] for key in ('id', 'channel', 'tick', 'value', 'site', 'direction', 'receipt')})
            lessons.append(dict(form=item['form'], offered_sign=item['observed_sign'],
                                before_tick=item['before_tick'], after_tick=item['after_tick'],
                                requests=requests,
                                all_inputs_applied=all(x['receipt']['status'] == 'applied' for x in requests)))
        result['lexical_exposures'] = lessons
        result['offered_updates_are_not_proof_of_full_acquisition'] = True
    else:
        result['actual_composition'] = {
            'memory_value': record['public_tool_result'].get('memory_value'),
            'operation': record['public_tool_result'].get('operation'),
            'numeric_result': record['public_tool_result'].get('numeric_result'),
            'inputs': record['public_tool_result'].get('inputs'),
            'reason': record['public_tool_result'].get('reason'),
            'host_ordered_pipeline': True,
            'host_computed_arithmetic_result': False,
        }
    return result


def run(stage, output):
    stage = stage.resolve(strict=True)
    output = output.resolve()
    need(stage == ROOT / 'load/evidencia/CARGA3_CONTINUACION_R06', 'EXACT_EXECUTED_CONTINUATION')
    need(not output.exists() and output.parent == stage, 'FRESH_PASSIVE_OUTPUT')
    summary = read(stage / 'RESULTADO_ETAPA.json')
    ledger_path = ROOT / 'control/LEDGER_V3.json'
    ledger = read(ledger_path)
    need(not ledger['intents'], 'ALL_GLOBAL_MATERIAL_INTENTS_SETTLED')
    reports = []
    seen_lives, seen_sessions, seen_operations, seen_queues = set(), set(), set(), set()
    for profile in PROFILES:
        native = ROOT / 'native' / profile
        folder = stage / profile
        result = read(folder / 'RESULTADO.json')
        need(result['closed'] is True and result['failure'] is None and result['pending_global_intent'] is None,
             'THREE_SUCCESSFULLY_CLOSED_WORKERS')
        need(len(result['results']) == 3 and result['state']['completed_new'] == 3, 'EXACT_THREE_EPISODES_EACH')
        life = result['life']
        session = result['state']['session_id']
        need(life not in seen_lives and session not in seen_sessions, 'LIFE_AND_TRANSPORT_NAMESPACES_DISJOINT')
        seen_lives.add(life); seen_sessions.add(session)
        phases = events(folder / 'FASES.jsonl')
        intents = {}; completed = []; functions = []
        for event in phases:
            if event.get('event') == 'INTENT':
                operation = event['context']['operation_id']
                need(operation not in intents and operation not in seen_operations, 'NO_OPERATION_REUSE')
                need(event['context']['session_id'] == session, 'EXACT_SESSION_PER_CALL')
                intents[operation] = event; seen_operations.add(operation)
            elif event.get('event') == 'COMPLETED':
                operation = event['context']['operation_id']; initial = intents.pop(operation)
                need(initial['context'] == event['context'], 'SAME_ADMITTED_OPERATION_CONTEXT')
                completed.append(dict(kind=event['kind'], context=event['context'],
                                      payload=initial['payload'], result=event['result'],
                                      elapsed_seconds=event['elapsed_seconds'],
                                      intent_utc=initial['utc'], completed_utc=event['utc']))
                if event['kind'] == 'function':
                    functions.append(function_primary(native, life, event))
        need(not intents, 'NO_AMBIGUOUS_MATERIAL_INTENT')
        need(len([x for x in completed if x['kind'] == 'decision']) == 2, 'FIRST_Q1_WAS_NOT_REPLAYED')
        need(sum(x.get('event') == 'ORIGINAL_Q1_REUSED_NO_REQUEST' for x in phases) == 1,
             'ONE_ORIGINAL_Q1_REFERENCE_ONLY')
        card_path = native / 'sistema/estado/vidas' / life / 'VIDA.json'
        card = read(card_path); physical = card['physical']
        need(physical['N'] == 67 and physical['tick'] == result['native_tick'], 'EXACT_FINAL_PHYSICAL_TICK')
        snapshot = native / 'sistema' / card['snapshot']
        need(sha(snapshot) == card['snapshot_sha256'], 'FULL_FINAL_SNAPSHOT_SHA_MATCH')
        journal_path = native / 'ENSAYOS.jsonl'; journal = events(journal_path)
        closed = next(row for row in reversed(journal) if row.get('kind') in ('OWNER_STARTED', 'OWNER_CLOSED'))
        need(closed['kind'] == 'OWNER_CLOSED' and closed['exit_code'] == 0 and
             closed['pid'] == result['owner_pid'] and closed['final_status']['running'] is False and
             closed['final_status']['tick'] == result['native_tick'], 'LATEST_OFFICIAL_OWNER_CLOSED')
        transport = queue_closed(native, life)
        queue_path = transport['database']['path']
        need(queue_path not in seen_queues, 'PRIVATE_QUEUE_PATHS_DISJOINT'); seen_queues.add(queue_path)
        budget = ledger['worlds'][life]
        need(budget['cycles'] == 3 and budget['reserved'] == 0 and
             budget['consumed'] == result['whole_new_ticks_since_PAR28'], 'LEDGER_EQUALS_REAL_WHOLE_DOSE')
        env = read(ROOT / 'control/RECUPERACION_LOAD_R06_TX' / profile / 'ENVIRONMENT_VALIDATED.json')
        reports.append(dict(profile=profile, life=life, session_id=session,
                            source_tick=991187, final_tick=result['native_tick'],
                            whole_native_ticks=result['whole_new_ticks_since_PAR28'],
                            continuation_native_ticks=result['continuation_new_ticks'],
                            original_Q1=env['original_Q1'], original_Q1_not_replayed=True,
                            actual_calls=completed, functions=functions, episodes=result['results'],
                            physical_fingerprint_recorded_by_closed_official_owner=physical,
                            snapshot=source(snapshot), card=source(card_path), owner_closed=closed,
                            worker_result=source(folder/'RESULTADO.json'), phases=source(folder/'FASES.jsonl'),
                            owner_journal=source(journal_path), transport=transport, ledger_world=budget))
    pairs = []
    for index, left in enumerate(reports):
        for right in reports[index + 1:]:
            pairs.append(dict(left=left['profile'], right=right['profile'],
                              equal_final_RAW=left['physical_fingerprint_recorded_by_closed_official_owner']['RAW_sha256'] == right['physical_fingerprint_recorded_by_closed_official_owner']['RAW_sha256'],
                              equal_final_clocks=left['physical_fingerprint_recorded_by_closed_official_owner']['clocks_sha256'] == right['physical_fingerprint_recorded_by_closed_official_owner']['clocks_sha256'],
                              equal_actual_function_input_signatures=[x['actual_input_signature_sha256'] for x in left['functions']] == [x['actual_input_signature_sha256'] for x in right['functions']],
                              equal_actual_public_function_results=[x['public_tool_result'] for x in left['functions']] == [x['public_tool_result'] for x in right['functions']] ))
    report = dict(schema='DEE.R07.LOAD.closed_actual_history.R06',
                  observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  status='THREE_EXISTING_LIVES_THREE_REAL_CLOSED_EPISODES_EACH',
                  source=source(stage/'RESULTADO_ETAPA.json'), supervisor_status=summary.get('status'),
                  ledger=source(ledger_path), global_consumed=ledger['consumed'], global_intents=ledger['intents'],
                  lives=reports, pairwise_observations=pairs,
                  namespace_isolation=dict(unique_lives=3, unique_sessions=3, unique_private_queues=3,
                                           operation_ids=len(seen_operations),
                                           native_numeric_input_ids_are_scoped_to_life=True),
                  limits=['All lives descend from the same PAR28 prefix; they are paired technical continuations, not independent organisms.',
                          'LESSON/A/B order, operands, sensors, and consequences are prepared host assistance.',
                          'Actual Native recall selects the fixed SUM/DIFF codec and actual integers feed the next arithmetic step.',
                          'This focal LOAD test executes no Roblox motion and counts no Roblox resource.',
                          'A changed RAW hash alone does not establish useful memory; actual recall and integer outputs are reported separately.',
                          'Technical uncertainty recovery was external administration at zero ticks, not learned self-repair.'],
                  new_native_calls_by_audit=0, new_native_ticks_by_audit=0)
    with output.open('x', encoding='utf8') as out:
        json.dump(report, out, ensure_ascii=False, indent=2); out.write('\n')
    return dict(output=str(output), sha256=sha(output), status=report['status'],
                global_consumed=ledger['consumed'], pairwise_observations=pairs)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage-root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.stage_root, arguments.output), ensure_ascii=False, indent=2))
