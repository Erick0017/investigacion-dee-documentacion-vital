"""Recalculate the matched six-op A/C contrast from archived primaries only.

Stdlib-only. Does not import DEE, instantiate a Runtime or advance any life.
Usage: python THIS.py --evidence EVIDENCIA_PORTABLE_R02 --out NEW_RESULT.json
"""
from pathlib import Path
import argparse
import hashlib
import json


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
    parser.add_argument('--evidence', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    base = args.evidence.resolve()
    members = json.loads((base / 'MANIFIESTO_MIEMBROS_ORIGINALES.json').read_text(encoding='utf8'))
    expected = {item['exported']: item for item in members['members']}
    branches = {}
    for branch in ('A', 'C'):
        rows, inputs, sources, final = [], {}, [], None
        for block in ('2_goal0_first4', '3_goal0_next2'):
            relative = branch + '/PRIMARIOS/apd04_attention_' + branch + '_' + block + '.json'
            path = base / relative
            encoded = path.read_bytes()
            digest = hashlib.sha256(encoded).hexdigest()
            if digest != expected[relative]['sha256'] or len(encoded) != expected[relative]['bytes']:
                raise ValueError('Primary bytes fail the archived original-member manifest: ' + relative)
            primary = json.loads(encoded)
            sources.append({'file': relative, 'sha256': digest, 'bytes': len(encoded)})
            rows.extend(primary['result']['rows'][0]['rows'])
            final = primary['result']['final']['memory_contract']['INSTRUMENTO']['physical']
            for item in walk(primary['result']['rows'][0]):
                if 'id' in item and 'port' in item and isinstance(item.get('receipt'), dict):
                    identifier = int(item['id'])
                    if identifier in inputs and item['receipt']['status'] in ('scheduled', 'queued'):
                        continue
                    inputs[identifier] = item
        branches[branch] = {'sources': sources, 'rows': rows, 'inputs': inputs, 'final': final}
    a, c = branches['A'], branches['C']
    changes, status_changes = [], []
    for identifier in sorted(a['inputs'].keys() | c['inputs'].keys()):
        aa, cc = a['inputs'].get(identifier), c['inputs'].get(identifier)
        if not aa or not cc:
            changes.append({'id': identifier, 'only_A': aa, 'only_C': cc})
            continue
        spec_a = {key: aa[key] for key in ('port', 'payload', 'tick')}
        spec_c = {key: cc[key] for key in ('port', 'payload', 'tick')}
        if spec_a != spec_c:
            changes.append({'id': identifier, 'A_input': spec_a, 'C_input': spec_c})
        if aa['receipt']['status'] != cc['receipt']['status']:
            status_changes.append({'id': identifier, 'port': aa['port'], 'requested_tick': aa['tick'],
                                   'A_status': aa['receipt']['status'], 'C_status': cc['receipt']['status']})
    value = {
        'schema': 'APD04.first6.same_prefix_encoding_contrast.portable.N0.v2',
        'A_sources': a['sources'], 'C_sources': c['sources'],
        'query_ticks_A': [row['selection']['query_tick'] for row in a['rows']],
        'query_ticks_C': [row['selection']['query_tick'] for row in c['rows']],
        'same_first_reader_observations': a['rows'][0]['selection']['reader']['observations'] == c['rows'][0]['selection']['reader']['observations'],
        'A_final': a['final'], 'C_final': c['final'],
        'input_unique_counts': [len(a['inputs']), len(c['inputs'])],
        'input_spec_differences': changes, 'receipt_status_differences': status_changes,
        'A_choices': [row['selection']['physical_choice'] for row in a['rows']],
        'C_choices': [row['selection']['physical_choice'] for row in c['rows']],
        'feedback_categories_A': [row['feedback']['category'] for row in a['rows']],
        'feedback_categories_C': [row['feedback']['category'] for row in c['rows']],
        'new_Native_ticks': 0,
        'scope': 'Same complete T639374 prefix and six completed fixed opportunities. '
                 'Both sensor symmetry and material payload dose vary: this does not isolate one microscopic cause. '
                 'A whole-state snapshot before every input was not archived. Rejection is an observed outcome. '
                 'The four C5 opportunities were requested as one processing block, but no individual completion/admission is certified.'
    }
    assert len(a['rows']) == len(c['rows']) == 6
    assert value['query_ticks_A'] == value['query_ticks_C']
    assert value['input_unique_counts'] == [102, 102]
    assert len(changes) == 3
    with args.out.open('x', encoding='utf8') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'out': str(args.out), 'sources_verified': 4, 'completed_each': 6,
                      'input_unique_counts': value['input_unique_counts'], 'spec_differences': len(changes),
                      'receipt_status_differences': len(status_changes), 'Native_ticks': 0}))


if __name__ == '__main__':
    main()
