"""Read-only R17 arithmetic evidence; standard library, no Runtime or replay.

The evaluator computes expected totals only after reading archived native
observations. This file is never imported by the participant/actor module.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path


def walk(value):
    if isinstance(value, dict):
        if value.get('kind') == 'native_joint_raw_perception':
            yield value
        for key, item in value.items():
            if key in ('stdout', 'result') and isinstance(item, str) and item.lstrip().startswith('{'):
                try:
                    yield from walk(json.loads(item))
                except json.JSONDecodeError:
                    pass
            else:
                yield from walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def calculate(source):
    encoded = source.read_bytes()
    rows = json.loads(gzip.decompress(encoded))
    cases, issues, seen = [], [], set()
    for row in rows:
        identity = str(row.get('id', ''))
        if not identity.startswith('fi60r3_'):
            continue
        for trial in walk(row):
            if identity in seen:
                continue
            seen.add(identity)
            when = trial['datum_tick'] - 2
            frames = [f for f in trial['frames'] if f['tick'] == when]
            gate = frames[0]['fields']['C'] if len(frames) == 1 else None
            scalar = None
            valid = False
            if gate:
                raw = int(gate['raw'])
                direction = [((raw >> shift) & 15) - (16 if ((raw >> shift) & 15) >= 8 else 0)
                             for shift in (48, 52, 56)]
                scalar = (raw >> 32) & 65535
                valid = (0 <= raw < 2**64 and bool(raw & 0xffffffff)
                         and ((raw >> 60) & 15) == 1
                         and direction == [1, -1, -1]
                         and gate['site'] == [12, 17, 18] and gate['tick'] == when)
            expected = sum(trial['raw_components'])  # Offline scoring only.
            exact = bool(valid and scalar == expected)
            if not exact:
                issues.append(identity)
            cases.append({'id': identity, 'input_tick': trial['input_tick'],
                          'datum_tick': trial['datum_tick'], 'read_tick': when,
                          'nonzero': [{'index': i, 'value': v}
                                      for i, v in enumerate(trial['raw_components']) if v],
                          'fixed_gate': gate, 'decoded_native_scalar': scalar,
                          'offline_expected_total': expected, 'matches': exact})
    return {'schema': 'APD01.prior_R17_numeric_gate_recalculation.v1',
            'native_ticks': 0, 'source_file': source.name,
            'source_sha256': hashlib.sha256(encoded).hexdigest(),
            'cases': cases, 'requested_cases': len(cases),
            'exact_numeric_gates': sum(case['matches'] for case in cases),
            'issues': issues,
            'scope': 'Retrospective existing sparse19/21 payloads only, not new pair '
                     'operation reservations, acquired arithmetic, or general internalization. '
                     'No archived answer is supplied to a new native run.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--registro', type=Path, required=True)
    parser.add_argument('--salida', type=Path, required=True)
    args = parser.parse_args()
    if args.salida.exists():
        raise FileExistsError('Preserve previous calculations')
    result = calculate(args.registro)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'cases': result['requested_cases'], 'exact_numeric_gates': result['exact_numeric_gates'],
                      'issues': result['issues'], 'native_ticks': 0}))
    raise SystemExit(bool(result['issues']))
