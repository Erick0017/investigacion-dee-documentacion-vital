"""Cierre APD04 sensorial R04, lectura de un run detenido, cero Native.

Revisión separada: preserva las extracciones de prefijos R01/R02. Conserva el
diario completo original y las fuentes congeladas ANTES del Native, no S actual.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil


def sha(data):
    return hashlib.sha256(data).hexdigest()


def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def walk(value, locator='$'):
    yield locator, value
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ('result', 'result_json') and isinstance(item, str):
                try:
                    item = json.loads(item)
                except ValueError:
                    pass
            yield from walk(item, locator + '.' + key)
    elif isinstance(value, list):
        for number, item in enumerate(value):
            yield from walk(item, locator + '[' + str(number) + ']')


def raw_fields(raw):
    value = int(raw)
    if not 0 <= value < 2**64:
        raise ValueError('Exact uint64 required')
    return {'state': value & 0xffffffff, 's_reg': (value >> 32) & 65535,
            'semantic': (value >> 60) & 15,
            'direction': [((value >> k) & 15) - (16 if ((value >> k) & 15) >= 8 else 0) for k in (48, 52, 56)]}


def panel_read(reader):
    candidates, active, mismatches = [], 0, []
    for row in reader['panel']:
        decoded = raw_fields(row['raw'])
        mismatches += [key for key, value in decoded.items() if key in row and row[key] != value]
        active += bool(decoded['state'])
        if decoded['state'] and decoded['semantic'] == 1 and decoded['direction'] in ([0, 0, -1], [0, 0, 1]):
            candidates.append({'sign': decoded['direction'][2], 'site': row['site'], 'raw': row['raw'], 'clock': row.get('clock')})
    sign = candidates[0]['sign'] if len(candidates) == 1 else None
    if mismatches or sign != reader['formed_native_command']:
        raise ValueError('Old-panel exact RAW disagrees with recorded fields/formed_native_command')
    return {'RAW_sign': sign, 'candidate_count': len(candidates), 'candidates': candidates,
            'active_observations': active, 'total_observations': len(reader['panel']),
            'reported_formed_native_command': reader['formed_native_command']}


def input_receipts(value):
    receipts = {}
    for _, row in walk(value):
        if not isinstance(row, dict) or not isinstance(row.get('receipt'), dict) or 'id' not in row['receipt']:
            continue
        receipt = row['receipt']
        key = str(receipt['id'])
        old = receipts.get(key)
        if old is None or old.get('status') in ('scheduled', 'pending', 'admitted'):
            receipts[key] = receipt
    counts = {}
    for row in receipts.values():
        status = row.get('status')
        counts[status] = counts.get(status, 0) + 1
    return {'unique_exported_receipt_IDs': len(receipts), 'status_counts': counts,
            'receipts': list(receipts.values()),
            'scope': 'Only exact Native receipt IDs exported in this material result; not the entire biographical queue.'}


def read_archived(folder, index, key):
    row = next(x for x in index['sources'] if x['id'] == key)
    data = (folder / row['export']).read_bytes()
    if sha(data) != row['export_sha256']:
        raise ValueError('Encoded source bytes differ')
    data = gzip.decompress(data) if row['gzip'] else data
    if sha(data) != row['source_sha256'] or len(data) != row['source_bytes']:
        raise ValueError('Original source bytes differ after extraction')
    return data


def recalculate(folder):
    index = json.loads((folder / 'INDICE.json').read_bytes())
    log = read_archived(folder, index, 'EVENTOS')
    result = json.loads(read_archived(folder, index, 'DRIVER_RESULT'))
    wrapper = json.loads(read_archived(folder, index, 'WRAPPER_RESULT'))
    history = json.loads(read_archived(folder, index, 'HISTORIC_PANEL_RECALC'))
    if result['error'] is not None or not result['owner_stop_confirmed'] or wrapper['exit_code'] != 0:
        raise ValueError('Not the declared cleanly closed R04 run')
    if result['final_native_job']['job_active_processes'] or wrapper['final_total_job']['job_active_processes']:
        raise ValueError('Owner/process tree not recorded closed')
    events = [json.loads(line) for line in log.splitlines() if line]
    material, old_panel, selectors = [], None, []
    all_receipts = {}
    for line_number, event in enumerate(events):
        if event.get('kind') != 'scheduled_material_result':
            continue
        request = event['result']['request']
        if request['status'] != 'completed':
            raise ValueError('Closed run has a non-COMPLETED scheduled result')
        native = request['result']
        native = json.loads(native) if isinstance(native, str) else native
        receipts = input_receipts(native)
        for receipt in receipts['receipts']:
            key = str(receipt['id'])
            old = all_receipts.get(key)
            if old is None or old.get('status') in ('scheduled', 'pending', 'admitted'):
                all_receipts[key] = receipt
        material.append({'request_id': event['requested_id'], 'line': line_number,
                         'before_tick': native['before_tick'], 'after_tick': native['after_tick'],
                         'committed_snapshot': native.get('committed_snapshot'),
                         'receipts': receipts, 'driver_window_seconds': event.get('window_seconds')})
        if event['requested_id'] == 'apd04continuable_r04_old_panel_r01':
            panel = native['result']['rows'][0]
            old_panel = {'source_line': line_number, 'request_id': event['requested_id'],
                         'before_tick': native['before_tick'], 'after_tick': native['after_tick'],
                         'committed_snapshot': native['committed_snapshot'], 'rows': [], 'receipts': receipts}
            for family, name in (('forms', 'form'), ('memories', 'context')):
                for number, item in enumerate(panel[family]):
                    old_panel['rows'].append({'family': family, 'name': item[name],
                         **panel_read(item['result']['reader']),
                         'locator': '$[' + str(line_number) + '].result.request.result.result.rows[0].' + family + '[' + str(number) + '].result.reader'})
        for locator, node in walk(native['result']):
            if not isinstance(node, dict) or not {'public_before', 'committed_effect', 'selection'} <= set(node):
                continue
            selection = node['selection']
            reader = selection.get('reader', selection.get('native_trial', {}).get('reader', {}))
            panel = reader['observations']
            expected = {(25 + 2*x, 15, 53): [x, 1, 0] for x in (-1, 0, 1)}
            if len(panel) != 3 or {tuple(x['site']) for x in panel} != set(expected):
                raise ValueError('Fixed selector coverage differs')
            candidates = []
            for item in panel:
                raw = raw_fields(item['raw'])
                if raw['state'] and raw['semantic'] == 1 and raw['direction'] == expected[tuple(item['site'])]:
                    candidates.append((item['site'][0] - 25) // 2)
            sign = candidates[0] if len(candidates) == 1 else None
            reported = selection.get('physical_choice', selection.get('native_trial', {}).get('physical_choice'))
            action = {-1: 'USE', 0: 'INSPECT', 1: 'INSPECT'}.get(sign)
            if sign != reported or action != node['physical_action']:
                raise ValueError('Selector RAW/action transduction differs')
            selectors.append({'request_id': event['requested_id'], 'episode': node['episode'],
                              'query_tick': selection['query_tick'], 'RAW_sign': sign, 'action': action,
                              'effect': node['committed_effect'], 'reader_observations': panel,
                              'public_before': node['public_before'],
                              'locator': '$[' + str(line_number) + '].result.request.result.result' + locator[1:]})
    if not old_panel or len(old_panel['rows']) != 22 or len(selectors) != 4:
        raise ValueError('Expected exact16+6 final old panel and four completed work opportunities')
    historic = {(r['family'], r['name']): r['RAW_sign'] for r in history['rows']}
    for row in old_panel['rows']:
        row['historical_RAW_sign_at_parent639374'] = historic[(row['family'], row['name'])]
        row['same_as_historic_panel'] = row['RAW_sign'] == row['historical_RAW_sign_at_parent639374']
    groups = {}
    for family in ('forms', 'memories'):
        rows = [r for r in old_panel['rows'] if r['family'] == family]
        groups[family] = {'requested': len(rows), 'unique_formed': sum(r['candidate_count'] == 1 for r in rows),
                         'unformed': sum(r['candidate_count'] == 0 for r in rows),
                         'ambiguous': sum(r['candidate_count'] > 1 for r in rows),
                         'same_as_parent_panel': sum(r['same_as_historic_panel'] for r in rows),
                         'some_observed_material_active': sum(r['active_observations'] > 0 for r in rows)}
    status_counts = {}
    for receipt in all_receipts.values():
        status = receipt.get('status')
        status_counts[status] = status_counts.get(status, 0) + 1
    return {'schema': 'APD04.R04.closed_run.exact_primary_recalculation.N0.R03',
            'life': result['life'], 'closed_without_outer_guard_kill': result['error'] is None and wrapper['error'] is None,
            'owner_stop_confirmed': result['owner_stop_confirmed'], 'owner_exit_code': result['final_native_job']['owned_owner_exit_code'],
            'outer_exit_code': wrapper['exit_code'], 'owner_active_at_close': result['final_native_job']['job_active_processes'],
            'outer_active_at_close': wrapper['final_total_job']['job_active_processes'],
            'window_seconds': events[-1].get('window_seconds'), 'driver_wall_seconds': result['driver_wall_seconds'],
            'actual_total_host_seconds': wrapper['actual_wall_seconds'],
            'scheduled_material_requests_completed': len(material), 'material_results': material,
            'work_opportunities': selectors, 'work_counts': {'requested_completed': len(selectors),
                'formed_valid': sum(r['RAW_sign'] is not None for r in selectors),
                'unformed': sum(r['RAW_sign'] is None for r in selectors),
                'useful': sum(bool(r['effect'].get('useful')) for r in selectors)},
            'final_old_panel': old_panel, 'final_old_panel_counts': groups,
            'selected_run_receipt_counts': {'unique_exported_IDs': len(all_receipts), 'status_counts': status_counts},
            'final_record': result['final_record'], 'final_protocol': result['final_protocol'],
            'current_new_APD04_signs_after_densification': 'NOT_MATERIALLY_QUERIED_BY_THIS_FINAL_OLD_PANEL',
            'new_native_ticks': 0, 'reserve60_minutes_proved': False,
            'limits': ['Queries are material and may alter the tested state; the22reads are not22independent learners.',
                       'Loss of fixed-reader use does not establish destruction of historical information or death.',
                       'Final old panel does not test clasifica/equilibra current access.',
                       'No exact complete snapshot is included; all local paired state is still required for continuation.',
                       'The2529second observed window is not the separately planned60minute reserve.']}


def export(root, out):
    ev = root / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    source = ev / 'CONTINUABLE_SENSOR_R04_R01'
    driver = json.loads((source / 'TRAYECTORIA/RESULTADO.json').read_bytes())
    wrapper = json.loads((source / 'RESULTADO_SUPERVISION.json').read_bytes())
    if driver['error'] is not None or not driver['owner_stop_confirmed'] or wrapper['exit_code'] != 0:
        raise ValueError('Run not cleanly closed; do not export a final scientific component')
    out.mkdir(parents=True, exist_ok=False)
    records = []

    def copy_file(key, path, relative, compress=True):
        data = path.read_bytes()
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        encoded = gzip.compress(data, compresslevel=9, mtime=0) if compress else data
        with target.open('xb') as stream:
            stream.write(encoded)
        if path.read_bytes() != data:
            raise ValueError('Closed source changed while copying')
        records.append({'id': key, 'source': path.relative_to(root).as_posix(), 'source_bytes': len(data),
                        'source_sha256': sha(data), 'export': relative, 'exported_bytes': len(encoded),
                        'export_sha256': sha(encoded), 'gzip': compress})

    for key, relative in [('EVENTOS', 'TRAYECTORIA/EVENTOS.jsonl'), ('DRIVER_RESULT', 'TRAYECTORIA/RESULTADO.json'),
                          ('WRAPPER_RESULT', 'RESULTADO_SUPERVISION.json'), ('PREFLIGHT', 'ANTES_DEL_PROCESO.json'),
                          ('BEFORE_NATIVE', 'TRAYECTORIA/ANTES_DE_NATIVE.json'),
                          ('WINDOW_START', 'TRAYECTORIA/INICIO_VENTANA.json'),
                          ('TOTAL_RESOURCES_CLASS8', 'MUESTRAS_TOTALES_CLASS8.jsonl')]:
        copy_file(key, source / relative, 'PRIMARIOS/' + key + Path(relative).suffix + '.gz')
    copy_file('HISTORIC_PANEL_RECALC', ev / 'PANEL_HEREDADO_RAW_N0_R01/RECALCULO_PANEL_HEREDADO.json',
              'CONTEXTO/RECALCULO_PANEL_HEREDADO.json.gz')
    frozen = source / 'TRAYECTORIA/FUENTES_ANTES_DE_NATIVE'
    omitted_sources = []
    for path in sorted(frozen.rglob('*')):
        if not path.is_file():
            continue
        if path.suffix.casefold() not in ('.py', '.json', '.md', '.txt'):
            omitted_sources.append({'source': path.relative_to(root).as_posix(), 'bytes': path.stat().st_size,
                                    'sha256': sha(path.read_bytes()), 'reason': 'Not a selected textual code/contract member'})
            continue
        copy_file('FROZEN_CODE_' + str(len(records)), path,
                  'FUENTES_EJECUTADAS/' + path.relative_to(frozen).as_posix() + '.gz')
    (out / 'CODIGO_Y_RECALCULO').mkdir()
    shutil.copyfile(Path(__file__), out / 'CODIGO_Y_RECALCULO' / Path(__file__).name)
    dump(out / 'INDICE.json', {'schema': 'APD04.closed_sensor_R04_export.R03', 'sources': records,
         'omitted': omitted_sources, 'full_snapshots_omitted': {'snapshot': driver['final_record']['snapshot'],
            'sha256': driver['final_record']['snapshot_sha256'], 'locator_scope': 'Canonical local system, no checkpoint embedded in this analysis.'},
         'all_run_statuses_and_original_source_bytes_preserved': True, 'new_native_ticks': 0})
    result = recalculate(out)
    dump(out / 'RECALCULO_CIERRE_R04_N0.json', result)
    dump(out / 'PLAN_RECALCULO.json', {'jobs': [{'id': 'R04_CLOSED_RUN', 'base': '.',
         'script': 'CODIGO_Y_RECALCULO/' + Path(__file__).name,
         'args': ['recalc', '--evidence', {'input': '.'}, '--out', '{output}'],
         'expected': 'RECALCULO_CIERRE_R04_N0.json', 'comparison': 'bytes'}]})
    members = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
               for p in sorted(out.rglob('*')) if p.is_file()]
    dump(out / 'MANIFIESTO.json', {'members': members, 'new_native_ticks': 0})
    print(json.dumps({'out': str(out), 'old_panel': result['final_old_panel_counts'],
                      'work': result['work_counts'], 'new_native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    p = sub.add_parser('export')
    p.add_argument('--root', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p = sub.add_parser('recalc')
    p.add_argument('--evidence', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    if args.operation == 'export':
        export(args.root.resolve(), args.out.resolve())
    else:
        dump(args.out, recalculate(args.evidence.resolve()))
