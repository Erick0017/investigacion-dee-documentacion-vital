"""Root-only finite retention panel on one explicitly imported B_REAL clone.

The default only prints the plan. FI uses the explicit fixed regulated mode:
the selected public alias was validated on A separately. No B episode or role
re-admission is allowed in this conservation identity. No promotion or reset.
"""
from pathlib import Path, PurePosixPath
from datetime import datetime, timezone
from collections import Counter
import argparse, copy, hashlib, importlib.util, json, os, re

P = Path(__file__).resolve().parents[1]
H = P / 'codigo'
C = P.parents[2] / 'DEE Cognitive 2.0'
RP = C / 'reproducibilidad'
PY = C / 'motor/python313/python.exe'
A = 'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
PANEL = RP / 'recetas/panel_12.json'
SEAL = H / 'SELLO_PI08_B_R01.json'
BOUND = 10184  # 7*512 +2*600 +3*1300 +1*1500; STATE/pause exactly0.

def require(ok, message):
    if not ok: raise ValueError(message)
def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module
def put(path, value):
    with path.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')
def regular(path):
    for node in (path, *path.parents):
        require(not node.exists() or not(node.is_symlink() or getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No linked experiment path')
    return path
def at(value, path):
    for key in path: value = value[key]
    return value
def receipts(items):
    unique = {}
    for item in items:
        identity, receipt = item['id'], item['receipt']
        require(type(identity) is int and receipt['id'] == identity, 'Current direct receipt ID mismatch')
        require(identity not in unique or unique[identity] == receipt, 'Conflicting receipt alias')
        unique[identity] = receipt
    return unique

def plan():
    result = copy.deepcopy(read(PANEL)['variants']['principal']['batches'][0])
    for step in result:
        if step['literal']['modo'] == 'eci01-balance':
            step['literal']['modo'] = 'eci01-pi07-fi-regulada'
            step['receipt_paths'] = [['result', 'rows', 0, 'requests']]
            step['max_ticks'] = 1300
        else:
            step['max_ticks'] = (0 if step.get('require_zero_ticks') else
                                 600 if step['literal']['modo'] == 'eci01-aritmetica-directa' else 512)
    require(sum('expected' in x for x in result) == 12, 'Exact twelve inherited witnesses required')
    return result

def native_ledger():
    cards = list((P / 'estados').glob('*/sistema/estado/vidas/*/VIDA.json')) + [C / 'sistema/estado/vidas' / A / 'VIDA.json']
    total, seen = 0, set()
    for file in cards:
        card = read(file); identity = card['life_id']; origin = card.get('parent', {}).get('source_tick')
        require(identity not in seen and type(origin) is int and card['physical']['tick'] >= origin,
                'Unambiguous imported-world origin required for campaign ledger')
        seen.add(identity); total += card['physical']['tick'] - origin
    return total, len(seen)

def main(args):
    steps = plan()
    if not args.ejecutar:
        print(json.dumps({'mode': 'PLAN_ONLY', 'Native_executed': False, 'panel_recipe_sha256': sha(PANEL),
            'steps': steps, 'additional_C2C': {'modo': 'eci01-pi04-c2c-oportunidad'},
            'C2C_expected_ordinal': 31, 'finite_Native_bound': BOUND,
            'conservation_identity': 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_CONSERVACION_01',
            'public_alias_scope': 'A selected public alias validated separately. Clone uses the explicit same regulated FI body; no alias validation inferred.'}, ensure_ascii=False))
        return 0
    require(args.sistema is not None and args.prefijo is not None and args.tick_inicial is not None,
            'Explicit isolated system, complete B_REAL prefix and exact current tick required')
    require(re.fullmatch(r'PI08_B_[A-Za-z0-9_]{1,45}', args.tag), 'One new bounded request tag')
    seal = read(SEAL); life = seal['conservation_life_id']; real = seal['research_life_ids']['real']
    require(life == 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_CONSERVACION_01', 'Prospectively fixed read-only B conservation identity required')
    system = regular(args.sistema.resolve(strict=True))
    require(system.name == 'sistema' and system.parent.parent == (P / 'estados').resolve(), 'One direct isolated PI08 system')
    require(not (system / 'estado/ACTIVO.json').exists(), 'Never test preservation on selected A/B principal')
    prefix = regular(args.prefijo.resolve(strict=True)); manifest = read(prefix / 'EXPORTACION_SERVICIO.json')
    require(manifest['life_id'] == real and manifest['physical']['tick'] == args.tick_inicial,
            'Actual final closed B_REAL full prefix required; no A or RAW-only substitute')
    mapping = read(system / 'estado/servicios_persistentes' / life / 'IMPORTACION.json')
    require(mapping['source_life_id'] == real and mapping['verification']['manifest_sha256'] == sha(prefix / 'EXPORTACION_SERVICIO.json'),
            'Conservation clone was not imported from the declared B_REAL pair')
    cardfile = system / 'estado/vidas' / life / 'VIDA.json'; card = read(cardfile)
    require(card['physical']['N'] == 67 and card['physical']['tick'] == args.tick_inicial, 'No stale restore or prior material use of conservation future')
    for folder in (system / 'estado/locks',): require(not folder.exists() or not any(folder.iterdir()), 'Affected writer lock remains')
    require(not (cardfile.parent / 'FUTURO_INTERRUMPIDO.json').exists(), 'Preserve interrupted future')
    require(not (RP / 'EJECUCION_MATERIAL.lock').exists(), 'RP material writer remains')
    marker = P / 'PI08_ROOT_NATIVE_WRITER.lock'; output = P / 'control' / (args.tag + '.json')
    require(not marker.exists() and not output.exists(), 'Existing writer/proof protected; do not reuse request IDs')
    budget = read(P / 'REGISTRO_CAMPANA.json')['budget']; used, worlds = native_ledger()
    require(used + BOUND <= budget['Native_ticks_all_branches'] and worlds <= budget['diagnostic_worlds_all_new'], 'Fixed Native/world budget insufficient')
    cutoff = datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
    require(datetime.now(timezone.utc) < cutoff, 'New experimental-use deadline reached')
    activefile = C / 'sistema/estado/ACTIVO.json'; acardfile = C / 'sistema/estado/vidas' / A / 'VIDA.json'; acard = read(acardfile)
    require(read(activefile)['life_id'] == A and acard['physical']['tick'] == seal['source_prefix']['T'], 'Protect exact adopted A used by B')
    protected = [activefile, acardfile, C / 'sistema' / acard['snapshot']]
    protected_hashes = {str(p): sha(p) for p in protected}
    panel_hash = sha(PANEL); seal_hash = sha(SEAL)
    put(marker, {'pid': os.getpid(), 'life_id': life, 'kind': 'B_CONSERVATION_CLONE_ONLY', 'bound': BOUND})
    supervisor = load('PI08_B_retention_existing_owner', RP / 'propietario_diagnostico.py'); supervisor.configure(P, system, PY)
    owner, error = None, None
    rows, states, notes, ids, totals, values = [], {}, [], set(), Counter(), {}

    def material(label, literal, bound):
        require(datetime.now(timezone.utc) < cutoff, 'Deadline between bounded operations')
        require(sha(PANEL) == panel_hash and sha(SEAL) == seal_hash, 'Frozen panel/seal changed during execution')
        value = owner.material(args.tag + '_' + label, literal, feedback='real', actuator='closed')
        require(0 <= value['after_tick'] - value['before_tick'] <= bound, 'Finite bound exceeded; preserve future')
        file = P / 'ensayos' / (args.tag + '_' + label + '.json')
        rows.append({'label': label, 'literal': literal, 'before_tick': value['before_tick'], 'after_tick': value['after_tick'],
                     'primary': str(file), 'primary_sha256': sha(file)})
        return value

    def count(items):
        direct = receipts(items); require(not ids.intersection(direct), 'Inherited receipt counted as current input')
        ids.update(direct); counts = Counter(r['status'] for r in direct.values())
        require(all(k == 'applied' or k.startswith('rejected') for k in counts), 'Unresolved Native admission; no automatic replay')
        totals.update(counts); rows[-1]['Native_inputs'] = {'unique_requested': len(direct), 'status_counts': dict(counts)}
        return direct

    try:
        owner = supervisor.Owner(life, args.tag, system=system)
        with owner:
            bbefore = material('B_pre', {'modo': 'eci01-pi08-b-estado'}, 0)['result']['rows'][0]
            states['B_pre'] = bbefore
            require(bbefore['progress']['ordinal'] == 30 and bbefore['progress']['control']['arm'] == 'real',
                    'Only completed real18 continuation is tested; no arbitrary development prefix')
            cpre = material('C2C_pre', {'modo': 'eci01-pi04-c2c-estado'}, 0)['result']['rows'][0]
            states['C2C_pre'] = cpre
            require(cpre['progress']['ordinal'] == cpre['device']['ordinal'] == 31 and len(cpre['device']['resources']) == 32,
                    'Exactly one inherited C2C opportunity must remain in the clone')
            for step in steps:
                literal = dict(step['literal'])
                if 'actual_integer_binding' in step:
                    binding = step['actual_integer_binding']; number = values[binding['from_step']]
                    require(type(number) is int, 'A missing actual result cannot be replaced with expected13')
                    literal[binding['field']] = number
                value = material(step['label'], literal, step['max_ticks'])
                if step.get('require_zero_ticks'): continue
                observed = at(value, step['read_path']); values[step['label']] = observed
                rows[-1].update(observed=observed, expected_evaluator_only=step['expected'], correct=observed == step['expected'])
                direct = count([item for path in step['receipt_paths'] for item in at(value, path)])
                if observed is None: notes.append({'label': step['label'], 'kind': 'NULL_PRESERVED_DISTINCT_FROM_MATERIAL_ZERO'})
            cuse = material('C2C31', {'modo': 'eci01-pi04-c2c-oportunidad'}, 1500)['result']['rows'][0]
            require(cuse['ordinal'] == 31, 'No different resource was consumed')
            arithmetic = cuse.get('native_arithmetic'); second = cuse.get('second_native_use')
            groups = [cuse['requests']]
            if arithmetic is not None: groups.append(arithmetic['native_operation']['native_trial']['requests'])
            if second is not None and isinstance(second.get('requests'), list): groups.append(second['requests'])
            current = count([item for group in groups for item in group])
            require(cuse['native_input_summary']['unique_requested'] == len(current), 'Direct C2C collector differs from scientific collector')
            rows[-1].update(correct=cuse['useful_product'], actual_numeric_result=cuse['actual_numeric_result'],
                            selected_operation=cuse['selected_operation'], second_motor=cuse['second_motor'])
            if cuse['useful_product']:
                product = cuse['actual_effect']['product']; relative = PurePosixPath(product['path'])
                require(not relative.is_absolute() and ':' not in product['path'] and '\\' not in product['path'] and all(v not in ('.', '..') for v in relative.parts), 'Unsafe actual product path')
                file = regular(system / 'estado/servicios_locales' / life / 'PI08_C2C_INTEGRACION_R01/dispositivo32' / relative)
                data = file.read_bytes()
                require(len(data) == product['bytes'] == 64 and sha(file) == product['sha256']
                        and type(cuse['actual_numeric_result']) is int and int.from_bytes(data[:2], 'little') == cuse['actual_numeric_result'], 'Actual64B product does not carry real arithmetic result')
                rows[-1]['actual_product'] = {'path': str(file), 'bytes': 64, 'sha256': sha(file)}
            bafter = material('B_post', {'modo': 'eci01-pi08-b-estado'}, 0)['result']['rows'][0]
            cafter = material('C2C_post', {'modo': 'eci01-pi04-c2c-estado'}, 0)['result']['rows'][0]
            states.update(B_post=bafter, C2C_post=cafter)
            require(bbefore['progress'] == bafter['progress'], 'Conservation must never advance/reset B environment progress')
            require(cafter['progress']['ordinal'] == cafter['device']['ordinal'] == 32, 'Last C2C opportunity did not close exactly once')
            owner.control('guardar')
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'automatic_retry': False}
    closed = bool(owner is not None and owner.proc is not None and owner.proc.poll() == 0 and not(owner.q.get_meta('owner') or {}).get('running') and not owner.q.outstanding())
    after = read(cardfile); delta = after['physical']['tick'] - args.tick_inicial
    witnesses = [r for r in rows if r['label'] in values]
    a_unchanged = protected_hashes == {str(p): sha(p) for p in protected}
    c2c = next((r for r in rows if r['label'] == 'C2C31'), {})
    criteria = bool(closed and error is None and a_unchanged and 0 <= delta <= BOUND
                    and len(witnesses) == 12 and all(r['correct'] for r in witnesses) and c2c.get('correct') is True
                    and all(status == 'applied' for status in totals))
    result = {'schema': 'DEE.PI08.B.real_clone_conservation.R02', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
              'life_id': life, 'source_B_REAL': real, 'source_full_pair': str(prefix), 'source_manifest_sha256': sha(prefix / 'EXPORTACION_SERVICIO.json'),
              'closed': closed, 'owner_closed': closed, 'criteria_met': criteria, 'error': error,
              'initial_tick': args.tick_inicial, 'final_tick': after['physical']['tick'], 'new_Native_ticks': delta,
              'finite_Native_bound': BOUND, 'snapshot_sha256': after['snapshot_sha256'],
              'panel_correct': sum(r['correct'] for r in witnesses), 'panel_witnesses': len(witnesses),
              'C2C_last_offer_product': c2c.get('correct'), 'rows': rows, 'states': states, 'notes': notes,
              'Native_inputs': {'unique_requested': len(ids), 'status_counts': dict(totals)},
              'adopted_A_unchanged': a_unchanged, 'protected_hashes': protected_hashes,
              'public_alias_not_tested_in_this_clone': True, 'FI_access': 'Explicit regulated FI body; selected public A alias validated separately. B selected alias is a distinct future operational gate if B is promoted.',
              'B_episode_never_called': True, 'no_promotion_or_reset': True, 'budget_before_ticks': used, 'worlds_before': worlds}
    put(output, result)
    if closed and marker.exists(): marker.unlink()
    print(json.dumps({'proof': str(output), 'sha256': sha(output), 'criteria_met': criteria,
                      'closed': closed, 'final_tick': after['physical']['tick'], 'panel_correct': result['panel_correct']}))
    return 0 if criteria else 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sistema', type=Path); parser.add_argument('--prefijo', type=Path)
    parser.add_argument('--tick-inicial', type=int); parser.add_argument('--tag', default='PI08_B_CONSERVACION_R02')
    parser.add_argument('--ejecutar', action='store_true')
    raise SystemExit(main(parser.parse_args()))
