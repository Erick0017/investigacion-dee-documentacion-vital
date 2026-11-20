"""Root-only prospective panel on the EXISTING closed None18 future.

No clone, role re-admission, B episode, reset, repair or new provider. Preserve
the complete None prefix before advancing. This never repairs the B gate.
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
BOUND = 8684  # Same12 witnesses; omit only the later C2C material use.
AUTOPROTOCOL=P/'control/PROTOCOLO_AUTOPSIA_PANEL_B_NONE_PI08_R01.json'
AUTOPROTOCOL_SHA='39776d62c93bc4879e3e7a20a0d1c49e2529d6219d88e5978c9e4fd88f374a2f'

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
            'steps': steps, 'additional_C2C': None,
            'C2C_ordinal_preserved': 31, 'finite_Native_bound': BOUND,
            'existing_None_identity': 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_NONE_01',
            'public_alias_scope': 'A selected public alias validated separately. Clone uses the explicit same regulated FI body; no alias validation inferred.'}, ensure_ascii=False))
        return 0
    require(args.sistema is not None and args.prefijo is not None and args.tick_inicial is not None,
            'Explicit isolated system, complete B_REAL prefix and exact current tick required')
    require(re.fullmatch(r'PI08_B_[A-Za-z0-9_]{1,45}', args.tag), 'One new bounded request tag')
    seal = read(SEAL); life = seal['research_life_ids']['none']; real = life
    require(sha(AUTOPROTOCOL)==AUTOPROTOCOL_SHA,'Prospective None autopsy protocol changed')
    autop=read(AUTOPROTOCOL); require(plan()==autop['literal_steps'],'Literal panel differs from sealed autopsy')
    require(datetime.now(timezone.utc)<datetime.fromisoformat(autop['latest_start_local']).astimezone(timezone.utc),'Start deadline18:15 reached')
    require(life == 'ECI02_PI03_REPRO_PI04_PI05_PI07_PI08_B_NONE_01', 'Only the existing sealed None identity')
    system = regular(args.sistema.resolve(strict=True))
    require(system.name == 'sistema' and system.parent.parent == (P / 'estados').resolve(), 'One direct isolated PI08 system')
    require(not (system / 'estado/ACTIVO.json').exists(), 'Never test preservation on selected A/B principal')
    prefix = regular(args.prefijo.resolve(strict=True)); manifest = read(prefix / 'EXPORTACION_SERVICIO.json')
    require(manifest['life_id']==life and manifest['physical']['tick']==args.tick_inicial==875451 and manifest['snapshot_sha256']==autop['source_snapshot_sha256'],'Exact preserved full None18 prefix required')
    preservation=read(prefix.parent/(prefix.name+'_PRESERVACION.json'))
    require(preservation['source_files_all_unchanged']is True and preservation['manifest_sha256']==sha(prefix/'EXPORTACION_SERVICIO.json'),'Complete checked None preservation required')
    require(sha(prefix/manifest['native_snapshot'])==manifest['snapshot_sha256'],'Preserved Native bytes changed')
    mapping = read(system / 'estado/servicios_persistentes' / life / 'IMPORTACION.json')
    require(mapping['source_life_id']==A and mapping['verification']['manifest_sha256']==seal['source_prefix']['manifest_sha256'],'Existing None must retain its original A import mapping; no reimport')
    cardfile = system / 'estado/vidas' / life / 'VIDA.json'; card = read(cardfile)
    require(system==(P/'estados/B_NONE_R01/sistema').resolve()and card['physical']['N']==67 and card['physical']['tick']==args.tick_inicial==875451 and card['snapshot_sha256']==autop['source_snapshot_sha256'],'No stale restore or prior new use of this None future')
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
            require(bbefore['progress']['ordinal'] == 30 and bbefore['progress']['control']['arm'] == 'none',
                    'Only the preserved existing None18 continuation; no role reset')
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
            bafter = material('B_post', {'modo': 'eci01-pi08-b-estado'}, 0)['result']['rows'][0]
            cafter = material('C2C_post', {'modo': 'eci01-pi04-c2c-estado'}, 0)['result']['rows'][0]
            states.update(B_post=bafter, C2C_post=cafter)
            require(bbefore['progress'] == bafter['progress'], 'Conservation must never advance/reset B environment progress')
            require(cafter['progress']==cpre['progress']and cafter['device']==cpre['device'],'C2C resource/history must remain literal; no material C2C use')
            owner.control('guardar')
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'automatic_retry': False}
    closed = bool(owner is not None and owner.proc is not None and owner.proc.poll() == 0 and not(owner.q.get_meta('owner') or {}).get('running') and not owner.q.outstanding())
    after = read(cardfile); delta = after['physical']['tick'] - args.tick_inicial
    witnesses = [r for r in rows if r['label'] in values]
    a_unchanged = protected_hashes == {str(p): sha(p) for p in protected}
    c2c = next((r for r in rows if r['label'] == 'C2C31'), {})
    criteria = bool(closed and error is None and a_unchanged and 0 <= delta <= BOUND
                    and len(witnesses) == 12 and all(r['correct'] for r in witnesses)
                    and all(status == 'applied' for status in totals))
    result = {'schema': 'DEE.PI08.B.existing_NONE_panel_autopsy.R01', 'recorded_utc': datetime.now(timezone.utc).isoformat(),
              'life_id': life, 'source_B_NONE': life, 'source_full_pair': str(prefix), 'source_manifest_sha256': sha(prefix / 'EXPORTACION_SERVICIO.json'),
              'closed': closed, 'owner_closed': closed, 'criteria_met': criteria, 'error': error,
              'initial_tick': args.tick_inicial, 'final_tick': after['physical']['tick'], 'new_Native_ticks': delta,
              'finite_Native_bound': BOUND, 'snapshot_sha256': after['snapshot_sha256'],
              'panel_correct': sum(r['correct'] for r in witnesses), 'panel_witnesses': len(witnesses),
              'C2C_material_use': False, 'C2C_resource_unchanged': states.get('C2C_pre')==states.get('C2C_post'), 'rows': rows, 'states': states, 'notes': notes,
              'Native_inputs': {'unique_requested': len(ids), 'status_counts': dict(totals)},
              'adopted_A_unchanged': a_unchanged, 'protected_hashes': protected_hashes,
              'public_alias_not_tested_in_this_clone': True, 'FI_access': 'Explicit regulated FI body; selected public A alias validated separately. B selected alias is a distinct future operational gate if B is promoted.',
              'B_episode_never_called': True, 'no_promotion_or_reset': True, 'budget_before_ticks': used, 'worlds_before': worlds,
              'prospective_protocol':{'path':str(AUTOPROTOCOL),'sha256':AUTOPROTOCOL_SHA},
              'original_B_conservation_gate_remains_false':True, 'reference_real_panel':autop['reference_real_panel']}
    refrows={r['label']:r for r in read(Path(autop['reference_real_panel']['path']))['rows']}
    result['phase_and_dose_comparison']=[{'label':r['label'],'before_tick_equal':r['before_tick']==refrows[r['label']]['before_tick'],'after_tick_equal':r['after_tick']==refrows[r['label']]['after_tick'],'current_Native_inputs':r.get('Native_inputs'),'reference_Native_inputs':refrows[r['label']].get('Native_inputs'),'same_nominal_mode':r['literal']['modo']==refrows[r['label']]['literal']['modo']}for r in rows if r['label']in refrows]
    result['comparison_limits']='Same nominal schedule is not proof of same Native input dose/geometry. Any Native-dependent action or transported-number difference is preserved above; no single-factor causal claim is automatic.'
    put(output, result)
    if closed and marker.exists(): marker.unlink()
    print(json.dumps({'proof': str(output), 'sha256': sha(output), 'criteria_met': criteria,
                      'closed': closed, 'final_tick': after['physical']['tick'], 'panel_correct': result['panel_correct']}))
    return 0 if criteria else 2

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sistema', type=Path); parser.add_argument('--prefijo', type=Path)
    parser.add_argument('--tick-inicial', type=int); parser.add_argument('--tag', default='PI08_B_NONE_AUTOPSIA_PANEL_R01')
    parser.add_argument('--ejecutar', action='store_true')
    raise SystemExit(main(parser.parse_args()))
