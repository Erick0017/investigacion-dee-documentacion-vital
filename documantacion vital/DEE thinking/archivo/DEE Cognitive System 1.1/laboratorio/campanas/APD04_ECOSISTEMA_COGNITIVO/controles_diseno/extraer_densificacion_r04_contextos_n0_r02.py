"""N0 exact saved R04 cuts and spatial counts; no engine/owner/SQLite access.

Build reads the already closed Delivery prefix, not a growing journal. Portable
--recalc uses exported exact arrays only. Endpoints do not identify a birth,
unique lineage, or the first causal collision in the unobserved interval.
"""
from array import array
from collections import Counter
import argparse
import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import zlib

ROOT = Path(__file__).resolve().parents[4]
CTRL = Path(__file__).resolve().parent
PREFIX = 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/PREFIJO_R04_COMPLETADO_WORK03_N0_R01'
PREFIX_SHA = '82fecf4203964d79d8e6bac2df9308cae2afc1d91c7c6ac497c58ea25a2a75b0'
CUTS = ((44, 653376, 'post_work02'), (49, 653846, 'post_goal1_before_work03'),
        (617, 655722, 'post_work03'))
BOXES = {'selector_gate_box': ((19, 31), (9, 21), (47, 59)),
         'mu_numeric_box': ((8, 22), (8, 24), (8, 24)),
         'new_lexicon_box': ((43, 56), (3, 17), (40, 54)),
         'R04_goal_interface_box': ((23, 29), (10, 16), (49, 57))}


def sha(data): return hashlib.sha256(data).hexdigest()
def file_sha(path): return sha(path.read_bytes())
def encoded_json(obj): return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode('utf8')


def save(path, obj):
    data = encoded_json(obj)
    with path.open('xb') as stream:
        stream.write(gzip.compress(data, mtime=0) if path.suffix == '.gz' else data)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def walk(obj, loc='$'):
    if isinstance(obj, dict):
        yield loc, obj
        for key, val in obj.items():
            if key in ('result', 'result_json') and isinstance(val, str) and val.lstrip().startswith(('{', '[')):
                try: val = json.loads(val)
                except json.JSONDecodeError: pass
            yield from walk(val, loc + '.' + str(key))
    elif isinstance(obj, list):
        for i, val in enumerate(obj): yield from walk(val, loc + '[' + str(i) + ']')


def metrics(raw, clocks, n, tick):
    states = Counter(int(v & 0xffffffff) for v in raw)
    return {'N': n, 'tick': tick, 'sites': len(raw), 'occupied_state_nonzero': len(raw) - states[0],
            'RAW_nonzero': sum(v != 0 for v in raw),
            'state_zero_RAW_nonzero': sum(bool(v) and not (v & 0xffffffff) for v in raw),
            'states_exact': {str(k): v for k, v in sorted(states.items())},
            'max_s_reg': max((v >> 32) & 65535 for v in raw),
            'clock_min': str(min(clocks)), 'clock_max': str(max(clocks)),
            'clocks_not_equal_to_tick': sum(v != tick for v in clocks)}


def columns(raw, n):
    return [[sum(bool(raw[(x * n + y) * n + z] & 0xffffffff) for y in range(n))
             for z in range(n)] for x in range(n)]


def local_metrics(raw, clocks, n, tick):
    result = {}
    for name, box in BOXES.items():
        ids = [(x * n + y) * n + z for x in range(box[0][0], box[0][1] + 1)
               for y in range(box[1][0], box[1][1] + 1) for z in range(box[2][0], box[2][1] + 1)]
        result[name] = {'box_inclusive': box, 'metrics': metrics([raw[i] for i in ids], [clocks[i] for i in ids], n, tick)}
    return result


def compare(a, b):
    ra, ca, ta = a; rb, cb, tb = b
    return {'ticks': [ta, tb], 'elapsed_ticks': tb - ta,
            'RAW_changed_sites': sum(x != y for x, y in zip(ra, rb)),
            'state_changed_sites': sum((x & 0xffffffff) != (y & 0xffffffff) for x, y in zip(ra, rb)),
            'new_occupied_sites': sum(not (x & 0xffffffff) and bool(y & 0xffffffff) for x, y in zip(ra, rb)),
            'lost_occupied_sites': sum(bool(x & 0xffffffff) and not (y & 0xffffffff) for x, y in zip(ra, rb)),
            'clock_changed_sites': sum(x != y for x, y in zip(ca, cb)),
            'clock_delta_not_elapsed_ticks': sum(y - x != tb - ta for x, y in zip(ca, cb)),
            's_reg_changed_sites': sum(((x >> 32) & 65535) != ((y >> 32) & 65535) for x, y in zip(ra, rb))}


def svg(col, tick, source_sha, occupied):
    n = len(col); scale = 6; left = 42; top = 70
    width = n * scale + 2 * left; height = n * scale + top + 110
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           f'<text x="20" y="24" font-family="sans-serif" font-size="17">T{tick}: ocupación por columna Y</text>',
           '<text x="20" y="45" font-family="sans-serif" font-size="12">Observación externa N0. No mide atención ni memoria.</text>']
    for x in range(n):
        for z in range(n):
            q = col[x][z]
            # One fixed 0..N color map, never normalized separately by cut.
            k = (q * 255) // n
            color = '#%02x%02x%02x' % (255 - k, 255 - (k * 3 // 4), 255 - (k // 4))
            out.append(f'<rect x="{left + x * scale}" y="{top + z * scale}" width="{scale}" height="{scale}" fill="{color}"/>')
    y0 = top + n * scale
    out += [f'<text x="{left}" y="{y0 + 19}" font-family="sans-serif" font-size="12">X: 0..{n - 1}; Z crece hacia abajo (0..{n - 1})</text>']
    for q in range(n + 1):
        k = (q * 255) // n; color = '#%02x%02x%02x' % (255 - k, 255 - k * 3 // 4, 255 - k // 4)
        out.append(f'<rect x="{left + q * 4}" y="{y0 + 28}" width="4" height="12" fill="{color}"/>')
    out += [f'<text x="{left}" y="{y0 + 55}" font-family="sans-serif" font-size="12">Escala común: 0..{n} sitios con state&gt;0 por columna; total={occupied}</text>',
            f'<text x="20" y="{y0 + 76}" font-family="monospace" font-size="8">SHA original: {source_sha}</text>', '</svg>']
    return ('\n'.join(out) + '\n').encode('utf8')


def build(out):
    if out.exists(): raise FileExistsError('Do not overwrite an earlier N0 extraction')
    source = ROOT / PREFIX / 'PREFIJO_COMPLETADO_ORIGINAL.jsonl.gz'
    encoded = source.read_bytes()
    if sha(encoded) != PREFIX_SHA: raise ValueError('Closed prefix changed')
    lines = gzip.decompress(encoded).splitlines(keepends=True)
    parser_path = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    parser_bytes = parser_path.read_bytes()
    obs = load_module('saved_R04_snapshot_parser_no_engine', parser_path)
    out.mkdir(); (out / 'CODIGO').mkdir()
    shutil.copy2(Path(__file__), out / 'CODIGO' / Path(__file__).name)
    with (out / 'CODIGO' / parser_path.name).open('xb') as stream: stream.write(parser_bytes)
    frames = []; arrays = []; before_ids = set(); after_new = []; work_receipts = {}
    for line_no, expected_tick, label in CUTS:
        line = lines[line_no]; row = json.loads(line)
        matches = [(loc, obj['committed_snapshot']) for loc, obj in walk(row) if 'committed_snapshot' in obj]
        if len(matches) != 1: raise ValueError('Unique committed full cut required')
        locator, record = matches[0]
        if record['life_id'] != 'APD04_CONTINUABLE_R01' or record['physical']['tick'] != expected_tick:
            raise ValueError('Never select a different life/cut as fallback')
        full = ROOT / 'sistema' / record['snapshot']
        snapshot = obs.Snapshot(full)
        if snapshot.encoded_sha256 != record['snapshot_sha256'] or snapshot.tick != expected_tick or not snapshot.checksum_valid:
            raise ValueError('Full saved snapshot differs from primary')
        rb, cb = obs.pbytes(snapshot.raw), obs.pbytes(snapshot.clocks)
        if sha(rb) != record['physical']['RAW_sha256'] or sha(cb) != record['physical']['clocks_sha256']:
            raise ValueError('Full arrays differ from primary')
        name = f'R04_T{snapshot.tick}_RAW_CLOCKS_U64_LE.zlib'
        data = zlib.compress(rb + cb, 9)
        with (out / name).open('xb') as stream: stream.write(data)
        metadata = {k: {'exact_value': val, 'packet_sha256': sha(snapshot.metadata_packets[k])}
                    for k, val in snapshot.metadata.items() if not k.startswith('dee_thinking.organizational.v1.')}
        owner_packets = [{'key': k, 'bytes': len(snapshot.metadata_packets[k]), 'sha256': sha(snapshot.metadata_packets[k])}
                         for k in snapshot.metadata if k.startswith('dee_thinking.organizational.v1.')]
        context = {'N': snapshot.N, 'tick': snapshot.tick, 'source_full_snapshot_sha256': snapshot.encoded_sha256,
                   'paused': snapshot.paused, 'phase': snapshot.phase, 'next_event_id': snapshot.next_event_id,
                   'next_sequence': snapshot.next_sequence, 'backend': snapshot.backend, 'threads': snapshot.threads,
                   'all_channels_exact_values': snapshot.channels, 'all_pending_native_inputs': snapshot.pending,
                   'non_organizational_metadata_exact_values': metadata,
                   'omitted_organizational_owner_chunks': owner_packets,
                   'all_native_receipts_in_original_count': len(snapshot.receipts),
                   'scope': 'Passive complete fields, all interfaces/pending Native inputs and non-owner operational packets. Historical receipts and organizational owner chunks remain in full source. No external SQLite queue at the historical instant is inferred from a later database. Not restorable alone.'}
        context_name = f'R04_T{snapshot.tick}_CONTEXTO.json.gz'; save(out / context_name, context)
        frame = {'label': label, 'zero_based_line_in_closed_prefix': line_no,
                 'primary_line_sha256': sha(line), 'original_request_id': row['event']['request_id'],
                 'committed_snapshot_locator': locator + '.committed_snapshot', 'committed_state_original_values': record,
                 'source_full_snapshot': full.relative_to(ROOT).as_posix(), 'source_full_snapshot_sha256': snapshot.encoded_sha256,
                 'source_full_snapshot_bytes': full.stat().st_size, 'source_checksum_valid': True,
                 'file': name, 'sha256': sha(data), 'bytes': len(data), 'N': snapshot.N, 'tick': snapshot.tick,
                 'decoded_RAW_sha256': sha(rb), 'decoded_clocks_sha256': sha(cb),
                 'metrics': metrics(snapshot.raw, snapshot.clocks, snapshot.N, snapshot.tick),
                 'local_boxes_nonadditive': local_metrics(snapshot.raw, snapshot.clocks, snapshot.N, snapshot.tick),
                 'context_file': context_name, 'context_sha256': file_sha(out / context_name)}
        frames.append(frame); arrays.append((snapshot.raw, snapshot.clocks, snapshot.tick))
        if expected_tick == 653846: before_ids = {r['id'] for r in snapshot.receipts}
        if expected_tick == 655722: after_new = [r for r in snapshot.receipts if r['id'] not in before_ids]
        if line_no == 617:
            for loc, node in walk(row):
                receipt = node.get('receipt')
                if isinstance(receipt, dict) and 'id' in receipt:
                    identifier = int(receipt['id'])
                    item = {'port': node.get('port'), 'site': node.get('site'),
                            'receipt_original': receipt, 'primary_line': 617, 'locator': loc + '.receipt'}
                    group = work_receipts.setdefault(identifier, {'id': identifier, 'all_primary_witnesses': []})
                    group['all_primary_witnesses'].append(item)
        del snapshot
    if parser_path.read_bytes() != parser_bytes: raise ValueError('Parser changed while capturing this N0 extraction')
    for identifier, row in work_receipts.items():
        exact = [r for r in after_new if r['id'] == identifier]
        row['native_snapshot_receipt_numeric'] = exact[0] if len(exact) == 1 else None
        row['all_primary_statuses'] = sorted({w['receipt_original']['status'] for w in row['all_primary_witnesses']})
        candidates = []
        if len(exact) == 1:
            for witness in row['all_primary_witnesses']:
                receipt = witness['receipt_original']
                if all(receipt.get(k) == exact[0].get(k) for k in ('id', 'requested_tick', 'effective_tick', 'channels', 'reason')):
                    candidates.append(receipt['status'])
        unique = set(candidates)
        row['final_status_supported_by_snapshot_and_primary'] = next(iter(unique)) if len(unique) == 1 else 'UNRESOLVED'
        row['final_status_scope'] = 'Match exact final native receipt by ID/requested/effective tick/channels/reason; never select last text or count repeated stage witnesses as separate inputs.'
    statuses = Counter(r['final_status_supported_by_snapshot_and_primary'] for r in work_receipts.values())
    index = {'schema': 'APD04.R04.exact_fields_context.N0.R02', 'Native_ticks': 0,
             'life': 'APD04_CONTINUABLE_R01', 'prefix_source': PREFIX + '/PREFIJO_COMPLETADO_ORIGINAL.jsonl.gz',
             'prefix_sha256': PREFIX_SHA, 'parser_sha256': sha(parser_bytes), 'fields': frames,
             'comparisons': [compare(arrays[0], arrays[1]), compare(arrays[1], arrays[2])],
             'work03_unique_receipts': sorted(work_receipts.values(), key=lambda r: r['id']),
             'work03_receipt_status_counts': dict(statuses), 'work03_new_snapshot_receipts': after_new,
             'primary_receipt_ids_missing_from_new_native_receipts': sorted(set(work_receipts) - {r['id'] for r in after_new}),
             'new_native_receipt_ids_without_primary_receipt_node': sorted({r['id'] for r in after_new} - set(work_receipts)),
             'bounds': {'pre_work02_tick': 653376, 'post_goal1_tick': 653846, 'post_work03_tick': 655722,
                        'exact_tick_before_first_density_birth_available': False,
                        'no_observed_collision_lineage_in_interval': True,
                        'no_before_after_control_same_protocol_without_work03_in_this_extraction': True},
             'limits': ['End states constrain growth to an interval, not one birth site, a unique load lineage or a proven cause.',
                        'State=0 with nonzero RAW is counted separately, not treated as an empty usable register.',
                        'All physical clocks advancing by elapsed ticks is a trivial clock property, not historical content decoding.',
                        'The geometric boxes overlap and are not exhaustive causal boundaries or autonomous bodies.',
                        'All queues/interfaces are only those encoded in these saved full snapshots. No current SQLite state is substituted for a historical queue.',
                        'No functionality, attention, memory, P2 or death is inferred from occupancy. Native unformed output remains NULL.']}
    save(out / 'INDICE_CAMPOS_Y_CONTEXTOS.json', index)
    # Flat exact integer CSV is an analysis intermediate, not a formatted workbook.
    buffer = io.StringIO(newline=''); writer = csv.writer(buffer, lineterminator='\n')
    writer.writerow(['tick', 'x', 'z', 'occupied_y_count', 'possible_y_sites', 'source_snapshot_sha256'])
    maps = []
    for frame, (raw, clocks, tick) in zip(frames, arrays):
        col = columns(raw, frame['N'])
        for x in range(frame['N']):
            for z in range(frame['N']): writer.writerow([tick, x, z, col[x][z], frame['N'], frame['source_full_snapshot_sha256']])
        if tick in (653846, 655722):
            name = f'MAPA_XZ_T{tick}.svg'
            with (out / name).open('xb') as stream: stream.write(svg(col, tick, frame['source_full_snapshot_sha256'], frame['metrics']['occupied_state_nonzero']))
            maps.append(name)
    with (out / 'OCUPACION_POR_COLUMNA_Y.csv').open('x', encoding='utf8', newline='') as stream: stream.write(buffer.getvalue())
    rr = list(csv.DictReader(io.StringIO(buffer.getvalue())))
    for frame in frames:
        if sum(int(r['occupied_y_count']) for r in rr if int(r['tick']) == frame['tick']) != frame['metrics']['occupied_state_nonzero']:
            raise ValueError('Exact CSV counts do not reconcile')
    members = [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': file_sha(p)}
               for p in sorted(out.rglob('*')) if p.is_file()]
    save(out / 'MANIFIESTO.json', {'members': members, 'self_hash_excluded': True, 'restorable_as_life': False})
    print(json.dumps({'out': str(out), 'ticks': [f['tick'] for f in frames], 'occupancy': [f['metrics']['occupied_state_nonzero'] for f in frames],
                      'work03_receipts': dict(statuses), 'maps': maps, 'Native_ticks': 0}, ensure_ascii=False))


def recalc(folder, out):
    if out.exists(): raise FileExistsError('Preserve previous recalc')
    index = json.loads((folder / 'INDICE_CAMPOS_Y_CONTEXTOS.json').read_bytes()); checks = []; arrays = []
    for frame in index['fields']:
        encoded = (folder / frame['file']).read_bytes(); data = zlib.decompress(encoded); count = frame['N'] ** 3
        if len(data) != count * 16 or sha(encoded) != frame['sha256']: raise ValueError('Field identity/dimensions differ')
        rb, cb = data[:count * 8], data[count * 8:]
        if sha(rb) != frame['decoded_RAW_sha256'] or sha(cb) != frame['decoded_clocks_sha256']: raise ValueError('Exact uint64 source hashes differ')
        raw, clocks = array('Q'), array('Q'); raw.frombytes(rb); clocks.frombytes(cb)
        if sys.byteorder != 'little': raw.byteswap(); clocks.byteswap()
        if metrics(raw, clocks, frame['N'], frame['tick']) != frame['metrics']: raise ValueError('Metrics differ')
        if json.loads(encoded_json(local_metrics(raw, clocks, frame['N'], frame['tick']))) != frame['local_boxes_nonadditive']: raise ValueError('Local box metrics differ')
        if file_sha(folder / frame['context_file']) != frame['context_sha256']: raise ValueError('Context hash differs')
        context = json.loads(gzip.decompress((folder / frame['context_file']).read_bytes()))
        if context['source_full_snapshot_sha256'] != frame['source_full_snapshot_sha256']: raise ValueError('Context provenance differs')
        col = columns(raw, frame['N'])
        if frame['tick'] in (653846, 655722):
            expected = svg(col, frame['tick'], frame['source_full_snapshot_sha256'], frame['metrics']['occupied_state_nonzero'])
            if expected != (folder / f'MAPA_XZ_T{frame["tick"]}.svg').read_bytes(): raise ValueError('SVG is not the fixed-scale numeric map')
        arrays.append((raw, clocks, frame['tick'])); checks.append({'tick': frame['tick'], 'exact_fields_and_metrics': True})
    pairs = [compare(arrays[0], arrays[1]), compare(arrays[1], arrays[2])]
    if pairs != index['comparisons']: raise ValueError('Physical endpoint comparison differs')
    statuses = dict(Counter(r['final_status_supported_by_snapshot_and_primary'] for r in index['work03_unique_receipts']))
    if statuses != index['work03_receipt_status_counts']: raise ValueError('Receipt denominator/status differs')
    rows = list(csv.DictReader((folder / 'OCUPACION_POR_COLUMNA_Y.csv').open(encoding='utf8', newline='')))
    for frame, (raw, clocks, tick) in zip(index['fields'], arrays):
        selected = [r for r in rows if int(r['tick']) == tick]; col = columns(raw, frame['N'])
        if len(selected) != frame['N'] ** 2: raise ValueError('CSV spatial coverage differs')
        if any(int(r['occupied_y_count']) != col[int(r['x'])][int(r['z'])] or r['source_snapshot_sha256'] != frame['source_full_snapshot_sha256'] for r in selected): raise ValueError('CSV values or origin differ')
    result = {'schema': 'APD04.R04.offline_fields_recalculated.R01', 'checks': checks, 'comparisons': pairs,
              'work03_receipt_status_counts': statuses, 'csv_rows_verified': len(rows), 'Native_ticks': 0,
              'scope': 'Archived exact-field/context/maps/receipt recalc only. Not Native replay or restoration.'}
    save(out, result); print(json.dumps(result, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--recalc', type=Path); args = ap.parse_args()
    recalc(args.recalc, args.out) if args.recalc else build(args.out)
