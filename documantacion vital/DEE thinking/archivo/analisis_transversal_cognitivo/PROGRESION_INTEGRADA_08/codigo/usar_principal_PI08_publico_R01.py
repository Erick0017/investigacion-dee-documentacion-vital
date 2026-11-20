"""Root-only public use of the actually COMMITTED PI08 principal.

Default is a plan. --ejecutar uses the existing bounded Cognitive owner,
public eci01-balance(18,7), then inherited alfa; expected values are evaluated
only after responses. No import, selection, teaching, resource reset or retry.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, hashlib, importlib.util, json, os

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = C / 'sistema'
RP = C / 'reproducibilidad'
PY = C / 'motor/python313/python.exe'
LIFE = 'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
PARENT = 'ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
TAG = 'PI08_USO_PUBLICO_PRINCIPAL_R01'
BOUND = 1812

def read(path):
    return json.loads(Path(path).read_text('utf-8-sig'))

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def require(ok, text):
    if not ok:
        raise ValueError(text)

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def put(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')

def receipts(items):
    unique = {}
    for item in items:
        identity, receipt = item['id'], item['receipt']
        require(type(identity) is int and receipt['id'] == identity,
                'Direct request/receipt identity mismatch')
        require(identity not in unique or unique[identity] == receipt,
                'Conflicting direct receipt alias')
        unique[identity] = receipt
    return unique

def main(args):
    output = P / 'control' / (TAG + '.json')
    require(not output.exists(), 'Existing use proof preserved; never repeat this ID')
    plan = [('FI18_7', {'modo': 'eci01-balance', 'izquierda': 18, 'derecha': 7}, 1300),
            ('alfa', {'modo': 'memoria', 'operacion_memoria': 'usar', 'contexto': 'alfa'}, 512)]
    if not args.ejecutar:
        print(json.dumps({'mode': 'PLAN_ONLY', 'life_id': LIFE, 'system': str(S),
                          'public_literals': [x[1] for x in plan],
                          'finite_Native_bound': BOUND, 'Native_executed': False}))
        return 0
    active_path = S / 'estado/ACTIVO.json'
    active = read(active_path)
    require(active['life_id'] == LIFE, 'Exact actually selected PI08 principal required')
    profile = read(S / 'contratos/PI08_USO_OPERATIVO_R01.json')
    require(profile['status'] == 'COMMITTED' and profile.get('adoption_decision_sha256'),
            'Actual COMMITTED permission required')
    card_path = S / 'estado/vidas' / LIFE / 'VIDA.json'
    before = read(card_path)
    initial = before['physical']['tick']
    require(before['physical']['N'] == 67 and initial >= 860622,
            'Actual adopted current future required; never restore an older cut')
    for folder in (S / 'estado/locks',):
        require(not folder.exists() or not any(folder.iterdir()), 'Affected owner lock remains')
    require(not (card_path.parent / 'FUTURO_INTERRUMPIDO.json').exists(),
            'Interrupted principal must remain preserved')
    require(not (RP / 'EJECUCION_MATERIAL.lock').exists(), 'Independent RP writer remains')
    marker = P / 'PI08_ROOT_NATIVE_WRITER.lock'
    require(not marker.exists(), 'PI08 sole-writer marker remains')
    parent_card = S / 'estado/vidas' / PARENT / 'VIDA.json'
    parent = read(parent_card)
    protected = [parent_card, S / parent['snapshot']]
    protected_before = {str(path): sha(path) for path in protected}
    # Include the adopted life after its relocation, without counting it twice.
    cards = list((P / 'estados').glob('*/sistema/estado/vidas/*/VIDA.json')) + [card_path]
    seen, ticks = set(), 0
    for path in cards:
        card = read(path)
        require(card['life_id'] not in seen, 'Duplicate current life while counting Native budget')
        seen.add(card['life_id'])
        origin = card.get('parent', {}).get('source_tick')
        require(type(origin) is int and card['physical']['tick'] >= origin, 'Missing current-world origin')
        ticks += card['physical']['tick'] - origin
    budget = read(P / 'REGISTRO_CAMPANA.json')['budget']
    require(ticks + BOUND <= budget['Native_ticks_all_branches'], 'Remaining Native budget insufficient')
    require(datetime.now(timezone.utc) < datetime.fromisoformat(budget['hard_stop_local']).astimezone(timezone.utc),
            'Campaign hard stop reached')
    put(marker, {'pid': os.getpid(), 'life_id': LIFE, 'kind': 'SELECTED_PUBLIC_OPERATIVE_USE',
                 'finite_Native_bound': BOUND})
    ownerlib = load('PI08_selected_public_owner', RP / 'propietario_diagnostico.py')
    ownerlib.configure(P, S, PY)
    owner, error, rows = None, None, []
    ids, counts = set(), Counter()
    try:
        owner = ownerlib.Owner(LIFE, TAG, system=S)
        with owner:
            for label, literal, limit in plan:
                identifier = TAG + '_' + label
                value = owner.material(identifier, literal, feedback='real', actuator='closed')
                primary = P / 'ensayos' / (identifier + '.json')
                require(0 <= value['after_tick'] - value['before_tick'] <= limit,
                        'Operation exceeded its prospective finite bound')
                row = value['result']['rows'][0]
                if label == 'FI18_7':
                    require('public_operands' in row and 'generic_return_failed' in row,
                            'Public command did not reach declared regulated FI route')
                    observed, expected, inner = row['early_physical_choice'], 1, row
                    detail = {'public_mode': literal['modo'], 'route_version': row['version'],
                              'sensor_state': row['sensor']['actual_state_datum'],
                              'Native_choice': row['reader']['choice'],
                              'pulse_applied': row['pulse_applied']}
                else:
                    inner = row['result']['rows'][0]
                    observed, expected, detail = inner['reader']['formed_native_command'], -1, {}
                direct = receipts(inner['requests'])
                require(not ids.intersection(direct), 'Inherited receipt counted as new input')
                ids.update(direct)
                status = Counter(x['status'] for x in direct.values())
                require(all(k == 'applied' or k.startswith('rejected') for k in status),
                        'Unresolved Native input; preserve future without resend')
                counts.update(status)
                rows.append({'label': label, 'literal': literal, 'primary': str(primary),
                             'primary_sha256': sha(primary), 'before_tick': value['before_tick'],
                             'after_tick': value['after_tick'], 'observed': observed,
                             'expected_evaluator_only': expected, 'correct': observed == expected,
                             'Native_inputs': {'unique_requested': len(direct), 'status_counts': dict(status)},
                             **detail})
            owner.control('guardar')
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'automatic_retry': False}
    closed = bool(owner is not None and owner.proc is not None and owner.proc.poll() == 0
                  and not (owner.q.get_meta('owner') or {}).get('running') and not owner.q.outstanding())
    after = read(card_path)
    unchanged = protected_before == {str(path): sha(path) for path in protected}
    delta = after['physical']['tick'] - initial
    criteria = bool(closed and error is None and unchanged and 0 <= delta <= BOUND
                    and len(rows) == 2 and all(r['correct'] for r in rows)
                    and all(k == 'applied' for k in counts)
                    and read(active_path)['life_id'] == LIFE)
    result = {'schema': 'DEE.PI08.selected_public_material_use.R01',
              'recorded_utc': datetime.now(timezone.utc).isoformat(), 'life_id': LIFE,
              'initial_tick': initial, 'final_tick': after['physical']['tick'],
              'new_Native_ticks': delta, 'finite_Native_bound': BOUND,
              'Native_executed': True, 'closed': closed, 'owner_closed': closed,
              'pending_reconciled': closed, 'criteria_met': criteria, 'error': error,
              'snapshot_sha256': after['snapshot_sha256'], 'rows': rows,
              'Native_inputs': {'unique_requested': len(ids), 'status_counts': dict(counts)},
              'previous_principal_unchanged': unchanged, 'protected_before': protected_before,
              'budget_before_ticks': ticks, 'scope': 'Actual selected public FI route and inherited alfa; '
              'operational validation, not an independent generalization or a new complete panel.'}
    put(output, result)
    if closed and marker.exists():
        marker.unlink()
    print(json.dumps({'proof': str(output), 'sha256': sha(output), 'criteria_met': criteria,
                      'closed': closed, 'new_Native_ticks': delta, 'final_tick': after['physical']['tick']}))
    return 0 if criteria else 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ejecutar', action='store_true')
    raise SystemExit(main(parser.parse_args()))
