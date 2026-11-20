"""Root-only bounded A2 continuation through the existing Cognitive owner.

No Native operation on import or --dry-run. Numeric errors remain results;
write uncertainty, an unknown receipt or a finite-bound failure preserves and
stops the affected future. No automatic resend, teaching, selection or reset.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, hashlib, importlib.util, json, os, re, sys

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
RP = C / 'reproducibilidad'
S = P / 'estados/RP_A01/sistema'
PY = C / 'motor/python313/python.exe'
PLAN = P / 'control/PROTOCOLO_CONSOLIDACION_A2_PI08_R01.json'
MAIN = 'ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
MAIN_SHA = 'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
R3STATE = {'modo': 'eci01-pi07-r03-estado'}
C2STATE = {'modo': 'eci01-pi04-c2c-estado'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def regular(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        if item.exists() and (item.is_symlink() or getattr(item.lstat(), 'st_file_attributes', 0) & 1024):
            raise ValueError('No linked experiment path: ' + str(path))
    return path


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def ledger():
    records = []
    seen = set()
    for path in sorted((P / 'estados').glob('*/sistema/estado/vidas/*/VIDA.json')):
        regular(path)
        card = read(path)
        life = card['life_id']
        require(life not in seen, 'Duplicate diagnostic identity in declared PI08 stores')
        seen.add(life)
        initial = card.get('parent', {}).get('source_tick')
        current = card['physical']['tick']
        require(type(initial) is int and current >= initial, 'A complete imported prefix is required')
        records.append({'life_id': life, 'card': str(path), 'initial_tick': initial,
                        'saved_tick': current, 'new_Native_ticks': current - initial})
    return sum(r['new_Native_ticks'] for r in records), records


def receipt_group(items):
    unique = {}
    aliases = 0
    for item in items:
        identity = item['id']
        receipt = item['receipt']
        require(type(identity) is int and receipt['id'] == identity, 'Direct receipt identity mismatch')
        if identity in unique:
            require(unique[identity] == receipt, 'Conflicting receipt alias')
            aliases += 1
        unique[identity] = receipt
    return unique, aliases


def c2c_inputs(row):
    groups = {'outer': row['requests']}
    arithmetic = row.get('native_arithmetic')
    second = row.get('second_native_use')
    if arithmetic is not None:
        groups['FI'] = arithmetic['native_operation']['native_trial']['requests']
    if second is not None and isinstance(second.get('requests'), list):
        groups['MU'] = second['requests']
    direct, aliases = receipt_group([item for group in groups.values() for item in group])
    quality = row['native_input_summary']
    counts = Counter(r['status'] for r in direct.values())
    require(quality['unique_requested'] == len(direct) and quality['applied'] == counts['applied'],
            'C2C outer/FI/MU collector differs from the unchanged scientific collector')
    if arithmetic is not None and second is not None and second.get('reader') is not None:
        require({key: len(value) for key, value in groups.items()} == {'outer': 6, 'FI': 176, 'MU': 4}
                and len(direct) == 186, 'Complete C2C must include6+176+4 current inputs')
    return direct, aliases, {key: len(value) for key, value in groups.items()}


def first_row(value):
    return value['result']['rows'][0]


def main(args):
    plan_bytes = PLAN.read_bytes()
    plan = json.loads(plan_bytes)
    require(plan['schema'] == 'DEE.PI08.A2.fixed_consolidation.protocol.R01'
            and plan['status'] == 'SEALED_BEFORE_A2_EVALUATION', 'Exact pre-evaluation plan required')
    require(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_[A-Za-z0-9_]{1,40}', args.vida),
            'One explicit imported PI08 diagnostic successor required')
    require(re.fullmatch(r'PI08_[A-Za-z0-9_]{1,45}', args.tag), 'Fresh bounded request tag required')
    phase = plan['phases'][args.fase]
    maximum = sum(step['max_Native_ticks'] for step in phase['steps'])
    if args.dry_run:
        print(json.dumps({'Native_executed': False, 'new_ticks': 0, 'phase': args.fase,
                          'plan_sha256': sha(PLAN), 'steps': len(phase['steps']),
                          'finite_Native_bound': maximum, 'system': str(S)}, ensure_ascii=False))
        return 0
    campaign = read(P / 'REGISTRO_CAMPANA.json')
    tick_total, lives = ledger()
    require(tick_total + maximum <= campaign['budget']['Native_ticks_all_branches'], 'PI08 Native budget insufficient')
    require(len(lives) <= campaign['budget']['diagnostic_worlds_all_new'], 'PI08 new-world limit exceeded')
    cutoff = datetime.fromisoformat(campaign['budget']['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
    require(datetime.now(timezone.utc) < cutoff, 'Scientific deadline reached')
    card_path = regular(S / 'estado/vidas' / args.vida / 'VIDA.json')
    card = read(card_path)
    require(card['physical']['N'] == 67 and card['physical']['tick'] == args.tick_inicial,
            'Exact current cut required; do not restore a stale future')
    require(not (S / 'estado/ACTIVO.json').exists(), 'A2 uses an unselected diagnostic successor')
    locks = S / 'estado/locks'
    require(not locks.exists() or not any(locks.iterdir()), 'Scoped owner/lock remains; inspect instead of replacing it')
    require(not (RP / 'EJECUCION_MATERIAL.lock').exists(), 'Material RP writer remains')
    require(not (card_path.parent / 'FUTURO_INTERRUMPIDO.json').exists(), 'An interrupted future cannot be retried')
    protected_paths = [C / 'sistema/estado/ACTIVO.json', C / 'sistema/estado/vidas' / MAIN / 'VIDA.json']
    source_card = read(protected_paths[1])
    require(read(protected_paths[0])['life_id'] == MAIN and source_card['physical']['tick'] == 824911
            and source_card['snapshot_sha256'] == MAIN_SHA, 'Original principal advanced; never overwrite it')
    protected_paths.append(C / 'sistema' / source_card['snapshot'])
    protected = {str(path): sha(path) for path in protected_paths}
    proof_path = P / 'control' / (args.tag + '.json')
    marker = P / 'PI08_ROOT_NATIVE_WRITER.lock'
    require(not proof_path.exists() and not marker.exists(), 'No reused proof/tag or second writer')
    with marker.open('x', encoding='utf-8') as stream:
        json.dump({'pid': os.getpid(), 'life_id': args.vida, 'phase': args.fase,
                   'plan_sha256': sha(PLAN)}, stream)
    # Configuration imports only QueueDB/process control. The managed process
    # created below is the sole Native writer; this supervisor imports no DEE.
    supervisor = load('PI08_scoped_owner', RP / 'propietario_diagnostico.py')
    supervisor.configure(P, S, PY)
    owner = None
    error = None
    notes = []
    rows = []
    intents = []
    current_ids = set()
    totals = Counter()
    token = None
    states = {}

    def material(label, literal, limit=0):
        require(datetime.now(timezone.utc) < cutoff, 'Deadline between material operations')
        identifier = args.tag + '_' + label
        intents.append({'id': identifier, 'literal': literal, 'finite_bound': limit})
        value = owner.material(identifier, literal, feedback='real', actuator='closed', allow_failure=True)
        path = P / 'ensayos' / (identifier + '.json')
        require('before_tick' in value and 'after_tick' in value, 'Incomplete transport result: preserve SAME id without resend')
        require(0 <= value['after_tick'] - value['before_tick'] <= limit, 'Actual use exceeded its prospective bound')
        rows.append({'label': label, 'literal': literal, 'primary': str(path), 'primary_sha256': sha(path),
                     'before_tick': value['before_tick'], 'after_tick': value['after_tick']})
        require(PLAN.read_bytes() == plan_bytes, 'Sealed evaluation plan changed during execution')
        return value

    def state(label):
        r3 = first_row(material('R03_' + label, R3STATE))
        c2 = first_row(material('C2C_' + label, C2STATE))
        states[label] = {'R03': r3, 'C2C': c2}
        expected = phase['before'] if label == 'pre' else phase['after']
        require(r3['progress']['ordinal'] == expected['R03_ordinal'], 'R03 history/counter differs from the fixed continuation')
        require(c2['progress']['ordinal'] == c2['device']['ordinal'] == expected['C2C_ordinal']
                and len(c2['device']['resources']) == expected['C2C_resources'], 'C2C history/resources differ')
        require(not any(r3['progress'].get(k) for k in ('pending', 'uncertain'))
                and not any(c2['device'].get(k) for k in ('pending', 'feedback_pending', 'uncertain')),
                'Operational future is uncertain; no cleanup or reset')

    try:
        owner = supervisor.Owner(args.vida, args.tag)
        with owner:
            state('pre')
            if args.fase == 'reapertura':
                access = first_row(material('FI_access_state', {'modo': 'eci01-pi07-fi-acceso-estado'}))
                if not access['admitted']:
                    admitted = first_row(material('FI_access_admit', {'modo': 'eci01-pi07-fi-acceso-admitir'}))
                    require(admitted['admitted'] is True, 'Explicit public-access admission did not complete')
            for step in phase['steps']:
                literal = dict(step['literal'])
                if step['kind'] == 'supply_commit':
                    require(token is not None, 'No successful preparation token; never guess one')
                    literal['token'] = token
                value = material(step['label'], literal, step['max_Native_ticks'])
                row = first_row(value)
                record = rows[-1]
                record['kind'] = step['kind']
                direct = {}
                if step['kind'] == 'supply_prepare':
                    token = row['token']
                    require(isinstance(token, str) and re.fullmatch('[0-9a-f]{64}', token), 'Exact preflight token required')
                    record['token'] = token
                elif step['kind'] == 'supply_commit':
                    record['result'] = row
                    # Post-state verifies32resources, ordinal30 and closed
                    # progress; Native delta of this transaction must be0.
                elif step['kind'] == 'R03':
                    require(row['ordinal'] == step['ordinal'], 'Wrong R03 opportunity consumed')
                    direct, aliases = receipt_group(row['requests'])
                    record.update(actual_sensor_state=row['sensor']['actual_state_datum'],
                        Native_choice=row['reader']['choice'], actual_motor=row['actual_motor'],
                        pulse_scheduled=row['pulse_scheduled'], pulse_applied=row['pulse_applied'],
                        FI_q4=row['FI']['early_physical_choice'], FI_q6=row['FI']['old_q6_choice'],
                        message_required=row['message']['required_payload'] is not None,
                        message_delivered=row['message']['delivered_exact'], actual_failed=row['actual_failed'],
                        returned_failed=row['returned_failed'], correct=not row['actual_failed'],
                        Native_aliases_not_new_events=aliases)
                elif step['kind'] == 'C2C':
                    require(row['ordinal'] == step['ordinal'], 'Wrong C2C opportunity consumed')
                    direct, aliases, groups = c2c_inputs(row)
                    record.update(correct=row['useful_product'], actual_numeric_result=row['actual_numeric_result'],
                                  selected_operation=row['selected_operation'], second_motor=row['second_motor'],
                                  actual_group_counts=groups, Native_aliases_not_new_events=aliases)
                    if row['useful_product']:
                        product = row['actual_effect']['product']
                        path = regular(S / 'estado/servicios_locales' / args.vida / 'PI04_C2C_COORDINACION_R01/dispositivo' / product['path'])
                        data = path.read_bytes()
                        require(len(data) == product['bytes'] == 64 and sha(path) == product['sha256']
                                and type(row['actual_numeric_result']) is int
                                and int.from_bytes(data[:2], 'little') == row['actual_numeric_result'],
                                'Real product does not carry the actual Native arithmetic result')
                        record['actual_product'] = {'path': str(path), 'bytes': 64, 'sha256': sha(path)}
                elif step['kind'] == 'public_FI':
                    # This field exists only on the declared regulated route.
                    # If legacy was reached accidentally, preserve that result
                    # and reject the migration claim rather than reinterpret it.
                    observed = row['early_physical_choice']
                    require('public_operands' in row and 'generic_return_failed' in row,
                            'Public outer command did not reach the regulated FI contract')
                    expected = (literal['izquierda'] > literal['derecha']) - (literal['izquierda'] < literal['derecha'])
                    direct, aliases = receipt_group(row['requests'])
                    record.update(observed=observed, expected_evaluator_only=expected,
                        correct=observed == expected, actual_sensor_state=row['sensor']['actual_state_datum'],
                        Native_choice=row['reader']['choice'], pulse_applied=row['pulse_applied'],
                        public_mode=literal['modo'], new_access_not_legacy198_176=True,
                        Native_aliases_not_new_events=aliases)
                else:
                    inner = row if step['kind'] == 'word' else row['result']['rows'][0]
                    observed = inner['reader']['formed_native_command']
                    direct, aliases = receipt_group(inner['requests'])
                    record.update(observed=observed, expected_evaluator_only=step['expected'],
                                  correct=observed == step['expected'], Native_aliases_not_new_events=aliases)
                if direct:
                    require(not current_ids.intersection(direct), 'A prior material receipt was counted as a new event')
                    current_ids.update(direct)
                    counts = Counter(item['status'] for item in direct.values())
                    require(all(key == 'applied' or key.startswith('rejected') for key in counts),
                            'Pending or unknown Native admission requires preservation and stop')
                    totals.update(counts)
                    record['Native_inputs'] = {'unique_requested': len(direct), 'status_counts': dict(counts)}
                    if any(key.startswith('rejected') for key in counts):
                        notes.append({'label': step['label'], 'kind': 'KNOWN_TERMINAL_NATIVE_REJECTION',
                                      'counts': dict(counts), 'not_automatically_a_transport_failure': True})
                if record.get('correct') is False:
                    notes.append({'label': step['label'], 'kind': 'KNOWN_FUNCTIONAL_ERROR_PRESERVED_NO_RETEACHING'})
            state('post')
            owner.control('guardar')
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'automatic_retry': False}
    closed = bool(owner is not None and owner.proc is not None and owner.proc.poll() == 0
                  and not (owner.q.get_meta('owner') or {}).get('running'))
    after = read(card_path)
    protected_after = {str(path): sha(path) for path in protected_paths}
    if protected_after != protected:
        error = {'type': 'PROTECTED_PRINCIPAL_ADVANCED_OR_CHANGED', 'automatic_retry': False}
    body_rows = [r for r in rows if r.get('kind')]
    proof = {'schema': 'DEE.PI08.A2.actual_phase.R01', 'at_utc': datetime.now(timezone.utc).isoformat(),
        'phase': args.fase, 'life_id': args.vida, 'status': 'CLOSED_PHASE' if closed and error is None else 'FAILED_PRESERVED',
        'closed': closed, 'all_planned_steps_executed': len(body_rows) == len(phase['steps']),
        'error': error, 'initial_tick': card['physical']['tick'], 'final_tick': after['physical']['tick'],
        'new_Native_ticks': after['physical']['tick'] - card['physical']['tick'],
        'finite_Native_bound': maximum, 'plan': str(PLAN), 'plan_sha256': sha(PLAN),
        'intents': intents, 'rows': rows, 'states': states, 'functional_notes': notes,
        'Native_inputs': {'unique_requested': len(current_ids), 'status_counts': dict(totals)},
        'Native_budget_before': tick_total, 'worlds_before': lives,
        'protected_before': protected, 'protected_after': protected_after,
        'no_adoption_by_this_runner': True,
        'functional_gates_require_combined_phase_evaluation': True,
        'numeric_NULL_zero_and_rejections_not_silently_excluded': True}
    with proof_path.open('x', encoding='utf-8') as stream:
        json.dump(proof, stream, ensure_ascii=False, indent=2); stream.write('\n')
    if closed:
        require(read(marker)['pid'] == os.getpid(), 'Writer marker identity changed')
        marker.unlink()
    print(json.dumps({'proof': str(proof_path), 'sha256': sha(proof_path), 'status': proof['status'],
                      'closed': closed, 'final_tick': after['physical']['tick'], 'error': error}, ensure_ascii=False))
    return 0 if closed and error is None else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--vida', required=True); parser.add_argument('--fase', choices=['previas', 'suministro', 'reapertura'], required=True)
    parser.add_argument('--tag', required=True); parser.add_argument('--tick-inicial', type=int, required=True)
    parser.add_argument('--dry-run', action='store_true')
    raise SystemExit(main(parser.parse_args()))
