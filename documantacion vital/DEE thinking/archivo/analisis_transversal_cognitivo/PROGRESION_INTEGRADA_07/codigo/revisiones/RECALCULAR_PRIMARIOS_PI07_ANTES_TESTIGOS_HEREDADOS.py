"""Standalone documentary PI07 primary verifier, stdlib only.

No DEE import, Native execution, recorded source-path access or experimental
reproduction. All opens resolve within the supplied extraction. The new output
may be outside it. Numerical expectations are auditor checks, never actor data.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import hashlib
import json


INDEX = '04_EVIDENCIAS/PRIMARIOS/INDICE_PRIMARIOS_PI07.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def local(root, relative):
    relative = Path(relative)
    if relative.is_absolute() or '..' in relative.parts:
        raise ValueError('Only extraction-relative evidence paths are allowed')
    path = (root / relative).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError('Evidence path escaped the extraction')
    for node in (path, *path.parents):
        if node == root.parent:
            break
        if node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0) & 1024:
            raise ValueError('Linked evidence is not allowed')
    return path


def checked(root, entry):
    path = local(root, entry['file'])
    data = path.read_bytes()
    if len(data) != entry['bytes'] or digest(data) != entry['sha256']:
        raise ValueError('Evidence bytes/SHA mismatch: ' + entry['file'])
    return path, data


def read_bytes(data):
    return json.loads(data.decode('utf-8-sig'))


def observation(record):
    raw = int(record['raw'])
    if not 0 <= raw < 2**64:
        raise ValueError('Exact uint64 RAW required')
    ds = [(raw >> shift) & 15 for shift in (48, 52, 56)]
    decoded = {'state': raw & 0xffffffff, 'semantic': raw >> 60,
               's_reg': (raw >> 32) & 65535,
               'direction': [v - 16 if v & 8 else v for v in ds]}
    if any(record.get(key) != value for key, value in decoded.items()):
        raise ValueError('Recorded observation fields differ from literal RAW')
    return decoded


def early_choice(record):
    obj = observation(record)
    x, y, z = obj['direction']
    return x if (obj['state'] > 0 and obj['semantic'] == 1
                 and x in (-1, 0, 1) and y == 1 and z in (0, -1)) else None


def late_FI_choice(reader):
    expected = {(15 + 2*x, 17, 15 + 2*z): (x, 1, z)
                for x in (-1, 0, 1) for z in (0, -1)}
    records = reader['observations']
    if len(records) != 6 or {tuple(o['site']) for o in records} != set(expected):
        raise ValueError('All six frozen FI late sites must be supplied')
    found = []
    for record in records:
        obj = observation(record)
        if (obj['state'] > 0 and obj['semantic'] == 1
                and obj['direction'] == list(expected[tuple(record['site'])])):
            found.append(obj['direction'][0])
    return found[0] if len(found) == 1 else None


def receipts(requests):
    unique = {}
    aliases = 0
    for request in requests:
        rid = request['id']
        receipt = request['receipt']
        if type(rid) is not int or rid != receipt['id']:
            raise ValueError('Actual request and receipt identities disagree')
        if rid in unique:
            if unique[rid] != receipt:
                raise ValueError('Receipt aliases disagree')
            aliases += 1
        unique[rid] = receipt
    return unique, aliases


def request_status(request):
    if request is None:
        return None
    unique, _ = receipts([request])
    return next(iter(unique.values()))['status']


def decoded_result(primary):
    value = primary.get('result')
    if value is None:
        return None, []
    if isinstance(value, str):
        value = json.loads(value)
    envelope = value
    if isinstance(value, dict) and 'rows' not in value and isinstance(value.get('result'), dict):
        value = value['result']
    return envelope, value.get('rows', []) if isinstance(value, dict) else []


def embedded_plans(value):
    """Parse JSON only. Recorded strings are never paths or executable code."""
    if isinstance(value, str):
        if len(value.encode('utf-8')) <= 1048576 and value[:1] in ('{', '['):
            try:
                yield from embedded_plans(json.loads(value))
            except json.JSONDecodeError:
                pass
    elif isinstance(value, list):
        for item in value:
            yield from embedded_plans(item)
    elif isinstance(value, dict):
        if value.get('schema') == 'DEE.PI07.yoked_return.roll5.v1':
            yield value
        else:
            for item in value.values():
                yield from embedded_plans(item)


def stage_counts(rows):
    out = {}
    for stage in sorted({r['stage'] for r in rows}):
        selected = [r for r in rows if r['stage'] == stage]
        out[stage] = {
            'opportunities': len(selected),
            'FI_correct': sum(r['FI_correct'] for r in selected),
            'legitimate_packets_scheduled': sum(r['message_required'] for r in selected),
            'legitimate_packets_delivered': sum(r['message_delivered'] for r in selected if r['message_required']),
            'complete_opportunities': sum(r['complete_opportunity'] for r in selected),
            'valid_Native_selections': sum(r['selection'] is not None for r in selected),
            'zero_Native_choices_not_NULL': sum(r['selection'] == 0 for r in selected),
            'NULL_Native_choices': sum(r['selection'] is None for r in selected),
            'pulse_requests_scheduled': sum(r['pulse_scheduled'] for r in selected),
            'pulse_requests_applied': sum(r['pulse_applied'] for r in selected),
            'actual_function_failures': sum(r['actual_failed'] for r in selected),
            'returned_failures': sum(r['returned_failed'] for r in selected),
        }
    return out


def inspect_episode(row, source, products_by_hash, checks):
    all_direct, aliases = receipts(row['requests'])
    counts = Counter(r['status'] for r in all_direct.values())
    summary = row['Native_inputs']
    rejected = sum(n for key, n in counts.items() if key.startswith('rejected'))
    if (summary['unique_requested'] != len(all_direct)
            or summary['applied'] != counts['applied']
            or summary['rejected'] != rejected
            or summary['pending_or_other'] != sum(n for key, n in counts.items()
                                                  if key != 'applied' and not key.startswith('rejected'))):
        raise ValueError('Actual episode direct receipts disagree with its summary')
    cal = row['calendar']
    q = cal['query_tick']
    perpendicular = row.get('version') == 'DEE.PI07.acquired_regulation.perpendicular_environment.R03'
    actuator_site = [53, 48, 56] if perpendicular else [52, 48, 51]
    actuator_direction = [-1, 0, 0] if perpendicular else [0, 0, -1]
    message_reader = [54, 48, 56] if perpendicular else [53, 48, 51]
    if row['sensor']['site'] != [52, 48, 47] or row['reader']['site'] != [8, 40, 50]:
        raise ValueError('Fixed sensor or Native selector location changed')
    if row['message']['site'] != message_reader:
        raise ValueError('Fixed versioned physical message reader changed')
    for request, site, direction, payload in (
            (row['actuator_request'], actuator_site, actuator_direction, 0),
            (row['message']['request'], actuator_site, [1, 0, 0], row['environment_spec']['message_payload'])):
        if request is not None and (request['site'] != site or request['direction'] != direction
                                    or request['payload'] != payload or request['requested_tick'] != q+7):
            raise ValueError('Versioned generic actuator or packet mapping changed')
    selector = early_choice(row['reader']['observation'])
    sensor = observation(row['sensor']['observation'])
    actual_state = row['sensor'].get('actual_state_datum', row['sensor'].get('identity_state_datum'))
    sent = row['sensor'].get('submitted_state_datum', actual_state)
    if actual_state != sensor['state'] or sent != (0 if row.get('sensor_ablation') else actual_state):
        raise ValueError('Identity sensor codec or declared material ablation changed')
    if selector != row['reader']['choice']:
        raise ValueError('Native selector choice differs from its fixed RAW signature')
    fi = row['FI']
    early = early_choice(fi['legacy_result']['early_observation'])
    old = late_FI_choice(fi['legacy_result']['original_result']['native_trial']['reader'])
    if early != fi['early_physical_choice'] or old != fi['old_q6_choice']:
        raise ValueError('FI q+4/q+6 decoded value mismatch')
    fi_direct, fi_aliases = receipts(fi['requests'])
    if len(fi_direct) != 176:
        raise ValueError('The historical FI contract must request exactly176 direct inputs')
    fi_applied = sum(r['status'] == 'applied' for r in fi_direct.values())
    if fi['Native_inputs']['unique_requested'] != 176 or fi['Native_inputs']['applied'] != fi_applied:
        raise ValueError('FI current direct receipt count mismatch')
    msg = row['message']
    physical_msg = observation(msg['observation'])
    message_valid = (physical_msg['state'] > 0 and physical_msg['semantic'] == 1
                     and physical_msg['direction'] == [1, 0, 0])
    actual_payload = physical_msg['s_reg'] if message_valid else None
    msg_status = request_status(msg['request'])
    required = row['environment_spec']['message_payload']
    delivered = (required is not None and msg_status == 'applied'
                 and message_valid and actual_payload == required)
    if msg['actual_payload'] != actual_payload or msg['delivered_exact'] is not delivered:
        raise ValueError('Message delivery was not its actual Native receipt/value')
    if delivered:
        artifact = msg['artifact']
        if artifact is None or artifact['bytes'] != 64:
            raise ValueError('Delivered message lacks its real64-byte artifact')
        if artifact['sha256'] not in products_by_hash:
            raise ValueError('Delivered message artifact must travel in the portable index')
        content = products_by_hash[artifact['sha256']]
        if content != actual_payload.to_bytes(8, 'little') * 8:
            raise ValueError('Message bytes do not encode the actual Native payload')
    pulse_status = request_status(row['actuator_request'])
    pulse_scheduled = row['actuator_request'] is not None
    pulse_applied = pulse_status == 'applied'
    if (row.get('pulse_scheduled', pulse_scheduled) is not pulse_scheduled
            or row.get('pulse_applied', pulse_applied) is not pulse_applied):
        raise ValueError('Pulse scheduling and actual admission were conflated')
    failed = old != 1 or (required is not None and not delivered)
    if row['actual_failed'] is not failed:
        raise ValueError('Actual failure predicate differs from the registered physical outcomes')
    before = row['reference_before']
    for record in before:
        observation(record)
    for frame in row['return_frames']:
        for key in ('A', 'B', 'hub'):
            observation(frame[key])
    delta_before = int(before[0]['s_reg']) - int(before[1]['s_reg'])
    final = row['return_frames'][-1]
    delta_after = int(final['A']['s_reg']) - int(final['B']['s_reg'])
    motor = row['actual_motor']
    predicted_credit = None if motor is None else (0 if not row['returned_failed'] else (1 if motor == -1 else -1))
    checks.append({'source': source, 'check': 'fixed_six_lap_calendar',
                   'passed': cal['seed_tick'] == q+7 and cal['outcome_injection_tick'] == q+408
                   and cal['collision_tick'] == q+409 and cal['contact_tick'] == q+410
                   and row['after_tick'] == q+412})
    checks.append({'source': source, 'check': 'reader_and_message_fixed_ticks',
                   'passed': row['reader']['tick'] == q+4 and row['sensor']['tick'] == q-1
                   and msg['read_tick'] == q+8 and fi['calendar']['query_tick'] == q+192})
    if row.get('feedback_arm') == 'real':
        checks.append({'source': source, 'check': 'real_return_equals_actual_outcome',
                       'passed': row['returned_failed'] is row['actual_failed']})
    elif row.get('feedback_arm') == 'none':
        checks.append({'source': source, 'check': 'constant_nonfailure_is_not_omitted_return',
                       'passed': row['returned_failed'] is False})
    return {
        'source': source, 'life_id': row.get('life_id', 'forced_R01:' + source),
        'version': row['version'], 'ordinal': row['ordinal'],
        'stage': row['environment_spec']['stage'], 'cue_fixture_not_actor_input': row['environment_spec']['cue'],
        'sensor_actual_state': actual_state, 'sensor_submitted_state': sent,
        'before_tick': row['before_tick'], 'after_tick': row['after_tick'], 'query_tick': q,
        'FI_query_tick': fi['calendar']['query_tick'], 'calendar': cal,
        'FI_calendar': fi['calendar'], 'selection': selector,
        'actual_motor': motor, 'forced_operator_action': row['operator_forced_action'],
        'sensor_ablation': row.get('sensor_ablation', False),
        'actuator_ablation': row.get('actuator_ablation', False),
        'pulse_scheduled': pulse_scheduled, 'pulse_applied': pulse_applied,
        'pulse_status': pulse_status, 'FI_q4': early, 'FI_q6': old, 'FI_correct': old == 1,
        'FI_inputs_unique_requested': len(fi_direct), 'FI_inputs_applied': fi_applied,
        'FI_inputs_rejected_or_other': len(fi_direct)-fi_applied,
        'message_required': required is not None, 'message_required_payload': required,
        'message_actual_payload': actual_payload, 'message_status': msg_status,
        'message_delivered': delivered, 'complete_opportunity': not failed,
        'actual_failed': failed, 'returned_failed': row['returned_failed'],
        'feedback_arm': row.get('feedback_arm'),
        'reference_delta_before': delta_before, 'reference_delta_after': delta_after,
        'observed_credit_increment': delta_after-delta_before,
        'expected_credit_increment_conditional_on_valid_motor': predicted_credit,
        'credit_increment_contract_matched': predicted_credit is not None and delta_after-delta_before == predicted_credit,
        'unique_current_requests': len(all_direct), 'status_counts': dict(counts),
        'aliases_not_new_events': aliases, 'FI_aliases_not_new_events': fi_aliases,
    }


def inspect_regulated_access(row, source, checks):
    """New access contract; no cue/message or R03 offer is invented."""
    direct, aliases = receipts(row['requests'])
    statuses = Counter(r['status'] for r in direct.values())
    dose = row['Native_inputs']
    rejected = sum(n for status, n in statuses.items() if status.startswith('rejected'))
    if dose['unique_requested'] != len(direct) or dose['applied'] != statuses['applied'] or dose['rejected'] != rejected:
        raise ValueError('Access wrapper direct dose mismatch')
    fi = row['FI']
    early = early_choice(fi['legacy_result']['early_observation'])
    late = late_FI_choice(fi['legacy_result']['original_result']['native_trial']['reader'])
    if early != row['early_physical_choice'] or early != fi['early_physical_choice'] or late != row['old_q6_choice']:
        raise ValueError('Regulated FI access did not return its actual fixed Native reader')
    operands = row['public_operands']
    left, right = operands['left'], operands['right']
    if type(left) is not int or type(right) is not int or not (0 <= left <= 20 and 0 <= right <= 20):
        raise ValueError('Public FI operand domain changed')
    reference = (left > right) - (left < right)  # auditor only, after actual RAW
    failed = early != reference
    if row['evaluator_after_function_expected_direction'] != reference or row['generic_return_failed'] is not failed:
        raise ValueError('Post-function evaluator differs from the registered general sign reference')
    sensor = observation(row['sensor']['observation'])
    if sensor['state'] != row['sensor']['actual_state_datum']:
        raise ValueError('Access sensor did not carry actual physical identity')
    expected_datum = 0 if row.get('sensor_ablation') else sensor['state']
    if row['sensor']['submitted_state_datum'] != expected_datum:
        raise ValueError('Unregistered sensor advice or material ablation')
    choice = early_choice(row['reader']['observation'])
    if choice != row['reader']['choice']:
        raise ValueError('Access selector RAW decoder mismatch')
    cal = row['calendar']; q = cal['query_tick']
    pulse = row['actuator_request']; pulse_status = request_status(pulse)
    if pulse is not None and (pulse['site'] != [53,48,56] or pulse['direction'] != [-1,0,0]
                              or pulse['payload'] != 0 or pulse['requested_tick'] != q+7):
        raise ValueError('General FI access changed the fixed actuator')
    if row['pulse_applied'] is not (pulse_status == 'applied'):
        raise ValueError('Access pulse request was confused with its physical admission')
    for frame in row['return_frames']:
        for key in ('A','B'):
            observation(frame[key])
    first, last = row['return_frames'][0], row['return_frames'][-1]
    db = first['A']['s_reg']-first['B']['s_reg']; da = last['A']['s_reg']-last['B']['s_reg']
    motor = row['native_motor']
    predicted = None if motor is None else (0 if not failed else 1 if motor == -1 else -1)
    checks.append({'source':source,'check':'general_access_fixed_calendar',
                   'passed':cal['seed_tick']==q+7 and cal['outcome_injection_tick']==q+408
                   and row['after_tick']==q+412 and fi['calendar']['query_tick']==q+192})
    checks.append({'source':source,'check':'general_access_preserves_zero_NULL_and_postfunction_reference',
                   'passed':row['NULL_is_not_zero'] is True and row['generic_return_failed'] is failed})
    return {'source':source,'life_id':row['life_id'],'version':row['version'],'ordinal':row['ordinal'],
            'stage':'regulated_FI_access','cue_fixture_not_actor_input':None,
            'sensor_actual_state':sensor['state'],'sensor_submitted_state':expected_datum,
            'before_tick':row['before_tick'],'after_tick':row['after_tick'],'query_tick':q,
            'FI_query_tick':fi['calendar']['query_tick'],'calendar':cal,'FI_calendar':fi['calendar'],
            'selection':choice,'actual_motor':motor,'forced_operator_action':None,
            'sensor_ablation':row.get('sensor_ablation',False),'actuator_ablation':row.get('actuator_ablation',False),
            'pulse_scheduled':pulse is not None,'pulse_applied':row['pulse_applied'],'pulse_status':pulse_status,
            'FI_q4':early,'FI_q6':late,'FI_correct':not failed,'public_operands':operands,
            'expected_afterwards_evaluator_only':reference,
            'message_required':False,'message_required_payload':None,'message_actual_payload':None,
            'message_status':None,'message_delivered':False,'complete_opportunity':not failed,
            'actual_failed':failed,'returned_failed':failed,'feedback_arm':'real',
            'reference_delta_before_return':db,'reference_delta_after':da,
            'observed_credit_increment':da-db,'expected_credit_increment_conditional_on_valid_motor':predicted,
            'credit_increment_contract_matched':predicted is not None and da-db==predicted,
            'unique_current_requests':len(direct),'status_counts':dict(statuses),'aliases_not_new_events':aliases,
            'scope':'General access contract, not a consumed R03 environmental offer or an unchanged old198tick/176input API.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raiz', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    root = args.raiz.resolve(strict=True)
    if args.salida.exists():
        raise FileExistsError(args.salida)
    index = read_bytes(local(root, INDEX).read_bytes())
    if index.get('schema') != 'DEE.PI07.portable_primary_index.v1':
        raise ValueError('Exact portable primary index required')
    products = {}
    for entry in index.get('products', []):
        _, data = checked(root, entry)
        products[digest(data)] = data
    episodes = []
    omitted_rows = []
    technical_failures = []
    documentary_wrappers = []
    checks = []
    yoke_plans = {}
    seen_files = set()
    for entry in index['primaries']:
        if entry['file'] in seen_files:
            raise ValueError('Duplicate indexed primary')
        seen_files.add(entry['file'])
        _, data = checked(root, entry)
        primary = read_bytes(data)
        for plan in embedded_plans(primary):
            values, source = plan['values'], plan['source_failed']
            if (len(values) != 12 or len(source) != 12
                    or any(type(v) is not bool for v in values+source)
                    or plan['roll'] != 5 or plan['roll_direction'] != 'source_plus_5'
                    or values != [source[(i+5) % 12] for i in range(12)]
                    or Counter(values) != Counter(source)):
                raise ValueError('Yoked plan changed its pre-fixed derangement/dose')
            yoke_plans[digest(json.dumps(plan, sort_keys=True, separators=(',', ':')).encode())] = plan
        envelope, rows = decoded_result(primary)
        if not rows:
            technical_failures.append({'source': entry['file'], 'status': primary.get('status'),
                                       'error': primary.get('error'),
                                       'scope': 'No complete material row available; no missing observations or success invented.'})
        for i, row in enumerate(rows):
            source_name = entry['file'] + '#row' + str(i)
            inner = row.get('original_result')
            if isinstance(inner, dict) and all(k in inner for k in ('FI', 'sensor', 'message', 'requests')):
                documentary_wrappers.append({'source': source_name,
                                              'outer_keys': sorted(row),
                                              'scope': 'Recalculate the original Native row once; the outer external-observation wrapper is not another opportunity or material dose.'})
                row = inner
                source_name += '/original_result'
            if ('reference_before' in row and 'return_frames' in row
                    and 'FI' in row and 'sensor' in row and 'message' in row):
                episodes.append(inspect_episode(row, source_name, products, checks))
            elif ('FI' in row and 'public_operands' in row and 'generic_return_failed' in row
                  and 'sensor' in row and 'return_frames' in row):
                episodes.append(inspect_regulated_access(row, source_name, checks))
            else:
                omitted_rows.append({'source': source_name, 'version': row.get('version'),
                                     'scope': row.get('scope'),
                                     'reason': 'Outside this fixed selector/FI/message recalculation; bytes/SHA verified only. No full scientific recalculation claimed.'})
    groups = defaultdict(list)
    for row in episodes:
        # R03 continues the same actual life and preserves all28 R02 events.
        # Its separately versioned environment has its own local ordinal;
        # local0 is not a reset or a duplicate of historical R02 ordinal0.
        groups[(row['life_id'], row['version'])].append(row)
    grouped = {}
    for (life, version), rows in groups.items():
        rows.sort(key=lambda row: row['ordinal'])
        if len({row['ordinal'] for row in rows}) != len(rows):
            raise ValueError('Same-life opportunity primary is duplicated')
        grouped[life+'|'+version] = {'life_id': life, 'version': version,
                         'actual_executed_opportunities_included': len(rows),
                         'stages': stage_counts(rows),
                         'Native_ticks_included': sum(r['after_tick']-r['before_tick'] for r in rows),
                         'credit_contract_matches': sum(r['credit_increment_contract_matched'] for r in rows),
                         'credit_contract_evaluable_valid_motors': sum(r['actual_motor'] is not None for r in rows),
                         'scope': 'Paired descendants may share a prefix; these are not independent individuals or concept counts.'}
    passed = all(check['passed'] for check in checks)
    result = {
        'schema': 'DEE.PI07.portable_primary_recalculation.v1',
        'status': 'DOCUMENTARY_CHECKS_MATCHED' if passed else 'DOCUMENTARY_MISMATCH_PRESERVED',
        'all_checks_passed': passed, 'new_Native_ticks': 0, 'DEE_imports': 0,
        'index_sha256': digest(local(root, INDEX).read_bytes()),
        'indexed_primaries': len(index['primaries']), 'indexed_product_files': len(index.get('products', [])),
        'episodes_recalculated': len(episodes), 'groups': grouped,
        'episodes': episodes, 'checks': checks, 'yoked_plans': list(yoke_plans.values()),
        'rows_hash_verified_not_recalculated': omitted_rows,
        'no_complete_rows_or_technical_errors': technical_failures,
        'external_observation_wrappers_not_double_counted': documentary_wrappers,
        'scope': 'Frozen-record documentary recalculation. It does not run DEE, re-acquire a skill, validate omitted observations, demonstrate unrestricted observer passivity or promote any life. All source_reference fields were ignored.',
    }
    with args.salida.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'passed': passed,
                      'episodes': len(episodes), 'checks': len(checks),
                      'output_sha256': digest(args.salida.read_bytes())}, ensure_ascii=False))
    return 0 if passed else 2


if __name__ == '__main__':
    raise SystemExit(main())
