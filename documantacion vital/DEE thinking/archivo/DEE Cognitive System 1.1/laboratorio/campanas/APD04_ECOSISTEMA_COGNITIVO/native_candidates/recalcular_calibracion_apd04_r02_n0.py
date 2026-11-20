"""Recalculate calibration directly from exact primary RAW/receipts, no DEE."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
LIFE = 'APD04_CALIB_R02'
IDENTIFIER = 'ui_m_39cb78fdbfe4496881a39c66c5177921'
SOURCE = ROOT / 'sistema/estado/servicios_persistentes' / LIFE / 'resultados' / (IDENTIFIER + '.json')
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/CALIBRACION_R02/RECALCULO_DESDE_RAW.json'


def direction(raw):
    result = []
    for shift in (48, 52, 56):
        value = (raw >> shift) & 15
        result.append(value - 16 if value >= 8 else value)
    return result


def read_choices(observations):
    found = []
    for row in observations:
        raw = int(row['raw'])
        if raw & 0xffffffff and ((raw >> 60) & 15) == 1:
            vector = direction(raw)
            if vector[0] in (-1, 0, 1) and vector[1] == 1 and vector[2] in (0, -1):
                expected_site = [(15 + 2*vector[0]) % 67, 17,
                                 (15 + 2*vector[2]) % 67]
                if row['site'] == expected_site:
                    found.append(vector[0])
    return found[0] if len(found) == 1 else None, found


def main():
    encoded = SOURCE.read_bytes()
    report = json.loads(encoded)
    rows = report['result']['rows'][0]['rows']
    cases = []
    checks = []
    for index, row in enumerate(rows):
        trial = row['native_trial']
        read, candidates = read_choices(trial['reader']['observations'])
        valid = read == row['physical_choice'] == trial['reader']['choice']
        checks.append(valid)
        requests = trial['requests']
        statuses = [item['receipt']['status'] for item in requests]
        primary = {'index': index, 'kind': row['kind'],
            'input': trial.get('raw_sensor_value', row.get('public_independent_loads')),
            'requested': len(requests), 'applied': statuses.count('applied'),
            'rejected': statuses.count('rejected'),
            'other_statuses': sorted(set(statuses) - {'applied', 'rejected'}),
            'read_tick': trial['read_tick'], 'choice_from_RAW': read,
            'candidates_from_RAW': candidates,
            'stored_reader_agrees': valid,
            'active_zero_observed': read == 0,
            'all_six_read_gates_RAW0': all(int(x['raw']) == 0 for x in trial['reader']['observations'])}
        if trial['kind'] == 'native_joint_raw_perception':
            components = trial['raw_components']
            fixed_frame = next(x for x in trial['frames'] if x['tick'] == trial['datum_tick'] - 2)
            raw = int(fixed_frame['fields']['C']['raw'])
            aggregate = (raw >> 32) & 65535
            primary.update(aggregate_from_RAW=aggregate,
                independent_components=components[:2],
                zero_padding_components=len(components) - 2,
                native_aggregate_agrees_with_auditor_sum=aggregate == sum(components))
            checks.append(aggregate == sum(components))
        cases.append(primary)
    result = {'schema': 'APD04.calibration.recalculation.v1',
        'source_file': str(SOURCE.relative_to(ROOT)).replace('\\', '/'),
        'source_sha256': hashlib.sha256(encoded).hexdigest(),
        'source_bytes': len(encoded), 'native_ticks_generated_by_recalculation': 0,
        'life': LIFE, 'cases': cases,
        'total_requested': sum(row['requested'] for row in cases),
        'total_applied': sum(row['applied'] for row in cases),
        'total_rejected': sum(row['rejected'] for row in cases),
        'checks': len(checks), 'discrepancies': checks.count(False),
        'conclusion_scope': 'Four nonzero directions and two absent outputs. '
            'Absence is not decoded as active zero, equality, learned WAIT or intelligent abstention. '
            'These six cases calibrate inherited native affordances, not learned Spanish or autonomous policy.'}
    if OUT.exists():
        previous = json.loads(OUT.read_text(encoding='utf8'))
        if previous != result:
            raise ValueError('Existing recalculation differs; preserve it and identify another revision')
    else:
        with OUT.open('x', encoding='utf8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
