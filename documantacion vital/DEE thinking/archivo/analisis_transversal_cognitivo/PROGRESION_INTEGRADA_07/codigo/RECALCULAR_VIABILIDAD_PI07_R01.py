"""Passive four-case calibration check. Stdlib only; never imports DEE.

Reads closed Root execution summaries and their literal primaries. No primary,
Native state, protocol or original source is changed; output must be new.
"""
from pathlib import Path
import argparse
import hashlib
import json


CASES = {
    'THREAT_PULSE': {'cue': 'threat', 'message': None, 'motor': 1,
                     'fi': 1, 'failure': False, 'delta': -2,
                     'requested': 184, 'applied': 184, 'rejected': 0},
    'THREAT_NONE': {'cue': 'threat', 'message': None, 'motor': -1,
                    'fi': -1, 'failure': True, 'delta': -1,
                    'requested': 183, 'applied': 183, 'rejected': 0},
    'MSG_PULSE': {'cue': 'falsecue', 'message': 5, 'motor': 1,
                  'fi': 1, 'failure': True, 'delta': -3,
                  'requested': 185, 'applied': 183, 'rejected': 2},
    'MSG_NONE': {'cue': 'falsecue', 'message': 5, 'motor': -1,
                 'fi': 1, 'failure': False, 'delta': -2,
                 'requested': 184, 'applied': 184, 'rejected': 0},
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def decode_result(primary):
    value = primary['result']
    if isinstance(value, str):
        value = json.loads(value)
    if 'rows' not in value:
        value = value['result']
    if len(value['rows']) != 1:
        raise ValueError('Exactly one complete diagnostic calibration row required')
    return value['rows'][0]


def request_receipt(request):
    if request is None:
        return None
    if 'receipt' not in request:
        raise ValueError('Direct actual Native receipt missing')
    receipt = request['receipt']
    if request['id'] != receipt['id']:
        raise ValueError('Direct request/receipt identity mismatch')
    return receipt


def observation(record):
    """Frozen uint64 layout; same documentary decoder used in PI06."""
    raw = int(record['raw'])
    if not 0 <= raw < 2**64:
        raise ValueError('Exact uint64 RAW required')
    directions = [(raw >> k) & 15 for k in (48, 52, 56)]
    decoded = {'state': raw & 0xffffffff, 'semantic': raw >> 60,
               's_reg': (raw >> 32) & 65535,
               'direction': [x - 16 if x & 8 else x for x in directions]}
    if any(record[k] != value for k, value in decoded.items()):
        raise ValueError('Reported observation differs from its literal RAW')
    return decoded


def early_choice(record):
    obj = observation(record)
    x, y, z = obj['direction']
    return x if (obj['state'] > 0 and obj['semantic'] == 1
                 and x in (-1, 0, 1) and y == 1 and z in (0, -1)) else None


def late_choice(reader):
    expected = {(15 + 2*x, 17, 15 + 2*z): (x, 1, z)
                for x in (-1, 0, 1) for z in (0, -1)}
    records = reader['observations']
    if len(records) != 6 or {tuple(o['site']) for o in records} != set(expected):
        raise ValueError('All six frozen late FI sites are required')
    found = []
    for record in records:
        obj = observation(record)
        direction = expected[tuple(record['site'])]
        if obj['state'] > 0 and obj['semantic'] == 1 and obj['direction'] == list(direction):
            found.append(direction[0])
    return found[0] if len(found) == 1 else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raiz', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    root = args.raiz.resolve(strict=True)
    if args.salida.exists():
        raise FileExistsError(args.salida)
    results = []
    checks = []
    calendars = []
    for name, expected in CASES.items():
        summary_path = root / 'control' / ('PI07_VIAB_' + name + '_R01.json')
        summary = read(summary_path)
        if not (summary['closed'] and summary['status'] == 'CLOSED'
                and summary['full_plan_completed'] and summary['error'] is None):
            raise ValueError('A complete closed Root case is required: ' + name)
        if len(summary['outcomes']) != 1:
            raise ValueError('One forced operation only: ' + name)
        outcome = summary['outcomes'][0]
        # Resolve the documented primary by its name inside this campaign;
        # never open its recorded absolute source path.
        primary_path = root / 'ensayos' / Path(outcome['primary']).name
        if sha(primary_path) != outcome['primary_sha256']:
            raise ValueError('Primary SHA differs: ' + name)
        primary = read(primary_path)
        row = decode_result(primary)
        receipts = {}
        aliases = 0
        for request in row['requests']:
            receipt = request_receipt(request)
            rid = receipt['id']
            if rid in receipts:
                if receipts[rid] != receipt:
                    raise ValueError('Conflicting alias for an actual Native receipt')
                aliases += 1
            receipts[rid] = receipt
        counts = {}
        for receipt in receipts.values():
            status = receipt['status']
            counts[status] = counts.get(status, 0) + 1
        rejected = sum(n for status, n in counts.items() if status.startswith('rejected'))
        before = row['reference_before']
        after = row['return_frames'][-1]
        before_delta = int(before[0]['s_reg']) - int(before[1]['s_reg'])
        after_delta = int(after['A']['s_reg']) - int(after['B']['s_reg'])
        pulse = request_receipt(row['actuator_request'])
        message = row['message']
        own_message = request_receipt(message['request'])
        fi = row['FI']
        fi_direct = {}
        for request in fi['requests']:
            receipt = request_receipt(request)
            if receipt['id'] in fi_direct and fi_direct[receipt['id']] != receipt:
                raise ValueError('FI receipt aliases disagree')
            fi_direct[receipt['id']] = receipt
        actual_early = early_choice(fi['legacy_result']['early_observation'])
        actual_late = late_choice(fi['legacy_result']['original_result']['native_trial']['reader'])
        actual_selector = early_choice(row['reader']['observation'])
        sensor_raw = observation(row['sensor']['observation'])
        for record in before:
            observation(record)
        for frame in row['return_frames']:
            for key in ('A', 'B', 'hub'):
                observation(frame[key])
        cal = row['calendar']
        calendars.append(cal)
        local = {
            'prepared_case': row['environment_spec']['cue'] == expected['cue']
                and row['environment_spec']['message_payload'] == expected['message'],
            'forced_action_declared': row['actual_motor'] == expected['motor']
                and row['operator_forced_action'] == ('pulso' if expected['motor'] == 1 else 'nada'),
            'same_actual_information_state1': int(row['sensor']['observation']['state']) == 1
                and row['sensor']['identity_state_datum'] == sensor_raw['state'] == 1,
            'fixed_physical_FI': fi['early_physical_choice'] == expected['fi']
                and fi['old_q6_choice'] == expected['fi'],
            'FI_choices_redecoded_from_RAW': actual_early == fi['early_physical_choice']
                and actual_late == fi['old_q6_choice'],
            'Native_selector_redecoded_from_RAW': actual_selector == row['reader']['choice'],
            'all_176_direct_FI_inputs_admitted': len(fi_direct) == 176
                and all(receipt['status'] == 'applied' for receipt in fi_direct.values())
                and fi['Native_inputs']['unique_requested'] == fi['Native_inputs']['applied'] == 176,
            'actual_generic_failure': row['actual_failed'] is expected['failure']
                and row['returned_failed'] is expected['failure'],
            'reference_polarity': before_delta == -2 and after_delta == expected['delta'],
            'direct_input_counts': len(receipts) == expected['requested']
                and counts.get('applied', 0) == expected['applied']
                and rejected == expected['rejected']
                and sum(counts.values()) == expected['requested'],
            'no_unknown_receipts': all(status == 'applied' or status.startswith('rejected') for status in counts),
            'summary_matches_directs': row['Native_inputs']['unique_requested'] == len(receipts)
                and row['Native_inputs']['applied'] == counts.get('applied', 0)
                and row['Native_inputs']['rejected'] == rejected,
            'fixed_489_ticks': row['after_tick'] - row['before_tick'] == 489
                and summary['new_ticks'] == 489,
            'return_boundary': cal['seed_tick'] == cal['query_tick'] + 7
                and cal['outcome_injection_tick'] == cal['query_tick'] + 408
                and cal['collision_tick'] == cal['query_tick'] + 409
                and cal['contact_tick'] == cal['query_tick'] + 410
                and row['after_tick'] == cal['query_tick'] + 412,
            'same_declared_FI_phase': fi['calendar']['query_tick'] == cal['query_tick'] + 192,
            'protected_main_unchanged': summary['protected_main_unchanged'] is True,
        }
        if name == 'MSG_PULSE':
            local['material_cost_not_host_label'] = (
                pulse is not None and pulse['status'] == 'rejected_conflict'
                and own_message is not None and own_message['status'] == 'rejected_conflict'
                and message['delivered_exact'] is False
                and row['pulse_scheduled'] is True and row['pulse_applied'] is False)
        elif name == 'MSG_NONE':
            local['material_delivery_without_pulse'] = (
                pulse is None and own_message is not None and own_message['status'] == 'applied'
                and message['delivered_exact'] is True
                and message['actual_payload'] == 5 and message['artifact']['bytes'] == 64)
        elif name == 'THREAT_PULSE':
            local['selected_tool_admitted'] = pulse is not None and pulse['status'] == 'applied'
        else:
            local['no_unreported_actuator'] = pulse is None
        for key, value in local.items():
            checks.append({'case': name, 'check': key, 'passed': bool(value)})
        results.append({
            'case': name, 'source_summary': summary_path.name,
            'summary_sha256': sha(summary_path), 'primary': primary_path.name,
            'primary_sha256': sha(primary_path), 'before_tick': row['before_tick'],
            'after_tick': row['after_tick'], 'query_tick': cal['query_tick'],
            'FI_query_tick': fi['calendar']['query_tick'],
            'native_unforced_motor': row['native_motor'], 'forced_motor': row['actual_motor'],
            'FI_q4': fi['early_physical_choice'], 'FI_q6': fi['old_q6_choice'],
            'actual_failed': row['actual_failed'], 'returned_failed': row['returned_failed'],
            'reference_delta_before': before_delta, 'reference_delta_after': after_delta,
            'unique_requested': len(receipts), 'status_counts': counts,
            'duplicate_aliases_not_new_events': aliases,
            'pulse_status': None if pulse is None else pulse['status'],
            'message_status': None if own_message is None else own_message['status'],
            'message_delivered': message['delivered_exact'],
        })
    checks.append({'case': 'PAIRED', 'check': 'same_full_calendar',
                   'passed': all(c == calendars[0] for c in calendars)})
    passed = all(item['passed'] for item in checks)
    result = {
        'schema': 'DEE.PI07.four_forced_calibrations.passive_recalculation.v1',
        'status': 'CALIBRATION_CONTRACT_MATCHED' if passed else 'CALIBRATION_MISMATCH_PRESERVED',
        'all_checks_passed': passed, 'new_Native_ticks': 0,
        'reported_original_Native_ticks': sum(c['after_tick'] - c['before_tick'] for c in results),
        'cases': results, 'checks': checks,
        'scope': 'Four forced paired technical controls, not acquired selection, independent organisms, new Native reproduction, or operational promotion.',
    }
    with args.salida.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'passed': passed,
                      'checks': len(checks), 'output': str(args.salida),
                      'sha256': sha(args.salida)}, ensure_ascii=False))
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
