"""Root-only historical panel or two explicitly consumed old C2C offers.

Input order, readers, actual integer binding and929receipts come literally
from the existing recipe. No Native operation occurs on import or --dry-run.
Every partial/negative material result is preserved before coherent closing.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import os
import re
import sys

P = Path(__file__).resolve().parents[1]
C = P.parents[2] / 'DEE Cognitive 2.0'
S = P / 'estados/candidato/sistema'
MAIN = 'ECI02_PI03_REPRO_PI04_PI05_MAIN_01'
MAIN_SNAPSHOT_SHA = 'af74c8f47e43ed3b2395a338a23a6cbd42f105ec2cff4daac15b7a4d45e90832'
PLAN = P / 'control/PLAN_PANEL_INTERCALADO_PI07_R01.json'
PLAN_SHA = '43b241d36dd0f05eb42779b42c5cd20345378a9092e495f3fbafdd4ed49a63df'
RECIPE = C / 'reproducibilidad/recetas/panel_12.json'
RECIPE_SHA = '8efe577083013eac0cbfe5bc1ac661e7f7265f52f01de380492bb976c417d9fe'
STATE = {'modo': 'eci01-pi07-r03-estado'}
WORD_BOUND = 512
FI_ARITHMETIC_BOUND = 600
C2C_BOUND = 1500


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def get(value, path):
    for key in path:
        value = value[key]
    return value


def require(condition, message):
    if not condition:
        raise ValueError(message)


def receipt_set(items, before, after):
    unique = {}
    aliases = 0
    for item in items:
        rid = item['id']
        receipt = item.get('receipt', item)
        require(type(rid) is int and receipt['id'] == rid, 'Direct receipt identity mismatch')
        require(before <= receipt['requested_tick'] <= after, 'Old receipt outside this material call')
        if rid in unique:
            require(unique[rid] == receipt, 'Contradictory receipt alias')
            aliases += 1
        unique[rid] = receipt
    return unique, aliases


def counts(receipts):
    return {'unique_requested': len(receipts),
            'applied': sum(r['status'] == 'applied' for r in receipts.values()),
            'rejected_or_other': sum(r['status'] != 'applied' for r in receipts.values())}


def bound(spec):
    if spec.get('require_zero_ticks'):
        return 0
    return (FI_ARITHMETIC_BOUND if spec['literal']['modo'] in
            ('eci01-balance', 'eci01-aritmetica-directa') else WORD_BOUND)


def main(args):
    require(re.fullmatch(r'ECI02_PI03_REPRO_PI04_PI05_PI07_[A-Za-z0-9_]{1,24}', args.vida),
            'Explicit existing PI07 diagnostic only')
    require(re.fullmatch(r'PI07_[A-Za-z0-9_]{1,40}', args.tag), 'Fresh bounded PI07 tag required')
    require(sha(PLAN) == PLAN_SHA and sha(RECIPE) == RECIPE_SHA, 'Historical plan/recipe changed')
    plan, recipe = read(PLAN), read(RECIPE)
    variant = recipe['variants']['principal']
    panel = [spec for batch in variant['batches'] for spec in batch]
    require(plan['phases']['panel12'] == panel, 'Literal historical panel differs')
    require(variant['native_receipt_expectations'] ==
            {'unique_requested': 929, 'applied': 929, 'rejected': 0}, 'Historical denominator changed')
    total_bound = sum(bound(spec) for spec in panel) if args.fase == 'panel12' else 2*C2C_BOUND
    if args.dry_run:
        print(json.dumps({'Native_executed': False, 'new_ticks': 0,
                          'phase': args.fase, 'plan_sha256': PLAN_SHA,
                          'recipe_sha256': RECIPE_SHA, 'max_native_ticks': total_bound,
                          'per_word_memory_bound': WORD_BOUND,
                          'per_FI_arithmetic_bound': FI_ARITHMETIC_BOUND,
                          'per_C2C_bound': C2C_BOUND,
                          'scope': 'Conservative finite bounds: PI05 actual words15..70ticks; actualFI/arithmetic198 plus at most391calendar wait. C2C1500 retains the official bound and covers PI06actual1031. No future response implied.'}, ensure_ascii=False))
        return 0
    driver_path = Path(__file__).with_name('ejecutar_plan_PI07_R01.py')
    module_spec = importlib.util.spec_from_file_location('PI07_passive_budget_guard', driver_path)
    driver = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(driver)
    campaign = read(P / 'REGISTRO_CAMPANA.json')
    ticks, lives = driver.ledger()
    require(ticks+total_bound <= campaign['budget']['Native_ticks_all_branches'], 'Native100000budget insufficient')
    require(len(lives) <= campaign['budget']['diagnostic_worlds'], 'Diagnostic14world budget exceeded')
    cutoff = datetime.fromisoformat(campaign['science_cutoff_local']).astimezone(timezone.utc)
    require(datetime.now(timezone.utc) < cutoff, 'Scientific cutoff reached')
    require(not (S / 'estado/ACTIVO.json').exists(), 'Diagnostic store must not select a principal')
    require(not (C / 'reproducibilidad/EJECUCION_MATERIAL.lock').exists(), 'Another RP material writer is active')
    locks = S / 'estado/locks'
    require(not locks.exists() or not any(locks.iterdir()), 'A scoped owner/lock remains; inspect without replacement')
    card_path = S / 'estado/vidas' / args.vida / 'VIDA.json'
    driver.regular(card_path)
    card = read(card_path)
    require(card['physical']['N'] == 67 and card['physical']['tick'] == args.tick_inicial,
            'Exact preregistered candidate cut required')
    require(not (card_path.parent / 'FUTURO_INTERRUMPIDO.json').exists(), 'Interrupted future preserved')
    active_path = C / 'sistema/estado/ACTIVO.json'
    source_card = C / 'sistema/estado/vidas' / MAIN / 'VIDA.json'
    original = read(source_card)
    require(read(active_path)['life_id'] == MAIN and original['physical']['tick'] == 824911
            and original['snapshot_sha256'] == MAIN_SNAPSHOT_SHA, 'Protected principal changed; do not overwrite its continuation')
    critical = [active_path, source_card, C / 'sistema' / original['snapshot']]
    protected = {str(path): sha(path) for path in critical}
    output = P / 'control' / (args.tag + '.json')
    marker = P / 'PI07_ROOT_NATIVE_WRITER.lock'
    require(not output.exists() and not marker.exists(), 'No overwritten proof/tag or second Native writer')
    with marker.open('x', encoding='utf-8') as stream:
        json.dump({'pid': os.getpid(), 'life': args.vida, 'phase': args.fase,
                   'plan_sha256': PLAN_SHA}, stream)
    rows, direct = [], {}
    numbers = {}
    owner = None
    error = None
    stop = None
    state_before = state_after = None
    try:
        sys.path.insert(0, str(P / 'codigo'))
        from servicio_ensayo_PI07 import Owner
        owner = Owner(args.vida, args.tag)
        with owner:
            state_before = owner.material(args.tag+'_R03_pre', STATE, feedback='omit', allow_failure=True)
            require(state_before.get('before_tick') == state_before.get('after_tick') == args.tick_inicial,
                    'R03 administrative precondition advanced or failed')
            progress = state_before['result']['rows'][0]['progress']
            require(progress['ordinal'] == 12 and not progress.get('pending') and not progress.get('uncertain'),
                    'Intercalation is fixed after R03ordinal11, before restore12/13')
            if args.fase == 'panel12':
                specs = panel
            else:
                check = owner.material(args.tag+'_C2C_pre', {'modo': 'eci01-pi04-c2c-estado'}, feedback='omit', allow_failure=True)
                require(check.get('before_tick') == check.get('after_tick'), 'C2C state must advance0ticks')
                state = check['result']['rows'][0]
                require(state['progress']['ordinal'] == state['device']['ordinal'] == 28
                        and len(state['device']['resources']) == 30
                        and not any(state['device'].get(k) for k in ('pending', 'feedback_pending', 'uncertain')),
                        'Only the two real pre-existing offers28/29; no reset/refill')
                specs = [{'label': 'C2C28', **plan['phases']['old_C2C_next']},
                         {'label': 'C2C29', **plan['phases']['old_C2C_next']}]
                for i, spec in enumerate(specs):
                    spec['label'] = 'C2C' + str(28+i)
            for spec in specs:
                require(datetime.now(timezone.utc) < cutoff, 'Scientific cutoff between material uses')
                literal = dict(spec['literal'])
                if 'actual_integer_binding' in spec:
                    binding = spec['actual_integer_binding']
                    actual = numbers[binding['from_step']]
                    require(type(actual) is int, 'Actual prior Native integer absent; never substitute expected13')
                    literal[binding['field']] = actual
                identifier = args.tag+'_'+spec['label']
                value = owner.material(identifier, literal,
                                       feedback='real' if args.fase == 'c2c2' else 'omit',
                                       actuator='closed', allow_failure=True)
                primary = P / 'ensayos' / (identifier+'.json')
                record = {'label': spec['label'], 'literal': literal,
                          'primary': str(primary), 'primary_sha256': sha(primary),
                          'before_tick': value.get('before_tick'), 'after_tick': value.get('after_tick')}
                rows.append(record)  # preserve even missing/failed result
                require('before_tick' in value and 'after_tick' in value, 'No complete transport result; future preserved without retry')
                step_bound = bound(spec) if args.fase == 'panel12' else C2C_BOUND
                require(0 <= value['after_tick']-value['before_tick'] <= step_bound,
                        'Actual use exceeds its prospective finite bound')
                items = []
                if args.fase == 'panel12':
                    observed = get(value, spec['read_path']) if 'read_path' in spec else None
                    if 'read_path' in spec:
                        numbers[spec['label']] = observed
                    record.update(observed=observed, expected_evaluator_only=spec.get('expected'),
                                  correct=None if 'expected' not in spec else observed == spec['expected'])
                    for path in spec.get('receipt_paths', []):
                        items.extend(get(value, path))
                else:
                    actual_row = value['result']['rows'][0]
                    require(actual_row['ordinal'] == 28+len(rows)-1, 'C2C ordinal did not continue actual history')
                    items = actual_row['requests']
                    record.update(useful_product=actual_row['useful_product'],
                                  actual_numeric_result=actual_row['actual_numeric_result'],
                                  first_native_choice=actual_row['first_reader']['choice'],
                                  second_native_motor=actual_row['second_motor'],
                                  correct=actual_row['useful_product'] is True)
                    if actual_row['useful_product']:
                        product = actual_row['actual_effect']['product']
                        path = S/'estado/servicios_locales'/args.vida/'PI04_C2C_COORDINACION_R01/dispositivo'/product['path']
                        driver.regular(path)
                        data = path.read_bytes()
                        require(len(data) == product['bytes'] == 64 and sha(path) == product['sha256']
                                and type(actual_row['actual_numeric_result']) is int
                                and int.from_bytes(data[:2], 'little') == actual_row['actual_numeric_result'],
                                'Useful product is not the actual Native integer/real64bytes')
                        record['actual_product'] = {'path': str(path), 'bytes': 64, 'sha256': sha(path)}
                current, aliases = receipt_set(items, value['before_tick'], value['after_tick'])
                require(not set(direct).intersection(current), 'Prior receipt counted again as a new event')
                direct.update(current)
                record.update(Native_inputs=counts(current), aliases_not_new_events=aliases,
                              new_native_ticks=value['after_tick']-value['before_tick'], finite_bound=step_bound)
                print(json.dumps(record, ensure_ascii=False), flush=True)
                if record['correct'] is False or any(r['status'] != 'applied' for r in current.values()):
                    stop = {'kind': 'MATERIAL_REGRESSION_OR_ADMISSION_FAILURE', 'label': spec['label'],
                            'no_reteaching_or_retry': True}
                    break
            owner.control('guardar')
            state_after = owner.material(args.tag+'_R03_post', STATE, feedback='omit', allow_failure=True)
            require(state_after.get('before_tick') == state_after.get('after_tick'), 'Post-state must advance0ticks')
            require(state_after['result']['rows'][0]['progress']['ordinal'] == 12,
                    'Historical use reset or consumed the separate R03 environment')
    except Exception as exc:
        error = {'type': type(exc).__name__, 'message': str(exc), 'automatic_retry': False}
    closed = bool(owner and owner.proc is not None and owner.proc.poll() == 0
                  and not (owner.q.get_meta('owner') or {}).get('running'))
    after = read(card_path)
    protected_after = {str(path): sha(path) for path in critical}
    if protected_after != protected:
        error = {'type': 'PROTECTED_PRINCIPAL_CHANGED', 'automatic_retry': False}
    expected_uses = 12 if args.fase == 'panel12' else 2
    correct = sum(row.get('correct') is True for row in rows)
    total = counts(direct)
    passed = (closed and error is None and stop is None and correct == expected_uses
              and total['rejected_or_other'] == 0)
    if args.fase == 'panel12':
        passed = passed and total['unique_requested'] == total['applied'] == 929
    else:
        passed = passed and total['unique_requested'] == total['applied'] == 372
    proof = {'schema': 'DEE.PI07.intercalated_heritage.actual.R01', 'phase': args.fase,
             'life_id': args.vida, 'status': 'COMPLETED_PHASE' if passed else 'STOPPED_PRESERVED',
             'closed': closed, 'criteria_met': passed, 'error': error, 'scientific_stop': stop,
             'plan': str(PLAN), 'plan_sha256': PLAN_SHA, 'recipe': str(RECIPE), 'recipe_sha256': RECIPE_SHA,
             'before_tick': card['physical']['tick'], 'after_tick': after['physical']['tick'],
             'new_Native_ticks': after['physical']['tick']-card['physical']['tick'],
             'correct': correct, 'tested': sum(row.get('correct') is not None for row in rows),
             'expected_uses': expected_uses, 'Native_inputs': total, 'rows': rows,
             'R03_state_before': state_before, 'R03_state_after': state_after,
             'closed_card': after, 'Native_budget_before': ticks, 'finite_phase_bound': total_bound,
             'protected_main_before': protected, 'protected_main_after': protected_after,
             'principal_modified': protected_after != protected,
             'no_promotion_no_supply_no_reteaching': True,
             'scope': 'Prepared historical12uses or exactlytwo consumed old C2C offers, not12faculties or discovered planning. Actual prior integer only; negative and partial results preserved.'}
    with output.open('x', encoding='utf-8') as stream:
        json.dump(proof, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    if closed:
        require(read(marker)['pid'] == os.getpid(), 'Writer marker identity changed')
        marker.unlink()
    print(json.dumps({'proof': str(output), 'sha256': sha(output), 'status': proof['status'],
                      'closed': closed, 'correct': correct, 'Native_inputs': total}, ensure_ascii=False))
    return 0 if passed else 2


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vida', required=True)
    parser.add_argument('--fase', choices=['panel12', 'c2c2'], required=True)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--tick-inicial', type=int, required=True)
    parser.add_argument('--dry-run', action='store_true')
    raise SystemExit(main(parser.parse_args()))
