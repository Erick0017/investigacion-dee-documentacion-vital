"""N0 work04 supplement. Reuses exact R02 RAW; never duplicates a dense world.

Only offline parsing of the published FULL and closed Delivery prefix. A constant
clock representation is accepted only after exact integer/hash verification.
Portable recalc requires this supplement AND its declared R02 base component.
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
PREFIX = 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/PREFIJO_R04_COMPLETADO_WORK04_N0_R02/PREFIJO_COMPLETADO_ORIGINAL.jsonl.gz'
PREFIX_SHA = 'a944ee889ef28a75d1ffbdb21e9c08da5c23cf64200fad541593ee6579c3c3ed'


def sha(data): return hashlib.sha256(data).hexdigest()
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module


def helpers():
    copied = HERE / 'extraer_densificacion_r04_contextos_n0_r02.py'
    return load('offline_R02_helpers_only', copied)


def base_arrays(base):
    index_bytes = (base / 'INDICE_CAMPOS_Y_CONTEXTOS.json').read_bytes()
    index = json.loads(index_bytes)
    frame = next(r for r in index['fields'] if r['tick'] == 655722)
    encoded = (base / frame['file']).read_bytes(); data = zlib.decompress(encoded); count = frame['N'] ** 3
    if len(data) != count * 16 or sha(encoded) != frame['sha256']: raise ValueError('R02 base arrays differ')
    rb, cb = data[:count * 8], data[count * 8:]
    if sha(rb) != frame['decoded_RAW_sha256'] or sha(cb) != frame['decoded_clocks_sha256']: raise ValueError('Base exact field hashes differ')
    raw, clocks = array('Q'), array('Q'); raw.frombytes(rb); clocks.frombytes(cb)
    if sys.byteorder != 'little': raw.byteswap(); clocks.byteswap()
    context = json.loads(gzip.decompress((base / frame['context_file']).read_bytes()))
    return index_bytes, frame, raw, clocks, context


def build(base, out):
    if out.exists(): raise FileExistsError('Never overwrite an existing offline supplement')
    h = helpers(); index_bytes, frame, raw, clocks, context = base_arrays(base)
    encoded = (ROOT / PREFIX).read_bytes()
    if sha(encoded) != PREFIX_SHA: raise ValueError('Closed work04 prefix differs')
    line = gzip.decompress(encoded).splitlines(keepends=True)[1490]; primary = json.loads(line)
    found = [(loc, node['committed_snapshot']) for loc, node in h.walk(primary) if 'committed_snapshot' in node]
    if len(found) != 1: raise ValueError('Unique published FULL required')
    loc, committed = found[0]
    if committed['life_id'] != 'APD04_CONTINUABLE_R01' or committed['physical']['tick'] != 657286:
        raise ValueError('Do not substitute another life/future')
    parser = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'; parser_bytes = parser.read_bytes()
    obs = load('work04_saved_snapshot_only', parser)
    source = ROOT / 'sistema' / committed['snapshot']; snapshot = obs.Snapshot(source)
    if snapshot.encoded_sha256 != committed['snapshot_sha256'] or not snapshot.checksum_valid:
        raise ValueError('Published full snapshot differs')
    rb, cb = obs.pbytes(snapshot.raw), obs.pbytes(snapshot.clocks)
    if sha(rb) != committed['physical']['RAW_sha256'] or sha(cb) != committed['physical']['clocks_sha256']:
        raise ValueError('Saved full fields differ from committed primary')
    if snapshot.raw != raw: raise ValueError('RAW is not identical: cannot use a reused-base encoding')
    constant = array('Q', [snapshot.tick]) * len(raw)
    if snapshot.clocks != constant or sha(obs.pbytes(constant)) != sha(cb):
        raise ValueError('Clocks are not exactly constant; do not omit their values')
    if context['all_pending_native_inputs']: raise ValueError('Base has pending IDs: age-only receipt threshold insufficient')
    new_receipts = [r for r in snapshot.receipts if r['id'] >= context['next_event_id']]
    receipts = {}
    for where, node in h.walk(primary):
        receipt = node.get('receipt')
        if isinstance(receipt, dict) and 'id' in receipt:
            receipts.setdefault(int(receipt['id']), []).append({'locator': where + '.receipt', 'receipt_original': receipt, 'port': node.get('port'), 'site': node.get('site')})
    resolved = []
    for identifier, witnesses in sorted(receipts.items()):
        terminal = [r for r in new_receipts if r['id'] == identifier]
        candidates = set()
        if len(terminal) == 1:
            candidates = {w['receipt_original']['status'] for w in witnesses
                          if all(w['receipt_original'].get(k) == terminal[0].get(k)
                                 for k in ('id', 'requested_tick', 'effective_tick', 'channels', 'reason'))}
        resolved.append({'id': identifier, 'all_primary_witnesses': witnesses,
                         'final_native_receipt': terminal[0] if len(terminal) == 1 else None,
                         'terminal_status_supported_by_FULL': next(iter(candidates)) if len(candidates) == 1 else 'UNRESOLVED'})
    out.mkdir(); (out / 'CODIGO').mkdir()
    for path in (Path(__file__), HERE / 'extraer_densificacion_r04_contextos_n0_r02.py'):
        shutil.copy2(path, out / 'CODIGO' / path.name)
    with (out / 'CODIGO' / parser.name).open('xb') as stream: stream.write(parser_bytes)
    work_context = {'tick': snapshot.tick, 'source_full_snapshot_sha256': snapshot.encoded_sha256,
                    'phase': snapshot.phase, 'paused': snapshot.paused, 'next_event_id': snapshot.next_event_id,
                    'next_sequence': snapshot.next_sequence, 'backend': snapshot.backend, 'threads': snapshot.threads,
                    'all_channels_exact_values': snapshot.channels, 'all_pending_native_inputs': snapshot.pending,
                    'non_organizational_metadata_exact_values': {k: {'exact_value': val, 'packet_sha256': sha(snapshot.metadata_packets[k])}
                        for k, val in snapshot.metadata.items() if not k.startswith('dee_thinking.organizational.v1.')},
                    'omitted_owner_chunks': [{'key': k, 'sha256': sha(snapshot.metadata_packets[k]), 'bytes': len(snapshot.metadata_packets[k])}
                        for k in snapshot.metadata if k.startswith('dee_thinking.organizational.v1.')],
                    'all_native_receipts_in_original_count': len(snapshot.receipts), 'all_new_native_receipts_since_base': new_receipts}
    h.save(out / 'CONTEXTO_T657286.json.gz', work_context)
    result = {'schema': 'APD04.R04.work04.RAW_persistence_supplement.N0.R03', 'Native_ticks': 0,
              'base_required': {'component': 'R04_DENSIFICACION_CONTEXTOS_N0_R02', 'index_sha256': sha(index_bytes),
                                'fields_file': frame['file'], 'fields_sha256': frame['sha256'], 'RAW_sha256': sha(rb),
                                'not_self_contained_without_base': True},
              'published_full': {'source': source.relative_to(ROOT).as_posix(), 'sha256': snapshot.encoded_sha256,
                                 'bytes': source.stat().st_size, 'checksum_valid': True},
              'primary': {'closed_prefix': PREFIX, 'sha256': PREFIX_SHA, 'line_zero_based': 1490,
                          'line_sha256': sha(line), 'committed_locator': loc + '.committed_snapshot',
                          'request_id': primary['event']['request_id'], 'committed_original_values': committed},
              'clock_encoding_exact_after_source_verification': {'encoding': 'uint64 little endian constant',
                           'value': str(snapshot.tick), 'count': len(raw), 'decoded_sha256': sha(cb),
                           'regeneration_verified_before_exclusion': True},
              'metrics': h.metrics(snapshot.raw, snapshot.clocks, snapshot.N, snapshot.tick),
              'comparison': h.compare((raw, clocks, 655722), (snapshot.raw, snapshot.clocks, snapshot.tick)),
              'context_file': 'CONTEXTO_T657286.json.gz', 'context_sha256': h.file_sha(out / 'CONTEXTO_T657286.json.gz'),
              'channels_equal': context['all_channels_exact_values'] == snapshot.channels,
              'pending_equal': context['all_pending_native_inputs'] == snapshot.pending,
              'metadata_changed_keys_non_owner': sorted(k for k in set(context['non_organizational_metadata_exact_values']) | set(work_context['non_organizational_metadata_exact_values'])
                    if context['non_organizational_metadata_exact_values'].get(k) != work_context['non_organizational_metadata_exact_values'].get(k)),
              'work04_receipts_by_unique_ID': resolved,
              'terminal_status_counts': dict(Counter(r['terminal_status_supported_by_FULL'] for r in resolved)),
              'new_native_receipt_count': len(new_receipts),
              'snapshot_receipt_count_increment': len(snapshot.receipts) - context['all_native_receipts_in_original_count'],
              'primary_IDs_equal_new_FULL_IDs': set(receipts) == {r['id'] for r in new_receipts},
              'limits': ['Same complete RAW for1564ticks is not the same complete causal state: clocks, receipts and operational packets changed.',
                         'All19new inputs being rejected in this window is not proof of irreversible global absorption or complete information loss.',
                         'No Native continuation, owner or SQLite was opened. Full states remain local; this differential extraction cannot continue a life.',
                         'This comparison supplies no controlled alternative past and no unique origin of the earlier densification.']}
    h.save(out / 'COMPARACION_WORK03_WORK04.json', result)
    h.save(out / 'MANIFIESTO.json', {'members': [{'file': p.relative_to(out).as_posix(), 'bytes': p.stat().st_size, 'sha256': h.file_sha(p)}
                                              for p in sorted(out.rglob('*')) if p.is_file()], 'self_hash_excluded': True,
                                    'external_analysis_base_required': 'R04_DENSIFICACION_CONTEXTOS_N0_R02'})
    print(json.dumps({'out': str(out), 'comparison': result['comparison'], 'statuses': result['terminal_status_counts'],
                      'new_receipts': len(new_receipts), 'base_required': True, 'Native_ticks': 0}, ensure_ascii=False))


def recalc(base, folder, out):
    h = helpers(); index_bytes, frame, raw, clocks, context = base_arrays(base)
    result = json.loads((folder / 'COMPARACION_WORK03_WORK04.json').read_bytes())
    if sha(index_bytes) != result['base_required']['index_sha256']: raise ValueError('Required base index changed')
    enc = result['clock_encoding_exact_after_source_verification']; count = enc['count']; new = array('Q', [int(enc['value'])]) * count
    tmp = array('Q', new)
    if sys.byteorder != 'little': tmp.byteswap()
    if sha(tmp.tobytes()) != enc['decoded_sha256']: raise ValueError('Regenerated constant clocks differ')
    if h.compare((raw, clocks, 655722), (raw, new, int(enc['value']))) != result['comparison']: raise ValueError('Endpoint comparison differs')
    if h.metrics(raw, new, frame['N'], int(enc['value'])) != result['metrics']: raise ValueError('Metrics differ')
    if h.file_sha(folder / result['context_file']) != result['context_sha256']: raise ValueError('Context differs')
    statuses = dict(Counter(r['terminal_status_supported_by_FULL'] for r in result['work04_receipts_by_unique_ID']))
    if statuses != result['terminal_status_counts']: raise ValueError('Unique-ID terminal denominator differs')
    if out.exists(): raise FileExistsError('Preserve previous recalc')
    h.save(out, {'schema': 'APD04.work04.differential_recalc.N0.R03', 'Native_ticks': 0,
                 'comparison': result['comparison'], 'terminal_status_counts': statuses,
                 'RAW_reused_with_exact_base_hash': True, 'constant_clocks_regenerated_exactly': True})
    print(json.dumps({'recalc': str(out), 'Native_ticks': 0, 'statuses': statuses}, ensure_ascii=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--base', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True); ap.add_argument('--recalc', type=Path)
    args = ap.parse_args(); recalc(args.base, args.recalc, args.out) if args.recalc else build(args.base, args.out)
