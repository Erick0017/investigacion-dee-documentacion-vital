"""Archived RAW/receipt recalculation of both sensory AUX, no Native imports."""
from pathlib import Path
import argparse
import hashlib
import json

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/SENSORES_Y_LEXICO_R01/RECALCULO_SENSORES.json'


def vector(raw):
    return [((raw >> shift) & 15) - (16 if ((raw >> shift) & 15) >= 8 else 0)
            for shift in (48, 52, 56)]


def decode(observations, zs):
    candidates = []
    for row in observations:
        raw = int(row['raw'])
        v = vector(raw)
        if raw & 0xffffffff and (raw >> 60) & 15 == 1:
            if v[0] in (-1, 0, 1) and v[1] == 1 and v[2] in zs:
                expected = [(25 + 2*v[0]) % 67, 15, (53 + 2*v[2]) % 67]
                if row['site'] == expected:
                    candidates.append({'x': v[0], 'z': v[2], 'site': row['site'],
                        'raw': row['raw'], 'clock': row['clock'],
                        'payload_from_RAW': (raw >> 32) & 65535})
    return candidates


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=Path, help='Portable evidence index; no system/runtime required')
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    portable = json.loads(args.index.read_text(encoding='utf8')) if args.index else None
    output = args.out or (args.index.parent / 'RECALCULO_SENSORES.json' if args.index else OUT)
    families = []
    discrepancies = []
    for family in ('R02', 'R03'):
        life = 'APD04_SENSOR_' + family + '_AUX'
        record = (portable['families'][family]['record'] if portable else
            json.loads((ROOT / 'sistema/estado/vidas' / life / 'VIDA.json').read_text(encoding='utf8')))
        operations = [row for row in record['operations'] if row['kind'] == 'PERSISTENT_SESION']
        if len(operations) != 2:
            raise ValueError('Both declared four-pair batches must be committed before recalculation')
        results = []
        sources = []
        for block, operation in enumerate(operations):
            source = (args.index.parent / operation['result_file'] if portable else
                ROOT / 'sistema/estado/servicios_persistentes' / life / operation['result_file'])
            encoded = source.read_bytes()
            digest = hashlib.sha256(encoded).hexdigest()
            if digest != operation['result_sha256']:
                raise ValueError('Primary bytes differ from the committed operational index')
            primary = json.loads(encoded)
            rows = primary['result']['rows'][0]['rows']
            sources.append({'file': (source.relative_to(args.index.parent).as_posix() if portable else source.relative_to(ROOT).as_posix()),
                'sha256': digest, 'bytes': len(encoded), 'block': block})
            for order, row in enumerate(rows):
                selection = row['selection']
                candidates = decode(selection['reader']['observations'], (0,))
                choice = candidates[0]['x'] if len(candidates) == 1 else None
                if choice != selection['physical_choice']:
                    discrepancies.append([family, block, order, 'historical action decoder'])
                diagnostic = row['auditor_only_gates9']['observations']
                candidates9 = decode(diagnostic, (-1, 0, 1))
                receipts = {}
                for item in walk(row):
                    if 'id' in item and 'port' in item and isinstance(item.get('receipt'), dict):
                        receipt = item['receipt']
                        previous = receipts.get(int(item['id']))
                        if previous and previous['port'] != item['port']:
                            discrepancies.append([family, block, order, 'request ID has two ports'])
                        if previous and receipt['status'] in ('scheduled', 'queued'):
                            continue
                        receipts[int(item['id'])] = item
                statuses = [item['receipt']['status'] for item in receipts.values()]
                results.append({'block': block, 'order': order,
                    'raw_components': row['raw_components'],
                    'query_tick': selection['query_tick'], 'read_tick': selection['reader']['tick'],
                    'physical_choice_from_RAW3': choice, 'stored_choice': selection['physical_choice'],
                    'payloads_from_RAW3': [item['payload_from_RAW'] for item in candidates],
                    'active_zero_observed': choice == 0,
                    'auditor_coherent_RAW9': candidates9,
                    'diagnostic_all9_RAW0': all(int(x['raw']) == 0 for x in diagnostic),
                    'requested_unique': len(receipts), 'applied': statuses.count('applied'),
                    'rejected': statuses.count('rejected'),
                    'other_statuses': sorted(set(statuses) - {'applied', 'rejected'}),
                    'query_payload': next(item['payload'] for item in receipts.values()
                        if item['port'].endswith('.query')),
                    'return_category': row['return']['category'], 'return_mode': row['return']['mode']})
        families.append({'family': family, 'life': life,
            'parent_snapshot_sha256': record['parent']['encoded_sha256'],
            'final_tick': record['physical']['tick'], 'snapshot_sha256': record['snapshot_sha256'],
            'sources': sources, 'rows': results,
            'valid_historical_outputs': sum(row['physical_choice_from_RAW3'] is not None for row in results),
            'opportunities': len(results),
            'requested_unique': sum(row['requested_unique'] for row in results),
            'applied': sum(row['applied'] for row in results),
            'rejected': sum(row['rejected'] for row in results)})
    result = {'schema': 'APD04.sensor_recalculation.v1', 'families': families,
        'discrepancies': discrepancies, 'new_native_ticks': 0,
        'scope': 'Two eight-use branches share one complete inherited prefix, not independent learners. '
                 'The inverse order follows earlier material history. No task-quality feedback occurred. '
                 'The nine-site panel is auditor-only and never replaces historical decisions. '
                 'Response availability or changed encoding does not establish learned attention/context semantics.'}
    if output.exists():
        if json.loads(output.read_text(encoding='utf8')) != result:
            raise ValueError('Do not overwrite a different recalculation')
    else:
        with output.open('x', encoding='utf8') as stream:
            json.dump(result, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
