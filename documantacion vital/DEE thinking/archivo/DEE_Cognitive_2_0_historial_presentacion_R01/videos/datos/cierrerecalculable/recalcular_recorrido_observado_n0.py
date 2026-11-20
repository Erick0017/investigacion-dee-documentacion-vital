"""Recalculate only recorded demonstration primaries; no HTTP or DEE imports.

Safe while the recording/owner run: it reads completed gzip results and the
append-only operator ledger. Partial last lines are explicitly reported, never
silently treated as a completed action. It does not choose any next action.
"""
from __future__ import annotations
import argparse
import collections
import csv
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path


def decode(value):
    if isinstance(value, str) and value[:1] in {'{', '['}:
        try:
            return json.loads(value)
        except ValueError:
            pass
    return value


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reduced(value, key=''):
    """Keep actual results, omit repeated microscopic arrays with provenance."""
    value = decode(value)
    if isinstance(value, dict):
        if {'raw', 'clock', 'state'} <= value.keys():
            return {'microscopic_witness_in_original_primary': True}
        result = {}
        for name, child in value.items():
            if name in {'panel', 'requests', 'physical', 'final', 'snapshot', 'before_panel',
                        'after_panel', 'state_before', 'state_after', 'admitted_recipe',
                        'all_generic_resources', 'frames', 'native_requests', 'input_requests',
                        'receipts', 'native_receipts', 'timeline', 'microstates'}:
                continue
            if name == 'candidates' and isinstance(child, list):
                result[name] = [{k: row[k] for k in row if not isinstance(row[k], (dict, list))
                                or k in {'site', 'direction'}}
                                for row in child if isinstance(row, dict)]
            elif name == 'raw_components' and isinstance(child, list) and len(child) > 32:
                result[name] = {'length': len(child), 'nonzero_index_value':
                                [[index, item] for index, item in enumerate(child) if item != 0],
                                'all_unlisted_values_are_exact_zero': True}
            else:
                result[name] = reduced(child, name)
        return result
    if isinstance(value, list):
        return [reduced(child, key) for child in value]
    return value


def receipt_groups(value, groups):
    value = decode(value)
    if isinstance(value, dict):
        receipt = value.get('receipt')
        if isinstance(receipt, dict) and 'id' in receipt:
            groups[str(receipt['id'])].append(receipt)
        for name, child in value.items():
            if name != 'receipt':
                receipt_groups(child, groups)
    elif isinstance(value, list):
        for child in value:
            receipt_groups(child, groups)


def count_receipts(rows):
    groups = collections.defaultdict(list)
    receipt_groups(rows, groups)
    counts = collections.Counter()
    conflicts = []
    exact = []
    terminal = {'applied', 'rejected_occupied', 'rejected_invalid', 'rejected', 'failed'}
    for ident, values in groups.items():
        distinct = {json.dumps(row, sort_keys=True) for row in values}
        terminal_values = [row for row in values if row.get('status') in terminal
                           or str(row.get('status', '')).startswith('rejected')]
        terminal_statuses = {row.get('status') for row in terminal_values}
        if len(terminal_statuses) > 1:
            conflicts.append({'id': ident, 'statuses': sorted(terminal_statuses)})
        chosen = terminal_values[-1] if terminal_values else values[-1]
        counts[chosen.get('status', 'unknown')] += 1
        exact.append({'id': int(ident), 'status': chosen.get('status'),
                      'channel': chosen.get('channels'), 'requested_tick': chosen.get('requested_tick'),
                      'effective_tick': chosen.get('effective_tick'), 'reason': chosen.get('reason'),
                      'aliases': len(values), 'distinct_alias_values': len(distinct)})
    return {'unique_native_request_ids_in_result_rows': len(groups), 'statuses': dict(counts),
            'terminal_conflicts': conflicts, 'requests': sorted(exact, key=lambda row: row['id']),
            'scope': 'Receipt objects in this operation result rows only, deduplicated by ID; not the whole world lifetime.'}


def salient_leaves(value, prefix=''):
    names = {'formed_native_command', 'native_operator_command', 'native_route_command',
             'selected_procedure', 'selected_operation', 'numeric_result', 'choice', 'task_success',
             'completed_task', 'completed_under_declared_limits', 'used_value', 'reported_value',
             'category', 'useful', 'quality_success', 'verified_file_goal_completed', 'abstention',
             'ambiguous', 'selected_action', 'response', 'result_value', 'accumulator_result'}
    rows = []
    if isinstance(value, dict):
        for key, child in value.items():
            path = prefix + '.' + key if prefix else key
            if key in names and not isinstance(child, (dict, list)):
                rows.append({'path': path, 'value': child})
            rows.extend(salient_leaves(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            rows.extend(salient_leaves(child, prefix + '[' + str(index) + ']'))
    return rows


def extract_job(primary):
    job = primary.get('job') or {}
    interface_result = decode(job.get('result')) or {}
    transport = interface_result.get('native_transport') or interface_result
    request = transport.get('request') if isinstance(transport, dict) else None
    if not isinstance(request, dict):
        return {'job_status': job.get('status'), 'interface_action': job.get('action'),
                'interface_result': reduced(interface_result), 'request_present': False}
    native = decode(request.get('result')) or {}
    result = decode(native.get('result')) or {}
    rows = result.get('rows', []) if isinstance(result, dict) else []
    return {'job_status': job.get('status'), 'job_error': job.get('error'),
            'interface_action': job.get('action'), 'transport_id': request.get('id'),
            'transport_status': request.get('status'), 'payload_sha256': request.get('payload_sha'),
            'payload': decode(request.get('payload')), 'before_tick': native.get('before_tick'),
            'after_tick': native.get('after_tick'), 'operation': native.get('operation'),
            'rows': reduced(rows), 'salient_observations': salient_leaves(reduced(rows)),
            'native_receipts': count_receipts(rows),
            'other_result_fields': reduced({key: value for key, value in result.items()
                                           if key not in {'rows', 'final'}}) if isinstance(result, dict) else result}


def extract_passive(primary):
    if 'life_id' not in primary:
        return {key: primary.get(key) for key in ('available', 'N', 'tick', 'captured_utc',
                'RAW_sha256', 'clocks_sha256') if key in primary}
    record = primary.get('record') or {}
    owner = primary.get('owner') or {}
    owner = owner.get('observation') or owner
    return {'life_id': primary.get('life_id'), 'pending': primary.get('pending'),
            'uncertain': primary.get('uncertain'), 'owned_by_this_app': primary.get('owned_by_this_app'),
            'record': {key: record.get(key) for key in ('life_id', 'world_id', 'parent', 'snapshot',
                'snapshot_sha256', 'physical', 'profile')},
            'owner': {key: owner.get(key) for key in ('life_id', 'running', 'paused', 'tick',
                'physical', 'uncertain_external_result', 'last_saved_tick')}}


def summarize_part(folder):
    ledger = folder / 'EVENTOS.jsonl'
    if not ledger.is_file():
        return {'part': folder.name, 'state': 'NOT_STARTED', 'steps': []}
    data = ledger.read_bytes()
    events, incomplete = [], []
    for index, line in enumerate(data.splitlines()):
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except ValueError:
            incomplete.append({'line': index + 1, 'bytes': len(line)})
    started = {row['step']: row for row in events if row.get('event') == 'step_started'}
    terminal = {row['step']: row for row in events if row.get('event') == 'job_terminal'}
    completed = {row['step'] for row in events if row.get('event') == 'step_completed'}
    observed = {row['step']: row for row in events if row.get('event') == 'passive_observation'}
    parts = []
    for ident, start in started.items():
        row = {'step': ident, 'kind': start.get('kind'), 'group': start.get('group'),
               'started_utc': start['utc'], 'elapsed_start_seconds': start['elapsed_seconds'],
               'completed_operator_step': ident in completed}
        capture_utc = start.get('capture_started_utc')
        if capture_utc:
            row['video_start_seconds'] = (datetime.fromisoformat(start['utc'].replace('Z', '+00:00'))
                - datetime.fromisoformat(capture_utc.replace('Z', '+00:00'))).total_seconds()
        end = terminal.get(ident) or observed.get(ident)
        if end:
            row.update(terminal_utc=end['utc'], elapsed_terminal_seconds=end['elapsed_seconds'])
            if capture_utc:
                row['video_terminal_seconds'] = (datetime.fromisoformat(end['utc'].replace('Z', '+00:00'))
                    - datetime.fromisoformat(capture_utc.replace('Z', '+00:00'))).total_seconds()
            primary_ref = end.get('primary')
            if primary_ref:
                primary_path = folder / primary_ref['file']
                if primary_path.is_file():
                    try:
                        actual_sha = sha(primary_path)
                        if actual_sha != primary_ref['sha256']:
                            raise ValueError('Primary hash differs from operator ledger')
                        with gzip.open(primary_path, 'rt', encoding='utf8') as stream:
                            primary = json.load(stream)
                        row['primary'] = {'file': str(primary_path.resolve()), 'sha256': actual_sha,
                                          'bytes': primary_path.stat().st_size}
                        row['observed'] = extract_job(primary) if 'job' in primary else extract_passive(primary)
                    except Exception as error:
                        row['primary_read_error'] = {'type': type(error).__name__, 'detail': str(error)}
                else:
                    row['primary_missing'] = str(primary_path)
        parts.append(row)
    finish = next((event for event in reversed(events) if event.get('event') == 'fixed_itinerary_finished'), None)
    report = folder / 'RESULTADO.json'
    return {'part': folder.name, 'state': 'CLOSED' if finish else 'IN_PROGRESS',
            'ledger_file': str(ledger.resolve()), 'ledger_sha256_at_read': hashlib.sha256(data).hexdigest(),
            'ledger_bytes_at_read': len(data), 'incomplete_lines': incomplete,
            'operator_result': json.loads(report.read_text(encoding='utf8')) if report.is_file() else None,
            'failures': [event for event in events if event.get('event') in
                         {'HTTP_failure_preserved', 'itinerary_aborted_preserve_future', 'job_deadline_preserved'}],
            'steps': parts}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    part_names = {path.name for path in args.data.glob('DEMO_PARTE_*') if path.is_dir()}
    part_names.update({'DEMO_PARTE_A', 'DEMO_PARTE_B'})
    result = {'schema': 'DEE20.offline_observed_demo_recalculation.v1',
              'no_http_no_native_no_actor_inputs': True,
              'attribution': 'Fixed operator itinerary; physical contents/results remain those of their recorded life.',
              'parts': [summarize_part(args.data / name) for name in sorted(part_names)]}
    all_ids = collections.defaultdict(list)
    for part in result['parts']:
        for row in part['steps']:
            for request in (row.get('observed') or {}).get('native_receipts', {}).get('requests', []):
                all_ids[str(request['id'])].append({'part': part['part'], 'step': row['step'], **request})
    all_statuses = collections.Counter()
    global_conflicts = []
    for ident, appearances in all_ids.items():
        statuses = {appearance['status'] for appearance in appearances}
        if len(statuses) != 1:
            global_conflicts.append({'id': int(ident), 'statuses': sorted(statuses)})
        else:
            all_statuses[next(iter(statuses))] += 1
    result['global_native_receipts_from_result_rows'] = {
        'unique_ids': len(all_ids), 'statuses': dict(all_statuses), 'conflicts': global_conflicts,
        'repeated_across_operation_primaries': {ident: [{'part': row['part'], 'step': row['step']}
            for row in appearances] for ident, appearances in all_ids.items() if len(appearances) > 1},
        'scope': 'Unique Native IDs discovered in the included result rows. Controls/idle ticks do not imply material inputs; no count is inferred from old cumulative counters.'}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    csv_path = args.out.with_suffix('.csv')
    with csv_path.open('w', encoding='utf-8-sig', newline='') as stream:
        fields = ['part', 'step', 'kind', 'video_start_seconds', 'video_terminal_seconds',
                  'job_status', 'transport_id', 'transport_status', 'before_tick', 'after_tick',
                  'native_inputs_unique', 'native_applied', 'native_not_applied', 'rows_json', 'primary_sha256']
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for part in result['parts']:
            for row in part['steps']:
                observation = row.get('observed') or {}
                receipts = observation.get('native_receipts') or {}
                counts = receipts.get('statuses') or {}
                writer.writerow({'part': part['part'], 'step': row['step'], 'kind': row['kind'],
                    'video_start_seconds': row.get('video_start_seconds'),
                    'video_terminal_seconds': row.get('video_terminal_seconds'),
                    **{key: observation.get(key) for key in ('job_status', 'transport_id', 'transport_status', 'before_tick', 'after_tick')},
                    'native_inputs_unique': receipts.get('unique_native_request_ids_in_result_rows'),
                    'native_applied': counts.get('applied', 0),
                    'native_not_applied': sum(n for status, n in counts.items() if status != 'applied'),
                    'rows_json': json.dumps(observation.get('rows'), ensure_ascii=False, separators=(',', ':')),
                    'primary_sha256': (row.get('primary') or {}).get('sha256')})
    print(json.dumps({'output': str(args.out.resolve()), 'csv': str(csv_path.resolve()),
        'parts': [{'part': part['part'], 'state': part['state'], 'steps': len(part['steps']),
                   'closed_jobs': sum('transport_status' in (row.get('observed') or {}) for row in part['steps']),
                   'failures': len(part.get('failures', []))} for part in result['parts']]}, ensure_ascii=False))


if __name__ == '__main__':
    main()
