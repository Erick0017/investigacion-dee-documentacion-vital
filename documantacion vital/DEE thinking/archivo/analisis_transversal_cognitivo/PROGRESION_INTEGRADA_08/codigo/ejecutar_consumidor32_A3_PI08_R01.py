"""Root-only single actual32-device use after the0tick transaction/reopening."""
from pathlib import Path
from datetime import datetime, timezone
from collections import Counter
import argparse, importlib.util, json, os, re

P = Path(__file__).resolve().parents[1]
PLAN = P / 'control/PROTOCOLO_CONSUMIDOR32_A3_PI08_R01.json'


def main(args):
    spec = importlib.util.spec_from_file_location('PI08_A2_readonly_helpers', P / 'codigo/ejecutar_consolidacion_A2_PI08_R02.py')
    a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
    plan_bytes = PLAN.read_bytes(); plan = json.loads(plan_bytes)
    a.require(plan['schema'] == 'DEE.PI08.A3.single32consumer.protocol.R01'
              and plan['status'] == 'SEALED_BEFORE_NEW_32_MATERIAL_USE', 'Prospective A3 plan required')
    a.require(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_[A-Za-z0-9_]{1,40}', args.vida), 'Explicit PI08 successor only')
    a.require(re.fullmatch(r'PI08_[A-Za-z0-9_]{1,45}', args.tag), 'Fresh bounded tag required')
    if args.dry_run:
        print(json.dumps({'Native_executed': False, 'new_ticks': 0, 'finite_bound': 1500,
                          'plan_sha256': a.sha(PLAN), 'expected_answer_supplied': False})); return 0
    campaign = a.read(P / 'REGISTRO_CAMPANA.json')
    used, lives = a.ledger()
    a.require(used + 1500 <= campaign['budget']['Native_ticks_all_branches']
              and len(lives) <= campaign['budget']['diagnostic_worlds_all_new'], 'Fixed PI08 budget insufficient')
    cutoff = datetime.fromisoformat(campaign['budget']['new_experimental_uses_cutoff_local']).astimezone(timezone.utc)
    a.require(datetime.now(timezone.utc) < cutoff, 'Science deadline reached')
    card_path = a.regular(a.S / 'estado/vidas' / args.vida / 'VIDA.json'); before_card = a.read(card_path)
    a.require(before_card['physical']['N'] == 67 and before_card['physical']['tick'] == args.tick_inicial,
              'Actual complete current cut differs')
    a.require(not (a.S / 'estado/ACTIVO.json').exists(), 'Unselected successor only before A adoption')
    locks = a.S / 'estado/locks'
    a.require(not locks.exists() or not any(locks.iterdir()), 'Scoped Native owner remains')
    a.require(not (a.RP / 'EJECUCION_MATERIAL.lock').exists(), 'Another material RP owner remains')
    active = a.C / 'sistema/estado/ACTIVO.json'; main_card = a.C / 'sistema/estado/vidas' / a.MAIN / 'VIDA.json'
    principal = a.read(main_card)
    a.require(a.read(active)['life_id'] == a.MAIN and principal['physical']['tick'] == 824911
              and principal['snapshot_sha256'] == a.MAIN_SHA, 'The protected principal advanced')
    protected_paths = [active, main_card, a.C / 'sistema' / principal['snapshot']]
    protected = {str(path): a.sha(path) for path in protected_paths}
    proof_path = P / 'control' / (args.tag + '.json'); marker = P / 'PI08_ROOT_NATIVE_WRITER.lock'
    a.require(not proof_path.exists() and not marker.exists(), 'Existing tag/proof or writer; no repeated use')
    with marker.open('x', encoding='utf-8') as stream:
        json.dump({'pid': os.getpid(), 'life_id': args.vida, 'phase': 'A3', 'plan_sha256': a.sha(PLAN)}, stream)
    supervisor = a.load('PI08_A3_owned_process', a.RP / 'propietario_diagnostico.py')
    supervisor.configure(P, a.S, a.PY)
    owner = None; rows = []; intents = []; error = None; functional = None; direct = {}; states = {}

    def call(label, literal, limit=0):
        a.require(datetime.now(timezone.utc) < cutoff, 'Science deadline before material use')
        identifier = args.tag + '_' + label; intents.append({'id': identifier, 'literal': literal})
        value = owner.material(identifier, literal, feedback='real', actuator='closed', allow_failure=True)
        file = P / 'ensayos' / (identifier + '.json')
        a.require('before_tick' in value and 'after_tick' in value, 'Uncertain transport result, preserve SAME id')
        a.require(0 <= value['after_tick'] - value['before_tick'] <= limit, 'Prospective finite bound exceeded')
        rows.append({'label': label, 'primary': str(file), 'sha256': a.sha(file),
                     'before_tick': value['before_tick'], 'after_tick': value['after_tick']})
        a.require(PLAN.read_bytes() == plan_bytes, 'A3 plan changed during execution')
        return a.first_row(value)

    def states_at(label, ordinal):
        transaction = call('A1state_' + label, {'modo': 'eci01-pi08-c2c-estado'})
        a.require(transaction['present'] and transaction['state']['phase'] == 'COMMITTED'
                  and transaction['state']['ready'] and not transaction['state']['uncertain'], '32 transaction not coherently committed')
        c2 = call('C2Cstate_' + label, a.C2STATE); r3 = call('R03state_' + label, a.R3STATE)
        a.require(c2['progress']['ordinal'] == c2['device']['ordinal'] == ordinal
                  and len(c2['device']['resources']) == 32, 'Effective32 consumer counter/resources mismatch')
        a.require(r3['progress']['ordinal'] == 6 and not r3['progress'].get('pending')
                  and not r3['progress'].get('uncertain'), 'A3 must not consume/reset a R03 opportunity')
        a.require(not any(c2['device'].get(k) for k in ('pending', 'feedback_pending', 'uncertain')), 'Pending/uncertain32 device')
        states[label] = {'transaction': transaction, 'C2C': c2, 'R03': r3}

    try:
        owner = supervisor.Owner(args.vida, args.tag)
        with owner:
            states_at('pre', 30)
            result = call('C2C30', {'modo': 'eci01-pi04-c2c-oportunidad'}, 1500)
            a.require(result['ordinal'] == 30, 'Another resource/opportunity was consumed')
            direct, aliases, groups = a.c2c_inputs(result)
            counts = Counter(receipt['status'] for receipt in direct.values())
            a.require(all(key == 'applied' or key.startswith('rejected') for key in counts), 'Unknown/pending material receipt')
            functional = {'actual_numeric_result': result['actual_numeric_result'],
                'first_Native_choice': result['first_reader']['choice'], 'selected_operation': result['selected_operation'],
                'second_motor': result['second_motor'], 'useful_product': result['useful_product'],
                'actual_failed': result['actual_failed'], 'Native_inputs': {'unique_requested': len(direct), 'status_counts': dict(counts)},
                'group_counts': groups, 'aliases_not_new_events': aliases,
                'not_expected_31_or23_fed': True}
            if result['useful_product']:
                product = result['actual_effect']['product']
                a.require(product['path'] == 'products/0030.bin', 'Unexpected unbounded artifact path')
                home = a.S / 'estado/servicios_locales' / args.vida / 'PI08_C2C_INTEGRACION_R01/dispositivo32'
                file = a.regular(home / product['path']); data = file.read_bytes()
                a.require(len(data) == product['bytes'] == 64 and a.sha(file) == product['sha256']
                          and type(result['actual_numeric_result']) is int
                          and int.from_bytes(data[:2], 'little') == result['actual_numeric_result'],
                          'Actual32 product must carry the real Native result')
                functional['actual_product'] = {'path': str(file), 'bytes': 64, 'sha256': a.sha(file)}
            states_at('post', 31)
            owner.control('guardar')
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'automatic_retry': False}
    closed = bool(owner and owner.proc is not None and owner.proc.poll() == 0
                  and not (owner.q.get_meta('owner') or {}).get('running'))
    after = a.read(card_path); protected_after = {str(path): a.sha(path) for path in protected_paths}
    if protected_after != protected: error = {'type': 'PROTECTED_PRINCIPAL_CHANGED', 'automatic_retry': False}
    criteria = bool(closed and error is None and functional and functional['useful_product'])
    proof = {'schema': 'DEE.PI08.A3.actual32consumer.R01', 'at_utc': datetime.now(timezone.utc).isoformat(),
        'life_id': args.vida, 'status': 'CLOSED_MATERIAL_USE' if closed and error is None else 'FAILED_PRESERVED',
        'closed': closed, 'criteria_met': criteria, 'error': error,
        'initial_tick': before_card['physical']['tick'], 'final_tick': after['physical']['tick'],
        'new_Native_ticks': after['physical']['tick'] - before_card['physical']['tick'], 'finite_Native_bound': 1500,
        'plan': str(PLAN), 'plan_sha256': a.sha(PLAN), 'rows': rows, 'intents': intents, 'states': states,
        'functional': functional, 'known_numeric_or_terminal_rejection_is_not_transport_uncertainty': True,
        'remaining_C2C_resources_if_completed': 1 if 'post' in states else None,
        'protected_before': protected, 'protected_after': protected_after, 'no_adoption_or_reset': True}
    with proof_path.open('x', encoding='utf-8') as stream: json.dump(proof, stream, ensure_ascii=False, indent=2); stream.write('\n')
    if closed:
        a.require(a.read(marker)['pid'] == os.getpid(), 'Writer marker changed'); marker.unlink()
    print(json.dumps({'proof': str(proof_path), 'sha256': a.sha(proof_path), 'closed': closed,
                      'criteria_met': criteria, 'final_tick': after['physical']['tick'], 'error': error}, ensure_ascii=False))
    return 0 if closed and error is None else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--vida', required=True)
    parser.add_argument('--tag', required=True); parser.add_argument('--tick-inicial', required=True, type=int)
    parser.add_argument('--dry-run', action='store_true'); raise SystemExit(main(parser.parse_args()))
