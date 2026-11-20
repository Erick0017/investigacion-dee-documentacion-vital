"""Passive ordered source outcomes for the pre-fixed +5 yoked control.

Requires closed Root phase summaries covering actual ordinals0..11 exactly.
Only documented primaries under PI07/ensayos are read. No Native, no actor.
"""
from pathlib import Path
from collections import Counter
import argparse
import hashlib
import importlib.util
import json

P = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pruebas', type=Path, nargs='+', required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    if args.salida.exists():
        raise FileExistsError(args.salida)
    module_path = Path(__file__).with_name('RECALCULAR_PRIMARIOS_PI07.py')
    spec = importlib.util.spec_from_file_location('PI07_documentary_decoder_only', module_path)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    rows = {}
    phases = []
    life = None
    for filename in args.pruebas:
        filename = filename.resolve(strict=True)
        if not filename.is_relative_to((P / 'control').resolve()):
            raise ValueError('Only explicit closed Root PI07 control proofs')
        proof = read(filename)
        if (proof.get('schema') != 'DEE.PI07.finite_owned_execution.R01'
                or proof.get('status') != 'CLOSED' or proof.get('closed') is not True
                or proof.get('full_plan_completed') is not True
                or proof.get('protected_main_unchanged') is not True
                or proof.get('error') is not None):
            raise ValueError('A complete closed protected Root execution is required')
        if life is None:
            life = proof['life_id']
        elif life != proof['life_id']:
            raise ValueError('Source twelve must belong to one actual continuing life')
        phases.append({'file': str(filename), 'sha256': sha(filename),
                       'initial_tick': proof['initial_tick'], 'final_tick': proof['final_tick'],
                       'new_ticks': proof['new_ticks']})
        for item in proof['outcomes']:
            # Source references never select an arbitrary input file.
            basename = Path(item['primary']).name
            primary_path = P / 'ensayos' / basename
            if sha(primary_path) != item['primary_sha256']:
                raise ValueError('Published primary differs from its closed Root proof')
            primary = read(primary_path)
            _, material_rows = decoder.decoded_result(primary)
            for row in material_rows:
                if 'actual_failed' not in row or 'FI' not in row:
                    continue  # zero-tick initialization, never an opportunity
                ordinal = row['ordinal']
                if ordinal not in range(12) or ordinal in rows:
                    raise ValueError('Exactly one real source for each ordinal0..11')
                if (row['life_id'] != life or row['feedback_arm'] != 'real'
                        or row['operator_forced_action'] is not None
                        or row.get('sensor_ablation') or row.get('actuator_ablation')):
                    raise ValueError('Only real unforced intact source experiences')
                fi = row['FI']
                old = decoder.late_FI_choice(fi['legacy_result']['original_result']['native_trial']['reader'])
                early = decoder.early_choice(fi['legacy_result']['early_observation'])
                if old != fi['old_q6_choice'] or early != fi['early_physical_choice']:
                    raise ValueError('Source physical FI decode mismatch')
                message = row['message']
                physical = decoder.observation(message['observation'])
                required = row['environment_spec']['message_payload']
                delivered = (required is not None
                             and decoder.request_status(message['request']) == 'applied'
                             and physical['state'] > 0 and physical['semantic'] == 1
                             and physical['direction'] == [1, 0, 0]
                             and physical['s_reg'] == required)
                failed = old != 1 or (required is not None and not delivered)
                if row['actual_failed'] is not failed or row['returned_failed'] is not failed:
                    raise ValueError('Source real return differs from actual physical effect')
                direct, aliases = decoder.receipts(row['requests'])
                if any(receipt['status'] != 'applied' and not receipt['status'].startswith('rejected')
                       for receipt in direct.values()):
                    raise ValueError('Unknown/pending source outcome must not be replayed')
                rows[ordinal] = {'ordinal': ordinal, 'actual_failed': failed,
                                  'query_tick': row['calendar']['query_tick'],
                                  'before_tick': row['before_tick'], 'after_tick': row['after_tick'],
                                  'FI_q4': early, 'FI_q6': old, 'message_delivered': delivered,
                                  'selector': row['reader']['choice'],
                                  'source_primary': basename, 'primary_sha256': sha(primary_path),
                                  'direct_unique_requests': len(direct), 'duplicate_aliases': aliases}
    if set(rows) != set(range(12)):
        raise ValueError('Twelve closed source opportunities are not available yet')
    ordered = [rows[i] for i in range(12)]
    outcomes = [row['actual_failed'] for row in ordered]
    values = [outcomes[(i+5) % 12] for i in range(12)]
    if Counter(outcomes) != Counter(values):
        raise AssertionError('Fixed derangement must preserve boolean dose exactly')
    output = {'schema': 'DEE.PI07.actual_outcomes_for_yoke.v1',
              'status': 'CLOSED_REAL_SOURCE_EXTRACTED_DOCUMENTARILY',
              'life_id': life, 'actual_failed': outcomes,
              'source_index_for_recipient': [(i+5) % 12 for i in range(12)],
              'roll_direction': 'source_plus_5', 'yoked_values': values,
              'phases': phases, 'opportunities': ordered, 'new_Native_ticks': 0,
              'scope': 'Evaluator-only fixed control source. These booleans must be read only by the generic-return control, never by the sensor, selector, actuator or a bank lookup.'}
    with args.salida.open('x', encoding='utf-8') as stream:
        json.dump(output, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'output': str(args.salida), 'sha256': sha(args.salida),
                      'actual_failed': outcomes, 'yoked_values': values,
                      'new_Native_ticks': 0}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
