"""Independent stdlib-only reader of exact Full GUI/transport primaries.

No engine import, Runtime, ticks, network, SQLite mutation or answer repair.
Signs are decoded from RAW at the frozen common24/common36 gate sets, not from
formed_native_command, UI summaries or the evaluator's expected answer.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

N = 67
EXPECTED_PROTOCOL_SHA256 = '737e69cc5f77bb3cca49ae931c06e9707ca06473ffcb9055c09071dc075e9c59'
I, J, H, K = (33, 33, 33), (47, 47, 47), (47, 17, 47), (47, 7, 47)
CODEC24 = [(I, v) for v in [(1,0,0),(0,1,0),(1,1,0),(-1,1,0),(1,-1,0),(-1,-1,0),(-1,0,0),(0,-1,0)]] + [(J, v) for v in [(-1,0,0),(0,-1,0),(1,0,0),(0,1,0)]]
CODEC36 = CODEC24 + [(H,(1,0,0)),(H,(0,1,0)),(K,(-1,0,0)),(K,(0,-1,0)),(K,(1,0,0)),(K,(1,1,0))]
NONTERMINAL = {'queued', 'pending', 'scheduled', 'admitted'}


def load(path):
    data = Path(path).read_bytes()
    return json.loads(gzip.decompress(data) if str(path).endswith('.gz') else data)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fields(raw):
    if isinstance(raw, float) or isinstance(raw, bool):
        raise ValueError('RAW must be exact, not floating point or boolean')
    value = int(raw)
    if not 0 <= value < 2**64:
        raise ValueError('RAW outside uint64')
    direction = []
    for shift in (48, 52, 56):
        nibble = (value >> shift) & 15
        direction.append(nibble - 16 if nibble >= 8 else nibble)
    return {'state': value & 0xffffffff, 's_reg': (value >> 32) & 65535,
            'semantic': (value >> 60) & 15, 'direction': direction}


def gates(codec):
    result = {}
    for origin, direction in codec:
        for sign in (-1, 1):
            site = tuple((origin[i] + 4 * direction[i] + (sign if i == 2 else 0)) % N for i in range(3))
            if site in result:
                raise ValueError('Frozen lexical gate geometry is not unique')
            result[site] = sign
    return result


def decode_lexical(reader, read_tick=None):
    panel = reader.get('panel')
    if not isinstance(panel, list):
        return {'supported': False, 'reason': 'No complete RAW lexical panel'}
    expected = gates(CODEC36 if len(panel) == 36 else CODEC24 if len(panel) == 24 else [])
    sites = [tuple(row['site']) for row in panel]
    geometry = bool(expected) and len(sites) == len(set(sites)) and set(sites) == set(expected)
    candidates, mismatches, ticks, decoded = [], [], [], []
    for observation in panel:
        site, physical = tuple(observation['site']), fields(observation['raw'])
        decoded.append(physical)
        fields(observation['clock'])  # Exact uint64 type/range validation, not a clock interpretation.
        ticks.append(int(observation['tick']))
        for key, value in physical.items():
            if key in observation and observation[key] != value:
                mismatches.append({'site': list(site), 'field': key})
        sign = expected.get(site)
        if sign is not None and physical['state'] > 0 and physical['semantic'] == 1 and physical['direction'] == [0, 0, sign]:
            candidates.append({'site': list(site), 'sign': sign, 'raw': str(observation['raw']), 's_reg': physical['s_reg']})
    coherent = bool(ticks) and len(set(ticks)) == 1 and (read_tick is None or ticks[0] == int(read_tick))
    formed = candidates[0]['sign'] if geometry and coherent and not mismatches and len(candidates) == 1 else None
    return {'supported': True, 'common_gate_count': len(panel), 'exact_frozen_geometry': geometry,
            'same_declared_read_tick': coherent, 'field_decode_mismatches': mismatches,
            'candidates_from_RAW': candidates, 'formed_from_RAW': formed,
            'local_reader_panel_state_positive': sum(row['state'] > 0 for row in decoded),
            'local_reader_panel_RAW_nonzero': sum(int(row['raw']) != 0 for row in panel),
            'local_panel_is_not_global_occupancy': True,
            'ambiguous_from_RAW': len(candidates) > 1,
            'reported_sign_agrees': reader.get('formed_native_command') == formed,
            'NULL_is_not_zero': True}


def admission(requests):
    rows = requests if isinstance(requests, list) else []
    statuses = Counter(row.get('receipt', {}).get('status', 'no_receipt') for row in rows)
    reasons = Counter(str(row.get('receipt', {}).get('reason')) for row in rows if row.get('receipt', {}).get('reason') is not None)
    cue = [row for row in rows if '.cue.' in str(row.get('channel', row.get('port', ''))) or str(row.get('channel', row.get('port', ''))).startswith('cue.')]
    return {'requested': len(rows), 'statuses': dict(statuses), 'receipt_reasons': dict(reasons),
            'applied': statuses['applied'],
            'rejected': sum(count for status, count in statuses.items() if status.startswith('rejected')),
            'all_declared_inputs_applied': bool(rows) and statuses['applied'] == len(rows),
            'cue_requested': len(cue), 'cue_applied': sum(row.get('receipt', {}).get('status') == 'applied' for row in cue),
            'resident_signal_not_current_use_if_rejected': True}


def decode_route(route):
    if not isinstance(route, dict) or not isinstance(route.get('reader'), dict):
        return None
    reader = route['reader']
    observations = reader.get('observations', [])
    expected = {((25 + 2*s) % N, 15, 53): s for s in (-1, 0, 1)}
    exact = len(observations) == 3 and {tuple(row['site']) for row in observations} == set(expected)
    candidates = []
    for row in observations:
        value = fields(row['raw']); sign = expected.get(tuple(row['site']))
        if sign is not None and value['state'] > 0 and value['semantic'] == 1 and value['direction'] == [sign, 1, 0]:
            candidates.append(sign)
    choice = candidates[0] if exact and len(candidates) == 1 else None
    return {'exact_R04_three_actuator_sites': exact, 'candidates_from_RAW': candidates,
            'choice_from_RAW': choice, 'reported_choice_agrees': reader.get('choice') == choice,
            'admission': admission(route.get('requests'))}


def decode_numeric(native):
    if not isinstance(native, dict) or not isinstance(native.get('native_trial'), dict):
        return None
    trial = native['native_trial']; at = int(trial['datum_tick']) - 2
    frames = [frame for frame in trial.get('frames', []) if int(frame['tick']) == at]
    if len(frames) != 1 or 'C' not in frames[0].get('fields', {}):
        return {'supported': False, 'reason': 'No unique frozen numeric C RAW observation'}
    observation = frames[0]['fields']['C']; physical = fields(observation['raw'])
    valid = observation['site'] == [12,17,18] and int(observation['tick']) == at and physical['state'] > 0 and physical['semantic'] == 1 and physical['direction'] == [1,-1,-1]
    operation = native.get('operation')
    result = physical['s_reg'] - (32 if operation == 'diferencia' else 0) if valid and operation in ('suma','diferencia') else None
    return {'supported': True, 'fixed_site_direction_valid_from_RAW': valid, 'raw': str(observation['raw']),
            'tick': at, 'numeric_from_RAW': result,
            'reported_numeric_agrees': native.get('numeric_reader', {}).get('numeric_result') == result,
            'admission': admission(trial.get('requests')),
            'scope': 'Prepared native aggregation and fixed numeric conversion; not learned arithmetic.'}


def parse_result(value):
    if isinstance(value, str):
        value = json.loads(value)
    return value if isinstance(value, dict) else {}


def native_rows(transport):
    value = parse_result(transport.get('result'))
    return value, value.get('result', {}).get('rows', [])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--protocol', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError('Use a fresh recalculation output; never overwrite prior results')
    root, protocol = args.root.resolve(), load(args.protocol)
    if digest(args.protocol) != EXPECTED_PROTOCOL_SHA256 or protocol.get('status') != 'CLOSED_FOR_EXACT_FULL_APD05_GUI_PROOF':
        raise ValueError('The prospective protocol bytes differ; do not retrospectively retarget this reader.')
    http, sources, step_rows, states, frame_witnesses = [], [], {}, [], []
    for path in sorted(root.glob('PHASE_*/HTTP_PRIMARIO.jsonl.gz')):
        sources.append({'file': str(path.relative_to(root)), 'bytes': path.stat().st_size, 'sha256': digest(path)})
        for line in gzip.decompress(path.read_bytes()).decode('utf8').splitlines():
            row = json.loads(line); row['_phase'] = path.parent.name; http.append(row)
            if row.get('path') == '/api/frame' and isinstance(row.get('response'), dict) and row['response'].get('available'):
                value = row['response']
                frame_witnesses.append({'phase': path.parent.name, 'wall_utc': row.get('wall_utc'),
                    **{key: value.get(key) for key in ('life_id','N','tick','coherent_tick','captured_utc','RAW_sha256','clocks_sha256','counts','coverage')}})
            if row.get('event') == 'gui_job_terminal':
                if row['step'] in step_rows:
                    raise ValueError('Duplicate terminal step, not an independent trial: ' + row['step'])
                step_rows[row['step']] = row
                states.append(row.get('status', {}))
    transports = []
    for path in sorted(root.glob('PHASE_*/TRANSPORTE_FINAL.json')):
        sources.append({'file': str(path.relative_to(root)), 'bytes': path.stat().st_size, 'sha256': digest(path)})
        transports.append(load(path))
    if not http:
        output = {'schema': 'APD05.Full_GUI_independent_RAW_recalculation.R01',
            'evaluation_state': 'NOT_EXECUTED_NO_COMPLETE_PRIMARY_PHASE', 'native_ticks_added': 0,
            'protocol_sha256': digest(args.protocol), 'sources': sources,
            'available_HTTP_primary_files': sum(row['file'].endswith('HTTP_PRIMARIO.jsonl.gz') for row in sources),
            'available_transport_phases': len(transports), 'observed_native_trials': None,
            'criterion_failures': None,
            'reason': 'No paired completed HTTP/transport primary phase is available. This is not zero successful cognitive trials, a failed Native experiment or a completed Full test.',
            'scope': 'Archived N0 availability result only; no world or missing observation was manufactured.'}
        args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
        print(json.dumps(output, ensure_ascii=True, indent=2)); return
    http_only = not transports
    if http_only:
        # An interrupted phase can preserve completed outbox results in HTTP
        # even though the final independent SQLite/journal cut was not reached.
        # Read those bytes as partial evidence; never synthesize a DB/journal.
        observed_requests = {}
        for entry in step_rows.values():
            result = entry.get('job', {}).get('result', {})
            request = result.get('request') if isinstance(result, dict) else None
            if isinstance(request, dict) and request.get('id'):
                observed_requests[request['id']] = request
        final = {'transport_rows': list(observed_requests.values())}
    else:
        final = transports[-1]
    latest = {row['id']: row for row in final.get('transport_rows', [])}
    step_ids = {}
    for step, entry in step_rows.items():
        result = entry.get('job', {}).get('result', {})
        request = result.get('request') if isinstance(result, dict) else None
        if request and request.get('id'):
            step_ids[request['id']] = step
    trials, receipts, receipt_conflicts = [], {}, []
    for identifier, transport in latest.items():
        value, rows = native_rows(transport)
        for number, row in enumerate(rows):
            reader = row.get('reader') or row.get('word', {}).get('reader')
            lexical = decode_lexical(reader, row.get('read_tick', row.get('word', {}).get('read_tick'))) if reader and 'panel' in reader else None
            requests = row.get('requests', row.get('word', {}).get('requests'))
            evidence = {'transport_id': identifier, 'transport_status': transport['status'],
                'step': step_ids.get(identifier), 'row_index': number, 'kind': row.get('kind'),
                'form': row.get('form', row.get('literal_form')), 'before_tick': value.get('before_tick'),
                'after_tick': value.get('after_tick'), 'lexical_RAW': lexical,
                'lexical_admission': admission(requests), 'route_RAW': decode_route(row.get('route')),
                'numeric_RAW': decode_numeric(row.get('native_numeric')),
                'teacher_sign_explicit': row.get('teacher_sign'), 'revision': row.get('revision'),
                'committed_effect': row.get('committed_effect')}
            if lexical or evidence['numeric_RAW'] or evidence['teacher_sign_explicit'] is not None:
                trials.append(evidence)
            def walk(node):
                if isinstance(node, list):
                    for item in node: walk(item)
                elif isinstance(node, dict):
                    if isinstance(node.get('receipt'), dict) and 'id' in node:
                        key = int(node['id']); receipt = node['receipt']
                        if int(receipt.get('id', key)) != key: receipt_conflicts.append({'id': key, 'reason': 'receipt ID mismatch'})
                        requested = node.get('tick')
                        if requested is not None and receipt.get('requested_tick') != requested: receipt_conflicts.append({'id': key, 'reason': 'requested tick mismatch'})
                        channel = node.get('channel', node.get('port'))
                        if channel and channel not in receipt.get('channels', []): receipt_conflicts.append({'id': key, 'reason': 'Native channel mismatch'})
                        if receipt.get('status') == 'applied' and receipt.get('effective_tick') != receipt.get('requested_tick'): receipt_conflicts.append({'id': key, 'reason': 'effective tick mismatch'})
                        old = receipts.get(key)
                        if old:
                            for field in ('id', 'kind', 'channels', 'requested_tick'):
                                if field in old and field in receipt and old[field] != receipt[field]: receipt_conflicts.append({'id': key, 'reason': 'receipt invariant mismatch', 'field': field})
                            if old.get('status') not in NONTERMINAL and receipt.get('status') not in NONTERMINAL and old != receipt: receipt_conflicts.append({'id': key, 'reason': 'conflicting terminal receipts'})
                        if old is None or receipt.get('status') not in NONTERMINAL: receipts[key] = receipt
                    for child in node.values(): walk(child)
            walk(row)
    pending_id = protocol['pending_transport_id']
    pending = [row for row in final.get('transport_rows', []) if row['id'] == pending_id]
    sessions = final.get('sessions', [])
    puts = [row for row in sessions if row.get('event') == 'literal_material_submission' and row.get('id') == pending_id]
    posts = [row for row in http if row.get('path') == '/api/action' and row.get('request', {}).get('action') == 'ejecutar' and (row['request'].get('value') or {}).get('id') == pending_id]
    expected = {'prior_clasifica': 1, 'old_luma_before_revision': 1, 'old_nara_before_revision': -1,
        'use_revised_association': -1, 'retention_old_luma': 1, 'retention_old_nara': -1,
        'retention_revised_association_after_reopen': -1, 'retention_old_luma_after_reopen': 1,
        'retention_old_nara_after_reopen': -1}
    checks = []
    for step, expected_sign in expected.items():
        matches = [row for row in trials if row['step'] == step and row['lexical_RAW']]
        observed = len(matches) == 1
        checks.append({'step': step, 'evaluation_state': 'OBSERVED' if observed else 'NOT_EXECUTED' if step not in step_rows else 'NO_RECALCULABLE_NATIVE_ROW', 'observed_rows': len(matches), 'expected_auditor_only': expected_sign,
            'raw_sign': matches[0]['lexical_RAW']['formed_from_RAW'] if len(matches) == 1 else None,
            'all_inputs_applied': matches[0]['lexical_admission']['all_declared_inputs_applied'] if len(matches) == 1 else False,
            'fulfilled': (matches[0]['lexical_RAW']['formed_from_RAW'] == expected_sign and matches[0]['lexical_RAW']['exact_frozen_geometry'] and matches[0]['lexical_RAW']['same_declared_read_tick'] and not matches[0]['lexical_RAW']['field_decode_mismatches'] and matches[0]['lexical_admission']['all_declared_inputs_applied']) if observed else None})
    pending_trial = [row for row in trials if row['transport_id'] == pending_id and row['lexical_RAW']]
    output = {'schema': 'APD05.Full_GUI_independent_RAW_recalculation.R01', 'native_ticks_added': 0,
        'evaluation_state': 'PARTIAL_HTTP_ONLY_NO_FINAL_TRANSPORT_CUT' if http_only else 'COMPLETE_PRIMARY_PHASES' if len(transports)==len(protocol['phases']) else 'PARTIAL_COMPLETED_PRIMARY_PHASES',
        'protocol_sha256': digest(args.protocol), 'sources': sources,
        'actual_http_records': len(http), 'actual_terminal_step_records': len(step_rows),
        'terminal_steps': [{'step': step, 'action': row.get('job', {}).get('action'),
            'job_status': row.get('job', {}).get('status'), 'error': row.get('job', {}).get('error'),
            'owner_observation': row.get('status', {}).get('owner')}
            for step, row in step_rows.items()],
        'available_transport_phases': len(transports), 'trials': trials, 'prospective_sign_checks': checks,
        'passive_frame_global_counts': frame_witnesses,
        'unique_native_receipts': len(receipts), 'native_statuses': dict(Counter(r.get('status') for r in receipts.values())),
        'receipt_consistency_errors': receipt_conflicts,
        'pending_exactly_once': {'id': pending_id, 'evaluation_state': 'OBSERVED_COMPLETE' if len(transports)==len(protocol['phases']) and pending else 'NOT_EXECUTED' if not posts else 'OBSERVED_PARTIAL_NOT_YET_RECONCILED', 'http_material_POSTs': len(posts), 'session_material_submissions': len(puts),
            'transport_rows_observed': len(pending), 'independent_final_DB_available': not http_only, 'final_status': pending[0]['status'] if len(pending)==1 else None,
            'first_reconciled_sign_from_RAW': pending_trial[0]['lexical_RAW']['formed_from_RAW'] if len(pending_trial)==1 else None,
            'all_inputs_applied': pending_trial[0]['lexical_admission']['all_declared_inputs_applied'] if len(pending_trial)==1 else False,
            'revised_content_used_in_pending': len(pending_trial)==1 and pending_trial[0]['lexical_RAW']['formed_from_RAW']==-1 and pending_trial[0]['lexical_admission']['all_declared_inputs_applied'],
            'fulfilled': (len(posts)==len(puts)==len(pending)==1 and pending[0]['status']=='completed') if len(transports)==len(protocol['phases']) else None},
        'complete_paired_imports_in_session_journal': sum(row.get('event')=='explicit_complete_paired_import' for row in sessions) if not http_only else None,
        'observed_lives': sorted({state.get('life_id') for state in states if state.get('life_id')}),
        'final_protocol_evidence_available': not http_only,
        'final_protocol_pending': final.get('protocol', {}).get('pending_material') if not http_only else 'NOT_AVAILABLE',
        'final_protocol_uncertain': final.get('protocol', {}).get('uncertain_preserved') if not http_only else 'NOT_AVAILABLE',
        'scope': 'Finite software/transport/lexical/numeric observations, not general Spanish, NSM65, learned attention, autonomous recovery, another computer or independent learner replicas. Missing/partial/NULL/rejected observations remain explicit.'}
    args.out.write_text(json.dumps(output, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
    print(json.dumps({'output': str(args.out), 'trials': len(trials), 'receipt_statuses': output['native_statuses'],
        'sign_checks_satisfied': sum(row['fulfilled'] is True for row in checks), 'sign_checks_observed': sum(row['evaluation_state']=='OBSERVED' for row in checks), 'sign_checks_NOT_EXECUTED_or_not_evaluable': sum(row['fulfilled'] is None for row in checks),
        'pending': output['pending_exactly_once'], 'receipt_consistency_error_count': len(receipt_conflicts)}, ensure_ascii=True, indent=2))


if __name__ == '__main__': main()
