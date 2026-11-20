"""Read archived action RAW and material receipts; never import the engine."""
from pathlib import Path
import argparse
from collections import Counter
import hashlib
import importlib.util
import json
import sqlite3

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/ATENCION_CONSECUENCIAS_AUX_R01'
LIVES = [('A', 'APD04_ATENCION_REAL_AUX'), ('B', 'APD04_ATENCION_OMIT_AUX'),
         ('C', 'APD04_ATENCION_SENSOR02_AUX')]


def read(path):
    return json.loads(path.read_text(encoding='utf8'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--index', type=Path, help='Portable primary index; no system, snapshots or Native needed')
    args = parser.parse_args()
    portable = read(args.index) if args.index else None
    output = args.out or (args.index.parent / 'RECALCULO_N0.json' if args.index else OUT / 'RECALCULO_N0.json')
    spec = importlib.util.spec_from_file_location('raw_decoder_only', Path(__file__).with_name('recalcular_sensores_apd04_r01_n0.py'))
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    records, discrepancies, first_contexts = [], [], {}
    for label, life in LIVES:
        declaration = portable['branches'].get(label) if portable else None
        vida = (args.index.parent / declaration['record'] if declaration else
                ROOT / 'sistema/estado/vidas' / life / 'VIDA.json')
        if portable and declaration is None:
            records.append({'branch': label, 'life': life, 'executed': False})
            continue
        if not vida.exists():
            records.append({'branch': label, 'life': life, 'executed': False})
            continue
        record = read(vida)
        if portable:
            transport_rows = declaration['transport_rows_from_read_only_SQLite']
        else:
            database = ROOT / 'sistema/estado/servicios_persistentes' / life / 'cola.sqlite3'
            with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as connection:
                connection.row_factory = sqlite3.Row
                transport_rows = [dict(row) for row in connection.execute(
                    'select id,payload,payload_sha,status,started_utc,finished_utc,error from requests where id like ? order by seq',
                    ('apd04_attention_' + label + '_%',))]
        functional_requested, common_probes_requested = 0, 0
        for transport in transport_rows:
            payload = json.loads(transport['payload'])
            for situation in payload.get('situaciones', []):
                if situation.get('modo') == 'apd04-vivir':
                    functional_requested += situation['oportunidades']
                elif situation.get('modo') == 'apd04-sensor-calibrar':
                    common_probes_requested += len(situation['pares'])
        rows, sources, receipt_map = [], [], {}
        for operation in record['operations']:
            if operation['kind'] != 'PERSISTENT_SESION':
                continue
            source = (args.index.parent / declaration['primaries'][operation['result_file']] if portable else
                      ROOT / 'sistema/estado/servicios_persistentes' / life / operation['result_file'])
            encoded = source.read_bytes()
            digest = hashlib.sha256(encoded).hexdigest()
            if digest != operation['result_sha256']:
                raise ValueError('The primary differs from the committed index')
            primary = json.loads(encoded)
            sources.append({'file': source.relative_to(args.index.parent if portable else ROOT).as_posix(), 'sha256': digest,
                'bytes': len(encoded), 'before_tick': primary['before_tick'], 'after_tick': primary['after_tick']})
            for outer in primary['result']['rows']:
                for row in outer.get('rows', []):
                    if 'selection' not in row:
                        continue
                    selection = row['selection']
                    if row.get('committed_effect') is not None and len(first_contexts.get(label, [])) < 2:
                        first_contexts.setdefault(label, []).append(row)
                    candidates = decoder.decode(selection['reader']['observations'], (0,))
                    choice = candidates[0]['x'] if len(candidates) == 1 else None
                    if choice != selection['physical_choice']:
                        discrepancies.append([life, row.get('episode'), 'action decoder mismatch'])
                    receipts = {}
                    for item in decoder.walk(row):
                        if 'id' in item and 'port' in item and isinstance(item.get('receipt'), dict):
                            old = receipts.get(int(item['id']))
                            if old and item['receipt']['status'] in ('scheduled', 'queued'):
                                continue
                            receipts[int(item['id'])] = item
                    for identifier, item in receipts.items():
                        previous = receipt_map.get(identifier)
                        if previous and previous['port'] != item['port']:
                            discrepancies.append([life, identifier, 'same request ID has two ports'])
                        receipt_map[identifier] = item
                    native_return = row.get('native_return', row.get('return', {}))
                    rows.append({'transport_id': primary['id'], 'episode': row.get('episode'),
                        'public_before': row.get('public_before'),
                        'raw_components': row.get('raw_sensor_components', row.get('raw_components')),
                        'query_tick': selection['query_tick'], 'read_tick': selection['reader']['tick'],
                        'choice_from_RAW': choice, 'payloads_from_RAW': [x['payload_from_RAW'] for x in candidates],
                        'active_zero_not_silence': choice == 0,
                        'physical_action': row.get('physical_action'),
                        'effect': row.get('committed_effect'),
                        'feedback': row.get('feedback'),
                        'auditor_after_effect': row.get('auditor_only_after_effect'),
                        'references_before_return': native_return.get('before'),
                        'references_after_return': native_return.get('after'),
                        'request_count': len(receipts),
                        'rejected_requests': [
                            {'id': identifier, 'port': item['port'], 'payload': item['payload'],
                             'receipt': item['receipt']} for identifier, item in sorted(receipts.items())
                            if item['receipt']['status'].startswith('rejected')],
                        'receipt_statuses': {s: sum(x['receipt']['status'] == s for x in receipts.values())
                            for s in sorted(set(x['receipt']['status'] for x in receipts.values()))}})
        statuses = [x['receipt']['status'] for x in receipt_map.values()]
        functional_rows = [x for x in rows if x['effect'] is not None]
        action_counts = Counter('NO_EMISSION' if x['physical_action'] is None else x['physical_action']
                                for x in functional_rows)
        records.append({'branch': label, 'life': life, 'executed': True,
            'source_parent_sha256': record['parent']['encoded_sha256'],
            'final_committed_tick': record['physical']['tick'], 'snapshot_sha256': record['snapshot_sha256'],
            'interrupted_future_marker_present': (declaration['interrupted_future_marker_present'] if portable else
                                                  (vida.parent / 'FUTURO_INTERRUMPIDO.json').exists()),
            'sources': sources, 'rows': rows, 'functional_opportunities': len(functional_rows),
            'functional_opportunities_requested_transport': functional_requested,
            'functional_opportunities_without_committed_primary': functional_requested - len(functional_rows),
            'common_sensor_probes_requested_transport': common_probes_requested,
            'common_sensor_probes_committed_primary': len(rows) - len(functional_rows),
            'transport_statuses': [{'id': row['id'], 'status': row['status']} for row in transport_rows],
            'valid_native_actions': sum(x['effect'].get('valid_native', False) for x in functional_rows),
            'useful': sum(x['effect'].get('useful', False) for x in functional_rows),
            'actions': dict(sorted(action_counts.items())),
            'requested_unique': len(receipt_map), 'applied': statuses.count('applied'),
            'rejected': sum(status.startswith('rejected') for status in statuses),
            'receipt_status_counts_exact': dict(sorted(Counter(statuses).items())),
            'other_statuses': sorted(status for status in set(statuses)
                                     if status != 'applied' and not status.startswith('rejected'))})
    local_matched_contrast = None
    if len(first_contexts.get('A', [])) == 2 and len(first_contexts.get('B', [])) == 2:
        a0, a1 = first_contexts['A']
        b0, b1 = first_contexts['B']
        local_matched_contrast = {
            'first_query_ticks': [a0['selection']['query_tick'], b0['selection']['query_tick']],
            'first_read_ticks': [a0['selection']['reader']['tick'], b0['selection']['reader']['tick']],
            'first_all_archived_local_frames_equal': a0['selection']['frames'] == b0['selection']['frames'],
            'first_action_RAW_observations_equal': a0['selection']['reader']['observations'] == b0['selection']['reader']['observations'],
            'second_query_ticks': [a1['selection']['query_tick'], b1['selection']['query_tick']],
            'second_raw_components_equal': a1['raw_sensor_components'] == b1['raw_sensor_components'],
            'second_all_archived_local_frames_equal': a1['selection']['frames'] == b1['selection']['frames'],
            'second_choices_from_primary': [a1['selection']['physical_choice'], b1['selection']['physical_choice']],
            'scope': 'Local archived equality, not an assertion of complete global causal-state identity. '
                     'Omitted generic return has a lower material dose. Usefulness must be evaluated separately.'}
    result = {'schema': 'APD04.archived_attention_consequences.v1', 'branches': records,
        'first_local_matched_A_B_contrast': local_matched_contrast,
        'discrepancies': discrepancies, 'native_ticks': 0,
        'scope': 'Exact primary result hashes, RAW action decoding and receipt denominators. '
                 'A/B/C share one prefix; no independent learners. Physical changes of references '
                 'do not alone establish useful contextual selection or learned attention.'}
    with output.open('x', encoding='utf8') as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    print(json.dumps({'branches': [{k: v for k, v in row.items() if k not in ('rows', 'sources')}
            for row in records], 'discrepancies': discrepancies}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
