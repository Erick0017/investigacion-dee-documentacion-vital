"""Prefijo APD04 R04 COMPLETED de un diario aún abierto; sólo lectura N0.

No espera ni reenvía work04, no accede al owner/SQLite/Runtime y no afirma
cerrado el run. Conserva bytes exactos del prefijo hasta un resultado completo.
"""
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def unjson(value):
    return json.loads(value) if isinstance(value, str) else value


def recalculate(folder):
    index = json.loads((folder / 'INDICE_PREFIJO_COMPLETADO.json').read_bytes())
    encoded = (folder / index['prefix_export']).read_bytes()
    data = gzip.decompress(encoded)
    if sha(encoded) != index['prefix_gzip_sha256'] or sha(data) != index['prefix_original_sha256']:
        raise ValueError('Archived exact prefix changed')
    decoder_path = folder / 'CODIGO/compactar_recalcular_taller_n0_CONGELADO.py'
    if sha(decoder_path.read_bytes()) != index['decoder_sha256']:
        raise ValueError('Frozen exact RAW decoder changed')
    spec = importlib.util.spec_from_file_location('r04_archive_decoder', decoder_path)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    results, all_receipts = [], {}
    for line_number, line in enumerate(data.splitlines()):
        event = json.loads(line)
        if event.get('kind') != 'scheduled_material_result':
            continue
        request = event['result']['request']
        if request['status'] != 'completed':
            raise ValueError('A selected result is not COMPLETED')
        native = unjson(request['result'])
        receipt_map = {}
        for _, node in decoder.walk(native):
            if not isinstance(node, dict) or not isinstance(node.get('receipt'), dict) or 'id' not in node['receipt']:
                continue
            receipt = node['receipt']
            key = str(receipt['id'])
            old = receipt_map.get(key)
            if old is None or old.get('status') in ('scheduled', 'pending', 'admitted'):
                receipt_map[key] = receipt
        for key, receipt in receipt_map.items():
            old = all_receipts.get(key)
            if old is None or old.get('status') in ('scheduled', 'pending', 'admitted'):
                all_receipts[key] = receipt
        statuses = {}
        for receipt in receipt_map.values():
            status = receipt.get('status')
            statuses[status] = statuses.get(status, 0) + 1
        rows = []
        for locator, node in decoder.walk(native['result']):
            if not isinstance(node, dict) or not {'public_before', 'committed_effect', 'selection'} <= set(node):
                continue
            selection = node['selection']
            reader = selection.get('reader', selection.get('native_trial', {}).get('reader', {}))
            sign = decoder.choice(reader, 'selection')
            reported = selection.get('physical_choice', selection.get('native_trial', {}).get('physical_choice'))
            if sign != reported:
                raise ValueError('Exact selector RAW disagrees with reported choice')
            action = {-1: 'USE', 0: 'INSPECT', 1: 'INSPECT'}.get(sign)
            if action != node.get('physical_action'):
                raise ValueError('Fixed action transduction disagrees with physical sign')
            rows.append({'episode': node['episode'], 'query_tick': selection.get('query_tick'),
                         'RAW_sign': sign, 'physical_action': action,
                         'selector_observations': reader['observations'],
                         'raw_sensor_components': node.get('raw_sensor_components'),
                         'public_before': node['public_before'], 'effect': node['committed_effect'],
                         'native_operation_present': node.get('native_operation') is not None,
                         'feedback': node.get('feedback'),
                         'actual_return_category': (node.get('native_return') or {}).get('category'),
                         'primary_line': line_number, 'JSON_locator': '$.result.request.result.result' + locator[1:]})
        results.append({'request_id': event['requested_id'], 'primary_line': line_number,
                        'before_tick': native['before_tick'], 'after_tick': native['after_tick'],
                        'committed_snapshot': native.get('committed_snapshot'),
                        'host_started_utc': native.get('started_utc'),
                        'host_finished_utc': native.get('finished_execution_utc'),
                        'driver_window_seconds': event.get('window_seconds'),
                        'physical_receipt_IDs_exported': len(receipt_map), 'receipt_statuses': statuses,
                        'physical_receipts': list(receipt_map.values()), 'opportunities': rows})
    opportunities = [row for result in results for row in result['opportunities']]
    if len(opportunities) != 3 or [r['episode'] for r in opportunities] != [21, 22, 23]:
        raise ValueError('This frozen revision covers exactly work01/work02/work03, not another future')
    all_statuses = {}
    for receipt in all_receipts.values():
        status = receipt.get('status')
        all_statuses[status] = all_statuses.get(status, 0) + 1
    return {'schema': 'APD04.R04.completed_prefix.archived_RAW.N0.R01',
            'life': 'APD04_CONTINUABLE_R01', 'status': 'COMPLETED_PREFIX_OF_AN_OPEN_RUN_NOT_A_FINAL_CUT',
            'prefix_original_sha256': sha(data), 'completed_material_requests': len(results),
            'results': results, 'completed_work_opportunities': len(opportunities),
            'useful_work_opportunities': sum(bool(r['effect'].get('useful')) for r in opportunities),
            'unique_exported_physical_receipts_in_selected_material_results': len(all_receipts),
            'receipt_statuses_in_selected_material_results': all_statuses,
            'new_native_ticks': 0, 'work04_evaluated_or_replayed': False,
            'scope': 'A frozen exact completed prefix, not a closed owner or continuable complete snapshot. Valid physical response does not imply useful action, contextual perception, memory destruction, or learned attention.'}


def export(root, out, stop_id):
    ev = root / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    path = ev / 'CONTINUABLE_SENSOR_R04_R01/TRAYECTORIA/EVENTOS.jsonl'
    size_at_start = path.stat().st_size
    with path.open('rb') as stream:
        read_bytes = stream.read(size_at_start)
    lines = read_bytes.splitlines(keepends=True)
    found = []
    for number, line in enumerate(lines):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            if number == len(lines) - 1:
                break
            raise
        if event.get('kind') == 'scheduled_material_result' and event.get('requested_id') == stop_id:
            if event['result']['request']['status'] != 'completed':
                raise ValueError('Requested stop point is not completed')
            found.append(number)
    if len(found) != 1:
        raise ValueError('Expected one completed stop-point result; do not wait, replay or inspect Native')
    number = found[0]
    prefix = b''.join(lines[:number + 1])
    with path.open('rb') as stream:
        if stream.read(len(prefix)) != prefix:
            raise ValueError('The source prefix was changed, not merely appended')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'CODIGO').mkdir()
    helper = root / 'laboratorio/campanas/APD04_ECOSISTEMA_COGNITIVO/controles_diseno/compactar_recalcular_taller_n0.py'
    helper_data = helper.read_bytes()
    (out / 'CODIGO/compactar_recalcular_taller_n0_CONGELADO.py').write_bytes(helper_data)
    shutil.copyfile(Path(__file__), out / 'CODIGO/exportar_prefijo_r04_completado_n0_r01.py')
    encoded = gzip.compress(prefix, compresslevel=9, mtime=0)
    (out / 'PREFIJO_COMPLETADO_ORIGINAL.jsonl.gz').write_bytes(encoded)
    dump(out / 'INDICE_PREFIJO_COMPLETADO.json', {
         'source': path.relative_to(root).as_posix(), 'source_is_open_may_grow': True,
         'source_bytes_at_initial_read': size_at_start, 'captured_prefix_bytes': len(prefix),
         'last_zero_based_line': number, 'stop_at_completed_request_id': stop_id,
         'prefix_original_sha256': sha(prefix), 'prefix_gzip_sha256': sha(encoded),
         'prefix_export': 'PREFIJO_COMPLETADO_ORIGINAL.jsonl.gz',
         'decoder_source': helper.relative_to(root).as_posix(), 'decoder_sha256': sha(helper_data),
         'selection': 'Original bytes through the unique COMPLETED work03 result, no reserialization, no later polls/material future.',
         'not_a_full_file_hash_or_closed_run_assertion': True, 'new_native_ticks': 0})
    result = recalculate(out)
    dump(out / 'RECALCULO_PREFIJO_R04_N0.json', result)
    plan = {'jobs': [{'id': 'R04_COMPLETED_PREFIX', 'base': '.',
             'script': 'CODIGO/exportar_prefijo_r04_completado_n0_r01.py',
             'args': ['recalc', '--evidence', {'input': '.'}, '--out', '{output}'],
             'expected': 'RECALCULO_PREFIJO_R04_N0.json', 'comparison': 'bytes'}]}
    dump(out / 'PLAN_RECALCULO.json', plan)
    members = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
               for p in sorted(out.rglob('*')) if p.is_file()]
    dump(out / 'MANIFIESTO.json', {'members': members, 'contains_no_complete_snapshot': True,
                                  'original_run_remains_open': True, 'new_native_ticks': 0})
    print(json.dumps({'out': str(out), 'completed_work_opportunities': result['completed_work_opportunities'],
                      'completed_material_requests': result['completed_material_requests'],
                      'useful': result['useful_work_opportunities'], 'new_native_ticks': 0,
                      'work04_touched': False}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    p = sub.add_parser('export')
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--stop-id', required=True, choices=['apd04continuable_r04_work03_r01'])
    p = sub.add_parser('recalc')
    p.add_argument('--evidence', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.operation == 'export':
        export(args.root.resolve(), args.out.resolve(), args.stop_id)
    else:
        dump(args.out, recalculate(args.evidence.resolve()))
