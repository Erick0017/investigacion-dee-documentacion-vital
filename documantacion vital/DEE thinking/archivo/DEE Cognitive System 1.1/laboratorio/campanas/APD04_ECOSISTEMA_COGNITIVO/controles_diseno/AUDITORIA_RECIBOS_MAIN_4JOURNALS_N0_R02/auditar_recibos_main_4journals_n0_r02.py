"""N0 audit of receipt scope: original workshop R01 vs whole MAIN FULL delta.

No engine, SQLite, writes to R01 or living state. Port/channel are attributes,
not filters: every exact Native receipt is grouped by its own integer ID.
"""
from collections import Counter, defaultdict
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
OLD = 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/RECALCULO_MAIN_CERRADO_PREFIJO_Y_ADVERSO_R01/RECALCULO_COMPACTO.json'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def load(name, path):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
def read(path): return json.loads(path.read_bytes())
def dump(path, value):
    with path.open('x', encoding='utf8', newline='\n') as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2); stream.write('\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__); ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    if a.out.exists(): raise FileExistsError('Do not overwrite earlier evidence')
    old_path = ROOT / OLD; old_bytes = old_path.read_bytes(); old = json.loads(old_bytes)
    helper_path = HERE / 'compactar_recalcular_taller_n0.py'; helper = load('receipt_walk_offline_only', helper_path)
    witness = defaultdict(list); wrappers = defaultdict(set); commits = []; primary_sources = []
    for source in old['sources']:
        path = Path(source['source']); encoded = path.read_bytes()
        if hashlib.sha256(encoded).hexdigest() != source['sha256_of_bytes_read']: raise ValueError('Original closed journal differs')
        primary_sources.append({'source': path.relative_to(ROOT).as_posix(), 'sha256': source['sha256_of_bytes_read'], 'bytes': len(encoded)})
        for line_no, line in enumerate(encoded.splitlines(keepends=True)):
            row = json.loads(line); event = row.get('event', {}).get('request_id')
            for loc, node in helper.walk(row):
                if not isinstance(node, dict): continue
                if 'committed_snapshot' in node:
                    commits.append({'source': path.relative_to(ROOT).as_posix(), 'line': line_no,
                                    'locator': loc + '.committed_snapshot', 'state': node['committed_snapshot']})
                wrapped = node.get('receipt')
                if isinstance(wrapped, dict) and type(wrapped.get('id')) is int:
                    if 'port' in node: wrappers[wrapped['id']].add('port')
                    if 'channel' in node: wrappers[wrapped['id']].add('channel')
                if {'id', 'kind', 'status', 'requested_tick', 'channels'} <= set(node) and type(node['id']) is int:
                    witness[node['id']].append({'receipt': node, 'source': path.relative_to(ROOT).as_posix(),
                                               'line': line_no, 'locator': loc, 'event': event})
    first_before = read(ROOT / 'evidencia/campanas/APD04_ECOSISTEMA_COGNITIVO/MAIN_PILOTO_R02/TRAYECTORIA/ANTES_DE_NATIVE.json')['record']
    last = max(commits, key=lambda c: c['state']['physical']['tick'])
    if first_before['physical']['tick'] != 604825 or last['state']['physical']['tick'] != 658938:
        raise ValueError('Expected original MAIN endpoints differ; no fallback')
    obs_path = ROOT / 'sistema/capacidades/observador_causal_retrospectivo_01.py'
    obs = load('snapshot_receipts_only_no_native', obs_path)
    base = obs.Snapshot(ROOT / 'sistema' / first_before['snapshot'], verify_checksum=False)
    final = obs.Snapshot(ROOT / 'sistema' / last['state']['snapshot'], verify_checksum=False)
    if base.encoded_sha256 != first_before['snapshot_sha256'] or final.encoded_sha256 != last['state']['snapshot_sha256']:
        raise ValueError('Exact encoded endpoint SHA differs')
    before = {r['id']: r for r in base.receipts}; after = {r['id']: r for r in final.receipts}
    changed_prefix = [i for i, r in before.items() if after.get(i) != r]
    added = {i: r for i, r in after.items() if i not in before}; terminal = {}; conflicts = []
    for identifier, snapshot_receipt in added.items():
        candidates = [r for r in witness.get(identifier, [])
                      if all(r['receipt'].get(k) == snapshot_receipt.get(k)
                             for k in ('id', 'requested_tick', 'effective_tick', 'channels', 'reason'))]
        statuses = {r['receipt']['status'] for r in candidates}
        terminal[identifier] = {'id': identifier, 'snapshot_receipt_numeric': snapshot_receipt,
                                'terminal_status': next(iter(statuses)) if len(statuses) == 1 else 'UNRESOLVED',
                                'primary_statuses': sorted({r['receipt']['status'] for r in witness.get(identifier, [])}),
                                'wrapper_fields_present': sorted(wrappers.get(identifier, set())),
                                'first_matching_primary': candidates[0] if candidates else None}
        if len(statuses) != 1: conflicts.append(identifier)
    legacy = {int(k): v for k, v in old['native_receipts_by_id'].items()}
    wrong_legacy = [i for i, r in legacy.items() if i not in terminal or r['status'] != terminal[i]['terminal_status']]
    outside = sorted(set(added) - set(legacy)); missing_global = sorted(set(added) - set(witness))
    grouped = defaultdict(set)
    for identifier in outside:
        for item in witness[identifier]:
            if item['event']: grouped[item['event']].add(identifier)
    result = {'schema': 'APD04.MAIN.four_closed_journals.receipt_scope_FULL.N0.R02', 'Native_ticks': 0,
              'old_R01': {'source': OLD, 'sha256': hashlib.sha256(old_bytes).hexdigest(),
                          'opportunities': old['unique_opportunities'], 'reported_native_IDs': len(legacy),
                          'status_counts': old['last_observation_exported_receipt_status']},
              'source_scope': primary_sources,
              'compactador_source': {'source': helper_path.relative_to(ROOT).as_posix(), 'sha256': sha(helper_path),
                                    'condition': 'Collects dict.receipt.id within recognized workshop rows, without requiring port or channel.',
                                    'RAW_decoder': 'state=raw&0xffffffff; semantic=(raw>>60)&15; signed direction nibbles48/52/56.'},
              'endpoints': [{'tick': s.tick, 'source': str(s.path.relative_to(ROOT)), 'encoded_sha256': s.encoded_sha256,
                             'receipt_count': len(s.receipts), 'next_event_id': s.next_event_id, 'pending_count': len(s.pending)}
                            for s in (base, final)],
              'prefix_receipts_changed_or_missing': changed_prefix,
              'FULL_new_native_IDs': len(added), 'FULL_new_status_counts_from_primaries': dict(Counter(v['terminal_status'] for v in terminal.values())),
              'primary_union_native_IDs': len(witness), 'new_FULL_IDs_missing_from_all_primary_receipts': missing_global,
              'old_workshop_IDs_missing_or_wrong_terminal_vs_FULL': wrong_legacy,
              'FULL_IDs_outside_R01_workshop_scope': outside,
              'outside_workshop_IDs_by_event_nonadditive_if_repeated': {k: sorted(v) for k, v in grouped.items()},
              'unresolved_terminal_IDs': conflicts, 'terminal_receipts_for_all_new_IDs': list(terminal.values()),
              'interpretation': 'The1669denominator describes receipts exported inside32workshop opportunities. Any additional FULL delta belongs to other serialized interventions/queries/preparation, unless IDs prove an omission within that stated scope. Do not relabel scope expansion as missing port/channel data.',
              'limitations': ['Exact encoded SHA/format/receipt tables verified; Native FNV checksum deliberately not recalculated.',
                             'Full endpoint difference and primary unions do not reproduce Native evolution or prove functional cognition.',
                             'Repeated query/poll locations are witnesses, not additional admitted inputs; port/channel are not counted as distinct identities.',
                             'Receipt-only audit does not certify all organizational metadata, queues or continuity of a current later life.']}
    a.out.mkdir(); dump(a.out / 'AUDITORIA_RECIBOS_MAIN.json', result)
    shutil.copy2(Path(__file__), a.out / Path(__file__).name)
    if old_path.read_bytes() != old_bytes: raise ValueError('R01 changed during read-only audit')
    print(json.dumps({'out': str(a.out), 'old_workshop_IDs': len(legacy), 'FULL_delta': len(added),
                      'all_primary_IDs': len(witness), 'outside_old_scope': len(outside), 'legacy_wrong': len(wrong_legacy),
                      'FULL_missing_primary': len(missing_global), 'unresolved': len(conflicts),
                      'status_counts': result['FULL_new_status_counts_from_primaries'], 'Native_ticks': 0}, ensure_ascii=False))


if __name__ == '__main__': main()
