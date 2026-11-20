"""Reserva ACTR02: prefijo COMPLETED + microscopio offline, no Native.

No lee VIDA viva, SQLite ni owner. El padre es un par histórico fijo T656420.
Los RAW/clocks exportados NO son snapshots operativos; los completos no cambian.
"""
from array import array
from collections import Counter
import argparse
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import zlib

PARENT = 'sistema/estado/fuentes_emparejadas/APD04_ACTUADOR_REAL_R02_T656420_PRE_RESERVA_R01/EXPORTACION_SERVICIO.json'
PARENT_SHA = 'ffd99f416fa0339884a21d2ddd85c817e60dccda1d2f56a57291555717ab0d96'
STOP_ID = 'apd04_reserve_r01_level2_work02'
MU_A, MU_B = [14, 14, 15], [16, 14, 15]


def sha(value):
    return hashlib.sha256(value).hexdigest()


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8')


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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


def receipt_map(value):
    result = {}
    for _, row in walk(value):
        if isinstance(row, dict) and isinstance(row.get('receipt'), dict) and 'id' in row['receipt']:
            receipt = row['receipt']
            key = str(receipt['id'])
            old = result.get(key)
            if old is None or old.get('status') in ('scheduled', 'pending', 'admitted'):
                result[key] = receipt
    return result


def metrics(raw, clocks, n, tick):
    states = Counter(int(value & 0xffffffff) for value in raw)
    return {'N': n, 'tick': tick, 'sites': len(raw), 'occupied': len(raw) - states[0],
            'RAW_nonzero': sum(bool(x) for x in raw),
            'state_zero_RAW_nonzero': sum(bool(x) and not x & 0xffffffff for x in raw),
            'states_exact': {str(key): value for key, value in sorted(states.items())},
            'max_s_reg': max((x >> 32) & 65535 for x in raw),
            'clocks_min_max': [str(min(clocks)), str(max(clocks))],
            'clocks_not_equal_to_tick': sum(x != tick for x in clocks)}


def contextual_sites(channels, n):
    sites = set()
    for center in ([15, 15, 15], [25, 15, 53], [47, 7, 47]):
        for x in range(-3, 4):
            for y in range(-3, 4):
                for z in range(-3, 4):
                    sites.add(tuple((center[i] + d) % n for i, d in enumerate((x, y, z))))
    for name, row in channels.items():
        if name.startswith(('APD02.trace.R04.', 'APD03.balanced_context.', 'APD04.LEX.')):
            sites.add(tuple(row['site']))
    sites.update((tuple(MU_A), tuple(MU_B)))
    return sorted(sites)


def unjson(value):
    return json.loads(value) if isinstance(value, str) else value


def primary_summary(data, observer):
    events = [json.loads(line) for line in data.splitlines() if line]
    result = []
    for number, event in enumerate(events):
        if event.get('kind') != 'scheduled_material_result':
            continue
        request = event['result']['request']
        if request['status'] != 'completed':
            raise ValueError('Only completed results permitted in this frozen prefix')
        native = unjson(request['result'])
        receipts = receipt_map(native)
        status = dict(Counter(x.get('status') for x in receipts.values()))
        rows = []
        for locator, node in walk(native['result']):
            if not isinstance(node, dict) or not {'public_before', 'selection', 'committed_effect'} <= set(node):
                continue
            selection = node['selection']
            reader = selection.get('reader', selection.get('native_trial', {}).get('reader', {}))
            expected = {(25 + 2*x, 15, 53): [x, 1, 0] for x in (-1, 0, 1)}
            panel = reader['observations']
            if len(panel) != 3 or {tuple(x['site']) for x in panel} != set(expected):
                raise ValueError('Fixed selector coverage differs')
            candidates = []
            for item in panel:
                fields = observer.fields(int(item['raw']))
                if fields['state'] and fields['semantic'] == 1 and fields['direction'] == expected[tuple(item['site'])]:
                    candidates.append((item['site'][0] - 25) // 2)
            sign = candidates[0] if len(candidates) == 1 else None
            reported = selection.get('physical_choice', selection.get('native_trial', {}).get('physical_choice'))
            action = {-1: 'INSPECT', 0: 'INSPECT', 1: 'USE'}.get(sign)
            if sign != reported or action != node['physical_action']:
                raise ValueError('ACTR02 fixed codec/RAW differs; do not use the old actuator codec')
            rows.append({'episode': node['episode'], 'query_tick': selection['query_tick'], 'RAW_choice': sign,
                         'physical_action': action, 'public_before': node['public_before'],
                         'selector_observations': panel, 'effect': node['committed_effect'],
                         'actual_return_category': (node.get('native_return') or {}).get('category'),
                         'raw_sensor_components': node.get('raw_sensor_components'),
                         'locator': '$[' + str(number) + '].result.request.result.result' + locator[1:]})
        result.append({'request_id': event['requested_id'], 'line': number,
                       'before_tick': native['before_tick'], 'after_tick': native['after_tick'],
                       'committed_snapshot': native['committed_snapshot'],
                       'driver_window_seconds': event.get('window_seconds'),
                       'unique_exported_physical_receipts': len(receipts), 'receipt_statuses': status,
                       'receipts': list(receipts.values()), 'work_opportunities': rows})
    return result


def read_source(folder, index, key):
    row = next(x for x in index['sources'] if x['id'] == key)
    encoded = (folder / row['export']).read_bytes()
    if sha(encoded) != row['export_sha256']:
        raise ValueError('Encoded archived source differs')
    data = gzip.decompress(encoded) if row['gzip'] else encoded
    if sha(data) != row['source_sha256'] or len(data) != row['source_bytes']:
        raise ValueError('Lossless source extraction differs')
    return data


def recalculate(folder):
    index = json.loads((folder / 'INDICE.json').read_bytes())
    observer = load_module('frozen_reserve_observer_no_native', folder / 'CODIGO/observador_snapshot_CONGELADO.py')
    if sha((folder / 'CODIGO/observador_snapshot_CONGELADO.py').read_bytes()) != index['observer_sha256']:
        raise ValueError('Observer source identity differs')
    primary = primary_summary(read_source(folder, index, 'COMPLETED_PREFIX'), observer)
    all_receipts = {str(x['id']): x for result in primary for x in result['receipts']}
    fields = []
    base_raw, base_clocks = None, None
    for row in index['field_cuts']:
        encoded = (folder / row['fields_file']).read_bytes()
        data = zlib.decompress(encoded)
        if sha(encoded) != row['fields_sha256'] or len(data) != row['N']**3 * 16:
            raise ValueError('Exact integer field dimensions/hash differ')
        count = row['N']**3
        raw, clocks = observer.qarray(data[:count * 8]), observer.qarray(data[count * 8:])
        if sha(data[:count * 8]) != row['RAW_sha256'] or sha(data[count * 8:]) != row['clocks_sha256']:
            raise ValueError('Exact whole-field identity differs')
        current_metrics = metrics(raw, clocks, row['N'], row['tick'])
        if current_metrics != row['metrics']:
            raise ValueError('Global field metrics differ')
        context = json.loads(read_source(folder, index, row['context_source_id']))
        for item in context['ROI_observations']:
            i = observer.index(item['site'], row['N'])
            if observer.fields(raw[i]) != {key: item[key] for key in ('raw', 'state', 's_reg', 'direction', 'semantic')} or str(clocks[i]) != item['clock']:
                raise ValueError('ROI observation differs from exact global fields')
        pair = []
        for site in (MU_A, MU_B):
            i = observer.index(site, row['N'])
            pair.append({'site': site, 'clock': str(clocks[i]), **observer.fields(raw[i])})
        if base_raw is None:
            base_raw, base_clocks = array('Q', raw), array('Q', clocks)
        delta = {'RAW_different_sites_vs_T656420': sum(x != y for x, y in zip(base_raw, raw)),
                 'clocks_different_sites_vs_T656420': sum(x != y for x, y in zip(base_clocks, clocks))}
        matched_receipts = []
        for receipt in context['receipts_added_since_baseline']:
            exported = all_receipts.get(str(receipt['id']))
            if exported:
                if receipt['channels'] != exported['channels'] or receipt['requested_tick'] != exported['requested_tick']:
                    raise ValueError('Full-snapshot/primary receipt specification differs')
                matched_receipts.append({'id': receipt['id'], 'snapshot_status_code': receipt['status'],
                                         'primary_status': exported['status']})
        fields.append({'id': row['id'], 'tick': row['tick'], 'source_full_snapshot_sha256': row['source_full_snapshot_sha256'],
                       'metrics': current_metrics, **delta, 'mu_numeric_A_B': pair,
                       'external_s_reg_B_minus_A': pair[1]['s_reg'] - pair[0]['s_reg'],
                       'receipt_reconciliation_with_primary': matched_receipts,
                       'new_receipts_since_baseline': len(context['receipts_added_since_baseline']),
                       'changed_inherited_receipts': len(context['receipts_changed_since_baseline']),
                       'deleted_inherited_receipts': len(context['receipts_deleted_since_baseline']),
                       'interfaces': len(context['channels']), 'pending_native_events': len(context['pending_native_events']),
                       'ROI_sites_checked': len(context['ROI_observations'])})
    work = [row for result in primary for row in result['work_opportunities']]
    if len(work) != 2:
        raise ValueError('This frozen revision covers exactly the first two reserve work opportunities')
    return {'schema': 'APD04.reserve.completed_prefix_microscope.N0.R01',
            'status': 'PARTIAL_RESERVE_STILL_OPEN_NOT_A_60MINUTE_CLOSURE',
            'life': 'APD04_ACTUADOR_REAL_R02', 'primary_results': primary, 'field_cuts': fields,
            'work_counts': {'completed': len(work), 'formed': sum(x['RAW_choice'] is not None for x in work),
                            'unformed': sum(x['RAW_choice'] is None for x in work),
                            'useful': sum(bool(x['effect'].get('useful')) for x in work)},
            'new_native_ticks': 0, 'native_owner_contacted': False,
            'limits': ['The original live journal may grow; only this immutable completed prefix is analysed.',
                       'Full snapshots remain local/unchanged. RAW+clocks+selected context is not a continuable snapshot.',
                       'An externally readable reference difference is not Native use or recovered memory.',
                       'A dense state, a rejected input, or a field near its native range limit is not a death criterion.',
                       'The third opportunity and later agenda are outside this frozen prefix; no FIN or60minute success is inferred.']}


def export(root, out):
    ev = root / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO'
    run = ev / 'RESERVA60_REAL_R02_R01'
    path = run / 'TRAYECTORIA/EVENTOS.jsonl'
    size = path.stat().st_size
    with path.open('rb') as stream:
        data = stream.read(size)
    lines = data.splitlines(keepends=True)
    matches = []
    for i, line in enumerate(lines):
        try:
            value = json.loads(line)
        except ValueError:
            if i == len(lines) - 1:
                break
            raise
        if value.get('kind') == 'scheduled_material_result' and value.get('requested_id') == STOP_ID:
            if value['result']['request']['status'] != 'completed':
                raise ValueError('Stop ID is not COMPLETED')
            matches.append(i)
    if len(matches) != 1:
        raise ValueError('No unique completed stop ID; never wait/replay or contact the owner')
    prefix = b''.join(lines[:matches[0] + 1])
    with path.open('rb') as stream:
        if stream.read(len(prefix)) != prefix:
            raise ValueError('The source prefix was modified, not merely appended')
    pair_path = root / PARENT
    pair_data = pair_path.read_bytes()
    if sha(pair_data) != PARENT_SHA:
        raise ValueError('Not the fixed complete historical parent T656420')
    pair = json.loads(pair_data)
    member = next(x for x in pair['members'] if x['file'] == 'VIDA.deetsnap.gz')
    out.mkdir(parents=True, exist_ok=False)
    (out / 'CODIGO').mkdir()
    observer_path = root / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    observer_data = observer_path.read_bytes()
    (out / 'CODIGO/observador_snapshot_CONGELADO.py').write_bytes(observer_data)
    shutil.copyfile(Path(__file__), out / 'CODIGO' / Path(__file__).name)
    observer = load_module('pure_reserve_snapshot_parser', out / 'CODIGO/observador_snapshot_CONGELADO.py')
    sources = []

    def archived(key, original_locator, content, relative, compress=True):
        target = out / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        encoded = gzip.compress(content, compresslevel=9, mtime=0) if compress else content
        with target.open('xb') as stream:
            stream.write(encoded)
        sources.append({'id': key, 'source': original_locator, 'source_bytes': len(content),
                        'source_sha256': sha(content), 'export': relative, 'exported_bytes': len(encoded),
                        'export_sha256': sha(encoded), 'gzip': compress})

    archived('COMPLETED_PREFIX', path.relative_to(root).as_posix(), prefix, 'PRIMARIOS/PREFIJO_COMPLETADO.jsonl.gz')
    archived('PARENT_COMPLETE_MANIFEST', PARENT, pair_data, 'PRIMARIOS/PAR_T656420_MANIFIESTO.json.gz')
    for name in ('ANTES_DEL_PROCESO.json', 'TRAYECTORIA/ANTES_DE_NATIVE.json', 'TRAYECTORIA/INICIO_VENTANA.json'):
        p = run / name
        archived(name.replace('/', '_'), p.relative_to(root).as_posix(), p.read_bytes(), 'PRIMARIOS/' + p.name + '.gz')
    primary = primary_summary(prefix, observer)
    cuts = [('BASE_T656420', pair_path.parent / 'VIDA.deetsnap.gz', member['sha256'], None)]
    cuts += [('ENV_T656423' if 'environment' in row['request_id'] else 'WORK' + str(i),
              root / 'sistema' / row['committed_snapshot']['snapshot'],
              row['committed_snapshot']['snapshot_sha256'], row['committed_snapshot']['physical'])
             for i, row in enumerate(primary) if row['request_id'] != STOP_ID or i == len(primary) - 1]
    fields, base_receipts = [], None
    for label, snapshot_path, expected_sha, committed in cuts:
        snapshot = observer.Snapshot(snapshot_path)
        if snapshot.encoded_sha256 != expected_sha or snapshot.N != 67:
            raise ValueError('Immutable complete snapshot identity/domain differs')
        raw_bytes, clock_bytes = observer.pbytes(snapshot.raw), observer.pbytes(snapshot.clocks)
        actual_metrics = metrics(snapshot.raw, snapshot.clocks, snapshot.N, snapshot.tick)
        if committed and (committed['RAW_sha256'] != sha(raw_bytes) or committed['clocks_sha256'] != sha(clock_bytes)
                          or committed['occupied'] != actual_metrics['occupied'] or committed['tick'] != snapshot.tick):
            raise ValueError('Complete snapshot differs from committed primary physical record')
        field_data = zlib.compress(raw_bytes + clock_bytes, level=9)
        field_name = 'CAMPOS/' + label + '_RAW_CLOCKS_U64_LE.zlib'
        (out / 'CAMPOS').mkdir(exist_ok=True)
        with (out / field_name).open('xb') as stream:
            stream.write(field_data)
        current = {row['id']: row for row in snapshot.receipts}
        if base_receipts is None:
            base_receipts = {key: dict(value) for key, value in current.items()}
        added = [row for key, row in current.items() if key not in base_receipts]
        changed = [{'before': base_receipts[key], 'after': row} for key, row in current.items()
                   if key in base_receipts and row != base_receipts[key]]
        context = {'id': label, 'tick': snapshot.tick, 'N': snapshot.N, 'paused': snapshot.paused,
                   'phase': snapshot.phase, 'next_event_id': snapshot.next_event_id, 'next_sequence': snapshot.next_sequence,
                   'channels': snapshot.channels, 'pending_native_events': snapshot.pending,
                   'complete_receipt_count': len(snapshot.receipts),
                   'complete_receipts_canonical_sha256': sha(canonical(snapshot.receipts)),
                   'receipts_added_since_baseline': added, 'receipts_changed_since_baseline': changed,
                   'receipts_deleted_since_baseline': [key for key in base_receipts if key not in current],
                   'inherited_receipts_unchanged': sum(key in current and current[key] == row for key, row in base_receipts.items()),
                   'metadata_packets_hex': {key: value.hex() for key, value in snapshot.metadata_packets.items()},
                   'ROI_observations': [snapshot.observation(list(site)) for site in contextual_sites(snapshot.channels, snapshot.N)],
                   'ROI_scope': 'Fixed radius3 windows plus registered relevant interfaces; global fields supplied separately. Not a complete causal cone or a new participant sensor.',
                   'full_snapshot_checksum_valid': snapshot.checksum_valid}
        context_id = label + '_CONTEXT'
        context_bytes = canonical(context)
        archived(context_id, snapshot_path.relative_to(root).as_posix() + '#offline-context-extraction',
                 context_bytes, 'CONTEXTOS/' + label + '.json.gz')
        fields.append({'id': label, 'source_full_snapshot': snapshot_path.relative_to(root).as_posix(),
                       'source_full_snapshot_sha256': snapshot.encoded_sha256, 'source_full_snapshot_bytes': snapshot.encoded_bytes,
                       'source_checksum_valid': snapshot.checksum_valid, 'N': snapshot.N, 'tick': snapshot.tick,
                       'RAW_sha256': sha(raw_bytes), 'clocks_sha256': sha(clock_bytes),
                       'fields_file': field_name, 'fields_sha256': sha(field_data), 'fields_bytes': len(field_data),
                       'metrics': actual_metrics, 'context_source_id': context_id})
        if sha(snapshot_path.read_bytes()) != expected_sha:
            raise ValueError('Original complete snapshot changed during offline inspection')
        del snapshot, current, raw_bytes, clock_bytes
    for p in sorted((run / 'TRAYECTORIA/FUENTES_ANTES_DE_NATIVE').rglob('*')):
        if p.is_file() and p.suffix.casefold() in ('.py', '.json', '.md', '.txt'):
            relative = p.relative_to(run / 'TRAYECTORIA/FUENTES_ANTES_DE_NATIVE').as_posix()
            archived('FROZEN_' + str(len(sources)), p.relative_to(root).as_posix(), p.read_bytes(), 'FUENTES_EJECUTADAS/' + relative + '.gz')
    dump(out / 'INDICE.json', {'schema': 'APD04.reserve.completed_prefix_offline_microscope.R01',
         'sources': sources, 'observer_sha256': sha(observer_data), 'field_cuts': fields,
         'source_journal_is_open': True, 'source_journal_bytes_at_read': size,
         'captured_completed_prefix_bytes': len(prefix), 'captured_last_zero_based_line': matches[0],
         'source_complete_parent_manifest_sha256': PARENT_SHA,
         'no_full_snapshot_embedded_no_operational_backup': True,
         'omitted_complete_snapshots': [{'file': x['source_full_snapshot'], 'sha256': x['source_full_snapshot_sha256'], 'bytes': x['source_full_snapshot_bytes']} for x in fields],
         'omissions_scope': 'All original complete snapshots remain local, unchanged. Exported global arrays/context are observational, not enough to restore a life.',
         'new_native_ticks': 0})
    result = recalculate(out)
    dump(out / 'RECALCULO_PREFIJO_RESERVA_N0.json', result)
    dump(out / 'PLAN_RECALCULO.json', {'jobs': [{'id': 'RESERVE_COMPLETED_PREFIX', 'base': '.',
         'script': 'CODIGO/' + Path(__file__).name,
         'args': ['recalc', '--evidence', {'input': '.'}, '--out', '{output}'],
         'expected': 'RECALCULO_PREFIJO_RESERVA_N0.json', 'comparison': 'bytes'}]})
    members = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': sha(p.read_bytes())}
               for p in sorted(out.rglob('*')) if p.is_file()]
    dump(out / 'MANIFIESTO.json', {'members': members, 'new_native_ticks': 0,
                                  'source_reserve_still_open': True, 'not_60minute_closure': True})
    print(json.dumps({'out': str(out), 'cuts': [(x['id'], x['tick'], x['metrics']['occupied']) for x in fields],
                      'work': result['work_counts'], 'new_native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    p = sub.add_parser('export')
    p.add_argument('--root', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    p = sub.add_parser('recalc')
    p.add_argument('--evidence', required=True, type=Path)
    p.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    if args.operation == 'export':
        export(args.root.resolve(), args.out.resolve())
    else:
        dump(args.out, recalculate(args.evidence.resolve()))
