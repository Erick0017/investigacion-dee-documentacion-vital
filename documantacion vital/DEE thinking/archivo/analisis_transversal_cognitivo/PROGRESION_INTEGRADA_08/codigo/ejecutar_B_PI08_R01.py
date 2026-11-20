"""Root-only bounded B owner runner. Default prints a plan; no Native import.

Run each explicit arm once on a new complete diagnostic clone of the SAME A
prefix. No loop retries, bank reset, principal replacement or implied adoption.
"""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, hashlib, importlib.util, json, os, re

P = Path(__file__).resolve().parents[1]
H = P/'codigo'
C = P.parents[2]/'DEE Cognitive 2.0'
RP = C/'reproducibilidad'
PY = C/'motor/python313/python.exe'
A = 'ECI02_PI03_REPRO_PI04_PI05_PI07_RP_R03_PI08_A01'
START = 'eci01-pi08-b-iniciar'
EPISODE = 'eci01-pi08-b-episodio'
STATE = 'eci01-pi08-b-estado'


def require(ok, message):
    if not ok: raise ValueError(message)
def read(path): return json.loads(Path(path).read_text('utf-8-sig'))
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def safe(path, root=P):
    path = Path(path).resolve(strict=True)
    require(path.is_relative_to(root.resolve()), 'Path outside declared PI08 workspace')
    for node in (path, *path.parents):
        require(not node.is_symlink() and not(getattr(node.lstat(), 'st_file_attributes', 0)&1024), 'No reparse or linked world')
    return path


def receipts(rows):
    unique = {}; aliases = 0
    for row in rows:
        rid = row['id']; receipt = row['receipt']
        require(type(rid) is int and receipt['id'] == rid, 'Native receipt identity mismatch')
        if rid in unique:
            require(unique[rid] == receipt, 'Contradictory Native alias')
            aliases += 1
        unique[rid] = receipt
    return unique, aliases


def native_ledger():
    paths = list((P/'estados').glob('*/sistema/estado/vidas/*/VIDA.json'))
    selected_A = C/'sistema/estado/vidas'/A/'VIDA.json'
    if selected_A.is_file(): paths.append(selected_A)
    seen = {}; total = 0
    for path in paths:
        card = read(path); life = card['life_id']
        current = card['physical']['tick']; initial = card.get('parent', {}).get('source_tick')
        require(type(initial) is int and current >= initial, 'Imported complete origin must remain known')
        row = {'life_id': life, 'card': str(path), 'initial_tick': initial, 'current_tick': current, 'Native_ticks': current-initial}
        if life in seen:
            require(seen[life]['current_tick'] == current and seen[life]['initial_tick'] == initial, 'Two divergent current stores for one identity')
            continue
        seen[life] = row; total += current-initial
    return total, list(seen.values())


def main(args):
    protocol_path = H/'PROTOCOLO_PI08_B_R01.json'; seal_path = H/'SELLO_PI08_B_R01.json'
    p = read(protocol_path); seal = read(seal_path)
    require(p['status'] == 'SEALED_BEFORE_B_NATIVE' and seal['protocol_sha256'] == sha(protocol_path), 'Prospective B seal required')
    life = seal['research_life_ids'][args.brazo]
    require(re.fullmatch(r'PI08_B_[A-Za-z0-9_]{1,40}', args.tag), 'Fresh explicit request tag')
    system = safe(args.sistema)
    require(system.name == 'sistema', 'Explicit isolated diagnostic system required')
    require(not (system/'estado/ACTIVO.json').exists(), 'Never run B on a selected principal')
    planned = [{'label': 'iniciar', 'literal': {'modo': START, 'brazo': args.brazo,
                 'prefijo_sha256': seal['source_prefix']['manifest_sha256'], 'registro_global': args.registro_global}}]
    if args.brazo == 'yoked':
        require(args.plan_yoke is not None, 'Actual real18-derived yoked plan is required')
        yp = safe(args.plan_yoke); text = yp.read_text('utf8'); digest = hashlib.sha256(text.encode('utf8')).hexdigest()
        planned[0]['literal'].update(plan=text, plan_sha256=digest)
    planned += [{'label': 'EP%02d' % i, 'literal': {'modo': EPISODE}} for i in range(18)]
    if not args.ejecutar:
        print(json.dumps({'mode': 'PLAN_ONLY_NO_NATIVE', 'life_id': life, 'role': args.brazo,
          'system': str(system), 'ordinal_before': 12, 'ordinal_after': 30, 'evaluated_opportunities': 18,
          'finite_Native_bound': 23400, 'prospective_global_captures': 5 if args.registro_global else 0,
          'protocol_sha256': sha(protocol_path), 'steps': planned}, ensure_ascii=False, indent=2))
        return
    budget = read(P/'REGISTRO_CAMPANA.json')['budget']
    cutoff = datetime.fromisoformat(budget['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
    tick_total, worlds = native_ledger()
    require(tick_total+23400 <= budget['Native_ticks_all_branches'], 'Finite B budget unavailable')
    require(len(worlds) <= budget['diagnostic_worlds_all_new'], 'Declared world limit exceeded')
    require(datetime.now(timezone.utc) < cutoff, 'New material work cutoff reached')
    card = read(safe(system/'estado/vidas'/life/'VIDA.json'))
    require(card['physical']['tick'] == seal['source_prefix']['T'], 'No stale/used branch or retrospective restart')
    require({k:card['physical'][k] for k in seal['source_prefix']['physical']} == seal['source_prefix']['physical'], 'Full-prefix physical mismatch')
    for path in (system/'estado/locks',):
        require(not path.exists() or not any(path.iterdir()), 'Owner lock remains; inspect, never erase')
    require(not (system/'estado/vidas'/life/'FUTURO_INTERRUMPIDO.json').exists(), 'Preserve interrupted future')
    require(not (RP/'EJECUCION_MATERIAL.lock').exists(), 'RP writer still active')
    active_path = C/'sistema/estado/ACTIVO.json'; active = read(active_path)
    require(active['life_id'] == A, 'A must remain the protected adopted principal')
    a_card_path = C/'sistema/estado/vidas'/A/'VIDA.json'; a_card = read(a_card_path)
    require(a_card['physical']['tick'] == seal['source_prefix']['T'], 'Protected A advanced beyond the sealed prefix; preserve it and revise prospectively')
    protected_paths = [active_path, a_card_path, C/'sistema'/a_card['snapshot']]
    protected = {str(path): sha(path) for path in protected_paths}
    for name, digest in seal['files_sha256'].items():
        require(sha(system/'capacidades'/name) == digest, 'Installed B dependency differs: '+name)
    require(sha(system/'capacidades/PROTOCOLO_PI08_B_R01.json') == sha(protocol_path)
            and sha(system/'capacidades/SELLO_PI08_B_R01.json') == sha(seal_path), 'Installed protocol or seal differs')
    proof_path = P/'control'/(args.tag+'.json'); marker = P/'PI08_ROOT_NATIVE_WRITER.lock'
    require(not proof_path.exists() and not marker.exists(), 'Fresh arm/tag and one Root Native writer only')
    with marker.open('x', encoding='utf8') as out:
        json.dump({'pid': os.getpid(), 'life_id': life, 'role': args.brazo, 'finite_Native_bound': 23400}, out)
    spec = importlib.util.spec_from_file_location('PI08_B_owned_driver', RP/'propietario_diagnostico.py')
    driver = importlib.util.module_from_spec(spec); spec.loader.exec_module(driver); driver.configure(P, system, PY)
    owner = None; error = None; records = []; intervals = []; seen_ids = set(); totals = Counter(); states = {}; intents = []
    initial_tick = card['physical']['tick']; frozen_protocol = protocol_path.read_bytes(); frozen_seal = seal_path.read_bytes()
    def call(label, literal, maximum):
        require(datetime.now(timezone.utc) < cutoff, 'Deadline before next opportunity')
        require(protocol_path.read_bytes() == frozen_protocol and seal_path.read_bytes() == frozen_seal, 'Sealed design changed')
        identifier = args.tag+'_'+label
        intents.append({'id': identifier, 'literal': literal, 'max_Native_ticks': maximum})
        value = owner.material(identifier, literal, feedback='real', actuator='closed', allow_failure=True)
        require('before_tick' in value and 'after_tick' in value and 0 <= value['after_tick']-value['before_tick'] <= maximum,
                'Missing/ambiguous result or finite-bound failure; do not retry')
        path = P/'ensayos'/(identifier+'.json')
        intervals.append({'label': label, 'before_tick': value['before_tick'], 'after_tick': value['after_tick'],
                          'primary': str(path), 'sha256': sha(path)})
        return value['result']['rows'][0]
    try:
        owner = driver.Owner(life, args.tag)
        with owner:
            state_before = call('estado_pre', {'modo': STATE}, 0)
            require(state_before['present'] is False, 'No new B world may already contain B progress')
            admission = call('iniciar', planned[0]['literal'], 0)
            require(admission['admitted'] and admission['control']['arm'] == args.brazo, 'Exact control admission failed')
            states['admission'] = admission
            for i in range(18):
                row = call('EP%02d' % i, {'modo': EPISODE}, 1300)
                require(row['B_ordinal'] == i and row['global_regulatory_ordinal'] == i+12 and row['ordinal'] == i+12, 'Wrong environmental/cognitive continuation ordinal')
                direct, aliases = receipts(row['requests']); count = Counter(r['status'] for r in direct.values())
                require(not seen_ids.intersection(direct), 'Historical Native receipt counted as new')
                seen_ids.update(direct); totals.update(count)
                require(all(k == 'applied' or k.startswith('rejected') for k in count), 'Unknown/pending Native input')
                require(row['Native_inputs']['unique_requested'] == len(direct) and row['Native_inputs']['applied'] == count['applied'], 'Direct current receipt denominator mismatch')
                require(row['R01_R02_metadata_literal_unchanged'], 'Old R01/R02/R03 history changed')
                records.append({'ordinal': row['ordinal'], 'B_ordinal': i, 'before_tick': row['before_tick'], 'after_tick': row['after_tick'],
                  'sensor_STATE': row['sensor']['actual_state_datum'], 'Native_choice': row['reader']['choice'], 'native_motor': row['native_motor'],
                  'Native_selection_valid': row['Native_selection_valid'],
                  'actual_motor': row['actual_motor'], 'executed_action_source': row['executed_action_source'],
                  'FI_q4': row['FI']['early_physical_choice'], 'FI_q6': row['FI']['old_q6_choice'],
                  'message_offered': row['message']['required_payload'] is not None, 'message_delivered': row['message']['delivered_exact'],
                  'pulse_scheduled': row['pulse_scheduled'], 'pulse_applied': row['pulse_applied'],
                  'actual_failed': row['actual_failed'], 'returned_failed': row['returned_failed'],
                  'calendar': row['calendar'], 'reference_before': row['reference_before'], 'return_frames': row['return_frames'],
                  'Native_inputs': {'unique_requested': len(direct), 'status_counts': dict(count), 'aliases_not_events': aliases},
                  'reference_policy_before': row['reference_policy_before'], 'reference_policy_after': row['reference_policy_after'],
                  'external_global_capture': row['external_global_capture']})
            states['final'] = call('estado_final', {'modo': STATE}, 0)
            progress = states['final']['progress']
            require(progress['ordinal'] == 30 and not progress['pending'] and not progress['uncertain'], 'Final B future incomplete')
            owner.control('guardar')
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'automatic_retry': False}
    closed = bool(owner is not None and owner.proc is not None and owner.proc.poll() == 0 and not (owner.q.get_meta('owner') or {}).get('running'))
    protected_after = {str(path): sha(path) for path in protected_paths}
    if protected_after != protected: error = {'type': 'PROTECTED_ADOPTED_A_CHANGED', 'automatic_retry': False}
    finalcard = read(system/'estado/vidas'/life/'VIDA.json')
    result = {'schema': 'DEE.PI08.B.actual_nonperiodic_arm.R01', 'at_utc': datetime.now(timezone.utc).isoformat(),
       'life_id': life, 'role': args.brazo, 'status': 'CLOSED_18_OPPORTUNITIES' if closed and error is None and len(records) == 18 else 'STOPPED_PRESERVED',
       'closed': closed, 'error': error, 'initial_tick': initial_tick, 'final_tick': finalcard['physical']['tick'],
       'new_Native_ticks': finalcard['physical']['tick']-initial_tick, 'finite_Native_bound': 23400,
       'opportunities_completed': len(records), 'joint_useful': sum(not row['actual_failed'] for row in records),
       'valid_Native_selections': sum(row['Native_selection_valid'] for row in records),
       'FI_correct_positive': sum(row['FI_q6'] == 1 for row in records),
       'messages_offered': sum(row['message_offered'] for row in records), 'messages_delivered': sum(row['message_delivered'] for row in records),
       'actual_failures': sum(row['actual_failed'] for row in records), 'returned_failures': sum(row['returned_failed'] for row in records),
       'return_mismatches': sum(row['actual_failed'] != row['returned_failed'] for row in records),
       'rows': records, 'intervals': intervals, 'intents': intents, 'states': states,
       'Native_inputs': {'unique_requested': len(seen_ids), 'status_counts': dict(totals)},
       'protocol_sha256': sha(protocol_path), 'seal_sha256': sha(seal_path), 'Native_budget_before': tick_total,
       'worlds_before': worlds, 'protected_before': protected, 'protected_after': protected_after,
       'no_adoption_by_this_runner': True, 'scope': 'Finite18 material opportunities, failures retained; four shared-prefix controls, not independent individuals. External WSLS is a declared benchmark, never a Native candidate policy.'}
    with proof_path.open('x', encoding='utf8') as out: json.dump(result, out, ensure_ascii=False, indent=2); out.write('\n')
    if closed and marker.exists(): marker.unlink()
    print(json.dumps({'status': result['status'], 'closed': closed, 'error': error, 'proof': str(proof_path),
                      'sha256': sha(proof_path), 'joint_useful': result['joint_useful'], 'opportunities': len(records)}, ensure_ascii=False))
    if error: raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--sistema', required=True)
    parser.add_argument('--brazo', choices=('real', 'none', 'yoked', 'reference'), required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--plan-yoke')
    parser.add_argument('--registro-global', action='store_true')
    parser.add_argument('--ejecutar', action='store_true')
    main(parser.parse_args())
